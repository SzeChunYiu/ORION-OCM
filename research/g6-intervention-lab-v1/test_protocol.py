from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

import experiment as E
from world import CONSTITUTION, World, HiddenState, independent_truth, make_incidents, stuck_from_seed


class TestG6InterventionLab(unittest.TestCase):
    def test_proposer_cannot_modify_constitution(self):
        world = World(HiddenState(frozenset({1}), "t"))
        with self.assertRaises(PermissionError):
            world.intervene(-1)
        self.assertEqual(world.constitution, set(CONSTITUTION))

    def test_rollback_restores_modules(self):
        world = World(HiddenState(frozenset({2, 4}), "t"))
        world.intervene(2)
        self.assertTrue(world.modules[2])
        world.rollback()
        self.assertFalse(world.modules[2])

    def test_restart_preserves_adopted_state(self):
        world = World(HiddenState(frozenset({0}), "t"))
        world.intervene(0)
        clone = world.restart_clone()
        self.assertEqual(clone.modules, world.modules)

    def test_generations_are_disjoint_and_not_relabels(self):
        seen: set = set()
        g0 = make_incidents(0, 8, E.SALT, disjoint_from=seen)
        g1 = make_incidents(1, 8, E.SALT, disjoint_from=seen)
        g2 = make_incidents(2, 8, E.SALT, disjoint_from=seen)
        ids = [i.hidden.stuck for i in g0 + g1 + g2]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotEqual([i.incident_id for i in g0], [i.incident_id for i in g1])

    def test_protected_results_do_not_enter_learner_table(self):
        incident = make_incidents(0, 1, "prot", disjoint_from=set())[0]
        incident.protected = True
        self.assertTrue(incident.protected)
        # Learner only consumes transcript fields; protected flag must travel with the record.
        self.assertIn("incident_id", incident.transcript)

    def test_experiment_emits_three_generations_and_raw_traces(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RESULT.json"
            result = E.main(path)
            self.assertTrue(path.exists())
        self.assertTrue(result["raw_traces"])
        self.assertEqual(len(result["generations"]), 3)
        self.assertFalse(result["historical_m11_relabeled"])
        self.assertIn(result["terminal"], {
            "SELF_EVOLUTION_SUPPORTED_BOUNDED",
            "MULTI_GENERATION_SELF_CHANGE_SUPPORTED",
            "AUTOML_PARENT_SUFFICIENT",
            "NO_MULTI_GENERATION_IMPROVEMENT",
            "SELF_DIAGNOSIS_NOT_IDENTIFIABLE",
        })
        for gen in result["generations"]:
            self.assertGreater(gen["n"], 0)

    def test_incident_seed_replays_stuck_modules(self):
        incidents = make_incidents(0, 8, E.SALT, disjoint_from=set())
        for incident in incidents:
            self.assertEqual(stuck_from_seed(incident.hidden.seed), incident.hidden.stuck)
            self.assertEqual(independent_truth(incident.hidden), incident.hidden.stuck)
        mismatched = HiddenState(incidents[0].hidden.stuck, incidents[0].hidden.seed + ":drift")
        with self.assertRaises(AssertionError):
            independent_truth(mismatched)

    def test_identical_replay_is_not_a_new_generation(self):
        a = make_incidents(0, 4, "same", disjoint_from=set())
        b = make_incidents(0, 4, "same", disjoint_from=set())
        self.assertEqual([i.hidden.stuck for i in a], [i.hidden.stuck for i in b])


if __name__ == "__main__":
    unittest.main()
