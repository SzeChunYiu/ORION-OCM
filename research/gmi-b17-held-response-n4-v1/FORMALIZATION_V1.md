# B17 preregistered held-family response test — N=4 formalization V1

Issue #752; parent ledger #602 B17. Pre-implementation authority: `FREEZE_V1.md`, commit `f50f36f500b272e8663baad1c3beec1394d020df`.

## 1. Scope, evidence classes, and parent subtraction

The registered claim is only

```text
B17_PREREGISTERED_HELD_RESPONSE_GREEN_AT_EXACT_N4_REGISTERED_SCOPE.
```

The scored state space is the fresh domain `X={0,1}^4`, disjoint from #660's three-bit domain. The target-generating rules, response coordinates, exact expected cells, negative controls, and falsifiers were committed before the N=4 witness, tests, or result receipt existed on the branch.

Evidence classes:

- R1–R4 structural laws below are P1 finite mathematical statements;
- exhaustive 24-order, 81-subcube, matching-certificate, and exact-reconstruction checks are P2 executable evidence;
- there is no P4 real-scale generative-model claim.

The mathematics is mostly parent-owned. Autoregressive factorization is the ordinary probability chain rule. Product-mixture support lower bounds are finite nonnegative support / Cartesian-rectangle arguments, closely related to rectangle-cover lower bounds used for nonnegative rank. A finite bijective flow only permutes atom probability masses; this is the discrete-flow limitation discussed in modern normalizing-flow treatments, including Papamakarios et al., *Normalizing Flows for Probabilistic Modeling and Inference*, JMLR 22 (2021). The local-refinement theorem is about a deliberately tiny independent-coordinate refresh class and is not a theorem about diffusion models.

The residual contribution here is prospective evidence discipline plus a response vector spanning four exact registered representation mechanisms.

---

## 2. Frozen targets

All target probabilities are exact rationals.

```text
FULL       : uniform on all 16 atoms
HALF       : uniform on x0=0
EVEN       : uniform on even-parity atoms
DIAGONAL   : uniform on {0000,1111}
HAMMING2   : uniform on Hamming-weight-2 atoms
EQUAL01    : uniform on x0=x1
AND_GRAPH  : uniform on y=x0*x1*x2, with y coordinate 3
BIASED_SWAP: reversed-coordinate pushforward of product marginals
             (1/2,1/3,1/4,1/5)
DELTA0     : point mass at 0000, control only
```

Support sizes are respectively `16,8,8,2,6,8,8,16,1`.

The old #660 overstrong AR law is not repaired. In particular, this capsule never uses

```text
coordinate asymmetry => ordering sensitivity.
```

`HALF` is frozen precisely to refute that converse again on a fresh domain: it is asymmetric yet AR-flat.

---

## 3. R1 — autoregressive row-storage response

For a coordinate order

```text
o=(o_1,o_2,o_3,o_4),
```

the chain rule gives

```text
P(x)=P(x_{o_1})
     P(x_{o_2}|x_{o_1})
     P(x_{o_3}|x_{o_1},x_{o_2})
     P(x_{o_4}|x_{o_1},x_{o_2},x_{o_3}).
```

At position `k`, define `r_k(o)` as the number of distinct Bernoulli conditional rows among contexts having positive prefix probability. The registered storage score is

```text
C_P(o)=sum_{k=1}^4 r_k(o).
```

Every one of the `4!=24` orders is scored, and the witness independently reconstructs the original joint exactly from every order.

### Theorem R1A — full coordinate symmetry is sufficient for AR flatness

Suppose `P` is invariant under every permutation of the four coordinates. Then

```text
C_P(o)=C_P(o')
```

for every two coordinate orders `o,o'`.

### Proof

Any two orders are related by a coordinate permutation `sigma`: applying `sigma` to each coordinate label in `o` produces `o'`. Coordinate invariance means the map

```text
x -> sigma(x)
```

is measure preserving for `P`. At every chain position it therefore gives a bijection between reachable prefix contexts under `o` and reachable prefix contexts under `o'`, and it preserves the corresponding conditional Bernoulli probability. Thus the sets of distinct conditional rows at matching positions have equal cardinality. Hence `r_k(o)=r_k(o')` for each `k`, and summing gives equal storage cost. QED.

The converse is false. `HALF` has coordinate stabilizer size 6 rather than 24, but all 24 orders have cost 4.

### Frozen symmetric controls

The exhaustive result is

```text
FULL:      C=4 for all 24 orders
EVEN:      C=5 for all 24 orders
DIAGONAL:  C=7 for all 24 orders
HAMMING2:  C=8 for all 24 orders.
```

Each of these distributions has full coordinate stabilizer size 24, so the flatness part follows from R1A; the exact numerical costs are finite exact calculations checked by the witness.

### Theorem R1B — AND_GRAPH response

For the registered `AND_GRAPH`,

```text
min_o C(o)=5,
max_o C(o)=9,
```

and every minimum-cost order puts output coordinate 3 last.

### Proof and exact cases

When output is last, the first three coordinates are independent fair inputs. Each input position therefore contributes one distinct conditional Bernoulli row. After all inputs are known, the deterministic AND output contributes exactly two distinct rows (`0` and `1`). Hence every input permutation followed by output has cost

```text
1+1+1+2=5.
```

There are six such orders.

The remaining 18 orders are exhaustively evaluated under exact rational conditionals. If output occurs third, the total is 7; if it occurs first or second in the registered cases, the maximum 9 is attained. The frozen complete histogram is

```text
cost 5 : 6 orders
cost 7 : 6 orders
cost 9 : 12 orders.
```

Because all six cost-5 orders are exactly the six input permutations followed by coordinate 3, no non-last-output order attains the minimum. The executable witness reconstructs the exact joint for all 24 orders, so this enumeration is a finite certificate rather than a sampling estimate. QED.

R1B is a microscope result about this storage score, not a universal statement that a particular neural autoregressive architecture will have the same training/sample efficiency.

---

## 4. R2 — exact product-mixture burden from support rectangles

A product component has form

```text
Q(x_0,x_1,x_2,x_3)=prod_i q_i(x_i).
```

Its positive support is therefore a Cartesian product

```text
supp(Q)=S_0 x S_1 x S_2 x S_3,
```

where each nonempty `S_i` is `{0}`, `{1}`, or `{0,1}`. There are exactly `3^4=81` nonempty subcubes of `{0,1}^4`.

Let a target `P` have positive support `S`, and suppose

```text
P=sum_{j=1}^K lambda_j Q_j,
lambda_j>0,
sum_j lambda_j=1,
```

with product components `Q_j`.

### Theorem R2A — rectangle-cover lower bound

Every positive-weight component satisfies

```text
supp(Q_j) subseteq S,
```

and the component supports cover `S`. Consequently

```text
K >= rho(S),
```

where `rho(S)` is the minimum number of subcubes contained in `S` whose union covers `S`.

### Proof

All mixture terms are nonnegative. If some `Q_j` placed positive mass on an atom `x` outside `S`, then the mixture would also place positive mass on `x`, contradicting `P(x)=0`; cancellation is impossible. Thus every component support lies inside `S`.

Conversely, every `x in S` has `P(x)>0`. Therefore at least one positive-weight term must have `Q_j(x)>0`, so the union of component supports covers `S`. Since every component support is a subcube, any exact K-component representation supplies a K-subcube cover. Hence `K>=rho(S)`. QED.

The witness independently enumerates all 81 subcubes and solves the finite cover problem exactly by dynamic programming over the target-support bit mask.

### Exact upper certificates and equality

For the frozen targets:

```text
FULL:       rho=1, K_min=1
HALF:       rho=1, K_min=1
DIAGONAL:   rho=2, K_min=2
EQUAL01:    rho=2, K_min=2
EVEN:       rho=8, K_min=8
HAMMING2:   rho=6, K_min=6.
```

Matching upper certificates are committed and reconstructed atom by atom:

- `FULL`: one fair product;
- `HALF`: one product with `x0=0` and three fair coordinates;
- `DIAGONAL`: two equally weighted point masses;
- `EQUAL01`: two equally weighted product faces `00**` and `11**`;
- `EVEN`: eight equally weighted point masses;
- `HAMMING2`: six equally weighted point masses.

For `EVEN`, any subcube with a free coordinate contains two atoms that differ in one bit and hence have opposite parity, so no non-singleton subcube lies inside the even support. Thus `rho=8`.

For `HAMMING2`, any subcube with a free coordinate contains atoms whose Hamming weights differ by one, so no non-singleton subcube lies entirely at weight 2. Thus `rho=6`.

For `EQUAL01`, its support is not a single Cartesian product, so `rho>1`; the two faces give `rho<=2`. Therefore `rho=2`.

Lower and upper bounds coincide in every registered cell, proving the exact component counts. QED.

This is a finite product-mixture statement. It is not a theorem about arbitrary latent neural architectures or approximate likelihood quality.

---

## 5. R3 — finite bijective-flow reachability

Let `Q` and `P` be probability mass functions on the same finite 16-element set `X`. A deterministic bijection `f:X->X` pushes `Q` forward to

```text
(f_*Q)(y)=Q(f^{-1}(y)).
```

### Theorem R3 — mass-multiset iff condition

There exists a bijection `f` with `f_*Q=P` if and only if the multisets

```text
{Q(x): x in X}
and
{P(x): x in X}
```

are equal, including multiplicities.

### Proof

Necessity is immediate: a bijection merely reindexes the atoms, so the list of mass values can only be permuted.

For sufficiency, group source and target atoms by their exact rational mass. Equality of multisets means every mass value occurs equally often in the two groups. Choose an arbitrary one-to-one pairing inside each equal-mass group. The union of those pairings is a bijection of all 16 atoms, and by construction each target receives exactly its required source mass. QED.

This finite theorem matches the standard limitation of discrete bijective flows: they permute probability masses rather than applying a continuous Jacobian density correction. citeturn897423search38

### Independent executable certificate

The scored predictor checks sorted mass multisets. The scored measurement separately constructs equal-mass matching buckets, emits an explicit 16-atom mapping for every positive cell, checks that the mapping is a permutation, and pushes the base through it atom by atom.

The frozen uniform base ladder has support sizes `16,8,6,2`. A uniform target of support size `k` has mass multiset consisting of `k` copies of `1/k` and `16-k` zeros. Therefore it is reachable from `Uk` and from no other registered uniform base.

The resulting frozen positives are:

```text
FULL      <- U16
HALF      <- U8
EVEN      <- U8
DIAGONAL  <- U2
HAMMING2  <- U6
EQUAL01   <- U8
AND_GRAPH <- U8.
```

`BIASED_SWAP` is a coordinate permutation of `BIASED`, hence an atom bijection gives reachability. `BIASED` is nonuniform while `FULL` is uniform, so their mass multisets differ.

Every frozen R3 positive has a verified explicit bijection and every negative fails both prediction and independent matching.

R3 is exact for deterministic bijections on this finite state space. It must not be exported as a statement about continuous normalizing flows.

---

## 6. R4 — bounded local independent-coordinate refinement

The registered iterative class starts at `DELTA0`. A single step chooses one coordinate `i` and replaces that bit by a fresh independent Bernoulli draw with parameter

```text
p in {0,1/2,1},
```

independently of all other bits and of the old value at coordinate `i`.

### Theorem R4A — reachable-class characterization

A distribution is reachable from `DELTA0` by finitely many registered refreshes if and only if it is a product law whose four bit-one marginals lie in `{0,1/2,1}`.

### Proof

Initially `DELTA0` is a product law with all marginals zero. A refresh of coordinate `i` replaces only its marginal with the chosen `p` and makes the new bit independent of the other coordinates; all other product factors are unchanged. Induction therefore shows every reachable law is product with marginals on the registered grid.

Conversely, given any product law with marginals `(p_0,p_1,p_2,p_3)` on the grid, refresh each coordinate having `p_i != 0` exactly once using parameter `p_i`. Unrefreshed coordinates retain marginal zero. The resulting product is exactly the target. QED.

### Theorem R4B — minimum step count

For a reachable target, the minimum number of steps from `DELTA0` equals

```text
#{i : p_i != 0}.
```

### Proof

A coordinate never refreshed remains deterministically zero, so every coordinate with nonzero target marginal must be refreshed at least once. Thus the displayed count is a lower bound. The constructive proof of R4A reaches the target with exactly one refresh for each such coordinate, attaining the bound. QED.

Therefore:

```text
DELTA0: min_steps=0
FULL:   min_steps=4
HALF:   min_steps=3.
```

The witness independently checks that `EVEN`, `DIAGONAL`, `HAMMING2`, `EQUAL01`, and `AND_GRAPH` differ from the product of their marginals, so they are structurally outside this class. `BIASED_SWAP` *is* a product law, but its marginals `(1/5,1/4,1/3,1/2)` are outside the registered refresh grid, giving a different structural failure mode.

This separation prevents `NONPRODUCT` from becoming a catch-all explanation.

---

## 7. Three different meanings of “unreachable”

The repository must not merge these statements:

1. **R3 finite-bijection structural impossibility.** If mass multisets differ, no deterministic bijection on the 16-state space can work, regardless of search depth.
2. **R4 registered-class structural impossibility.** A target can fail because it is nonproduct or outside the refresh-probability grid. This rules out only the frozen local independent-refresh class; a richer local stochastic kernel can escape the obstruction.
3. **#660 bounded-depth failure.** A target reported as `not <= 3` under a local-step search is only known not to occur within the searched depth/class; unless a separate invariant rules it out forever, that is a search limit rather than a universal structural impossibility.

This distinction is part of the claim, not commentary: hostile controls ensure the receipt contains both R4 failure reasons and never calls the bounded local class “general diffusion.”

---

## 8. Held-test interpretation and the preserved #660 correction

#660 remains historically correct about its own evidence: its receipt records that the earlier prediction was not frozen before the outcome. This successor does not rewrite that provenance.

Instead, #752 moved to a fresh four-bit state space and committed before implementation:

- all target generators;
- every exact response cell used for acceptance;
- the base ladder;
- the `HALF` asymmetric-flat negative control;
- the `AND_GRAPH` ordering-sensitive positive control;
- the R2 component counts;
- the R3 reachability rules;
- the R4 reachability/minimum-step rules;
- falsifiers and claim ceiling.

Thus a GREEN result is evidence only for those preregistered N=4 response laws. It does **not** repair the failed #660 chain-ordering converse. Indeed `HALF` gives another counterexample to the converse on the held domain.

The parent literature also supports keeping the AR claim narrow: recent work on autoregressive Ising models explicitly studies variable ordering as a model-complexity choice rather than treating every asymmetric distribution as automatically order-sensitive. citeturn897423academia36

---

## 9. Verification matrix

`test_held_response_n4_v1.py` contains 29 exact/adversarial tests covering:

- target support rules and normalization;
- exact `Fraction` arithmetic and float rejection;
- all 24 AR orders plus chain reconstruction;
- full-symmetry controls and asymmetric-flat `HALF`;
- exact `AND_GRAPH` extrema and minimum-order placement;
- all 81 subcubes;
- exact rectangle-cover minima;
- exact product-mixture upper certificates;
- singleton-only support arguments for parity and fixed Hamming weight;
- the full registered finite-flow response matrix;
- explicit bijection pushforward certificates;
- local-refinement positive reconstruction and minimum steps;
- correlated-negative product checks;
- product-but-outside-grid `BIASED_SWAP`;
- the old false-converse guard;
- deterministic claim guards and absence of floats in the receipt.

The dedicated workflow runs the suite under normal Python and `python -O`, verifies the freeze commit is an ancestor and contains only `FREEZE_V1.md` from this new capsule, checks that implementation/result artifacts were absent at freeze time, and reproduces `RESULT_V1.json` byte-for-byte through `emit_receipt_v1.py`.

---

## 10. Falsifiers and closure boundary

The claim is falsified if any frozen AR cost differs, if `HALF` becomes ordering-sensitive under the registered score, if any R2 lower/upper certificate disagrees, if a predicted R3 negative admits a verified bijection, if a predicted R3 positive lacks one, if an R4 negative is reachable in the registered step semantics, if optimized mode changes the receipt, or if the result is described as continuous-flow/general-diffusion/G5 closure.

Passing the capsule earns only the exact N=4 held-family response row. Broader questions remain open: approximate representations, learned parameterization, optimization, continuous density transformations, rich diffusion kernels, scale, perceptual quality, and transfer outside the registered finite family.