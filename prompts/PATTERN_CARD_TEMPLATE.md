# Pattern Card Template

One card per pattern, pasted underneath the master prompt. Every field maps to something
the script actually uses — nothing here is decoration.

The fields marked **engine** decide behaviour (detection, gating, filtering). The fields
marked **card** become the text inside the hold-to-read tooltip.

---

## Template

```text
NUMBER              12                      # engine · catalogue order 1-45
NAME                Bullish Engulfing       # card   · shown on the tooltip's second line
ABBREVIATION        BEC                     # engine · the ONLY thing drawn on the chart
CATEGORY            Double Candle           # engine · Single Candle | Double Candle | Triple & Multi
CANDLES             2                       # engine · how many candles the pattern spans (1-5)
DIRECTION           Bullish                 # engine · Bullish | Bearish | Neutral | Dual
ROLE                Reversal                # engine · Reversal | Continuation | Exhaustion | Indecision
PRIORITY            Must                    # engine · Must | Important | Rare
RELIABILITY         78                      # engine · percent, used by the minimum-reliability filter
IDEAL TIME FRAME    H1 · H4 · D1            # engine · the pattern prints ONLY on these
RISK REWARD         1:2 - 1:3               # card
RISK LEVEL          Low                     # card

DESCRIPTION
After a downtrend, a small bearish candle appears whose body is fully engulfed by a large
bullish candle. One of the most reliable and best-known upside reversal patterns.

HOW TO RECOGNIZE
Prior downtrend. Candle 1 bearish, candle 2 bullish with its body covering the entire body
of candle 1 (shadows may exceed). The larger the engulfing ratio, the stronger.

REQUIRED TREND      Downtrend               # engine · read BEFORE candle 1 of the pattern
IDEAL LOCATION      Strong support / demand zone
VOLUME              Candle 2 volume must be heavy
CONFIRMATION        Next candle closes above the pattern high, stronger with a volume spike
FAILURE CONDITION   A later close below the pattern low = failed takeover

STOP LOSS
Below the engulfing candle low.

TAKE PROFIT
Nearest resistance then swing high; this pattern often starts long moves — consider
trailing.

MARKET PSYCHOLOGY
The green candle fully engulfing the previous red body shows a total and instant transfer
of control from sellers to buyers.

PRO TIPS
Engulfing at major support with heavy volume is an A+ setup. A second candle that is also a
marubozu raises accuracy. Check the higher time frame to confirm direction.
```

---

## Field notes

**ABBREVIATION** — 3 letters is the sweet spot. It must be unique across all 45 patterns.
The convention used in this repo is B… for bullish and S… for the bearish twin
(`BEC`/`SEC` for the engulfings, `BKK`/`SKK` for the kickers), so a pair reads as a pair on
the chart.

**IDEAL TIME FRAME** — list every time frame you would genuinely take the trade on,
separated by `·`. This is the single most important engine field: it is what stops a D1
pattern from cluttering an M5 chart. Use names from the ladder
`M1 M2 M3 M5 M10 M15 M30 M45 H1 H2 H3 H4 H6 H8 H12 D1 W1 MN1`.

**CANDLES** — must match CATEGORY: 1 for Single, 2 for Double, 3-5 for Triple & Multi.
It also tells the engine how far back to read the prior trend: a 3-candle pattern checks
the trend state 3 bars before the current one, so the pattern's own candles cannot
manufacture the trend they are supposed to reverse.

**DIRECTION = Dual** — for patterns that exist in both a bullish and a bearish form under
one catalogue entry (Belt Hold, Separating Lines). The engine emits them separately and
applies the direction filter to whichever form actually fired.

**HOW TO RECOGNIZE** — write it as geometry, not as a feeling. Every clause you write here
becomes a clause in the detector, so "a large bullish candle" is ambiguous but "body at
least 1.25x the 20-candle average body" is implementable. If you leave it vague, the AI
will pick a threshold for you and you will not know what it picked.

**REQUIRED TREND** — leave it as `None` for patterns that are defined by shape alone
(Kicker, Marubozu). For everything else this is what separates twins: Hammer and Hanging
Man are the identical shape and only the prior trend tells them apart.

**RELIABILITY** — your own number from your own catalogue. The engine never invents these;
it only filters on them.
