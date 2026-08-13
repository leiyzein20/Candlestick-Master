# TESTS

Two layers, because half of this system can be checked with arithmetic and half can only be
checked on a chart.

| Layer | What it covers | How it runs |
| --- | --- | --- |
| **Executable** | L1/L2 arithmetic, timeframe matching, RSI divergence timing, EMA reclaim semantics, volume states, confirmation state machine, confluence scoring | `python3 tools/run_tests.py` |
| **Manual** | compilation, labels, tooltips, alerts, resource limits, live-bar behaviour, repaint checks on real data | [`PINE_COMPILE_CHECKLIST.md`](PINE_COMPILE_CHECKLIST.md) + the per-engine documents here |

```bash
python3 tools/run_tests.py            # everything
python3 tools/run_tests.py -v rsi_divergence
python3 tools/run_tests.py timeframe validation
```

Current state: **2435 checks, all passing**, against `tools/reference_model.py`. No pattern
tests exist yet — no pattern specifications have been supplied.

## Files

| File | Covers |
| --- | --- |
| [`OHLC_TESTS.md`](OHLC_TESTS.md) | candle primitives, shape classes, candle-to-candle relationships |
| [`TIMEFRAME_TESTS.md`](TIMEFRAME_TESTS.md) | canonical timeframes, classes, enforcement modes, test mode |
| [`RSI_TESTS.md`](RSI_TESTS.md) | RSI states, precedence, divergence and its confirmation delay |
| [`EMA_TESTS.md`](EMA_TESTS.md) | alignment, reclaim vs above, rejection, warm-up |
| [`CONFIRMATION_TESTS.md`](CONFIRMATION_TESTS.md) | the lifecycle state machine, expiry vs failure |
| [`PATTERN_TESTS.md`](PATTERN_TESTS.md) | the seven-case template every supplied pattern must pass, plus display/alert/resource checks |
| [`PINE_COMPILE_CHECKLIST.md`](PINE_COMPILE_CHECKLIST.md) | the manual gate run after every implementation batch |
| `vectors/*.json` | the machine-readable expectations |

## Vector format

Each suite is a JSON file with hand-computed expectations and a `spec` field naming the
document the numbers come from. Expectations are **derived from the specification, not from
the model** — otherwise the tests would only prove the model agrees with itself.

```json
{
  "suite": "relationship",
  "spec": "engines/RELATIONSHIP_ENGINE.md",
  "cases": [
    {
      "id": "REL-003",
      "desc": "penetration exactly 0.5 sits ON the previous body midpoint",
      "a": {"o": 101.0, "h": 106.0, "l": 100.0, "c": 105.0},
      "b": {"o": 110.0, "h": 112.0, "l": 98.0, "c": 100.0},
      "expect": {"penetration_up": 0.5, "close_above_prev_body_mid": false}
    }
  ]
}
```

Float comparisons use a tolerance of `1e-9`. Booleans and `null` are compared exactly, so a
`null` (undefined) result can never quietly pass as `false`.

## What the executable layer deliberately proves

Beyond arithmetic, three behavioural properties that are easy to get wrong and impossible to
see by eye:

1. **A pivot is never used before its confirmation bar.** The divergence suite asserts
   inactivity on every bar between the pivot and `pivotBar + right`, then activity from the
   confirmation bar. This is the no-repaint rule, tested rather than promised.
2. **Being above an EMA is not a reclaim.** An 80-bar uptrend that stays above its 20 EMA
   must report zero reclaims after the initial crossing.
3. **`rsi > 50` is momentum, never divergence.** A monotonically rising series must produce
   no divergence at all.

## What only a chart can prove

Compilation, label placement, tooltip text, alert firing, `max_labels_count` behaviour,
`syminfo.type` wording for forex vs equities, and live-bar behaviour. These are enumerated as
explicit manual checks with recorded results, because "it looked right" is not a test result.

## Adding tests for a supplied pattern

At intake, each pattern gets `tests/vectors/<slug>.json` and a filled-in
[`PATTERN_TESTS.md`](PATTERN_TESTS.md) row set: valid, invalid, wrong trend, wrong timeframe,
failed confirmation, successful confirmation, expired, plus its own boundary cases (body
ratio, wick ratio, 50% penetration, gap, OHLC relationship). Vectors are written **from the
supplied specification**, before any implementation, so the test cannot be quietly shaped to
match the code.
