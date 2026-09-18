"""Azure OpenAI embedding provider.

Requires: pip install openai
Configuration (environment variables):
    AZURE_OPENAI_API_KEY       required (API-key auth; see note below for
                                 managed identity)
    AZURE_OPENAI_ENDPOINT      required, e.g. https://my-resource.openai.azure.com
    AZURE_OPENAI_DEPLOYMENT    required — the embedding model's deployment
                                 name in Azure AI Foundry/Azure OpenAI, not
                                 the base model name
    AZURE_OPENAI_API_VERSION   optional, defaults to "2024-10-21"

For managed-identity auth instead of an API key (the preference in
skills/dotnet/azure.md), pass a `azure_ad_token_provider` built from
`azure-identity`'s `DefaultAzureCredential` — this module uses an API key
by default to keep the dependency footprint minimal for a local CLI tool;
swap it if running this in an Azure-hosted context where managed identity
is available.
"""
from __future__ import annotations

import os


class AzureOpenAIEmbeddingProvider:
    def __init__(self) -> None:
        try:
            from openai import AzureOpenAI
        except ImportError as e:
            raise ImportError(
                "The 'azure-openai' provider requires the openai package: pip install openai"
            ) from e

        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
        if not (api_key and endpoint and deployment):
            raise RuntimeError(
                "AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and "
                "AZURE_OPENAI_DEPLOYMENT must all be set."
            )

        self.model_name = deployment
        self._client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self._client.embeddings.create(input=batch, model=self.model_name)
            results.extend(item.embedding for item in response.data)
        return results
