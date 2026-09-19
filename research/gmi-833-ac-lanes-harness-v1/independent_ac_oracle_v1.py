#!/usr/bin/env python3
"""Route B - independent AC oracle (issue #833, AC01/AC03/AC04/AC06).

Imports nothing from `ac_lanes_harness_v1.py` and uses **no regular
expressions**: markdown tables are split by index, lane headings are found by
prefix, and the four-digit year test is a digit scan.  The row strings are
re-read from `FREEZE_V1.md`, not copied from route A, so a corrupted row
constant in route A cannot be reproduced here by construction.

stdlib only; python3.8-compatible.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LIT = ROOT / "research" / "gmi-833-tranche-ab-ac-lit"
STOP = set(["the", "a", "of", "and", "or", "in", "to", "for", "with", "sense", "exact"])


class OracleError(RuntimeError):
    pass


def rows_from_freeze() -> Dict[str, str]:
    """Recover the verbatim AC rows from the pre-implementation freeze."""
    text = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    block = text.split("Verbatim from comment 5684607872 under the anchor above:", 1)[1]
    block = block.split("**No neighboring row is earned here.**", 1)[0]
    out = []
    for line in block.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            out.append(stripped)
    if len(out) != 5:
        raise OracleError("freeze does not quote exactly five AC rows: %d" % len(out))
    keys = ["AC01", "AC03", "AC04", "AC06", "AC07"]
    return dict(zip(keys, out))


def norm(text: str) -> str:
    buf = []
    for ch in text.lower():
        if ch in "*`":
            continue
        if ch in "-/,–":
            buf.append(" ")
        else:
            buf.append(ch)
    return " ".join("".join(buf).split())


def drop_parens(text: str) -> str:
    out = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth:
                depth -= 1
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def tokens(text: str) -> Set[str]:
    return set(w for w in norm(drop_parens(text)).split()
               if w not in STOP and len(w) > 2)


def split_terms(cell: str) -> List[str]:
    body = drop_parens(cell)
    parts = [p.strip() for p in body.split(";") if p.strip()]
    if len(parts) == 1 and "," in parts[0]:
        parts = [p.strip() for p in parts[0].split(",") if p.strip()]
    if len(parts) == 1 and "/" in parts[0]:
        parts = [p.strip() for p in parts[0].split("/") if p.strip()]
    return parts


def has_year(cell: str) -> bool:
    for i in range(len(cell) - 3):
        chunk = cell[i:i + 4]
        if not chunk.isdigit():
            continue
        if i > 0 and cell[i - 1].isdigit():
            continue
        if i + 4 < len(cell) and cell[i + 4].isdigit():
            continue
        year = int(chunk)
        if 1800 <= year <= 2029:
            return True
    return False


def table_cells(line: str) -> Optional[List[str]]:
    if not line.startswith("| "):
        return None
    body = line.strip()
    if not body.endswith("|"):
        return None
    cells = [c.strip() for c in body[1:-1].split("|")]
    return cells


def crosswalk() -> List[List[str]]:
    # AMENDMENT_01 (2026-09-19): route B reads the crosswalk at the blob sha
    # written in this package's FREEZE_V1.md addendum pin (independently of
    # route A, which parses MANIFEST_V1.json); unreachable => distinct failure.
    import hashlib
    import subprocess
    freeze = (HERE / "AC_CROSSWALK_ADDENDUM_V1.md").read_text(encoding="utf-8")
    start = freeze.index("blob `") + len("blob `")
    sha = freeze[start:start + 40]
    if len(sha) != 40 or set(sha) - set("0123456789abcdef"):
        raise SystemExit("PINNED_PARENT_PIN_UNREADABLE (route B)")
    proc = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-p", sha], capture_output=True)
    if proc.returncode != 0:
        raise SystemExit("PINNED_PARENT_UNREACHABLE (route B): %s" % sha)
    data = proc.stdout
    if hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() != sha:
        raise SystemExit("PINNED_PARENT_MISMATCH (route B): %s" % sha)
    text = data.decode("utf-8")
    out = []
    for line in text.split("\n"):
        cells = table_cells(line)
        if cells is None or len(cells) != 9:
            continue
        if not cells[0].isdigit():
            continue
        out.append(cells)
    return out


def lanes() -> Tuple[List[str], Dict[str, int]]:
    text = (LIT / "EXPERT_LITERATURE_LANES_V1.md").read_text(encoding="utf-8")
    titles = []
    counts = {}
    current = None
    for line in text.split("\n"):
        if line.startswith("## Lane "):
            tail = line[len("## Lane "):]
            for sep in ("—", "-"):
                if sep in tail:
                    num, title = tail.split(sep, 1)
                    current = num.strip()
                    titles.append(title.strip())
                    counts[current] = 0
                    break
            continue
        if current is None:
            continue
        cells = table_cells(line)
        if cells is not None and len(cells) == 3:
            if cells[0].lower() == "work":
                continue
            if set(cells[0]) <= set("-: "):
                continue
            counts[current] += 1
    return titles, counts


def addendum_tables() -> Tuple[Set[str], Dict[str, str]]:
    text = (HERE / "AC_CROSSWALK_ADDENDUM_V1.md").read_text(encoding="utf-8")
    part1, rest = text.split("## Part 2", 1)
    part1 = part1.split("## Part 1", 1)[1]
    ac04 = set()
    for line in part1.split("\n"):
        cells = table_cells(line)
        if cells and cells[0].isdigit():
            ac04.add(cells[0])
    ac06 = {}
    for line in rest.split("\n"):
        cells = table_cells(line)
        if cells and cells[0].isdigit():
            ac06[cells[0]] = cells[2]
    return ac04, ac06


def derive() -> Dict[str, object]:
    rows = rows_from_freeze()
    items = [p.strip().rstrip(".")
             for p in rows["AC01"].split("lanes:", 1)[1].split(";")
             if p.strip().rstrip(".")]
    titles, counts = lanes()
    normalized_titles = [norm(t) for t in titles]
    bound = 0
    unbound = []
    for item in items:
        if normalized_titles.count(norm(item)) == 1:
            bound += 1
        else:
            unbound.append(item)

    cw = crosswalk()
    exact = [r for r in cw if r[5].upper().startswith("EXACT")]
    ac03_ok = 0
    for r in exact:
        adopt = r[8].startswith("RENAME") or r[8].startswith("PAPER-RENAME")
        share = bool(tokens(r[2]) & tokens(r[4]))
        if adopt or share:
            ac03_ok += 1

    add04, add06 = addendum_tables()
    ante = [r for r in cw if len(set(t.lower() for t in split_terms(r[4]))) >= 2]
    ac04_parent = 0
    ac04_unresolved = []
    for r in ante:
        if len(split_terms(r[2])) == 1 or "(" in r[8]:
            ac04_parent += 1
        elif r[0] not in add04:
            ac04_unresolved.append(r[0])

    anchored = 0
    missing = []
    status = {"VERIFIED": 0, "CITE-TF": 0, "UNMARKED": 0}
    for r in cw:
        cell = r[6]
        if has_year(cell) or "ISO" in cell or "Wikipedia" in cell:
            anchored += 1
        else:
            missing.append(r[0])
        if "VERIFIED" in cell:
            status["VERIFIED"] += 1
        elif "CITE-TF" in cell:
            status["CITE-TF"] += 1
        else:
            status["UNMARKED"] += 1
    supplied = sum(1 for n in missing if has_year(add06.get(n, "")))

    return {
        "schema": "GMI_833_AC_ORACLE_V1",
        "route": "B",
        "rows_recovered_from_freeze": sorted(rows),
        "lane_items": len(items),
        "lane_headings": len(titles),
        "bound_one_to_one": bound,
        "unbound_row_items": sorted(unbound),
        "entries_per_lane": dict(sorted(counts.items())),
        "total_entries": sum(counts.values()),
        "crosswalk_rows": len(cw),
        "exact_rows": len(exact),
        "ac03_satisfying_either": ac03_ok,
        "ac04_antecedent_rows": len(ante),
        "ac04_resolved_by_frozen_parent": ac04_parent,
        "ac04_resolved_by_addendum": len(add04),
        "ac04_unresolved": sorted(ac04_unresolved),
        "ac06_with_parent_in_parent_artifact": anchored,
        "ac06_missing_in_parent_artifact": sorted(missing),
        "ac06_supplied_by_addendum": supplied,
        "ac06_total_with_parent_record": anchored + supplied,
        "ac06_verification_status": status,
    }


if __name__ == "__main__":
    print(json.dumps(derive(), indent=2, sort_keys=True))
