from index_store import Chunk, connect, count, search, upsert


def make_chunk(id_, category="skill", domain="dotnet", text="hello world"):
    return Chunk(id=id_, path=f"{id_}.md", title=id_, category=category, domain=domain, text=text)


def test_upsert_and_count(tmp_path):
    conn = connect(tmp_path / "index.db")
    chunks = [make_chunk("a"), make_chunk("b")]
    embeddings = [[1.0, 0.0], [0.0, 1.0]]
    upsert(conn, chunks, embeddings, "test-model")
    assert count(conn) == 2


def test_upsert_updates_in_place_on_conflict(tmp_path):
    conn = connect(tmp_path / "index.db")
    upsert(conn, [make_chunk("a", text="old")], [[1.0, 0.0]], "m1")
    upsert(conn, [make_chunk("a", text="new")], [[0.0, 1.0]], "m2")

    assert count(conn) == 1
    row = conn.execute("SELECT text, embedding_model FROM chunks WHERE id = 'a'").fetchone()
    assert row == ("new", "m2")


def test_search_ranks_by_cosine_similarity(tmp_path):
    conn = connect(tmp_path / "index.db")
    chunks = [make_chunk("close"), make_chunk("far")]
    embeddings = [[1.0, 0.01], [0.0, 1.0]]
    upsert(conn, chunks, embeddings, "m")

    results = search(conn, [1.0, 0.0], top_k=2)

    assert [r.id for r in results] == ["close", "far"]
    assert results[0].score > results[1].score


def test_search_top_k_limits_results(tmp_path):
    conn = connect(tmp_path / "index.db")
    chunks = [make_chunk(str(i)) for i in range(5)]
    embeddings = [[float(i), 1.0] for i in range(5)]
    upsert(conn, chunks, embeddings, "m")

    assert len(search(conn, [1.0, 1.0], top_k=2)) == 2


def test_search_category_filter(tmp_path):
    conn = connect(tmp_path / "index.db")
    chunks = [make_chunk("s1", category="skill"), make_chunk("r1", category="rule")]
    embeddings = [[1.0, 0.0], [1.0, 0.0]]
    upsert(conn, chunks, embeddings, "m")

    results = search(conn, [1.0, 0.0], category="rule")

    assert [r.id for r in results] == ["r1"]


def test_search_domain_filter_treats_null_and_both_as_universal(tmp_path):
    # Skills carry a single `domain`; agents/rules/workflows have none
    # (NULL) and a cross-track skill can be "both" — both must still
    # surface under any single-domain filter (see index_store.search()).
    conn = connect(tmp_path / "index.db")
    chunks = [
        make_chunk("dotnet-skill", domain="dotnet"),
        make_chunk("ai-skill", domain="agentic-ai"),
        make_chunk("cross-track-skill", domain="both"),
        make_chunk("rule-no-domain", domain=None),
    ]
    embeddings = [[1.0, 0.0]] * 4
    upsert(conn, chunks, embeddings, "m")

    results = search(conn, [1.0, 0.0], domain="dotnet")

    assert {r.id for r in results} == {"dotnet-skill", "cross-track-skill", "rule-no-domain"}


def test_search_empty_store_returns_empty_list(tmp_path):
    conn = connect(tmp_path / "index.db")
    assert search(conn, [1.0, 0.0]) == []
