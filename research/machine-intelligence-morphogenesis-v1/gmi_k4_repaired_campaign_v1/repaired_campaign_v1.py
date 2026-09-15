"""Executable registered campaign under repaired K4 pricing (overlay only).

Items 22/23/35 clause (c): run a label-free retention-recovery campaign under
R1+R2+R3 without mutating the frozen V4 model or rewriting frozen cell verdicts.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIM = HERE.parent
if str(MIM) not in sys.path:
    sys.path.insert(0, str(MIM))

import gmi_k4_resource_native_v4 as rn  # noqa: E402
import gmi_k4_substitution_repair_v1 as rep  # noqa: E402

PROTOCOL_PATH = HERE / "PROTOCOL_FREEZE_V1.json"
PROTOCOL = json.loads(PROTOCOL_PATH.read_text())

CAMPAIGN_ID = PROTOCOL["campaign_id"]
GRAMMAR = PROTOCOL["task_plan"]["grammars"][0]
SCALE = int(PROTOCOL["task_plan"]["scales"][0])
REUSE_SCHEDULE = tuple(int(x) for x in PROTOCOL["task_plan"]["reuse_schedule"])
N_CANDIDATES = int(PROTOCOL["task_plan"]["candidate_draws"])
SEED = int(PROTOCOL["task_plan"]["seed"], 16)
COVERAGE_BAR = float(PROTOCOL["adjudication"]["coverage_bar"])
RETENTION_ONSET = int(PROTOCOL["adjudication"]["retention_onset_reuse"])
FULL_COVERAGE_REUSE = 256
FULL_COVERAGE_BAR = 0.999

FROZEN_PINS = PROTOCOL["frozen_model_pins"]
REPAIR_PIN = PROTOCOL["repaired_pricing"]["module_sha256"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_frozen_untouched() -> dict:
    """Fail closed if this campaign is used as cover for mutating frozen bytes."""
    checks = {
        "gmi_k4_resource_native_v4.py": FROZEN_PINS["gmi_k4_resource_native_v4.py_sha256"],
        "gmi_k4_search_v4.py": FROZEN_PINS["gmi_k4_search_v4.py_sha256"],
        "GMI_K4_LOFO_FREEZE_V1.json": FROZEN_PINS["GMI_K4_LOFO_FREEZE_V1.json_sha256"],
        "GMI_K4_MEASURED_RESOURCE_SUCCESSOR_FREEZE_V4.json": FROZEN_PINS[
            "GMI_K4_MEASURED_RESOURCE_SUCCESSOR_FREEZE_V4.json_sha256"
        ],
        "GMI_K4_EXECUTION_FREEZE_V7.json": FROZEN_PINS["GMI_K4_EXECUTION_FREEZE_V7.json_sha256"],
        "gmi_k4_substitution_repair_v1.py": REPAIR_PIN,
    }
    out = {}
    for name, expected in checks.items():
        got = sha256_file(MIM / name)
        out[name] = {"expected": expected, "got": got, "ok": got == expected}
        if got != expected:
            raise AssertionError(
                "frozen/repair pin drift for %s: expected %s got %s" % (name, expected, got)
            )
    if FROZEN_PINS.get("mutate_frozen_v4_v7_model"):
        raise AssertionError("protocol must not authorise mutating the frozen model")
    if FROZEN_PINS.get("untouched") is not True:
        raise AssertionError("protocol must declare frozen model untouched")
    if PROTOCOL["protocol_decision"].get("mutate_frozen_v4_v7_model") is not False:
        raise AssertionError("protocol_decision.mutate_frozen_v4_v7_model must be false")
    if PROTOCOL["protocol_decision"].get("rewrite_frozen_cell_verdicts") is not False:
        raise AssertionError("protocol_decision.rewrite_frozen_cell_verdicts must be false")
    return out


def sample_pool(n: int = N_CANDIDATES, grammar: str = GRAMMAR, seed: int = SEED):
    out = []
    for i in range(n):
        c = rn.sampled_candidate(grammar, seed, i)
        try:
            rn.lifecycle(c, SCALE, {"reuse_multiplier": 1.0})
        except Exception:
            continue
        out.append(c)
    return out


def retains(cand) -> bool:
    state, _ = rn.resource_counts(cand, SCALE)
    return cand.retrieval != "none" and rep.coverage(cand, state, SCALE) >= COVERAGE_BAR


def winner(cands, reuse: float, pricing: str):
    """Label-free argmin over scalar lifecycle cost."""
    best_v, best_c = None, None
    prof = {"reuse_multiplier": float(reuse)}
    for c in cands:
        try:
            if pricing == "repaired":
                v = rep.scalar(rep.lifecycle(c, SCALE, prof, r1=True, r2=True, r3=True))
            elif pricing == "frozen":
                v = rep.scalar(rn.lifecycle(c, SCALE, prof))
            else:
                raise ValueError(pricing)
        except Exception:
            continue
        if best_v is None or v < best_v:
            best_v, best_c = v, c
    return best_c, best_v


def expected_retains(reuse: int) -> bool:
    return int(reuse) >= RETENTION_ONSET


def full_coverage_at_registered_reuse(
    cells, reuse: int = FULL_COVERAGE_REUSE, coverage_bar: float = FULL_COVERAGE_BAR
) -> bool:
    """Require the registered reuse cell itself to meet the coverage bar.

    A later cell cannot retroactively satisfy a "by reuse 256" prediction.  The
    registered schedule must contain exactly one target cell; missing or duplicate
    target cells fail closed.
    """
    matches = [c for c in cells if int(c.get("reuse", -1)) == int(reuse)]
    if len(matches) != 1:
        return False
    return float(matches[0]["repaired"]["coverage"]) >= float(coverage_bar)


def adjudicate_cell(reuse: int, repaired_winner, frozen_winner) -> dict:
    state_r, _ = rn.resource_counts(repaired_winner, SCALE)
    state_f, _ = rn.resource_counts(frozen_winner, SCALE)
    cov_r = rep.coverage(repaired_winner, state_r, SCALE)
    cov_f = rep.coverage(frozen_winner, state_f, SCALE)
    rep_ret = retains(repaired_winner)
    frz_ret = retains(frozen_winner)
    expect = expected_retains(reuse)

    if frz_ret:
        verdict = "INVALID_INSTRUMENT"
        reason = "frozen v4 control retained; campaign cannot certify repaired greens"
    elif rep_ret == expect:
        verdict = "K4_REPAIRED_CAMPAIGN_GREEN"
        reason = (
            "repaired winner retains as predicted at reuse %d (expect_retains=%s)"
            % (reuse, expect)
        )
    else:
        verdict = "K4_REPAIRED_CAMPAIGN_RED"
        reason = (
            "repaired winner retention=%s but expect_retains=%s at reuse %d"
            % (rep_ret, expect, reuse)
        )

    return {
        "schema": "GMIK4RepairedCampaignCellV1",
        "campaign_id": CAMPAIGN_ID,
        "grammar": GRAMMAR,
        "scale": SCALE,
        "reuse": int(reuse),
        "verdict": verdict,
        "reason": reason,
        "expect_retains": expect,
        "repaired": {
            "retrieval": repaired_winner.retrieval,
            "state": state_r,
            "coverage": round(cov_r, 4),
            "retains": rep_ret,
            "candidate_id": repaired_winner.cid,
        },
        "frozen_control": {
            "retrieval": frozen_winner.retrieval,
            "state": state_f,
            "coverage": round(cov_f, 4),
            "retains": frz_ret,
            "candidate_id": frozen_winner.cid,
        },
        "frozen_model_mutated": False,
    }


def run_campaign(n_candidates: int = N_CANDIDATES) -> dict:
    pins = assert_frozen_untouched()
    cands = sample_pool(n=n_candidates)
    cells = []
    for r in REUSE_SCHEDULE:
        wr, _ = winner(cands, r, "repaired")
        wf, _ = winner(cands, r, "frozen")
        if wr is None or wf is None:
            raise RuntimeError("empty winner at reuse %s" % r)
        cells.append(adjudicate_cell(r, wr, wf))

    repaired_profiles = [
        (c["repaired"]["retrieval"], c["repaired"]["state"]) for c in cells
    ]
    frozen_profiles = [
        (c["frozen_control"]["retrieval"], c["frozen_control"]["state"]) for c in cells
    ]
    states = [c["repaired"]["state"] for c in cells]
    green = sum(1 for c in cells if c["verdict"] == "K4_REPAIRED_CAMPAIGN_GREEN")
    red = sum(1 for c in cells if c["verdict"] == "K4_REPAIRED_CAMPAIGN_RED")
    invalid = sum(1 for c in cells if c["verdict"] == "INVALID_INSTRUMENT")

    invariants = {
        "repaired_reuse_sensitive": len(set(repaired_profiles)) > 1,
        "frozen_reuse_invariant": len(set(frozen_profiles)) == 1,
        "repaired_state_monotone": states == sorted(states),
        "declines_retention_at_reuse_1": cells[0]["repaired"]["retains"] is False,
        "full_coverage_by_256": full_coverage_at_registered_reuse(cells),
        "frozen_never_retains": all(not c["frozen_control"]["retains"] for c in cells),
        "green_cells_earned": green > 0,
    }
    if not all(invariants.values()):
        failed = [k for k, v in invariants.items() if not v]
        raise AssertionError("campaign invariants failed: %s" % failed)

    return {
        "schema": "GMIK4RepairedCampaignReceiptV1",
        "campaign_id": CAMPAIGN_ID,
        "protocol": str(PROTOCOL_PATH.name),
        "n_candidates": len(cands),
        "requested_candidates": n_candidates,
        "grammar": GRAMMAR,
        "scale": SCALE,
        "seed": SEED,
        "pins": pins,
        "cells": cells,
        "summary": {
            "n_cells": len(cells),
            "green": green,
            "red": red,
            "invalid_instrument": invalid,
            "green_reuses": [c["reuse"] for c in cells if c["verdict"] == "K4_REPAIRED_CAMPAIGN_GREEN"],
            "red_reuses": [c["reuse"] for c in cells if c["verdict"] == "K4_REPAIRED_CAMPAIGN_RED"],
        },
        "invariants": invariants,
        "claim_ceiling": PROTOCOL["claim_ceiling"],
        "frozen_verdicts_rewritten": False,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    n = N_CANDIDATES
    if argv:
        n = int(argv[0])
    receipt = run_campaign(n_candidates=n)
    out = HERE / "RECEIPT_V1.json"
    out.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "campaign_id": receipt["campaign_id"],
                "green": receipt["summary"]["green"],
                "red": receipt["summary"]["red"],
                "invalid_instrument": receipt["summary"]["invalid_instrument"],
                "green_reuses": receipt["summary"]["green_reuses"],
                "receipt": str(out),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
