# Adapter: Windsurf

Windsurf's Cascade agent has filesystem access comparable to Cursor/Claude
Code. This adapter explains only the wiring — the knowledge stays in
`AGENTS.md`, `RULES.md`, `agents/`, `skills/`, `rules/`, `workflows/`.

## Setup

After installing this toolkit at `.ai/toolkit/`, create `.windsurfrules`
at the project root:

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

Windsurf's rules file has a character-budget limit that varies by plan —
if the full instruction block above doesn't fit alongside other project
rules, keep only the path pointers (`.ai/toolkit/AGENTS.md`,
`.ai/toolkit/RULES.md`, `.ai/config.yaml`) and drop the explanatory prose;
Cascade will read the referenced files for the detail.

## Agents

Windsurf has no first-class subagent registration comparable to Claude
Code's. Reference a specific `agents/*.md` file explicitly in a prompt
(e.g. "follow `.ai/toolkit/agents/database-engineer.md`") when a
particular role should apply.

## Skills

Read directly via Cascade's filesystem access — no upload step needed.

## Retrieval

Tier 1 applies directly. Windsurf supports MCP server configuration; if
`retrieval/mcp-server` (Batch J) is configured, it's usable the same way
as in Claude Code/Cursor.

## Project overrides

Same as any filesystem-access platform — `.ai/config.yaml` and
`.ai/overrides/*.md` are read directly; precedence follows `RULES.md`
unchanged.

## Limitations

Rules-file size limits (see Setup) are the main platform-specific
constraint — mitigate with the pointer-only fallback above rather than
truncating the toolkit's actual content.
