"""Embedding generation using sentence-transformers or lightweight embedding models."""

from typing import List, Union
import numpy as np


class EmbeddingModel:
    """Wrapper around sentence transformer embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _lazy_load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is not installed. Install via `pip install sentence-transformers`."
                )

    def encode(self, texts: Union[str, List[str]], batch_size: int = 64) -> np.ndarray:
        """Encode text or list of texts into dense vectors.

        Args:
            texts: Single string or list of strings.
            batch_size: Batch size for encoding.

        Returns:
            Numpy array of shape (N, embedding_dim).
        """
        self._lazy_load()
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings
