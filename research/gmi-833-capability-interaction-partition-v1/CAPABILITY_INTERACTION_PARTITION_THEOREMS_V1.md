# Capability Interaction Partition — named theorems V1 (CIP-1 … CIP-4)

**Package**: `gmi-833-capability-interaction-partition-v1`
**Status**: CORRECTION of a GREEN mainline object — `CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1`
(Theorem CI-U + Corollary CI-A4), prior disposition GREEN, confirmed OVERSTRONG by the #939
verdict table and revived under the #976 L58 revival chain.
**Claim ceiling**: G2. **Evidence class**: P1 (formal) + P2 (finite-exact controls).
**Freeze**: `FREEZE_V1.md`, committed before any implementation commit in this package.

---

## 0. What is being corrected, and what is NOT

Section 1.2 of the shipped theorem defines four interaction types by **burden relations**:
`Independent: joint = sum`, `Redundant: joint = max`, `Synergistic: joint < sum`,
`Interfering: joint > sum`. Corollary CI-A4 then assigns those same four names from
**channel-set overlap alone** (`interactions_witness.interaction_type`): no shared channels
→ `independent`; all channels shared → `synergistic`; partial overlap → `redundant`. No
burden is ever computed.

Measured on the real 27-capability A4 contract (351 unordered pairs), in the corollary's own
fully-shareable/nested accounting (`joint = |R(X) ∪ R(Y)|`, `individual = |R(X)|`):

- **DEF-1** — **56 / 351** shipped labels are FALSE by Section 1.2's own defining condition.
  Canonical witness: `cap-perception` ({S,T}) × `cap-communication` ({S,M}) is labelled
  `redundant`, defined `joint = max`, while `B(X)=2, B(Y)=2, max=2, joint=3, sum=4` — so
  `max = 2 < joint = 3`, and the defining equality simply does not hold.
- **DEF-2** — **287 / 351** pairs satisfy more than one Section 1.2 label, so the four-class
  taxonomy does not partition: `Redundant` (`joint = max`) is a strict sub-case of
  `Synergistic` (`joint < sum`) whenever `max < sum`.
- **DEF-3** — `interactions_witness.verify_no_interference()` is **vacuous**:
  `interaction_type()` has no `"interfering"` return path, so the function cannot return
  `False`. Section 3 (Negative Twin) and the MANIFEST falsifier both rested on it.

**NOT under attack.** Lemmas A, B and C are SOUND and are not weakened here. Lemma A
(disjoint channels ⇒ `joint = sum`) is unconditional. Lemma B's bounds and its
nested/disjoint/partial equality characterization are correct **under counting measure on a
finite unit set**, which is exactly what the code implements (`len(qx | qy)`); CIP-4 only
pins that hypothesis down so the `iff`s are exact as stated. Lemma C's feasible-set-inclusion
argument is correct. CE-1 and CE-2 are correct, and CE-2 is the reason the `INTERFERING`
class is **retained** below rather than deleted.

The defect is confined to the **naming/classification layer**: Section 1.2's table and
Corollary CI-A4's label assignment.

---

## 1. CIP-1 — the exact partition theorem

### Setup

Let `X, Y` be capabilities. Write

- `B(X), B(Y) ∈ R_{>=0}` for their individual burdens,
- `J = B({X,Y})` for the joint burden under the ambient accounting,
- `m = max(B(X), B(Y))`, `s = B(X) + B(Y)`.

`J` is a general burden functional. It is **not** assumed to be union accounting: CE-2
exhibits accountings where `J > s`.

### Axioms of admissibility

- **(N) Non-negativity.** `B(X) >= 0` and `B(Y) >= 0`.
- **(M) Monotonicity.** `J >= m`.
  *Justification.* The joint system must satisfy both capabilities' claims, so its feasible
  set is contained in each single-capability feasible set (the same inclusion argument as
  Lemma C). Running the pair can never cost less than running the more expensive one alone.
  Under union accounting (M) is a theorem, not an assumption: `|Q_X ∪ Q_Y| >= |Q_X|` channel
  by channel. Outside it, (M) is what fixes the region on which the classification is
  defined; a functional with `J < m` is **inadmissible** and is rejected, not silently
  absorbed into a class (hostile (e)).

**Lemma 1.0.** Under (N), `m <= s`.
*Proof.* `s - m = min(B(X), B(Y)) >= 0`. ∎

So every admissible pair satisfies `m <= J` and `m <= s`, with no a-priori relation between
`J` and `s`.

### The four classes

| class | condition |
|---|---|
| `INDEPENDENT` | `J = s` |
| `REDUNDANT` | `J = m` **and** `m < s` |
| `PARTIAL_SHARING` | `m < J < s` |
| `INTERFERING` | `J > s` |

### Theorem CI P-1 (exact partition)

*For every pair `(X, Y)` satisfying (N) and (M), exactly one of the four classes applies.*

**Proof — exhaustiveness.** Trichotomy on `J` versus `s`.
1. `J > s` ⇒ `INTERFERING`.
2. `J = s` ⇒ `INDEPENDENT`.
3. `J < s`. By (M), `m <= J`, hence `m <= J < s` and in particular `m < s`. Either `J = m`,
   giving `J = m` and `m < s` ⇒ `REDUNDANT`; or `m < J`, giving `m < J < s` ⇒
   `PARTIAL_SHARING`.
Every admissible pair falls in case 1, 2 or 3. ∎

**Proof — mutual exclusivity.** Sort by `J` versus `s`. `INTERFERING` needs `J > s`;
`INDEPENDENT` needs `J = s`; `REDUNDANT` needs `J = m < s`, hence `J < s`; `PARTIAL_SHARING`
needs `J < s`. The three buckets `J > s`, `J = s`, `J < s` are disjoint, so the only pair
that could collide is `REDUNDANT` versus `PARTIAL_SHARING`; the first needs `J = m`, the
second needs `m < J`. Disjoint. ∎

### The degenerate case `m = s` (explicitly)

`m = s` ⟺ `min(B(X), B(Y)) = 0`, i.e. one capability has zero burden.

**Why the `m < s` guard is needed.** Suppose `B(Y) = 0`, so `m = B(X) = s`. By (M),
`J >= m = s`. If the accounting is additionally subadditive (`J <= s`, e.g. union
accounting) then `J = s = m`. Without the guard, `INDEPENDENT` (`J = s`) and a guardless
`REDUNDANT` (`J = m`) would **both** hold, and the taxonomy would fail to partition on
exactly this pair. The guard `m < s` removes `REDUNDANT` from this triple and leaves
`INDEPENDENT` alone.

**Why the guard does not break exhaustiveness.** *Claim:* every admissible triple with
`m = s` still lands in exactly one class. *Proof.* With `m = s`, (M) gives `J >= m = s`, so
case 3 of the exhaustiveness proof (`J < s`) is vacuous. Only `J > s` (`INTERFERING`) and
`J = s` (`INDEPENDENT`) remain, and they are disjoint. The guard therefore only ever removes
`REDUNDANT` from triples already covered by `INDEPENDENT`; it never orphans a triple. ∎

**Why `INDEPENDENT` is the right name for it.** Additivity holds exactly (`J = s`) and there
is no saving to speak of: a zero-burden partner cannot amortize anything. `REDUNDANT`'s
semantic content — *the joint costs no more than the more expensive alone, and that is a
strict saving relative to running both* — is precisely what the `m < s` guard encodes.

### Nothing is deleted: the `SAVING` refinement

Define `SAVING := { J < s }` — the shipped `Synergistic` condition verbatim.

**Corollary CIP-1a.** `SAVING = REDUNDANT ⊔ PARTIAL_SHARING` (disjoint union).
*Proof.* `⊇`: both classes require `J < s`. `⊆`: if `J < s` then by (M) `m <= J < s`, so
either `J = m` (with `m < s`) or `m < J < s`. ∎

So the repair is a **refinement**, not a deletion: the old `Synergistic` class survives
intact as a named aggregate and is resolved into its two exact sub-cases. This is exactly
DEF-2's content: the old `Redundant` was the boundary `J = m` *inside* the old `Synergistic`.

### `INTERFERING` is retained, and is not vacuous

**Admissibility of `J > s`.** (M) and (N) do not bound `J` above. Union accounting does
(`J <= s`, by subadditivity of cardinality), but the shipped theorem's own CE-2 exhibits an
accounting outside it: a capability with mandatory upkeep `delta > 0` charged from the same
hard budget as `X` makes the joint burden exceed `sum` by `delta`. The class must therefore
stay in the partition — deleting it would make the taxonomy non-exhaustive on the very
accounting CE-2 constructs (hostile (b) demonstrates this: a three-class map places the CE-2
triple in **zero** classes).

**Theorem CIP-2b (interference is empty on the A4 instance — proved, not assumed).**
Under union accounting, `J = Σ_c mu(Q_X(c) ∪ Q_Y(c)) <= Σ_c [mu(Q_X(c)) + mu(Q_Y(c))] = s`
by subadditivity of `mu`, with equality iff every per-channel intersection is null. Hence
`INTERFERING` is empty for every A4 pair. *Checked non-vacuously on all 351 pairs*: the
classifier computes `J` and `s` and has a reachable `INTERFERING` branch, exercised by the
CE-2 triple. This replaces the shipped `verify_no_interference()`, which could not return
`False` (DEF-3).

---

## 2. CIP-2 — the corrected 27×27 census

**Registered accounting (unchanged from Corollary CI-A4).** Each capability's per-channel
claim is fully shareable: all capabilities using channel `c` claim the *same* single unit of
`c`. So `Q_X(c) = {unit(c)}` for `c ∈ R(X)`, empty otherwise, `mu` = counting measure, and

```
B(X) = |R(X)|        J = |R(X) ∪ R(Y)|        s = |R(X)| + |R(Y)|        m = max(|R(X)|, |R(Y)|)
```

**Theorem CIP-2.** Over the 351 unordered pairs of the frozen 27-row A4 contract:

| class | pairs |
|---|---:|
| `INDEPENDENT` | **8** |
| `REDUNDANT` | **287** |
| `PARTIAL_SHARING` | **56** |
| `INTERFERING` | **0** |
| total | 351 |

against the shipped census `independent 8, synergistic 161, redundant 182, interfering 0`.
**217 of 351 labels change.** The complete per-pair delta is `DELTA_TABLE_V1.md` (generated,
not transcribed) and `RESULT_V1.json` (`per_pair`, all 351 rows).

**Corollary CIP-2a (the two defect sets are exactly two classes).**
- The DEF-1 set (shipped label false by Section 1.2) is **exactly** `PARTIAL_SHARING`
  (56 pairs). *Reason:* the shipped classifier returns `redundant` for any partial channel
  overlap, and on the non-nested sub-case `m < J`, refuting `J = max`.
- The DEF-2 set (non-unique Section 1.2 label) is **exactly** `REDUNDANT` (287 pairs).
  *Reason:* `J = m < s` satisfies both `J = m` (Redundant) and `J < s` (Synergistic).

Both identities are checked pair-by-pair in `test_partition_v1.py`.

---

## 3. CIP-3 — correspondence and divergence, EARNED-BY-COUNTEREXAMPLE

Let `O(X,Y) ∈ {disjoint, equal, nested-proper, non-nested-overlap}` be the relation of the
channel sets, and let `O*(X,Y) ∈ {disjoint, equal, partial}` be the coarser signature the
shipped classifier actually tests (it distinguishes only *empty intersection*, *set
equality*, and *everything else*). Let `K(X,Y)` be the CIP-1 class.

**Theorem CIP-3.** Under the A4 registered nested/fully-shareable accounting, with every
`R(C)` nonempty:

1. **Exact coincidence on `INDEPENDENT`.**
   `K = INDEPENDENT ⟺ R(X) ∩ R(Y) = ∅`.
   *Proof.* `s - J = |R(X) ∩ R(Y)|` by inclusion–exclusion, so `J = s ⟺ |R(X) ∩ R(Y)| = 0`.
   ∎ This is why the 8-pair no-alarm control passes: on this class the channel-overlap
   *predicate* and the burden *classification* agree exactly.
2. **The `equal` fibre is a single class, but not the one the shipped label names.**
   `R(X) = R(Y)` (nonempty) ⇒ `J = m = |R(X)| < 2|R(X)| = s` ⇒ `K = REDUNDANT`.
   The shipped label here is `synergistic`, whose Section 1.2 condition `J < s` does hold —
   just not uniquely (DEF-2). 161 pairs.
3. **The `partial` fibre SPLITS — this is the divergence.**
   `R(X) ∩ R(Y) ≠ ∅` and `R(X) ≠ R(Y)` ⇒ `K = REDUNDANT` if one set properly contains the
   other (126 pairs), and `K = PARTIAL_SHARING` otherwise (56 pairs). Both occur, so `K` is
   **not** a function of `O*`.
   *Proof.* `J = m ⟺ |R(X) ∪ R(Y)| = max(|R(X)|, |R(Y)|) ⟺ R(X) ⊆ R(Y)` or `R(Y) ⊆ R(X)`.
   Nesting is invisible to `O*`, which only tests intersection-nonemptiness and equality. ∎
4. **The exact refinement.** `K` **is** a function of `O` (the nesting-aware relation):
   `disjoint ↦ INDEPENDENT`, `equal ↦ REDUNDANT`, `nested-proper ↦ REDUNDANT`,
   `non-nested-overlap ↦ PARTIAL_SHARING`. The minimal refinement of `O*` that determines
   `K` is therefore the **nesting predicate**, not the Jaccard/intersection overlap.

**Counterexample mapping the boundary (label: EARNED-BY-COUNTEREXAMPLE, in the style of
CE-1/CE-2).** `cap-perception` ({S,T}) × `cap-communication` ({S,M}):
`B(X)=2, B(Y)=2, m=2, J=3, s=4`. The shipped classifier returns `redundant`, whose Section
1.2 definition is `J = max`; but `J = 3 ≠ 2 = max`. This single pair refutes "channel overlap
determines the burden class" and, together with clause 1, locates the divergence exactly:
the overlap predicate is correct on `INDEPENDENT`, correct-but-non-unique on `equal`, and
**wrong on the 56 non-nested partial-overlap pairs**.

**Hypothesis used.** Every A4 capability has a nonempty channel set (verified: all 27 do).
Without it, a capability with `R(C) = ∅` is disjoint from everything *and* nested in
everything, and clause 1's `⟸` would need the degenerate-case argument of CIP-1 instead.

---

## 4. CIP-4 — Lemma B precision: `mu` is counting measure (strict positivity is load-bearing)

The shipped text says only "`mu` measures claim size". Lemma B's equality characterizations
are stated as `iff`s:

- `mu(Q_X ∪ Q_Y) = max` **iff** the claims are nested;
- `mu(Q_X ∪ Q_Y) = sum` **iff** the claims are disjoint.

**Theorem CIP-4.** Let `mu` be additive and non-negative on subsets of a finite unit set.

1. *(the `if` directions need nothing extra)* If `Q_X ⊆ Q_Y` then `Q_X ∪ Q_Y = Q_Y`, so
   `mu(Q_X ∪ Q_Y) = mu(Q_Y) = max(mu Q_X, mu Q_Y)` by monotonicity. If `Q_X ∩ Q_Y = ∅` then
   additivity gives `mu(Q_X ∪ Q_Y) = mu(Q_X) + mu(Q_Y)`. ∎
2. *(the `only if` directions need STRICT POSITIVITY)* Assume
   **(P) `mu(A) = 0 ⇒ A = ∅`** (equivalently `mu({u}) > 0` for every unit `u`). If
   `mu(Q_X ∪ Q_Y) = max(mu Q_X, mu Q_Y)`, take WLOG `mu(Q_Y) >= mu(Q_X)`; writing
   `Q_X ∪ Q_Y = Q_Y ⊔ (Q_X \ Q_Y)` and using additivity,
   `mu(Q_X \ Q_Y) = mu(Q_X ∪ Q_Y) − mu(Q_Y) = 0`, so by (P) `Q_X \ Q_Y = ∅`, i.e.
   `Q_X ⊆ Q_Y`. Likewise `mu(Q_X ∪ Q_Y) = mu(Q_X) + mu(Q_Y)` forces
   `mu(Q_X ∩ Q_Y) = 0`, hence `Q_X ∩ Q_Y = ∅`. ∎
3. **Counting measure on a finite unit set satisfies (P)** (`mu({u}) = 1 > 0`), which is what
   `interactions_witness.py` and `ci_universal_witness_v1.py` actually implement
   (`len(qx | qy)`). Lemma B's `iff`s are therefore exact as stated for the implemented
   theory.

**(P) is load-bearing, not decoration — explicit counterexample.** Take
`U = {u1, u2, u3}` with `mu({u1}) = mu({u2}) = 1` and `mu({u3}) = 0`, extended additively.
Let `Q_X = {u1}`, `Q_Y = {u3}`. Then
`mu(Q_X ∪ Q_Y) = mu({u1,u3}) = 1 = max(1, 0)`, yet `Q_X ⊄ Q_Y` and `Q_Y ⊄ Q_X`: the claims
are **not** nested. The `iff nested` direction fails. (`mu(Q_X) = 1`, `mu(Q_Y) = 0`, all
values exact rationals.) The same measure breaks `iff disjoint`: `Q_X = {u1,u3}`,
`Q_Y = {u2,u3}` give `mu(union) = 2 = mu(Q_X) + mu(Q_Y)` with `Q_X ∩ Q_Y = {u3} ≠ ∅`.

The exhaustive check over all `2^3 × 2^3` subset pairs is `lemma_b_nested_iff` — `True` for
counting measure, `False` with the null unit, both computed with `fractions.Fraction`.

---

## 5. Scope, quantifiers, assumptions, falsifiers

| result | scope / quantifiers | assumptions | falsifier |
|---|---|---|---|
| CIP-1 | every pair `(X,Y)` with real non-negative burdens and any burden functional `J` | (N), (M) | an admissible triple in 0 or ≥2 classes |
| CIP-1a | same | same | a pair with `J < s` outside `REDUNDANT ∪ PARTIAL_SHARING` |
| CIP-2 | the 351 unordered pairs of the frozen 27-row A4 contract | registered fully-shareable/nested accounting; `mu` = counting measure | any pair whose class differs between routes A, B, C |
| CIP-2b | the same 351 pairs, union accounting | subadditivity of `mu` | an A4 pair with `J > s` |
| CIP-3 | the same 351 pairs, all `R(C)` nonempty | as CIP-2 | an `INDEPENDENT` pair with intersecting channels, or a non-nested partial-overlap pair that is not `PARTIAL_SHARING` |
| CIP-4 | finite unit set, additive non-negative `mu` | (P) for the `only if` directions | a proof of `J = max ⇒ nested` that does not use (P) |

## 6. Strongest parents

- **Shipped Lemmas A/B/C and CE-1/CE-2** (`CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1`,
  #976 L58 revival chain, commit `c4def870`) — the claim-set mechanism, the bounds, and the
  two boundary counterexamples are *theirs*, are correct, and are used unchanged here. CIP-1
  is built on Lemma B's bounds; CIP-2b is Lemma B's subadditivity; CIP-4 sharpens Lemma B's
  hypothesis rather than replacing the lemma.
- **Inclusion–exclusion / submodularity of counting measure** (classical). `m <= J <= s` is
  the standard union bound; CIP-1's content is not that inequality but the *partition* the
  three-way comparison induces, and the `m < s` guard that makes it exact at the degenerate
  point.
- See `PARENT_OWNERSHIP_V1.md` for the full disclosure and the named residual.

## 7. Forbidden extrapolations

- CIP-2's counts are for the **frozen 27-row A4 contract under its registered
  fully-shareable/nested accounting only**. They do not transfer to another contract, to a
  different claim registration, or to ordered pairs.
- CIP-2b's "no interference" is a statement about **union accounting**, not about capability
  interaction in general. CE-2 accounting violates it, by construction.
- CIP-1 says nothing about *which* class a given real system falls into; it fixes the
  taxonomy, not the physics.
- Nothing here raises the claim ceiling above **G2**, and nothing here closes a #833 row.
