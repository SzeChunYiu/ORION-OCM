#!/usr/bin/env python3
"""Finite semantic checks for open-world and asymmetric warrant theorems.

The NP/coNP classifications are mathematical proofs in the paired theory file;
this finite program checks semantics and planted counterexamples.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from typing import Sequence

Literal = int
Clause = tuple[Literal, ...]
CNF = tuple[Clause, ...]
Support = frozenset[int]
SupportFamily = tuple[Support, ...]


def eval_literal(literal: Literal, assignment: Sequence[int]) -> bool:
    if literal == 0:
        raise ValueError("literal 0 is invalid")
    index = abs(literal) - 1
    if not 0 <= index < len(assignment):
        raise IndexError("literal variable out of range")
    value = bool(assignment[index])
    return value if literal > 0 else not value


def eval_cnf(formula: CNF, assignment: Sequence[int]) -> bool:
    return all(any(eval_literal(lit, assignment) for lit in clause) for clause in formula)


def satisfying_assignments(formula: CNF, variable_count: int):
    return tuple(
        assignment
        for assignment in itertools.product((0, 1), repeat=variable_count)
        if eval_cnf(formula, assignment)
    )


def verify_retain_certificate(
    formula: CNF, variable_count: int, witness: Sequence[int]
) -> bool:
    return len(witness) == variable_count and eval_cnf(formula, witness)


def retain(formula: CNF, variable_count: int) -> bool:
    return bool(satisfying_assignments(formula, variable_count))


def retract(formula: CNF, variable_count: int) -> bool:
    return not retain(formula, variable_count)


def explicit_surviving_supports(
    supports: SupportFamily, revoked: frozenset[int]
):
    return tuple(support for support in supports if support.isdisjoint(revoked))


def explicit_warrant_decision(
    supports: SupportFamily, revoked: frozenset[int]
) -> str:
    return "RETAIN" if explicit_surviving_supports(supports, revoked) else "RETRACT"


def verify_explicit_retain(
    supports: SupportFamily, revoked: frozenset[int], support_index: int
) -> bool:
    return (
        0 <= support_index < len(supports)
        and supports[support_index].isdisjoint(revoked)
    )


def verify_explicit_retract(
    supports: SupportFamily,
    revoked: frozenset[int],
    hitting_atoms: Sequence[int],
    *,
    complete_manifest: bool,
) -> bool:
    if not complete_manifest or len(hitting_atoms) != len(supports):
        return False
    return all(
        atom in revoked and atom in support
        for atom, support in zip(hitting_atoms, supports)
    )


@dataclass(frozen=True)
class OpenWorldObservation:
    observed_positive_supports: SupportFamily
    complete_manifest: bool = False


def open_world_ambiguous_pair(
    observation: OpenWorldObservation,
    revoked: frozenset[int],
    unseen_surviving_support: Support,
):
    if observation.complete_manifest:
        raise ValueError("a complete manifest closes the open world")
    if any(support.isdisjoint(revoked) for support in observation.observed_positive_supports):
        raise ValueError("observed supports already settle RETAIN")
    if not unseen_surviving_support.isdisjoint(revoked):
        raise ValueError("planted unseen support must survive")
    if unseen_surviving_support in observation.observed_positive_supports:
        raise ValueError("planted support must be unobserved")

    world_retract = observation.observed_positive_supports
    world_retain = observation.observed_positive_supports + (unseen_surviving_support,)
    return {
        "observation_identical": True,
        "world_retract_supports": [sorted(x) for x in world_retract],
        "world_retain_supports": [sorted(x) for x in world_retain],
        "revoked": sorted(revoked),
        "correct_action_world_retract": explicit_warrant_decision(
            world_retract, revoked
        ),
        "correct_action_world_retain": explicit_warrant_decision(
            world_retain, revoked
        ),
        "deterministic_exact_action_exists": False,
        "randomized_no_abstention_minimax_error_lower_bound": 0.5,
        "zero_error_requires": [
            "completeness/closure certificate",
            "future support-discovery query",
            "explicit abstention",
        ],
    }


def run_exact_calibration():
    sat_formula: CNF = ((1, 2), (-1, 2), (1, -2))
    unsat_formula: CNF = ((1,), (-1,))
    sat_witnesses = satisfying_assignments(sat_formula, 2)
    unsat_witnesses = satisfying_assignments(unsat_formula, 1)
    if not sat_witnesses or unsat_witnesses:
        raise AssertionError("implicit support witness semantics drift")
    if not any(
        verify_retain_certificate(sat_formula, 2, witness)
        for witness in sat_witnesses
    ):
        raise AssertionError("positive warrant certificate did not verify")
    if verify_retain_certificate(unsat_formula, 1, (0,)):
        raise AssertionError("false positive warrant certificate verified")

    supports: SupportFamily = (
        frozenset({0, 1}),
        frozenset({1, 2}),
        frozenset({3}),
    )
    revoked = frozenset({1, 3})
    if explicit_warrant_decision(supports, revoked) != "RETRACT":
        raise AssertionError("explicit support decision drift")
    if not verify_explicit_retract(
        supports, revoked, (1, 1, 3), complete_manifest=True
    ):
        raise AssertionError("complete explicit retract certificate failed")
    if verify_explicit_retract(
        supports, revoked, (1, 1, 3), complete_manifest=False
    ):
        raise AssertionError("retract verified without closure manifest")

    supports_with_survivor = supports + (frozenset({4}),)
    if explicit_warrant_decision(supports_with_survivor, revoked) != "RETAIN":
        raise AssertionError("surviving explicit support was ignored")
    if not verify_explicit_retain(
        supports_with_survivor, revoked, len(supports_with_survivor) - 1
    ):
        raise AssertionError("surviving-support witness did not verify")

    ambiguous = open_world_ambiguous_pair(
        OpenWorldObservation(
            (frozenset({0, 1}), frozenset({1, 2}))
        ),
        revoked=frozenset({1}),
        unseen_surviving_support=frozenset({3}),
    )
    if ambiguous["correct_action_world_retract"] != "RETRACT":
        raise AssertionError("open-world negative world drift")
    if ambiguous["correct_action_world_retain"] != "RETAIN":
        raise AssertionError("open-world positive world drift")

    atoms = tuple(range(4))
    candidate_supports = tuple(
        frozenset(s)
        for size in range(1, 3)
        for s in itertools.combinations(atoms, size)
    )
    family_checks = retain_cases = retract_cases = 0
    for family_size in (1, 2, 3):
        for support_indices in itertools.combinations(
            range(len(candidate_supports)), family_size
        ):
            family = tuple(candidate_supports[i] for i in support_indices)
            for revoked_bits in itertools.product((0, 1), repeat=len(atoms)):
                revoked_set = frozenset(
                    atom for atom, bit in zip(atoms, revoked_bits) if bit
                )
                decision = explicit_warrant_decision(family, revoked_set)
                family_checks += 1
                if decision == "RETAIN":
                    retain_cases += 1
                    survivor_index = next(
                        i
                        for i, support in enumerate(family)
                        if support.isdisjoint(revoked_set)
                    )
                    if not verify_explicit_retain(
                        family, revoked_set, survivor_index
                    ):
                        raise AssertionError("finite retain certificate failed")
                else:
                    retract_cases += 1
                    hitting_atoms = tuple(
                        next(iter(support & revoked_set)) for support in family
                    )
                    if not verify_explicit_retract(
                        family,
                        revoked_set,
                        hitting_atoms,
                        complete_manifest=True,
                    ):
                        raise AssertionError("finite retract certificate failed")
    if retain_cases == 0 or retract_cases == 0:
        raise AssertionError("suite lacks retain/retract coverage")

    return {
        "schema": "orion.ocm.warrant-asymmetry.exact-results.v1",
        "terminal": "PASS_FINITE_SEMANTIC_CALIBRATION_ONLY",
        "implicit_support": {
            "satisfiable_formula": sat_formula,
            "satisfying_assignment_count": len(sat_witnesses),
            "unsatisfiable_formula": unsat_formula,
            "unsatisfying_assignment_count": len(unsat_witnesses),
            "retain_has_assignment_witness": True,
            "retract_is_absence_of_any_assignment": True,
        },
        "open_world_impossibility": ambiguous,
        "explicit_closed_world_protocol": {
            "family_revoked": [sorted(x) for x in supports],
            "revoked": sorted(revoked),
            "decision": explicit_warrant_decision(supports, revoked),
            "retract_certificate_verified_with_manifest": True,
            "retract_certificate_rejected_without_manifest": True,
            "family_with_survivor": [sorted(x) for x in supports_with_survivor],
            "retain_certificate_verified": True,
        },
        "exhaustive_finite_checks": {
            "evidence_atoms": len(atoms),
            "candidate_supports_size_one_or_two": len(candidate_supports),
            "support_families_and_revocations_checked": family_checks,
            "retain_cases": retain_cases,
            "retract_cases": retract_cases,
        },
        "authority": {
            "finite_semantics": True,
            "np_conp_proof_in_paired_artifact": True,
            "novelty": False,
            "architecture_separation": False,
            "publication_readiness": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = run_exact_calibration()
    except (AssertionError, ValueError, IndexError) as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        counts = result["exhaustive_finite_checks"]
        print(
            "PASS finite warrant semantics: "
            f"{counts['support_families_and_revocations_checked']} "
            "explicit-family/revocation cases checked."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
