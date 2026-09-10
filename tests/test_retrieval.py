"""Unit tests for retrieval module."""

import numpy as np
import pytest
from src.retrieval.index import VectorIndex
from src.retrieval.retrieve import Retriever


class MockEmbeddingModel:
    def encode(self, texts, batch_size=64):
        if isinstance(texts, str):
            texts = [texts]
        # Return deterministic dummy vectors
        return np.ones((len(texts), 4), dtype=np.float32) / 2.0


def test_vector_index_and_retriever():
    mock_emb = MockEmbeddingModel()
    index = VectorIndex(embedding_dim=4)

    docs = [
        {"id": 1, "text": "Tracking order details"},
        {"id": 2, "text": "Refund processing time"},
    ]
    embeddings = np.array([
        [0.5, 0.5, 0.5, 0.5],
        [0.1, 0.2, 0.3, 0.4],
    ], dtype=np.float32)

    index.add_documents(docs, embeddings)
    retriever = Retriever(index=index, embedding_model=mock_emb)

    results = retriever.retrieve("where is order", top_k=2)
    assert len(results) == 2
    assert results[0]["id"] == 1
    assert "similarity_score" in results[0]
