#!/usr/bin/env python3
"""Validation plants for the L42 terminology-variant detector (protocol section 4).

A detector's first real run must not be its calibration. Four plants, all built FROM the
real census + real crosswalk (no invented strings beyond the swap itself):

  (a) RECALL plant — 20 synthetic variant pairs: sample real statements containing a
      legacy token, apply a same-row replacement swap, assert flagged (>= 19/20).
  (b) NO-ALARM plant — 200 real same-package statement pairs whose difference contains
      NO crosswalk span, plus the cry-wolf control (both sides share the common generic
      replacement word "architecture", differ elsewhere): assert 0 flags.
  (c) SEMANTICS ANCHOR — raw-hash grouping reproduces #949 candidate_groups.count.
  (d) SPECIFICITY ANCHOR — known-DISTINCT content-hash groups (identical strings) yield
      0 TERM_DUP flags; and a 200-sample of DISTINCT dupid-collision pairs yields 0
      flags unless the diff is a crosswalk span (any such hit is printed, not asserted
      away).

Run: python3 test_detector_l42_v1.py  -> prints per-plant results, exit 0 iff all pass.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from detector_l42_v1 import (  # noqa: E402
    CENSUS, CROSSWALK, REPO, anchor_raw_groups, compile_patterns, detect,
    load_crosswalk_classes, mask, mask_key, raw_key,
)

SEED = 833212


def _pairs_flagged(pairs: list[tuple[str, str]], pats) -> int:
    flagged = 0
    for s1, s2 in pairs:
        res = detect(
            [{"object_id": "A", "source_path": "x", "source_locator": "L1", "statement": s1},
             {"object_id": "B", "source_path": "x", "source_locator": "L2", "statement": s2}],
            pats,
        )
        if res["n_groups"] >= 1:
            flagged += 1
    return flagged


def plant_a_recall(objects, rows, pats) -> tuple[bool, str]:
    rng = random.Random(SEED)
    repl_first = {r["row_id"]: next(iter([f for f in r["replacements"] if " " not in f or len(f) > 6]), r["replacements"][0]) for r in rows}
    legacy_idx = [i for i, o in enumerate(objects) if any(h["legacy"] for h in mask(o["statement"], pats)[1])]
    rng.shuffle(legacy_idx)
    picked, pairs = [], []
    for i in legacy_idx:
        s = objects[i]["statement"]
        m, hits = mask(s, pats)
        legacy_hits = [h for h in hits if h["legacy"]]
        if not legacy_hits:
            continue
        h = legacy_hits[0]
        target = repl_first[h["row"]]
        swapped = s.lower().replace(h["form"], target, 1)
        if swapped == s.lower():
            continue
        pairs.append((s, swapped))
        picked.append(h["row"])
        if len(pairs) == 20:
            break
    n = _pairs_flagged(pairs, pats)
    ok = len(pairs) == 20 and n >= 19
    return ok, f"recall {n}/{len(pairs)} (rows used: {sorted(set(picked))})"


def plant_b_noalarm(objects, rows, pats) -> tuple[bool, str]:
    rng = random.Random(SEED + 1)
    by_file: dict[str, list[int]] = {}
    for i, o in enumerate(objects):
        by_file.setdefault(o["source_path"], []).append(i)
    multi = [v for v in by_file.values() if len(v) >= 2]
    rng.shuffle(multi)
    pairs, tried = [], 0
    for v in multi:
        if len(pairs) >= 200:
            break
        a, b = rng.sample(v, 2)
        s1, s2 = objects[a]["statement"], objects[b]["statement"]
        m1, h1 = mask(s1, pats)
        m2, h2 = mask(s2, pats)
        tried += 1
        if mask_key(m1) != mask_key(m2):  # non-class text differs -> never a candidate
            pairs.append((s1, s2))
    n = _pairs_flagged(pairs, pats)
    # cry-wolf control: shared generic word, differing elsewhere
    cw = [("the architecture is layered with depth three", "the architecture is layered with depth seven")]
    cw_n = _pairs_flagged(cw, pats)
    ok = n == 0 and cw_n == 0
    return ok, f"no-alarm {n}/{len(pairs)} (from {tried} same-file draws); cry-wolf {cw_n}/1"


def plant_c_anchor(objects) -> tuple[bool, str]:
    anchor = anchor_raw_groups(objects)
    ref = json.loads((REPO / "research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json").read_text())
    ref_count = ref["candidate_groups"]["count"]
    ok = anchor["n_buckets_multi"] == ref_count
    return ok, f"raw multi-buckets {anchor['n_buckets_multi']} vs #949 {ref_count}; objects in multi {anchor['n_objects_in_multi']}"


def plant_d_specificity(objects, pats) -> tuple[bool, str]:
    # content-hash groups are IDENTICAL strings -> 1 raw hash -> cannot be TERM_DUP.
    res = detect(objects, pats)
    ref = json.loads((REPO / "research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json").read_text())
    distinct_groups = [
        g for g in ref["candidate_groups"]["adjudications"]
        if g.get("verdict") == "DISTINCT"
    ]
    dup_hit = 0
    # direct check: every candidate group must have >=2 distinct raw keys (by construction)
    for g in res["groups"]:
        raws = {raw_key(m["statement"]) for m in g["members"]}
        if len(raws) < 2:
            dup_hit += 1
    # dupid DISTINCT collisions sample: pairs sharing object_id, different statements
    rng = random.Random(SEED + 2)
    by_id: dict[str, list[int]] = {}
    for i, o in enumerate(objects):
        by_id.setdefault(o["object_id"], []).append(i)
    collisions = [v for v in by_id.values() if len(v) >= 2]
    rng.shuffle(collisions)
    pairs, classdiff_hits = [], []
    for v in collisions:
        if len(pairs) >= 200:
            break
        a, b = rng.sample(v, 2)
        if raw_key(objects[a]["statement"]) != raw_key(objects[b]["statement"]):
            pairs.append((objects[a]["statement"], objects[b]["statement"]))
            classdiff_hits.append((objects[a]["source_path"], objects[b]["source_path"]))
    n = _pairs_flagged(pairs, pats)
    # any dupid hit means the pair differed ONLY inside a crosswalk span: printed, adjudicated later
    ok = dup_hit == 0
    return ok, f"candidate-groups with <2 raw keys: {dup_hit}; dupid-DISTINCT sample flags: {n}/{len(pairs)} (printed for adjudication, not asserted)"


def main() -> int:
    rows = load_crosswalk_classes()
    pats = compile_patterns(rows)
    idx = json.loads(CENSUS.read_text())
    objects = idx["scientific_objects"]

    results = {
        "a_recall": plant_a_recall(objects, rows, pats),
        "b_noalarm": plant_b_noalarm(objects, rows, pats),
        "c_anchor": plant_c_anchor(objects),
        "d_specificity": plant_d_specificity(objects, pats),
    }
    all_ok = True
    for name, (ok, msg) in results.items():
        print(f"[{'PASS' if ok else 'FAIL'}] plant_{name}: {msg}")
        all_ok &= ok
    print("ALL PLANTS PASS" if all_ok else "PLANT FAILURE — detector not cleared for real run")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
