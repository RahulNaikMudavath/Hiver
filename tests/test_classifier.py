"""Unit tests for classification models."""

import pytest
from src.classification.baseline_majority import MajorityClassifier
from src.classification.baseline_tfidf import TFIDFClassifier
from src.classification.llm_classifier import LLMClassifier


def test_majority_classifier():
    texts = ["hello", "where is order", "refund please", "package delayed"]
    labels = ["GREETING", "ORDER", "REFUND", "ORDER"]

    clf = MajorityClassifier()
    clf.fit(texts, labels)

    preds = clf.predict(["new query 1", "new query 2"])
    assert preds == ["ORDER", "ORDER"]
    assert clf.confidence == 0.5


def test_tfidf_classifier():
    pytest.importorskip("sklearn")
    texts = [
        "track my order package",
        "where is my shipment",
        "cancel my order and refund",
        "i need a money refund",
    ]
    labels = ["ORDER", "ORDER", "REFUND", "REFUND"]

    clf = TFIDFClassifier()
    clf.fit(texts, labels)

    pred = clf.predict(["where is my order tracking"])
    assert len(pred) == 1
    assert pred[0] in ["ORDER", "REFUND"]


def test_llm_classifier_fallback():
    clf = LLMClassifier()
    res = clf.classify("where is my order package status?")
    assert "intent" in res
    assert "confidence" in res
    assert res["intent"] == "ORDER_STATUS_TRACKING"
