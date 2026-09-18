#!/usr/bin/env python3
"""Build the local semantic index over this toolkit's own corpus.

Indexes every agents/*.md, rules/*.md, workflows/*.md, and skills/**/*.md
file — the same content set `index/*.yaml` already indexes by keyword.
This is Tier 3 retrieval (see README.md): an optional, opt-in upgrade for
MCP-capable agents, never required for the toolkit to work.

Usage:
    python build_index.py --provider local
    python build_index.py --provider openai
    python build_index.py --provider azure-openai --db custom/path.db

Re-run after any content change — there's no file-watcher; this is a
deliberate, explicit step, not a background service.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_store import Chunk, connect, count, upsert  # noqa: E402
from providers import get_provider  # noqa: E402

MAX_CHARS = 6000  # conservative cap so one file can't blow an embedding call's input limit


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}, text
    fm: dict = {}
    for line in m.group(1).split("\n"):
        line = line.rstrip()
        mm = re.match(r"^([a-zA-Z_]+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm, text[m.end() :]


def collect(root: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    patterns = ["agents/*.md", "rules/*.md", "workflows/*.md", "skills/**/*.md"]
    for pattern in patterns:
        for f in sorted(root.glob(pattern)):
            text = f.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            fid = fm.get("id")
            if not fid:
                continue  # skip files without frontmatter (templates, etc.)
            rel = str(f.relative_to(root)).replace("\\", "/")
            embed_text = f"{fm.get('title', fid)}\n\n{body.strip()}"[:MAX_CHARS]
            chunks.append(
                Chunk(
                    id=fid,
                    path=rel,
                    title=fm.get("title", fid),
                    category=fm.get("category", "unknown"),
                    domain=fm.get("domain"),
                    text=embed_text,
                )
            )
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=["openai", "azure-openai", "local"])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Toolkit root (default: parent of retrieval/)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(__file__).resolve().parent / ".index" / "toolkit.db",
        help="SQLite index file (default: retrieval/.index/toolkit.db)",
    )
    args = parser.parse_args()

    chunks = collect(args.root)
    if not chunks:
        print(f"No content files found under {args.root}. Is --root correct?", file=sys.stderr)
        return 1

    print(f"Embedding {len(chunks)} files with provider '{args.provider}'...")
    provider = get_provider(args.provider)
    embeddings = provider.embed([c.text for c in chunks])

    conn = connect(args.db)
    upsert(conn, chunks, embeddings, provider.model_name)
    print(f"Indexed {count(conn)} chunks into {args.db} (model: {provider.model_name}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
