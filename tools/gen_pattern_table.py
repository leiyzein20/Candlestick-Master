#!/usr/bin/env python3
"""Generate docs/PATTERNS.md from the addPat() registry in the Pine source.

The table is derived rather than maintained by hand so the documentation can never drift
away from what the indicator actually does.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINE = ROOT / "pine" / "candlestick_master_45.pine"
OUT = ROOT / "docs" / "PATTERNS.md"

ENTRY = re.compile(
    r'^addPat\("(?P<code>[A-Z0-9]+)"\s*,\s*"(?P<name>[^"]+)"\s*,\s*(?P<num>\d+)\s*,\s*'
    r'(?P<cat>\d)\s*,\s*(?P<dir>-?\d)\s*,\s*(?P<prio>\d)\s*,\s*(?P<rel>\d+)\s*,\s*'
    r'"(?P<tf>[^"]*)"\s*,\s*"(?P<role>[^"]+)"\s*,\s*(?P<len>\d)\s*,\s*\n\s*"(?P<what>[^"]+)"',
    re.M,
)

CAT = {1: "Single Candle", 2: "Double Candle", 3: "Triple & Multi"}
DIR = {1: "Bullish", -1: "Bearish", 0: "Dual / Neutral"}
PRIO = {1: "Must", 2: "Important", 3: "Rare"}


def main() -> int:
    raw = PINE.read_text(encoding="utf-8")
    rows = [m.groupdict() for m in ENTRY.finditer(raw)]
    if len(rows) != 45:
        print(f"expected 45 registry entries, parsed {len(rows)}")
        return 1
    rows.sort(key=lambda r: int(r["num"]))

    out: list[str] = []
    out.append("# The 45 Patterns\n")
    out.append(
        "Generated from the `addPat()` registry in "
        "[`pine/candlestick_master_45.pine`](../pine/candlestick_master_45.pine) by "
        "`tools/gen_pattern_table.py`. Do not edit by hand — edit the registry and "
        "regenerate.\n"
    )
    out.append(
        "`Ideal TF` is the gate: with the default strict setting the pattern only ever "
        "draws when your chart is on one of those time frames.\n"
    )

    for cat in (1, 2, 3):
        group = [r for r in rows if int(r["cat"]) == cat]
        out.append(f"\n## {CAT[cat]} ({len(group)})\n")
        out.append("| # | Code | Pattern | Direction | Role | Priority | Rel. | Candles | Ideal TF |")
        out.append("| --: | :-- | :-- | :-- | :-- | :-- | --: | --: | :-- |")
        for r in group:
            tf = r["tf"].strip("|").replace("|", " · ")
            out.append(
                f"| {int(r['num']):02d} | `{r['code']}` | {r['name']} | {DIR[int(r['dir'])]} "
                f"| {r['role']} | {PRIO[int(r['prio'])]} | {r['rel']}% | {r['len']} | {tf} |"
            )

    out.append("\n## Which patterns are armed on which time frame\n")
    ladder = ["M1", "M2", "M3", "M5", "M10", "M15", "M30", "M45",
              "H1", "H2", "H3", "H4", "H6", "H8", "H12", "D1", "W1", "MN1"]
    out.append("| Chart TF | Patterns armed (strict mode) |")
    out.append("| :-- | :-- |")
    for tf in ladder:
        armed = [r["code"] for r in rows if f"|{tf}|" in r["tf"]]
        cell = ", ".join(f"`{c}`" for c in armed) if armed else "_none — the chart stays empty_"
        out.append(f"| {tf} | {cell} |")

    out.append(
        "\nAn empty row is not a bug. It is the whole point: there is no candlestick "
        "pattern in this catalogue that a professional would trade off an M2 chart, so an "
        "M2 chart shows nothing. Switch the time frame gating to `Ideal ± 1 step` or `Off` "
        "if you want to study them anyway.\n"
    )

    out.append("\n## Descriptions\n")
    for r in rows:
        tf = r["tf"].strip("|").replace("|", " · ")
        out.append(f"**{int(r['num']):02d} · `{r['code']}` — {r['name']}** ({tf})  ")
        out.append(f"{r['what']}\n")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(rows)} patterns")
    return 0


if __name__ == "__main__":
    sys.exit(main())
