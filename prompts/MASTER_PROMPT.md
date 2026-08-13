# The Master Prompt

This is the prompt to hand to an AI when you want it to build, rebuild or extend the
TradingView indicator. Copy everything inside the fenced block, then paste your pattern
cards underneath it.

The prompt is written so the AI cannot cheat on the parts that usually get skipped:
time frame gating, wick/body maths, the abbreviation-only chart, and the hold-to-read
tooltip.

---

## 1. The build prompt (copy this whole block)

```text
ROLE
You are a Pine Script v6 engineer and a candlestick technician. You write indicators for
TradingView that behave the way a professional price-action trader reads a chart, not the
way a beginner's "pattern scanner" behaves.

GOAL
Build ONE TradingView Pine Script v6 indicator that recognises candlestick patterns on
forex charts from pure OHLC geometry, gates every pattern to its own ideal time frame(s),
prints only a short abbreviation on the chart, and reveals the full professional card when
the abbreviation is hovered or held.

────────────────────────────────────────────────────────────────────────
HARD REQUIREMENTS — do not drop any of these
────────────────────────────────────────────────────────────────────────

1. PURE OHLC DETECTION
   · Validity is decided by the open/high/low/close relationship, NEVER by candle colour.
     A hammer is valid whether its body is green or red.
   · Measure real geometry: body = |close - open|, upper shadow = high - max(open,close),
     lower shadow = min(open,close) - low, range = high - low.
   · "Long body", "small body" and "doji" must be RELATIVE to a rolling average body over
     the last N candles, not absolute pip values, so the script works on every pair and
     every time frame.
   · Where a definition says "closes above the 50% of the previous candle", implement it
     literally as close > (open[1] + close[1]) / 2 — the midpoint of the BODY, not of the
     range. Say in a comment which one you used.
   · Engulfing = the BODY engulfs the previous BODY. Shadows are allowed to stick out.

2. TIME FRAME GATING  ← the feature most scripts get wrong
   · Every pattern carries its own list of ideal time frames, e.g. "H1 · H4 · D1".
   · The pattern may ONLY print when the chart's current time frame is one of its ideal
     time frames. If the chart is on M5 and the pattern is H4/D1, nothing prints.
   · A pattern with three ideal time frames must print on all three, not just the first.
   · Detect the chart time frame with timeframe.in_seconds() and map it onto a ladder:
     M1 M2 M3 M5 M10 M15 M30 M45 H1 H2 H3 H4 H6 H8 H12 D1 W1 MN1.
   · Store the ideal list pipe-delimited ("|H1|H4|D1|") and match with a delimiter on both
     sides, so that "M1" never accidentally matches "M15".
   · Give the user a setting with three modes: Strict (ideal only, default),
     Ideal ± 1 ladder step, and Off (show everywhere).

3. CHART LABELS — abbreviation only
   · The label text on the chart is the abbreviation ONLY, e.g. BEC, HAM, MST. Never the
     full name, so the chart stays clean.
   · Bullish labels sit under the candle, bearish labels above it. Distance from the candle
     is measured in ATR so it scales with volatility.
   · When several patterns fire on the same candle, stack them and cap the number with a
     "max labels per candle" setting.
   · The label must be attached to the LAST candle of the pattern.

4. HOLD-TO-READ TOOLTIP
   · Use the tooltip= parameter of label.new(). On TradingView, hovering (desktop) or
     holding (mobile) the label shows this text.
   · The tooltip must open with exactly this block, filled in live for that candle:

       BEC
       Bullish Engulfing
       Status: CONFIRMED

       Pattern: Valid ✓
       Trend: Downtrend ✓
       Location: Support ✓
       RSI: Bullish divergence ✓
       EMA: Reclaiming 20 EMA ✓
       Volume: Above average ✓

       Validation: STRONG

   · Each of those lines is a LIVE check, not decoration. A line that fails prints ✗ and
     the real state, e.g. "Trend: Downtrend ✗" or "Location: Support ✗".
   · Below that block, print the static card: number, category, role, structure, ideal time
     frames, reliability %, pattern high/low, what it is, how to recognise it, stop loss,
     take profit, and one pro tip.

5. CONFIRMATION ENGINE — how it coordinates with the other indicators
   · Status comes from the candle AFTER the pattern completes:
       CONFIRMED = that candle closes beyond the pattern high (bullish) or low (bearish)
       FAILED    = it closes beyond the opposite extreme
       PENDING   = neither yet
     Evaluate the pattern one bar late and draw the label back onto the pattern candle, so
     nothing ever repaints.
   · Score five independent cross-checks, each worth one point:
       TREND    — the required prior trend, measured BEFORE the pattern's first candle
                  (a 3-candle pattern reads the trend state 3 bars back), from an EMA
                  slope + price position rule.
       LOCATION — the pattern sits at a swing-pivot support (bullish) or resistance
                  (bearish) within a configurable ATR distance.
       RSI      — oversold / overbought, or a pivot-based bullish / bearish divergence.
       EMA      — price is above (bullish) or below (bearish) the fast EMA; say explicitly
                  when the EMA was just reclaimed or just lost.
       VOLUME   — volume above its own moving average by a configurable multiplier. Handle
                  symbols with no volume feed gracefully instead of failing the check
                  silently.
   · Grade the total: 5-4 = STRONG, 3 = MODERATE, 1-2 = WEAK, 0 = NONE. Expose a minimum
     score setting so the user can hide everything below A+ setups.
   · Never block a pattern because a cross-check failed — show it with ✗ and let the score
     speak. Only the trend is allowed to be definitional, and only where the trend IS the
     definition (hammer vs hanging man are the same shape; only the prior trend separates
     them).

6. FILTERS — the user must be able to narrow the chart without editing code
   Provide inputs for:
   · Direction: All / Bullish only / Bearish only / Neutral only.
   · Role: All / Reversal only / Continuation only / Exhaustion only / Indecision only.
   · Category on/off: single-candle, double-candle, triple & multi-candle.
   · Priority: All / Must only / Must + Important.
   · Minimum reliability %.
   · A whitelist and a blacklist of abbreviations as comma-separated text.
   · Status: Confirmed only / Confirmed + Pending / Everything including failed.
   For dual-direction patterns (Belt Hold, Separating Lines) apply the direction filter to
   the direction that actually fired, not to the catalogue entry.

7. FOREX REALITY — gaps
   Spot forex trades 24/5 and almost never gaps, so the stock-market definitions of Morning
   Star, Tri-Star, Breakaway, Concealing Baby Swallow, Kicker and Upside Gap Two Crows
   would never trigger. Provide a "Gap rule" setting with three modes:
     Strict (wick gap)          — a true price gap, the classic definition
     Body gap (forex-friendly)  — bodies must not overlap; DEFAULT
     Off                        — ignore the gap clause entirely
   A Kicker is an exception: even in body mode its open must clear the whole previous
   candle, otherwise every ordinary higher open would be labelled a kicker.

8. STRUCTURE OF THE CODE
   · One registry function addPat(...) called once per pattern, holding all metadata and
     all the educational text. All 45 calls sit together so the catalogue can be edited in
     one place without touching detection logic.
   · One detector boolean per pattern, one line each, named p01 … p45.
   · One emitter function that applies the filters and queues candidates.
   · One render block that builds the tooltip, draws the label and fires alert().
   · Respect Pine's limits: max_labels_count=500, keep local scopes low by putting the
     heavy logic in the single render loop instead of inside the per-pattern function.

9. ALERTS
   Fire alert() with alert.freq_once_per_bar_close carrying abbreviation, name, status,
   score, symbol and time frame. Tell the user to create the alert with the condition
   "Any alert() function call".

10. QUALITY BAR
   · Pine Script v6, must compile with no errors and no warnings.
   · Every tolerance (doji %, long body multiple, shadow ratio, tweezer tolerance, ATR
     distances) is an input, never a magic number buried in a condition.
   · Comment the non-obvious parts only. Do not narrate the code.
   · Do not invent statistics. Reliability percentages come from the cards I give you.

────────────────────────────────────────────────────────────────────────
PATTERN DATA
────────────────────────────────────────────────────────────────────────
I will paste pattern cards below. Each card gives you: number, name, abbreviation,
category, direction, role, priority, reliability, ideal time frames, candle count, the
description, how to recognise it, required trend, confirmation rule, failure condition,
volume note, ideal location, stop loss, take profit and pro tips.

For every card you must produce:
  a) the addPat(...) registry entry, using my exact wording, and
  b) the detector boolean that implements "How to Recognize" literally, and
  c) a one-line note telling me any place where you had to loosen or interpret the
     definition, and why.

Never silently approximate a rule. If a rule cannot be expressed in OHLC terms, say so.

────────────────────────────────────────────────────────────────────────
DELIVERABLE
────────────────────────────────────────────────────────────────────────
Output the complete .pine file, ready to paste into the TradingView Pine Editor, followed
by a short table of every pattern with its abbreviation and ideal time frames, and then
your list of interpretation notes.
```

---

## 2. Variation prompts

Once the indicator exists, you do not need to rebuild it. These are the follow-up prompts
for the changes you asked about. Each one assumes the AI still has the script.

**Only bullish patterns**

```text
Keep everything as it is. I only want bullish patterns on the chart. Set the Direction
filter to "Bullish only" by default, and make sure dual-direction patterns (Belt Hold,
Separating Lines) are judged by the direction that actually fired, so a bearish Belt Hold
stays hidden.
```

**Only one category**

```text
Show only the triple and multi-candle patterns (26-45). Turn the single-candle and
double-candle category switches off by default, and leave the rest of the engine untouched.
```

**Only the highest-quality signals**

```text
Default the script to A+ setups only: Priority = "Must only", minimum reliability 70%,
minimum validation score 4 of 5, and status "Confirmed only". Everything else stays.
```

**Lock the script to one time frame**

```text
I only trade H4. Add a setting "Force single time frame" that, when a time frame is chosen,
hides every pattern whose ideal list does not contain that time frame, regardless of what
chart I am on. Default it to off so the existing behaviour is unchanged.
```

**Add a new pattern to the catalogue**

```text
Add pattern #46 using the card below. Give it a 3-letter abbreviation that does not clash
with any existing code, add its addPat() entry in catalogue order, write its detector as
pXX, register it with f_check using the matching index, and tell me which existing patterns
it can fire alongside on the same candle.

<paste the pattern card here>
```

**Change what the tooltip shows**

```text
In the tooltip, move the stop loss and take profit lines directly under the "Validation:"
line so I can read them without scrolling, and add a line "Entry: <price>" showing the
close of the confirmation candle. Keep the header block exactly as it is.
```

**Tighten a pattern that fires too often**

```text
HAM is printing too often on H1. Tighten it: require the lower shadow to be at least 2.5x
the body, the body to sit in the top 40% of the range, and the prior downtrend to have
lasted at least 5 candles. Expose all three as inputs with the current values as defaults
so I can tune them without editing code.
```

**Debug a pattern that never fires**

```text
CBS has never printed on EURUSD D1 in 5 years of history. Add a temporary debug mode that
plots, for that pattern only, how many of its individual clauses passed on each candle, so
I can see which clause is blocking it. Tell me which clause is the bottleneck before
changing anything.
```

---

## 3. What to paste under the prompt

Use `PATTERN_CARD_TEMPLATE.md` in this folder. One filled card per pattern. The cards you
already have in your app's format work as-is — the template just names the fields the
script actually consumes, so nothing gets lost in translation.
