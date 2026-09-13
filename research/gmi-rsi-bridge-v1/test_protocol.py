"""Hostile tests for the GMI ↔ RSI bridge evidence contract."""
from __future__ import annotations

import importlib.util
import sys
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC_M = importlib.util.spec_from_file_location("gmi_rsi_model", HERE / "model.py")
M = importlib.util.module_from_spec(SPEC_M)
sys.modules[SPEC_M.name] = M
SPEC_M.loader.exec_module(M)
SPEC_E = importlib.util.spec_from_file_location("gmi_rsi_experiment", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC_E)
sys.modules[SPEC_E.name] = E
SPEC_E.loader.exec_module(E)


class TestRecursiveEvolvabilityProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen, cls.mutable, cls.fixed_d, cls.gaming, cls.extra_compute = E.arms()

    def test_fixed_updater_repeated_self_edit_is_not_rsi(self):
        result = M.classify(self.fixed_d, frozen_comparator=self.frozen)
        self.assertEqual(result.level, M.RSILevel.R2_SELF_MODIFICATION)

    def test_mutable_updater_with_matched_descendant_gain_reaches_r4(self):
        result = M.classify(self.mutable, frozen_comparator=self.frozen)
        self.assertEqual(result.level, M.RSILevel.R4_HERITABLE_RECURSIVE_DEVELOPMENT)
        self.assertIsNotNone(result.meta_gain)
        self.assertGreater(result.meta_gain.delta, 0)

    def test_r3_allows_a_temporarily_worse_stepping_stone(self):
        self.assertLess(self.mutable.records[1].shadow_quality, self.mutable.records[0].shadow_quality)
        result = M.classify(self.mutable, frozen_comparator=self.frozen)
        self.assertGreaterEqual(result.level, M.RSILevel.R3_RECURSIVE_EVOLVABILITY)

    def test_resource_confound_fails_closed(self):
        result = M.classify(self.extra_compute, frozen_comparator=self.frozen)
        self.assertEqual(result.level, M.RSILevel.R2_SELF_MODIFICATION)
        self.assertTrue(any("resource matched" in r or "resource" in r for r in result.reasons))

    def test_evaluator_gaming_fails_without_frozen_shadow(self):
        result = M.classify(self.gaming, frozen_comparator=self.frozen)
        self.assertEqual(result.level, M.RSILevel.R2_SELF_MODIFICATION)
        self.assertIn("mutable evaluator lacks frozen shadow reference", result.reasons)

    def test_positive_recursive_evolvability_does_not_imply_acceleration(self):
        result = M.classify(self.mutable, frozen_comparator=self.frozen)
        self.assertGreaterEqual(result.level, M.RSILevel.R3_RECURSIVE_EVOLVABILITY)
        self.assertFalse(M.is_strictly_accelerating([r.shadow_quality for r in self.mutable.records]))

    def test_finite_transfer_never_promotes_to_open_ended_r5(self):
        result = M.classify(
            self.mutable,
            frozen_comparator=self.frozen,
            cross_domain_replications=100,
            open_ended_generations=1000,
        )
        self.assertEqual(result.level, M.RSILevel.R4_HERITABLE_RECURSIVE_DEVELOPMENT)
        self.assertTrue(any("do not establish R5" in r for r in result.reasons))

    def test_hidden_human_intervention_blocks_r3(self):
        arm = M.AssayArm(
            **{**self.mutable.__dict__, "name": "HIDDEN_HUMAN", "hidden_human_intervention": True}
        )
        result = M.classify(arm, frozen_comparator=self.frozen)
        self.assertEqual(result.level, M.RSILevel.R2_SELF_MODIFICATION)

    def test_external_constitution_self_mutation_is_rejected(self):
        bad = M.GenerationRecord(
            generation=0, task_quality=.5, shadow_quality=.5,
            persistent_change=False, self_change=False,
            development_operator_changed=False, development_operator_digest="D0",
            machine_digest="ROOT",
            external_constitution_changed_by_agent=True,
        )
        with self.assertRaises(M.EvidenceError):
            bad.validate()

    def test_cosmetic_d_edit_without_execution_stays_r2(self):
        records = list(self.mutable.records)
        changed = records[1]
        records[1] = M.GenerationRecord(**{**changed.__dict__, "development_operator_executed": False})
        arm = M.AssayArm(**{**self.mutable.__dict__, "name": "COSMETIC_D", "records": tuple(records)})
        result = M.classify(arm, frozen_comparator=self.frozen)
        self.assertEqual(result.level, M.RSILevel.R2_SELF_MODIFICATION)
        self.assertTrue(any("lacks executed" in r for r in result.reasons))

    def test_human_originated_or_unadmitted_d_change_stays_r2(self):
        for field in ("machine_originated", "externally_admitted"):
            records = list(self.mutable.records)
            changed = records[1]
            records[1] = M.GenerationRecord(**{**changed.__dict__, field: False})
            arm = M.AssayArm(**{**self.mutable.__dict__, "name": f"BAD_{field}", "records": tuple(records)})
            result = M.classify(arm, frozen_comparator=self.frozen)
            self.assertEqual(result.level, M.RSILevel.R2_SELF_MODIFICATION)

    def test_held_out_ecology_must_differ_from_development_ecology(self):
        arm = M.AssayArm(**{**self.mutable.__dict__, "held_out_ecology": self.mutable.development_ecology})
        with self.assertRaises(M.EvidenceError):
            arm.validate()

    def test_lineage_parent_discontinuity_fails_closed(self):
        records = list(self.mutable.records)
        child = records[2]
        records[2] = M.GenerationRecord(**{**child.__dict__, "parent_digest": "WRONG"})
        arm = M.AssayArm(**{**self.mutable.__dict__, "name": "BROKEN_LINEAGE", "records": tuple(records)})
        with self.assertRaises(M.EvidenceError):
            arm.validate()

    def test_claim_ledger_has_no_dangling_or_nonterminal_nodes(self):
        ledger = json.loads((HERE / "CLAIM_LEDGER.json").read_text(encoding="utf-8"))
        M.assert_terminal_ledger(ledger)
        self.assertTrue(ledger["recursive_ledger_terminal"])

    def test_every_gap_family_has_atomic_children(self):
        ledger = json.loads((HERE / "CLAIM_LEDGER.json").read_text(encoding="utf-8"))
        required = {"definition", "mechanism", "observable", "test", "counterexample", "boundary"}
        roots = ledger["gap_families"]
        self.assertEqual(len(roots), 15)
        for root in roots:
            self.assertEqual(set(root["children"]), required, root["id"])

    def test_synthetic_result_is_reproducible(self):
        generated = E.run(out=None)
        committed = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual(generated, committed)


if __name__ == "__main__":
    unittest.main()
