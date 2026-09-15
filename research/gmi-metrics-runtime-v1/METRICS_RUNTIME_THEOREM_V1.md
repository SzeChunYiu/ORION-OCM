# Metrics Runtime Theorem v1

## Definitions

### 1. Coordinate Space

A **capability** C is characterized by a vector of 11 non-negative coordinates:

```
C = (T, M, E, D, U, X, G, R, P, S, I)
```

| Symbol | Name                | Domain     | Description                                      |
|--------|---------------------|------------|--------------------------------------------------|
| T      | wall_clock          | [0, inf)   | Elapsed time per invocation (seconds)            |
| M      | memory_bytes        | [0, inf)   | Peak resident set size (bytes)                   |
| E      | energy_joules       | [0, inf)   | Estimated energy (power x time)                  |
| D      | description_length  | [0, inf)   | Kolmogorov-complexity proxy (bits)               |
| U      | update_cost         | [0, inf)   | State change cost per learning step              |
| X      | execution_cost      | [0, inf)   | Per-inference compute cost                       |
| G      | generalization_gap  | [0, 1]     | Train/test performance difference                |
| R      | retention_rate      | [0, 1]     | Performance after n time steps                   |
| P      | plasticity          | [0, 1]     | Rate of adaptation to new tasks                  |
| S      | stability           | [0, 1]     | Resistance to catastrophic forgetting            |
| I      | information_required| [0, inf)   | Minimum input bits needed                        |

### 2. Aggregate Cost

The **aggregate cost** of a capability is the L1 norm (sum) of all coordinates:

```
Cost(C) = T + M + E + D + U + X + G + (1-R) + (1-P) + (1-S) + I
```

Note: G, (1-R), (1-P), (1-S) are used because higher G (gap), lower R, lower P, lower S all represent worse outcomes, so they contribute positively to cost.

### 3. Subadditivity

For two capabilities A and B operating on the same resource pool:

```
Cost(A + B) <= Cost(A) + Cost(B)
```

This holds because shared infrastructure (memory allocator, runtime, scheduler) amortizes fixed costs. The inequality is strict when capabilities share resources.

**Proof sketch:** Let shared cost = S_shared. Then Cost(A+B) = Cost(A) + Cost(B) - S_shared, where S_shared >= 0 by the resource-sharing axiom.

### 4. Budget Allocation

A **budget allocation** for capability C is a function:

```
b: B -> Coordinates
```

mapping budget level b in [0, B_max] to a coordinate vector. We assume b is monotonically non-decreasing in each coordinate (more budget => at least as much capability).

### 5. ROI (Return on Investment)

For capability C at budget b:

```
ROI(C, b) = dP(C, b) / db
```

where P(C, b) is the system performance as a function of budget allocated to C. In discrete form:

```
ROI(C, b1, b2) = (P(C, b2) - P(C, b1)) / (b2 - b1)
```

### 6. Budget Flip

A **budget flip** occurs at budget level b* for capability C if:

```
ROI(C, b*) < 0
```

meaning that increasing the budget allocated to C beyond b* causes overall system performance to decrease.

## Theorems

### Theorem 1: At-Most-One Flip

**Statement:** For any finite budget B and any capability C whose ROI function ROI(C, b) is unimodal (single-peaked), there exists at most one flip point b* such that ROI(C, b*) < 0.

**Proof:** Assume for contradiction there exist two flip points b1 < b2 with ROI(C, b1) < 0 and ROI(C, b2) < 0. Since ROI is unimodal, it has a single maximum. Between b1 and b2, ROI must either be entirely negative (contradicting unimodality since ROI was positive before b1) or cross zero twice (contradicting single-peakedness). Therefore at most one flip point exists. QED.

### Theorem 2: Non-Negativity

**Statement:** All 11 coordinates are non-negative for any valid capability measurement.

**Proof:** Each coordinate measures a physical or informational quantity that is inherently non-negative: time, memory, energy, description length, costs, gaps, rates, and information are all >= 0 by their definitions. QED.

### Theorem 3: Subadditivity of Aggregate Cost

**Statement:** For capabilities A and B sharing a resource pool:

```
Cost(A + B) <= Cost(A) + Cost(B)
```

**Proof:** Cost(A+B) = sum_i coord_i(A+B). By the resource-sharing axiom, coord_i(A+B) <= coord_i(A) + coord_i(B) for each i (shared infrastructure reduces per-unit cost). Summing over all 11 coordinates yields the result. QED.

### Theorem 4: Budget-Flip Detection Correctness

**Statement:** The budget-flip detector correctly identifies all flip points in a finite discrete budget sequence.

**Proof:** The detector computes ROI between consecutive budget levels. A flip is detected whenever ROI(b_k, b_{k+1}) < 0. Since the budget sequence is finite and ordered, every pair of consecutive levels is examined. By Theorem 1, at most one such pair yields negative ROI. The detector therefore reports exactly the flip point (or none). QED.

## Known Limitations

1. **Aggregate cost is a normalized comparison proxy, not a physical quantity.** The L1 sum adds across disparate units (seconds, bytes, joules, bits). It is valid for *relative* ordering of capabilities within a fixed measurement harness, not as an absolute cost bound across harnesses with different scales.

2. **The (1-value) inversion for retention/plasticity/stability is a documented convention.** Cost-boosting coords (T,M,E,D,U,X,G,I) add directly; the three performance-like coords add as distance-from-ideal (1 - value). A truly scale-free formulation would define *every* coordinate as distance-to-ideal before summing.

3. **Theorem 1's at-most-one-flip claim assumes ROI is unimodal.** This is a stated assumption. The detector itself does NOT depend on it: it examines every consecutive budget transition in a finite sequence and reports each negative-ROI case exactly, so the detector is exact for finite budgets regardless of the theorem.
