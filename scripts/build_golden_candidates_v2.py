import json
import random
from pathlib import Path
from collections import Counter, defaultdict


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/processed/amazonhelp_final_labeled.jsonl"
)

CONVERSATIONS_FILE = Path(
    "data/processed/amazonhelp_conversations.jsonl"
)

OUTPUT_FILE = Path(
    "data/golden/golden_candidates_v2.jsonl"
)

SEED = 42


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
# EXACT CANDIDATE ALLOCATION
# ============================================================

TARGET_COUNTS = {
    "delivery_status_delay": 45,
    "delivery_not_received": 12,
    "delivery_carrier_issue": 20,
    "order_cancellation": 6,
    "return_issue": 8,
    "refund_issue": 12,
    "product_issue": 15,
    "payment_or_cashback": 10,
    "pricing_or_promotion": 10,
    "account_access_security": 8,
    "prime_or_subscription": 8,
    "product_service_information": 25,
    "customer_support_experience": 25,
    "seller_support_issue": 8,
    "technical_or_system_issue": 8,
    "other_support": 5,
    "non_support_social": 25,
}


# ============================================================
# LOAD JSONL
# ============================================================

def load_jsonl(path):

    records = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if line:
                records.append(
                    json.loads(line)
                )

    return records


# ============================================================
# FORMAT FULL CONVERSATION
# ============================================================

def format_conversation(conversation):

    if not conversation:
        return "NO CONVERSATION CONTEXT AVAILABLE"

    lines = []

    for message in conversation.get(
        "messages",
        []
    ):

        speaker = (
            "CUSTOMER"
            if message.get("inbound") is True
            else "AGENT"
        )

        text = message.get(
            "text",
            ""
        )

        lines.append(
            f"{speaker}: {text}"
        )

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("BUILDING GOLDEN CANDIDATE SET V2")
    print("=" * 70)

    # --------------------------------------------------------
    # Validate allocation
    # --------------------------------------------------------

    total_requested = sum(
        TARGET_COUNTS.values()
    )

    print(
        f"\nRequested candidates: "
        f"{total_requested}"
    )

    if total_requested != 250:

        raise ValueError(
            "Candidate allocation must equal exactly 250."
        )

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------

    records = load_jsonl(
        INPUT_FILE
    )

    conversations = load_jsonl(
        CONVERSATIONS_FILE
    )

    print(
        f"Loaded labeled records: "
        f"{len(records)}"
    )

    print(
        f"Loaded conversations: "
        f"{len(conversations)}"
    )

    # --------------------------------------------------------
    # Conversation lookup
    # --------------------------------------------------------

    conversation_lookup = {}

    for conversation in conversations:

        conversation_id = str(
            conversation.get(
                "conversation_id"
            )
        )

        conversation_lookup[
            conversation_id
        ] = conversation

    # --------------------------------------------------------
    # Group by intent
    # --------------------------------------------------------

    by_intent = defaultdict(list)

    for record in records:

        intent = record.get(
            "intent"
        )

        if intent in INTENTS:

            by_intent[intent].append(
                record
            )

    # --------------------------------------------------------
    # Display availability
    # --------------------------------------------------------

    print("\nAvailable examples:")
    print("-" * 55)

    for intent in INTENTS:

        available = len(
            by_intent[intent]
        )

        requested = TARGET_COUNTS[intent]

        status = (
            "OK"
            if available >= requested
            else "NOT ENOUGH"
        )

        print(
            f"{intent:35} "
            f"{available:4} available / "
            f"{requested:3} needed  [{status}]"
        )

    # --------------------------------------------------------
    # Validate enough data
    # --------------------------------------------------------

    insufficient = []

    for intent in INTENTS:

        if len(by_intent[intent]) < TARGET_COUNTS[intent]:

            insufficient.append(
                intent
            )

    if insufficient:

        print(
            "\nERROR: Not enough examples for:"
        )

        for intent in insufficient:
            print(
                f"  - {intent}"
            )

        raise RuntimeError(
            "Cannot create exact 250-candidate set."
        )

    # --------------------------------------------------------
    # Deterministic sampling
    # --------------------------------------------------------

    rng = random.Random(
        SEED
    )

    selected = []

    for intent in INTENTS:

        available = by_intent[intent]

        requested = TARGET_COUNTS[intent]

        sampled = rng.sample(
            available,
            requested
        )

        selected.extend(
            sampled
        )

    # --------------------------------------------------------
    # Shuffle final candidate order
    # --------------------------------------------------------

    rng.shuffle(
        selected
    )

    # --------------------------------------------------------
    # Build candidate records
    # --------------------------------------------------------

    output_records = []

    for candidate_id, record in enumerate(
        selected,
        start=1
    ):

        conversation_id = str(
            record.get(
                "conversation_id"
            )
        )

        conversation = conversation_lookup.get(
            conversation_id
        )

        context = format_conversation(
            conversation
        )

        candidate = {

            "candidate_id":
                candidate_id,

            "conversation_id":
                conversation_id,

            "target_tweet_id":
                record.get(
                    "tweet_id"
                ),

            "target_text":
                record.get(
                    "text",
                    ""
                ),

            # Existing label is only a suggestion.
            "suggested_intent":
                record.get(
                    "intent"
                ),

            # IMPORTANT:
            # This will be independently verified.
            "gold_intent":
                None,

            "annotation_notes":
                "",

            "conversation_context":
                context,

            "source":
                "amazonhelp_final_labeled",

            "random_seed":
                SEED
        }

        output_records.append(
            candidate
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for candidate in output_records:

            f.write(
                json.dumps(
                    candidate,
                    ensure_ascii=False
                ) + "\n"
            )

    # --------------------------------------------------------
    # Verify output
    # --------------------------------------------------------

    distribution = Counter(
        candidate[
            "suggested_intent"
        ]
        for candidate in output_records
    )

    unique_tweet_ids = {
        str(
            candidate[
                "target_tweet_id"
            ]
        )
        for candidate in output_records
    }

    unique_candidate_ids = {
        candidate[
            "candidate_id"
        ]
        for candidate in output_records
    }

    print("\n" + "=" * 70)
    print("GOLDEN CANDIDATES CREATED")
    print("=" * 70)

    print(
        f"\nTotal candidates: "
        f"{len(output_records)}"
    )

    print(
        f"Unique tweet IDs: "
        f"{len(unique_tweet_ids)}"
    )

    print(
        f"Unique candidate IDs: "
        f"{len(unique_candidate_ids)}"
    )

    print("\nCandidate distribution:")
    print("-" * 55)

    for intent in INTENTS:

        actual = distribution[intent]

        expected = TARGET_COUNTS[intent]

        status = (
            "OK"
            if actual == expected
            else "ERROR"
        )

        print(
            f"{intent:35} "
            f"{actual:3} / "
            f"{expected:3} [{status}]"
        )

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nIMPORTANT:")
    print(
        "suggested_intent is NOT the gold label."
    )

    print(
        "gold_intent must be independently verified."
    )

    print("\nNext phase:")
    print(
        "Select and verify 200 of these 250 candidates."
    )


if __name__ == "__main__":
    main()