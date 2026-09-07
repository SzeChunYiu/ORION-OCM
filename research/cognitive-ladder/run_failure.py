"""Run the scoped failure-knowledge pilot and emit its receipt.

    python run_failure.py --out results/FAILURE_PILOT_V1.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import failure_parents as fp


def terminal_for(totals: dict) -> tuple[str, str]:
    """Fixed before the run: the terminal is a function of the totals."""
    gov = totals["governed"]
    for name, t in totals.items():
        if name == "governed":
            continue
        if (t["wasted_work_avoided"] >= gov["wasted_work_avoided"]
                and t["false_exclusions"] <= gov["false_exclusions"]
                and t["missed_reopenings"] <= gov["missed_reopenings"]
                and t["broken_shut"] <= gov["broken_shut"]):
            return ("PARENT_SUFFICIENT",
                    f"the {name} parent matches or beats the governed store on every coordinate")
    if gov["false_exclusions"] or gov["missed_reopenings"] or gov["broken_shut"]:
        return ("GOVERNED_POLICY_DEFECTIVE",
                "the governed store made a false exclusion, missed a reopening, or closed shut")
    return ("PILOT_DISCRIMINATION_CALIBRATED_NOT_CONFIRMATORY",
            "the governed store separates from every implemented parent on worlds authored "
            "alongside it; this is calibration, not confirmation")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    if out.exists():
        print(f"refusing to overwrite existing receipt {out}", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)

    matrix = fp._score_matrix()
    per_world = {
        policy: {wid: {k: getattr(s, k) for k in
                       ("queries", "wasted_work_avoided", "repeated_wasted_work",
                        "false_exclusions", "missed_reopenings", "broken_shut")}
                 for wid, s in by_world.items()}
        for policy, by_world in matrix.items()
    }
    totals = {
        policy: {k: sum(w[k] for w in by_world.values()) for k in
                 ("queries", "wasted_work_avoided", "repeated_wasted_work",
                  "false_exclusions", "missed_reopenings", "broken_shut")}
        for policy, by_world in per_world.items()
    }
    terminal, reason = terminal_for(totals)

    receipt = {
        "receipt": "CL_FAILURE_PILOT_V1",
        "study_id": "CL-FAILURE-PILOT-V1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E2",
        "contribution_level": "L1",
        "study_role": "PILOT_AND_DESIGN_EVIDENCE_ONLY",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "worlds": [w.world_id for w in fp.WORLDS],
        "policies": list(fp.POLICIES),
        "per_world": per_world,
        "totals": totals,
        "terminal": terminal,
        "terminal_reason": reason,
        "where_the_parent_ties": (
            "The nogood parent is given full strength: correct assumption-set keying and "
            "dependency-directed retraction. It ties the governed store exactly on four of the "
            "seven worlds. The residual is confined to the three worlds where the failure's cause "
            "carries no information about correctness: a spent budget, a probe set that provably "
            "could not discriminate, and a defective checker."
        ),
        "why_this_is_not_confirmatory": [
            "All four arms are handed a CORRECT diagnosis by the world. Nothing here measures "
            "whether a machine can tell an evaluator defect from a genuine refutation when both "
            "report 'refuted by checker'. That is the real problem and it is not attempted.",
            "The worlds were authored alongside the governed policy.",
            "If a future draw contained no cause-discriminating world, the honest report for this "
            "rung would be PARENT_SUFFICIENT.",
        ],
        "preserved_prior_terminals": [
            "FAILURE_MEMORY_USEFUL_BUT_STANDARD_METHODS_SUFFICIENT: the strongest-parent "
            "incremental gap was frozen at 0 of 32 BEFORE execution",
            "TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT (failure-to-negative-knowledge atom)",
            "P7_TRANSPORT_SUFFICIENT (negative-knowledge staleness atom)",
            "MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED (silent-failure observability atom)",
        ],
        "authority": (
            "This receipt records a calibration of a scoped failure store against three parents on "
            "seven authored worlds. It establishes no causal mechanism and no advantage over the "
            "truth-maintenance parent outside the three cause-discriminating worlds."
        ),
    }
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(json.dumps({"terminal": terminal, "totals": totals, "out": str(out)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
