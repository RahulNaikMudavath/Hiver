import json
import os
import sys
import time
import warnings
from pathlib import Path
from collections import defaultdict
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
    / "intent_discovery_classified_clean.jsonl"
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
    / "unclear_context_reclassified.jsonl"
)


MODEL = "gemini-3.5-flash-lite"
BATCH_SIZE = 10


INTENTS = {
    "delivery_status_delay": "Delivery is late, delayed, missed, or taking too long.",
    "delivery_not_received": "Order is marked delivered but customer did not receive it.",
    "delivery_carrier_issue": "Courier, driver, carrier, delivery location, safe-place, or delivery-attempt issue.",
    "order_cancellation": "Customer wants to cancel an order or has a cancellation problem.",
    "return_issue": "Problem with returning an item, return pickup, return label, eligibility, or return process.",
    "refund_issue": "Refund is missing, delayed, incorrect, or customer asks about refund status/method.",
    "product_issue": "Product is damaged, defective, faulty, wrong, or has a product-quality problem.",
    "payment_or_cashback": "Payment problem, Amazon Pay issue, cashback, voucher, or payment-related credit.",
    "pricing_or_promotion": "Price discrepancy, discount, promotion, offer, or promotional eligibility.",
    "account_access_security": "Login, hacked account, account locked/held, email/password/security issue.",
    "prime_or_subscription": "Amazon Prime membership, Prime benefits, subscription, or Prime-related issue.",
    "product_service_information": "General question about a product/service, availability, content, terminology, or how something works.",
    "other_support": "A genuine customer-support issue that does not fit the categories above.",
    "non_support_social": "Casual/social conversation, praise, jokes, or content that is not a support request.",
    "unclear": "Even with conversation context, there is not enough information to determine the intent."
}


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_conversation_index(path):
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
            marker = "  <-- TARGET MESSAGE"

        text = message.get("text", "").strip()
        lines.append(f"{speaker}{marker}: {text}")
    return "\n".join(lines)


def classify_batch(client, batch, max_retries: int = 5):
    taxonomy = "\n".join(
        f"- {name}: {description}"
        for name, description in INTENTS.items()
    )

    messages_text = []
    for i, item in enumerate(batch):
        messages_text.append(
            f"""
ITEM {i}

Conversation:
{item["conversation_context"]}

Target customer message:
{item["text"]}
"""
        )

    prompt = f"""
You are classifying Amazon customer-support conversations.

The target message was previously labeled "unclear" when viewed
without conversation context.

Now use the FULL conversation to determine the customer's actual
support intent.

Choose EXACTLY ONE label from this taxonomy:

{taxonomy}

Important rules:

1. Use the surrounding conversation to resolve short messages such
   as "No", "Still waiting", "Thanks", etc.
2. Identify the underlying customer issue being discussed.
3. Prefer the most specific applicable intent.
4. Do not invent information that is not supported by the conversation.
5. Use non_support_social only when the conversation is genuinely
   social/non-support.
6. Use other_support when it is clearly customer support but does not
   fit a specific category.
7. Use unclear only if the conversation STILL does not provide enough
   information.

Return a JSON array.

Each element must have:

{{
    "item": 0,
    "intent": "one_taxonomy_label",
    "confidence": 0.0,
    "reason": "short explanation"
}}

{''.join(messages_text)}
"""

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
            # Remove markdown fences if returned
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

    if not CLASSIFIED_FILE.exists():
        raise FileNotFoundError(f"Missing classified file: {CLASSIFIED_FILE}")
    if not CONVERSATIONS_FILE.exists():
        raise FileNotFoundError(f"Missing conversations file: {CONVERSATIONS_FILE}")

    classified = load_jsonl(CLASSIFIED_FILE)
    conversations = build_conversation_index(CONVERSATIONS_FILE)

    unclear = [
        item
        for item in classified
        if item.get("intent") == "unclear"
    ]

    print("=" * 70, flush=True)
    print("CONTEXT-AWARE UNCLEAR RECLASSIFICATION", flush=True)
    print("=" * 70, flush=True)

    print(f"Total classified records: {len(classified):,}", flush=True)
    print(f"Unclear records:          {len(unclear):,}", flush=True)

    prepared = []
    for item in unclear:
        conversation = conversations.get(str(item["conversation_id"]))
        if conversation is None:
            print(f"WARNING: Conversation not found: {item['conversation_id']}", flush=True)
            continue

        context = format_conversation(conversation, item["tweet_id"])
        prepared.append({
            **item,
            "conversation_context": context
        })

    # Resume support
    already_done = set()
    if OUTPUT_FILE.exists():
        existing = load_jsonl(OUTPUT_FILE)
        already_done = {str(item["tweet_id"]) for item in existing}
        print(f"Already reclassified:     {len(already_done):,}", flush=True)

    remaining = [
        item
        for item in prepared
        if str(item["tweet_id"]) not in already_done
    ]

    print(f"Remaining:                 {len(remaining):,}", flush=True)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for start in range(0, len(remaining), BATCH_SIZE):
            batch = remaining[start : start + BATCH_SIZE]
            current_progress = start + len(already_done) + len(batch)
            print(
                f"[{current_progress}/{len(prepared)}] Classifying batch of {len(batch)}...",
                flush=True
            )

            results = classify_batch(client, batch)
            result_map = {r.get("item"): r for r in results if isinstance(r, dict) and "item" in r}

            for idx, source in enumerate(batch):
                result = result_map.get(idx)
                if result:
                    intent = result.get("intent", "unclear")
                    if intent not in INTENTS:
                        intent = "unclear"
                    confidence = float(result.get("confidence", 0.9))
                    reason = result.get("reason", "Context-aware reclassification.")
                else:
                    intent = "unclear"
                    confidence = 0.0
                    reason = "Batch parsing fallback."

                output = {
                    "conversation_id": source["conversation_id"],
                    "tweet_id": source["tweet_id"],
                    "text": source["text"],
                    "previous_intent": source["intent"],
                    "intent": intent,
                    "confidence": confidence,
                    "reason": reason,
                }
                f.write(json.dumps(output, ensure_ascii=False) + "\n")

            f.flush()
            print("    -> Batch saved successfully.", flush=True)
            time.sleep(3.0)

    print("=" * 70, flush=True)
    print("CONTEXT RECLASSIFICATION COMPLETE", flush=True)
    print("=" * 70, flush=True)
    print(f"Output: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    main()