"""Unittest controls for developmental history phase law.

10+ controls verifying trajectory length monotonicity, negative twin failure,
morphology separation, and burden dynamics. Python 3.8 safe, unittest, no network.
"""
import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "devhist", ROOT / "dev_history_witness.py"
)
devhist = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = devhist
SPEC.loader.exec_module(devhist)


class TestRegistration(unittest.TestCase):
    """Control 1: morphologies and ecologies register correctly."""

    def test_three_morphologies(self):
        morphs = devhist.register_morphologies()
        self.assertEqual(len(morphs), 3)
        names = {m.name for m in morphs}
        self.assertEqual(names, {"neural", "symbolic", "negative"})

    def test_three_ecologies(self):
        ecos = devhist.register_ecologies()
        self.assertEqual(len(ecos), 3)
        names = {e.name for e in ecos}
        self.assertEqual(names, {"simple", "moderate", "complex"})

    def test_ecology_complexity_ordering(self):
        ecos = devhist.register_ecologies()
        self.assertLess(ecos[0].running_need, ecos[1].running_need)
        self.assertLess(ecos[1].running_need, ecos[2].running_need)


class TestTrajectoryMonotonicity(unittest.TestCase):
    """Control 2: trajectory length increases with ecology complexity."""

    def test_neural_monotone(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        neural = [m for m in morphs if m.name == "neural"][0]
        lengths = [devhist.trajectory_length(neural, e) for e in ecos]
        self.assertLessEqual(lengths[0], lengths[1])
        self.assertLessEqual(lengths[1], lengths[2])

    def test_symbolic_monotone(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        symbolic = [m for m in morphs if m.name == "symbolic"][0]
        lengths = [devhist.trajectory_length(symbolic, e) for e in ecos]
        self.assertLessEqual(lengths[0], lengths[1])
        self.assertLessEqual(lengths[1], lengths[2])


class TestSimpleEcologyShortTrajectory(unittest.TestCase):
    """Control 3: simple ecology gives short trajectory for all morphologies."""

    def test_simple_short_all(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        simple = ecos[0]
        for morph in morphs:
            if morph.gain_rate <= 0:
                continue
            T = devhist.trajectory_length(morph, simple)
            self.assertLessEqual(T, 5,
                f"{morph.name} has T={T} at simple ecology, expected <= 5")


class TestComplexEcologyLongTrajectory(unittest.TestCase):
    """Control 4: complex ecology gives long trajectory."""

    def test_complex_long_positive_gain(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        complex_ = ecos[2]
        for morph in morphs:
            if morph.gain_rate <= 0:
                continue
            T = devhist.trajectory_length(morph, complex_)
            self.assertGreaterEqual(T, 3,
                f"{morph.name} has T={T} at complex ecology, expected >= 3")


class TestNegativeTwinFails(unittest.TestCase):
    """Control 5: negative twin returns -1 (impossible) for all ecologies."""

    def test_negative_twin_all_minus_one(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        neg = [m for m in morphs if m.name == "negative"][0]
        for eco in ecos:
            T = devhist.trajectory_length(neg, eco)
            self.assertEqual(T, -1,
                f"negative twin at {eco.name}: T={T}, expected -1")


class TestNeuralShorterThanSymbolic(unittest.TestCase):
    """Control 6: neural has shorter trajectory than symbolic at complex ecology."""

    def test_neural_shorter_complex(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        complex_ = ecos[2]
        neural = [m for m in morphs if m.name == "neural"][0]
        symbolic = [m for m in morphs if m.name == "symbolic"][0]
        T_neural = devhist.trajectory_length(neural, complex_)
        T_symbolic = devhist.trajectory_length(symbolic, complex_)
        self.assertLessEqual(T_neural, T_symbolic,
            f"neural T={T_neural} > symbolic T={T_symbolic} at complex ecology")


class TestNeuralReachesAdultSimple(unittest.TestCase):
    """Control 7: neural reaches adult competence quickly at simple ecology."""

    def test_neural_adult_simple(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        neural = [m for m in morphs if m.name == "neural"][0]
        simple = ecos[0]
        T = devhist.trajectory_length(neural, simple)
        self.assertLessEqual(T, 2,
            f"neural T={T} at simple ecology, expected <= 2")


class TestBurdenDecreasing(unittest.TestCase):
    """Control 8: burden decreases along trajectory for positive-gain morphologies."""

    def test_burden_decreasing_neural_simple(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        neural = [m for m in morphs if m.name == "neural"][0]
        simple = ecos[0]
        traj = devhist.developmental_trajectory(neural, simple)
        for i in range(len(traj) - 1):
            self.assertGreaterEqual(traj[i], traj[i + 1],
                f"burden increased at step {i}: {traj[i]:.4f} -> {traj[i+1]:.4f}")

    def test_burden_decreasing_symbolic_complex(self):
        morphs = devhist.register_morphologies()
        ecos = devhist.register_ecologies()
        symbolic = [m for m in morphs if m.name == "symbolic"][0]
        complex_ = ecos[2]
        traj = devhist.developmental_trajectory(symbolic, complex_)
        for i in range(len(traj) - 1):
            self.assertGreaterEqual(traj[i], traj[i + 1],
                f"burden increased at step {i}: {traj[i]:.4f} -> {traj[i+1]:.4f}")


class TestAllPass(unittest.TestCase):
    """Control 9: build_results returns all_pass=True."""

    def test_all_pass(self):
        result = devhist.build_results()
        self.assertTrue(result["all_pass"],
            f"assertions: {result['assertions']}")


class TestCommittedReceiptReproduces(unittest.TestCase):
    """Control 10: committed RESULT_V1.json matches fresh computation."""

    def test_reproduces(self):
        committed_path = ROOT / "RESULT_V1.json"
        if not committed_path.exists():
            self.skipTest("RESULT_V1.json not yet committed")
        committed = json.loads(committed_path.read_text(encoding="utf-8"))
        fresh = devhist.build_results()
        self.assertEqual(committed["all_pass"], fresh["all_pass"])
        self.assertEqual(committed["phase_table"], fresh["phase_table"])
        self.assertEqual(committed["assertions"], fresh["assertions"])


if __name__ == "__main__":
    unittest.main()
