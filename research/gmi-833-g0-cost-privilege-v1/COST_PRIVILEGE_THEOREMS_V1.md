# E7 cost-privilege theorems

## Scope and parent ownership

The object is the registered finite G0 grammar audit object. It is not a theorem about all grammars or all notions of machine complexity.

Parent results are subtracted rather than reclaimed. SyGuS makes the candidate expression language/grammar an explicit input to synthesis. Machine/coding choices are therefore part of the experimental/computational object, not an ignorable presentation detail. Standard Pareto optimization owns positive-weight dominance preservation. The merged #875 tranche already establishes finite G0 description/reachability bias and the difference between isometric remints and same-semantics non-isometric recodings. The merged #863 tranche owns the robustness-control requirement to vary encodings/search/scalarization.

## Definitions

For presentation `p`, raw cost is `rho(p)=(L(p),d(p))`, where `L>0` is registered description length and `d>=0` is registered distance from the frozen grammar start. For positive exact rational `w=(w_L,w_d)`,

`C_w(p)=w_L L(p)+w_d d(p)`.

The post-hoc `family_label(p)` is not an argument of either `rho` or `C_w`. For semantic class `s`, `m_w(s)=min_{p in s} C_w(p)`. Selection returns the complete set of semantic classes that attain the global minimum; tied classes are never broken by names.

## LABEL-1 — family-label blindness

**Statement.** For any permutation `pi` of the registered family-label set and every registered weight `w`, relabeling only `family_label` leaves all point raw vectors, point scalar costs, semantic-class minima, and selected-class sets unchanged.

**Proof.** By definition, `rho(p)` is a function of `(L,d)` only. `pi` changes neither coordinate, so `rho(pi p)=rho(p)`. Substituting in `C_w` gives `C_w(pi p)=C_w(p)`. Each semantic class retains exactly the same multiset of scalar costs, hence the same minimum. The global argmin set is therefore identical. QED.

**Machine certificate.** All `3!=6` label permutations, 5 registered weights and 6 presentations: 180 point-cost identities, 90 class-minimum identities and 30 selected-set identities, zero failures. The independent oracle repeats these checks without importing the main implementation.

## ISO-1 — certified cost/search isometry invariance

**Statement.** Let `phi` be a bijection of presentation identities that preserves protected semantic class, raw `(L,d)` and transports the search adjacency relation exactly. Then every registered scalar cost, semantic-class minimum, raw Pareto relation and selected semantic-class set is invariant under `phi`.

**Proof.** Raw-vector equality gives scalar-cost equality pointwise. Semantic preservation establishes a cost-preserving bijection within every class, hence class minima agree. Coordinatewise comparisons of identical raw vectors preserve Pareto relations. Global minima over equal class-minimum maps yield equal selected sets. Exact transport of adjacency establishes that the remint is a search-graph isometry rather than merely a semantic recoding. QED.

**Machine certificate.** The six base presentation identities are renamed through all `6!=720` bijections onto fresh syntax identities. Each transports the registered edge set and preserves all class minima/selection values for all weights. Raw-cost and edge mutations are required to terminate `NON_ISOMETRIC_REMINT`.

## BIAS-1 — semantic coverage is insufficient for neutrality

**Statement.** There exist two grammars with identical protected semantic coverage whose registered raw cost geometry reverses the selected semantic class under the same positive weight.

**Witness.** Under `w=(1,1)`, grammar `GA` assigns `ALPHA=(1,1)` and `BETA=(3,2)`, selecting `ALPHA`. Grammar `GB` assigns `ALPHA=(3,2)` and `BETA=(1,1)`, selecting `BETA`. Both expose exactly `{ALPHA,BETA}`.

**Consequence.** Family-label blindness and semantic coverage do not imply representation/search neutrality. Universal no-privilege wording is therefore rejected at this scope. The row-level terminal is `NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE`.

## DOM-1 — positive scalar weights preserve strict raw dominance

**Statement.** If `x=(L_x,d_x)` weakly improves `y=(L_y,d_y)` in both coordinates and improves at least one strictly, then every strictly positive weight has `C_w(x)<C_w(y)`.

**Proof.** `C_w(y)-C_w(x)=w_L(L_y-L_x)+w_d(d_y-d_x)`. Each summand is nonnegative and at least one is strictly positive; both weights are positive. Hence the difference is strictly positive. QED.

For incomparable vectors no common sign follows. The frozen `(1,4)` and `(4,1)` pair reverses between weights `(4,1)` and `(1,4)`.

**Machine certificate.** All 25 vectors in `{0,1,2,3,4}^2` give 600 ordered distinct pairs. There are 200 strict-dominance ordered pairs and 1,000 dominance/weight checks; zero violations.

## Hostile results

* nonconstant family-label adjustment -> `FAMILY_LABEL_COST_LEAK`;
* `(0,0)` family-specific macro -> `ZERO_COST_FAMILY_MACRO`;
* lexical singleton resolution of a true selected-set tie -> `LABEL_DEPENDENT_TIE_BREAK`;
* raw-vector or search-edge mutation under a claimed isometry -> `NON_ISOMETRIC_REMINT`.

## Claim ceiling

`GMI_G0_COST_LABEL_BLINDNESS_AND_STRUCTURAL_PRIVILEGE_BOUNDARY_AT_REGISTERED_SCOPE`

This does not establish an unbiased grammar, universal representation invariance, universal search neutrality, an architecture-prior-free grammar, or agreement of all scalarizations.
