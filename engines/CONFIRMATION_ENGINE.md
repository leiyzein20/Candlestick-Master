# CONFIRMATION ENGINE (L7)

The pattern lifecycle. `DETECTED` is not `CONFIRMED`, and nothing is confirmed by a candle
that is still forming.

---

## 1. Purpose

Track every detected pattern until it resolves, using only closed candles, and keep the
three outcomes distinguishable: it worked, it was negated, or nothing happened.

## 2. State machine

```
                        ┌─────────────┐
     structure valid    │  DETECTED   │   label created at the pattern's last candle
   ────────────────────►└──┬───┬───┬──┘
                           │   │   │
        trigger reached    │   │   │   window elapsed
        ┌──────────────────┘   │   └──────────────────┐
        ▼                      ▼                      ▼
  ┌───────────┐         ┌────────────┐         ┌───────────┐
  │ CONFIRMED │         │   FAILED   │         │  EXPIRED  │
  └───────────┘         └────────────┘         └───────────┘
                     invalidation reached
```

All three transitions require a **fully closed** candle *after* the pattern's last candle.
States are terminal: a `FAILED` pattern is never revived, a `CONFIRMED` pattern is never
downgraded.

## 3. Contract

**Inputs per detection:** pattern id, direction, `triggerLevel`, `invalidationLevel`,
`confirmBars`, the bar index of the pattern's last candle, and the label handle.

**Outputs:** a status per tracked pattern, the resolution bar, and events for the display and
alert layers.

## 4. Trigger and invalidation levels

Generic rule when a supplied specification gives none `[ENGINE-DEFAULT]` `CV-CONF-001`:

| Direction | Trigger → `CONFIRMED` | Invalidation → `FAILED` |
| --- | --- | --- |
| bullish | a closed candle **closes above the pattern high** | a closed candle **closes below the pattern low** |
| bearish | a closed candle **closes below the pattern low** | a closed candle **closes above the pattern high** |
| neutral | either side breaks; the breaking side becomes the resolved direction | — |

"Pattern high/low" means the extreme across **all** candles of the pattern, not just the last
one. For a three-candle pattern that is `maxHigh(0, 2)` / `minLow(0, 2)` at the detection bar,
captured as a fixed number when the pattern is detected — not recomputed later, which would
let a level drift with new bars.

**Closes**, not touches: a wick through the level does not confirm. Reason — an intrabar touch
is knowable only while the bar is forming, which would violate the closed-candle rule in
[`../MASTER_SPECIFICATION.md`](../MASTER_SPECIFICATION.md) §12. A supplied specification saying
"trades above the high" is implemented as supplied, and its intrabar nature is recorded as an
`AUDIT FLAG` describing the extra bar of delay.

Any pattern whose specification defines its own confirmation or failure rule uses **that**
rule; this table is only the fallback, and each pattern file states which applied.

## 5. Window

`confirmBars`, default `3` closed candles `[ENGINE-DEFAULT]` `CV-CONF-002`, per pattern.

The window starts at the first candle **after** the pattern's last candle. With
`confirmBars = 3`, candles `+1`, `+2`, `+3` can resolve it; if none does, the pattern becomes
`EXPIRED` at the close of candle `+3`.

## 6. Same-candle collisions

A single candle can reach both levels — a wide-range bar that closes beyond one of them, or a
gap that opens beyond both.

Rule `[ENGINE-DEFAULT]` `CV-CONF-003`: **`FAILED` wins.** A candle whose close satisfies the
invalidation is a failure even if it also satisfied the trigger at some point.

Since resolution is by *close*, a single close cannot literally be both above the pattern high
and below the pattern low, so the collision only arises with supplied intrabar rules. The
precedence is defined anyway, because leaving it undefined would make behaviour depend on
evaluation order.

## 7. `EXPIRED` is not `FAILED`

| Status | Meaning | Alert |
| --- | --- | --- |
| `FAILED` | the market did the opposite thing — the pattern was negated | fires the failed alert |
| `EXPIRED` | neither level was reached within the window — nothing happened | **no** failure alert |

Merging them would misreport: a hammer that drifts sideways for three bars did not fail, it
was simply never confirmed. Keeping them separate also keeps the confirmation factor honest —
`EXPIRED` scores `0` for confirmation, the same as an unresolved `DETECTED`, and neither is a
negative.

## 8. Live (forming) bar

On the forming bar the engine does nothing: no detection, no resolution, no label change, no
alert. Everything is gated on `barstate.isconfirmed`.

Consequence, stated plainly: a pattern appears at the **close** of its last candle, not while
the candle is forming. That is one bar of "lateness" compared with an indicator that reads the
live bar, and it is the price of a signal that never disappears after the fact.

## 9. Pending queue

Detections awaiting resolution live in a capped structure (one record per pending pattern),
holding: pattern id, direction, trigger level, invalidation level, bars remaining, label
handle, and the confluence factors captured at detection.

| Property | Value | Reason |
| --- | --- | --- |
| Capacity | 60 `[ENGINE-DEFAULT]` `CV-CONF-004` | bounded per-bar loop (`ARCHITECTURE.md` §6) |
| Overflow | oldest pending record dropped, counted, and surfaced in the info panel | never silently lost |
| Removal | on resolution, or on expiry | queue length stays near the number of patterns × window |

With a 3-bar window, the queue rarely exceeds a handful of records; 60 is headroom, not an
expectation.

## 10. Label lifecycle and why status updates are not repainting

A label is created at `DETECTED` and its tooltip is **rewritten** when the pattern resolves.
The label stays at the pattern's own bar.

This is a state machine advancing, not a repaint:

* the detection bar never moves;
* the detection itself is never withdrawn;
* the resolution is attributed to the bar on which it happened, and the tooltip names that bar
  (`Resolved: +2 bars`);
* no historical decision is revised in the light of later data — later data only *adds* the
  outcome.

The distinction that matters for honesty: a repainting indicator would show, on history, a
signal that could not have been seen at the time. Here, the `DETECTED` label existed at its
bar and the `CONFIRMED` text appeared later, exactly as it would have live.

Historical labels are subject to Pine's `max_labels_count` (500): the oldest are culled
automatically on long histories. That is a platform limit, documented, not a design choice.

## 11. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 0 |
| Loop iterations | ≤ 60 per bar (pending queue) |
| Labels | 1 per detection, tooltip rewritten in place |
| Arrays | 1 (records) |

## 12. Tests

[`../tests/CONFIRMATION_TESTS.md`](../tests/CONFIRMATION_TESTS.md), vectors
`tests/vectors/confirmation.json`:

* bullish detection, then a close above the pattern high on `+1` → `CONFIRMED` at `+1`;
* the same on `+3` → `CONFIRMED`; on `+4` → already `EXPIRED`, and the late close does
  **not** confirm it;
* close below the pattern low on `+2` → `FAILED`, with no later revival;
* nothing happens for 3 bars → `EXPIRED`, and no failure alert fires;
* a wick above the level with a close below → not confirmed;
* pattern high taken across all candles of a 3-candle pattern, not just the last;
* the level captured at detection does not change when later bars print higher highs;
* neutral pattern resolving in each direction, with the resolved direction recorded;
* forming-bar check: on the live bar no status changes and no alert fires;
* queue overflow: 61 simultaneous pendings → the drop is counted and reported.

## 13. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Default window of 3 closed candles — right for daily as well as 1m? | `3` everywhere (`CV-CONF-002`), per-pattern override |
| 2 | Should confirmation require a **close** beyond the level, or a touch? | close (§4) |
| 3 | For multi-candle patterns, is the trigger the whole pattern's extreme or the last candle's? | whole pattern (§4) |
| 4 | Should `EXPIRED` patterns keep their label? | yes, tooltip marked `EXPIRED`; an input can hide them |
