"""Run the escalation pilot and emit its receipt.

    python run_escalation.py --out results/ESCALATION_PILOT_V1.json

The receipt records the pre-registration commitment, the derived seeds, every
arm's score on both the registered nine worlds and the commitment-derived
generated draw, and -- prominently -- the reasons this is an E2 pilot and not
confirmatory evidence.  The honest terminal is written into the receipt by the
script, not chosen after reading the numbers: the terminal function below is
fixed and takes the scores as input.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from escalation import JUMP_THRESHOLD, diagnose, score
from escalation_generator import LEVELS, draw_suite
from escalation_parents import PARENTS
from escalation_worlds import WORLDS
from prereg import commit

PLAN = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "scaling_protocol": "COGNITIVE_LADDER_SCALING_V1",
    "study_id": "CL-ESCALATION-PILOT-V1",
    "pilot": "escalation",
    "levels": [l.name for l in LEVELS],
    "per_level": 10,
    "arms": ["governed"] + sorted(PARENTS),
    "primary_endpoint": "minimum_sufficient_level_exact_match",
    "secondary_endpoints": ["false_jump_rate", "missed_jump_rate", "overreach_rate"],
    "jump_threshold": JUMP_THRESHOLD.name,
    "analysis": "exact counts over generated worlds; no inferential test at pilot stage",
}


def _score_pool(pool, arms) -> dict:
    out = {}
    for name, fn in arms.items():
        rows = [score(w, fn(w)) for w in pool]
        n = len(rows)
        out[name] = {
            "n": n,
            "exact_match": sum(r["exact_match"] for r in rows),
            "false_jump": sum(r["false_jump"] for r in rows),
            "missed_jump": sum(r["missed_jump"] for r in rows),
            "overreach": sum(r["overreach"] for r in rows),
            "underreach": sum(r["underreach"] for r in rows),
            "witnessed": sum(r["witnessed"] for r in rows),
            "confusions": sorted(
                {f"{r['minimum_sufficient']}->{r['diagnosed']}" for r in rows if not r["exact_match"]}
            ),
        }
    return out


def terminal_for(generated: dict) -> tuple[str, str]:
    """Decide the terminal from the scores, by a rule fixed before the run."""
    gov = generated["governed"]
    best_parent = max(
        (v["exact_match"] for k, v in generated.items() if k != "governed"), default=0
    )
    if gov["exact_match"] <= best_parent:
        return (
            "PARENT_SUFFICIENT",
            "a parent matched or exceeded the governed policy on the primary endpoint",
        )
    if gov["false_jump"] > 0:
        return (
            "GOVERNED_POLICY_FALSE_ESCALATES",
            "the governed policy escalated where the minimum sufficient level was below the threshold",
        )
    return (
        "PILOT_DISCRIMINATION_CALIBRATED_NOT_CONFIRMATORY",
        "the governed policy separates from every implemented parent on worlds whose defect type "
        "was chosen by a generator sharing the policy's own theory; this is calibration",
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output path; must not already exist")
    args = ap.parse_args(argv)
    out_path = pathlib.Path(args.out)
    if out_path.exists():
        print(f"refusing to overwrite existing receipt {out_path}", file=sys.stderr)
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)

    c = commit(PLAN)
    arms = {"governed": diagnose}
    arms.update(PARENTS)
    generated = _score_pool(draw_suite(c.protected_seed, PLAN["per_level"]), arms)
    terminal, reason = terminal_for(generated)

    receipt = {
        "receipt": "CL_ESCALATION_PILOT_V1",
        "study_id": PLAN["study_id"],
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E2",
        "contribution_level": "L1",
        "study_role": "PILOT_AND_DESIGN_EVIDENCE_ONLY",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "commitment": c.as_dict(),
        "registered_worlds": _score_pool(WORLDS, arms),
        "generated_worlds": generated,
        "terminal": terminal,
        "terminal_reason": reason,
        "why_this_is_not_confirmatory": [
            "The nine registered worlds were authored alongside the diagnosis policy.",
            "The generated worlds are drawn by a generator that instantiates the defect type the "
            "policy is built to detect, so the verdict is fixed by the construction. This is the "
            "ORION FAILURE_LEDGER pattern STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE.",
            "No independently authored world family exists yet, and #144 §11 requires one.",
            "No inferential test is reported, because the independent unit at pilot stage is the "
            "defect type and there are seven of them.",
        ],
        "preserved_prior_terminals": [
            "REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE (ORION V1 Jump programme closure)",
            "REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE: the verified-regime-revision parent "
            "matched ORION on every protected metric; the protected incremental gap was exactly zero",
            "ME-X2 PARENT_SUFFICIENT (B5_DOMINATES): the parent won on minimum-escalation accuracy",
            "ME-X2 V3 THRESHOLD_NULL: parity on a fresh seed",
            "ME-X2 and V3 replicated asymmetry: false escalations 0 versus 21, then 0 versus 14",
        ],
        "authority": (
            "This receipt records a calibration of an escalation-diagnosis policy against four "
            "implemented parents on synthetic exact worlds. It establishes no causal mechanism, no "
            "scaling result, no transfer result and no novelty. The binary Jump decision is already "
            "closed against a fully-resourced parent elsewhere in the programme and this pilot does "
            "not reopen it."
        ),
    }
    out_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "terminal": terminal,
        "arms": {k: f"{v['exact_match']}/{v['n']} exact, {v['false_jump']} false jumps"
                 for k, v in generated.items()},
        "out": str(out_path),
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
