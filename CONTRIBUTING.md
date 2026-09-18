# Contributing

This repository is a knowledge base an AI assistant consumes, not a
traditional codebase. The bar for a contribution is: **would a competent
.NET or AI engineer trust this file enough to act on it without checking
elsewhere, and can an AI assistant load it without loading the rest of the
repo?**

## Before you open a PR

1. **Use the template.** Every skill, agent, rule, workflow, and prompt must
   follow its canonical template in `_meta/`:
   - Skill → `_meta/skill-template.md`
   - Agent → `_meta/agent-template.md`
   - Rule → `_meta/rule-template.md`
   - Workflow → `_meta/workflow-template.md`
   - Prompt → `_meta/prompt-template.md`
2. **Add frontmatter.** Every file needs the metadata block described in
   `_meta/frontmatter-schema.md` — `id`, `domain`, `category`, `triggers`,
   `requires`/`related`/`optional` where applicable. This is what makes the
   file discoverable without an AI having to read the whole repo.
3. **Register it in the index.** Add a matching entry to the relevant
   `index/*.yaml` file. A skill/agent/rule/workflow that exists but isn't
   indexed is effectively invisible to the retrieval flow described in
   `AGENTS.md`.
4. **Validate against schema.** Run the schema validation described in
   `.github/workflows/validate-schema.yml` locally before pushing
   (`schemas/*.schema.json`).
5. **Stay LLM-agnostic in `skills/`, `rules/`, `agents/`, `workflows/`,
   `prompts/`.** Write "the AI assistant must," never "Claude must" or "GPT
   should." Vendor-specific phrasing belongs only in `adapters/*.md`.
6. **No duplication.** If your content overlaps an existing file by more than
   a paragraph, extend that file (and its `related`/`requires` links) instead
   of creating a new one. If you're adding an agentic-AI concern that's
   really a general engineering concern in disguise (e.g. "logging"), put it
   in the shared `dotnet` track and have the `agentic-ai` skill `require` it.
7. **One practical example per skill,** using modern C# / .NET or the
   relevant stack — not a toy snippet, and not prose-only theory.

## Style

- Concise, deterministic, imperative. "Never do X," "Always do Y," not "it's
  generally good practice to consider X."
- No motivational or filler text.
- No vendor assumptions in core content (`skills/`, `rules/`, `agents/`,
  `workflows/`, `prompts/`). Assume the reader might be a tool with no
  filesystem or shell access at all — see `AGENTS.md` §2.
- Prefer a short table or checklist over a paragraph when the content is
  enumerable.

## Adding a new skill

1. Pick the right domain folder (`skills/dotnet/...` or
   `skills/agentic-ai/...`).
2. Copy `_meta/skill-template.md`, fill every section — do not leave a
   section header with no content; delete sections that genuinely don't
   apply and say why in the PR description.
3. Fill `requires` with hard dependencies only (the skill doesn't make sense
   without them). Fill `related` with skills that often co-occur but aren't
   mandatory. Fill `optional` only for things gated behind project config
   (e.g. a specific framework or cloud provider).
4. Add the entry to `index/skills.yaml`.
5. If the skill introduces a new agentic-AI framework or provider, it belongs
   under `skills/agentic-ai/frameworks/`, not mixed into a concept-level
   skill — see the framework-neutrality note in
   `skills/agentic-ai/fundamentals/`.

## Adding a new agent

Agents are role definitions, not clones of each other per domain. If an
existing agent (e.g. `security-reviewer`) should also apply to the
agentic-AI track, extend its "skills it should load" section to include the
relevant `agentic-ai` skills rather than creating
`security-reviewer-ai.md`.

## Reporting a problem

Open an issue describing: which file, what's wrong (incorrect, outdated,
conflicts with another rule, vendor-specific language leaked into core
content, missing index entry), and if you know it, the fix.
