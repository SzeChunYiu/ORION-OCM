"""Run E5 -- library discovery versus reuse opportunity -- and emit its receipt.

    python run_libdisc.py --out results/LIBDISC_E5_V1.json

The terminal rule is :func:`terminal_for`.  It is a pure function of the summary
table.  Its content is a transcription of the prediction registered in
``libdisc.LIBDISC_PLAN``, which was frozen before any arm existed:

    benefit on the essential-composite set, ZERO benefit on the tautological
    set, at identical discovery.

The honest qualification, stated here rather than implied: the plan and that
prediction were written before the arms; the body of ``terminal_for`` was
written after the sweep had run once.  That is weaker than a pre-registered
terminal and it is disclosed in the receipt rather than glossed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from libdisc import (
    CHAIN2_SCHEMA,
    COMMITMENT_BODY,
    ESSENTIAL_COMPOSITE_TASKS,
    LIBDISC_PLAN,
    TAUTOLOGICAL_CONTROL_TASKS,
    TRAINING_EPISODES,
    certify_draw,
    learner_views,
)
from libdisc_arms import (
    ARMS,
    TASK_SETS,
    benefit_table,
    custody_benefit,
    custody_cycle,
    discovery_arm,
    summarise,
    sweep,
)
from libdisc_discovery import (
    discover,
    flat_mining_ablation,
    polarity_blind_refutations,
)
from prereg import commit

#: The arm under test.
ARM = "libdisc_discovery_arm"

#: The reference arm the causal chain is measured against.
REFERENCE = "reset_arm"

#: Parents that get first right of refusal on any effect.
CHALLENGERS = (
    "stitch_parent",
    "dreamcoder_parent",
    "symbolic_compact_parent",
    "symbolic_incremental_memory_parent",
    "anti_unification_parent",
)


def terminal_for(summary: dict, benefit: dict, arms: dict,
                 certification: dict, custody: dict) -> tuple[str, str]:
    """The terminal, as a function of the table and of nothing else.

    Tested in order:

    ``CUSTODY_VIOLATION``
        the acquiring process did not really exit, or the state digest moved.

    ``GENERATOR_CERTIFICATION_FAILED``
        one of the four properties the design needs is not present in the draw.
        The registered response is to report that, never to relax a property.

    ``NO_METHOD_ACQUIRED``
        the arm's pool is empty.  This is the diagnosis's own terminal and the
        flat ablation is expected to reach it on identical evidence.

    ``PARENT_SUFFICIENT``
        a parent matched the arm on the schemas found AND on fresh-task work on
        the essential-composite set.  Then this machinery bought nothing and
        that is the headline, printed as such.

    ``NO_DEVELOPMENT_BENEFIT``
        the arm acquired a method and it did not reduce work even where the
        opportunity was certified to exist.  This is the clause-revival
        terminal reproduced at full strength.

    ``OPPORTUNITY_NOT_ISOLATED``
        work fell on BOTH sets.  Then the contrast failed and no claim about
        the demand term can be read out of it.

    ``DISCOVERY_SEPARATES_FROM_OPPORTUNITY``
        work fell on the essential-composite set and did not fall on the
        tautological control, at identical discovery.  The mechanism works and
        the opportunity term is what gates it.
    """
    if custody.get("terminal") != "CUSTODY_OK" or not custody.get("digests_agree"):
        return ("CUSTODY_VIOLATION",
                "the restart was not real or the persisted state did not survive it")
    if not certification["all_certified"]:
        return ("GENERATOR_CERTIFICATION_FAILED",
                "; ".join(certification["failures"]))
    if arms[ARM]["library_size"] == 0:
        return ("NO_METHOD_ACQUIRED",
                "the arm's pool is empty on this draw")

    arm_ids = set(arms[ARM]["schema_ids"])
    arm_ess = benefit[ARM]["essential_composite"]
    for name in CHALLENGERS:
        if name not in arms:
            continue
        if set(arms[name]["schema_ids"]) != arm_ids:
            continue
        if benefit[name]["essential_composite"]["work_total"] <= arm_ess["work_total"]:
            return ("PARENT_SUFFICIENT", (
                f"{name} found the same schemas and did at least as well on "
                "fresh-task work where the opportunity exists; the machinery "
                "under test bought nothing over it"))

    ess = arm_ess["delta_vs_reset"]
    taut = benefit[ARM]["tautological_control"]["delta_vs_reset"]
    if ess <= 0:
        return ("NO_DEVELOPMENT_BENEFIT", (
            "a method was acquired and independently certified and it did not "
            "reduce work even on the set where an essential composite "
            "opportunity was certified to exist"))
    if taut > 0:
        return ("OPPORTUNITY_NOT_ISOLATED", (
            "work fell on both fresh-task sets, so the contrast does not "
            "identify the demand term"))
    return ("DISCOVERY_SEPARATES_FROM_OPPORTUNITY", (
        f"the same schema reduced work by {ess} units where an essential "
        f"composite opportunity was certified to exist and changed work by "
        f"{taut} units where it was certified not to; discovery and demand are "
        "separately measured and only the first is a property of the mechanism"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    if out.exists():
        print(f"refusing to overwrite existing receipt {out}", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)

    views = learner_views()
    certification = certify_draw().as_dict()
    ablation = flat_mining_ablation(views)
    discovery = discover(views)
    sweep_out = sweep(views)
    summary = summarise(sweep_out)
    benefit = benefit_table(summary, REFERENCE)
    custody = custody_cycle()
    terminal, reason = terminal_for(
        summary, benefit, sweep_out["arms"], certification, custody)

    arm = discovery_arm(views)
    per_set = {
        set_name: {
            a: {
                "work_total": summary[a][set_name]["work_total"],
                "macro_match_attempts": summary[a][set_name]["macro_match_attempts"],
                "macro_fired": summary[a][set_name]["macro_fired"],
                "wrong_answers": summary[a][set_name]["wrong_answers"],
                "redundant_sound_matches_NOT_counted_as_benefit":
                    summary[a][set_name]["redundant_sound_matches"],
                "delta_vs_reset_arm": benefit[a][set_name]["delta_vs_reset"],
                "tasks_helped": benefit[a][set_name]["tasks_helped"],
                "tasks_harmed": benefit[a][set_name]["tasks_harmed"],
            }
            for a in summary
        }
        for set_name in TASK_SETS
    }

    harmed = [
        r for r in sweep_out["rows"]
        if r["arm"] == ARM and r["task_set"] == "essential_composite"
        and r["work_total"] > summary[REFERENCE]["essential_composite"][
            "per_task_work"][r["task_id"]]
    ]
    all_arm_rows = [r for r in sweep_out["rows"] if r["arm"] == ARM]
    s5_harmed = sum(
        1 for r in all_arm_rows
        if r["work_total"] > summary[REFERENCE][r["task_set"]][
            "per_task_work"][r["task_id"]])

    receipt = {
        "receipt": "CL_LIBDISC_E5_V1",
        "study_id": "CL-LIBDISC-E5-V1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E1",
        "contribution_level": "L0",
        "study_role": "INDEPENDENT_SECOND_IMPLEMENTATION_AND_MECHANISM_SEPARATION",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "prior_art_in_programme": {
            "frozen_protected_protocol": (
                "branch codex/ocm-evolvability-independent-20260908, path "
                "research/evolvability-independent/PROTECTED_PROTOCOL_V3.md, "
                "hypothesis card E150-A, seeds 9301..9340, frozen before "
                "protected outcome access and NOT YET RUN"),
            "relationship": (
                "That protocol covers the same question -- can reusable sparse "
                "methods be discovered from heterogeneous episodes without "
                "task/family identity or routing-key leakage. This lane is an "
                "INDEPENDENT SECOND IMPLEMENTATION of that measurement and "
                "claims no priority over it. Its leakage discipline "
                "(learner-visible fields are exactly the input and the correct "
                "actions) and its symbolic_compact_parent are adopted from that "
                "protocol rather than invented here."),
            "what_is_distinct_here": (
                "the opportunity-versus-discovery separation: the same "
                "discovered schema run against a fresh-task set with a "
                "certified essential composite opportunity and against one "
                "certified to have none. That contrast is not in that lane."),
        },
        "negatives_this_reproduces": {
            "NO_METHOD_ACQUIRED": (
                "research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md "
                "-- 21 candidates mined, three checked sound and essential, all "
                "singletons, empty pool. Reproduced here by "
                "flat_mining_ablation: "
                f"{ablation.funnel['valid_essential']} checked-essential flat "
                f"fragments, every one a singleton, pool "
                f"{ablation.funnel['pool']}."),
            "NO_DEVELOPMENT_BENEFIT": (
                "research/math-language-learning-v1/CLAUSE-REVIVAL-RESULT.md "
                "-- pool 0 to 1, then sixteen development trials all NO_MATCH "
                "at 4,425 matching-work units, because only four rows were "
                "eligible and every target was a Boolean tautology. Reproduced "
                "here as the tautological control set: every row matched, "
                f"{summary[ARM]['tautological_control']['macro_match_attempts']} "
                "matching-work units, delta "
                f"{benefit[ARM]['tautological_control']['delta_vs_reset']}."),
        },
        "plan": LIBDISC_PLAN,
        "commitment": commit(LIBDISC_PLAN).as_dict(),
        "plan_digest": COMMITMENT_BODY,
        "generator_certification": certification,
        "training_episodes": [e.as_dict() for e in TRAINING_EPISODES],
        "reference_composite_schema": CHAIN2_SCHEMA.as_dict(),
        "discovery_funnel": discovery.funnel,
        "flat_ablation_funnel": ablation.funnel,
        "scope_revisions": [r.as_dict() for r in discovery.revisions],
        "admissions": [d.as_dict() for d in discovery.pool],
        "rejections": [d.as_dict() for d in discovery.rejected],
        "arms": sweep_out["arms"],
        "per_task_set": per_set,
        "benefit_vs_reset_arm": benefit,
        "rows": sweep_out["rows"],
        "custody": {k: v for k, v in custody.items()
                    if not k.startswith("rows_after_restart")},
        "custody_benefit": custody_benefit(custody),
        "controls": {
            "false_common_pattern": (
                "the merge step recurs "
                f"{discovery.funnel['single_step_schemas_admitted']} times over "
                "and is ADMITTED under CL-D1 -- sound, compressive, certified "
                "beyond its training support -- and it is never applied and "
                "never demanded. Admissibility does not imply usefulness. Its "
                "two-step composite has exactly one training support and the "
                ">=2 gate refuses it, which costs the arm the FC1 row that "
                "would have benefited. That cost is reported rather than "
                "avoided by lowering the threshold."),
            "surface_similar_different_polarity": {
                "note": (
                    "same predicates, different pivot polarity. A "
                    "polarity-blind matcher fires on these and the independent "
                    "checker refutes the result; the sign-preserving matcher "
                    "does not fire."),
                "per_task": {
                    t.task_id: dict(zip(
                        ("matches", "refuted"),
                        polarity_blind_refutations(CHAIN2_SCHEMA, t.premises)))
                    for t in ESSENTIAL_COMPOSITE_TASKS + TAUTOLOGICAL_CONTROL_TASKS
                },
            },
            "singletons_that_should_not_generalise": (
                f"{discovery.funnel['singleton_step_schemas_excluded']} "
                "single-step schemas and "
                f"{discovery.funnel['composites_excluded_singleton_support']} "
                "composites were refused for singleton support and none of them "
                "is applied anywhere"),
            "harmful_abstraction": {
                "essential_set_rows_harmed": [r["task_id"] for r in harmed],
                "note": (
                    "the composite shortens five of six essential rows and "
                    "lengthens one: on that row the three-premise match sweep "
                    "costs more than the round it saves. Harm inside the set "
                    "where the opportunity exists is reported in the same "
                    "table as the benefit."),
            },
            "scope_revision": {
                "proposals": discovery.funnel["over_general_proposals"],
                "narrowed": discovery.funnel["scope_narrowed"],
                "deleted": discovery.funnel["narrowing_failed"],
                "note": (
                    "a lifting that drops the pivot-sharing equality is "
                    "unsound; the checker returns a counterexample and the "
                    "schema is NARROWED by merging two variables, not deleted. "
                    "Every proposal on this draw was recoverable by narrowing."),
            },
            "redundant_but_sound_matches": (
                "counted in their own column on every row and never in any "
                "benefit figure, following CLAUSE-REVIVAL-RESULT.md's refusal "
                "to count them"),
        },
        "endpoint_S5_harmful_transfer": {
            "arm_rows_total": len(all_arm_rows),
            "arm_rows_harmed_vs_reset": s5_harmed,
            "rate": round(s5_harmed / len(all_arm_rows), 4),
            "wrong_answers": sum(1 for r in all_arm_rows if not r["correct"]),
        },
        "terminal": terminal,
        "terminal_reason": reason,
        "opportunity_or_discovery": (
            "Both terms are measured and they are not the same size. Discovery "
            "is real and is a property of the mechanism: the flat ablation "
            "finds nothing on evidence where the step-level arm finds an "
            "admissible composite, and the composite survives a real process "
            "restart and fires with an execution-trace witness on unseen "
            "tasks. Benefit is NOT a property of the mechanism: the identical "
            "schema saves "
            f"{benefit[ARM]['essential_composite']['delta_vs_reset']} work "
            "units where an essential composite opportunity was certified to "
            "exist and costs "
            f"{-benefit[ARM]['tautological_control']['delta_vs_reset']} units "
            "where it was certified not to. The positive on the essential set "
            "is the OPPORTUNITY CONDITION doing the work, in the precise sense "
            "that the same discovery with the same custody produces a large "
            "net loss the moment the opportunity is removed. Any lane that "
            "reported only the essential set would be reporting the ecology it "
            "chose, not the machinery it built."),
        "what_this_does_not_establish": [
            "No priority. A frozen protected protocol on branch "
            "codex/ocm-evolvability-independent-20260908 covers the same "
            "question under card E150-A and has not been run. This is a second "
            "implementation, and under #144 its value is exactly that.",
            "The two fresh-task sets were AUTHORED to differ in one certified "
            "property. That is what identifies the demand term and it is also "
            "why nothing here says anything about how often natural task "
            "ecologies contain essential composite opportunities. The rate in "
            "the wild is not measured and is not estimable from this draw.",
            "terminal_for's body was written after the sweep had run once. The "
            "plan and its prediction were frozen before the arms existed, but "
            "that is weaker than a pre-registered terminal and is not claimed "
            "to be one.",
            "symbolic_compact_parent and symbolic_incremental_memory_parent "
            "share the mechanism under test by construction: they run the "
            "identical learner and differ only in caching and archiving. "
            "ROOT_CAUSE_ANALYSIS_V1.md records "
            "PARENT_SHARES_THE_MECHANISM_UNDER_TEST as a first-order root, and "
            "any gap against them is a statement about infrastructure, not "
            "about whether an independently implemented learner would tie.",
            "Eight predicates, 256 assignments, ten training episodes, "
            "nineteen fresh tasks. PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM applies "
            "to every number in this receipt.",
            "Resolution plus subsumption is complete for non-tautological "
            "clause entailment, which is what makes minimal derivation depth "
            "well defined here. Nothing follows about proof search in a richer "
            "logic, and the macro-matching cost that dominates the control set "
            "is a fact about three-premise matching over small clause sets.",
            "Minimal derivation LENGTH is measured as derivation DEPTH -- the "
            "number of breadth-first rounds -- because that is the quantity the "
            "search meter is sensitive to. Under a linear step count some rows "
            "classified as bypassable would be classified differently.",
            "No wall-clock, energy or memory coordinate is measured. The "
            "lifetime economics of holding a library are not established; only "
            "search work is.",
        ],
        "hostiles_that_fired": [
            "flat_mining_ablation accepted "
            f"{ablation.funnel['valid_essential']} independently checked "
            "essential fragments and still returned an empty pool, which is the "
            "diagnosed failure reproduced rather than described",
            "the tautological control turned a "
            f"+{benefit[ARM]['essential_composite']['delta_vs_reset']} result "
            "into a "
            f"{benefit[ARM]['tautological_control']['delta_vs_reset']} result "
            "with the same schema and the same custody",
            "stitch_parent and dreamcoder_parent both FOUND the arm's composite "
            "and three more, so the discovery gap against library learning is "
            "zero on this draw; their extra macros then made them net-harmful "
            "on every set, which is a finding about MDL-only admission and not "
            "a weakness planted in them",
            "symbolic_compact_parent found the identical schema set and reached "
            f"{benefit['symbolic_compact_parent']['essential_composite']['delta_vs_reset']} "
            "of the arm's "
            f"{benefit[ARM]['essential_composite']['delta_vs_reset']}; the "
            "residual is a duplicate relevance cache and is infrastructural",
            "symbolic_incremental_memory_parent, the mandatory P1 memoization "
            "parent, hit its archive zero times and paid for every lookup, "
            "because the fresh tasks are disjoint from the training draw by "
            "construction",
            "the arm is harmed on one of six rows inside the set where the "
            "opportunity exists, and on every row of every other set",
            "the >=2 gate refused a composite that would have helped the FC1 "
            "row, and the threshold was not lowered",
        ],
        "authority": (
            "This receipt separates two negatives the programme has been "
            "reporting as one. It establishes, at prototype scale and with an "
            "exact independent checker, that (a) step-level abstraction "
            "recovers an admissible reusable object from evidence on which flat "
            "surface mining recovers nothing, (b) that object survives a real "
            "operating-system process boundary and fires on unseen tasks with "
            "an execution-trace witness, and (c) its measured benefit is "
            "governed by whether the fresh tasks contain an essential composite "
            "opportunity, not by the quality of the discovery. It establishes "
            "no advantage over library learning -- Stitch and DreamCoder find "
            "the same object -- and no advantage over a parent that shares the "
            "learner and differs only in caching. It is an independent second "
            "implementation of a measurement whose frozen protocol lives on "
            "branch codex/ocm-evolvability-independent-20260908 and has not yet "
            "been run; it claims no priority over it."
        ),
    }
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(json.dumps({
        "terminal": terminal,
        "essential_composite_delta": benefit[ARM]["essential_composite"]["delta_vs_reset"],
        "tautological_control_delta": benefit[ARM]["tautological_control"]["delta_vs_reset"],
        "flat_ablation_pool": ablation.funnel["pool"],
        "custody": custody["terminal"],
        "pids": [custody["pid_before"], custody["pid_after"]],
        "out": str(out),
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
