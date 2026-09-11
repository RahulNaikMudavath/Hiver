import json
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

try:
    from sklearn.metrics import (
        accuracy_score,
        precision_recall_fscore_support,
        classification_report,
        confusion_matrix,
    )
except ImportError:
    import numpy as np

    def accuracy_score(y_true, y_pred):
        return sum(yt == yp for yt, yp in zip(y_true, y_pred)) / len(y_true) if y_true else 0.0

    def precision_recall_fscore_support(y_true, y_pred, labels=None, average=None, zero_division=0):
        if labels is None:
            labels = sorted(set(y_true) | set(y_pred))

        precisions = []
        recalls = []
        f1s = []
        supports = []

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
            if total_sup > 0:
                wp = np.average(precisions, weights=supports)
                wr = np.average(recalls, weights=supports)
                wf = np.average(f1s, weights=supports)
                return wp, wr, wf, None
            else:
                return 0.0, 0.0, 0.0, None
        elif average is None:
            return precisions, recalls, f1s, supports

    def classification_report(y_true, y_pred, labels=None, zero_division=0, digits=4):
        if labels is None:
            labels = sorted(set(y_true) | set(y_pred))
        precisions, recalls, f1s, supports = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, zero_division=zero_division
        )

        max_len = max(len(str(lbl)) for lbl in labels + ["accuracy", "macro avg", "weighted avg"])
        width = max(max_len + 2, 25)

        lines = []
        header = f"{'':<{width}}  {'precision':>10}  {'recall':>10}  {'f1-score':>10}  {'support':>10}"
        lines.append(header)
        lines.append("")

        for label, p, r, f, s in zip(labels, precisions, recalls, f1s, supports):
            lines.append(f"{str(label):<{width}}  {p:10.{digits}f}  {r:10.{digits}f}  {f:10.{digits}f}  {int(s):10d}")

        lines.append("")
        acc = accuracy_score(y_true, y_pred)
        total_s = int(supports.sum())
        lines.append(f"{'accuracy':<{width}}  {'':>10}  {'':>10}  {acc:10.{digits}f}  {total_s:10d}")

        lines.append(f"{'macro avg':<{width}}  {precisions.mean():10.{digits}f}  {recalls.mean():10.{digits}f}  {f1s.mean():10.{digits}f}  {total_s:10d}")

        wp, wr, wf, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average="weighted", zero_division=0
        )
        lines.append(f"{'weighted avg':<{width}}  {wp:10.{digits}f}  {wr:10.{digits}f}  {wf:10.{digits}f}  {total_s:10d}")

        return "\n".join(lines)

    def confusion_matrix(y_true, y_pred, labels=None):
        if labels is None:
            labels = sorted(set(y_true) | set(y_pred))
        label_to_idx = {l: i for i, l in enumerate(labels)}
        matrix = np.zeros((len(labels), len(labels)), dtype=int)
        for yt, yp in zip(y_true, y_pred):
            if yt in label_to_idx and yp in label_to_idx:
                matrix[label_to_idx[yt], label_to_idx[yp]] += 1
        return matrix


INPUT = Path("data/golden/baseline_keyword_predictions.jsonl")


def main():

    y_true = []
    y_pred = []

    with INPUT.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)

                y_true.append(row["gold_intent"])
                y_pred.append(row["predicted_intent"])

    labels = sorted(set(y_true) | set(y_pred))

    accuracy = accuracy_score(y_true, y_pred)

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0
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

    print("=" * 80)
    print("BASELINE 1 — FULL EVALUATION")
    print("=" * 80)

    print(f"Total examples     : {len(y_true)}")
    print(f"Accuracy            : {accuracy:.4f}")
    print(f"Macro Precision     : {macro_precision:.4f}")
    print(f"Macro Recall        : {macro_recall:.4f}")
    print(f"Macro F1            : {macro_f1:.4f}")
    print(f"Weighted Precision  : {weighted_precision:.4f}")
    print(f"Weighted Recall     : {weighted_recall:.4f}")
    print(f"Weighted F1        : {weighted_f1:.4f}")

    print("\n")
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

    print("=" * 80)
    print("CONFUSION MATRIX")
    print("=" * 80)

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    print("\nLabels:")
    for i, label in enumerate(labels):
        print(f"{i}: {label}")

    print("\nMatrix:")
    print(cm)


if __name__ == "__main__":
    main()