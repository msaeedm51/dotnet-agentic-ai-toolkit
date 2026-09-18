# Adapter: Claude / Claude Code

This adapter explains how to wire this toolkit into Claude Code (or Claude
via the API/desktop app with filesystem access). It does not restate any
engineering knowledge — that stays in `AGENTS.md`, `RULES.md`, `agents/`,
`skills/`, `rules/`, `workflows/`, `prompts/`.

## Setup

After running `scripts/install.sh`/`install.ps1` (or manually placing this
repo at `.ai/toolkit/` per the root `README.md` consumption model), create
`CLAUDE.md` at the consuming project's root:

```markdown
# Project AI Instructions

This project uses the .NET AI Engineering Toolkit at `.ai/toolkit/`.

Before any non-trivial task:
1. Read `.ai/toolkit/AGENTS.md` for the operating principles and entry
   sequence.
2. Read `.ai/toolkit/RULES.md` for rule precedence.
3. Read `.ai/config.yaml` for this project's stack/architecture/domains.
4. Resolve relevant skills/agents/rules/workflows via
   `.ai/toolkit/index/*.yaml` per `AGENTS.md` §4 — do not load the whole
   toolkit into context for a small task.

Project-specific overrides live in `.ai/overrides/` and take precedence
per `.ai/toolkit/RULES.md`'s precedence order.
```

Claude Code reads `CLAUDE.md` automatically at session start, so this is
the entry point — everything else is loaded on demand via the resolution
algorithm in `AGENTS.md` §4.

## Agents

Claude Code supports subagents (`.claude/agents/*.md`, invoked via the
`Agent` tool or `/agents`). Optionally mirror this toolkit's `agents/*.md`
as thin Claude Code subagent definitions:

```markdown
---
name: dotnet-developer
description: Use for implementing .NET features. Loads
  .ai/toolkit/agents/dotnet-developer.md for its full role definition.
---
Read .ai/toolkit/agents/dotnet-developer.md and follow it exactly. Resolve
skills via .ai/toolkit/index/skills.yaml per AGENTS.md §4.
```

This is optional — Claude Code can equally follow `agents/*.md` directly
within a single session without registering them as formal subagents.

## Skills

Claude Code's filesystem access means skills are read directly — no upload
step needed. If this toolkit's content is also registered as a Claude Code
*Skill* (the `Skill` tool's plugin mechanism, distinct from this toolkit's
own `skills/` folder — naming collision is unfortunate but the concepts are
different), keep that as a thin pointer into `skills/**`, not a duplicate.

## Retrieval

Tier 1 (`retrieval/README.md`) applies directly — Claude Code reads
`index/*.yaml` and the resolved skill files via its filesystem tools. If
`retrieval/mcp-server` (Batch J) is configured as an MCP server in Claude
Code's settings, prefer it for semantic search over a large corpus;
otherwise the keyword index is sufficient and requires no setup.

## Project overrides

`.ai/config.yaml` and `.ai/overrides/*.md` are read directly by Claude Code
like any other file — no special handling needed. Precedence follows
`RULES.md` unchanged.

## Limitations

None specific to this platform — Claude Code has full filesystem, shell,
and (optionally) MCP access, so all three retrieval tiers are available.
