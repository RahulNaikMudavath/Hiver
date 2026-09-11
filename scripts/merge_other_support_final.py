import json
from pathlib import Path
from collections import Counter


# ============================================================
# FILES
# ============================================================

INPUT_FILE = Path(
    "data/processed/intent_discovery_final.jsonl"
)

RECLASSIFIED_FILE = Path(
    "data/processed/other_support_final_reclassified_clean.jsonl"
)

OUTPUT_FILE = Path(
    "data/processed/intent_discovery_taxonomy_final.jsonl"
)


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
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("MERGING FINAL TAXONOMY")
    print("=" * 70)

    # --------------------------------------------------------
    # Load original dataset
    # --------------------------------------------------------

    original = load_jsonl(INPUT_FILE)

    # --------------------------------------------------------
    # Load context-aware reclassifications
    # --------------------------------------------------------

    reclassified = load_jsonl(
        RECLASSIFIED_FILE
    )

    print(
        f"\nOriginal records: {len(original)}"
    )

    print(
        f"Reclassified records: {len(reclassified)}"
    )

    # --------------------------------------------------------
    # Build lookup
    # --------------------------------------------------------

    reclassification_lookup = {}

    for record in reclassified:

        tweet_id = str(
            record["tweet_id"]
        )

        reclassification_lookup[tweet_id] = (
            record["new_intent"]
        )

    print(
        f"Reclassification lookup size: "
        f"{len(reclassification_lookup)}"
    )

    # --------------------------------------------------------
    # Replace labels
    # --------------------------------------------------------

    final_records = []

    changed = 0
    unchanged = 0

    for record in original:

        tweet_id = str(
            record.get("tweet_id")
        )

        old_intent = record.get(
            "intent"
        )

        if (
            old_intent == "other_support"
            and tweet_id in reclassification_lookup
        ):

            new_intent = (
                reclassification_lookup[
                    tweet_id
                ]
            )

            record["intent"] = new_intent

            # Keep an audit trail
            record["previous_intent"] = (
                "other_support"
            )

            record["label_source"] = (
                "context_aware_reclassification"
            )

            changed += 1

        else:

            # Existing labels remain unchanged
            if old_intent == "other_support":
                unchanged += 1

            if "label_source" not in record:
                record["label_source"] = (
                    "initial_classification"
                )

        final_records.append(record)

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

        for record in final_records:

            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    # --------------------------------------------------------
    # Distribution
    # --------------------------------------------------------

    distribution = Counter(
        record.get("intent")
        for record in final_records
    )

    print("\n" + "=" * 70)
    print("MERGE COMPLETE")
    print("=" * 70)

    print(
        f"\nFinal records: {len(final_records)}"
    )

    print(
        f"Reclassified: {changed}"
    )

    print(
        f"Remaining old other_support: {unchanged}"
    )

    print("\nFINAL TAXONOMY DISTRIBUTION:")
    print("-" * 55)

    for intent, count in sorted(
        distribution.items(),
        key=lambda x: (-x[1], x[0])
    ):

        percentage = (
            count / len(final_records) * 100
        )

        print(
            f"{intent:35} "
            f"{count:4} "
            f"({percentage:5.1f}%)"
        )

    print("\nOutput:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()