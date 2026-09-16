# GMI #833 Search-Law Morphology-Change Theorems V1

Status: **FINITE THEOREM / EXACT TWO-LAW CENSUS / HOSTILE-CLOSED AT REGISTERED SCOPE**  
Source issue: #879  
Master checklist: #833 Section J, exactly one row: `Derive when search law changes observed morphology.`  
Freeze: `619e44aca017d288435afce6e6f9765e675dde6a`  
Source main: `6368cda406d8e3395283049abacb36129ae94637`

Claim ceiling:

`GMI_FINITE_DETERMINISTIC_SEARCH_LAW_MORPHOLOGY_DISAGREEMENT_DERIVED_AT_REGISTERED_SCOPE`

## 1. Independent review lenses and parent subtraction

This tranche was checked under four roles:

1. **Search theory:** verify charged completion-prefix semantics and the geometry induced by two completion schedules.
2. **Optimization:** separate objective-value disagreement from morphology-identity disagreement.
3. **Algorithm selection / search bias:** keep dependence on the registered search law explicit and identify conditions under which it disappears.
4. **Formal methods:** make ties, pre-evaluation terminals, rational thresholds, malformed laws, and objective-semantic mismatches fail closed.

The generic idea that algorithm choice matters is parent-owned. Rice's *The Algorithm Selection Problem* (Advances in Computers 15, 1976, pp. 65–118) supplies the classical algorithm-selection frame. Zilberstein's *Using Anytime Algorithms in Intelligent Systems* (AI Magazine 17(3), 1996, pp. 73–83) treats computation time as a resource traded against result quality. Tie-breaking effects in best-first search are also established parent territory; see Asai & Fukunaga, *Tie-Breaking Strategies for Cost-Optimal Best First Search* (JAIR 58, 2017, pp. 67–121).

Merged GMI parents already go further empirically:

- #712 / E1 demonstrates finite-budget search and encoding dependence on one frozen target;
- #724 / E2 compares multiple parent-owned search mechanisms on one world;
- #877 derives the exact one-law finite-prefix incumbent and recovery threshold `B*`;
- #864 explicitly keeps semantic remint invariance separate from search-order invariance.

The residual here is therefore narrow: an exact **two registered deterministic search-law** disagreement theorem with value/identity decomposition, threshold-cell geometry, and conditions for eventual agreement versus tie-persistent identity disagreement.

## 2. Registered objects

Let:

- `M` be a finite nonempty morphology set;
- `f:M->Q` be one exact scalar objective to minimize;
- `L_j=(pi_j,c_j)` for `j in {1,2}` be complete deterministic search laws;
- `pi_j` be a permutation of `M`;
- `c_j:M->Q_{>0}` be strictly positive exact evaluation costs;
- both laws use the same earliest-seen tie policy.

For law `j`, let cumulative completion thresholds be

`C_{j,k}=sum_{i<=k} c_j(pi_{j,i})`.

At exact budget `B>=0`, #877's parent rule exposes the maximal completed prefix. If none exists, write `I_j(B)=NO_EVALUATED_CANDIDATE`; otherwise `I_j(B)` is the earliest-seen objective minimum in that prefix and `q_j(B)=f(I_j(B))`.

Let `A*=Argmin_M f`. Let `B*_j` be the first completion threshold of a member of `A*` under law `j`.

## 3. SLM-1 — disagreement is piecewise constant on the joint threshold partition

Let `T` be the sorted union of all completion thresholds from both laws. Partition nonnegative budgets into half-open cells

`[0,t_1), [t_1,t_2), ..., [t_r,infinity)`.

On every such cell, the pair

`(I_1(B), I_2(B))`

is constant. Hence the cross-law identity-disagreement indicator can change only at a threshold in `T`.

### Proof

For one deterministic positive-cost law, no candidate changes completion status between two consecutive cumulative thresholds. Therefore its evaluated prefix and earliest-seen prefix argmin are constant on each interval between thresholds. Refining both laws' individual threshold partitions by their sorted union produces cells on which **both** prefixes are constant. Their selected identities, values, and disagreement classification are therefore constant on each joint cell. QED.

This theorem concerns the observable selected morphology, not arbitrary internal states of a search algorithm.

## 4. SLM-2 — exact disagreement decomposition

At any budget where both laws have an incumbent and `I_1(B) != I_2(B)`, exactly one of the following holds:

1. **value disagreement:** `q_1(B) != q_2(B)`;
2. **equal-value identity disagreement:** `q_1(B) = q_2(B)` but `I_1(B) != I_2(B)`.

The two cases are mutually exclusive and exhaustive.

If exactly one law has an incumbent, the machine-distinct classification is `DISAGREEMENT_AVAILABILITY` and no fictitious objective value is assigned to the empty law.

### Proof

Equality of exact rational objective values is decidable. For two existing incumbents with different identities, either their values are equal or they are not. These cases partition all possibilities. If one incumbent does not exist, comparing its value would be ill-typed, so the availability case is separate. QED.

This prevents a common promotion error: equal performance does not imply identical morphology.

## 5. SLM-3 — changing the search law need not change observed morphology

Different registered search laws can induce the same observed morphology for one budget, many budgets, or every budget.

### Exact witness

Let

- `f(best)=0`, `f(mid)=1`, `f(bad)=2`;
- unit costs;
- `L1=(best,mid,bad)`;
- `L2=(best,bad,mid)`.

The laws differ, but:

- at budget 0 both return `NO_EVALUATED_CANDIDATE`;
- at every budget `B>=1`, both select `best`.

Therefore

`L1 != L2`

does **not** imply

`I_1(B) != I_2(B)`.

The scientific object is the law-conditioned observable, not law identity by itself.

## 6. SLM-4 — a unique global optimum erases deterministic law dependence after joint recovery

Suppose `A*={m*}` is a singleton. Then for every

`B >= max(B*_1,B*_2)`,

both laws select `m*`.

### Proof

By #877 FSB-4, at `B>=B*_j`, law `j` has completed at least one global optimizer and therefore recovers the global optimum value. Since the global optimizer is unique, every prefix morphology attaining that value is `m*`. Thus both laws select `m*` once both recovery thresholds have been crossed. QED.

This is an identity theorem only because uniqueness is an explicit premise.

## 7. SLM-5 — global ties can preserve identity disagreement forever

If the full-space global optimum is not unique, complete search need not erase morphology identity dependence.

### Exact witness

Let

- `f(a)=f(b)=0`, `f(c)=1`;
- unit costs;
- `L1=(a,b,c)`;
- `L2=(b,a,c)`.

At complete budget both laws have zero regret and have evaluated all candidates. Yet earliest-seen tie-breaking selects `a` under `L1` and `b` under `L2`.

Thus:

`q_1=q_2=q*`

can coexist with

`I_1 != I_2`.

Completeness guarantees global **value** recovery, not search-law-invariant optimizer identity when global ties exist.

## 8. SLM-6 — injective objectives eliminate identity-only disagreement

If `f` is injective on `M`, then whenever both incumbents exist,

`I_1(B) != I_2(B)  =>  q_1(B) != q_2(B)`.

### Proof

Injectivity gives `x != y => f(x) != f(y)` for every pair of morphologies. Apply this directly to the two incumbent identities. QED.

Therefore the equal-value identity branch is a tie phenomenon, not an artifact of the classifier.

## 9. Rational-cost threshold witness

The implementation includes a non-unit exact-rational example with different completion schedules. Its joint threshold partition is

`[0,1/2), [1/2,3/2), [3/2,2), [2,3), [3,4), [4,infinity)`.

The classifications across those cells are respectively:

1. both empty;
2. availability disagreement;
3. value disagreement;
4. identity agreement;
5. value disagreement;
6. identity agreement.

Several exact rational representatives are checked inside every cell. All signatures are constant, exercising SLM-1 independently of the unit-cost exhaustive census.

## 10. Exact bounded census

The executable checker enumerates all worlds with:

- `1 <= |M| <= 4`;
- objective alphabet `{0,1,2}`;
- unit evaluation costs;
- every ordered pair of complete search permutations;
- every integer budget from `0` through `|M|`.

Exact totals:

- **47,667** ordered search-law pairs;
- **237,282** law-pair/budget points;
- **47,724** value-disagreement points;
- **56,130** equal-value identity-disagreement points;
- **5,220** changed-law worlds with agreement at every checked budget;
- **14,784** tied-global worlds with identity disagreement at complete budget;
- zero theorem/decomposition failures.

The census is a bounded implementation certificate. SLM-1 through SLM-6 are finite analytic consequences of the registered premises and do not depend on extrapolating the census.

## 11. Parent boundary

### #877

#877 owns one-law finite-budget prefix selection, regret monotonicity, and the recovery threshold `B*`. This child imports those semantics and compares two laws; it does not re-claim FSB-1…FSB-6.

### #712 / #724

These merged Section-E packages already demonstrate that search/encoding/searcher choice can change finite-budget recovery. Their stochastic/differentiable mechanisms remain **evidence only** here. SLM is not a stochastic-search theorem.

### Algorithm-selection / anytime parents

Rice and anytime-computation theory already own the broad proposition that algorithm choice and computational resource allocation affect outcomes/quality. The GMI residual is only the exact morphology-observable integration and claim governance above.

## 12. Falsifiers and fail-closed conditions

The implementation rejects:

- empty or duplicate morphology universes;
- incomplete, duplicate, or non-permutation search traces;
- missing, extra, floating-point, or Boolean objective entries;
- missing, extra, zero, negative, floating-point, or Boolean costs;
- negative, floating-point, or Boolean budgets;
- comparison of laws registered on different morphology universes;
- comparison under different objective semantics.

Before any candidate completes, selection remains typed `NO_EVALUATED_CANDIDATE`; no morphology or objective value is fabricated.

A valid counterexample to SLM-1…SLM-6 under these exact premises would falsify this tranche.

## 13. Forbidden extrapolations

This tranche alone does not establish:

- that every search-law change changes morphology;
- search-law-invariant morphology identity under global ties;
- a stochastic-search law theorem;
- universal searcher dominance;
- real optimizer convergence;
- prospective held-out morphology transitions;
- P3 recovery;
- complete GMI.

Its only earned conclusion is the finite deterministic two-law morphology-disagreement theorem at the registered scope.
