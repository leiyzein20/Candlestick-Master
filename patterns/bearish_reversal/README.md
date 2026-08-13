# BEARISH REVERSAL PATTERNS

`Direction: Bearish` + `Primary category: Reversal`.

Filename: `<slug>.md` (no direction prefix — the directory carries it).

## What lands here

A prior **upward** move is expected to turn downward. The pattern's own rules require, or
its supplied text describes, a preceding advance.

Does **not** land here:

| Case | Goes to |
| --- | --- |
| bearish, but the spec frames it as a buying climax / blow-off top | [`../exhaustion/`](../exhaustion/) |
| bearish, and the gap **is** the pattern | [`../gap_patterns/`](../gap_patterns/) |
| bearish, and it resumes an existing downtrend | [`../continuation/`](../continuation/) |
| indecision candle used as a topping signal (`Neutral` direction) | [`../neutral/`](../neutral/) |

## Category-specific checks at intake

* **Required trend must be recorded.** A bearish reversal without a stated prior uptrend
  gets an `MS-` entry rather than an assumed uptrend.
* **Confirmation direction is downward.** Default trigger: a closed candle closing below the
  pattern low; default invalidation: a closed candle closing above the pattern high
  (`CV-CONF-001`).
* **Location factor is `AT_RESISTANCE` / `AT_SUPPLY` / `SWING_HIGH`**.
* **Mirror-symmetry is not assumed.** A bearish pattern is *not* filled in by mirroring its
  bullish counterpart. If the supplied bearish spec omits a rule its bullish twin has, that
  omission is recorded as `MS-`, not silently copied across
  (`MASTER_SPECIFICATION.md` §1.2).

## Index

| ID | ABBR | Name | Candles | Timeframes | Status |
| --- | --- | --- | --- | --- | --- |
| *(none yet)* | | | | | |
