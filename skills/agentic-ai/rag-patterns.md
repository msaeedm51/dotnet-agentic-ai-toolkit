---
id: agentic-ai.rag-patterns
title: RAG Patterns and Types
category: skill
domain: agentic-ai
technologies: [dotnet, embeddings, vector-search]
triggers: [rag types, rag patterns, advanced rag, hybrid search, reranking, query rewriting, hyde, multi query, corrective rag, self rag, adaptive rag, agentic rag, graph rag, multimodal rag, text to sql rag, conversational rag, multi hop retrieval, cache augmented generation, which rag should i use, which rag technique, unsure which rag, best rag approach, poor retrieval quality]
requires: [agentic-ai.rag]
related: [agentic-ai.chunking, agentic-ai.embeddings, agentic-ai.vector-search, agentic-ai.evaluation, agentic-ai.observability, agentic-ai.cost-optimization, agentic-ai.fundamentals.agent-loops, agentic-ai.tool-calling, agentic-ai.model-routing, agentic-ai.memory, agentic-ai.ai-security, dotnet.database.postgresql]
optional: []
prerequisites: [agentic-ai.rag, agentic-ai.vector-search]
tags: [rag, retrieval, hybrid-search, reranking, graph-rag, agentic-rag]
---

# RAG Patterns and Types

## Purpose
Choose the right RAG architecture for the failure being fixed. Naive
retrieve-then-generate (`agentic-ai.rag`) is the baseline; this skill
catalogs the other RAG types — hybrid, reranked, query-transformed,
conversational, multi-hop, corrective, adaptive, agentic, graph, structured,
multimodal, and long-context — with when each pays for itself and what each
adds in latency, cost, and attack surface. It is separate from
`agentic-ai.rag` so the baseline stays short and this catalog is loaded only
when the baseline measurably fails.

## When to Use
- The baseline RAG pipeline misses relevant content, ranks it poorly, or
  answers confidently from irrelevant chunks.
- Questions are multi-part, multi-hop, conversational, tabular, relational,
  or span the whole corpus.
- Choosing between RAG, agentic retrieval, and putting the corpus in the
  context window.
- A request says "advanced RAG", "hybrid search", "reranker", "Graph RAG",
  "agentic RAG", "corrective RAG", or "text-to-SQL".
- The user needs RAG but has not chosen a technique ("which RAG should I
  use?") — follow "When the User Is Unsure" below.

## Prerequisites
`agentic-ai.rag` (baseline pipeline, authorization filtering, citations),
`agentic-ai.vector-search`. Chunking choices live in `agentic-ai.chunking`.

## Inputs Required
- The baseline's measured failures from the evaluation set
  (`agentic-ai.evaluation`) — no evidence of a failure means no pattern
  change. If no evaluation set exists, build one first.
- Latency and cost budgets per query (`agentic-ai.cost-optimization`).
- Corpus shape: size, stability, structure (prose, tables, entities,
  media), number of sources.
- Question shape: single fact, multi-part, follow-up, aggregate, relational.
- Authorization model, which every pattern below must preserve.
- Any decisions already recorded in `.ai/config.yaml` -> `ai.rag`
  (chunking, patterns, evaluation set) — read before proposing changes.

## Engineering Principles
1. Start from naive RAG with an evaluation set. Add one pattern at a time,
   only for a measured failure, and keep it only if the metric improves by
   more than its latency/cost price.
2. Fix retrieval before adding generation-side machinery: chunking
   (`agentic-ai.chunking`), hybrid search, and reranking resolve most
   failures without extra LLM calls in the loop.
3. Every LLM step added to the pipeline (rewrite, grade, route, decompose)
   is a cost, a latency hit, and a prompt-injection surface. Bound each one:
   max iterations, max tokens, timeout, and a defined fallback
   (`rules/agentic-ai.md`).
4. Authorization filtering applies to every retrieval call the pattern
   makes — sub-queries, multi-query variants, graph traversals, fallbacks,
   and tool-driven retrieval — inside the query, not after
   (`agentic-ai.vector-search`).
5. All retrieved material is untrusted, including graph nodes, community
   summaries, generated SQL results, image captions, and web fallback
   results (`agentic-ai.ai-security`).
6. Grade relevance against the user's original question, not the rewritten
   query, so a bad rewrite cannot vouch for itself.
7. Preserve the "not answerable from the sources" path in every pattern;
   more retrieval machinery must not make the system more willing to guess.
8. Evaluate retrieval and generation separately: recall@k, MRR/nDCG, and
   context precision for retrieval; groundedness, answer relevance, and
   abstention correctness for generation.

## RAG Type Catalog

### Architecture levels

| Type | What it is | Use when |
|---|---|---|
| Naive RAG | Chunk, embed, top-k vector search, stuff into prompt, generate | Baseline; small clean corpus; every project starts here |
| Advanced RAG | Naive plus pre-retrieval (query transformation, better indexing) and post-retrieval (rerank, compress, dedupe) stages | Baseline retrieval is roughly right but noisy or poorly ranked |
| Modular RAG | Pipeline of swappable modules (router, retriever, reranker, grader, generator) composed per query | Multiple sources or question types need different paths |

### Retrieval-quality patterns

| Pattern | Mechanism | Fixes | Cost |
|---|---|---|---|
| Hybrid search | Dense vector search plus sparse keyword/BM25/full-text, merged by Reciprocal Rank Fusion or weighted score | Misses on exact terms: IDs, error codes, product names, acronyms | Second index; fusion step |
| Reranking | Retrieve 25-100 candidates cheaply, rescore with a cross-encoder or LLM reranker, keep top 3-8 | Right chunk retrieved but ranked low; noisy top-k | Extra model call per query |
| Multi-query / RAG-Fusion | LLM writes N paraphrases; retrieve for each; fuse with RRF | Vocabulary mismatch; ambiguous queries | N retrievals plus one LLM call |
| Query rewriting | LLM turns a vague or messy query into a precise search query | Short, vague, or typo-heavy queries | One LLM call |
| HyDE | LLM drafts a hypothetical answer; embed that instead of the query | Queries phrased very differently from documents | One LLM call; can anchor on a wrong draft |
| Step-back | LLM asks a broader question first; retrieve for both | Questions needing background principles | One LLM call plus extra retrieval |
| Query decomposition | LLM splits a compound question into sub-questions; retrieve each; synthesize | Multi-part questions | LLM calls scale with parts |
| Parent-document / small-to-big | Match on small chunks, return larger parents (`agentic-ai.chunking`) | Precise match but answer needs surrounding text | Two-level storage |
| Contextual retrieval | Prepend chunk-specific LLM context before embedding and keyword indexing (`agentic-ai.chunking`), usually with hybrid search | Chunks ambiguous when read alone | LLM call per chunk at ingestion |
| Context compression | Extract only the relevant sentences from retrieved chunks before prompting | Context budget pressure; noisy chunks | Extra LLM call; can drop needed detail |
| Metadata-filtered / self-query | LLM converts the question into a structured filter plus a search string (year, product, author) | Questions with explicit constraints | LLM call; filter must be validated against an allowlist |

### Control-flow patterns

| Pattern | Mechanism | Fixes | Cost |
|---|---|---|---|
| Conversational RAG | Condense chat history plus follow-up into a standalone query before retrieval | Follow-ups like "and for contractors?" | One LLM call per turn |
| Multi-hop / iterative | Retrieve, reason, form the next query, retrieve again, up to N hops | Answers chained across documents | Latency grows per hop |
| Corrective RAG (CRAG) | Grade retrieved chunks; if weak, rewrite and retry, or fall back to another source | Confident answers from irrelevant retrieval | Grader call(s) per query |
| Self-RAG | Model (or grader steps) decides whether to retrieve, then critiques relevance and support of its own draft | Unneeded retrieval; unsupported claims | Several LLM calls; needs bounded loop |
| Adaptive RAG | Classify the query and route: no retrieval, single-step RAG, or multi-step | Mixed easy/hard traffic; cost control | Router call; misrouting risk |
| Agentic RAG | Retrieval exposed as tools to an agent that plans, picks sources, retrieves repeatedly, and verifies (`agentic-ai.fundamentals.agent-loops`, `agentic-ai.tool-calling`) | Multiple heterogeneous sources; open-ended research | Highest cost and variance; needs loop bounds |
| Federated / multi-source RAG | Route to several indexes or systems, fuse results | Knowledge spread across systems | Routing plus per-source auth |

### Data-shape patterns

| Pattern | Mechanism | Fixes | Cost |
|---|---|---|---|
| Graph RAG | Extract entities and relations into a knowledge graph; traverse it and/or use community summaries | Relational questions across entities; corpus-wide "themes" questions | Heavy LLM cost at ingestion; graph upkeep |
| Structured / text-to-SQL RAG | LLM generates a read-only query against a database or API; results are the context | Numeric, tabular, aggregate questions | Injection and over-access risk; needs a query allowlist |
| Multimodal RAG | Retrieve images, tables, audio via captions or a multimodal embedding model; pass to a multimodal generator | Answers living in figures, slides, scans | Extraction/caption quality; larger context |
| Hierarchical / summary-tree RAG | Retrieve across chunk and summary levels (`agentic-ai.chunking`) | Questions at varying granularity | Ingestion LLM cost |
| Memory-augmented RAG | Retrieve from the user's or agent's memory alongside documents (`agentic-ai.memory`) | Personalized or session-continuous answers | Per-user isolation required |

### Alternatives to retrieval

| Approach | Mechanism | Use when |
|---|---|---|
| Long-context stuffing | Put the whole corpus in the prompt | Corpus is small (well under the context window), stable, and answers need cross-document reasoning |
| Cache-augmented generation (CAG) | Long-context stuffing with the corpus in a cached prompt prefix (`agentic-ai.cost-optimization`) | Same as above, with many queries over the same corpus |
| Fine-tuning | Bake behavior or style into the model | Style/format/skill, not facts that change; not a substitute for RAG on changing knowledge |

## Choosing a Pattern

| Observed failure (from the evaluation set) | Try, in order |
|---|---|
| Exact identifiers, codes, names not found | Hybrid search |
| Correct chunk in top-25 but not top-5 | Reranking |
| Chunk retrieved but meaningless alone | Contextual retrieval, parent-child (`agentic-ai.chunking`) |
| Short or vague queries return nothing useful | Query rewriting, HyDE, multi-query |
| Compound questions answered half-way | Query decomposition |
| Follow-up questions lose context | Conversational condensing |
| Answer needs facts from several documents in sequence | Multi-hop, then agentic RAG |
| Model answers confidently from irrelevant chunks | Relevance threshold, then Corrective RAG |
| Most queries are easy and cost is high | Adaptive routing |
| Relational or whole-corpus questions fail | Graph RAG, hierarchical summaries |
| Numeric/tabular questions answered wrongly | Text-to-SQL RAG |
| Answers live in images, charts, scans | Multimodal RAG |
| Corpus fits in context and is stable | Long-context / CAG, skip retrieval |
| Context budget exceeded or noisy | Reranking with smaller k, context compression |

## When the User Is Unsure
The user needs RAG but has not chosen a technique, a chunking strategy, or
an evaluation approach. Being unsure is not a blocker: do not stop the task
and do not ask the user to pick from the catalog above.
1. Check `.ai/config.yaml` -> `ai.rag`. If set, follow it and propose
   changes only with evaluation evidence. If unset, treat the project as
   undecided and continue with the steps below.
2. Discover before asking (`AGENTS.md` §7): inspect the corpus for content
   types, size, structure, update frequency, and the existing authorization
   model.
3. Ask at most three questions, and only those the project cannot answer:
   - What kinds of questions will users ask — single-fact lookups,
     multi-part, follow-ups in a conversation, summaries across many
     documents, or numbers/tables?
   - What is the latency and cost budget per query?
   - Who may see which content?

   If the user cannot answer, proceed on labeled assumptions: mostly
   fact lookups plus follow-ups, one retrieval and at most one extra LLM
   call per query, per-user authorization.
4. Choose chunking by content type from `agentic-ai.chunking` ("Choosing a
   Strategy").
5. Build the baseline (`agentic-ai.rag`): the chosen chunking, vector
   search, in-query authorization, citations, and an abstention path.
6. Build a starter evaluation set: 20-50 questions generated from the
   actual documents, including unanswerable and unauthorized cases, each
   with its expected source. Have the user review it before treating it as
   ground truth, and label it a starter set.
7. Run the baseline and classify failures with "Choosing a Pattern". Add
   upgrades one at a time, only for an observed failure, in this order:
   hybrid search, reranking, query-side patterns (rewriting,
   decomposition, conversational condensing), control-flow patterns
   (corrective, adaptive), and only then agentic RAG, Graph RAG,
   multimodal, or LLM-assisted chunking. Re-run the evaluation after each.
8. Question shape can decide a pattern before any measurement, because it
   is a requirement and not tuning: numeric/tabular/aggregate questions
   need text-to-SQL; conversational use needs history condensing;
   whole-corpus "themes" questions need hierarchical summaries or Graph
   RAG; a small, stable corpus makes long-context/CAG worth comparing.
9. Record the outcome in `ai.rag` in `.ai/config.yaml` and in the feature
   documentation: what was adopted and why, the evaluation results, and
   each rejected candidate with the failure that would justify revisiting
   it.

Never adopt Graph RAG, agentic RAG, or LLM-assisted chunking "to be safe":
each adds cost, latency, and attack surface that only a measured failure or
a data-shape requirement justifies.

## Step-by-Step Workflow
1. Confirm the baseline (`agentic-ai.rag`) is in place with an evaluation set
   covering answerable, unanswerable, and unauthorized cases.
2. Run the evaluation set and classify failures using the table above;
   record retrieval metrics and generation metrics separately.
3. Pick the cheapest pattern that targets the dominant failure; prefer
   retrieval-side fixes over adding LLM steps in the loop.
4. Implement it as a module behind an interface (`IQueryTransformer`,
   `IRetriever`, `IReranker`, `IRelevanceGrader`) so it composes and can be
   removed.
5. Bound every added step: iteration cap, token cap, timeout, and fallback.
6. Re-run the evaluation set; keep the pattern only if the target metric
   improves without regressing the others or breaking the latency/cost
   budget.
7. Add tracing for each stage (query variants, candidates, scores, grader
   decisions) so a bad answer can be diagnosed
   (`agentic-ai.observability`).
8. Verify authorization on every retrieval path the pattern introduced
   (sub-queries, fallbacks, graph traversal, tools).

## Code Standards
- Each stage is an interface with one job; the pipeline is a composition,
  not one large handler.
- Fusion, filtering, and scoring logic is pure and unit-testable, separate
  from I/O.
- Iteration limits and thresholds are named constants or options, not
  literals scattered through the code.
- LLM-calling stages return structured output validated against a schema
  (`agentic-ai.structured-outputs`).
- Follow `rules/csharp.md` and `rules/dotnet.md` for the rest.

## Architecture Constraints
- Retrieval, ranking, grading, and generation remain separable so each can
  be evaluated alone (`agentic-ai.rag` constraint).
- Agentic RAG is an agent-loop concern: use the loop bounds and tool
  boundaries from `agentic-ai.fundamentals.agent-loops` and
  `agentic-ai.tool-calling`; do not embed an unbounded loop inside a
  retriever.
- Graph stores, SQL connections, and web search sit behind ports like any
  other infrastructure (`dotnet.architecture.repository-specification`).

## Security Considerations
- Authorization is enforced inside every retrieval call, including graph
  traversal (edges must not reveal unauthorized entities) and generated
  queries.
- Text-to-SQL: run with a read-only, least-privilege database role against
  an allowlisted schema or views, with row-level security for the user;
  parse and validate generated SQL, cap row counts and execution time;
  never execute model output with the application's own privileges
  (`dotnet.security`).
- Web or external-source fallbacks (CRAG) can leak the user's query and
  private context to a third party; send only sanitized queries and only if
  data-handling policy allows.
- Rewritten, decomposed, and hypothetical queries are model output derived
  from user input; treat them as untrusted and re-apply filters on top.
- Metadata filters produced by self-query must be validated against an
  allowlist of fields and values; never concatenate them into queries.
- Retrieved text, captions, and graph summaries can carry injected
  instructions; keep them delimited and untrusted at generation time
  (`agentic-ai.ai-security`).

## Testing Requirements
- Unit: fusion (RRF), thresholding, and deduplication logic with fixed
  inputs and expected order.
- Unit: every LLM stage's output validation with malformed and hostile
  outputs; loop caps terminate with the defined fallback.
- Integration: authorization holds on every retrieval path — user A never
  receives user B's content through hybrid, sub-query, fallback, graph, or
  SQL paths.
- Evaluation: per-pattern before/after on the same question set for
  recall@k, MRR/nDCG, context precision, groundedness, answer relevance,
  abstention on unanswerable questions, plus latency and cost per query.
- Regression: the "not answerable" cases still abstain after the pattern is
  added.

## Common Mistakes
- Adding a fashionable pattern (Graph RAG, agentic RAG) with no evaluation
  showing the baseline failed on the questions it addresses.
- Reranking or rewriting without a baseline comparison, so the added
  latency buys nothing measurable.
- Filtering by authorization on the first retrieval but not on rewritten,
  decomposed, or fallback retrievals.
- Grading relevance against the rewritten query, so a drifted rewrite
  passes its own grader.
- Unbounded corrective or multi-hop loops that retry until cost or time is
  exhausted.
- Hybrid search that mixes raw BM25 and cosine scores directly; the scales
  differ. Use rank-based fusion (RRF) or normalize first.
- Reranking a candidate set too small to contain the answer (retrieve 3,
  rerank to 3).

## Anti-Patterns
- **Pattern stacking**: enabling hybrid, multi-query, HyDE, reranking, and
  self-RAG simultaneously, so latency and cost balloon and failures cannot
  be attributed to any one stage.
- **Agentic by default**: routing simple lookups through a planning agent
  when a single retrieval would do.
- **Unsupervised fallback**: sending a failed private query to a web search
  API with no policy check.
- **Graph without a graph question**: paying for entity extraction over a
  corpus whose questions are single-document fact lookups.
- **Confident retry**: a corrective loop that ends by answering from the
  last weak results instead of abstaining.

## Validation Checklist
- [ ] Baseline naive RAG and its evaluation results exist before any
      pattern is added.
- [ ] Each adopted pattern maps to a measured failure and improved the
      target metric.
- [ ] Every added LLM step has iteration, token, and time bounds and a
      defined fallback.
- [ ] Authorization is enforced inside every retrieval path the pattern
      adds.
- [ ] Relevance grading uses the original question.
- [ ] The abstention ("not answerable") path still works.
- [ ] Rank-based fusion or score normalization is used when merging
      retrievers.
- [ ] Generated SQL/filters are validated and run least-privilege.
- [ ] Latency and cost per query are measured against budget.
- [ ] Stage-level traces exist for diagnosis.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; each adopted
pattern has a before/after evaluation result, a bounded control flow, and an
authorization test on every retrieval path it introduced.

## Example
Hybrid retrieval fused with Reciprocal Rank Fusion, wrapped in a bounded
corrective loop that abstains when nothing relevant is found.

```csharp
public sealed record ScoredChunk(Guid Id, string Text, double Score);

public interface IVectorSearchService
{
    Task<IReadOnlyList<ScoredChunk>> QueryAsync(string queryText, int topK, Guid authorizedFor, CancellationToken ct);
}

public interface IKeywordSearchService
{
    Task<IReadOnlyList<ScoredChunk>> QueryAsync(string queryText, int topK, Guid authorizedFor, CancellationToken ct);
}

public interface IRelevanceGrader
{
    Task<IReadOnlyList<ScoredChunk>> KeepRelevantAsync(string question, IReadOnlyList<ScoredChunk> chunks, CancellationToken ct);
}

public interface IQueryRewriter
{
    Task<string> RewriteAsync(string question, CancellationToken ct);
}

public static class ReciprocalRankFusion
{
    // Rank-based, so BM25 and cosine scores never need a shared scale.
    public static IReadOnlyList<ScoredChunk> Fuse(
        IEnumerable<IReadOnlyList<ScoredChunk>> rankedLists, int topK, int k = 60)
    {
        var fused = new Dictionary<Guid, (ScoredChunk Chunk, double Score)>();
        foreach (var list in rankedLists)
        {
            for (var rank = 0; rank < list.Count; rank++)
            {
                var chunk = list[rank];
                var contribution = 1.0 / (k + rank + 1);
                fused[chunk.Id] = fused.TryGetValue(chunk.Id, out var existing)
                    ? (existing.Chunk, existing.Score + contribution)
                    : (chunk, contribution);
            }
        }

        return fused.Values
            .OrderByDescending(x => x.Score)
            .Take(topK)
            .Select(x => x.Chunk with { Score = x.Score })
            .ToList();
    }
}

public sealed class HybridRetriever(IVectorSearchService dense, IKeywordSearchService sparse)
{
    private const int CandidateMultiplier = 5;

    public async Task<IReadOnlyList<ScoredChunk>> RetrieveAsync(string query, Guid userId, int topK, CancellationToken ct)
    {
        var candidates = topK * CandidateMultiplier;

        // Both searches apply the authorization filter inside the query.
        var denseTask = dense.QueryAsync(query, candidates, userId, ct);
        var sparseTask = sparse.QueryAsync(query, candidates, userId, ct);
        await Task.WhenAll(denseTask, sparseTask);

        return ReciprocalRankFusion.Fuse([await denseTask, await sparseTask], topK);
    }
}

public sealed class CorrectiveRagHandler(
    HybridRetriever retriever,
    IRelevanceGrader grader,
    IQueryRewriter rewriter,
    IChatClient model)
{
    private const int MaxRewrites = 1; // bounded loop: rules/agentic-ai.md

    public async Task<RagAnswer> AnswerAsync(string question, Guid userId, CancellationToken ct)
    {
        var query = question;

        for (var attempt = 0; attempt <= MaxRewrites; attempt++)
        {
            var candidates = await retriever.RetrieveAsync(query, userId, topK: 8, ct);

            // Grade against the ORIGINAL question so a drifted rewrite cannot vouch for itself.
            var relevant = await grader.KeepRelevantAsync(question, candidates, ct);
            if (relevant.Count > 0)
                return await GenerateAsync(question, relevant, ct);

            if (attempt < MaxRewrites)
                query = await rewriter.RewriteAsync(question, ct);
        }

        return RagAnswer.NotFound("No relevant documents were found for this question.");
    }

    private async Task<RagAnswer> GenerateAsync(string question, IReadOnlyList<ScoredChunk> chunks, CancellationToken ct)
    {
        var context = string.Join("\n\n", chunks.Select(c => $"<source id=\"{c.Id}\" untrusted=\"true\">{c.Text}</source>"));
        var answer = await model.GetResponseAsync(
            RagPrompts.System,
            $"Question: {question}\n\nSources:\n{context}\n\nAnswer only from the sources above. If they don't answer the question, say so.",
            ct);

        return RagAnswer.Success(answer.Text, sourceIds: chunks.Select(c => c.Id).ToList());
    }
}
```

Test:
```csharp
public class ReciprocalRankFusionTests
{
    [Fact]
    public void Chunk_ranked_by_both_retrievers_outranks_single_retriever_hits()
    {
        var shared = new ScoredChunk(Guid.NewGuid(), "shared", 0.5);
        var denseOnly = new ScoredChunk(Guid.NewGuid(), "dense", 0.9);
        var sparseOnly = new ScoredChunk(Guid.NewGuid(), "sparse", 12.4); // BM25 scale differs; irrelevant to RRF

        var fused = ReciprocalRankFusion.Fuse([[denseOnly, shared], [sparseOnly, shared]], topK: 3);

        Assert.Equal(shared.Id, fused[0].Id);
        Assert.Equal(3, fused.Count);
    }
}
```
Trade-off: hybrid retrieval and one grader call add latency and cost to every query. The grader call and the rewrite retry are the price of abstaining instead of guessing; drop the loop (keep `HybridRetriever`) if the evaluation set shows retrieval is already reliable. `IChatClient`, `RagAnswer`, and `RagPrompts` are the types from `agentic-ai.rag`.

## Related Skills
- `agentic-ai.rag` (requires) — the baseline pipeline, authorization filtering, and citations every pattern extends.
- `agentic-ai.chunking` — parent-child, contextual, and hierarchical chunking that several patterns depend on.
- `agentic-ai.vector-search` — dense retrieval and in-query authorization used by every pattern.
- `agentic-ai.embeddings` — models for dense, multimodal, and query embeddings.
- `agentic-ai.evaluation` — the before/after measurement that justifies any pattern.
- `agentic-ai.observability` — stage-level tracing of multi-step pipelines.
- `agentic-ai.cost-optimization` — budgets, caching, and the CAG option.
- `agentic-ai.fundamentals.agent-loops` and `agentic-ai.tool-calling` — bounds and tool boundaries for agentic RAG.
- `agentic-ai.model-routing` — routing queries and stages to appropriately sized models.
- `agentic-ai.memory` — memory-augmented retrieval.
- `agentic-ai.ai-security` — untrusted retrieved and generated content.
- `dotnet.database.postgresql` — full-text and `pgvector` hybrid search in one database.
