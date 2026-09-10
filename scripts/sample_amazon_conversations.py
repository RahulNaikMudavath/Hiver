import json
import random
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
    / "amazonhelp_samples.txt"
)

SAMPLE_SIZE = 100

random.seed(42)

# --------------------------------------------------
# Load conversations
# --------------------------------------------------

conversations = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in f:
        conversations.append(json.loads(line))

print(f"Loaded {len(conversations):,} conversations")

# --------------------------------------------------
# Sample
# --------------------------------------------------

sample = random.sample(
    conversations,
    min(SAMPLE_SIZE, len(conversations))
)

# --------------------------------------------------
# Save human-readable examples
# --------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

    for i, conversation in enumerate(sample, start=1):

        out.write("\n")
        out.write("=" * 90 + "\n")
        out.write(f"CONVERSATION {i}\n")
        out.write("=" * 90 + "\n")

        out.write(
            f"Conversation ID: "
            f"{conversation.get('conversation_id')}\n"
        )

        out.write(
            f"Turns: "
            f"{conversation.get('num_turns')}\n"
        )

        out.write(
            f"Brands: "
            f"{', '.join(conversation.get('brands', []))}\n\n"
        )

        for message in conversation.get("messages", []):

            speaker = (
                "CUSTOMER"
                if message.get("inbound") is True
                else "AMAZONHELP"
            )

            text = message.get("text", "")

            out.write(f"[{speaker}]\n")
            out.write(f"{text}\n\n")

print("\n" + "=" * 90)
print("DONE")
print("=" * 90)

print(f"Sample size: {len(sample)}")
print(f"Output:      {OUTPUT_FILE}")