#!/usr/bin/env python3
"""Validation for depgraph_miner_v1 (known-positives + no-alarm + determinism).

A false positive costs more than a miss: every assertion here was derived from
lines read during the manual review pass, not from the miner's own output.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import depgraph_miner_v1 as M  # noqa: E402

G = json.loads((HERE / "DEPENDENCY_GRAPH_V2.json").read_text(encoding="utf-8"))
A1 = G["edges"]["file_local"]
FAM = G["edges"]["parent_family_anchor"]
B = G["edges"]["external_literature"]
C = G["edges"]["corpus_package"]
PKG = G["edges"]["pointer_rollup"]

failures = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        failures.append(msg)


def has(layer, child, parent, relation=None):
    return any(e["child"] == child and e["parent"] == parent
               and (relation is None or e["relation"] == relation)
               for e in layer)


# --- known positives (verified by hand against the cited lines) -----------
check(has(A1, "AUTO-122A9F457E75B5D86CE7", "PVR-3", "USES"),
      "known positive: capability-interactions 'ruled out by PVR-3'")
check(has(A1, "AUTO-4B3949FE5DA4182BF4B0", "PVR-3", "DERIVES_FROM"),
      "known positive: residual-memory 'derived from PVR-3'")
check(has(A1, "ADAPTIVE_ROW_CREATION_THEOREM_V1",
          "ADAPTIVE_ROW_CONFIDENCE_THEOREM_V1", "STRONGEST_PARENT_DECLARED"),
      "known positive: Parents: [ARC-1-4] header")
check(has(A1, "P9A.BLUM_SPEEDUP", "P0.BLUM_SPEEDUP", "INHERITS"),
      "known positive: corpus copy inherits literature parent")
check(has(A1, "GMI-T3", "H-ENCODING-BIAS", "INSTANTIATES"),
      "known positive: GMI-T3 instantiates hostile")
check(has(A1, "EA-5", "TDA-1", "USES"),
      "known positive: EA-5 'uses compatible leaves (TDA-1)'")
check(has(FAM, "GMI-T5", "P7", "PARENT_FAMILY_ANCHOR"),
      "known positive: GMI-T5 (P7P8P6P5) family anchor")
check(has(FAM, "GMI-T3", "P7", "PARENT_FAMILY_ANCHOR"),
      "known positive: GMI-T3 family anchor")
check(any("aj8" in e["citation"] and "Legg & Hutter" in e["parent"]
          for e in B),
      "known positive: AJ8 strongest parent Legg & Hutter (2007)")
check(has(C, "gmi-833-aj9e-k04-blind-recovery-v1",
          "gmi-833-aj9a-known-family-benchmark-v1"),
      "known positive: AJ9e freeze references AJ9a benchmark")
check(len(PKG) > 0 and any(e.get("rollup") for e in PKG),
      "pointer rollup layer non-empty")

# --- no-alarm (verified false-positive classes must stay absent) ----------
check(not any(e["parent"] in M.STATUS_VALUE_IDS for e in A1 + PKG),
      "no-alarm: no status-string id is a parent")
check(not has(A1, "RR-1", "RR-2"),
      "no-alarm: subject-misattributed RR-2 edge excluded")
check(not has(A1, "NMI-12", "NMI-1"),
      "no-alarm: quoted-chain 'AND generalizes AND' excluded")
check(not has(A1, "P_W", "GMI-T10"),
      "no-alarm: open-question 'can be derived' excluded")
check(not has(A1, "ORION-OCM", "LITERATURE_LEDGER"),
      "no-alarm: URL/path-fragment ids excluded")
check(not has(A1, "RV-377-018", "PH-5"),
      "no-alarm: adjective 'generalizing kNN memory' excluded")
check(not any(e["parent"] == "L_NEURAL" for e in A1),
      "no-alarm: adjective 'refined bounds' excluded")
check(not has(A1, "T602-27", "T602-10"),
      "no-alarm: negated 'No sign follows from' excluded")

# no-alarm file control: audit-close FREEZE_V1.md has a Parent: #833 header
# (programme parent) and no claim dependencies -> zero edges, one mention
objs = M.load_census()
claims = [o for o in objs
          if o["source_path"].endswith("gmi-833-corpus-audit-close-v1/FREEZE_V1.md")
          and o["object_class"] in M.CLAIM_CLASSES]
if claims:
    lines = (M.REPO_ROOT / claims[0]["source_path"]).read_text().splitlines()
    edges, prog, named = M.mine_file(claims[0]["source_path"], lines,
                                     sorted(claims, key=lambda o: int(o["source_locator"][1:])),
                                     M.build_id_index(objs))
    check(not edges, "no-alarm: audit-close FREEZE yields zero claim edges")
else:
    check(True, "no-alarm: audit-close FREEZE declares no claim objects (vacuous)")

# --- determinism: two runs byte-identical --------------------------------
out = HERE / "DEPENDENCY_GRAPH_V2.json"
before = out.read_bytes()
res = subprocess.run([sys.executable, str(HERE / "depgraph_miner_v1.py")],
                     capture_output=True, text=True)
after = out.read_bytes()
check(res.returncode == 0 and before == after,
      "determinism: rerun reproduces DEPENDENCY_GRAPH_V2.json byte-identically")

# --- structural sanity ----------------------------------------------------
total = sum(len(v) for k, v in G["edges"].items() if isinstance(v, list))
check(total == len(A1) + len(PKG) + len(FAM) + len(B) + len(C),
      "edge layers sum to total")
check(all(e.get("citation") for e in A1 + PKG + FAM + B + C),
      "every edge carries a citation")
check(all(e.get("evidence") for e in A1 + PKG + FAM + B + C),
      "every edge carries evidence text")

print()
if failures:
    print(f"VALIDATION FAILED: {len(failures)}")
    sys.exit(1)
print("ALL VALIDATION CHECKS PASSED")
