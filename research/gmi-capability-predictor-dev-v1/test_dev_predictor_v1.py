import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("dev_predictor_v1", ROOT / "dev_predictor_v1.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class ProtocolTests(unittest.TestCase):
    def test_claim_gate_metadata_complete(self):
        protocol = json.loads((ROOT / "DEV_PREDICTOR_PROTOCOL_V1.json").read_text())
        for field in (
            "scope",
            "assumptions",
            "evidence_class",
            "strongest_parent",
            "negative_twin",
            "nearest_counterexample",
            "falsifier",
            "claim_ceiling",
            "status",
        ):
            self.assertTrue(protocol[field], field)
        self.assertEqual("G2", protocol["claim_ceiling"])
        self.assertEqual(243, protocol["development_world_count"])
        self.assertEqual(set(mod.TARGETS), set(protocol["capability_targets"]))
        self.assertEqual(set(mod.FORBIDDEN_FIELDS), set(protocol["forbidden_fit_fields"]))


class DevelopmentCorpusTests(unittest.TestCase):
    def test_exact_registered_cube(self):
        worlds = mod.generate_development_worlds()
        self.assertEqual(243, len(worlds))
        self.assertEqual(243, len({tuple(w[a] for a in mod.AXES) for w in worlds}))

    def test_no_identity_or_held_fields_exist(self):
        for world in mod.generate_development_worlds():
            self.assertFalse(set(world).intersection(mod.FORBIDDEN_FIELDS))

    def test_forbidden_held_outcome_is_rejected(self):
        bad = dict(mod.generate_development_worlds()[0])
        bad["heldout_outcome"] = 1
        with self.assertRaises(ValueError):
            mod.MonotoneDevelopmentPredictor.fit([bad])

    def test_extra_architecture_identity_is_rejected(self):
        bad = dict(mod.generate_development_worlds()[0])
        bad["architecture_name"] = "opaque-family-id"
        with self.assertRaises(ValueError):
            mod.MonotoneDevelopmentPredictor.fit([bad])

    def test_non_integer_margin_is_rejected(self):
        bad = copy.deepcopy(mod.generate_development_worlds()[0])
        bad["memory_margin"] = "-1"
        with self.assertRaises(ValueError):
            mod.MonotoneDevelopmentPredictor.fit([bad])

    def test_non_monotone_mutation_is_rejected(self):
        worlds = copy.deepcopy(mod.generate_development_worlds())
        # The all-negative corner must have memory_exact=0. Flipping it to 1
        # conflicts with larger worlds that still have memory_margin=-1.
        worlds[0]["capabilities"]["memory_exact"] = 1
        with self.assertRaises(ValueError):
            mod.MonotoneDevelopmentPredictor.fit(worlds)


class PredictorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds = mod.generate_development_worlds()
        cls.predictor = mod.MonotoneDevelopmentPredictor.fit(cls.worlds)

    def test_replays_every_development_world_exactly(self):
        for world in self.worlds:
            point = {axis: world[axis] for axis in mod.AXES}
            self.assertEqual(world["capabilities"], self.predictor.predict_vector(point))

    def test_planning_requires_joint_memory_and_depth(self):
        point = {
            "memory_margin": 0,
            "planning_margin": 0,
            "communication_margin": -1,
            "routing_margin": -1,
            "verification_margin": -1,
        }
        self.assertEqual(1, self.predictor.predict_one(point, "planning_exact"))
        point["memory_margin"] = -1
        self.assertEqual(0, self.predictor.predict_one(point, "planning_exact"))

    def test_abstains_outside_identified_partial_order_region(self):
        point = {
            "memory_margin": 2,
            "planning_margin": -2,
            "communication_margin": 0,
            "routing_margin": 0,
            "verification_margin": 0,
        }
        self.assertEqual(
            mod.CANNOT_IDENTIFY,
            self.predictor.predict_one(point, "planning_exact"),
        )

    def test_identifiable_extrapolation_is_allowed_only_by_monotonicity(self):
        high = {axis: 3 for axis in mod.AXES}
        low = {axis: -3 for axis in mod.AXES}
        self.assertEqual({target: 1 for target in mod.TARGETS}, self.predictor.predict_vector(high))
        self.assertEqual({target: 0 for target in mod.TARGETS}, self.predictor.predict_vector(low))

    def test_unknown_target_rejected(self):
        point = {axis: 0 for axis in mod.AXES}
        with self.assertRaises(ValueError):
            self.predictor.predict_one(point, "family_score")


if __name__ == "__main__":
    unittest.main()
