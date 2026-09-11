"""Re-hash FREEZE_V2_EXECUTED.json: keep every listed path, add the new receipts/documents given on the command line
(or the default list below), recompute sha256 for all, stamp utc."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_NEW = [
    "microscopes/results/STAGE_DE_SMOOTH_V5_PARITY_PH5.json", "microscopes/results/STAGE_DE_SMOOTH_V5B_PARITY_PH5_MIXED.json",
    "microscopes/results/STAGE_DE_SMOOTH_V4B_SMOOTH3_ROWS_V4_CALIB.json", "microscopes/results/STAGE_DE_SMOOTH_V4C_SMOOTH1_ROWS_V6_CALIB.json",
    "microscopes/results/STAGE_DE_SMOOTH_V6_SYM3.json", "microscopes/results/STAGE_DE_SMOOTH_V6_SYM5.json", "microscopes/results/STAGE_DE_SMOOTH_V6_SYM7.json", "microscopes/results/STAGE_DE_SMOOTH_V6_SYM8.json",
    "microscopes/results/STAGE_DE_SYM_PREDICTION.json", "microscopes/results/STAGE_DE_SYM_VERDICT.json",
    "microscopes/results/STAGE_DE_SMOOTH_V8_SYM3_H.json", "microscopes/results/STAGE_DE_SMOOTH_V8_SYM5_H.json", "microscopes/results/STAGE_DE_SMOOTH_V8_SYM7_H.json", "microscopes/results/STAGE_DE_SMOOTH_V8_SYM8_H.json", "microscopes/results/STAGE_DE_SMOOTH_V8_SMOOTH3_H.json",
    "microscopes/results/STAGE_DE_SYM2_PREDICTION.json", "microscopes/results/STAGE_DE_SYM2_VERDICT.json",
    "microscopes/results/STAGE_DE_SMOOTH_V7_PARITY_COSET_XOR.json", "microscopes/results/STAGE_DE_SMOOTH_V7_PARITY_MIXED_XOR.json", "microscopes/results/STAGE_DE_SMOOTH_V7_SMOOTH3_XOR.json",
    "microscopes/results/STAGE_DE_HOLE_CENSUS_V1.json",
    "microscopes/results/STAGE_F_BLIND_RECOVERY_RUN3B_BIND16_SEED4.json",
    "microscopes/results/STAGE_F_BLIND_RECOVERY_RUN7_SMOOTH8_REGEVO_S5.json", "microscopes/results/STAGE_F_BLIND_RECOVERY_RUN7_SMOOTH8_REGEVO_S6.json", "microscopes/results/STAGE_F_BLIND_RECOVERY_RUN7_SMOOTH8_REGEVO_S7.json",
    "microscopes/results/STAGE_F_BLIND_RECOVERY_RUN8_SMOOTH8_DIV_REGEVO_S5.json", "microscopes/results/STAGE_F_BLIND_RECOVERY_RUN8_SMOOTH8_DIV_REGEVO_S6.json", "microscopes/results/STAGE_F_BLIND_RECOVERY_RUN8_SMOOTH8_DIV_REGEVO_S7.json",
    "microscopes/results/STAGE_DE_SMOOTH_V9_SMOOTH3_H_SHRFIX.json",
    "microscopes/results/STAGE_DE_SMOOTH_V10_SMOOTH3_BAYES_E6.json",
    "microscopes/results/STAGE_DE_SMOOTH_V12_SMOOTH3_BAYES_E6_FIX.json", "microscopes/results/STAGE_DE_SMOOTH_V12_SMOOTH3_BAYES_NOISE_FIX.json", "microscopes/results/STAGE_DE_SMOOTH_V12_SMOOTH3_BAYES_REF_FIX.json",
    "microscopes/results/STAGE_DE_CREDIT_V11_CREDIT_E8.json", "microscopes/results/STAGE_DE_CREDIT_V11_CREDIT_E32.json",
    "microscopes/results/STAGE_E1_V13_E1_VLC.json", "microscopes/results/STAGE_E1_V13_VERDICT.json", "microscopes/results/STAGE_E1_V14_E1_CP.json",
    "microscopes/results/STAGE_DE_SMOOTH_V15_SYM3_ATT.json", "microscopes/results/STAGE_DE_SMOOTH_V15_SYM5_ATT.json", "microscopes/results/STAGE_DE_SMOOTH_V15_SYM7_ATT.json", "microscopes/results/STAGE_DE_SMOOTH_V15_SYM8_ATT.json",
    "microscopes/results/STAGE_DE_SMOOTH_V16_SMOOTH3_HW.json", "microscopes/results/STAGE_DE_SMOOTH_V16_SYM3_HW.json", "microscopes/results/STAGE_DE_SMOOTH_V16_SYM5_HW.json",
    "microscopes/results/STAGE_E1_V17_E1_CQU.json", "microscopes/results/STAGE_E1_V18_E1_ABL.json", "microscopes/results/STAGE_E1_V19_E1_LINEAGE.json",
    "GMI_THEORY_CORE_V3_EXECUTED.md", "GMI_COST_AND_REACHABILITY_TABLE_V1.json", "GMI_COST_AND_REACHABILITY_TABLE_V1.md",
    "REVIVAL_LEDGER.jsonl", "CLAIM_LADDER_V4.json", "REPO_STATE.json", "README.md", "GMI_NOTE_QUESTIONS_STATUS_V1.md", "GMI_EXPERIMENT_PROGRAMME_V2_EXECUTED_LANE.md", "THEOREM_REGISTRY_CANONICAL_377.json",
]


def main(new=None):
    p = os.path.join(ROOT, "FREEZE_V2_EXECUTED.json")
    f = json.load(open(p))
    paths = sorted(set(f["sha256"]) | set(new or DEFAULT_NEW))
    missing = [x for x in paths if not os.path.exists(os.path.join(ROOT, x))]
    if missing: raise SystemExit(f"missing: {missing}")
    f["sha256"] = {x: hashlib.sha256(open(os.path.join(ROOT, x), "rb").read()).hexdigest() for x in paths}
    f["utc"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    f["n_files"] = len(paths)
    json.dump(f, open(p, "w"), indent=1, sort_keys=True)
    print("frozen", len(paths), "files at", f["utc"])


if __name__ == "__main__":
    main(sys.argv[1:] or None)
