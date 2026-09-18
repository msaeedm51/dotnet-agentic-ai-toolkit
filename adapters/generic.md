# Adapter: Generic / Any Other AI Assistant

Use this adapter for any AI coding tool not covered by a dedicated adapter
— a future tool, an internal/custom agent, or a platform whose specific
conventions this toolkit hasn't caught up with yet. It's also the template
for writing a new dedicated adapter.

## Step 1 — determine the platform's capabilities

Before wiring anything up, determine what the platform can actually do —
per `AGENTS.md` §2's capability table:

| Capability | Check |
|---|---|
| Filesystem access | Can it read arbitrary project files on demand? |
| Shell access | Can it run build/test commands and read output? |
| Persistent project-level instructions | Does it read a convention file (like `CLAUDE.md`/`.cursorrules`) automatically at session start? |
| File upload / native knowledge base | Can you attach files it retrieves from automatically (Custom GPT-style)? |
| MCP or external tool support | Can it connect to an MCP server? |

This determines which retrieval tier (`retrieval/README.md`) applies:
**Tier 1** (filesystem access) → **Tier 2** (upload as native knowledge) →
**Tier 3** (MCP) → manual paste, in that order of preference.

## Step 2 — wire the entry point

**If it has filesystem access and reads a convention file automatically**
(most coding-agent-style tools): create that file at the project root with
this content, adjusting only the filename to match the platform's
convention:

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

**If it has filesystem access but no automatic convention file** (e.g. a
plain chat interface with a file-read tool): paste this same block as the
first message of the session.

**If it has native knowledge/file-upload (no live filesystem access)**:
follow `adapters/chatgpt.md`'s Custom GPT pattern — upload `AGENTS.md`,
`RULES.md`, `agents/`, `rules/`, `workflows/`, and a relevant subset of
`skills/`, with a system-prompt instruction to defer to them over general
knowledge.

**If it has none of the above**: paste the relevant file(s) manually into
each conversation as needed — start with `AGENTS.md`/`RULES.md`, then the
specific skill/rule/workflow file the task requires (find the path via
`index/skills.yaml` etc. in an editor or another session first).

## Step 3 — map agents (if the platform has a subagent/persona concept)

If the platform supports defining named roles/subagents, mirror
`agents/*.md` as thin pointers (see `adapters/claude.md`'s subagent example
for the pattern). Otherwise, reference a specific `agents/*.md` file
directly in a prompt when a particular role should apply.

## Step 4 — verify project overrides are reachable

Confirm `.ai/config.yaml` and `.ai/overrides/*.md` are included wherever
the platform gets its context (filesystem, uploaded knowledge, or manual
paste) — these are what let a project deviate from toolkit defaults per
`RULES.md`'s precedence order, and are easy to forget when wiring up a new
platform.

## Writing a new dedicated adapter

If a platform is used often enough to warrant its own file, copy this
file's structure into `adapters/<platform>.md`, fill in the platform-
specific setup steps, and add it to the table in the root `README.md`.
Keep it thin — a dedicated adapter should never restate engineering
knowledge that belongs in `skills/`/`rules/`/`workflows/`.
