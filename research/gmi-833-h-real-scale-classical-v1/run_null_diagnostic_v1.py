"""Diagnostic for the registered SIGMA_H02 null, which failed.

`FREEZE_V1.md` P02d / `FREEZE_V2_ADDENDUM.md` Q02d require that none of 200
row-permuted design controls beats the **best constant arm**. 98 of 200 did.

The reason is structural, not empirical: a control arm fitted by least squares on
a permuted design **nests** the constant arm — with all slopes at zero it *is*
the constant arm — so on 294,832 fit rows and 33 parameters the two differ by a
relative amount of order 1e-4 and the comparison is a coin flip by construction.
A control that cannot be distinguished from the model it is meant to falsify
carries no information either way; it is a vacuous null, of the same defect
class as a hostile that cannot fire.

This script records, for exactly the same 200 controls under exactly the same
seed, the comparison that does carry information: whether any control beats the
**selected arm**. It is written and reported as a diagnostic. It does **not**
replace the registered null and it closes no row: the registered falsifier was
not met, and `SIGMA_H02` is reported open on `R05`.
"""
from __future__ import print_function
from fractions import Fraction as F
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_real_scale_v1 as R    # noqa: E402
import run_real_scale_v2 as V2   # noqa: E402
import run_controls_v2 as C2     # noqa: E402

N_NULL = 200


def main():
    src, d1b, pcm, lines, _ = R.load_sources()
    rec = json.load(open(os.path.join(V2.OUT, "scope_H02.json")))
    eco = V2.reorder(R.ecology_H02(pcm))
    sl = V2.slices_v2(eco)
    Xf, yf = R.design(eco, sl["fit"])
    Xh_i = eco["Xi"][sl["held"]]
    Yh_i = eco["yi"][sl["held"]]
    den = R.RAT_DEN
    true_sse = C2.frac(rec["winner"]["evaluation"]["held"]["sse"])
    cval = int(round(float(yf.mean()) * den))
    const_sse = C2.affine_exact_sse([0] * 32, cval, Xh_i, Yh_i, eco["xden"],
                                    eco["yden"], den)
    rs = np.random.RandomState(8330003)      # identical seed to run_controls_v2
    beat_true = 0
    beat_const = 0
    ratios = []
    for _ in range(N_NULL):
        perm = rs.permutation(len(yf))
        beta = R.ols(Xf[perm], yf)
        P = [int(round(v * den)) for v in beta[:32]]
        B = int(round(beta[32] * den))
        s = C2.affine_exact_sse(P, B, Xh_i, Yh_i, eco["xden"], eco["yden"], den)
        if s < true_sse:
            beat_true += 1
        if s < const_sse:
            beat_const += 1
        ratios.append(int(F(10 ** 9) * s / const_sse))
    out = {
        "schema": "GMI833HRealScaleH02NullDiagnosticV1",
        "status": "DIAGNOSTIC_ONLY__THE_REGISTERED_NULL_Q02d_FAILED_AND_IS_NOT_"
                  "REPLACED_BY_THIS",
        "controls": N_NULL,
        "registered_criterion": "no control beats the best constant arm",
        "registered_outcome_controls_beating_constant": beat_const,
        "registered_criterion_met": bool(beat_const == 0),
        "why_the_registered_null_is_vacuous":
            "a least-squares control on a permuted design nests the constant "
            "arm (all slopes zero), so the two are indistinguishable up to a "
            "relative 1e-4 on 294,832 fit rows and 33 parameters; the "
            "comparison is a coin flip by construction",
        "informative_criterion": "no control beats the selected arm",
        "controls_beating_the_selected_arm": beat_true,
        "informative_criterion_met": bool(beat_true == 0),
        "control_sse_over_constant_sse_parts_per_billion": {
            "min": min(ratios), "max": max(ratios),
            "median": sorted(ratios)[len(ratios) // 2]},
        "selected_arm_sse_over_constant_sse_parts_per_billion":
            int(F(10 ** 9) * true_sse / const_sse),
        "closes_no_row": True,
    }
    with open(os.path.join(V2.OUT, "null_diagnostic_H02.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps({k: out[k] for k in (
        "registered_outcome_controls_beating_constant",
        "controls_beating_the_selected_arm",
        "selected_arm_sse_over_constant_sse_parts_per_billion",
        "control_sse_over_constant_sse_parts_per_billion")}, indent=1))


if __name__ == "__main__":
    main()
