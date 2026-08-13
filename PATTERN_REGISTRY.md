# Pattern Registry

Master index of all candlestick pattern specifications collected so far. See
`docs/PROCESS.md` for the intake process and `docs/PATTERN_SPEC_TEMPLATE.md` for the
per-pattern file template.

Pine Script implementation has **not** begun. Implementation begins only after the maintainer
sends: "ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION."

## Index

| Pattern Name | Abbr | Direction | Primary Category | Candle Count | Ideal Timeframes | File | Status | Audit Flags | Ambiguities |
|---|---|---|---|---|---|---|---|---|---|
| _(none yet — awaiting first pattern submission)_ | | | | | | | | | |

## Legend

- **Status:**
  - `Specified` — captured and organized, no open issues.
  - `Specified (flagged)` — has open Audit Flag(s) and/or Ambiguities; review before
    implementation.
  - `Implemented` — Pine Script written (post go-ahead only).
- **Audit Flags / Ambiguities columns:** `None` or a short pointer to the relevant section in
  the pattern's spec file (e.g. "See Audit Flags §").

## Directory Structure

```
patterns/
  bullish/
    reversal/
    continuation/
    exhaustion/
    neutral/
    gap/
  bearish/
    reversal/
    continuation/
    exhaustion/
    neutral/
    gap/
  neutral/
    reversal/
    continuation/
    exhaustion/
    neutral/
    gap/
```
