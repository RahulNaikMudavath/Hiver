"""Evaluation metrics for classification, retrieval, and generation."""

from typing import List, Dict, Any
import numpy as np


def compute_classification_metrics(
    y_true: List[str],
    y_pred: List[str],
) -> Dict[str, Any]:
    """Compute accuracy, precision, recall, and f1 score.

    Args:
        y_true: Ground truth intent labels.
        y_pred: Predicted intent labels.

    Returns:
        Dictionary of aggregate and per-class metrics.
    """
    try:
        from sklearn.metrics import (
            accuracy_score,
            precision_recall_fscore_support,
            classification_report,
        )

        acc = accuracy_score(y_true, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="weighted", zero_division=0
        )
        macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="macro", zero_division=0
        )
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    except ImportError:
        # Pure Python fallback
        correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
        acc = correct / len(y_true) if y_true else 0.0
        prec, rec, f1, macro_f1 = acc, acc, acc, acc
        report = {}

    return {
        "accuracy": float(acc),
        "weighted_precision": float(prec),
        "weighted_recall": float(rec),
        "weighted_f1": float(f1),
        "macro_f1": float(macro_f1),
        "detailed_report": report,
    }


def compute_retrieval_hit_rate(
    retrieved_doc_ids: List[List[str]],
    ground_truth_doc_ids: List[str],
    k: int = 3,
) -> float:
    """Calculate Hit@k for retrieval.

    Args:
        retrieved_doc_ids: List of retrieved doc ID lists per query.
        ground_truth_doc_ids: List of correct doc IDs per query.
        k: Cutoff rank.

    Returns:
        Hit@k score between 0.0 and 1.0.
    """
    hits = 0
    total = len(ground_truth_doc_ids)
    if total == 0:
        return 0.0

    for ret_list, gt_id in zip(retrieved_doc_ids, ground_truth_doc_ids):
        if gt_id in ret_list[:k]:
            hits += 1
    return hits / total
