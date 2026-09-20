#!/usr/bin/env python3
"""Assemble RESULT_V1.json: bind the frozen outcome, the posthoc
adjudication, the oracle, the float control, and the custody pins into the
package receipt.  Runs after all of them exist.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

CLAIM_CEILING = (
    "GMI_833_H_REALSECALE_FOUR_FAMILY_MORPHOLOGIES_RECOVERED_NEUTRALLY_WITH_"
    "MEASURED_BOUNDARIES_AT_REGISTERED_EXACTDYADIC_SCOPE"
)
FORBIDDEN_PROMOTIONS = [
    "FINITE_STATE_AUTOMATA_FAMILY_ROW_CLOSED_BEYOND_REGISTERED_SCOPE",
    "LINEAR_REGRESSION_CLASSIFIER_FAMILY_ROW_CLOSED_BEYOND_REGISTERED_SCOPE",
    "GLM_FAMILY_ROW_CLOSED_BEYOND_REGISTERED_SCOPE",
    "BASIS_KERNEL_FAMILY_ROW_CLOSED_BEYOND_REGISTERED_SCOPE",
    "ALL_KNOWN_FAMILIES_RECOVERED",
    "REAL_SCALE_VALIDATION_COMPLETE",
    "UNIVERSAL_GRAMMAR_NEUTRALITY",
    "SEARCH_NEUTRALITY",
    "COMPLETE_GMI",
    "SMOOTH_LINK_TIER_MEMBERSHIP",
    "FLOAT64_REQUIRED_FOR_RECOVERY",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    outcome = json.loads((HERE / "OUTCOME_FULL_V1.json").read_text())
    posthoc = json.loads((HERE / "POSTHOC_RESULT_V1.json").read_text())
    preds = json.loads((HERE / "FROZEN_PREDICTIONS_V1.json").read_text())
    oracle = json.loads((HERE / "ORACLE_RESULT_V1.json").read_text())
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
    reg = json.loads((HERE / "BATTERY_REGISTRY_V1.json").read_text())
    float_control = json.loads((HERE / "FLOAT_CONTROL_V1.json").read_text())

    adjs = posthoc["adjudications"]
    inter = posthoc["interventions"]
    checks = {
        "all_four_families_recovered": all(
            a["verdict"] == "RECOVERED_AT_REGISTERED_REAL_SCALE"
            for a in adjs.values()),
        "member_censuses_complete": all(
            a["member_census"]["recovered"] == a["member_census"]["n"]
            for a in adjs.values()),
        "all_nulls_zero": all(
            a["null_census"]["recovered"] == 0 for a in adjs.values()),
        "boundary_twins_hold": all(
            a["boundary_census"]["recovered"] == 0 for a in adjs.values()),
        "frozen_predictions_match": all(
            a["prediction_match"]["matches"] == a["prediction_match"]["total"]
            for a in adjs.values()),
        "proc2_agrees": all(
            a["proc2_agreement"]["agree"] == a["proc2_agreement"]["of"]
            for a in adjs.values()),
        "clause_bijections": all(a["clause_count_assert"] for a in adjs.values()),
        "hostility_clean": posthoc["hostility"]["source_self_scan_clean"]
        and posthoc["hostility"]["reversed_row_order_verdicts_invariant"],
        "delay_ablation_jumps": inter["delay_ablation"]["jump_exceeds_band"],
        "counting_bound_exact": inter["counting_bound"]["all_exact"],
        "coefficient_zeroing_jumps": inter["coefficient_zeroing"]["jump_exceeds_band"],
        "decision_realization_reported": "realization_agreement" in inter["decision_equivalence"],
        "link_nonlinearity": inter["link_nonlinearity"]["all_nonlinear"],
        "dual_kernel_exact": inter["dual_kernel"]["exact_equality"],
        "remint_transports": all(
            v["predictions_transport_exactly"] for v in inter["remint"].values()),
        "crossover_regimes_reported": len(inter["crossover"]["table"]) > 0,
        "oracle_agrees": oracle["all_agree"],
        "oracle_direct_lag": oracle["direct_lag_ok"],
        "float_control_reported": float_control["rows"] != [],
        "outcome_rows_complete": len(outcome["rows"]) == len(reg["tasks"]),
        "custody_pins_valid": all(
            sha(HERE / p) == h for p, h in manifest["pins"].items()),
        "claim_ceiling_frozen": manifest["claim_ceiling"] == CLAIM_CEILING,
    }
    doc = {
        "schema": "GMI833HRealScaleResultV1",
        "parent_issue": 833,
        "benchmark_issue": 434,
        "source_pr": manifest.get("source_pr"),
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "freeze_commit": manifest.get("freeze_commit"),
        "battery_commit": manifest.get("battery_commit"),
        "family_verdicts": {k: v["verdict"] for k, v in adjs.items()},
        "family_summaries": {
            k: {
                "member_census": v["member_census"],
                "null_census": v["null_census"],
                "boundary_census": v["boundary_census"],
                "fisher_exact_one_sided": v["fisher_exact_one_sided"],
                "error_bars_member_risk": v["error_bars_member_risk"],
            } for k, v in adjs.items()},
        "interventions_summary": {
            "delay_ablation": inter["delay_ablation"],
            "counting_bound": {"all_exact": inter["counting_bound"]["all_exact"],
                               "checks": len(inter["counting_bound"]["checks"])},
            "coefficient_zeroing": inter["coefficient_zeroing"],
            "link_nonlinearity": {"count": inter["link_nonlinearity"]["count"],
                                  "all_nonlinear": inter["link_nonlinearity"]["all_nonlinear"]},
            "dual_kernel": inter["dual_kernel"],
            "crossover": inter["crossover"],
            "remint": inter["remint"],
        },
        "float_control": {
            "first_float_disagreement_kappa": float_control.get("kappa_at_first_disagreement"),
            "rows": len(float_control["rows"]),
        },
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }
    (HERE / "RESULT_V1.json").write_text(json.dumps(doc, sort_keys=True, indent=1) + "\n")
    print(doc["verdict"], {k: v for k, v in doc["family_verdicts"].items()})


if __name__ == "__main__":
    main()
