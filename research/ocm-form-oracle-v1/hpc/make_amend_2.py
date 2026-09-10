"""FORM_ORACLE_PROTOCOL_V1_AMEND_2 — recorded supersession WITH a re-run.

Unlike AMEND_1 this one invalidated a scored result, so the freeze discipline's
full cost applies: cause recorded, superseded results named, arms re-run.

CAUSE -- a defect in the Form Oracle's own reading of the frozen evaluator
    search/successive_halving.py returns survivor records whose TOP-LEVEL
    "evaluation" key is the T0 evaluation (total_tasks 15, ecology_id None).
    The T2 result lives in a separate "t2" sub-record (total_tasks 88,
    ecology_id LifetimeEcologyV2). oracle/run_form_oracle.py read the top level.

    Objective 1 is frozen as "T2 solved_fraction (LifetimeEcologyV2)". The first
    arms campaign therefore scored the cheap 15-task screen and reported it as
    the 12-epoch developmental battery. Objective 2 (burden) read the same wrong
    evaluation, and the behaviour signature was built from the T0 per-family
    profile rather than the eight frozen T2 families.

    The defect was caught by a consistency check, not by a failing run: record
    capabilities spanned [0.533, 0.867] while a direct measurement on 92
    T2-feasible forms put T0 at mean 0.512 (range [0.267, 0.867]) and T2 at mean
    0.804 (range [0.659, 1.000]). The reported values sat in the T0 range.

SECOND DEFECT, same root cause -- the governance gate compared unlike things
    oracle/evolvability.governed_step evaluated each proposal at T0 and compared
    its solved_fraction against a base capability that the protocol defines at
    T2. On those same 92 forms T0 capability was below T2 capability in 92 of 92
    cases, so a T0-versus-T2 test is not a no-regression gate at all. Because
    the base capability actually passed in was also T0 (first defect), the two
    errors cancelled into a gate that accepted the first proposal every time:
    n_accepted was 3 of 3 in all 1108 measurements, and the accepted mutations
    were effectively arbitrary. That is why delta_cap_FOF1 was 0.0 in 1078 of
    1108 cases and evolvability came out indistinguishable from its null.

    The null was NOT caused by a saturated future family. That hypothesis was
    tested and FALSIFIED before this amendment was written: forms with the most
    headroom (cap_FOF1 before < 0.6) showed delta_nonzero in 0.0% of cases, and
    Pearson(headroom, |delta_cap|) was 0.003.

CHANGE
    1. Objectives, burden components and the behaviour signature read
       rec["t2"]["evaluation"] and rec["t2"]["gates"].
    2. governed_step scores candidates at T2 and compares T2 with T2. T0 is
       retained as a cheap pre-filter on the frozen hard gates; both tiers are
       charged.
    3. A survivor lacking a T2 sub-record is counted, not silently dropped.

WHAT DID NOT CHANGE
    No objective DEFINITION changed -- objective 1 was always T2 solved_fraction
    and is now actually read from T2. No estimator formula, admission rule,
    hard gate, rung, seed, null or falsifier changed.

SUPERSEDED RESULTS -- re-run required and performed
    FO_FO_*.json from array 3588685 and the aggregate built from them.
    D26 (FO_D26_TRANSFER.json) and D27 (FO_D27_*.json, FO_D27_AGGREGATE.json)
    are NOT affected: D26 touches no zoo evaluator, and D27 calls
    evaluation.lifetime2.run_lifetime2 directly, which is T2 by construction.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FROZEN_PROTOCOL_SHA = ("3c956d336793b04c98c8dce19af2137e"
                       "7365c3ef971bd70aefaeed889ecbf833")


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    proto = json.load(open(os.path.join(ROOT, "FORM_ORACLE_PROTOCOL_V1.json")))
    frozen = proto.get("code_digests", {})
    current = {}
    for fn in sorted(os.listdir(os.path.join(ROOT, "oracle"))):
        if fn.endswith(".py"):
            current["oracle/" + fn] = _sha256_file(
                os.path.join(ROOT, "oracle", fn))
    changed = {k: {"frozen": frozen.get(k), "current": v}
               for k, v in current.items() if frozen.get(k) != v}

    amend = {
        "amendment_id": "FORM_ORACLE_PROTOCOL_V1_AMEND_2",
        "supersedes_digest": FROZEN_PROTOCOL_SHA,
        "supersedes_amendment": "FORM_ORACLE_PROTOCOL_V1_AMEND_1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "timing": "AFTER_A_SCORED_RUN",
        "severity": "INVALIDATES_A_SCORED_RESULT",
        "cause": {
            "defect_1": (
                "survivor records from search/successive_halving.py carry the "
                "T0 evaluation at the top level (total_tasks 15, ecology_id "
                "None) and the T2 evaluation in a 't2' sub-record "
                "(total_tasks 88, ecology_id LifetimeEcologyV2); "
                "run_form_oracle read the top level, so objective 1 and "
                "objective 2 scored the 15-task screen and reported it as the "
                "frozen 12-epoch developmental battery"),
            "defect_1_evidence": {
                "reported_capability_range": [0.533333, 0.866667],
                "measured_T0": {"n": 92, "mean": 0.5116,
                                "range": [0.266667, 0.866667]},
                "measured_T2": {"n": 92, "mean": 0.8037,
                                "range": [0.659091, 1.0]},
                "T0_ge_T2_count": "0 of 92",
            },
            "defect_2": (
                "evolvability.governed_step scored proposals at T0 and "
                "compared them against a base capability the protocol defines "
                "at T2; combined with defect 1 the gate accepted the first "
                "proposal every time"),
            "defect_2_evidence": {
                "n_accepted_distribution": {"3": 1108},
                "delta_cap_fof_zero": "1078 of 1108",
                "falsified_alternative_explanation": {
                    "hypothesis": "the future family FOF1 is saturated",
                    "test": "condition delta on pre-step headroom",
                    "result": ("forms with headroom > 0.4 showed "
                               "delta_nonzero in 0.0% of 16 cases; "
                               "Pearson(headroom, |delta_cap|) = 0.003"),
                    "verdict": "FALSIFIED",
                },
            },
        },
        "change": [
            "objectives, burden and the behaviour signature read "
            "rec['t2']['evaluation'] and rec['t2']['gates']",
            "governed_step scores candidates at T2 and compares T2 with T2; "
            "T0 is retained as a charged pre-filter on the frozen hard gates",
            "survivors lacking a t2 sub-record are counted, not dropped",
        ],
        "unchanged": [
            "objective 1 was ALWAYS defined as T2 solved_fraction; the "
            "definition did not move, the read did",
            "every estimator formula, admission rule, hard gate, rung, seed, "
            "null and falsifier",
        ],
        "rerun_required": True,
        "superseded_results": [
            "fo/results/FO_FO_*.json from SLURM array 3588685",
            "fo/results/FO_ARMS_AGGREGATE.json built from them",
        ],
        "unaffected_results": {
            "FO_D26_TRANSFER.json": "touches no zoo evaluator",
            "FO_D27_*.json": ("calls evaluation.lifetime2.run_lifetime2 "
                              "directly, which is T2 by construction"),
        },
        "code_digest_drift": {"changed": changed},
    }
    out = os.path.join(ROOT, "FORM_ORACLE_PROTOCOL_V1_AMEND_2.json")
    blob = json.dumps(amend, indent=1, sort_keys=True, default=str)
    with open(out, "w") as fh:
        fh.write(blob + "\n")
    sys.stderr.write("amend2 sha256 %s changed=%d\n"
                     % (hashlib.sha256((blob + "\n").encode()).hexdigest(),
                        len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
