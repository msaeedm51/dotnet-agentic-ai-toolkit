#!/usr/bin/env python3
"""Query the local semantic index directly from the command line.

Useful for testing an index built with build_index.py before wiring up
the MCP server — same search logic, no MCP client needed.

Usage:
    python query.py "how do I bound an agent loop" --provider local
    python query.py "postgresql isolation levels" --provider openai --top-k 3
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_store import connect, search  # noqa: E402
from providers import get_provider  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--provider", required=True, choices=["openai", "azure-openai", "local"])
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--category", choices=["skill", "agent", "rule", "workflow"])
    parser.add_argument("--domain", choices=["dotnet", "agentic-ai"])
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(__file__).resolve().parent / ".index" / "toolkit.db",
    )
    args = parser.parse_args()

    if not args.db.exists():
        print(f"No index found at {args.db}. Run build_index.py first.", file=sys.stderr)
        return 1

    provider = get_provider(args.provider)
    query_vector = provider.embed([args.query])[0]

    conn = connect(args.db)
    results = search(conn, query_vector, top_k=args.top_k, category=args.category, domain=args.domain)

    if not results:
        print("No results.")
        return 0

    for r in results:
        print(f"{r.score:.3f}  {r.id}  ({r.path})")
        print(f"        {r.snippet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
