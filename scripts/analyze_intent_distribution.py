import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_final.jsonl"
)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    records = [json.loads(line) for line in f if line.strip()]

counts = Counter(record["intent"] for record in records)

print("=" * 70)
print("INTENT DISCOVERY DISTRIBUTION")
print("=" * 70)

print(f"Total classified messages: {len(records):,}")
print()

for intent, count in counts.most_common():
    percentage = count / len(records) * 100
    print(f"{intent:<30} {count:>5}  ({percentage:>5.1f}%)")

print()
print("=" * 70)
print("TOTAL")
print("=" * 70)
print(sum(counts.values()))