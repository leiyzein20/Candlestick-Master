# Conventions

Rules governing how supplied pattern specifications are classified, named, and recorded.
These conventions exist so that no pattern requires a routing question: every supplied
specification resolves to exactly one directory and one registry row.

---

## 1. Directory hierarchy

```
patterns/<direction>/<primary-category>/<pattern-name>.md
```

**Direction** (exactly one, lowercase directory name):

| Direction | Meaning |
|---|---|
| `bullish` | Pattern implies or resolves to upward price movement |
| `bearish` | Pattern implies or resolves to downward price movement |
| `neutral` | Pattern is directionless on its own; resolution depends on context or breakout |

**Category** (exactly one primary, lowercase directory name):

| Category | Meaning |
|---|---|
| `reversal` | Signals a change in the prevailing trend direction |
| `continuation` | Signals resumption of the prevailing trend after a pause |
| `exhaustion` | Signals depletion of the driving force of the current move (climax, blow-off, thrust failure) |
| `neutral` | Indecision / balance; no directional or trend implication asserted |
| `gap` | The defining structural feature is a price gap between candles |

The full 3 x 5 matrix is materialised, including combinations that are rare in practice
(e.g. `neutral/exhaustion`), so that classification never fails for lack of a destination.

## 2. Primary category selection

A pattern may belong to more than one conceptual category. The **primary** category is
selected from the supplied specification using this precedence, applied top-down:

1. If the supplied specification states a primary category explicitly, that value wins.
   No inference is performed.
2. Otherwise, if the pattern's defining structural rule is a gap between candle bodies or
   ranges, primary category is `gap`.
3. Otherwise, if the supplied contextual requirement is an extended/climactic prior move and
   the supplied confirmation concerns the failure of that move, primary category is `exhaustion`.
4. Otherwise, if the supplied contextual requirement is a prior trend that the pattern is
   specified to terminate, primary category is `reversal`.
5. Otherwise, if the supplied contextual requirement is a prior trend that the pattern is
   specified to resume, primary category is `continuation`.
6. Otherwise, primary category is `neutral`.

All non-primary categories that the supplied specification implies are recorded in the
spec file's `Secondary Categories` field and in the registry. They do not affect file location.

If the supplied specification is genuinely ambiguous between two primary categories, the
pattern is filed under the higher-precedence category above, and the ambiguity is recorded
verbatim in the spec file's **Ambiguities** section and in `AUDIT_LOG.md`. It is not resolved
by invention.

## 3. File naming

- Spec filename: kebab-case of the supplied pattern name, `.md` extension.
  Example: `Bullish Engulfing` -> `patterns/bullish/reversal/bullish-engulfing.md`
- The supplied name is preserved verbatim inside the file; only the filename is normalised.
- If two supplied patterns normalise to the same filename, the later one is suffixed with a
  disambiguator drawn from the supplied specification, and the collision is noted in `AUDIT_LOG.md`.

## 4. Abbreviation assignment

Format: `<DIR>-<ROOT>`

- `<DIR>` is the direction code: `BU` (bullish), `BR` (bearish), `NT` (neutral).
- `<ROOT>` is 2-6 uppercase alphanumeric characters derived from the supplied pattern name:
  - Multi-word names: initials of the significant words, extended with additional letters from
    the final word until unique (`Morning Star` -> `MS`, `Morning Doji Star` -> `MDS`).
  - Single-word names: the first consonant-preserving contraction (`Hammer` -> `HAM`,
    `Marubozu` -> `MRBZ`).
  - Direction words already encoded in `<DIR>` (Bullish, Bearish, Rising, Falling, Up, Down)
    are dropped from `<ROOT>` unless dropping them causes a collision.
- Abbreviations are globally unique across all directions and categories.
- If the supplied specification provides its own abbreviation, that value is used verbatim and
  this scheme is not applied. A supplied abbreviation that collides with an existing one is
  recorded in `AUDIT_LOG.md` and left unchanged.

## 5. Candle count

Recorded as the exact integer count of candles the supplied structural rules describe.
If the supplied specification permits a variable count, the range is recorded as `N-M`
(e.g. `3-5`) together with the supplied rule that governs the variability.

## 6. Timeframes

All ideal timeframes named in the supplied specification are recorded, in the order supplied.
No timeframe is added, removed, generalised, or ranked beyond what was supplied.

## 7. Fidelity rules

- Supplied trading rules are transcribed, not reinterpreted. Wording is preserved where the
  wording carries a threshold, comparison, or condition.
- Nothing is normalised into a different rule, tightened, loosened, or merged with another rule.
- Missing fields are recorded as `NOT SUPPLIED` rather than filled in by inference.
- Where a supplied rule appears technically incorrect, internally inconsistent, or in conflict
  with another supplied rule, the original is preserved verbatim and annotated immediately below it:

```
AUDIT FLAG:
[explanation]
```

  Every audit flag is also copied into `AUDIT_LOG.md`. Audit flags never modify the rule they annotate.

- Ambiguities are recorded separately from rules, in the spec file's **Ambiguities** section
  and in `AUDIT_LOG.md`. An ambiguity is an under-determined supplied rule; an audit flag is a
  supplied rule that appears incorrect. A single item may warrant both.

## 8. Implementation gate

No Pine Script is written until the exact instruction is given:

> ALL PATTERN DATA PROVIDED. BEGIN IMPLEMENTATION.

Until then this repository holds specifications, classification, and registry data only.
