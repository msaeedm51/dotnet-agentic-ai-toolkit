## What changed

## Why

## Checklist

- [ ] New/changed skill, agent, rule, workflow, or prompt follows its
      canonical template in `_meta/`
- [ ] Frontmatter added/updated (`id`, `category`, `domain`,
      `triggers`, `requires`/`related`/`optional` as applicable) —
      see `_meta/frontmatter-schema.md`
- [ ] Matching `index/*.yaml` entry added/updated
- [ ] `python scripts/validate.py` passes locally
- [ ] `npx markdownlint-cli2 "**/*.md"` passes locally
- [ ] No vendor-specific language (`Claude must`, `GPT should`, etc.) in
      `skills/`, `rules/`, `agents/`, `workflows/`, or `prompts/` —
      vendor-specific phrasing belongs only in `adapters/*.md`
- [ ] No unjustified duplication of an existing file's content
      (`CONTRIBUTING.md`'s no-duplication rule)
- [ ] Every skill includes at least one practical, modern C#/.NET (or
      relevant stack) example — not a toy snippet
