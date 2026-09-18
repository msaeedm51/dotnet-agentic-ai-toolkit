---
id: rule.anti-hallucination
title: Anti-Hallucination Rules
category: rule
tech_tags: []
triggers: [verify before referencing, does this api exist, invented method, made up class]
severity: blocking
tags: [anti-hallucination, verification]
---

# Anti-Hallucination Rules

## Never invent an API or method signature

**Rule:** Never reference a method, property, or class member without having
verified it exists in the referenced package/codebase — by reading the
source, checking documentation, or checking the package's actual public
surface.

**Why:** An invented method compiles in the AI's head but not in the build;
worse, a wrong-but-plausible signature can pass a superficial review and
fail only at runtime or in CI, wasting the reviewer's trust.

**Applies to:** Every code suggestion or implementation.

**Exception:** None.

---

## Never assume a package is installed

**Rule:** Before using a type from a NuGet/npm package, confirm it's
actually referenced in the project file / lock file. If it isn't, say so
and ask before adding it, rather than assuming it's already there.

**Why:** Suggesting code that depends on an unreferenced package produces a
build failure the user has to debug back to "oh, that package isn't
installed."

**Applies to:** Any new type/namespace reference.

**Exception:** None.

---

## Never assume a database schema

**Rule:** Never write a query or migration against table/column names that
haven't been verified against the actual schema (migrations, a live schema
inspection, or an explicit statement from the user).

**Why:** A wrong assumed column name fails at runtime, often only under a
specific code path, and can be expensive to trace back to the root cause.

**Applies to:** Any EF Core query, raw SQL, or migration.

**Exception:** A genuinely new table/column being introduced in the same
change — that's a design decision, not an assumption, and should be stated
as such.

---

## Never assume a configuration value exists

**Rule:** Before reading `IConfiguration`/`IOptions<T>` for a key, confirm
the key is actually defined somewhere (appsettings, environment variable
convention, or being added as part of this change).

**Why:** A missing configuration key typically fails at runtime with a
null/default value silently accepted, not a compile error — a common
source of "works on my machine" bugs.

**Applies to:** Any configuration read.

**Exception:** None.

---

## Verify before referencing existing code

**Rule:** Before claiming "this project already has X" or building on an
assumed existing abstraction, actually locate and read it. Don't rely on
what's typical for this kind of project.

**Why:** Projects diverge from convention constantly; assuming a typical
structure produces confidently wrong guidance.

**Applies to:** Any claim about the current codebase's structure or
contents.

**Exception:** None.

---

## Label assumptions explicitly

**Rule:** When a gap in the requirement was filled with a reasonable guess
rather than verified fact, say so explicitly in the response ("Assuming X,
since the requirement didn't specify") rather than presenting the guess as
established fact.

**Why:** A silently-embedded assumption is invisible to the reviewer until
it causes a problem; a labeled one can be corrected immediately.

**Applies to:** Any response where a gap was filled with a guess.

**Exception:** None.

---

## Ask when missing information is load-bearing

**Rule:** If a piece of missing information would materially change the
implementation or architecture, ask for it rather than picking a plausible
default and proceeding.

**Why:** Picking a default for a load-bearing unknown risks building the
wrong thing entirely, which costs more to unwind than asking up front.

**Applies to:** Requirements with architecture- or correctness-affecting
ambiguity (see `AGENTS.md` §7 for the general escalation rule this refines).

**Exception:** Non-load-bearing details (e.g. exact wording of a log
message) don't need to block on a question — make a reasonable choice and
note it.

---

## Detect and surface requirement inconsistencies

**Rule:** If two parts of a requirement (or a requirement and the existing
codebase) contradict each other, say so explicitly rather than silently
picking one interpretation.

**Why:** Silently resolving a contradiction hides a decision the user
should have been part of, and the "wrong" resolution may not surface until
much later.

**Applies to:** Any request with internal or codebase-contradicting
requirements.

**Exception:** None.
