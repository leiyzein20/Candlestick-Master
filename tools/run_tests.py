#!/usr/bin/env python3
"""Run every engine test vector and property check against tools/reference_model.py.

Usage:
    python3 tools/run_tests.py [-v] [suite ...]

Two kinds of check:

* Vector suites  - JSON tables in tests/vectors/, hand-computed from the specification.
* Property suites - invariants that a table cannot express, most importantly that a pivot
  is never used before its confirmation bar (the no-repaint rule) and that being above an
  EMA is not a reclaim.

Exit code 0 only if everything passes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reference_model as rm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
VECTORS = ROOT / "tests" / "vectors"
TOL = 1e-9

VERBOSE = False
PASSED = 0
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASSED
    if ok:
        PASSED += 1
        if VERBOSE:
            print(f"  pass  {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


def eq(name: str, got, want) -> None:
    if isinstance(want, bool) or want is None or isinstance(got, bool) or got is None:
        check(name, got == want, f"got {got!r}, want {want!r}")
    elif isinstance(want, (int, float)) and isinstance(got, (int, float)):
        check(name, abs(got - want) <= TOL, f"got {got!r}, want {want!r}")
    else:
        check(name, got == want, f"got {got!r}, want {want!r}")


def load(fname: str) -> dict:
    with open(VECTORS / fname, encoding="utf-8") as fh:
        return json.load(fh)


def candle(d: dict) -> rm.Candle:
    return rm.Candle(d["o"], d["h"], d["l"], d["c"])


# ---------------------------------------------------------------------------
# vector suites
# ---------------------------------------------------------------------------


def suite_ohlc() -> None:
    data = load("ohlc_engine.json")
    for case in data["cases"]:
        k = candle(case["candle"])
        m = rm.metrics(k)
        for key, want in case["expect"].items():
            eq(f"{case['id']}.{key}", m[key], want)
        # every candle, in every case, must satisfy the engine identities
        violations = rm.check_identities(k)
        check(f"{case['id']}.identities", not violations, "; ".join(violations))


def suite_identities_random() -> None:
    """The identities must hold for arbitrary well-formed candles, not just chosen ones."""
    import random

    rnd = random.Random(20260813)
    for i in range(2000):
        lo = rnd.uniform(1.0, 500.0)
        hi = lo + rnd.choice([0.0, 0.0001, rnd.uniform(0.01, 50.0)])
        o = rnd.uniform(lo, hi)
        c = rnd.uniform(lo, hi)
        k = rm.Candle(o, hi, lo, c)
        violations = rm.check_identities(k)
        if violations:
            check(f"random.identities[{i}]", False, f"{k} -> {violations}")
            return
    check("random.identities (2000 candles)", True)


def suite_wick_body() -> None:
    data = load("wick_body.json")
    for case in data["cases"]:
        k = candle(case["candle"])
        cl = rm.classes(k)
        for key, want in case["expect"].items():
            eq(f"{case['id']}.{key}", cl[key], want)
    # documented overlaps: the classes are not a partition
    for case in data["cases"]:
        cl = rm.classes(candle(case["candle"]))
        if cl["is_doji_body"]:
            check(f"{case['id']}.doji_implies_small", cl["is_small_body"],
                  "a doji body must also be a small body")
        if cl["is_marubozu"]:
            check(f"{case['id']}.marubozu_implies_large", cl["is_large_body"],
                  "a marubozu must also be a large body")


def suite_relationship() -> None:
    data = load("relationship.json")
    for case in data["cases"]:
        a, b = candle(case["a"]), candle(case["b"])
        r = rm.relationship(a, b, case.get("atr"))
        for key, want in case["expect"].items():
            eq(f"{case['id']}.{key}", r.get(key), want)

        # identity: body_inside(a, b) == body_engulfs(b, a)
        rev = rm.relationship(b, a)
        eq(f"{case['id']}.inside_engulf_identity", r["body_inside"], rev["body_engulfs"])

        # identity: close_above_prev_body_pct(a, b, 0.5) == close_above_prev_body_mid
        eq(f"{case['id']}.body_pct_half_identity",
           rm.close_above_prev_body_pct(a, b, 0.5), r["close_above_prev_body_mid"])


def suite_timeframe() -> None:
    data = load("timeframe.json")
    for case in data["class_cases"]:
        eq(f"tf_class({case['minutes']})", rm.tf_class(case["minutes"]), case["expect"])
    for case in data["allow_cases"]:
        eq(f"tf_allowed({case['minutes']},EXACT)",
           rm.tf_allowed(case["minutes"], case["tfs"], "EXACT"), case["exact"])
        eq(f"tf_allowed({case['minutes']},CLASS)",
           rm.tf_allowed(case["minutes"], case["tfs"], "CLASS"), case["class"])
    for case in data["override_cases"]:
        eq(f"tf_override({case['minutes']},{case['mode']},test={case['test_mode']})",
           rm.tf_allowed(case["minutes"], case["tfs"], case["mode"], case["test_mode"]),
           case["expect"])
    # a pattern listing all three of H1/H4/D1 must be allowed on all three - the owner's
    # explicit requirement, asserted directly rather than inferred from the table above
    for minutes in (60, 240, 1440):
        check(f"all_ideal_tfs_work({minutes})",
              rm.tf_allowed(minutes, "60,240,1440", "EXACT")
              and rm.tf_allowed(minutes, "60,240,1440", "CLASS"),
              "every listed ideal timeframe must work")
    # every class span is total and non-overlapping
    seen = set()
    for minutes in [0.1, 0.5] + list(range(1, 2000)) + [4320, 10079, 10080, 43199, 43200, 1e6]:
        cls = rm.tf_class(minutes)
        check(f"tf_class_total({minutes})", cls is not None, "unclassifiable timeframe")
        seen.add(cls)
    check("tf_class_covers_all", len(seen) == 9, f"classes reached: {sorted(seen)}")


def suite_validation() -> None:
    data = load("validation.json")
    for case in data["cases"]:
        res = rm.validate(rm.Factors(case["factors"]))
        for key, want in case["expect"].items():
            eq(f"{case['id']}.{key}", res[key], want)

    # VERY STRONG is unreachable without the confirmation factor. With the current factor
    # set this is implied by the arithmetic, since confirmation is never excluded; the
    # explicit ceiling in the engine is a guard for future band or weight changes.
    for name in rm.FACTOR_ORDER:
        factors = {f: "pass" for f in rm.FACTOR_ORDER}
        factors["confirmation"] = "fail"
        factors[name] = factors.get(name, "pass")
        res = rm.validate(rm.Factors(factors))
        check(f"unconfirmed_never_very_strong[{name}]", res["band"] != "VERY STRONG",
              f"unconfirmed pattern reached {res['band']}")

    # an excluded factor must never be counted as a pass or a fail
    base = {f: "fail" for f in rm.FACTOR_ORDER}
    r_all = rm.validate(rm.Factors(dict(base)))
    excl = dict(base)
    excl["volume"] = "excluded"
    r_excl = rm.validate(rm.Factors(excl))
    check("exclusion_lowers_max", r_excl["max_score"] == r_all["max_score"] - 1,
          f"{r_excl['max_score']} vs {r_all['max_score']}")
    check("exclusion_keeps_score", r_excl["score"] == r_all["score"],
          "excluding a factor must not change the score")


def suite_confirmation() -> None:
    data = load("confirmation.json")
    for case in data["cases"]:
        p = case["pending"]
        pending = rm.Pending(p["direction"], p["trigger"], p["invalidation"], p["bars"])
        res = rm.resolve(pending, case["closes"])
        for key, want in case["expect"].items():
            eq(f"{case['id']}.{key}", getattr(res, key), want)

    # terminal states never change, whatever happens afterwards
    pending = rm.Pending(1, 110.0, 100.0, 3)
    rm.resolve(pending, [99.0])
    before = pending.status
    rm.resolve(pending, [999.0, 999.0, 999.0])
    check("failed_is_terminal", pending.status == before == "FAILED",
          f"status became {pending.status}")


# ---------------------------------------------------------------------------
# property suites
# ---------------------------------------------------------------------------


def suite_rsi_no_divergence_in_trend() -> None:
    """A monotonically rising series has momentum, never a bullish divergence."""
    closes = [100.0 + i for i in range(120)]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    divs = rm.find_divergences(highs, lows, closes)
    check("rising_series_has_no_bull_div",
          not any(d.kind == "BULL" for d in divs),
          f"found {[(d.kind, d.second.bar) for d in divs]}")

    rsi = rm.rsi_wilder(closes)
    state = rm.rsi_state(rsi[100], rsi[99], False, False)
    check("rising_series_state_is_momentum_or_ob", state in ("BULL_MOM", "OVERBOUGHT"),
          f"state was {state}")


# A bullish-divergence fixture: pivot lows at bar 40 (steep decline) and bar 90 (shallow
# decline to a marginally lower price). Separation 50 bars, within CV-RSI-004/005.
ANCHORS_BULL_DIV = [(0, 100.0), (25, 130.0), (40, 60.0), (65, 100.0), (90, 59.0), (120, 90.0)]


def _zigzag(points: list[tuple[int, float]], length: int) -> list[float]:
    """Linearly interpolate a close series through (bar, price) anchors."""
    series = [0.0] * length
    for (b0, p0), (b1, p1) in zip(points, points[1:]):
        for i in range(b0, b1 + 1):
            t = (i - b0) / (b1 - b0)
            series[i] = p0 + t * (p1 - p0)
    last_bar, last_price = points[-1]
    for i in range(last_bar, length):
        series[i] = last_price
    return series


def suite_rsi_divergence_delay() -> None:
    """A bullish divergence must not be usable before its second pivot is confirmed.

    Series: a deep first low reached by a steep decline, a bounce, then a marginally lower
    second low reached far more slowly. The slower decline leaves RSI higher at the second
    low, which is the divergence. Pivot separation is 50 bars, inside the 5..60 window.
    """
    length = 160
    anchors = ANCHORS_BULL_DIV
    closes = _zigzag(anchors, length)
    highs = [c + 0.4 for c in closes]
    lows = [c - 0.4 for c in closes]

    divs = rm.find_divergences(highs, lows, closes)
    bull = [d for d in divs if d.kind == "BULL"]
    check("divergence_found", len(bull) >= 1, "no bullish divergence detected in fixture")
    if not bull:
        return

    d = bull[0]
    right = int(rm.DEFAULTS["pivot_right"])
    eq("div_second_pivot_confirmation_bar", d.second.confirmed_at, d.second.bar + right)
    eq("div_active_from_equals_confirmation", d.active_from, d.second.confirmed_at)
    check("div_price_lower_low", d.second.price < d.first.price,
          f"{d.second.price} !< {d.first.price}")

    rsi = rm.rsi_wilder(closes)
    check("div_rsi_higher_low", rsi[d.second.bar] > rsi[d.first.bar],
          f"rsi {rsi[d.second.bar]} !> {rsi[d.first.bar]}")

    # the no-repaint assertion: not active on the pivot bar, nor on any bar before
    # confirmation; active from the confirmation bar onward
    for bar in range(d.second.bar, d.second.confirmed_at):
        check(f"div_not_active_before_confirmation[{bar}]",
              not rm.divergence_active(divs, "BULL", bar),
              "divergence used before its pivot was confirmed")
    check("div_active_at_confirmation",
          rm.divergence_active(divs, "BULL", d.second.confirmed_at),
          "divergence should be active from the confirmation bar")

    # and it expires
    last = d.active_to
    check("div_active_at_window_end", rm.divergence_active(divs, "BULL", last))
    check("div_inactive_after_window",
          not rm.divergence_active(divs, "BULL", last + 1),
          "divergence must expire after its active window")

    # RSI state precedence: divergence outranks oversold
    eq("div_outranks_oversold", rm.rsi_state(25.0, 24.0, True, False), "BULL_DIV")
    eq("oversold_without_divergence", rm.rsi_state(25.0, 24.0, False, False), "OVERSOLD")
    eq("momentum_is_not_divergence", rm.rsi_state(60.0, 55.0, False, False), "BULL_MOM")


def suite_rsi_divergence_gap_limits() -> None:
    cfg_min = dict(rm.DEFAULTS, div_min_gap=51)
    cfg_max = dict(rm.DEFAULTS, div_max_gap=49)
    length = 160
    closes = _zigzag(ANCHORS_BULL_DIV, length)
    highs = [c + 0.4 for c in closes]
    lows = [c - 0.4 for c in closes]

    # the fixture's pivots are 50 bars apart, so raising the minimum above 50 or lowering the
    # maximum below 50 must reject the same divergence the default settings accept
    default_bull = [d for d in rm.find_divergences(highs, lows, closes) if d.kind == "BULL"]
    check("div_accepted_at_default_gap", bool(default_bull),
          "fixture should produce a divergence at the default separation limits")
    check("div_rejected_when_below_min_gap",
          not [d for d in rm.find_divergences(highs, lows, closes, cfg_min) if d.kind == "BULL"],
          "minimum pivot separation not enforced")
    check("div_rejected_when_above_max_gap",
          not [d for d in rm.find_divergences(highs, lows, closes, cfg_max) if d.kind == "BULL"],
          "maximum pivot separation not enforced")


def suite_ema_reclaim() -> None:
    """Being above an EMA is not a reclaim; a reclaim needs a crossing inside the window."""
    window = int(rm.DEFAULTS["reclaim_window"])

    # 80 bars of a steady uptrend: price is above the EMA throughout, and after the initial
    # crossing there is no reclaim anywhere.
    closes = [100.0 + i * 0.5 for i in range(80)]
    e = rm.ema(closes, 20)
    rec = rm.reclaim_series(closes, e, window)
    late = [i for i in range(40, 80) if rec[i]]
    check("long_uptrend_has_no_late_reclaim", not late,
          f"reclaim reported at bars {late[:5]} while merely above the EMA")
    check("long_uptrend_is_above_ema",
          all(closes[i] > e[i] for i in range(40, 80) if e[i] is not None),
          "fixture should keep price above the EMA")

    # a genuine crossing: 40 flat-ish bars, a dip below, then a close back above
    base = [100.0] * 40 + [99.0 - i * 0.4 for i in range(15)]
    base += [base[-1] + 3.0 * (i + 1) for i in range(6)]
    e2 = rm.ema(base, 20)
    rec2 = rm.reclaim_series(base, e2, window)
    cross_bars = [i for i in range(1, len(base))
                  if e2[i] is not None and e2[i - 1] is not None
                  and base[i] > e2[i] and base[i - 1] <= e2[i - 1]]
    check("crossing_exists", bool(cross_bars), "fixture produced no crossover")
    if cross_bars:
        x = cross_bars[0]
        check("reclaim_true_on_crossing_bar", rec2[x], "the crossing bar must be a reclaim")
        for k in range(1, window + 1):
            if x + k < len(base) and base[x + k] > (e2[x + k] or 0):
                check(f"reclaim_true_within_window[+{k}]", rec2[x + k],
                      "still inside the reclaim window")
        far = x + window + 1
        if far < len(base) and e2[far] is not None and base[far] > e2[far]:
            check("reclaim_false_after_window", not rec2[far],
                  "the reclaim window must expire")


def suite_volume() -> None:
    eq("vol_high_boundary", rm.volume_state(1.50, 1.0)[0], "HIGH")
    eq("vol_above_boundary", rm.volume_state(1.20, 1.0)[0], "ABOVE")
    eq("vol_normal", rm.volume_state(1.00, 1.0)[0], "NORMAL")
    eq("vol_below_boundary", rm.volume_state(0.80, 1.0)[0], "BELOW")
    eq("vol_zero_bar", rm.volume_state(0.0, 1.0)[0], "BELOW")
    eq("vol_no_series", rm.volume_state(None, None)[0], "UNAVAILABLE")
    eq("vol_zero_average_no_division", rm.volume_state(5.0, 0.0)[0], "UNAVAILABLE")


def suite_degenerate_gating() -> None:
    """A zero-range candle must never satisfy a shape rule that implies a real candle."""
    k = rm.Candle(50.0, 50.0, 50.0, 50.0)
    m = rm.metrics(k)
    check("degenerate_not_measurable", not m["is_measurable"])
    check("degenerate_close_pos_is_half", abs(m["close_pos"] - 0.5) < TOL)
    cl = rm.classes(k)
    check("degenerate_not_marubozu", not cl["is_marubozu"],
          "a zero-range candle must not classify as a marubozu")
    check("degenerate_no_long_wick_r",
          not cl["is_long_upper_wick_r"] and not cl["is_long_lower_wick_r"])
    check("degenerate_is_doji_body", cl["is_doji_body"],
          "body_pct is defined as 0 for a degenerate candle")


SUITES = {
    "ohlc": suite_ohlc,
    "identities": suite_identities_random,
    "wick_body": suite_wick_body,
    "relationship": suite_relationship,
    "timeframe": suite_timeframe,
    "validation": suite_validation,
    "confirmation": suite_confirmation,
    "rsi_trend": suite_rsi_no_divergence_in_trend,
    "rsi_divergence": suite_rsi_divergence_delay,
    "rsi_gaps": suite_rsi_divergence_gap_limits,
    "ema_reclaim": suite_ema_reclaim,
    "volume": suite_volume,
    "degenerate": suite_degenerate_gating,
}


def main(argv: list[str]) -> int:
    global VERBOSE
    args = [a for a in argv if a not in ("-v", "--verbose")]
    VERBOSE = len(args) != len(argv)
    wanted = args or list(SUITES)

    unknown = [s for s in wanted if s not in SUITES]
    if unknown:
        print(f"unknown suite(s): {', '.join(unknown)}")
        print(f"available: {', '.join(SUITES)}")
        return 2

    print("CANDLESTICK MASTER - engine reference tests")
    print("=" * 60)
    for name in wanted:
        print(f"[{name}]")
        SUITES[name]()

    print("=" * 60)
    if FAILURES:
        print(f"FAILED  {len(FAILURES)} check(s), {PASSED} passed")
        for f in FAILURES[:20]:
            print(f"  - {f}")
        return 1
    print(f"OK  {PASSED} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
