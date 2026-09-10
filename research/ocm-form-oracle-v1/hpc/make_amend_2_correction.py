"""AMEND_2 CORRECTION — the tier defect was real, but it does NOT explain the null.

AMEND_2 recorded a tier defect and, in `defect_2_evidence`, presented it as the
CAUSE of the evolvability null: "combined with defect 1 the gate accepted the
first proposal every time ... which is why delta_cap_fof was 0.0 in 1078 of
1108". Running the corrected gate contradicts that. The defect is real and the
fix stands; the causal claim does not.

MEASUREMENT (corrected T2-versus-T2 gate, 240 measurements over 6 seeds,
successive-halving survivors, LUNARC lu48)

    n_accepted                  3 in 240 of 240
    total_proposals             3 in 168, 4 in 55, 5 in 13, 6 in 4
    delta_cap_FOF1 == 0         240 of 240 (positive 0, negative 0)
    cap_FOF1 before, mean       0.9052   (min 0.5)
    b_steps, mean               3183.1

WHAT THIS RULES OUT

  * "the gate was not gating".  Under the defective T0-versus-T2 comparison the
    first proposal was accepted every time.  Corrected, 72 of 240 forms needed
    more than one proposal somewhere in their three steps, so the gate is
    selecting.  The null survives that change and is in fact MORE complete
    afterwards: exactly 240 of 240 zero, against 1078 of 1108 before.

  * "the future family is saturated".  Tested and falsified before AMEND_2 was
    written: forms with pre-step capability below 0.6 -- the largest headroom in
    the sample -- showed a nonzero delta in 0.0% of cases, and
    Pearson(headroom, |delta_cap|) = 0.003.

  * "the burden denominator is degenerate".  b_steps is 3183.1 on average and
    never zero, so no measurement fell to CANNOT_CHECK_ZERO_BURDEN.

WHAT REMAINS -- one stage, and it is not the governance

    Three mutations that preserve T2 capability never change FOF1 capability at
    all, in any of 240 forms, in either direction. The capability-preserving
    neighbourhood of a T2 survivor is invariant on the future family. The null
    belongs to the MUTATION OPERATOR interacting with the no-regression
    constraint, not to the gate, not to the family, and not to the estimator's
    arithmetic.

    This is a scoped negative, not a claim that evolvability is unmeasurable.
    It is specific to k=3 steps, TAU=0.0 (no regression permitted at all) and
    the frozen mutation operator. The obvious next lever is TAU>0 -- permitting
    a bounded capability regression so a step can cross a valley -- which is a
    genuine mechanic change and would need its own freeze.

STATUS OF AMEND_2
    The FIX stands: reading T2 where the protocol says T2, and comparing like
    with like in the gate, are both correct independent of this. Only the
    causal sentence in defect_2_evidence is withdrawn.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main() -> int:
    rec = {
        "correction_id": "FORM_ORACLE_PROTOCOL_V1_AMEND_2_CORRECTION",
        "corrects": "FORM_ORACLE_PROTOCOL_V1_AMEND_2",
        "corrects_field": "cause.defect_2_evidence",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "withdrawn_claim": (
            "that the T0-versus-T2 unit mismatch is why delta_cap_FOF1 was "
            "0.0 in 1078 of 1108 measurements"),
        "why_withdrawn": (
            "the null persists, and is more complete, after the gate was "
            "corrected to compare T2 with T2"),
        "measurement": {
            "gate": "corrected T2-versus-T2",
            "n": 240, "seeds": list(range(6)),
            "population": "successive-halving T2 survivors",
            "n_accepted_distribution": {"3": 240},
            "total_proposals_distribution": {"3": 168, "4": 55, "5": 13,
                                             "6": 4},
            "delta_cap_fof_zero": 240,
            "delta_cap_fof_positive": 0,
            "delta_cap_fof_negative": 0,
            "mean_cap_fof_before": 0.9052,
            "min_cap_fof_before": 0.5,
            "mean_b_steps": 3183.1,
            "host": "LUNARC lu48",
        },
        "ruled_out": {
            "gate_not_gating": (
                "72 of 240 forms needed more than one proposal somewhere in "
                "their three steps under the corrected gate, against "
                "first-proposal acceptance every time under the defective one"),
            "future_family_saturated": (
                "falsified: forms with pre-step capability below 0.6 showed a "
                "nonzero delta in 0.0% of cases; "
                "Pearson(headroom, |delta_cap|) = 0.003"),
            "degenerate_burden_denominator": (
                "mean b_steps 3183.1, never zero; no measurement fell to "
                "CANNOT_CHECK_ZERO_BURDEN"),
        },
        "remaining_attribution": {
            "stage": "MUTATION_OPERATOR_UNDER_NO_REGRESSION_CONSTRAINT",
            "statement": (
                "three mutations that preserve T2 capability never change FOF1 "
                "capability, in any of 240 forms, in either direction; the "
                "capability-preserving neighbourhood of a T2 survivor is "
                "invariant on the future family"),
            "scope": ("specific to k=3, TAU=0.0 and the frozen mutation "
                      "operator; not a claim that evolvability is "
                      "unmeasurable"),
            "next_lever": ("TAU > 0, permitting a bounded capability "
                           "regression so a step can cross a valley; a genuine "
                           "mechanic change requiring its own freeze"),
        },
        "amend_2_fix_status": (
            "STANDS. Reading T2 where the protocol says T2, and comparing like "
            "with like in the gate, are correct independent of this "
            "correction. Only the causal sentence is withdrawn."),
    }
    out = os.path.join(ROOT, "FORM_ORACLE_PROTOCOL_V1_AMEND_2_CORRECTION.json")
    blob = json.dumps(rec, indent=1, sort_keys=True, default=str)
    with open(out, "w") as fh:
        fh.write(blob + "\n")
    sys.stderr.write("correction sha256 %s\n"
                     % hashlib.sha256((blob + "\n").encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
