# CONTINUATION PATTERNS

`Primary category: Continuation`, any direction.

Filename: `bull_<slug>.md` / `bear_<slug>.md` / `neut_<slug>.md` — the directory is shared,
so the prefix carries the direction.

## What lands here

An existing move is expected to **resume** after a pause. The supplied text requires a prior
move in the *same* direction as the pattern implies.

The distinction from a reversal is mechanical: a reversal requires a prior **opposite**
move, a continuation a prior **same-direction** move (`CLASSIFICATION.md` §4, rungs 3–4).

## Category-specific checks at intake

* **Trend requirement is usually structural here.** "Resumes an uptrend" is meaningless
  without an uptrend, so a missing trend statement produces an `MS-` entry.
* **The trend factor scores differently.** For a bullish continuation, the *supporting*
  trend state is `UPTREND` — the same state that would oppose a bullish reversal. This is
  handled by the registry's `reqTrend` field, not by special-casing in the scoring code
  (`engines/VALIDATION_ENGINE.md`).
* **Contradiction cap awareness.** A bullish continuation in a `DOWNTREND` is exactly the
  case the anti-inflation cap exists for (`MASTER_SPECIFICATION.md` §9.1).
* **Gaps are common but usually not definitional.** Apply the §3 test in
  `CLASSIFICATION.md`: if removing the gap still leaves a named candle formation, this stays
  a continuation with `Gap` as a secondary category.
* **Confirmation defaults to a break in the direction of the prevailing move**, which for a
  continuation is the same as its own direction — the default rule in `CV-CONF-001` already
  covers it, keyed off `Dir`.

## Index

| ID | ABBR | Name | Dir | Candles | Timeframes | Status |
| --- | --- | --- | --- | --- | --- | --- |
| *(none yet)* | | | | | | |
