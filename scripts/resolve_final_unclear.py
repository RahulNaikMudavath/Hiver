import json
import os
import sys
import time
import warnings
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Reconfigure console encoding for Windows emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Suppress harmless warnings
warnings.filterwarnings("ignore")

# Load environment variables from .env
load_dotenv()


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/processed/intent_discovery_taxonomy_final.jsonl"
)

CONVERSATIONS_FILE = Path(
    "data/processed/amazonhelp_conversations.jsonl"
)

OUTPUT_FILE = Path(
    "data/processed/final_unclear_resolved.jsonl"
)

MODEL = "gemini-3.5-flash-lite"


# ============================================================
# FINAL TAXONOMY
# ============================================================

INTENTS = [
    "delivery_status_delay",
    "delivery_not_received",
    "delivery_carrier_issue",
    "order_cancellation",
    "return_issue",
    "refund_issue",
    "product_issue",
    "payment_or_cashback",
    "pricing_or_promotion",
    "account_access_security",
    "prime_or_subscription",
    "product_service_information",
    "customer_support_experience",
    "seller_support_issue",
    "technical_or_system_issue",
    "other_support",
    "non_support_social",
]


# ============================================================
# LOAD JSONL
# ============================================================

def load_jsonl(path):

    records = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


# ============================================================
# CONVERSATION LOOKUP
# ============================================================

def build_lookup(conversations):

    lookup = {}

    for conversation in conversations:

        cid = str(
            conversation.get("conversation_id")
        )

        lookup[cid] = conversation

    return lookup


# ============================================================
# FORMAT CONTEXT
# ============================================================

def format_context(conversation):

    if not conversation:
        return "NO CONVERSATION CONTEXT AVAILABLE"

    lines = []

    for message in conversation.get("messages", []):

        speaker = (
            "CUSTOMER"
            if message.get("inbound") is True
            else "AGENT"
        )

        text = message.get("text", "")

        lines.append(
            f"{speaker}: {text}"
        )

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("RESOLVING FINAL UNCLEAR EXAMPLES")
    print("=" * 70)

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    client = genai.Client(
        api_key=api_key
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    records = load_jsonl(INPUT_FILE)

    conversations = load_jsonl(
        CONVERSATIONS_FILE
    )

    conversation_lookup = build_lookup(
        conversations
    )

    unclear = [
        record
        for record in records
        if record.get("intent") == "unclear"
    ]

    print(
        f"\nUnclear examples: {len(unclear)}"
    )

    if not unclear:

        print("\nNo unclear examples remain.")
        return

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    examples = []

    for index, record in enumerate(
        unclear,
        start=1
    ):

        cid = str(
            record.get("conversation_id")
        )

        conversation = conversation_lookup.get(
            cid
        )

        examples.append(
            f"""
================ EXAMPLE {index} ================

Conversation ID:
{cid}

Tweet ID:
{record.get("tweet_id")}

TARGET CUSTOMER MESSAGE:
{record.get("text", "")}

FULL CONVERSATION:
{format_context(conversation)}
"""
        )

    taxonomy = "\n".join(
        f"- {intent}"
        for intent in INTENTS
    )

    prompt = f"""
You are performing final intent annotation for an
Amazon customer-support evaluation dataset.

There are a few examples that were previously labeled
"unclear". You MUST resolve each one into exactly ONE
of the following final taxonomy labels.

FINAL TAXONOMY:

{taxonomy}

Use the FULL conversation context.

Important:

- Determine the underlying customer issue.
- Do not classify based only on the target message.
- If the customer is complaining about Amazon support itself,
  use customer_support_experience.
- If the issue concerns delivery delay, use
  delivery_status_delay.
- If the order was marked delivered but not received, use
  delivery_not_received.
- If the courier/driver/carrier is the issue, use
  delivery_carrier_issue.
- If the website/app/form/system is malfunctioning, use
  technical_or_system_issue.
- If it is seller-specific, use seller_support_issue.
- Use other_support only when no more specific category fits.
- Do NOT return "unclear".
- Choose exactly one label per example.

Return ONLY valid JSON:

[
  {{
    "index": 1,
    "intent": "label"
  }},
  {{
    "index": 2,
    "intent": "label"
  }}
]

Examples:

{"".join(examples)}
"""

    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    print("\nSending examples for final resolution...")

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )

            text = response.text.strip()

            # Remove markdown fences
            if text.startswith("```"):

                lines = text.splitlines()

                lines = lines[1:]

                if (
                    lines
                    and lines[-1].strip().startswith("```")
                ):
                    lines = lines[:-1]

                text = "\n".join(lines).strip()

            predictions = json.loads(text)

            if len(predictions) != len(unclear):

                raise ValueError(
                    f"Expected {len(unclear)} predictions, "
                    f"got {len(predictions)}"
                )

            results = []

            for i, record in enumerate(unclear):

                intent = predictions[i].get(
                    "intent"
                )

                if intent not in INTENTS:

                    raise ValueError(
                        f"Invalid intent returned: {intent}"
                    )

                results.append(
                    {
                        "tweet_id":
                            record.get("tweet_id"),

                        "conversation_id":
                            record.get("conversation_id"),

                        "text":
                            record.get("text"),

                        "old_intent":
                            "unclear",

                        "new_intent":
                            intent,

                        "label_source":
                            "final_context_resolution"
                    }
                )

            break

        except Exception as e:

            print(
                f"Attempt {attempt + 1}/3 failed: {e}"
            )

            if attempt == 2:
                raise

            time.sleep(3)

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

        for result in results:

            f.write(
                json.dumps(
                    result,
                    ensure_ascii=False
                ) + "\n"
            )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("UNCLEAR RESOLUTION COMPLETE")
    print("=" * 70)

    for result in results:

        print(
            f"\nTweet ID: {result['tweet_id']}"
        )

        print(
            f"Old intent: {result['old_intent']}"
        )

        print(
            f"New intent: {result['new_intent']}"
        )

        print(
            f"Text: {result['text']}"
        )

    print("\nOutput:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()