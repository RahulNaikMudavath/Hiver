import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_classified_clean.jsonl"
)

CONTEXT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "unclear_context_reclassified.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_final.jsonl"
)


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f
            if line.strip()
        ]


base_records = load_jsonl(BASE_FILE)
context_records = load_jsonl(CONTEXT_FILE)


# Context-aware classifications indexed by tweet_id.
context_by_id = {
    str(record["tweet_id"]): record
    for record in context_records
}


final_records = []

for record in base_records:

    tweet_id = str(record["tweet_id"])

    if record["intent"] == "unclear" and tweet_id in context_by_id:

        context_record = context_by_id[tweet_id]

        updated = dict(record)

        updated["original_intent"] = record["intent"]
        updated["original_confidence"] = record.get("confidence")

        updated["intent"] = context_record["intent"]
        updated["confidence"] = context_record["confidence"]
        updated["reason"] = context_record["reason"]

        final_records.append(updated)

    else:
        final_records.append(record)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for record in final_records:

        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            ) + "\n"
        )


print("=" * 70)
print("FINAL DISCOVERY DATASET")
print("=" * 70)

print(f"Base records:              {len(base_records):,}")
print(f"Context classifications:   {len(context_records):,}")
print(f"Final records:             {len(final_records):,}")

remaining_unclear = sum(
    1
    for record in final_records
    if record["intent"] == "unclear"
)

print(f"Remaining unclear:         {remaining_unclear:,}")

print()
print(f"Output: {OUTPUT_FILE}")