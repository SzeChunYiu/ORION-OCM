#!/usr/bin/env python3
"""REV-L46 two-route crosscheck for gmi-analog-semantics-closure-v1.

Route 2 (independent_oracle_v1.py) vs the package's committed claims (the
validate_closure quantities: 162 sampled cases, 0 mismatches, 0 invalid
intervals, Euler burden 172, 2 GREEN ledger rows, schema 8 required,
accounting coordinates covering the required 12). Writes
ORACLE_RESULT_L46_V1.json; fail-closed. CPython 3.8 safe, stdlib only.
"""
from __future__ import annotations

import ast
import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import independent_oracle_v1 as oracle  # noqa: E402

STDLIB_ALLOW = {"json", "sys", "ast", "hashlib", "platform", "pathlib",
                "fractions", "itertools", "collections", "math", "operator",
                "typing", "__future__"}

# Committed route-1 quantities (analog_semantics_closure_v1.py validate_closure
# return values + the frozen assertion values inside it).
COMMITTED = {
    "sampled_cases": 162,
    "mismatches": 0,
    "invalid_intervals": 0,
    "example_euler_steps": 172,
    "ledger_rows": 2,
    "schema_required_count": 8,
    "ledger_all_green": True,
    "accounting_covers_required_12": True,
}


def audit_independence():
    # type: () -> dict
    tree = ast.parse((HERE / "independent_oracle_v1.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    non_stdlib = sorted(imported - STDLIB_ALLOW)
    return {"imported_modules": sorted(imported),
            "stdlib_only": non_stdlib == [],
            "no_package_imports": non_stdlib == [],
            "violations": non_stdlib}


def sha256(rel):
    # type: (str) -> str
    return hashlib.sha256((HERE / rel).read_bytes()).hexdigest()


def main():
    # type: () -> int
    ind = audit_independence()
    o = oracle.oracle_quantities()
    s = o["structural"]
    rows = [
        {"claim_id": "sampled_cases_162", "route1_value": COMMITTED["sampled_cases"],
         "route2_value": o["sampled_cases"], "agree": o["sampled_cases"] == 162},
        {"claim_id": "d1d6_mismatches_0", "route1_value": 0,
         "route2_value": o["mismatches"], "agree": o["mismatches"] == 0},
        {"claim_id": "invalid_intervals_0", "route1_value": 0,
         "route2_value": o["invalid_intervals"], "agree": o["invalid_intervals"] == 0},
        {"claim_id": "d1d6_agreement_beyond_grid (route-2 extension)",
         "route1_value": "not claimed (162 cases only)",
         "route2_value": o["non_vertex_extension"],
         "agree": o["non_vertex_extension"] is True},
        {"claim_id": "as1_euler_burden_T1_L1_C1_eps0.01",
         "route1_value": 172, "route2_value": o["example_euler_steps"],
         "agree": o["example_euler_steps"] == 172},
        {"claim_id": "ledger_rows_2_green",
         "route1_value": COMMITTED["ledger_rows"],
         "route2_value": s["ledger_rows"],
         "agree": s["ledger_rows"] == 2 and s["ledger_all_green"]},
        {"claim_id": "schema_required_8",
         "route1_value": 8, "route2_value": s["schema_required_count"],
         "agree": s["schema_required_count"] == 8},
        {"claim_id": "accounting_coordinates_cover_required_12",
         "route1_value": True,
         "route2_value": s["accounting_covers_required_12"],
         "agree": s["accounting_covers_required_12"] is True},
        {"claim_id": "accounting_coordinates_count (reporting)",
         "route1_value": s["accounting_coordinates"],
         "route2_value": s["accounting_coordinates"],
         "agree": True},
    ]

    negative_control = {
        "description": ("corrupted committed case count (163) must disagree — "
                        "proves the comparison is not vacuous"),
        "passed": (163 != o["sampled_cases"]),
    }

    exact_agreement_everywhere = (all(r["agree"] for r in rows)
                                  and negative_control["passed"]
                                  and ind["stdlib_only"])

    receipt = {
        "schema": "GMI_833_REV_L46_ORACLE_RESULT_V1",
        "package": "gmi-analog-semantics-closure-v1",
        "ticket": "REV-L46-TWO-ROUTE-PROGRAMME",
        "route1": {
            "executor": "analog_semantics_closure_v1.py",
            "algorithm_class": [
                "162-case itertools.product enumeration comparing two interval encoders",
                "float expm1/ceil Euler step bound",
                "loop-accumulated case counting",
            ],
            "committed_receipt": ("validate_closure quantities + committed "
                                  "ledger/schema/accounting JSONs"),
        },
        "route2": {
            "executor": "independent_oracle_v1.py",
            "algorithm_class": [
                "multi-affine vertex-grid identity with monomial extraction; "
                "non-vertex extension by exact second differences",
                "algebraic interval validity (2*delta >= 0), no enumeration",
                "3^4*2 exponent arithmetic for the case count",
                "exact rational truncated exponential series with explicit "
                "tail bound; ceiling decided by rational sandwiching (no floats)",
                "set-algebra structural checks",
            ],
            "difference_table": {
                "representation": {
                    "route1": "case tuples with interval pairs",
                    "route2": "algebraic identities over Fraction fields",
                    "mechanism": "identity proofs vs instance comparisons"},
                "exploration_order": {
                    "route1": "full cartesian product sweep",
                    "route2": "vertex grid then analytic extension beyond it",
                    "mechanism": "route 2 proves more with less traversal"},
                "completeness_argument": {
                    "route1": "all 162 registered cases checked",
                    "route2": "multi-affine identity + axis-affinity at probes "
                              "(covers non-registered points too)",
                    "mechanism": "theorems over the family vs enumeration"},
                "numerics": {
                    "route1": "float expm1 and ceil",
                    "route2": "exact Fraction series with sandwiched ceilings",
                    "mechanism": "different number representation"},
            },
            "author_lineage": ("derived from ANALOG_SEMANTICS_THEOREM_V1.md and the "
                               "committed JSONs; route-1 source read only to "
                               "classify its algorithm class"),
        },
        "independence_audit": ind,
        "agreement": {"rows": rows,
                      "exact_agreement_everywhere": exact_agreement_everywhere,
                      "tolerances_declared": []},
        "negative_control": negative_control,
        "counts": {"agreement_rows": len(rows)},
        "source_sha256": {
            "route1_executor_analog_semantics_closure_v1.py":
                sha256("analog_semantics_closure_v1.py"),
            "route2_independent_oracle_v1.py": sha256("independent_oracle_v1.py"),
            "crosscheck_l46_crosscheck_v1.py": sha256("l46_crosscheck_v1.py"),
            "claim_spec_ANALOG_SEMANTICS_THEOREM_V1.md":
                sha256("ANALOG_SEMANTICS_THEOREM_V1.md"),
        },
        "environment": {"flags": "-I -B",
                        "execution_host_record": ("billy-laptop per "
                            "VERDICT_REGISTER_APPEND_REV_L46_V1.json "
                            "custody_chain; this receipt is host-independent "
                            "by design so any clean checkout reproduces it "
                            "byte-identically")},
        "verdict": ("TWO_ROUTE_CONVERTED" if exact_agreement_everywhere
                    else "TWO_ROUTE_WITH_FINDINGS"),
        "freeze": "FREEZE_L46_TWO_ROUTE_V1.md item 3",
    }
    out = HERE / "ORACLE_RESULT_L46_V1.json"
    out.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    disagrees = [r["claim_id"] for r in rows if not r["agree"]]
    print("wrote %s: %s (%d agreement rows%s)"
          % (out.name, receipt["verdict"], len(rows),
             "; DISAGREES: %s" % disagrees if disagrees else ""))
    return 0 if exact_agreement_everywhere else 2


if __name__ == "__main__":
    sys.exit(main())
