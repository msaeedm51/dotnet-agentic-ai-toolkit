# Adapter: Cursor

Cursor has filesystem access and an agent mode, similar in capability to
Claude Code. This adapter explains only the wiring — the knowledge stays in
`AGENTS.md`, `RULES.md`, `agents/`, `skills/`, `rules/`, `workflows/`.

## Setup

After installing this toolkit at `.ai/toolkit/`, create `.cursorrules` (or
`.cursor/rules/*.mdc` for the newer per-directory rules format) at the
project root:

```markdown
# Project AI Instructions

This project uses the .NET AI Engineering Toolkit at .ai/toolkit/.

Before any non-trivial task, read .ai/toolkit/AGENTS.md (operating
principles + entry sequence) and .ai/toolkit/RULES.md (precedence), then
.ai/config.yaml for this project's stack. Resolve relevant
skills/agents/rules/workflows via .ai/toolkit/index/*.yaml per AGENTS.md
§4 rather than loading the whole toolkit.

.ai/overrides/*.md take precedence over toolkit defaults per RULES.md.
```

If using `.cursor/rules/*.mdc` (project-scoped rules with glob-based
activation), a thin rule file per major area (e.g. one activating on
`**/*.cs` that points to `dotnet.csharp`/`dotnet.dotnet`) can reduce how
much Cursor needs to reason about resolution itself — still just a
pointer, not a copy of the content.

## Agents

Cursor doesn't have a first-class "subagent" concept equivalent to Claude
Code's. Cursor's agent mode reads `agents/*.md` directly as role
descriptions when the task at hand matches one — reference the relevant
agent file explicitly in a prompt (e.g. "follow
`.ai/toolkit/agents/api-engineer.md`") when you want a specific role
applied.

## Skills

Read directly via Cursor's filesystem access — no upload step. Cursor's
own `@` file-reference syntax can pull a specific skill file into context
explicitly when the automatic resolution via `.cursorrules` isn't precise
enough for a given prompt.

## Retrieval

Tier 1 applies directly (filesystem access + `index/*.yaml`). Cursor
supports MCP servers in its settings — if `retrieval/mcp-server` (Batch J)
is configured there, it can be used for semantic search the same way as in
Claude Code.

## Project overrides

Same as any filesystem-access platform — `.ai/config.yaml` and
`.ai/overrides/*.md` are read directly; precedence follows `RULES.md`
unchanged.

## Limitations

None specific to this platform for the Tier 1/3 retrieval path. Cursor has
no native platform-level RAG/knowledge-upload feature (Tier 2), so Tier 1
(filesystem) or Tier 3 (MCP) are the practical options here.
