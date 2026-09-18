# Adapter: GitHub Copilot

Covers both Copilot's repository-level custom instructions (used by
inline/chat completions) and Copilot's agent mode (comparable filesystem
access to Cursor/Windsurf when enabled).

## Setup

After installing this toolkit at `.ai/toolkit/`, create
`.github/copilot-instructions.md` at the project root:

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

Copilot also supports path-scoped instruction files
(`.github/instructions/*.instructions.md` with a glob `applyTo` frontmatter
field) — optionally add one per major tech area (e.g. `applyTo: "**/*.cs"`
pointing at `dotnet.csharp`/`dotnet.dotnet`) for more precise activation
than the single repo-wide file provides.

## Agents

Copilot has no subagent registration comparable to Claude Code's. In agent
mode (where Copilot can read files and iterate), reference a specific
`agents/*.md` file explicitly in a chat prompt (e.g. "follow
`.ai/toolkit/agents/security-reviewer.md`") when a particular role should
apply. For plain inline/chat completions without agent mode, Copilot relies
on `copilot-instructions.md` alone — it cannot read additional toolkit
files on demand mid-completion, so the repo-wide instructions file carries
more weight here than on a filesystem-access platform.

## Skills

In agent mode: read directly via filesystem access, same as Cursor/
Windsurf. In plain chat/completion mode without agent capabilities: Copilot
cannot fetch a skill file on demand — for that mode, keep
`copilot-instructions.md` more self-contained (a condensed summary of the
most commonly needed rules) rather than assuming skill files will be
consulted per `AGENTS.md` §4's resolution flow.

## Retrieval

Tier 1 applies in agent mode. Copilot's MCP support (where available) can
use `retrieval/mcp-server` (Batch J) the same way as other MCP-capable
platforms. For plain chat/completions with no file or MCP access, fall
back to Tier 2's manual pattern: paste the relevant `skills/` file content
into the chat directly.

## Project overrides

Same as any filesystem-access platform in agent mode. In plain chat mode,
project overrides need to be manually pasted or summarized into the
conversation, since Copilot can't read `.ai/overrides/*.md` on demand
without agent-mode file access.

## Limitations

Capability varies significantly between Copilot's completion mode
(no dynamic file access) and agent mode (comparable to Cursor/Windsurf) —
this adapter's guidance branches accordingly above; confirm which mode is
active before assuming Tier 1 retrieval is available.
