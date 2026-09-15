"""
test_phase_rv.py — 23+ unittest controls for morphology R/V phase law.

Tests phase boundary correctness, held-out prediction accuracy, negative twins,
and independent R/V axis effects. Python 3.8 safe, unittest, no network.
"""

import os
import sys
import unittest

# Import phase_rv_witness from sibling file using importlib (lane convention)
_SPEC = None
_MOD = None


def _import_witness():
    """Import phase_rv_witness.py using importlib.util.spec_from_loader."""
    global _SPEC, _MOD
    if _MOD is not None:
        return _MOD
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "phase_rv_witness.py")
    import importlib.util
    _SPEC = importlib.util.spec_from_file_location("phase_rv_witness", path)
    _MOD = importlib.util.module_from_spec(_SPEC)
    _SPEC.loader.exec_module(_MOD)
    return _MOD


class TestPhaseRVRegistration(unittest.TestCase):
    """Control 1: archetypes register and have distinct names."""

    def test_three_archetypes_registered(self):
        witness = _import_witness()
        morphs = witness.register_archetypes()
        self.assertEqual(len(morphs), 3)
        names = [m.name for m in morphs]
        self.assertEqual(len(set(names)), 3)

    def test_archetype_names(self):
        witness = _import_witness()
        morphs = witness.register_archetypes()
        names = {m.name for m in morphs}
        self.assertIn("neural", names)
        self.assertIn("symbolic", names)
        self.assertIn("probabilistic", names)


class TestPhaseBoundaryCorrectness(unittest.TestCase):
    """Control 2: phase boundaries occur where theory predicts."""

    def test_neural_wins_high_R_high_V(self):
        """At high R and high V, neural wins (ecology alignment dominates)."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[60.0], V_values=[0.8], N=100, H=50.0
        )
        self.assertEqual(grid[0][0], "neural")

    def test_symbolic_wins_low_R_low_V(self):
        """At low R and low V, symbolic wins (low build cost dominates)."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[2.0], V_values=[0.1], N=100, H=50.0
        )
        self.assertEqual(grid[0][0], "symbolic")

    def test_probabilistic_wins_mid_R_mid_V(self):
        """At moderate R and moderate V, probabilistic wins."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[20.0], V_values=[0.6], N=100, H=50.0
        )
        self.assertEqual(grid[0][0], "probabilistic")


class TestHeldOutPrediction(unittest.TestCase):
    """Control 3: held-out prediction accuracy > 90%."""

    def test_prediction_accuracy_above_90_percent(self):
        witness = _import_witness()
        morphs = witness.register_archetypes()
        R_values = [2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 60.0]
        V_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        result = witness.held_out_prediction(
            morphs, R_values, V_values, fraction_held=0.25, seed=42
        )
        self.assertGreaterEqual(result["prediction_accuracy"], 0.90,
            f"Prediction accuracy {result['prediction_accuracy']:.4f} < 0.90")

    def test_no_held_mismatches(self):
        """With frozen archetypes on a small world, all held cells should match."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        R_values = [2.0, 5.0, 10.0, 20.0, 30.0, 60.0]
        V_values = [0.2, 0.4, 0.6, 0.8]
        result = witness.held_out_prediction(
            morphs, R_values, V_values, fraction_held=0.25, seed=42
        )
        mismatches = [h for h in result["held_results"] if not h["match"]]
        self.assertEqual(len(mismatches), 0,
            f"Mismatches at: {[{'R': h['R'], 'V': h['V']} for h in mismatches]}")


class TestNegativeTwins(unittest.TestCase):
    """Control 4: verify morphologies LOSE where predicted."""

    def test_symbolic_loses_at_high_R_high_V(self):
        """Symbolic should NOT win at high R, high V."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[60.0], V_values=[0.8], N=100, H=50.0
        )
        self.assertNotEqual(grid[0][0], "symbolic")

    def test_neural_loses_at_low_R_low_V(self):
        """Neural should NOT win at low R, low V."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[2.0], V_values=[0.1], N=100, H=50.0
        )
        self.assertNotEqual(grid[0][0], "neural")

    def test_neural_loses_at_low_R_high_V(self):
        """At low R and high V, neural loses (resource pressure dominates)."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[2.0], V_values=[0.8], N=100, H=50.0
        )
        self.assertNotEqual(grid[0][0], "neural")

    def test_symbolic_loses_at_high_R_mid_V(self):
        """At high R and mid V, symbolic loses."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[60.0], V_values=[0.5], N=100, H=50.0
        )
        self.assertNotEqual(grid[0][0], "symbolic")


class TestRAxisIndependence(unittest.TestCase):
    """Control 5: R axis independently affects the winner (not just E)."""

    def test_increasing_R_shifts_winner(self):
        """As R increases at mid V, the winner should change."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        V_fixed = 0.7
        low_grid = witness.compute_phase_grid(
            morphs, R_values=[2.0], V_values=[V_fixed], N=100, H=50.0
        )
        high_grid = witness.compute_phase_grid(
            morphs, R_values=[60.0], V_values=[V_fixed], N=100, H=50.0
        )
        self.assertNotEqual(low_grid[0][0], high_grid[0][0],
            "R axis has no effect on winner — theory predicts R matters")

    def test_R_increasing_favors_neural(self):
        """As R increases at high V, neural should appear."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        V_fixed = 0.8
        winners = []
        for R in [2.0, 5.0, 10.0, 20.0, 40.0, 60.0]:
            grid = witness.compute_phase_grid(
                morphs, R_values=[R], V_values=[V_fixed], N=100, H=50.0
            )
            winners.append(grid[0][0])
        self.assertIn("neural", winners[-3:],
            f"Neural never appears as R increases: {winners}")


class TestVAxisIndependence(unittest.TestCase):
    """Control 6: V axis independently affects the winner (not just E)."""

    def test_increasing_V_shifts_winner(self):
        """As V increases at mid R, the winner should change."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        R_fixed = 20.0
        low_grid = witness.compute_phase_grid(
            morphs, R_values=[R_fixed], V_values=[0.2], N=100, H=50.0
        )
        high_grid = witness.compute_phase_grid(
            morphs, R_values=[R_fixed], V_values=[0.8], N=100, H=50.0
        )
        self.assertNotEqual(low_grid[0][0], high_grid[0][0],
            "V axis has no effect on winner — theory predicts V matters")

    def test_V_increasing_transitions_symbolic_to_neural(self):
        """As V increases at high R, winner should go symbolic -> prob -> neural."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        R_fixed = 40.0
        winners = []
        for V in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            grid = witness.compute_phase_grid(
                morphs, R_values=[R_fixed], V_values=[V], N=100, H=50.0
            )
            winners.append(grid[0][0])
        # Should see all three morphologies across the V range
        unique = set(winners)
        self.assertEqual(len(unique), 3,
            f"Expected 3 winners across V range, got {len(unique)}: {winners}")


class TestPhaseTransitions(unittest.TestCase):
    """Control 7: phase boundaries produce actual transitions."""

    def test_transitions_exist(self):
        witness = _import_witness()
        morphs = witness.register_archetypes()
        R_values = [2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 60.0]
        V_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        transitions = witness.find_phase_boundary(morphs, R_values, V_values)
        self.assertGreater(len(transitions), 0,
            "No phase transitions found — theory predicts boundaries exist")

    def test_multiple_morphologies_appear(self):
        """All three morphologies should appear somewhere in the grid."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        R_values = [2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 60.0]
        V_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        grid = witness.compute_phase_grid(morphs, R_values, V_values)
        all_winners = set()
        for row in grid:
            all_winners.update(row)
        self.assertEqual(len(all_winners), 3,
            f"Only {len(all_winners)} morphologies appear as winners: {all_winners}")


class TestResourcePressure(unittest.TestCase):
    """Control 8: resource pressure terms activate correctly."""

    def test_low_R_activates_storage_pressure(self):
        """When R is low and morphology needs many resources, burden increases."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        neural = [m for m in morphs if m.name == "neural"][0]
        # Low R
        burden_low = neural.burden(N=100, H=50.0, R=2.0, V=0.5)
        # High R
        burden_high = neural.burden(N=100, H=50.0, R=60.0, V=0.5)
        self.assertGreater(burden_low, burden_high,
            "Low resources should increase burden")


class TestComplexityPressure(unittest.TestCase):
    """Control 9: complexity pressure terms activate correctly."""

    def test_high_V_increases_symbolic_burden_more_than_neural(self):
        """High V (complex ecology) penalizes symbolic (high complexity penalty)
        more than neural (low complexity penalty)."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        neural = [m for m in morphs if m.name == "neural"][0]
        symbolic = [m for m in morphs if m.name == "symbolic"][0]
        # Low V
        n_low = neural.burden(N=100, H=50.0, R=60.0, V=0.1)
        s_low = symbolic.burden(N=100, H=50.0, R=60.0, V=0.1)
        # High V
        n_high = neural.burden(N=100, H=50.0, R=60.0, V=0.8)
        s_high = symbolic.burden(N=100, H=50.0, R=60.0, V=0.8)
        n_penalty = n_high - n_low
        s_penalty = s_high - s_low
        self.assertGreater(s_penalty, n_penalty,
            "Symbolic should be penalized more than neural at high V")


class TestGridConsistency(unittest.TestCase):
    """Control 10: grid dimensions match input."""

    def test_grid_shape(self):
        witness = _import_witness()
        morphs = witness.register_archetypes()
        R_values = [2.0, 5.0, 10.0]
        V_values = [0.2, 0.4, 0.6, 0.8]
        grid = witness.compute_phase_grid(morphs, R_values, V_values)
        self.assertEqual(len(grid), len(V_values))
        for row in grid:
            self.assertEqual(len(row), len(R_values))


class TestEdgeCases(unittest.TestCase):
    """Control 11: edge cases — extreme R, extreme V."""

    def test_extreme_high_R_V(self):
        """At very high R and V, neural should win."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[1000.0], V_values=[0.9], N=100, H=50.0
        )
        self.assertEqual(grid[0][0], "neural")

    def test_extreme_low_R_V(self):
        """At very low R and V, symbolic should win."""
        witness = _import_witness()
        morphs = witness.register_archetypes()
        grid = witness.compute_phase_grid(
            morphs, R_values=[0.1], V_values=[0.01], N=100, H=50.0
        )
        self.assertEqual(grid[0][0], "symbolic")


class TestHeldOutDifferentSeeds(unittest.TestCase):
    """Control 12: held-out prediction is stable across different seeds."""

    def test_two_seeds_above_90_percent(self):
        witness = _import_witness()
        morphs = witness.register_archetypes()
        R_values = [2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 60.0]
        V_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        for seed in [42, 137]:
            result = witness.held_out_prediction(
                morphs, R_values, V_values, fraction_held=0.25, seed=seed
            )
            self.assertGreaterEqual(result["prediction_accuracy"], 0.90,
                f"Seed {seed}: accuracy {result['prediction_accuracy']:.4f} < 0.90")


if __name__ == "__main__":
    unittest.main(verbosity=2)
