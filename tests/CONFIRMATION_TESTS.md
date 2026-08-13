# CONFIRMATION TESTS

Covers [`engines/CONFIRMATION_ENGINE.md`](../engines/CONFIRMATION_ENGINE.md).

```bash
python3 tools/run_tests.py confirmation
```

Vectors: `vectors/confirmation.json`.

The properties this suite defends: **`EXPIRED` is not `FAILED`**, **terminal states are
terminal**, and **only closed candles resolve anything**.

---

## 1. The state machine — `vectors/confirmation.json`

Bullish pending: trigger `110`, invalidation `100`, window `3` closed candles.

| ID | Closes after the pattern | Status | Resolved after |
| --- | --- | --- | --- |
| `CONF-001` | `111` | `CONFIRMED` | 1 |
| `CONF-002` | `105, 106, 111` | `CONFIRMED` | 3 (window edge) |
| `CONF-003` | `105, 106, 107, 111` | `EXPIRED` | — (the 4th close is too late) |
| `CONF-004` | `99` | `FAILED` | 1 |
| `CONF-005` | `105, 98, 111` | `FAILED` | 2 (and the later trigger is ignored) |
| `CONF-006` | `105, 106, 107` | `EXPIRED` | — |
| `CONF-007` | `110, 110, 110` | `EXPIRED` | — (a close **on** the trigger is not above it) |
| `CONF-012` | window `1`, closes `105, 111` | `EXPIRED` | — |
| `CONF-013` | no closes yet | `DETECTED` | — |

Bearish pending: trigger `100` (close below), invalidation `110`.

| ID | Closes | Status |
| --- | --- | --- |
| `CONF-008` | `99` | `CONFIRMED` |
| `CONF-009` | `111` | `FAILED` |

Neutral pending: either side resolves it and the breaking side becomes the direction.

| ID | Closes | Status | Resolved direction |
| --- | --- | --- | --- |
| `CONF-010` | `105, 111` | `CONFIRMED` | `+1` |
| `CONF-011` | `99` | `CONFIRMED` | `-1` |

## 2. `CONF-003` and `CONF-005` are the important ones

`CONF-003` — the trigger is reached one candle after the window closed. A naive
implementation that keeps scanning would report `CONFIRMED`, producing a signal that looks
excellent on history and never appears live at the same moment. The expected result is
`EXPIRED`, and the late close changes nothing.

`CONF-005` — the pattern failed on candle 2 and the trigger was reached on candle 3. The
expected result is `FAILED`. A pattern is not rescued by later price action; the state is
terminal.

## 3. Terminal states

Asserted programmatically rather than by vector: a `FAILED` pending is re-run against three
very bullish closes and must remain `FAILED`. This caught a real bug during development — the
resolver looped over the new closes without first checking that the pending had already
resolved, turning a `FAILED` pattern into `CONFIRMED`.

## 4. `EXPIRED` vs `FAILED`

| Status | Meaning | Failure alert |
| --- | --- | --- |
| `FAILED` | the market did the opposite thing | fires |
| `EXPIRED` | neither level was reached in the window | **does not fire** |

Merging them would misreport a pattern that simply drifted sideways as a failure, and it would
corrupt any later review of which patterns were negated.

## 5. Levels are captured at detection

| Check | Expected |
| --- | --- |
| trigger level for a 3-candle pattern | the maximum high across **all three** candles |
| the level after later bars print higher highs | unchanged — it was captured at detection |

This is a manual check as well as a design rule, because a Pine implementation that recomputed
`ta.highest()` at resolution time would drift the level upward and quietly make confirmation
harder as the pattern aged.

## 6. Only closed candles

The reference model never receives a forming bar: `resolve()` takes a list of closed candle
closes. In Pine the equivalent guarantee is that every detection and every resolution is gated
on `barstate.isconfirmed`. That gate is a manual check (M1, M2) since it depends on the Pine
runtime.

## 7. To add when specifications arrive

* Patterns that supply their own confirmation rule (e.g. "closes above the high of candle 2"),
  each with its own vector.
* Patterns that supply their own failure rule.
* Patterns whose supplied rule is intrabar ("trades above the high") — implemented as supplied,
  with the extra delay recorded as an `AUDIT FLAG`.
* Gap-fill confirmation, where the trigger is a previous candle's high rather than the
  pattern's own extreme.
* Queue overflow: 61 simultaneous pendings, asserting the drop is counted and surfaced.

## 8. Manual checks (TradingView only)

| # | Check | Expected |
| --- | --- | --- |
| M1 | watch a forming bar that would confirm a pending pattern | status stays `DETECTED` until the bar closes |
| M2 | watch a forming bar that would detect a new pattern | no label until the close |
| M3 | a confirmed pattern on history | the label sits at the **pattern's** bar, not the confirming bar |
| M4 | tooltip after resolution | `Status: CONFIRMED` plus `Resolved: +n bars` |
| M5 | reload the chart | statuses and bar positions are identical |
| M6 | an expired pattern | tooltip says `EXPIRED`; no failure alert was received |
| M7 | a long history (10k+ bars) | oldest labels culled by `max_labels_count`, no error |
| M8 | replay mode, bar by bar | the sequence `DETECTED → CONFIRMED` happens on the bars the tooltip claims |

M8 is the strongest available repaint check: stepping forward one bar at a time shows the exact
bar on which each state change occurred, which can then be compared against what history shows
after a reload.
