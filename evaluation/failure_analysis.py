"""Analyze and group agent failure modes and error distributions."""

from typing import List, Dict, Any
from collections import defaultdict
import pandas as pd


def categorize_failures(
    eval_records: List[Dict[str, Any]],
    score_threshold: float = 3.0,
) -> pd.DataFrame:
    """Filter records with sub-par performance and group by error symptoms.

    Args:
        eval_records: List of evaluated query records.
        score_threshold: Rating threshold below which a case is considered a failure.

    Returns:
        DataFrame with categorized failure modes.
    """
    failures = []
    for rec in eval_records:
        overall = rec.get("overall_score", 5.0)
        if overall < score_threshold:
            reasons = []
            if rec.get("correctness_score", 5.0) < score_threshold:
                reasons.append("HALLUCINATION_OR_FACTUAL_ERROR")
            if rec.get("empathy_score", 5.0) < score_threshold:
                reasons.append("POOR_EMPATHY_OR_TONE")
            if rec.get("actionability_score", 5.0) < score_threshold:
                reasons.append("INSUFFICIENT_ACTIONABILITY")

            failures.append({
                "query": rec.get("query"),
                "intent": rec.get("intent"),
                "generated_reply": rec.get("generated_reply"),
                "overall_score": overall,
                "primary_failure": reasons[0] if reasons else "UNCATEGORIZED",
                "critique": rec.get("critique", ""),
            })

    return pd.DataFrame(failures)
