#!/usr/bin/env python3
"""Route B - independent oracle for the AC05 structural check.

Written without importing the route-A module: a different row tokenizer
(regex on the row prefix + rsplit from the right, so a stray pipe inside a
citation cannot shift the column), a different identifier grammar (character
classes instead of the route-A alternation), and its own reading of the
register. It re-derives, for every row, the four booleans and the
identifier set, and the total n/48. Route A's test asserts equality.

    python3 -I -B research/gmi-833-ac05-citation-revival-v1/independent_ac05_oracle_v1.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CW = ROOT / "research" / "gmi-833-tranche-ab-ac-lit" / "GMI_TERMINOLOGY_CROSSWALK_V2.md"
REG = HERE / "CITATION_VERIFICATION_V1.json"
DATE = "2026-09-19"
ROW = re.compile(r"^\| (\d{1,2}) \| (.*) \|\s*$")
DOI = re.compile(r"doi:10\.[0-9]{4,9}/[^\s|]+")
ARX = re.compile(r"arXiv:[0-9]{4}\.[0-9]{4,5}")
ISBN = re.compile(r"ISBN[ :]?[-0-9Xx]{10,17}")
URL = re.compile(r"https?://[^\s|)]+")
COMMIT = re.compile(r"@ ([0-9a-f]{40})")


def rows():
    out = {}
    for line in CW.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        n = int(m.group(1))
        # 8 remaining cells: split from the RIGHT so the citations cell is
        # the third-from-last regardless of what it contains.
        tail = m.group(2).rsplit(" | ", 2)          # [.. up to citations, definition, migration]
        head = tail[0].rsplit(" | ", 5)             # legacy, proposed, field, canonical, match, citations
        if len(tail) != 3 or len(head) != 6:
            continue
        out[n] = {"citations": head[5].strip(), "definition": tail[1].strip()}
    return out


def _balance(tok):
    # a DOI may contain a balanced "(87)"; anything closing more than it
    # opened is table punctuation, not identifier
    opened = closed = 0
    out = []
    for ch in tok:
        if ch == "(":
            opened += 1
        if ch == ")":
            closed += 1
            if closed > opened:
                break
        out.append(ch)
    return "".join(out).rstrip(",;.")


def idents(cell):
    s = set()
    # URLs first; an ISBN or DOI spelled inside a URL is part of that URL,
    # not a second identifier
    urls = [_balance(t) for t in URL.findall(cell)]
    s.update(urls)
    stripped = URL.sub(" ", cell)
    for rx in (DOI, ARX, ISBN):
        s.update(_balance(t) for t in rx.findall(stripped))
    for c in COMMIT.findall(cell):
        s.add("@ " + c)
    return s


def derive():
    cw = rows()
    reg = json.loads(REG.read_text(encoding="utf-8"))["rows"]
    per = {}
    for n, r in sorted(cw.items()):
        cell = r["citations"]
        ids = idents(cell)
        rec = reg.get(str(n))
        b1 = bool(ids)
        b2 = ("VERIFIED-%s" % DATE) in cell
        b3 = b4 = False
        if rec is not None:
            prims = [a for a in rec["anchors"] if a["role"] == "primary"]
            if len(prims) == 1:
                p = prims[0]
                nw = len((p.get("passage") or "").split())
                http = (p.get("resolution") or {}).get("http")
                internal = p.get("identifier_kind") == "internal"
                b3 = (rec.get("verdict") == "VERIFIED" and rec.get("resolved") is True
                      and 1 <= nw <= 15 and bool(p.get("locator")) and (internal or http in (200, 301, 302, 303)))
                if internal:
                    m = COMMIT.search(p.get("identifier") or "")
                    b4 = bool(m) and (m.group(1) in cell)
                else:
                    b4 = bool(p.get("identifier")) and p["identifier"] in cell
        per[n] = {"c1": b1, "c2": b2, "c3": b3, "c4": b4, "passes": b1 and b2 and b3 and b4,
                  "identifiers": sorted(ids)}
    harel = cw.get(1, {}).get("citations", "")
    seg = re.search(r"Biting the silver bullet[^;]*", harel)
    harel_ok = bool(seg) and "*Computer* 25(1)" in seg.group(0) and "IEEE Software" not in seg.group(0) \
        and "10.1109/2.108047" in seg.group(0)
    return {"schema": "GMI_833_AC05_ORACLE_V1", "route": "B", "rows": len(cw),
            "passing": sum(1 for p in per.values() if p["passes"]),
            "failing_rows": [n for n, p in sorted(per.items()) if not p["passes"]],
            "harel_ok": harel_ok, "per_row": {str(n): p for n, p in sorted(per.items())}}


if __name__ == "__main__":
    print(json.dumps(derive(), indent=2, sort_keys=True))
