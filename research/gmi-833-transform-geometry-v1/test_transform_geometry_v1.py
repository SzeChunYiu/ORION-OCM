import json
import math
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fractions import Fraction

from transform_geometry_v1 import (
    CLAIM_CEILING,
    TransformError,
    all_pairs_distances,
    compose,
    finite_certificate,
    identity,
    make_transform,
    scalar_burden,
    triangle_violations,
)


class TransformGeometryTests(unittest.TestCase):
    def setUp(self):
        self.f = make_transform("A", "B", "1/10", (1, 2, 0), (("scope", "omega"),), ("e_f",))
        self.g = make_transform("B", "C", "1/20", (2, 0, 1), (("scope", "omega"),), ("e_g",))
        self.h = make_transform("C", "D", "1/25", (0, 1, 1), (("scope", "omega"),), ("e_h",))

    def test_identity_laws_exact(self):
        self.assertEqual(compose(identity("A"), self.f), self.f)
        self.assertEqual(compose(self.f, identity("B")), self.f)

    def test_associativity_exact(self):
        self.assertEqual(compose(compose(self.f, self.g), self.h), compose(self.f, compose(self.g, self.h)))

    def test_additive_error_resources(self):
        x = compose(self.f, self.g)
        self.assertEqual(x.semantic_error, Fraction(3, 20))
        self.assertEqual(x.resources, (Fraction(3), Fraction(2), Fraction(1)))

    def test_endpoint_mismatch_fails_closed(self):
        with self.assertRaisesRegex(TransformError, "ENDPOINT_MISMATCH"):
            compose(self.f, self.h)

    def test_assumption_conflict_fails_closed(self):
        a = make_transform("A", "B", 0, (0, 0, 0), (("mode", "x"),), ("a",))
        b = make_transform("B", "C", 0, (0, 0, 0), (("mode", "y"),), ("b",))
        with self.assertRaisesRegex(TransformError, "ASSUMPTION_CONFLICT"):
            compose(a, b)

    def test_missing_evidence_fails_closed(self):
        with self.assertRaisesRegex(TransformError, "MISSING_EVIDENCE"):
            make_transform("A", "B", 0, (0, 0, 0))

    def test_negative_costs_fail_closed(self):
        with self.assertRaisesRegex(TransformError, "NEGATIVE_ERROR"):
            make_transform("A", "B", -1, (0, 0, 0), evidence=("e",))
        with self.assertRaisesRegex(TransformError, "NEGATIVE_RESOURCE"):
            make_transform("A", "B", 0, (-1, 0, 0), evidence=("e",))

    def test_weights_fail_closed(self):
        with self.assertRaisesRegex(TransformError, "NONPOSITIVE_RESOURCE_WEIGHT"):
            scalar_burden(self.f, (1, 0, 1), 1)
        with self.assertRaisesRegex(TransformError, "NEGATIVE_ERROR_WEIGHT"):
            scalar_burden(self.f, (1, 1, 1), -1)

    def test_directed_distance_triangle_asymmetry_unreachable(self):
        nodes = ("A", "B", "C", "D")
        edges = (
            make_transform("A", "B", 0, (1, 0, 0), evidence=("ab",)),
            make_transform("B", "C", 0, (2, 0, 0), evidence=("bc",)),
            make_transform("C", "A", 0, (9, 0, 0), evidence=("ca",)),
        )
        d = all_pairs_distances(nodes, edges, (1, 1, 1), 1)
        self.assertEqual(d[("A", "A")], 0)
        self.assertEqual(d[("A", "C")], 3)
        self.assertEqual(d[("C", "A")], 9)
        self.assertNotEqual(d[("A", "C")], d[("C", "A")])
        self.assertTrue(math.isinf(d[("A", "D")]))
        self.assertEqual(triangle_violations(nodes, d), [])

    def test_receipt_is_green_and_json_exact(self):
        r = finite_certificate()
        self.assertEqual(r["claim_ceiling"], CLAIM_CEILING)
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        s = json.dumps(r, sort_keys=True, separators=(",", ":"))
        self.assertNotIn("NaN", s)


if __name__ == "__main__":
    unittest.main()
