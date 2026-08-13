<!--
  Template for a single candlestick pattern specification.
  Copy this file into patterns/<direction>/<category>/<pattern-slug>.md and fill it in.
  Do NOT alter the supplied trading logic. Transcribe as given.
  If something looks technically incorrect, keep the original spec and add an
  "AUDIT FLAG:" callout immediately below it — do not silently correct it.
-->

# <Pattern Name>

- **Abbreviation:** <ABBR>
- **Direction:** <Bullish | Bearish | Neutral>
- **Primary Category:** <Reversal | Continuation | Exhaustion | Neutral | Gap>
- **Secondary/Conceptual Categories:** <none | list, with rationale>
- **Candle Count:** <integer — number of candles the pattern spans>
- **Ideal Timeframes:** <list, e.g. 1H, 4H, 1D>
- **Status:** <Specified | Specified (flagged)>

## Structural OHLC Rules

<Transcribe the exact open/high/low/close structural conditions as supplied, verbatim.
Use a numbered or bulleted list, one condition per line, in the order supplied.>

## Contextual Requirements

<Prior trend context, location requirements (e.g. "must occur after N-bar downtrend"),
support/resistance context, or any other precondition supplied.>

## Confirmation Rules

<Rules that must be satisfied on the confirming candle(s)/bar(s) after the pattern forms.>

## Failure Conditions

<Conditions under which the pattern is considered invalidated/failed.>

## RSI / EMA / Volume Validation

<Any RSI thresholds, EMA relationships/crossovers, or volume conditions supplied for this
pattern. If none were supplied, write "None supplied.">

## Audit Flags

<List any AUDIT FLAG callouts referenced above, or write "None.">

```
AUDIT FLAG:
[explanation]
```

## Ambiguities

<List anything underspecified in the supplied information that needs clarification or a
future decision. If none, write "None.">

## Source

<Note of when/how this specification was supplied, if useful for traceability.>
