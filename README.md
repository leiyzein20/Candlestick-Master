# Candlestick-Master

A structured library of candlestick pattern specifications, organized by direction and
category, intended for eventual Pine Script implementation.

## Status

This repository is currently in the **specification/organization phase**. Pattern
specifications are being collected and classified. No Pine Script implementation exists yet —
implementation begins only once explicitly instructed.

## Structure

- `PATTERN_REGISTRY.md` — master index of every pattern collected so far.
- `docs/PROCESS.md` — the intake process, classification hierarchy, and fidelity rules used to
  organize every submitted pattern.
- `docs/PATTERN_SPEC_TEMPLATE.md` — the template used to write each pattern's spec file.
- `patterns/<direction>/<category>/<pattern-slug>.md` — one specification file per pattern,
  where:
  - `direction` is one of `bullish`, `bearish`, `neutral`
  - `category` is one of `reversal`, `continuation`, `exhaustion`, `neutral`, `gap`

See `docs/PROCESS.md` for full details on how patterns are classified and recorded.
