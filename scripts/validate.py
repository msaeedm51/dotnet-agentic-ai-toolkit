#!/usr/bin/env python3
"""Validate this toolkit's structural consistency.

Checks, in order:
  1. Every skill/agent/rule/workflow file's frontmatter validates against
     its JSON Schema in schemas/.
  2. Every requires/related/optional/prerequisites/escalates_to/
     related_skills/related_agents/agents_involved/skills_default/
     skills_loaded reference resolves to a real content id.
  3. Every index/*.yaml entry has a matching content file (and vice
     versa), and every entry's `path` exists on disk.
  4. Every example config.yaml in examples/ validates against
     schemas/config.schema.json.
  5. No vendor-specific imperative language ("Claude must", "GPT should",
     etc.) appears in skills/, rules/, agents/, workflows/, or prompts/.

Exits non-zero if any check fails. Run from the repo root:
    python scripts/validate.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: PyYAML. Install with: pip install pyyaml jsonschema", file=sys.stderr)
    sys.exit(2)

try:
    import jsonschema
except ImportError:
    print("Missing dependency: jsonschema. Install with: pip install pyyaml jsonschema", file=sys.stderr)
    sys.exit(2)

import json

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}, text
    fm = yaml.safe_load(m.group(1)) or {}
    return fm, text[m.end():]


def load_schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


CATEGORY_SCHEMA = {
    "skill": "skill-frontmatter.schema.json",
    "agent": "agent-frontmatter.schema.json",
}


def collect_content_files() -> dict[str, dict]:
    """Returns {id: {"path": relpath, "fm": frontmatter dict}}."""
    files: dict[str, dict] = {}
    patterns = ["agents/*.md", "rules/*.md", "workflows/*.md", "skills/**/*.md"]
    for pattern in patterns:
        for f in sorted(ROOT.glob(pattern)):
            text = f.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            if not fm:
                continue
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            fid = fm.get("id")
            if not fid:
                err(f"{rel}: missing 'id' in frontmatter")
                continue
            if fid in files:
                err(f"duplicate id '{fid}': {rel} and {files[fid]['path']}")
            files[fid] = {"path": rel, "fm": fm}

            schema_name = CATEGORY_SCHEMA.get(fm.get("category", ""))
            if schema_name:
                schema = load_schema(schema_name)
                try:
                    jsonschema.validate(instance=fm, schema=schema)
                except jsonschema.ValidationError as e:
                    err(f"{rel}: frontmatter schema violation — {e.message}")
    return files


def check_references(files: dict[str, dict]) -> None:
    ref_fields = [
        "requires", "related", "optional", "prerequisites", "escalates_to",
        "related_skills", "related_agents", "agents_involved",
        "skills_default", "skills_loaded",
    ]
    for fid, info in files.items():
        fm = info["fm"]
        for field in ref_fields:
            vals = fm.get(field)
            if not vals:
                continue
            if isinstance(vals, str):
                vals = [vals]
            for v in vals:
                if v and v not in files:
                    err(f"{info['path']}: '{field}' references unknown id '{v}'")


def check_indexes(files: dict[str, dict]) -> None:
    index_map = {
        "skills.yaml": ("skills", "skill"),
        "agents.yaml": ("agents", "agent"),
        "rules.yaml": ("rules", "rule"),
        "workflows.yaml": ("workflows", "workflow"),
    }
    index_schema = load_schema("index-entry.schema.json")
    for fname, (list_key, category) in index_map.items():
        p = ROOT / "index" / fname
        if not p.exists():
            err(f"missing index file: index/{fname}")
            continue
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        entries = data.get(list_key) or []
        index_ids = set()
        for e in entries:
            try:
                jsonschema.validate(instance=e, schema=index_schema)
            except jsonschema.ValidationError as ex:
                err(f"index/{fname}: entry '{e.get('id')}' schema violation — {ex.message}")
            eid = e.get("id")
            epath = e.get("path")
            index_ids.add(eid)
            if epath and not (ROOT / epath).exists():
                err(f"index/{fname}: entry '{eid}' path '{epath}' does not exist")
            if eid not in files:
                err(f"index/{fname}: entry '{eid}' has no matching content file")
        fm_ids = {fid for fid, info in files.items() if info["fm"].get("category") == category}
        for missing in fm_ids - index_ids:
            err(f"index/{fname}: '{missing}' exists as a file but is not indexed")


def check_examples() -> None:
    schema = load_schema("config.schema.json")
    examples_dir = ROOT / "examples"
    if not examples_dir.exists():
        return
    for f in sorted(examples_dir.glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            err(f"{f.relative_to(ROOT)}: does not match config.schema.json — {e.message}")


def check_vendor_language() -> None:
    vendor_terms = [
        "Claude must", "Claude should", "Claude will",
        "ChatGPT must", "ChatGPT should",
        "GPT must", "GPT should",
        "Gemini must", "Gemini should",
        "Copilot must", "Copilot should",
        "Cursor must", "Cursor should",
    ]
    for cat in ["skills", "rules", "agents", "workflows", "prompts"]:
        d = ROOT / cat
        if not d.exists():
            continue
        for f in d.rglob("*.md"):
            text = f.read_text(encoding="utf-8")
            for term in vendor_terms:
                if term in text:
                    err(f"{f.relative_to(ROOT)}: vendor-specific language '{term}' in core content")


def main() -> int:
    files = collect_content_files()
    check_references(files)
    check_indexes(files)
    check_examples()
    check_vendor_language()

    if ERRORS:
        print(f"FAILED — {len(ERRORS)} issue(s):\n")
        for e in ERRORS:
            print(f"  - {e}")
        return 1

    print(f"OK — {len(files)} content files validated, no issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
