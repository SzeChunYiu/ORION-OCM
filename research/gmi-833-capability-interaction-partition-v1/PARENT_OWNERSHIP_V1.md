# Parent ownership disclosure — gmi-833-capability-interaction-partition-v1

Assimilation-first: absorb the strongest parent, then state the delta. Nothing below is
claimed novel unless it appears in Section 3.

---

## 1. In-corpus parents (the strongest ones, absorbed unchanged)

| parent | what it owns | status here |
|---|---|---|
| `CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1`, Lemma A (#976 L58 revival chain, commit `c4def870`, blob `a9a67f8e`) | disjoint-channel additivity `joint = sum`, unconditional | **used unchanged**; it is clause 1 of CIP-3 in the A4 instance |
| same, Lemma B | the bounds `max <= joint_c <= sum` per shared channel and the nested / disjoint / partial equality characterization, by inclusion–exclusion on claim sets | **used unchanged**; CIP-1 is built on these bounds, CIP-2b is its subadditivity half, CIP-4 only pins `mu` so the stated `iff`s are exact |
| same, Lemma C | free-option monotonicity by feasible-set inclusion | **used unchanged**; it is the justification for CIP-1's monotonicity axiom (M) |
| same, CE-1 / CE-2 | the two boundary counterexamples (`joint = max` fails for disjoint within-channel claims; no-interference fails under mandatory upkeep) | **used unchanged**; CE-2 is the reason `INTERFERING` is retained in CIP-1 rather than deleted |
| same, the per-channel claim-set mechanism `Q_X(c)` and `B(A) = Σ_c mu(∪ Q_X(c))` | the accounting itself | **used unchanged** |
| `interactions_witness.py` `RESOURCE_CHANNELS` (frozen A4 27-row assignment, blob `70de5ec7`) | the input data | **used unchanged**; all three routes are checked against it pair-by-pair |
| `gmi-capability-interactions-v{1,2,3}` tranche theorems | the pairwise interaction results the unified capsule synthesizes | untouched |

**Explicitly NOT claimed novel, and explicitly NOT attacked:** Lemmas A, B and C are sound.
The `joint` bounds, the claim-set mechanism, the counterexamples CE-1/CE-2, and the A4
channel assignment are all the parents'. This tranche corrects the **naming/classification
layer only** — Section 1.2's table and Corollary CI-A4's label assignment.

## 2. External parents

| work | what it owns | relation |
|---|---|---|
| G. L. Nemhauser, L. A. Wolsey, M. L. Fisher, "An analysis of approximations for maximizing submodular set functions—I", *Mathematical Programming* **14**(1):265–294, 1978. doi:[10.1007/BF01588971](https://doi.org/10.1007/BF01588971) | submodular / coverage set functions; the cardinality-of-union functional and its diminishing-returns structure | the source of `max <= joint <= sum` under union accounting. CIP-1 adds nothing to this inequality. |
| L. Lovász, "Submodular functions and convexity", in *Mathematical Programming: The State of the Art*, Springer, 1983, pp. 235–257. doi:[10.1007/978-3-642-68874-4_10](https://doi.org/10.1007/978-3-642-68874-4_10) | the canonical treatment of submodularity | same; the "joint cost lies between the max and the sum" intuition is entirely classical |
| J. Edmonds, "Submodular Functions, Matroids, and Certain Polyhedra" (1970), reprinted in *Combinatorial Optimization — Eureka, You Shrink!*, LNCS, Springer, 2003, pp. 11–26. doi:[10.1007/3-540-36478-1_2](https://doi.org/10.1007/3-540-36478-1_2) | the foundational submodular-function framework | same |
| G. M. Amdahl, "Validity of the single processor approach to achieving large scale computing capabilities", *AFIPS '67 (Spring)*, 1967, p. 483. doi:[10.1145/1465482.1465560](https://doi.org/10.1145/1465482.1465560) | the shared-versus-exclusive resource decomposition that underlies "amortize the shared part, add the exclusive part" | the informal reading of `PARTIAL_SHARING` (`max` on shared, `sum` on exclusive); the arithmetic is classical, not ours |
| Inclusion–exclusion and finite measure theory (textbook) | `mu(A ∪ B) = mu(A) + mu(B) − mu(A ∩ B)`; monotonicity; strict positivity | CIP-4's proof is a two-line application; the content of CIP-4 is identifying **which** hypothesis the shipped `iff`s need |

All four DOIs above were resolved against the Crossref API during this tranche and the
title/author/year/pages shown match what Crossref returned. No DOI is asserted for any work
not listed here.

## 3. Named residual contribution of this tranche

Everything in Sections 1 and 2 is the parents'. What is left over, and is claimed at G2:

1. **The measurement (CIP-2, DEF-1/DEF-2/DEF-3).** That the shipped Corollary CI-A4's labels
   contradict the shipped Section 1.2 on **56 of 351** A4 pairs, that Section 1.2's four
   conditions fail to partition on **287 of 351**, and that
   `interactions_witness.verify_no_interference()` is vacuous. These are facts about a GREEN
   mainline object, reproduced from the frozen blobs, not known to the parents.
2. **The `max < sum` guard, and its proof of necessity and harmlessness (CIP-1).** Adding the
   guard to `REDUNDANT` is what turns the classical bound chain into an exact partition. The
   two halves — that without it the degenerate `max = sum` triple lands in two classes, and
   that with it no triple is orphaned because (M) makes the `joint < sum` branch vacuous when
   `max = sum` — are the tranche's own.
3. **Monotonicity (M) named as an admissibility axiom rather than a consequence.** Union
   accounting makes `joint >= max` a theorem; the partition must also cover CE-2 accounting,
   where the upper bound is gone. Fixing the admissible region by axiom is what lets
   `INTERFERING` stay in the taxonomy without breaking exclusivity — and makes `joint < max`
   a **rejected** input rather than a silently misclassified one.
4. **Corollary CIP-1a (`SAVING = REDUNDANT ⊔ PARTIAL_SHARING`).** The statement that the
   repair is a *refinement* of the original `Synergistic` class, so nothing is deleted.
5. **Theorem CIP-3.** The exact correspondence-and-divergence statement between the
   channel-overlap predicate and the burden classification: coincidence on `INDEPENDENT`
   (which is why the 8-pair control passes), non-uniqueness on the `equal` fibre, and a
   proved split of the `partial` fibre by the **nesting predicate** — with the 56 divergent
   pairs named individually.
6. **CIP-4's demonstration that strict positivity is load-bearing** — the explicit
   non-strictly-positive `mu` under which Lemma B's `iff nested` fails, checked exhaustively
   over all subset pairs with exact rationals.
7. **Theorem CIP-2b** replacing the vacuous interference check with a proved, non-vacuous one.

## 4. What this tranche does NOT claim

- No #833 issue row. See `FREEZE_V1.md`: *"No neighbouring row is earned here."*
- No claim above ceiling **G2**.
- No generalization of the 351-pair census beyond the frozen 27-row A4 contract under its
  registered fully-shareable/nested accounting.
- No novelty for submodularity, inclusion–exclusion, or the `max <= joint <= sum` bound.
- No weakening, narrowing or downgrading of Theorem CI-U or Corollary CI-A4.
