# The 45 Patterns

Generated from the `addPat()` registry in [`pine/candlestick_master_45.pine`](../pine/candlestick_master_45.pine) by `tools/gen_pattern_table.py`. Do not edit by hand — edit the registry and regenerate.

`Ideal TF` is the gate: with the default strict setting the pattern only ever draws when your chart is on one of those time frames.


## Single Candle (12)

| # | Code | Pattern | Direction | Role | Priority | Rel. | Candles | Ideal TF |
| --: | :-- | :-- | :-- | :-- | :-- | --: | --: | :-- |
| 01 | `HAM` | Hammer | Bullish | Reversal | Must | 72% | 1 | H1 · H4 · D1 |
| 02 | `HGM` | Hanging Man | Bearish | Reversal | Must | 68% | 1 | H1 · H4 · D1 |
| 03 | `IHM` | Inverted Hammer | Bullish | Reversal | Important | 65% | 1 | H1 · H4 · D1 |
| 04 | `SHS` | Shooting Star | Bearish | Reversal | Must | 71% | 1 | H1 · H4 · D1 |
| 05 | `BMZ` | Bullish Marubozu | Bullish | Continuation | Important | 66% | 1 | M15 · H1 · H4 |
| 06 | `SMZ` | Bearish Marubozu | Bearish | Continuation | Important | 66% | 1 | M15 · H1 · H4 |
| 07 | `DOJ` | Doji | Dual / Neutral | Indecision | Must | 55% | 1 | H1 · H4 · D1 |
| 08 | `DFD` | Dragonfly Doji | Bullish | Reversal | Important | 69% | 1 | H1 · H4 · D1 |
| 09 | `GSD` | Gravestone Doji | Bearish | Reversal | Important | 69% | 1 | H1 · H4 · D1 |
| 10 | `LLD` | Long-Legged Doji | Dual / Neutral | Indecision | Important | 58% | 1 | H1 · H4 · D1 |
| 11 | `SPT` | Spinning Top | Dual / Neutral | Indecision | Important | 54% | 1 | H1 · H4 |
| 12 | `BLH` | Belt Hold | Dual / Neutral | Reversal | Rare | 60% | 1 | H1 · H4 · D1 |

## Double Candle (13)

| # | Code | Pattern | Direction | Role | Priority | Rel. | Candles | Ideal TF |
| --: | :-- | :-- | :-- | :-- | :-- | --: | --: | :-- |
| 13 | `BEC` | Bullish Engulfing | Bullish | Reversal | Must | 78% | 2 | H1 · H4 · D1 |
| 14 | `SEC` | Bearish Engulfing | Bearish | Reversal | Must | 77% | 2 | H1 · H4 · D1 |
| 15 | `BHA` | Bullish Harami | Bullish | Reversal | Important | 64% | 2 | H4 · D1 |
| 16 | `SHA` | Bearish Harami | Bearish | Reversal | Important | 63% | 2 | H4 · D1 |
| 17 | `BHC` | Bullish Harami Cross | Bullish | Reversal | Important | 70% | 2 | H4 · D1 |
| 18 | `SHC` | Bearish Harami Cross | Bearish | Reversal | Important | 70% | 2 | H4 · D1 |
| 19 | `PLN` | Piercing Line | Bullish | Reversal | Must | 71% | 2 | H4 · D1 |
| 20 | `DCC` | Dark Cloud Cover | Bearish | Reversal | Must | 71% | 2 | H4 · D1 |
| 21 | `TWB` | Tweezer Bottom | Bullish | Reversal | Important | 62% | 2 | M15 · H1 · H4 |
| 22 | `TWT` | Tweezer Top | Bearish | Reversal | Important | 62% | 2 | M15 · H1 · H4 |
| 23 | `BKK` | Bullish Kicker | Bullish | Reversal | Rare | 79% | 2 | H4 · D1 · W1 |
| 24 | `SKK` | Bearish Kicker | Bearish | Reversal | Rare | 79% | 2 | H4 · D1 · W1 |
| 25 | `SPL` | Separating Lines | Dual / Neutral | Continuation | Rare | 60% | 2 | H1 · H4 |

## Triple & Multi (20)

| # | Code | Pattern | Direction | Role | Priority | Rel. | Candles | Ideal TF |
| --: | :-- | :-- | :-- | :-- | :-- | --: | --: | :-- |
| 26 | `MST` | Morning Star | Bullish | Reversal | Must | 76% | 3 | H4 · D1 |
| 27 | `EST` | Evening Star | Bearish | Reversal | Must | 76% | 3 | H4 · D1 |
| 28 | `MDS` | Morning Doji Star | Bullish | Reversal | Important | 79% | 3 | H4 · D1 |
| 29 | `EDS` | Evening Doji Star | Bearish | Reversal | Important | 79% | 3 | H4 · D1 |
| 30 | `TWS` | Three White Soldiers | Bullish | Reversal | Must | 74% | 3 | H4 · D1 |
| 31 | `TBC` | Three Black Crows | Bearish | Reversal | Must | 74% | 3 | H4 · D1 |
| 32 | `TIU` | Three Inside Up | Bullish | Reversal | Important | 70% | 3 | H4 · D1 |
| 33 | `TID` | Three Inside Down | Bearish | Reversal | Important | 70% | 3 | H4 · D1 |
| 34 | `TOU` | Three Outside Up | Bullish | Reversal | Important | 73% | 3 | H4 · D1 |
| 35 | `TOD` | Three Outside Down | Bearish | Reversal | Important | 73% | 3 | H4 · D1 |
| 36 | `R3M` | Rising Three Methods | Bullish | Continuation | Important | 72% | 5 | H4 · D1 |
| 37 | `F3M` | Falling Three Methods | Bearish | Continuation | Important | 72% | 5 | H4 · D1 |
| 38 | `BKA` | Breakaway (Bullish) | Bullish | Reversal | Rare | 66% | 5 | D1 |
| 39 | `LDB` | Ladder Bottom | Bullish | Reversal | Rare | 65% | 5 | D1 |
| 40 | `CBS` | Concealing Baby Swallow | Bullish | Reversal | Rare | 67% | 4 | D1 |
| 41 | `U3R` | Unique Three River | Bullish | Reversal | Rare | 62% | 3 | D1 |
| 42 | `TS3` | Tri-Star (Bullish) | Bullish | Reversal | Rare | 68% | 3 | D1 · W1 |
| 43 | `ADB` | Advance Block | Bearish | Exhaustion | Important | 61% | 3 | H4 · D1 |
| 44 | `DLB` | Deliberation Pattern | Bearish | Exhaustion | Important | 60% | 3 | H4 · D1 |
| 45 | `UGC` | Upside Gap Two Crows | Bearish | Exhaustion | Rare | 59% | 3 | D1 |

## Which patterns are armed on which time frame

| Chart TF | Patterns armed (strict mode) |
| :-- | :-- |
| M1 | _none — the chart stays empty_ |
| M2 | _none — the chart stays empty_ |
| M3 | _none — the chart stays empty_ |
| M5 | _none — the chart stays empty_ |
| M10 | _none — the chart stays empty_ |
| M15 | `BMZ`, `SMZ`, `TWB`, `TWT` |
| M30 | _none — the chart stays empty_ |
| M45 | _none — the chart stays empty_ |
| H1 | `HAM`, `HGM`, `IHM`, `SHS`, `BMZ`, `SMZ`, `DOJ`, `DFD`, `GSD`, `LLD`, `SPT`, `BLH`, `BEC`, `SEC`, `TWB`, `TWT`, `SPL` |
| H2 | _none — the chart stays empty_ |
| H3 | _none — the chart stays empty_ |
| H4 | `HAM`, `HGM`, `IHM`, `SHS`, `BMZ`, `SMZ`, `DOJ`, `DFD`, `GSD`, `LLD`, `SPT`, `BLH`, `BEC`, `SEC`, `BHA`, `SHA`, `BHC`, `SHC`, `PLN`, `DCC`, `TWB`, `TWT`, `BKK`, `SKK`, `SPL`, `MST`, `EST`, `MDS`, `EDS`, `TWS`, `TBC`, `TIU`, `TID`, `TOU`, `TOD`, `R3M`, `F3M`, `ADB`, `DLB` |
| H6 | _none — the chart stays empty_ |
| H8 | _none — the chart stays empty_ |
| H12 | _none — the chart stays empty_ |
| D1 | `HAM`, `HGM`, `IHM`, `SHS`, `DOJ`, `DFD`, `GSD`, `LLD`, `BLH`, `BEC`, `SEC`, `BHA`, `SHA`, `BHC`, `SHC`, `PLN`, `DCC`, `BKK`, `SKK`, `MST`, `EST`, `MDS`, `EDS`, `TWS`, `TBC`, `TIU`, `TID`, `TOU`, `TOD`, `R3M`, `F3M`, `BKA`, `LDB`, `CBS`, `U3R`, `TS3`, `ADB`, `DLB`, `UGC` |
| W1 | `BKK`, `SKK`, `TS3` |
| MN1 | _none — the chart stays empty_ |

An empty row is not a bug. It is the whole point: there is no candlestick pattern in this catalogue that a professional would trade off an M2 chart, so an M2 chart shows nothing. Switch the time frame gating to `Ideal ± 1 step` or `Off` if you want to study them anyway.


## Descriptions

**01 · `HAM` — Hammer** (H1 · H4 · D1)  
After a downtrend a small body sits at the TOP of the range with a lower shadow at least 2x the body. Sellers pushed price deep down, buyers slammed it back to the open. Body colour does not decide validity — the OHLC relationship does.

**02 · `HGM` — Hanging Man** (H1 · H4 · D1)  
The same shape as the hammer but printed after an UPTREND. The long lower shadow proves sellers are already able to drive price deep inside the session — the first crack in buyer control.

**03 · `IHM` — Inverted Hammer** (H1 · H4 · D1)  
After a downtrend, buyers manage a strong intrabar push up but cannot hold it. The long upper shadow shows demand is testing the water — a bottoming attempt that must be confirmed.

**04 · `SHS` — Shooting Star** (H1 · H4 · D1)  
After an uptrend, price spikes up and is rejected all the way back to the open. The long upper shadow is trapped-buyer inventory sitting above the market.

**05 · `BMZ` — Bullish Marubozu** (M15 · H1 · H4)  
A full-bodied green candle with virtually no shadows: buyers controlled the candle from the first tick to the last. Pure momentum.

**06 · `SMZ` — Bearish Marubozu** (M15 · H1 · H4)  
A full-bodied red candle with virtually no shadows: sellers controlled every tick of the candle.

**07 · `DOJ` — Doji** (H1 · H4 · D1)  
Open and close are effectively equal. Buyers and sellers finished the candle exactly where they started — a complete stalemate. Direction comes from what breaks the doji's range.

**08 · `DFD` — Dragonfly Doji** (H1 · H4 · D1)  
Open, high and close sit at the top while a long lower shadow shows a complete rejection of lower prices. The strongest member of the doji family for bottoms.

**09 · `GSD` — Gravestone Doji** (H1 · H4 · D1)  
Open, low and close sit at the bottom while a long upper shadow marks a total rejection of higher prices — the mirror of the dragonfly.

**10 · `LLD` — Long-Legged Doji** (H1 · H4 · D1)  
A doji with long shadows on BOTH sides: violent two-sided fighting that ends in a perfect draw. Volatility expansion with zero resolution.

**11 · `SPT` — Spinning Top** (H1 · H4)  
A small body with shadows on both sides that are each longer than the body. Neither side could finish what they started — momentum is draining.

**12 · `BLH` — Belt Hold** (H1 · H4 · D1)  
A long candle that opens exactly at its extreme and never trades back through it: the bullish version opens at the low, the bearish version opens at the high. One side seized control at the opening tick and never let go.

**13 · `BEC` — Bullish Engulfing** (H1 · H4 · D1)  
After a downtrend a small bearish candle appears whose body is fully engulfed by a large bullish candle. One of the most reliable and best-known upside reversal patterns.

**14 · `SEC` — Bearish Engulfing** (H1 · H4 · D1)  
After an uptrend a small bullish candle is completely swallowed by a large bearish candle: an instant and total transfer of control from buyers to sellers.

**15 · `BHA` — Bullish Harami** (H4 · D1)  
A large bearish candle is followed by a small bullish candle contained entirely inside its body. Selling pressure suddenly evaporates — the market is 'pregnant' with a reversal.

**16 · `SHA` — Bearish Harami** (H4 · D1)  
A large bullish candle followed by a small bearish candle held entirely inside its body — buying momentum stalls abruptly.

**17 · `BHC` — Bullish Harami Cross** (H4 · D1)  
A harami whose second candle is a doji: total indecision appearing directly inside the body of a big selling candle. Stronger than the ordinary harami.

**18 · `SHC` — Bearish Harami Cross** (H4 · D1)  
A harami whose second candle is a doji, printed after an uptrend: buyers walked straight into a wall of indecision.

**19 · `PLN` — Piercing Line** (H4 · D1)  
After a downtrend, a bullish candle opens at or below the previous low and closes back ABOVE the 50% level of the previous bearish body. Buyers reclaimed more than half of the damage in one candle.

**20 · `DCC` — Dark Cloud Cover** (H4 · D1)  
After an uptrend, a bearish candle opens above the previous high and closes back BELOW the 50% level of the previous bullish body — the mirror of the piercing line.

**21 · `TWB` — Tweezer Bottom** (M15 · H1 · H4)  
Two consecutive candles print virtually the SAME low: the market tested a price twice and was refused twice. A double bottom compressed into two candles.

**22 · `TWT` — Tweezer Top** (M15 · H1 · H4)  
Two consecutive candles print virtually the same HIGH — price was rejected twice from the identical level.

**23 · `BKK` — Bullish Kicker** (H4 · D1 · W1)  
A bearish candle is followed by a bullish candle that opens ABOVE the previous body and never trades back into it. Nobody who sold gets a second chance — usually driven by news.

**24 · `SKK` — Bearish Kicker** (H4 · D1 · W1)  
A bullish candle followed by a bearish candle opening below the previous body with no overlap: every buyer is trapped instantly.

**25 · `SPL` — Separating Lines** (H1 · H4)  
A counter-trend candle is completely negated by the next candle, which opens at the SAME open price and runs back with the trend. The pullback is cancelled and the trend resumes.

**26 · `MST` — Morning Star** (H4 · D1)  
The classic three-candle bullish reversal: a big red candle, a small indecisive star that separates from it, then a big green candle driving back into the first body. Panic, pause, recovery.

**27 · `EST` — Evening Star** (H4 · D1)  
The classic three-candle bearish reversal: a big green candle, a small star that separates above it, then a big red candle tearing back into the first body.

**28 · `MDS` — Morning Doji Star** (H4 · D1)  
A morning star whose middle candle is a perfect doji — total indecision precisely at the bottom of the move. The purest form of the three-candle bottom.

**29 · `EDS` — Evening Doji Star** (H4 · D1)  
An evening star whose middle candle is a doji — perfect indecision at the very top.

**30 · `TWS` — Three White Soldiers** (H4 · D1)  
Three consecutive long green candles, each opening inside the previous body and closing progressively higher with small upper shadows: a full, orderly buyer assault.

**31 · `TBC` — Three Black Crows** (H4 · D1)  
Three consecutive long red candles with progressively lower closes and small lower shadows — total seller domination.

**32 · `TIU` — Three Inside Up** (H4 · D1)  
A bullish harami that gets its confirmation candle: the staged version of an upside reversal. Stall, contain, then break out.

**33 · `TID` — Three Inside Down** (H4 · D1)  
A bearish harami plus its confirmation candle — a staged downside reversal.

**34 · `TOU` — Three Outside Up** (H4 · D1)  
A bullish engulfing plus a confirmation candle: the affirmed version of the market's best-known bullish reversal.

**35 · `TOD` — Three Outside Down** (H4 · D1)  
A bearish engulfing plus a confirmation candle — an affirmed downside reversal.

**36 · `R3M` — Rising Three Methods** (H4 · D1)  
A pause inside an uptrend: a big green candle, three small candles drifting back but staying inside its range, then another big green candle breaking to new highs. The trend simply took a breath.

**37 · `F3M` — Falling Three Methods** (H4 · D1)  
A pause inside a downtrend: a big red candle, three small candles drifting up inside its range, then another big red candle breaking to new lows.

**38 · `BKA` — Breakaway (Bullish)** (D1)  
Sellers running out of breath: a long red candle, a red candle separating below it, two more weak declining candles, then a strong green candle that reclaims all of the fall back to the separation zone.

**39 · `LDB` — Ladder Bottom** (D1)  
A broken ladder: three consecutive declining red candles, a fourth red candle that finally shows a meaningful upper shadow (the first buying attempt), then a green candle that opens above the whole previous body.

**40 · `CBS` — Concealing Baby Swallow** (D1)  
A small swallow hidden inside a big red candle. Seller panic peaks and is instantly absorbed: two long declining reds, a third red separating lower whose upper shadow reaches back into candle 2, then a fourth big red candle that completely engulfs the third.

**41 · `U3R` — Unique Three River** (D1)  
A big red candle, then a hammer-like red candle that digs to a new low but closes back up inside, then a small green candle that locks the base without exceeding the previous close.

**42 · `TS3` — Tri-Star (Bullish)** (D1 · W1)  
Three consecutive dojis with the middle one separating below the other two — a three-act equilibrium at the bottom of a move. Extremely rare and, at the right location, extremely telling.

**43 · `ADB` — Advance Block** (H4 · D1)  
Three soldiers losing step: three green candles with shrinking bodies and lengthening upper shadows. The advance is still going but every candle is meeting more supply than the last.

**44 · `DLB` — Deliberation Pattern** (H4 · D1)  
Three soldiers pausing to think: two strong green candles, then a third that shrinks into a small body / spinning top right at the highs. Buyers hesitated for the first time.

**45 · `UGC` — Upside Gap Two Crows** (D1)  
Two black crows perched above a gap: a strong green candle, then a red candle separating above it, then a bigger red candle that swallows the first crow but still closes above the green candle's close. The euphoria is being eaten from the top down.

