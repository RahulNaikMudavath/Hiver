import json
from pathlib import Path
from collections import Counter, defaultdict


# ============================================================
# CONFIG
# ============================================================

PREDICTIONS_FILE = Path(
    "data/golden/rag_predictions_v2.jsonl"
)

FAILURES_FILE = Path(
    "data/golden/rag_failures_v2_clean.txt"
)

ANALYSIS_FILE = Path(
    "data/golden/rag_failure_analysis_v2.json"
)


# ============================================================
# LOAD PREDICTIONS
# ============================================================

records = []

with open(
    PREDICTIONS_FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:
        line = line.strip()

        if not line:
            continue

        records.append(json.loads(line))


# ============================================================
# FILTER REAL FAILURES
# ============================================================

failures = []

for r in records:

    gold = r.get("gold_intent")
    pred = r.get("predicted_intent")

    # Only genuine classification failures
    if gold != pred:

        failures.append(r)


print("=" * 80)
print("RAG V2 FAILURE ANALYSIS")
print("=" * 80)

print(f"Total examples : {len(records)}")
print(f"Total failures : {len(failures)}")
print(
    f"Accuracy       : "
    f"{(len(records) - len(failures)) / len(records):.2%}"
)


# ============================================================
# CONFUSION PAIRS
# ============================================================

pair_counter = Counter(
    (
        r.get("gold_intent"),
        r.get("predicted_intent")
    )
    for r in failures
)


print("\n" + "=" * 80)
print("TOP CONFUSION PAIRS")
print("=" * 80)

for (gold, pred), count in pair_counter.most_common():

    print(
        f"{count:>3}  "
        f"{gold} -> {pred}"
    )


# ============================================================
# FAILURE RATE BY GOLD INTENT
# ============================================================

gold_total = Counter(
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

failure_rate_data = {}

for intent, total in gold_total.most_common():

    failed = gold_failures[intent]

    rate = failed / total if total else 0

    failure_rate_data[intent] = {
        "total": total,
        "failures": failed,
        "failure_rate": rate
    }

    print(
        f"{intent:<35} "
        f"{failed:>3}/{total:<3} "
        f"({rate:.2%})"
    )


# ============================================================
# RETRIEVAL SCORE ANALYSIS
# ============================================================

correct_scores = []
failure_scores = []

for r in records:

    retrieved = r.get("retrieved_cases", [])

    if not retrieved:
        continue

    top_score = retrieved[0].get(
        "retrieval_score"
    )

    if top_score is None:
        continue

    if r.get("gold_intent") == r.get("predicted_intent"):
        correct_scores.append(float(top_score))
    else:
        failure_scores.append(float(top_score))


def average(values):

    if not values:
        return 0.0

    return sum(values) / len(values)


print("\n" + "=" * 80)
print("RETRIEVAL SCORE ANALYSIS")
print("=" * 80)

print(
    f"Correct predictions : "
    f"{average(correct_scores):.4f}"
)

print(
    f"Failed predictions  : "
    f"{average(failure_scores):.4f}"
)

print(
    f"Difference          : "
    f"{average(correct_scores) - average(failure_scores):.4f}"
)


# ============================================================
# WRITE CLEAN FAILURE FILE
# ============================================================

with open(
    FAILURES_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "RAG V2 — CLEAN FAILURE ANALYSIS\n"
    )

    f.write(
        "=" * 80 + "\n\n"
    )

    for i, r in enumerate(
        failures,
        start=1
    ):

        f.write(
            f"FAILURE {i}\n"
        )

        f.write(
            "-" * 80 + "\n"
        )

        f.write(
            f"Candidate ID : "
            f"{r.get('candidate_id')}\n"
        )

        f.write(
            f"Gold intent  : "
            f"{r.get('gold_intent')}\n"
        )

        f.write(
            f"Prediction   : "
            f"{r.get('predicted_intent')}\n"
        )

        f.write(
            f"Customer     : "
            f"{r.get('target_text') or r.get('customer_message')}\n"
        )

        f.write(
            f"Context      : "
            f"{r.get('conversation_context', '')}\n"
        )

        f.write(
            f"Reply        : "
            f"{r.get('reply', '')}\n"
        )

        f.write(
            "\nRetrieved cases:\n"
        )

        for j, case in enumerate(
            r.get("retrieved_cases", []),
            start=1
        ):

            f.write(
                f"  [{j}] "
                f"intent={case.get('intent')} "
                f"score={case.get('retrieval_score')}\n"
            )

            f.write(
                f"      customer="
                f"{case.get('customer_message', '')}\n"
            )

        f.write("\n\n")


# ============================================================
# SAVE STRUCTURED ANALYSIS
# ============================================================

analysis = {

    "total_examples": len(records),

    "total_failures": len(failures),

    "accuracy": (
        (len(records) - len(failures))
        / len(records)
        if records
        else 0
    ),

    "top_confusion_pairs": [

        {
            "gold_intent": gold,
            "predicted_intent": pred,
            "count": count
        }

        for (gold, pred), count
        in pair_counter.most_common()
    ],

    "failure_rate_by_intent":
        failure_rate_data,

    "retrieval_score_analysis": {

        "correct_mean_top_score":
            average(correct_scores),

        "failure_mean_top_score":
            average(failure_scores),

        "difference":
            average(correct_scores)
            - average(failure_scores)

    }
}


with open(
    ANALYSIS_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        analysis,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 80)
print("FILES CREATED")
print("=" * 80)

print(
    f"Failures : {FAILURES_FILE}"
)

print(
    f"Analysis : {ANALYSIS_FILE}"
)