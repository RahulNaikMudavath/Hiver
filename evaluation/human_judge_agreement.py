"""Calculate agreement metrics between human annotators and LLM judges."""

from typing import List, Dict, Any
import numpy as np


def compute_agreement(
    human_ratings: List[float],
    judge_ratings: List[float],
) -> Dict[str, float]:
    """Calculate Cohen's Kappa, Pearson correlation, and Mean Absolute Error.

    Args:
        human_ratings: List of numerical ratings from humans.
        judge_ratings: List of numerical ratings from LLM judge.

    Returns:
        Dictionary of agreement metrics.
    """
    assert len(human_ratings) == len(judge_ratings), "Rating lists must have identical lengths"

    if not human_ratings:
        return {"mae": 0.0, "pearson_r": 0.0, "cohen_kappa": 0.0}

    # Binned kappa for discrete rating scales
    human_binned = [round(r) for r in human_ratings]
    judge_binned = [round(r) for r in judge_ratings]
    try:
        from sklearn.metrics import cohen_kappa_score
        kappa = cohen_kappa_score(human_binned, judge_binned)
    except Exception:
        kappa = 0.0

    mae = float(np.mean(np.abs(np.array(human_ratings) - np.array(judge_ratings))))

    # Pearson r
    if len(set(human_ratings)) > 1 and len(set(judge_ratings)) > 1:
        corr_matrix = np.corrcoef(human_ratings, judge_ratings)
        pearson_r = float(corr_matrix[0, 1])
    else:
        pearson_r = 1.0 if human_ratings == judge_ratings else 0.0

    return {
        "mae": mae,
        "pearson_r": pearson_r,
        "cohen_kappa": float(kappa),
    }
