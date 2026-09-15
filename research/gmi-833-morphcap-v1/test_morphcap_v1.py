#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("morphcap_v1", HERE / "morphcap_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)


class MorphCapV1Tests(unittest.TestCase):
    def test_receipt_green(self):
        r = mod.build_receipt()
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))

    def test_receipt_byte_reproduction(self):
        expected = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(mod.build_receipt(), expected)
        self.assertEqual(mod.canonical_json(expected), (HERE / "RESULT_V1.json").read_text())

    def test_state_renaming_and_label_order_are_morphology_invariant(self):
        base, renamed, _, _, _ = mod.witness_machines()
        self.assertNotEqual(tuple(base["actions"]), tuple(renamed["actions"]))
        self.assertTrue(mod.morphology_equivalent(base, renamed))
        self.assertEqual(mod.canonical_mechanism(base), mod.canonical_mechanism(renamed))

    def test_equivalence_relation_controls(self):
        base, renamed, renamed2, _, _ = mod.witness_machines()
        self.assertTrue(mod.morphology_equivalent(base, base))
        self.assertTrue(mod.morphology_equivalent(base, renamed))
        self.assertTrue(mod.morphology_equivalent(renamed, base))
        self.assertTrue(mod.morphology_equivalent(renamed, renamed2))
        self.assertTrue(mod.morphology_equivalent(base, renamed2))

    def test_behavior_only_is_too_weak(self):
        base, _, _, resource_twin, intervention_twin = mod.witness_machines()
        words = ((), ("flip",), ("stay",), ("flip", "flip"), ("stay", "flip"))
        self.assertTrue(all(mod.run_word(base, w) == mod.run_word(resource_twin, w) for w in words))
        self.assertFalse(mod.morphology_equivalent(base, resource_twin))
        self.assertFalse(mod.morphology_equivalent(base, intervention_twin))

    def test_unreachable_registered_junk_is_rejected(self):
        base, _, _, _, _ = mod.witness_machines()
        junk = dict(base)
        junk["states"] = ("A", "B", "J")
        junk["output"] = dict(base["output"], J=0)
        junk["transition"] = dict(base["transition"])
        junk["transition"].update({("J", "flip"): "J", ("J", "stay"): "J"})
        junk["intervention_response"] = dict(base["intervention_response"])
        junk["intervention_response"][("J", "probe")] = 0
        junk["development_edges"] = set(base["development_edges"])
        with self.assertRaisesRegex(ValueError, "only reachable registered states"):
            mod.canonical_mechanism(junk)

    def test_incomplete_transition_contract_is_rejected(self):
        base, _, _, _, _ = mod.witness_machines()
        malformed = dict(base)
        malformed["transition"] = dict(base["transition"])
        del malformed["transition"][("A", "stay")]
        with self.assertRaisesRegex(ValueError, "transition relation must be total"):
            mod.canonical_mechanism(malformed)

    def test_equivalent_capability_regions_match(self):
        base, renamed, _, resource_twin, _ = mod.witness_machines()
        contracts = mod.witness_contracts()
        self.assertEqual(mod.capability_region(base, contracts), mod.capability_region(renamed, contracts))
        self.assertNotEqual(mod.capability_region(base, contracts), mod.capability_region(resource_twin, contracts))

    def test_capability_has_no_architecture_label_input(self):
        base, _, _, _, _ = mod.witness_machines()
        contract = mod.witness_contracts()[0]
        self.assertEqual(mod.capability_value(base, contract), Fraction(1))
        self.assertNotIn("architecture", contract)
        self.assertNotIn("family", contract)

    def test_budget_relaxation_ceiling_monotone(self):
        w = mod.capability_monotonicity_witness()
        self.assertEqual(w["ceilings"], (Fraction(1,4), Fraction(3,4), Fraction(1)))
        self.assertLessEqual(w["ceilings"][0], w["ceilings"][1])
        self.assertLessEqual(w["ceilings"][1], w["ceilings"][2])

    def test_class_relaxation_ceiling_monotone(self):
        w = mod.capability_monotonicity_witness()
        self.assertEqual(w["class_ceiling_small"], Fraction(3,4))
        self.assertEqual(w["class_ceiling_large"], Fraction(1))
        self.assertLessEqual(w["class_ceiling_small"], w["class_ceiling_large"])

    def test_hidden_information_ceiling_is_exact_half(self):
        grid = [Fraction(k,32) for k in range(33)]
        self.assertEqual({mod.hidden_world_score(p) for p in grid}, {Fraction(1,2)})
        with self.assertRaises(ValueError):
            mod.hidden_world_score(Fraction(33, 32))

    def test_revealed_information_positive_twin_reaches_one(self):
        self.assertEqual(mod.revealed_world_score(Fraction(0), Fraction(1)), Fraction(1))
        w = mod.information_ceiling_witness()
        self.assertEqual(w["revealed_ceiling"], Fraction(1))
        self.assertEqual(w["grid_points_revealed"], 1089)

    def test_empty_feasible_class_has_no_fabricated_ceiling(self):
        c = ({"score": Fraction(1), "resources": (2,2)},)
        self.assertIsNone(mod.finite_ceiling(c, (1,1)))

    def test_negative_task_weight_is_rejected(self):
        base, _, _, _, _ = mod.witness_machines()
        bad = {
            "tasks": ({"word": (), "target": 0, "weight": -1},),
            "budget": (3, 2),
            "threshold": 0,
        }
        with self.assertRaisesRegex(ValueError, "weights must be nonnegative"):
            mod.capability_value(base, bad)

    def test_claim_ceiling_stays_bounded(self):
        r = mod.build_receipt()
        self.assertEqual(r["claim_ceiling"], "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE")
        self.assertIn("ALL_CAPABILITY_CEILINGS_REPROVED", r["forbidden_promotions"])
        self.assertIn("COMPLETE_GMI", r["forbidden_promotions"])

    def test_no_floats_in_receipt(self):
        def walk(x):
            if isinstance(x, float): self.fail("float found in exact receipt")
            if isinstance(x, dict):
                for v in x.values(): walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(mod.build_receipt())


if __name__ == "__main__":
    unittest.main()
