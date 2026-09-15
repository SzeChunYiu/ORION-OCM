# #752 freeze — B17 preregistered held-family response test on a fresh N=4 domain

Date: 2026-09-15. Parent ledger: #602 B17. Corrected parent artifact: #660 / `GMI_GENERATIVE_FAMILY_DERIVATION_V1.md`.

This commit is the pre-implementation authority. No N=4 scored witness, result receipt, hostile test, or response result for this tranche exists on this branch before this file.

## Why a successor is necessary

The #660 witness is scientifically useful and preserves its held-law failures, but its receipt explicitly says

```text
prediction_frozen_before_outcome: false.
```

Therefore this tranche does not relabel #660 as prospective. It moves to `{0,1}^4`, freezes the target-generating rules and exact response predictions now, and only then permits a scored witness.

## Claim boundary

Target only:

```text
B17_PREREGISTERED_HELD_RESPONSE_GREEN_AT_EXACT_N4_REGISTERED_SCOPE
```

This may establish that four exact registered response laws survive on the frozen N=4 target family. It may not establish a universal generative-family law, continuous normalizing-flow theory, general diffusion theory, real-scale generative performance, G5 closure, open-ended family generalization, or complete GMI.

## Parent subtraction

The mathematical parents are ordinary probability chain factorization, finite product distributions / nonnegative mixtures, Cartesian-product (rectangle/subcube) support arguments, and the fact that finite bijections permute probability masses. The local-refinement result is intentionally about a tiny registered independent-coordinate refresh class, not diffusion in general.

The only repository-level residual sought here is prospective evidence discipline: frozen N=4 structural target rules, exact family-response coordinates, hostile negative controls, and deterministic reproduction.

## Frozen state space

```text
X = {0,1}^4
|X| = 16
```

All probabilities are exact `Fraction`s. No floats are permitted in scored computation.

Coordinate 3 is the output coordinate in the `AND_GRAPH` target; coordinates 0,1,2 are its input coordinates.

## Frozen held targets

Every target is defined by a rule before the witness exists.

1. `FULL`: uniform on all 16 atoms.
2. `HALF`: uniform on atoms satisfying `x0=0` (8 atoms).
3. `EVEN`: uniform on atoms with even Hamming parity (8 atoms).
4. `DIAGONAL`: uniform on `{0000,1111}`.
5. `HAMMING2`: uniform on atoms of Hamming weight exactly 2 (6 atoms).
6. `EQUAL01`: uniform on atoms satisfying `x0=x1` (8 atoms).
7. `AND_GRAPH`: uniform over the 8 graph atoms `(x0,x1,x2,y)` satisfying `y=x0*x1*x2`.
8. `BIASED_SWAP`: start from the registered product base with bit-one probabilities

```text
(1/2, 1/3, 1/4, 1/5)
```

and reverse the coordinate order. This is a full-support nonuniform target.

A deterministic-start control `DELTA0` is the point mass at `0000` and is used only for the local-refinement zero-step check.

Because the parent #660 domain has only three bits, every N=4 target is state-space disjoint from the earlier scored distributions.

# Response coordinate R1 — autoregressive conditional-row storage

For an order `o` of the four coordinates, factor the joint by the chain rule. At each position count the number of **distinct Bernoulli conditional rows among reachable contexts**; the total stored-row cost is the sum across positions.

Score all `4! = 24` coordinate orders.

## R1 theorem target

If a target distribution is invariant under every coordinate permutation, the multiset of AR costs over orders is constant; in particular min cost equals max cost.

The converse is **not** claimed. #660 already falsified an overstrong converse, and `HALF` is frozen here as an asymmetric-flat negative control.

## Frozen exact R1 cells

```text
FULL:       min=max=4
EVEN:       min=max=5
DIAGONAL:   min=max=7
HAMMING2:   min=max=8
HALF:       min=max=4   # asymmetric but flat: negative control to the false converse
AND_GRAPH:  min=5, max=9
```

For `AND_GRAPH`, every min-cost order must place coordinate 3 last. At least one non-last-output order must attain max cost 9. The scored receipt must report the complete 24-order cost histogram, not only extrema.

Falsifier: any frozen exact cell differs; or the implementation treats asymmetry as sufficient for sensitivity.

# Response coordinate R2 — latent product-mixture component burden

A product component is any probability distribution factoring across the four binary coordinates. Because mixture weights and component masses are nonnegative, the support of every positive-weight component in an exact representation must be a Cartesian product subset (subcube) of the target support.

For a support `S`, let `rho(S)` be the minimum number of nonempty subcubes contained in `S` whose union covers `S`. Every exact nonnegative product mixture needs at least `rho(S)` positive components.

For each frozen target below, a registered explicit mixture reaches the same number, proving exact `K_min=rho(S)` at this scope.

## Frozen exact R2 cells

```text
FULL:       K_min=1
HALF:       K_min=1
DIAGONAL:   K_min=2
EQUAL01:    K_min=2
EVEN:       K_min=8
HAMMING2:   K_min=6
```

Registered upper-bound constructions:

- `FULL`: one product with all four marginals fair;
- `HALF`: one product with `x0=0` and the other three marginals fair;
- `DIAGONAL`: two equally weighted point masses;
- `EQUAL01`: two equally weighted faces `00**` and `11**`, each uniform on its last two coordinates;
- `EVEN`: eight equally weighted point masses;
- `HAMMING2`: six equally weighted point masses.

For `EVEN` and `HAMMING2`, every non-singleton subcube contains two atoms differing in one bit and therefore contains both parities / two distinct Hamming weights, so no non-singleton subcube lies inside the support. Hence the lower bound equals support cardinality.

For `EQUAL01`, the support is not itself a product set, so `K_min>1`; the two registered faces give `K_min<=2`.

Falsifier: the independently enumerated subcube-cover minimum disagrees with any frozen K, or a registered mixture certificate fails exact atom-by-atom reconstruction.

# Response coordinate R3 — finite flow / bijection reachability

For exact distributions `Q,P` on the same 16-element state space, a deterministic bijection `f:X->X` pushes `Q` to `P` iff the multisets of the 16 atom probabilities are equal.

Necessity: a bijection only permutes atoms. Sufficiency: equality of finite multisets permits a value-preserving perfect matching of source atoms to target atoms, which is a bijection.

## Frozen base ladder

1. `U16`: uniform on all 16 atoms.
2. `U8`: uniform on `HALF` support (8 positive atoms, 8 zeros).
3. `U6`: uniform on the lexicographically first six atoms (6 positive atoms, 10 zeros).
4. `U2`: uniform on `{0000,0001}` (2 positive atoms, 14 zeros).
5. `BIASED`: full-support product base with bit-one probabilities `(1/2,1/3,1/4,1/5)`.

## Frozen R3 matrix rules

For every uniform held target, reachability from `Uk` is true iff the target has exactly `k` support atoms. Thus:

```text
FULL      reachable only from U16 among U-bases
HALF      reachable only from U8 among U-bases
EVEN      reachable only from U8 among U-bases
DIAGONAL  reachable only from U2 among U-bases
HAMMING2  reachable only from U6 among U-bases
EQUAL01   reachable only from U8 among U-bases
AND_GRAPH reachable only from U8 among U-bases
```

`BIASED_SWAP` is reachable from `BIASED` and is not equal-multiset to `U16`.

The scored measurement must be an independently implemented perfect-matching certificate on equal-probability edges, not simply a call to a sorted-multiset predicate. It must return an explicit 16-atom bijection for every positive cell and verify the pushed distribution exactly.

This result is about deterministic bijections on a finite set. It does not claim anything about continuous flows or Jacobians.

Falsifier: any predicted positive cell lacks a verified bijection, or any negative cell admits one.

# Response coordinate R4 — bounded local independent-coordinate refinement

Register the following deliberately narrow iterative class.

Start from `DELTA0`. One step chooses exactly one coordinate `i` and replaces that coordinate by an independent Bernoulli draw with

```text
p_i in {0, 1/2, 1}
```

independent of all other coordinates and of its previous value. Repeated refreshes are allowed; only the last refresh of a coordinate matters.

## R4 theorem target

Every reachable law is a product distribution whose four bit-one marginals each lie in `{0,1/2,1}`. Conversely every such product law is reachable. Its minimum step count from `DELTA0` is the number of coordinates whose target marginal differs from zero.

Therefore the frozen cells are:

```text
DELTA0:     reachable, min_steps=0
FULL:       reachable, min_steps=4
HALF:       reachable, min_steps=3
EVEN:       structurally unreachable in this class
DIAGONAL:   structurally unreachable in this class
HAMMING2:   structurally unreachable in this class
EQUAL01:    structurally unreachable in this class
AND_GRAPH:  structurally unreachable in this class
BIASED_SWAP: structurally unreachable in this class because at least one marginal is outside {0,1/2,1}
```

For each correlated negative target, the witness must independently compute that the joint is not the product of its marginals. For `BIASED_SWAP`, it must show product factorization holds but the registered probability grid fails. These are structural impossibilities **within this frozen local class**, not finite-depth search failures and not claims about general diffusion.

Falsifier: a frozen negative is reachable under the exact registered step semantics, or the reported minimum steps for a positive cell are not minimal.

# Hostile controls

At minimum the suite must verify:

1. exact N=4 target supports/cardinalities and normalization;
2. every reported number is integer/Fraction, with no float in receipt;
3. all 24 AR orders are scored and exact reconstruction by the chain rule succeeds;
4. `HALF` is coordinate-asymmetric yet AR-flat;
5. `AND_GRAPH` has the frozen min/max and every minimum places output last;
6. all 81 nonempty/empty-coordinate subcube patterns are considered in the R2 rectangle search, excluding empty intersections and subcubes not contained in target support;
7. R2 cover lower bound and independent explicit mixture upper certificate agree on every registered target;
8. flow positives return explicit perfect-match bijections that reproduce targets atom-by-atom;
9. flow negatives fail perfect matching and sorted-multiset equality;
10. local-refinement positives reconstruct exactly from a minimal registered step sequence;
11. local-refinement correlated negatives fail an independent product-of-marginals check;
12. `BIASED_SWAP` is product but fails only the local probability grid, preventing “correlated” from becoming a catch-all explanation;
13. the old false implication `coordinate asymmetry => AR ordering sensitivity` is explicitly asserted false by the `HALF` control;
14. normal Python and `python -O` produce byte-identical deterministic receipts.

# Proof obligations

The formalization must prove:

- R1 symmetry sufficiency by conjugating coordinate orders under distribution-preserving coordinate permutations; explicitly deny the converse;
- R2 rectangle-cover lower bound from nonnegative support monotonicity and each exact upper construction;
- R3 multiset iff bijection theorem and the matching certificate equivalence;
- R4 reachable-class characterization and minimum-step formula;
- why R3 structural impossibility differs from R4 bounded-class structural impossibility and from #660's `not <= 3` search-depth result;
- why passing this exact held test does not repair #660's failed held chain law or imply real/continuous-family closure.

# Verification order

After this freeze commit only:

1. implement the N=4 witness;
2. add hostile/exact tests;
3. emit deterministic receipt;
4. write formal proof document with parent subtraction and claim ceiling;
5. dedicated normal / `python -O` CI verifies freeze custody and byte-identical receipt;
6. merge only if every frozen falsifier remains false.

No #602 checkbox is changed merely because this freeze exists.