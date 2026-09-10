"""TF-IDF + Logistic Regression baseline for intent classification."""

from typing import List, Tuple
import numpy as np


class TFIDFClassifier:
    """TF-IDF Vectorizer with Logistic Regression classifier."""

    def __init__(self, max_features: int = 5000, ngram_range: Tuple[int, int] = (1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.pipeline = None
        self.is_fitted = False

    def _init_pipeline(self):
        if self.pipeline is None:
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.linear_model import LogisticRegression
                from sklearn.pipeline import Pipeline

                self.pipeline = Pipeline(
                    [
                        (
                            "tfidf",
                            TfidfVectorizer(
                                max_features=self.max_features,
                                ngram_range=self.ngram_range,
                            ),
                        ),
                        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000)),
                    ]
                )
            except ImportError:
                raise ImportError(
                    "scikit-learn is required for TFIDFClassifier. Install with `pip install scikit-learn`."
                )

    def fit(self, texts: List[str], labels: List[str]) -> "TFIDFClassifier":
        """Train the TF-IDF + Logistic Regression pipeline.

        Args:
            texts: Training sentences.
            labels: Intent target labels.

        Returns:
            Fitted classifier.
        """
        self._init_pipeline()
        self.pipeline.fit(texts, labels)
        self.is_fitted = True
        return self

    def predict(self, texts: List[str]) -> List[str]:
        """Predict intent labels for input texts."""
        if not self.is_fitted or self.pipeline is None:
            raise ValueError("Classifier is not fitted.")
        return list(self.pipeline.predict(texts))

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Predict probability distributions across classes."""
        if not self.is_fitted or self.pipeline is None:
            raise ValueError("Classifier is not fitted.")
        return self.pipeline.predict_proba(texts)
