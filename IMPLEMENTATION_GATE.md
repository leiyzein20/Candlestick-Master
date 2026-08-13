# IMPLEMENTATION GATE

## State

```
┌──────────────────────────────────────────────────────────────────┐
│  GATE: CLOSED                                                    │
│  Phase: SPECIFICATION COLLECTION                                 │
│  Pine Script written: NONE (by instruction)                      │
└──────────────────────────────────────────────────────────────────┘
```

## The rule

No Pine Script is written — not a skeleton, not a harness, not a "just to prove it
compiles" file — until the project owner sends, verbatim:

```
ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION.
```

Until then, work is limited to:

* receiving pattern specifications,
* classifying and filing them (`patterns/CLASSIFICATION.md`),
* registering them (`PATTERN_REGISTRY.md`),
* recording ambiguities, conflicts, and audit flags (`CONFLICT_LOG.md`),
* refining engine specifications (`engines/*.md`) and tests (`tests/*.md`),
* repo-side tooling that is not Pine (`tools/`).

## Why this file exists

An earlier draft of this repo planned a "Phase 0 Pine architecture harness" containing
three provisional patterns. That plan was **withdrawn** on owner instruction. Two reasons
it was withdrawn are worth keeping visible, because they are permanent rules and not a
one-off correction:

1. **Provisional pattern rules are still invented rules.** Writing plausible Hammer
   numbers before the Hammer specification arrives creates a definition that later has to
   be un-learned, and risks the supplied spec being quietly bent toward it.
2. **Architecture stability does not require code to prove it.** The engine contracts,
   execution order, registry schema, and resource budget are all falsifiable on paper
   (`ARCHITECTURE.md` §§2–6). What code would prove — that Pine accepts the syntax — is
   verified in one pass at the start of implementation, against real specifications.

Consequence: `pine/` is empty apart from a placeholder, and no file in this repo contains
Pine source.

## What happens the moment the gate opens

In this order, per `DEVELOPMENT_PLAN.md`:

1. Re-read `CONFLICT_LOG.md`. Any `BLOCKING` entry is raised before code, not after.
2. Freeze the registry: IDs, abbreviations, categories, timeframe lists.
3. Build the engine stack only (sections 0–14, 16–18 of `ARCHITECTURE.md` §7) with **zero**
   patterns, and compile it. This is the architecture proof, done with real specs in hand.
4. Then implement patterns in batches of 3–5, compiling and running the batch gate
   checklist after every batch.
5. Stop on the first failure and fix the root cause before adding anything.

## Signals that do NOT open the gate

* "Here are the next patterns."
* "Looks good, continue."
* "How would you code this one?"
* Any partial-batch delivery, however large.

Anything short of the exact sentence keeps the gate closed and keeps work in the
specification phase.
