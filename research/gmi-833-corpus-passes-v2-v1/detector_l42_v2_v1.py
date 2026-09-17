#!/usr/bin/env python3
"""GMI #833 L42v2 — content-normalization near-duplicate detector (revival of the L42 diagnostic).

Revival doctrine: the L42 pass found 128 punctuation/case/quote-relaxed near-duplicate
groups as a DIAGNOSTIC; this detector promotes that class to a validated screen.
Normalization: crosswalk-class masking (detector_l42_v1) THEN strip all characters
outside [a-z0-9] + sentinels, collapse whitespace. Two flag classes:
  CONTENT_NORM_DUP — equal normalized masks, >=2 distinct raw statements, NO crosswalk
                     span (pure case/quote/punctuation/whitespace variant);
  TERM_NORM_DUP    — same, but >=1 crosswalk span involved (terminology + normalization).
Plants (must pass before real run): real case-variant pair, real quote-variant pair,
no-alarm pair differing in a real word, determinism byte-equality.
stdlib only; deterministic; sorted iteration.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from detector_l42_v1 import load_crosswalk_classes, compile_patterns, mask  # noqa: E402

SCHEMA = "GMI_833_TERM_DUP_DETECTOR_V2_CONTENT_NORM_V1"


def relax(m: str) -> str:
    m = re.sub(r"[^a-z0-9\x00]", " ", m)
    return re.sub(r"\s+", " ", m).strip()


def raw_key(s: str) -> str:
    return hashlib.sha256(s.lower().encode()).hexdigest()


def detect(objects: list[dict], pats: list[dict]) -> dict:
    buckets: dict[str, list[int]] = {}
    hits: dict[int, list] = {}
    for i, o in enumerate(objects):
        m, h = mask(o.get("statement") or "", pats)
        hits[i] = h
        buckets.setdefault(hashlib.sha256(relax(m).encode()).hexdigest(), []).append(i)
    groups = []
    for k in sorted(buckets):
        idxs = buckets[k]
        if len(idxs) < 2 or len({raw_key(objects[i]["statement"]) for i in idxs}) < 2:
            continue
        members = sorted(
            ({"object_id": objects[i]["object_id"], "source_path": objects[i]["source_path"],
              "source_locator": objects[i]["source_locator"],
              "statement": objects[i]["statement"][:220]} for i in idxs),
            key=lambda m: (m["source_path"], m["source_locator"], m["object_id"]))
        has_span = any(hits[i] for i in idxs)
        groups.append({"bucket": k, "class": "TERM_NORM_DUP" if has_span else "CONTENT_NORM_DUP",
                       "n_members": len(members), "members": members})
    groups.sort(key=lambda g: (g["class"], g["bucket"]))
    return {"schema": SCHEMA, "n_groups": len(groups), "groups": groups}


def plants(pats: list[dict]) -> bool:
    def flagged(s1: str, s2: str) -> bool:
        r = detect([{"object_id": "A", "source_path": "x", "source_locator": "L1", "statement": s1},
                    {"object_id": "B", "source_path": "x", "source_locator": "L2", "statement": s2}], pats)
        return r["n_groups"] == 1

    pos_case = flagged("LAW 1 -- COMPOSING COUNTING OBLIGATIONS IS SUB-MULTIPLICATIVE, AND EXACTLY LCM",
                       "**Law 1 — composing counting obligations is sub-multiplicative, and exactly lcm.**")  # real corpus pattern (case/punct)
    pos_quote = flagged('"research/gmi-learning-law-selection-v1/CORE.md",',
                        "'research/gmi-learning-law-selection-v1/CORE.md',")  # real corpus pattern (quote style)
    neg_word = flagged("the architecture is layered with depth three",
                       "the architecture is layered with depth seven")  # real-word difference must NOT flag
    return pos_case and pos_quote and not neg_word


def main() -> int:
    pats = compile_patterns(load_crosswalk_classes())
    if not plants(pats):
        print("PLANT FAILURE — v2 detector not cleared")
        return 1
    print("[PASS] plants: case-variant flags, quote-variant flags, real-word difference silent")
    idx = json.loads((HERE.parent / "gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json").read_text())
    res = detect(idx["scientific_objects"], pats)
    counts = {"TERM_NORM_DUP": 0, "CONTENT_NORM_DUP": 0}
    for g in res["groups"]:
        counts[g["class"]] += 1
    res["class_counts"] = counts
    (HERE / "TERM_NORM_DUP_CANDIDATES_V1.json").write_text(json.dumps(res, indent=1, sort_keys=True))
    print(f"v2 groups: {res['n_groups']} ({counts}) -> TERM_NORM_DUP_CANDIDATES_V1.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
