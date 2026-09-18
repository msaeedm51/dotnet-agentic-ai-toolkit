<!--
Canonical rule-file template. Each rules/*.md file is a flat list of
individually enforceable rules for one topic — not prose essays. Keep each
rule short enough that an AI assistant can check compliance mechanically.
-->
---
id: rule.<topic>
title: <Topic> Rules
category: rule
tech_tags: []
triggers: []
severity: blocking   # or: recommended (see RULES.md precedence levels 4/5 vs 6)
tags: []
---

# <Topic> Rules

<!-- One rule per entry. Use this shape for every rule in the file: -->

## <Short rule name>

**Rule:** One or two sentences, imperative, unambiguous ("Never X" / "Always
Y" / "Do X unless Y").

**Why:** The concrete failure mode this rule prevents. Not "best practice" —
the actual thing that goes wrong.

**Applies to:** tech/context this rule is scoped to, if not universal.

**Exception:** When this rule legitimately doesn't apply, if ever. If there
is truly no exception, write "None."

---

<!-- Repeat the block above for each rule. Order roughly by how often the
     rule matters / how severe a violation is. -->
