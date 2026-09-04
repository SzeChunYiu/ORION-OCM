# Lane #201 terminal record — authority-indexed representation lattice, selective reopening

**Terminal: `PARENT_SUFFICIENT`.**
**Residual `CERTIFIED_REPRESENTATION_RESIDUAL`: `NOT_EARNED`.** The one theorem this lane adds beyond
its parents is a conservation statement (L4) that *refutes the matched-resource reading* of the
conjecture; it is architecture-neutral and elementary.

Date: 2026-09-04 · Umbrella: #194 · Execution master: #197 · Lane: #201
Exact checker: `reference/ocm_lane201_lattice_exact.py` · Tests: `tests/unit/test_ocm_lane201_lattice_exact.py`

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** The four retracted comments on #201 (2026-09-03) are
respected: nothing from them is reused; every object below is derived and checked afresh.

## 0. Substrate-form restatement (operator directive, #194 comment 5539487737, 2026-09-04)

Under the directive this lane is the *representation half of constraint (c)*: a self-extending
machine that revises its own representation must do so **without losing exact authority over what
it already knows**. L1–L6 below are the constraint made exact, not a target: the coarsest
authority-preserving representation exists and is the meet of the registered kernels (L1); any
saving from holding a coarser representation is a relocation of state into later access, never a
free reduction (L4); reopening on revision is sound and minimal exactly on the blocks where the new
query is non-constant (L5); composed authority is scope intersection (L6). The strongest parents own
each statement. The terminal `PARENT_SUFFICIENT` is unchanged; what changes is its role — these are
the invariants the substrate's revision operator must satisfy, and
`reference/ocm_reference_semantics.py` (lane #203) checks them on the executable substrate.

## 1. What the lane asked

> A machine that selects the coarsest representation carrying a certificate sufficient for the
> current query can obtain a strict active-state or communication advantage over any single
> representation preserving all registered queries, while soundly and minimally reopening state
> when the query, criterion or authority scope changes.

## 2. Model

Finite worlds `Omega`; registered queries `Q`, each a function `q: Omega -> A_q`; a representation
is a partition `P` of `Omega` (the machine holds the block of the true world); `P` is *sufficient*
for `q` iff `q` is constant on every block. Order partitions by refinement (`P <= P'` iff `P` is
finer). Active state of `P` is `ceil(log2 |P|)` bits (Hartley).

## 3. L1 — the coarsest sufficient representation is the meet of the kernels

**Theorem L1.** For any `Q' ⊆ Q` the coarsest partition sufficient for every `q ∈ Q'` exists, is
unique, and equals the common refinement `meet_{q∈Q'} ker q`.

*Proof.* `P` is sufficient for `q` iff `P` refines `ker q`. The set of partitions refining every
`ker q` has a unique coarsest element, their meet in the partition lattice (the lattice is complete
and finite). ∎ The checker verifies coarsest-ness by the complete pair-merge test: if `P'` is
strictly coarser than `P` and sufficient, then some single pair-merge of `P` refines `P'` and is
sufficient by monotonicity; so "every pair-merge is insufficient" certifies coarsest-ness. It also
enumerates all partitions (4,140 on 8 worlds, 203 on 6) and confirms the meet is the unique
coarsest sufficient one.

*Parents.* Partition lattice (Birkhoff); minimal sufficient statistic as the coarsest sufficient
partition (Fisher 1922, Lehmann–Scheffé 1950); Blackwell 1953 for the decision-theoretic reading.
Disposition `PARENT_OWNED`.

## 4. L2 / L3 — the advantage exists and is Hartley counting

**L2.** Any single representation sufficient for all of `Q` has `>= |meet ker q|` blocks, so
`>= ceil(log2 |meet|)` bits. **L3.** Holding only `ker q_t` costs `max_t ceil(log2 |q_t(Omega)|)`
bits plus routing `ceil(log2 |Q|)`. On the incompatible family "bit `i` of a 3-bit world" the gap
is `3 - 1 = 2` bits; on identical kernels it is `0`. The lane's "incompatible-partition witness
family" is exactly a family of pairwise non-nested kernels; both cases are checked.

*Parents.* Hartley 1928; the per-decision minimal sufficient statistic (Blackwell). The strict gap
is the unmatched-resource reading of the conjecture and is **true but parent-owned**.

## 5. L4 — conservation: the saving is a relocation

A query-relative machine that drops state must recover it from the source when the query changes.
Model the source as answering binary questions at one bit each.

**Theorem L4.** For any deterministic zero-error machine and any query sequence `q_1..q_T`,
`(initial state bits) + (total source-access bits) >= ceil(log2 |meet_t ker q_t|)`.

*Proof.* The answers `(q_1(w),...,q_T(w))` are a function of the initial state and the access
transcript, because each later state is a function of the previous state and that step's accesses.
The answer vector takes `|meet_t ker q_t|` distinct values over `Omega`, so the pair (initial
state, transcript) must take at least that many values. ∎

Consequences checked exactly on the 3-bit family: over all 6 query orders the retentive strategy
pays exactly the meet bits (tight); when every query is asked twice the forgetful (query-relative)
strategy pays `6` against the retentive `3`; a planted "free reopening" strategy that answers
without access where its block does not determine the query is caught with an unsound witness.
So under matched total resources (active state + access) the conjectured strict advantage does not
exist: it is a trade between active state and reopening access.

*Parents.* This is the "no disappearing resource" principle of #194 C3 made exact; the underlying
count is the same decision-tree/communication argument as LI-1. Cell-probe/data-structure
space–query trade-offs (Yao 1981) are the general parent. Disposition: `ARCHITECTURE_NEUTRAL`,
elementary, refutes the matched-resource conjecture.

## 6. L5 — selective reopening soundness and minimality

With stored partition `P` and new query `q'`, the blocks that must be reopened are exactly
`{B ∈ P : q' not constant on B}`.

**Theorem L5.** Answering `q'` on a non-reopened block is sound iff `q'` is constant there (fibre
criterion); reopening a block on which `q'` is constant is unnecessary. Hence the rule is sound and
minimal, and every deviation is either unsound (under-reopening) or non-minimal (over-reopening). ∎

The checker plants both deviations and catches each with the offending blocks listed.

*Parents.* Counterexample-guided abstraction refinement (Clarke, Grumberg, Jha, Lu, Veith 2000):
split exactly the abstract states on which the property is not constant; abstract interpretation
(Cousot–Cousot 1977); truth maintenance / dependency-directed invalidation (Doyle 1979). Disposition
`PARENT_OWNED`.

## 7. L6 — authority index is scope intersection

A composite of components with scopes `S_1..S_m` is soundly authorised only on `∩ S_i`; for any
context outside some `S_i` a countermodel makes that component wrong there. Checked with a planted
union-scope rule (four countermodels found) and an equal-scope no-alarm case. This is WLL-4 restated;
parent: intersection of refinement/trust types. Disposition `PARENT_OWNED`.

## 8. Relation to Warrant Lift (the lane's no-double-claim checkbox)

Warrant Lift is `H_0(L|B) = ceil(log2 max_b |fibre|)` (lane-200 record, Theorem A). The
single-representation bound L2 is `H_0` of the meet partition. Both are the conditional Hartley
entropy of a partition refinement; neither is claimed twice, and neither is claimed as new.

## 9. Lane checklist disposition

| #201 task | Disposition |
|---|---|
| reconstruct parents (sufficient statistics, Blackwell, partition lattices, abstract interpretation/CEGAR, data structures/communication, incremental computation, TMS) | named per theorem (§3–§7); primary full-text reconstruction remains a review obligation |
| freeze world/query/answer/verifier model and access order | §2; access order = one binary question per bit |
| define the lattice and certificate semantics | §2, §7 |
| prove minimal sufficient representations exist | L1 |
| lower bound for any single all-query representation | L2 |
| adaptive query-relative upper bound incl. routing | L3 |
| selective reopening soundness; test minimality; preserve counterexamples | L5; planted counterexamples recorded in the checker output |
| compare against a recurrent Transformer with identical memory/query access | L4 is architecture-neutral: any machine obeys it; no separation |
| incompatible-partition witnesses and two independent checkers | bit family and six-world family; coarsest-ness verified two ways (pair-merge test and full enumeration) |
| compare with Warrant Lift; no double claim | §8 |
| record terminal | `PARENT_SUFFICIENT` |

## 10. Non-consequences and reopen conditions

Supported: L1–L6 as stated, each elementary. Not supported: novelty, priority, architecture
separation, natural-language competence, quantum advantage, publication readiness. No checkbox in
#197 is closed by this file.

Reopens if a representation model with a *charged* access channel yields a strict advantage after
L4's accounting — for instance an access model where refining costs less than the Hartley count —
in which case the parent is the corresponding data-structure lower bound, not this lane.
