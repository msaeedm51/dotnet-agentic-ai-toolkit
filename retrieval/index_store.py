"""Local, dependency-light vector store for the toolkit's own corpus.

Deliberately NOT a dedicated vector database — the corpus is ~100 files,
which brute-force cosine similarity in Python handles in milliseconds.
Storage is a single SQLite file (stdlib `sqlite3`, no native extension),
with embeddings serialized as raw float32 bytes. This keeps Tier 3
retrieval (see README.md) free of any infrastructure dependency beyond
`numpy` for the similarity computation.
"""
from __future__ import annotations

import sqlite3
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    domain TEXT,
    text TEXT NOT NULL,
    embedding BLOB NOT NULL,
    embedding_model TEXT NOT NULL
);
"""


@dataclass
class Chunk:
    id: str
    path: str
    title: str
    category: str
    domain: str | None
    text: str


@dataclass
class SearchResult:
    id: str
    path: str
    title: str
    category: str
    domain: str | None
    score: float
    snippet: str


def _pack(vector: list[float]) -> bytes:
    return struct.pack(f"{len(vector)}f", *vector)


def _unpack(blob: bytes) -> np.ndarray:
    count = len(blob) // 4
    return np.array(struct.unpack(f"{count}f", blob), dtype=np.float32)


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def upsert(
    conn: sqlite3.Connection,
    chunks: list[Chunk],
    embeddings: list[list[float]],
    embedding_model: str,
) -> None:
    rows = [
        (c.id, c.path, c.title, c.category, c.domain, c.text, _pack(vec), embedding_model)
        for c, vec in zip(chunks, embeddings)
    ]
    conn.executemany(
        """
        INSERT INTO chunks (id, path, title, category, domain, text, embedding, embedding_model)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            path=excluded.path, title=excluded.title, category=excluded.category,
            domain=excluded.domain, text=excluded.text, embedding=excluded.embedding,
            embedding_model=excluded.embedding_model
        """,
        rows,
    )
    conn.commit()


def count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]


def search(
    conn: sqlite3.Connection,
    query_vector: list[float],
    top_k: int = 5,
    category: str | None = None,
    domain: str | None = None,
) -> list[SearchResult]:
    sql = "SELECT id, path, title, category, domain, text, embedding FROM chunks"
    clauses, params = [], []
    if category:
        clauses.append("category = ?")
        params.append(category)
    if domain:
        # Only skills carry a single-string `domain` in frontmatter; agents
        # use a `domains` list and rules/workflows have none at all, so
        # build_index.py stores NULL for those. Treat NULL as "applies to
        # every domain" rather than excluding it — a domain filter should
        # still surface a relevant agent/rule/workflow, not just skills.
        clauses.append("(domain = ? OR domain = 'both' OR domain IS NULL)")
        params.append(domain)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)

    rows = conn.execute(sql, params).fetchall()
    if not rows:
        return []

    q = np.array(query_vector, dtype=np.float32)
    q_norm = q / (np.linalg.norm(q) + 1e-10)

    scored: list[tuple[float, sqlite3.Row]] = []
    for row in rows:
        vec = _unpack(row[6])
        vec_norm = vec / (np.linalg.norm(vec) + 1e-10)
        score = float(np.dot(q_norm, vec_norm))
        scored.append((score, row))

    scored.sort(key=lambda t: t[0], reverse=True)

    results = []
    for score, row in scored[:top_k]:
        rid, path, title, cat, dom, text, _ = row
        snippet = text.strip().replace("\n", " ")[:280]
        results.append(SearchResult(rid, path, title, cat, dom, score, snippet))
    return results
