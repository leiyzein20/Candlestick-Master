# VOLUME ENGINE (L3)

Volume context, with the wording tied to what the data actually is.

---

## 1. Purpose

Publish a volume ratio and a state, and describe them in language the data supports —
including saying "tick volume" on forex feeds and "no volume data" where there is none.

## 2. Contract

**Inputs:** `volume`, `syminfo.type`, `bar_index`.

**Outputs:**

| Output | Type | Meaning |
| --- | --- | --- |
| `volAvg` | float | `ta.sma(volume, 20)` |
| `volRatio` | float | `volume / volAvg` |
| `volState` | int enum | `HIGH` / `ABOVE` / `NORMAL` / `BELOW` / `UNAVAILABLE` |
| `volSource` | int enum | `CENTRALISED` / `TICK` / `NONE` |
| `volText` | string | the exact tooltip string |
| `volReady` | bool | `bar_index >= 20` and a volume series exists |

## 3. Thresholds

| State | Rule | Default | ID |
| --- | --- | --- | --- |
| `HIGH` | `volRatio >= volHigh` | `1.50` | `CV-VOL-003` |
| `ABOVE` | `volRatio >= volAbove` | `1.20` | `CV-VOL-002` |
| `BELOW` | `volRatio <= volBelow` | `0.80` | `CV-VOL-004` |
| `NORMAL` | otherwise (`0.80 < ratio < 1.20`) | — | `[DERIVED]` |

Average period `20` `[ENGINE-DEFAULT]` `CV-VOL-001`. All four are inputs.

Two thresholds above 1.0 rather than one: "above average" in a supplied specification is a
soft statement, while "volume expansion" or "climactic volume" is not, and a single cut-off
would force the two to mean the same thing. Both `HIGH` and `ABOVE` satisfy the confluence
factor; only `HIGH` is described as expansion in the tooltip.

## 4. Data-source honesty `[OWNER]`

This is a correctness requirement, not a presentation preference.

| `volSource` | Detected when | Tooltip wording |
| --- | --- | --- |
| `CENTRALISED` | a volume series exists and `syminfo.type` is not forex/CFD | `Volume: Above average ✓` |
| `TICK` | `syminfo.type` is `forex` or `cfd`, or the feed is broker-specific | `Volume: Above average tick volume ✓` |
| `NONE` | `volume` is `na` or zero across the averaging window | `Volume: n/a (no volume data)` |

What each wording is allowed to imply:

* **`CENTRALISED`** — the venue reports traded size. On a single-venue crypto pair or an
  equity, this is real traded volume *for that venue*. It is not consolidated across all
  venues, and nothing claims it is.
* **`TICK`** — the number of price updates the **broker's own feed** produced. It correlates
  with activity but is not traded size, is not comparable between brokers, and can differ
  between two feeds for the same instrument on the same day. Describing it as market volume
  would be false, so the word "tick" is in the string, always.
* **`NONE`** — indices and some CFDs report nothing. The factor is **excluded** from the
  confluence maximum (`maxScore` drops by one) rather than scored as a failure, so an index
  chart is not systematically rated weaker than a stock chart
  ([`VALIDATION_ENGINE.md`](VALIDATION_ENGINE.md)).

The engine never estimates, synthesises, or substitutes a proxy for missing volume.

### 4.1 What is never said

* That volume shows institutional participation, accumulation, distribution, or absorption.
  None of that is observable in a single volume number.
* That high volume confirms a pattern's outcome. High volume is a *confluence factor* worth
  `+1`, nothing more.
* That forex tick volume approximates exchange volume.
* Any specific figure for "smart money" activity.

Supplied specifications sometimes contain such claims. They are preserved verbatim in the
pattern file's *As Supplied* block and, where they assert something the data cannot support,
they receive an `AUDIT FLAG:` and are excluded from the quantitative engine
([`../MASTER_SPECIFICATION.md`](../MASTER_SPECIFICATION.md) §14).

## 5. Edge cases

| Case | Behaviour |
| --- | --- |
| `volume == 0` on a single bar (holiday, halt) | `volRatio = 0` → `BELOW`; not an error |
| `volAvg == 0` (no volume anywhere in the window) | `volSource = NONE`, factor excluded — never a division by zero |
| first 20 bars | `volReady = false`, `Volume: n/a (warming up)`, factor excluded |
| a single enormous print (bad tick) | no outlier filter — the raw ratio is shown; filtering would be an undocumented model, and the tooltip shows the ratio so the anomaly is visible |
| session-boundary bars, extended hours | the volume series is taken as the chart provides it; no session normalisation |

`volRatio` is clamped to `[0, 20]` for display only `[ENGINE-DEFAULT]` `CV-VOL-005`; logic uses
the raw value.

## 6. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 1 (`sma(volume, 20)`) |
| Per-bar work | 4 comparisons |
| Arrays / drawings | 0 |

## 7. Tests

Vectors `tests/vectors/volume.json`, plus manual checks recorded in
[`../tests/PATTERN_TESTS.md`](../tests/PATTERN_TESTS.md):

* ratio exactly `1.20`, `1.50`, `0.80` → boundary states, inclusive;
* `volume == 0`;
* `volAvg == 0` → `UNAVAILABLE`, no division error, factor excluded and `maxScore` reduced;
* warm-up bars excluded;
* a forex symbol produces the `tick volume` wording and a stock symbol does not — checked
  manually on real charts, since `syminfo.type` cannot be simulated in the reference model;
* an index with no volume produces `n/a` and a `maxScore` of 5 rather than a `WEAK` bias.

## 8. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Is "above average" `1.2×` or `1.5×`? | both exist; `1.2×` satisfies the factor (`CV-VOL-002/003`) |
| 2 | Should the average be 20 bars, or match the pattern's timeframe? | 20 bars (`CV-VOL-001`) |
| 3 | Any pattern where volume is **mandatory** rather than confluence? | none assumed; a spec saying "requires volume expansion" would make it mandatory for that pattern |
| 4 | On instruments with no volume, should such a pattern be suppressed entirely? | no — the factor is excluded and the pattern still reports |
