# Retrieval

Optional semantic search over this toolkit's own corpus (`skills/`,
`agents/`, `rules/`, `workflows/`). **Nothing in this toolkit requires
this folder.** `AGENTS.md` §4's default resolution algorithm — match a
task to `index/*.yaml` by keyword, expand via `requires`/`related`/
`optional` — works with zero setup on any platform with file access. This
folder is for two narrower cases:

1. You're on an MCP-capable AI assistant and want semantic ("what's
   relevant to X") search instead of keyword matching.
2. You want to feed this toolkit into a platform with built-in
   file-search/knowledge (a ChatGPT Custom GPT, a Gemini Gem) — in which
   case you don't need anything here either; that platform's own
   retrieval does the work (see `adapters/chatgpt.md` / `adapters/gemini.md`).

## The three retrieval tiers

| Tier | Who it's for | Setup |
|---|---|---|
| **1 — Keyword index** | Any AI assistant with filesystem access (Claude Code, Cursor, Windsurf, Copilot agent mode) | None — read `index/*.yaml` per `AGENTS.md` §4 |
| **2 — Platform-native RAG** | ChatGPT Custom GPTs, Claude Projects, Gemini Gems | None from this repo — upload `skills/`/`rules/`/`agents/`/`workflows/` as the platform's own knowledge files (see `adapters/chatgpt.md`, `adapters/gemini.md`) |
| **3 — This folder** | Any MCP-capable assistant, or a large custom corpus where keyword matching under-performs | `pip install` + `build_index.py` + wire up `mcp-server/server.py` |

Prefer Tier 1 by default. Reach for Tier 3 only when keyword matching is
genuinely insufficient — e.g. you've extended this toolkit with many
project-specific skills and `index/*.yaml` triggers no longer capture
enough of the corpus's actual vocabulary.

## What's in this folder

```text
retrieval/
├── index_store.py       # SQLite-backed vector storage + brute-force
│                           cosine search (no vector-DB dependency —
│                           the corpus is ~100 files, brute force is fast)
├── build_index.py        # walks skills/agents/rules/workflows, embeds
│                           each file, writes retrieval/.index/toolkit.db
├── query.py               # CLI: test the index without an MCP client
├── providers/              # pluggable embedding backends
│   ├── openai_provider.py
│   ├── azure_openai_provider.py
│   └── local_provider.py    # self-hosted, no data leaves the machine
├── mcp-server/
│   └── server.py            # exposes search_toolkit() as an MCP tool
└── requirements.txt
```

No provider is hardcoded anywhere in `index_store.py`, `build_index.py`,
or `mcp-server/server.py` — they only ever go through
`providers.get_provider(name)`. This is the same framework/provider-
neutrality principle as `skills/agentic-ai/fundamentals/` applied to this
tool itself.

## Setup

```bash
cd retrieval
pip install -r requirements.txt   # uncomment the provider(s) you need first

# Build the index once (re-run after any content change — no watcher):
python build_index.py --provider local        # self-hosted, no API key
# or: python build_index.py --provider openai        # needs OPENAI_API_KEY
# or: python build_index.py --provider azure-openai   # needs AZURE_OPENAI_*

# Test it directly:
python query.py "how do I bound an agent loop's cost" --provider local
```

See each provider module's docstring (`providers/*.py`) for its exact
environment variables.

**The provider used to build the index and the provider used to query it
must be the same** — embeddings from different models aren't comparable
(`skills/agentic-ai/embeddings.md`). Set `RETRIEVAL_PROVIDER` for the MCP
server to match whatever you used for `build_index.py --provider`.

## Wiring up the MCP server

```bash
export RETRIEVAL_PROVIDER=local   # must match how the index was built
python mcp-server/server.py       # runs over stdio
```

Point your MCP client's config at this command. For Claude Code, see
`adapters/claude.md`'s Retrieval section; the same pattern (an MCP server
entry with `command: python`, `args: ["retrieval/mcp-server/server.py"]`,
and the `RETRIEVAL_PROVIDER`/`RETRIEVAL_DB` env vars) applies to any other
MCP-capable client (Cursor, Windsurf).

The server exposes one tool, `search_toolkit(query, top_k, category?,
domain?)`, returning `id`/`path`/`title`/`category`/`domain`/`score`/
`snippet` per result — always read the file at `path` for the full
content; the snippet is a preview, not a substitute for
`AGENTS.md` §4's "load the full file contents last" step.

## Keeping the index current

There's no file watcher by design — re-run `build_index.py` after a
meaningful content change (a new skill, a rule rewrite). A stale index
degrades gracefully (it just won't surface the new/changed content), it
doesn't error.

## Cost and privacy

- `local` provider: no data leaves the machine, no API cost, needs
  `sentence-transformers` (downloads a model on first use).
- `openai`/`azure-openai`: sends this toolkit's own content (not your
  project's) to the provider for embedding — review your organization's
  data-handling policy same as any other use of that provider
  (`skills/agentic-ai/frameworks/local-models.md` has the fuller
  reasoning for when self-hosting matters more).
- Query-time cost is one embedding call per search — the toolkit's own
  content, already indexed, is never re-sent per query.
