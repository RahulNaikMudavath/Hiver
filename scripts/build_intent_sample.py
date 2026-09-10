import json
import random
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "amazonhelp_conversations.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_sample.jsonl"
)

SAMPLE_SIZE = 1000

random.seed(42)

# --------------------------------------------------
# Load customer messages
# --------------------------------------------------

customer_messages = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in f:

        conversation = json.loads(line)

        for message in conversation.get("messages", []):

            if message.get("inbound") is not True:
                continue

            text = message.get("text", "").strip()

            if not text:
                continue

            customer_messages.append({
                "conversation_id":
                    conversation.get("conversation_id"),

                "tweet_id":
                    message.get("tweet_id"),

                "text": text,

                "created_at":
                    message.get("created_at")
            })


print(f"Customer messages available: {len(customer_messages):,}")

# --------------------------------------------------
# Sample
# --------------------------------------------------

sample_size = min(
    SAMPLE_SIZE,
    len(customer_messages)
)

sample = random.sample(
    customer_messages,
    sample_size
)

# --------------------------------------------------
# Save
# --------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    for item in sample:

        f.write(
            json.dumps(
                item,
                ensure_ascii=False
            ) + "\n"
        )

print("=" * 70)
print("INTENT DISCOVERY SAMPLE")
print("=" * 70)

print(f"Sample size: {sample_size:,}")
print(f"Output:      {OUTPUT_FILE}")