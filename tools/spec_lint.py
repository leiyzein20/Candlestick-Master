#!/usr/bin/env python3
"""Consistency checks for the Candlestick Master specification set.

Enforces the invariants in PATTERN_REGISTRY.md section 4 and patterns/INTAKE.md section 4,
so that a pattern cannot be half-filed, mis-routed, duplicated, or quietly stripped of a
mandatory field.

Usage:
    python3 tools/spec_lint.py [-v]

Exit code 0 only if every check passes. Runs cleanly with zero patterns, which is the
current state.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "patterns"
REGISTRY = ROOT / "PATTERN_REGISTRY.md"
CONFLICTS = ROOT / "CONFLICT_LOG.md"
CONVERSIONS = ROOT / "docs" / "DEFINITION_CONVERSIONS.md"
GATE = ROOT / "IMPLEMENTATION_GATE.md"

# Files in patterns/ that are process documents, not pattern specifications.
NON_PATTERN_FILES = {"README.md", "SPEC_TEMPLATE.md", "INTAKE.md", "CLASSIFICATION.md"}

CANONICAL_TF = {
    "1m", "2m", "3m", "5m", "10m", "15m", "30m", "45m",
    "1H", "2H", "3H", "4H", "6H", "8H", "12H", "1D", "1W", "1M",
}

RESERVED_ABBR = {"HAM", "BEC", "PL", "MS", "MDS", "ES", "EDS", "TWS", "TBC", "THRU"}

DIRECTIONS = {"Bullish", "Bearish", "Neutral"}
CATEGORIES = {"Reversal", "Continuation", "Exhaustion", "Neutral", "Gap"}

# patterns/CLASSIFICATION.md section 2, complete over all 15 combinations.
ROUTING = {
    ("Bullish", "Reversal"): ("bullish_reversal", ""),
    ("Bullish", "Continuation"): ("continuation", "bull_"),
    ("Bullish", "Exhaustion"): ("exhaustion", "bull_"),
    ("Bullish", "Gap"): ("gap_patterns", "bull_"),
    ("Bullish", "Neutral"): ("neutral", "bull_"),
    ("Bearish", "Reversal"): ("bearish_reversal", ""),
    ("Bearish", "Continuation"): ("continuation", "bear_"),
    ("Bearish", "Exhaustion"): ("exhaustion", "bear_"),
    ("Bearish", "Gap"): ("gap_patterns", "bear_"),
    ("Bearish", "Neutral"): ("neutral", "bear_"),
    ("Neutral", "Reversal"): ("neutral", "neut_"),
    ("Neutral", "Continuation"): ("continuation", "neut_"),
    ("Neutral", "Exhaustion"): ("exhaustion", "neut_"),
    ("Neutral", "Gap"): ("gap_patterns", "neut_"),
    ("Neutral", "Neutral"): ("neutral", "neut_"),
}

MANDATORY_SECTIONS = [
    (1, "As Supplied"),
    (2, "Identity"),
    (3, "Classification record"),
    (4, "Structure"),
    (5, "Ideal timeframes"),
    (6, "Required trend"),
    (7, "OHLC rules"),
    (8, "Body rules"),
    (9, "Wick rules"),
    (10, "Candle-to-candle relationships"),
    (11, "50% and penetration rules"),
    (12, "Gap requirements"),
    (13, "Context requirements"),
    (14, "Confirmation"),
    (15, "Failure condition"),
    (16, "Supplied classifications"),
    (17, "Ambiguity register"),
    (18, "Audit flags"),
    (19, "Test plan"),
    (20, "Implementation notes"),
]

VALID_STATUS = {"RECEIVED", "SPECIFIED", "BLOCKED", "TESTS-READY", "IMPLEMENTED",
                "VERIFIED", "WITHDRAWN"}

VERBOSE = False
ERRORS: list[str] = []
WARNINGS: list[str] = []
CHECKS = 0


def fail(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def ok(msg: str) -> None:
    global CHECKS
    CHECKS += 1
    if VERBOSE:
        print(f"  pass  {msg}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_fences(text: str) -> str:
    """Remove fenced code blocks.

    Needed because CONFLICT_LOG.md documents its own entry format inside a fence; a naive
    scan would count that example as a real entry.
    """
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


# ---------------------------------------------------------------------------
# minimal front-matter parser (no third-party dependency)
# ---------------------------------------------------------------------------


def parse_front_matter(text: str) -> dict:
    """Read the first ```yaml fenced block as simple key: value pairs.

    Supports scalars, quoted strings, inline [] lists, and null. Deliberately small: the
    template only uses those forms, and a real YAML dependency would be a new install
    requirement for a repo that otherwise needs nothing.
    """
    match = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
    if not match:
        return {}
    out: dict = {}
    for line in match.group(1).splitlines():
        line = line.split("#", 1)[0].rstrip()
        if not line.strip() or ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key, raw = key.strip(), raw.strip()
        if not key or key != key.lower().replace(" ", "_"):
            continue
        out[key] = _scalar(raw)
    return out


def _scalar(raw: str):
    if raw == "" or raw.lower() in {"null", "none", "~"}:
        return None
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_scalar(p.strip()) for p in inner.split(",")]
    if raw.startswith(('"', "'")) and raw.endswith(('"', "'")) and len(raw) >= 2:
        return raw[1:-1]
    if raw.lower() in {"true", "false"}:
        return raw.lower() == "true"
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------


def parse_registry() -> list[dict]:
    text = read(REGISTRY)
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 11:
            continue
        if not re.fullmatch(r"CM-\d{3}", cells[0]):
            continue
        rows.append({
            "id": cells[0], "abbr": cells[1], "name": cells[2], "dir": cells[3],
            "primary": cells[4], "secondary": cells[5], "candles": cells[6],
            "timeframes": cells[7], "file": cells[8], "status": cells[9],
            "flags": cells[10],
        })
    return rows


def pattern_files() -> list[Path]:
    files = []
    for path in sorted(PATTERNS.rglob("*.md")):
        if path.name in NON_PATTERN_FILES:
            continue
        files.append(path)
    return files


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------


def check_ids_exist() -> None:
    """Every CV- and SI- id referenced anywhere must be defined in its registry."""
    conv_text = read(CONVERSIONS)
    defined_cv = set(re.findall(r"CV-[A-Z]+-\d{3}", conv_text))
    conflict_text = read(CONFLICTS)
    defined_si = set(re.findall(r"\bSI-\d{2}\b", conflict_text))

    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = read(md)
        for cv in sorted(set(re.findall(r"CV-[A-Z]+-\d{3}", text))):
            if cv not in defined_cv:
                fail(f"{md.relative_to(ROOT)}: cites {cv}, which is not defined in "
                     f"docs/DEFINITION_CONVERSIONS.md")
        if md != CONFLICTS:
            for si in sorted(set(re.findall(r"\bSI-\d{2}\b", text))):
                if si not in defined_si:
                    fail(f"{md.relative_to(ROOT)}: cites {si}, which is not a standing item "
                         f"in CONFLICT_LOG.md")
    ok(f"all CV- ids resolve ({len(defined_cv)} defined)")
    ok(f"all SI- ids resolve ({len(defined_si)} defined)")


def check_conversion_count() -> None:
    text = read(CONVERSIONS)
    defined = set(re.findall(r"CV-[A-Z]+-\d{3}", text))
    claimed = re.search(r"Total conversions:\s*\*\*(\d+)\*\*", text)
    if not claimed:
        fail("docs/DEFINITION_CONVERSIONS.md: no 'Total conversions' line found")
        return
    if int(claimed.group(1)) != len(defined):
        fail(f"docs/DEFINITION_CONVERSIONS.md: claims {claimed.group(1)} conversions but "
             f"defines {len(defined)}")
    else:
        ok(f"conversion count matches ({len(defined)})")


def check_gate() -> None:
    text = read(GATE)
    closed = "GATE: CLOSED" in text
    pine_files = [p for p in (ROOT / "pine").rglob("*.pine")]
    if closed and pine_files:
        fail("IMPLEMENTATION_GATE.md says CLOSED but pine/ contains "
             f"{len(pine_files)} .pine file(s): {[p.name for p in pine_files]}")
    else:
        state = "CLOSED" if closed else "OPEN"
        ok(f"implementation gate {state}, {len(pine_files)} .pine file(s)")


def check_conflict_log_format() -> None:
    text = strip_fences(read(CONFLICTS))
    entries = re.findall(r"^### ((?:CF|AM|MS|AF)-\d{4}) — (.+)$", text, re.MULTILINE)
    for entry_id, _title in entries:
        block = text.split(f"### {entry_id}", 1)[1]
        block = block.split("\n### ", 1)[0]
        for field in ("**Pattern(s):**", "**Type:**", "**Severity:**", "**Status:**"):
            if field not in block:
                fail(f"CONFLICT_LOG.md {entry_id}: missing {field}")
    ok(f"conflict log entries well formed ({len(entries)} entries)")
    return


def blocking_flags() -> set[str]:
    """Flag ids whose entry is marked BLOCKING."""
    text = strip_fences(read(CONFLICTS))
    out = set()
    for entry_id in re.findall(r"^### ((?:CF|AM|MS|AF)-\d{4})", text, re.MULTILINE):
        block = text.split(f"### {entry_id}", 1)[1].split("\n### ", 1)[0]
        if "BLOCKING" in block:
            out.add(entry_id)
    return out


def known_flags() -> set[str]:
    return set(re.findall(r"^### ((?:CF|AM|MS|AF)-\d{4})", strip_fences(read(CONFLICTS)),
                          re.MULTILINE))


def check_patterns(rows: list[dict]) -> None:
    files = pattern_files()
    by_id = {r["id"]: r for r in rows}
    flags_defined = known_flags()
    flags_blocking = blocking_flags()

    if len(by_id) != len(rows):
        fail("PATTERN_REGISTRY.md: duplicate registry ids")

    # every registry row must have its file
    for row in rows:
        path = ROOT / row["file"]
        if not path.exists():
            fail(f"{row['id']}: registry names {row['file']}, which does not exist")

    seen_abbr: dict[str, str] = {}
    file_ids: set[str] = set()

    for path in files:
        rel = path.relative_to(ROOT)
        text = read(path)
        fm = parse_front_matter(text)

        if not fm:
            fail(f"{rel}: no ```yaml front-matter block found")
            continue

        pid = fm.get("id")
        if not isinstance(pid, str) or not re.fullmatch(r"CM-\d{3}", pid):
            fail(f"{rel}: front-matter id {pid!r} is not of the form CM-000")
            continue
        file_ids.add(pid)

        row = by_id.get(pid)
        if row is None:
            fail(f"{rel}: {pid} is not listed in PATTERN_REGISTRY.md")

        # mandatory sections
        for num, title in MANDATORY_SECTIONS:
            if not re.search(rf"^##\s*{num}\.\s", text, re.MULTILINE):
                fail(f"{rel}: missing mandatory section {num} ({title})")

        # direction / category vocabulary
        direction = fm.get("direction")
        primary = fm.get("primary_category")
        if direction not in DIRECTIONS:
            fail(f"{rel}: direction {direction!r} is not one of {sorted(DIRECTIONS)}")
        if primary not in CATEGORIES:
            fail(f"{rel}: primary_category {primary!r} is not one of {sorted(CATEGORIES)}")

        # routing
        if direction in DIRECTIONS and primary in CATEGORIES:
            want_dir, want_prefix = ROUTING[(direction, primary)]
            if path.parent.name != want_dir:
                fail(f"{rel}: {direction}/{primary} must live in patterns/{want_dir}/ "
                     f"(CLASSIFICATION.md section 2)")
            if want_prefix and not path.name.startswith(want_prefix):
                fail(f"{rel}: {direction}/{primary} filename must start with "
                     f"{want_prefix!r} in a shared directory")

        # abbreviation
        abbr = fm.get("abbr")
        if not isinstance(abbr, str) or not re.fullmatch(r"[A-Z]{2,4}", abbr):
            fail(f"{rel}: abbr {abbr!r} must be 2-4 uppercase letters")
        else:
            if abbr in seen_abbr:
                fail(f"{rel}: abbreviation {abbr} already used by {seen_abbr[abbr]} — "
                     f"raise a CF- entry, do not rename (PATTERN_REGISTRY.md section 3)")
            seen_abbr[abbr] = str(rel)

        # timeframes
        tfs = fm.get("timeframes")
        if tfs in (None, [], ""):
            warn(f"{rel}: no ideal timeframes supplied — expects an MS- entry, and the "
                 f"pattern is not timeframe-gated until supplied")
        elif isinstance(tfs, list):
            for token in tfs:
                if token not in CANONICAL_TF:
                    fail(f"{rel}: timeframe {token!r} is not a canonical token "
                         f"(MASTER_SPECIFICATION.md section 6)")

        # candle count vs the section 4 table
        count = fm.get("candle_count")
        if not isinstance(count, int) or count < 1:
            fail(f"{rel}: candle_count {count!r} must be an integer >= 1")

        # status
        status = fm.get("status")
        if status not in VALID_STATUS:
            fail(f"{rel}: status {status!r} is not one of {sorted(VALID_STATUS)}")

        # flags must exist, and a blocking flag forbids implementation
        pattern_flags = fm.get("flags") or []
        if isinstance(pattern_flags, list):
            for flag in pattern_flags:
                if flag not in flags_defined:
                    fail(f"{rel}: flag {flag} is not an entry in CONFLICT_LOG.md")
                elif flag in flags_blocking and status in {"IMPLEMENTED", "VERIFIED"}:
                    fail(f"{rel}: status {status} while carrying BLOCKING flag {flag}")

        # conversions cited must exist
        for cv in fm.get("conversions") or []:
            if not re.fullmatch(r"CV-[A-Z]+-\d{3}", str(cv)):
                fail(f"{rel}: conversion id {cv!r} is malformed")

        # registry agreement
        if row:
            for key, fm_key in (("abbr", "abbr"), ("dir", "direction"),
                                ("primary", "primary_category")):
                if row[key] != fm.get(fm_key):
                    fail(f"{rel}: registry {key}={row[key]!r} disagrees with front-matter "
                         f"{fm_key}={fm.get(fm_key)!r}")
            if row["file"] != str(rel):
                fail(f"{rel}: registry file path is {row['file']!r}")

        # the As Supplied block must not be an unfilled placeholder
        if "<paste the owner's specification here" in text:
            fail(f"{rel}: section 1 (As Supplied) still holds the template placeholder")

    for pid in by_id:
        if pid not in file_ids:
            fail(f"PATTERN_REGISTRY.md: {pid} has no pattern file carrying that id")

    # every conflict entry naming a pattern must be listed in that pattern's flags
    text = strip_fences(read(CONFLICTS))
    for entry_id in known_flags():
        block = text.split(f"### {entry_id}", 1)[1].split("\n### ", 1)[0]
        for pid in re.findall(r"CM-\d{3}", block):
            path = ROOT / by_id[pid]["file"] if pid in by_id else None
            if path is None or not path.exists():
                fail(f"CONFLICT_LOG.md {entry_id}: names {pid}, which has no registry row")
                continue
            fm = parse_front_matter(read(path))
            if entry_id not in (fm.get("flags") or []):
                fail(f"{path.relative_to(ROOT)}: CONFLICT_LOG.md {entry_id} names this "
                     f"pattern but it is not listed in its flags")

    ok(f"pattern files consistent ({len(files)} files, {len(rows)} registry rows)")


def check_registry_counters(rows: list[dict]) -> None:
    text = read(REGISTRY)
    match = re.search(r"\|\s*Total patterns\s*\|\s*(\d+)\s*\|", text)
    if not match:
        fail("PATTERN_REGISTRY.md: no 'Total patterns' counter found")
        return
    if int(match.group(1)) != len(rows):
        fail(f"PATTERN_REGISTRY.md: counter says {match.group(1)} patterns, table has "
             f"{len(rows)}")
    else:
        ok(f"registry counters agree with the table ({len(rows)})")


def check_reserved_abbr(rows: list[dict]) -> None:
    for row in rows:
        if row["abbr"] in RESERVED_ABBR:
            ok(f"{row['id']} uses reserved abbreviation {row['abbr']} (expected once its "
               f"specification arrives)")
    ok(f"{len(RESERVED_ABBR)} reserved abbreviations protected")


def check_category_indexes() -> None:
    for sub in ("bullish_reversal", "bearish_reversal", "continuation", "exhaustion",
                "neutral", "gap_patterns"):
        readme = PATTERNS / sub / "README.md"
        if not readme.exists():
            fail(f"patterns/{sub}/README.md is missing")
    ok("every category directory has a README index")


def main(argv: list[str]) -> int:
    global VERBOSE
    VERBOSE = any(a in ("-v", "--verbose") for a in argv)

    print("CANDLESTICK MASTER - specification lint")
    print("=" * 60)

    rows = parse_registry()

    check_ids_exist()
    check_conversion_count()
    check_gate()
    check_conflict_log_format()
    check_category_indexes()
    check_registry_counters(rows)
    check_reserved_abbr(rows)
    check_patterns(rows)

    print("=" * 60)
    for w in WARNINGS:
        print(f"WARN  {w}")
    if ERRORS:
        print(f"FAILED  {len(ERRORS)} error(s)")
        for e in ERRORS:
            print(f"  - {e}")
        return 1
    print(f"OK  {CHECKS} checks passed, {len(rows)} pattern(s) registered, "
          f"{len(WARNINGS)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
