"""Tests for capability interactions unified theorem V1.

10+ unittest controls covering:
- Shared-nothing independence
- Full overlap synergy
- Partial overlap redundancy
- No interfering pair (PVR-3)
- 27x27 matrix symmetry
- Pairwise Jaccard overlap correctness
- Interaction type classification correctness
- Capability count = 27
- Summary statistics consistency
"""

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "interactions_witness", ROOT / "interactions_witness.py"
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class StructuralTests(unittest.TestCase):
    """Top-level structural properties of the interaction matrix."""

    def test_exactly_27_capabilities(self):
        self.assertEqual(27, len(mod.CAPABILITY_IDS))

    def test_no_interfering_pairs(self):
        """PVR-3 guarantee: no capability pair is interfering."""
        self.assertTrue(mod.verify_no_interference())

    def test_interaction_matrix_is_symmetric(self):
        """interaction_type(X,Y) == interaction_type(Y,X) for all pairs."""
        self.assertTrue(mod.verify_symmetric())

    def test_summary_total_matches_pairs(self):
        """Sum of all interaction types equals C(27,2) = 351."""
        summary = mod.interaction_summary()
        total = sum(summary.values())
        self.assertEqual(351, total)

    def test_no_interfering_in_summary(self):
        summary = mod.interaction_summary()
        self.assertEqual(0, summary["interfering"])


class JaccardOverlapTests(unittest.TestCase):
    """Jaccard overlap computations."""

    def test_empty_sets_overlap_zero(self):
        self.assertAlmostEqual(0.0, mod.jaccard_overlap(frozenset(), frozenset()))

    def test_identical_sets_overlap_one(self):
        self.assertAlmostEqual(1.0, mod.jaccard_overlap(frozenset({"S", "T"}), frozenset({"S", "T"})))

    def test_disjoint_sets_overlap_zero(self):
        self.assertAlmostEqual(0.0, mod.jaccard_overlap(frozenset({"S"}), frozenset({"M"})))

    def test_partial_overlap(self):
        # {S,T} vs {S,M}: intersection={S}, union={S,T,M}, Jaccard=1/3
        self.assertAlmostEqual(1.0 / 3.0, mod.jaccard_overlap(frozenset({"S", "T"}), frozenset({"S", "M"})))

    def test_subset_overlap(self):
        # {S} vs {S,T}: intersection={S}, union={S,T}, Jaccard=1/2
        self.assertAlmostEqual(0.5, mod.jaccard_overlap(frozenset({"S"}), frozenset({"S", "T"})))


class InteractionTypeTests(unittest.TestCase):
    """Interaction classification for specific cases."""

    def test_shared_nothing_is_independent(self):
        """Two capabilities sharing no channels are independent."""
        self.assertEqual("independent", mod.interaction_type(frozenset({"S"}), frozenset({"M"})))

    def test_full_overlap_is_synergistic(self):
        """Two capabilities using exactly the same channels are synergistic."""
        self.assertEqual("synergistic", mod.interaction_type(frozenset({"S", "T"}), frozenset({"S", "T"})))

    def test_partial_overlap_is_redundant(self):
        """Two capabilities sharing some but not all channels are redundant."""
        self.assertEqual("redundant", mod.interaction_type(frozenset({"S", "T"}), frozenset({"S", "M"})))

    def test_compute_only_vs_smt_is_redundant(self):
        """causal-inference ({T}) vs retrieval ({S,T,M}) is redundant."""
        self.assertEqual(
            "redundant",
            mod.interaction_type(RESOURCE_CHANNELS["cap-causal-inference"], RESOURCE_CHANNELS["cap-retrieval"]),
        )

    def test_communication_only_vs_tool_use_is_redundant(self):
        """communication ({S,M}) vs tool-use ({S,T,M}) is redundant."""
        self.assertEqual(
            "redundant",
            mod.interaction_type(RESOURCE_CHANNELS["cap-communication"], RESOURCE_CHANNELS["cap-tool-use"]),
        )


# Import RESOURCE_CHANNELS for the above tests
RESOURCE_CHANNELS = mod.RESOURCE_CHANNELS


class PairwiseMatrixTests(unittest.TestCase):
    """Properties of the full 27x27 matrix."""

    def test_overlap_matrix_dimensions(self):
        matrix = mod.pairwise_overlap_matrix()
        self.assertEqual(27, len(matrix))
        for row in matrix:
            self.assertEqual(27, len(row))

    def test_interaction_matrix_dimensions(self):
        matrix = mod.pairwise_interaction_matrix()
        self.assertEqual(27, len(matrix))
        for row in matrix:
            self.assertEqual(27, len(row))

    def test_diagonal_is_synergistic(self):
        """Every capability paired with itself is synergistic (full overlap)."""
        matrix = mod.pairwise_interaction_matrix()
        for i in range(27):
            self.assertEqual("synergistic", matrix[i][i])

    def test_diagonal_overlap_is_one(self):
        """Jaccard overlap of a capability with itself is 1.0."""
        matrix = mod.pairwise_overlap_matrix()
        for i in range(27):
            self.assertAlmostEqual(1.0, matrix[i][i])

    def test_overlap_matrix_symmetric(self):
        matrix = mod.pairwise_overlap_matrix()
        for i in range(27):
            for j in range(27):
                self.assertAlmostEqual(matrix[i][j], matrix[j][i])


class SpecificCapabilityTests(unittest.TestCase):
    """Tests for specific known interactions."""

    def test_causal_inference_is_compute_only(self):
        self.assertEqual(frozenset({"T"}), RESOURCE_CHANNELS["cap-causal-inference"])

    def test_metacognition_is_compute_only(self):
        self.assertEqual(frozenset({"T"}), RESOURCE_CHANNELS["cap-metacognition"])

    def test_communication_has_comm_channel(self):
        self.assertIn("M", RESOURCE_CHANNELS["cap-communication"])

    def test_retrieval_has_all_three(self):
        self.assertEqual(frozenset({"S", "T", "M"}), RESOURCE_CHANNELS["cap-retrieval"])

    def test_tool_use_has_all_three(self):
        self.assertEqual(frozenset({"S", "T", "M"}), RESOURCE_CHANNELS["cap-tool-use"])

    def test_imputation_compute_only(self):
        self.assertEqual(frozenset({"T"}), RESOURCE_CHANNELS["cap-imitation"])

    def test_two_compute_only_are_synergistic(self):
        """causal-inference and metacognition share all channels ({T})."""
        self.assertEqual(
            "synergistic",
            mod.interaction_type(
                RESOURCE_CHANNELS["cap-causal-inference"],
                RESOURCE_CHANNELS["cap-metacognition"],
            ),
        )


if __name__ == "__main__":
    unittest.main()
