import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

from google import genai
from google.genai import types

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path("data/golden/golden_eval_draft.jsonl")
OUTPUT_FILE = Path("data/golden/baseline_llm_predictions.jsonl")

MODEL = "gemini-3.5-flash-lite"

# Rate limit and pacing settings
SLEEP_BETWEEN_CALLS = 0.5   # Base sleep in seconds between successful API calls
MAX_RETRIES = 5             # Maximum retry attempts per example on failure
INITIAL_BACKOFF = 10.0      # Base backoff in seconds for 429 rate limits

# ============================================================
# TAXONOMY (LOCKED 17-CLASS)
# ============================================================

TAXONOMY = {
    "delivery_status_delay":
        "Order is delayed, late, dispatch is delayed, or customer asks about delivery/tracking status.",

    "delivery_not_received":
        "Order is marked delivered or expected to be delivered, but customer says they did not receive it.",

    "delivery_carrier_issue":
        "Problem with courier, driver, delivery attempt, delivery location, safe place, or carrier behavior.",

    "order_cancellation":
        "Customer wants to cancel an order or has an issue specifically involving cancellation.",

    "return_issue":
        "Problem with returning an item, return process, return label, or return request.",

    "refund_issue":
        "Problem involving a refund, refund status, missing refund, or money being returned.",

    "product_issue":
        "Product is damaged, defective, broken, wrong, missing, incomplete, or otherwise has a product-level problem.",

    "payment_or_cashback":
        "Payment, charge, billing transaction, card payment, or cashback issue.",

    "pricing_or_promotion":
        "Price, discount, coupon, promotion, offer, deal, or promotional eligibility issue.",

    "account_access_security":
        "Account access, login, password, security, unauthorized access, or account-related problem.",

    "prime_or_subscription":
        "Amazon Prime, membership, subscription, renewal, or subscription cancellation.",

    "product_service_information":
        "Customer is asking for information, availability, features, specifications, or general product/service details.",

    "customer_support_experience":
        "Complaint about customer support itself: unresponsive agents, failed callbacks, repeated escalations, poor support experience, or inability to get help.",

    "seller_support_issue":
        "Issue specifically concerning seller support, seller account, seller inventory, or seller-side processes.",

    "technical_or_system_issue":
        "Website, application, form, system, technical, or software-related problem.",

    "other_support":
        "A genuine customer-support issue that does not fit any other taxonomy category.",

    "non_support_social":
        "Social, casual, conversational, promotional, or non-support content that is not a genuine customer-support request."
}

TAXONOMY_TEXT = "\n".join(
    f"- {name}: {description}"
    for name, description in TAXONOMY.items()
)

SYSTEM_PROMPT = f"""You are an expert customer-support intent classifier for Amazon customer interactions.

Your task is to classify the customer's issue into EXACTLY ONE intent from the provided taxonomy.

IMPORTANT INSTRUCTIONS:
1. Use the FULL conversation context provided.
2. Do not classify based only on the final target message.
3. Identify the true underlying customer problem or request.
4. If the latest message is a brief follow-up (e.g., "yes", "still waiting", "done", "please help"), use the preceding conversation context to understand what it refers to.
5. Return exactly one label strictly from the TAXONOMY below.
6. Never invent a new label.
7. Do not explain your answer.
8. Output MUST be valid JSON in the format: {{"intent": "one_taxonomy_label"}}

TAXONOMY:
{TAXONOMY_TEXT}
"""

# ============================================================
# PROMPT BUILDER
# ============================================================

def build_prompt(record: dict) -> str:
    """
    Builds the user prompt using only conversation_context and target_text.
    Note: gold_intent is strictly excluded to prevent data leakage.
    """
    context = record.get("conversation_context", "").strip()
    target_text = record.get("target_text", "").strip()

    if not context:
        context = "NO PREVIOUS CONVERSATION CONTEXT AVAILABLE"

    return f"""CONVERSATION CONTEXT:
{context}

TARGET CUSTOMER MESSAGE:
{target_text}

Classify the underlying customer intent for this interaction.
Return JSON strictly: {{"intent": "one_taxonomy_label"}}"""


def parse_intent(response_text: str) -> str:
    """Extracts and validates the predicted intent from the model's response."""
    if not response_text:
        return None

    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    # Try direct parse
    try:
        data = json.loads(cleaned)
        intent = data.get("intent", "").strip()
        if intent in TAXONOMY:
            return intent
    except Exception:
        pass

    # Try substring extract
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1:
        try:
            data = json.loads(cleaned[start:end + 1])
            intent = data.get("intent", "").strip()
            if intent in TAXONOMY:
                return intent
        except Exception:
            pass

    return None


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("=" * 70)
    print("BASELINE 2 — LLM ZERO-SHOT WITH FULL CONVERSATION CONTEXT")
    print("=" * 70)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. Please check your .env file."
        )

    client = genai.Client(api_key=api_key)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    records = []
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"Total dataset records : {len(records)}")
    print(f"Model                  : {MODEL}")
    print(f"Input file             : {INPUT_FILE}")
    print(f"Output file            : {OUTPUT_FILE}")

    # --------------------------------------------------------
    # RESUMPTION SUPPORT: Load already processed tweet IDs
    # --------------------------------------------------------
    processed_ids = set()
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        row = json.loads(line)
                        if "tweet_id" in row and row["tweet_id"]:
                            processed_ids.add(str(row["tweet_id"]))
                    except json.JSONDecodeError:
                        continue

    print(f"Already processed      : {len(processed_ids)}")

    remaining_records = [
        r for r in records
        if str(r.get("target_tweet_id")) not in processed_ids
    ]
    print(f"Remaining to process   : {len(remaining_records)}")
    print("=" * 70)

    if not remaining_records:
        print("\nAll records have already been processed! Nothing left to run.")
        return

    # --------------------------------------------------------
    # PROCESS RECORDS WITH RETRIES AND IMMEDIATE PERSISTENCE
    # --------------------------------------------------------
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("a", encoding="utf-8") as out_f:
        completed_count = len(processed_ids)

        for i, record in enumerate(remaining_records, start=1):
            tweet_id = str(record.get("target_tweet_id"))
            target_text = record.get("target_text", "")
            gold_intent = record.get("gold_intent")
            candidate_id = record.get("candidate_id")

            prompt = build_prompt(record)
            predicted_intent = None
            api_success = False

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = client.models.generate_content(
                        model=MODEL,
                        contents=SYSTEM_PROMPT + "\n\n" + prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.0,
                        ),
                    )

                    predicted = parse_intent(response.text)
                    if predicted:
                        predicted_intent = predicted
                        api_success = True
                        break
                    else:
                        print(f"  [Attempt {attempt}/{MAX_RETRIES}] Invalid model response: {response.text!r}")
                        time.sleep(2.0)

                except Exception as e:
                    err_msg = str(e)
                    is_rate_limit = (
                        "429" in err_msg
                        or "RESOURCE_EXHAUSTED" in err_msg
                        or "quota" in err_msg.lower()
                    )

                    if is_rate_limit:
                        wait_sec = INITIAL_BACKOFF * attempt
                        print(
                            f"  [429 Rate Limit] Attempt {attempt}/{MAX_RETRIES} hit rate limit. "
                            f"Sleeping {wait_sec:.1f}s before retry..."
                        )
                        time.sleep(wait_sec)
                    else:
                        wait_sec = 3.0 * attempt
                        print(
                            f"  [API Error] Attempt {attempt}/{MAX_RETRIES} encountered error: {err_msg}. "
                            f"Waiting {wait_sec:.1f}s..."
                        )
                        time.sleep(wait_sec)

            # CRITICAL REQUIREMENT: Never convert an API or parsing error into 'other_support'!
            if not api_success or not predicted_intent:
                print("\n" + "!" * 70)
                print(f"FATAL ERROR: Failed to classify tweet_id={tweet_id} after {MAX_RETRIES} attempts.")
                print("Exiting cleanly without corrupting the dataset with false predictions.")
                print(f"You can safely re-run this script; it will automatically resume from example #{completed_count + 1}.")
                print("!" * 70)
                sys.exit(1)

            # Save prediction immediately to disk
            output_row = {
                "candidate_id": candidate_id,
                "tweet_id": tweet_id,
                "gold_intent": gold_intent,
                "predicted_intent": predicted_intent,
                "customer_message": target_text,
            }
            out_f.write(json.dumps(output_row, ensure_ascii=False) + "\n")
            out_f.flush()  # Guarantee immediate flush to disk

            completed_count += 1
            print(
                f"[{completed_count:03d}/{len(records)}] "
                f"ID:{tweet_id} | Gold: {gold_intent:<27} -> Pred: {predicted_intent}"
            )

            # Polite pacing between API requests
            time.sleep(SLEEP_BETWEEN_CALLS)

    print()
    print("=" * 70)
    print("CLASSIFICATION COMPLETE")
    print(f"Results successfully saved to: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()