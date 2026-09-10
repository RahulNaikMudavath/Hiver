"""Majority class baseline for intent classification."""

from typing import List, Optional
from collections import Counter


class MajorityClassifier:
    """Predicts the most frequent class in the training dataset."""

    def __init__(self):
        self.majority_class: Optional[str] = None
        self.confidence: float = 0.0

    def fit(self, texts: List[str], labels: List[str]) -> "MajorityClassifier":
        """Fit baseline by determining most frequent label.

        Args:
            texts: List of input texts (unused for majority).
            labels: Ground truth intent labels.

        Returns:
            Fitted classifier instance.
        """
        if not labels:
            raise ValueError("Labels list cannot be empty.")
        counts = Counter(labels)
        self.majority_class, top_count = counts.most_common(1)[0]
        self.confidence = top_count / len(labels)
        return self

    def predict(self, texts: List[str]) -> List[str]:
        """Predict majority class for all input texts."""
        if self.majority_class is None:
            raise ValueError("Classifier is not fitted.")
        return [self.majority_class] * len(texts)

    def predict_proba(self, texts: List[str]) -> List[float]:
        """Predict probability (frequency ratio) for all input texts."""
        return [self.confidence] * len(texts)
