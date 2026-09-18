"""Local / self-hosted embedding provider — no data leaves the machine.

Requires: pip install sentence-transformers
Configuration (environment variables):
    LOCAL_EMBEDDING_MODEL   optional, defaults to "all-MiniLM-L6-v2"
                             (a small, fast, well-established sentence-
                             embedding model — swap for a larger one if
                             retrieval quality matters more than speed)

See skills/agentic-ai/frameworks/local-models.md for the data-residency
reasoning behind choosing this provider over a hosted one.
"""
from __future__ import annotations

import os


class LocalEmbeddingProvider:
    def __init__(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "The 'local' provider requires sentence-transformers: "
                "pip install sentence-transformers"
            ) from e

        self.model_name = os.environ.get("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self._model = SentenceTransformer(self.model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return [v.tolist() for v in vectors]
