"""Vector index construction and management using FAISS or cosine search."""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional


class VectorIndex:
    """FAISS-based or numpy-based vector index for nearest-neighbor search."""

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self._faiss_index = None

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray) -> None:
        """Add documents and their precomputed embeddings to the index.

        Args:
            documents: Metadata and text records.
            embeddings: 2D numpy array of shape (N, embedding_dim).
        """
        assert len(documents) == len(embeddings), "Mismatch between doc count and embeddings count"
        self.documents.extend(documents)
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        try:
            import faiss
            if self._faiss_index is None:
                self._faiss_index = faiss.IndexFlatIP(self.embedding_dim)
            self._faiss_index.add(embeddings.astype(np.float32))
        except ImportError:
            pass  # Fallback to numpy cosine similarity in retrieve

    def save(self, directory: Path = Path("./data/processed/index")) -> None:
        """Persist index documents and embeddings to disk.

        Args:
            directory: Path to storage folder.
        """
        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / "docs.json", "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2)

        if self.embeddings is not None:
            np.save(directory / "embeddings.npy", self.embeddings)
        print(f"Saved vector index ({len(self.documents)} docs) to {directory}")

    @classmethod
    def load(cls, directory: Path = Path("./data/processed/index")) -> "VectorIndex":
        """Load vector index from disk.

        Args:
            directory: Path to storage folder.

        Returns:
            Instantiated VectorIndex.
        """
        instance = cls()
        docs_file = directory / "docs.json"
        emb_file = directory / "embeddings.npy"

        if docs_file.exists():
            with open(docs_file, "r", encoding="utf-8") as f:
                instance.documents = json.load(f)

        if emb_file.exists():
            embeddings = np.load(emb_file)
            instance.embedding_dim = embeddings.shape[1]
            instance.embeddings = embeddings
            try:
                import faiss
                instance._faiss_index = faiss.IndexFlatIP(instance.embedding_dim)
                instance._faiss_index.add(embeddings.astype(np.float32))
            except ImportError:
                pass

        return instance
