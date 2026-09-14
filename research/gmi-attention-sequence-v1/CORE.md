# Attention sequence: read first

This capsule closes 602 Section E boxes on sparse/local attention and the
long-sequence ecology where obligations compound faster than a fixed-carry
machine can amortize them.

## Claims closed

| Box | Claim | Status |
|-----|-------|--------|
| E (sparse/local) | Derive sparse/local attention under locality/budget pressure | T1 + T2 |
| E (phase boundary) | Predict full vs sparse/local routing phase boundary | T2 |
| E (long-sequence) | Neutral recovery in a held-out long-sequence ecology | T3 |

## Files

| Read | What it contains |
|------|-----------------|
| [ATTENTION_SEQUENCE_THEOREM_V1](ATTENTION_SEQUENCE_THEOREM_V1.md) | Theorems T1 (sparse wins), T2 (phase boundary), T3 (crossover) |
| [attention_witness](attention_witness.py) | Sweep (M, K, N) cells verifying all three theorems |
| [test_attention_sequence](test_attention_sequence.py) | 16 unit tests covering all claims |

## Parents

- **DYNAMIC_ROUTING** (gmi-formal-derivation-v1): single-pointer routing condition
- **HIERARCHICAL_CHUNKING** (gmi-formal-derivation-v1): skill formation subroutine

## Ceiling

G2: phase boundary and crossover hold structurally across ecology instances.
