# TIMEFRAME TESTS

Covers [`engines/TIMEFRAME_ENGINE.md`](../engines/TIMEFRAME_ENGINE.md).

```bash
python3 tools/run_tests.py timeframe
```

Vectors: `vectors/timeframe.json`.

---

## 1. The owner's requirement, asserted directly

> If a pattern has three ideal timeframes, it MUST work on all three. Do NOT select only one
> timeframe.

Asserted as its own check for a pattern listed `H1, H4, D1`:

```
tf_allowed(60,   "60,240,1440", EXACT) and tf_allowed(60,   ..., CLASS)   -> true
tf_allowed(240,  "60,240,1440", EXACT) and tf_allowed(240,  ..., CLASS)   -> true
tf_allowed(1440, "60,240,1440", EXACT) and tf_allowed(1440, ..., CLASS)   -> true
```

and the fast timeframes must be hidden:

```
tf_allowed(1,  "60,240,1440", EXACT | CLASS)  -> false
tf_allowed(5,  "60,240,1440", EXACT | CLASS)  -> false
tf_allowed(15, "60,240,1440", EXACT | CLASS)  -> false
```

## 2. Enforcement table — asserted cell by cell

Pattern listed `H1, H4, D1`:

| Chart | `EXACT` | `CLASS` | Reason |
| --- | --- | --- | --- |
| 0.5m (30s) | false | false | `SUB_MINUTE`; nothing listed there |
| 1m | false | false | `MIN_FAST` |
| 5m | false | false | `MIN_MID` |
| 15m | false | false | `MIN_SLOW` |
| 45m | false | false | `MIN_SLOW` — the closest listed timeframe is a different class |
| 1H | **true** | **true** | listed |
| 2H | false | **true** | `HOUR_LOW`, shared with the listed 1H |
| 3H | false | **true** | `HOUR_LOW` |
| 4H | **true** | **true** | listed |
| 6H | false | **true** | `HOUR_HIGH`, shared with the listed 4H |
| 12H | false | **true** | `HOUR_HIGH` |
| 1D | **true** | **true** | listed |
| 2D | false | **true** | `DAILY` |
| 1W | false | false | `WEEKLY`; nothing listed there |
| 1M | false | false | `MONTHLY` |

A second pattern listed `5m, 15m, 30m` checks the low end: allowed on 5m (exact) and 10m
(class), hidden on 1D. This catches a class table that only happens to work for hourly
patterns.

## 3. Class assignment

Every canonical token, plus non-canonical timeframes, plus both sides of every boundary:

| Boundary | Below | At |
| --- | --- | --- |
| `MIN_FAST` / `MIN_MID` | 4 → `MIN_FAST` | 5 → `MIN_MID` |
| `MIN_MID` / `MIN_SLOW` | 14 → `MIN_MID` | 15 → `MIN_SLOW` |
| `MIN_SLOW` / `HOUR_LOW` | 59 → `MIN_SLOW` | 60 → `HOUR_LOW` |
| `HOUR_LOW` / `HOUR_HIGH` | 239 → `HOUR_LOW` | 240 → `HOUR_HIGH` |
| `HOUR_HIGH` / `DAILY` | 1439 → `HOUR_HIGH` | 1440 → `DAILY` |
| `DAILY` / `WEEKLY` | 10079 → `DAILY` | 10080 → `WEEKLY` |
| `WEEKLY` / `MONTHLY` | 43199 → `WEEKLY` | 43200 → `MONTHLY` |

Non-canonical timeframes that must still classify without error: `7m` → `MIN_MID`,
`9H (540)` → `HOUR_HIGH`, `2D (2880)` and `3D (4320)` → `DAILY`, `2W (20160)` → `WEEKLY`,
`3M (129600)` → `MONTHLY`.

**Totality** is asserted separately: every value in `{0.1, 0.5} ∪ [1..2000] ∪ {4320, 10079,
10080, 43199, 43200, 10⁶}` receives a class, and all nine classes are reachable. A chart
timeframe that fell through the table would be an unclassifiable timeframe, which is exactly
the bug this check exists to prevent — and it caught a real one during development (`1m`
landing in `SUB_MINUTE` because the sub-minute span was written inclusive of 1).

## 4. Overrides

| Case | Expected |
| --- | --- |
| `OFF` on a 5m chart with an hourly pattern | allowed |
| `TEST MODE` with `EXACT` on a 5m chart | allowed — test mode overrides everything |
| `TEST MODE` with `CLASS` | allowed |
| pattern with an **empty** timeframe list, `EXACT` | allowed — an unsupplied list must not silently hide a pattern everywhere |

The last row is a policy decision worth restating: a specification that arrives without
timeframes produces an `MS-` entry in `CONFLICT_LOG.md`, and until the list is supplied the
pattern is **not** timeframe-gated. The alternative — treating "no list" as "no timeframes
allowed" — would make an incomplete specification look like a broken indicator.

## 5. Manual checks (TradingView only)

| # | Check | Expected |
| --- | --- | --- |
| M1 | switch a chart 1m → 5m → 1H → 4H → 1D → 1W | pattern visibility follows §2; script reloads and re-resolves |
| M2 | seconds chart (30s) | no error, nothing shown while enforcing |
| M3 | tick chart | no error; documented as out of scope for time-based patterns |
| M4 | Renko / Range chart | no error; documented limitation, patterns are defined for time bars |
| M5 | info panel timeframe row | shows minutes, class, and enforcement mode correctly |
| M6 | `TEST MODE` on | banner visible in the panel **and** in every tooltip |
| M7 | exotic chart timeframes (7m, 3D, 2W) | classified, no error, behaviour matches §3 |

M1 is the one that catches a resolution cached across a timeframe change; the chart timeframe
cannot change mid-run, but a script that resolved permissions from a stale value would show it
here.
