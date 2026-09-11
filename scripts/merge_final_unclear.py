import json
from pathlib import Path
from collections import Counter


INPUT_FILE = Path(
    "data/processed/intent_discovery_taxonomy_final.jsonl"
)

RESOLVED_FILE = Path(
    "data/processed/final_unclear_resolved.jsonl"
)

OUTPUT_FILE = Path(
    "data/processed/amazonhelp_final_labeled.jsonl"
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
    print("MERGING FINAL UNCLEAR RESOLUTIONS")
    print("=" * 70)

    original = load_jsonl(INPUT_FILE)
    resolved = load_jsonl(RESOLVED_FILE)

    print(f"\nOriginal records: {len(original)}")
    print(f"Resolved unclear: {len(resolved)}")

    lookup = {}

    for record in resolved:
        lookup[str(record["tweet_id"])] = record["new_intent"]

    final = []
    changed = 0

    for record in original:

        tweet_id = str(record.get("tweet_id"))

        if tweet_id in lookup:

            record["previous_intent"] = record.get(
                "intent"
            )

            record["intent"] = lookup[tweet_id]

            record["label_source"] = (
                "final_context_resolution"
            )

            changed += 1

        final.append(record)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for record in final:

            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    distribution = Counter(
        record.get("intent")
        for record in final
    )

    print("\n" + "=" * 70)
    print("MERGE COMPLETE")
    print("=" * 70)

    print(f"\nFinal records: {len(final)}")
    print(f"Unclear records resolved: {changed}")
    print(
        f"Remaining unclear: "
        f"{distribution.get('unclear', 0)}"
    )

    print("\nFINAL DISTRIBUTION:")
    print("-" * 55)

    for intent, count in sorted(
        distribution.items(),
        key=lambda x: (-x[1], x[0])
    ):

        print(
            f"{intent:35} "
            f"{count:4} "
            f"({count / len(final) * 100:5.1f}%)"
        )

    print("\nOutput:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()