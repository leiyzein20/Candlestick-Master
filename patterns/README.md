# PATTERNS

One file per pattern. Filing is mechanical — see [`CLASSIFICATION.md`](CLASSIFICATION.md).
Processing is mechanical — see [`INTAKE.md`](INTAKE.md). Format is fixed — see
[`SPEC_TEMPLATE.md`](SPEC_TEMPLATE.md).

| Directory | Holds | Filename |
| --- | --- | --- |
| [`bullish_reversal/`](bullish_reversal/) | Bullish + `Reversal` | `<slug>.md` |
| [`bearish_reversal/`](bearish_reversal/) | Bearish + `Reversal` | `<slug>.md` |
| [`continuation/`](continuation/) | any direction + `Continuation` | `bull_` / `bear_` / `neut_` prefix |
| [`exhaustion/`](exhaustion/) | any direction + `Exhaustion` | prefixed |
| [`neutral/`](neutral/) | `Neutral` direction, and any pattern with `Primary: Neutral` | prefixed |
| [`gap_patterns/`](gap_patterns/) | any direction + `Primary: Gap` (the gap *is* the pattern) | prefixed |

**Current count: 0.** Awaiting supplied specifications.

The authoritative index is [`../PATTERN_REGISTRY.md`](../PATTERN_REGISTRY.md); the per-directory
index tables are a navigation convenience and are regenerated from it.

## Reading a pattern file

* §1 is the owner's text, verbatim and immutable.
* §§4–12 are structure — OHLC arithmetic only, no indicators.
* §13 is context — trend/location/RSI/EMA/volume, scored as confluence unless the supplied
  text marks a factor mandatory.
* §§14–15 are the lifecycle rules (confirmed / failed / expired).
* §16 is stored narrative and supplied labels. It never enters a calculation.
* §17 lists every ambiguity, separately, with a `CONFLICT_LOG.md` ID.
* §18 holds `AUDIT FLAG:` notes — concerns recorded *beside* preserved rules, never instead
  of them.
