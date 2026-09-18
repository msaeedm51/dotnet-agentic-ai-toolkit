---
id: workflow.agentic-ai-feature
title: Agentic AI Feature Development
category: workflow
triggers: [build an agent, implement rag, add tool calling, build a support agent]
agents_involved: [agent.architect, agent.ai-engineer, agent.test-engineer, agent.security-reviewer, agent.code-reviewer, agent.performance-engineer]
skills_loaded: []
tags: [agentic-ai, feature-development, multi-agent]
---

# Agentic AI Feature Development

## Purpose
The agentic-AI-track counterpart to `workflows/new-feature.md` — same
shape (requirement → design → implement → test → review → ship), with the
agent-pattern selection, evaluation harness, and cost/guardrail stages this
track specifically requires inserted.

## When to Use
A request to build or modify an agent, RAG pipeline, tool-calling feature,
or any capability under `skills/agentic-ai/`.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-2 | AI assistant | Request | Clarified requirement | Step 3 |
| 3 | `agent.architect` | Requirement | Project Understanding (if not done) | Step 4 |
| 4 | `agent.architect` | Requirement | Agent pattern selection | Step 5 |
| 5 | `agent.architect` | Pattern | Design + implementation plan | Step 6 |
| 6 | `agent.ai-engineer` | Plan | Implementation | Step 7 |
| 7 | `agent.test-engineer`/`agent.ai-engineer` | Implementation | Evaluation harness | Step 8 |
| 8 | `agent.security-reviewer` | Implementation | Security findings | Step 9 (if findings) or 10 |
| 9 | `agent.ai-engineer` | Findings | Fixes | Step 8 (re-review) |
| 10 | `agent.performance-engineer` | Implementation | Cost/latency findings | Step 11 |
| 11 | `agent.code-reviewer` | Implementation | Review findings | Step 12 (if findings) or 13 |
| 12 | `agent.ai-engineer` | Findings | Fixes | Step 11 (re-review) |
| 13 | AI assistant | All of the above | Validation | Step 14 |
| 14 | `agent.documentation-engineer` | Implementation | Feature documentation | End |

## Stages

### 1. Requirement
- **Actions:** Restate the requirement to confirm understanding — what
  should the agent actually accomplish, and what should it explicitly not
  do.
- **Output:** Confirmed requirement, including out-of-scope actions.
- **Gate:** None.

### 2. Clarify assumptions
- **Actions:** Identify gaps (model provider, framework, cost/latency
  budget) — check `.ai/config.yaml` before asking; escalate genuinely
  undetermined load-bearing gaps.
- **Output:** Assumptions list / confirmed config.
- **Gate:** No unresolved load-bearing ambiguity (especially: what
  irreversible actions, if any, the agent can take).

### 3. Inspect existing code
- **Actions:** Run `workflows/project-discovery.md` if not already done;
  identify existing agentic-AI infrastructure in the project (model client
  abstractions, existing agents) to reuse rather than duplicate.
- **Output:** Relevant existing patterns identified.
- **Gate:** None.

### 4. Select agent pattern
- **Actions:** `agent.architect` chooses the pattern based on the actual
  task shape — single-agent loop, RAG, tool-use, plan-then-execute, or
  multi-agent — per `skills/agentic-ai/fundamentals/`. Default to the
  simplest pattern that fits; multi-agent requires a stated, concrete
  scope justification.
- **Output:** Pattern decision.
- **Gate:** The pattern isn't more complex than the task requires
  (`agentic-ai.fundamentals.multi-agent-systems` anti-pattern check).

### 5. Design
- **Actions:** Design the context/tool/prompt structure; identify bounds
  (steps, cost, timeout), guardrails needed, and human-in-the-loop
  checkpoints for any irreversible tool action.
- **Output:** Design + implementation plan.
- **Gate:** Every irreversible action identified in step 1 has a planned
  human-in-the-loop checkpoint (`agentic-ai.human-in-the-loop`).

### 6. Implementation
- **Actions:** `agent.ai-engineer` implements per the plan, following
  `rules/agentic-ai.md` and the relevant `skills/agentic-ai/*` files.
- **Output:** Working implementation with bounds and guardrails enforced
  in code.
- **Gate:** Loop bounds, guardrails, and human-in-the-loop checkpoints are
  implemented in code, not left as prompt-only instructions
  (`rules/agentic-ai.md`).

### 7. Evaluation harness
- **Actions:** Build/extend an evaluation suite covering happy-path, edge,
  and adversarial (prompt-injection-style) cases
  (`agentic-ai.evaluation`).
- **Output:** Evaluation suite with a baseline pass rate.
- **Gate:** At least one adversarial case is included and passes.

### 8. Security review
- **Actions:** `agent.security-reviewer` checks the instruction-source
  boundary (untrusted content vs. instructions), tool authorization scope,
  and model provider credential handling
  (`agentic-ai.ai-security`).
- **Output:** Findings (if any).
- **Gate:** No BLOCKER-severity finding remains open.

### 9. Performance/cost review
- **Actions:** `agent.performance-engineer` checks token usage, cost per
  request, and latency against the project's budget
  (`agentic-ai.cost-optimization`, `agentic-ai.observability`).
- **Output:** Findings (if any).
- **Gate:** Cost/latency is within the stated budget, or the budget
  decision is escalated explicitly.

### 10. Code review
- **Actions:** `agent.code-reviewer` checks correctness, architecture, and
  maintainability per `workflows/code-review.md`.
- **Output:** Findings (if any).
- **Gate:** No BLOCKER-severity finding remains open.

### 11. Validation
- **Actions:** Check against `rules/definition-of-done.md` and the
  relevant skill files' own Definition of Done sections.
- **Output:** Confirmed done, or a list of what's outstanding.
- **Gate:** All applicable items satisfied.

### 12. Documentation
- **Actions:** `agent.documentation-engineer` documents what the agent can
  and cannot do, its bounds, and known failure modes — this is
  operationally load-bearing for this track, not optional polish
  (`agents/documentation-engineer.md`).
- **Output:** Feature documentation.
- **Gate:** None.

## Escalation
A gate failure returns to the responsible agent for that stage. A design
question about acceptable autonomy/risk (should this action require human
approval) escalates to the user — this is a product decision, not a
technical one `agent.architect` should make unilaterally.

## Related Workflows
- `workflows/new-feature.md` — the general-track counterpart this mirrors.
- `workflows/code-review.md` — detail for the review stage.
- `workflows/architecture-decision.md` — for a standalone agent-pattern
  decision not tied to one specific feature.
