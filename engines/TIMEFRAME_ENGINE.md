# TIMEFRAME ENGINE (L5)

Every pattern carries its **own** list of ideal timeframes, and all of them work. This
engine decides whether the current chart timeframe is one of them.

---

## 1. Purpose

The owner's requirement, restated as the engine's contract: a pattern listing H1, H4 and D1
must display on 1H, 4H **and** 1D — never on a chosen one of the three — and must be hidden
on 1m, 5m and 15m when enforcement is on. Sub-minute, 45m, 3H, 2D and any other valid
TradingView timeframe must be handled without special-casing.

## 2. Contract

**Inputs:** `timeframe.in_seconds()`, the pattern's timeframe list, the enforcement mode,
`TEST MODE`.

**Outputs:**

| Output | Type | Meaning |
| --- | --- | --- |
| `chartMinutes` | float | chart timeframe in minutes (`< 1` for seconds/ticks) |
| `chartToken` | string | canonical token if it matches one exactly, else the raw label |
| `chartClass` | int enum | §4 |
| `tfAllowed(patternId)` | bool | resolved once per pattern per chart |
| `tfText` | string | e.g. `1H (class HOUR_LOW, allowed)` |

## 3. Chart timeframe → minutes

```
chartMinutes = timeframe.in_seconds() / 60
```

`timeframe.in_seconds()` is used rather than string parsing because it resolves every
TradingView timeframe — seconds, ticks, minutes, hours, days, weeks, months — to one
comparable number, and because string parsing of `"45"` vs `"45S"` vs `"1D"` is exactly the
kind of fragile code that breaks on an unusual chart.

Canonical tokens and minute values:

| Token | Minutes | Token | Minutes | Token | Minutes |
| --- | --- | --- | --- | --- | --- |
| `1m` | 1 | `30m` | 30 | `6H` | 360 |
| `2m` | 2 | `45m` | 45 | `8H` | 480 |
| `3m` | 3 | `1H` | 60 | `12H` | 720 |
| `5m` | 5 | `2H` | 120 | `1D` | 1440 |
| `10m` | 10 | `3H` | 180 | `1W` | 10080 |
| `15m` | 15 | `4H` | 240 | `1M` | 43200 |

A pattern's list is stored as the CSV of its minute values (`"60,240,1440"` for H1/H4/D1),
which makes matching arithmetic rather than textual.

Months are approximated as 43200 minutes (30 days) `[DERIVED]`. Calendar months vary, but
the value is only ever used for comparison against other timeframes, never for date maths.
Anything `>= 43200` is monthly-or-higher.

## 4. Timeframe classes

`[ENGINE-DEFAULT]` `CV-TF-001`. Classes exist to answer "what should a 3H chart do with a
pattern listed for H1 and H4?" without either hiding everything or ignoring the owner's
lists.

| Class | Minute span | Contains |
| --- | --- | --- |
| `SUB_MINUTE` | `< 1` | seconds and tick charts |
| `MIN_FAST` | `1 – 3` | 1m, 2m, 3m |
| `MIN_MID` | `5 – 10` | 5m, 10m |
| `MIN_SLOW` | `15 – 45` | 15m, 30m, 45m |
| `HOUR_LOW` | `60 – 180` | 1H, 2H, 3H |
| `HOUR_HIGH` | `240 – 720` | 4H, 6H, 8H, 12H |
| `DAILY` | `1440 – 4319` | 1D, 2D, 3D |
| `WEEKLY` | `4320 – 43199` | 1W, 2W |
| `MONTHLY` | `>= 43200` | 1M and above |

Every possible `chartMinutes` value falls in exactly one class, so no timeframe is
unclassifiable. The class boundaries are a judgement and are recorded as such — 3H sits with
1H because a 3H candle behaves closer to an hourly than to a 4H structural candle, and 45m
sits with 15m/30m for the same reason.

## 5. Enforcement modes

| Mode | Rule | Use |
| --- | --- | --- |
| `OFF` | `tfAllowed = true` always | the owner's "enforce ideal timeframe = off" |
| `CLASS` *(default)* | allowed if `chartClass` equals the class of **any** listed timeframe | practical: a 3H chart shows H1/H4 patterns |
| `EXACT` | allowed only if `chartMinutes` equals a listed minute value | literal reading of the ideal list |
| `TEST MODE` | overrides everything, plus relaxes context gating | verification |

Worked example — pattern listed `H1, H4, D1` (`"60,240,1440"`):

| Chart | `EXACT` | `CLASS` | Why |
| --- | --- | --- | --- |
| 1m, 5m, 15m | hidden | hidden | no listed timeframe is in `MIN_*` |
| 45m | hidden | hidden | `MIN_SLOW`; nothing listed is in it |
| 1H | shown | shown | exact match |
| 2H, 3H | hidden | shown | same class as the listed 1H |
| 4H | shown | shown | exact match |
| 6H, 12H | hidden | shown | same class as the listed 4H |
| 1D | shown | shown | exact match |
| 2D, 3D | hidden | shown | same class as the listed 1D |
| 1W, 1M | hidden | hidden | no listed timeframe is weekly or monthly |

This satisfies the requirement exactly: all three listed timeframes work, the fast
timeframes are hidden, and unlisted-but-similar timeframes are a documented, switchable
decision rather than an accident.

`CLASS` is the default because `EXACT` silently produces an empty chart on any timeframe
the owner did not enumerate, which looks like a broken indicator rather than a policy.

## 6. Resolution happens once

The chart timeframe cannot change during a script run — a timeframe change reloads the
script. So `tfAllowed` is resolved **once**, on the first bar, per pattern, and stored.

Consequence: timeframe gating costs one boolean read per pattern per bar and nothing else,
so gating 50+ patterns is free. This is why the pattern list is stored as data
([`../ARCHITECTURE.md`](../ARCHITECTURE.md) A4) instead of being coded per pattern.

## 7. TEST MODE

`[OWNER]` requirement. When on:

* timeframe restrictions are ignored (all patterns eligible on any chart);
* mandatory-context gating is relaxed so a pattern can be seen in isolation;
* the info panel shows a `TEST MODE` banner and every tooltip produced carries the line
  `TEST MODE: timeframe/context gating bypassed`.

The banner is not optional. A screenshot taken in test mode must be self-evidently a test.

## 8. Sub-minute and unusual timeframes

* Seconds and tick charts fall in `SUB_MINUTE`. Unless a pattern lists a sub-minute
  timeframe (none can, since the canonical token set starts at 1m), they are hidden in both
  `CLASS` and `EXACT` — which is the correct outcome for patterns whose specifications
  target 1H and above.
* Range and Renko charts report a timeframe, but their bars are not time-based. Documented
  limitation: candlestick pattern definitions assume time-based candles, and no attempt is
  made to reinterpret them for non-time bars.
* Extended/regular session and `HTF` chart types do not affect the engine; it reads only the
  chart's own resolution.

## 9. Cost

| Item | Count |
| --- | --- |
| `ta.*` calls | 0 |
| Per-bar work | one boolean read per pattern |
| First-bar work | one string→number parse per pattern (≤ ~70 total) |

## 10. Tests

[`../tests/TIMEFRAME_TESTS.md`](../tests/TIMEFRAME_TESTS.md), vectors
`tests/vectors/timeframe.json`:

* the full §5 example table, asserted cell by cell;
* every canonical token maps to exactly one class;
* class boundaries at 3/5, 10/15, 45/60, 180/240, 720/1440, 4319/4320, 43199/43200;
* non-canonical timeframes (7m, 9H, 2D, 2W) get a class and never error;
* sub-minute charts hide everything and do not error;
* `OFF` shows every pattern on every timeframe;
* `TEST MODE` overrides `EXACT` and emits the banner;
* a pattern whose list is `NOT SUPPLIED` is not timeframe-gated at all (documented, so an
  incomplete spec cannot silently become "hidden everywhere").

## 11. Open questions for supplied specifications

| # | Question | Until answered |
| --- | --- | --- |
| 1 | Should `CLASS` or `EXACT` be the shipped default? | `CLASS` (§5 rationale) |
| 2 | Are the class boundaries acceptable, especially 3H↔`HOUR_LOW` and 45m↔`MIN_SLOW`? | as tabled (`CV-TF-001`) |
| 3 | Do any patterns have weekly/monthly ideal timeframes? | none assumed; the classes exist |
| 4 | Should a pattern be *shown but marked* off-timeframe instead of hidden? | hidden, per the owner's wording |
