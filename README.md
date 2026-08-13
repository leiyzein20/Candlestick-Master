# CANDLESTICK MASTER

An educational candlestick-pattern **recognition and validation** engine for TradingView
(Pine Script v6).

> **Status: PHASE 0 — specification collection.**
> The pattern database is intentionally **empty**. It is waiting for the 50+ supplied
> pattern specifications. See [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md) and
> [`patterns/INTAKE.md`](patterns/INTAKE.md).
>
> **IMPLEMENTATION GATE — no Pine Script is written until the project owner states,
> verbatim: `ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION.`**
> `pine/` therefore contains no code yet, by instruction. See
> [`IMPLEMENTATION_GATE.md`](IMPLEMENTATION_GATE.md).

---

## What this project is

A strict, rule-based pattern engine that:

1. **Recognises pattern structure** mathematically, from OHLC only.
2. **Then** validates that structure against context (trend, location, RSI, EMA, volume).
3. **Then** tracks the outcome (`DETECTED` → `CONFIRMED` / `FAILED` / `EXPIRED`) using
   closed candles only.

Structure and context are never mixed. A Bullish Engulfing does not stop being a Bullish
Engulfing because RSI is neutral — it just scores lower. See
[`MASTER_SPECIFICATION.md` §2](MASTER_SPECIFICATION.md).

## What this project is not

* It is not a trading system. It never places, sizes, or manages an order.
* It does not claim win rates, hit rates, or edge. Any statistic that arrives with a
  supplied specification is stored verbatim and labelled `User-provided reference`, and is
  excluded from every quantitative calculation. See
  [`MASTER_SPECIFICATION.md` §14](MASTER_SPECIFICATION.md).
* It does not observe institutional order flow. "Demand" / "supply" / "major support" are
  explicitly documented *approximations* built from confirmed swing pivots. See
  [`engines/LOCATION_ENGINE.md`](engines/LOCATION_ENGINE.md).

---

## Repository map

| Path | Purpose |
| --- | --- |
| [`MASTER_SPECIFICATION.md`](MASTER_SPECIFICATION.md) | **Normative** global rules. Single source of truth for every formula, threshold, state machine, and output format. |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Layers, data flow, module boundaries, Pine resource budget, no-repaint design. |
| [`PATTERN_REGISTRY.md`](PATTERN_REGISTRY.md) | The one authoritative index of every pattern: ID, abbreviation, category, timeframes, implementation status. |
| [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md) | Phased build order, per-batch gate checklist, definition of done. |
| [`CONFLICT_LOG.md`](CONFLICT_LOG.md) | Every contradiction / ambiguity / missing rule found in supplied specs. Nothing is resolved silently. |
| `patterns/<category>/` | One file per pattern, verbatim spec + derived machine rules. |
| [`patterns/SPEC_TEMPLATE.md`](patterns/SPEC_TEMPLATE.md) | The mandatory 22-field pattern specification form. |
| [`patterns/INTAKE.md`](patterns/INTAKE.md) | The process applied to each supplied specification. |
| `engines/*.md` | One specification per engine (formulas, Pine mapping, edge cases, open questions). |
| `tests/*.md` | Test plans plus machine-readable vectors in `tests/vectors/`. |
| [`patterns/CLASSIFICATION.md`](patterns/CLASSIFICATION.md) | Deterministic direction × category → directory routing. Removes the need to ask where a pattern goes. |
| `pine/` | Reserved for the deliverable `CandlestickMaster.pine`. **Empty until the gate opens.** |
| `tools/` | Repo-side helpers: spec/registry linter, engine reference model, vector runner. |
| [`docs/DEFINITION_CONVERSIONS.md`](docs/DEFINITION_CONVERSIONS.md) | Every vague phrase ("clear downtrend", "major support") → explicit measurable rule, with an ID. |
| [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | Exact meaning of every term used in specs (e.g. *candle midpoint* vs *body midpoint*). |

## How a supplied pattern is handled

No questions asked about filing; the routing is mechanical
([`patterns/CLASSIFICATION.md`](patterns/CLASSIFICATION.md)).

1. Classify: direction (Bullish / Bearish / Neutral) × primary category (Reversal /
   Continuation / Exhaustion / Neutral / Gap) → target directory.
2. Create `patterns/<dir>/<slug>.md` from
   [`SPEC_TEMPLATE.md`](patterns/SPEC_TEMPLATE.md), with the supplied text preserved
   **verbatim** in the *As Supplied* block.
3. Assign and reserve the abbreviation; register the row in
   [`PATTERN_REGISTRY.md`](PATTERN_REGISTRY.md).
4. Record candle count, every ideal timeframe, structural OHLC rules, contextual
   requirements, confirmation rule, failure condition, and RSI/EMA/volume validation.
5. Record ambiguities and missing rules **separately**, in the pattern file's *Ambiguity
   Register* and in [`CONFLICT_LOG.md`](CONFLICT_LOG.md).
6. If something looks technically wrong, the original is kept unchanged and an
   `AUDIT FLAG:` note is added beside it. Nothing is ever silently corrected, reworded,
   or "improved".

## Local tooling

```bash
python3 tools/spec_lint.py      # pattern files vs template vs PATTERN_REGISTRY.md consistency
python3 tools/run_tests.py      # engine test vectors in tests/vectors/ vs the reference model
```

`tools/reference_model.py` is a Python mirror of the **engine mathematics only** (candle
measurements and candle-to-candle relationships). It exists so the numbers in
`MASTER_SPECIFICATION.md` are executable and regression-checked before any Pine is
written. It contains no pattern definitions.

A Pine static checker (`tools/pine_lint.py`) is specified in
[`tests/PINE_COMPILE_CHECKLIST.md`](tests/PINE_COMPILE_CHECKLIST.md) and lands with the
first Pine batch. Nothing replaces a real paste-and-compile in TradingView.

## Next action

Send the pattern specifications, in any order and any batch size. They will be organised,
registered, and audited as they arrive. Pine implementation begins only on the explicit
go-ahead.
