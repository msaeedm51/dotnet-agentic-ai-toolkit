---
id: agentic-ai.frameworks.anthropic
title: Anthropic Provider (Optional)
category: skill
domain: agentic-ai
technologies: [dotnet, anthropic]
triggers: [anthropic api, claude model, claude api dotnet]
requires: [agentic-ai.fundamentals.agent-loops]
related: [agentic-ai.frameworks.azure-openai, agentic-ai.model-routing]
optional: []
prerequisites: []
tags: [anthropic, claude, provider, framework]
---

# Anthropic Provider (Optional)

## Purpose
Provider-specific detail for integrating the Anthropic (Claude) API from
.NET — only load this skill when `.ai/config.yaml` → `ai.model_providers`
names `anthropic`.

## When to Use
The project has explicitly chosen Anthropic/Claude as a model provider.

## Prerequisites
`agentic-ai.fundamentals.agent-loops`.

## Inputs Required
Confirmation the project's config names this provider, and which
model/feature set (tool use, extended context, prompt caching) is in scope.

## Engineering Principles
1. Integrate behind `IChatClient` (or this project's equivalent
   abstraction) — same framework-neutrality principle as any other
   provider.
2. Use native tool-use and structured-output support
   (`agentic-ai.tool-calling`, `agentic-ai.structured-outputs`) rather than
   prompt-only conventions.
3. Take advantage of prompt caching for stable system prompts/few-shot
   examples where it meaningfully reduces cost
   (`agentic-ai.cost-optimization`), verified against actual usage
   patterns.
4. API keys follow standard secret-handling rules (`dotnet.security`).

## Step-by-Step Workflow
1. Confirm `.ai/config.yaml` names Anthropic as a provider.
2. Implement `IChatClient` (or equivalent) against the Anthropic API,
   registered via DI, configured with API key from the secret store.
3. Wrap calls with the project's standard resilience policy
   (`agentic-ai.reliability`).
4. Use native tool-use/structured-output features rather than parsing free
   text.

## Code Standards
The Anthropic SDK/HTTP client is referenced only inside the provider
implementation class, not scattered through application code.

## Architecture Constraints
Provider implementation lives in the agentic-AI infrastructure layer,
behind the same abstraction any other provider implements.

## Security Considerations
API key handling per `dotnet.security`; confirm data sent to Anthropic's
infrastructure matches the project's data-handling requirements.

## Testing Requirements
Integration tests against the provider (or a recorded/mocked equivalent for
CI) verifying the `IChatClient` contract — same tests should pass
regardless of which provider implements the interface.

## Common Mistakes
Referencing Anthropic SDK types directly in application/domain code instead
of behind the abstraction.

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
- `agentic-ai.frameworks.azure-openai` — an alternative managed provider.
- `agentic-ai.model-routing` — routing across multiple providers.
