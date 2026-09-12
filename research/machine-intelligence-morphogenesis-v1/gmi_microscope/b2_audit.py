"""DG-2 / protocol-rule-28 audit of this lane's stage-B2 receipts, run before they are committed.

Protocol rule 28: "a receipt that reports a frontier must carry the PER-ROW COST COORDINATES that produced it, or its
grid cannot be audited by anyone, including its author" (RV-377-068: 9 of 73 receipts were unauditable from their own
contents). Gap DG-2: "every frontier grid must extend past the analytic crossover of every price vector it reports"
(34 of 73 receipts were truncated).

Every stage-B2 receipt of this lane therefore carries `b2_frontiers`, one block per context, each holding the per-row
cost coordinates (A, E), every analytic crossover, the shared reuse grid built from those crossovers, and the frontier
as maximal runs. `gmi_microscope/grid_audit.py` family C grades them: it recomputes each receipt's own frontier from
the receipt's own coordinates (the soundness gate) and then checks whether the occupant is constant beyond the grid.

Writes microscopes/results/STAGE_B2_DG2_AUDIT_V1.json. Run: python3 -m gmi_microscope.b2_audit
"""
from __future__ import annotations

import glob
import json
import os

from .core import sha256_of
from .grid_audit import audit_receipt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")


def _nested_frontier_keys(d, prefix="", depth=0):
    """Frontier-looking keys anywhere below the top level: a receipt that reports a frontier only in a nested block is
    invisible to grid_audit.py's corpus scan, which matches TOP-LEVEL keys only."""
    out = []
    if depth > 3 or not isinstance(d, dict):
        return out
    for k, v in d.items():
        if "frontier" in str(k) and depth > 0:
            out.append(prefix + str(k))
        if isinstance(v, dict):
            out.extend(_nested_frontier_keys(v, prefix + str(k) + ".", depth + 1))
    return sorted(set(out))[:8]


def main(path=None):
    paths = sorted(p for p in glob.glob(os.path.join(RES, "STAGE_B2_*.json"))
                   if not os.path.basename(p).startswith("STAGE_B2_DG2_AUDIT"))
    rows = []
    for p in paths:
        d = json.load(open(p))
        if not isinstance(d, dict):
            continue
        if "b2_frontiers" not in d and not any("frontier" in k for k in d):
            nested = _nested_frontier_keys(d)
            rows.append({"receipt": os.path.basename(p), "schema": d.get("schema"),
                         "revival_record": d.get("revival_id"),
                         "verdict": "NO_FRONTIER" if not nested else "UNAUDITABLE_BY_INSTRUMENT",
                         "nested_frontier_keys": nested,
                         "reason": ("this receipt reports no frontier anywhere, so rule 28 has nothing to audit"
                                    if not nested else
                                    "this receipt DOES report a frontier, but only NESTED inside its cells and with no "
                                    "top-level per-row cost coordinates. gmi_microscope/grid_audit.py's corpus scan "
                                    "looks only at TOP-LEVEL keys containing 'frontier', so the receipt was never "
                                    "graded by the DG-2 corpus audit of RV-377-068 and is not auditable by that "
                                    "instrument now. Rule 28 is satisfied in substance (the per-arm costs are printed "
                                    "per cell) and unsatisfied in form.")})
            continue
        r = audit_receipt(p)
        r["revival_record"] = d.get("revival_id") or r.get("revival_record")
        rows.append({k: v for k, v in r.items() if k not in ("crossovers_beyond_grid", "occupant_changes_beyond_grid",
                                                             "rows_denied_a_cell_by_truncation", "extension", "grid_H")})
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    receipt = {
        "schema": "GMI_B2_DG2_AUDIT_V1", "issue": [377, 422],
        "rule_audited": "protocol rule 28 and gap DG-2, over this lane's stage-B2 receipts only",
        "auditor": "gmi_microscope/grid_audit.py, family C (stage-B2 receipts, graded from their own carried per-row "
                   "cost coordinates; no generating module is imported and nothing is replayed)",
        "n_receipts": len(rows), "counts": counts,
        "receipts": rows,
        "no_frontier_is_not_a_pass": "a receipt listed NO_FRONTIER makes no frontier claim at all; it is neither SAFE "
                                     "nor TRUNCATED, and rule 28 does not apply to it",
        "claim_ceiling": "the audit is exact on the receipts whose cost lines are carried in the receipt itself; a SAFE "
                         "verdict is a statement about that receipt's own admissible set and price vectors, not about "
                         "rows or prices it never reported",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(RES, "STAGE_B2_DG2_AUDIT_V1.json"), "w"), indent=1, sort_keys=True,
              default=str)
    return receipt


if __name__ == "__main__":
    rc = main()
    print(rc["counts"])
    for r in rc["receipts"]:
        print("  %-11s %-42s %s" % (r["verdict"], r["receipt"],
                                    r.get("reason") or ("contexts=%s cells=%s grid_max=%s largest_crossover=%s" % (
                                        r.get("n_contexts"), r.get("n_cells_reproduced"), r.get("grid_max_H"),
                                        r.get("largest_crossover")))))
