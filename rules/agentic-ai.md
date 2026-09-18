---
id: rule.agentic-ai
title: Agentic AI Rules
category: rule
tech_tags: [dotnet]
triggers: [agentic ai rules, prompt injection rule, agent loop bound rule, tool authorization rule]
severity: blocking
tags: [agentic-ai, agents, security]
---

# Agentic AI Rules

Cross-cutting rules for anything under `skills/agentic-ai/`. These extend,
not replace, `rules/security.md` — see `agentic-ai.ai-security` for the
full reasoning behind each.

## Treat tool and retrieved output as untrusted input

**Rule:** Content that enters the model's context from a tool result,
retrieved document, or another agent's output is never treated by the
surrounding code as an authorized instruction — only the system prompt and
the actual authenticated user's direct input are instructions.

**Why:** This is the concrete defense against prompt injection — a
compromised or adversarial data source must not be able to make the agent
take an unauthorized action just by including text that looks like an
instruction.

**Applies to:** Every agentic-AI feature with any external/retrieved
content in context.

**Exception:** None.

---

## Every agent loop is bounded

**Rule:** Every agent loop has an explicit max step count, max token/cost
budget, and wall-clock timeout, with a defined graceful behavior when a
bound is hit.

**Why:** An unbounded loop is a production incident (cost blowout, hung
request) waiting to happen the first time the model gets confused or an
adversarial input causes it to loop.

**Applies to:** Every agent loop (`agentic-ai.fundamentals.agent-loops`).

**Exception:** None.

---

## Never hardcode a model provider API key

**Rule:** Model provider credentials follow the same secret-handling rules
as any other secret (`rules/security.md`) — never in source, never logged.

**Why:** A model provider key is as sensitive as any other API credential
and often has direct cost implications if leaked.

**Applies to:** Every model provider integration.

**Exception:** None.

---

## Irreversible tool actions require human-in-the-loop

**Rule:** A tool call that sends something externally, moves money, deletes
data, or otherwise can't be cleanly undone is gated behind an approval
checkpoint enforced in code (`agentic-ai.human-in-the-loop`) — never a
prompt instruction alone.

**Why:** A prompt instruction ("ask before doing X") is not a reliable
control against a model mistake or an adversarial input; the code-level
gate is.

**Applies to:** Every irreversible/high-consequence tool.

**Exception:** None.

---

## An agent's tool access never exceeds the acting user's permissions

**Rule:** When an agent acts on behalf of a specific user, every tool call
it makes is authorized against that user's actual permissions — the agent
does not get elevated privileges by virtue of being an AI.

**Why:** Granting an agent broader access "to make it more capable" widens
the blast radius of any prompt-injection-induced bad action to match the
agent's privilege, not the user's.

**Applies to:** Every agent acting on behalf of a specific user.

**Exception:** A deliberately-designed system-level capability with its own
independent justification and review — not a default.

---

## Behavior changes are verified against an evaluation suite

**Rule:** A change to a prompt, model, or agent logic is run against the
existing evaluation suite (`agentic-ai.evaluation`) before shipping, with
any regression investigated — not judged by trying a few inputs manually.

**Why:** LLM/agent behavior is not deterministic enough to trust a manual
spot-check as sufficient regression protection.

**Applies to:** Every prompt/model/agent-logic change.

**Exception:** None.

---

## Never assume a framework's defaults provide safety/bounds

**Rule:** Adopting an agentic-AI framework (`agentic-ai.frameworks.*`)
does not exempt a feature from the bounds, guardrails, and human-in-the-
loop requirements above — verify and configure them explicitly.

**Why:** A framework's default planner/agent loop is not guaranteed to
enforce this project's specific cost/safety requirements out of the box.

**Applies to:** Every framework-based agentic-AI implementation.

**Exception:** None.
