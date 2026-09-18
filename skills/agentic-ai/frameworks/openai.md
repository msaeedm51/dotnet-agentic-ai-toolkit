---
id: agentic-ai.frameworks.openai
title: OpenAI Provider (Optional)
category: skill
domain: agentic-ai
technologies: [dotnet, openai]
triggers: [openai api, gpt model, openai sdk dotnet]
requires: [agentic-ai.fundamentals.agent-loops]
related: [agentic-ai.frameworks.azure-openai, agentic-ai.model-routing]
optional: []
prerequisites: []
tags: [openai, provider, framework]
---

# OpenAI Provider (Optional)

## Purpose
Provider-specific detail for integrating the OpenAI API from .NET — only
load this skill when `.ai/config.yaml` → `ai.model_providers` names
`openai`.

## When to Use
The project has explicitly chosen OpenAI as a model provider.

## Prerequisites
`agentic-ai.fundamentals.agent-loops` — provider integration sits behind
the concept-first abstraction, not the other way around.

## Inputs Required
Confirmation the project's config names this provider, and which specific
models/features (structured outputs, function calling) are in scope.

## Engineering Principles
1. Integrate behind `IChatClient` (or this project's equivalent
   abstraction) — calling code never references the OpenAI SDK types
   directly, per the framework-neutrality principle in
   `skills/agentic-ai/fundamentals/`.
2. Use the SDK's native structured-output/function-calling features
   (`agentic-ai.structured-outputs`, `agentic-ai.tool-calling`) rather than
   prompt-only JSON instructions.
3. API keys follow standard secret-handling rules
   (`dotnet.security`) — never in source, least-privilege where the
   provider supports scoped keys.
4. Respect the provider's rate limits and cost structure explicitly in
   resilience (`agentic-ai.reliability`) and cost
   (`agentic-ai.cost-optimization`) design.

## Step-by-Step Workflow
1. Confirm `.ai/config.yaml` names OpenAI as a provider.
2. Implement `IChatClient` (or equivalent) against the OpenAI SDK,
   registered via DI, configured with API key from the secret store.
3. Wrap calls with the project's standard resilience policy
   (`agentic-ai.reliability`).
4. Use structured outputs/function calling natively rather than parsing
   free text.

## Code Standards
The OpenAI SDK is referenced only inside the provider implementation class,
not scattered through application code.

## Architecture Constraints
Provider implementation lives in the agentic-AI infrastructure layer,
behind the same abstraction any other provider implements.

## Security Considerations
API key handling per `dotnet.security`; be aware that request content is
sent to OpenAI's infrastructure — confirm this matches the project's
data-handling requirements.

## Testing Requirements
Integration tests against the provider (or a recorded/mocked equivalent for
CI) verifying the `IChatClient` implementation's contract — same tests
should pass regardless of which provider implements the interface.

## Common Mistakes
Referencing OpenAI SDK types directly in application/domain code instead of
behind the abstraction, making a future provider swap or A/B test expensive.

## Anti-Patterns
Treating this provider as the only option baked into the design instead of
one interchangeable implementation of `IChatClient`.

## Validation Checklist
- [ ] `.ai/config.yaml` explicitly names this provider.
- [ ] Integration is entirely behind `IChatClient`/equivalent.
- [ ] API key follows standard secret handling.

## Definition of Done
Meets `rules/definition-of-done.md`.

## Related Skills
- `agentic-ai.frameworks.azure-openai` — the Azure-hosted alternative.
- `agentic-ai.model-routing` — routing across multiple providers.
