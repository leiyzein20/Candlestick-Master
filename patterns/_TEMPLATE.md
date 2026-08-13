# <Pattern Name>

> Specification file. Transcribed from supplied specification. No Pine Script implementation.

## 1. Identity

| Field | Value |
|---|---|
| Pattern name | <verbatim supplied name> |
| Abbreviation | <ABBREV> |
| Direction | bullish / bearish / neutral |
| Primary category | reversal / continuation / exhaustion / neutral / gap |
| Secondary categories | <list, or NONE> |
| Candle count | <N, or N-M> |
| Spec status | supplied fields recorded / fields outstanding |

## 2. Ideal Timeframes

<All timeframes named in the supplied specification, in supplied order. NOT SUPPLIED if absent.>

## 3. Structural OHLC Rules

<Candle-by-candle open/high/low/close relationships exactly as supplied. Numbered per candle,
using C1 for the earliest candle in the pattern.>

- **C1:**
- **C2:**

## 4. Contextual Requirements

<Prior trend, location, swing structure, support/resistance, session, or any other
pre-conditions as supplied.>

## 5. Confirmation Rules

<What must occur after the pattern completes for it to be treated as valid, as supplied,
including the bar or time window in which confirmation must occur.>

## 6. Failure Conditions

<What invalidates the pattern before or after confirmation, as supplied.>

## 7. Indicator Validation

### RSI

<As supplied. NOT SUPPLIED if absent.>

### EMA

<As supplied. NOT SUPPLIED if absent.>

### Volume

<As supplied. NOT SUPPLIED if absent.>

## 8. Ambiguities

<Under-determined points in the supplied specification, recorded separately from the rules
above. Each is stated as the open question, not as a resolution. NONE if there are none.>

## 9. Audit Flags

<Supplied rules that appear technically incorrect or internally inconsistent. The original
rule is preserved verbatim in its section above; this section carries the annotation.
NONE if there are none.>

```
AUDIT FLAG:
[explanation]
```

## 10. Source

| Field | Value |
|---|---|
| Supplied on | <date> |
| Supplied verbatim | yes / partially, see Ambiguities |
| Modified by agent | no |
