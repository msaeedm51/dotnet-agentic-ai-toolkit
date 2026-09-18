---
id: agentic-ai.context-engineering
title: Context Engineering
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [context window, context management, what to put in context, context pruning, context budget]
requires: []
related: [agentic-ai.prompt-engineering, agentic-ai.memory, agentic-ai.fundamentals.agent-loops, agentic-ai.cost-optimization]
optional: []
prerequisites: []
tags: [agents, context]
---

# Context Engineering

## Purpose
Deliberately decide what goes into the model's context window at each
call — system instructions, conversation history, retrieved documents,
tool results — instead of accumulating everything by default until the
window fills up or cost balloons. Covers both the up-front design ("context
engineering") and the ongoing runtime management of what stays in ("context
management") as one concern.

## When to Use
Every agent/LLM call with more than a single static prompt — any
multi-turn conversation, agent loop, or RAG pipeline.

## Prerequisites
None.

## Inputs Required
The model's actual context window limit, the cost per token for the model
in use, and which pieces of available information are actually relevant to
the current step (not just available).

## Engineering Principles
1. Context is a budget, not a dumping ground — every token included has a
   cost (latency, price, and the model's attention diluted across
   everything present).
2. Include what's relevant to *this* step, not the full history of
   everything that's happened — summarize or drop what's no longer
   load-bearing.
3. Order matters for some models/tasks — put the most important
   instructions/context where the model attends to it most reliably
   (typically start and end of the context); don't bury a critical
   constraint in the middle of a long document dump.
4. Tool results are trimmed to what the model needs, not the full raw
   payload — a database query returning 500 rows doesn't belong in context
   verbatim; summarize, paginate, or let the model request more if needed.
5. Long-running conversations need a summarization/compaction strategy
   before hitting the context limit, not a hard failure when they do.

## Step-by-Step Workflow
1. Identify every candidate piece of context for this call: system
   instructions, task, conversation history, retrieved documents, prior
   tool results.
2. For each, decide: is it relevant to this specific step, and does it need
   to be in full or summarized form?
3. Trim tool results and retrieved documents to the specific fields/
   passages relevant to the task, not the entire raw object/document.
4. For long conversations, implement a compaction strategy: summarize older
   turns, keep recent turns verbatim, or use `agentic-ai.memory` for
   information that should persist beyond the current context window.
5. Monitor actual token usage per call (`agentic-ai.observability`,
   `agentic-ai.cost-optimization`) to catch context bloat before it becomes
   a cost or reliability problem.

## Code Standards
Context assembly is a distinct, testable function/class — not implicitly
built by string-concatenating whatever happens to be in scope at the call
site.

## Architecture Constraints
Context assembly logic is separate from the model-calling code, so it can
be tested and evaluated independently of the actual API call.

## Security Considerations
Content from untrusted sources (user input, retrieved documents, tool
output) included in context must be clearly delineated from trusted
system/developer instructions — and the model instructed (and, more
importantly, the calling code designed) to treat it as data, not
instructions (`agentic-ai.ai-security` — the same instruction-source
boundary this toolkit's own `AGENTS.md` enforces for the AI assistant using
this repo applies equally to any agent you build with it).

## Testing Requirements
Evaluation cases with long/edge-case context (many turns, large retrieved
documents) verifying the compaction/trimming strategy keeps the model
performant and within budget, and doesn't drop information that was
actually load-bearing for the task.

## Common Mistakes
- Appending every tool result and every conversation turn to context
  forever, until the call fails or costs balloon.
- Losing a critical instruction's effectiveness by burying it in the middle
  of a large context dump instead of positioning it prominently.
- No compaction strategy, so a long-running conversation eventually hard-
  fails when it exceeds the context window instead of degrading gracefully.

## Anti-Patterns
- **Context as memory substitute**: relying on an ever-growing context
  window instead of `agentic-ai.memory` for information that should persist
  and be retrievable across sessions.
- **Undifferentiated trust**: mixing untrusted retrieved/tool content into
  the context with no distinction from trusted instructions, making prompt
  injection easier.

## Validation Checklist
- [ ] Context assembly is deliberate per call, not accumulated by default.
- [ ] Tool/retrieved content is trimmed to what's relevant, not dumped raw.
- [ ] A compaction strategy exists for long-running conversations.
- [ ] Untrusted content is clearly delineated from trusted instructions.

## Definition of Done
Meets `rules/definition-of-done.md`; token usage per call is measured and
within the project's defined budget (`agentic-ai.cost-optimization`).

## Example
```csharp
public sealed class ContextBuilder(ITokenCounter tokenCounter, int maxTokens)
{
    public IReadOnlyList<ChatMessage> Build(AgentState state)
    {
        var messages = new List<ChatMessage> { ChatMessage.System(SupportAgentPrompts.System) };

        // Recent turns verbatim, older turns summarized — bounded, not unbounded history
        messages.AddRange(state.RecentTurns.TakeLast(6));
        if (state.OlderTurnsSummary is not null)
            messages.Insert(1, ChatMessage.System($"Earlier conversation summary: {state.OlderTurnsSummary}"));

        // Untrusted retrieved content clearly delineated from instructions
        foreach (var doc in state.RetrievedChunks.Take(5))
            messages.Add(ChatMessage.System($"<retrieved-document untrusted=\"true\">{doc.Excerpt}</retrieved-document>"));

        var used = tokenCounter.Count(messages);
        if (used > maxTokens)
            throw new ContextBudgetExceededException(used, maxTokens);

        return messages;
    }
}
```

## Related Skills
- `agentic-ai.prompt-engineering` — the stable-instructions half of what
  goes into context.
- `agentic-ai.memory` — persisting information beyond the context window.
- `agentic-ai.cost-optimization` — token budget as a cost concern.
