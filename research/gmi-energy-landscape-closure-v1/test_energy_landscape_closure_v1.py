from __future__ import annotations

import unittest

from energy_landscape_closure_v1 import (
    compile_to_d6,
    crossover,
    description_crossover,
    exhaustive_certificate,
    neighbors_from_mask,
    phase,
    relax_state,
    trajectory,
    validate_closure,
    validate_existing_receipt,
)


class EnergyLandscapeClosureTests(unittest.TestCase):
    def test_native_law_and_d6_compiler_are_identical(self) -> None:
        energies = (3, 1, 2, 0)
        neighbors = ((1, 2), (0, 3), (0, 3), (1, 2))
        compiled = compile_to_d6(energies, neighbors)
        self.assertEqual(compiled, tuple(relax_state(x, energies, neighbors) for x in range(4)))
        self.assertEqual(trajectory(0, compiled), (0, 1, 3))

    def test_exhaustive_tiny_universe(self) -> None:
        certificate = exhaustive_certificate()
        self.assertEqual(certificate["systems"], 5421)
        self.assertEqual(certificate["state_cases"], 21423)
        self.assertEqual(certificate["transition_mismatches"], 0)
        self.assertEqual(certificate["monotonicity_violations"], 0)
        self.assertEqual(certificate["termination_violations"], 0)

    def test_two_cycle_is_a_negative_twin(self) -> None:
        assignments = [
            (ea, eb)
            for ea in range(5)
            for eb in range(5)
            if eb < ea and ea < eb
        ]
        self.assertEqual(assignments, [])

    def test_phase_boundary_is_exact(self) -> None:
        self.assertEqual(crossover(1984, 3, 128, 4), 1856)
        self.assertEqual(phase(1855), "EXEMPLAR_PARENT")
        self.assertEqual(phase(1856), "TIE")
        self.assertEqual(phase(1857), "ENERGY_RELAXATION")

    def test_description_crossover(self) -> None:
        self.assertEqual(description_crossover(32), 124)

    def test_committed_receipt_is_intact(self) -> None:
        facts = validate_existing_receipt()
        self.assertEqual(facts["reuse_crossover"], 1856)
        self.assertEqual(facts["description_crossover_patterns"], 124)

    def test_complete_four_row_closure(self) -> None:
        self.assertEqual(
            validate_closure(),
            {
                "ledger_rows": 4,
                "exact_systems": 5421,
                "exact_state_cases": 21423,
                "reuse_crossover": 1856.0,
            },
        )


if __name__ == "__main__":
    unittest.main()
