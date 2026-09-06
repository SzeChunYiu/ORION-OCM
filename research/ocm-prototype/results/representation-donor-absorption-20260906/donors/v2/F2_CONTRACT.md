# MEG-09 Frontier F2 — multiscale navigation reduces to parent lumpability/intertwining

**Status:** strongest-parent reduction for issue #329 F2. **NO NOVELTY OR NEW CATEGORY-THEORY CLAIM.** For the current finite KSO navigation semantics, the proposed fibre/base commutation problem is already owned mathematically by strong lumpability/intertwining of finite Markov/substochastic kernels. KSO adds a separate three-valued warrant-measurability gate.

## Object

Let a nonempty finite fine KSO state space `V` be partitioned into nonempty, pairwise disjoint fibres `B_1,...,B_m` covering all of `V`. Let `A` be the linear pushforward that sums fine activation mass inside each fibre. For a registered revocation state `R`, let `P_R` be the nonnegative warranted fine transition matrix with every row sum at most one (possibly substochastic because revoked/disabled structure dissipates mass). For a finite nonnegative seed `s`, restart navigation is

`a* = α s + (1-α) P_R^T a*`, `0<α≤1`.

A base transition matrix `Q_R` is a valid projected dynamics when

`A P_R^T = Q_R^T A`.                                         (1)

This is the standard intertwining/strong-lumpability condition. In row form, (1) exists iff for every source fibre `B_i`, every two fine states `x,x'∈B_i`, and every target fibre `B_j`,

`Σ_{y∈B_j} P_R[x,y] = Σ_{y∈B_j} P_R[x',y]`.                  (2)

Substochasticity changes none of the algebra; missing mass may equivalently be sent to a cemetery state.

## Theorem F2.1 — restart fixed points commute with the parent projection

If (1) holds and the base seed is `A s`, then

`A a* = \bar a*`,

where `\bar a*` is the restart fixed point of `Q_R` with seed `A s` and the same `α`.

### Proof

Apply `A` to the fine fixed-point equation:

`A a* = α A s + (1-α) A P_R^T a*`
`      = α A s + (1-α) Q_R^T A a*`.

The right side is exactly the base restart equation. The quotient is nonnegative
substochastic because its row sum is a representative fine row sum. Therefore
`||Q_R^T||_1≤1`, and its restart map contracts in `l1` by at most `1−α<1`.
Existence and uniqueness follow from the convergent Neumann series (or Banach's
fixed-point theorem). Its solution is `\bar a*`. ∎

Equivalently, the result follows termwise from the Neumann series because (1) implies `A(P_R^T)^j=(Q_R^T)^j A` for every `j`.

## Theorem F2.2 — strong lumpability is the exact finite criterion for state-only fibre projection

For a fixed partition and fine kernel, a Markovian base kernel whose transition probabilities depend only on the source fibre exists exactly when (2) holds.

### Proof

If (2) holds, define `Q_R[i,j]` as the common total transition mass from any `x∈B_i` into `B_j`; this gives (1). Conversely, if a base state `i` has one well-defined transition mass to `j`, every fine state projecting to `i` must have that same aggregate target-fibre mass, yielding (2). ∎

This is parent-owned strong lumpability, not an ORION theorem.

This is the criterion **for all fine starting states/distributions**. Agreement
on one seed or one equilibrium alone does not prove it. At `α=1`, every restart
solution is just its seed, so projected equality holds even for a non-lumpable
kernel. At a fixed `0<α<1`, equality of the two restart operators on every
basis seed is equivalent to (1): multiply the equality of resolvents on the
left by `I−(1−α)Q_R^T` and on the right by `I−(1−α)P_R^T`, then cancel the
nonzero factor `1−α`.

## Theorem F2.3 — KSO multiscale warrant gate

Navigation commutation alone is insufficient for a KSO quotient/fibre state. For every registered revocation/evidence state `R`, three-valued liveness must also be constant inside each fibre for any atom-level predicate represented at the base. Otherwise the base state has no well-defined `LIVE/DEAD/UNKNOWN` value.

Thus a valid KSO multiscale certificate for `(partition, Γ)` requires, for every `R∈Γ`:

1. **transition lumpability** of `P_R`;
2. **warrant measurability** inside every fibre;
3. seed/query aggregation and any base answer functional to factor through the projection (MEG-20).

When a revocation changes fine gating so that either 1 or 2 fails, the certificate becomes `REFINE_REQUIRED`; the old base dynamics may not be reused by name.

The checker treats the registered `Γ` as an explicitly enumerated, nonempty
snapshot family; it cannot infer coverage of unlisted interventions. Missing
states, invalid liveness values, dimensions, partitions, non-rational inputs,
negative entries and super-stochastic rows are `CANNOT_CHECK`. The answer gate
checks a declared per-state observable, not arbitrary downstream functions of
the full fine graph. Each such function needs its own factorization proof.

For the claimed WARRANTED atom-navigation mode, positive transitions must have
LIVE source and destination atoms. An ungated matrix cannot become warranted
merely by attaching fibre-constant DEAD labels; the checker rejects this
mismatch. The revocation fixture zeros incoming/outgoing mass for the first
fibre while leaving the other fibre LIVE and its surviving `3/4` entries
unchanged. This necessary atom-gate check still does not reconstruct hidden
hyperedge premises, structural denominators or evidence histories; a complete
KSO matrix-construction receipt remains an upstream obligation.

**Lifecycle boundary.** Snapshot checks for every `R` are insufficient to reuse
an evolving quotient across state updates. For every registered revision `r`,
also require `q∘r = r̄∘q` (and the corresponding evidence/answer identities).
For example the identity navigation kernel is lumpable on `{0,1},{2}`, while
revision `r=(0,2,2)` splits the first fibre and admits no state-only base
revision. `field_dynamics_v1/field_dynamics_exact.py::revision_commutes` supplies
the separate finite criterion. Revocation followed by reinstatement may restore
a warrant projection without restoring the append-only audit history.

## Cross-fibre transport

No extra theorem is obtained by naming certain edges “transport.” Every cross-fibre edge contributes to the aggregate sums in (2). If two fine states in one fibre export different total mass to another fibre, the partition is non-lumpable. A larger state that records the distinguishing fine context may restore lumpability; that is a state refinement, not a new navigation law.

## Hostile examples

The exact checker includes:

- a 4-state / 2-fibre lumpable kernel with exact rational restart pushforward equality;
- a cross-fibre mutant where one fine state exports a different aggregate mass, making base navigation ill-defined;
- a warranted partition that is transition-lumpable but has `LIVE` and `DEAD` fine states in one fibre under revocation, hence `REFINE_REQUIRED`;
- a revocation family where both transition and liveness criteria hold as a no-alarm case;
- a cemetery-state embedding showing the substochastic case reduces to ordinary stochastic lumpability without changing live-state projections.

## Parent subtraction

Strong lumpability of finite Markov chains (Kemeny–Snell line) owns the
state-projection theorem. The primary paper [Jacobi and Gornerup, A dual
eigenvector condition for strong lumpability of Markov chains, §2 Theorem 1
and equation (2.1)](https://arxiv.org/pdf/0710.1986) was read on 2026-09-05:
it states the common row-block-sum criterion and the representative quotient.
Only this criterion is used; none of that paper's spectral-rank conditions are
needed for the direct check here. The displayed fixed-point and substochastic
extensions follow by the algebra above. Hierarchical/multilevel methods supply
computational schemes but are unnecessary for this criterion. No empirical
comparison of those schemes has been performed.

The only KSO-specific addition is the already-required warrant/answer measurability: a dynamically lumpable fibre may still be epistemically invalid if its members disagree in liveness or registered answers.

## Terminal

```text
MEG-09 = PARENT_LUMPABILITY_SUFFICIENT__KSO_ADDS_WARRANT_AND_ANSWER_MEASURABILITY
MULTISCALE_NAVIGATION_NOVELTY = NONE_ESTABLISHED
GENERAL_NOVELTY = NOT_ESTABLISHED
```

Reopen only if a future OCM multiscale object cannot be represented as a finite fine-state kernel plus projection, or if a claimed cross-scale operator has a discriminating theorem beyond strong lumpability/intertwining.

## Integration, cost and verification

The original three files came from PR #332 head
`63ab0ac2b22d2a05b4f2b68a6803ce00309e4259` (base
`theory/meg-foundation-batch2`), then were hardened locally. Dense row-block
aggregation costs `O(n²)` arithmetic operations per state, followed by `O(nm)`
comparison against one representative per fibre; the old redundant all-pairs
comparison was removed. Exact dense elimination costs `O(n³)` arithmetic
operations, with rational bit growth additional to these operation counts.
The quotient can reduce solve dimension from `n` to `m` only after all gates
hold; this is a computational implication, not a measured speedup.

Run `python research/machine-epistemics-theory/meg_frontier_f2_multiscale_exact.py`
and `python -m pytest -q tests/unit/test_meg_frontier_f2_multiscale.py`.
Controls cover every basis seed at three restart rates, actual noncommutation,
one-fibre-only liveness revocation, cemetery projection, malformed inputs and
CLI 0/1/2 (optimized Python cannot silently skip assert-based checks).
