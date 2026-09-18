# Frontmatter Schema

Every file under `skills/`, `agents/`, `rules/`, `workflows/`, `prompts/`
starts with a YAML frontmatter block. This is what makes the repository
machine-routable — `index/*.yaml` is a copy of these fields, kept in sync so
an AI assistant can decide what to load without opening every file. Formal
JSON Schema for each is in `schemas/*.schema.json`; this document explains
the fields in prose.

## Common fields (all content types)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable, dotted identifier. Convention: `<folder-path-with-dots>`, e.g. `dotnet.architecture.clean-architecture`, `agentic-ai.rag`, `agent.code-reviewer`, `rule.security`, `workflow.new-feature`. Never reused for a different file; if a file is renamed, keep its `id` unless the meaning genuinely changed. |
| `title` | string | yes | Human-readable name. |
| `category` | string | yes | One of `skill`, `agent`, `rule`, `workflow`, `prompt`. |
| `tags` | string[] | no | Free-text search aids beyond `triggers` (e.g. `["owasp", "jwt"]`). |

## Skill-specific fields (`skills/**`)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `domain` | `dotnet` \| `agentic-ai` | yes | Which track the skill belongs to. |
| `technologies` | string[] | yes | Concrete tech this skill applies to, e.g. `[aspnetcore, efcore, postgresql]`. Used to match a project's `config.yaml` stack. |
| `triggers` | string[] | yes | Phrases/keywords that should resolve a user request to this skill, e.g. `["create endpoint", "minimal api", "rest api"]`. Lowercase, no punctuation. |
| `requires` | string[] (ids) | no | **Hard** dependencies — always loaded alongside this skill. Reserve for "this skill doesn't make sense without that one," e.g. `agentic-ai.rag` requires `dotnet.api-design`. |
| `related` | string[] (ids) | no | Frequently co-occurring but not mandatory — loaded only if the project/task context supports it. |
| `optional` | string[] (ids) | no | Gated behind explicit project config (a specific framework, cloud provider, database engine). Never loaded by default. |
| `prerequisites` | string[] (ids) | no | Skills a reader/AI should already understand before this one — a *learning* order, distinct from `requires` (a *loading* order). Often the same list; kept separate because they can diverge (e.g. a skill can *require* loading `dotnet.security` at implementation time without *prerequiring* the reader to have read it first). |

## Agent-specific fields (`agents/**`)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `domains` | (`dotnet` \| `agentic-ai`)[] | yes | Which track(s) this agent operates in. Most agents list both — see `_meta/agent-template.md` on domain-awareness instead of per-domain agent clones. |
| `skills_default` | string[] (ids) | yes | Skills this agent loads for a typical task in its role, before task-specific resolution. |
| `escalates_to` | string[] (ids) | no | Other agent ids this agent hands off to when it hits the edge of its responsibility. |

## Rule-specific fields (`rules/**`)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `tech_tags` | string[] | yes | Same purpose as `technologies` on skills. |
| `triggers` | string[] | yes | Same as skill `triggers`. |
| `severity` | `blocking` \| `recommended` | yes | Whether a violation should block a review (precedence level 4/5) or is an optional recommendation (level 6). See `RULES.md`. |

## Workflow-specific fields (`workflows/**`)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `triggers` | string[] | yes | What kind of request should invoke this workflow. |
| `agents_involved` | string[] (ids) | yes | Which agents participate, in what's usually sequence order. |
| `skills_loaded` | string[] (ids) | no | Skills the workflow itself references directly (beyond what each participating agent already loads). |

## Prompt-specific fields (`prompts/**`)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `domain` | `dotnet` \| `agentic-ai` \| `both` | yes | |
| `related_skills` | string[] (ids) | no | |
| `related_agents` | string[] (ids) | no | |

## Example

```yaml
---
id: agentic-ai.rag
title: RAG (Retrieval-Augmented Generation)
category: skill
domain: agentic-ai
technologies: [dotnet, aspnetcore, embeddings, vector-search]
triggers: [rag, retrieval augmented generation, vector search, knowledge base q&a]
requires: [dotnet.api-design, dotnet.efcore]
related: [dotnet.database.postgresql, dotnet.security, agentic-ai.evaluation, agentic-ai.observability]
optional: [agentic-ai.frameworks.semantic-kernel]
prerequisites: [agentic-ai.fundamentals.agent-loops]
tags: [rag, retrieval, embeddings, agents]
---
```
