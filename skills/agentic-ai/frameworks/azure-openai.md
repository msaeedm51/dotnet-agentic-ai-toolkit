---
id: agentic-ai.frameworks.azure-openai
title: Azure OpenAI Provider (Optional)
category: skill
domain: agentic-ai
technologies: [dotnet, azure, azureopenai]
triggers: [azure openai, azure ai foundry, managed identity openai]
requires: [agentic-ai.fundamentals.agent-loops, dotnet.azure]
related: [agentic-ai.frameworks.openai, agentic-ai.model-routing]
optional: []
prerequisites: [dotnet.azure]
tags: [azure-openai, provider, framework]
---

# Azure OpenAI Provider (Optional)

## Purpose
Provider-specific detail for integrating Azure OpenAI Service from .NET —
only load this skill when `.ai/config.yaml` → `ai.model_providers` names
`azure-openai`. The main advantage over the direct OpenAI API is Azure-
native auth (managed identity) and data residency/compliance alignment for
Azure-hosted projects.

## When to Use
The project deploys on Azure (`dotnet.azure`) and needs OpenAI models with
Azure AD authentication, private networking, or Azure-specific compliance
guarantees.

## Prerequisites
`agentic-ai.fundamentals.agent-loops`, `dotnet.azure`.

## Inputs Required
Confirmation the project's config names this provider, and the Azure
resource/deployment details (endpoint, deployment name) it targets.

## Engineering Principles
1. Prefer managed identity (`DefaultAzureCredential`) over an API key for
   authentication, consistent with `dotnet.azure`'s general Azure-to-Azure
   auth principle.
2. Integrate behind `IChatClient` (or equivalent) — same framework-
   neutrality principle as any other provider.
3. Model deployment names (not raw model names) are the addressing
   mechanism in Azure OpenAI — track them as configuration, since they're
   project/resource-specific.
4. Data sent to Azure OpenAI stays within the configured Azure region/
   tenant boundary — this is often the specific compliance reason this
   provider was chosen over the direct OpenAI API; don't undermine it by
   also routing the same data through a non-Azure fallback without
   checking that's acceptable.

## Step-by-Step Workflow
1. Confirm `.ai/config.yaml` names Azure OpenAI as a provider, with its
   endpoint/deployment configuration.
2. Implement `IChatClient` (or equivalent) against the Azure OpenAI SDK,
   authenticated via managed identity where the hosting environment
   supports it (`dotnet.azure`).
3. Wrap calls with the project's standard resilience policy
   (`agentic-ai.reliability`).
4. Use native tool-use/structured-output features rather than parsing free
   text.

## Code Standards
The Azure OpenAI SDK is referenced only inside the provider implementation
class.

## Architecture Constraints
Provider implementation lives in the agentic-AI infrastructure layer,
behind the same abstraction any other provider implements.

## Security Considerations
Managed identity preferred over API key (`dotnet.azure`); confirm any
fallback provider doesn't violate the data-residency reason this provider
was chosen.

## Testing Requirements
Integration tests against the provider (or a recorded/mocked equivalent for
CI) verifying the `IChatClient` contract.

## Common Mistakes
Using an API key instead of managed identity when the hosting environment
already supports it. Referencing Azure OpenAI SDK types directly outside
the provider implementation.

## Anti-Patterns
Falling back to a non-Azure provider during an outage without checking
whether that violates the data-residency/compliance reason Azure OpenAI was
chosen in the first place.

## Validation Checklist
- [ ] `.ai/config.yaml` explicitly names this provider.
- [ ] Managed identity used where supported, over API key.
- [ ] Integration is entirely behind `IChatClient`/equivalent.
- [ ] Any fallback provider respects the same data-residency requirement.

## Definition of Done
Meets `rules/definition-of-done.md`.

## Related Skills
- `dotnet.azure` — the managed-identity/deployment foundation this relies
  on.
- `agentic-ai.frameworks.openai` — the non-Azure alternative.
