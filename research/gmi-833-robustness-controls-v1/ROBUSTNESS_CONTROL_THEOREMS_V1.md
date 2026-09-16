# GMI #833 derivation robustness controls — definitions and finite theorems v1

**Issue:** #863  
**Parent:** #833 Section D  
**Claim ceiling:** `GMI_DERIVATION_ROBUSTNESS_CONTROL_REQUIREMENTS_FORMALIZED_AT_REGISTERED_FINITE_SCOPE`

This note formalizes four *required controls* for architecture-uncommitted derivation experiments. It deliberately separates **control compliance** from **invariance of the scientific conclusion**. A valid control may expose sensitivity; that is an informative result, not a protocol failure.

## 1. Parent ownership and novelty boundary

The following principles are parent mathematics/methodology rather than new GMI theorems:

- inductive bias and representation/search bias (Mitchell, 1980; Mitchell, 1982);
- no-free-lunch / problem-distribution dependence of optimizer performance (Wolpert & Macready, 1997);
- negative/control experiments as artifact and causal-interpretation checks;
- semantics-preserving transformations/metamorphic tests as invariance probes;
- Pareto dominance, Pareto fronts and weighted-sum scalarization in multiobjective optimization.

The residual contribution here is a typed finite GMI control record, exact hostile witnesses, and fail-closed governance semantics.

## 2. R1 — matched grammar negative twin

Let `C+` be the finite candidate multiset visible to search. Let `m:C+->{0,1}` mark the predicted mechanism and let

`b : {c in C+ : m(c)=0} -> B`

be the registered *irrelevant/background search-capacity signature*: every feature of a mechanism-free candidate that is allowed to affect its search opportunity but is not the target mechanism itself.

A negative twin `C-` is **matched** iff:

1. `m(c)=0` for every `c in C-`;
2. the multisets of background signatures agree exactly,

   `{{ b(c) : c in C+, m(c)=0 }} = {{ b(c) : c in C- }}`;

3. ecology, verifier/evaluator, search budget, and stopping semantics are identical.

The total number of candidates may decrease by exactly the number of target-containing candidates removed from `C+`; that decrease is reported explicitly. Deleting any extra mechanism-free candidate changes the background multiset and is `GRAMMAR_TWIN_UNMATCHED`.

### R1 theorem — background-opportunity preservation

For any statistic `f:B->Q` depending only on registered background capacity,

`sum_{c in C+, m(c)=0} f(b(c)) = sum_{c in C-} f(b(c))`.

**Proof.** Equality of finite multisets means every `b in B` has identical multiplicity on both sides. Group each sum by `b`; corresponding terms and multiplicities are equal. QED.

This theorem does **not** say the two total grammar spaces have identical cardinality, nor that removing the mechanism leaves search dynamics unchanged when search explicitly depends on target-containing candidates. Those are separate falsifiers.

## 3. R2 — semantic remint / alternate encoding

An encoding is a finite map `e:S->K` from surface identifiers `S` to canonical protected semantic classes `K`. Two encodings `e1:S1->K` and `e2:S2->K` form a valid remint pair when a bijection `phi:S1->S2` satisfies

`e1(s) = e2(phi(s))` for all `s in S1`.

This is the finite commuting diagram

`e1 = e2 o phi`.

A result is compared only after projection to `K`. Therefore surface equality is irrelevant; semantic equality is the invariant of interest.

### R2 theorem — canonical invariance under a valid remint

If a decision rule `A` is semantic, i.e. there exists `A_K` with `e(A(e)) = A_K(K-data)` independently of surface names, then two valid remints yield the same canonical result.

**Proof.** Both executions factor through the same canonical semantic data and the same `A_K`; applying `e1` and `e2` to the selected surface results yields the same element of `K`. QED.

**Hostile.** A lexicographic surface-name tie break need not factor through `K`. The frozen remint changes the lexicographically first identifier while preserving semantics, producing canonical winners `A` and `B`; terminal `ENCODING_SENSITIVE`.

A non-bijective or non-semantics-preserving map is not evidence of encoding sensitivity. It is `CANNOT_AUDIT_ENCODING` because the comparison itself is invalid.

## 4. R3 — alternate search algorithms

A search-run record contains at least:

`(strategy_id, strategy_signature, objective_id, declared_budget, canonical_winner)`.

Two runs count as alternate algorithms only when their registered strategy signatures differ. Renaming the same signature does not satisfy the requirement.

Comparability additionally requires the same scientific objective and the same declared budget frame. If budgets are not commensurate, the terminal is `CANNOT_COMPARE_SEARCH_BUDGETS`, not an invariance claim.

### Positive finite certificate

On scores `A=3, B=1, C=2`, exhaustive enumeration and an independently implemented admissible-lower-bound branch-and-bound search both return the unique optimum `B`. The branch-and-bound lower-bound invariant is checked: `LB(c) <= score(c)` for every candidate.

This is a bounded agreement certificate, not a theorem that exhaustive and branch-and-bound search agree on all spaces.

### Search-sensitivity hostile

Under a budget of one evaluation and a tied scientific objective, forward early stop over `[A,B]` returns `A`, while reverse early stop over `[B,A]` returns `B`. The objective and budget are identical; only the search procedure/order differs. Therefore the scientific winner is `SEARCH_ALGORITHM_SENSITIVE` at this registered scope.

This is consistent with the parent no-free-lunch lesson: algorithm superiority/invariance requires structure or restrictions; it is not free of problem/search assumptions.

## 5. R4 — Pareto analysis and alternate scalarizations

Let each candidate have an exact minimization resource vector `r(c) in Q^d_{>=0}`. Define strict Pareto dominance

`a <_P b` iff `a_i <= b_i` for every `i` and strict inequality holds for at least one coordinate.

Raw vectors and the Pareto frontier are primary. A weighted scalar score is

`S_w(c)=w dot r(c)` with `w_i>0`.

### R4a — positive scalarization preserves strict Pareto dominance

If `r(a) <_P r(b)` and `w>0`, then `S_w(a) < S_w(b)`.

**Proof.** Every term `w_i(r_i(a)-r_i(b))` is nonpositive and at least one is strictly negative, so the sum is strictly negative. QED.

Consequently a correctly implemented positive weighted minimization cannot select a strictly dominated candidate while a dominator is available.

### R4b — incomparable vectors can reverse

For the registered hostile `a=(1,4)`, `b=(4,1)`:

- with `w=(4,1)`: `S_w(a)=8 < 17=S_w(b)`;
- with `w=(1,4)`: `S_w(b)=8 < 17=S_w(a)`.

Thus a universal winner is unsupported; the result is `PRICE_SENSITIVE` unless phrased explicitly conditional on the registered price vector.

### R4c — finite sampled weights do not prove universal scalarization invariance

For the same `a,b`, both sampled weights `(3,2)` and `(4,2)` select `a`, yet positive weight `(1,4)` selects `b`. Therefore agreement on finitely many registered weights establishes only invariance at those weights. It does not establish invariance over the full positive orthant, Pareto completeness, or recovery of unsupported Pareto points. QED by counterexample.

## 6. Control compliance is orthogonal to robustness

Let the four structural control predicates be `P1,...,P4`, and let `I_j` denote whether control `j` preserves the registered canonical conclusion.

Define

`CONTROL_REQUIREMENTS_SATISFIED <=> P1 and P2 and P3 and P4`.

Conditional on that:

- `ROBUST_AT_REGISTERED_CONTROLS <=> all I_j`;
- `SENSITIVE_AT_REGISTERED_CONTROLS <=> exists j: not I_j`.

Therefore

`CONTROL_REQUIREMENTS_SATISFIED` does **not** imply `ROBUST_AT_REGISTERED_CONTROLS`.

The frozen sensitive fixture is the exact counterexample: all four controls are validly present, while the remint, alternate search, and alternate scalarization each change the canonical conclusion. This distinction is necessary so a scientifically valuable negative result is not treated as a missing control.

## 7. Missing-control completeness certificate

There are four required blocks. The executor enumerates all `2^4=16` present/missing masks. Exactly one mask—the all-present mask—satisfies the structural requirements. All other masks terminate fail-closed rather than defaulting to robustness.

This is a complete certificate for missing-block logic only; it is not an exhaustive census of all malformed contents inside each block.

## 8. Strongest claim and falsifiers

If the executor/tests/CI and exact #833 reconciliation are green, the strongest earned statement is:

`GMI_DERIVATION_ROBUSTNESS_CONTROL_REQUIREMENTS_FORMALIZED_AT_REGISTERED_FINITE_SCOPE`.

Falsifiers include:

- a grammar twin accepted despite changed mechanism-free background multiplicity or changed context;
- a non-bijective/nonsemantic remint treated as invariance evidence;
- two renamed instances of one search signature accepted as materially distinct algorithms;
- unequal search budgets silently compared as algorithm invariance;
- duplicate/nonpositive scalar weights accepted as alternate valid prices;
- a dominated candidate selected under a strictly positive weighted minimization;
- a missing required control producing `ROBUST` or `CONTROL_REQUIREMENTS_SATISFIED`;
- any promotion to the forbidden claims listed in the freeze/manifest.

None of this establishes that the whole GMI corpus is robust, architecture-neutral, representation-invariant, optimizer-independent, or scalarization-independent. Those require running these controls on each target claim.
