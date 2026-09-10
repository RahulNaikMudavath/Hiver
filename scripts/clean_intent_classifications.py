import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_classified.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_classified_clean.jsonl"
)


records_by_tweet_id = {}

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue

        record = json.loads(line)

        tweet_id = record["tweet_id"]

        # Keep the first classification for each unique tweet.
        if tweet_id not in records_by_tweet_id:
            records_by_tweet_id[tweet_id] = record


clean_records = list(records_by_tweet_id.values())


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for record in clean_records:
        f.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )


print("=" * 70)
print("CLEANED INTENT CLASSIFICATIONS")
print("=" * 70)

print(f"Original records: {sum(1 for _ in open(INPUT_FILE, encoding='utf-8')):,}")
print(f"Unique records:   {len(clean_records):,}")
print(f"Removed duplicates: {1437 - len(clean_records):,}")

print()
print(f"Output: {OUTPUT_FILE}")