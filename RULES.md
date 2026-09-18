# RULES.md — Precedence System

This file defines **precedence only**. It does not contain rule content — that
lives in `rules/*.md`, one topic per file, so a rule is defined in exactly one
place. `AGENTS.md` defines *behavior* (how the AI works); `rules/*.md` define
*constraints* (what the resulting code/design must satisfy).

## Precedence order

When two applicable rules conflict, resolve in this order — highest wins:

1. **System/platform safety constraints** — whatever the AI platform itself
   enforces (content policy, tool permission boundaries). Outside this
   repository; always wins.
2. **This session's direct requirements** — what the user explicitly asked
   for in the current conversation.
3. **Project-specific decisions** — the consuming project's
   `.ai/config.yaml` and any `.ai/overrides/*.md` ADRs. A project can
   tighten or deliberately override a toolkit rule here (e.g. "we do not use
   the outbox pattern," "all endpoints require API key auth in addition to
   JWT"). It cannot override level 1 or 2.
4. **This toolkit's rules** — `rules/*.md`, and the behavioral contract in
   `AGENTS.md`.
5. **Generic .NET/C# baseline** — `rules/dotnet.md` and `rules/csharp.md`,
   applied when nothing more specific (architecture, API, database, security,
   agentic-ai) already covers the situation.
6. **Optional recommendations** — anything phrased as "prefer" or "consider"
   rather than "must"/"never." Non-blocking; a reviewer agent may note it but
   should not block on it alone.

### Conflict resolution in practice

- If `rules/security.md` says "never log tokens" and a project's
  `.ai/config.yaml` sets `logging.verbose: true`, level 4 still wins over
  level 5-adjacent defaults, but level 3 (an explicit project override in
  `.ai/overrides/`) can only relax a level-4 rule if the override document
  states the trade-off explicitly — silence is not an override.
- If two toolkit rule files disagree, that is a defect in this repository —
  file an issue; do not silently pick one.
- A rule marked "optional recommendation" never blocks a code review by
  itself; a rule from `rules/security.md` or `rules/architecture.md` can.

## Rule files

| File | Covers |
|---|---|
| [`rules/anti-hallucination.md`](rules/anti-hallucination.md) | Verification before referencing APIs, schemas, packages, config |
| [`rules/definition-of-done.md`](rules/definition-of-done.md) | Universal completion checklist |
| [`rules/general.md`](rules/general.md) | Cross-cutting rules not specific to a layer |
| [`rules/csharp.md`](rules/csharp.md) | C# language-level rules |
| [`rules/dotnet.md`](rules/dotnet.md) | .NET runtime/framework-level rules |
| [`rules/architecture.md`](rules/architecture.md) | Dependency direction, module boundaries, pattern selection |
| [`rules/api.md`](rules/api.md) | HTTP/API contract rules |
| [`rules/database.md`](rules/database.md) | Schema, migration, query rules |
| [`rules/security.md`](rules/security.md) | AuthN/AuthZ, secrets, input handling |
| [`rules/testing.md`](rules/testing.md) | What must be tested and how |
| [`rules/performance.md`](rules/performance.md) | Allocation, async, I/O, scalability rules |
| [`rules/git.md`](rules/git.md) | Commit/branch/PR hygiene |
| [`rules/agentic-ai.md`](rules/agentic-ai.md) | Cross-cutting rules for agent loops, tool calls, prompts, model providers |

`AGENTS.md` is the behavioral counterpart to this table — read it alongside
these, not instead of them.

## How rules are selected for a task

Rule files are indexed in [`index/rules.yaml`](index/rules.yaml) the same way
skills are indexed — with `triggers` and `tech_tags` — so an AI assistant
resolves only the rule files relevant to the current task instead of loading
all of `rules/` every time. See `AGENTS.md` §4 for the resolution algorithm.
