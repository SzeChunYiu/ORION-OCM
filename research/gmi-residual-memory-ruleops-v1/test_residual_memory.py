#!/usr/bin/env python3
"""
test_residual_memory.py

Unit tests for residual memory conditions, retrieval frequency laws,
index cost laws, and rule operators.
"""
import math
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from residual_memory_witness import (
    parametric_capacity,
    residual_memory_condition,
    compute_residual_quotient,
    optimal_retrieval_frequency,
    index_cost_amortization_condition,
    minimal_rewrite_system_complexity,
    emitter_selector_analysis,
    comparison_with_existing_systems,
    neutral_recovery_condition
)


class TestParametricCapacity(unittest.TestCase):
    """Tests for parametric_capacity function."""

    def test_capacity_ratio_basic(self):
        """Test basic capacity ratio calculation."""
        result = parametric_capacity(task_facts=100, model_capacity=50)
        self.assertEqual(result, 2.0)

    def test_capacity_ratio_equal(self):
        """Test capacity ratio when facts equal capacity."""
        result = parametric_capacity(task_facts=100, model_capacity=100)
        self.assertEqual(result, 1.0)

    def test_capacity_ratio_less_than_one(self):
        """Test capacity ratio when facts less than capacity."""
        result = parametric_capacity(task_facts=50, model_capacity=100)
        self.assertEqual(result, 0.5)


class TestResidualMemoryCondition(unittest.TestCase):
    """Tests for residual_memory_condition function."""

    def test_external_memory_needed(self):
        """Test when external memory is required."""
        needed, quotient = residual_memory_condition(
            task_facts=10000,
            model_capacity=1000,
            retrieval_cost=10,
            parametric_expansion_cost=0.1
        )
        self.assertTrue(needed)
        self.assertGreater(quotient, 0)

    def test_external_memory_not_needed(self):
        """Test when external memory is not required."""
        needed, quotient = residual_memory_condition(
            task_facts=50,
            model_capacity=1000,
            retrieval_cost=10,
            parametric_expansion_cost=0.1
        )
        self.assertFalse(needed)
        self.assertEqual(quotient, 0.0)

    def test_boundary_condition(self):
        """Test boundary where retrieval cost equals expansion cost."""
        needed, quotient = residual_memory_condition(
            task_facts=2000,
            model_capacity=1000,
            retrieval_cost=100,  # 1000 facts * 0.1 = 100
            parametric_expansion_cost=0.1
        )
        self.assertFalse(needed)  # Equal means not strictly less


class TestResidualQuotient(unittest.TestCase):
    """Tests for compute_residual_quotient function."""

    def test_quotient_basic(self):
        """Test basic quotient calculation."""
        Q = compute_residual_quotient(
            target_frequency=0.5,
            num_facts=1000,
            model_capacity=100,
            retrieval_count=10,
            retrieval_cost=1.0
        )
        # Q = (0.5 * 1000) / (100 + 10 * 1.0) = 500 / 110 ≈ 4.545
        self.assertAlmostEqual(Q, 4.545, places=3)

    def test_quotient_advantage(self):
        """Test quotient > 1 means external memory advantage."""
        Q = compute_residual_quotient(
            target_frequency=1.0,
            num_facts=1000,
            model_capacity=100,
            retrieval_count=5,
            retrieval_cost=1.0
        )
        # Q = 1000 / (100 + 5) ≈ 9.52
        self.assertGreater(Q, 1.0)

    def test_quotient_no_advantage(self):
        """Test quotient < 1 means no external memory advantage."""
        Q = compute_residual_quotient(
            target_frequency=0.01,
            num_facts=100,
            model_capacity=1000,
            retrieval_count=10,
            retrieval_cost=1.0
        )
        # Q = 1 / (1000 + 10) ≈ 0.001
        self.assertLess(Q, 1.0)

    def test_quotient_zero_denominator(self):
        """Test quotient with zero denominator returns infinity."""
        Q = compute_residual_quotient(
            target_frequency=0.5,
            num_facts=100,
            model_capacity=0,
            retrieval_count=0,
            retrieval_cost=0
        )
        self.assertEqual(Q, float('inf'))


class TestOptimalRetrievalFrequency(unittest.TestCase):
    """Tests for optimal_retrieval_frequency function."""

    def test_square_root_scaling(self):
        """Test that frequencies follow square-root scaling."""
        frequencies = [0.5, 0.3, 0.2]
        result = optimal_retrieval_frequency(frequencies)

        # Should sum to 1
        self.assertAlmostEqual(sum(result), 1.0, places=10)

        # sqrt(0.5) ≈ 0.707, sqrt(0.3) ≈ 0.548, sqrt(0.2) ≈ 0.447
        # Total ≈ 1.702
        # Normalized: 0.707/1.702 ≈ 0.415, 0.548/1.702 ≈ 0.322, 0.447/1.702 ≈ 0.263
        self.assertAlmostEqual(result[0], 0.415, places=3)
        self.assertAlmostEqual(result[1], 0.322, places=3)
        self.assertAlmostEqual(result[2], 0.263, places=3)

    def test_uniform_frequencies(self):
        """Test with uniform frequencies."""
        frequencies = [0.25, 0.25, 0.25, 0.25]
        result = optimal_retrieval_frequency(frequencies)

        # All should be equal (0.25 each)
        for r in result:
            self.assertAlmostEqual(r, 0.25, places=10)

    def test_empty_list(self):
        """Test with empty list."""
        result = optimal_retrieval_frequency([])
        self.assertEqual(result, [])

    def test_single_frequency(self):
        """Test with single frequency."""
        result = optimal_retrieval_frequency([1.0])
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0], 1.0, places=10)


class TestIndexCostAmortization(unittest.TestCase):
    """Tests for index_cost_amortization_condition function."""

    def test_amortization_basic(self):
        """Test basic amortization calculation."""
        result = index_cost_amortization_condition(
            num_stored_facts=1000,
            model_capacity=1000
        )
        # index_cost = 1000 * log2(1001) ≈ 1000 * 9.97 ≈ 9966
        # min_retrievals = ceil(9966 / 1000) = 10
        self.assertEqual(result, 10)

    def test_amortization_small_index(self):
        """Test amortization with small index."""
        result = index_cost_amortization_condition(
            num_stored_facts=10,
            model_capacity=1000
        )
        # index_cost = 10 * log2(11) ≈ 10 * 3.46 ≈ 34.6
        # min_retrievals = ceil(34.6 / 1000) = 1
        self.assertEqual(result, 1)

    def test_amortization_large_index(self):
        """Test amortization with large index."""
        result = index_cost_amortization_condition(
            num_stored_facts=100000,
            model_capacity=1000
        )
        # index_cost = 100000 * log2(100001) ≈ 100000 * 16.61 ≈ 1661000
        # min_retrievals = ceil(1661000 / 1000) = 1661
        self.assertEqual(result, 1661)

    def test_amortization_zero_capacity(self):
        """Test with zero capacity returns infinity."""
        result = index_cost_amortization_condition(
            num_stored_facts=100,
            model_capacity=0
        )
        self.assertEqual(result, float('inf'))


class TestMinimalRewriteSystemComplexity(unittest.TestCase):
    """Tests for minimal_rewrite_system_complexity function."""

    def test_complexity_basic(self):
        """Test basic complexity calculation."""
        pairs = [("a", "b"), ("c", "d")]
        alphabet_size = 26

        result = minimal_rewrite_system_complexity(pairs, alphabet_size)
        # Total chars = (1+1) + (1+1) = 4
        # Complexity = 4 / 26 ≈ 0.154
        self.assertAlmostEqual(result, 4/26, places=3)

    def test_complexity_longer_pairs(self):
        """Test complexity with longer pairs."""
        pairs = [("hello", "world"), ("foo", "bar")]
        alphabet_size = 26

        result = minimal_rewrite_system_complexity(pairs, alphabet_size)
        # Total chars = (5+5) + (3+3) = 16
        # Complexity = 16 / 26 ≈ 0.615
        self.assertAlmostEqual(result, 16/26, places=3)

    def test_complexity_empty_pairs(self):
        """Test complexity with empty pairs."""
        result = minimal_rewrite_system_complexity([], 26)
        self.assertEqual(result, 0.0)

    def test_complexity_zero_alphabet(self):
        """Test complexity with zero alphabet size."""
        result = minimal_rewrite_system_complexity([("a", "b")], 0)
        self.assertEqual(result, 0.0)


class TestEmitterSelectorAnalysis(unittest.TestCase):
    """Tests for emitter_selector_analysis function."""

    def test_analysis_basic(self):
        """Test basic analysis."""
        pairs = [("a", "x"), ("b", "y"), ("c", "z")]

        result = emitter_selector_analysis(pairs)

        self.assertEqual(result["emitter_count"], 3)  # 3 unique inputs
        self.assertEqual(result["selector_count"], 3)  # 3 unique outputs
        self.assertEqual(result["total_rules"], 6)

    def test_analysis_with_repeated_outputs(self):
        """Test analysis with repeated outputs."""
        pairs = [("a", "x"), ("b", "x"), ("c", "y")]

        result = emitter_selector_analysis(pairs)

        self.assertEqual(result["emitter_count"], 3)  # 3 unique inputs
        self.assertEqual(result["selector_count"], 2)  # 2 unique outputs (x, y)
        self.assertEqual(result["total_rules"], 5)

    def test_analysis_empty_pairs(self):
        """Test analysis with empty pairs."""
        result = emitter_selector_analysis([])

        self.assertEqual(result["emitter_count"], 0)
        self.assertEqual(result["selector_count"], 0)
        self.assertEqual(result["total_rules"], 0)


class TestComparisonWithExistingSystems(unittest.TestCase):
    """Tests for comparison_with_existing_systems function."""

    def test_all_systems_present(self):
        """Test that all systems are present."""
        systems = comparison_with_existing_systems()

        expected_systems = [
            "residual_memory", "rag", "adapters", "caches", "databases"
        ]
        for system in expected_systems:
            self.assertIn(system, systems)

    def test_system_properties(self):
        """Test that systems have required properties."""
        systems = comparison_with_existing_systems()

        for name, props in systems.items():
            self.assertIn("type", props)
            self.assertIn("memory", props)
            self.assertIn("retrieval", props)
            self.assertIn("policy", props)

    def test_residual_memory_is_hybrid(self):
        """Test that residual memory is classified as hybrid."""
        systems = comparison_with_existing_systems()

        self.assertEqual(systems["residual_memory"]["type"], "hybrid")


class TestNeutralRecoveryCondition(unittest.TestCase):
    """Tests for neutral_recovery_condition function."""

    def test_all_conditions_met(self):
        """Test when all conditions are met."""
        result = neutral_recovery_condition(True, True, True, True)
        self.assertTrue(result)

    def test_missing_capacity(self):
        """Test when missing finite capacity."""
        result = neutral_recovery_condition(False, True, True, True)
        self.assertFalse(result)

    def test_missing_external_storage(self):
        """Test when missing external storage."""
        result = neutral_recovery_condition(True, False, True, True)
        self.assertFalse(result)

    def test_missing_adaptive_retrieval(self):
        """Test when missing adaptive retrieval."""
        result = neutral_recovery_condition(True, True, False, True)
        self.assertFalse(result)

    def test_missing_consolidation(self):
        """Test when missing consolidation."""
        result = neutral_recovery_condition(True, True, True, False)
        self.assertFalse(result)

    def test_multiple_missing(self):
        """Test when multiple conditions are missing."""
        result = neutral_recovery_condition(False, False, True, False)
        self.assertFalse(result)

    def test_no_conditions_met(self):
        """Test when no conditions are met."""
        result = neutral_recovery_condition(False, False, False, False)
        self.assertFalse(result)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions."""

    def test_short_context_scenario(self):
        """Test short context scenario end-to-end."""
        task_facts = 50
        model_capacity = 1000

        capacity_ratio = parametric_capacity(task_facts, model_capacity)
        needed, quotient = residual_memory_condition(
            task_facts, model_capacity, 10, 0.1
        )

        self.assertLess(capacity_ratio, 1.0)
        self.assertFalse(needed)

    def test_long_context_scenario(self):
        """Test long context scenario end-to-end."""
        task_facts = 10000
        model_capacity = 1000

        capacity_ratio = parametric_capacity(task_facts, model_capacity)
        needed, quotient = residual_memory_condition(
            task_facts, model_capacity, 10, 0.1
        )

        self.assertGreater(capacity_ratio, 1.0)
        self.assertTrue(needed)

    def test_retrieval_frequency_optimization(self):
        """Test retrieval frequency optimization integrates correctly."""
        frequencies = [0.5, 0.3, 0.2]
        optimal = optimal_retrieval_frequency(frequencies)

        # Verify square-root property: optimal[i]/optimal[j] = sqrt(freq[i]/freq[j])
        ratio_opt = optimal[0] / optimal[1]
        ratio_freq = math.sqrt(frequencies[0] / frequencies[1])
        self.assertAlmostEqual(ratio_opt, ratio_freq, places=10)


if __name__ == "__main__":
    unittest.main()
