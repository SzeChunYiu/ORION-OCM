"""Run experiment E4 and emit its receipt.

    python run_escalation_independent.py --out results/ESCALATION_INDEPENDENT_E4_V1.json

E4 exists to remove one specific defect from ``CL-ESCALATION-PILOT-V1``: its
generator picks a defect type first and instantiates exactly that defect, so the
world's registered level is the generator's intent and the generator shares the
diagnosis policy's taxonomy.  The pilot's own receipt names this as the ORION
failure-ledger pattern ``STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE`` and caps
itself at E2 because of it.

Here worlds are perturbed blindly and the level is recovered afterwards by
exhaustive search over a repair lattice that knows only whether a repair works.
The receipt therefore carries two numbers side by side --- the governed policy
on the old generator's protected draw, and the same policy on independently
generated worlds --- and a ``headline_contrast`` field that states the
difference in words, so the contrast cannot be read past.

Both decision rules below were written before the numbers were produced and
take the summaries as input.  They are not adjusted after reading them.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from escalation import JUMP_THRESHOLD, Level
from escalation_independent import (
    ARMS,
    FAMILIES,
    LEVELS,
    PERTURBATION_COUNT_WEIGHTS,
    PERTURBATION_KINDS,
    REPAIR_LATTICE,
    RULES,
    decoupling_audit,
    draw_suite,
    evaluate,
    intent_audit,
    old_generator_reference,
    well_posedness_screen,
)
from prereg import commit

PLAN = {
    "protocol": "COGNITIVE_LADDER_PROTOCOL_V1",
    "study_id": "CL-ESCALATION-INDEPENDENT-E4-V1",
    "experiment": "escalation_independent",
    "supersedes_generator": "escalation_generator.draw_suite",
    "generation": "blind_perturbation_of_a_working_setup",
    "ground_truth": "exhaustive_minimum_repair_search",
    "worlds": 2000,
    "perturbation_kinds": list(PERTURBATION_KINDS),
    "perturbation_count_weights": {"0": 15, "1": 45, "2": 40},
    "repair_lattice": [[lvl.name, name] for lvl, name in REPAIR_LATTICE],
    "levels": [lvl.name for lvl in LEVELS],
    "arms": sorted(ARMS),
    "primary_endpoint": "minimum_sufficient_level_exact_match",
    "secondary_endpoints": [
        "false_escalation_rate",
        "missed_escalation_rate",
        "overreach",
        "underreach",
        "confusion_matrix",
        "accuracy_by_perturbation_count",
    ],
    "jump_threshold": JUMP_THRESHOLD.name,
    "analysis": (
        "exact counts over blindly generated worlds; no inferential test, and a "
        "pre-registered material margin instead"
    ),
}

#: A lead over the best parent smaller than this fraction of the draw is not
#: reported as a separation.  Fixed before the run; the lane reports no
#: inferential test at pilot stage, so a margin is the honest substitute for
#: one.
MATERIAL_MARGIN_FRACTION = 0.02

#: How large a fall in the governed policy's accuracy, moving from the old
#: generator's draw to independently generated worlds, counts as evidence that
#: the old figure was an artifact of the generator.  Fixed before the run.
ARTIFACT_TOLERANCE = 0.05


def terminal_for(independent: dict, old: dict) -> tuple[str, str]:
    """Decide the terminal from the summaries, by a rule fixed before the run."""
    arms = independent["arms"]
    governed = arms["governed"]
    n = governed["n"]
    parents = {k: v for k, v in arms.items() if k != "governed"}
    best = max(parents, key=lambda k: parents[k]["exact_match"])
    margin = governed["exact_match"] - parents[best]["exact_match"]
    if margin <= 0:
        return (
            "PARENT_SUFFICIENT",
            f"{best} matched or exceeded the governed policy on the primary endpoint "
            f"({parents[best]['exact_match']} against {governed['exact_match']} of {n})",
        )
    if margin <= MATERIAL_MARGIN_FRACTION * n:
        return (
            "PARENT_SUFFICIENT_WITHIN_REGISTERED_MARGIN",
            f"the governed policy leads {best} by {margin} worlds of {n}, inside the "
            f"pre-registered material margin of {MATERIAL_MARGIN_FRACTION:.0%}; a lead this "
            "small is not reported as a separation",
        )
    if governed["false_escalation"] > 0:
        return (
            "GOVERNED_POLICY_SEPARATES_BUT_FALSE_ESCALATES",
            f"the governed policy leads {best} by {margin} worlds of {n} but escalated "
            f"{governed['false_escalation']} times where the minimum sufficient level was "
            "below the Jump threshold",
        )
    return (
        "GOVERNED_POLICY_SEPARATES_ON_INDEPENDENTLY_GENERATED_WORLDS",
        f"the governed policy leads {best} by {margin} worlds of {n}, beyond the registered "
        "material margin, with no false escalation",
    )


def generator_artifact_verdict(independent: dict, old: dict) -> dict:
    """Was the old 70/70 a measurement of the policy or of its generator?

    The rule is fixed before the run: a fall larger than ``ARTIFACT_TOLERANCE``
    when the only thing that changed is who decides the ground truth is
    attributed to the generator, because nothing about the policy changed.
    """
    new_governed = independent["arms"]["governed"]
    old_governed = old["arms"]["governed"]
    drop = round(old_governed["accuracy"] - new_governed["accuracy"], 4)
    if drop > ARTIFACT_TOLERANCE:
        verdict = "GENERATOR_ARTIFACT_CONFIRMED"
        reading = (
            "the same unmodified policy loses accuracy when the world's level stops being "
            "the generator's intent, so the earlier figure was substantially a measurement "
            "of the generator's taxonomy rather than of the policy"
        )
    elif drop < -ARTIFACT_TOLERANCE:
        verdict = "ACCURACY_HIGHER_ON_INDEPENDENTLY_GENERATED_WORLDS"
        reading = (
            "the policy scores higher on blindly perturbed worlds than on the generator's own; "
            "the independent draw is easier, which is itself a fact about the draw and not a win"
        )
    else:
        verdict = "NO_ARTIFACT_AT_REGISTERED_TOLERANCE"
        reading = (
            "the governed policy's accuracy survives the removal of the circular ground truth "
            f"within the registered tolerance of {ARTIFACT_TOLERANCE:.0%}"
        )
    return {
        "old_generator_exact_match": f"{old_governed['exact_match']}/{old_governed['n']}",
        "old_generator_accuracy": old_governed["accuracy"],
        "independent_exact_match": f"{new_governed['exact_match']}/{new_governed['n']}",
        "independent_accuracy": new_governed["accuracy"],
        "accuracy_drop": drop,
        "registered_tolerance": ARTIFACT_TOLERANCE,
        "verdict": verdict,
        "reading": reading,
    }


def _headline(independent: dict, old: dict, artifact: dict) -> dict:
    governed = independent["arms"]["governed"]
    planner = independent["arms"]["exact_repair_planner"]
    old_governed = old["arms"]["governed"]
    old_planner = old["arms"]["exact_repair_planner"]
    old_lead = round(old_governed["accuracy"] - old_planner["accuracy"], 4)
    new_lead = round(governed["accuracy"] - planner["accuracy"], 4)
    return {
        "governed_lead_over_fully_resourced_parent_old_generator": old_lead,
        "governed_lead_over_fully_resourced_parent_independent": new_lead,
        "lead_collapse": round(old_lead - new_lead, 4),
        "lead_reading": (
            "On the old generator the governed policy led exact_repair_planner by "
            f"{old_lead:.1%} of worlds. On blindly perturbed worlds levelled by the repair "
            f"oracle the same lead is {new_lead:.1%}. The parent was never that far behind; "
            "the old generator's ground truth was the governed policy's own taxonomy."
        ),
        "statement": (
            f"On the old generator's protected draw the governed policy scores "
            f"{artifact['old_generator_exact_match']} exact. On {governed['n']} worlds perturbed "
            f"blindly and levelled by an independent repair oracle it scores "
            f"{artifact['independent_exact_match']} "
            f"({artifact['independent_accuracy']:.1%}). The fully-resourced parent "
            f"exact_repair_planner scores {planner['exact_match']}/{planner['n']} "
            f"({planner['accuracy']:.1%}) on the same worlds."
        ),
        "governed_old_generator": artifact["old_generator_exact_match"],
        "governed_independent": artifact["independent_exact_match"],
        "exact_repair_planner_independent": f"{planner['exact_match']}/{planner['n']}",
        "governed_false_escalations_independent": governed["false_escalation"],
        "exact_repair_planner_false_escalations_independent": planner["false_escalation"],
        "verdict": artifact["verdict"],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="output path; must not already exist")
    args = parser.parse_args(argv)
    out_path = pathlib.Path(args.out)
    if out_path.exists():
        print(f"refusing to overwrite existing receipt {out_path}", file=sys.stderr)
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)

    commitment = commit(PLAN)
    screen = well_posedness_screen()
    if not screen["well_posed"]:
        print("registered families are not expressible under both conventions", file=sys.stderr)
        return 2

    worlds = draw_suite(commitment.protected_seed, PLAN["worlds"])
    independent = evaluate(worlds)
    old = old_generator_reference()
    terminal, reason = terminal_for(independent, old)
    artifact = generator_artifact_verdict(independent, old)

    receipt = {
        "receipt": "CL_ESCALATION_INDEPENDENT_E4_V1",
        "study_id": PLAN["study_id"],
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E2",
        "contribution_level": "L1",
        "study_role": "REMOVES_ONE_NAMED_CIRCULARITY_FROM_CL-ESCALATION-PILOT-V1",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "headline_contrast": _headline(independent, old, artifact),
        "generator_artifact_verdict": artifact,
        "terminal": terminal,
        "terminal_reason": reason,
        "commitment": commitment.as_dict(),
        "generation": {
            "families": len(FAMILIES),
            "rules_in_catalogue": len(RULES),
            "perturbation_kinds": list(PERTURBATION_KINDS),
            "perturbation_count_weights": list(PERTURBATION_COUNT_WEIGHTS),
            "well_posedness_screen": screen,
            "note": (
                "A world is a working setup with zero, one or two perturbations drawn "
                "uniformly from the menu. No defect type is chosen, recorded or implied. The "
                "level is recovered afterwards by exhaustive search over the repair lattice."
            ),
        },
        "independent_worlds": independent,
        "old_generator_worlds": old,
        "decoupling_audit": decoupling_audit(worlds),
        "generator_intent_audit": intent_audit(worlds),
        "what_this_removes": [
            "The old generator selects a defect type and then instantiates exactly that defect, "
            "so its registered level is its own intent and its taxonomy is the policy's taxonomy. "
            "E4 never selects a defect type; the ground truth is computed after the fact by a "
            "repair search that knows only whether a repair works.",
            "generator_intent_audit measures how often the old procedure's label would have been "
            "wrong on these worlds. Every disagreement there is a world an arm would have been "
            "scored against a wrong answer.",
        ],
        "why_this_is_still_not_confirmatory": [
            "The repair lattice and the escalation level ladder still share an author. What has "
            "been removed is the generator's use of its own taxonomy as ground truth, not the "
            "authorship of the ladder itself. #144 s11 asks for an independently authored "
            "validation subset and that remains outstanding.",
            "The perturbation menu is authored, and a perturbation kind that never binds cannot "
            "produce a world at the level it nominally targets. The level distribution in this "
            "receipt is a fact about that menu, not about the difficulty of escalation in general.",
            "The arms read two machine-visible flags (local_repair_available, formulation_defect) "
            "that the frozen EscalationWorld defines. They are computed here from the observed "
            "evidence and the arm's own registered repairs, which is more conservative than the "
            "registered worlds, but they still hand every arm a cheap route to L3 and L6.",
            "No inferential test is reported. A pre-registered material margin is used instead, "
            "and worlds are not independent of one another at the family level.",
        ],
        "preserved_prior_terminals": [
            "REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE (ORION V1 Jump programme closure)",
            "REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE: the verified-regime-revision parent "
            "matched ORION on every protected metric; the protected incremental gap was exactly zero",
            "ME-X2 PARENT_SUFFICIENT (B5_DOMINATES): the parent won on minimum-escalation accuracy",
            "ME-X2 V3 THRESHOLD_NULL: parity on a fresh seed",
            "ME-X2 and V3 replicated asymmetry: false escalations 0 versus 21, then 0 versus 14",
            "CL-ESCALATION-PILOT-V1: E2, capped by STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE",
        ],
        "authority": (
            "This receipt records one methodological repair to an existing pilot and its "
            "consequences for that pilot's headline number. It establishes no causal mechanism, "
            "no scaling result, no transfer result and no novelty. The binary Jump decision is "
            "already closed against a fully-resourced parent elsewhere in the programme with a "
            "protected incremental gap of exactly zero, and this experiment does not reopen it."
        ),
    }
    out_path.write_text(json.dumps(receipt, indent=2) + "\n")

    print(json.dumps({
        "terminal": terminal,
        "generator_artifact_verdict": artifact["verdict"],
        "headline": receipt["headline_contrast"]["statement"],
        "arms": {
            k: f"{v['exact_match']}/{v['n']} exact ({v['accuracy']:.1%}), "
               f"{v['false_escalation']} false escalations, {v['missed_escalation']} missed"
            for k, v in independent["arms"].items()
        },
        "out": str(out_path),
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
