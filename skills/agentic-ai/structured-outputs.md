---
id: agentic-ai.structured-outputs
title: Structured Outputs
category: skill
domain: agentic-ai
technologies: [dotnet]
triggers: [structured output, json mode, schema constrained generation, typed llm response]
requires: []
related: [agentic-ai.tool-calling, agentic-ai.fundamentals.planning, agentic-ai.evaluation]
optional: []
prerequisites: []
tags: [agents, structured-output]
---

# Structured Outputs

## Purpose
Get a typed, schema-conformant response from the model instead of free
text that must be parsed with regex/string-matching — the same discipline
as an API contract (`dotnet.api-design`), applied to the model boundary.

## When to Use
Any time the response needs to be consumed programmatically (a plan, a
tool call, a classification, extracted data) rather than displayed as
prose to a human.

## Prerequisites
None.

## Inputs Required
The exact shape the caller needs — over-specifying speculative fields the
caller doesn't use adds prompt cost and model confusion for no benefit.

## Engineering Principles
1. Define the response schema as a real type (JSON Schema derived from a
   C# type), not implied by prompt instructions the model might not
   follow exactly.
2. Use the provider's native structured-output/JSON-mode feature when
   available — it's more reliable than "please respond in JSON" prompt
   instructions alone.
3. Validate the response against the schema after generation — a provider
   feature reduces but doesn't eliminate malformed output; handle the
   failure case explicitly (retry, fallback, or fail the request).
4. Keep the schema minimal — every field the model must populate is a
   chance for it to get one wrong; don't ask for more structure than the
   caller actually consumes.
5. Enums/closed sets over free-text fields wherever the domain has a fixed
   set of valid values (a status field, a category) — constrains the
   model's output space and simplifies downstream handling.

## Step-by-Step Workflow
1. Define the target C# type for the response.
2. Generate/derive its JSON Schema and pass it to the model via the
   provider's structured-output mechanism.
3. Deserialize the response into the typed object.
4. Validate: does it satisfy domain constraints beyond what the schema
   alone captures (e.g. a numeric field's actual valid range)?
5. On validation failure, decide the fallback: retry with a clarifying
   message, fall back to a safe default, or fail the operation explicitly
   — never silently pass through invalid data.

## Code Standards
Structured-output types are the same kind of record types used elsewhere
in the codebase — no separate, parallel "LLM response" type system that
diverges from domain types unnecessarily.

## Architecture Constraints
A structured output type sits at the agentic-AI implementation boundary,
same as a tool-call argument type — it's translated to/from domain types at
that boundary, not used as the domain type itself throughout the
application.

## Security Considerations
A structured response is still model output — don't treat schema
conformance as a substitute for validating the actual values against
business rules and authorization (e.g. a model-suggested "approved: true"
field still needs a real authorization check before acting on it).

## Testing Requirements
Evaluation cases covering a valid response, a response requiring the
fallback path (malformed/schema-violating), and — for enum/classification
fields — coverage of each expected category.

## Common Mistakes
- Relying on prompt instructions alone ("respond only in JSON") without
  using the provider's actual structured-output feature, causing
  intermittent parse failures.
- Trusting a structured response's business-meaningful fields (like an
  "authorized" flag) without a real authorization check downstream.
- Over-specifying a large schema with many optional fields the caller never
  uses, increasing cost and error surface for no benefit.

## Anti-Patterns
- **Regex parsing of free text**: extracting structured data from a prose
  response with pattern matching instead of requesting structured output
  directly.
- **Schema as security**: assuming a schema-conformant response is
  inherently safe/authorized to act on without further validation.

## Validation Checklist
- [ ] Response schema matches a real, minimal C# type.
- [ ] Provider's native structured-output feature is used, not prompt-only
      JSON instructions.
- [ ] Response is validated against domain constraints beyond schema
      conformance.
- [ ] A defined fallback exists for schema-violating output.

## Definition of Done
Meets `rules/definition-of-done.md`; evaluation covers both valid and
fallback-triggering responses.

## Example
```csharp
public sealed record TicketClassification(
    [property: JsonPropertyName("category")] TicketCategory Category,
    [property: JsonPropertyName("confidence")] double Confidence,
    [property: JsonPropertyName("summary")] string Summary);

public enum TicketCategory { Billing, Technical, AccountAccess, Other }

var result = await model.GetStructuredResponseAsync<TicketClassification>(
    prompt: BuildClassificationPrompt(ticketText),
    ct: ct);

if (result.Confidence < 0.6)
    return ClassificationResult.NeedsHumanReview(ticketText); // don't blindly trust low-confidence output
```

## Related Skills
- `agentic-ai.tool-calling` — a specific application of structured output
  (tool-call arguments).
- `agentic-ai.fundamentals.planning` — plans as structured output.
- `agentic-ai.evaluation` — testing structured-output correctness.
