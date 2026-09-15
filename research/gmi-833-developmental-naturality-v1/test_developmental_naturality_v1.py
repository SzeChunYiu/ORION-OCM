import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from developmental_naturality_v1 import (
    CLAIM_CEILING,
    NaturalityError,
    compose_transforms,
    exact_developmental_natural,
    exhaustive_trajectory_check,
    finite_certificate,
    identity,
    make_system,
    make_transform,
    naturality_violations,
    static_behavior_preserving,
)


class DevelopmentalNaturalityTests(unittest.TestCase):
    def setUp(self):
        self.m = make_system(
            "M", ("0", "1"), ("x",), {"0": "a", "1": "b"},
            {("0", "x"): "1", ("1", "x"): "0"},
        )
        self.n = make_system(
            "N", ("A", "B"), ("x",), {"A": "a", "B": "b"},
            {("A", "x"): "B", ("B", "x"): "A"},
        )
        self.p = make_system(
            "P", ("L", "R"), ("x",), {"L": "a", "R": "b"},
            {("L", "x"): "R", ("R", "x"): "L"},
        )
        self.f = make_transform(self.m, self.n, {"0": "A", "1": "B"}, ("f",))
        self.g = make_transform(self.n, self.p, {"A": "L", "B": "R"}, ("g",))

    def test_identity_exact(self):
        self.assertTrue(exact_developmental_natural(self.m, self.m, identity(self.m)))

    def test_composition_exact(self):
        gf = compose_transforms(self.m, self.n, self.p, self.f, self.g)
        self.assertTrue(exact_developmental_natural(self.m, self.p, gf))

    def test_trajectory_induction_certificate(self):
        self.assertEqual(exhaustive_trajectory_check(self.m, self.n, self.f, 8), 18)

    def test_static_not_developmental(self):
        bad = make_system(
            "BAD", ("A", "B"), ("x",), {"A": "a", "B": "b"},
            {("A", "x"): "A", ("B", "x"): "B"},
        )
        t = make_transform(self.m, bad, {"0": "A", "1": "B"}, ("e",))
        self.assertTrue(static_behavior_preserving(self.m, bad, t))
        self.assertTrue(naturality_violations(self.m, bad, t))
        self.assertFalse(exact_developmental_natural(self.m, bad, t))

    def test_behavior_mismatch_blocks_certificate(self):
        bad = make_system(
            "BADLABEL", ("A", "B"), ("x",), {"A": "b", "B": "a"},
            {("A", "x"): "B", ("B", "x"): "A"},
        )
        t = make_transform(self.m, bad, {"0": "A", "1": "B"}, ("e",))
        self.assertEqual(naturality_violations(self.m, bad, t), [])
        self.assertFalse(static_behavior_preserving(self.m, bad, t))
        self.assertFalse(exact_developmental_natural(self.m, bad, t))

    def test_non_total_map_fails_closed(self):
        with self.assertRaisesRegex(NaturalityError, "NON_TOTAL_STATE_MAP"):
            make_transform(self.m, self.n, {"0": "A"}, ("e",))

    def test_experience_mismatch_fails_closed(self):
        q = make_system("Q", ("q",), ("z",), {"q": "a"}, {("q", "z"): "q"})
        with self.assertRaisesRegex(NaturalityError, "EXPERIENCE_ALPHABET_MISMATCH"):
            make_transform(self.m, q, {"0": "q", "1": "q"}, ("e",))

    def test_receipt_green(self):
        r = finite_certificate()
        self.assertEqual(r["claim_ceiling"], CLAIM_CEILING)
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        json.dumps(r, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    unittest.main()
