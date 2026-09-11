import json
import random
from pathlib import Path
from collections import Counter, defaultdict

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path("data/processed/intent_discovery_final.jsonl")
OUTPUT_DIR = Path("data/golden")
OUTPUT_FILE = OUTPUT_DIR / "golden_candidates.jsonl"

SEED = 42

# We select more than 200 candidates first.
# This gives us room to manually verify the strongest examples.
CANDIDATE_COUNT = 300

# Final taxonomy
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
# LOAD DATA
# ============================================================

def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            records.append(json.loads(line))

    return records


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("BUILDING GOLDEN EVALUATION CANDIDATE SET")
    print("=" * 70)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    records = load_jsonl(INPUT_FILE)

    print(f"\nLoaded records: {len(records)}")

    # --------------------------------------------------------
    # Group records by intent
    # --------------------------------------------------------

    by_intent = defaultdict(list)

    for record in records:
        intent = record.get("intent")

        if intent in INTENTS:
            by_intent[intent].append(record)

    print("\nAvailable examples by intent:")
    print("-" * 50)

    for intent in INTENTS:
        print(f"{intent:35} {len(by_intent[intent])}")

    # --------------------------------------------------------
    # Desired distribution
    #
    # We intentionally don't make this purely proportional.
    # Rare but important intents get minimum representation.
    # --------------------------------------------------------

    target_counts = {
        "delivery_status_delay": 50,
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
        "customer_support_experience": 20,
        "seller_support_issue": 5,
        "technical_or_system_issue": 5,
        "other_support": 6,
        "non_support_social": 20,
    }

    print("\nRequested candidate distribution:")
    print("-" * 50)

    for intent in INTENTS:
        print(f"{intent:35} {target_counts[intent]}")

    print(f"\nTotal requested: {sum(target_counts.values())}")

    # --------------------------------------------------------
    # Deterministic sampling
    # --------------------------------------------------------

    rng = random.Random(SEED)

    selected = []

    for intent in INTENTS:

        available = by_intent[intent]
        requested = target_counts[intent]

        if not available:
            print(
                f"\nWARNING: No examples available for {intent}"
            )
            continue

        # If there aren't enough examples,
        # take everything available.
        count = min(requested, len(available))

        sampled = rng.sample(available, count)

        selected.extend(sampled)

    # --------------------------------------------------------
    # If total is less than CANDIDATE_COUNT,
    # fill from remaining examples.
    # --------------------------------------------------------

    selected_ids = {
        str(record.get("tweet_id"))
        for record in selected
    }

    remaining = []

    for record in records:

        tweet_id = str(record.get("tweet_id"))

        if tweet_id not in selected_ids:
            intent = record.get("intent")

            if intent in INTENTS:
                remaining.append(record)

    rng.shuffle(remaining)

    needed = CANDIDATE_COUNT - len(selected)

    if needed > 0:
        selected.extend(remaining[:needed])

    # --------------------------------------------------------
    # Sort deterministically
    # --------------------------------------------------------

    rng.shuffle(selected)

    # --------------------------------------------------------
    # Add candidate metadata
    # --------------------------------------------------------

    output_records = []

    for index, record in enumerate(selected, start=1):

        output_record = {
            "candidate_id": index,

            "conversation_id": record.get("conversation_id"),

            "target_tweet_id": record.get("tweet_id"),

            "target_text": record.get("text"),

            # Existing model label is ONLY for candidate selection.
            # It is NOT the gold label.
            "suggested_intent": record.get("intent"),

            # To be filled during human verification.
            "gold_intent": None,

            "annotation_notes": "",

            "source": "intent_discovery_final",

            "random_seed": SEED
        }

        output_records.append(output_record)

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for record in output_records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    # --------------------------------------------------------
    # Final statistics
    # --------------------------------------------------------

    distribution = Counter(
        record["suggested_intent"]
        for record in output_records
    )

    print("\n" + "=" * 70)
    print("GOLDEN CANDIDATE SET CREATED")
    print("=" * 70)

    print(f"\nCandidates created: {len(output_records)}")

    print("\nActual candidate distribution:")
    print("-" * 50)

    for intent in INTENTS:
        print(
            f"{intent:35} "
            f"{distribution[intent]}"
        )

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nIMPORTANT:")
    print("suggested_intent is NOT the gold label.")
    print("gold_intent must be verified independently.")

    print("\nNext step:")
    print("Review these candidates and create the final")
    print("200-example golden evaluation set.")


if __name__ == "__main__":
    main()