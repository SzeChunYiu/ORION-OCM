import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ci_universal_witness_v1", ROOT / "ci_universal_witness_v1.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CE1_X, CE1_Y = _mod.CE1_X, _mod.CE1_Y
ce2_mandatory_upkeep = _mod.ce2_mandatory_upkeep
channel_burden = _mod.channel_burden
joint_burden = _mod.joint_burden
lemma_a_disjoint_additivity = _mod.lemma_a_disjoint_additivity
lemma_b_bounds = _mod.lemma_b_bounds
lemma_c_free_option_monotonicity = _mod.lemma_c_free_option_monotonicity


class TestLemmaA(unittest.TestCase):
    def test_disjoint_channels_additive(self):
        x = {"S": frozenset("ab"), "T": frozenset("c")}
        y = {"M": frozenset("de")}
        self.assertTrue(lemma_a_disjoint_additivity(x, y))

    def test_additivity_fails_when_channels_shared(self):
        x = {"S": frozenset("ab")}
        y = {"S": frozenset("cd")}
        with self.assertRaises(AssertionError):
            lemma_a_disjoint_additivity(x, y)


class TestLemmaB(unittest.TestCase):
    def test_nested_claims_give_max(self):
        ok, label = lemma_b_bounds({"S": frozenset("abc")}, {"S": frozenset("ab")}, "S")
        self.assertTrue(ok); self.assertEqual(label, "MAX (nested claims)")

    def test_disjoint_claims_give_sum(self):
        ok, label = lemma_b_bounds({"S": frozenset("ab")}, {"S": frozenset("cd")}, "S")
        self.assertTrue(ok); self.assertEqual(label, "SUM (disjoint claims)")

    def test_partial_overlap_strictly_between(self):
        ok, label = lemma_b_bounds({"S": frozenset("abc")}, {"S": frozenset("bcd")}, "S")
        self.assertTrue(ok); self.assertEqual(label, "STRICTLY BETWEEN (partial within-channel overlap)")

    def test_union_arithmetic_exact(self):
        x, y = {"S": frozenset("abc")}, {"S": frozenset("bcd")}
        self.assertEqual(joint_burden(x, y), 4)
        self.assertEqual(channel_burden(x) + channel_burden(y), 6)


class TestLemmaCAndCounterexamples(unittest.TestCase):
    def test_free_option_monotone(self):
        self.assertTrue(lemma_c_free_option_monotonicity(10, 10))
        self.assertTrue(lemma_c_free_option_monotonicity(12, 10))

    def test_ce1_shared_channel_disjoint_claims(self):
        joint = joint_burden(CE1_X, CE1_Y)
        self.assertEqual(joint, 7)
        self.assertGreater(joint, max(len(CE1_X["S"]), len(CE1_Y["S"])))

    def test_ce2_mandatory_upkeep_interferes(self):
        self.assertTrue(ce2_mandatory_upkeep(budget=10, x_needs=10, upkeep=2))
        self.assertFalse(ce2_mandatory_upkeep(budget=10, x_needs=10, upkeep=0))


if __name__ == "__main__":
    unittest.main()
