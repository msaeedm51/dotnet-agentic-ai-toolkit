# Adapter: ChatGPT

ChatGPT's capability varies widely by surface: plain chat has no file
access at all; a Custom GPT has built-in file-search/RAG over uploaded
knowledge files (Tier 2 in `retrieval/README.md`); ChatGPT with a
connector or a coding-agent surface (e.g. Codex-style tooling) can have
real filesystem access (Tier 1). This adapter covers all three.

## Setup — Custom GPT (recommended default for ChatGPT)

Create a Custom GPT ("Explore GPTs" → "Create") with:

- **Instructions** (the GPT's system prompt):
  ```text
  You are a .NET/agentic-AI engineering assistant using the attached
  .NET AI Engineering Toolkit knowledge files. Before answering a
  non-trivial engineering question: consult AGENTS.md for operating
  principles, RULES.md for precedence, and search the attached skill/
  rule/workflow/agent files for the ones relevant to the question — do
  not answer from general knowledge when a specific toolkit file covers
  it more precisely.
  ```
- **Knowledge files**: upload `AGENTS.md`, `RULES.md`, and the contents of
  `agents/`, `rules/`, `workflows/` directly (these are small enough in
  aggregate). For `skills/`, upload the subset relevant to the GPT's
  intended use (e.g. a "‍.NET API GPT" uploads `skills/dotnet/aspnetcore/`,
  `api-design/`, `security/`, `testing/`, `architecture/`, rather than all
  58 skill files) — ChatGPT's per-GPT file count/size limits make
  uploading the entire corpus impractical, and its built-in retrieval
  already does the semantic matching this toolkit's own keyword index
  would otherwise do.

This is Tier 2 retrieval: ChatGPT's own file-search feature does the
chunking/embedding/retrieval — no build step, no `retrieval/mcp-server`
needed.

## Setup — plain ChatGPT chat (no file access)

Paste the relevant file(s) directly into the conversation before asking
the question — start with `AGENTS.md` and `RULES.md` if the session is new,
then the specific `skills/`/`rules/`/`workflows/` file(s) the task needs
(use `index/skills.yaml`/`index/rules.yaml`/`index/workflows.yaml` from
another session or your editor to find the right path by keyword first).

## Setup — ChatGPT with real file/filesystem access

If the specific ChatGPT surface in use has genuine file/repo access
(check its actual capabilities — don't assume), follow the same pattern as
`adapters/generic.md`: point it at `.ai/toolkit/AGENTS.md` and
`.ai/toolkit/RULES.md` as the entry point, and let it resolve
`index/*.yaml` on demand (Tier 1).

## Agents

Custom GPT instructions can reference a specific `agents/*.md` file's
content directly (if uploaded) — "acting as the role described in
`code-reviewer.md`" — since ChatGPT has no native subagent concept.

## Retrieval

Tier 2 (Custom GPT knowledge/file-search) is the practical default for
this platform. Tier 1 only where the specific ChatGPT surface has real file
access — verify before assuming it.

## Project overrides

For a Custom GPT, include the project's `.ai/config.yaml` and any
`.ai/overrides/*.md` as additional uploaded knowledge files (or paste them
into the conversation for plain chat) — ChatGPT can't read a project's
live filesystem in the Custom GPT/plain-chat modes.

## Limitations

No automatic access to a live, changing codebase in the Custom GPT or
plain-chat modes — knowledge files reflect whatever was uploaded, not the
current state of the toolkit or the project. Re-upload after a meaningful
toolkit update.
