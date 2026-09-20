"""Exact distribution-free decision checks and hostile assumption boundaries."""
import copy
import unittest
from fractions import Fraction as Q
from itertools import permutations, product

import decision_v7 as core
import independent_oracle_v7 as oracle

PARTITIONS = oracle.partitions(3)
TABLES = tuple(tuple(tuple(flat[2 * i:2 * i + 2]) for i in range(3))
               for flat in product(range(3), repeat=6))
COVERAGE = {"loss_tables": 729, "partitions": 5, "minimax_comparisons": 3645,
            "policy_evaluations": 16038, "ordered_partition_pairs": 25,
            "dominance_comparisons": 18225, "refinement_pairs": 12,
            "nonrefinement_witnesses": 13, "transported_profiles": 30618,
            "signal_relabel_cases": 30, "action_relabel_cases": 10,
            "affine_cases": 3645, "certificate_mutations": 21}


class DecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {(losses, signal): core.minimax(losses, signal)
                       for losses, signal in product(TABLES, PARTITIONS)}

    def test_all_tables_against_independent_blockwise_oracle(self):
        self.assertEqual(len(TABLES), COVERAGE["loss_tables"])
        self.assertEqual(len(PARTITIONS), COVERAGE["partitions"])
        count = evaluated = 0
        for (losses, signal), result in self.results.items():
            self.assertEqual(result["value"], oracle.blockwise_minimax(losses, signal))
            self.assertTrue(oracle.certificate_is_valid(losses, signal, result))
            self.assertEqual(core.policy_profile(losses, signal, result["policy"]),
                             oracle.policy_profile(losses, signal, result["policy"]))
            evaluated += result["policy_evaluations"]
            count += 1
        self.assertEqual(count, COVERAGE["minimax_comparisons"])
        self.assertEqual(evaluated, COVERAGE["policy_evaluations"])

    def test_universal_dominance_exactly_characterizes_refinement(self):
        pairs = comparisons = refinements = witnesses = 0
        for fine, coarse in product(PARTITIONS, repeat=2):
            ordered = oracle.refinement(fine, coarse)
            self.assertEqual(core.refines(fine, coarse), ordered)
            comparisons_for_pair = [self.results[losses, fine]["value"] <=
                                    self.results[losses, coarse]["value"] for losses in TABLES]
            self.assertEqual(all(comparisons_for_pair), ordered)
            comparisons += len(comparisons_for_pair)
            pairs += 1
            refinements += int(ordered)
            if not ordered:
                supplied = core.separation_witness(fine, coarse)
                i, j = supplied["merged_worlds"]
                self.assertEqual(fine[i], fine[j])
                self.assertNotEqual(coarse[i], coarse[j])
                for losses in (supplied["losses"], oracle.separating_losses(fine, coarse)):
                    self.assertEqual(set(value for row in losses for value in row), {0, 1})
                    self.assertEqual(oracle.blockwise_minimax(losses, coarse), 0)
                    self.assertEqual(oracle.blockwise_minimax(losses, fine), 1)
                    self.assertEqual(core.minimax(losses, coarse)["value"], 0)
                    self.assertEqual(core.minimax(losses, fine)["value"], 1)
                witnesses += 1
        for count, key in ((pairs, "ordered_partition_pairs"), (comparisons, "dominance_comparisons"),
                           (refinements, "refinement_pairs"), (witnesses, "nonrefinement_witnesses")):
            self.assertEqual(count, COVERAGE[key])

    def test_transport_preserves_every_loss_profile(self):
        count = 0
        for fine, coarse in product(PARTITIONS, repeat=2):
            if not oracle.refinement(fine, coarse):
                continue
            mapping = core.refinement_map(fine, coarse)
            self.assertEqual(tuple(mapping[label] for label in fine), coarse)
            for policy in oracle.all_policies(coarse, 2):
                transported = core.transport_policy(fine, coarse, policy, 2)
                for losses in TABLES:
                    self.assertEqual(core.policy_profile(losses, fine, transported),
                                     oracle.policy_profile(losses, coarse, policy))
                    count += 1
        self.assertEqual(count, COVERAGE["transported_profiles"])

    def test_relabelings_and_positive_affine_losses(self):
        losses = ((0, 2), (2, 1), (1, 0))
        signals = actions = affine = 0
        for signal in PARTITIONS:
            expected = self.results[losses, signal]["value"]
            for ordering in permutations(range(3)):
                renamed = tuple("label:" + str(signal[i]) for i in ordering)
                reordered = tuple(losses[i] for i in ordering)
                self.assertEqual(core.minimax(reordered, renamed)["value"], expected)
                signals += 1
            for ordering in permutations(range(2)):
                relabeled = tuple(tuple(row[a] for a in ordering) for row in losses)
                self.assertEqual(core.minimax(relabeled, signal)["value"], expected)
                actions += 1
        for (losses, signal), result in self.results.items():
            transformed = tuple(tuple(Q(3, 2) * loss - Q(2, 3) for loss in row) for row in losses)
            self.assertEqual(core.minimax(transformed, signal)["value"],
                             Q(3, 2) * result["value"] - Q(2, 3))
            affine += 1
        for count, key in ((signals, "signal_relabel_cases"), (actions, "action_relabel_cases"),
                           (affine, "affine_cases")):
            self.assertEqual(count, COVERAGE[key])

    def test_paid_cost_restrictions_worlds_and_randomization_boundaries(self):
        losses, coarse, fine = ((0, 1), (1, 0)), (0, 0), (0, 1)
        coarse_value, fine_value = (core.minimax(losses, s)["value"] for s in (coarse, fine))
        for cost, verdict in ((0, "IMPROVES"), (1, "TIES"), (2, "WORSENS")):
            paid = core.paid_information(coarse_value, fine_value, cost)
            self.assertEqual(paid, {"classification": verdict, "paid_value": Q(cost),
                                    "net_gain": Q(1 - cost)})
        self.assertEqual(core.minimax(losses, fine, allowed_actions=(0,))["value"], 1)
        self.assertEqual(core.minimax(losses, fine, policies=({0: 0, 1: 0},))["value"], 1)
        asymmetric = ((0, 2), (1, 0))
        baseline = core.minimax(asymmetric, coarse)["value"]
        self.assertGreater(core.minimax(asymmetric, fine, allowed_actions=(1,))["value"], baseline)
        self.assertGreater(core.minimax(asymmetric, fine, policies=({0: 1, 1: 0},))["value"], baseline)
        omitted_world = core.minimax(losses[:1], coarse[:1])["value"]
        self.assertLess(omitted_world, coarse_value)
        self.assertEqual(core.minimax(((0, 0), (0, 0)), coarse)["value"], 0)
        randomized = oracle.randomized_worst_expected(losses, (Q(1, 2), Q(1, 2)))
        self.assertEqual(randomized, Q(1, 2))
        self.assertLess(randomized, coarse_value)
        # An adversary that sees the realized action can always choose loss 1.
        self.assertEqual(sum(Q(1, 2) * max(row[a] for row in losses) for a in (0, 1)), 1)

    def test_mutated_certificates_rejected_independently(self):
        losses, mutations = ((0, 2), (2, 1), (1, 0)), []
        for signal in PARTITIONS:
            result = self.results[losses, signal]
            wrong_value = copy.deepcopy(result)
            wrong_value["value"] += 1
            wrong_action = copy.deepcopy(result)
            wrong_action["policy"][0] = 2
            missing = copy.deepcopy(result)
            del missing["policy"][0]
            alias = copy.deepcopy(result)
            alias["policy"][False] = alias["policy"].pop(0)
            mutations.extend((signal, mutated) for mutated in
                             (wrong_value, wrong_action, missing, alias))
        for signal, mutated in mutations:
            self.assertFalse(oracle.certificate_is_valid(losses, signal, mutated))
        # Feasible, honestly scored, but nonoptimal: lower-bound check must fail.
        self.assertFalse(oracle.certificate_is_valid(((0, 1),), (0,),
                                                     {"policy": {0: 1}, "value": Q(1)}))
        self.assertEqual(len(mutations) + 1, COVERAGE["certificate_mutations"])

    def test_malformed_inputs_and_illegal_transports(self):
        bad = [((), ()), (((0, 1),), ()), (((0, 1), (0,)), (0, 1)),
               (((0.0, 1),), (0,)), (((True, 1),), (0,)), (((0, 1),), (False,)),
               (((0, 1), (1, 0)), (0, False)), (((0, 1),), (None,))]
        for losses, signal in bad:
            with self.subTest(losses=losses, signal=signal), self.assertRaises(ValueError):
                core.minimax(losses, signal)
        losses, signal = ((0, 1), (1, 0)), (0, 1)
        for kwargs in ({"allowed_actions": ()}, {"allowed_actions": (0, 0)},
                       {"allowed_actions": (0, False)}, {"allowed_actions": (2,)},
                       {"policies": ()}, {"policies": ({0: 0},)},
                       {"policies": ({0: 0, 1: False},)}, {"policies": ({False: 0, 1: 1},)}):
            with self.assertRaises(ValueError):
                core.minimax(losses, signal, **kwargs)
        with self.assertRaises(ValueError):
            core.transport_policy((0, 0), (0, 1), {0: 0, 1: 1}, 2)
        with self.assertRaises(ValueError):
            core.separation_witness((0, 1), (0, 0))
        for fine, coarse in (((), ()), ((0,), (0, 1)), ((0, False), (0, 1))):
            with self.assertRaises(ValueError):
                core.refines(fine, coarse)
        for policy, action_count in (({0: 0}, True), ({0: False}, 2), ({}, 2)):
            with self.assertRaises(ValueError):
                core.transport_policy((0, 1), (0, 0), policy, action_count)
        with self.assertRaises(ValueError):
            core.minimax(losses, signal, allowed_actions=(0,), policies=({0: 0, 1: 1},))
        for bad_cost in (-1, True, 1.0):
            with self.assertRaises(ValueError):
                core.paid_information(1, 0, bad_cost)


if __name__ == "__main__":
    unittest.main()
