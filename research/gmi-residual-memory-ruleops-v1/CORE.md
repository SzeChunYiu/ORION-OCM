# CORE: Residual Memory Rule Operators v1

## Quick Start

This capsule derives formal theorems for residual memory conditions, retrieval frequency laws, index cost laws, and rule operators from generic transformations.

**Parent capsules:** MEMORY_REGIME_PARTITION, CONSOLIDATION_FORGETTING
**Ceiling:** G2

## Key Results

### Residual Memory Condition
External memory is required when:
- Task facts N > Model capacity C
- Retrieval cost r < Parametric expansion cost p * (N - C)

### Predictive-Target Residual Quotient
Q = (freq(Y) * N) / (C + retrieval_count * r)
- Q > 1: external memory provides net advantage
- Q < 1: parametric storage suffices

### Retrieval Frequency Law
Optimal retrieval frequency f_i ∝ sqrt(p_i) (square-root scaling)
- More frequently accessed facts retrieved more often
- Sublinear rate prevents over-retrieval

### Index Cost Law
- Index building cost: O(K log K) where K = stored facts
- Amortized when: retrieval_count > K log K / C

### Rule Operators
- Minimal rewrite system complexity: K(x,y) / alpha
- K(x,y) = Kolmogorov complexity of pair set
- Alpha = alphabet size
- Requires both emitter and selector rules

## Comparison with Existing Systems

| System | Type | Memory | Retrieval | Policy |
|--------|------|--------|-----------|--------|
| Residual Memory | Hybrid | External + Parametric | Adaptive | Frequency-based |
| RAG | External only | External | Fixed (top-k) | None |
| Adapters | Parametric only | Internal | None | None |
| Caches | Working memory | External | Exact match | LRU/LFU |
| Databases | Storage only | External | Query-based | Manual |

## Files

- `RESIDUAL_MEMORY_RULEOPS_THEOREM_V1.md` - Formal theorems and proofs
- `residual_memory_witness.py` - Exact computation witness
- `test_residual_memory.py` - Unit tests (10+ test cases)

## Usage

```bash
# Run witness demonstration
python3 residual_memory_witness.py

# Run unit tests
python3 -m pytest test_residual_memory.py -v
# or
python3 test_residual_memory.py
```

## Neutral Recovery

A system exhibits residual-memory behavior iff it satisfies:
1. Parametric bound (finite capacity C)
2. External storage (facts outside parameters)
3. Adaptive retrieval (frequency-dependent)
4. Consolidation (periodic absorption into parameters)
