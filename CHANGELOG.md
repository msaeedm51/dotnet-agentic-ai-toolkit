# Changelog

All notable changes to this repository are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/); versioning follows
[SemVer](https://semver.org/) once tagged.

## [Unreleased]

### RAG coverage
- New skill `agentic-ai.chunking`: strategy catalog (fixed-size, sliding
  window, sentence, recursive separator, structure-aware, code-aware/AST,
  table/layout-aware, record-based, conversation, semantic, parent-child,
  sentence-window, hierarchical/summary-tree, proposition/agentic,
  contextual, late chunking, multimodal), a content-type decision table,
  sizing starting points, and a compiled, tested C# recursive/Markdown
  chunker that carries provenance and inherits the source ACL onto every
  chunk.
- New skill `agentic-ai.rag-patterns`: the RAG types beyond the naive
  baseline — Naive/Advanced/Modular, hybrid search, reranking,
  multi-query/RAG-Fusion, query rewriting, HyDE, step-back, decomposition,
  parent-document, contextual retrieval, context compression, self-query,
  conversational, multi-hop, Corrective, Self-RAG, Adaptive, Agentic,
  federated, Graph RAG, text-to-SQL, multimodal, hierarchical,
  memory-augmented, and the long-context/CAG alternative — with a
  failure-to-pattern decision table and per-pattern security notes. The C#
  example (RRF hybrid retrieval plus a bounded corrective loop that
  abstains) is compiled and tested.
- `agentic-ai.rag` stays the baseline and now points to both; `embeddings`
  and `vector-search` link to the new skills, and chunking guidance that
  pointed at `rag` now points at `chunking`.
- `prompts/agentic-ai/rag-implementation.md` chunks per content type and
  adds a measure-first step for adopting a pattern.

### README: step-by-step usage
- "Using this in a project" is now a seven-step guide (get the toolkit,
  install for PowerShell and bash, adapter table, configure
  `.ai/config.yaml` including the `agentic-ai` and undecided-`ai.rag` cases,
  start a fresh session, example requests, customise, update) plus a
  troubleshooting table. The copy-mode installs (PowerShell 5.1 and bash),
  the config snippets and schema check, and the BOM repair were run against
  scratch projects. Submodule mode and `git submodule update --remote` were
  not run, since they pull from the published GitHub remote.

### Installer fix: BOM-less generated files
- `scripts/install.ps1` wrote `.ai/config.yaml` and the adapter entry files
  (`CLAUDE.md`, `.cursorrules`, ...) with `Out-File -Encoding utf8`, which on
  Windows PowerShell 5.1 emits a UTF-8 BOM. Anything reading the config with
  a non-UTF-8 default codepage — e.g. Python's `open()` on Windows — saw
  junk ahead of the first `#` comment and PyYAML failed with
  `expected '<document start>', but found '<block mapping start>'`
  at line 3. Found by a user following a documented config-validation step;
  reproduced, then fixed by writing generated files as BOM-less UTF-8
  (`Write-Utf8NoBom`). The script itself keeps its BOM (needed for 5.1 to
  read its own em dashes). Verified against 5.1: default and relative
  `-Target`, multiple adapters, and re-run leaving an existing config
  unchanged. `install.sh` was never affected.
- Existing installs keep the BOM; strip it with
  `$p='.ai\config.yaml'; $t=[IO.File]::ReadAllText((Resolve-Path $p)); [IO.File]::WriteAllText((Resolve-Path $p),$t,(New-Object Text.UTF8Encoding $false))`,
  or read the file with `encoding='utf-8'`.

### RAG technique selection when the user is unsure
- Tracing a request through `workflows/agentic-ai-feature.md` showed nobody
  owned the RAG technique decision: stage 2 didn't list it as a gap, stage 4
  chose only the agent pattern, stage 5 had no retrieval design, and the
  evaluation stage came after implementation, so a user who didn't know
  which RAG to use got an unexamined naive pipeline.
- `agentic-ai.rag-patterns` gains a "When the User Is Unsure" procedure:
  read `ai.rag`, inspect the corpus, ask at most three questions, choose
  chunking by content type, build the baseline, generate a starter
  evaluation set, add upgrades one at a time for measured failures, and
  record the outcome. Trigger phrases added for "which RAG should I use".
- `workflows/agentic-ai-feature.md`: unchosen RAG technique is explicitly not
  a clarification blocker (stage 2); the architect records a provisional
  retrieval decision (stage 4); the design states chunking, baseline,
  candidate upgrades, and the evaluation plan (stage 5); RAG evaluation
  loops with implementation instead of following it (stage 7).
- `agent.architect` owns the retrieval decision; `agent.ai-engineer`
  implements the baseline and adds patterns only for measured failures.
  Neither loads the RAG skills by default, only when RAG is chosen.
- `agentic-ai.rag` now `requires` `agentic-ai.chunking` (every RAG pipeline
  needs it) and has a step 0 that resolves an unspecified technique.
- `.ai/config.yaml`: new optional `ai.rag` block (`chunking`, `patterns`,
  `evaluation_set`) to record the decision. Free-form strings, not enums,
  so the schema cannot drift from the skill catalogs; unset means
  undecided.

## [1.0.0] - 2026-09-19

### Dogfooding fixes
- `scripts/install.ps1` was UTF-8 without a BOM, so Windows PowerShell 5.1
  misread its em dashes via the system codepage and failed with parser
  errors before running a single line — found by actually running it, not
  just reading it. Added a BOM.
- Same script leaked a non-zero `$LASTEXITCODE` from an internal git-repo
  probe (expected to fail when falling back to `-Copy` against a non-git
  target) as its own exit code. Reset it after the probe.
- `AGENTS.md` §4's resolution algorithm never referenced `index/rules.yaml`,
  despite `RULES.md` saying rules resolve the same way skills do "per
  `AGENTS.md` §4" — found by tracing a real task ("add JWT auth to a
  minimal API") through the documented algorithm and seeing
  `rules/security.md` never load. Fixed, plus the same gap in
  `agents/dotnet-developer.md`'s hardcoded rules fallback list.
- Both install scripts verified end-to-end (submodule and copy modes)
  against scratch git repos, generating the exact `.ai/` layout
  `README.md` documents.

### Retrieval layer test suite
- `retrieval/tests/`: pytest coverage for `index_store.py` (upsert, count,
  update-in-place on conflict, cosine-similarity ranking, `top_k`,
  category filter, the domain filter's NULL/`both`-matches-every-domain
  behavior, empty-store search) and `build_index.py` (frontmatter
  parsing, directory walking across `agents/`/`rules/`/`workflows/`/
  nested `skills/**`, skipping files with no frontmatter `id`, the
  `MAX_CHARS` truncation), plus `providers.get_provider()` rejecting an
  unknown provider name. Batch J's "verified with a unit test" claim
  described work done ad hoc and not checked in; these tests replace that
  with something CI actually re-runs (`.github/workflows/test-retrieval.yml`,
  `pip install numpy pytest` — no provider SDK needed, since the tests
  exercise storage/indexing logic, not real embedding calls).

### Batch J — Retrieval Layer (Optional)
- `retrieval/index_store.py`: SQLite-backed vector storage with
  brute-force cosine similarity search in Python (no vector-database
  dependency — the ~100-file corpus makes this fast enough, verified with
  a unit test covering upsert, cluster search, category/domain filtering,
  and update-in-place).
- `retrieval/build_index.py`: walks `agents/`, `rules/`, `workflows/`,
  `skills/**` and embeds each file via a pluggable provider. Verified
  against the real repo: collects exactly 94 chunks (11 agents, 13 rules,
  12 workflows, 58 skills), correctly captures `domain` for skills and
  leaves it `NULL` for agents/rules/workflows (agents use a `domains`
  list, not a single `domain` string — `index_store.search()` treats
  `NULL` as "matches every domain filter" rather than excluding it, since
  a domain-filtered search should still surface a relevant agent/rule).
- `retrieval/providers/`: `openai_provider.py`, `azure_openai_provider.py`
  (API-key auth by default; docstring notes the managed-identity
  alternative per `dotnet.azure`), `local_provider.py`
  (`sentence-transformers`, no data leaves the machine) — each behind the
  same `EmbeddingProvider` protocol, resolved only through
  `providers.get_provider(name)`; no provider SDK is imported directly by
  `index_store.py`/`build_index.py`/the MCP server.
- `retrieval/mcp-server/server.py`: exposes `search_toolkit(query, top_k,
  category?, domain?)` as an MCP tool via `FastMCP` (pinned to `mcp<2` —
  the SDK's `FastMCP` was renamed to `MCPServer` with a changed API in
  `mcp` 2.x during this build; pinned for stability rather than chasing a
  just-released breaking change). Verified end-to-end against real repo
  content with a fake deterministic embedding provider (no API key/model
  download needed for the test): querying "how do I bound an agent loop
  with a cost limit" correctly ranks `agentic-ai.fundamentals.agent-loops`
  first.
- `retrieval/query.py`: CLI to test the index without an MCP client.
- `retrieval/README.md`: the 3-tier retrieval strategy (keyword index /
  platform-native RAG / this folder), setup, and cost/privacy notes.
  `adapters/claude.md`'s Retrieval section gained a concrete `.mcp.json`
  example wiring this server in.
- All Python files verified with `py_compile`; every API used
  (`openai.OpenAI`/`AzureOpenAI`/`embeddings.create`,
  `mcp.server.fastmcp.FastMCP`) was checked against the actually-installed
  SDK in this environment rather than assumed from memory
  (`rules/anti-hallucination.md`).

### Batch I — Consistency Review
- Ran an automated structural audit across all 94 skill/agent/rule/
  workflow content files: 0 broken `requires`/`related`/`optional`/
  `prerequisites`/`escalates_to`/etc. references, 0 `index/*.yaml`
  mismatches (every content file indexed, every index entry backed by a
  real file with a resolvable path), 0 vendor-specific imperative
  language (`Claude must`, `GPT should`, etc.) in `skills/`, `rules/`,
  `agents/`, `workflows/`, or `prompts/`.
- Found and closed a real gap: `.github/workflows/` was an empty stub
  despite `CONTRIBUTING.md`/`README.md` promising CI there since Batch A.
  Added:
  - `scripts/validate.py` — the actual audit script above, now a
    reusable/CI-runnable asset instead of a one-off check.
  - `.github/workflows/validate-schema.yml` — runs `validate.py` on every
    push/PR.
  - `.github/workflows/lint.yml` + `.markdownlint.json` + `.yamllint.yml`
    — markdown/YAML linting, verified against the actual repo content
    (not just written and assumed to pass).
  - `.github/ISSUE_TEMPLATE/bug_report.md`, `new_skill.md`, `config.yml`,
    and `.github/PULL_REQUEST_TEMPLATE.md`.
- Fixed real issues the lint run surfaced: 28 fenced code blocks missing
  a language tag (`prompts/**`, `README.md`, `skills/dotnet/git/git.md`,
  `templates/**/README.md`) now tagged `text`; one trailing-whitespace
  line in `skills/agentic-ai/observability.md`.
- Deliberately disabled MD022/MD031/MD032/MD060 in `.markdownlint.json` —
  documented in `CONTRIBUTING.md` — because every skill/agent/rule/
  workflow file consistently uses a compact "heading directly followed by
  content" style, which is valid CommonMark and renders correctly on
  GitHub; those rules enforce a different style preference, not a
  correctness issue. MD003 and MD020 are disabled because they false-
  positive on this repo's content specifically (`_meta/*.md`'s
  HTML-comment-before-frontmatter header, and headings ending in "C#").
- Terminology spot-check: `agentic-AI` hyphenation/casing is consistent
  across all 39 files that use the term; no stray vendor-authorship
  language found in any newly-added file.

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

### Batch A completion note
All 10 batches from the original implementation plan (Batch A through
Batch J) are now complete. Nothing is pending from that plan; future
changes are ordinary contributions per `CONTRIBUTING.md`.
