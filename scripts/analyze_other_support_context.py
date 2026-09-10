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

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLASSIFIED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_final.jsonl"
)

CONVERSATIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "amazonhelp_conversations.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "other_support_context_analysis.json"
)

MODEL = "gemini-3.5-flash-lite"
BATCH_SIZE = 10


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [
            json.loads(line)
            for line in f
            if line.strip()
        ]


def load_conversations(path):
    conversations = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            conversation = json.loads(line)
            conversations[str(conversation["conversation_id"])] = conversation
    return conversations


def format_conversation(conversation, target_tweet_id):
    lines = []
    for message in conversation.get("messages", []):
        speaker = (
            "CUSTOMER"
            if message.get("inbound") is True
            else "AMAZON SUPPORT"
        )
        marker = ""
        if str(message.get("tweet_id")) == str(target_tweet_id):
            marker = " <-- TARGET"
        text = message.get("text", "").strip()
        lines.append(f"{speaker}{marker}: {text}")
    return "\n".join(lines)


def analyze_batch_with_retry(client, prompt: str, max_retries: int = 5):
    for attempt in range(1, max_retries + 1):
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
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            if isinstance(data, dict) and "items" in data:
                data = data["items"]
            return data
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                wait_sec = 10 * attempt
                print(f"    [Rate limit 429] Waiting {wait_sec}s (attempt {attempt}/{max_retries})...", flush=True)
                time.sleep(wait_sec)
            else:
                print(f"    [Error] {e} (attempt {attempt}/{max_retries})", flush=True)
                time.sleep(2)
    return []


def main():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. Please check your .env file."
        )

    client = genai.Client(api_key=api_key)

    records = load_jsonl(CLASSIFIED_FILE)
    conversations = load_conversations(CONVERSATIONS_FILE)

    other_support = [
        record
        for record in records
        if record.get("intent") == "other_support"
    ]

    print("=" * 70, flush=True)
    print("OTHER SUPPORT CONTEXT ANALYSIS", flush=True)
    print("=" * 70, flush=True)

    print(f"Other-support messages: {len(other_support):,}", flush=True)

    prepared = []
    for record in other_support:
        conversation = conversations.get(str(record["conversation_id"]))
        if not conversation:
            continue
        prepared.append({
            "conversation_id": record["conversation_id"],
            "tweet_id": record["tweet_id"],
            "text": record["text"],
            "conversation": format_conversation(conversation, record["tweet_id"]),
        })

    print(f"Messages with conversation context: {len(prepared):,}", flush=True)

    all_results = []
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    for start in range(0, len(prepared), BATCH_SIZE):
        batch = prepared[start : start + BATCH_SIZE]
        print(f"[{start + 1}-{start + len(batch)} / {len(prepared)}] Analyzing...", flush=True)

        examples = []
        for i, item in enumerate(batch):
            examples.append(
                f"""
ITEM {i}

FULL CONVERSATION:
{item["conversation"]}

TARGET MESSAGE:
{item["text"]}
"""
            )

        prompt = f"""
You are analyzing Amazon customer-support conversations.

These messages were initially classified as "other_support".

Your task is NOT to force them into the existing taxonomy.

Instead, identify the underlying customer-support issue and group
similar cases into meaningful recurring themes.

For each item:

1. Identify the underlying issue.
2. Suggest a concise theme name.
3. Decide whether the issue fits an existing intent.
4. If it fits an existing intent, name that intent.
5. If it does not fit, suggest a potential NEW intent.
6. Give a short reason.

Existing intents:

- delivery_status_delay
- delivery_not_received
- delivery_carrier_issue
- order_cancellation
- return_issue
- refund_issue
- product_issue
- payment_or_cashback
- pricing_or_promotion
- account_access_security
- prime_or_subscription
- product_service_information
- other_support
- non_support_social

IMPORTANT:

Use the full conversation context.

Do not invent details.

Return ONLY valid JSON array in this format:

[
  {{
    "item": 0,
    "theme": "short theme name",
    "existing_intent": "intent name or null",
    "suggested_new_intent": "intent name or null",
    "reason": "short explanation"
  }}
]

{''.join(examples)}
"""

        results = analyze_batch_with_retry(client, prompt)
        res_map = {r.get("item"): r for r in results if isinstance(r, dict) and "item" in r}

        for idx, source in enumerate(batch):
            res = res_map.get(idx, {})
            all_results.append({
                "conversation_id": source["conversation_id"],
                "tweet_id": source["tweet_id"],
                "text": source["text"],
                "theme": res.get("theme"),
                "existing_intent": res.get("existing_intent"),
                "suggested_new_intent": res.get("suggested_new_intent"),
                "reason": res.get("reason"),
            })

        print("    -> Batch analyzed successfully.", flush=True)
        time.sleep(3.0)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("=" * 70, flush=True)
    print("ANALYSIS COMPLETE", flush=True)
    print("=" * 70, flush=True)
    print(f"Results: {len(all_results):,}", flush=True)
    print(f"Output: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    main()