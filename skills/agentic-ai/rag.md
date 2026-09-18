---
id: agentic-ai.rag
title: RAG (Retrieval-Augmented Generation)
category: skill
domain: agentic-ai
technologies: [dotnet, aspnetcore, embeddings, vector-search]
triggers: [rag, retrieval augmented generation, knowledge base q&a, document search with llm, grounded answers]
requires: [dotnet.api-design, dotnet.efcore]
related: [dotnet.database.postgresql, dotnet.security, agentic-ai.evaluation, agentic-ai.observability, agentic-ai.embeddings, agentic-ai.vector-search]
optional: [agentic-ai.frameworks.semantic-kernel]
prerequisites: [agentic-ai.embeddings, agentic-ai.vector-search]
tags: [rag, retrieval, embeddings, agents]
---

# RAG (Retrieval-Augmented Generation)

## Purpose
Ground an LLM's answer in retrieved, authoritative content instead of
relying on its training data alone — retrieve relevant chunks from a
knowledge source, and require the model to answer from them.

## When to Use
Question-answering or generation tasks over a specific, changing, or
private knowledge base (documentation, support articles, internal data) —
where you need answers grounded in that source, with citations, rather than
the model's general knowledge.

## Prerequisites
`agentic-ai.embeddings`, `agentic-ai.vector-search`.

## Inputs Required
The knowledge source (documents, database records), its update frequency
(drives re-indexing strategy), and whether answers need citations back to
source.

## Engineering Principles
1. Chunk documents at a size that keeps semantic coherence (a chunk should
   be a complete-enough thought to be useful alone) while fitting
   comfortably in context alongside several other retrieved chunks.
2. Retrieve top-k relevant chunks by vector similarity
   (`agentic-ai.vector-search`), optionally re-ranked, and pass only those
   into context — not the whole knowledge base.
3. Instruct the model explicitly to answer only from the retrieved content
   and to say so when the retrieved content doesn't answer the question —
   don't let it silently fall back to unsourced training knowledge.
4. Cite sources — track which chunk(s) informed which part of the answer,
   so the response is verifiable, not just plausible-sounding.
5. Re-indexing strategy matches the knowledge source's actual update
   frequency — a nightly batch re-index is fine for slowly-changing docs;
   near-real-time indexing is needed if content changes are meant to be
   immediately reflected.

## Step-by-Step Workflow
1. Chunk source documents at an appropriate size/overlap; store chunks with
   their embeddings (`agentic-ai.embeddings`) and metadata (source, section,
   last-updated).
2. On a query, embed the query and retrieve top-k relevant chunks
   (`agentic-ai.vector-search`); optionally re-rank for relevance.
3. Assemble context from the retrieved chunks, clearly delineated as
   retrieved/untrusted content distinct from system instructions
   (`agentic-ai.context-engineering`, `agentic-ai.ai-security`).
4. Prompt the model to answer only from the provided context and to state
   when it can't answer from what was retrieved.
5. Return the answer with citations back to the source chunks.
6. Build an evaluation set (`agentic-ai.evaluation`) of representative
   questions with known-correct answers/sources to measure retrieval and
   answer quality, not just "it looks right."

## Code Standards
Chunk and embedding storage uses the project's normal database
(`dotnet.database.postgresql` + `pgvector`, or a dedicated vector store),
accessed through the same repository pattern as any other data
(`dotnet.architecture.repository-specification`).

## Architecture Constraints
The retrieval step and the generation step are separable and independently
testable — retrieval quality (are the right chunks found) and answer
quality (does the model use them well) are different failure modes and
need different evaluation.

## Security Considerations
Retrieved content is untrusted input to the prompt, even though it comes
from "your own" knowledge base — if that knowledge base includes
user-generated or externally-sourced content, it could contain a
prompt-injection attempt (`agentic-ai.ai-security`). Authorization matters
at retrieval time too — a user must not retrieve chunks from documents
they're not authorized to see; filter by permission before (or as part of)
the vector search, not after.

## Testing Requirements
Evaluation set covering: questions answerable from the knowledge base
(verify correct answer + correct citation), questions NOT answerable from
it (verify the model says so instead of hallucinating), and an
authorization case (verify a user doesn't receive content they're not
permitted to see).

## Common Mistakes
- No authorization filter on retrieval, leaking content across permission
  boundaries through the RAG pipeline even though the direct document
  access path is properly secured.
- Chunks too large (diluting relevance, wasting context budget) or too
  small (losing necessary surrounding context for coherent understanding).
- No "I don't know" path — the model always produces a confident-sounding
  answer even when retrieval found nothing relevant.

## Anti-Patterns
- **Retrieve everything**: passing the entire top-100 results into context
  instead of a relevance-filtered top-k, diluting the model's attention and
  wasting budget.
- **Unlabeled trust**: mixing retrieved content into the prompt
  indistinguishably from system instructions, widening the prompt-injection
  surface.

## Validation Checklist
- [ ] Retrieval is authorization-filtered per user/tenant.
- [ ] Retrieved content is clearly delineated as untrusted in the prompt.
- [ ] The model has an explicit "not answerable from context" fallback.
- [ ] Answers include citations to the retrieved source(s).
- [ ] An evaluation set measures retrieval and answer quality separately.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; evaluation
set covers answerable, unanswerable, and unauthorized-access cases.

## Example
```csharp
public sealed class RagQueryHandler(IVectorSearchService search, IChatClient model)
{
    public async Task<RagAnswer> AnswerAsync(string question, Guid userId, CancellationToken ct)
    {
        var chunks = await search.QueryAsync(question, topK: 5, authorizedFor: userId, ct); // authz-filtered
        if (chunks.Count == 0)
            return RagAnswer.NotFound("No relevant documents were found for this question.");

        var context = string.Join("\n\n", chunks.Select(c => $"<source id=\"{c.Id}\" untrusted=\"true\">{c.Text}</source>"));
        var answer = await model.GetResponseAsync(
            RagPrompts.System,
            $"Question: {question}\n\nSources:\n{context}\n\nAnswer only from the sources above. If they don't answer the question, say so.",
            ct);

        return RagAnswer.Success(answer.Text, sourceIds: chunks.Select(c => c.Id).ToList());
    }
}
```

## Related Skills
- `agentic-ai.embeddings` — how chunks are vectorized.
- `agentic-ai.vector-search` — the retrieval mechanism.
- `agentic-ai.evaluation` — measuring retrieval and answer quality.
- `dotnet.database.postgresql` — `pgvector`-based storage option.
