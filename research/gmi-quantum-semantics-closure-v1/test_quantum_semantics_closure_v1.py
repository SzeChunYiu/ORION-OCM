from __future__ import annotations

import unittest
from fractions import Fraction

from quantum_semantics_closure_v1 import (
    STATES,
    apply_h,
    apply_x,
    exhaustive_semantics_certificate,
    measure_z,
    simulation_bounds,
    validate_closure,
)


class QuantumSemanticsClosureTests(unittest.TestCase):
    def test_exact_channels_and_measurement(self) -> None:
        zero = STATES[0]
        one = apply_x(zero)
        plus = apply_h(zero)
        self.assertEqual(one, STATES[1])
        self.assertEqual(plus, STATES[2])
        self.assertEqual(measure_z(plus), (Fraction(1, 2), Fraction(1, 2)))

    def test_exhaustive_exact_compiler(self) -> None:
        result = exhaustive_semantics_certificate()
        self.assertEqual(result["trajectories"], 155)
        self.assertEqual(result["compiler_mismatches"], 0)
        self.assertEqual(result["trace_violations"], 0)
        self.assertEqual(result["measurement_violations"], 0)

    def test_exponential_storage_is_explicit(self) -> None:
        self.assertEqual(simulation_bounds(8), {
            "state_vector_complex_entries": 256,
            "density_matrix_complex_entries": 65536,
            "dense_unitary_entries": 65536,
        })

    def test_three_tasks_close_and_frontier_stays_open(self) -> None:
        result = validate_closure()
        self.assertEqual(result["ledger_rows"], 3)
        self.assertEqual(result["violations"], 0)
        self.assertEqual(result["accounting_coordinates"], 24)


if __name__ == "__main__":
    unittest.main()
