# DEVELOPMENT PLAN

Accuracy over pattern count. Maintainability over short code. Testing over assumptions.

---

## Where the project is

```
PHASE 0  scaffold ................................. COMPLETE
PHASE 1  specification intake ..................... IN PROGRESS  <-- waiting on pattern data
PHASE 2  engine implementation .................... BLOCKED by the implementation gate
PHASE 3  pattern batches .......................... BLOCKED
PHASE 4  full-system review ....................... BLOCKED
```

The gate: **no Pine Script until the owner sends
`ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION.`**
See [`IMPLEMENTATION_GATE.md`](IMPLEMENTATION_GATE.md).

---

## Phase 0 — scaffold (complete)

| Deliverable | State |
| --- | --- |
| Project structure | done |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) — layers, execution order, registry design, resource budget, no-repaint design | done |
| [`MASTER_SPECIFICATION.md`](MASTER_SPECIFICATION.md) — normative rules, every formula and threshold with provenance | done |
| [`PATTERN_REGISTRY.md`](PATTERN_REGISTRY.md) — schema, status lifecycle, abbreviation policy, invariants | done |
| 12 engine specifications in [`engines/`](engines/) | done |
| [`patterns/`](patterns/) — routing, 20-section template, intake procedure, category guidance | done |
| [`tests/`](tests/) — plans, 2435 executable checks, Pine compile checklist | done |
| [`docs/DEFINITION_CONVERSIONS.md`](docs/DEFINITION_CONVERSIONS.md) — 65 registered engine defaults | done |
| [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | done |
| `tools/` — reference model, vector runner, specification linter | done |
| Pattern database | **empty, by design** |

Verification available right now:

```bash
python3 tools/run_tests.py      # 2435 checks against the specification's own numbers
python3 tools/spec_lint.py      # registry / routing / template / id-resolution invariants
```

## Phase 1 — specification intake (in progress)

For each supplied pattern, the twelve steps in [`patterns/INTAKE.md`](patterns/INTAKE.md):
classify, file, register, abbreviate, record candle count, record **all** timeframes, record
structural rules, record context, record confirmation, record failure, record RSI/EMA/volume,
record ambiguities separately.

Per batch:

1. Capture supplied text verbatim before any analysis.
2. File by the routing table — no questions unless genuinely contradictory.
3. Translate to machine rules beside the original, citing a `CV-` id for every default used.
4. Raise `CF-` / `AM-` / `MS-` / `AF-` entries in [`CONFLICT_LOG.md`](CONFLICT_LOG.md).
5. Write the seven mandatory test cases plus edge cases from the **specification**, before any
   code exists.
6. Run `spec_lint.py`.
7. Report back with the batch intake report, whose only actionable section is
   "needs owner decision".

Exit criteria: every supplied pattern is `SPECIFIED` or `TESTS-READY`, and every `BLOCKING`
entry is resolved or explicitly accepted.

## Phase 2 — engine implementation (on gate open)

**Zero patterns.** Sections 0–14 and 16–18 of [`ARCHITECTURE.md`](ARCHITECTURE.md) §7 only:
inputs, timeframe engine, OHLC/wick-body, relationships, shared indicators, trend, RSI, EMA,
volume, location, validation, confirmation, display, registry, emit/gating, alerts, panel.

Compile that. It is the architecture proof, done once, with real specifications in hand:

* every `ta.*` call site exists exactly once and matches the list in
  [`engines/README.md`](engines/README.md);
* the registry loop, the pending queue, the label pipeline, and the alert layer all run with an
  empty pattern set;
* the info panel reports warm-up and timeframe state correctly;
* `tests/PINE_COMPILE_CHECKLIST.md` §§1–3 and 8 pass.

Then two throwaway probe patterns — the crudest possible structures (a single bullish candle, a
single bearish candle), deleted before Phase 3 — purely to exercise detect → confirm → fail →
expire, the label pipeline, and the alert payloads end to end. They are debug fixtures, not
pattern definitions, and they never enter the registry.

## Phase 3 — pattern batches (on gate open, after Phase 2)

Batches of **3–5** patterns, ordered by dependency: simplest single-candle structures first,
then multi-candle, then gap-dependent, then anything needing a new engine capability.

The owner's Phase 1 list (Hammer, Bullish Engulfing, Piercing Line) is the first batch **once
those three specifications have arrived**. They are not pre-written from memory.

After **every** batch, in order, per [`tests/PINE_COMPILE_CHECKLIST.md`](tests/PINE_COMPILE_CHECKLIST.md):

1. Compile.
2. Check syntax and types (`na` handling, series vs simple).
3. Check historical indexing (candle *k* ↔ offset `n - k`).
4. Check repainting (replay bar by bar, then reload, then compare).
5. Check timeframe logic on every ideal timeframe **and** on one excluded timeframe.
6. Check labels and tooltips against `MASTER_SPECIFICATION.md` §10.
7. Check alerts.
8. Check resource usage against `ARCHITECTURE.md` §6.
9. Check that every previously implemented pattern still fires on its VALID vector.

**On any failure: stop.** Find the root cause — not the reported line — fix it, re-check the
whole affected module, then look for the secondary errors the first one was masking. No new
pattern is added while anything is broken.

Record the batch result block in `tests/PATTERN_TESTS.md` §10. An unrecorded batch is untested.

## Phase 4 — full-system review

| # | Review | Against |
| --- | --- | --- |
| 1 | Pine v6 compliance, whole file | `tests/PINE_COMPILE_CHECKLIST.md` §§1–3 |
| 2 | Resource limits, whole file | `ARCHITECTURE.md` §6 |
| 3 | No-repaint, whole file | `MASTER_SPECIFICATION.md` §12 |
| 4 | Every pattern's rules against its *As Supplied* block, line by line | pattern files §1 vs §§7–15 |
| 5 | Every `[ENGINE-DEFAULT]` in use is registered | `docs/DEFINITION_CONVERSIONS.md` |
| 6 | No unresolved `BLOCKING` entry | `CONFLICT_LOG.md` |
| 7 | No fabricated statistic anywhere | `MASTER_SPECIFICATION.md` §14 |
| 8 | Rarity preserved — recorded signal counts match expectations from the specifications | `tests/PATTERN_TESTS.md` X5 |
| 9 | Definition of done | `MASTER_SPECIFICATION.md` §15 |

Only after all nine is the project described as finished.

---

## Standing rules

| Rule | Consequence |
| --- | --- |
| A rule is never loosened to produce more signals | a rare pattern stays rare |
| A supplied rule is never silently corrected | `AUDIT FLAG:` beside it, implemented as supplied |
| A contradiction is never resolved by preference | `CF-` entry, pattern held |
| A number is never invented | either a registered `CV-` default or an `AM-` entry |
| A pattern never calls `ta.*` | engines compute once, patterns consume |
| Nothing is confirmed on a forming bar | closed candles only |
| No probability, win rate, or reliability figure is manufactured | supplied ones are stored as `User-provided reference`, excluded from all maths |
| The script never trades | no `strategy.*` calls, ever |

## Risk register

| Risk | Mitigation |
| --- | --- |
| 50+ patterns exceed Pine's compiled-script limits | registry-driven design: fixed engine cost, one row + one function per pattern (`ARCHITECTURE.md` §4) |
| String building for tooltips becomes the bottleneck | strings built only at detection and resolution, never per pattern per bar |
| Pivot confirmation delay makes divergence look late | documented, tested, and preferred over a repainting alternative |
| Supplied specifications contradict each other across patterns | `CONFLICT_LOG.md`, plus the duplicate/superset scan at intake |
| Two similarly named patterns get merged | forbidden; asserted by test X4 |
| Ambiguity defaults quietly become "the rules" | every default has a `CV-` id, a rationale, and an input; every pattern cites the ids it relies on |
| Label budget exhausted on dense charts | ≤ 4 labels per bar per side, 500 declared, oldest culled by Pine |
| An implementation drifts from its specification | vectors written from the specification before the code, and §4 of Phase 4 re-reads both |
