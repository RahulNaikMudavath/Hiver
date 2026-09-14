import json
import os
import sys
import time
import warnings
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Windows UTF-8 reconfig
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

warnings.filterwarnings("ignore")
load_dotenv()

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path("data/golden/golden_candidates_v2.jsonl")
OUTPUT_CACHE_FILE = Path("data/golden/candidates_annotated_cache.jsonl")
MODEL = "gemini-3.5-flash-lite"
BATCH_SIZE = 10
SLEEP_SECONDS = 1.0

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

TAXONOMY_DEF = """
1. delivery_status_delay: Late, delayed, dispatched late, tracking delay, missed estimated delivery date.
2. delivery_not_received: Order is marked delivered or supposedly delivered, but customer says they did not receive it.
3. delivery_carrier_issue: Courier/driver/carrier behavior, delivery attempt problems, wrong delivery location, unsafe delivery, carrier-specific issue.
4. order_cancellation: Customer wants to cancel, order was automatically cancelled, cancellation problem.
5. return_issue: Customer wants to return an item or has a problem with the return process.
6. refund_issue: Customer is specifically waiting for, requesting, or disputing a refund/money-back resolution.
7. product_issue: Product is damaged, defective, faulty, wrong, incomplete, missing components, unusable, etc.
8. payment_or_cashback: Payment failure, payment method problem, Amazon Pay balance, cashback, charge/payment-related issue.
9. pricing_or_promotion: Price discrepancy, discount, deal, promotion, coupon, promotional offer.
10. account_access_security: Login/access/account lock/security/fraudulent account activity/verification access problems.
11. prime_or_subscription: Prime membership/subscription-specific issue that is NOT primarily a delivery problem.
12. product_service_information: Customer is asking for information about a product/service, compatibility, availability, features, policies, etc.
13. customer_support_experience: Poor/unresponsive customer service, failed callbacks, repeated escalation, support agents not helping, bad support experience.
14. seller_support_issue: Seller/Marketplace seller-specific problem, seller behavior, seller inventory/policy issue.
15. technical_or_system_issue: Website/app/form/system/technical malfunction that is itself the primary issue.
16. other_support: Genuine Amazon support problem that does not reasonably fit any other category.
17. non_support_social: Casual/social/praise/jokes/general commentary that is not actually requesting or reporting a support issue.
"""

PRIORITY_RULES = """
PRIORITY RULES:
A. If Prime is mentioned but the actual problem is a late delivery: use delivery_status_delay, NOT prime_or_subscription.
B. If the target complains specifically about Amazon customer service: use customer_support_experience even if an underlying order issue exists, when the target's primary complaint is the poor support experience.
C. If the actual issue is a product defect/damage/wrong product: use product_issue.
D. If the customer is primarily trying to return the product: use return_issue.
E. If the customer is primarily requesting money back/refund: use refund_issue.
F. If the issue is a website/app/form failure: use technical_or_system_issue.
G. If the problem is specifically caused by a courier/driver/carrier: use delivery_carrier_issue.
H. If an order is marked delivered but the customer says it never arrived: use delivery_not_received.
I. Do not create new labels.
J. Use other_support only when none of the existing labels reasonably fit.
CONTEXT RULE:
Infer underlying customer intent from preceding conversation context for vague target messages (e.g., "Sent!", "Thanks", "Please help", "What now?").
"""

def load_jsonl(path):
    records = []
    if not path.exists():
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def build_prompt(batch):
    examples_str = ""
    for b in batch:
        examples_str += f"""
Candidate ID: {b['candidate_id']}
Previous Suggested Intent: {b.get('suggested_intent')}
Target Customer Message: {b['target_text']}
Full Conversation Context:
{b['conversation_context']}
--------------------------------------------------
"""

    return f"""You are an expert customer-support annotator for Amazon Twitter customer support conversations.
You must annotate each candidate with its true underlying customer intent according to the LOCKED TAXONOMY and PRIORITY RULES.

LOCKED TAXONOMY:
{TAXONOMY_DEF}

{PRIORITY_RULES}

For each candidate:
1. Carefully read the Target Customer Message and the Full Conversation Context.
2. Select exactly ONE gold_intent from the 17 taxonomy labels.
3. Provide a concise annotation_notes (1-2 sentences) explaining your decision (especially noting context signals or why suggested_intent is overridden if applicable).
4. Set is_ambiguous (boolean): true if the case is borderline or ambiguous, false otherwise.

Return ONLY a JSON array with exactly {len(batch)} objects matching this schema:
[
  {{
    "candidate_id": <int>,
    "gold_intent": "<one of the 17 valid intents>",
    "annotation_notes": "<concise explanation>",
    "is_ambiguous": <true or false>
  }},
  ...
]

Candidates to annotate:
{examples_str}
"""

def main():
    print("=" * 70)
    print("ANNOTATING GOLDEN CANDIDATES WITH GEMINI")
    print("=" * 70)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)

    candidates = load_jsonl(INPUT_FILE)
    print(f"Loaded {len(candidates)} candidates from {INPUT_FILE}")

    # Resume capability
    existing_records = load_jsonl(OUTPUT_CACHE_FILE)
    done_ids = {r["candidate_id"] for r in existing_records}
    print(f"Already annotated: {len(done_ids)}")

    remaining = [c for c in candidates if c["candidate_id"] not in done_ids]
    print(f"Remaining to annotate: {len(remaining)}")

    if not remaining:
        print("All candidates are already annotated!")
        return

    total_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE

    for b_idx in range(total_batches):
        batch = remaining[b_idx * BATCH_SIZE : (b_idx + 1) * BATCH_SIZE]
        print(f"\n[Batch {b_idx + 1}/{total_batches}] Annotating candidate IDs: {[c['candidate_id'] for c in batch]}")

        prompt = build_prompt(batch)
        success = False

        for attempt in range(4):
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
                    lines = text.splitlines()
                    lines = lines[1:]
                    if lines and lines[-1].strip().startswith("```"):
                        lines = lines[:-1]
                    text = "\n".join(lines).strip()

                parsed = json.loads(text)
                if len(parsed) != len(batch):
                    raise ValueError(f"Expected {len(batch)} items, got {len(parsed)}")

                # Validate labels
                for item in parsed:
                    if item["gold_intent"] not in INTENTS:
                        raise ValueError(f"Invalid intent returned: {item['gold_intent']}")

                # Save immediately to cache file
                with open(OUTPUT_CACHE_FILE, "a", encoding="utf-8") as out:
                    for i, c in enumerate(batch):
                        ann = parsed[i]
                        rec = dict(c)
                        rec["gold_intent"] = ann["gold_intent"]
                        rec["annotation_notes"] = ann.get("annotation_notes", "")
                        rec["is_ambiguous"] = ann.get("is_ambiguous", False)
                        out.write(json.dumps(rec, ensure_ascii=False) + "\n")

                success = True
                print(f"  Batch {b_idx + 1} succeeded.")
                time.sleep(SLEEP_SECONDS)
                break

            except Exception as e:
                print(f"  Attempt {attempt + 1}/4 failed: {e}")
                time.sleep(4 * (attempt + 1))

        if not success:
            raise RuntimeError(f"Batch {b_idx + 1} failed after all retries.")

    print("\nAnnotation completed. Cache saved to:", OUTPUT_CACHE_FILE)

if __name__ == "__main__":
    main()
