from __future__ import annotations

import importlib.util
import itertools
import json
import pathlib
import unittest
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("development_spine_v1", ROOT / "development_spine_v1.py")
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load development spine")
SPEC.loader.exec_module(mod)


class DefinitionTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "reset": (("goal_a", 5), ("goal_b", 6)),
            "learned": (("goal_a", 1), ("goal_b", 2)),
            "goal_a": (),
            "goal_b": (),
        }

    def test_current_capability_separate_from_learning_potential(self):
        current_reset = {"now_1": True, "now_2": False}
        current_learned = {"now_1": True, "now_2": False}
        self.assertEqual(Fraction(1, 2), mod.current_capability(current_reset))
        self.assertEqual(mod.current_capability(current_reset), mod.current_capability(current_learned))
        future = {"A": {"goal_a"}, "B": {"goal_b"}}
        self.assertEqual(Fraction(0, 1), mod.learning_potential(self.graph, "reset", future, budget=2))
        self.assertEqual(Fraction(1, 1), mod.learning_potential(self.graph, "learned", future, budget=2))

    def test_adaptation_and_morphology_search_burden(self):
        self.assertEqual(5, mod.adaptation_burden(self.graph, "reset", {"goal_a"}))
        self.assertEqual(1, mod.adaptation_burden(self.graph, "learned", {"goal_a"}))
        self.assertEqual(2, mod.morphology_search_burden(self.graph, "learned", {"goal_b"}))

    def test_useful_descendant_mass_counts_states_not_paths(self):
        weights = {"goal_a": 2, "goal_b": 3}
        self.assertEqual(0, mod.useful_descendant_mass(self.graph, "reset", weights, budget=2))
        self.assertEqual(5, mod.useful_descendant_mass(self.graph, "learned", weights, budget=2))

    def test_transfer_sign_and_harmful_transfer(self):
        self.assertEqual(4, mod.transfer_benefit(self.graph, reset_state="reset", continued_state="learned", satisfying_states={"goal_a"}))
        self.assertFalse(mod.harmful_transfer(self.graph, reset_state="reset", continued_state="learned", satisfying_states={"goal_a"}))
        self.assertEqual(-4, mod.transfer_benefit(self.graph, reset_state="learned", continued_state="reset", satisfying_states={"goal_a"}))
        self.assertTrue(mod.harmful_transfer(self.graph, reset_state="learned", continued_state="reset", satisfying_states={"goal_a"}))

    def test_path_dependence_requires_present_equivalence_and_future_difference(self):
        outputs = {"current_task": "same"}
        self.assertTrue(mod.developmental_path_dependence(self.graph, "reset", "learned", outputs, dict(outputs), [{"goal_a"}, {"goal_b"}]))
        self.assertFalse(mod.developmental_path_dependence(self.graph, "reset", "learned", outputs, {"current_task": "different"}, [{"goal_a"}]))


class OptionalInheritanceTests(unittest.TestCase):
    def test_constructive_optional_inheritance_witness(self):
        base = {
            "s": (("a", 3),),
            "a": (("b", 3),),
            "b": (),
        }
        inherited = {
            "s": (("a", 3), ("a", 1), ("b", 2)),
            "a": (("b", 3), ("b", 1)),
            "b": (),
        }
        result = mod.optional_inheritance_monotonicity(
            base,
            inherited,
            start="s",
            target_sets=[{"a"}, {"b"}],
            useful_weights={"a": 1, "b": 2},
            budget=2,
        )
        self.assertTrue(result["burden_nonincreasing"])
        self.assertTrue(result["useful_mass_nondecreasing"])
        self.assertEqual((3, 6), result["base_burdens"])
        self.assertEqual((1, 2), result["inherited_burdens"])
        self.assertEqual(0, result["base_useful_mass"])
        self.assertEqual(3, result["inherited_useful_mass"])

    def test_exhaustive_three_state_free_option_extensions(self):
        states = ("s", "a", "b")
        edges = tuple((u, v) for u in states for v in states if u != v)
        # Each potential unit-cost edge is absent, extension-only, or present
        # in both base and extension. That exhausts 3^6 = 729 legal relations.
        checked = 0
        for marks in itertools.product((0, 1, 2), repeat=len(edges)):
            base = {state: [] for state in states}
            extended = {state: [] for state in states}
            for mark, (u, v) in zip(marks, edges):
                if mark == 2:
                    base[u].append((v, 1))
                    extended[u].append((v, 1))
                elif mark == 1:
                    extended[u].append((v, 1))
            base = {k: tuple(v) for k, v in base.items()}
            extended = {k: tuple(v) for k, v in extended.items()}
            self.assertTrue(mod.graph_extends_without_repricing(base, extended))
            old = mod.shortest_costs(base, "s")
            new = mod.shortest_costs(extended, "s")
            for state in states:
                self.assertLessEqual(new.get(state, float("inf")), old.get(state, float("inf")))
            checked += 1
        self.assertEqual(729, checked)

    def test_mandatory_maintenance_counterexample_is_outside_theorem_scope(self):
        base = {"s": (("g", 1),), "g": ()}
        mandatory_cost = {"s": (("g", 3),), "g": ()}
        self.assertFalse(mod.graph_extends_without_repricing(base, mandatory_cost))
        self.assertEqual(1, mod.adaptation_burden(base, "s", {"g"}))
        self.assertEqual(3, mod.adaptation_burden(mandatory_cost, "s", {"g"}))
        with self.assertRaises(ValueError):
            mod.optional_inheritance_monotonicity(
                base,
                mandatory_cost,
                start="s",
                target_sets=[{"g"}],
                useful_weights={"g": 1},
                budget=3,
            )


class RegistryAndHostileTests(unittest.TestCase):
    def test_registry_exact_rows_and_claim_gate(self):
        registry = json.loads((ROOT / "DEVELOPMENT_SPINE_V1.json").read_text())
        self.assertEqual(7, len(registry["rows"]))
        self.assertEqual("G2", registry["claim_ceiling"])
        for field in ("scope", "assumptions", "evidence_class", "strongest_parent", "negative_twin", "nearest_counterexample", "falsifier", "claim_boundary"):
            self.assertTrue(registry[field], field)
        for row in registry["rows"]:
            for field in ("ledger_row", "definition", "strongest_parent", "negative_twin", "falsifier"):
                self.assertTrue(row[field], (row["id"], field))

    def test_boolean_and_negative_costs_refused(self):
        with self.assertRaises(ValueError):
            mod.shortest_costs({"s": (("g", True),), "g": ()}, "s")
        with self.assertRaises(ValueError):
            mod.shortest_costs({"s": (("g", -1),), "g": ()}, "s")
        with self.assertRaises(ValueError):
            mod.learning_potential({"s": ()}, "s", {"x": {"s"}}, budget=True)


if __name__ == "__main__":
    unittest.main()
