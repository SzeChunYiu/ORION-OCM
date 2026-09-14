#!/usr/bin/env python3
"""
residual_memory_witness.py

Exact computation witness for residual memory conditions, retrieval frequency laws,
index cost laws, and rule operators derived from generic transformations.
"""
import math
from typing import List, Dict, Tuple


def parametric_capacity(task_facts: int, model_capacity: int) -> float:
    """
    Compute the parametric capacity ratio.

    Args:
        task_facts: Number of distinct facts required by the task
        model_capacity: Maximum facts storable in parameters

    Returns:
        Ratio of task facts to model capacity (>1 means external memory needed)
    """
    return task_facts / model_capacity


def residual_memory_condition(
    task_facts: int,
    model_capacity: int,
    retrieval_cost: float,
    parametric_expansion_cost: float
) -> Tuple[bool, float]:
    """
    Determine if external memory is required.

    Args:
        task_facts: Number of distinct facts required by the task
        model_capacity: Maximum facts storable in parameters
        retrieval_cost: Cost per retrieval (tokens/operations)
        parametric_expansion_cost: Cost per fact to expand parameters

    Returns:
        Tuple of (external_memory_needed, residual_quotient)
    """
    excess_facts = task_facts - model_capacity
    if excess_facts <= 0:
        return False, 0.0

    # Residual quotient: retrieval cost vs parametric expansion cost
    total_expansion_cost = parametric_expansion_cost * excess_facts
    residual_quotient = retrieval_cost / total_expansion_cost

    # External memory needed when retrieval is cheaper than expansion
    external_memory_needed = retrieval_cost < total_expansion_cost

    return external_memory_needed, residual_quotient


def compute_residual_quotient(
    target_frequency: float,
    num_facts: int,
    model_capacity: int,
    retrieval_count: int,
    retrieval_cost: float
) -> float:
    """
    Compute the predictive-target residual quotient Q.

    Q = (freq(Y) * N) / (C + retrieval_count * r)

    Args:
        target_frequency: Frequency of target Y in task distribution
        num_facts: Number of relevant facts N
        model_capacity: Parametric capacity C
        retrieval_count: Number of retrievals per query
        retrieval_cost: Cost per retrieval r

    Returns:
        Residual quotient Q (>1 means external memory provides net advantage)
    """
    numerator = target_frequency * num_facts
    denominator = model_capacity + retrieval_count * retrieval_cost
    return numerator / denominator if denominator > 0 else float('inf')


def optimal_retrieval_frequency(frequencies: List[float]) -> List[float]:
    """
    Compute optimal retrieval frequencies using square-root scaling.

    Given K distinct facts accessed with frequency p_i (sum = 1),
    optimal retrieval frequency f_i ∝ sqrt(p_i).

    Args:
        frequencies: List of access frequencies (should sum to 1)

    Returns:
        Normalized optimal retrieval frequencies
    """
    if not frequencies:
        return []

    # Square root scaling
    raw_frequencies = [math.sqrt(f) for f in frequencies]

    # Normalize to sum to 1
    total = sum(raw_frequencies)
    if total == 0:
        return [1.0 / len(frequencies)] * len(frequencies)

    return [f / total for f in raw_frequencies]


def index_cost_amortization_condition(
    num_stored_facts: int,
    model_capacity: int
) -> int:
    """
    Compute the minimum retrieval count needed to amortize index building cost.

    Index cost = O(K log K) where K = num_stored_facts
    Amortization: retrieval_count > K log K / C

    Args:
        num_stored_facts: Number of facts K to store in index
        model_capacity: Parametric cost equivalent C

    Returns:
        Minimum retrieval count needed to amortize index cost
    """
    if model_capacity <= 0:
        return float('inf')

    index_cost = num_stored_facts * math.log2(num_stored_facts + 1)
    min_retrievals = math.ceil(index_cost / model_capacity)
    return min_retrievals


def minimal_rewrite_system_complexity(
    input_output_pairs: List[Tuple[str, str]],
    alphabet_size: int
) -> float:
    """
    Compute minimal rewrite system complexity.

    Complexity = K(x, y) / alpha
    where K(x, y) is Kolmogorov complexity of the pair set
    and alpha is the alphabet size.

    Args:
        input_output_pairs: List of (input, output) pairs
        alphabet_size: Size of the alphabet used

    Returns:
        Estimated minimal rewrite system complexity
    """
    if not input_output_pairs or alphabet_size <= 0:
        return 0.0

    # Estimate Kolmogorov complexity as total character count (upper bound)
    total_chars = sum(len(inp) + len(out) for inp, out in input_output_pairs)

    # Complexity = total chars / alphabet size
    return total_chars / alphabet_size


def emitter_selector_analysis(
    input_output_pairs: List[Tuple[str, str]]
) -> Dict[str, int]:
    """
    Analyze the emitter vs selector requirements for a set of pairs.

    Args:
        input_output_pairs: List of (input, output) pairs

    Returns:
        Dictionary with emitter_count, selector_count, and total_rules
    """
    # Simple heuristic: count unique inputs and unique outputs
    unique_inputs = set(inp for inp, _ in input_output_pairs)
    unique_outputs = set(out for _, out in input_output_pairs)

    # Emitter rules: one per unique input (transforms input to output)
    emitter_count = len(unique_inputs)

    # Selector rules: one per unique output (chooses among outputs)
    selector_count = len(unique_outputs)

    return {
        "emitter_count": emitter_count,
        "selector_count": selector_count,
        "total_rules": emitter_count + selector_count
    }


def comparison_with_existing_systems() -> Dict[str, Dict[str, str]]:
    """
    Compare residual memory with existing systems.

    Returns:
        Dictionary mapping system names to their properties
    """
    return {
        "residual_memory": {
            "type": "hybrid",
            "memory": "external + parametric",
            "retrieval": "adaptive",
            "policy": "frequency-based"
        },
        "rag": {
            "type": "external only",
            "memory": "external",
            "retrieval": "fixed (top-k)",
            "policy": "none (always retrieve)"
        },
        "adapters": {
            "type": "parametric only",
            "memory": "internal",
            "retrieval": "none (all in params)",
            "policy": "none (always use)"
        },
        "caches": {
            "type": "working memory",
            "memory": "external",
            "retrieval": "exact match",
            "policy": "LRU/LFU"
        },
        "databases": {
            "type": "storage only",
            "memory": "external",
            "retrieval": "query-based",
            "policy": "manual"
        }
    }


def neutral_recovery_condition(
    has_finite_capacity: bool,
    has_external_storage: bool,
    has_adaptive_retrieval: bool,
    has_consolidation: bool
) -> bool:
    """
    Check if a system satisfies the neutral recovery conditions for residual-memory behavior.

    Args:
        has_finite_capacity: System has a finite capacity C
        has_external_storage: System can store facts outside parameters
        has_adaptive_retrieval: Retrieval frequency depends on access pattern
        has_consolidation: System can periodically absorb facts into parameters

    Returns:
        True if all conditions are satisfied
    """
    return all([
        has_finite_capacity,
        has_external_storage,
        has_adaptive_retrieval,
        has_consolidation
    ])


# =============================================================================
# Task Type Demonstrations
# =============================================================================

def demo_short_context():
    """Task type 1: Short context (parametric suffices)."""
    print("=" * 60)
    print("TASK TYPE 1: SHORT CONTEXT (Parametric Suffices)")
    print("=" * 60)

    task_facts = 50
    model_capacity = 1000

    needed, quotient = residual_memory_condition(
        task_facts=task_facts,
        model_capacity=model_capacity,
        retrieval_cost=10,
        parametric_expansion_cost=0.1
    )

    print(f"Task facts: {task_facts}")
    print(f"Model capacity: {model_capacity}")
    print(f"External memory needed: {needed}")
    print(f"Residual quotient: {quotient:.4f}")
    print(f"Capacity ratio: {parametric_capacity(task_facts, model_capacity):.4f}")
    print()


def demo_long_context():
    """Task type 2: Long context (external memory needed)."""
    print("=" * 60)
    print("TASK TYPE 2: LONG CONTEXT (External Memory Needed)")
    print("=" * 60)

    task_facts = 10000
    model_capacity = 1000

    needed, quotient = residual_memory_condition(
        task_facts=task_facts,
        model_capacity=model_capacity,
        retrieval_cost=10,
        parametric_expansion_cost=0.1
    )

    print(f"Task facts: {task_facts}")
    print(f"Model capacity: {model_capacity}")
    print(f"External memory needed: {needed}")
    print(f"Residual quotient: {quotient:.4f}")
    print(f"Capacity ratio: {parametric_capacity(task_facts, model_capacity):.4f}")
    print()


def demo_growing_context():
    """Task type 3: Growing context (crossover)."""
    print("=" * 60)
    print("TASK TYPE 3: GROWING CONTEXT (Crossover)")
    print("=" * 60)

    model_capacity = 1000

    for task_facts in [100, 500, 1000, 2000, 5000]:
        needed, quotient = residual_memory_condition(
            task_facts=task_facts,
            model_capacity=model_capacity,
            retrieval_cost=10,
            parametric_expansion_cost=0.1
        )

        print(f"Facts: {task_facts:5d} | Capacity: {model_capacity} | "
              f"Needed: {str(needed):5s} | Quotient: {quotient:.4f}")

    print()


def demo_retrieval_frequency():
    """Demonstrate square-root scaling of retrieval frequency."""
    print("=" * 60)
    print("RETRIEVAL FREQUENCY: Square-Root Scaling")
    print("=" * 60)

    # 10 facts with known frequencies
    facts = ["fact_1", "fact_2", "fact_3", "fact_4", "fact_5",
             "fact_6", "fact_7", "fact_8", "fact_9", "fact_10"]

    # Zipf-like distribution
    frequencies = [1.0/i for i in range(1, 11)]
    total = sum(frequencies)
    frequencies = [f/total for f in frequencies]

    optimal_freqs = optimal_retrieval_frequency(frequencies)

    print(f"{'Fact':<10} {'Access Freq':<15} {'Optimal Ret Freq':<18}")
    print("-" * 43)
    for fact, freq, opt_freq in zip(facts, frequencies, optimal_freqs):
        print(f"{fact:<10} {freq:<15.4f} {opt_freq:<18.4f}")

    print()


def demo_index_cost():
    """Demonstrate index cost amortization."""
    print("=" * 60)
    print("INDEX COST: Amortization Condition")
    print("=" * 60)

    model_capacity = 1000

    for num_facts in [100, 1000, 10000, 100000]:
        min_retrievals = index_cost_amortization_condition(num_facts, model_capacity)
        index_cost = num_facts * math.log2(num_facts + 1)

        print(f"Facts: {num_facts:6d} | Index Cost: {index_cost:12.0f} | "
              f"Min Retrievals: {min_retrievals:6d}")

    print()


def demo_rule_operators():
    """Demonstrate minimal rewrite system complexity."""
    print("=" * 60)
    print("RULE OPERATORS: Minimal Rewrite System")
    print("=" * 60)

    pairs = [
        ("a", "b"),
        ("b", "c"),
        ("c", "d"),
        ("x", "y"),
        ("y", "z"),
        ("hello", "world"),
        ("foo", "bar")
    ]

    alphabet_size = 26  # lowercase letters

    complexity = minimal_rewrite_system_complexity(pairs, alphabet_size)
    analysis = emitter_selector_analysis(pairs)

    print(f"Input-output pairs: {len(pairs)}")
    print(f"Alphabet size: {alphabet_size}")
    print(f"Estimated Kolmogorov complexity: {sum(len(i)+len(o) for i,o in pairs)}")
    print(f"Minimal rewrite system complexity: {complexity:.4f}")
    print(f"\nEmitter rules needed: {analysis['emitter_count']}")
    print(f"Selector rules needed: {analysis['selector_count']}")
    print(f"Total rules: {analysis['total_rules']}")
    print()


def demo_comparison():
    """Compare residual memory with existing systems."""
    print("=" * 60)
    print("COMPARISON WITH EXISTING SYSTEMS")
    print("=" * 60)

    systems = comparison_with_existing_systems()

    print(f"{'System':<20} {'Type':<15} {'Memory':<20} {'Retrieval':<20} {'Policy':<20}")
    print("-" * 95)

    for name, props in systems.items():
        print(f"{name:<20} {props['type']:<15} {props['memory']:<20} "
              f"{props['retrieval']:<20} {props['policy']:<20}")

    print()


def demo_neutral_recovery():
    """Demonstrate neutral recovery conditions."""
    print("=" * 60)
    print("NEUTRAL RECOVERY: Conditions for Residual-Memory Behavior")
    print("=" * 60)

    test_cases = [
        ("Full system", True, True, True, True),
        ("No external storage", True, False, True, True),
        ("No adaptive retrieval", True, True, False, True),
        ("No consolidation", True, True, True, False),
        ("Minimal system", False, True, True, True),
    ]

    for name, cap, ext, adapt, consol in test_cases:
        result = neutral_recovery_condition(cap, ext, adapt, consol)
        print(f"{name:<25} -> Residual-memory behavior: {result}")

    print()


if __name__ == "__main__":
    print("RESIDUAL MEMORY WITNESS DEMONSTRATION")
    print("=" * 60)
    print()

    demo_short_context()
    demo_long_context()
    demo_growing_context()
    demo_retrieval_frequency()
    demo_index_cost()
    demo_rule_operators()
    demo_comparison()
    demo_neutral_recovery()

    print("=" * 60)
    print("All demonstrations complete.")
