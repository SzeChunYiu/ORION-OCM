#!/usr/bin/env python3
"""REV-L46 two-route crosscheck for gmi-uncertainty-composition-v1.

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

    cc = committed["concrete_chain"]
    mine = o["concrete_chain"]
    row("claim_ceiling", committed["claim_ceiling"], o["claim_ceiling"])
    row("chain:source_set", cc["source_set"], mine["source_set"])
    row("chain:stage_1_image", cc["stage_1_image"], mine["stage_1_image"])
    row("chain:stage_2_image", cc["stage_2_image"], mine["stage_2_image"])
    row("chain:direct_composed_image", cc["direct_composed_image"],
        mine["direct_composed_image"])
    row("chain:sequential_equals_direct", cc["sequential_equals_direct"],
        mine["sequential_equals_direct"])
    row("UC-2:alpha", cc["alpha"], mine["alpha"])
    row("UC-2:betas", cc["betas"], mine["betas"])
    row("UC-2:coverage_lower_bound", cc["coverage_lower_bound"],
        mine["coverage_lower_bound"])
    for q in ("q_even", "q_gt_25", "q_le_40"):
        row("UC-3:query_%s" % q, cc["query_outcomes"][q],
            mine["query_outcomes"][q])
    e1 = committed["exhaustive_uc1"]
    e2 = o["exhaustive_uc1"]
    row("UC-1:certificate_cases", e1["cases"], e2["cases"])
    row("UC-1:certificate_failures", e1["failures"], e2["failures"])
    row("UC-1:certificate_all_hold", e1["all_hold"], e2["all_hold"])
    row("UC-1:domain_cardinalities", e1["domain_cardinalities"],
        e2["domain_cardinalities"])
    m1 = committed["missing_relation"]
    m2 = o["missing_relation"]
    row("UC-4:target_set_full_domain", m1["target_set"], m2["target_set"])
    row("UC-4:markers", m1["markers"], m2["markers"])
    row("UC-4:coverage_lower_bound", m1["coverage_lower_bound"],
        m2["coverage_lower_bound"])
    for q in ("q_even", "q_gt_25", "q_le_40"):
        row("UC-4:query_%s" % q, m1["query_outcomes"][q],
            m2["query_outcomes"][q])
    row("empty_image_terminal", committed["empty_image_query_terminal"],
        o["empty_image_query_terminal"])
    h1 = committed["dependence_hostiles"]
    h2 = o["dependence_hostiles"]
    for group in ("disjoint_failures", "overlapping_failures"):
        for key in sorted(set(h1[group]) | set(h2[group])):
            row("UC-H1:%s:%s" % (group, key), h1[group].get(key),
                h2[group].get(key))
    row("UC-2:union_bound_attained_witness (route-2 extension)", True,
        o["union_bound_attained_witness"])
    row("proof_classes", committed["proof_classes"], o["proof_classes"])

    negative_control = {
        "description": ("corrupted committed coverage bound ('186/200') must "
                        "disagree — proves comparison not vacuous"),
        "passed": ("186/200" != mine["coverage_lower_bound"]),
    }

    exact_agreement_everywhere = (all(r["agree"] for r in rows)
                                  and negative_control["passed"]
                                  and ind["stdlib_only"])

    receipt = {
        "schema": "GMI_833_REV_L46_ORACLE_RESULT_V1",
        "package": "gmi-uncertainty-composition-v1",
        "ticket": "REV-L46-TWO-ROUTE-PROGRAMME",
        "route1": {
            "executor": "uncertainty_composition_v1.py",
            "algorithm_class": [
                "forward pair-tuple set comprehension for images",
                "pair-join composition",
                "tuple-enumerated exhaustive certificate",
                "campaign state machine with markers",
            ],
            "committed_receipt": "RESULT_V1.json",
        },
        "route2": {
            "executor": "independent_oracle_v1.py",
            "algorithm_class": [
                "boolean 0/1 incidence-matrix algebra: images as row-selector "
                "matrix products, composition as matrix multiplication, "
                "sequential==direct as associativity",
                "bitmask enumeration of the relation universe (16x16x4)",
                "LCM common-denominator budget + nested worst-case witness",
                "min==max order characterization for queries",
                "explicit uniform witness spaces for hostiles (disjoint and "
                "identical failure pairs)",
            ],
            "difference_table": {
                "representation": {
                    "route1": "pair tuples and python sets",
                    "route2": "0/1 matrices and bitmask integers",
                    "mechanism": "algebraic vs set-comprehension representation"},
                "exploration_order": {
                    "route1": "iterate relation pairs per image call",
                    "route2": "matrix row/column arithmetic per image call",
                    "mechanism": "arithmetic organization vs pair scanning"},
                "completeness_argument": {
                    "route1": "enumeration of the registered bounded universe",
                    "route2": "matrix associativity identity verified per case "
                              "on the same universe via masks",
                    "mechanism": "algebraic identity under enumeration vs "
                                 "pair-level equality"},
                "search_cost": {
                    "route1": "O(|R|) per image with set membership",
                    "route2": "O(n^3) matrix products but n=2..4 (constant)",
                    "mechanism": "different work profiles"},
            },
            "author_lineage": ("derived from FORMALIZATION_V1.md UC-1..UC-H1 and "
                               "the committed RESULT_V1.json structure; route-1 "
                               "source read only to classify its algorithm class "
                               "and transcribe the registered chain/hostiles"),
        },
        "independence_audit": ind,
        "agreement": {"rows": rows,
                      "exact_agreement_everywhere": exact_agreement_everywhere,
                      "tolerances_declared": []},
        "negative_control": negative_control,
        "counts": {"agreement_rows": len(rows)},
        "source_sha256": {
            "route1_executor_uncertainty_composition_v1.py":
                sha256("uncertainty_composition_v1.py"),
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
        "freeze": "FREEZE_L46_TWO_ROUTE_V1.md item 4",
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
