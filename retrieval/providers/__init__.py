"""Pluggable embedding providers.

No provider is a hard dependency of `retrieval/` itself — each provider
module imports its own SDK lazily, so `pip install`ing only what you need
(see ../requirements.txt) is enough. This is the same framework/provider-
neutrality principle as `skills/agentic-ai/fundamentals/` applied to this
tool: the retrieval layer's core (index_store.py, build_index.py, the MCP
server) never imports a provider SDK directly — only through this factory.
"""
from __future__ import annotations

from typing import Protocol


class EmbeddingProvider(Protocol):
    """A provider embeds a batch of texts into equal-length float vectors."""

    model_name: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def get_provider(name: str) -> EmbeddingProvider:
    """Resolve a provider by name: 'openai', 'azure-openai', or 'local'.

    Each provider reads its own configuration from environment variables
    (documented in its module and in ../README.md) so no secret is ever
    passed as a CLI argument or hardcoded here.
    """
    if name == "openai":
        from .openai_provider import OpenAIEmbeddingProvider

        return OpenAIEmbeddingProvider()
    if name == "azure-openai":
        from .azure_openai_provider import AzureOpenAIEmbeddingProvider

        return AzureOpenAIEmbeddingProvider()
    if name == "local":
        from .local_provider import LocalEmbeddingProvider

        return LocalEmbeddingProvider()
    raise ValueError(f"Unknown embedding provider '{name}'. Expected: openai, azure-openai, local.")
