import json
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(
    "data/processed/other_support_final_reclassified.jsonl"
)

OUTPUT_FILE = Path(
    "data/processed/other_support_final_reclassified_clean.jsonl"
)


def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def main():

    print("=" * 70)
    print("CLEANING OTHER_SUPPORT RECLASSIFICATIONS")
    print("=" * 70)

    records = load_jsonl(INPUT_FILE)

    print(f"\nInput records: {len(records)}")

    # --------------------------------------------------------
    # Find duplicate tweet IDs
    # --------------------------------------------------------

    tweet_ids = [
        str(record.get("tweet_id"))
        for record in records
    ]

    counts = Counter(tweet_ids)

    duplicate_ids = {
        tweet_id
        for tweet_id, count in counts.items()
        if count > 1
    }

    duplicate_records = sum(
        count - 1
        for count in counts.values()
        if count > 1
    )

    print(f"Unique tweet IDs: {len(counts)}")
    print(f"Duplicated tweet IDs: {len(duplicate_ids)}")
    print(f"Duplicate records: {duplicate_records}")

    # --------------------------------------------------------
    # Keep FIRST classification for each tweet ID
    # --------------------------------------------------------

    seen = set()
    cleaned = []

    for record in records:

        tweet_id = str(
            record.get("tweet_id")
        )

        if tweet_id in seen:
            continue

        seen.add(tweet_id)
        cleaned.append(record)

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

        for record in cleaned:

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
        record["new_intent"]
        for record in cleaned
    )

    print("\n" + "=" * 70)
    print("CLEANING COMPLETE")
    print("=" * 70)

    print(f"\nClean records: {len(cleaned)}")
    print(f"Unique tweet IDs: {len(seen)}")

    print("\nDistribution:")
    print("-" * 50)

    for intent, count in sorted(
        distribution.items(),
        key=lambda x: (-x[1], x[0])
    ):
        print(
            f"{intent:35} {count}"
        )

    print("\nOutput:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()