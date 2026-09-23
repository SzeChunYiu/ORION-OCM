#!/usr/bin/env python3
"""Route A - structural AC05 check over the crosswalk citations column.

Exact instrument, stdlib only, no network. For each of the 48 rows of
research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md it checks
the four clauses of FREEZE_V1.md section 4 as far as they are checkable
offline:

  C1 identifier   the citations cell carries >=1 resolvable-identifier pattern
                  (doi:10.x/, arXiv:, ISBN, https://, or an explicit
                  programme-internal primary-source pointer "@ <commit>")
  C2 mark         the cell carries >=1 `VERIFIED-2026-09-19` mark
  C3 register     CITATION_VERIFICATION_V1.json has a record for the row with
                  verdict VERIFIED, resolved true, exactly one primary anchor,
                  a primary passage of <=15 words with a locator, and the
                  primary anchor's resolution HTTP status in {200,301,302,303}
                  (or an internal pointer)
  C4 in place     the primary anchor's identifier string occurs in the row's
                  own citations cell (a citation living only in another file
                  verifies nothing)

Resolution itself (the HTTP requests) was performed on the recorded date and
is NOT re-run here; this check verifies that the register records it and that
the table and register agree. Run:

    python3 -I -B research/gmi-833-ac05-citation-revival-v1/ac05_citation_check_v1.py
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CROSSWALK = REPO / "research" / "gmi-833-tranche-ab-ac-lit" / "GMI_TERMINOLOGY_CROSSWALK_V2.md"
REGISTER = HERE / "CITATION_VERIFICATION_V1.json"

DATE = "2026-09-19"
MARK = "VERIFIED-" + DATE
_IDENT = re.compile(r"(doi:10\.\d{4,9}/\S+|arXiv:\d{4}\.\d{4,5}|ISBN[ :]?[-0-9Xx]{10,17}|https?://\S+|@ [0-9a-f]{40})")


def _trim(tok: str) -> str:
    """Drop closing parentheses that do not belong to the identifier (a DOI
    such as 10.1016/0167-6423(87)90035-9 keeps its balanced pair)."""
    while tok.endswith((")", ",", ";", ".")) and tok.count(")") > tok.count("("):
        tok = tok[:-1]
    return tok.rstrip(",;.")


class _Ident:
    @staticmethod
    def findall(cell: str) -> List[str]:
        return [_trim(t) for t in _IDENT.findall(cell)]

    @staticmethod
    def sub(repl: str, cell: str) -> str:
        return _IDENT.sub(repl, cell)


IDENT = _Ident()
OK_HTTP = (200, 301, 302, 303)
HAREL_CONTAINER = "Computer"  # Crossref container-title for 10.1109/2.108047 (frozen 2026-09-19)


class AC05Error(Exception):
    pass


# ----------------------------------------------------------------------------- parsing
COLS = ("n", "legacy", "proposed", "field", "canonical", "match",
        "citations", "definition", "migration")


def crosswalk_rows(text: Optional[str] = None) -> List[Dict[str, str]]:
    text = CROSSWALK.read_text(encoding="utf-8") if text is None else text
    out = []
    for line in text.split("\n"):
        if not line.startswith("| ") or line.count("|") < 10:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 9 or not cells[0].isdigit():
            continue
        out.append(dict(zip(COLS, cells)))
    return out


def load_register(path: Path = REGISTER) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


# ----------------------------------------------------------------------------- per-row check
def check_row(row: Dict[str, str], reg: Dict[str, object]) -> Dict[str, object]:
    cell = row["citations"]
    n = row["n"]
    idents = IDENT.findall(cell)
    c1 = len(idents) > 0
    c2 = MARK in cell
    rec = reg.get("rows", {}).get(n)
    c3 = False
    c4 = False
    primary_ident = None
    reasons: List[str] = []
    if rec is None:
        reasons.append("no register record")
    else:
        prim = [a for a in rec.get("anchors", []) if a.get("role") == "primary"]
        if len(prim) != 1:
            reasons.append("primary anchors = %d" % len(prim))
        else:
            p = prim[0]
            passage = p.get("passage") or ""
            http = p.get("resolution", {}).get("http")
            internal = p.get("identifier_kind") == "internal"
            c3 = (rec.get("verdict") == "VERIFIED" and rec.get("resolved") is True
                  and 0 < len(passage.split()) <= 15 and bool(p.get("locator"))
                  and (internal or http in OK_HTTP))
            if not c3:
                reasons.append("register: verdict=%s resolved=%s words=%d http=%s"
                               % (rec.get("verdict"), rec.get("resolved"), len(passage.split()), http))
            primary_ident = p.get("identifier")
            if internal:
                key = re.search(r"@ ([0-9a-f]{40})", primary_ident or "")
                c4 = bool(key) and key.group(1) in cell
            else:
                c4 = bool(primary_ident) and primary_ident in cell
            if not c4:
                reasons.append("primary identifier not in the row's own cell")
    if not c1:
        reasons.append("no identifier pattern in cell")
    if not c2:
        reasons.append("no %s mark in cell" % MARK)
    return {"row": int(n), "c1_identifier": c1, "c2_mark": c2, "c3_register": c3,
            "c4_in_place": c4, "passes": c1 and c2 and c3 and c4,
            "identifiers_in_cell": sorted(set(idents)), "primary_identifier": primary_ident,
            "reasons": reasons}


def audit(rows: Sequence[Dict[str, str]], reg: Dict[str, object]) -> Dict[str, object]:
    per = [check_row(r, reg) for r in rows]
    passing = [p["row"] for p in per if p["passes"]]
    failing = [p["row"] for p in per if not p["passes"]]
    return {"rows": len(rows), "passing": len(passing), "failing_rows": failing,
            "per_row": per}


# ----------------------------------------------------------------------------- Harel venue
def harel_venue_ok(rows: Sequence[Dict[str, str]]) -> Dict[str, object]:
    cell = next(r["citations"] for r in rows if r["n"] == "1")
    m = re.search(r"Biting the silver bullet[^;]*", cell)
    seg = m.group(0) if m else ""
    ok = bool(m) and ("*Computer* 25(1)" in seg) and ("IEEE Software" not in seg) and ("10.1109/2.108047" in seg)
    return {"segment_found": bool(m), "container_expected": HAREL_CONTAINER, "ok": ok}


# ----------------------------------------------------------------------------- hostiles
def _rewrite_cell(text: str, n: int, fn) -> str:
    out = []
    for line in text.split("\n"):
        if line.startswith("| %d |" % n):
            parts = line.split(" | ")
            parts[6] = fn(parts[6])
            line = " | ".join(parts)
        out.append(line)
    return "\n".join(out)


def hostiles(text: str, reg: Dict[str, object]) -> List[Dict[str, object]]:
    base = audit(crosswalk_rows(text), reg)["passing"]
    out = []

    def rec(name, moved, before, after, applicable, detected):
        out.append({"name": name, "moved_quantity": moved, "before": before, "after": after,
                    "applicable": applicable, "detected": detected})

    # H1 - delete every identifier from one row's cell.
    t1 = _rewrite_cell(text, 19, lambda c: IDENT.sub("", c))
    a1 = audit(crosswalk_rows(t1), reg)["passing"]
    rec("H1_identifier_deleted_row19", "passing_rows", base, a1, t1 != text, a1 < base)

    # H2 - a row marked verified with no register record.
    reg2 = json.loads(json.dumps(reg))
    reg2["rows"].pop("21")
    a2 = audit(crosswalk_rows(text), reg2)["passing"]
    rec("H2_mark_without_register_row21", "passing_rows", base, a2, "21" in reg["rows"], a2 < base)

    # H3 - register record with resolved false.
    reg3 = json.loads(json.dumps(reg))
    reg3["rows"]["34"]["resolved"] = False
    a3 = audit(crosswalk_rows(text), reg3)["passing"]
    rec("H3_register_resolved_false_row34", "passing_rows", base, a3, reg["rows"]["34"]["resolved"] is True, a3 < base)

    # H4 - passage longer than 15 words.
    reg4 = json.loads(json.dumps(reg))
    for a in reg4["rows"]["41"]["anchors"]:
        if a["role"] == "primary":
            a["passage"] = " ".join(["word"] * 16)
    a4 = audit(crosswalk_rows(text), reg4)["passing"]
    rec("H4_passage_16_words_row41", "passing_rows", base, a4, True, a4 < base)

    # H5 - citation moved out of place: strip the primary identifier from the
    # cell but leave the register intact (the addendum situation).
    p47 = next(a for a in reg["rows"]["47"]["anchors"] if a["role"] == "primary")["identifier"]
    t5 = _rewrite_cell(text, 47, lambda c: c.replace(p47, "[see addendum]"))
    a5 = audit(crosswalk_rows(t5), reg)["passing"]
    rec("H5_citation_only_in_another_file_row47", "passing_rows", base, a5, p47 in text, a5 < base)

    # H6 - wrong venue on the Harel anchor.
    t6 = _rewrite_cell(text, 1, lambda c: c.replace("*Computer* 25(1)", "*IEEE Software* 25(1)"))
    h6 = harel_venue_ok(crosswalk_rows(t6))["ok"]
    rec("H6_harel_wrong_venue_row1", "harel_venue_ok", int(harel_venue_ok(crosswalk_rows(text))["ok"]), int(h6),
        t6 != text, (not h6) and harel_venue_ok(crosswalk_rows(text))["ok"])

    # H7 - internal pointer (row 48) with its commit hash removed from the cell.
    t7 = _rewrite_cell(text, 48, lambda c: re.sub(r"@ [0-9a-f]{40}", "@ <commit>", c))
    a7 = audit(crosswalk_rows(t7), reg)["passing"]
    rec("H7_internal_pointer_without_commit_row48", "passing_rows", base, a7, t7 != text, a7 < base)
    return out


# ----------------------------------------------------------------------------- null
def null_control(text: str, reg: Dict[str, object], draws: int = 200, seed: int = 833) -> Dict[str, object]:
    """Delete ONE identifier occurrence from one random row (full 64-bit
    Mersenne draws via random.Random - never low bits of a small LCG). Each
    draw must reduce the passing count below 48 unless the deleted identifier
    was a secondary one - so the null reports both the strict and the
    primary-only count and the true result (48/48 intact) must beat it."""
    rnd = random.Random(seed)
    rows = crosswalk_rows(text)
    base = audit(rows, reg)["passing"]
    reduced = 0
    primary_hits = 0
    for _ in range(draws):
        r = rnd.choice(rows)
        idents = IDENT.findall(r["citations"])
        victim = rnd.choice(idents)
        prim = next(a for a in reg["rows"][r["n"]]["anchors"] if a["role"] == "primary")["identifier"]
        is_primary = (victim in prim) or (prim in victim)
        t = _rewrite_cell(text, int(r["n"]), lambda c, v=victim: c.replace(v, "", 1))
        a = audit(crosswalk_rows(t), reg)["passing"]
        if a < base:
            reduced += 1
        if is_primary:
            primary_hits += 1
            if a >= base:
                raise AC05Error("null: primary identifier deleted from row %s but count did not drop" % r["n"])
    return {"draws": draws, "seed": seed, "base_passing": base, "draws_reducing_count": reduced,
            "draws_hitting_primary": primary_hits, "primary_deletions_missed": 0}


# ----------------------------------------------------------------------------- main
def main() -> Dict[str, object]:
    text = CROSSWALK.read_text(encoding="utf-8")
    reg = load_register()
    rows = crosswalk_rows(text)
    if len(rows) != 48:
        raise AC05Error("crosswalk row count changed: %d" % len(rows))
    a = audit(rows, reg)
    harel = harel_venue_ok(rows)
    host = hostiles(text, reg)
    null = null_control(text, reg)
    routes = {}
    for a_ in reg["rows"].values():
        for anc in a_["anchors"]:
            routes[anc.get("passage_route") or "NONE"] = routes.get(anc.get("passage_route") or "NONE", 0) + 1
    return {
        "schema": "GMI_833_AC05_CHECK_V1",
        "route": "A",
        "crosswalk_rows": len(rows),
        "passing_rows": a["passing"],
        "failing_rows": a["failing_rows"],
        "per_row": [dict({k: v for k, v in p.items() if k != "reasons"}, reasons=p["reasons"]) for p in a["per_row"]],
        "harel_row1": harel,
        "register": {"date": reg.get("verification_date"), "rows": len(reg.get("rows", {})),
                     "primary_passage_routes": {k: sum(1 for r in reg["rows"].values() if r["primary_passage_route"] == k)
                                                for k in sorted({r["primary_passage_route"] for r in reg["rows"].values()})},
                     "anchor_passage_routes": dict(sorted(routes.items()))},
        "hostiles": host,
        "null": null,
    }


if __name__ == "__main__":
    try:
        print(json.dumps(main(), indent=2, sort_keys=True))
    except AC05Error as exc:
        print(json.dumps({"schema": "GMI_833_AC05_CHECK_V1", "error": str(exc)}))
        sys.exit(2)
