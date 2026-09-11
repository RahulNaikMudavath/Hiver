import json
import os
import sys
import time
import warnings
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Reconfigure console encoding for Windows emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Suppress harmless warnings
warnings.filterwarnings("ignore")

# Load environment variables from .env
load_dotenv()


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/processed/intent_discovery_final.jsonl"
)

CONVERSATIONS_FILE = Path(
    "data/processed/amazonhelp_conversations.jsonl"
)

OUTPUT_FILE = Path(
    "data/processed/other_support_final_reclassified.jsonl"
)

MODEL = "gemini-3.5-flash-lite"

BATCH_SIZE = 5

SLEEP_SECONDS = 1.0


# ============================================================
# FINAL TAXONOMY
# ============================================================

INTENTS = [
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
]


# ============================================================
# LOAD JSONL
# ============================================================

def load_jsonl(path):

    records = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


# ============================================================
# SAVE JSONL
# ============================================================

def append_jsonl(path, records):

    with open(path, "a", encoding="utf-8") as f:

        for record in records:

            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )


# ============================================================
# CONVERSATION LOOKUP
# ============================================================

def build_conversation_lookup(conversations):

    lookup = {}

    for conversation in conversations:

        conversation_id = str(
            conversation.get("conversation_id")
        )

        lookup[conversation_id] = conversation

    return lookup


# ============================================================
# FORMAT CONVERSATION
# ============================================================

def format_conversation(conversation):

    if not conversation:
        return "NO CONVERSATION CONTEXT AVAILABLE"

    messages = conversation.get("messages", [])

    lines = []

    for msg in messages:

        direction = (
            "CUSTOMER"
            if msg.get("inbound") is True
            else "AGENT"
        )

        text = msg.get("text", "")

        lines.append(
            f"{direction}: {text}"
        )

    return "\n".join(lines)


# ============================================================
# PROMPT
# ============================================================

def build_prompt(batch):

    examples = []

    for i, item in enumerate(batch, start=1):

        examples.append(
            f"""
================ EXAMPLE {i} ================

Conversation ID:
{item["conversation_id"]}

Target tweet ID:
{item["tweet_id"]}

TARGET CUSTOMER MESSAGE:
{item["text"]}

FULL CONVERSATION:
{item["conversation_context"]}
"""
        )

    examples_text = "\n".join(examples)

    taxonomy_text = "\n".join(
        f"- {intent}"
        for intent in INTENTS
    )

    return f"""
You are labeling customer-support conversations for an
Amazon customer-support AI evaluation dataset.

We previously labeled these examples as "other_support",
but that category is too broad.

Your job is to assign the BEST intent from the FINAL taxonomy
below using the FULL conversation context.

FINAL TAXONOMY:

{taxonomy_text}

INTENT DEFINITIONS:

delivery_status_delay
= Delivery is delayed, late, stuck, not dispatched, or tracking
  indicates a delay.

delivery_not_received
= Order is marked delivered or delivery is supposedly complete,
  but customer says they did not receive it.

delivery_carrier_issue
= Problem specifically involving courier, driver, delivery
  attempt, delivery location, safe place, or carrier behavior.

order_cancellation
= Customer wants to cancel an order or has a cancellation issue.

return_issue
= Returning an item, return label, return process, or return
  eligibility problem.

refund_issue
= Refund is missing, delayed, incorrect, or customer asks about
  receiving a refund.

product_issue
= Product is damaged, defective, faulty, wrong, incomplete,
  unusable, or otherwise has a product-specific problem.

payment_or_cashback
= Payment, charge, card, billing transaction, cashback,
  promotional credit, or payment-method issue.

pricing_or_promotion
= Price discrepancy, discount, coupon, promotion, deal,
  offer, or promotional eligibility.

account_access_security
= Account login, password, account access, security, verification,
  or account-related problem.

prime_or_subscription
= Prime membership, subscription, membership benefits, or
  subscription billing/cancellation.

product_service_information
= Customer asks for information about a product, service,
  availability, features, policy, or general Amazon service.

customer_support_experience
= Problem is specifically with Amazon customer support itself:
  unresponsive agents, failed callbacks, repeated escalation,
  agents hanging up, poor support experience, inability to get
  help, support communication problems, etc.

seller_support_issue
= Issue specifically concerns seller-side support, seller
  inventory, seller account/process, or seller-specific problems.

technical_or_system_issue
= Website, app, form, technical system, page, download,
  submission, or software/system malfunction.

other_support
= Genuine customer-support issue that cannot reasonably be
  assigned to any of the more specific categories above.

non_support_social
= Casual/social interaction, praise, joke, general conversation,
  or message that is not actually seeking customer support.

IMPORTANT RULES:

1. Use the FULL conversation, not only the target message.
2. Determine the underlying customer problem.
3. "No response", "help", "please look into this", etc. are
   context-dependent.
4. If the problem is failure of customer support itself,
   use customer_support_experience.
5. If the issue is clearly seller-related, use seller_support_issue.
6. If the issue is clearly a website/app/system problem,
   use technical_or_system_issue.
7. Do NOT invent an intent outside the taxonomy.
8. Choose exactly ONE intent per example.
9. Return valid JSON only.
10. Do not include explanations outside the JSON.

Return exactly this structure:

[
  {{
    "index": 1,
    "intent": "one_of_the_taxonomy_labels"
  }},
  {{
    "index": 2,
    "intent": "one_of_the_taxonomy_labels"
  }}
]

Here are the examples:

{examples_text}
"""



# ============================================================
# PARSE MODEL RESPONSE
# ============================================================

def parse_response(text):

    text = text.strip()

    # Remove markdown fences if Gemini adds them
    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    data = json.loads(text)

    if not isinstance(data, list):
        raise ValueError(
            "Model response is not a JSON list"
        )

    return data


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("RECLASSIFYING OTHER_SUPPORT")
    print("=" * 70)

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    client = genai.Client(
        api_key=api_key
    )

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    records = load_jsonl(INPUT_FILE)

    conversations = load_jsonl(
        CONVERSATIONS_FILE
    )

    conversation_lookup = (
        build_conversation_lookup(conversations)
    )

    # --------------------------------------------------------
    # Select OTHER_SUPPORT
    # --------------------------------------------------------

    other_support = [
        record
        for record in records
        if record.get("intent") == "other_support"
    ]

    print(
        f"\nOther-support records: "
        f"{len(other_support)}"
    )

    # --------------------------------------------------------
    # Prepare examples
    # --------------------------------------------------------

    examples = []

    for record in other_support:

        conversation_id = str(
            record.get("conversation_id")
        )

        conversation = conversation_lookup.get(
            conversation_id
        )

        examples.append(
            {
                "tweet_id": record.get("tweet_id"),
                "conversation_id": conversation_id,
                "text": record.get("text", ""),
                "conversation_context":
                    format_conversation(conversation)
            }
        )

    # --------------------------------------------------------
    # Resume support
    # --------------------------------------------------------

    processed_ids = set()

    if OUTPUT_FILE.exists():

        previous = load_jsonl(
            OUTPUT_FILE
        )

        for record in previous:

            processed_ids.add(
                str(record["tweet_id"])
            )

        print(
            f"Already processed: "
            f"{len(processed_ids)}"
        )

    remaining = [
        item
        for item in examples
        if str(item["tweet_id"])
        not in processed_ids
    ]

    print(
        f"Remaining: {len(remaining)}"
    )

    if not remaining:

        print("\nNothing left to process.")
        return

    # --------------------------------------------------------
    # Process batches
    # --------------------------------------------------------

    total_batches = (
        (len(remaining) + BATCH_SIZE - 1)
        // BATCH_SIZE
    )

    for batch_number in range(
        total_batches
    ):

        start = (
            batch_number * BATCH_SIZE
        )

        end = start + BATCH_SIZE

        batch = remaining[start:end]

        print(
            f"\n[{batch_number + 1}/{total_batches}] "
            f"Analyzing {len(batch)} examples..."
        )

        prompt = build_prompt(batch)

        success = False

        for attempt in range(5):

            try:

                response = client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0,
                    ),
                )

                predictions = parse_response(
                    response.text
                )

                if len(predictions) != len(batch):

                    raise ValueError(
                        f"Expected {len(batch)} predictions, "
                        f"got {len(predictions)}"
                    )

                output_batch = []

                for i, item in enumerate(batch):

                    prediction = predictions[i]

                    intent = prediction.get(
                        "intent"
                    )

                    if intent not in INTENTS:

                        raise ValueError(
                            f"Invalid intent: {intent}"
                        )

                    output_batch.append(
                        {
                            "tweet_id":
                                item["tweet_id"],

                            "conversation_id":
                                item["conversation_id"],

                            "text":
                                item["text"],

                            "old_intent":
                                "other_support",

                            "new_intent":
                                intent,

                            "conversation_context":
                                item[
                                    "conversation_context"
                                ]
                        }
                    )

                append_jsonl(
                    OUTPUT_FILE,
                    output_batch
                )

                distribution = {}

                for item in output_batch:

                    label = item["new_intent"]

                    distribution[label] = (
                        distribution.get(label, 0) + 1
                    )

                print(
                    "  ✓ Saved "
                    f"{len(output_batch)}"
                    " classifications"
                )

                for label, count in sorted(
                    distribution.items()
                ):
                    print(
                        f"    {label}: {count}"
                    )

                success = True
                break

            except Exception as e:

                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait_sec = 10 * (attempt + 1)
                    print(
                        f"  ⚠ Rate limit 429 encountered: waiting {wait_sec}s (attempt {attempt + 1}/5)..."
                    )
                    time.sleep(wait_sec)
                else:
                    print(
                        f"  ⚠ Attempt {attempt + 1}/5 failed: "
                        f"{e}"
                    )
                    time.sleep(3)

        if not success:

            print(
                "\nERROR: Batch failed after 3 attempts."
            )

            print(
                "The script is resumable."
            )

            return

        time.sleep(
            SLEEP_SECONDS
        )

    # --------------------------------------------------------
    # Final statistics
    # --------------------------------------------------------

    results = load_jsonl(
        OUTPUT_FILE
    )

    print("\n" + "=" * 70)
    print("RECLASSIFICATION COMPLETE")
    print("=" * 70)

    print(
        f"\nTotal results: {len(results)}"
    )

    counts = {}

    for record in results:

        label = record["new_intent"]

        counts[label] = (
            counts.get(label, 0) + 1
        )

    print("\nFinal distribution:")
    print("-" * 50)

    for label in INTENTS:

        print(
            f"{label:35} "
            f"{counts.get(label, 0)}"
        )

    print("\nOutput:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()