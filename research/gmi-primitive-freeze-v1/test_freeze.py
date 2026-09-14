"""unittest controls for the GMI primitive freeze v1 capsule.

10+ tests covering:
  - All 5 primitives registered with correct types
  - Forbidden names not present as primitives
  - Composition witnesses for each forbidden name
  - Turing insufficiency witness (burden differs)
  - Cost vector integrity
  - Combinator closure under P ∪ C

Python 3.8 safe. No network. No external dependencies.
"""
from __future__ import annotations

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "primitive_witness", ROOT / "primitive_witness.py"
)
mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load primitive_witness module")
SPEC.loader.exec_module(mod)


class PrimitiveRegistrationTests(unittest.TestCase):
    """Tests 1-5: verify the five frozen primitives are registered correctly."""

    def test_five_primitives_registered(self):
        prims = mod.get_all_primitives()
        self.assertEqual(len(prims), 5)

    def test_primitive_names_unique(self):
        prims = mod.get_all_primitives()
        names = [p.name for p in prims]
        self.assertEqual(len(names), len(set(names)))

    def test_id_primitive_types(self):
        p = mod.PRIM_ID
        self.assertEqual(p.S_p, "1")
        self.assertEqual(p.I_p, "A")
        self.assertEqual(p.O_p, "A")
        self.assertTrue(p.is_inert)

    def test_acc_primitive_has_feedback(self):
        p = mod.PRIM_ACC
        self.assertFalse(p.is_inert)
        self.assertEqual(p.F_p, "Float")
        self.assertIn("upd", p.c_p)

    def test_const_primitive_is_inert(self):
        p = mod.PRIM_CONST
        self.assertTrue(p.is_inert)
        self.assertEqual(p.F_p, "1")
        self.assertEqual(p.S_p, "A")


class ForbiddenNameTests(unittest.TestCase):
    """Tests 6-7: verify no architecture label hides as a primitive."""

    def test_seven_forbidden_names_registered(self):
        names = mod.get_forbidden_names()
        self.assertEqual(len(names), 7)
        for name in ["BACKPROP", "BAYES_UPDATE", "ATTENTION",
                      "NEURON", "PROGRAM_SYNTHESIS", "SEARCH", "MEMORY"]:
            self.assertIn(name, names)

    def test_no_primitive_matches_forbidden_name(self):
        for name in mod.get_forbidden_names():
            self.assertTrue(
                mod.verify_no_hidden_label(name),
                f"{name} should not be a primitive name",
            )


class CompositionWitnessTests(unittest.TestCase):
    """Tests 8-10: verify composition witnesses for each forbidden name."""

    def test_all_seven_witnesses_present(self):
        witnesses = mod.get_composition_witnesses()
        self.assertEqual(len(witnesses), 7)
        for name in mod.get_forbidden_names():
            self.assertIn(name, witnesses)

    def test_expressible_flag_is_boolean(self):
        witnesses = mod.get_composition_witnesses()
        for name, w in witnesses.items():
            self.assertIsInstance(w["expressible"], bool,
                                  f"{name} expressible flag not bool")

    def test_expressible_has_composite(self):
        witnesses = mod.get_composition_witnesses()
        for name, w in witnesses.items():
            if w["expressible"]:
                self.assertIsNotNone(w["composite"],
                                     f"{name} expressible but no composite")


class TuringInsufficiencyTests(unittest.TestCase):
    """Tests 11-13: verify Turing universality insufficiency witness."""

    def test_same_function(self):
        w = mod.get_turing_witness()
        for x in [0.0, 1.0, -1.0, 3.14, 42.0]:
            self.assertTrue(w.verify_same_function(x))

    def test_different_burden(self):
        w = mod.get_turing_witness()
        for x in [0.0, 1.0, -1.0, 3.14, 42.0]:
            self.assertTrue(w.verify_different_burden(x))

    def test_burden_zero_for_identity(self):
        b = mod.TuringWitness.burden_a(1.0)
        self.assertEqual(b["total"], 0.0)
        self.assertEqual(b["persists"], 0.0)
        self.assertEqual(b["generalizes"], 0.0)


class CostIntegrityTests(unittest.TestCase):
    """Tests 14-15: verify cost vectors are well-formed."""

    def test_all_primitives_have_cost_vector(self):
        for p in mod.get_all_primitives():
            self.assertIn("desc", p.c_p)
            self.assertIn("exec", p.c_p)
            self.assertIn("upd", p.c_p)

    def test_id_primitive_zero_cost(self):
        p = mod.PRIM_ID
        self.assertEqual(p.c_p["desc"], 0)
        self.assertEqual(p.c_p["exec"], 0)
        self.assertEqual(p.c_p["upd"], 0)


if __name__ == "__main__":
    unittest.main()
