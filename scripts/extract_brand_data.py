import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "conversations.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "amazonhelp_conversations.jsonl"
)

BRAND = "AmazonHelp"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

count = 0

with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

    for line in infile:

        conversation = json.loads(line)

        if BRAND not in conversation.get("brands", []):
            continue

        outfile.write(
            json.dumps(
                conversation,
                ensure_ascii=False
            ) + "\n"
        )

        count += 1

print("=" * 70)
print("AMAZONHELP EXTRACTION")
print("=" * 70)

print(f"Brand:         {BRAND}")
print(f"Conversations: {count:,}")
print(f"Output:        {OUTPUT_FILE}")