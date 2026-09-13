"""MS-2 applied to MEASURED profiles -- the empirical step that GRAND GMI END_TO_END_DERIVATIONS_V1 §7 names
("replace the synthetic resource profiles with independently measured profiles").

The Stage D'/E' frontier receipts (`STAGE_DE_SMOOTH_V*.json`) already contain exactly the object the
Morphology Selection Theorem quantifies over: for every registered ecology, every price column (a declared
resource model B0..B3 / U / P3) and every (reuse horizon H, revision count r) cell, the frontier winner rows
under the CHARGED lifecycle meter.  Rows are hand-built parents of known families:
  S4 gradient net (coefficient / neural), S2/S2a exact linear search (program), S5 exemplar table (memory),
  S5h generalizing memory (kNN), S3 particles over the grammar (stochastic search), plus later additions.
MS-2 says a family/property P is DERIVED at a scope iff every frontier morphology at that scope has P.
This module reads the receipts and reports, per (ecology receipt, column):
  * the set of winner families over the (H, r) grid and whether one family is derived (all cells);
  * the cells where the winner family changes (the measured phase boundary);
and, per receipt, the cross-column inversions: (H, r) cells whose winner family differs between two price
columns although the capabilities are identical -- the measured instance of E2E-4 (same semantics, family
selected by the resource model).  Pure aggregation of committed receipts; no search, no fitting.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
FAMILY = {"S4": "COEFFICIENT", "S4n": "COEFFICIENT", "S2": "PROGRAM_SEARCH", "S2a": "PROGRAM_SEARCH", "S5": "MEMORY_EXACT",
          "S5h": "MEMORY_GENERALIZING", "S3": "STOCHASTIC_SEARCH", "S1": "STATELESS", "CONST": "CONSTANT", "S6": "OTHER_S6"}


def fam(row):
    base = row.split("@")[0]
    return FAMILY.get(base, FAMILY.get(re.sub(r"\d+$", "", base), base))


def analyse(path):
    d = json.load(open(path)); fr = d.get("frontier_H_r")
    if not fr: return None
    cells = {}
    for k, winners in fr.items():
        col, H, r = k.split("|")[0], int(re.search(r"H=(\d+)", k).group(1)), int(re.search(r"r=(\d+)", k).group(1))
        cells.setdefault(col, {})[(H, r)] = sorted({fam(w) for w in winners})
    per_col = {}
    for col, grid in cells.items():
        fams = sorted({f for v in grid.values() for f in v})
        derived = fams[0] if len(fams) == 1 else None
        # boundary: along r at fixed H, and along H at fixed r, where the winner set changes
        bnd = []
        for (H, r), v in sorted(grid.items()):
            for (H2, r2) in ((H, 2 * r if r else 1), (2 * H, r)):
                if (H2, r2) in grid and grid[(H2, r2)] != v:
                    bnd.append({"from": [H, r], "to": [H2, r2], "winner_from": v, "winner_to": grid[(H2, r2)]})
        per_col[col] = {"families_on_frontier": fams, "derived_family": derived, "n_cells": len(grid),
                        "cells_by_family": {f: sum(1 for v in grid.values() if v == [f]) for f in fams},
                        "n_boundary_transitions": len(bnd), "boundary": bnd[:12]}
    cols = sorted(cells)
    inversions = []
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            for key in sorted(set(cells[a]) & set(cells[b])):
                if cells[a][key] != cells[b][key]:
                    inversions.append({"cell_H_r": list(key), "column_a": a, "winner_a": cells[a][key], "column_b": b, "winner_b": cells[b][key]})
    return {"receipt": os.path.basename(path), "revival_record": d.get("revival_record"), "rows": d.get("ecology", {}).get("rows"),
            "columns": cols, "per_column": per_col, "n_cross_column_inversions": len(inversions), "cross_column_inversions": inversions[:20]}


def main(host="lead"):
    out = {"schema": "MS2MeasuredProfileSelectionV1", "source": "STAGE_DE_SMOOTH_V*.json frontier_H_r (charged lifecycle meter)",
           "family_map": FAMILY, "receipts": []}
    for p in sorted(glob.glob(os.path.join(RES, "STAGE_DE_SMOOTH_V*.json"))):
        try: a = analyse(p)
        except Exception as e: a = {"receipt": os.path.basename(p), "error": repr(e)[:200]}
        if a: out["receipts"].append(a)
    rs = [r for r in out["receipts"] if "per_column" in r]
    derived = sum(1 for r in rs for c in r["per_column"].values() if c["derived_family"])
    total = sum(len(r["per_column"]) for r in rs)
    out["summary"] = {"n_receipts": len(rs), "n_scopes(receipt x column)": total, "n_scopes_with_one_derived_family": derived,
                      "n_scopes_with_family_boundary": sum(1 for r in rs for c in r["per_column"].values() if c["n_boundary_transitions"]),
                      "n_receipts_with_cross_column_inversion": sum(1 for r in rs if r["n_cross_column_inversions"]),
                      "derived_family_histogram": {}}
    for r in rs:
        for c in r["per_column"].values():
            if c["derived_family"]:
                out["summary"]["derived_family_histogram"][c["derived_family"]] = out["summary"]["derived_family_histogram"].get(c["derived_family"], 0) + 1
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    path = os.path.join(RES, f"STAGE_MS2_MEASURED_SELECTION_{host}.json")
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)
    print(json.dumps(out["summary"], indent=1))
    for r in rs:
        print(r["receipt"], "| inversions", r["n_cross_column_inversions"], "|",
              " ".join(f"{col}:{(c['derived_family'] or 'MIXED(' + ','.join(c['families_on_frontier']) + ')')}" for col, c in r["per_column"].items()))
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "lead")
