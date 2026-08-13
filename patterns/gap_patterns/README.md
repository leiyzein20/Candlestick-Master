# GAP PATTERNS

`Primary category: Gap`, any direction — patterns whose **identity is the gap itself**.

Filename: `bull_<slug>.md` / `bear_<slug>.md` / `neut_<slug>.md`.

## The admission test

From `CLASSIFICATION.md` §3, applied mechanically:

1. Remove the gap requirement from the supplied specification. Is a recognisable, separately
   named candle formation still described?
   * **Yes** → the pattern does not belong here. It keeps its behavioural category
     (`Reversal` / `Exhaustion` / `Continuation`) and records `Gap` as a **secondary**
     category, with the gap rule captured in template §12.
   * **No** → it belongs here.

So a star-family formation that requires a gap is *not* a gap pattern, while a specification
whose whole content is "price gaps beyond the prior range and behaves thus" is.

## Category-specific checks at intake

* **Gap type must be explicit.** True range gap (`L > H1` / `H < L1`) and body gap
  (`bodyBottom > bodyTop1` / `bodyTop < bodyBottom1`) are different tests and are never
  conflated. Outside the star family the engine default for an unqualified "gap" is the
  **true range gap** (`CV-REL-005`); the choice is recorded per pattern.
* **Instrument reality is documented, not hidden.** 24-hour instruments (spot FX, crypto)
  rarely produce true intraday range gaps; equities gap at every session boundary. A gap
  pattern is therefore effectively session-dependent, and its pattern file states which
  instrument classes can produce it at all. No rule is relaxed to manufacture gaps on
  instruments that do not gap (`MASTER_SPECIFICATION.md` §14.7).
* **Minimum size.** "Significant gap" needs a number; the engine offers
  `gapUpSizeAtr >= gapMinAtr` with default `0` (`CV-REL-006`). A supplied size wins; a vague
  size becomes an `AM-` entry.
* **Session gaps vs data holes.** A missing bar, a holiday, or a feed outage can look like a
  gap. This is recorded as a known limitation per pattern; nothing in Pine can distinguish a
  genuine liquidity gap from absent data.
* **Fill tracking.** "The gap is filled" is a confirmation/failure rule, not structure, and
  goes in template §§14–15 with an explicit price level (typically `H1` for an up-gap), so
  the lifecycle engine can evaluate it on closed candles only.

## Index

| ID | ABBR | Name | Dir | Gap type | Candles | Timeframes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *(none yet)* | | | | | | | |
