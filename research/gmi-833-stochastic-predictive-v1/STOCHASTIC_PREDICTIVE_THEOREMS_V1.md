# Finite stochastic predictive quotient and exact linear dimension — v1

**Issue:** #836, child of #833  
**Freeze:** `f79f748c909e67dceab8f4d05ad6e1de4c273060`  
**Frozen source main:** `5db372ef7003253d5846b324ed80a2454613983c`  
**Claim ceiling:** `GMI_FINITE_PREDICTIVE_BLOCK_LINEAR_DIMENSION_AT_REGISTERED_HORIZON`

This package formalizes one exact finite controlled-stochastic block. It does not claim novelty for predictive-state representations, system-dynamics-matrix rank, or ordinary rank factorization. #846 already owns the registered predictive-row quotient/cardinality-minimality theorem; Littman–Sutton–Singh (2001) and Singh–James–Rudary (2004) are the strongest literature parents for predictive state and linear PSR rank/core-test results. No Lean/Coq/Isabelle proof-assistant claim is made because those toolchains are not available in the execution environment; the evidence here is analytic finite proof plus exact rational machine certificates.

## Registered object

Fix finite nonempty action and observation alphabets `A,O`, a finite horizon `N>=1`, and exact rational controlled kernels `K_h(o|a)` for every positive reachable history `h` of depth `<N`. A history has likelihood equal to the product of its registered observation probabilities under the chosen actions. Conditional predictive rows are defined only for histories of positive probability; a request on a zero-probability history fails closed.

For residual horizon `ell`, let `T_ell` contain every controlled action/observation test of lengths `0..ell`, including the empty test. At fixed history depth `d` with `d+ell<=N`, let `H_d^+` be the positive histories and define the finite system-dynamics block

`D[h,t] = P_h(t)`, for `h in H_d^+`, `t in T_ell`.

All executable arithmetic uses exact `Fraction` values.

## PQ-1 — predictive-row quotient

Define `h ~P h'` iff the complete rows `D[h,:]` and `D[h',:]` are equal.

**Sufficiency.** For every registered test `t`, `P_h(t)` is a function of `[h]~P`: equal classes have equal complete rows, hence equal `t` coordinates.

**Arbitrary-statistic cardinality minimality.** If a statistic `S` permits exact reconstruction of every registered test probability, then `S(h)=S(h')` implies `D[h,:]=D[h',:]`. Thus every exact predictive statistic refines the predictive quotient and cannot have fewer labels than the number of distinct rows. This theorem is inherited/revalidated from #846 PS-1 rather than reclaimed here.

A load-bearing hostile uses two histories equal on every test of length at most one but separated by a length-two test. Therefore completeness is always relative to the explicitly registered residual horizon.

## LR-1 — exact linear rank lower bound

An exact `q`-dimensional linear predictive representation is a factorization

`D[h,t] = s(h)^T w(t)` with `s(h),w(t) in Q^q`.

Stacking state vectors into a matrix `S` and test vectors into `W` gives `D=SW`. Hence

`rank(D) <= min(rank(S),rank(W)) <= q`.

Therefore no exact linear predictive representation can have dimension below `rank(D)`. This constrains linear coordinate representations only; nonlinear sufficient statistics are outside the theorem.

For rational `D`, rational rank equals real rank because rank is the largest order of a nonzero minor and every minor determinant is rational. The executor uses no floating-point tolerance.

## LR-2 — rank-attaining core-test factorization

Let `r=rank(D)` and choose `r` linearly independent columns of `D`; call their index set `C` and let `Q=D[:,C]`. Those columns form a basis of the column space, so every column of `D` has exact rational coordinates in that basis. Collecting these coordinates gives `W` with

`D = QW`.

Define the core-test state `s_C(h)=D[h,C] in Q^r`. Then every registered test prediction is a linear functional of this state. Combined with LR-1, the minimum exact **linear** predictive dimension of the fixed finite block is exactly `rank(D)`.

The machine certificate computes rank two independent ways—rational Gaussian elimination and the maximum order of a nonzero exact determinant/minor—then selects independent core columns, solves an invertible exact row minor, and requires entrywise reconstruction of `D`.

This is parent-owned PSR/linear-algebra mathematics (especially Singh–James–Rudary 2004), not a novel rank theorem.

## SEP-1 — predictive class count can exceed linear dimension

Use one action `a`, observations `{A,B,C,X,Y}`, and horizon two. From the empty history, `A,B,C` each occur with probability `1/3`; `X,Y` have probability zero. At depth one:

- after `A`, next observation is `X` with probability `1`;
- after `B`, `X,Y` each have probability `1/2`;
- after `C`, next observation is `Y` with probability `1`.

For `d=1, ell=1`, the complete rows over `[epsilon,(a,A),(a,B),(a,C),(a,X),(a,Y)]` are

`R_A=[1,0,0,0,1,0]`,
`R_B=[1,0,0,0,1/2,1/2]`,
`R_C=[1,0,0,0,0,1]`.

They are three distinct predictive classes, but `R_B=(R_A+R_C)/2` and `R_A,R_C` are independent. Thus class count is `3` while exact linear predictive dimension is `2`. Cardinality-minimal arbitrary statistics and minimum linear coordinate dimension are different optimization problems.

## LAT-1 — latent realization is not identified by observable prediction alone

Model L1 has one latent state and emits an independent fair observable bit at each step. Model L2 has two latent states: independently resample a fair hidden bit each step and emit it deterministically. For every observable binary word of length `m`, both models assign probability `2^-m`.

Therefore the complete observable predictive law is identical while latent realizations and latent-state cardinalities differ. No deterministic function of that observable predictive law alone can identify the unique latent realization or its cardinality over a model class containing both models.

The exact receipt checks every binary word of lengths `0..5`: **63 total words including the empty word, 62 nonempty**, with zero probability disagreements. This is an observational non-identifiability result only; added causal interventions or structural assumptions may change the answer.

## Exact finite census

As corroboration, not as the analytic proof, the executor enumerates all four-history one-step binary predictive blocks whose Bernoulli-1 probabilities lie in `{0,1/2,1}`. There are `3^4=81` blocks. For each it checks exact class count, both rank implementations, exact rank factorization, and all `4^4=256` statistic-label assignments. Totals:

- 81 blocks;
- 20,736 statistic assignments;
- 0 rank/class violations;
- 0 rank-factorization failures;
- 0 statistic-minimality failures;
- 36 blocks with class count strictly above rank.

## Gap discipline

The pre-existing `GAP-833-STOCHASTIC-QUOTIENT` remains OPEN. This tranche adds only `CLAIM-836-FINITE-PREDICTIVE-BLOCK` as `LOCALLY_CLOSED`, while four CRITICAL siblings remain OPEN and continue to block the broader parent:

- `GAP-836-INFINITE-MEASURABLE`;
- `GAP-836-APPROXIMATE-PREDICTIVE`;
- `GAP-836-FINITE-SAMPLE-ID`;
- `GAP-836-CAUSAL-LATENT-ID`.

## Forbidden promotions

This tranche does not license `UNIVERSAL_STOCHASTIC_MINIMALITY`, `GENERAL_MEASURABLE_PSR_THEORY`, `INFINITE_HORIZON_PREDICTIVE_IDENTIFICATION`, `FINITE_SAMPLE_PREDICTIVE_IDENTIFICATION`, `CAUSAL_LATENT_IDENTIFICATION`, `ALL_PSRS_ARE_MINIMAL`, `NOVEL_PSR_RANK_THEOREM`, or `COMPLETE_GMI`.

## Parent anchors

- M. L. Littman, R. S. Sutton, S. Singh, *Predictive Representations of State*, NeurIPS 2001.
- S. Singh, M. R. James, M. R. Rudary, *Predictive State Representations: A New Theory for Modeling Dynamical Systems*, UAI 2004.
- H. Jaeger, observable-operator-model literature.
- #846 `gmi-833-parent-equivalence-v1`, especially PS-1 / PSR-1.
