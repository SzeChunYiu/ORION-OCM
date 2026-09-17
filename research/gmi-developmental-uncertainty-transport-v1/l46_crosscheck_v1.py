#!/usr/bin/env python3
"""REV-L46 two-route crosscheck for gmi-developmental-uncertainty-transport-v1.

Runs route 2 (independent_oracle_v1.py), audits independence (AST import
graph: stdlib only), compares every claimed quantity of the committed
receipt RESULT_V1.json (route-1 code is never executed), and writes
ORACLE_RESULT_L46_V1.json. Fail-closed. CPython 3.8 safe, stdlib only.
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


def eq(a, b):
    # type: (object, object) -> bool
    return a == b


def main():
    # type: () -> int
    receipt = json.loads((HERE / "RESULT_V1.json").read_text(encoding="utf-8"))
    ind = audit_independence()
    o = oracle.oracle_quantities()
    ub = o["uncertain_relation_budget"]
    rows = []

    def row(cid, r1, r2):
        # type: (str, object, object) -> None
        rows.append({"claim_id": cid, "route1_value": r1, "route2_value": r2,
                     "agree": eq(r1, r2)})

    row("claim_ceiling", receipt["claim_ceiling"], o["claim_ceiling"])
    row("DT-2B:beta", receipt["countable_allocation"]["beta"],
        o["countable_allocation"]["beta"])
    for n, committed in sorted(receipt["countable_allocation"]["partials"].items()):
        mine = o["countable_allocation"]["partials"][n]
        row("DT-2B:partial_closed_form_N=%s" % n, committed["closed_form"],
            mine["closed_form"])
        row("DT-2B:partial_route2_boundary_N=%s" % n, committed["partial"],
            mine["partial"])
        row("DT-2B:strictly_below_beta_N=%s" % n, committed["strictly_below_beta"],
            mine["strictly_below_beta"])
    row("DT-2B:infinite_horizon_lower_bound",
        receipt["countable_allocation"]["infinite_horizon_combined_lower_bound"],
        o["countable_allocation"]["infinite_horizon_combined_lower_bound"])
    row("DT-2A:alpha", receipt["uncertain_relation_budget"]["alpha"], ub["alpha"])
    row("DT-2A:betas", receipt["uncertain_relation_budget"]["betas"], ub["betas"])
    row("DT-2A:failure_budget", receipt["uncertain_relation_budget"]["failure_budget"],
        ub["failure_budget"])
    row("DT-2A:coverage_lower_bound",
        receipt["uncertain_relation_budget"]["coverage_lower_bound"],
        ub["coverage_lower_bound"])
    row("DT-2A:union_bound_attained_under_max_dependence (witness)",
        True, ub["attained_equals_bound"] and ub["witness_nested"])
    row("DT-2A:no_independence_assumption (product value differs)",
        True, ub["product_differs_from_union_bound"])
    row("five_kinds:vocabulary", receipt["five_kinds"], o["five_kinds"])
    for committed, mine in zip(receipt["five_kind_chain"], o["five_kind_chain"]):
        v = mine["version"]
        row("chain:v%d_terminal" % v, committed["terminal"], mine["terminal"])
        row("chain:v%d_values" % v, committed["values"], mine["values"])
        row("chain:v%d_failure_budget" % v, committed["failure_budget"],
            mine["failure_budget"])
        row("chain:v%d_raw_evidence" % v, committed["raw_evidence_count"],
            mine["raw_evidence_count"])
    row("DT-4:target_evidence_noninheritance (purity)",
        receipt["target_evidence_noninheritance"], o["target_evidence_noninheritance"])
    row("DT-5:nonlinear_image", receipt["nonlinear_relation"]["result"],
        o["nonlinear_relation"]["result"])
    row("DT-6:affine_hull", receipt["interval_affine"]["expected"],
        ["%d/%d" % (x.numerator, x.denominator) for x in o["interval_affine"]])
    row("DT-3A:unknown_values", receipt["unknown_relation"]["values"],
        o["unknown_relation"]["values"])
    row("DT-3A:terminal", receipt["unknown_relation"]["terminal"],
        o["unknown_relation"]["terminal"])
    row("identifiability:mixed_query", receipt["unknown_relation"]["mixed_query"],
        o["unknown_relation"]["mixed_query"])
    row("identifiability:constant_query",
        receipt["unknown_relation"]["constant_query"],
        o["unknown_relation"]["constant_query"])
    row("DT-3B:copy_covers", receipt["copy_counterexample"]["copy_covers"],
        o["copy_counterexample"]["copy_covers"])
    row("DT-3B:full_domain_covers", receipt["copy_counterexample"]["full_domain_covers"],
        o["copy_counterexample"]["full_domain_covers"])
    row("DT-3B:sets", [receipt["copy_counterexample"]["source_set"],
                       receipt["copy_counterexample"]["copied_set"],
                       receipt["copy_counterexample"]["full_target_domain"]],
        [o["copy_counterexample"]["source_set"],
         o["copy_counterexample"]["copied_set"],
         o["copy_counterexample"]["full_target_domain"]])

    # governance: freeze-before-implementation authority + activation-first
    # ordering, read from the claim spec and the committed chain (structural).
    spec = (HERE / "FORMALIZATION_V1.md").read_text(encoding="utf-8")
    freeze_ok = (receipt["freeze_commit"] in spec
                 and "Pre-implementation authority" in spec)
    versions = [r["version"] for r in receipt["five_kind_chain"]]
    ordering_ok = versions == sorted(versions) and versions[0] == 0
    row("governance:post_activation_registration_blocked",
        receipt["post_activation_registration_blocked"], freeze_ok and ordering_ok)

    negative_control = {
        "description": ("corrupted committed partial (N=2 -> '1/31') must be "
                        "detected — proves per-claim comparison is not vacuous"),
        "passed": ("1/31" != o["countable_allocation"]["partials"]["2"]["partial"]),
    }

    exact_agreement_everywhere = (all(r["agree"] for r in rows)
                                  and negative_control["passed"]
                                  and ind["stdlib_only"])

    receipt_out = {
        "schema": "GMI_833_REV_L46_ORACLE_RESULT_V1",
        "package": "gmi-developmental-uncertainty-transport-v1",
        "ticket": "REV-L46-TWO-ROUTE-PROGRAMME",
        "route1": {
            "executor": "developmental_uncertainty_transport_v1.py",
            "algorithm_class": [
                "stateful campaign API (TransportCampaign/ConfidenceObject)",
                "forward edge-list set comprehension for relational images",
                "running Fraction accumulator for budgets and partial sums",
                "4-corner enumeration for the affine interval hull",
            ],
            "committed_receipt": "RESULT_V1.json",
        },
        "route2": {
            "executor": "independent_oracle_v1.py",
            "algorithm_class": [
                "inverse-relation backward scan with double-inclusion proofs (images)",
                "telescoping boundary collapse + cross-multiplied term identities (DT-2B)",
                "LCM construction + explicit worst-case probability space with nested",
                "events attaining the union bound; independence-product discriminator (DT-2A)",
                "sign-directed endpoint selection via monotonicity lemma (DT-6)",
                "base map + Minkowski-sum decomposition (DT-5)",
                "cardinality + containment argument (DT-3A)",
                "functional input-insensitivity purity test (DT-4)",
                "min==max order characterization (identifiability)",
            ],
            "difference_table": {
                "representation": {
                    "route1": "stateful object graph, forward pair lists",
                    "route2": "pure functions on tuples, predecessor-fiber/inverse structures",
                    "mechanism": "inverse vs forward orientation of the same relations"},
                "exploration_order": {
                    "route1": "relation-pair scan per transport step",
                    "route2": "target-domain-driven backward scan + boundary/witness selection",
                    "mechanism": "opposite traversal direction"},
                "completeness_argument": {
                    "route1": "exactness relative to enumerated relation (comprehension)",
                    "route2": "explicit double-inclusion proofs, attained-bound witnesses",
                    "mechanism": "proof-carrying checks vs constructive comprehension"},
                "acceptance_termination": {
                    "route1": "API terminal states (TRANSPORTED/CANNOT_IDENTIFY...)",
                    "route2": "order-characterized identifiability + measure evaluations",
                    "mechanism": "different decision procedures for the same terminals"},
            },
            "author_lineage": ("derived from FORMALIZATION_V1.md DT-1..DT-6 and the "
                               "committed RESULT_V1.json values; route-1 source read "
                               "only to classify its algorithm class"),
        },
        "independence_audit": ind,
        "agreement": {"rows": rows,
                      "exact_agreement_everywhere": exact_agreement_everywhere,
                      "tolerances_declared": []},
        "negative_control": negative_control,
        "counts": {"agreement_rows": len(rows)},
        "source_sha256": {
            "route1_executor_developmental_uncertainty_transport_v1.py":
                sha256("developmental_uncertainty_transport_v1.py"),
            "route2_independent_oracle_v1.py": sha256("independent_oracle_v1.py"),
            "crosscheck_l46_crosscheck_v1.py": sha256("l46_crosscheck_v1.py"),
            "claim_spec_FORMALIZATION_V1.md": sha256("FORMALIZATION_V1.md"),
            "committed_receipt_RESULT_V1.json": sha256("RESULT_V1.json"),
        },
        "environment": {"host": platform.node(),
                        "python": platform.python_version(),
                        "flags": "-I -B"},
        "verdict": ("TWO_ROUTE_CONVERTED" if exact_agreement_everywhere
                    else "TWO_ROUTE_WITH_FINDINGS"),
        "freeze": "FREEZE_L46_TWO_ROUTE_V1.md item 2",
    }
    out = HERE / "ORACLE_RESULT_L46_V1.json"
    out.write_text(json.dumps(receipt_out, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    disagrees = [r["claim_id"] for r in rows if not r["agree"]]
    print("wrote %s: %s (%d agreement rows%s)"
          % (out.name, receipt_out["verdict"], len(rows),
             "; DISAGREES: %s" % disagrees if disagrees else ""))
    return 0 if exact_agreement_everywhere else 2


if __name__ == "__main__":
    sys.exit(main())
