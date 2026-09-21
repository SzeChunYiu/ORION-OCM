"""Build MANIFEST_V1.json: parent pins (path + blob sha + claim ceiling),
source_main, freeze_commit, forbidden promotions, and the package's own file
digests.  Run from the repository root:  python3 -I -B research/gmi-833-kl-revival-v1/build_manifest_v1.py
"""

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PKG = "research/gmi-833-kl-revival-v1"
SOURCE_MAIN = "f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5"
FREEZE_COMMIT = "233bb38a504f7ba10a1a75578840c0416b2e5c0d"
AMENDMENT_1_COMMIT = "65d0025765fef14d423d4e98e0194d23922c0b3d"
CLAIM_CEILING = ("GMI_833_KL_REVIVAL_SET_VALUED_BRIDGE_AND_POSTERIOR_DATED_FUTURITY"
                 "_AT_REGISTERED_FINITE_SCOPE")

PARENTS = (
    ("research/gmi-833-capability-predictor-v1/capability_predictor_v1.py",
     "GMI_833_EXACT_CAPABILITY_PREDICTOR_FAILURE_TAXONOMY_AND_TOTAL_UNCERTAINTY_AT_REGISTERED_FINITE_SCOPE"),
    ("research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v1.py",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_REGISTERED_FINITE_SCOPE"),
    ("research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v3.py",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_REGISTERED_FINITE_SCOPE"),
    ("research/gmi-833-capability-predictor-evaluation-v1/REAL_RUNS/REAL_MEASURED_V1.json",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_REGISTERED_FINITE_SCOPE"),
    ("research/gmi-833-capability-predictor-evaluation-v1/REAL_RUNS_V2/REAL_MEASURED_V2.json",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_REGISTERED_FINITE_SCOPE"),
    ("research/gmi-833-capability-predictor-evaluation-v1/REAL_RUNS_V3/REAL_MEASURED_V3.json",
     "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_REGISTERED_FINITE_SCOPE"),
    ("research/gmi-833-real-developmental-validation-v1/train_continual_v3.py",
     "GMI_833_REAL_SYSTEM_UPDATE_LAW_AND_DEVELOPMENTAL_VALIDATION_AND_DERIVED_INVENTION_LIBRARY_CONDITIONS_AT_REGISTERED_SCOPE"),
) + tuple(
    ("research/gmi-833-real-developmental-validation-v1/REAL_RUNS/cl3_T%02d.json" % i,
     "GMI_833_REAL_SYSTEM_UPDATE_LAW_AND_DEVELOPMENTAL_VALIDATION_AND_DERIVED_INVENTION_LIBRARY_CONDITIONS_AT_REGISTERED_SCOPE")
    for i in list(range(1, 8)) + list(range(11, 18))
) + (
    ("research/gmi-833-body-residual-akl-v1/BODY_RESIDUAL_AKL_THEOREMS_V1.md",
     "GMI_833_BODY_RESIDUAL_AKL_DISPOSITION_AT_REGISTERED_FINITE_SCOPE"),
)

FORBIDDEN = (
    "FOURTH_REGISTRATION_LAW", "F_IS_DEFECTIVE", "KE_3_INVALIDATED", "BRIDGE_TRUTHFUL_IN_GENERAL",
    "CAPABILITY_PREDICTION_SOLVED", "PREDICTOR_TESTED_BEYOND_SIGMA_REAL4", "REVEALING_SET_RESCORED",
    "FUTURE_TASK_FAMILY_CONSTRUCTED", "OUT_OF_SAMPLE_EQUALS_FUTURE", "EVOLVABILITY_MECHANISM_GENERAL",
    "CONTINUAL_LEARNING_GENERAL_CLAIM", "WIKIPEDIA_CONTENT_ENDORSED", "SECTION_K_COMPLETE",
    "SECTION_L_COMPLETE", "M5", "INDEPENDENT_TEAM_REPLICATION", "REAL_SCALE_VALIDATION",
    "CHECKLIST_CLOSURE_IMPLIES_COMPLETENESS",
    # FREEZE_V1_AMENDMENT_1.md 7
    "POTENTIAL_ORDERING_CLOSES_EVOLVABILITY_ROW", "FIRST_WINDOW_RESCORED_OR_DROPPED", "THIRD_WINDOW_OPENED",
    "EV_Q_DEFINITION_CHANGED", "THRESHOLD_TUNED_TO_OUTCOME",
)


def blob_sha(path):
    with open(os.path.join(REPO, path), "rb") as h:
        data = h.read()
    return hashlib.sha1(("blob %d\0" % len(data)).encode("ascii") + data).hexdigest(), \
        hashlib.sha256(data).hexdigest(), len(data)


def git_committer_time(commit):
    p = subprocess.run(["git", "show", "-s", "--format=%cI", commit], cwd=REPO,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.decode().strip() if p.returncode == 0 else None


def main():
    out = {
        "schema": "GMI_833_MANIFEST_V1",
        "package": "gmi-833-kl-revival-v1",
        "issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "freeze_committer_time": git_committer_time(FREEZE_COMMIT),
        "amendment_commits": [{"id": "FREEZE_V1_AMENDMENT_1", "commit": AMENDMENT_1_COMMIT,
                               "committer_time": git_committer_time(AMENDMENT_1_COMMIT)}],
        "disclosed_post_freeze_deviations": ["D1", "D2", "D3", "D4"],
        "forbidden_promotions": list(FORBIDDEN),
        "parent_pins": [],
        "package_files": {},
    }
    for path, ceiling in PARENTS:
        b, s, n = blob_sha(path)
        out["parent_pins"].append({"path": path, "blob_sha": b, "sha256": s, "bytes": n,
                                   "claim_ceiling": ceiling})
    for name in sorted(os.listdir(HERE)):
        p = os.path.join(HERE, name)
        if os.path.isdir(p):
            for sub in sorted(os.listdir(p)):
                q = os.path.join(p, sub)
                if os.path.isfile(q) and not sub.endswith(".pyc"):
                    b, s, n = blob_sha(os.path.join(PKG, name, sub))
                    out["package_files"][name + "/" + sub] = {"sha256": s, "bytes": n}
        elif os.path.isfile(p) and name not in ("MANIFEST_V1.json",) and not name.endswith(".pyc"):
            b, s, n = blob_sha(os.path.join(PKG, name))
            out["package_files"][name] = {"sha256": s, "bytes": n}
    text = json.dumps(out, indent=1, sort_keys=True)
    with open(os.path.join(HERE, "MANIFEST_V1.json"), "w") as h:
        h.write(text)
        h.write("\n")
    sys.stdout.write("parent pins: %d, package files: %d\n" % (len(out["parent_pins"]), len(out["package_files"])))


if __name__ == "__main__":
    main()
