# Candlestick-Master

Specification repository for candlestick pattern definitions.

**Current phase:** collecting and organising pattern specifications.
**Pine Script implementation has not started and will not start** until the instruction
`ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION.` is given.

## Layout

```
PATTERN_REGISTRY.md      Single source of truth: one row per pattern
CONVENTIONS.md           Classification, naming, abbreviation and fidelity rules
AUDIT_LOG.md             Aggregated audit flags and ambiguities
patterns/
  _TEMPLATE.md           Spec file template
  <direction>/           bullish | bearish | neutral
    <category>/          reversal | continuation | exhaustion | neutral | gap
      <pattern>.md       One specification file per pattern
```

The full 3 x 5 direction/category matrix exists so that every supplied pattern has a
deterministic destination and no routing question needs to be asked.

## What each spec file records

Each pattern file follows [`patterns/_TEMPLATE.md`](patterns/_TEMPLATE.md) and records:
abbreviation, candle count, all ideal timeframes, structural OHLC rules, contextual
requirements, confirmation rules, failure conditions, RSI/EMA/volume validation, and —
kept separately from the rules — ambiguities and audit flags.

## Fidelity

Supplied specifications are transcribed, not reinterpreted. Where a supplied rule appears
technically incorrect it is preserved verbatim and annotated with an `AUDIT FLAG` block
explaining the concern. Nothing is silently corrected. See [`CONVENTIONS.md`](CONVENTIONS.md)
section 7.
