#!/usr/bin/env python3
"""Structural sanity checks for the Candlestick Master Pine source.

Pine Script cannot be compiled outside TradingView, so this checks the things that
are mechanically verifiable: balanced delimiters, registry/detector alignment,
indentation, and the abbreviation codes staying unique.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PINE = Path(__file__).resolve().parents[1] / "pine" / "candlestick_master_45.pine"

errors: list[str] = []
warnings: list[str] = []


def strip_comment(line: str) -> str:
    out, in_str = [], False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            in_str = not in_str
        if not in_str and ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def main() -> int:
    if not PINE.exists():
        print(f"missing {PINE}")
        return 1

    raw = PINE.read_text(encoding="utf-8")
    lines = raw.splitlines()

    if not lines[0].startswith("//@version=6"):
        errors.append("line 1 must be //@version=6")

    # 1. delimiters and quotes; parentheses are tracked across continuation lines
    balance = 0
    opened_at = 0
    for n, line in enumerate(lines, 1):
        if "\t" in line:
            errors.append(f"line {n}: tab character (Pine requires spaces)")
        code = strip_comment(line)
        if code.count('"') % 2:
            errors.append(f"line {n}: odd number of double quotes")
        if balance == 0 and code.strip():
            opened_at = n
        balance += code.count("(") - code.count(")")
        if balance < 0:
            errors.append(f"line {n}: closing parenthesis without a matching opener")
            balance = 0
    if balance != 0:
        errors.append(f"unclosed parenthesis in the statement starting at line {opened_at}")

    # 2. indentation of block bodies must be a multiple of 4;
    #    continuation lines must NOT be a multiple of 4
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("//"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent and indent % 4 != 0 and not re.match(r"^\s+\"", line):
            warnings.append(f"line {n}: indent {indent} — only valid as a continuation line")

    # 3. registry
    codes = re.findall(r'^addPat\("([A-Z0-9]+)"\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d)\s*,\s*(-?\d)\s*,\s*(\d)\s*,\s*(\d+)\s*,\s*"([^"]*)"\s*,\s*"([^"]+)"\s*,\s*(\d)\s*,',
                       raw, re.M)
    if len(codes) != 45:
        errors.append(f"expected 45 addPat() entries, found {len(codes)}")

    seen_codes: dict[str, int] = {}
    seen_nums: dict[int, str] = {}
    ladder = {"M1", "M2", "M3", "M5", "M10", "M15", "M30", "M45",
              "H1", "H2", "H3", "H4", "H6", "H8", "H12", "D1", "W1", "MN1"}
    roles = {"Reversal", "Continuation", "Exhaustion", "Indecision"}

    for code, name, num, cat, dr, prio, rel, tf, role, ln in codes:
        num_i = int(num)
        if code in seen_codes:
            errors.append(f"duplicate abbreviation {code}")
        seen_codes[code] = num_i
        if num_i in seen_nums:
            errors.append(f"duplicate pattern number {num_i}")
        seen_nums[num_i] = code
        if not 1 <= num_i <= 45:
            errors.append(f"{code}: number {num_i} out of range")
        if int(cat) not in (1, 2, 3):
            errors.append(f"{code}: bad category {cat}")
        if int(dr) not in (-1, 0, 1):
            errors.append(f"{code}: bad direction {dr}")
        if int(prio) not in (1, 2, 3):
            errors.append(f"{code}: bad priority {prio}")
        if not 40 <= int(rel) <= 95:
            warnings.append(f"{code}: reliability {rel}% looks implausible")
        if role not in roles:
            errors.append(f"{code}: unknown role {role!r}")
        if not 1 <= int(ln) <= 5:
            errors.append(f"{code}: candle count {ln} out of range")
        if not (tf.startswith("|") and tf.endswith("|")):
            errors.append(f"{code}: ideal time frames must be pipe-delimited, got {tf!r}")
        else:
            for part in [p for p in tf.split("|") if p]:
                if part not in ladder:
                    errors.append(f"{code}: {part!r} is not on the time frame ladder")
        # category must match the candle count
        cat_i, ln_i = int(cat), int(ln)
        if cat_i == 1 and ln_i != 1:
            errors.append(f"{code}: single-candle category but {ln_i} candles")
        if cat_i == 2 and ln_i != 2:
            errors.append(f"{code}: double-candle category but {ln_i} candles")
        if cat_i == 3 and ln_i < 3:
            errors.append(f"{code}: multi-candle category but only {ln_i} candles")

    expected_cat = {1: 12, 2: 13, 3: 20}
    actual_cat: dict[int, int] = {}
    for _c, _n, _num, cat, *_ in codes:
        actual_cat[int(cat)] = actual_cat.get(int(cat), 0) + 1
    for cat, want in expected_cat.items():
        got = actual_cat.get(cat, 0)
        if got != want:
            errors.append(f"category {cat}: expected {want} patterns, found {got}")

    # 4. detectors <-> registry alignment
    defined = set(re.findall(r"^bool (p\d{2}[bs]?) =", raw, re.M))
    checked = re.findall(r"^f_check\((\d+),\s*(p\d{2}[bs]?),", raw, re.M)
    checked_vars = {v for _i, v in checked}
    for miss in sorted(defined - checked_vars):
        errors.append(f"detector {miss} is defined but never registered with f_check")
    for miss in sorted(checked_vars - defined):
        errors.append(f"f_check references undefined detector {miss}")

    idx_used = sorted({int(i) for i, _v in checked})
    if idx_used != list(range(45)):
        missing = sorted(set(range(45)) - set(idx_used))
        extra = sorted(set(idx_used) - set(range(45)))
        errors.append(f"registry indices not fully covered — missing {missing}, unexpected {extra}")

    # the registry index must be the pattern number minus one
    for i, var in checked:
        want = int(re.search(r"p(\d{2})", var).group(1)) - 1
        if int(i) != want:
            errors.append(f"f_check index {i} does not match detector {var} (expected {want})")

    # 5. every input group is referenced
    for grp in re.findall(r"^string (G_[A-Z]+) =", raw, re.M):
        if len(re.findall(rf"\b{grp}\b", raw)) < 2:
            warnings.append(f"input group {grp} declared but never used")

    print(f"checked {len(lines)} lines, {len(codes)} patterns, {len(checked)} detectors")
    for w in warnings:
        print(f"  warn  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    if errors:
        print(f"\n{len(errors)} error(s)")
        return 1
    print("\nstructure OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
