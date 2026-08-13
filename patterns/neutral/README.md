# NEUTRAL PATTERNS

Holds two things:

1. `Direction: Neutral` patterns, whatever their primary category;
2. any pattern whose `Primary category` is `Neutral`.

Filename: `neut_<slug>.md`, or `bull_` / `bear_` prefix in the second case.

## What lands here

Balance and indecision: the pattern itself expresses no directional expectation, or the
supplied text describes equilibrium between buyers and sellers.

A `Neutral`-direction pattern that the supplied text presents as a turning signal keeps
`Primary: Reversal` in the registry while living in this directory — the routing table
allows that combination explicitly (`CLASSIFICATION.md` §2).

## Category-specific checks at intake

* **Direction resolution for confirmation.** A neutral pattern has no side, so the generic
  confirmation rule resolves direction by whichever side breaks first: the resolved
  direction is recorded on the event, and the tooltip shows it
  (`MASTER_SPECIFICATION.md` §8). If the supplied text gives its own rule, that wins.
* **Scoring asymmetry.** Trend, location, RSI, and EMA factors need a direction to be
  "supportive". For a neutral pattern before resolution, the directional factors are
  **excluded** from `maxScore` rather than scored as zero, so an unresolved neutral pattern
  is not artificially pushed to `WEAK` (`engines/VALIDATION_ENGINE.md`).
* **Doji tolerance is a threshold, not a metaphysical equality.** `open == close` almost
  never holds exactly, so the doji family uses `bodyPct <= dojiMaxBody` (`CV-BODY-001`), and
  any supplied numeric tolerance overrides it.
* **Flat candles.** `close == open` exactly (a four-price bar on illiquid data) is neither
  bullish nor bearish; a zero-range bar is rejected outright
  (`MASTER_SPECIFICATION.md` §§3.3, 3.5).
* **Label position.** Neutral labels are drawn above the bar by default (`CV-DISP-001`).

## Index

| ID | ABBR | Name | Dir | Primary | Candles | Timeframes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *(none yet)* | | | | | | | |
