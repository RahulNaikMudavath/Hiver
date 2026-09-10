import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

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


SYSTEM_PROMPT = """
You are classifying Amazon customer-support messages.

Your task is to assign EXACTLY ONE intent to each customer message.

Use the taxonomy provided below.

Important rules:
1. Choose the most specific applicable intent.
2. Do not infer facts that are not present in the message.
3. If the message is casual/social and not a support request, use non_support_social.
4. If it is clearly a support issue but none of the specific categories fit, use other_support.
5. If there is genuinely insufficient information, use unclear.
6. Return ONLY valid JSON.
"""


taxonomy_text = "\n".join(
    f"- {name}: {description}"
    for name, description in INTENTS.items()
)


def classify_message_gemini(client, text: str) -> dict:
    from google.genai import types

    user_prompt = f"""{SYSTEM_PROMPT}

Taxonomy:
{taxonomy_text}

Customer message:
"{text}"

Return JSON in exactly this format:
{{
  "intent": "one_taxonomy_label",
  "confidence": 0.0,
  "reason": "short explanation"
}}
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )
    result = json.loads(response.text)
    if result.get("intent") not in INTENTS:
        result["intent"] = "unclear"
    return result


def classify_message_openai(client, text: str) -> dict:
    user_prompt = f"""
Taxonomy:

{taxonomy_text}

Customer message:

{text}

Return JSON in exactly this format:

{{
  "intent": "one_taxonomy_label",
  "confidence": 0.0,
  "reason": "short explanation"
}}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    result = json.loads(response.choices[0].message.content)
    if result.get("intent") not in INTENTS:
        result["intent"] = "unclear"
    return result


def main():
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    provider = None
    client = None

    if gemini_key:
        from google import genai
        client = genai.Client(api_key=gemini_key)
        provider = "gemini"
        print("Using Gemini API (gemini-3.6-flash) for intent classification.")
    elif openai_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        provider = "openai"
        print("Using OpenAI API (gpt-4o-mini) for intent classification.")
    else:
        raise RuntimeError(
            "Neither GEMINI_API_KEY nor OPENAI_API_KEY is set in .env. Please configure at least one."
        )

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found at {INPUT_FILE}. Run build_intent_sample.py first.")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        messages = [json.loads(line) for line in f]

    print(f"Messages loaded: {len(messages):,}")

    results = []

    for i, item in enumerate(messages, start=1):
        print(f"[{i}/{len(messages)}] Classifying...")

        try:
            if provider == "gemini":
                classification = classify_message_gemini(client, item["text"])
            else:
                classification = classify_message_openai(client, item["text"])

            result = {
                **item,
                **classification,
            }
            results.append(result)
            print(f"    -> {classification['intent']} ({classification.get('confidence', 1.0)})")

        except Exception as e:
            print(f"    ERROR: {e}")
            result = {
                **item,
                "intent": "unclear",
                "confidence": 0.0,
                "reason": f"Classification error: {e}",
            }
            results.append(result)

        # Small pause between calls
        time.sleep(0.05)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in results:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("=" * 70)
    print("CLASSIFICATION COMPLETE")
    print("=" * 70)
    print(f"Messages: {len(results):,}")
    print(f"Output:   {OUTPUT_FILE}")


if __name__ == "__main__":
    main()