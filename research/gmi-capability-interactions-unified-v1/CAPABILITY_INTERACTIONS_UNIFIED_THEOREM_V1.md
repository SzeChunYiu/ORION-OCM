# Capability Interactions Unified Theorem V1

**Issue**: #602 Section F boxes 7-11 (cross-cutting capability interactions)
**Scope**: Universal interaction classification for arbitrary capability pairs under channel-wise resource accounting (Theorem CI-U, proven lemmas), with the 27x27 pairs of the frozen A4 contract as the registered fully-shareable instance (Corollary CI-A4). Boundary of the original CI equalities mapped and earned by counterexample (Section 2.5), not by proof convenience.
**Evidence class**: P1 (formal) + P2 (finite-exact controls)
**Claim ceiling**: G2
**Parent capsule**: Synthesizes tranches 1-3 from `gmi-capability-interactions-v{1,2,3}/`

> ## CORRECTION NOTICE (2026-09-18)
>
> Sections 1.2, 3, 4 and Corollary CI-A4 of this document **were wrong** and have been
> corrected in place by `research/gmi-833-capability-interaction-partition-v1/`
> (Theorems CIP-1 .. CIP-4, receipt `CORRECTION_NOTICE_V1.json`). Measured on this
> document's own 27-capability A4 contract, 351 unordered pairs:
>
> - **DEF-1 — 56 / 351** shipped labels were FALSE by Section 1.2's own defining condition.
>   Witness: `cap-perception` ({S,T}) x `cap-communication` ({S,M}) was labelled `redundant`,
>   defined `joint = max`, while `B(X)=2, B(Y)=2, max=2, joint=3, sum=4`.
> - **DEF-2 — 287 / 351** pairs satisfied more than one Section 1.2 label: the four
>   conditions did not partition, because `Redundant` (`joint = max`) is a strict sub-case of
>   `Synergistic` (`joint < sum`) whenever `max < sum`.
> - **DEF-3** — `interactions_witness.verify_no_interference()` was **vacuous**:
>   `interaction_type()` has no `"interfering"` return path, so it could never return `False`,
>   yet Section 3 and `MANIFEST.json`'s falsifier rested on it.
>
> Root cause: Section 1.2 defines the four types by **burden** relations, while
> `interactions_witness.py:interaction_type()` assigned those same names from **channel-set
> overlap alone**, never computing a burden.
>
> **Lemmas A, B and C and the counterexamples CE-1 / CE-2 are SOUND and are unchanged.** The
> defect was confined to the naming/classification layer. The corrected census is
> `INDEPENDENT 8, REDUNDANT 287, PARTIAL_SHARING 56, INTERFERING 0` against the shipped
> `independent 8, synergistic 161, redundant 182, interfering 0` — **217 of 351 labels
> change**; every changed pair is named in
> `research/gmi-833-capability-interaction-partition-v1/DELTA_TABLE_V1.md`.

---

## 1. Definitions

### 1.1 Resource Channels

Each capability `C_i` in the 27-row A4 contract consumes resources from a finite set of **resource channels**:

- **Storage** (S): persistent state capacity (memory, code, models)
- **Compute** (T): transformation/processing steps (tau)
- **Communication** (M): message width, channel uses, protocol overhead

Let `R(C_i) ⊆ {S, T, M}` denote the resource channels consumed by capability `C_i`.

### 1.2 Interaction Types (CORRECTED — Theorem CIP-1)

Given two capabilities `X` and `Y`, write `B(X), B(Y) >= 0` for their individual burdens, `J`
for the joint burden under the ambient accounting, and

```
m = max(B(X), B(Y))        s = B(X) + B(Y)
```

**Admissibility.** `(N)` non-negativity: `B(X), B(Y) >= 0`, hence `m <= s`. `(M)` monotonicity:
`J >= m` — the joint system must satisfy both capabilities' claim sets, so its feasible set is
contained in each single-capability feasible set (Lemma C's inclusion argument). A functional
with `J < m` is inadmissible and is rejected, not classified.

| Type | Condition | Meaning |
|------|-----------|---------|
| **INDEPENDENT** | `J = s` | no shared resource contention; also the degenerate case in which one capability has zero burden (`m = s`) |
| **REDUNDANT** | `J = m` **and** `m < s` | fully shared: the joint cost equals the more expensive capability alone, and that is a strict saving |
| **PARTIAL_SHARING** | `m < J < s` | partly shared: cheaper than running both, dearer than the more expensive alone |
| **INTERFERING** | `J > s` | resource contention creates super-additive cost |

**Theorem CIP-1.** On the admissible region, **exactly one** of the four classes applies
(proof: trichotomy on `J` vs `s`; if `J < s` then `m <= J < s` by `(M)`, so `m < s` and the
`REDUNDANT` guard is met, and `J = m` or `m < J` splits the remaining two classes). The
`m < s` guard is what makes the classes disjoint at the degenerate point `m = s`, where
`INDEPENDENT` and an unguarded `REDUNDANT` would otherwise both hold; it costs no
exhaustiveness, because `(M)` makes the `J < s` branch vacuous when `m = s`.

**Nothing is deleted.** The former `Synergistic` condition survives verbatim as the named
aggregate `SAVING := { J < s } = REDUNDANT (disjoint union) PARTIAL_SHARING` (Corollary
CIP-1a). `INTERFERING` is retained: CE-2 (Section 2.5) constructs an accounting in which it
is nonempty, so deleting it would make the taxonomy non-exhaustive there.

Full statement, proofs, scope and falsifiers:
`research/gmi-833-capability-interaction-partition-v1/CAPABILITY_INTERACTION_PARTITION_THEOREMS_V1.md`.

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

*Measure hypothesis (pinned 2026-09-18, Theorem CIP-4).* `mu` is **counting measure on a
finite unit set** — equivalently, `mu` is additive, non-negative and **strictly positive**:
`mu(A) = 0 => A = empty`. This is what the implementation computes (`len(qx | qy)`), and the
`iff` characterizations below need it: the `if` directions (nested => max, disjoint => sum)
hold for any monotone additive `mu`, but the converses do not. Counterexample: on
`U = {u1,u2,u3}` with `mu({u1}) = mu({u2}) = 1` and `mu({u3}) = 0`, take `Q_X = {u1}`,
`Q_Y = {u3}`; then `mu(Q_X u Q_Y) = 1 = max(1, 0)` while the claims are NOT nested. So
strict positivity is load-bearing, not decoration.

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

**CORRECTED 2026-09-18 (Theorem CIP-2).** The previous text assigned the four class names
from channel-set overlap alone. That was wrong: the labels contradicted Section 1.2's own
definitions on **56 of 351** pairs (DEF-1), and Section 1.2 did not partition on **287 of
351** (DEF-2).

Under the A4 contract's frozen accounting, each capability's per-channel claims are
registered as fully shared/nested within a channel (the contract tables price channel usage,
not disjoint claim sets — `interactions_witness.py` assigns each capability its
`R(C) ⊆ {S,T,M}`). With `mu` = counting measure this gives, for every pair,

```
B(X) = |R(X)|      J = |R(X) ∪ R(Y)|      s = |R(X)| + |R(Y)|      m = max(|R(X)|, |R(Y)|)
```

and the CIP-1 classes over the 27x27 = 729 ordered pairs (351 unordered) of the frozen
contract are:

| class | condition on the channel sets | pairs |
|---|---|---:|
| `INDEPENDENT` | `R(X) ∩ R(Y) = ∅` | **8** |
| `REDUNDANT` | nested (`R(X) ⊆ R(Y)` or conversely), both nonempty — equal sets included | **287** |
| `PARTIAL_SHARING` | intersecting but **not** nested | **56** |
| `INTERFERING` | — (provably empty under union accounting, Theorem CIP-2b) | **0** |

against the previously shipped `independent 8, synergistic 161, redundant 182,
interfering 0`. **217 of 351 labels change.** The decisive channel-level invariant is
**nesting**, not channel overlap: the old rule could not distinguish `R(X) ⊆ R(Y)` from a
non-nested intersection, and those are exactly the 56 pairs it got wrong (Theorem CIP-3).
Every changed pair is named in
`research/gmi-833-capability-interaction-partition-v1/DELTA_TABLE_V1.md`; all 351 rows are in
`RESULT_V1.json`, computed by three materially independent routes that agree exactly.

`interactions_witness.py:interaction_type()` is retained unchanged as the historical
**channel-overlap predicate** (its docstring now says so); it is NOT a burden classification.
The burden classification is
`research/gmi-833-capability-interaction-partition-v1/partition_witness_v1.py`.

This is the registered instance, kept with its evidence class P1 + P2.

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
| original `joint=max` rule | PROVED iff nested claims (Lemma B, under strictly positive `mu` — CIP-4); boundary CE-1 |
| Section 1.2 taxonomy partitions | PROVED (Theorem CIP-1); was FALSE as previously stated (DEF-2, 287/351) |
| degenerate `max = sum` case | PROVED (CIP-1, the `m < s` guard) |
| A4 27x27 classes | computed instance, CORRECTED (Corollary CI-A4 / Theorem CIP-2; three independent routes, P2 controls) |
| no interference on the A4 instance | PROVED non-vacuously (Theorem CIP-2b); the previous `verify_no_interference()` check was vacuous (DEF-3) |

Executable controls: `ci_universal_witness_v1.py` (+ `test_ci_universal_v1.py`) checks
Lemmas A/B/C on registered fixtures and instantiates CE-1/CE-2 as hostile witnesses.

## 3. Negative Twin (CORRECTED — Theorem CIP-2b)

The **negative twin** of the interaction classification is:

- Two capabilities that **interfere** (`joint > sum`).
- Under the A4 contract's frozen **union accounting** this is provably empty, not merely
  ruled out by fiat: `J = Σ_c mu(Q_X(c) ∪ Q_Y(c)) <= Σ_c [mu(Q_X(c)) + mu(Q_Y(c))] = s` by
  subadditivity of `mu`. Verified by direct computation on all 351 pairs, non-vacuously — the
  classifier computes `J` and `s` and has a reachable `INTERFERING` branch, exercised by the
  CE-2 hostile.
- **The previous check was vacuous (DEF-3).** `interactions_witness.verify_no_interference()`
  calls `interaction_type()`, which has no `"interfering"` return path, so it could never
  return `False`. It proved nothing; Theorem CIP-2b replaces it.
- Interference is nonetheless REAL outside union / free-option accounting: a mandatory
  maintenance cost charged from the same hard budget with no compensating benefit produces
  `J > s` (CE-2). That is why `INTERFERING` remains a class of the CIP-1 partition.

---

## 4. Falsifier

**CORRECTED 2026-09-18.** The third clause below previously read "two capabilities with full
resource overlap are not synergistic", which the corrected classification *satisfies*: equal
channel sets give `J = m < s`, i.e. `REDUNDANT`, and the old clause would therefore have
fired on the repair. It is replaced by the falsifiers the corrected statement actually risks.

An instance where:
- Two capabilities from the A4 contract interfere (`joint > sum`) under the declared resource
  channels and union accounting, OR
- Two capabilities with no shared resource channels are not `INDEPENDENT`, OR
- Two capabilities with identical (or nested, both nonempty) channel sets are not
  `REDUNDANT`, OR
- Two capabilities whose channel sets intersect without nesting are not `PARTIAL_SHARING`, OR
- An admissible burden triple `(m, J, s)` that lands in zero or in two or more of the four
  CIP-1 classes, OR
- A disagreement between the three independent census routes of
  `gmi-833-capability-interaction-partition-v1`.

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

- **`INDEPENDENT`**: direct consequence of additivity over disjoint resource sets
- **`REDUNDANT`** (`J = m < s`): amortization over shared resources, the nested-claims case
  (well-known in resource pooling). *The previous gloss "maximum over shared channels with
  exclusive additions" described `PARTIAL_SHARING`'s arithmetic, not this class.*
- **`PARTIAL_SHARING`** (`m < J < s`): maximum on the shared channels **plus** the sum of the
  exclusive ones — the genuinely mixed case the old three-name taxonomy had no slot for
- **`INTERFERING`** (`J > s`): retained; empty under union accounting (CIP-2b), nonempty under
  CE-2 accounting
- **PVR-3 (no interference)**: free-option monotonicity from tranche 3; see the corrected
  Section 3

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
