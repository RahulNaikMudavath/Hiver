"""Quick Reproduction Script for Headline Results.

Reproduces all headline evaluation metrics across:
1. Baseline 1: Rule-Based Keyword Classifier
2. Baseline 2: Zero-Shot LLM Classifier (with full context, no retrieval)
3. Model 1: RAG Agent V1 (TF-IDF + Historical Resolution Grounding)
4. Model 2: RAG Agent V2 (Retrieval + Optimized Intent Decision Policy & Disambiguation)

Execution time: < 5 seconds.
"""

import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

try:
    import numpy as np
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
except ImportError:
    import numpy as np

    def accuracy_score(y_true, y_pred):
        return sum(yt == yp for yt, yp in zip(y_true, y_pred)) / len(y_true) if y_true else 0.0

    def precision_recall_fscore_support(y_true, y_pred, labels=None, average=None, zero_division=0):
        if labels is None:
            labels = sorted(set(y_true) | set(y_pred))
        precisions, recalls, f1s, supports = [], [], [], []
        for label in labels:
            tp = sum(yt == label and yp == label for yt, yp in zip(y_true, y_pred))
            fp = sum(yt != label and yp == label for yt, yp in zip(y_true, y_pred))
            fn = sum(yt == label and yp != label for yt, yp in zip(y_true, y_pred))
            sup = sum(yt == label for yt in y_true)
            p = tp / (tp + fp) if (tp + fp) > 0 else float(zero_division)
            r = tp / (tp + fn) if (tp + fn) > 0 else float(zero_division)
            f = 2 * p * r / (p + r) if (p + r) > 0 else float(zero_division)
            precisions.append(p)
            recalls.append(r)
            f1s.append(f)
            supports.append(sup)
        precisions = np.array(precisions)
        recalls = np.array(recalls)
        f1s = np.array(f1s)
        supports = np.array(supports)
        if average == "macro":
            return precisions.mean(), recalls.mean(), f1s.mean(), None
        elif average == "weighted":
            total_sup = supports.sum()
            wp = np.average(precisions, weights=supports) if total_sup > 0 else 0.0
            wr = np.average(recalls, weights=supports) if total_sup > 0 else 0.0
            wf = np.average(f1s, weights=supports) if total_sup > 0 else 0.0
            return wp, wr, wf, None
        return precisions, recalls, f1s, supports


DATA_DIR = Path("data/golden")
FILES = {
    "Baseline 1 (Keyword)": DATA_DIR / "baseline_keyword_predictions.jsonl",
    "Baseline 2 (Zero-shot LLM)": DATA_DIR / "baseline_llm_predictions.jsonl",
    "RAG Agent V1": DATA_DIR / "rag_predictions.jsonl",
    "RAG Agent V2": DATA_DIR / "rag_predictions_v2.jsonl",
}


def load_predictions(path: Path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def evaluate(records):
    y_true = []
    y_pred = []
    for r in records:
        gold = r.get("gold_intent")
        pred = r.get("predicted_intent")
        if gold and pred:
            y_true.append(gold)
            y_pred.append(pred)

    labels = sorted(list(set(y_true)))
    acc = accuracy_score(y_true, y_pred)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="weighted", zero_division=0
    )

    return {
        "count": len(y_true),
        "accuracy": acc,
        "macro_p": macro_p,
        "macro_r": macro_r,
        "macro_f1": macro_f1,
        "weighted_p": weighted_p,
        "weighted_r": weighted_r,
        "weighted_f1": weighted_f1,
    }


def main():
    print("=" * 88)
    print(" " * 22 + "HIVER AI SUPPORT AGENT — HEADLINE RESULTS")
    print("=" * 88)
    print(f"{'Model':<28} | {'Accuracy':<10} | {'Weighted F1':<12} | {'Weighted P':<11} | {'Macro F1':<10}")
    print("-" * 88)

    results = {}
    for name, path in FILES.items():
        if not path.exists():
            print(f"{name:<28} | [FILE NOT FOUND: {path}]")
            continue
        records = load_predictions(path)
        metrics = evaluate(records)
        results[name] = metrics
        print(
            f"{name:<28} | "
            f"{metrics['accuracy'] * 100:>8.2f}% | "
            f"{metrics['weighted_f1']:>12.4f} | "
            f"{metrics['weighted_p']:>11.4f} | "
            f"{metrics['macro_f1']:>10.4f}"
        )

    print("=" * 88)
    if "Baseline 1 (Keyword)" in results and "RAG Agent V2" in results:
        b1_acc = results["Baseline 1 (Keyword)"]["accuracy"]
        v2_acc = results["RAG Agent V2"]["accuracy"]
        diff = (v2_acc - b1_acc) * 100
        rel = ((v2_acc - b1_acc) / b1_acc) * 100
        print(f"Key Improvement (RAG V2 vs Baseline 1): +{diff:.2f}% absolute (+{rel:.1f}% relative)")
    if "Baseline 2 (Zero-shot LLM)" in results and "RAG Agent V2" in results:
        b2_acc = results["Baseline 2 (Zero-shot LLM)"]["accuracy"]
        v2_acc = results["RAG Agent V2"]["accuracy"]
        diff = (v2_acc - b2_acc) * 100
        rel = ((v2_acc - b2_acc) / b2_acc) * 100
        print(f"Key Improvement (RAG V2 vs Baseline 2): +{diff:.2f}% absolute (+{rel:.1f}% relative)")
    print("=" * 88)


if __name__ == "__main__":
    main()
