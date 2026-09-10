import json
import os
import sys
import time
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Reconfigure stdout/stderr for Unicode/emoji support on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Suppress harmless SDK warnings
warnings.filterwarnings("ignore")

# Load environment variables from .env
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_sample.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_discovery_classified.jsonl"
)

BATCH_SIZE = 10  # Group messages per API call to minimize request count and avoid rate limits

INTENTS = {
    "delivery_status_delay": "Delivery is late, delayed, missed, or taking too long.",
    "delivery_not_received": "Order is marked delivered or supposedly delivered, but customer did not receive it.",
    "delivery_carrier_issue": "Issue specifically involving courier/driver/carrier behavior, delivery location, safe place, delivery attempt, or carrier handling.",
    "order_cancellation": "Customer wants to cancel an order or has a cancellation problem.",
    "return_issue": "Problem with returning an item, return eligibility, return pickup, return label, or return process.",
    "refund_issue": "Refund is missing, delayed, incorrect, or customer asks about refund method/status.",
    "product_issue": "Product is damaged, defective, faulty, wrong, missing parts, or has a product-quality problem.",
    "payment_or_cashback": "Payment problem, Amazon Pay issue, cashback, voucher, payment failure, or payment-related credit.",
    "pricing_or_promotion": "Wrong price, price difference, discount, promotion, offer, or promotional eligibility.",
    "account_access_security": "Cannot log in, account hacked, account compromised, account locked/held, email/password/security issue.",
    "prime_or_subscription": "Amazon Prime membership, Prime benefits, Prime delivery eligibility, Prime subscription, or subscription-related issue.",
    "product_service_information": "General question about a product/service, availability, terminology, content availability, delivery eligibility, or how something works.",
    "other_support": "A genuine Amazon customer-support issue that does not fit the categories above.",
    "non_support_social": "Casual/social conversation, praise, jokes, entertainment chatter, or content that is not really a customer-support request.",
    "unclear": "Not enough information to determine the intent."
}

SYSTEM_PROMPT = """You are an expert AI classifying Amazon customer-support messages into an intent taxonomy.

Allowed Intents:
{taxonomy_text}

Guidelines:
1. Assign EXACTLY ONE intent to each message based strictly on the text.
2. If casual/social or praise with no support request, use non_support_social.
3. If support issue but no specific category fits, use other_support.
4. If truly insufficient context, use unclear.
5. Return a valid JSON array of objects with keys: "tweet_id", "intent", "confidence", "reason".
"""

taxonomy_text = "\n".join(
    f"- {name}: {description}"
    for name, description in INTENTS.items()
)


def classify_batch_gemini(client, batch_items: list, max_retries: int = 5) -> list:
    from google.genai import types

    batch_prompt_lines = ["Classify the following customer messages:"]
    for item in batch_items:
        clean_text = item["text"].replace("\n", " ").strip()
        batch_prompt_lines.append(f"- [tweet_id: {item['tweet_id']}] \"{clean_text}\"")

    prompt = (
        SYSTEM_PROMPT.format(taxonomy_text=taxonomy_text)
        + "\n\n"
        + "\n".join(batch_prompt_lines)
        + "\n\nReturn JSON array:"
        + "\n[{\"tweet_id\": \"...\", \"intent\": \"...\", \"confidence\": 0.95, \"reason\": \"...\"}]"
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            data = json.loads(response.text)
            if isinstance(data, dict) and "classifications" in data:
                data = data["classifications"]
            if not isinstance(data, list):
                data = [data]
            return data

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                wait_sec = 10 * attempt
                print(f"    [Rate limit 429] Backing off for {wait_sec}s (attempt {attempt}/{max_retries})...", flush=True)
                time.sleep(wait_sec)
            else:
                print(f"    [API Error] {e} (attempt {attempt}/{max_retries})", flush=True)
                time.sleep(2)

    return []


def main():
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not gemini_key and not openai_key:
        raise RuntimeError("Neither GEMINI_API_KEY nor OPENAI_API_KEY is configured in .env.")

    from google import genai
    client = genai.Client(api_key=gemini_key)
    print("Using Gemini API (gemini-3.5-flash-lite) with batching for high throughput.", flush=True)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found at {INPUT_FILE}.")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        messages = [json.loads(line) for line in f]

    print(f"Total sample messages loaded: {len(messages):,}", flush=True)

    # Resume capability: keep track of already classified tweet_ids
    processed_ids = set()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        rec = json.loads(line)
                        if rec.get("intent") != "unclear" or "Classification error:" not in rec.get("reason", ""):
                            processed_ids.add(str(rec.get("tweet_id")))
                    except Exception:
                        pass

    remaining_messages = [m for m in messages if str(m.get("tweet_id")) not in processed_ids]
    print(f"Already classified: {len(processed_ids):,} | Remaining to classify: {len(remaining_messages):,}", flush=True)

    if not remaining_messages:
        print("All messages have already been successfully classified!", flush=True)
        return

    # Process in batches
    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for batch_idx in range(0, len(remaining_messages), BATCH_SIZE):
            batch = remaining_messages[batch_idx : batch_idx + BATCH_SIZE]
            current_num = len(processed_ids) + len(batch)
            print(f"[{current_num}/{len(messages)}] Classifying batch of {len(batch)} messages...", flush=True)

            predictions = classify_batch_gemini(client, batch)
            pred_map = {str(p.get("tweet_id")): p for p in predictions if isinstance(p, dict)}

            for item in batch:
                t_id = str(item.get("tweet_id"))
                pred = pred_map.get(t_id)

                if pred:
                    intent = pred.get("intent", "unclear")
                    if intent not in INTENTS:
                        intent = "unclear"
                    confidence = float(pred.get("confidence", 0.9))
                    reason = pred.get("reason", "Classified by Gemini model.")
                else:
                    intent = "unclear"
                    confidence = 0.0
                    reason = "Batch parsing fallback."

                record = {
                    **item,
                    "intent": intent,
                    "confidence": confidence,
                    "reason": reason,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                processed_ids.add(t_id)

            out.flush()
            print(f"    -> Successfully classified and saved batch ({len(batch)} records).", flush=True)

            # Small pause between batches
            time.sleep(3.0)

    print("=" * 70, flush=True)
    print("CLASSIFICATION COMPLETE", flush=True)
    print("=" * 70, flush=True)
    print(f"Total records saved: {len(processed_ids):,}")
    print(f"Output path: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()