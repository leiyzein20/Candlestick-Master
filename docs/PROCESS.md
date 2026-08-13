# Pattern Intake & Organization Process

This document defines the standing operating procedure for collecting, classifying, and
recording candlestick pattern specifications in this repository. It is authoritative until
explicitly amended.

## Scope

This process governs **specification and organization only**. Pine Script implementation is
explicitly out of scope until the maintainer sends the exact phrase:

> ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION.

Until that phrase is received, no `.pine` files should be created or modified for pattern logic.

## Classification Hierarchy

Every pattern is filed under `patterns/<direction>/<category>/`.

### Direction (top level)

- `bullish`
- `bearish`
- `neutral`

### Category (second level)

- `reversal`
- `continuation`
- `exhaustion`
- `neutral`
- `gap`

A pattern may conceptually relate to more than one category, but exactly one **primary
category** must be chosen based on the supplied specification, and the file lives under that
primary category's directory. Secondary/conceptual category relationships are recorded as notes
in the pattern file and in the registry's "Ambiguities / Notes" column, not by duplicating the
file.

## Intake Steps (performed for every pattern submitted)

1. Determine the correct directory (`patterns/<direction>/<category>/`) from the supplied
   specification.
2. Create the pattern specification file at
   `patterns/<direction>/<category>/<pattern-slug>.md` using `docs/PATTERN_SPEC_TEMPLATE.md`.
3. Add a row for the pattern to `PATTERN_REGISTRY.md`.
4. Assign its abbreviation (as supplied, or a reasonable short code if none was supplied —
   flagged per the rules below).
5. Record its candle count.
6. Record all ideal timeframes.
7. Record structural OHLC rules exactly as supplied.
8. Record contextual requirements (e.g. required prior trend, location, prior candle relations).
9. Record confirmation rules.
10. Record failure conditions.
11. Record RSI / EMA / volume validation rules.
12. Record ambiguities separately, in their own section — never merged silently into the rules.

## Fidelity Rules (non-negotiable)

- **Never rewrite supplied trading rules.** Transcribe the specification as given, preserving
  the original thresholds, comparisons, and logic structure.
- **Never silently "fix" a rule that looks technically questionable.** Instead:
  - Preserve the original specification verbatim in the appropriate rule section.
  - Add a clearly marked callout directly beneath it:

    ```
    AUDIT FLAG:
    [explanation of the suspected issue]
    ```

  - Audit flags are also aggregated in the "Audit Flags" section of the pattern file and noted
    in the registry.
- **Ambiguities are not guesses.** If a detail is missing or underspecified, record it under
  "Ambiguities" in the pattern file rather than inventing a value. Only ask the maintainer for
  clarification if the classification (direction/category) itself is genuinely ambiguous —
  missing secondary details should simply be logged as open ambiguities.

## Files

- `PATTERN_REGISTRY.md` — master index of every pattern, one row each.
- `docs/PATTERN_SPEC_TEMPLATE.md` — template used to create each pattern's spec file.
- `patterns/<direction>/<category>/<pattern-slug>.md` — one file per pattern.

## Status Lifecycle

Each pattern in the registry has a `Status` column with one of:

- `Specified` — specification captured, organized, no ambiguities blocking review.
- `Specified (flagged)` — specification captured, but has one or more open Audit Flags and/or
  Ambiguities that should be reviewed before implementation.
- `Implemented` — Pine Script has been written for this pattern (only possible after the
  maintainer issues the "ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION." instruction).
