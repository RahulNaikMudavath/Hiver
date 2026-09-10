import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_final.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "other_support_samples.txt"
)

records = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue

        record = json.loads(line)

        if record.get("intent") == "other_support":
            records.append(record)

print("=" * 70)
print("OTHER SUPPORT INSPECTION")
print("=" * 70)

print(f"Other-support records: {len(records):,}")
print()

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

    for i, record in enumerate(records, start=1):

        text = record.get("text", "").replace("\n", " ")

        out.write(
            f"\n{'=' * 70}\n"
        )

        out.write(
            f"EXAMPLE {i}\n"
        )

        out.write(
            f"Conversation ID: {record.get('conversation_id')}\n"
        )

        out.write(
            f"Tweet ID: {record.get('tweet_id')}\n"
        )

        out.write(
            f"Text: {text}\n"
        )

        out.write(
            f"Reason: {record.get('reason', '')}\n"
        )

print(f"Output: {OUTPUT_FILE}")