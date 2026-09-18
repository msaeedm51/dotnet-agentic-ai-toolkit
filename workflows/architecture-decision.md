---
id: workflow.architecture-decision
title: Architecture Decision
category: workflow
triggers: [architecture decision, should we use this pattern, evaluate this approach, write an adr]
agents_involved: [agent.architect, agent.security-reviewer, agent.performance-engineer, agent.database-engineer, agent.documentation-engineer]
skills_loaded: []
tags: [architecture, adr, multi-agent]
---

# Architecture Decision

## Purpose
Evaluate an architectural choice from multiple specialist angles before
committing to it, and record the decision — the
Architect → Security → Performance → Database → Final Architect chain from
your original spec.

## When to Use
A standalone architecture question not tied to implementing one specific
feature: choosing a pattern, evaluating a technology, deciding on a module
boundary, or any decision expensive enough to reverse that it warrants an
ADR.

## Participants

| Step | Responsible | Consumes | Produces | Consumed by |
|---|---|---|---|---|
| 1-2 | `agent.architect` | Question | Candidate approaches | Step 3 |
| 3 | `agent.security-reviewer` | Candidates | Security implications | Step 6 |
| 4 | `agent.performance-engineer` | Candidates | Performance implications | Step 6 |
| 5 | `agent.database-engineer` (if data-relevant) | Candidates | Data implications | Step 6 |
| 6 | `agent.architect` | All specialist input | Final decision | Step 7 |
| 7 | `agent.documentation-engineer` | Decision | ADR | End |

## Stages

### 1. Frame the question
- **Actions:** State the decision to be made precisely, and the concrete
  requirement/constraint driving the need for a decision at all
  (`rules/architecture.md` — no pattern without a concrete reason).
- **Output:** Framed question.
- **Gate:** None.

### 2. Identify candidate approaches
- **Actions:** `agent.architect` identifies 2-3 real candidate approaches,
  including "do nothing/simplest option" as a baseline comparison.
- **Output:** Candidate list.
- **Gate:** The simplest option is included as a candidate, even if it's
  expected to be rejected.

### 3. Security review of candidates
- **Actions:** `agent.security-reviewer` evaluates each candidate's
  security implications (new attack surface, trust boundaries introduced).
- **Output:** Security input per candidate.
- **Gate:** None — input feeds the final decision.

### 4. Performance review of candidates
- **Actions:** `agent.performance-engineer` evaluates scalability/latency/
  cost implications of each candidate.
- **Output:** Performance input per candidate.
- **Gate:** None — input feeds the final decision.

### 5. Database review of candidates (if relevant)
- **Actions:** `agent.database-engineer` evaluates data-model/migration
  implications if the decision touches persistence.
- **Output:** Data input per candidate.
- **Gate:** None — input feeds the final decision.

### 6. Final decision
- **Actions:** `agent.architect` synthesizes all specialist input into a
  final recommendation, with trade-offs and rejected alternatives stated
  explicitly.
- **Output:** Final decision with reasoning.
- **Gate:** The decision states what was rejected and why, not just what
  was chosen.

### 7. Record the ADR
- **Actions:** `agent.documentation-engineer` records the decision using
  the ADR template (`templates/` — added in Batch H): Status, Context,
  Decision, Alternatives, Consequences, Risks.
- **Output:** ADR.
- **Gate:** ADR includes alternatives considered, not just the final
  choice.

## Escalation
A decision with significant cost, licensing, or organizational implications
(not just technical) escalates to the user for a final call —
`agent.architect` recommends, but doesn't unilaterally decide, on matters
outside pure technical trade-offs.

## Related Workflows
- `workflows/new-feature.md` — where a smaller-scoped architecture decision
  (sized to one feature) happens inline rather than as this standalone
  workflow.
