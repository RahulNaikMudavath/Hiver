import json
import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# ============================================================
# CONFIG
# ============================================================

GOLDEN_FILE = Path("data/golden/golden_eval_draft.jsonl")
OUTPUT_FILE = Path("data/golden/rag_predictions.jsonl")

# Gemini free-tier safety margin.
# ~14 requests/minute instead of hitting the 15 RPM limit.
REQUEST_DELAY_SECONDS = 4.5

INVALID_LABEL = "__INVALID__"

ALLOWED_INTENTS = {
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
}


# ============================================================
# JSONL HELPERS
# ============================================================

def load_jsonl(path):
    rows = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                rows.append(json.loads(line))

    return rows


def append_jsonl(path, row):
    with path.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                row,
                ensure_ascii=False
            ) + "\n"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    if not GOLDEN_FILE.exists():
        raise FileNotFoundError(
            f"Golden set not found:\n{GOLDEN_FILE}"
        )

    golden = load_jsonl(GOLDEN_FILE)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Resume support
    # --------------------------------------------------------

    existing = []

    if OUTPUT_FILE.exists():
        existing = load_jsonl(OUTPUT_FILE)

    completed_ids = {
        row.get("candidate_id")
        for row in existing
        if row.get("candidate_id") is not None
    }

    print("=" * 80)
    print("RAG AGENT — 200-EXAMPLE EVALUATION")
    print("=" * 80)

    print(f"Golden examples : {len(golden)}")
    print(f"Already done    : {len(completed_ids)}")
    print(
        f"Remaining       : "
        f"{len(golden) - len(completed_ids)}"
    )

    print()

    # --------------------------------------------------------
    # Import RAG agent
    # --------------------------------------------------------

    print("Loading RAG agent...")

    from rag_agent import run_agent

    print("RAG agent loaded.")
    print()

    # --------------------------------------------------------
    # Run evaluation
    # --------------------------------------------------------

    for i, row in enumerate(golden, start=1):

        candidate_id = row.get("candidate_id")

        if candidate_id in completed_ids:
            continue

        customer_message = row.get(
            "target_text",
            ""
        )

        conversation_context = row.get(
            "conversation_context",
            ""
        )

        gold_intent = row.get(
            "gold_intent"
        )

        print("-" * 80)
        print(
            f"Example {i}/{len(golden)}"
        )
        print(
            f"Candidate ID : {candidate_id}"
        )
        print(
            f"Gold intent  : {gold_intent}"
        )
        print(
            f"Customer     : "
            f"{customer_message[:200]}"
        )

        started = time.time()

        try:

            result = run_agent(
                customer_message,
                conversation_context
            )

            predicted_intent = result.get(
                "predicted_intent"
            )

            # ------------------------------------------------
            # Never silently convert invalid output to
            # other_support.
            # ------------------------------------------------

            if predicted_intent not in ALLOWED_INTENTS:

                predicted_intent = INVALID_LABEL

            output_row = {

                "candidate_id":
                    candidate_id,

                "conversation_id":
                    row.get("conversation_id"),

                "target_tweet_id":
                    row.get("target_tweet_id"),

                "target_text":
                    customer_message,

                "conversation_context":
                    conversation_context,

                "gold_intent":
                    gold_intent,

                "predicted_intent":
                    predicted_intent,

                "reply":
                    result.get(
                        "reply",
                        ""
                    ),

                "escalate":
                    result.get(
                        "escalate"
                    ),

                "escalation_reason":
                    result.get(
                        "escalation_reason",
                        ""
                    ),

                "retrieved_cases":
                    result.get(
                        "retrieved_cases",
                        []
                    ),

                "runtime_seconds":
                    round(
                        time.time() - started,
                        3
                    )
            }

            append_jsonl(
                OUTPUT_FILE,
                output_row
            )

            if predicted_intent == gold_intent:

                print(
                    f"Prediction : "
                    f"{predicted_intent} [CORRECT]"
                )

            else:

                print(
                    f"Prediction : "
                    f"{predicted_intent} [WRONG]"
                )

        except Exception as exc:

            # ------------------------------------------------
            # Save failures explicitly.
            # ------------------------------------------------

            output_row = {

                "candidate_id":
                    candidate_id,

                "conversation_id":
                    row.get("conversation_id"),

                "target_tweet_id":
                    row.get("target_tweet_id"),

                "target_text":
                    customer_message,

                "conversation_context":
                    conversation_context,

                "gold_intent":
                    gold_intent,

                "predicted_intent":
                    INVALID_LABEL,

                "reply":
                    "",

                "escalate":
                    None,

                "escalation_reason":
                    "Agent execution error.",

                "retrieved_cases":
                    [],

                "error":
                    repr(exc),

                "runtime_seconds":
                    round(
                        time.time() - started,
                        3
                    )
            }

            append_jsonl(
                OUTPUT_FILE,
                output_row
            )

            print(
                f"ERROR: {exc}"
            )

        completed_ids.add(
            candidate_id
        )

        # ----------------------------------------------------
        # Rate-limit protection
        # ----------------------------------------------------

        if len(completed_ids) < len(golden):

            print(
                f"Waiting "
                f"{REQUEST_DELAY_SECONDS}s..."
            )

            time.sleep(
                REQUEST_DELAY_SECONDS
            )

    # ========================================================
    # FINAL EVALUATION
    # ========================================================

    print()
    print("=" * 80)
    print("CALCULATING FINAL INTENT METRICS")
    print("=" * 80)

    predictions = load_jsonl(
        OUTPUT_FILE
    )

    # --------------------------------------------------------
    # Deduplicate by candidate_id.
    # Last saved result wins.
    # --------------------------------------------------------

    by_id = {}

    for row in predictions:

        by_id[
            row.get("candidate_id")
        ] = row

    ordered_predictions = []

    for row in golden:

        candidate_id = row.get(
            "candidate_id"
        )

        if candidate_id in by_id:

            ordered_predictions.append(
                by_id[candidate_id]
            )

    predictions = ordered_predictions

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    y_true = [
        row["gold_intent"]
        for row in predictions
    ]

    y_pred = [
        row["predicted_intent"]
        for row in predictions
    ]

    labels = sorted(
        set(y_true) | set(y_pred)
    )

    try:

        from sklearn.metrics import (
            accuracy_score,
            precision_recall_fscore_support,
            classification_report,
            confusion_matrix,
        )

    except ImportError:

        print(
            "ERROR: scikit-learn is required."
        )

        sys.exit(1)

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision, recall, f1, support = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0
        )
    )

    macro_precision = precision.mean()
    macro_recall = recall.mean()
    macro_f1 = f1.mean()

    weighted_precision, weighted_recall, weighted_f1, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0
        )
    )

    invalid_count = sum(
        prediction == INVALID_LABEL
        for prediction in y_pred
    )

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print()
    print("=" * 80)
    print("RAG AGENT — INTENT RESULTS")
    print("=" * 80)

    print(
        f"Examples evaluated  : "
        f"{len(y_true)}"
    )

    print(
        f"Invalid/error cases : "
        f"{invalid_count}"
    )

    print(
        f"Accuracy            : "
        f"{accuracy:.4f}"
    )

    print(
        f"Macro Precision     : "
        f"{macro_precision:.4f}"
    )

    print(
        f"Macro Recall        : "
        f"{macro_recall:.4f}"
    )

    print(
        f"Macro F1            : "
        f"{macro_f1:.4f}"
    )

    print(
        f"Weighted Precision  : "
        f"{weighted_precision:.4f}"
    )

    print(
        f"Weighted Recall     : "
        f"{weighted_recall:.4f}"
    )

    print(
        f"Weighted F1         : "
        f"{weighted_f1:.4f}"
    )

    # ========================================================
    # PER-INTENT
    # ========================================================

    print()
    print("=" * 80)
    print("PER-INTENT RESULTS")
    print("=" * 80)

    print(
        classification_report(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0,
            digits=4
        )
    )

    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    print("=" * 80)
    print("CONFUSION MATRIX")
    print("=" * 80)

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    print()
    print("Labels:")

    for i, label in enumerate(labels):

        print(
            f"{i}: {label}"
        )

    print()
    print("Matrix:")

    print(cm)

    # ========================================================
    # RETRIEVAL SUMMARY
    # ========================================================

    retrieval_scores = []

    for row in predictions:

        for case in row.get(
            "retrieved_cases",
            []
        ):

            score = case.get(
                "retrieval_score"
            )

            if isinstance(
                score,
                (int, float)
            ):

                retrieval_scores.append(
                    float(score)
                )

    if retrieval_scores:

        print()
        print("=" * 80)
        print("RETRIEVAL SUMMARY")
        print("=" * 80)

        print(
            f"Retrieved cases scored : "
            f"{len(retrieval_scores):,}"
        )

        print(
            f"Mean similarity        : "
            f"{sum(retrieval_scores) / len(retrieval_scores):.4f}"
        )

        print(
            f"Max similarity         : "
            f"{max(retrieval_scores):.4f}"
        )

    # ========================================================
    # SAVE SUMMARY JSON
    # ========================================================

    summary = {

        "total_examples":
            len(y_true),

        "invalid_or_error_cases":
            invalid_count,

        "accuracy":
            round(accuracy, 6),

        "macro_precision":
            round(macro_precision, 6),

        "macro_recall":
            round(macro_recall, 6),

        "macro_f1":
            round(macro_f1, 6),

        "weighted_precision":
            round(weighted_precision, 6),

        "weighted_recall":
            round(weighted_recall, 6),

        "weighted_f1":
            round(weighted_f1, 6),

        "output_file":
            str(OUTPUT_FILE)
    }

    summary_file = Path(
        "data/golden/rag_metrics.json"
    )

    with summary_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=2
        )

    print()
    print("=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)

    print(
        f"Predictions : "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Metrics     : "
        f"{summary_file}"
    )


if __name__ == "__main__":

    main()
