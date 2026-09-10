"""Run end-to-end evaluation pipeline on golden benchmark dataset."""

import json
from pathlib import Path
from typing import List, Dict, Any
from src.agent import SupportAgent
from evaluation.metrics import compute_classification_metrics
from evaluation.judge import LLMJudge
from evaluation.failure_analysis import categorize_failures


def load_golden_set(path: Path = Path("./data/golden/test_set.jsonl")) -> List[Dict[str, Any]]:
    """Load evaluation benchmark dataset."""
    if not path.exists():
        # Fallback sample evaluation cases if file not yet populated
        return [
            {
                "query": "My order #12345 hasn't arrived yet and was supposed to be here yesterday.",
                "true_intent": "ORDER_STATUS_TRACKING",
                "reference_reply": "Hi! We'd be glad to track order #12345 for you. Let us check the courier status.",
            },
            {
                "query": "I want to cancel my subscription and get my money back immediately.",
                "true_intent": "CANCELLATION_REFUND",
                "reference_reply": "We are sorry to see you go. Please share your account email so we can process the cancellation.",
            },
            {
                "query": "The app keeps crashing whenever I try to log in on Android.",
                "true_intent": "TECHNICAL_SUPPORT",
                "reference_reply": "We apologize for the trouble. Could you check if you are on the latest app version?",
            },
        ]
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def run_evaluation(
    golden_path: Path = Path("./data/golden/test_set.jsonl"),
    output_results_dir: Path = Path("./experiments/results"),
) -> Dict[str, Any]:
    """Execute end-to-end evaluation."""
    print("Initializing Agent and Judge...")
    agent = SupportAgent()
    judge = LLMJudge()

    dataset = load_golden_set(golden_path)
    print(f"Evaluating {len(dataset)} examples...")

    eval_records = []
    y_true = []
    y_pred = []

    for item in dataset:
        query = item["query"]
        true_intent = item.get("true_intent")
        ref_reply = item.get("reference_reply", "")

        result = agent.process_message(query)
        pred_intent = result["intent"]
        gen_reply = result["reply"]

        if true_intent:
            y_true.append(true_intent)
            y_pred.append(pred_intent)

        judge_eval = judge.evaluate(query, gen_reply, ref_reply)

        eval_records.append({
            "query": query,
            "true_intent": true_intent,
            "pred_intent": pred_intent,
            "reference_reply": ref_reply,
            "generated_reply": gen_reply,
            **judge_eval,
        })

    metrics = {}
    if y_true and y_pred:
        metrics["classification"] = compute_classification_metrics(y_true, y_pred)

    failures_df = categorize_failures(eval_records)
    print("\n--- Evaluation Summary ---")
    if "classification" in metrics:
        print(f"Classification Accuracy: {metrics['classification']['accuracy']:.2f}")
    print(f"Identified Failures: {len(failures_df)}")

    output_results_dir.mkdir(parents=True, exist_ok=True)
    with open(output_results_dir / "eval_records.json", "w", encoding="utf-8") as f:
        json.dump(eval_records, f, indent=2)

    with open(output_results_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Evaluation artifacts saved to {output_results_dir}")
    return {"metrics": metrics, "eval_records": eval_records}


if __name__ == "__main__":
    run_evaluation()
