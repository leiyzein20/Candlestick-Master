"""Reference model for the Candlestick Master engine mathematics.

A Python mirror of the L1/L2 arithmetic and of the state machines defined in
MASTER_SPECIFICATION.md, engines/OHLC_ENGINE.md, engines/WICK_BODY_ENGINE.md,
engines/RELATIONSHIP_ENGINE.md, engines/TIMEFRAME_ENGINE.md, engines/RSI_ENGINE.md,
engines/EMA_ENGINE.md, engines/CONFIRMATION_ENGINE.md and engines/VALIDATION_ENGINE.md.

Purpose: make the specification executable before any Pine Script exists, so that every
threshold and every edge case is pinned down by a test rather than by prose alone. When the
implementation gate opens, the Pine code must agree with this model, and the vectors in
tests/vectors/ are the contract.

This module contains NO pattern definitions. Patterns arrive with the owner's
specifications; nothing here anticipates them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Defaults. Every value here is an [ENGINE-DEFAULT] registered in
# docs/DEFINITION_CONVERSIONS.md. Nothing may hardcode a threshold elsewhere.
# ---------------------------------------------------------------------------

DEFAULTS = {
    # body / wick classes
    "doji_max_body": 0.10,        # CV-BODY-001
    "small_body_max": 0.30,       # CV-BODY-002
    "large_body_min": 0.60,       # CV-BODY-003
    "marubozu_min": 0.90,         # CV-BODY-004
    "long_wick_min": 0.60,        # CV-WICK-001
    "long_wick_body_mult": 2.0,   # CV-WICK-002
    "short_wick_max": 0.10,       # CV-WICK-003
    # relative size
    "size_avg_len": 20,           # CV-SIZE-001 / CV-SIZE-002
    "large_candle_min": 1.5,      # CV-SIZE-003
    "small_candle_max": 0.6,      # CV-SIZE-004
    # comparison
    "eps_ticks": 0.0,             # CV-MATH-001
    # rsi
    "rsi_len": 14,                # [OWNER]
    "rsi_ob": 70.0,               # CV-RSI-001
    "rsi_os": 30.0,               # CV-RSI-001
    "pivot_left": 5,              # CV-RSI-003
    "pivot_right": 5,             # CV-RSI-003
    "div_min_gap": 5,             # CV-RSI-004
    "div_max_gap": 60,            # CV-RSI-005
    "div_active_bars": 10,        # CV-RSI-006
    # ema
    "reclaim_window": 3,          # CV-EMA-001
    # volume
    "vol_avg_len": 20,            # CV-VOL-001
    "vol_above": 1.20,            # CV-VOL-002
    "vol_high": 1.50,             # CV-VOL-003
    "vol_below": 0.80,            # CV-VOL-004
    # confirmation
    "confirm_bars": 3,            # CV-CONF-002
    # validation bands (on ratio)
    "band_weak_max": 1.0 / 3.0,   # <= 0.3333 -> WEAK
    "band_moderate_max": 0.5,     # <= 0.5    -> MODERATE
    "band_strong_max": 5.0 / 6.0,  # <= 0.8333 -> STRONG
}

TOL = 1e-9


# ---------------------------------------------------------------------------
# L1 - OHLC engine
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Candle:
    o: float
    h: float
    l: float
    c: float

    def validate(self) -> None:
        """Reject impossible candles outright rather than producing nonsense."""
        if self.h < self.l:
            raise ValueError(f"high {self.h} below low {self.l}")
        if not (self.l - TOL <= self.o <= self.h + TOL):
            raise ValueError(f"open {self.o} outside range [{self.l}, {self.h}]")
        if not (self.l - TOL <= self.c <= self.h + TOL):
            raise ValueError(f"close {self.c} outside range [{self.l}, {self.h}]")


def metrics(k: Candle) -> dict:
    """OHLC_ENGINE.md sections 2-5. Degenerate candles get defined constants, never na."""
    k.validate()
    rng = k.h - k.l
    body = abs(k.c - k.o)
    upper = k.h - max(k.o, k.c)
    lower = min(k.o, k.c) - k.l
    measurable = rng > 0

    if measurable:
        body_pct = body / rng
        upper_pct = upper / rng
        lower_pct = lower / rng
        close_pos = (k.c - k.l) / rng
        open_pos = (k.o - k.l) / rng
    else:
        # OHLC_ENGINE.md section 5: fixed values plus is_measurable=False, so no boolean
        # anywhere can become undefined. Patterns must gate on is_measurable.
        body_pct = upper_pct = lower_pct = 0.0
        close_pos = open_pos = 0.5

    return {
        "range": rng,
        "body": body,
        "upper_wick": upper,
        "lower_wick": lower,
        "body_top": max(k.o, k.c),
        "body_bottom": min(k.o, k.c),
        "body_pct": body_pct,
        "upper_wick_pct": upper_pct,
        "lower_wick_pct": lower_pct,
        "close_pos": close_pos,
        "open_pos": open_pos,
        "candle_mid": (k.h + k.l) / 2.0,
        "body_mid": (k.o + k.c) / 2.0,
        "is_bull": k.c > k.o,
        "is_bear": k.c < k.o,
        "is_flat": k.c == k.o,
        "is_measurable": measurable,
    }


def check_identities(k: Candle) -> list[str]:
    """OHLC_ENGINE.md section 3. Returns a list of violated identities (empty == good)."""
    m = metrics(k)
    bad: list[str] = []

    if abs(m["range"] - (m["body"] + m["upper_wick"] + m["lower_wick"])) > TOL:
        bad.append("range != body + upper_wick + lower_wick")
    if m["is_measurable"]:
        total = m["body_pct"] + m["upper_wick_pct"] + m["lower_wick_pct"]
        if abs(total - 1.0) > TOL:
            bad.append("percentages do not sum to 1")
        if abs(m["close_pos"] - (1.0 - (k.h - k.c) / m["range"])) > TOL:
            bad.append("close_pos inconsistent")
    if abs((m["body_top"] - m["body_bottom"]) - m["body"]) > TOL:
        bad.append("body_top - body_bottom != body")
    if sum([m["is_bull"], m["is_bear"], m["is_flat"]]) != 1:
        bad.append("colour flags not mutually exclusive")
    for key in ("body_pct", "upper_wick_pct", "lower_wick_pct", "close_pos", "open_pos"):
        if not (-TOL <= m[key] <= 1.0 + TOL):
            bad.append(f"{key} outside 0..1")
    return bad


# ---------------------------------------------------------------------------
# L1 - wick/body classification
# ---------------------------------------------------------------------------


def classes(k: Candle, cfg: Optional[dict] = None) -> dict:
    """WICK_BODY_ENGINE.md section 2. Both long-wick idioms are published separately."""
    c = dict(DEFAULTS, **(cfg or {}))
    m = metrics(k)
    body, upper, lower = m["body"], m["upper_wick"], m["lower_wick"]
    mult = c["long_wick_body_mult"]

    return {
        "is_doji_body": m["body_pct"] <= c["doji_max_body"],
        "is_small_body": m["body_pct"] <= c["small_body_max"],
        "is_large_body": m["body_pct"] >= c["large_body_min"],
        "is_marubozu": m["body_pct"] >= c["marubozu_min"],
        # ...WickR: fraction of range
        "is_long_upper_wick_r": m["upper_wick_pct"] >= c["long_wick_min"],
        "is_long_lower_wick_r": m["lower_wick_pct"] >= c["long_wick_min"],
        # ...WickB: multiple of body. Multiplication, never division: with body == 0 this is
        # trivially true, which is the documented trap in WICK_BODY_ENGINE.md section 3.
        "is_long_upper_wick_b": upper >= mult * body,
        "is_long_lower_wick_b": lower >= mult * body,
        "is_short_upper_wick": m["upper_wick_pct"] <= c["short_wick_max"],
        "is_short_lower_wick": m["lower_wick_pct"] <= c["short_wick_max"],
    }


def relative_size(k: Candle, avg_range: float, avg_body: float,
                  cfg: Optional[dict] = None) -> dict:
    c = dict(DEFAULTS, **(cfg or {}))
    m = metrics(k)
    rel_range = m["range"] / avg_range if avg_range > 0 else None
    rel_body = m["body"] / avg_body if avg_body > 0 else None
    return {
        "rel_range": rel_range,
        "rel_body": rel_body,
        "is_large_candle": rel_range is not None and rel_range >= c["large_candle_min"],
        "is_small_candle": rel_range is not None and rel_range <= c["small_candle_max"],
    }


# ---------------------------------------------------------------------------
# L2 - relationship engine
# ---------------------------------------------------------------------------


def relationship(a: Candle, b: Candle, atr: Optional[float] = None) -> dict:
    """RELATIONSHIP_ENGINE.md. `a` is the newer candle, `b` the older one."""
    ma, mb = metrics(a), metrics(b)
    prev_body = abs(b.o - b.c)

    # Penetration is undefined without a previous body (RELATIONSHIP_ENGINE.md section 7).
    pen_up = (a.c - b.c) / (b.o - b.c) if prev_body > 0 and b.o > b.c else None
    pen_dn = (b.c - a.c) / (b.c - b.o) if prev_body > 0 and b.c > b.o else None

    true_gap_up = a.l > b.h
    true_gap_dn = a.h < b.l

    out = {
        "body_engulfs": ma["body_top"] >= mb["body_top"] and ma["body_bottom"] <= mb["body_bottom"],
        "body_engulfs_strict": ma["body_top"] > mb["body_top"] and ma["body_bottom"] < mb["body_bottom"],
        "range_engulfs": a.h >= b.h and a.l <= b.l,
        "range_engulfs_strict": a.h > b.h and a.l < b.l,
        "body_inside": ma["body_top"] <= mb["body_top"] and ma["body_bottom"] >= mb["body_bottom"],
        "range_inside": a.h <= b.h and a.l >= b.l,
        "close_above_prev_body_mid": a.c > mb["body_mid"],
        "close_below_prev_body_mid": a.c < mb["body_mid"],
        "close_above_prev_range_mid": a.c > mb["candle_mid"],
        "close_below_prev_range_mid": a.c < mb["candle_mid"],
        "penetration_up": pen_up,
        "penetration_down": pen_dn,
        "true_gap_up": true_gap_up,
        "true_gap_down": true_gap_dn,
        "body_gap_up": ma["body_bottom"] > mb["body_top"],
        "body_gap_down": ma["body_top"] < mb["body_bottom"],
        "gap_up_size": (a.l - b.h) if true_gap_up else 0.0,
        "gap_down_size": (b.l - a.h) if true_gap_dn else 0.0,
        "open_above_prev_close": a.o > b.c,
        "open_below_prev_close": a.o < b.c,
        "open_above_prev_open": a.o > b.o,
        "open_below_prev_open": a.o < b.o,
        "close_above_prev_close": a.c > b.c,
        "close_below_prev_close": a.c < b.c,
        "close_above_prev_high": a.c > b.h,
        "close_below_prev_low": a.c < b.l,
        "higher_high": a.h > b.h,
        "lower_low": a.l < b.l,
    }
    if atr and atr > 0:
        out["gap_up_size_atr"] = out["gap_up_size"] / atr
        out["gap_down_size_atr"] = out["gap_down_size"] / atr
    return out


def close_above_prev_body_pct(a: Candle, b: Candle, p: float) -> bool:
    """Generalised form; p == 0.5 must equal close_above_prev_body_mid."""
    mb = metrics(b)
    return a.c > mb["body_bottom"] + p * (mb["body_top"] - mb["body_bottom"])


# ---------------------------------------------------------------------------
# L5 - timeframe engine
# ---------------------------------------------------------------------------

CANONICAL_TF = {
    "1m": 1, "2m": 2, "3m": 3, "5m": 5, "10m": 10, "15m": 15, "30m": 30, "45m": 45,
    "1H": 60, "2H": 120, "3H": 180, "4H": 240, "6H": 360, "8H": 480, "12H": 720,
    "1D": 1440, "1W": 10080, "1M": 43200,
}

# CV-TF-001. Ordered, non-overlapping, and total over all minute values >= 1.
# Anything below 1 minute is SUB_MINUTE and is handled before this table is consulted.
TF_CLASSES = [
    ("MIN_FAST", 1, 4),
    ("MIN_MID", 5, 14),
    ("MIN_SLOW", 15, 59),
    ("HOUR_LOW", 60, 239),
    ("HOUR_HIGH", 240, 1439),
    ("DAILY", 1440, 10079),
    ("WEEKLY", 10080, 43199),
    ("MONTHLY", 43200, float("inf")),
]


def tf_class(minutes: float) -> str:
    if minutes < 1:
        return "SUB_MINUTE"
    for name, lo, hi in TF_CLASSES:
        if lo <= minutes <= hi:
            return name
    return "MONTHLY"


def tf_allowed(chart_minutes: float, pattern_tfs: str, mode: str,
               test_mode: bool = False) -> bool:
    """TIMEFRAME_ENGINE.md section 5. `pattern_tfs` is a CSV of canonical minute values."""
    if test_mode or mode == "OFF":
        return True
    if not pattern_tfs.strip():
        # An unsupplied timeframe list must not silently hide a pattern everywhere.
        return True
    listed = [float(x) for x in pattern_tfs.split(",") if x.strip()]
    if mode == "EXACT":
        return any(abs(chart_minutes - m) < TOL for m in listed)
    if mode == "CLASS":
        return tf_class(chart_minutes) in {tf_class(m) for m in listed}
    raise ValueError(f"unknown enforcement mode {mode!r}")


# ---------------------------------------------------------------------------
# L3 - RSI engine (Wilder) and pivot divergence
# ---------------------------------------------------------------------------


def rsi_wilder(closes: list[float], length: int = 14) -> list[Optional[float]]:
    """Wilder RSI, matching ta.rsi(). None for bars before the seed is complete."""
    out: list[Optional[float]] = [None] * len(closes)
    if len(closes) <= length:
        return out
    gains = losses = 0.0
    for i in range(1, length + 1):
        d = closes[i] - closes[i - 1]
        gains += max(d, 0.0)
        losses += max(-d, 0.0)
    avg_gain, avg_loss = gains / length, losses / length
    out[length] = _rsi_from(avg_gain, avg_loss)
    for i in range(length + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        avg_gain = (avg_gain * (length - 1) + max(d, 0.0)) / length
        avg_loss = (avg_loss * (length - 1) + max(-d, 0.0)) / length
        out[i] = _rsi_from(avg_gain, avg_loss)
    return out


def _rsi_from(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 100.0
    if avg_gain == 0:
        return 0.0
    return 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)


@dataclass
class Pivot:
    bar: int
    price: float
    confirmed_at: int          # bar + right: the first bar on which it may be used


def find_pivot_lows(lows: list[float], left: int, right: int) -> list[Pivot]:
    piv = []
    for i in range(left, len(lows) - right):
        window = lows[i - left:i + right + 1]
        if lows[i] == min(window) and window.count(lows[i]) == 1:
            piv.append(Pivot(i, lows[i], i + right))
    return piv


def find_pivot_highs(highs: list[float], left: int, right: int) -> list[Pivot]:
    piv = []
    for i in range(left, len(highs) - right):
        window = highs[i - left:i + right + 1]
        if highs[i] == max(window) and window.count(highs[i]) == 1:
            piv.append(Pivot(i, highs[i], i + right))
    return piv


@dataclass
class Divergence:
    kind: str                  # "BULL" | "BEAR"
    first: Pivot
    second: Pivot
    active_from: int
    active_to: int


def find_divergences(highs: list[float], lows: list[float], closes: list[float],
                     cfg: Optional[dict] = None) -> list[Divergence]:
    """RSI_ENGINE.md section 5.

    RSI is sampled at the *price* pivot (CV-RSI-007). A divergence becomes usable only from
    the second pivot's confirmation bar (pivot bar + right), never from the pivot bar
    itself - this is the no-repaint requirement made concrete.
    """
    c = dict(DEFAULTS, **(cfg or {}))
    rsi = rsi_wilder(closes, int(c["rsi_len"]))
    left, right = int(c["pivot_left"]), int(c["pivot_right"])
    out: list[Divergence] = []

    def scan(pivots: list[Pivot], kind: str) -> None:
        for prev, cur in zip(pivots, pivots[1:]):
            gap = cur.bar - prev.bar
            if not (c["div_min_gap"] <= gap <= c["div_max_gap"]):
                continue
            r_prev, r_cur = rsi[prev.bar], rsi[cur.bar]
            if r_prev is None or r_cur is None:
                continue
            if kind == "BULL" and cur.price < prev.price and r_cur > r_prev:
                pass
            elif kind == "BEAR" and cur.price > prev.price and r_cur < r_prev:
                pass
            else:
                continue
            out.append(Divergence(kind, prev, cur, cur.confirmed_at,
                                  cur.confirmed_at + int(c["div_active_bars"])))

    scan(find_pivot_lows(lows, left, right), "BULL")
    scan(find_pivot_highs(highs, left, right), "BEAR")
    return out


def divergence_active(divs: list[Divergence], kind: str, bar: int) -> bool:
    return any(d.kind == kind and d.active_from <= bar <= d.active_to for d in divs)


def rsi_state(rsi_now: Optional[float], rsi_prev: Optional[float],
              bull_div: bool, bear_div: bool, cfg: Optional[dict] = None) -> str:
    """RSI_ENGINE.md section 4. Precedence: divergence > OB/OS > momentum > neutral.

    `rsi > 50` is BULL_MOM. It is never reported as a divergence.
    """
    c = dict(DEFAULTS, **(cfg or {}))
    if rsi_now is None:
        return "UNAVAILABLE"
    if bull_div:
        return "BULL_DIV"
    if bear_div:
        return "BEAR_DIV"
    if rsi_now <= c["rsi_os"]:
        return "OVERSOLD"
    if rsi_now >= c["rsi_ob"]:
        return "OVERBOUGHT"
    if rsi_prev is not None and rsi_now > 50 and rsi_now > rsi_prev:
        return "BULL_MOM"
    if rsi_prev is not None and rsi_now < 50 and rsi_now < rsi_prev:
        return "BEAR_MOM"
    return "NEUTRAL"


# ---------------------------------------------------------------------------
# L3 - EMA engine
# ---------------------------------------------------------------------------


def ema(values: list[float], length: int) -> list[Optional[float]]:
    """Matches ta.ema(): SMA seed at bar `length-1`, then the standard recursion."""
    out: list[Optional[float]] = [None] * len(values)
    if len(values) < length:
        return out
    alpha = 2.0 / (length + 1.0)
    seed = sum(values[:length]) / length
    out[length - 1] = seed
    prev = seed
    for i in range(length, len(values)):
        prev = alpha * values[i] + (1 - alpha) * prev
        out[i] = prev
    return out


def reclaim_series(closes: list[float], line: list[Optional[float]],
                   window: int) -> list[bool]:
    """EMA_ENGINE.md section 4.

    Two conditions, both required: the close is above the line now, AND the crossing
    happened within `window` closed bars. Being above the line for 40 bars is not a
    reclaim.
    """
    out = [False] * len(closes)
    bars_since_cross: Optional[int] = None
    for i in range(len(closes)):
        e, e_prev = line[i], line[i - 1] if i > 0 else None
        if e is None:
            continue
        if bars_since_cross is not None:
            bars_since_cross += 1
        if i > 0 and e_prev is not None and closes[i] > e and closes[i - 1] <= e_prev:
            bars_since_cross = 0
        if closes[i] > e and bars_since_cross is not None and bars_since_cross <= window:
            out[i] = True
    return out


# ---------------------------------------------------------------------------
# L3 - volume engine
# ---------------------------------------------------------------------------


def volume_state(vol: Optional[float], vol_avg: Optional[float],
                 cfg: Optional[dict] = None) -> tuple[str, Optional[float]]:
    """VOLUME_ENGINE.md section 3. Missing or all-zero volume is UNAVAILABLE, which the
    validation engine excludes from maxScore rather than scoring as a failure."""
    c = dict(DEFAULTS, **(cfg or {}))
    if vol is None or vol_avg is None or vol_avg <= 0:
        return "UNAVAILABLE", None
    ratio = vol / vol_avg
    if ratio >= c["vol_high"]:
        return "HIGH", ratio
    if ratio >= c["vol_above"]:
        return "ABOVE", ratio
    if ratio <= c["vol_below"]:
        return "BELOW", ratio
    return "NORMAL", ratio


# ---------------------------------------------------------------------------
# L7 - confirmation engine
# ---------------------------------------------------------------------------


@dataclass
class Pending:
    direction: int                 # +1 bullish, -1 bearish, 0 neutral
    trigger: float                 # captured at detection, never recomputed
    invalidation: float
    bars_left: int
    status: str = "DETECTED"
    resolved_after: Optional[int] = None
    resolved_direction: Optional[int] = None


def resolve(pending: Pending, closes: list[float]) -> Pending:
    """CONFIRMATION_ENGINE.md sections 4-7.

    `closes` are the closes of the candles AFTER the pattern's last candle, in order. Only
    closed candles are passed in - the forming bar never reaches this function.

    Terminal states are terminal: once resolved, no later price action revisits the outcome.
    """
    if pending.status != "DETECTED":
        return pending

    for offset, close in enumerate(closes, start=1):
        if pending.bars_left <= 0:
            break
        pending.bars_left -= 1

        if pending.direction > 0:
            failed = close < pending.invalidation
            confirmed = close > pending.trigger
        elif pending.direction < 0:
            failed = close > pending.invalidation
            confirmed = close < pending.trigger
        else:
            confirmed = close > pending.trigger or close < pending.invalidation
            failed = False

        # CV-CONF-003: failure wins a same-candle collision.
        if failed:
            pending.status = "FAILED"
            pending.resolved_after = offset
            return pending
        if confirmed:
            pending.status = "CONFIRMED"
            pending.resolved_after = offset
            if pending.direction == 0:
                pending.resolved_direction = 1 if close > pending.trigger else -1
            return pending

    if pending.status == "DETECTED" and pending.bars_left <= 0:
        pending.status = "EXPIRED"      # not FAILED: nothing happened
    return pending


# ---------------------------------------------------------------------------
# L6 - validation engine
# ---------------------------------------------------------------------------

FACTOR_ORDER = ["trend", "location", "rsi", "ema", "volume", "confirmation"]


@dataclass
class Factors:
    """Each factor is 'pass', 'fail', 'oppose', or 'excluded'.

    'fail' means measurable but not supportive; 'oppose' means measurable and actively
    pointing the other way (which triggers a cap, not a negative score); 'excluded' means
    not measurable here and lowers maxScore.
    """
    values: dict = field(default_factory=dict)

    def get(self, name: str) -> str:
        return self.values.get(name, "excluded")


def validate(factors: Factors, cfg: Optional[dict] = None) -> dict:
    """VALIDATION_ENGINE.md sections 4-5."""
    c = dict(DEFAULTS, **(cfg or {}))
    score = 0
    max_score = 0
    opposing = 0

    for name in FACTOR_ORDER:
        v = factors.get(name)
        if v == "excluded":
            continue
        max_score += 1
        if v == "pass":
            score += 1
        elif v == "oppose":
            opposing += 1

    if max_score == 0:
        return {"score": 0, "max_score": 0, "ratio": None, "band": "WEAK",
                "opposing": opposing, "cap": None}

    ratio = score / max_score
    if ratio <= c["band_weak_max"] + TOL:
        band = "WEAK"
    elif ratio <= c["band_moderate_max"] + TOL:
        band = "MODERATE"
    elif ratio <= c["band_strong_max"] + TOL:
        band = "STRONG"
    else:
        band = "VERY STRONG"

    order = ["WEAK", "MODERATE", "STRONG", "VERY STRONG"]
    cap = None

    # 5.3 unconfirmed ceiling: VERY STRONG requires the confirmation factor.
    if band == "VERY STRONG" and factors.get("confirmation") != "pass":
        band = "STRONG"
        cap = "unconfirmed"

    # 5.1 contradiction cap.
    if opposing >= 2:
        limit = "WEAK"
    elif opposing == 1:
        limit = "MODERATE"
    else:
        limit = None
    if limit and order.index(band) > order.index(limit):
        band = limit
        cap = f"{opposing} opposing"

    return {"score": score, "max_score": max_score, "ratio": ratio, "band": band,
            "opposing": opposing, "cap": cap}
