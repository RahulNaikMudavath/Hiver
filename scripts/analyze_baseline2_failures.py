import json
from collections import Counter, defaultdict
from pathlib import Path

INPUT_FILE = Path("data/golden/baseline_llm_predictions.jsonl")
OUTPUT_JSON = Path("data/golden/baseline2_failure_analysis.json")
OUTPUT_TXT = Path("data/golden/baseline2_failures.txt")


def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            records.append(json.loads(line))

    return records


records = load_jsonl(INPUT_FILE)

failures = [
    r for r in records
    if r.get("gold_intent") != r.get("predicted_intent")
]

print("=" * 80)
print("BASELINE 2 — FAILURE ANALYSIS")
print("=" * 80)

print(f"Total examples : {len(records)}")
print(f"Correct       : {len(records) - len(failures)}")
print(f"Failures      : {len(failures)}")

# ---------------------------------------------------------
# 1. Overall prediction distribution
# ---------------------------------------------------------

predicted_counts = Counter(
    r.get("predicted_intent")
    for r in records
)

print("\n" + "=" * 80)
print("PREDICTED INTENT DISTRIBUTION")
print("=" * 80)

for intent, count in predicted_counts.most_common():
    print(f"{intent:35s} {count:4d}")

# ---------------------------------------------------------
# 2. Most common gold -> predicted confusions
# ---------------------------------------------------------

confusions = Counter(
    (r.get("gold_intent"), r.get("predicted_intent"))
    for r in failures
)

print("\n" + "=" * 80)
print("TOP CONFUSION PAIRS")
print("=" * 80)

for (gold, pred), count in confusions.most_common(20):
    print(f"{gold:35s} -> {pred:35s} : {count}")

# ---------------------------------------------------------
# 3. How often other_support swallowed real intents
# ---------------------------------------------------------

other_support_failures = [
    r for r in failures
    if r.get("predicted_intent") == "other_support"
    and r.get("gold_intent") != "other_support"
]

print("\n" + "=" * 80)
print("OTHER_SUPPORT OVER-PREDICTION")
print("=" * 80)

print(
    f"Wrong predictions to other_support : "
    f"{len(other_support_failures)}"
)

swallowed = Counter(
    r.get("gold_intent")
    for r in other_support_failures
)

for intent, count in swallowed.most_common():
    print(f"{intent:35s} -> other_support : {count}")

# ---------------------------------------------------------
# 4. Failure rate by gold intent
# ---------------------------------------------------------

gold_counts = Counter(
    r.get("gold_intent")
    for r in records
)

gold_failures = Counter(
    r.get("gold_intent")
    for r in failures
)

print("\n" + "=" * 80)
print("FAILURE RATE BY GOLD INTENT")
print("=" * 80)

failure_rates = []

for intent, total in gold_counts.items():

    failed = gold_failures[intent]
    rate = failed / total

    failure_rates.append(
        (intent, total, failed, rate)
    )

for intent, total, failed, rate in sorted(
    failure_rates,
    key=lambda x: x[3],
    reverse=True
):

    print(
        f"{intent:35s} "
        f"total={total:3d} "
        f"failed={failed:3d} "
        f"failure_rate={rate:.1%}"
    )

# ---------------------------------------------------------
# 5. Save detailed failures
# ---------------------------------------------------------

failure_records = []

for r in failures:

    failure_records.append({
        "candidate_id": r.get("candidate_id"),
        "conversation_id": r.get("conversation_id"),
        "target_tweet_id": r.get("target_tweet_id"),
        "target_text": r.get("target_text"),
        "conversation_context": r.get("conversation_context"),
        "gold_intent": r.get("gold_intent"),
        "predicted_intent": r.get("predicted_intent"),
        "annotation_notes": r.get("annotation_notes"),
    })


analysis = {
    "total_examples": len(records),
    "correct": len(records) - len(failures),
    "failures": len(failures),
    "predicted_distribution": dict(predicted_counts),
    "top_confusions": [
        {
            "gold_intent": gold,
            "predicted_intent": pred,
            "count": count
        }
        for (gold, pred), count in confusions.most_common(20)
    ],
    "other_support_overprediction": {
        "count": len(other_support_failures),
        "by_gold_intent": dict(swallowed)
    },
    "failure_rate_by_intent": [
        {
            "intent": intent,
            "total": total,
            "failed": failed,
            "failure_rate": rate
        }
        for intent, total, failed, rate in sorted(
            failure_rates,
            key=lambda x: x[3],
            reverse=True
        )
    ],
    "failures": failure_records
}

OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        analysis,
        f,
        indent=2,
        ensure_ascii=False
    )


# ---------------------------------------------------------
# Human-readable failure file
# ---------------------------------------------------------

with open(
    OUTPUT_TXT,
    "w",
    encoding="utf-8"
) as f:

    f.write("BASELINE 2 — MISCLASSIFIED EXAMPLES\n")
    f.write("=" * 80 + "\n\n")

    for i, r in enumerate(failures, 1):

        f.write(f"FAILURE #{i}\n")
        f.write("-" * 80 + "\n")

        f.write(
            f"Gold      : {r.get('gold_intent')}\n"
        )

        f.write(
            f"Predicted : {r.get('predicted_intent')}\n"
        )

        f.write(
            f"Tweet ID  : {r.get('target_tweet_id')}\n"
        )

        f.write(
            f"Message   : {r.get('target_text')}\n"
        )

        f.write(
            f"Context   : {r.get('conversation_context')}\n"
        )

        notes = r.get("annotation_notes")

        if notes:
            f.write(
                f"Notes     : {notes}\n"
            )

        f.write("\n")


print("\n" + "=" * 80)
print("FILES CREATED")
print("=" * 80)

print(f"JSON : {OUTPUT_JSON}")
print(f"TXT  : {OUTPUT_TXT}")

print("\n🔥 Baseline 2 failure analysis complete!")