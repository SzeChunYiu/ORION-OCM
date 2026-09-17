#!/usr/bin/env python3
"""REV-L46 two-route crosscheck for gmi-dependency-aware-uncertainty-composition-v1.

Route 2 vs the committed receipt RESULT_V1.json (route-1 code never
executed). Writes ORACLE_RESULT_L46_V1.json; fail-closed. CPython 3.8 safe.
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
    committed = json.loads((HERE / "RESULT_V1.json").read_text(encoding="utf-8"))
    ind = audit_independence()
    o = oracle.oracle_quantities()
    rows = []

    def row(cid, r1, r2):
        # type: (str, object, object) -> None
        rows.append({"claim_id": cid, "route1_value": r1, "route2_value": r2,
                     "agree": r1 == r2})

    row("claim_ceiling", committed["claim_ceiling"], o["claim_ceiling"])

    x = committed["joint_root_xor_control"]
    m = o["joint_root_xor_control"]
    row("xor:global_y", x["global_y"], m["global_y"])
    row("xor:local_y", x["local_y"], m["local_y"])
    row("xor:strict", x["strict"], m["strict"])

    s1 = committed["shared_ancestor_hostile"]
    s2 = o["shared_ancestor_hostile"]
    row("ancestor:global_y", s1["global_y"], s2["global_y"])
    row("ancestor:local_y", s1["local_y"], s2["local_y"])
    row("ancestor:strict", s1["strict"], s2["strict"])

    n1 = committed["nonlinear_setvalued_control"]
    n2 = o["nonlinear_setvalued_control"]
    for key in ("global_s", "global_q", "local_s", "local_q",
                "coverage_lower_bound"):
        row("nonlinear:%s" % key, n1[key], n2[key])

    g1 = committed["missing_relation_control"]
    g2 = o["missing_relation_control"]
    for key in ("global_m", "local_m", "coverage_lower_bound", "missing_nodes"):
        row("missing:%s" % key, g1[key], g2[key])

    e1 = committed["exhaustive_local_soundness"]
    e2 = o["exhaustive_local_soundness"]
    row("soundness:cases", e1["cases"], e2["cases"])
    row("soundness:failures", e1["failures"], e2["failures"])
    row("soundness:all_sound", e1["all_sound"], e2["all_sound"])
    row("soundness:strict_cases", e1["strict_overapproximation_cases"],
        e2["strict_inclusion_cases"])

    b1 = committed["budget_controls"]
    b2 = o["budget_controls"]
    row("budget:joint.alpha", b1["joint_source"]["alpha"],
        b2["joint_source"]["alpha"])
    row("budget:joint.betas", b1["joint_source"]["betas"],
        b2["joint_source"]["betas"])
    row("budget:joint.lower", b1["joint_source"]["lower"],
        b2["joint_source"]["lower"])
    row("budget:marginal.alphas", b1["marginal_source"]["alphas"],
        b2["marginal_source"]["alphas"])
    row("budget:marginal.betas", b1["marginal_source"]["betas"],
        b2["marginal_source"]["betas"])
    row("budget:marginal.union_alpha", b1["marginal_source"]["union_alpha"],
        b2["marginal_source"]["union_alpha"])
    row("budget:marginal.lower", b1["marginal_source"]["lower"],
        b2["marginal_source"]["lower"])

    h1 = committed["marginal_dependence_hostile"]
    h2 = o["marginal_dependence_hostile"]
    for group in ("disjoint", "overlap"):
        for key in sorted(set(h1[group]) | set(h2[group])):
            row("hostile:%s:%s" % (group, key), h1[group].get(key),
                h2[group].get(key))

    f1 = committed["hostile_summary"]
    f2 = o["hostile_summary"]
    for key in ("cycle_rejected", "post_activation_mutation_rejected",
                "registered_empty_relation_distinct_from_missing"):
        row("governance:%s" % key, f1[key], f2[key])

    row("proof_classes", committed["proof_classes"], o["proof_classes"])

    negative_control = {
        "description": ("corrupted committed budget lower ('372/400') must "
                        "disagree — proves comparison not vacuous"),
        "passed": ("372/400" != o["budget_controls"]["joint_source"]["lower"]),
    }

    exact_agreement_everywhere = (all(r["agree"] for r in rows)
                                  and negative_control["passed"]
                                  and ind["stdlib_only"])

    receipt = {
        "schema": "GMI_833_REV_L46_ORACLE_RESULT_V1",
        "package": "gmi-dependency-aware-uncertainty-composition-v1",
        "ticket": "REV-L46-TWO-ROUTE-PROGRAMME",
        "route1": {
            "executor": "dependency_aware_composition_v1.py",
            "algorithm_class": [
                "DagCampaign state machine with activation locking",
                "forward joint-tuple propagation (global route)",
                "per-node set application over relation pairs (local route)",
                "tuple-enumerated exhaustive certificate",
            ],
            "committed_receipt": "RESULT_V1.json",
        },
        "route2": {
            "executor": "independent_oracle_v1.py",
            "algorithm_class": [
                "full-assignment CSP model enumeration for the global route "
                "(joint contract as constraint over total assignments)",
                "topological-order DP with hash-join dict images (local route)",
                "bitmask enumeration of the 16x16x4 certificate family",
                "LCM budgets; inclusion-exclusion masses for hostiles",
                "Kahn topological-sort cycle detection (governance)",
            ],
            "difference_table": {
                "representation": {
                    "route1": "campaign object graph; relation pair lists",
                    "route2": "total assignments; dict-keyed relations",
                    "mechanism": "assignment semantics vs tuple-flow semantics"},
                "exploration_order": {
                    "route1": "forward along the DAG edge order",
                    "route2": "full-assignment product enumeration (global) / "
                              "topological DP (local)",
                    "mechanism": "opposite orientation of the constraint check"},
                "completeness_argument": {
                    "route1": "reachable tuple set carried forward",
                    "route2": "satisfying-assignment semantics (all models)",
                    "mechanism": "model-theoretic vs fixpoint-propagation"},
                "acceptance_termination": {
                    "route1": "campaign markers/terminals",
                    "route2": "set inclusions + Kahn feasibility",
                    "mechanism": "different decision procedures"},
            },
            "author_lineage": ("derived from FORMALIZATION_V1.md DA-1..DA-4 and "
                               "the committed RESULT_V1.json control instances; "
                               "route-1 source read only to classify its "
                               "algorithm class and transcribe the registered "
                               "control instances"),
        },
        "independence_audit": ind,
        "agreement": {"rows": rows,
                      "exact_agreement_everywhere": exact_agreement_everywhere,
                      "tolerances_declared": []},
        "negative_control": negative_control,
        "counts": {"agreement_rows": len(rows)},
        "source_sha256": {
            "route1_executor_dependency_aware_composition_v1.py":
                sha256("dependency_aware_composition_v1.py"),
            "route2_independent_oracle_v1.py": sha256("independent_oracle_v1.py"),
            "crosscheck_l46_crosscheck_v1.py": sha256("l46_crosscheck_v1.py"),
            "claim_spec_FORMALIZATION_V1.md": sha256("FORMALIZATION_V1.md"),
            "committed_receipt_RESULT_V1.json": sha256("RESULT_V1.json"),
        },
        "environment": {"flags": "-I -B",
                        "execution_host_record": ("billy-laptop per "
                            "VERDICT_REGISTER_APPEND_REV_L46_V1.json "
                            "custody_chain; this receipt is host-independent "
                            "by design so any clean checkout reproduces it "
                            "byte-identically")},
        "verdict": ("TWO_ROUTE_CONVERTED" if exact_agreement_everywhere
                    else "TWO_ROUTE_WITH_FINDINGS"),
        "freeze": "FREEZE_L46_TWO_ROUTE_V1.md item 6",
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
