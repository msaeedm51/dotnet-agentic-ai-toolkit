# Adapter: Gemini

Like ChatGPT, Gemini's capability varies by surface: the plain Gemini web
chat has no file access; a Gemini Gem has file-upload knowledge (Tier 2,
similar to a Custom GPT); Gemini Code Assist / Gemini CLI in an IDE or
terminal has real filesystem access (Tier 1).

## Setup — Gemini Code Assist / Gemini CLI (recommended when available)

These have genuine project file access, comparable to Cursor/Windsurf.
Follow the same pattern as `adapters/generic.md`: create a
`GEMINI.md` (Gemini CLI's convention for project-level context, read
automatically) at the project root:

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

This is Tier 1 retrieval — no upload step needed.

## Setup — Gemini Gem (file-upload knowledge)

Create a Gem with:
- **Instructions**: same system-prompt pattern as
  `adapters/chatgpt.md`'s Custom GPT section — point at the uploaded
  files, defer to them over general knowledge.
- **Knowledge files**: `AGENTS.md`, `RULES.md`, `agents/`, `rules/`,
  `workflows/`, plus the subset of `skills/` relevant to the Gem's
  intended scope (not the full 58-file corpus, for the same size-limit
  reasons as `adapters/chatgpt.md`).

This is Tier 2 retrieval, using Gemini's own file-grounding feature.

## Setup — plain Gemini chat (no file access)

Same as `adapters/chatgpt.md`'s plain-chat guidance: paste the relevant
file(s) into the conversation, starting with `AGENTS.md`/`RULES.md`.

## Agents

No native subagent concept — reference a specific `agents/*.md` file's
content directly in a prompt or Gem instruction set.

## Retrieval

Tier 1 for Gemini Code Assist/CLI; Tier 2 for a Gem; manual paste for
plain chat with no file access — verify which surface is actually in use
before assuming a tier.

## Project overrides

For Tier 1 surfaces, `.ai/config.yaml`/`.ai/overrides/*.md` are read
directly. For a Gem or plain chat, include/paste them the same way as
other knowledge files.

## Limitations

Same knowledge-staleness caveat as `adapters/chatgpt.md` for the Gem and
plain-chat modes — re-upload/re-paste after a meaningful toolkit update.
