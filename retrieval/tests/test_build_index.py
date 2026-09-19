from build_index import collect, parse_frontmatter

FRONTMATTER = """---
id: dotnet.testing.example
title: Example Skill
category: skill
domain: dotnet
---
Body content here.
"""


def test_parse_frontmatter_extracts_fields():
    fm, body = parse_frontmatter(FRONTMATTER)

    assert fm["id"] == "dotnet.testing.example"
    assert fm["title"] == "Example Skill"
    assert fm["domain"] == "dotnet"
    assert body.strip() == "Body content here."


def test_parse_frontmatter_missing_block_returns_whole_text():
    text = "# No frontmatter\n\nJust content."

    fm, body = parse_frontmatter(text)

    assert fm == {}
    assert body == text


def test_collect_walks_agents_rules_workflows_and_nested_skills(tmp_path):
    (tmp_path / "skills" / "dotnet").mkdir(parents=True)
    (tmp_path / "agents").mkdir()
    (tmp_path / "rules").mkdir()
    (tmp_path / "workflows").mkdir()

    (tmp_path / "skills" / "dotnet" / "example.md").write_text(FRONTMATTER, encoding="utf-8")
    (tmp_path / "agents" / "reviewer.md").write_text(
        "---\nid: agent.reviewer\ntitle: Reviewer\ncategory: agent\n---\nReview things.",
        encoding="utf-8",
    )
    (tmp_path / "rules" / "general.md").write_text(
        "---\nid: rule.general\ntitle: General\ncategory: rule\n---\nBe careful.",
        encoding="utf-8",
    )
    (tmp_path / "workflows" / "new-feature.md").write_text(
        "---\nid: workflow.new-feature\ntitle: New Feature\ncategory: workflow\n---\nDo the thing.",
        encoding="utf-8",
    )

    chunks = collect(tmp_path)

    assert {c.id for c in chunks} == {
        "dotnet.testing.example",
        "agent.reviewer",
        "rule.general",
        "workflow.new-feature",
    }
    example = next(c for c in chunks if c.id == "dotnet.testing.example")
    assert example.path == "skills/dotnet/example.md"
    assert example.domain == "dotnet"
    assert example.category == "skill"


def test_collect_skips_files_without_a_frontmatter_id(tmp_path):
    (tmp_path / "rules").mkdir()
    (tmp_path / "rules" / "no-id.md").write_text("no frontmatter here", encoding="utf-8")

    assert collect(tmp_path) == []


def test_collect_truncates_embed_text_to_max_chars(tmp_path):
    (tmp_path / "rules").mkdir()
    long_body = "x" * 10000
    text = f"---\nid: rules.long\ntitle: Long\ncategory: rule\n---\n{long_body}"
    (tmp_path / "rules" / "long.md").write_text(text, encoding="utf-8")

    chunks = collect(tmp_path)

    assert len(chunks) == 1
    assert len(chunks[0].text) <= 6000
