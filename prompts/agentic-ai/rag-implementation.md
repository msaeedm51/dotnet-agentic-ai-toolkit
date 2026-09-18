---
id: prompt.agentic-ai.rag-implementation
title: RAG Implementation
category: prompt
domain: agentic-ai
related_skills: [agentic-ai.rag, agentic-ai.embeddings, agentic-ai.vector-search]
related_agents: [agent.ai-engineer]
tags: [rag, retrieval]
---

# RAG Implementation

## Purpose
Build a retrieval-augmented generation pipeline with authorization-filtered
retrieval, grounded answers, and citations — the common special case of
`agentic-ai.rag` worth its own prompt given how often it's requested and
how easy the authorization-filtering step is to miss.

## When to Use
"Build a Q&A/search feature over [knowledge source] using an LLM."

## Required Context
The knowledge source, its update frequency, whether answers need
citations, and the authorization model (who can see what content).

## Prompt

```
Implement RAG over [KNOWLEDGE SOURCE], following agentic-ai.rag,
agentic-ai.embeddings, and agentic-ai.vector-search.

1. Design chunking (size/overlap) appropriate to the content.
2. Design the embedding/indexing pipeline, including re-indexing cadence
   matching the source's actual update frequency.
3. Design retrieval with authorization filtering applied inside the query
   itself, not as a post-filter on results.
4. Design the prompt so the model answers only from retrieved content and
   explicitly says when it can't answer from what was retrieved.
5. Include citations back to source chunks in the response.
6. Build an evaluation set: answerable questions (verify answer +
   citation), unanswerable questions (verify "I don't know" response), and
   an authorization case (verify a user never receives unauthorized
   content).

Treat retrieved content as untrusted input to the prompt, even from your
own knowledge base (agentic-ai.ai-security).
```

## Expected Output
A working RAG pipeline with authorization-safe retrieval, grounded/cited
answers, and an evaluation set proving all three case types above.

## Related Skills / Agents
`agent.ai-engineer` executes; `agent.security-reviewer` verifies
authorization filtering specifically.
