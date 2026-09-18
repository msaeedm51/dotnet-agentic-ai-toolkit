"""OpenAI embedding provider.

Requires: pip install openai
Configuration (environment variables):
    OPENAI_API_KEY        required
    OPENAI_EMBEDDING_MODEL  optional, defaults to "text-embedding-3-small"
"""
from __future__ import annotations

import os


class OpenAIEmbeddingProvider:
    def __init__(self) -> None:
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError(
                "The 'openai' provider requires the openai package: pip install openai"
            ) from e

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

        self.model_name = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self._client = OpenAI(api_key=api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        # The API accepts a batch in one call; chunk defensively for very
        # large corpora so one oversized request can't fail the whole run.
        results: list[list[float]] = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self._client.embeddings.create(input=batch, model=self.model_name)
            results.extend(item.embedding for item in response.data)
        return results
