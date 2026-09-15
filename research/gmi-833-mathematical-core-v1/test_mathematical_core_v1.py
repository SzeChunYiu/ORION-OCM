from __future__ import annotations

from fractions import Fraction
from itertools import product
import unittest

from mathematical_core_v1 import (
    CANNOT_IDENTIFY,
    BehavioralSpecification,
    CapabilityContract,
    FiniteProcess,
    FiniteUncertainty,
    Morphology,
    aliasing_ceiling_grid,
    capability_bounds,
    capability_profile,
    capability_region,
    ceiling_monotone,
    compose_uncertainty,
    expected_binary_success,
    identified_decision,
    machine_species_equivalent,
    morphology_equivalent,
    stable_behavior_partition,
    validate_all,
)


class MathematicalCoreTests(unittest.TestCase):
    def setUp(self):
        self.transitions = {(s, a): s ^ a for s in (0, 1) for a in (0, 1)}

    def test_all_registered_claims(self):
        result = validate_all()
        self.assertEqual(result["axioms_satisfied"], 10)
        self.assertEqual(result["scientific_claim_ledgers"], 4)
        self.assertEqual(result["open_independent_review_gaps"], 1)
        self.assertEqual(result["closure_level"], "LOCALLY_CLOSED")
        self.assertTrue(result["model_satisfies_registered_axioms"])

    def test_axiom_partition_matches_all_small_continuation_profiles(self):
        states, actions = (0, 1), (0, 1)
        pairs = tuple(product(states, actions))
        words = [()]
        for length in range(1, len(states) + 1):
            words.extend(product(actions, repeat=length))
        for observations in product((0, 1), repeat=len(states)):
            observation = dict(zip(states, observations, strict=True))
            for successors in product(states, repeat=len(pairs)):
                transition = dict(zip(pairs, successors, strict=True))
                process = FiniteProcess(states, actions, observation, transition)
                quotient = {
                    state: block
                    for block, group in enumerate(stable_behavior_partition(process))
                    for state in group
                }

                def profile(state):
                    values = []
                    for word in words:
                        current = state
                        trace = [observation[current]]
                        for action in word:
                            current = transition[current, action]
                            trace.append(observation[current])
                        values.append(tuple(trace))
                    return tuple(values)

                self.assertEqual(quotient[0] == quotient[1], profile(0) == profile(1))

    def test_invalid_process_fails_closed(self):
        with self.assertRaises(ValueError):
            stable_behavior_partition(FiniteProcess((0, 1), (0,), {0: 0, 1: 1}, {(0, 0): 0}))

    def test_morphology_equivalence_ignores_names_not_structure(self):
        left_process = FiniteProcess((0, 1), (0, 1), {0: "z", 1: "o"}, self.transitions)
        right_transition = {("a", 0): "a", ("a", 1): "b", ("b", 0): "b", ("b", 1): "a"}
        right_process = FiniteProcess(("a", "b"), (0, 1), {"a": "z", "b": "o"}, right_transition)
        left = Morphology(
            left_process,
            {0: "CELL", 1: "CELL"},
            ((0, "probe", "z"), (1, "probe", "o")),
            (("experiment", (2, 3)),),
            ((0, 1, (1, 0)), (1, 0, (1, 0))),
        )
        right = Morphology(
            right_process,
            {"a": "CELL", "b": "CELL"},
            (("a", "probe", "z"), ("b", "probe", "o")),
            (("experiment", (2, 3)),),
            (("a", "b", (1, 0)), ("b", "a", (1, 0))),
        )
        self.assertTrue(morphology_equivalent(left, right))
        self.assertTrue(machine_species_equivalent(left, right))
        expensive = Morphology(
            right_process,
            {"a": "CELL", "b": "CELL"},
            right.intervention_response,
            (("experiment", (2, 4)),),
            right.development_edges,
        )
        self.assertFalse(morphology_equivalent(left, expensive))
        self.assertFalse(machine_species_equivalent(left, expensive))

    def test_intervention_and_development_are_not_silently_dropped(self):
        process = FiniteProcess((0, 1), (0, 1), {0: "z", 1: "o"}, self.transitions)
        base = Morphology(process, {0: "CELL", 1: "CELL"}, ((0, "probe", "z"),), (("e", (1,)),), ((0, 1, (1,)),))
        changed_intervention = Morphology(process, {0: "CELL", 1: "CELL"}, ((0, "probe", "o"),), (("e", (1,)),), ((0, 1, (1,)),))
        changed_development = Morphology(process, {0: "CELL", 1: "CELL"}, ((0, "probe", "z"),), (("e", (1,)),), ((1, 0, (1,)),))
        self.assertFalse(morphology_equivalent(base, changed_intervention))
        self.assertFalse(morphology_equivalent(base, changed_development))

    def test_capability_and_abstention(self):
        copy = BehavioralSpecification("COPY", (0, 1), lambda x, y: x == y)
        behaviors = ({0: 0, 1: 1}, {0: 0, 1: 0})
        self.assertEqual(capability_profile(behaviors[0], (copy,)), (("COPY", True),))
        self.assertEqual(capability_region(behaviors[0], (copy,)), frozenset({"COPY"}))
        self.assertEqual(capability_bounds(behaviors, (copy,)), {"COPY": (0, 1)})
        self.assertEqual(identified_decision({True, False}), CANNOT_IDENTIFY)
        self.assertTrue(ceiling_monotone((Fraction(1, 2),), (Fraction(1, 2), Fraction(1))))

    def test_union_bound_and_independence_are_distinct(self):
        a = FiniteUncertainty(frozenset({0, 1}), Fraction(9, 10))
        b = FiniteUncertainty(frozenset({0, 1}), Fraction(4, 5))
        self.assertEqual(compose_uncertainty(a, b).confidence, Fraction(7, 10))
        self.assertEqual(compose_uncertainty(a, b, independent=True).confidence, Fraction(18, 25))
        self.assertEqual(len(compose_uncertainty(a, b).worlds), 4)

    def test_aliasing_ceiling_and_revealed_positive_control(self):
        self.assertEqual(set(aliasing_ceiling_grid(100)), {Fraction(1, 2)})
        contract = CapabilityContract("LATENT", (0, 1), (Fraction(1, 2), Fraction(1, 2)), Fraction(3, 4))
        success = expected_binary_success(
            {"left": Fraction(0), "right": Fraction(1)},
            {0: "left", 1: "right"},
            {0: 0, 1: 1},
            contract,
        )
        self.assertEqual(success, 1)

    def test_uncertainty_and_confidence_fail_closed(self):
        with self.assertRaises(ValueError):
            FiniteUncertainty(frozenset())
        with self.assertRaises(ValueError):
            FiniteUncertainty(frozenset({1}), Fraction(2))


if __name__ == "__main__":
    unittest.main()
