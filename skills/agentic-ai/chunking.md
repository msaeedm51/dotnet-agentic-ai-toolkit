---
id: agentic-ai.chunking
title: Chunking Strategies
category: skill
domain: agentic-ai
technologies: [dotnet, embeddings, vector-search]
triggers: [chunking, chunking strategy, chunk size, chunk overlap, text splitter, document splitting, semantic chunking, parent child chunks, late chunking, contextual chunks]
requires: [agentic-ai.embeddings]
related: [agentic-ai.rag, agentic-ai.rag-patterns, agentic-ai.vector-search, agentic-ai.evaluation, agentic-ai.ai-security]
optional: []
prerequisites: [agentic-ai.embeddings]
tags: [chunking, rag, retrieval, ingestion]
---

# Chunking Strategies

## Purpose
Split source content into retrievable units that are each coherent enough
to be useful alone, small enough to embed precisely, and traceable back to
their source. Chunking is the single biggest ingestion-time lever on
retrieval quality, and it has enough distinct strategies (structural,
semantic, hierarchical, LLM-assisted) that it is its own skill rather than a
paragraph inside `agentic-ai.rag`.

## When to Use
- Building or tuning an ingestion pipeline for RAG or semantic search.
- Retrieval returns the right document but the wrong passage, or a passage
  missing the context needed to answer.
- Choosing chunk size/overlap, or deciding whether an expensive strategy
  (semantic, parent-child, contextual) is worth it.
- Ingesting content that is not plain prose: source code, tables, PDFs,
  chat logs, database records.

## Prerequisites
`agentic-ai.embeddings` (chunk size is bounded by the embedding model's max
input and measured in its tokenizer). Read `agentic-ai.rag` for how chunks
are consumed.

## Inputs Required
- Content types in the corpus (prose, Markdown/HTML, code, tables, PDFs,
  transcripts, records) — discoverable by inspecting the source.
- Embedding model and its max input tokens — from `.ai/config.yaml` or the
  project's embedding client.
- The kinds of questions users ask (fact lookup vs. explanation vs.
  cross-section synthesis) — ask if unknown; it drives chunk size.
- Access-control model (which permission attaches to which document) — every
  chunk inherits it.

## Engineering Principles
1. Split on the content's own structure first (headings, sections,
   functions, rows, turns); use size-based splitting only inside a
   structural unit that is still too large.
2. Measure size in tokens of the embedding model's tokenizer, never
   characters. A chunk over the model's max input is silently truncated.
3. Never split what must stay whole: a table with its header row, a code
   block, a list with its lead-in sentence, a Q&A pair, a legal clause with
   its numbering.
4. Every chunk carries provenance: document id, source URI, heading path,
   ordinal, page or offset range, content hash, and the chunker name and
   version. Citations and incremental re-indexing depend on it.
5. The chunker is deterministic and versioned. Changing strategy or
   parameters means re-chunking and re-embedding — treat it like an
   embedding-model change (`agentic-ai.embeddings`), not a config tweak.
6. Pick by measurement. Start with the cheapest strategy that respects
   structure, then adopt semantic, hierarchical, or LLM-assisted strategies
   only when the evaluation set (`agentic-ai.evaluation`) shows a retrieval
   failure they fix.
7. Every chunk inherits the access-control metadata of its source document,
   including derived chunks (parents, summaries, context headers). Do not
   drop it during transformation.
8. Treat source content as untrusted when an LLM processes it at ingestion
   time (contextualization, propositions, summaries): an injected
   instruction in a document must not steer the ingestion model
   (`agentic-ai.ai-security`).

## Step-by-Step Workflow
1. Inventory the content types and pick a strategy per type from the table
   below — do not force one strategy across a mixed corpus.
2. Parse the structure (Markdown/HTML headings, DOCX styles, PDF layout,
   Roslyn syntax tree for C#) before splitting text.
3. Split along structure; recursively split oversized units using the
   separator ladder `paragraph -> line -> sentence -> word`.
4. Apply overlap (10-20% of chunk size) only for size-based splits where
   an idea can straddle a boundary; structural splits usually need none.
5. Attach metadata (principle 4) and the source document's ACL
   (principle 7). Prepend or store the heading path so the chunk is
   self-describing when embedded.
6. If using parent-child, sentence-window, or contextual chunking, store
   both the retrieval unit and the context unit and link them by id.
7. Hash each chunk's normalized text; skip re-embedding unchanged chunks
   (`agentic-ai.embeddings`).
8. Build a retrieval evaluation set and compare candidate strategies on
   recall@k and context precision before adopting one.

## Strategy Catalog

| Strategy | How it splits | Best for | Cost / trade-off |
|---|---|---|---|
| Fixed-size (token) | Cut every N tokens | Baseline; homogeneous plain text | Cuts mid-sentence; ignores structure |
| Sliding window (fixed + overlap) | Fixed-size with 10-20% overlap | Ideas that straddle boundaries | Larger index; near-duplicate hits |
| Sentence-based | Group whole sentences up to a size | FAQs, short prose, transcripts | Uneven chunk sizes |
| Recursive separator | Paragraph, then line, sentence, word, until it fits | **Default for prose** | Ignores headings and semantics |
| Structure-aware | Split on headings/sections; keep heading path | Docs, wikis, manuals, legal, policies | Needs parseable structure |
| Code-aware (AST) | One chunk per type/method/member, with signature and namespace | Source code | Language-specific parser; huge members need sub-splitting |
| Table / layout-aware | Keep table rows with headers; use PDF layout extraction or OCR | PDFs, spreadsheets, invoices, forms | Extraction quality is the bottleneck |
| Record-based | One chunk per row/ticket/message/product | Structured data, tickets, CRM | Records may be too small or too large |
| Conversation / turn-based | Group by speaker turns or time windows | Chat logs, call transcripts | Needs a time/turn boundary policy |
| Semantic | Embed sentences; split where adjacent similarity drops | Long text that shifts topic without headings | Ingestion embedding cost; unstable across model versions |
| Parent-child (small-to-big) | Embed small children; return the larger parent | Precision in matching plus context in answering | Two-level storage and lookup |
| Sentence-window | Embed one sentence; return it with +/- k neighbors | Dense prose where one sentence carries the fact | Neighbor lookup at query time |
| Hierarchical / summary tree | Chunks, section summaries, document summaries (RAPTOR-style) | Corpus-wide or multi-section questions | LLM cost at ingestion; summaries can drift |
| Proposition / agentic | LLM rewrites content into atomic, self-contained statements, or picks boundaries | High-value dense content (policies, specs) | LLM cost; rewriting can introduce errors |
| Contextual | LLM prepends a short chunk-specific context ("This is from the Q3 2025 ACME filing...") before embedding and keyword indexing | Chunks that are ambiguous alone | LLM call per chunk; reduce with prompt caching |
| Late chunking | Embed the whole document with a long-context embedding model, then pool token vectors per chunk | Chunks that depend on document-wide context | Needs a long-context embedding model that exposes token vectors |
| Multimodal | Caption images/diagrams or embed with a multimodal model; keep figure and caption together | Manuals, slides, scanned docs | Caption quality; extra model dependency |

## Choosing a Strategy

| Content / symptom | Start with | Escalate to |
|---|---|---|
| Prose articles, emails | Recursive separator, 300-500 tokens, 10-15% overlap | Contextual if chunks are ambiguous |
| Markdown/HTML docs, wikis | Structure-aware with heading path | Parent-child (section as parent) |
| Legal, policy, contracts | Structure-aware by clause; never split a clause | Proposition or contextual chunking |
| Source code | Code-aware by member | Add file/namespace summary chunk |
| PDFs with tables/figures | Layout-aware extraction; table as one unit | Multimodal |
| Support tickets, CRM, catalog | Record-based | Add a per-record summary |
| Chat/call transcripts | Turn-window with overlap | Hierarchical summaries |
| Answers need surrounding text | Parent-child or sentence-window | Late chunking |
| Chunk retrieved but meaningless alone ("it grew 3%") | Contextual chunking | Proposition chunking |
| Questions span the whole corpus ("main themes") | Hierarchical summary tree | Graph RAG (`agentic-ai.rag-patterns`) |

## Sizing Guidance
Starting points to evaluate, not defaults to ship:
- Fact lookup and FAQ: 150-300 tokens.
- Explanations and how-to: 400-800 tokens.
- Parent chunks: 1000-2000 tokens; child chunks: 100-300 tokens.
- Overlap: 10-20% for size-based splits, 0 for clean structural splits.
- Hard ceiling: the embedding model's max input, minus any prepended
  context header.
- Retrieval budget: `top_k x chunk size` must fit the context window with
  room for instructions and the answer (`agentic-ai.context-engineering`).

## Code Standards
- The chunker sits behind `IChunker` and takes a source document, returning
  chunks with provenance. The ingestion pipeline depends on the interface,
  so strategies are swappable per content type.
- Token counting sits behind `ITokenCounter`, backed by the embedding
  model's tokenizer.
- Chunk records are immutable (`record`), with a stable id derived from
  document id, ordinal, and content hash so re-runs are idempotent.
- Follow `rules/csharp.md` for the rest.

## Architecture Constraints
Chunking is an ingestion-layer concern. Query-time code never re-chunks; it
reads what ingestion produced. The chunker does not call the embedding
service or the vector store — the indexer composes them
(`agentic-ai.embeddings`), which keeps each stage independently testable.

## Security Considerations
- ACL metadata is copied to every chunk and every derived unit; a chunk
  without it is unfilterable (`agentic-ai.vector-search`).
- Redact secrets and prohibited PII before chunks leave the infrastructure
  for an external embedding or contextualization provider
  (`agentic-ai.embeddings`).
- LLM-assisted strategies read untrusted documents: constrain the ingestion
  prompt, validate output shape, and cap output length
  (`agentic-ai.ai-security`, `agentic-ai.structured-outputs`).
- Do not put one tenant's content into another tenant's parent chunk,
  summary, or shared context header.

## Testing Requirements
- Unit: no chunk exceeds the token limit; concatenated chunks cover the
  source with no lost text; overlap is present where configured (test with
  an overlap budget that fits at least one splitting unit — see the
  trade-off note in the example).
- Unit: tables, code blocks, and lists are never split mid-unit.
- Unit: chunk ids and hashes are stable across runs on identical input.
- Unit: each chunk carries provenance and the source ACL.
- Evaluation: compare candidate strategies on the same question set using
  recall@k, MRR, and context precision; the chosen strategy must beat the
  baseline on the metric that matches the failure being fixed.

## Common Mistakes
- Sizing by characters or words, so chunks exceed the embedding model's
  limit and are silently truncated.
- One strategy for the whole corpus, so tables are mangled by a prose
  splitter or code is split mid-method.
- Overlap on structural splits, producing near-duplicate hits that crowd out
  distinct results in top-k.
- Chunks with no heading path or document title, so retrieved text is
  ambiguous ("the limit is 5") and unciteable.
- Adopting semantic or LLM-assisted chunking without a baseline comparison.
- Changing chunk size in place, leaving old and new chunks mixed in one
  index.

## Anti-Patterns
- **Chunk-size cargo cult**: copying "512 tokens, 50 overlap" from a
  tutorial without measuring it on the project's questions and content.
- **Lossy splitting**: dropping headers, table headers, or list lead-ins
  during splitting so the chunk is no longer self-describing.
- **Unversioned chunker**: no record of which chunker and parameters
  produced a chunk, making re-indexing and debugging guesswork.
- **Summary-only index**: embedding only LLM summaries and discarding the
  source text, so answers cannot be grounded or cited.

## Validation Checklist
- [ ] A strategy is chosen per content type, with the reason recorded.
- [ ] Size is measured with the embedding model's tokenizer and stays under
      its limit including any prepended context.
- [ ] Tables, code blocks, and lists are kept whole.
- [ ] Every chunk has provenance, chunker version, content hash, and ACL.
- [ ] Chunker output is deterministic; ids and hashes are stable.
- [ ] Candidate strategies were compared on an evaluation set.
- [ ] LLM-assisted ingestion treats content as untrusted and is
      cost-bounded.

## Definition of Done
Meets `rules/definition-of-done.md` and `rules/agentic-ai.md`; the chosen
strategy has an evaluation result against a baseline, and the
size/structure/provenance tests above pass.

## Example
A recursive splitter that respects a token budget with overlap, wrapped by a
Markdown chunker that splits on headings and keeps the heading path.

```csharp
public interface ITokenCounter
{
    int Count(string text);
}

public sealed record SourceDocument(Guid Id, string Uri, string Markdown, IReadOnlySet<Guid> AllowedUserIds);

public sealed record Chunk(
    Guid Id,
    Guid DocumentId,
    int Ordinal,
    string Text,
    string HeadingPath,
    string ContentHash,
    string ChunkerVersion,
    IReadOnlySet<Guid> AllowedUserIds);

public interface IChunker
{
    IReadOnlyList<Chunk> Chunk(SourceDocument document);
}

public sealed class RecursiveTextSplitter(ITokenCounter tokens, int maxTokens, int overlapTokens)
{
    private static readonly string[] Separators = ["\n\n", "\n", ". ", " "];

    public IReadOnlyList<string> Split(string text) => Split(text, level: 0);

    private List<string> Split(string text, int level)
    {
        if (tokens.Count(text) <= maxTokens)
            return [text];
        if (level >= Separators.Length)
            return [text]; // a single unbreakable token run; nothing left to split on

        var separator = Separators[level];
        var pieces = new List<string>();
        var window = new List<string>();
        var windowTokens = 0;
        var fresh = 0; // parts in the window not yet emitted (excludes carried overlap)

        void Emit()
        {
            pieces.Add(string.Join(separator, window));
            var carried = new List<string>();
            var carriedTokens = 0;
            for (var i = window.Count - 1; i >= 0; i--)
            {
                var t = tokens.Count(window[i]);
                if (carriedTokens + t > overlapTokens) break;
                carried.Insert(0, window[i]);
                carriedTokens += t;
            }
            window = carried;
            windowTokens = carriedTokens;
            fresh = 0;
        }

        foreach (var part in text.Split(separator))
        {
            var partTokens = tokens.Count(part);

            if (partTokens > maxTokens)
            {
                if (fresh > 0) Emit();
                window.Clear();
                windowTokens = 0;
                pieces.AddRange(Split(part, level + 1));
                continue;
            }

            if (fresh > 0 && windowTokens + partTokens > maxTokens)
                Emit();

            // carried overlap must never push the next chunk over the limit
            while (window.Count > 0 && windowTokens + partTokens > maxTokens)
            {
                windowTokens -= tokens.Count(window[0]);
                window.RemoveAt(0);
            }

            window.Add(part);
            windowTokens += partTokens;
            fresh++;
        }

        if (fresh > 0)
            pieces.Add(string.Join(separator, window));
        return pieces;
    }
}

public sealed class MarkdownChunker(RecursiveTextSplitter splitter) : IChunker
{
    private const string Version = "markdown-recursive/1";

    public IReadOnlyList<Chunk> Chunk(SourceDocument document)
    {
        var chunks = new List<Chunk>();
        var headings = new List<string>();
        var body = new StringBuilder();

        void FlushSection()
        {
            var text = body.ToString().Trim();
            body.Clear();
            if (text.Length == 0) return;

            var path = string.Join(" > ", headings);
            foreach (var piece in splitter.Split(text))
            {
                var hash = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(piece)));
                var ordinal = chunks.Count;
                chunks.Add(new Chunk(
                    Id: DeterministicId(document.Id, ordinal, hash),
                    DocumentId: document.Id,
                    Ordinal: ordinal,
                    Text: piece,
                    HeadingPath: path,
                    ContentHash: hash,
                    ChunkerVersion: Version,
                    AllowedUserIds: document.AllowedUserIds)); // ACL inherited by every chunk
            }
        }

        foreach (var line in document.Markdown.Split('\n'))
        {
            var level = HeadingLevel(line);
            if (level == 0)
            {
                body.AppendLine(line);
                continue;
            }

            FlushSection();
            if (headings.Count >= level) headings.RemoveRange(level - 1, headings.Count - level + 1);
            headings.Add(line.TrimStart('#').Trim());
        }
        FlushSection();
        return chunks;
    }

    private static int HeadingLevel(string line)
    {
        var hashes = line.TakeWhile(c => c == '#').Count();
        return hashes is > 0 and <= 6 && line.Length > hashes && line[hashes] == ' ' ? hashes : 0;
    }

    private static Guid DeterministicId(Guid documentId, int ordinal, string hash)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes($"{documentId}:{ordinal}:{hash}"));
        return new Guid(bytes.AsSpan(0, 16));
    }
}
```

Test:
```csharp
public sealed class WhitespaceTokenCounter : ITokenCounter
{
    public int Count(string text) => text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries).Length;
}

public class MarkdownChunkerTests
{
    private readonly MarkdownChunker _chunker = new(new RecursiveTextSplitter(new WhitespaceTokenCounter(), maxTokens: 20, overlapTokens: 5));

    [Fact]
    public void Chunks_stay_under_limit_keep_heading_path_and_inherit_acl()
    {
        var owner = Guid.NewGuid();
        var body = string.Join(" ", Enumerable.Range(1, 60).Select(i => $"word{i}"));
        var doc = new SourceDocument(Guid.NewGuid(), "kb://leave-policy", $"# Leave\n## Sick leave\n{body}", new HashSet<Guid> { owner });

        var chunks = _chunker.Chunk(doc);

        Assert.All(chunks, c =>
        {
            Assert.True(new WhitespaceTokenCounter().Count(c.Text) <= 20);
            Assert.Equal("Leave > Sick leave", c.HeadingPath);
            Assert.Contains(owner, c.AllowedUserIds);
        });
        Assert.True(chunks.Count > 1);
    }
}
```
Trade-off: overlap is carried in whole separator units (paragraphs, lines, sentences, or words at the level that produced the split), keeping chunks on natural boundaries. If every unit at that level is larger than `overlapTokens`, no overlap is carried — set `overlapTokens` at least as large as a typical sentence, or accept zero overlap for that content. A single unbreakable run longer than `maxTokens` (a base64 blob, a minified line) is emitted whole and exceeds the limit; strip or handle such content before chunking.

## Related Skills
- `agentic-ai.embeddings` (requires) — token limits, batching, and re-embedding on change.
- `agentic-ai.rag` — consumes chunks; owns the retrieve-and-generate flow.
- `agentic-ai.rag-patterns` — parent-child, contextual, and graph RAG build on chunking choices made here.
- `agentic-ai.vector-search` — stores chunks and enforces ACL filtering at query time.
- `agentic-ai.evaluation` — the recall@k comparison that justifies a strategy.
- `agentic-ai.ai-security` — untrusted content in LLM-assisted ingestion.
