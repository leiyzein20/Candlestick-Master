# BULLISH REVERSAL PATTERNS

`Direction: Bullish` + `Primary category: Reversal`.

Filename: `<slug>.md` (no direction prefix — the directory carries it).

## What lands here

A prior **downward** move is expected to turn upward. The pattern's own rules require, or
its supplied text describes, a preceding decline.

Does **not** land here:

| Case | Goes to |
| --- | --- |
| bullish, but the spec frames it as buyer exhaustion of a *selling climax* | [`../exhaustion/`](../exhaustion/) |
| bullish, and the gap **is** the pattern | [`../gap_patterns/`](../gap_patterns/) |
| bullish, and it resumes an existing uptrend | [`../continuation/`](../continuation/) |
| indecision candle used as a turning signal (`Neutral` direction) | [`../neutral/`](../neutral/) |

## Category-specific checks at intake

* **Required trend must be recorded.** A bullish reversal without a stated prior downtrend
  gets an `MS-` entry — the trend is usually structural for this family, and assuming it
  would be inventing a rule.
* **Confirmation direction is upward.** Default trigger: a closed candle closing above the
  pattern high; default invalidation: a closed candle closing below the pattern low
  (`CV-CONF-001`).
* **Location factor is `AT_SUPPORT` / `AT_DEMAND` / `SWING_LOW`** for the confluence score.
* **Watch for superset relationships.** Several bullish reversals differ only by one wick or
  body condition; where pattern B's rules are implied by pattern A's, both will fire, and
  that is recorded in §20 of each file rather than suppressed.

## Index

| ID | ABBR | Name | Candles | Timeframes | Status |
| --- | --- | --- | --- | --- | --- |
| *(none yet)* | | | | | |
