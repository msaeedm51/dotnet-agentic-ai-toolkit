---
id: workflow.project-discovery
title: Project Discovery
category: workflow
triggers: [new to this codebase, understand this project, before modifying an unfamiliar project, onboard to this repo]
agents_involved: [agent.architect]
skills_loaded: []
tags: [discovery, onboarding]
---

# Project Discovery

## Purpose
Build an accurate picture of an unfamiliar project's architecture, stack,
and conventions before changing anything in it — required by `AGENTS.md`
§0 before modifying unfamiliar code, and the entry point for every other
workflow when the project hasn't been inspected yet this session.

## When to Use
The first substantive task in a project this session hasn't already
inspected, or when returning to a project after enough time/change that
prior findings may be stale.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-7 | AI assistant (typically framed as `agent.architect`) | The repository | Project Understanding document | Every subsequent workflow this session |

## Stages

### 1. Inspect solution/project structure
- **Input:** Repository root.
- **Actions:** Read solution files, project files, directory layout;
  identify the major projects/modules and how they reference each other.
- **Output:** A map of projects and their dependency graph.
- **Gate:** None.

### 2. Inspect dependencies and technology stack
- **Input:** Project files, lock files, `package.json`/`.csproj`.
- **Actions:** Identify .NET version, key NuGet/npm packages, ORM,
  frontend framework if any — do not assume from this toolkit's target
  profile; verify against what's actually referenced.
- **Output:** Confirmed technology stack.
- **Gate:** None.

### 3. Inspect configuration and database setup
- **Input:** `appsettings.*`, connection strings (structure, not secret
  values), migration folders.
- **Actions:** Identify database engine(s), whether EF Core owns
  migrations, and any per-environment configuration pattern.
- **Output:** Data-access and configuration picture.
- **Gate:** None.

### 4. Inspect authentication/authorization

- **Actions:** Identify the auth scheme in use (JWT/OAuth2/OIDC, identity
  provider), and how authorization policies are structured.
- **Output:** AuthN/AuthZ picture.
- **Gate:** None.

### 5. Inspect API surface, existing patterns, and tests
- **Actions:** Sample a few endpoints/handlers to identify the
  architecture actually in use (Clean Architecture, CQRS, vertical slices,
  etc.) and existing conventions to follow; identify the test project(s)
  and testing approach in use.
- **Output:** Architecture and convention picture; testing strategy.
- **Gate:** None.

### 6. Inspect CI/CD, Docker, and documentation
- **Actions:** Identify build/deploy pipeline, containerization approach,
  and what documentation already exists and whether it's current.
- **Output:** Deployment model picture.
- **Gate:** None.

### 7. Produce Project Understanding
- **Actions:** Synthesize findings into a concise summary: architecture,
  major modules, technologies, key dependencies, data access approach,
  authentication, testing strategy, deployment model, risks noticed, and
  existing patterns to follow.
- **Output:** Project Understanding document (can be a response section,
  not necessarily a file) — the reference point for the actual task.
- **Gate:** This must exist before proceeding to implementation in a
  project not already inspected this session.

## Escalation
If the codebase contradicts the user's stated assumptions about it (e.g.
they said "we use PostgreSQL" but the connection string is SQL Server), flag
this explicitly per `rules/anti-hallucination.md` rather than silently
trusting either source.

## Related Workflows
Precedes every other workflow in this file for a project not yet inspected
this session — `workflows/new-feature.md`, `.bug-fix.md`,
`.database-change.md`, etc. all assume this has run.
