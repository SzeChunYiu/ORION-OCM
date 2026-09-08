"""E1 software assurance using abstract predicates, never actual donor families.

All nineteen full-true monotone Boolean functions on THREE variables are
embedded into the four-bit API with one irrelevant bit. These authored software
fixtures test implementation contracts, not cognitive efficacy or transfer.
No source catalogue or development experiment is executed.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact_verification import all_monotone_truth_tables
from support_effects import Cost, SupportLearner, monotone_tables


class SupportEffectSoftwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basis = monotone_tables(4, Cost())
        cls.truths = tuple(t for t in all_monotone_truth_tables(3) if t[7])
        assert len(cls.truths) == 19

    def learner(self, arm, context=None):
        return SupportLearner(arm, 4,
            context or {"scope": "E1_ABSTRACT_INTERFACE_ONLY", "checker": "three-bit-truth-table"},
            Cost(), self.basis if arm == "active_monotone" else ())

    def test_complete_abstract_predicate_domain_sound_arms(self):
        for truth in self.truths:
            for arm in ("active_monotone", "antichain_parent", "eager_table", "lazy_cache"):
                with self.subTest(truth=truth, arm=arm):
                    learner = self.learner(arm)
                    calls = []

                    def oracle(mask):
                        calls.append(mask)
                        return bool(truth[mask & 7])

                    learner.acquire(oracle)
                    self.assertEqual(len(calls), learner.cost.query_calls)
                    self.assertEqual(len(calls), len(set(calls)))
                    self.assertLessEqual(len(calls), 15)
                    for mask in range(16):
                        prediction = learner.predict(mask)
                        if prediction is not None:
                            self.assertEqual(prediction, bool(truth[mask & 7]))
                        answer, _ = learner.answer(mask, oracle)
                        self.assertEqual(answer, bool(truth[mask & 7]))
                    self.assertEqual(len(calls), learner.cost.query_calls)

    def test_known_redundancy_refutes_single_deletion_ablation(self):
        learner = self.learner("loo_ablation")
        learner.acquire(lambda mask: bool(mask & 7))
        self.assertTrue(learner.predict(0))
        self.assertFalse(bool(0 & 7))
        self.assertEqual(learner.record()["certification"], "UNSOUND_ABLATION")

    def test_counterfactual_removal_keeps_exact_observations(self):
        learner = self.learner("antichain_parent")
        learner.observe(1, True)
        self.assertTrue(learner.predict(3))
        self.assertIsNone(learner.predict(3, generalize=False))
        self.assertTrue(learner.predict(1, generalize=False))
        original = dict(learner.observations)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            identity = learner.persist(path)
            removed = SupportLearner.restart(path, expected_hash=identity,
                expected_context=learner.context, cost=Cost())
            self.assertEqual(removed.observations, original)
            self.assertIsNone(removed.predict(3, generalize=False))
            self.assertTrue(removed.predict(1, generalize=False))

    def test_restart_integrity_and_scope_binding(self):
        learner = self.learner("antichain_parent")
        learner.observe(1, True)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            identity = learner.persist(path)
            restarted_cost = Cost()
            restarted = SupportLearner.restart(path, expected_hash=identity,
                expected_context=copy.deepcopy(learner.context), cost=restarted_cost)
            self.assertTrue(restarted.predict(3))
            self.assertEqual(restarted_cost.serialization_bytes_read, path.stat().st_size)
            with self.assertRaises(ValueError):
                SupportLearner.restart(path, expected_hash=identity,
                    expected_context={"scope": "DIFFERENT"}, cost=Cost())
            payload = json.loads(path.read_text())
            payload["record"]["observations"]["1"] = False
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                SupportLearner.restart(path, expected_hash=identity,
                    expected_context=learner.context, cost=Cost())

    def test_context_is_detached_and_partial_knowledge_stays_marked(self):
        context = {"source": {"version": "v1"}, "scope": "E1_ABSTRACT_ONLY"}
        learner = self.learner("lazy_cache", context)
        context["source"]["version"] = "v2"
        self.assertEqual(learner.context["source"]["version"], "v1")
        record = learner.record()
        self.assertFalse(record["predictions_cover_domain"])
        self.assertEqual(len(record["unknown_masks"]), 15)
        self.assertIn("not a global minimal-support certificate", record["minimality_scope"])
        record["context"]["source"]["version"] = "v3"
        self.assertEqual(learner.context["source"]["version"], "v1")

    def test_contradictory_membership_evidence_is_refused(self):
        for arm in ("active_monotone", "antichain_parent", "eager_table"):
            with self.subTest(arm=arm):
                learner = self.learner(arm)
                learner.observe(1, True)
                with self.assertRaises(ValueError):
                    learner.observe(3, False)
        with self.assertRaises(ValueError):
            self.learner("antichain_parent").observe(1, 1)

    def test_invalid_mask_refused_before_oracle(self):
        learner = self.learner("antichain_parent")
        for mask in (-1, 16, True, 1.5):
            with self.subTest(mask=mask):
                with self.assertRaises(ValueError):
                    learner.answer(mask, lambda _: self.fail("invalid mask reached oracle"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
