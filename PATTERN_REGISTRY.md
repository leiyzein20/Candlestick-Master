# PATTERN_REGISTRY

Master index of all candlestick/chart pattern specifications in this repository.

## Organizational hierarchy

Every pattern file lives at:

```
patterns/<direction>/<primary-category>/<pattern-name>.md
```

**Direction** (first level):

- `bullish`
- `bearish`
- `neutral`

**Category** (second level):

- `reversal`
- `continuation`
- `exhaustion`
- `neutral`
- `gap`

A pattern may conceptually belong to more than one category, but it is filed under its
**primary** category as determined by the supplied specification. Secondary categories
are noted in the pattern file and in the registry table below.

## Conventions

- Specifications are recorded **verbatim as supplied**. They are never rewritten into
  different trading rules.
- Anything that appears technically incorrect is preserved as supplied and marked in the
  pattern file with an `AUDIT FLAG:` block explaining the concern. Nothing is silently
  "fixed".
- Ambiguities in a supplied specification are recorded in a dedicated **Ambiguities**
  section of the pattern file (and flagged in the registry table).
- No Pine Script is implemented until the explicit instruction
  `"ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION."` is given.

## Registry

| # | Pattern | Abbrev. | Direction | Primary Category | Secondary Categories | Candles | Ideal Timeframes | File | Audit Flags | Ambiguities |
|---|---------|---------|-----------|------------------|----------------------|---------|------------------|------|-------------|-------------|
| — | *(no patterns registered yet)* | — | — | — | — | — | — | — | — | — |

## Abbreviation index

Abbreviations are unique across the registry.

| Abbrev. | Pattern |
|---------|---------|
| — | *(none assigned yet)* |
