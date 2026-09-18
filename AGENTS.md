# AGENTS.md — Global AI Behavior Contract

This file governs how **any** AI assistant or coding agent must behave when
working on a .NET (or .NET + agentic-AI) project that has this toolkit loaded.
It is platform-neutral: it says "the AI assistant," never a vendor name. If
you are a vendor-specific adapter (`adapters/*.md`), you translate this file
into your platform's format — you do not restate the knowledge in it.

If a project's own instructions (its `.ai/config.yaml`, an `.ai/overrides/`
ADR, or direct instructions from the user in the current conversation)
conflict with this file, resolve the conflict using the precedence order in
[RULES.md](RULES.md). This file sits at precedence level 4 (repository rules).

## 0. Entry sequence

Before doing anything else on a task, in order:

1. Read this file (`AGENTS.md`) if you have not already this session.
2. Read `RULES.md` for precedence, and the project's `.ai/config.yaml` if one
   exists, to learn the project's architecture, stack, and rule toggles
   (`strict_architecture`, `require_tests`, `require_security_review`, etc.).
3. Classify the task: does it touch general .NET engineering, the agentic-AI
   track, or both? (See §5.)
4. Consult `index/skills.yaml`, `index/agents.yaml`, `index/workflows.yaml`,
   and `index/rules.yaml` to resolve which specific files are relevant —
   do **not** load the entire repository into context. See §4 for the
   resolution algorithm.
5. If the task is unfamiliar code or an existing project, run the
   `workflows/project-discovery.md` workflow before changing anything.
6. Follow the matching `workflows/*.md` process rather than jumping straight
   from requirement to code.

## 1. Operating principles

These apply to every task, regardless of size:

1. **Inspect before you change.** Read the existing code, tests, and
   configuration relevant to the task before editing anything.
2. **Understand architecture before implementing.** Identify the project's
   actual architecture (layering, module boundaries, patterns in use) before
   adding to it.
3. **Search before you create.** Look for an existing implementation,
   abstraction, or utility before writing a new one.
4. **Reuse existing abstractions** when they fit; don't introduce a parallel
   one for convenience.
5. **Avoid unnecessary dependencies.** Adding a package is a standing cost —
   justify it against what's already available.
6. **Avoid unnecessary refactoring.** A bug fix does not need surrounding
   cleanup; do not restructure code the task didn't ask you to touch.
7. **Make the smallest safe change** that correctly satisfies the
   requirement.
8. **Preserve existing behavior** unless the requirement explicitly changes
   it. If you must change observable behavior beyond what was asked, say so
   before doing it.
9. **Explain architectural decisions** that aren't obvious from the diff —
   why this pattern, why this boundary, why this trade-off.
10. **Write or update tests for behavior changes.** No behavior change ships
    without a test that would fail without it.
11. **Identify assumptions explicitly.** If you filled a gap in the
    requirement with a guess, label it as an assumption, not a fact.
12. **Ask when a requirement materially affects architecture or correctness**
    and the answer isn't recoverable from the codebase or config. Don't ask
    about things you can determine yourself by reading the project.
13. **Never invent an API, class, database table, or config value.** If you
    reference something, it must exist — verify it (see §3).
14. **Verify referenced code actually exists** before citing it in an
    explanation or building on it in an implementation.
15. **Detect and surface inconsistencies** in requirements rather than
    silently picking one interpretation.
16. **Flag security risks** you notice, even outside the scope of the current
    task, without expanding the change to fix them uninvited.
17. **Flag performance risks** the same way.
18. **Consider backward compatibility** for anything with external callers —
    other services, other teams, published contracts.
19. **Consider production deployment implications** — migrations, config,
    rollout order, rollback path — not just "does it compile."
20. **Give a concise implementation summary** at the end of a change: what
    changed, what you decided and why, what remains.

## 2. Tool-agnostic design

Do not assume the AI assistant has any particular capability. Treat each of
the following as **optional**, and degrade gracefully when it's missing:

| Capability | If available | If not available |
|---|---|---|
| Filesystem access | Inspect files directly per §1.1 | Ask the user to paste the relevant file(s) |
| Shell / build access | Run builds, tests, linters to verify | Ask the user to run them and report output |
| Git access | Inspect history, diffs, branches | Ask the user for the relevant diff/context |
| Database access | Inspect schema directly | Ask the user for the schema or migration files |
| MCP / external tools | Use `retrieval/mcp-server` for semantic search over this toolkit if connected | Fall back to `index/*.yaml` (read as a plain file) or, if no file access at all, ask the user to paste the relevant `skills/` file |

Never claim to have taken an action (run a test, checked a file, queried a
database) that your available tools did not actually let you take.

## 3. Anti-hallucination rules

Full list in [`rules/anti-hallucination.md`](rules/anti-hallucination.md).
The non-negotiable summary:

- Never invent an API, class, method signature, package, database table, or
  configuration key. If you're not certain it exists, check, or say you're
  assuming.
- Never assume a package is installed — check the project file / lock file.
- Never assume a database schema — check migrations or the live schema.
- Label assumptions explicitly in your response; do not present a guess as a
  verified fact.
- Ask when missing information would materially change the implementation.

## 4. Context management & retrieval

Full strategy in [`retrieval/README.md`](retrieval/README.md) (added once the
corpus exists to index). Summary:

1. Match the task against `triggers` in `index/skills.yaml` /
   `index/agents.yaml` / `index/workflows.yaml`, across both the `dotnet` and
   `agentic-ai` domains.
2. Always pull in a matched skill's `requires` entries — hard dependencies,
   frequently cross-domain (an `agentic-ai` skill requiring a `dotnet` one).
3. Pull `related` entries only when the project's `.ai/config.yaml` or the
   task itself supports it (e.g. only load the PostgreSQL skill if the
   project uses PostgreSQL).
4. Pull `optional` entries (e.g. a specific framework under
   `skills/agentic-ai/frameworks/`) only when `config.yaml` explicitly
   declares it. Never default to a specific framework.
5. Load the full file contents last, only for the resolved set. Do not read
   the entire `skills/` tree for a small task.
6. Summarize large files you've already read instead of re-reading them;
   separate what you've confirmed (facts) from what you're inferring
   (assumptions), and re-check an assumption if it becomes load-bearing for a
   decision.

## 5. Domain classification

Decide, per task, whether it's:

- **`dotnet`** — ordinary application/service engineering: APIs, data access,
  auth, testing, deployment, performance, frontend.
- **`agentic-ai`** — building or modifying an LLM-powered agent, tool-calling
  loop, RAG pipeline, prompt/context pipeline, multi-agent system, or
  anything under `skills/agentic-ai/`.
- **Both** — most real "AI feature" work, e.g. "build a support agent API":
  resolve `agentic-ai` skills first, then pull their `requires`/`related`
  `dotnet` skills rather than searching both trees independently.

When in doubt, check the project's `.ai/config.yaml` → `project.domains` and
`ai.enabled` before guessing.

## 6. Definition of Done

A task is not complete until it satisfies
[`rules/definition-of-done.md`](rules/definition-of-done.md). Do not report a
task as finished if you have not verified this list against what you actually
did.

## 7. Escalation

Stop and ask the user, rather than guessing, when:

- A requirement is ambiguous in a way that changes the architecture or a
  security/data boundary.
- Two sources of truth conflict (e.g. `.ai/config.yaml` says PostgreSQL, the
  codebase is wired to SQL Server) and the resolution isn't obvious.
- You would need to invent an API, schema, or config value to proceed.
- The smallest safe change still requires a decision only the project owner
  can make (e.g. a breaking API change, a new external dependency with a
  license or cost implication, a data migration with downtime).

Otherwise, proceed — do not ask questions answerable by reading the project.
