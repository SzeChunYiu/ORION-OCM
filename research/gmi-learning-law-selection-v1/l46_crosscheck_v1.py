#!/usr/bin/env python3
"""REV-L46 two-route crosscheck for gmi-learning-law-selection-v1.

Route 2 vs the committed claims (the frozen theorem tables 36/92/0 and
36/50/42, the LLS-3 flips, LLS-4/5 statements, and the committed
DEFERRED_EXECUTION_RECEIPT_V1.json). Route-1 code is never executed. Writes
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

COMMITTED = {
    "lls2_total": 128,
    "lls2_infeasible": 36,
    "lls6_generic": {"infeasible": 36, "selected": 92, "undetermined": 0},
    "lls6_uniform": {"infeasible": 36, "selected": 50, "undetermined": 42},
    "lls3_K1_admits": ["BAYES_UPDATE", "MIRROR_DESCENT"],
    "lls3_K1_cheap_gradient": "MIRROR_DESCENT",
    "lls3_K1_cheap_likelihood": "BAYES_UPDATE",
    "lls3_K2_admits": ["EXACT_SEARCH", "ORDINAL_HILL_CLIMB"],
    "lls3_K2_cheap_enum": "EXACT_SEARCH",
    "lls3_K2_cheap_cmp": "ORDINAL_HILL_CLIMB",
    "lls3_K3_admits": ["GRADIENT_STEP", "MIRROR_DESCENT"],
    "lls3_K3_cheap_proj": "GRADIENT_STEP",
    "lls3_K3_cheap_norm": "MIRROR_DESCENT",
    "deferred_held": 3,
    "deferred_total": 3,
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
    f = o["lls3_flips"]
    d = o["deferred_predictions"]
    rows = [
        {"claim_id": "LLS-2:total_128", "route1_value": COMMITTED["lls2_total"],
         "route2_value": o["lls2_total_contracts"],
         "agree": o["lls2_total_contracts"] == 128},
        {"claim_id": "LLS-2:infeasible_36 (law-event I-E)",
         "route1_value": 36, "route2_value": 128 - o["lls2_feasible_by_law_inclusion_exclusion"],
         "agree": 128 - o["lls2_feasible_by_law_inclusion_exclusion"] == 36},
        {"claim_id": "LLS-2:infeasible_36 (predicate-clause I-E)",
         "route1_value": 36,
         "route2_value": o["lls2_infeasible_by_predicate_inclusion_exclusion"],
         "agree": o["lls2_infeasible_by_predicate_inclusion_exclusion"] == 36},
        {"claim_id": "LLS-2:censuses_agree", "route1_value": True,
         "route2_value": o["lls2_censuses_agree"], "agree": o["lls2_censuses_agree"]},
        {"claim_id": "LLS-6:generic_census_36/92/0",
         "route1_value": COMMITTED["lls6_generic"],
         "route2_value": o["lls6_generic_census"],
         "agree": o["lls6_generic_census"] == COMMITTED["lls6_generic"]},
        {"claim_id": "LLS-6:genericity_proved_for_binary_family (route-2 extension)",
         "route1_value": "probed on two generic vectors",
         "route2_value": o["lls6_binary_uniqueness_proven"],
         "agree": o["lls6_binary_uniqueness_proven"] is True},
        {"claim_id": "LLS-6:uniform_census_36/50/42",
         "route1_value": COMMITTED["lls6_uniform"],
         "route2_value": o["lls6_uniform_census"],
         "agree": o["lls6_uniform_census"] == COMMITTED["lls6_uniform"]},
        {"claim_id": "LLS-6:genericity_load_bearing", "route1_value": True,
         "route2_value": o["lls6_genericity_load_bearing"],
         "agree": o["lls6_genericity_load_bearing"] is True},
        {"claim_id": "LLS-3:K1_admits", "route1_value": COMMITTED["lls3_K1_admits"],
         "route2_value": f["K1_admits"],
         "agree": f["K1_admits"] == COMMITTED["lls3_K1_admits"]},
        {"claim_id": "LLS-3:K1_cheap_gradient", "route1_value": COMMITTED["lls3_K1_cheap_gradient"],
         "route2_value": f["K1_cheap_gradient_selects"],
         "agree": f["K1_cheap_gradient_selects"] == COMMITTED["lls3_K1_cheap_gradient"]},
        {"claim_id": "LLS-3:K1_cheap_likelihood", "route1_value": COMMITTED["lls3_K1_cheap_likelihood"],
         "route2_value": f["K1_cheap_likelihood_selects"],
         "agree": f["K1_cheap_likelihood_selects"] == COMMITTED["lls3_K1_cheap_likelihood"]},
        {"claim_id": "LLS-3:K2_admits", "route1_value": COMMITTED["lls3_K2_admits"],
         "route2_value": f["K2_admits"],
         "agree": f["K2_admits"] == COMMITTED["lls3_K2_admits"]},
        {"claim_id": "LLS-3:K2_cheap_enum", "route1_value": COMMITTED["lls3_K2_cheap_enum"],
         "route2_value": f["K2_cheap_enum_selects"],
         "agree": f["K2_cheap_enum_selects"] == COMMITTED["lls3_K2_cheap_enum"]},
        {"claim_id": "LLS-3:K2_cheap_cmp", "route1_value": COMMITTED["lls3_K2_cheap_cmp"],
         "route2_value": f["K2_cheap_cmp_selects"],
         "agree": f["K2_cheap_cmp_selects"] == COMMITTED["lls3_K2_cheap_cmp"]},
        {"claim_id": "LLS-3:K3_admits", "route1_value": COMMITTED["lls3_K3_admits"],
         "route2_value": f["K3_admits"],
         "agree": f["K3_admits"] == COMMITTED["lls3_K3_admits"]},
        {"claim_id": "LLS-3:K3_cheap_proj", "route1_value": COMMITTED["lls3_K3_cheap_proj"],
         "route2_value": f["K3_cheap_proj_selects"],
         "agree": f["K3_cheap_proj_selects"] == COMMITTED["lls3_K3_cheap_proj"]},
        {"claim_id": "LLS-3:K3_cheap_norm", "route1_value": COMMITTED["lls3_K3_cheap_norm"],
         "route2_value": f["K3_cheap_norm_selects"],
         "agree": f["K3_cheap_norm_selects"] == COMMITTED["lls3_K3_cheap_norm"]},
        {"claim_id": "LLS-4:projection_hiding_witness", "route1_value": True,
         "route2_value": o["lls4_projection_hiding"]["same_projection"]
                         and o["lls4_projection_hiding"]["different_admissible_sets"],
         "agree": bool(o["lls4_projection_hiding"]["same_projection"]
                       and o["lls4_projection_hiding"]["different_admissible_sets"])},
        {"claim_id": "LLS-5:empty_contract_infeasible", "route1_value": True,
         "route2_value": o["lls5_refusals"]["empty_contract_infeasible"],
         "agree": o["lls5_refusals"]["empty_contract_infeasible"] is True},
        {"claim_id": "LLS-5:missing_price_raises", "route1_value": True,
         "route2_value": o["lls5_refusals"]["missing_price_raises"],
         "agree": o["lls5_refusals"]["missing_price_raises"] is True},
        {"claim_id": "LLS-5:float_prices_refused", "route1_value": True,
         "route2_value": o["lls5_refusals"]["float_prices_refused"],
         "agree": o["lls5_refusals"]["float_prices_refused"] is True},
        {"claim_id": "deferred:held_3_of_3", "route1_value": COMMITTED["deferred_held"],
         "route2_value": d["held"],
         "agree": d["held"] == d["total"] == 3},
        {"claim_id": "deferred:digest_matches_frozen_predictions", "route1_value": True,
         "route2_value": d["receipt_digest_matches_frozen_predictions"],
         "agree": d["receipt_digest_matches_frozen_predictions"] is True},
    ]

    negative_control = {
        "description": ("corrupted committed infeasible count (35) must "
                        "disagree — proves comparison not vacuous"),
        "passed": (35 != 128 - o["lls2_feasible_by_law_inclusion_exclusion"]),
    }

    exact_agreement_everywhere = (all(r["agree"] for r in rows)
                                  and negative_control["passed"]
                                  and ind["stdlib_only"])

    receipt = {
        "schema": "GMI_833_REV_L46_ORACLE_RESULT_V1",
        "package": "gmi-learning-law-selection-v1",
        "ticket": "REV-L46-TWO-ROUTE-PROGRAMME",
        "route1": {
            "executor": "learning_law_selection_v1.py",
            "algorithm_class": [
                "full enumeration of 128 capability sets via itertools.product",
                "per-set premise-subset admissibility checks",
                "two explicitly probed generic price vectors for LLS-6",
            ],
            "committed_receipt": ("LEARNING_LAW_SELECTION_THEOREM_V1.md frozen "
                                  "tables + DEFERRED_EXECUTION_RECEIPT_V1.json"),
        },
        "route2": {
            "executor": "independent_oracle_v1.py",
            "algorithm_class": [
                "inclusion-exclusion over law-admissibility events AND over "
                "predicate clauses (two independent counts of 36, no "
                "capability-set enumeration)",
                "binary-representation uniqueness theorem for generic "
                "tie-freeness (proves LLS-6 for the whole power-of-two "
                "family; route 1 probed two vectors)",
                "arity-partition explanation of the uniform-price ties",
                "adversarial price constructions with strict-inequality "
                "uniqueness verification (LLS-3)",
                "explicit projection-hiding two-contract witness (LLS-4)",
                "functional refusal semantics (LLS-5)",
            ],
            "difference_table": {
                "representation": {
                    "route1": "capability bitmasks with per-set subset tests",
                    "route2": "event algebra over premise blocks + price-family "
                              "theorems",
                    "mechanism": "counting algebra vs instance enumeration"},
                "exploration_order": {
                    "route1": "row-major product over 128 sets",
                    "route2": "I-E block sums; adversarial witness vectors; "
                              "binary-price totals (census kept as verification)",
                    "mechanism": "counting first, enumeration only to verify"},
                "completeness_argument": {
                    "route1": "checked all 128 sets on two generic vectors",
                    "route2": "multiset-distinctness theorem covers ALL binary "
                              "price vectors at once",
                    "mechanism": "family-level proof vs vector-level probing"},
                "search_cost": {
                    "route1": "O(128 x |L|) per price vector probed",
                    "route2": "O(2^5) I-E terms for the census counts",
                    "mechanism": "different work profiles"},
            },
            "author_lineage": ("derived from LEARNING_LAW_SELECTION_THEOREM_V1.md "
                               "and the committed receipt; route-1 source read only "
                               "to classify its algorithm class"),
        },
        "independence_audit": ind,
        "agreement": {"rows": rows,
                      "exact_agreement_everywhere": exact_agreement_everywhere,
                      "tolerances_declared": []},
        "negative_control": negative_control,
        "counts": {"agreement_rows": len(rows)},
        "source_sha256": {
            "route1_executor_learning_law_selection_v1.py":
                sha256("learning_law_selection_v1.py"),
            "route2_independent_oracle_v1.py": sha256("independent_oracle_v1.py"),
            "crosscheck_l46_crosscheck_v1.py": sha256("l46_crosscheck_v1.py"),
            "claim_spec_LEARNING_LAW_SELECTION_THEOREM_V1.md":
                sha256("LEARNING_LAW_SELECTION_THEOREM_V1.md"),
            "committed_receipt_DEFERRED_EXECUTION_RECEIPT_V1.json":
                sha256("DEFERRED_EXECUTION_RECEIPT_V1.json"),
        },
        "environment": {"host": platform.node(),
                        "python": platform.python_version(),
                        "flags": "-I -B"},
        "verdict": ("TWO_ROUTE_CONVERTED" if exact_agreement_everywhere
                    else "TWO_ROUTE_WITH_FINDINGS"),
        "freeze": "FREEZE_L46_TWO_ROUTE_V1.md item 8",
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
