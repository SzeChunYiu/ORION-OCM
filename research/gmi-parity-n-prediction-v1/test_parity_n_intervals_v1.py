"""Finite exact controls only; no parity-candidate compilation or measurement."""

from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import types
import unittest

HERE = Path(__file__).resolve().parent
m = types.ModuleType("parity_intervals_checked")
source = HERE / "parity_n_interval_model_v1.py"
exec(compile(source.read_bytes(), str(source), "exec"), m.__dict__)


class IntervalControls(unittest.TestCase):
    def test_authored_operation_sum_is_two_n(self):
        for n in range(1, 13):
            self.assertEqual(m.counted_expression(n), 2*n)
            self.assertNotEqual(m.counted_expression(n), 2*n + 1)

    def test_lower_bound_certifies_xor_below_five(self):
        for n in (1, 2, 3, 4):
            self.assertEqual(m.relation(*m.costs(n, F(2*n+1))), m.LEFT)

    def test_equal_lower_endpoint_is_not_exact_tie(self):
        self.assertEqual(m.relation(*m.costs(5, F(11))), m.UNRESOLVED)
        self.assertEqual(m.relation(*m.costs(5, F(11), F(11))), m.TIE)
        self.assertEqual(m.relation(*m.costs(5, F(12), F(12))), m.LEFT)

    def test_one_lower_bound_permits_all_three_orderings(self):
        expected = (m.RIGHT, m.TIE, m.LEFT)
        for native, result in zip((13, 14, 15), expected):
            self.assertGreaterEqual(native, 13)
            self.assertEqual(m.relation(*m.costs(6, F(native), F(native))), result)
        self.assertEqual(m.relation(*m.costs(6, F(13))), m.UNRESOLVED)

    def test_lower_only_has_no_reverse_certificate_at_larger_n(self):
        for n in range(6, 13):
            self.assertEqual(m.relation(*m.costs(n, F(2*n+1))), m.UNRESOLVED)

    def test_exact_model_crossover_and_full_sweep_table(self):
        rows = {3: (88, 104), 4: (224, 240), 5: (544, 544),
                6: (1280, 1216), 7: (2944, 2688), 8: (6656, 5888)}
        for n, pair in rows.items():
            a, b = m.exact_hypothesis(n, sweep=True)
            self.assertEqual((a[0], b[0]), pair)
            self.assertEqual((a[1], b[1]), pair)
            self.assertEqual(m.relation(a, b), m.LEFT if n < 5 else m.TIE if n == 5 else m.RIGHT)

    def test_different_exact_cost_moves_crossover(self):
        for n in range(1, 9):
            actual = m.relation(*m.costs(n, F(2*n), F(2*n)))
            self.assertEqual(actual, m.LEFT if n < 4 else m.TIE if n == 4 else m.RIGHT)

    def test_nonnegative_linear_cost_need_not_cross(self):
        for n in range(1, 13):
            self.assertEqual(m.relation(*m.costs(n, F(4*n), F(4*n))), m.LEFT)

    def test_upper_bound_can_certify_delegation(self):
        self.assertEqual(m.relation(*m.costs(6, F(10), F(13))), m.RIGHT)
        self.assertEqual(m.relation(*m.costs(6, F(13), F(15))), m.UNRESOLVED)

    def test_written_net_lower_is_above_xor_only_in_declared_model(self):
        for n in range(1, 13):
            xor, _ = m.costs(n)
            self.assertEqual(m.relation(xor, m.written_net_lower(n)), m.LEFT)

    def test_interval_claims_hold_for_enumerated_completions(self):
        for n in range(1, 9):
            for lo in range(26):
                for hi in (lo, lo+1, lo+3):
                    a, b = m.costs(n, F(lo), F(hi))
                    result = m.relation(a, b)
                    self.assertEqual(result, m.relation(*m.costs(n, F(lo), F(hi), True)))
                    for native in range(lo, hi+1):
                        difference = 3*n+2 - (6+native)
                        if result == m.LEFT:
                            self.assertLess(difference, 0)
                        elif result == m.RIGHT:
                            self.assertGreater(difference, 0)
                        elif result == m.TIE:
                            self.assertEqual(difference, 0)

    def test_invalid_domains_cannot_supply_certificate(self):
        for n in (0, -1, True, F(3), 3.0):
            with self.assertRaises(ValueError):
                m.costs(n)
        for lo, hi in ((F(-1), None), (F(2), F(1)), (0.0, None), (F(0), float("inf"))):
            with self.assertRaises(ValueError):
                m.costs(3, lo, hi)

    def test_original_sources_and_active_frozen_records_are_unchanged(self):
        folder = HERE / "raw/pr573-8bd474de"
        bindings = json.loads((folder / "SOURCE_BINDINGS_V1.json").read_text())
        self.assertEqual(bindings["source_commit"], "8bd474deaf162580c6f47f8e2ef0c75835a18960")
        for name, row in bindings["files"].items():
            data = (folder / name).read_bytes()
            self.assertEqual(len(data), row["bytes"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])
            if name != "CORE.md":
                self.assertEqual((HERE / name).read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
