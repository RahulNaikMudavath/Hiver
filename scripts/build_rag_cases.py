import json
import re
from pathlib import Path
from collections import defaultdict

CONVERSATIONS_FILE = Path(
    "data/processed/amazonhelp_conversations.jsonl"
)

LABELED_FILE = Path(
    "data/processed/amazonhelp_final_labeled.jsonl"
)

GOLDEN_FILE = Path(
    "data/golden/golden_eval_draft.jsonl"
)

OUTPUT_DIR = Path("data/knowledge")
OUTPUT_FILE = OUTPUT_DIR / "amazonhelp_historical_cases.jsonl"

# ---------------------------------------------------------
# Locked taxonomy
# ---------------------------------------------------------

VALID_INTENTS = {
    "delivery_status_delay",
    "delivery_not_received",
    "delivery_carrier_issue",
    "order_cancellation",
    "return_issue",
    "refund_issue",
    "product_issue",
    "payment_or_cashback",
    "pricing_or_promotion",
    "account_access_security",
    "prime_or_subscription",
    "product_service_information",
    "customer_support_experience",
    "seller_support_issue",
    "technical_or_system_issue",
    "other_support",
    "non_support_social",
}


def load_jsonl(path):
    records = []

    if not path.exists():
        print(f"WARNING: File not found: {path}")
        return records

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return records


def mask_pii(text):
    if not text:
        return ""

    # Phone numbers
    text = re.sub(
        r"\b(?:\+?\d[\d\s().-]{8,}\d)\b",
        "[PHONE]",
        text
    )

    # Email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL]",
        text
    )

    return text


print("=" * 80)
print("BUILD AMAZONHELP HISTORICAL RAG CASES")
print("=" * 80)

# ---------------------------------------------------------
# Load conversations
# ---------------------------------------------------------

conversations = load_jsonl(CONVERSATIONS_FILE)

print(f"\nConversations loaded : {len(conversations):,}")

# ---------------------------------------------------------
# Load labels
# ---------------------------------------------------------

labeled = load_jsonl(LABELED_FILE)

label_by_tweet = {}

for row in labeled:

    tweet_id = str(
        row.get("tweet_id")
        or row.get("target_tweet_id")
        or ""
    )

    intent = (
        row.get("source_label")
        or row.get("gold_intent")
        or row.get("intent")
    )

    if tweet_id and intent in VALID_INTENTS:
        label_by_tweet[tweet_id] = intent

print(f"Labeled messages      : {len(label_by_tweet):,}")

# ---------------------------------------------------------
# Load golden set IDs
#
# IMPORTANT:
# Never retrieve a golden evaluation example.
# ---------------------------------------------------------

golden = load_jsonl(GOLDEN_FILE)

golden_tweet_ids = set()

for row in golden:

    tweet_id = str(
        row.get("target_tweet_id")
        or row.get("tweet_id")
        or ""
    )

    if tweet_id:
        golden_tweet_ids.add(tweet_id)

print(f"Golden test IDs       : {len(golden_tweet_ids):,}")

# ---------------------------------------------------------
# Build historical customer -> agent cases
# ---------------------------------------------------------

cases = []

seen_customer_ids = set()

for conversation in conversations:

    conversation_id = str(
        conversation.get("conversation_id", "")
    )

    messages = conversation.get("messages", [])

    if not messages:
        continue

    # Ensure chronological order
    messages = sorted(
        messages,
        key=lambda x: x.get("created_at", "")
    )

    for i, customer in enumerate(messages):

        if not customer.get("inbound"):
            continue

        customer_id = str(
            customer.get("tweet_id", "")
        )

        if not customer_id:
            continue

        # Never put golden evaluation examples into KB
        if customer_id in golden_tweet_ids:
            continue

        # Prevent duplicate customer cases
        if customer_id in seen_customer_ids:
            continue

        # Find the next AmazonHelp response
        response = None

        for j in range(i + 1, len(messages)):

            candidate = messages[j]

            if not candidate.get("inbound"):
                response = candidate
                break

        if response is None:
            continue

        response_id = str(
            response.get("tweet_id", "")
        )

        response_text = response.get("text", "").strip()

        customer_text = customer.get(
            "text", ""
        ).strip()

        if not customer_text or not response_text:
            continue

        # -------------------------------------------------
        # Context before customer message
        # -------------------------------------------------

        previous_messages = []

        for previous in messages[:i]:

            role = (
                "CUSTOMER"
                if previous.get("inbound")
                else "AMAZONHELP"
            )

            text = previous.get("text", "").strip()

            if text:
                previous_messages.append(
                    f"{role}: {mask_pii(text)}"
                )

        context = "\n".join(
            previous_messages[-6:]
        )

        # -------------------------------------------------
        # Label
        # -------------------------------------------------

        intent = label_by_tweet.get(customer_id)

        # Keep unlabeled cases for retrieval if useful,
        # but mark them explicitly.
        if intent is None:
            intent = "unlabeled"

        cases.append({
            "case_id": f"{conversation_id}_{customer_id}",
            "conversation_id": conversation_id,
            "customer_tweet_id": customer_id,
            "agent_tweet_id": response_id,

            "intent": intent,

            "customer_message": mask_pii(
                customer_text
            ),

            "historical_response": mask_pii(
                response_text
            ),

            "previous_context": context,

            "source": "AmazonHelp historical conversation"
        })

        seen_customer_ids.add(customer_id)


# ---------------------------------------------------------
# Remove unusable records
# ---------------------------------------------------------

cases = [
    c for c in cases
    if len(c["customer_message"]) >= 3
    and len(c["historical_response"]) >= 3
]

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    for case in cases:

        f.write(
            json.dumps(
                case,
                ensure_ascii=False
            )
            + "\n"
        )


# ---------------------------------------------------------
# Statistics
# ---------------------------------------------------------

intent_counts = defaultdict(int)

for case in cases:
    intent_counts[case["intent"]] += 1


print("\n" + "=" * 80)
print("RAG CORPUS CREATED")
print("=" * 80)

print(
    f"Historical cases : {len(cases):,}"
)

print(
    f"Unique customers : {len(seen_customer_ids):,}"
)

print(
    f"Golden IDs excluded : {len(golden_tweet_ids):,}"
)

print(
    f"\nOutput:"
)

print(
    f"  {OUTPUT_FILE}"
)

print("\n" + "=" * 80)
print("CASES BY INTENT")
print("=" * 80)

for intent, count in sorted(
    intent_counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    print(
        f"{intent:35s} {count:8,}"
    )


print("\n🔥 Historical AmazonHelp RAG corpus complete!")