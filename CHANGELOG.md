# Changelog

All notable changes to this repository are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/); versioning follows
[SemVer](https://semver.org/) once tagged.

## [Unreleased]

### Batch H — Examples, Templates, Install Scripts
- `examples/`: 4 filled `.ai/config.yaml` samples, validated against
  `schemas/config.schema.json` — `config.clean-architecture-api.yaml`,
  `config.modular-monolith.yaml`, `config.minimal-api.yaml`, and
  `config.agentic-ai-support-agent.yaml` (added beyond the original
  3-sample plan specifically to demonstrate the `ai:` block that gates
  agentic-AI `optional` skill resolution).
- `templates/`: 4 project bootstrap scaffolds (`dotnet-api`,
  `clean-architecture`, `modular-monolith`, `library`), each with a
  `README.md` describing the folder layout (cross-referencing the
  relevant `skills/dotnet/` files) plus `.editorconfig`,
  `Directory.Build.props`, `global.json`, `.gitignore` — scoped to
  structure + key config, not full runnable apps, per the Batch A design
  decision. Plus a root `templates/README.md` explaining that decision
  and why the four config files are intentionally duplicated across
  templates (each is meant to be copied out as a standalone unit).
- `scripts/install.sh` and `install.ps1`: install the toolkit into a
  consuming project as a git submodule (default) or a plain copy
  (`--copy`/`-Copy`, also the automatic fallback when the target isn't a
  git repo), seed `.ai/config.yaml` if none exists, and optionally
  generate an adapter entry-point file (`--adapter claude|cursor|windsurf|copilot`)
  — matching each adapter's Setup section from Batch G exactly, since both
  scripts and the adapter docs share the same entry-point content.

### Batch G — Adapters
- `adapters/`: 7 files — `claude`, `cursor`, `windsurf`, `copilot`,
  `chatgpt`, `gemini`, `generic`. Each explains only the wiring (entry-
  point file/convention, how agents map, which retrieval tier applies,
  how project overrides reach the platform) — none restate engineering
  knowledge from `AGENTS.md`/`skills/`/`rules/`/`workflows/`.
- Design notes:
  - Adapters are grouped by actual capability, not by vendor identity:
    `claude`/`cursor`/`windsurf` are near-identical (full filesystem
    access, Tier 1 retrieval) and mostly differ in which convention file
    the platform reads automatically; `copilot` branches internally
    between its file-access agent mode and its no-file-access completion
    mode; `chatgpt`/`gemini` branch between a native-knowledge mode
    (Custom GPT / Gem — Tier 2) and a filesystem-access mode where one
    exists (Gemini Code Assist/CLI) versus plain chat with no access at
    all.
  - `adapters/generic.md` is written as a decision procedure (determine
    capability → pick a tier → wire the entry point) rather than a fixed
    template, and doubles as the instructions for writing a new dedicated
    adapter for a future platform.
  - Every adapter's entry-point content is near-identical by design (same
    four sentences pointing at `AGENTS.md`, `RULES.md`, `.ai/config.yaml`,
    and `index/*.yaml`) — the adapters differ in *where* that content
    goes and *how retrieval works after that*, not in what it says.

### Batch F — Prompts
- `prompts/`: 19 files across all 9 categories — `architecture/`
  (architecture-analysis, codebase-exploration), `coding/`
  (feature-implementation, refactoring, api-design,
  deployment-readiness), `testing/` (test-generation), `review/`
  (code-review, performance-review), `debugging/` (bug-investigation,
  incident-investigation), `database/` (database-optimization,
  migration), `security/` (security-review), `documentation/`
  (documentation), `agentic-ai/` (agent-feature-implementation,
  rag-implementation, agent-evaluation, agent-security-review). Each
  follows `_meta/prompt-template.md` and is written for "the AI
  assistant" — LLM-agnostic — with every prompt body pointing back into
  the corresponding `workflows/*.md` so the prompt and the process it
  invokes can never drift apart.
- Design note: no `index/prompts.yaml` was added. Unlike skills/agents/
  rules/workflows, prompts aren't meant to be auto-resolved by keyword
  matching mid-task — they're explicit, named templates a user or
  workflow step invokes directly by category/name. `prompt-template.md`'s
  frontmatter reflects this (`related_skills`/`related_agents`, no
  `triggers` field), which is a deliberate deviation from the other
  content types' frontmatter, not an oversight.
- Section 26 of the original spec listed 15 prompt categories
  (architecture analysis, codebase exploration, feature implementation,
  bug investigation, code review, security review, performance review,
  database optimization, API design, test generation, refactoring,
  migration, documentation, deployment, incident investigation) — all 15
  are covered, several sharing a folder where they're closely related
  (e.g. `database-optimization` + `migration` both live in `database/`).

### Batch E — Workflows
- `workflows/`: 12 files — `project-discovery`, `new-feature`, `bug-fix`
  (includes systematic debugging), `refactoring`, `api-development`,
  `database-change`, `authentication-feature`, `code-review`,
  `performance-investigation`, `production-incident`,
  `architecture-decision`, `agentic-ai-feature`. Each follows
  `_meta/workflow-template.md`: purpose, participants table (agent → what
  it consumes/produces → who's next), and staged input/actions/output/gate
  blocks.
- `index/workflows.yaml`: populated with all 12 entries.
- Design notes:
  - `workflow.bug-fix` is the single home for debugging (merges what the
    original spec listed separately as a "debugging workflow" and
    "bug-fix workflow" — same process, one file, per the duplication check
    flagged in Phase 1).
  - `workflow.agentic-ai-feature` mirrors `workflow.new-feature` stage for
    stage, with agent-pattern selection, an evaluation-harness stage, and
    a cost/latency review stage inserted — kept as a parallel file rather
    than branching logic inside one workflow, since the participant sets
    differ (`agent.ai-engineer` vs. `agent.dotnet-developer`).
  - `workflow.production-incident` explicitly reuses
    `workflow.bug-fix` stages 3-9 rather than restating the debugging
    discipline, adding only the urgency-specific impact/mitigation stages
    around it.

### Batch D — Rules
- `rules/`: 13 files — `anti-hallucination`, `definition-of-done`,
  `general`, `csharp`, `dotnet`, `architecture`, `api`, `database`,
  `security`, `testing`, `performance`, `git`, `agentic-ai`. Each follows
  `_meta/rule-template.md`: one Rule/Why/Applies-to/Exception block per
  enforceable rule, with a `severity` of `blocking` or `recommended`.
- `index/rules.yaml`: populated with all 13 entries.
- Design note: dropped the previously-planned `rules/ai-behavior.md` (see
  Batch A note) — `AGENTS.md` remains the single source for AI behavior;
  `rules/*.md` cover only checkable constraints on the resulting
  code/design, avoiding the duplication risk flagged in Phase 1.
  `rules/general.md` and `rules/csharp.md` deliberately restate a couple of
  `AGENTS.md` principles (smallest change, no unjustified abstraction) in
  their enforceable, diff-checkable form — cross-referenced back to
  `AGENTS.md` rather than re-explained.

### Batch C — Skills (both tracks)
- `skills/dotnet/`: 32 skill files — 10 architecture skills
  (clean-architecture, ddd, cqrs, modular-monolith, microservices,
  event-driven, result-rop, repository-specification,
  domain-events-outbox, background-processing) plus csharp, dotnet
  (runtime/hosting fundamentals), aspnetcore, efcore, api-design,
  authentication, authorization, security, testing, database (engine-
  agnostic + sql-server + postgresql = 3 files), performance, caching,
  messaging, azure, docker, linux, react, typescript, git, documentation.
- `skills/agentic-ai/`: 26 skill files — 3 fundamentals (agent-loops,
  planning, multi-agent-systems), 17 core (tool-calling,
  structured-outputs, prompt-engineering, context-engineering, memory,
  rag, embeddings, vector-search, mcp, human-in-the-loop, evaluation,
  guardrails, ai-security, reliability, observability, cost-optimization,
  model-routing), 6 optional framework adapters (semantic-kernel,
  microsoft-agent-framework, openai, anthropic, azure-openai,
  local-models).
- `index/skills.yaml`: populated with all 58 entries, including the
  `requires`/`related`/`optional` relationship graph connecting the two
  tracks.
- Design notes:
  - Added `dotnet.database` (engine-agnostic schema/transaction/operations
    skill) alongside `dotnet.database.sql-server` and
    `.postgresql` — not in the original Phase 1 plan, added because
    several skills referenced a general `dotnet.database` id and the
    concepts (isolation levels, pagination, bulk ops, database
    classification) that apply to both engines needed one home.
  - Framework skills (`agentic-ai.frameworks.*`) are deliberately lighter
    (no full worked example) since they're optional, config-gated
    implementation adapters over the concept-first fundamentals, not
    foundational knowledge.
  - `agentic-ai.rag` is the concrete example of cross-track composition:
    it `requires` `dotnet.api-design`/`dotnet.efcore`, `relates to`
    `dotnet.database.postgresql`/`dotnet.security`, and `optional`s
    `agentic-ai.frameworks.semantic-kernel` — resolved automatically per
    `AGENTS.md` §4 rather than hand-wired per request.

### Batch B — Agents
- `agents/`: 11 role definitions — `architect`, `dotnet-developer`,
  `ai-engineer` (new, agentic-AI-track counterpart to `dotnet-developer`),
  `code-reviewer`, `test-engineer`, `security-reviewer`,
  `database-engineer`, `api-engineer`, `devops-engineer`,
  `performance-engineer`, `documentation-engineer`.
- `index/agents.yaml`: populated with all 11 entries.
- Design note: agents are domain-aware (a "Skills to Load" split for
  `dotnet` vs. `agentic-ai` defaults) rather than cloned per domain — see
  `CONTRIBUTING.md` "Adding a new agent."

### Batch A — Scaffolding
- Root docs: `README.md`, `AGENTS.md` (global AI behavior contract),
  `RULES.md` (precedence system), `CONTRIBUTING.md`, `LICENSE` (MIT).
- `_meta/`: canonical templates for skills, agents, rules, workflows,
  prompts, plus the shared frontmatter schema doc.
- `schemas/`: JSON Schema for `config.yaml`, skill/agent frontmatter, and
  index entries.
- `index/`: seed (empty) routing manifests for skills, agents, workflows,
  rules — populated as each is authored in later batches.
- Full directory skeleton for `agents/`, `rules/`, `workflows/`, `prompts/`,
  `templates/`, `adapters/`, `examples/`, `scripts/`, `retrieval/`,
  `skills/dotnet/*`, `skills/agentic-ai/*`.

### Pending
- Batch I: consistency review (broken links, duplicate/conflicting rules,
  index completeness, terminology pass)
- Batch J: `retrieval/` (optional semantic search / MCP layer)

Nothing in this repository should be treated as complete or authoritative
until the Batch I consistency review lands.
