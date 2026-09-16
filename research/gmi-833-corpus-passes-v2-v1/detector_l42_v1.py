#!/usr/bin/env python3
"""GMI #833 L42 — terminology-variant duplicate detector (frozen protocol PASS-L42).

Detects the duplicate class the content-hash (`statement.lower()`) and DUPID detectors
cannot see: two census objects whose statements differ textually ONLY inside spans
belonging to one crosswalk migration row (legacy term on one side, a sanctioned
replacement on the other, or two sanctioned replacements of the same row).

Authority chain (frozen): equivalence classes are PARSED from
research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md migration rule table
(+ deterministic inflection expansion). Nothing hand-curated. Population P1 = census
CORPUS_INDEX_V1.json scientific_objects (frozen 2fffb144 / result 861b1ba1).

Method (O(N), no pairwise scan): mask() replaces every crosswalk-class span with a row
marker; objects bucket by sha256(mask). Two objects with equal masks differ ONLY inside
class spans (all other text is preserved verbatim by construction). A bucket with >= 2
distinct raw statements is a TERM_DUP_CAND group:
  CLASS_A  legacy surface on at least one side of a differing span (migration evidence);
  CLASS_B  replacement<->replacement only (weaker; adjudication-gated).

Validation plants (protocol section 4) live in test_detector_l42_v1.py and MUST pass
before any real run; this module refuses to emit candidates unless the anchor checks
(raw-hash grouping == #949 content-hash group semantics) hold on the loaded corpus.

stdlib only; deterministic; iteration over sorted keys.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CENSUS = REPO / "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json"
CROSSWALK = REPO / "research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md"

SCHEMA = "GMI_833_TERM_DUP_DETECTOR_V1"


# ---------------------------------------------------------------- crosswalk parsing
def _clean(cell: str) -> list[str]:
    """Split a crosswalk cell into surface forms; strip qualifiers/quotes."""
    forms = []
    for part in re.split(r"[/;]", cell):
        p = part.strip()
        p = re.sub(r"\([^)]*\)", " ", p)  # drop parenthetical qualifiers
        p = p.strip(" “”\"'`.")
        if p and len(p) > 2 and "," not in p[:1]:
            forms.append(p.lower())
    return forms


def _inflect(form: str) -> list[str]:
    """Deterministic inflection/separator variants of a surface form."""
    out = {form}
    words = form.split()
    if words:
        last = words[-1]
        if last.endswith("y"):
            out.add(" ".join(words[:-1] + [last[:-1] + "ies"]))
        elif not last.endswith("s"):
            out.add(" ".join(words[:-1] + [last + "s"]))
    if "-" in form:
        out.add(form.replace("-", " "))
    if " " in form:
        out.add(form.replace(" ", "-"))
    return sorted(out)


def load_crosswalk_classes(path: Path = CROSSWALK) -> list[dict]:
    """Parse the migration rule table; return row records with compiled patterns."""
    text = path.read_text()
    rows: list[dict] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("## Migration rule table"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                if rows:
                    break
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or cells[0].startswith("legacy GMI term") or set(cells[0]) <= {"-", " "}:
                continue
            legacy_forms: list[str] = []
            for f in _clean(cells[0]):
                legacy_forms.extend(_inflect(f))
            repl_forms: list[str] = []
            for f in _clean(cells[2]):
                repl_forms.extend(_inflect(f))
            rows.append(
                {
                    "row_id": f"R{len(rows) + 1}",
                    "legacy_canonical": cells[0].lower(),
                    "legacy": sorted(set(legacy_forms)),
                    "replacements": sorted(set(repl_forms)),
                }
            )
    return rows


def compile_patterns(rows: list[dict]) -> list[dict]:
    """Longest-first compiled patterns; each span records row + whether legacy."""
    pats = []
    for row in rows:
        for side in ("legacy", "replacements"):
            for form in row[side]:
                rx = re.compile(r"\b" + re.escape(form).replace(r"\ ", r"[\s\-_]+") + r"\b")
                pats.append({"row": row["row_id"], "legacy": side == "legacy", "form": form, "rx": rx})
    pats.sort(key=lambda p: (-len(p["form"]), p["form"], p["row"]))
    return pats


# ---------------------------------------------------------------- masking
SENTINEL = "\x00{}\x00"


def mask(statement: str, pats: list[dict]) -> tuple[str, list[dict]]:
    """Replace crosswalk spans with row sentinels; return (masked, hits)."""
    s = statement.lower()
    hits: list[dict] = []
    for p in pats:
        def _sub(m: re.Match, p=p) -> str:
            hits.append({"row": p["row"], "legacy": p["legacy"], "form": p["form"], "span": m.group(0)})
            return SENTINEL.format(p["row"])

        s = p["rx"].sub(_sub, s)
    return s, hits


def raw_key(statement: str) -> str:
    """The #949 content-hash group key semantics: statement.lower()."""
    return hashlib.sha256(statement.lower().encode()).hexdigest()


def mask_key(masked: str) -> str:
    return hashlib.sha256(masked.encode()).hexdigest()


# ---------------------------------------------------------------- detector
def detect(objects: list[dict], pats: list[dict]) -> dict:
    """Bucket by mask; return candidate groups (>=2 distinct raw statements)."""
    buckets: dict[str, list[int]] = {}
    masked_cache: dict[int, tuple[str, list[dict]]] = {}
    for i, obj in enumerate(objects):
        m, hits = mask(obj.get("statement") or "", pats)
        masked_cache[i] = (m, hits)
        buckets.setdefault(mask_key(m), []).append(i)

    groups = []
    for mk in sorted(buckets):
        idxs = buckets[mk]
        raws = {raw_key(objects[i]["statement"]) for i in idxs}
        if len(idxs) < 2 or len(raws) < 2:
            continue
        members = sorted(
            (
                {
                    "object_id": objects[i]["object_id"],
                    "source_path": objects[i]["source_path"],
                    "source_locator": objects[i]["source_locator"],
                    "statement": objects[i]["statement"],
                    "class_hits": [h["row"] + ("*" if h["legacy"] else "") for h in masked_cache[i][1]],
                }
                for i in idxs
            ),
            key=lambda m: (m["source_path"], m["source_locator"], m["object_id"]),
        )
        rows_used = sorted({r.split("*")[0] for m in members for r in m["class_hits"]})
        has_legacy = any(r.endswith("*") for m in members for r in m["class_hits"])
        groups.append(
            {
                "mask_hash": mk,
                "candidate_class": "CLASS_A" if has_legacy else "CLASS_B",
                "rows_unifying": rows_used,
                "n_members": len(members),
                "members": members,
            }
        )
    groups.sort(key=lambda g: (g["candidate_class"], g["mask_hash"]))
    return {"schema": SCHEMA, "n_groups": len(groups), "groups": groups}


# ---------------------------------------------------------------- anchors
def anchor_raw_groups(objects: list[dict]) -> dict:
    """Anchor (c): raw-hash grouping must reproduce #949 content-hash group semantics."""
    buckets: dict[str, int] = {}
    for obj in objects:
        k = raw_key(obj["statement"])
        buckets[k] = buckets.get(k, 0) + 1
    return {"n_buckets_multi": sum(1 for v in buckets.values() if v >= 2),
            "n_objects_in_multi": sum(v for v in buckets.values() if v >= 2)}


def main() -> int:
    rows = load_crosswalk_classes()
    pats = compile_patterns(rows)
    print(f"crosswalk rows parsed: {len(rows)}; compiled spans: {len(pats)}")
    for r in rows:
        print(f"  {r['row_id']}: legacy={r['legacy'][:4]}... repl={len(r['replacements'])} forms")

    idx = json.loads(CENSUS.read_text())
    objects = idx["scientific_objects"]
    print(f"population P1: {len(objects)} objects")

    anchor = anchor_raw_groups(objects)
    print(f"anchor raw-hash multi-buckets: {anchor}")
    dup = json.loads((REPO / "research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json").read_text())
    ref_groups = dup.get("candidate_groups", {}).get("count")
    print(f"#949 reference content-hash groups: {ref_groups}")
    if ref_groups is not None and anchor["n_buckets_multi"] != ref_groups:
        print("ANCHOR FAIL: raw-hash semantics diverge from #949 grouping; refusing to emit candidates")
        return 2

    result = detect(objects, pats)
    out = Path(__file__).parent / "TERM_DUP_CANDIDATES_V1.json"
    counts = {"CLASS_A": 0, "CLASS_B": 0}
    for g in result["groups"]:
        counts[g["candidate_class"]] += 1
    result["class_counts"] = counts
    out.write_text(json.dumps(result, indent=1, sort_keys=True))
    print(f"candidate groups: {result['n_groups']} ({counts})")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
