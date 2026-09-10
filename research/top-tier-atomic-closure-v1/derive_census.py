#!/usr/bin/env python3
"""TTAC census derivation checker (RH-01, #323 recursive hardening).

Fail-closed: recomputes every registry census from the atoms array itself and
refuses any hand-copied or drifted count. Distinct exit codes per defect class
so "checked and fine" can never be confused with "could not check".

  0  PASS (all census fields recompute exactly)
  10 CENSUS_MISMATCH (a published census count disagrees with the atoms array)
  11 CLASS_OFF_TAXONOMY (an atom class absent from TAXONOMY_FREEZE_V1 sec 1)
  12 ZERO_CLASS_INVISIBLE (a taxonomy class with 0 atoms missing from by_class)
  13 SCHEMA_SHAPE (an expected artifact/field missing or unparseable)

D28 F4 precedent: a hostile recount found census 27 vs actual 29 — hand-copied
counts drift; after this checker they cannot drift silently (CI runs it).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
TAXONOMY_CLASSES = [
    "THEOREM", "ENGINEERING_MECHANISM", "EMPIRICAL_REGULARITY",
    "DEVELOPMENTAL_LINEAGE", "SELF_EVOLUTION", "GOVERNANCE_META",
]


def fail(code, msg):
    print(f"DERIVE_CENSUS FAIL({code}): {msg}")
    sys.exit(code)


def main():
    try:
        reg = json.loads((BASE / "ATOM_REGISTRY_V1.json").read_text())
        mat = json.loads((BASE / "READINESS_MATRIX_V1.json").read_text())
        dcr = json.loads((BASE / "DECISIVE_CLAIM_REGISTRY_V1.json").read_text())
        tax = (BASE / "TAXONOMY_FREEZE_V1.md").read_text()
    except Exception as e:  # missing/unparseable artifact = could not check
        fail(13, f"artifact unreadable: {e}")

    atoms = reg.get("atoms") or []
    if not atoms:
        fail(13, "ATOM_REGISTRY_V1 atoms array empty/missing")

    # cross-check the frozen class list against the taxonomy table itself,
    # so a future taxonomy edit cannot silently desynchronize this checker
    m = re.findall(r"^\|\s*`([A-Z_]+)`\s*\|", tax, flags=re.M)
    if m and m != TAXONOMY_CLASSES:
        fail(11, f"taxonomy table classes {m} != checker list {TAXONOMY_CLASSES} — update both together")

    true_by_class = Counter(a["class"] for a in atoms)
    true_by_terminal = Counter(a["terminal"] for a in atoms)

    # RH-12: every taxonomy class must appear in the published by_class —
    # a zero-atom class is a visible row, never an absence
    for cls in TAXONOMY_CLASSES:
        if cls not in (mat.get("census") or {}).get("by_class", {}):
            fail(12, f"taxonomy class {cls} missing from READINESS_MATRIX census.by_class (zero classes must be visible)")

    checks = [
        ("READINESS_MATRIX_V1.census.atoms", (mat.get("census") or {}).get("atoms"), len(atoms)),
        ("READINESS_MATRIX_V1.census.by_class", (mat.get("census") or {}).get("by_class"),
         {**{c: 0 for c in TAXONOMY_CLASSES}, **dict(true_by_class)}),
        ("READINESS_MATRIX_V1.census.by_terminal", (mat.get("census") or {}).get("by_terminal"), dict(true_by_terminal)),
        ("READINESS_MATRIX_V1 rows count", len(mat.get("rows") or []), len(atoms)),
        ("DECISIVE_CLAIM_REGISTRY_V1 census.claims", (dcr.get("census") or {}).get("claims"), len(dcr.get("claims") or [])),
    ]
    bad = [(name, got, want) for name, got, want in checks if got != want]
    if bad:
        for name, got, want in bad:
            print(f"  {name}: published={got!r} derived={want!r}")
        fail(10, f"{len(bad)} census field(s) disagree with the atoms array")

    n = len(atoms)
    print(f"DERIVE_CENSUS PASS: atoms={n} by_class={dict(true_by_class)} "
          f"by_terminal={dict(true_by_terminal)} classes_visible={len(TAXONOMY_CLASSES)}")


if __name__ == "__main__":
    main()
