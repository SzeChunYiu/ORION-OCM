# -*- coding: utf-8 -*-
"""Merge the five stage receipts into RESULT_V1.json, the package's machine-readable
receipt: one entry per named result FX-1 .. FX-6 with the exact numbers each row of the
reconciliation quotes, the claim ceiling and forbidden promotions from the freeze.

    python3 -I -B build_result_v1.py            # write RESULT_V1.json
    python3 -I -B build_result_v1.py --check    # rebuild in memory and require byte equality
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

CEILING = "AJ15_FLAGSHIP_END_TO_END_EXECUTED_WITH_FAMILY_REGISTRY_HIDDEN_AT_REGISTERED_FINITE_B1_AND_B2_SCOPES"
FORBIDDEN = ["NAMED_FAMILY_RECOVERED", "FAMILY_IDENTITY_FROM_OPERATIONAL_EQUIVALENCE", "PREDICTED_SELECTED",
             "PREDICTED_SELECTED_FOR_ALL_FAMILIES", "REAL_SCALE_VALIDATION", "INDEPENDENT_TEAM_REPLICATION",
             "M5", "GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE", "FULL_GMI_THEORY_SUPPORTED_AT_DECLARED_SCOPE",
             "NOVEL_MI_DISCOVERED", "LITERAL_HISTORICAL_IGNORANCE_PROVED", "FAMILY_INEVITABILITY",
             "ALL_MACHINE_INTELLIGENCES_COMPLETELY_CLASSIFIED", "AJ16_EARNED", "COMPLETE_GMI"]


def load(name):
    return _load_json(os.path.join(HERE, name))


def build():
    b = load("BLIND_OUTCOME_V1.json")
    o = load("ORACLE_RESULT_V1.json")
    p = load("POSTHOC_RESULT_V1.json")
    l = load("LADDER_RESULT_V1.json")
    lo = load("LADDER_ORACLE_RESULT_V1.json")
    regimes = {t: {"exact_solvers": r["exact_solvers"], "with_state_dependent_output": r["with_state_dependent_output"],
                   "memoryless_realizable": r["memoryless_realizable"],
                   "K02_fingerprint_passes_posthoc": p["per_regime"][t]["K02_fingerprint_passes"],
                   "unknown_channel": p["per_regime"][t]["unknown_channel"],
                   "unknown_parent_reduced": p["per_regime"][t]["unknown_parent_reduced"]}
               for t, r in b["B1"]["regimes"].items()}
    b2 = {t: {"S1_terminal": r["terminal"], "S1_evaluations": r["evaluations"],
              "S2_terminal": o["B2_S2"][t]["terminal"], "S2_residual_classes": o["B2_S2"][t]["residual_classes"],
              "S1_solver_certified_all_words_by_route_B": o["S1_solvers_certified_by_route_B"][t]["certified"],
              "state_dependent_output": r["state_dependent_output"],
              "posthoc": (p["B2"][t]["adjudication"]["registered_family"] if isinstance(p["B2"][t]["adjudication"], dict) else None)}
          for t, r in b["B2"]["regimes"].items()}
    unknown_total = sum(v["unknown_channel"] for v in regimes.values()) + (1 if b2["identity"]["posthoc"] is None else 0)
    reduced_total = sum(v["unknown_parent_reduced"] for v in regimes.values()) + (1 if b2["identity"]["posthoc"] is None else 0)
    hostiles = {}
    for src in (b["hostiles"], p["hostiles"], l["hostiles"]):
        for k, v in src.items():
            hostiles[k] = {"applicable": v["applicable"], "detected": v["detected"], "planted": v["planted"]}
    n1 = Fraction(b["nulls"]["N1"]["rate"])
    results = {
        "FX-1": {"universe_B1_presentations": b["B1"]["presentations"], "operational_classes": b["B1"]["operational_classes"],
                 "pair_checks": b["B1"]["pair_checks"], "equivalent_pairs": b["B1"]["equivalent_pairs"],
                 "atlas_sha256": b["B1"]["atlas_sha256"], "regimes": regimes,
                 "regime_prediction_verdict_route_A": b["B1"]["verdict"], "regime_prediction_verdict_route_B": o["verdict"],
                 "posthoc_agrees_with_frozen_prediction": p["posthoc_agrees_with_frozen_prediction"],
                 "universe_constructed_before_registry_freeze": b["universe_provenance"]},
        "FX-2": {"unknown_channel_solvers_total": unknown_total, "unknown_parent_reduced_total": reduced_total,
                 "novel_form_claimed": p["novel_form_claimed"], "novel_replication_gate": p["novel_replication_gate"],
                 "registered_fingerprint_recoveries_B1": sum(v["K02_fingerprint_passes_posthoc"] for v in regimes.values()),
                 "same_run_produces_both": True},
        "FX-3": {"universe_B2_presentations": b["B2"]["presentations"], "enumerated": b["B2"]["enumerated"], "regimes": b2,
                 "honest_failure_terminal_exercised_on": [t for t, v in b2.items() if v["S1_terminal"] == "NOT_RECOVERED_AT_SCOPE"],
                 "independent_search_implementations": ["S1 hill-climb (route A)", "S2 residual construction (route B)"],
                 "independent_team_replication_claimed": False},
        "FX-4": {"hostiles": hostiles, "hostiles_applicable_and_detected": sum(1 for h in hostiles.values() if h["applicable"] and h["detected"]),
                 "hostiles_total": len(hostiles),
                 "N1_state_dependence_rate_random_B1": b["nulls"]["N1"]["rate"], "N1_strictly_between_0_and_1": 0 < n1 < 1,
                 "N2_chance_B1": b["nulls"]["N2"]["B1"]["chance"], "N2_chance_B2": b["nulls"]["N2"]["B2"]["chance"],
                 "N2_joint_chance": b["nulls"]["N2"]["joint_chance"],
                 "N3_random_B2_delay2_solvers": "%d/%d" % (b["nulls"]["N3"]["exact_delay2_solvers"], b["nulls"]["N3"]["draws"]),
                 "falsifier_live": hostiles["H3"]["detected"], "falsified_claim_under_H3": "SEEN_UNSEEN_REGIME_CONDITIONAL_RECOVERY_AT_SCOPE"},
        "FX-5": {"aj13_criteria_satisfied": l["aj13"]["criteria_satisfied"], "aj13_terminal": l["aj13"]["terminal"],
                 "aj14_earned_badges": l["aj14_earned_badges"], "aj14_unearned_badges": l["aj14_unearned_badges"],
                 "full_gmi_supported_now": l["full_gmi_supported_now"], "blocking_gates": l["blocking_gates"],
                 "route_B_ladder_agrees": lo["status"] == "GREEN",
                 "independent_oracle_for_parent_receipts": {"aj11": o["aj11_independent_oracle"], "aj13_aj14": l["parent_receipt_pins"]}},
        "FX-6": {"registry_read_in_blind_stage": b["registry_read"] or o["registry_read"],
                 "adjudication_started_after_blind_outcome": p["adjudication_started_after_blind_outcome"],
                 "blind_outcome_sha256_recorded_by_posthoc": p["blind_outcome_sha256"],
                 "registry_blob": p["registry_blob"],
                 "source_audit_violations": p["source_audit"]["violations"],
                 "source_audit_planted_recall": p["source_audit"]["planted_recall"],
                 "source_audit_control_hits": p["source_audit"]["control_posthoc_hits"],
                 "aj9g_custody_gap": "NO_FREEZE_FILE in gmi-833-aj9g-k06-blind-recovery-v1 (recorded by gmi-833-aj9-holdout-source-audit-v1); not load-bearing here"},
    }
    problems = []
    if b["verdict"] != "CONFIRMED" or o["verdict"] != "CONFIRMED":
        problems.append("blind verdict not CONFIRMED on both routes")
    for name, rec in (("posthoc", p), ("ladder", l), ("ladder_oracle", lo)):
        if rec["status"] != "GREEN":
            problems.append("%s not GREEN" % name)
    if results["FX-4"]["hostiles_applicable_and_detected"] != results["FX-4"]["hostiles_total"]:
        problems.append("a hostile is vacuous or undetected")
    return {"schema": "AJ15_FLAGSHIP_RESULT_V1", "issue": 833, "package": "gmi-833-aj15-flagship-experiment-v1",
            "claim_ceiling": CEILING, "forbidden_promotions": FORBIDDEN,
            "ceilings_not_exceeded": ["AJ9_ALL_11_REGISTERED_FAMILIES_RECOVERED_WITH_FAMILY_LABELS_HIDDEN_AT_DECLARED_FINITE_TASK_AND_BASIS_SCOPES", "FGS-4"],
            "terminal": "AJ15_FLAGSHIP_EXECUTED_AT_B1_AND_B2__REGIME_PREDICTIONS_CONFIRMED__HONEST_FAILURE_TERMINAL_EXERCISED__NO_NOVEL_FORM__FULL_GMI_NOT_EARNED",
            "results": results, "problems": problems, "status": "GREEN" if not problems else "RED"}


def main(argv=None):
    doc = build()
    text = json.dumps(doc, indent=1, sort_keys=True) + "\n"
    path = os.path.join(HERE, "RESULT_V1.json")
    if "--check" in (argv or sys.argv[1:]):
        cur = _read_text(path)
        if cur != text:
            sys.stderr.write("RESULT_V1.json differs from a live rebuild\n")
            return 1
        print("RESULT_V1.json matches a live rebuild; status=%s" % doc["status"])
        return 0 if doc["status"] == "GREEN" else 1
    _write_text(path, text)
    print(json.dumps({"status": doc["status"], "problems": doc["problems"]}))
    return 0 if doc["status"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
