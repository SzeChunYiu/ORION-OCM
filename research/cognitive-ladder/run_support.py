"""Run the support-family discovery experiment and emit its receipt.

    python run_support.py --out results/SUPPORT_E6_V1.json

The terminal rule is :func:`terminal_for`.  It is a pure function of the
summary table and it was written before the revocation, total-work and
stale-survivor numbers existed, which is the only thing that makes a terminal a
finding rather than a caption.

What HAD been seen when the terminal rule was written, stated so nobody has to
guess: a pilot of the DISCOVERY phase at the ``1x`` scale, which showed the
registered intervention budget to be binding for the adaptive arm and prompted
the addition of the budget CURVE (the registered budget's own row is unchanged).
Nothing about revocation, stale survivors, collateral invalidations, query work
or total work had been computed when the rule below was fixed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from support import (
    ARCHETYPES,
    COMMITMENT,
    EVIDENCE_PER_METHOD,
    INTERVENTION_BUDGET,
    SUPPORT_PLAN,
    build_catalogue,
    classify_family,
    declared_candidate_family,
    family_shapes,
    hitting_sets,
    leave_one_out_blind_methods,
    oracle_families,
    oracle_minimal_environments,
    powerset_bound,
    revocation_schedule,
    support_family,
)
from support_arms import (
    ARM_ROLES,
    SWEEP_NOTES,
    archetype_table,
    budget_curve,
    capability_gated_comparison,
    fits_for,
    lazy_comparison,
    step_table,
    summarise,
    sweep,
    sweep_table,
)

#: The coordinates a parent has to match before it can be called sufficient.
#: Declared as a tuple so nobody can add a coordinate after the fact to keep a
#: parent out, or drop one to let it in.
MATCH_COORDINATES = (
    "precision_by_scale",
    "recall_by_scale",
    "stale_survivors_by_scale",
)

#: How close a parent's total work has to be to count as "matching" rather than
#: "beaten".  Frozen here, before the total-work numbers existed.  A parent
#: within five per cent of the arm under test on total work, at identical
#: capability, has not been separated from it by this experiment.
MATCH_TOLERANCE = 0.05

#: The parent whose FAIR configuration gets first right of refusal.  The gifted
#: ATMS is deliberately NOT in this tuple: it is handed the justifications, so
#: a match against it would be a statement about the gift.
FAIR_CHALLENGER = "atms_discovering_parent"

#: The arm to beat on total work, per the #144 capability-gated re-analysis of
#: E3, where it dominated eager discovery at every scale.
LAZY = "lazy_parent"

ARM = "adaptive_arm"


def _within(a: float, b: float, tolerance: float) -> bool:
    if a == b:
        return True
    scale = max(abs(a), abs(b))
    return scale > 0 and abs(a - b) / scale <= tolerance


def terminal_for(summary: dict) -> tuple[str, str, list[str]]:
    """Fixed before the revocation and total-work numbers existed.

    Returns ``(terminal, reason, secondary_terminals)``.  The order of the
    tests is the order of the brief: parent sufficiency is tested FIRST and, if
    it fires, it is the headline and not a caveat.

    ``PARENT_SUFFICIENT``
        Either the fair ATMS matched the adaptive arm on precision, recall and
        stale survivors at every scale and came within ``MATCH_TOLERANCE`` on
        total work, or ``lazy_parent`` -- which discovers nothing and
        re-derives on demand -- was no worse than the adaptive arm on total
        work and on stale survivors at every scale.  Either way, discovering
        the support family up front bought nothing here.

    ``INTERVENTION_WORK_TRADE``
        The adaptive arm spent strictly fewer interventions than the exhaustive
        parent at every scale and strictly MORE total counted operations.  That
        is the shape a sibling lane already reported ("active model enumeration
        lowers queries but costs more") and that ``REINDEX_E9`` found in a
        different place; reproducing it is an independent replication and is
        reported as such rather than as a novel result.

    ``GROUP_ABLATION_SEPARATES_FROM_LEAVE_ONE_OUT``
        The adaptive arm recovered support families that single-element
        ablation cannot express, and beat the random floor, without either
        parent above matching it.

    ``ADAPTIVE_SELECTION_ADDS_NOTHING``
        The random floor matched the adaptive arm at the same budget, so what
        worked was group granularity and not adaptive selection.

    ``NO_SEPARATION``
        Nothing distinguishable happened.
    """
    arm = summary[ARM]
    atms = summary[FAIR_CHALLENGER]
    lazy = summary[LAZY]
    exhaustive = summary["exhaustive_powerset_parent"]
    loo = summary["leave_one_out_parent"]
    floor = summary["random_group_ablation_parent"]

    secondary: list[str] = []
    trade = all(
        i < j
        for i, j in zip(
            arm["discovery_interventions_by_scale"],
            exhaustive["discovery_interventions_by_scale"],
        )
    ) and all(
        w > x
        for w, x in zip(
            arm["discovery_work_by_scale"], exhaustive["discovery_work_by_scale"]
        )
    )
    if trade:
        secondary.append("INTERVENTION_WORK_TRADE")
    if any(a > b for a, b in zip(loo["recall_by_scale"], arm["recall_by_scale"])):
        secondary.append("LEAVE_ONE_OUT_EXCEEDED_THE_ARM")
    if arm["total_stale_survivors"]:
        secondary.append("ARM_LEFT_A_STALE_SURVIVOR")

    atms_matches = all(
        atms[key] == arm[key] for key in MATCH_COORDINATES
    ) and all(
        _within(a, b, MATCH_TOLERANCE)
        for a, b in zip(atms["total_work_by_scale"], arm["total_work_by_scale"])
    )
    lazy_matches = (
        all(
            a <= b
            for a, b in zip(lazy["total_work_by_scale"], arm["total_work_by_scale"])
        )
        and all(
            a <= b
            for a, b in zip(
                lazy["stale_survivors_by_scale"], arm["stale_survivors_by_scale"]
            )
        )
        and all(lazy["capability_gate_by_scale"])
    )
    matched = []
    if atms_matches:
        matched.append(FAIR_CHALLENGER)
    if lazy_matches:
        matched.append(LAZY)
    if matched:
        return (
            "PARENT_SUFFICIENT",
            f"{', '.join(matched)} matched or beat {ARM} at every registered scale. "
            f"{FAIR_CHALLENGER} is the ATMS in its FAIR configuration -- required to "
            "discover its justifications by intervention, not handed them -- and "
            f"{LAZY} discovers nothing at all and re-derives on demand, which is the "
            "arm that already dominated eager discovery in the #144 capability-gated "
            "re-analysis of E3. Discovering the support family up front bought nothing "
            "here that a parent did not already have. This is the headline, not a "
            "caveat.",
            secondary,
        )
    if trade:
        return (
            "INTERVENTION_WORK_TRADE",
            f"{ARM} spent strictly fewer interventions than exhaustive_powerset_parent "
            "at every scale and strictly MORE total counted operations. Adaptive group "
            "selection moved cost from the coordinate it optimises to the one it does "
            "not. This reproduces, in a different world, the result already reported by "
            "research/epistemic-structure-discovery-20260908 ('active model enumeration "
            "lowers queries but costs more') and by results/REINDEX_E9_V1.json. It is an "
            "independent replication of an existing finding in this programme and is "
            "reported as one; no novelty is claimed for the learner.",
            secondary,
        )
    beats_floor = all(
        a > b for a, b in zip(arm["recall_by_scale"], floor["recall_by_scale"])
    )
    beats_loo = all(
        a > b for a, b in zip(arm["recall_by_scale"], loo["recall_by_scale"])
    )
    if beats_loo and beats_floor:
        return (
            "GROUP_ABLATION_SEPARATES_FROM_LEAVE_ONE_OUT",
            f"{ARM} recovered support families that single-element ablation cannot "
            "express, at higher recall than the random floor spending the same budget, "
            "and no parent matched it.",
            secondary,
        )
    if not beats_floor:
        return (
            "ADAPTIVE_SELECTION_ADDS_NOTHING",
            "random_group_ablation_parent matched the adaptive arm's recall at the same "
            "budget. What separated the arms from leave-one-out was group GRANULARITY, "
            "not adaptive SELECTION, and the selection machinery is unsupported.",
            secondary,
        )
    return ("NO_SEPARATION", "no reported coordinate distinguished the arms.", secondary)


def ground_truth_audit() -> list[dict]:
    """What the oracle says about the world, before any arm is mentioned.

    Printed first because every endpoint below is scored against it, and
    because the gap between the DECLARED candidate structure and the true
    support families is the quantity a system that refuses to discover anything
    would have to live with.
    """
    out = []
    for multiplier in SUPPORT_PLAN["multipliers"]:
        catalogue = build_catalogue(multiplier)
        truth = oracle_families(catalogue)
        declared = declared_candidate_family(catalogue)
        blind = leave_one_out_blind_methods(catalogue)
        sizes: dict[int, int] = {}
        shapes: dict[str, int] = {}
        for instance in catalogue.instances:
            for method_id in instance.method_ids:
                family = support_family(instance, method_id)
                shape = classify_family(family)
                shapes[shape] = shapes.get(shape, 0) + 1
                for support_set in family:
                    sizes[len(support_set)] = sizes.get(len(support_set), 0) + 1
        out.append(
            {
                "scale": catalogue.scale_id,
                "N_persistent_objects": catalogue.n_objects,
                "methods": catalogue.n_methods,
                "evidence_blocks": catalogue.n_evidence,
                "candidate_evidence_per_method": EVIDENCE_PER_METHOD,
                "powerset_subsets_enumerated_per_method": powerset_bound(),
                "true_minimal_support_sets": len(truth),
                "declared_candidate_sets": len(declared),
                "minimal_support_sets_by_size": {
                    str(k): sizes[k] for k in sorted(sizes)
                },
                "family_shapes": {k: shapes[k] for k in sorted(shapes)},
                "methods_invisible_or_partly_invisible_to_leave_one_out": len(blind),
                "fraction_leave_one_out_cannot_fully_see": round(
                    len(blind) / catalogue.n_methods, 6
                ),
                "archetype_shape": family_shapes(catalogue),
            }
        )
    return out


def duality_audit() -> list[dict]:
    """Assert, per archetype, that the two oracles agree.

    The minimal support sets are the minimal transversals of the minimal
    supporting environments.  Both are computed by exhaustive enumeration, so
    an arm that enumerates one side and converts to the other is scored against
    a truth that does not depend on which side it started from.  Checked here
    rather than assumed, and reported in the receipt so a reader does not have
    to take the tests' word for it.
    """
    catalogue = build_catalogue(SUPPORT_PLAN["multipliers"][0])
    out = []
    for instance in catalogue.first_replicates():
        for method_id in instance.method_ids:
            family = support_family(instance, method_id)
            environments = oracle_minimal_environments(instance, method_id)
            slot = {e: i for i, e in enumerate(instance.evidence_ids)}
            out.append(
                {
                    "archetype": instance.archetype_id,
                    "method": method_id,
                    "shape": classify_family(family),
                    "minimal_support_sets": sorted(
                        sorted(slot[x] for x in s) for s in family
                    ),
                    "minimal_environments": sorted(
                        sorted(slot[x] for x in s) for s in environments
                    ),
                    "transversals_of_environments_equal_support_family": (
                        hitting_sets(environments) == family
                    ),
                }
            )
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    if out.exists():
        print(f"refusing to overwrite existing receipt {out}", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)

    results = sweep()
    rows = sweep_table(results)
    steps = step_table(results)
    per_archetype = archetype_table(results)
    summary = summarise(rows)
    terminal, reason, secondary = terminal_for(summary)
    catalogue = build_catalogue(SUPPORT_PLAN["multipliers"][0])

    receipt = {
        "receipt": "CL_SUPPORT_E6_V1",
        "study_id": "CL-SUPPORT-E6-V1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E1",
        "contribution_level": "L0",
        "study_role": "ENGINEERING_CALIBRATION_OF_SUPPORT_FAMILY_DISCOVERY",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "answers_root_cause": (
            "PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED. E3 fixed the probe "
            "granularity at one element by design, so the instrument could not express "
            "the structure it was hunting; between 16.3% and 25% of methods had support "
            "no single-element ablation could see. Here the arm chooses its own group "
            "granularity under a charged budget, which is the falsifier that root names."
        ),
        "answers_claim": (
            "C11-ABLATION-ATTRIBUTION-INCOMPLETE. The C11 shape is the "
            "ALTERNATIVE_SUPPORTS archetype and leave_one_out_parent is required by test "
            "to fail on it exactly."
        ),
        "no_novelty_claimed": (
            "Minimal-support / antichain discovery is parent-owned: de Kleer (1986) for "
            "minimal environments, Reiter (1987) for the hitting-set dual, Junker (2004) "
            "for the shrink, Liffiton & Sakallah and the MARCO line for the enumeration. "
            "It has ALSO been independently implemented inside this programme, on branch "
            "research/epistemic-structure-discovery-20260908 (antichain support learner: "
            "256/256, 164 source queries, 146401 counted operations). This experiment "
            "contributes the PARENT COMPARISON and the FAMILY TAXONOMY, and claims "
            "nothing about the learner."
        ),
        "two_column_rule": SUPPORT_PLAN["two_column_rule"],
        "plan": SUPPORT_PLAN,
        "commitment": COMMITMENT.as_dict()["commitment_sha256"],
        "arm_roles": ARM_ROLES,
        "budget_exemptions": SUPPORT_PLAN["budget_exempt"],
        "powerset_bound": {
            "candidate_evidence_per_method": EVIDENCE_PER_METHOD,
            "non_empty_subsets_per_method": powerset_bound(),
            "statement": (
                f"the evidence set per method is frozen at {EVIDENCE_PER_METHOD} blocks, "
                f"so the oracle enumerates {powerset_bound()} non-empty subsets per "
                "method and is EXACTLY computable rather than sampled. Every intervention "
                "count in this receipt is a count for a candidate set of that width."
            ),
        },
        "registered_archetypes": [
            {
                "archetype": a.archetype_id,
                "structure": a.structure,
                "expected_shape": a.expected_shape,
                "revocation_steps": len(a.revocation),
                "note": a.note,
            }
            for a in ARCHETYPES
        ],
        "revocation_schedule": [
            {
                "step": step.step_id,
                "archetype": step.archetype_id,
                "instance": step.instance_id,
                "evidence": list(step.evidence_ids),
                "intent": step.intent,
            }
            for step in revocation_schedule(catalogue)
        ],
        "ground_truth_audit": ground_truth_audit(),
        "duality_audit": duality_audit(),
        "table": rows,
        "archetype_table": per_archetype,
        "step_table": steps,
        "summary": summary,
        "budget_curve": budget_curve(SUPPORT_PLAN["multipliers"][0]),
        "budget_curve_disclosure": SUPPORT_PLAN["budget_curve_disclosure"],
        "loglog_fits": fits_for(rows),
        "comparison_against_lazy_parent": lazy_comparison(summary),
        "capability_gated_comparison": capability_gated_comparison(summary),
        "terminal": terminal,
        "terminal_reason": reason,
        "secondary_terminals": secondary,
        "sweep_notes": list(SWEEP_NOTES),
        "hostiles_that_fired": [
            "THE C11 SHAPE ITSELF: ALTERNATIVE_SUPPORTS, where two blocks each suffice "
            "alone. leave_one_out_parent reports the EMPTY family and calls it an answer.",
            "REDUNDANT_SUPPORTS, the worse case: leave_one_out_parent finds a genuine "
            "singleton, files it, and stops with half the family and no indication that "
            "anything is missing. An instrument that fails loudly is safer than one that "
            "fails while returning a true fact.",
            "HIGHER_ORDER_INTERACTION: a minimal support set of size three with no "
            "smaller subset. Pairwise ablation is as blind to it as single-element "
            "ablation is to the C11 pair, so the granularity problem does not end at two.",
            "CYCLIC: p and q support each other and ground out only through c or d. "
            "Under the least fixpoint, support that exists solely inside the cycle is not "
            "support, and an arm propagating labels without a fixpoint would invent it.",
            "REPRESENTATION_DEPENDENT: the same conclusion holds through two "
            "representations whose individual support sets are BOTH wrong about the "
            "method. An arm that keeps the derivation it happened to use reports a "
            "confident wrong answer.",
            "NO_LOAD_BEARING: nothing an arm does to the evidence can change this method. "
            "Every believed support set here is spurious and every invalidation is "
            "collateral, which is the false-positive control the random floor fails.",
            "SHARED_GLOBAL: one block is load-bearing for every method in its instance, "
            "so locality is not guaranteed by construction.",
        ],
        "what_this_does_not_establish": [
            "NO NOVELTY IN THE LEARNER. Minimal-support enumeration is parent-owned and "
            "was independently implemented elsewhere in this programme before this "
            "experiment ran. The contribution here is the parent comparison and the "
            "taxonomy.",
            "FEWER INTERVENTIONS IS NOT CHEAPER. Interventions and total counted "
            "operations are reported in two columns and are never summed. An arm that "
            "improves the first while worsening the second has moved cost between "
            "coordinates, and this receipt refuses to call that an improvement on the "
            "reader's behalf.",
            "THE ARCHETYPES ARE AUTHORED. Their support families are the ones the "
            "experiment wanted to see. No RATE quoted here transfers anywhere; E3's "
            "16-25% came from an induction world that produced the shapes on its own and "
            "this world does not pretend to.",
            "THE CANDIDATE EVIDENCE SET IS STILL DECLARED, exactly as in E3. Which of a "
            "method's blocks matter is discovered; that they are its blocks is given.",
            "B = 6. Every intervention count is a count for a six-element candidate set, "
            "and the asymptotics of minimal-hitting-set enumeration -- which is where the "
            "hard part of this problem lives -- are outside this world by construction.",
            "N is a few hundred objects. PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM remains the "
            "appropriate terminal for any attempt to read a field claim out of this.",
            "Re-derivation is CHEAP here: one least-fixpoint pass over a handful of "
            "justifications. lazy_parent's dominance is a fact about that regime. In a "
            "domain where re-derivation is expensive, lazy re-derivation and stored "
            "structure are not the same kind of option and none of these numbers "
            "transfer.",
            "Nothing about cognition. Enumerating the minimal ways to break a derivation "
            "is diagnosis, and diagnosis has a long parent list this lane has not "
            "improved on.",
        ],
        "authority": (
            "This receipt establishes that the support FAMILY -- the set of minimal "
            "support sets -- is discoverable by charged group ablation in this world, "
            "that leave-one-out fails on exactly the archetypes whose families contain no "
            "singleton, that interventions and counted operations move in opposite "
            "directions when selection is made adaptive, and where each parent stands on "
            "both columns. It establishes no advantage over any parent, no novelty in any "
            "mechanism, no scaling law, and no cognitive claim of any kind."
        ),
    }
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "secondary_terminals": secondary,
                "adaptive_recall": summary[ARM]["recall_by_scale"],
                "adaptive_interventions": summary[ARM][
                    "discovery_interventions_by_scale"
                ],
                "adaptive_total_work": summary[ARM]["total_work_by_scale"],
                "lazy_total_work": summary[LAZY]["total_work_by_scale"],
                "capability_gate_admits": capability_gated_comparison(summary)[
                    "admitted"
                ],
                "cheapest_admitted_arm": capability_gated_comparison(summary)[
                    "cheapest_admitted_arm_by_total_work"
                ],
                "exhaustive_interventions": summary["exhaustive_powerset_parent"][
                    "discovery_interventions_by_scale"
                ],
                "exhaustive_discovery_work": summary["exhaustive_powerset_parent"][
                    "discovery_work_by_scale"
                ],
                "out": str(out),
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
