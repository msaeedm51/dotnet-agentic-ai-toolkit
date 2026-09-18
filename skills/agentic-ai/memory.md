---
id: agentic-ai.memory
title: Memory
category: skill
domain: agentic-ai
technologies: [dotnet, efcore]
triggers: [agent memory, conversation history persistence, long term memory, user preferences memory]
requires: [dotnet.efcore]
related: [agentic-ai.context-engineering, agentic-ai.vector-search, dotnet.database]
optional: []
prerequisites: [agentic-ai.context-engineering]
tags: [agents, memory]
---

# Memory

## Purpose
Persist information across conversations/sessions that a single context
window can't hold indefinitely — user preferences, facts learned, past
decisions — retrieved deliberately when relevant, not re-derived every
time or lost when the conversation ends.

## When to Use
The agent needs to recall something from a previous session, or a
conversation is long enough that early context must be persisted and
retrieved rather than kept verbatim in the context window
(`agentic-ai.context-engineering`).

## Prerequisites
`agentic-ai.context-engineering`.

## Inputs Required
What actually needs to persist (facts, preferences, decisions) versus
what's fine to lose when the session ends, and any data-retention/privacy
constraints on storing it.

## Engineering Principles
1. Memory is a deliberate write, not everything the agent has ever seen —
   decide explicitly what's worth persisting (a stated user preference, a
   confirmed fact) versus transient conversational content.
2. Store memory in a normal, queryable datastore
   (`dotnet.efcore`/`dotnet.database`) — this is application data, not a
   special "AI-only" store that bypasses the project's normal data
   governance.
3. Retrieval is scoped and relevant — don't dump all stored memory into
   every context; retrieve what's relevant to the current task
   (potentially via `agentic-ai.vector-search` for semantic retrieval).
4. Memory has the same data-retention and deletion obligations as any other
   user data — if a user can request deletion of their data, stored
   agent memory about them is included.
5. Distinguish memory the user explicitly confirmed/stated from memory the
   agent inferred — treat inferred memory with more caution before acting
   on it as fact.

## Step-by-Step Workflow
1. Decide what's worth persisting from this session (explicit user
   statements, confirmed facts, decisions) — not the raw transcript by
   default.
2. Write it to a normal datastore with structure appropriate to querying it
   later (a `UserPreference` table, not a blob of unstructured text unless
   semantic retrieval is genuinely needed).
3. On a new session, retrieve relevant memory scoped to the current
   user/task — via direct query for structured facts, or
   `agentic-ai.vector-search` for semantic recall over less structured
   memory.
4. Feed retrieved memory into context deliberately
   (`agentic-ai.context-engineering`), distinguishing it from the current
   conversation.
5. Honor deletion/correction requests against stored memory the same way
   the project honors them for any other user data.

## Code Standards
Memory records are typed entities with an owner (user/tenant id), a source
(explicit statement vs. inferred), and a timestamp — not an opaque blob
with no structure or provenance.

## Architecture Constraints
Memory storage is infrastructure the application layer accesses through a
normal repository/port (`dotnet.architecture.repository-specification`),
not a special-cased bypass of the project's usual data-access patterns.

## Security Considerations
Stored memory can contain PII — apply the same encryption-at-rest,
access-control, and retention rules as any other PII
(`dotnet.security`). Never let one user's stored memory be retrievable into
another user's context — scope every retrieval query by owner.

## Testing Requirements
Test that memory scoped to one user is never retrieved into another user's
context (a cross-tenant/cross-user leak here is a security bug, not just a
correctness bug). Test deletion actually removes the record, not just
hides it from normal retrieval.

## Common Mistakes
- Persisting the entire raw transcript as "memory" instead of deliberately
  extracted, structured facts — expensive to store and imprecise to
  retrieve.
- No owner scoping on retrieval, risking one user's memory leaking into
  another's context.
- Treating an agent's inferred assumption as confirmed fact in later
  sessions without ever re-validating it.

## Anti-Patterns
- **Unbounded memory growth**: never pruning or expiring old memory,
  degrading retrieval quality and increasing storage/PII exposure over
  time with no corresponding benefit.
- **Memory as a trust upgrade**: treating something recalled from memory as
  more authoritative than the same claim made fresh in conversation, when
  it was actually just an unconfirmed inference stored earlier.

## Validation Checklist
- [ ] Only deliberately extracted, structured facts are persisted — not
      the raw transcript by default.
- [ ] Every retrieval query is scoped by owner (user/tenant).
- [ ] Deletion/correction requests are honored against stored memory.
- [ ] Inferred vs. explicitly-confirmed memory is distinguished.

## Definition of Done
Meets `rules/definition-of-done.md`; a test proves memory retrieval is
scoped correctly per owner and deletion actually removes the record.

## Example
```csharp
public sealed record UserMemory(Guid UserId, string Fact, MemorySource Source, DateTimeOffset RecordedAtUtc);
public enum MemorySource { ExplicitlyStated, Inferred }

public sealed class MemoryStore(AppDbContext db)
{
    public async Task<IReadOnlyList<UserMemory>> GetRelevantAsync(Guid userId, string currentTask, CancellationToken ct) =>
        await db.UserMemories.AsNoTracking()
            .Where(m => m.UserId == userId) // owner-scoped, always
            .OrderByDescending(m => m.RecordedAtUtc)
            .Take(20)
            .ToListAsync(ct);

    public Task DeleteAllForUserAsync(Guid userId, CancellationToken ct) =>
        db.UserMemories.Where(m => m.UserId == userId).ExecuteDeleteAsync(ct);
}
```

## Related Skills
- `agentic-ai.context-engineering` — how retrieved memory enters context.
- `agentic-ai.vector-search` — semantic retrieval over less structured
  memory.
- `dotnet.database` — the underlying storage engine's own rules.
