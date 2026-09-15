# GMI #833 finite update-law no-free-lunch theorems v1

**Issue:** #870  
**Parent:** #833 Section I  
**Claim ceiling:** `GMI_FINITE_UPDATE_LAW_NO_FREE_LUNCH_BOUNDARY_AT_UNIFORM_COMPLETION_SCOPE`

## 1. Parent ownership and interpretation

This package is a finite specialization/integration of parent no-free-lunch and inductive-bias results, not a new discovery of those results.

- D. H. Wolpert and W. G. Macready, *No Free Lunch Theorems for Optimization*, IEEE Transactions on Evolutionary Computation 1(1):67–82 (1997), DOI `10.1109/4235.585893`.
- T. M. Mitchell, *The Need for Biases in Learning Generalizations*, Rutgers technical report CBM-TR-117 (1980).

The scientifically relevant lesson is conditional: under a symmetric/uniform problem average, algorithm advantages cancel; selecting a useful learner/update law requires restrictions or weighting in the ecology/model/resource assumptions. This package explicitly rejects the stronger reading that all algorithms are equal in real-world, structured, nonuniform environments.

## 2. Registered finite setting

Let `X` be a finite context set and `Y` a finite label/action alphabet with `|Y|=k>=2`. A registered observed set `O subset X` has fixed labels `h:O->Y`; let `U=X\O`, required nonempty.

An update law `A`, after seeing `h`, supplies at every `x in U` a normalized predictive vector

`q_A(.|h,x) in Delta(Y)`.

The law may be deterministic or randomized. The theorem does not inspect its internal architecture, update implementation, optimizer, or representation.

A completion `f:X->Y` is admissible iff `f|O=h`. Let `F_h` be the finite set of all such completions, so `|F_h|=k^|U|`.

For a target `f`, define expected mean held-out accuracy of `A`

`Acc(A,f) = (1/|U|) sum_{x in U} q_A(f(x)|h,x)`.

## 3. NFL-I1 — exact equality under uniform completions

**Theorem.** If `f` is uniform on `F_h`, then for every normalized deterministic or randomized update law `A`,

`E_f Acc(A,f) = 1/k`.

Equivalently, expected mean 0–1 error is `1-1/k`.

### Proof

Fix one held-out context `x`. For each label `y in Y`, exactly `k^(|U|-1)` completions satisfy `f(x)=y`. Therefore the marginal of `f(x)` under the uniform distribution on `F_h` is uniform on `Y`. Hence

`E_f q_A(f(x)|h,x)`
`= sum_{y in Y} (1/k) q_A(y|h,x)`
`= (1/k) sum_y q_A(y|h,x)`
`= 1/k`,

using only normalization of the predictive vector. Averaging the identical value `1/k` over all `x in U` proves the result. QED.

The observed history is arbitrary but fixed. It restricts the completion set while leaving each registered unconstrained held-out coordinate symmetric under uniform completion. Thus the theorem is not a zero-data artifact.

## 4. NFL-I2 — randomization cannot escape the equality

NFL-I1 already quantifies over arbitrary normalized probability vectors. In particular, for a ternary held-out prediction

`q=(1/7,2/7,4/7)`,

uniform-completion accuracy is

`(1/3)(1/7+2/7+4/7)=1/3`.

Therefore injecting randomness is not an escape from the symmetric average. The executor includes several exact-rational randomized controls, including multiple held-out coordinates.

## 5. NFL-I3 — constructive ecology preference reversal for any distinct laws

The previous theorem gives equality under one special ecological weighting. A stronger boundary explains why ecological assumptions are necessary to prefer one law.

Let `A` and `B` be two predictively distinct update laws on the same fixed history. For each held-out context define

`d_x(y)=q_A(y|h,x)-q_B(y|h,x)`.

Because both predictive vectors normalize,

`sum_y d_x(y)=0`.

Therefore `max_y d_x(y)>=0` and `min_y d_x(y)<=0`. If the laws differ at `x`, the maximum is strictly positive and the minimum strictly negative.

Construct two target completions coordinatewise:

- `f_A(x)` chooses a label attaining `max_y d_x(y)`;
- `f_B(x)` chooses a label attaining `min_y d_x(y)`;
- both use the fixed observed labels `h` on `O`.

Then

`Acc(A,f_A)-Acc(B,f_A) = (1/|U|) sum_x max_y d_x(y) > 0`,

because the laws differ somewhere. Likewise

`Acc(A,f_B)-Acc(B,f_B) = (1/|U|) sum_x min_y d_x(y) < 0`.

Point-mass ecologies on `f_A` and `f_B` therefore prefer opposite laws. QED.

**Corollary.** In any update-law class containing at least two distinct predictive laws, no member is a strict ecology-independent winner over all admissible target-completion distributions. A preference requires an ecology/model/resource restriction or weighting. Identical predictive laws tie everywhere and are scientifically indistinguishable at this protected prediction scope.

This is narrower than saying every pair of arbitrary learning systems reverses under every conceivable loss/resource notion. It is a theorem for the registered finite prediction contract and mean held-out 0–1 accuracy.

## 6. Frozen finite witnesses

### Binary deterministic preference reversal

For one binary held-out context:

- `A0` predicts 0;
- `A1` predicts 1.

Under ecology `P0=(3/4,1/4)`, accuracies are `3/4` and `1/4`. Under `P1=(1/4,3/4)`, the scores reverse.

### Randomized pairwise construction

The executor also freezes two distinct ternary randomized laws over two held-out contexts. The constructive theorem generates point ecologies with exact scores

- under `P_A`: `A=15/28`, `B=13/84`;
- under `P_B`: `A=13/84`, `B=15/28`.

This exercises the general randomized proof rather than only deterministic corner points.

## 7. Exhaustive bounded certificate

The analytic theorem is independent of enumeration. The executable census additionally checks all deterministic prediction vectors across registered small configurations with:

- binary alphabets and held-out sizes 1, 2, 3;
- ternary alphabets and held-out sizes 1, 2;
- multiple observed histories.

The current census contains 136 law/history cases and zero failures. Exact randomized controls are checked separately.

This certificate detects implementation mistakes; it does not turn the finite sample of configurations into the proof of NFL-I1.

## 8. Fail-closed boundary conditions

The theorem/checker rejects or distinguishes:

- no held-out context -> `NOT_APPLICABLE_NO_HELDOUT`;
- `k<2`;
- malformed or non-normalized predictive vectors;
- negative predictive probabilities;
- float probabilities/weights;
- target support inconsistent with the observed history;
- incomplete ecology support declared as uniform;
- nonuniform weights declared `UNIFORM`;
- non-normalized or negative ecology weights.

A nonuniform ecology is valid evidence for conditional preference, but it cannot be silently relabeled as the NFL-I1 uniform premise.

## 9. Historical branch subtraction

The unmerged historical branch `gmi/learning-law-selection` contains a conditional capability/price-to-law selector and explicitly refuses premise-free selection. It is useful historical context, but because it is unmerged it is **not** proof authority for this tranche and no artifact from it is imported as an earned parent.

## 10. Scope and falsifiers

The strongest earned statement, if exact tests/CI/reconciliation pass, is:

`GMI_FINITE_UPDATE_LAW_NO_FREE_LUNCH_BOUNDARY_AT_UNIFORM_COMPLETION_SCOPE`.

Falsifiers include:

- a normalized law whose exact uniform-completion expected accuracy differs from `1/k`;
- a predictively distinct law pair for which the coordinatewise construction fails to produce opposite preferences;
- acceptance of malformed/nonuniform evidence as a valid `UNIFORM` certificate;
- treating an empty held-out set as positive learning evidence;
- any promotion to the forbidden claims registered in the freeze/manifest.

The result does **not** establish `ALL_ALGORITHMS_EQUAL_IN_REAL_WORLD`, and it does not block useful learning-law selection. Instead it proves why such selection must state the ecological/model/resource assumptions that break the NFL symmetry.
