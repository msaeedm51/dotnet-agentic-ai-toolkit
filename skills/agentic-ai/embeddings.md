---
id: agentic-ai.embeddings
title: Embeddings
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [embeddings, vectorize text, embedding model, chunk and embed]
requires: []
related: [agentic-ai.vector-search, agentic-ai.rag]
optional: [agentic-ai.frameworks.openai, agentic-ai.frameworks.azure-openai]
prerequisites: []
tags: [embeddings, rag]
---

# Embeddings

## Purpose
Convert text (or other content) into vector representations that capture
semantic meaning, enabling similarity search — the foundation
`agentic-ai.vector-search` and `agentic-ai.rag` build on.

## When to Use
Any time you need to compare content by meaning rather than exact/keyword
match: semantic search, RAG retrieval, deduplication, clustering.

## Prerequisites
None.

## Inputs Required
The content to embed, its expected volume (drives batching/cost
decisions), and whether it will be compared only against other embeddings
from the same model (embeddings from different models are generally not
comparable).

## Engineering Principles
1. Use one embedding model consistently for a given vector space — mixing
   embeddings from different models/versions in the same similarity search
   produces meaningless comparisons.
2. Chunk before embedding for long documents — an embedding of an entire
   long document averages/dilutes meaning across everything in it, hurting
   retrieval precision (see `agentic-ai.rag` for chunking strategy).
3. Batch embedding requests where the provider supports it — far more
   cost/latency efficient than one call per chunk.
4. Store the embedding model identifier alongside the vectors — if the
   model is ever upgraded, you need to know which vectors must be
   re-embedded, not silently mix old and new.
5. Normalize/cache embeddings for content that doesn't change — re-
   embedding identical content repeatedly wastes cost for no benefit.

## Step-by-Step Workflow
1. Chunk the source content appropriately for the use case
   (`agentic-ai.rag`).
2. Call the embedding model in batches, respecting the provider's rate
   limits and batch size limits.
3. Store each vector alongside its source chunk id, the embedding model
   identifier/version, and any metadata needed for filtering
   (`agentic-ai.vector-search`).
4. Cache/skip re-embedding for content whose hash hasn't changed since the
   last embedding run.
5. If the embedding model is ever changed, plan a full re-embedding of
   existing content rather than mixing vector spaces — treat it like a
   schema migration (`workflows/database-change.md`).

## Code Standards
Embedding calls go through a typed client wrapping the provider SDK/API,
not inline HTTP calls scattered across the codebase — same discipline as
any other external dependency (`dotnet.dotnet` — `HttpClientFactory` +
resilience).

## Architecture Constraints
The embedding provider is behind an interface (`IEmbeddingService`) so it
can be swapped (a different provider, a local model) without changing
callers — consistent with this toolkit's framework-neutrality principle
(`skills/agentic-ai/fundamentals/`).

## Security Considerations
Content sent to an embedding provider's API leaves your infrastructure
(unless self-hosted/local) — don't embed content containing secrets or
data your data-handling policy prohibits sending to that provider
(`dotnet.security`, `agentic-ai.frameworks.local-models` for a
self-hosted alternative).

## Testing Requirements
Test that near-duplicate content produces high-similarity vectors and
clearly unrelated content produces low-similarity vectors, as a sanity
check on the embedding pipeline (not testing the model itself, testing your
integration of it).

## Common Mistakes
- Mixing vectors from two different embedding models/versions in one
  similarity search, producing meaningless results with no error to signal
  it.
- Embedding entire long documents unchunked, hurting retrieval precision.
- Re-embedding unchanged content on every indexing run instead of caching
  by content hash.

## Anti-Patterns
- **Silent model drift**: upgrading the embedding model without
  re-embedding existing content, so old and new vectors coexist in the same
  index producing inconsistent similarity results.
- **Embedding everything unconditionally**: embedding at ingestion time
  regardless of whether the content will ever actually be searched,
  wasting cost.

## Validation Checklist
- [ ] One consistent embedding model per vector space; version tracked.
- [ ] Long content is chunked before embedding.
- [ ] Embedding calls are batched where supported.
- [ ] Content sent to an external embedding provider complies with data-
      handling policy.

## Definition of Done
Meets `rules/definition-of-done.md`; a sanity test confirms similar content
embeds as similar and dissimilar content embeds as dissimilar.

## Example
```csharp
public interface IEmbeddingService
{
    Task<IReadOnlyList<float[]>> EmbedBatchAsync(IReadOnlyList<string> texts, CancellationToken ct);
}

public sealed class DocumentIndexer(IEmbeddingService embeddings, IChunkStore store)
{
    public async Task IndexAsync(Document document, CancellationToken ct)
    {
        var chunks = DocumentChunker.Chunk(document.Text, maxTokens: 500, overlapTokens: 50);
        var unchanged = await store.FilterUnchangedByHashAsync(chunks, ct);
        var toEmbed = chunks.Except(unchanged).ToList();

        var vectors = await embeddings.EmbedBatchAsync(toEmbed.Select(c => c.Text).ToList(), ct);

        for (var i = 0; i < toEmbed.Count; i++)
            await store.SaveAsync(toEmbed[i], vectors[i], modelVersion: "text-embedding-3-small", ct);
    }
}
```

## Related Skills
- `agentic-ai.vector-search` — indexing and querying these vectors.
- `agentic-ai.rag` — the primary consumer of embeddings in this toolkit.
