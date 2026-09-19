#!/usr/bin/env python3
"""Route B - independent oracle for AB08 and AB25.

Imports nothing from `residual_definitions_v1.py` and uses **no regular
expressions**: headings are matched by prefix, bold labels are found by index,
and the row strings are re-read out of `FREEZE_V1.md` rather than shared as
constants - so a corrupted row constant in route A cannot be reproduced here.

stdlib only; python3.8-compatible.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
RICE = HERE / "RICE_PARENT_SUBTRACTION_V1.md"
LADDER = HERE / "NOVELTY_LADDER_V1.md"
VERDICTS = ("ABSORBED", "PARTIAL", "DIVERGENT")


class OracleError(RuntimeError):
    pass


def norm(text: str) -> str:
    buf = []
    for ch in text.lower():
        if ch in "*`":
            continue
        buf.append(" " if ch in "-/,–" else ch)
    return " ".join("".join(buf).split())


def rows_from_freeze() -> Tuple[str, str, str]:
    text = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    scope = text.split("Verbatim from comment 5684607872 under the anchor above:", 1)[1]
    scope = scope.split("**No neighboring row is earned here.**", 1)[0]
    rows = [l.strip() for l in scope.split("\n") if l.strip().startswith("- [ ]")]
    if len(rows) != 2:
        raise OracleError("freeze does not quote exactly two AB rows: %d" % len(rows))
    ante_block = text.split("That row is **AB25's declared antecedent**", 1)[0]
    ante = [l.strip() for l in ante_block.split("\n") if l.strip().startswith("- [x]")]
    if len(ante) != 1:
        raise OracleError("freeze does not quote exactly one antecedent row")
    ab08 = [r for r in rows if "parent-subtract" in r][0]
    ab25 = [r for r in rows if "novelty ladder" in r][0]
    return ab08, ab25, ante[0]


def bold_runs(line: str) -> List[str]:
    """Every `**...**` run on a line, found by index scan."""
    out = []
    i = 0
    while True:
        a = line.find("**", i)
        if a < 0:
            break
        b = line.find("**", a + 2)
        if b < 0:
            break
        inner = line[a + 2:b]
        if inner and "*" not in inner:
            out.append(inner)
        i = b + 2
    return out


def leading_label(line: str) -> Optional[Tuple[str, str]]:
    if not line.startswith("**"):
        return None
    close = line.find("**", 2)
    if close <= 2:
        return None
    label = line[2:close].strip()
    while label and label[-1] in ".:":
        label = label[:-1]
    return label, line[close + 2:].strip()


def sections(path: Path) -> List[Tuple[str, List[str]]]:
    out = []
    title = None
    body = []  # type: List[str]
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line[:3] == "## " and line[:4] != "### ":
            if title is not None:
                out.append((title, body))
            title = line[3:].strip()
            body = []
            continue
        if title is not None:
            body.append(line)
    if title is not None:
        out.append((title, body))
    return out


def labelled(body: Sequence[str]) -> Dict[str, str]:
    out = {}
    current = None
    for line in body:
        hit = leading_label(line)
        if hit:
            current = hit[0]
            out[current] = hit[1]
        elif current is not None and line.strip():
            out[current] = (out[current] + " " + line.strip()).strip()
        elif not line.strip():
            current = None
    return out


def split_after(text: str, marker: str) -> str:
    at = text.find(marker)
    if at < 0:
        raise OracleError("marker %r not found" % marker)
    return text[at + len(marker):]


def derive() -> Dict[str, object]:
    ab08, ab25, ante = rows_from_freeze()

    comps = [p.strip() for p in
             split_after(ab08, "algorithm selection**:").rstrip(".").split(",")
             if p.strip()]
    levels = bold_runs(split_after(ante, "distinguish"))

    rice_sections = []
    for title, body in sections(RICE):
        if not title.startswith("Component "):
            continue
        name = title.split("—", 1)[1].strip() if "—" in title else title
        rice_sections.append((norm(name), labelled(body)))
    rice_map = dict(rice_sections)

    present = 0
    complete = 0
    verdicts = {v: 0 for v in VERDICTS}
    for comp in comps:
        vals = rice_map.get(norm(comp))
        if vals is None:
            continue
        present += 1
        keys = set(vals)
        needed = {"Rice's object", "GMI's object", "Verdict",
                  "What Rice already supplies", "Residual"}
        verdict = None
        for v in VERDICTS:
            if v in vals.get("Verdict", ""):
                verdict = v
        if verdict:
            verdicts[verdict] += 1
        residual_ok = bool(vals.get("Residual", "").strip())
        absorbed_ok = verdict != "ABSORBED" or \
            vals.get("Residual", "").strip().lower().startswith("none")
        if needed <= keys and verdict and residual_ok and absorbed_ok:
            complete += 1

    ladder_sections = []
    for title, body in sections(LADDER):
        if not title.startswith("Level "):
            continue
        tail = title[len("Level "):]
        num = tail.split(" ", 1)[0].strip()
        if not num.isdigit():
            continue
        name = title.split("—", 1)[1].strip() if "—" in title else ""
        ladder_sections.append((int(num), norm(name), labelled(body)))
    ladder_sections.sort()
    nonzero = [x for x in ladder_sections if x[0] > 0]

    order_ok = [n for _, n, _ in nonzero] == [norm(l) for l in levels]
    lvl_complete = 0
    witness = 0
    down = 0
    criteria = []
    for n, name, vals in nonzero:
        needed = {"Operational criterion", "Falsifier", "Parent literature",
                  "Demotion rule"}
        if needed <= set(vals) and all(vals[k].strip() for k in needed):
            lvl_complete += 1
        crit = vals.get("Operational criterion", "")
        criteria.append(norm(crit))
        if "witness" in crit.lower():
            witness += 1
        dem = norm(vals.get("Demotion rule", ""))
        target = None
        words = dem.split()
        for i, w in enumerate(words):
            if w != "level" or i + 1 >= len(words):
                continue
            nxt = words[i + 1].strip(".;:,")
            if nxt.isdigit():
                target = int(nxt)
                break
        if target is not None and target < n:
            down += 1

    return {
        "schema": "GMI_833_AB_DEFINITIONS_ORACLE_V1",
        "route": "B",
        "rows_recovered_from_freeze": True,
        "ab08_row_components": comps,
        "ab08_sections": len(rice_sections),
        "ab08_present": present,
        "ab08_complete": complete,
        "ab08_verdicts": verdicts,
        "ab25_row_levels": levels,
        "ab25_levels_found": len(nonzero),
        "ab25_declares_level_zero": any(n == 0 for n, _, _ in ladder_sections),
        "ab25_order_matches": order_ok,
        "ab25_complete": lvl_complete,
        "ab25_naming_a_witness": witness,
        "ab25_demotions_pointing_down": down,
        "ab25_criteria_pairwise_distinct": len(set(criteria)) == len(criteria),
    }


if __name__ == "__main__":
    print(json.dumps(derive(), indent=2, sort_keys=True))
