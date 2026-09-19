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

This toolkit is consumed, not copied line-by-line into your project. It takes
about five minutes to set up. You need `git`, plus PowerShell (Windows) or bash
(macOS, Linux, Git Bash). Python is only needed for the optional config check
in step 3.

After setup, your project looks like this:

```text
my-project/
├── .ai/
│   ├── toolkit/           ← this repo (git submodule or a copy; read-only)
│   ├── config.yaml         ← project-owned, validated against schemas/config.schema.json
│   └── overrides/          ← optional project-specific rule/architecture overrides (ADRs)
├── CLAUDE.md                ← entry file your assistant reads (name depends on the assistant)
├── .cursorrules
├── .github/copilot-instructions.md
└── ...
```

### 1. Get the toolkit

Clone it anywhere outside your project. You only run its install script from
this clone.

```bash
git clone https://github.com/msaeedm51/dotnet-agentic-ai-toolkit.git
```

### 2. Install it into your project

Run the script from **your project's root**, not from the toolkit folder.

Windows (PowerShell):

```powershell
cd C:\path\to\your-project
powershell -NoProfile -ExecutionPolicy Bypass -File C:\path\to\dotnet-agentic-ai-toolkit\scripts\install.ps1 -Adapter claude
```

macOS, Linux, or Git Bash:

```bash
cd /path/to/your-project
/path/to/dotnet-agentic-ai-toolkit/scripts/install.sh --adapter claude
```

Pick the adapter for the assistant you use:

| Assistant | Adapter value | File created |
|---|---|---|
| Claude Code | `claude` | `CLAUDE.md` |
| Cursor | `cursor` | `.cursorrules` |
| Windsurf | `windsurf` | `.windsurfrules` |
| GitHub Copilot | `copilot` | `.github/copilot-instructions.md` |
| ChatGPT, Gemini | none | No file entry point; follow [`adapters/chatgpt.md`](adapters/chatgpt.md) or [`adapters/gemini.md`](adapters/gemini.md) |

To set up several assistants, repeat the flag in bash
(`--adapter claude --adapter cursor`). In PowerShell, call the script directly
with a comma list (`& C:\path\to\install.ps1 -Adapter claude,cursor`) because
`powershell -File` does not accept comma lists.

By default the toolkit is added as a **git submodule** at `.ai/toolkit`, so you
can pin and update it. Add `--copy` (bash) or `-Copy` (PowerShell) to take a
plain snapshot instead. Copy mode is used automatically when your project is not
a git repository. The script never overwrites an existing `.ai/config.yaml` or
entry file.

### 3. Configure `.ai/config.yaml`

The installer seeds a minimal .NET config. Open `.ai/config.yaml` and adjust it
to your project, or start from the closest file in [`examples/`](examples/):

| Example | Use for |
|---|---|
| [`config.minimal-api.yaml`](examples/config.minimal-api.yaml) | Small single-purpose minimal API, no layering |
| [`config.clean-architecture-api.yaml`](examples/config.clean-architecture-api.yaml) | Clean Architecture ASP.NET Core API on SQL Server |
| [`config.modular-monolith.yaml`](examples/config.modular-monolith.yaml) | Modular monolith with a React/TypeScript frontend on PostgreSQL |
| [`config.agentic-ai-support-agent.yaml`](examples/config.agentic-ai-support-agent.yaml) | An LLM agent or RAG assistant |

**Building an AI agent or RAG feature?** Add `agentic-ai` to `domains` and an
`ai:` block, otherwise the agentic-AI skills are not resolved:

```yaml
project:
  name: my-project
  domains: [dotnet, agentic-ai]
ai:
  enabled: true
  model_providers: [anthropic]   # your provider(s)
  frameworks: []                 # empty = framework-neutral
  patterns: [rag]                # rag, tool-use, single-agent, multi-agent
```

Not sure which RAG technique or chunking strategy to use? Leave `ai.rag` out. The
assistant treats the project as undecided, picks a sensible baseline, measures
it, and writes its decision back to `ai.rag`. See
[`skills/agentic-ai/rag-patterns.md`](skills/agentic-ai/rag-patterns.md).

Optional: check the config against the schema (`pip install pyyaml jsonschema`
first).

```bash
python -c "import json,yaml,jsonschema; jsonschema.validate(yaml.safe_load(open('.ai/config.yaml',encoding='utf-8')), json.load(open('.ai/toolkit/schemas/config.schema.json',encoding='utf-8'))); print('config OK')"
```

### 4. Start your assistant

Open your project in a **new** session. Assistants read their entry file
(`CLAUDE.md`, `.cursorrules`, and so on) only at session start, so a session
opened before the install will not see the toolkit.

The entry file tells the assistant to read `.ai/toolkit/AGENTS.md`,
`.ai/toolkit/RULES.md` and `.ai/config.yaml`, then load only the skills, rules
and workflows the task needs from `.ai/toolkit/index/*.yaml`. To confirm it
works, watch the assistant's first tool calls: it should read those files
before it starts on your task.

### 5. Ask for work

Describe the task in plain language. You do not need to name skills or agents.
The assistant matches your request against the triggers in `index/*.yaml`, loads
the matching skills and their required dependencies, and follows the matching
workflow. For example:

- "Add a `POST /orders` endpoint with validation and tests."
- "Review this branch for security problems."
- "Build a support agent that answers questions from our docs."
- "I need RAG over `docs/policies`, but I'm not sure which approach to use."

Reusable prompt templates are in [`prompts/`](prompts/), for example
[`prompts/agentic-ai/rag-implementation.md`](prompts/agentic-ai/rag-implementation.md).

### 6. Customise

- **Project-specific rules:** put them in `.ai/overrides/*.md`. They take
  precedence over the toolkit's defaults (see [RULES.md](RULES.md)).
- **Stack details:** keep `.ai/config.yaml` current (database, ORM, providers).
  The assistant checks it before asking you questions.
- **Do not edit `.ai/toolkit/`.** Treat it as read-only so you can update it.

### 7. Update the toolkit

- **Submodule install:** `git submodule update --remote .ai/toolkit`, then
  commit the updated pointer.
- **Copy install:** delete `.ai/toolkit/`, pull the latest toolkit clone, and
  re-run the install script. Your `.ai/config.yaml` and entry files are kept.

### Troubleshooting

| Problem | Fix |
|---|---|
| The assistant ignores the toolkit | Check the entry file exists at the project root, then start a **new** session. |
| PowerShell blocks the script | Use `-ExecutionPolicy Bypass` as shown in step 2. |
| `-Adapter claude,cursor` is rejected | Call the script directly (`& .\install.ps1 -Adapter claude,cursor`) instead of through `powershell -File`. |
| Config check fails with `expected '<document start>'` | The file has a UTF-8 BOM from an older installer. Strip it: `$p='.ai\config.yaml'; $t=[IO.File]::ReadAllText((Resolve-Path $p)); [IO.File]::WriteAllText((Resolve-Path $p),$t,(New-Object Text.UTF8Encoding $false))` |
| "Target is not a git repository" | Expected. The installer falls back to copy mode. |
| The agentic-AI skills are not used | Confirm `domains` includes `agentic-ai` and `ai.enabled` is `true`. |

For assistant-specific details, see the files in [`adapters/`](adapters/).

## Status

The full initial build (all 10 batches in `CHANGELOG.md`, including the
consistency review and the optional `retrieval/` layer) is complete. Future
changes are ordinary contributions — see `CONTRIBUTING.md`.

## License

[MIT](LICENSE)
