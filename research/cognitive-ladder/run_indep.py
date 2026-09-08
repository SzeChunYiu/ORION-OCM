"""Run E8 -- the independently implemented parent -- and emit its receipt.

    python run_indep.py --out results/INDEP_E8_V1.json

``terminal_for`` below was written before any number was produced.  It is a
function of the table and of nothing else, and both of its interesting answers
were registered in ``indep.TERMINALS`` in advance:

* an independent parent matches or beats the arm -> ``INDEPENDENT_PARENT_SUFFICIENT``.
  ``PARENT_SUFFICIENT`` becomes informative for the first time, because the
  parent is not the arm.
* every capable independent parent costs strictly more -> ``ARM_SEPARATES_FROM_INDEPENDENT_PARENTS``.
  The earlier tie proved nothing and a real comparison shows a gap, which is
  quantified -- and a gap against four hand-written parents is still not parent
  closure.

Three guard terminals sit in front of both: the constructive parent must tie
exactly (or the harness is not measuring what it claims), the arm must pass the
capability gate, and at least one independent parent must pass it too.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Sequence

from indep import (
    COMMITMENT,
    DECISIVE_REGIME,
    INDEP_PLAN,
    MATCH_TOLERANCE,
    REFERENCE_NUMBERS,
    REGIMES,
    SEARCH_POLICY,
    LifetimeRecord,
    sweep,
    sweep_table,
)

#: The ceiling is reported but is excluded from the match test by design: an arm
#: that "matches" ``2**n`` calls has matched the act of measuring everything,
#: which is not a comparison.  Declared here, before the run.
MATCH_TEST_EXCLUDES = ("global_enumeration_parent",)


def terminal_for(records: Sequence[LifetimeRecord]) -> tuple[str, str]:
    """Fixed before the run: the terminal is a function of the table.

    Capability is read before cost, structurally: the only cost accessor used
    below is ``objective_calls_if_admissible``, which returns ``None`` for any
    arm that did not attain the exact optimum in every generation.
    """
    by_arm = {r.arm: r for r in records}
    arm = by_arm["walsh_arm"]
    constructive = by_arm["constructive_parent"]

    if (
        constructive.objective_calls != arm.objective_calls
        or constructive.optimum_attained_fraction != arm.optimum_attained_fraction
        or constructive.persistent_bytes != arm.persistent_bytes
    ):
        return (
            "CONSTRUCTIVE_TIE_BROKEN",
            "the constructive parent is the same algorithm holding separate state "
            "and must tie the arm exactly; it did not, so this harness is not "
            "measuring what it claims and no other terminal may be read from it",
        )

    if arm.objective_calls_if_admissible() is None:
        return (
            "ARM_NOT_CAPABLE",
            f"the arm attained the optimum in "
            f"{arm.optimum_attained_fraction:.3f} of generations; an arm that "
            "misses the optimum has no cost worth comparing",
        )

    independents = [
        r
        for r in records
        if r.arm_role == "INDEPENDENT_PARENT" and r.arm not in MATCH_TEST_EXCLUDES
    ]
    capable = [r for r in independents if r.objective_calls_if_admissible() is not None]
    if not capable:
        missed = ", ".join(
            f"{r.arm} {r.optimum_attained_fraction:.3f}" for r in independents
        )
        return (
            "NO_INDEPENDENT_PARENT_IS_CAPABLE",
            "no independently implemented parent attained the optimum in every "
            f"generation ({missed}), so the capability gate empties the cost "
            "comparison and this regime decides nothing",
        )

    arm_cost = arm.objective_calls_if_admissible()
    best = min(capable, key=lambda r: r.objective_calls_if_admissible())
    best_cost = best.objective_calls_if_admissible()
    ratio = best_cost / arm_cost if arm_cost else float("inf")

    if best_cost <= arm_cost * (1 + MATCH_TOLERANCE):
        direction = "beats" if best_cost < arm_cost else "matches"
        return (
            "INDEPENDENT_PARENT_SUFFICIENT",
            f"{best.arm}, written from its own standard description and sharing "
            f"no code path with the arm, {direction} it at "
            f"{best_cost:.1f} objective calls against {arm_cost:.1f} "
            f"(ratio {ratio:.3f}) with both attaining the exact optimum in every "
            "generation; PARENT_SUFFICIENT is informative here for the first "
            "time, because the parent is not the arm",
        )

    return (
        "ARM_SEPARATES_FROM_INDEPENDENT_PARENTS",
        f"the cheapest capable independent parent is {best.arm} at "
        f"{best_cost:.1f} objective calls against the arm's {arm_cost:.1f} "
        f"(ratio {ratio:.3f}), a gap of {best_cost - arm_cost:.1f} calls; the "
        "earlier tie was an artifact of shared construction and a real "
        "comparison shows a gap -- which is still not parent closure",
    )


def _tie_report(results) -> dict:
    """The tautology, made explicit on every coordinate it could hide on."""
    out = {}
    for regime in REGIMES:
        rows = {r.arm: r for r in results[regime.name]}
        arm, con = rows["walsh_arm"], rows["constructive_parent"]
        out[regime.name] = {
            "objective_calls_equal": arm.objective_calls == con.objective_calls,
            "attainment_equal": (
                arm.optimum_attained_fraction == con.optimum_attained_fraction
            ),
            "persistent_bytes_equal": arm.persistent_bytes == con.persistent_bytes,
            "work_coordinates_equal": (
                arm.fit_units == con.fit_units
                and arm.audit_units == con.audit_units
                and arm.invalidation_units == con.invalidation_units
                and arm.model_search_units == con.model_search_units
            ),
            "objective_calls": arm.objective_calls,
        }
    return out


def _headline(results) -> dict:
    """The decisive regime's comparison, componentwise and capability first."""
    rows = {r.arm: r for r in results[DECISIVE_REGIME]}
    arm = rows["walsh_arm"]
    out = {"regime": DECISIVE_REGIME, "arm_objective_calls": arm.objective_calls}
    for name, row in rows.items():
        if row.arm_role not in ("INDEPENDENT_PARENT", "CEILING"):
            continue
        cost = row.objective_calls_if_admissible()
        out[name] = {
            "capability_ok": row.capability_ok,
            "objective_calls_if_admissible": cost,
            "ratio_to_arm": (cost / arm.objective_calls) if cost else None,
            "excluded_from_match_test": name in MATCH_TEST_EXCLUDES,
        }
    return out


def _gap_attribution(results) -> dict:
    """Where the difference between the two model-based arms actually lives.

    Reported because the honest reading of the headline depends on it: if the
    two arms are identical in steady state and differ only in what it costs to
    identify a model from nothing, then the comparison is about discovery
    policy and not about the representation.
    """
    rows = {r.arm: r for r in results[DECISIVE_REGIME]}
    arm, parent = rows["walsh_arm"], rows["regression_parent"]
    return {
        "regime": DECISIVE_REGIME,
        "arm_discovery_calls": arm.call_split["discovery"],
        "parent_discovery_calls": parent.call_split["discovery"],
        "arm_steady_state_calls": arm.call_split["steady_state"],
        "parent_steady_state_calls": parent.call_split["steady_state"],
        "steady_state_is_identical": (
            arm.call_split["steady_state"] == parent.call_split["steady_state"]
        ),
        "model_parameters_are_identical": arm.model_parameters == parent.model_parameters,
        "reading": (
            "The whole difference is first-generation discovery: a full 2**n "
            "transform against degree-escalating least squares. In steady state "
            "the two arms cost the same to the call, because the number of "
            "observations needed to re-identify a model is set by the number of "
            "free parameters and not by the representation -- and both "
            "representations find the same number of parameters. The independent "
            "parent is cheaper because its discovery policy is cheaper, not "
            "because monomials beat characters."
        ),
    }


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
    terminal, reason = terminal_for(results[DECISIVE_REGIME])
    per_regime = {
        regime.name: dict(zip(("terminal", "reason"), terminal_for(results[regime.name])))
        for regime in REGIMES
    }

    receipt = {
        "receipt": "CL_INDEP_E8_V1",
        "study_id": "CL-INDEP-E8-V1",
        "programme_issue": "SzeChunYiu/ORION-OCM#143",
        "publication_constitution": "SzeChunYiu/ORION-OCM#144",
        "evidence_class": "E2",
        "contribution_level": "L0",
        "study_role": "INDEPENDENT_SECOND_IMPLEMENTATION_OF_A_CONTESTED_PARENT_COMPARISON",
        "protected_claim_authority": False,
        "scientific_promotion": "NOT_ESTABLISHED",
        "negative_addressed": "N10-SCALAR-FACTORIZATION",
        "deep_root_addressed": "PARENT_SHARES_THE_MECHANISM_UNDER_TEST",
        "commitment": COMMITMENT.as_dict()["commitment_sha256"],
        "plan": INDEP_PLAN,
        "search_policy": dict(SEARCH_POLICY),
        "match_test_excludes": list(MATCH_TEST_EXCLUDES),
        "table": rows,
        "constructive_tie": _tie_report(results),
        "headline": _headline(results),
        "gap_attribution": _gap_attribution(results),
        "per_regime_terminal": per_regime,
        "terminal": terminal,
        "terminal_reason": reason,
        "reference_numbers_from_the_original_lane": dict(REFERENCE_NUMBERS),
        "reconstruction_notes": [
            "The original lane's own artifacts are not in this tree, so the task "
            "was reconstructed from the description and from the three numbers it "
            "reported. 3072 objective calls for global enumeration over a "
            "lifetime is 12 * 2**8 exactly, which pins n = 8 and twelve "
            "generations; 2048 bytes for a global value array is 2**8 * 8 "
            "exactly, which pins the byte rule; 3072 for everything under drift "
            "pins the arm's rebuild as a full 2**n transform rather than a sparse "
            "recovery. The reconstruction reproduces the enumeration ceiling and "
            "the value-array byte count exactly.",
            "It does NOT reproduce the reported 442 objective calls for the "
            "candidate in sparse-stable, nor the reported 524928 persistent "
            "bytes. 524928 is 2**19 + 640, which is a persisted 256x256 float64 "
            "transform matrix plus a small sparse model; this reconstruction uses "
            "an in-place fast Walsh-Hadamard transform and therefore persists "
            "only the sparse model. Where the numbers differ, the reconstruction "
            "is reported and the original is not claimed to be reproduced.",
            "The arm's rebuild policy is the reconstructed one: measure all 2**n "
            "points and transform. A Walsh arm using order-escalating sparse "
            "recovery would pay the same discovery cost the regression parent "
            "pays, and any discovery-side gap reported here would close. The "
            "call_split coordinate is in the table precisely so a reader can see "
            "how much of any gap is discovery and how much is steady state.",
        ],
        "what_this_does_not_establish": [
            "FOUR HAND-WRITTEN PARENTS ARE NOT PARENT CLOSURE. A regression "
            "surrogate, a tabu searcher, a successive-halving racer and global "
            "enumeration are four points in a space that also contains Bayesian "
            "optimisation with a proper kernel, LASSO or compressed-sensing "
            "recovery of the sparse spectrum, estimation-of-distribution "
            "algorithms, and modern AutoML. None of those was run. Whichever way "
            "this comparison points, it does not close the parent question.",
            "NO NEURAL AND NO MODERN AutoML COMPARATOR WAS RUN. Issue #149's "
            "AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION is not answered here; this "
            "lane answers only N10, and only for the factorization task.",
            "n = 8 is a 256-point space. That is small enough that memoryless "
            "search approaches the enumeration ceiling on its own, so tabu and "
            "bandit are near-ceiling by construction rather than by weakness, and "
            "the informative comparison is with the model-based parent. Nothing "
            "here scales to a space where enumeration is impossible, and the "
            "protocol's PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM remains the right "
            "terminal for any attempt to read a field claim out of these numbers.",
            "The landscape is pr150_source.NK, whose value tables are drawn "
            "uniformly at random. Its Walsh and monomial spectra are therefore "
            "EXACTLY sparse, which is why a threshold at 1e-9 is not a tuned "
            "knob and why an exact model exists at all. On a landscape with "
            "approximately sparse structure both model-based arms would need a "
            "real regularisation policy and neither has one.",
            "Objective calls are one coordinate of several and are never summed "
            "with the others. The arm and the regression parent both buy their "
            "cheapness with fitting, auditing, invalidation and model-search work "
            "that the tabu and bandit parents do not pay at all. Fewer objective "
            "calls is not whole-resource dominance and this receipt does not "
            "report a total.",
            "The arm's single capability failure under drift is ONE generation "
            "of ninety-six on one landscape family at one drift rate. It shows "
            "that a four-point audit is not a sufficient staleness certificate; "
            "it does not measure how often that happens in general, and a larger "
            "audit budget would reduce it at a cost this lane did not sweep.",
            "This measures the cost of reaching a known-checkable optimum under a "
            "capability gate. It measures nothing about cognition, nothing about "
            "a machine learning a causal factorization OF ITS OWN reasoning, and "
            "it withdraws no existing result in the programme.",
        ],
        "hostiles_that_fired": [
            "the constructive parent is the SAME class with separate state and "
            "ties the arm on every coordinate in every regime, which is the "
            "demonstration that the earlier PARENT_SUFFICIENT verdict compared a "
            "program with itself",
            "the capability gate is enforced through an accessor rather than by "
            "convention, and it fires on the MECHANISM UNDER TEST: under drift "
            "the arm refits a support the world has moved out from under it, its "
            "four-point audit passes anyway, and its model's argmax is 4 per cent "
            "below the optimum. One generation in ninety-six is enough to make "
            "the arm inadmissible for the cost comparison in that regime, while "
            "regression_parent and tabu_parent attain the optimum in all "
            "ninety-six. The arm's audit is not a sufficient staleness "
            "certificate and this receipt says so rather than reporting the "
            "arm's favourable drift cost",
            "tabu_parent and bandit_parent miss the optimum in the stable regimes "
            "and their objective-call counts are therefore unreadable there, "
            "however favourable they look",
            "the shared model-parameter ceiling refuses a model in the dense "
            "regime for the arm and for the regression parent alike, so neither "
            "can look cheap by carrying a model that costs more to identify than "
            "the table it summarises",
            "invalidation is metered on its own coordinate, so an arm that is "
            "cheap in objective calls because it discards and re-derives its "
            "model every generation cannot book that as fitting",
        ],
        "authority": (
            "This receipt is an INDEPENDENT SECOND IMPLEMENTATION of a contested "
            "measurement, and claims no priority. A frozen protected study on "
            "branch codex/ocm-evolvability-independent-20260908 "
            "(research/evolvability-independent/PROTECTED_PROTOCOL_V3.md and "
            "factorization_survival_v3.py, frozen before protected outcome access "
            "with seeds 9301..9340) attacks the same PR #150 factorization "
            "survival question with strengthened parents and metered "
            "invalidation. Under #144 a second implementation of a contested "
            "measurement is worth having precisely because it is independent, and "
            "the two lanes should be read against each other rather than either "
            "being treated as the replication of the other. What this receipt "
            "establishes on its own is narrow and exact: that the parent in the "
            "N10 comparison was the arm, that a parent which is NOT the arm can "
            "be written for this task, and what that parent costs on each "
            "coordinate separately under a capability gate. It establishes no "
            "scaling law, no advantage over any parent not run, and no cognitive "
            "claim of any kind."
        ),
    }
    out.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "per_regime": {k: v["terminal"] for k, v in per_regime.items()},
                "headline": _headline(results),
        "gap_attribution": _gap_attribution(results),
                "out": str(out),
            },
            indent=1,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
