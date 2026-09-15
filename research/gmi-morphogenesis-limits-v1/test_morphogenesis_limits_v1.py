from __future__ import annotations

import importlib.util
import itertools
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("morphogenesis_limits_v1", ROOT / "morphogenesis_limits_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load morphogenesis limits module")
SPEC.loader.exec_module(mod)


class ExpansionPruningTests(unittest.TestCase):
    def test_expansion_crosses_lifecycle_threshold(self):
        # Keep pays 6/task. Expanded form costs 8 once, then 1 loss + 1 maintenance/task.
        self.assertEqual(mod.KEEP, mod.expansion_verdict(horizon=1, current_loss_per_task=6, expanded_loss_per_task=1, expansion_cost=8, expanded_maintenance_per_task=1)["verdict"])
        self.assertEqual(mod.EXPAND, mod.expansion_verdict(horizon=3, current_loss_per_task=6, expanded_loss_per_task=1, expansion_cost=8, expanded_maintenance_per_task=1)["verdict"])

    def test_expansion_negative_twin_no_functional_gain(self):
        result = mod.expansion_verdict(horizon=10, current_loss_per_task=3, expanded_loss_per_task=3, expansion_cost=1, expanded_maintenance_per_task=1)
        self.assertEqual(mod.KEEP, result["verdict"])

    def test_pruning_unused_structure_eventually_wins(self):
        # Keeping unused structure costs 2/task; pruning costs 5 once and causes no loss.
        self.assertEqual(mod.KEEP, mod.pruning_verdict(horizon=2, maintenance_per_task=2, keep_loss_per_task=0, post_prune_loss_per_task=0, prune_cost=5)["verdict"])
        self.assertEqual(mod.PRUNE, mod.pruning_verdict(horizon=3, maintenance_per_task=2, keep_loss_per_task=0, post_prune_loss_per_task=0, prune_cost=5)["verdict"])

    def test_pruning_load_bearing_structure_can_lose(self):
        result = mod.pruning_verdict(horizon=4, maintenance_per_task=1, keep_loss_per_task=0, post_prune_loss_per_task=3, prune_cost=0)
        self.assertEqual(mod.KEEP, result["verdict"])


class CompilationAndLocalMorphogenesisTests(unittest.TestCase):
    def test_self_compilation_reuse_crossover(self):
        # Interpreted=6/use. Compile once for 10, then 2/use + 1 verification/use.
        self.assertEqual(mod.INTERPRET, mod.self_compilation_verdict(reuse=2, interpreted_cost_per_use=6, compiled_cost_per_use=2, compile_cost=10, verification_cost_per_use=1)["verdict"])
        self.assertEqual(mod.COMPILE, mod.self_compilation_verdict(reuse=4, interpreted_cost_per_use=6, compiled_cost_per_use=2, compile_cost=10, verification_cost_per_use=1)["verdict"])

    def test_verification_can_erase_compilation_gain(self):
        result = mod.self_compilation_verdict(reuse=100, interpreted_cost_per_use=5, compiled_cost_per_use=2, compile_cost=0, verification_cost_per_use=3)
        self.assertEqual(mod.TIE, result["verdict"])

    def test_local_morphogenesis_requires_sufficiency_then_cost_advantage(self):
        sufficient = mod.local_morphogenesis_verdict(
            horizon=4,
            global_rebuild_cost=20,
            local_patch_cost=5,
            local_verification_cost=2,
            local_residual_loss_per_task=1,
            local_obligation_sufficient=True,
        )
        self.assertEqual(mod.LOCAL, sufficient["verdict"])
        insufficient = mod.local_morphogenesis_verdict(
            horizon=4,
            global_rebuild_cost=20,
            local_patch_cost=1,
            local_verification_cost=1,
            local_residual_loss_per_task=0,
            local_obligation_sufficient=False,
        )
        self.assertEqual(mod.GLOBAL, insufficient["verdict"])


class MultiGenerationTests(unittest.TestCase):
    def test_exact_bounded_trajectory(self):
        self.assertEqual((10, 8, 6, 4, 2, 1, 1), mod.generation_burden_trajectory(initial_burden=10, inherited_reduction=3, maintenance=1, generations=6))

    def test_maintenance_larger_than_reduction_drives_growth(self):
        self.assertEqual((2, 4, 6, 8), mod.generation_burden_trajectory(initial_burden=2, inherited_reduction=1, maintenance=3, generations=3))

    def test_reset_like_zero_inheritance_fixed_point(self):
        self.assertEqual((4, 4, 4, 4), mod.generation_burden_trajectory(initial_burden=4, inherited_reduction=0, maintenance=0, generations=3))


class FiniteStateLimitTests(unittest.TestCase):
    def test_simple_tail_then_cycle(self):
        transition = {"a": "b", "b": "c", "c": "b"}
        cert = mod.finite_state_cycle_certificate(transition, "a")
        self.assertEqual(1, cert["prefix_length"])
        self.assertEqual(2, cert["cycle_length"])
        self.assertFalse(cert["open_ended_distinct_state_growth_possible"])

    def test_exhaustive_deterministic_maps_through_four_states(self):
        checked = 0
        for n in range(1, 5):
            states = tuple(str(i) for i in range(n))
            for images in itertools.product(states, repeat=n):
                transition = dict(zip(states, images))
                for start in states:
                    cert = mod.finite_state_cycle_certificate(transition, start)
                    self.assertLessEqual(cert["distinct_before_repeat"], n)
                    self.assertGreaterEqual(cert["cycle_length"], 1)
                    self.assertFalse(cert["open_ended_distinct_state_growth_possible"])
                    checked += 1
        self.assertEqual(1081, checked)


class ExhaustiveCostAndRegistryTests(unittest.TestCase):
    def test_small_expansion_cost_comparisons(self):
        checked = 0
        for horizon in range(1, 5):
            for current_loss in range(4):
                for expanded_loss in range(4):
                    for expansion_cost in range(4):
                        for maintenance in range(3):
                            result = mod.expansion_verdict(
                                horizon=horizon,
                                current_loss_per_task=current_loss,
                                expanded_loss_per_task=expanded_loss,
                                expansion_cost=expansion_cost,
                                expanded_maintenance_per_task=maintenance,
                            )
                            keep = horizon * current_loss
                            expand = expansion_cost + horizon * (expanded_loss + maintenance)
                            expected = mod.EXPAND if expand < keep else mod.KEEP if expand > keep else mod.TIE
                            self.assertEqual(expected, result["verdict"])
                            checked += 1
        self.assertEqual(768, checked)

    def test_registry_exact_six_rows(self):
        registry = json.loads((ROOT / "MORPHOGENESIS_LIMITS_V1.json").read_text())
        self.assertEqual(6, len(registry["rows"]))
        self.assertEqual("G2", registry["claim_ceiling"])
        for field in ("scope", "assumptions", "evidence_class", "strongest_parent", "negative_twin", "nearest_counterexample", "falsifier", "claim_boundary"):
            self.assertTrue(registry[field], field)
        for row in registry["rows"]:
            for field in ("ledger_row", "law", "strongest_parent", "negative_twin", "falsifier"):
                self.assertTrue(row[field], (row["id"], field))

    def test_boolean_numeric_smuggling_refused(self):
        with self.assertRaises(ValueError):
            mod.expansion_verdict(horizon=True, current_loss_per_task=1, expanded_loss_per_task=0, expansion_cost=0, expanded_maintenance_per_task=0)
        with self.assertRaises(ValueError):
            mod.generation_burden_trajectory(initial_burden=1, inherited_reduction=False, maintenance=0, generations=1)


if __name__ == "__main__":
    unittest.main()
