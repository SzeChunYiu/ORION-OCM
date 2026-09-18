"""Regenerate MANIFEST_V1.json: parent pins as path + blob sha + claim ceiling."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))

SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
FREEZE_COMMIT = "c9dec25dad00ddde53ddadd3852c1d5fef1a0e03"

PARENTS = [
    ("research/gmi-833-capability-predictor-v1/capability_predictor_v1.py",
     "GMI_833_EXACT_CAPABILITY_PREDICTOR_FAILURE_TAXONOMY_AND_TOTAL_UNCERTAINTY_"
     "AT_REGISTERED_FINITE_SCOPE", "F itself; never modified here"),
    ("research/gmi-833-capability-predictor-v1/RESULT_V1.json",
     "GMI_833_EXACT_CAPABILITY_PREDICTOR_FAILURE_TAXONOMY_AND_TOTAL_UNCERTAINTY_"
     "AT_REGISTERED_FINITE_SCOPE", "KP-1/KP-2/KP-3 receipt"),
    ("research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v1.py",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_"
     "REGISTERED_FINITE_SCOPE", "SIGMA_REAL, the registration surface, VERIFIED"),
    ("research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v2.py",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_"
     "REGISTERED_FINITE_SCOPE", "SIGMA_REAL2"),
    ("research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v3.py",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_"
     "REGISTERED_FINITE_SCOPE", "SIGMA_REAL3 and the V3 registered law"),
    ("research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v4.py",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_"
     "REGISTERED_FINITE_SCOPE", "SIGMA_SYN2/SIGMA_ARCH2, counter-validation only"),
    ("research/gmi-833-capability-predictor-evaluation-v1/FREEZE_V3_ADDENDUM.md",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_"
     "REGISTERED_FINITE_SCOPE", "section 6 registers the terminal honoured here"),
    ("research/gmi-833-capability-predictor-evaluation-v1/RESULT_V1.json",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_"
     "REGISTERED_FINITE_SCOPE", "KE-1..KE-7, KE-3, KE-3D"),
    ("research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py",
     "see gmi-833-tranche-ab-ac-lit", "the banned-term patterns; route A imports them"),
    ("research/gmi-833-ab-terminology-harness-v1/RESULT_V1.json",
     "REGISTERED_TERMINOLOGY_AUDIT_VERIFIED_V1", "ABH-1/ABH-2/ABH-3"),
    ("research/gmi-833-real-developmental-validation-v1/RESULT_V1.json",
     "GMI_833_REAL_SYSTEM_UPDATE_LAW_AND_DEVELOPMENTAL_VALIDATION_AND_DERIVED_"
     "INVENTION_LIBRARY_CONDITIONS_AT_REGISTERED_SCOPE",
     "recorded the L row open on custody grounds"),
    ("research/gmi-833-developmental-reuse-v1/RESULT_V1.json",
     "see gmi-833-developmental-reuse-v1", "the closed L rows"),
]

FORBIDDEN = [
    "ROW_A_CLOSED_BY_MEASUREMENT", "TERMINOLOGY_MIGRATION_COMPLETE",
    "RESIDUAL_IS_UNOWNED", "PAPER_FACING_SCOPE_DEFINED_HERE",
    "PREDICTOR_TESTED_ON_REAL_TRAINED_SYSTEMS", "F_IS_DEFECTIVE",
    "KE_3_INVALIDATED", "FOURTH_REGISTRATION_LAW", "BRIDGE_REPAIRED",
    "CAPABILITY_PREDICTION_IMPOSSIBLE_IN_GENERAL",
    "FUTURE_TASK_FAMILY_CONSTRUCTED", "EVOLVABILITY_PREDICTED_PROSPECTIVELY",
    "OUT_OF_SAMPLE_EQUALS_FUTURE", "SECTION_A_COMPLETE", "SECTION_K_COMPLETE",
    "SECTION_L_COMPLETE", "SECTION_M_ANY_ROW_EARNED", "PR_927_EVIDENCE_CITED",
    "CHECKLIST_CLOSURE_IMPLIES_COMPLETENESS",
]


def blob_sha(path):
    with open(os.path.join(REPO, path), "rb") as fh:
        data = fh.read()
    return hashlib.sha1(("blob %d\0" % len(data)).encode("ascii") + data).hexdigest()


def main():
    doc = {
        "schema": "GMI_833_BODY_RESIDUAL_AKL_MANIFEST_V1",
        "issue": 833,
        "package": "gmi-833-body-residual-akl-v1",
        "claim_ceiling":
            "GMI_833_BODY_RESIDUAL_AKL_DISPOSITION_AT_REGISTERED_FINITE_SCOPE",
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "rows_in_scope": ["ROW_A", "ROW_K", "ROW_L"],
        "rows_out_of_scope": {"ROW_M1": "issue #926 / draft PR #927",
                              "ROW_M2": "issue #926 / draft PR #927",
                              "ROW_M3": "issue #926 / draft PR #927"},
        "issue_body_is_never_edited_by_this_package": True,
        "parents": [{"path": p, "blob_sha": blob_sha(p), "claim_ceiling": c,
                     "owns": why} for p, c, why in PARENTS],
        "forbidden_promotions": FORBIDDEN,
    }
    body = json.dumps(doc, indent=1, sort_keys=True) + "\n"
    with open(os.path.join(HERE, "MANIFEST_V1.json"), "w") as fh:
        fh.write(body)
    print("MANIFEST_V1.json: %d parents pinned" % len(PARENTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
