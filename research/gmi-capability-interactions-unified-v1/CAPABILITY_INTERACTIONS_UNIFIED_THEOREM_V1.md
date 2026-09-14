# Capability Interactions Unified Theorem V1

**Issue**: #602 Section F boxes 7-11 (cross-cutting capability interactions)
**Scope**: Unified interaction classification for all 27 capabilities in the A4 contract
**Evidence class**: P1 (formal) + P2 (finite-exact controls)
**Claim ceiling**: G2
**Parent capsule**: Synthesizes tranches 1-3 from `gmi-capability-interactions-v{1,2,3}/`

---

## 1. Definitions

### 1.1 Resource Channels

Each capability `C_i` in the 27-row A4 contract consumes resources from a finite set of **resource channels**:

- **Storage** (S): persistent state capacity (memory, code, models)
- **Compute** (T): transformation/processing steps (tau)
- **Communication** (M): message width, channel uses, protocol overhead

Let `R(C_i) ⊆ {S, T, M}` denote the resource channels consumed by capability `C_i`.

### 1.2 Interaction Types

Given two capabilities `X` and `Y`, their **joint burden** under simultaneous activation is classified as:

| Type | Condition | Meaning |
|------|-----------|---------|
| **Independent** | `joint = sum(individual)` | No shared resource contention |
| **Redundant** | `joint = max(individual)` | Shared resources overlap; joint cost equals the more expensive |
| **Synergistic** | `joint < sum(individual)` | Shared resources enable cheaper joint operation |
| **Interfering** | `joint > sum(individual)` | Resource contention creates super-additive cost |

### 1.3 Resource Overlap

Define the **resource overlap** between capabilities `X` and `Y`:

```
overlap(X, Y) = |R(X) ∩ R(Y)| / |R(X) ∪ R(Y)|
```

This is the Jaccard similarity of their resource channel sets.

---

## 2. Main Theorem

### Theorem CI (Capability Interaction Classification)

For any two capabilities `X` and `Y` from the 27-row A4 contract:

1. **If `R(X) ∩ R(Y) = ∅`** (no shared resource channels):
   - `X` and `Y` are **independent**
   - Joint burden = sum of individual burdens

2. **If `R(X) ∩ R(Y) = R(X) = R(Y)`** (all channels shared):
   - `X` and `Y` are **synergistic**
   - Joint burden < sum of individual burdens (shared resources amortized)

3. **If `∅ ⊂ R(X) ∩ R(Y) ⊂ R(X) ∪ R(Y)`** (partial overlap):
   - `X` and `Y` are **redundant**
   - Joint burden = max(individual burdens) on shared channels

4. **Interference is ruled out by PVR-3**:
   - Under the frozen accounting of the A4 contract, adding a capability cannot increase the burden of another beyond sum
   - This follows from the free-option monotonicity theorem (tranche 3, Theorem IF)

### Proof Sketch

**Independence (Case 1)**: When capabilities share no resource channels, their operations are disjoint. No contention or sharing is possible, so burdens add.

**Synergy (Case 2)**: When all channels are shared, the joint operation can reuse the same resources. For example, two memory-intensive capabilities sharing the same storage pool incur storage cost once, not twice. The joint burden is bounded by the maximum individual burden on each shared channel.

**Redundancy (Case 3)**: Partial overlap means some resources are shared (amortized) while others are exclusive. The joint burden equals the exclusive costs plus the amortized shared cost, which is max(individual) on the shared channels.

**No Interference (Case 4)**: PVR-3 (the free-option monotonicity theorem from tranche 3) guarantees that adding an optional capability cannot reduce optimal performance on the original capability. Interference requires a load-bearing coupling that removes an old feasible solution, which the A4 contract's frozen accounting prevents.

---

## 3. Negative Twin

The **negative twin** of the interaction classification is:

- Two capabilities that **interfere** (joint > sum)
- This is ruled out by PVR-3 under the A4 contract's frozen accounting
- Interference would require a mandatory maintenance cost from the same hard budget with no compensating benefit

---

## 4. Falsifier

An instance where:
- Two capabilities from the A4 contract interfere (joint > sum) under the declared resource channels, OR
- Two capabilities with no shared resource channels are not independent, OR
- Two capabilities with full resource overlap are not synergistic

---

## 5. Scope Boundary

This theorem establishes:
- A classification of pairwise interactions based on resource channel overlap
- The guarantee that no pair interferes under PVR-3

This theorem does NOT establish:
- G6 morphology-to-capability prediction
- Empirical universality of interaction types
- That synergy is always beneficial (cost-benefit depends on specific values)

---

## 6. Parent Subtraction

- **Independence**: Direct consequence of additivity over disjoint resource sets
- **Synergy**: Amortization over shared resources (well-known in resource pooling)
- **Redundancy**: Maximum over shared channels with exclusive additions
- **PVR-3 (no interference)**: Free-option monotonicity from tranche 3

The GMI contribution is the architecture-independent registration of all 27×27 pairwise interactions under one formal framework with explicit falsifiers.

---

## 7. Reference to Tranche Theorems

| Interaction Type | Tranche Theorem | Status |
|-----------------|-----------------|--------|
| Memory × Planning | MP (tranche 1) | PROVED_BOUNDED |
| Memory × Abstraction | MA (tranche 1) | PROVED_BOUNDED |
| Search × Heuristic | SH (tranche 1) | PROVED_BOUNDED |
| Social × Communication | SC (tranche 1) | PROVED_BOUNDED |
| Communication × Teaching | tranche 2 | PROVED_BOUNDED |
| Teaching × Culture | tranche 2 | PROVED_BOUNDED |
| Metacognition × Allocation | tranche 2 | PROVED_BOUNDED |
| Causal × Planning | tranche 2 | PROVED_BOUNDED |
| Tool × Verification | tranche 2 | PROVED_BOUNDED |
| Joint-Only Thresholds | JT (tranche 3) | PROVED_BOUNDED |
| Interference | IF (tranche 3) | PROVED_BOUNDED |

All 11 registered F3 rows are covered at bounded finite scope.
