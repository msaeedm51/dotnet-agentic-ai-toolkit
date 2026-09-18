---
id: agentic-ai.vector-search
title: Vector Search
category: skill
domain: agentic-ai
technologies: [dotnet, postgresql, pgvector]
triggers: [vector search, similarity search, nearest neighbor search, ivfflat, hnsw]
requires: [agentic-ai.embeddings]
related: [agentic-ai.rag, dotnet.database.postgresql]
optional: []
prerequisites: [agentic-ai.embeddings]
tags: [vector-search, rag]
---

# Vector Search

## Purpose
Store and query embedding vectors efficiently for nearest-neighbor
similarity search, with authorization filtering applied correctly — the
retrieval mechanism `agentic-ai.rag` and semantic `agentic-ai.memory`
depend on.

## When to Use
Any semantic similarity query over embedded content — RAG retrieval,
semantic memory recall, deduplication by meaning.

## Prerequisites
`agentic-ai.embeddings`.

## Inputs Required
Expected corpus size (drives index type choice), query latency
requirements, and the authorization/filtering dimensions queries must
respect (user, tenant, document permission).

## Engineering Principles
1. Choose a vector store that fits the project's existing infrastructure
   before reaching for a dedicated vector database — `pgvector` on an
   already-used PostgreSQL instance (`dotnet.database.postgresql`) avoids a
   new infrastructure dependency for small-to-medium corpora.
2. Index type matches corpus size and recall/latency needs: `ivfflat` is
   cheaper to build, `hnsw` generally gives better recall/latency at query
   time for larger corpora — verify against the project's actual scale
   rather than defaulting blindly.
3. Authorization filtering happens as part of the query (a `WHERE` clause
   alongside the similarity search), not as a post-filter after retrieving
   top-k results — post-filtering can return fewer than k authorized
   results even when more exist.
4. Similarity search returns a relevance score — use a minimum-relevance
   threshold to avoid returning weakly-related results just to fill top-k.
5. Re-index (or incrementally update) as content changes, on a cadence
   matching the source's actual update frequency (`agentic-ai.embeddings`).

## Step-by-Step Workflow
1. Choose the vector store (existing PostgreSQL + `pgvector`, or a
   dedicated vector database) based on corpus size and existing
   infrastructure.
2. Create the appropriate index type for the corpus size and distance
   metric (cosine similarity is the common default for text embeddings).
3. Build the query: embed the search text, run the similarity query with
   authorization/tenant filters applied in the same query, apply a minimum-
   relevance threshold, return top-k with scores.
4. Verify authorization filtering is correct with a test proving a user
   never receives a result from content they're not authorized to see.
5. Monitor query latency and recall quality as the corpus grows;
   revisit index type/parameters if either degrades.

## Code Standards
Vector search queries go through a dedicated service
(`IVectorSearchService`), not raw SQL scattered across callers — keeps
authorization filtering enforced in one place.

## Architecture Constraints
The vector search service is infrastructure, accessed through the same
kind of port/interface as any other data access
(`dotnet.architecture.repository-specification`) — the application layer
doesn't know or care whether it's `pgvector`, a dedicated vector database,
or an in-memory index for a small corpus.

## Security Considerations
Authorization filtering is enforced inside the query itself, not as a
post-processing step on the client side — a missing or incorrect filter
here is a direct data leak across permission boundaries, at BLOCKER
severity (`agent.security-reviewer`).

## Testing Requirements
Integration test against a real vector store (Testcontainers PostgreSQL
with `pgvector`) covering: relevant content is retrieved for a matching
query, irrelevant content is excluded, and unauthorized content is never
returned regardless of similarity score.

## Common Mistakes
- Post-filtering top-k results by authorization instead of filtering inside
  the query — can silently return fewer results than requested, or worse,
  leak a result briefly visible before filtering in a client-side
  implementation.
- No minimum-relevance threshold, returning weakly related "top-k" results
  that dilute the RAG context with noise.
- Using a B-tree/default index (or no index) on the vector column at real
  scale, causing a full table scan for every query.

## Anti-Patterns
- **Unfiltered global search**: a vector search with no tenant/user
  scoping option at all, forcing every consumer to filter results after
  the fact (see the authorization mistake above).
- **One-size index**: always defaulting to the same index type regardless
  of corpus size, rather than checking whether it still fits as data grows.

## Validation Checklist
- [ ] Authorization filtering is applied inside the query, not
      post-retrieval.
- [ ] Index type matches actual corpus size and query patterns.
- [ ] A minimum-relevance threshold prevents low-quality results from
      filling top-k.
- [ ] Query latency is monitored as the corpus grows.

## Definition of Done
Meets `rules/definition-of-done.md`; an integration test proves
authorization filtering can't be bypassed via a high-similarity match.

## Example
```csharp
public interface IVectorSearchService
{
    Task<IReadOnlyList<ScoredChunk>> QueryAsync(string queryText, int topK, Guid authorizedFor, CancellationToken ct);
}

public sealed class PgVectorSearchService(NpgsqlDataSource dataSource, IEmbeddingService embeddings) : IVectorSearchService
{
    public async Task<IReadOnlyList<ScoredChunk>> QueryAsync(string queryText, int topK, Guid authorizedFor, CancellationToken ct)
    {
        var queryVector = (await embeddings.EmbedBatchAsync([queryText], ct))[0];

        await using var cmd = dataSource.CreateCommand("""
            SELECT chunk_id, text, 1 - (embedding <=> $1) AS score
            FROM document_chunks c
            JOIN document_permissions p ON p.document_id = c.document_id
            WHERE p.user_id = $2 AND 1 - (embedding <=> $1) > 0.7
            ORDER BY embedding <=> $1
            LIMIT $3
            """); // authorization filter is part of the query, not a post-filter
        cmd.Parameters.AddWithValue(new Vector(queryVector));
        cmd.Parameters.AddWithValue(authorizedFor);
        cmd.Parameters.AddWithValue(topK);

        await using var reader = await cmd.ExecuteReaderAsync(ct);
        var results = new List<ScoredChunk>();
        while (await reader.ReadAsync(ct))
            results.Add(new ScoredChunk(reader.GetGuid(0), reader.GetString(1), reader.GetDouble(2)));
        return results;
    }
}
```

## Related Skills
- `agentic-ai.embeddings` — producing the vectors this searches.
- `agentic-ai.rag` — the primary consumer.
- `dotnet.database.postgresql` — `pgvector` setup and index tuning detail.
