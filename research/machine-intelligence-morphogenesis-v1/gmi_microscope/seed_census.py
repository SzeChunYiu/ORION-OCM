"""RV-377-040: seed census of the stochastic particle row S3 (the only row that consumes the machine seed) on the three
frontier ecologies, B0 column, sizes 4 and 8, seeds 0..N-1. Admissibility of a stochastic row is a distribution over seeds,
not a number; this census measures it. Writes microscopes/results/STAGE_DE_S3_SEED_CENSUS_V1.json."""
from __future__ import annotations

import glob
import json
import os
import sys

from . import bases
from .core import sha256_of
from . import smooth

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
B0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
ECOLOGIES = {"E_smooth3": smooth.COEFFS_V3, "E_sym3": (3 / 16,) * 4, "E_sym5": (5 / 16,) * 4}


def main(n_seeds=32, tag="V1"):
    rows = {"S3": smooth.ROWS_V6["S3"]}; out = {}
    for eco, coeffs in ECOLOGIES.items():
        out[eco] = {}
        for seed in range(n_seeds):
            t = f"CENSUS_TMP_{eco}_S{seed}"
            smooth.main(seed=seed, coeffs=coeffs, tag=t, n_events=16, rows=rows, criterion="unseen", columns={B0: bases.ALL[B0]})
            r = json.load(open(os.path.join(RES, f"STAGE_DE_SMOOTH_{t}.json")))
            out[eco][seed] = {k.split("|")[2]: v for k, v in r["capability_by_cell"].items()}
            for f in glob.glob(os.path.join(RES, f"*{t}*")): os.remove(f)
    summary = {}
    for eco, by_seed in out.items():
        for size in ("4", "8"):
            vals = sorted(by_seed[s][size] for s in by_seed)
            summary[f"{eco}|size={size}"] = {"n": len(vals), "n_admissible": sum(v >= smooth.THETA for v in vals), "max": vals[-1], "median": vals[len(vals) // 2] if len(vals) % 2 else round((vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2, 4), "min": vals[0],
                                              "admissible_seeds": [s for s in by_seed if by_seed[s][size] >= smooth.THETA]}
    receipt = {"schema": "StageDES3SeedCensusV1", "issue": 377, "revival_record": "RV-377-040", "run_tag": tag, "column": B0, "theta": smooth.THETA, "n_seeds": n_seeds, "capability_by_ecology_seed_size": out, "summary": summary}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DE_S3_SEED_CENSUS_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for k, v in summary.items(): print(k, v)
    return receipt


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 32)
