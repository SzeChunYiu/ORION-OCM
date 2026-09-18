"""Freeze the SIGMA_REAL3 revival predictions BEFORE the V2 training runs.

Run:  python3 -I -B freeze_predictions_v2.py
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu    # noqa: E402
import heldout_universes_v2 as hv2   # noqa: E402
import heldout_universes_v3 as hv    # noqa: E402
import freeze_predictions_v1 as fp   # noqa: E402


def main():
    parent = hu.load_parent()
    base = hu.sigma_1()
    baseline = hu.code_fingerprint(parent)
    spec = hv.sigma_real3()
    certs = [hu.disjointness_certificate(base, "SIGMA_1", spec["UNIVERSE"], "SIGMA_REAL3"),
             hu.disjointness_certificate(hu.SYN_RAW, "SIGMA_SYN", spec["UNIVERSE"], "SIGMA_REAL3"),
             hu.disjointness_certificate(hu.ARCH_RAW, "SIGMA_ARCH", spec["UNIVERSE"], "SIGMA_REAL3"),
             hu.disjointness_certificate(hu.REAL_RAW, "SIGMA_REAL", spec["UNIVERSE"], "SIGMA_REAL3"),
             hu.disjointness_certificate(hv2.REAL2_RAW, "SIGMA_REAL2", spec["UNIVERSE"], "SIGMA_REAL3")]
    clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
    fingerprint = hu.install_universe(parent, clean)
    sdig, _payload = fp.spec_digest(spec)
    summary, stream = fp.sweep(parent, "SIGMA_REAL3")
    summary["spec_sha256"] = sdig
    summary["disjointness"] = certs
    summary["curves"] = fp.build_curves(parent)
    summary["parent_code_unchanged"] = (fingerprint[0] == baseline[0])
    out = {
        "schema": "GMI_833_K_EVAL_FROZEN_PREDICTIONS_V3",
        "supersedes": None,
        "amends": "FROZEN_PREDICTIONS_V1.json (SIGMA_REAL only; SIGMA_SYN and "
                  "SIGMA_ARCH are untouched and their V1 results stand)",
        "claim_ceiling": fp.CLAIM_CEILING,
        "parent_file_blob_sha": hu.git_blob_sha(hu.PARENT_FILE),
        "parent_code_fingerprint_before": baseline[0],
        "universes": [summary],
        "real_system_protocol": {
            "source": hu.REAL_SOURCE,
            "word_length": hu.REAL_WORD_LEN,
            "train_windows": list(hu.REAL_TRAIN_WINDOWS),
            "protected_eval_windows": list(hu.REAL_EVAL_WINDOWS),
            "training": hu.REAL_TRAINING,
            "training_budget_unchanged_from_v1": True,
            "solved_band": str(hv.REAL3_BAND),
            "systems": [list(m) for m in hv.REAL3_MACHINES],
            "registered_solved_bits": dict(
                ("|".join(str(x) for x in m), hv.real3_solved_law(m))
                for m in hv.REAL3_MACHINES),
            "mu": [str(x) for x in hu.MU_REAL],
        },
    }
    body = fp.canonical_json(out)
    text = json.dumps(json.loads(body), indent=2, sort_keys=True)
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_V3.json"), "w") as handle:
        handle.write(text)
        handle.write("\n")
    lines = stream.rstrip("\n").split("\n")
    sample = ["# universe=SIGMA_REAL3 rows=%d rule=every_101st_row" % len(lines)]
    for i in range(0, len(lines), 101):
        sample.append("SIGMA_REAL3\t" + lines[i])
    with open(os.path.join(HERE, "FROZEN_PREDICTION_SAMPLE_V3.tsv"), "w") as handle:
        handle.write("\n".join(sample) + "\n")
    sys.stdout.write(text)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
