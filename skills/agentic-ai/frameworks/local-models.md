---
id: agentic-ai.frameworks.local-models
title: Local / Self-Hosted Models (Optional)
category: skill
domain: agentic-ai
technologies: [dotnet, onnx, ollama]
triggers: [local model, self hosted llm, on premises model, ollama, onnx runtime]
requires: [agentic-ai.fundamentals.agent-loops]
related: [dotnet.security, agentic-ai.model-routing]
optional: []
prerequisites: []
tags: [local-models, self-hosted, framework]
---

# Local / Self-Hosted Models (Optional)

## Purpose
Provider-specific detail for running a model locally/on-premises (via
Ollama, ONNX Runtime, or a self-hosted inference server) — only load this
skill when `.ai/config.yaml` → `ai.model_providers` names a local option.
The main driver is usually data residency (nothing leaves the network) or
cost at high volume, traded against generally lower capability than a
frontier hosted model.

## When to Use
Data cannot leave the organization's infrastructure (regulatory/contractual
requirement), or volume/cost economics favor self-hosting for a task a
smaller local model can handle adequately (verified by evaluation, not
assumed).

## Prerequisites
`agentic-ai.fundamentals.agent-loops`.

## Inputs Required
Confirmation the project's config names a local provider, the specific
model and serving infrastructure, and the hardware/capacity available to
run it.

## Engineering Principles
1. Integrate behind `IChatClient` (or equivalent) — same framework-
   neutrality principle as any hosted provider.
2. Verify capability against the evaluation suite before relying on a
   smaller local model for a task — local models are frequently less
   capable than frontier hosted ones; don't assume parity.
3. Capacity/throughput is now the project's own operational
   responsibility (no provider auto-scaling) — plan for the model server's
   resource limits explicitly (`dotnet.performance`,
   `dotnet.architecture.background-processing` for queueing under load).
4. The main benefit (data never leaves the network) is only real if the
   entire pipeline respects it — don't send the same request to a hosted
   fallback provider without checking that's acceptable
   (`agentic-ai.reliability`).

## Step-by-Step Workflow
1. Confirm `.ai/config.yaml` names a local provider and which model/serving
   stack.
2. Implement `IChatClient` (or equivalent) against the local serving
   API (e.g. Ollama's HTTP API, an ONNX Runtime-hosted endpoint).
3. Run the evaluation suite against this model for its intended task types
   before routing production traffic to it (`agentic-ai.evaluation`,
   `agentic-ai.model-routing`).
4. Plan capacity: request queueing/backpressure if the local server has
   limited concurrent throughput.

## Code Standards
The local serving client is referenced only inside the provider
implementation class.

## Architecture Constraints
Provider implementation lives in the agentic-AI infrastructure layer,
behind the same abstraction any hosted provider implements.

## Security Considerations
Verify the actual network path — "local" only delivers its data-residency
benefit if the model server and all its dependencies stay within the
intended network boundary; confirm no telemetry/logging path
inadvertently sends content externally.

## Testing Requirements
Evaluation suite run against this specific local model/version for its
assigned task types, since capability can differ significantly by model
size/quantization.

## Common Mistakes
- Assuming a local model matches a frontier hosted model's capability
  without verifying against the evaluation suite.
- No capacity planning, causing request queueing/timeouts under load with a
  fixed local inference capacity.
- A "fallback to hosted provider" reliability path that quietly defeats the
  entire reason local hosting was chosen.

## Anti-Patterns
- **Unverified downgrade**: swapping to a local model for cost/compliance
  reasons without evaluating whether it still meets the task's quality bar.
- **Leaky boundary**: a supposedly self-hosted pipeline that still sends
  logs, telemetry, or a fallback request outside the intended network.

## Validation Checklist
- [ ] `.ai/config.yaml` explicitly names this provider.
- [ ] Capability verified against the evaluation suite for assigned tasks.
- [ ] Capacity/throughput planned for the local server's actual limits.
- [ ] No part of the pipeline leaks data outside the intended boundary.

## Definition of Done
Meets `rules/definition-of-done.md`.

## Related Skills
- `dotnet.security` — data-residency/boundary verification.
- `agentic-ai.model-routing` — routing between local and hosted models.
