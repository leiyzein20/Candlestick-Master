# pine/

Reserved for the deliverable:

```
pine/CandlestickMaster.pine
```

**This directory is intentionally empty of code.**

Pine Script is not written until the project owner sends, verbatim:

```
ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION.
```

See [`../IMPLEMENTATION_GATE.md`](../IMPLEMENTATION_GATE.md). `tools/spec_lint.py` fails the
build if a `.pine` file appears here while the gate is recorded as closed, so the rule is
enforced rather than merely stated.

## What is already decided

So that implementation is transcription rather than design:

| Decision | Where |
| --- | --- |
| Section layout of the file (0–18) | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) §7 |
| Execution order within a bar | `ARCHITECTURE.md` §3 |
| Which values are computed once and shared | [`../engines/README.md`](../engines/README.md) |
| Every formula and threshold | [`../MASTER_SPECIFICATION.md`](../MASTER_SPECIFICATION.md) |
| Registry-driven pattern dispatch | `ARCHITECTURE.md` §4 |
| Resource budget and rejected designs | `ARCHITECTURE.md` §6 |
| Label, tooltip, panel, and alert formats | [`../engines/DISPLAY_ENGINE.md`](../engines/DISPLAY_ENGINE.md) |
| v6 constraints to honour | `MASTER_SPECIFICATION.md` §13 |
| The build order and per-batch gate | [`../DEVELOPMENT_PLAN.md`](../DEVELOPMENT_PLAN.md) |

## What the file will declare

```
//@version=6
indicator("Candlestick Master", overlay = true, max_labels_count = 500)
```

with zero boxes, zero lines, one table, zero `request.*` calls, and a fixed set of ~18 `ta.*`
call sites that does not grow as patterns are added.

## Verification path

1. `python3 tools/run_tests.py` — engine mathematics.
2. `python3 tools/spec_lint.py` — specification consistency.
3. `python3 tools/pine_lint.py` — static Pine heuristics (lands with the first Pine batch).
4. [`../tests/PINE_COMPILE_CHECKLIST.md`](../tests/PINE_COMPILE_CHECKLIST.md) — the manual gate
   in TradingView. Nothing replaces this: only TradingView compiles Pine.
