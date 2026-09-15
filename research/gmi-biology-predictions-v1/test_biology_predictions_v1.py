"""
Tests for GMI Biology Predictions V1

15+ tests covering morphology prediction, negative twins, and developmental ordering.
All tests use Python 3.8 compatible syntax, unittest, no network.
"""
import sys
import os
import unittest

# -I safety: import via spec
_dir = os.path.dirname(os.path.abspath(__file__))
_spec = __import__('importlib').util.spec_from_file_location(
    "biology_predictions_v1",
    os.path.join(_dir, "biology_predictions_v1.py"))
_mod = __import__('importlib').util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

SpeciesParams = _mod.SpeciesParams
Morphology = _mod.Morphology
predict_morphology = _mod.predict_morphology
predict_morphology_with_burden = _mod.predict_morphology_with_burden
negative_twin = _mod.negative_twin
predict_developmental_trajectory = _mod.predict_developmental_trajectory
DevelopmentalStage = _mod.DevelopmentalStage

CORVID = _mod.CORVID
CEPHALOPOD = _mod.CEPHALOPOD
RODENT = _mod.RODENT
PRIMATE = _mod.PRIMATE
HUMAN_DEVELOPMENT = _mod.HUMAN_DEVELOPMENT
HUMAN_E = _mod.HUMAN_E


class TestSpeciesParams(unittest.TestCase):
    """SpeciesParams validation tests."""

    def test_valid_construction(self):
        sp = SpeciesParams(E=5.0, R=5.0, V=5.0, name="test")
        self.assertEqual(sp.E, 5.0)
        self.assertEqual(sp.R, 5.0)
        self.assertEqual(sp.V, 5.0)
        self.assertEqual(sp.name, "test")

    def test_default_name(self):
        sp = SpeciesParams(E=1.0, R=2.0, V=3.0)
        self.assertEqual(sp.name, "unknown")

    def test_extreme_values(self):
        sp_lo = SpeciesParams(E=0.0, R=0.0, V=0.0)
        sp_hi = SpeciesParams(E=100.0, R=100.0, V=100.0)
        self.assertEqual(sp_lo.E, 0.0)
        self.assertEqual(sp_hi.E, 100.0)


class TestMorphologyPrediction(unittest.TestCase):
    """Core morphology prediction tests."""

    def test_corvid_prediction(self):
        winner = predict_morphology(CORVID)
        self.assertIn(winner, ("neural", "symbolic", "probabilistic"))

    def test_cephalopod_prediction(self):
        winner = predict_morphology(CEPHALOPOD)
        self.assertIn(winner, ("neural", "symbolic", "probabilistic"))

    def test_rodent_prediction(self):
        winner = predict_morphology(RODENT)
        self.assertIn(winner, ("neural", "symbolic", "probabilistic"))

    def test_primate_prediction(self):
        winner = predict_morphology(PRIMATE)
        self.assertIn(winner, ("neural", "symbolic", "probabilistic"))

    def test_prediction_with_burden(self):
        winner, burdens = predict_morphology_with_burden(PRIMATE)
        self.assertIn(winner, burdens)
        self.assertEqual(winner, min(burdens, key=burdens.get))

    def test_all_burdens_positive(self):
        _, burdens = predict_morphology_with_burden(CORVID)
        for name, b in burdens.items():
            self.assertGreater(b, 0.0, f"Burden for {name} should be positive")


class TestNegativeTwins(unittest.TestCase):
    """Negative twin construction tests."""

    def test_negative_twin_returns_different_morphology(self):
        predicted = predict_morphology(CORVID)
        twin = negative_twin(CORVID, predicted)
        if twin is not None:
            twin_winner = predict_morphology(twin)
            self.assertNotEqual(predicted, twin_winner)

    def test_negative_twin_params_valid(self):
        predicted = predict_morphology(RODENT)
        twin = negative_twin(RODENT, predicted)
        if twin is not None:
            self.assertGreaterEqual(twin.E, 0.0)
            self.assertGreaterEqual(twin.R, 0.0)
            self.assertGreaterEqual(twin.V, 0.0)
            self.assertLessEqual(twin.E, 10.0)
            self.assertLessEqual(twin.R, 10.0)
            self.assertLessEqual(twin.V, 10.0)


class TestDevelopmentalOrdering(unittest.TestCase):
    """Developmental ordering tests."""

    def test_human_development_trajectory(self):
        trajectory = predict_developmental_trajectory(HUMAN_DEVELOPMENT, HUMAN_E)
        self.assertEqual(len(trajectory), 3)
        self.assertEqual(trajectory[0].name, "infant")
        self.assertEqual(trajectory[1].name, "child")
        self.assertEqual(trajectory[2].name, "adult")

    def test_trajectory_stages_have_morphologies(self):
        trajectory = predict_developmental_trajectory(HUMAN_DEVELOPMENT, HUMAN_E)
        for stage in trajectory:
            self.assertIn(stage.predicted_morphology, ("neural", "symbolic", "probabilistic"))

    def test_trajectory_resource_increase(self):
        trajectory = predict_developmental_trajectory(HUMAN_DEVELOPMENT, HUMAN_E)
        r_values = [s.R for s in trajectory]
        self.assertEqual(r_values, sorted(r_values))


class TestEdgeCases(unittest.TestCase):
    """Edge case tests."""

    def test_zero_resources(self):
        sp = SpeciesParams(E=5.0, R=0.0, V=5.0, name="zero_r")
        winner = predict_morphology(sp)
        self.assertIn(winner, ("neural", "symbolic", "probabilistic"))

    def test_high_verifier_pressure(self):
        sp = SpeciesParams(E=5.0, R=5.0, V=100.0, name="high_v")
        winner = predict_morphology(sp)
        self.assertIn(winner, ("neural", "symbolic", "probabilistic"))

    def test_consistent_predictions(self):
        winner1 = predict_morphology(PRIMATE)
        winner2 = predict_morphology(PRIMATE)
        self.assertEqual(winner1, winner2)


if __name__ == "__main__":
    unittest.main()
