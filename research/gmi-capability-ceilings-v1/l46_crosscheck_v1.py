#!/usr/bin/env python3
"""REV-L46 two-route crosscheck for gmi-capability-ceilings-v1.

Route 2 (independent_oracle_v1.py) is compared against the package's
COMMITTED witnesses: the frozen registry F2_CEILINGS_V1.json and the frozen
test assertions of test_capability_ceilings_v1.py (transcribed below as the
committed value table — route-1 code is never executed). Writes
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

# Committed route-1 witness values, transcribed from the frozen test file
# test_capability_ceilings_v1.py (the package's P2 evidence layer).
COMMITTED = {
    "state_capacity": {"K3_S2": False, "K3_S3": True, "K1_S1": True},
    "observation": {"collision_bad": False, "collapse_realisable": True},
    "communication": {"K4_B2": True, "K5_B2": False, "min_bits_K5": 3,
                      "K3_B1": False, "K1_B0": True, "K2_B0_allows": False},
    "precision": {"capacity_B2_P4": 4, "cover_P4_B2": False,
                  "min_bits_P4": 3, "capacity_B2_P3": 4, "cover_P3_B2": True},
    "update": {"capacity_m2_s2": 4, "T5_m2_s2_allows": False,
               "T4_m2_s2_allows": True, "min_steps_T5_m2": 3,
               "decoder_T5": False, "decoder_T4": True},
    "protected_rank": {"rank_2rows": 2, "nullity_2rows_dim3": 1,
                       "frontier_plastic1": True, "frontier_plastic2": False,
                       "rank_redundant": 1, "nullity_redundant": 2,
                       "rank_fraction": 2},
    "planning": {"nodes_b2_h0": 1, "nodes_b2_h2": 7, "nodes_b2_h3": 15,
                 "nodes_b1_h4": 5, "budget_b2_h3_R14": False,
                 "budget_b2_h3_R15": True, "max_horizon_b2_R14": 2,
                 "max_horizon_b2_R15": 3, "max_horizon_b1_R5": 4,
                 "adversary_b2_h3_14": True, "adversary_b2_h3_15": False},
    "search": {"allows_5_4": False, "allows_5_5": True, "max_guaranteed_Q4": 4,
               "adversary_5_q0123": 4, "adversary_5_full": None,
               "adversary_5_q4201": 3, "invariance": True},
    "verification": {"fa_10_1_8": "1/5", "fa_10_1_10": "0",
                     "fa_6_2_2": "2/5", "exchangeability": True,
                     "min_checks_10_1_1_5": 8, "min_checks_10_1_0": 10,
                     "adversarial_zero_10_9": False, "adversarial_zero_10_10": True},
    "acquisition": {"capacity_o2_q2": 4, "allows_5_2_2": False,
                    "allows_4_2_2": True, "min_queries_1": 0,
                    "min_queries_5_o2": 3, "min_queries_9_o3": 2,
                    "max_queries_budget5_cost2": 2,
                    "budget_capacity_o2_b5_c2": 4,
                    "budget_capacity_o3_b6_c2": 27,
                    "separating_5_2_2": False, "separating_4_2_2": True},
    "social": {"base_response_identifiable": False,
               "diagnostic_response_identifiable": True,
               "base_model_identifiable": False,
               "diagnostic_model_identifiable": True,
               "base_class_count": 2, "diagnostic_class_count": 3,
               "same_response_identifiable": True},
    "registry": {"eleven_ids_in_order": True, "unique": True,
                 "row_fields_present": True, "claim_ceiling_G2": True,
                 "terminal": True, "schema": True, "evidence_class_P1_P2": True,
                 "eleven_parents": True},
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


def canon(value):
    # type: (object) -> object
    from fractions import Fraction
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return "%d" % value.numerator
        return "%d/%d" % (value.numerator, value.denominator)
    return value


def main():
    # type: () -> int
    ind = audit_independence()
    o = oracle.oracle_quantities()
    rows = []
    for section in sorted(COMMITTED):
        mine = o[section]
        for key in sorted(COMMITTED[section]):
            committed = COMMITTED[section][key]
            got = canon(mine[key])
            rows.append({"claim_id": "%s:%s" % (section, key),
                         "route1_value": committed,
                         "route2_value": got,
                         "agree": got == committed})

    negative_control = {
        "description": ("corrupted committed witness (communication:K4_B2 -> "
                        "False) must disagree — proves comparison not vacuous"),
        "passed": (canon(o["communication"]["K4_B2"]) != False),  # noqa: E712
    }

    exact_agreement_everywhere = (all(r["agree"] for r in rows)
                                  and negative_control["passed"]
                                  and ind["stdlib_only"])

    receipt = {
        "schema": "GMI_833_REV_L46_ORACLE_RESULT_V1",
        "package": "gmi-capability-ceilings-v1",
        "ticket": "REV-L46-TWO-ROUTE-PROGRAMME",
        "route1": {
            "executor": "capability_ceilings_v1.py",
            "algorithm_class": [
                "procedural registry validation with hardcoded id tuple",
                "exhaustive search over candidate codes/policies/decoders "
                "(caps 2,000,000)",
                "closed-form capacity formulas and log-based minimum-bit counts",
                "Gaussian-elimination rank",
            ],
            "committed_receipt": ("F2_CEILINGS_V1.json registry + "
                                  "test_capability_ceilings_v1.py frozen witnesses"),
        },
        "route2": {
            "executor": "independent_oracle_v1.py",
            "algorithm_class": [
                "pigeonhole injectivity counting + constructive witnesses (state)",
                "partition-lattice refinement algebra (observation, social)",
                "falling-factorial counting + constructive binary codes; "
                "doubling search for minima (no logarithms)",
                "gap-cell counting for threshold placements",
                "word-count bijection by integer decoding (update/acquisition)",
                "largest-nonsingular-minor enumeration with exact determinants (rank)",
                "node-count recurrence + incremental horizon walk (planning)",
                "set-complement adversary with permutation invariance (search)",
                "Pascal-recurrence binomial ratios + exchangeability symmetry "
                "(verification)",
            ],
            "difference_table": {
                "representation": {
                    "route1": "candidate spaces enumerated as explicit iterables",
                    "route2": "counting functions (falling factorials, binomials, "
                              "partitions) with constructive witnesses",
                    "mechanism": "existence by counting+construction vs search"},
                "exploration_order": {
                    "route1": "iterate candidates in enumeration order until one fits",
                    "route2": "algebraic decision then witness construction",
                    "mechanism": "no candidate iteration in route 2"},
                "completeness_argument": {
                    "route1": "exhaustive over the capped candidate space",
                    "route2": "injectivity/pigeonhole/partition-lattice theorems",
                    "mechanism": "counting proof vs exhaustive check"},
                "search_cost": {
                    "route1": "up to 2,000,000 candidates per boundary",
                    "route2": "polynomial counting/constructive work per boundary",
                    "mechanism": "asymptotically different work"},
            },
            "author_lineage": ("derived from FORMALIZATION_V1.md, the F2 registry, "
                               "and the frozen test witnesses; route-1 source read "
                               "only to classify its algorithm class and to "
                               "transcribe the registered social witness instance"),
        },
        "independence_audit": ind,
        "agreement": {"rows": rows,
                      "exact_agreement_everywhere": exact_agreement_everywhere,
                      "tolerances_declared": []},
        "negative_control": negative_control,
        "counts": {"agreement_rows": len(rows)},
        "source_sha256": {
            "route1_executor_capability_ceilings_v1.py": sha256("capability_ceilings_v1.py"),
            "route2_independent_oracle_v1.py": sha256("independent_oracle_v1.py"),
            "crosscheck_l46_crosscheck_v1.py": sha256("l46_crosscheck_v1.py"),
            "claim_spec_FORMALIZATION_V1.md": sha256("FORMALIZATION_V1.md"),
            "committed_registry_F2_CEILINGS_V1.json": sha256("F2_CEILINGS_V1.json"),
            "committed_witnesses_test_capability_ceilings_v1.py":
                sha256("test_capability_ceilings_v1.py"),
        },
        "environment": {"flags": "-I -B",
                        "execution_host_record": ("billy-laptop per "
                            "VERDICT_REGISTER_APPEND_REV_L46_V1.json "
                            "custody_chain; this receipt is host-independent "
                            "by design so any clean checkout reproduces it "
                            "byte-identically")},
        "verdict": ("TWO_ROUTE_CONVERTED" if exact_agreement_everywhere
                    else "TWO_ROUTE_WITH_FINDINGS"),
        "freeze": "FREEZE_L46_TWO_ROUTE_V1.md item 5",
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
