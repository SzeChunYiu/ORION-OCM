#!/usr/bin/env python3
"""Tests for the #833 Section-M social/metacognitive re-audit.

Runnable with no third-party dependency:

    python3 -I -B  research/gmi-833-cognitive-reaudit-social-v1/test_cognitive_reaudit_social_v1.py
    python3 -I -O -B research/gmi-833-cognitive-reaudit-social-v1/test_cognitive_reaudit_social_v1.py

`-I` removes the script directory from `sys.path`, so the path is restored
explicitly below, exactly as the executor does.
"""

from __future__ import annotations

import ast
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cognitive_reaudit_social_v1 as exe     # noqa: E402
import registered_scopes_v1 as scopes         # noqa: E402
import route_b_oracle_v1 as route_b           # noqa: E402


RESULT_PATH = HERE / "RESULT_V1.json"


class TestExactnessDiscipline(unittest.TestCase):
    """No float may appear anywhere in the package's decision path."""

    def test_no_float_literals_in_any_source_file(self):
        for name in ("cognitive_reaudit_social_v1.py",
                     "registered_scopes_v1.py",
                     "route_b_oracle_v1.py",
                     "test_cognitive_reaudit_social_v1.py"):
            tree = ast.parse((HERE / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, float):
                    self.fail("float literal %r in %s line %d"
                              % (node.value, name, node.lineno))

    def test_exact_guard_rejects_floats_and_bools(self):
        self.assertEqual(scopes.exact(3), F(3))
        self.assertEqual(scopes.exact(F(1, 3)), F(1, 3))
        with self.assertRaises(ValueError):
            scopes.exact(float(1))
        with self.assertRaises(ValueError):
            scopes.exact(True)

    def test_registered_priors_are_exact_probability_vectors(self):
        for prior in scopes.SOCIAL_PRIORS_2 + scopes.SOCIAL_PRIORS_3:
            self.assertTrue(scopes.is_probability_vector(prior))
        for _family, _n, _a, _levels, priors in scopes.COMM_FAMILIES:
            for prior in priors:
                self.assertTrue(scopes.is_probability_vector(prior))
        for probs in scopes.DELIB_PROBS:
            self.assertTrue(scopes.is_probability_vector(probs))

    def test_probability_vector_rejects_off_simplex(self):
        self.assertFalse(scopes.is_probability_vector((F(1, 2), F(1, 3))))
        self.assertFalse(scopes.is_probability_vector((F(-1), F(2))))


class TestRouteIndependence(unittest.TestCase):
    def test_oracle_does_not_import_the_analytic_executor(self):
        tree = ast.parse((HERE / "route_b_oracle_v1.py").read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
        self.assertNotIn("cognitive_reaudit_social_v1", imported)

    def test_registered_scopes_module_holds_no_verdict_vocabulary(self):
        text = (HERE / "registered_scopes_v1.py").read_text(encoding="utf-8")
        for banned in ("GREEN", "claim_ceiling", "def route_a_", "backward"):
            self.assertNotIn(banned, text)


class TestMC1Metacognition(unittest.TestCase):
    def test_voc1_threshold_hand_computed(self):
        # root retained value 0; outcomes 1/2 : 1/2 onto values 2 and 0; price 1.
        scope = {
            "node_value": {(): F(0), (0,): F(2), (1,): F(0),
                           (0, 0): F(0), (0, 1): F(0), (1, 0): F(0), (1, 1): F(0)},
            "price": {(): F(1), (0,): F(1), (1,): F(1)},
            "prob": (F(1, 2), F(1, 2)),
            "depth": 2, "branch": 2,
        }
        improvement, worth = exe.route_a_voc(scope, ())
        self.assertEqual(improvement, F(1))
        # exactly break-even: strictly greater is required, so it is NOT worth it
        self.assertFalse(worth)
        worth_b, stop_value, step_value = route_b.brute_force_myopic_step_worth(
            scope, (), F(0))
        self.assertFalse(worth_b)
        self.assertEqual(step_value - stop_value, F(0))

    def test_voc1_is_never_negative_on_the_full_census(self):
        seen = 0
        for index, scope in enumerate(scopes.iter_deliberation_scopes()):
            if index % 97:
                continue
            for path in scopes.delib_decision_paths():
                improvement, _worth = exe.route_a_voc(scope, path)
                self.assertGreaterEqual(improvement, F(0))
                seen += 1
        self.assertGreater(seen, 0)

    def test_voc2_matches_exhaustive_policy_enumeration_on_a_sample(self):
        checked = 0
        for index, scope in enumerate(scopes.iter_deliberation_scopes()):
            if index % 311:
                continue
            value_a, policy_a = exe.route_a_optimal_allocation(scope)
            value_b, _policy_b = route_b.brute_force_best_allocation(scope)
            self.assertEqual(value_a, value_b)
            self.assertEqual(exe.route_a_trace(scope, policy_a),
                             route_b.brute_force_reachable_trace(scope, policy_a))
            checked += 1
        self.assertGreater(checked, 10)

    def test_nonid1_twin_exists_for_deterministic_allocation(self):
        instance_scopes = scopes.aliasing_instance_scopes()
        observed = {}
        for label in sorted(instance_scopes):
            _value, policy = exe.route_a_optimal_allocation(instance_scopes[label])
            observed[label] = [exe.route_a_trace(instance_scopes[label], policy)]
        twin = exe.route_a_fixed_schedule_twin(observed)
        self.assertIsNotNone(twin)
        matches = route_b.brute_force_schedules_matching_trace_sets(
            instance_scopes, observed)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], twin)

    def test_nonid1_boundary_latent_draw_admits_no_twin(self):
        instance_scopes = scopes.aliasing_instance_scopes()
        observed = {}
        for label in sorted(instance_scopes):
            _value, policy = exe.route_a_optimal_allocation(instance_scopes[label])
            observed[label] = [exe.route_a_trace(instance_scopes[label], policy)]
        label = sorted(instance_scopes)[0]
        scope = instance_scopes[label]
        decisions = scopes.delib_decision_paths(scope["depth"], scope["branch"])
        observed[label] = [
            exe.route_a_trace(scope, dict((d, False) for d in decisions)),
            exe.route_a_trace(scope, dict((d, True) for d in decisions)),
        ]
        self.assertNotEqual(observed[label][0], observed[label][1])
        self.assertIsNone(exe.route_a_fixed_schedule_twin(observed))
        self.assertEqual(
            route_b.brute_force_schedules_matching_trace_sets(instance_scopes, observed),
            [])


class TestMC2SocialCognition(unittest.TestCase):
    def test_false_belief_witness_exact_gap(self):
        prior = (F(1, 2), F(1, 2))
        score = ((F(2), F(0)), (F(0), F(2)))
        v_obs = exe.route_a_refinement_value(prior, score, (0, 0), 2)
        v_hid = exe.route_a_finest_value(prior, score, 2)
        self.assertEqual(v_obs, F(1))
        self.assertEqual(v_hid, F(2))
        self.assertEqual(v_hid - v_obs, F(1))

    def test_behaviour_reading_twin_matches_exactly(self):
        prior = (F(1, 2), F(1, 2))
        score = ((F(2), F(0)), (F(0), F(2)))
        v_obs = exe.route_a_refinement_value(prior, score, (0, 1), 2)
        v_hid = exe.route_a_finest_value(prior, score, 2)
        self.assertEqual(v_hid - v_obs, F(0))

    def test_soc1_monotone_and_equality_iff_on_a_sample(self):
        checked = 0
        for index, eco in enumerate(scopes.iter_social_ecologies()):
            if index % 401:
                continue
            prior, score = eco["prior"], eco["score"]
            n_actions = eco["n_actions"]
            v_obs = exe.route_a_refinement_value(prior, score, eco["channel"], n_actions)
            v_hid = exe.route_a_finest_value(prior, score, n_actions)
            self.assertEqual(v_obs, route_b.brute_force_channel_value(eco))
            self.assertEqual(v_hid, route_b.brute_force_hidden_value(eco))
            self.assertGreaterEqual(v_hid, v_obs)
            predicate = exe.route_a_pointwise_sufficient(
                prior, score, eco["channel"], n_actions)
            self.assertEqual(predicate, v_hid == v_obs)
            checked += 1
        self.assertGreater(checked, 10)

    def test_support_restriction_is_load_bearing(self):
        # state 1 carries zero probability and has a different pointwise optimum.
        # Equality still holds; a naive condition ignoring the support would fail.
        prior = (F(1), F(0))
        score = ((F(2), F(0)), (F(0), F(2)))
        v_obs = exe.route_a_refinement_value(prior, score, (0, 0), 2)
        v_hid = exe.route_a_finest_value(prior, score, 2)
        self.assertEqual(v_hid, v_obs)
        self.assertTrue(exe.route_a_pointwise_sufficient(prior, score, (0, 0), 2))


class TestMC3Communication(unittest.TestCase):
    def test_com2_equivalence_on_a_sample(self):
        checked = 0
        seen_true = 0
        seen_false = 0
        for index, eco in enumerate(scopes.iter_communication_ecologies()):
            if index % 1013:
                continue
            prior, score = eco["prior"], eco["score"]
            n_actions = eco["n_actions"]
            trivial = tuple(0 for _ in prior)
            v_pi = exe.route_a_refinement_value(prior, score, eco["partition"], n_actions)
            v_0 = exe.route_a_refinement_value(prior, score, trivial, n_actions)
            constant = route_b.brute_force_constant_action_is_blockwise_optimal(eco)
            self.assertEqual(v_pi == v_0, constant)
            if constant:
                seen_true += 1
            else:
                seen_false += 1
            checked += 1
        self.assertGreater(checked, 10)
        self.assertGreater(seen_true, 0)
        self.assertGreater(seen_false, 0)

    def test_free_but_useless_boundary(self):
        prior = (F(1, 2), F(1, 2))
        score = ((F(2), F(0)), (F(3), F(1)))   # action 0 dominates in every state
        eco = {"prior": prior, "score": score, "partition": (0, 1),
               "n_actions": 2, "price": F(0)}
        v_pi = exe.route_a_refinement_value(prior, score, (0, 1), 2)
        v_0 = exe.route_a_refinement_value(prior, score, (0, 0), 2)
        self.assertEqual(v_pi, v_0)
        self.assertFalse(route_b.brute_force_channel_strictly_pays(eco))

    def test_valuable_but_unaffordable_boundary(self):
        prior = (F(1, 2), F(1, 2))
        score = ((F(2), F(0)), (F(0), F(2)))
        eco = {"prior": prior, "score": score, "partition": (0, 1),
               "n_actions": 2, "price": F(1)}
        v_pi = exe.route_a_refinement_value(prior, score, (0, 1), 2)
        v_0 = exe.route_a_refinement_value(prior, score, (0, 0), 2)
        self.assertEqual(v_pi - v_0, F(1))       # genuinely valuable
        self.assertFalse(route_b.brute_force_channel_strictly_pays(eco))  # exactly break-even
        eco_cheap = dict(eco)
        eco_cheap["price"] = F(1, 2)
        self.assertTrue(route_b.brute_force_channel_strictly_pays(eco_cheap))

    def test_shared_observation_hostile_twin(self):
        prior = (F(1, 2), F(1, 2))
        score = ((F(2), F(0)), (F(0), F(2)))
        eco = {"prior": prior, "score": score, "partition": (0, 1),
               "n_actions": 2, "price": F(1, 2)}
        shared = route_b.brute_force_shared_observation_value(eco)
        channelled = route_b.brute_force_channel_partition_value(eco)
        self.assertEqual(shared, channelled)   # same coordination, zero channel charge


class TestMC4ImitationAndTeaching(unittest.TestCase):
    def test_all_four_cells_are_realizable(self):
        seen = set()
        for instance in scopes.iter_teaching_instances():
            seen.add(route_b.brute_force_cell(instance))
        self.assertEqual(seen, {(True, True), (True, False), (False, True), (False, False)})

    def test_failed_teaching_is_not_teaching(self):
        instance = {"learner_control": F(1), "learner_demo": F(1),
                    "demonstrator": F(2), "learners": 3}
        self.assertTrue(exe.route_a_demonstrator_pays(instance))
        self.assertFalse(exe.route_a_imitation(instance))
        self.assertTrue(exe.route_a_failed_teaching(instance))
        self.assertFalse(exe.route_a_teaching(instance))

    def test_tch2_threshold_exact_and_strict(self):
        # n * Delta == D exactly: total charge is unchanged, so it is NOT worth it.
        break_even = {"learner_control": F(2), "learner_demo": F(1),
                      "demonstrator": F(3), "learners": 3}
        with_demo, without_demo = route_b.brute_force_totals(break_even)
        self.assertEqual(with_demo, F(6))
        self.assertEqual(without_demo, F(6))
        self.assertFalse(exe.route_a_jointly_worthwhile(break_even))
        self.assertFalse(route_b.brute_force_teaching_worthwhile(break_even))
        # one more learner tips n * Delta strictly above D.
        worth = dict(break_even)
        worth["learners"] = 4
        self.assertTrue(exe.route_a_jointly_worthwhile(worth))
        self.assertTrue(route_b.brute_force_teaching_worthwhile(worth))
        # and it is exactly the demonstrator charge that decides it
        self.assertTrue(exe.route_a_free_labour_worthwhile(break_even))

    def test_tch3_containment_is_strict(self):
        strict_witnesses = 0
        for instance in scopes.iter_teaching_instances():
            charged = exe.route_a_jointly_worthwhile(instance)
            free = exe.route_a_free_labour_worthwhile(instance)
            self.assertFalse(charged and not free)      # containment
            if free and not charged:
                strict_witnesses += 1
        self.assertGreater(strict_witnesses, 0)

    def test_nonid4_control_arm_is_load_bearing(self):
        rng = scopes.Lcg(seed=7)
        naive_fires = 0
        control_fires = 0
        trials = 0
        for _ in range(100):
            instance = scopes.random_concurrent_cause_instance(rng)
            trials += 1
            if exe.route_a_naive_prepost_imitation(instance):
                naive_fires += 1
            if exe.route_a_imitation(instance):
                control_fires += 1
        self.assertEqual(naive_fires, trials)
        self.assertEqual(control_fires, 0)


class TestMC5CulturalAccumulation(unittest.TestCase):
    def test_closed_form_matches_iteration_on_the_full_census(self):
        for phi, g, a0 in scopes.iter_culture_triples():
            self.assertEqual(
                exe.route_a_closed_form_trajectory(phi, g, a0, 6),
                route_b.brute_force_trajectory(phi, g, a0, 6))

    def test_exact_ratchet_condition(self):
        phi, g, a0 = F(1, 2), F(1), F(0)
        traj = exe.route_a_closed_form_trajectory(phi, g, a0, 6)
        self.assertEqual(traj[1], F(1))
        self.assertEqual(traj[2], F(3, 2))
        star = g / (F(1) - phi)
        self.assertEqual(star, F(2))
        flags = exe.route_a_ratchet_flags(phi, g, traj)
        self.assertEqual(flags, route_b.brute_force_ratchet_flags(traj))
        self.assertTrue(all(flags))                 # every generation below a*
        self.assertTrue(all(a < star for a in traj))

    def test_return_to_baseline_without_innovation(self):
        traj = exe.route_a_closed_form_trajectory(F(1, 2), F(0), F(4), 6)
        self.assertEqual(traj[-1], F(4) * F(1, 2) ** 6)
        self.assertLess(traj[-1], F(4))
        zero = exe.route_a_closed_form_trajectory(F(0), F(0), F(4), 6)
        self.assertEqual(zero[-1], F(0))

    def test_lossless_unbounded_ratchet(self):
        traj = exe.route_a_closed_form_trajectory(F(1), F(1, 2), F(1), 8)
        self.assertEqual(traj[-1], F(1) + F(8) * F(1, 2))

    def test_nonid5_zero_transmission_twin_reproduces_every_trajectory(self):
        for phi, g, a0 in scopes.iter_culture_triples():
            traj = route_b.brute_force_trajectory(phi, g, a0, 6)
            twin = route_b.brute_force_rederivation_twin(traj, 6)
            self.assertEqual(twin, traj)

    def test_cul3_equal_unit_costs_never_separate(self):
        for phi, g, a0 in scopes.iter_culture_triples():
            traj = exe.route_a_closed_form_trajectory(phi, g, a0, 4)
            for unit in scopes.CULTURE_UNIT_COSTS:
                for n in range(4):
                    self.assertEqual(
                        exe.route_a_cost_separation(phi, g, traj[n], unit, unit, unit),
                        F(0))

    def test_cul3_strict_margin_when_transmission_is_cheaper(self):
        phi, g, a0 = F(1, 2), F(1), F(2)
        traj = exe.route_a_closed_form_trajectory(phi, g, a0, 4)
        t, r, k = F(1, 2), F(2), F(2)      # k == r, t < r
        for n in range(4):
            margin = exe.route_a_cost_separation(phi, g, traj[n], t, r, k)
            self.assertEqual(margin, -(r - t) * phi * traj[n])
            if phi * traj[n] > 0:
                self.assertLess(margin, F(0))   # transmission strictly cheaper


class TestCommittedReceipt(unittest.TestCase):
    def test_receipt_exists_and_is_green(self):
        self.assertTrue(RESULT_PATH.is_file(), "RESULT_V1.json must be committed")
        payload = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(payload["verdict"], "GREEN")
        self.assertEqual(payload["claim_ceiling"], exe.CLAIM_CEILING)
        self.assertEqual(payload["frozen_source_main"], exe.FROZEN_SOURCE_MAIN)
        for row in payload["rows"].values():
            for count in row["two_route_mismatches"].values():
                self.assertEqual(count, 0)

    def test_receipt_carries_no_forbidden_promotion_as_a_claim(self):
        payload = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        blob = json.dumps(payload["rows"], sort_keys=True)
        for promotion in exe.FORBIDDEN_PROMOTIONS:
            self.assertNotIn(promotion, blob)

    def test_receipt_reproduces_exactly(self):
        payload = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        rebuilt = exe.build_result()
        self.assertEqual(
            json.dumps(rebuilt, indent=2, sort_keys=True),
            json.dumps(payload, indent=2, sort_keys=True))

    def test_parents_are_pinned_without_drift(self):
        audit = exe.audit_parents()
        self.assertEqual(audit["drift"], [])
        self.assertTrue(audit["all_pinned"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
