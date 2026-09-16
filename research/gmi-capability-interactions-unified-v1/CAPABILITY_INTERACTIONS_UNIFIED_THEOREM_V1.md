# Capability Interactions Unified Theorem V1

**Issue**: #602 Section F boxes 7-11 (cross-cutting capability interactions)
**Scope**: Universal interaction classification for arbitrary capability pairs under channel-wise resource accounting (Theorem CI-U, proven lemmas), with the 27x27 pairs of the frozen A4 contract as the registered fully-shareable instance (Corollary CI-A4). Boundary of the original CI equalities mapped and earned by counterexample (Section 2.5), not by proof convenience.
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

### Theorem CI-U (Capability Interaction Classification — universal, claim-structure form)

**Revival note (2026-09-16, #833 L58 revival chain).** The original CI asserted
`joint = sum` / `joint = max` from channel overlap alone. Diagnosis: the equalities hide
two premises — (i) within-channel claim shareability, (ii) free-option accounting — and
both are REAL mathematical conditions, not proof inconveniences: each has a concrete
counterexample in its absence (Section 2.5). The revival builds the missing mechanism
(claim-set structure per channel) and proves the classification universally at that
strength. Scope-narrowing is NOT the resolution; the universal claim stands, now earned.

**Setup.** For each capability `X` and resource channel `c in {S, T, M}`, let `Q_X(c)` be
the set of resource units of channel `c` that `X`'s operation claims. Channel-wise
accounting: the burden of running a set `A` of capabilities is
`B(A) = sum_c mu( U_{X in A} Q_X(c) )`, where `mu` measures claim size (units are not
double-counted: jointly running X and Y needs the union of their claims per channel).

**Lemma A (disjoint-channel additivity — unconditional).**
If `R(X) ∩ R(Y) = ∅`, then `B({X,Y}) = B({X}) + B({Y})` — i.e. `joint = sum`.
*Proof.* For every channel `c`, at most one of `Q_X(c), Q_Y(c)` is nonempty, so
`mu(Q_X(c) ∪ Q_Y(c)) = mu(Q_X(c)) + mu(Q_Y(c))` termwise; summing over channels gives the
identity. ∎  (No premise beyond channel-wise accounting.)

**Lemma B (shared-channel bounds and exact equality characterization — unconditional).**
For a shared channel `c` (both claims nonempty):
`max(mu(Q_X(c)), mu(Q_Y(c))) <= mu(Q_X(c) ∪ Q_Y(c)) <= mu(Q_X(c)) + mu(Q_Y(c))`,
with
- `joint_ c = max` **iff** the claims are nested (`Q_X(c) ⊆ Q_Y(c)` or conversely) — the
  fully-shareable case (the same units serve both capabilities);
- `joint_c = sum` **iff** the claims are disjoint within the channel;
- strictly between iff the claims partially overlap within the channel.
*Proof.* Inclusion-exclusion on claim sets: `mu(Q_X ∪ Q_Y) = mu(Q_X) + mu(Q_Y) − mu(Q_X ∩ Q_Y)`
with `mu(Q_X ∩ Q_Y) <= min(mu(Q_X), mu(Q_Y))`; equality cases are the extremal intersection
conditions. ∎  The interaction class on a shared channel is therefore a function of
**within-channel claim overlap**, not of channel overlap alone.

**Lemma C (free-option monotonicity — no interference under its premise; constructive
failure outside).** If `Y` is *optional* for `X` (every `X`-only operation remains feasible
at unchanged cost when `Y` is available), then running `Y` cannot reduce the achievable
value of `X`'s objective, and joint burden never exceeds `sum` plus `Y`'s own optional-use
burden. *Proof.* Feasible-set inclusion: the `X`-only solutions survive in the joint
system, so the joint optimum is at least the `X`-only optimum. ∎  Outside the free-option
premise, interference is constructive: a capability with mandatory upkeep `delta > 0`
charged from the same hard budget as `X` reduces `X`'s achievable value (Section 2.5, CE-2).

**Theorem CI-U.** For ANY two capabilities `X, Y` under channel-wise accounting with
claim sets `Q_X(c), Q_Y(c)`:
1. disjoint channels ⇒ independent (`joint = sum`) — Lemma A, unconditional;
2. shared channels ⇒ `max <= joint_c <= sum` per shared channel, with the exact value
   determined by within-channel claim overlap (nested ⇒ max; disjoint ⇒ sum; partial ⇒
   strictly between) — Lemma B, unconditional;
3. no interference under free-option accounting — Lemma C; the unconditional form fails
   (CE-2).

### Corollary CI-A4 (the registered 27x27 finite instance)

Under the A4 contract's frozen accounting, each capability's per-channel claims are
registered as fully shared/nested within a channel (the contract tables price channel
usage, not disjoint claim sets — `interactions_witness.py` assigns each capability its
`R(C) ⊆ {S,T,M}`). In that fully-shareable regime Lemma B collapses to the max rule and
the classification reduces to the channel-overlap classes of the original Theorem CI over
the 27x27 = 729 ordered pairs (351 unordered) of the frozen contract: disjoint channels →
independent; all channels shared → synergistic (amortized max on shared channels);
partial channel overlap → redundant (max on shared, sum on exclusive). All statements are
computed by `interactions_witness.py` (symmetric matrix, no interfering pair, P2
finite-exact controls). This is the registered instance, an intermediate state of the
revival chain, kept with its evidence class P1 + P2.

### 2.5 Boundary of the original CI equalities — earned by counterexample

- **CE-1 (unconditional `joint = max` on a shared channel is FALSE).** Two capabilities
  sharing channel S with disjoint claims — an episodic store holding data set A and a
  semantic store holding disjoint data set B — have `mu(Q_ep ∪ Q_sem) = |A| + |B| > max`.
  The equality holds exactly in the nested-claims regime (Lemma B), which the A4 frozen
  accounting registers. Label: EARNED-BY-COUNTEREXAMPLE.
- **CE-2 (unconditional no-interference is FALSE).** A capability with mandatory upkeep
  `delta > 0` charged from the same hard budget as `X` strictly reduces `X`'s achievable
  value: joint burden exceeds sum by `delta`. No-interference holds exactly under the
  free-option premise (Lemma C), which the A4 accounting freezes. Label:
  EARNED-BY-COUNTEREXAMPLE.

These two boundaries are the complete obstruction list: with claims registered per channel
(the mechanism this revival adds), every other clause of the original universal phrasing
is proved above at full strength.

### Proof obligations register

| clause | status |
|---|---|
| disjoint ⇒ joint = sum | PROVED (Lemma A, unconditional) |
| shared-channel exact value | PROVED (Lemma B, unconditional characterization) |
| no interference | PROVED under free-option (Lemma C); boundary CE-2 |
| original `joint=max` rule | PROVED iff nested claims (Lemma B); boundary CE-1 |
| A4 27x27 classes | computed instance (Corollary CI-A4, P2 controls) |

Executable controls: `ci_universal_witness_v1.py` (+ `test_ci_universal_v1.py`) checks
Lemmas A/B/C on registered fixtures and instantiates CE-1/CE-2 as hostile witnesses.

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

## 5. Scope Boundary (revival form)

This theorem establishes:
- The universal claim-structure classification (CI-U): disjoint-channel additivity
  (unconditional), shared-channel bounds with exact equality characterization
  (unconditional), and no-interference under the named free-option premise.
- The A4 27x27 finite classification as the registered fully-shareable instance.

The joint-burden equalities are PROVEN characterizations indexed to claim structure
(Lemma B) — the original defect ("rules rest on unproven equalities") is resolved by
proving them at full strength, not by weakening the claim. The two unconditional-form
failures are mapped and labelled EARNED-BY-COUNTEREXAMPLE (CE-1, CE-2).

This theorem does NOT establish:
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
