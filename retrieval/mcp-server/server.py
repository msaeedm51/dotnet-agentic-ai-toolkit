#!/usr/bin/env python3
"""MCP server exposing semantic search over this toolkit's corpus.

Requires: pip install mcp (see ../requirements.txt)

Exposes one tool, `search_toolkit`, so any MCP-capable AI assistant
(Claude Code, Cursor, Windsurf, etc. — see ../../adapters/) can query the
index built by build_index.py directly, instead of (or alongside) the
keyword-based `index/*.yaml` lookup described in AGENTS.md §4.

This is Tier 3 retrieval (../README.md) — entirely optional. An index
must already exist (`python ../build_index.py --provider <name>`) before
this server has anything to search.

Configuration (environment variables):
    RETRIEVAL_PROVIDER   which embedding provider to query WITH — must
                          match the provider the index was BUILT with
                          (mixing providers produces meaningless results;
                          see skills/agentic-ai/embeddings.md). One of:
                          openai, azure-openai, local. Defaults to "local".
    RETRIEVAL_DB          path to the SQLite index file. Defaults to
                          ../.index/toolkit.db.

Run directly for local testing:
    python server.py
Or point an MCP client's config at this file — e.g. for Claude Code,
add an MCP server entry with command "python" and this file's path as
an argument. See adapters/claude.md's Retrieval section.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

RETRIEVAL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RETRIEVAL_ROOT))

from index_store import connect, search  # noqa: E402
from providers import get_provider  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    raise ImportError("This server requires the mcp package: pip install mcp") from e

DB_PATH = Path(os.environ.get("RETRIEVAL_DB", str(RETRIEVAL_ROOT / ".index" / "toolkit.db")))
PROVIDER_NAME = os.environ.get("RETRIEVAL_PROVIDER", "local")

mcp = FastMCP(
    "dotnet-ai-toolkit-retrieval",
    instructions=(
        "Semantic search over the .NET AI Engineering Toolkit's skills, "
        "agents, rules, and workflows. Prefer this over guessing when the "
        "keyword-based index/*.yaml lookup (AGENTS.md §4) doesn't "
        "surface an obviously relevant file."
    ),
)

_provider = None  # lazy-loaded on first call, not at import time


def _get_provider():
    global _provider
    if _provider is None:
        _provider = get_provider(PROVIDER_NAME)
    return _provider


@mcp.tool()
def search_toolkit(
    query: str,
    top_k: int = 5,
    category: str | None = None,
    domain: str | None = None,
) -> list[dict]:
    """Semantically search the toolkit's skills/agents/rules/workflows.

    Args:
        query: Natural-language description of what you need (e.g.
            "how to bound an agent loop's cost", "postgresql isolation
            levels").
        top_k: Maximum number of results to return.
        category: Optionally restrict to one of "skill", "agent", "rule",
            "workflow".
        domain: Optionally restrict to "dotnet" or "agentic-ai".

    Returns:
        A list of results, each with: id, path (read this file for the
        full content — this tool returns only a short snippet), title,
        category, domain, score, snippet.
    """
    if not DB_PATH.exists():
        return [
            {
                "error": (
                    f"No index found at {DB_PATH}. Run "
                    f"'python build_index.py --provider {PROVIDER_NAME}' first."
                )
            }
        ]

    provider = _get_provider()
    query_vector = provider.embed([query])[0]

    conn = connect(DB_PATH)
    results = search(conn, query_vector, top_k=top_k, category=category, domain=domain)

    return [
        {
            "id": r.id,
            "path": r.path,
            "title": r.title,
            "category": r.category,
            "domain": r.domain,
            "score": round(r.score, 4),
            "snippet": r.snippet,
        }
        for r in results
    ]


if __name__ == "__main__":
    mcp.run()  # stdio transport — the standard for a locally-spawned MCP server
