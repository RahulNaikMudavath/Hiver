"""Context retrieval logic for incoming customer queries."""

from typing import List, Dict, Any, Optional
import numpy as np
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.index import VectorIndex


class Retriever:
    """Retrieves top-k relevant past support resolutions or knowledge base snippets."""

    def __init__(
        self,
        index: Optional[VectorIndex] = None,
        embedding_model: Optional[EmbeddingModel] = None,
    ):
        self.embedding_model = embedding_model or EmbeddingModel()
        self.index = index or VectorIndex()

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve most similar context records given a user query.

        Args:
            query: Incoming customer message text.
            top_k: Number of nearest documents to return.

        Returns:
            List of matching records with similarity score and metadata.
        """
        if not self.index.documents or self.index.embeddings is None:
            return []

        query_vec = self.embedding_model.encode(query)

        # If FAISS index is loaded
        if self.index._faiss_index is not None:
            scores, indices = self.index._faiss_index.search(
                query_vec.astype(np.float32), min(top_k, len(self.index.documents))
            )
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.index.documents):
                    doc = dict(self.index.documents[idx])
                    doc["similarity_score"] = float(score)
                    results.append(doc)
            return results

        # Fallback to numpy dot product (vectors normalized)
        dot_products = np.dot(self.index.embeddings, query_vec.T).squeeze()
        top_indices = np.argsort(-dot_products)[:top_k]

        results = []
        for idx in top_indices:
            doc = dict(self.index.documents[idx])
            doc["similarity_score"] = float(dot_products[idx])
            results.append(doc)
        return results
