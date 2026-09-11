import json
import re
import sys
from collections import Counter
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


INPUT = Path("data/golden/golden_eval_draft.jsonl")
OUTPUT = Path("data/golden/baseline_keyword_predictions.jsonl")


def normalize(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text


def classify(text):
    text = normalize(text)

    rules = [
        (
            "delivery_not_received",
            [
                "marked delivered",
                "shows delivered",
                "says delivered",
                "delivered but",
                "didn't receive",
                "did not receive",
                "not received",
                "never received",
            ],
        ),

        (
            "delivery_status_delay",
            [
                "where is my order",
                "where's my order",
                "order delayed",
                "delivery delayed",
                "late delivery",
                "still waiting",
                "not arrived yet",
                "when will my order",
                "delivery date",
                "tracking",
                "track my order",
                "dispatch",
            ],
        ),

        (
            "delivery_carrier_issue",
            [
                "delivery driver",
                "delivery person",
                "courier",
                "carrier",
                "driver",
                "delivery attempt",
                "safe place",
                "left with neighbor",
            ],
        ),

        (
            "order_cancellation",
            [
                "cancel my order",
                "cancel order",
                "cancellation",
                "want to cancel",
            ],
        ),

        (
            "return_issue",
            [
                "return my",
                "return an item",
                "return item",
                "return request",
                "send it back",
                "return label",
            ],
        ),

        (
            "refund_issue",
            [
                "refund",
                "money back",
                "refund pending",
                "refund hasn't",
                "refund has not",
            ],
        ),

        (
            "product_issue",
            [
                "damaged",
                "broken",
                "defective",
                "faulty",
                "wrong item",
                "missing item",
                "incomplete order",
                "doesn't work",
                "does not work",
            ],
        ),

        (
            "payment_or_cashback",
            [
                "payment",
                "charged",
                "charge",
                "cashback",
                "credit card",
                "debit card",
                "payment failed",
            ],
        ),

        (
            "pricing_or_promotion",
            [
                "price",
                "pricing",
                "discount",
                "promotion",
                "promo",
                "coupon",
                "offer",
                "deal",
            ],
        ),

        (
            "account_access_security",
            [
                "account",
                "login",
                "log in",
                "sign in",
                "password",
                "locked out",
                "security",
                "hack",
            ],
        ),

        (
            "prime_or_subscription",
            [
                "prime",
                "subscription",
                "membership",
                "renewal",
                "cancel prime",
            ],
        ),

        (
            "product_service_information",
            [
                "is this available",
                "availability",
                "how much",
                "what is",
                "information",
                "details",
                "features",
            ],
        ),

        (
            "customer_support_experience",
            [
                "customer service",
                "customer support",
                "support team",
                "no response",
                "not responding",
                "no one helped",
                "agent",
                "representative",
                "callback",
                "escalate",
                "escalation",
            ],
        ),

        (
            "seller_support_issue",
            [
                "seller",
                "selling",
                "seller support",
                "seller account",
                "inventory",
            ],
        ),

        (
            "technical_or_system_issue",
            [
                "website",
                "app",
                "technical",
                "error",
                "bug",
                "form",
                "system",
                "page isn't working",
                "page is not working",
            ],
        ),
    ]

    for intent, keywords in rules:
        for keyword in keywords:
            if keyword in text:
                return intent

    return "other_support"


def main():
    records = []

    with INPUT.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    predictions = []

    for record in records:
        text = record.get("customer_message") or record.get("target_text") or record.get("text", "")
        tweet_id = record.get("tweet_id") or record.get("target_tweet_id")

        predicted = classify(text)

        predictions.append({
            "candidate_id": record.get("candidate_id"),
            "tweet_id": tweet_id,
            "gold_intent": record.get("gold_intent"),
            "predicted_intent": predicted,
            "customer_message": text,
        })

    with OUTPUT.open("w", encoding="utf-8") as f:
        for row in predictions:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    correct = sum(
        r["gold_intent"] == r["predicted_intent"]
        for r in predictions
    )

    total = len(predictions)

    print("=" * 60)
    print("BASELINE 1 — KEYWORD CLASSIFIER")
    print("=" * 60)
    print(f"Total examples : {total}")
    print(f"Correct        : {correct}")
    print(f"Accuracy       : {correct / total:.4f}")
    print()

    print("Predicted distribution:")
    counts = Counter(r["predicted_intent"] for r in predictions)

    for intent, count in counts.most_common():
        print(f"{intent:35} {count}")

    print()
    print(f"Output written to: {OUTPUT}")


if __name__ == "__main__":
    main()
    