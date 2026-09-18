# Changelog

All notable changes to this repository are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/); versioning follows
[SemVer](https://semver.org/) once tagged.

## [Unreleased]

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
- Batch F: `prompts/**` content
- Batch G: `adapters/*.md`
- Batch H: `examples/`, `templates/**`, `scripts/install.*`
- Batch I: consistency review (broken links, duplicate/conflicting rules,
  index completeness, terminology pass)
- Batch J: `retrieval/` (optional semantic search / MCP layer)

Nothing in this repository should be treated as complete or authoritative
until the Batch I consistency review lands.
