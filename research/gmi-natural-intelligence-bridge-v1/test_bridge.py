"""Test suite for Natural Intelligence Bridge Theorem V1 (items #36/#37).

28 tests total: clean bijection, held-out prediction, negative twins,
prediction edge cases, and legacy mapping-consistency.
All pass under python3 -I -B.
"""
import importlib.util
import os
import sys
import unittest


def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError("Could not load spec for %s" % module_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


bridge = load_module_from_path(
    "bridge_witness",
    os.path.join(os.path.dirname(__file__), "bridge_witness.py"),
)


# ======================================================================
# Clean Bijection Tests (6 tests)
# ======================================================================

class TestCleanBijection(unittest.TestCase):
    def test_bijection_holds(self):
        result = bridge.verify_clean_bijection()
        self.assertTrue(result["is_bijection"],
                        "Violations: %s" % result["violations"])

    def test_all_six_pressures_mapped(self):
        result = bridge.verify_clean_bijection()
        self.assertEqual(len(result["pressure_to_category"]), 6)

    def test_all_six_categories_claimed(self):
        result = bridge.verify_clean_bijection()
        self.assertEqual(len(result["category_to_pressure"]), 6)

    def test_no_violations(self):
        result = bridge.verify_clean_bijection()
        self.assertEqual(result["violations"], [])

    def test_pressure_bearing_count(self):
        result = bridge.verify_clean_bijection()
        self.assertEqual(result["pressure_bearing_count"], 6)
        self.assertEqual(result["total_a3_categories"], 602)

    def test_specific_pairs(self):
        result = bridge.verify_clean_bijection()
        p2c = result["pressure_to_category"]
        self.assertEqual(p2c[bridge.P_CONSISTENCY], "A3-042")
        self.assertEqual(p2c[bridge.P_CONTENT], "A3-187")
        self.assertEqual(p2c[bridge.P_TRIVIALITY], "A3-301")
        self.assertEqual(p2c[bridge.P_STRUCTURE], "A3-419")
        self.assertEqual(p2c[bridge.P_RECURSION], "A3-528")
        self.assertEqual(p2c[bridge.P_CONTEXT], "A3-601")


# ======================================================================
# Held-Out Prediction Tests (5 tests)
# ======================================================================

class TestHeldOutPrediction(unittest.TestCase):
    def test_accuracy_exceeds_threshold(self):
        acc = bridge.compute_prediction_accuracy(bridge.HELD_OUT_TASKS)
        self.assertGreater(acc, 0.85,
                           "Accuracy %.1f%% <= 85%%" % (acc * 100))

    def test_enough_held_out_tasks(self):
        self.assertGreaterEqual(len(bridge.HELD_OUT_TASKS), 10)

    def test_all_predictions_valid(self):
        valid = set(bridge.MORPHOLOGY_NAMES)
        for profile, expected in bridge.HELD_OUT_TASKS:
            pred = bridge.predict_morphology(profile)
            self.assertIn(pred, valid)

    def test_all_expected_valid(self):
        valid = set(bridge.MORPHOLOGY_NAMES)
        for profile, expected in bridge.HELD_OUT_TASKS:
            self.assertIn(expected, valid)

    def test_deterministic(self):
        for profile, expected in bridge.HELD_OUT_TASKS:
            self.assertEqual(
                bridge.predict_morphology(profile),
                bridge.predict_morphology(profile))


# ======================================================================
# Negative Twin Tests (3 tests)
# ======================================================================

class TestNegativeTwins(unittest.TestCase):
    def test_one_twin_per_morphology(self):
        morphs = {t.morphology for t in bridge.NEGATIVE_TWINS}
        for m in bridge.MORPHOLOGY_NAMES:
            self.assertIn(m, morphs)

    def test_wins_predicted_correctly(self):
        for twin in bridge.NEGATIVE_TWINS:
            pred = bridge.predict_morphology(twin.wins_profile)
            self.assertEqual(pred, twin.morphology,
                             "Wins task for %s predicted %s" %
                             (twin.morphology, pred))

    def test_loses_predicted_differently(self):
        for twin in bridge.NEGATIVE_TWINS:
            pred = bridge.predict_morphology(twin.loses_profile)
            self.assertNotEqual(pred, twin.morphology,
                                "Loses task for %s also predicted %s" %
                                (twin.morphology, pred))


# ======================================================================
# Morphology Prediction Edge Cases (4 tests)
# ======================================================================

class TestPredictionEdgeCases(unittest.TestCase):
    def test_high_consistency_recursion_gives_symbolic(self):
        p = bridge._pp(c=1.0, r=1.0)
        self.assertEqual(bridge.predict_morphology(p), "symbolic")

    def test_high_content_context_gives_neural(self):
        p = bridge._pp(co=1.0, cx=1.0)
        self.assertEqual(bridge.predict_morphology(p), "neural")

    def test_high_structure_gives_probabilistic(self):
        p = bridge._pp(s=1.0)
        self.assertEqual(bridge.predict_morphology(p), "probabilistic")

    def test_all_zeros_gives_neural(self):
        p = bridge._pp()
        self.assertEqual(bridge.predict_morphology(p), "neural")


# ======================================================================
# Legacy Mapping Tests (6 tests)
# ======================================================================

class TestMappingConsistency(unittest.TestCase):
    def test_valid_consistent(self):
        self.assertTrue(bridge.verify_mapping_consistency(
            bridge.ALL_MORPHOLOGIES, bridge.ALL_ECOLOGIES,
            bridge.build_valid_mapping()))

    def test_inconsistent_fails(self):
        self.assertFalse(bridge.verify_mapping_consistency(
            bridge.ALL_MORPHOLOGIES, bridge.ALL_ECOLOGIES,
            bridge.build_inconsistent_mapping()))


class TestMappingContent(unittest.TestCase):
    def test_valid_has_content(self):
        self.assertTrue(bridge.verify_mapping_content(
            bridge.ALL_MORPHOLOGIES, bridge.ALL_ECOLOGIES,
            bridge.build_valid_mapping()))

    def test_trivial_fails_content(self):
        self.assertFalse(bridge.verify_mapping_content(
            bridge.ALL_MORPHOLOGIES, bridge.ALL_ECOLOGIES,
            bridge.build_trivial_mapping()))


class TestMappingNonTrivial(unittest.TestCase):
    def test_valid_non_trivial(self):
        self.assertTrue(bridge.verify_mapping_trivial(
            bridge.build_valid_mapping()))

    def test_trivial_fails(self):
        self.assertFalse(bridge.verify_mapping_trivial(
            bridge.build_trivial_mapping()))


class TestPVR3Legacy(unittest.TestCase):
    def test_valid_pairs(self):
        self.assertTrue(bridge.pvr3_satisfied(
            bridge.MORPH_ALPHA, bridge.ECO_SOCIAL))
        self.assertTrue(bridge.pvr3_satisfied(
            bridge.MORPH_GAMMA, bridge.ECO_PREDATOR))

    def test_invalid_pairs(self):
        self.assertFalse(bridge.pvr3_satisfied(
            bridge.MORPH_ALPHA, bridge.ECO_PREDATOR))
        self.assertFalse(bridge.pvr3_satisfied(
            bridge.MORPH_GAMMA, bridge.ECO_SOCIAL))


class TestScopeG2(unittest.TestCase):
    def test_g2_documented(self):
        path = os.path.join(os.path.dirname(__file__),
                            "BRIDGE_THEOREM_V1.md")
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            self.assertIn("G2", content)
            self.assertIn("Ceiling", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
