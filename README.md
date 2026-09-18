# .NET AI Engineering Toolkit

A reusable, **LLM-agnostic** AI engineering operating system for professional .NET
developers. Bring it into any .NET project and configure whichever AI coding
assistant you use — Claude Code, ChatGPT, Gemini, GitHub Copilot, Cursor,
Windsurf, or a future tool — to follow the same architecture, coding, security,
testing, and review standards every time.

This is not a prompt. It is a modular knowledge base: an AI assistant loads only
the skills, rules, and agent definitions relevant to the task in front of it,
instead of one giant system prompt.

## Two knowledge domains

```text
                    ┌──────────────────────┐
                    │  .NET AI Engineering │
                    │        Toolkit       │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                              │
                ↓                              ↓
       General .NET Track              Agentic AI Track
  (skills/dotnet/, ~20 areas)     (skills/agentic-ai/, ~26 areas)
  Clean Architecture, DDD, CQRS,   Agent loops, tool calling, RAG,
  ASP.NET Core, EF Core, SQL      context engineering, memory,
  Server/PostgreSQL, API design,  evaluation, guardrails, AI security,
  security, testing, performance, cost/model routing, optional
  Docker, Azure, React/TS               framework adapters
                │                              │
                └──────────────┬───────────────┘
                               ↓
                  Production .NET / AI applications
```

The Agentic AI track **extends** the .NET track, it does not replace it. A RAG
API skill declares the .NET skills it requires (API design, EF Core, security)
instead of re-explaining them. See [RULES.md](RULES.md) for how relationships
between skills are resolved.

## Repository structure

| Path | Contents |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Global AI behavior contract — read this first, every session |
| [`RULES.md`](RULES.md) | Rule precedence system; pointers into `rules/` |
| `agents/` | Specialized agent role definitions (architect, developer, reviewer, etc.) |
| `skills/dotnet/` | General .NET engineering knowledge |
| `skills/agentic-ai/` | Agentic AI / LLM application engineering knowledge |
| `rules/` | Short, deterministic, enforceable rules by topic |
| `workflows/` | Multi-step processes (feature dev, bug fix, DB change, code review, ...) |
| `prompts/` | LLM-agnostic reusable prompt templates |
| `templates/` | Project bootstrap scaffolds (structure + key config files) |
| `adapters/` | Thin per-platform translation layers (Claude, ChatGPT, Cursor, Copilot, ...) |
| `index/` | Machine-readable routing manifests — what to load for a given task |
| `retrieval/` | Optional semantic search / MCP server layer over the whole corpus |
| `schemas/` | JSON Schema for config and frontmatter validation |
| `_meta/` | Canonical templates every skill/agent/rule/workflow/prompt must follow |
| `examples/` | Filled `config.yaml` samples for common project archetypes |
| `scripts/` | Install scripts for consuming this toolkit from another repo |

Full rationale for this structure — including why it's split this way and what
was deliberately left out — lives in the project's design discussion; a
condensed version is in `CONTRIBUTING.md`.

## Using this in a project

This toolkit is consumed, not copied line-by-line into your project. Recommended
layout inside a consuming repository:

```text
my-project/
├── .ai/
│   ├── toolkit/           ← this repo, as a git submodule (read-only, versioned)
│   ├── config.yaml         ← project-owned, validated against schemas/config.schema.json
│   └── overrides/          ← optional project-specific rule/architecture overrides (ADRs)
├── CLAUDE.md                ← generated from adapters/claude.md + config.yaml
├── .cursorrules
├── .github/copilot-instructions.md
└── ...
```

```bash
# from your project root
./path/to/dotnet-agentic-ai-toolkit/scripts/install.sh --adapter claude
```

The install script adds the toolkit as a submodule under `.ai/toolkit`, copies a
starter `config.yaml` into `.ai/`, and generates the adapter entry file(s) for
whichever assistant(s) you name. See `scripts/install.sh` (or `.ps1`) and
`adapters/` for details.

## Status

The full initial build (all 10 batches in `CHANGELOG.md`, including the
consistency review and the optional `retrieval/` layer) is complete. Future
changes are ordinary contributions — see `CONTRIBUTING.md`.

## License

[MIT](LICENSE)
