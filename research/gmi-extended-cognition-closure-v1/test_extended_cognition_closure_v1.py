from __future__ import annotations

import unittest

from extended_cognition_closure_v1 import (
    agent_only_episode,
    capability,
    extended_episode,
    memory_parent_episode,
    minimality_certificate,
    reduction_certificate,
    validate_closure,
    validate_prediction,
)


class ExtendedCognitionClosureTests(unittest.TestCase):
    def test_external_bit_is_necessary_at_frozen_boundary(self) -> None:
        certificate = minimality_certificate()
        self.assertTrue(certificate["same_agent_projection"])
        self.assertTrue(certificate["different_external_states"])
        self.assertTrue(certificate["different_required_future_outputs"])

    def test_exact_capabilities_and_negative_twin(self) -> None:
        self.assertEqual(capability([extended_episode(b) for b in (0, 1)]), 1.0)
        self.assertEqual(capability([agent_only_episode(b) for b in (0, 1)]), 0.5)
        self.assertEqual(capability([extended_episode(b, erase_write=True) for b in (0, 1)]), 0.5)
        self.assertEqual(capability([memory_parent_episode(b) for b in (0, 1)]), 1.0)

    def test_memory_parent_absorbs_at_matched_scope(self) -> None:
        certificate = reduction_certificate()
        self.assertTrue(certificate["protected_answers_equal"])
        self.assertEqual(certificate["joint_state_bits"], certificate["parent_state_bits"])
        self.assertEqual(certificate["conclusion"], "REDUCED_TO_PARENT_D2_D6_AT_MATCHED_FINITE_SCOPE")

    def test_prediction_is_exact(self) -> None:
        result = validate_prediction()
        self.assertEqual(result["zero_bit_functions_exhausted"], 2)
        self.assertEqual(result["extended_capability"], 1.0)
        self.assertEqual(result["agent_only_zero_bit_upper_bound"], 0.5)

    def test_four_row_closure(self) -> None:
        self.assertEqual(
            validate_closure(),
            {
                "ledger_rows": 4,
                "histories": 2,
                "zero_bit_functions_exhausted": 2,
                "extended_capability": 1.0,
                "agent_only_capability": 0.5,
                "parent_capability": 1.0,
            },
        )


if __name__ == "__main__":
    unittest.main()
