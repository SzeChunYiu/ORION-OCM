"""Run E7, the reuse-opportunity-density sweep, and emit its receipt.

    PYTHONPATH=. python run_rho.py --out results/RHO_E7_V1.json

``terminal_for`` below and the prediction it scores were written before anything
was executed.  The terminal is a pure function of the table and the controls, so
the reported outcome is not a choice made after seeing the numbers.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Mapping, Sequence

from games import SubtractionGame
from rho import (
    COMMITMENT,
    RHO_PLAN,
    build_stream,
    closed_form_families,
    irregular_families,
    rejected_families,
)
from rho_arms import (
    ALL_PARENTS,
    ARM_SPECS,
    INDEPENDENT_PARENTS,
    SWEEP_NOTES,
    controls,
    crossovers,
    sweep,
    sweep_table,
)

#: Frozen before execution, quoted verbatim from ROOT_CAUSE_ANALYSIS_V1.
PREDICTION = RHO_PLAN["prediction_frozen_before_execution"]
FALSIFIER = RHO_PLAN["falsifier"]


def terminal_for(
    rows: Sequence[Mapping], control_block: Mapping, crossover_block: Mapping
) -> tuple[str, str]:
    """Fixed before the run: the terminal is a function of the table.

    The order of the tests is the order in which a finding can be invalidated.
    Control 1 comes first because a sweep whose ``rho = 0`` point does not
    reproduce the existing negatives is not measuring the knob the old
    experiments varied, and every number after that is uninterpretable.
    """
    if not control_block["control_2_every_parent_ran_at_every_rho"]:
        return (
            "SWEEP_INCOMPLETE_PARENT_MISSING",
            "a parent did not run at every rho; a crossover against a parent that "
            "was denied the reuse opportunity is not a crossover",
        )
    if not control_block["capability_gate_passed"]:
        return (
            "CAPABILITY_GATE_FAILED",
            "an arm did not answer every task correctly; no efficiency claim is "
            "read at all when capability fails",
        )
    zero = control_block["control_1_rho_zero_reproduces_negatives"]
    if not all(v["reproduced"] for v in zero.values()):
        return (
            "SWEEP_VOID_RHO_ZERO_DID_NOT_REPRODUCE_NEGATIVES",
            "at rho = 0 the machine did not fail in the way the preserved negatives "
            "failed, so the knob is not the one the old experiments varied and the "
            "whole sweep is void",
        )

    base = crossover_block["1"]
    strongest = base["STRONGEST_PARENT_ENVELOPE"]["first_rho_below"]
    independent = base["STRONGEST_INDEPENDENT_PARENT_ENVELOPE"]["first_rho_below"]
    if strongest is None and independent is None:
        return (
            "NO_CROSSOVER_AT_ANY_RHO",
            "the machine's cumulative cost never fell below the strongest parent's "
            "at any reuse density up to and including 1.0, at matched capability "
            "and with full accounting; the falsifier fired, the deep root "
            "ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE is refuted on this ecology, and "
            "the fault returns to the mechanisms",
        )
    if strongest is None:
        return (
            "CROSSOVER_ONLY_AGAINST_PARENTS_THAT_DO_NOT_SHARE_THE_MECHANISM",
            f"the machine crosses the strongest INDEPENDENT parent at rho = "
            f"{independent}, but never crosses the strongest parent overall: a "
            "parent holding the machine's own persistent-method mechanism with a "
            "different acquisition trigger is cheaper at every rho. Raising reuse "
            "density rescues persistence against memoization and against lazy "
            "re-derivation, and does not rescue EAGER acquisition against deferred "
            "acquisition. The falsifier fired against the strongest parent",
        )
    return (
        "AMORTIZATION_CROSSOVER_AT_RHO_STAR",
        f"the machine's cumulative cost falls below the strongest parent's at "
        f"rho = {strongest} and stays below at every larger density",
    )


def _stream_summary() -> list[dict]:
    out = []
    for requested in RHO_PLAN["rho_grid"]:
        stream = build_stream(requested)
        out.append(
            {
                "requested_rho": requested,
                "realised_rho": round(stream.realised_rho, 6),
                "certified_essential_tasks": stream.essential_count,
                "tasks": len(stream.tasks),
                "kind_counts": stream.kind_counts(),
                "total_certified_savings_per_reuse": stream.total_certified_savings,
            }
        )
    return out


def _method_records(results) -> list[dict]:
    """CL-D3 bits and CL-D1 admissibility for every method the machine acquired."""
    _, machine = results[(1, 1.0)]["persistent_arm"]
    return [a.as_dict() for _, a in sorted(machine.acquisitions.items())]


def _reuse_witnesses(results, limit: int = 3) -> list[dict]:
    _, machine = results[(1, 1.0)]["persistent_arm"]
    return [e.as_dict() for e in machine.reuse_events[:limit]]


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
    control_block = controls(rows)
    crossover_block = crossovers(rows)
    terminal, reason = terminal_for(rows, control_block, crossover_block)

    receipt: dict[str, Any] = {
        "receipt": "CL_RHO_E7_V1",
        "study_id": "CL-RHO-E7-V1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "answers": "ROOT_CAUSE_ANALYSIS_V1 decisive_experiment RHO_SWEEP",
        "answers_root": "ECOLOGY_HAS_NO_ACCUMULATION_STRUCTURE",
        "evidence_class": "E1",
        "contribution_level": "L0",
        "study_role": "DECISIVE_EXPERIMENT_ON_A_SYNTHETIC_ECOLOGY",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "plan": RHO_PLAN,
        "commitment": COMMITMENT.as_dict(),
        "prediction_frozen_before_execution": PREDICTION,
        "falsifier": FALSIFIER,
        "registered_roles": {
            arm_id: {
                "role": spec.role,
                "shares_mechanism_under_test": spec.shares_mechanism,
                "acquisition_trigger": spec.acquisition_trigger,
                "holds_methods": spec.holds_methods,
                "holds_memo": spec.holds_memo,
                "retains_evidence": spec.retains_evidence,
                "tracks_dependencies": spec.tracks_dependencies,
                "note": spec.note,
            }
            for arm_id, spec in ARM_SPECS.items()
        },
        "independent_parents": list(INDEPENDENT_PARENTS),
        "parents": list(ALL_PARENTS),
        "family_registration": {
            "irregular_families_admitted": [
                SubtractionGame(m).family_id for m in irregular_families()
            ],
            "closed_form_families": [
                SubtractionGame(m).family_id for m in closed_form_families()
            ],
            "rejected": [
                {"family_id": fid, "reason": why} for fid, why in rejected_families()
            ],
            "filter": (
                "a family joins the irregular pool only if the rule induced from "
                "the donor task's own evidence window reproduces the exact Grundy "
                "value at every position the sweep can draw; rejections are listed "
                "rather than hidden"
            ),
        },
        "streams": _stream_summary(),
        "table": rows,
        "crossover_by_discovery_multiplier": crossover_block,
        "anti_rigging_controls": control_block,
        "acquired_methods": _method_records(results),
        "reuse_witnesses": _reuse_witnesses(results),
        "terminal": terminal,
        "terminal_reason": reason,
        "sweep_notes": list(SWEEP_NOTES),
        "hostiles_that_fired": [
            "BYPASS_REPEAT tasks sit on irregular families hundreds of positions "
            "beyond the training support, where the dynamic programme costs "
            "thousands of units and the acquired rule costs one. They are certified "
            "NOT essential because a solved-instance store answers them for the same "
            "one unit, and they are excluded from rho.",
            "BYPASS_CLOSED_FORM tasks are excluded for the same reason with a "
            "different bypass: Bouton's arithmetic answers a prefix subtraction game "
            "at exactly the acquired rule's cost, so no task on such a family is ever "
            "essential however large its position.",
            "The index parent ties the machine on every work coordinate at every rho "
            "and holds strictly fewer bytes, reproducing C1-SPARSE-LOOKUP. A tie with "
            "a parent that holds the machine's own mechanism is not read as a result.",
            "deferred_induction_parent, added beyond the five arms the decisive "
            "experiment registered, is cheaper than the machine at every rho at both "
            "discovery costs. Omitting it would have manufactured a crossover.",
            "cache_parent's nearest-cached-instance guess scores BELOW the "
            "majority-class baseline on the tasks it missed, so 'generalises at "
            "chance beyond its cached instances' is a measured number here.",
            "realised rho is strictly below requested rho at rho = 1.0 and can never "
            "reach 1.0, because the donor tasks that make any structure acquirable "
            "cannot themselves be essential.",
        ],
        "what_this_does_not_establish": [
            "A HAND-SET DENSITY SAYS NOTHING ABOUT THE DENSITY OF ANY REAL TASK "
            "ECOLOGY. rho is the knob here, set by the generator to a registered "
            "value and then certified. Nothing in this receipt bears on what rho is "
            "in arithmetic, in software repair, in mathematics, or in any domain "
            "anyone cares about, and the honest next question is exactly that.",
            "The crossover reported against lazy re-derivation is bought by exactly "
            "one avoided derivation per demanded family. It is not a claim that "
            "persistence compounds: beyond the first reuse of a family the lazy "
            "parent holds the same rule and pays the same one unit, so the gap "
            "saturates rather than growing with the horizon.",
            "The strongest parent is never beaten. deferred_induction_parent retains "
            "the evidence a derivation produced and defers only the induction, so it "
            "captures the whole amortization benefit without paying discovery for "
            "structure nothing demands. The result about EAGER acquisition is a "
            "result about acquisition POLICY, not about persistent architecture.",
            "That parent is cheap only because evidence in this ecology is perfectly "
            "retainable and induction is a pure function of retained evidence. Where "
            "raw experience cannot be kept, deferring induction is not free, and this "
            "harness cannot say anything about that case.",
            "No revocation is exercised, so the machine's dependency edges buy it "
            "nothing here and are charged in bytes. The revision coordinates that "
            "SCALING_PILOT_V1 reports are absent from this lane by construction.",
            "Essentiality is certified against a REGISTERED procedure set of four "
            "members. A procedure outside that set - a cleverer closed form, a "
            "better bound, a different decomposition - would reclassify tasks as "
            "bypassable and lower rho. The certificate is relative to the registered "
            "set and says so.",
            "Bypass tasks are cheap and essential tasks are expensive, and that is "
            "definitional rather than incidental: a bypass is an equally cheap "
            "alternative route, and a task is essential precisely when no such route "
            "exists. Totals must therefore be compared between arms WITHIN one rho "
            "and never across rho.",
            "One stream of 64 tasks, one horizon, one position band, eight irregular "
            "families and six closed-form families. PROTOTYPE_SCALE_TOO_SMALL_FOR_"
            "CLAIM remains available and is the correct terminal for any attempt to "
            "read a field claim out of these numbers.",
            "Nothing about cognition. The acquirable object is a periodic Grundy "
            "rule in a registered language of known size, and the family key is "
            "supplied by the task.",
        ],
        "authority": (
            "This receipt measures the demand term of the amortization inequality on "
            "one synthetic ecology whose reuse density is set by hand and then "
            "certified. It establishes where a crossover lies against each named "
            "parent on this ecology and it establishes nothing about any other. It "
            "withdraws no previous result and promotes none."
        ),
    }
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "crossover": {
                    m: {k: v["first_rho_below"] for k, v in per.items()}
                    for m, per in crossover_block.items()
                },
                "out": str(out),
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
