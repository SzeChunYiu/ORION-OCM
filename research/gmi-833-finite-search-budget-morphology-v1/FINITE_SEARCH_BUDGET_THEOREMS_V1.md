# GMI #833 Finite Search-Budget Morphology Selection Theorems V1

Status: **FINITE THEOREM / EXACT CENSUS / HOSTILE-CLOSED AT REGISTERED SCOPE**  
Source issue: #877  
Master checklist: #833 Section J, exactly one row: `Derive morphology under finite search budgets.`  
Freeze: `ea8bb2d457ee96ebedc2a3a74a735284690a0973`  
Source main: `4de059b76c0a805f616b645eab636580394a42ed`

Claim ceiling:

`GMI_FINITE_SEARCH_PREFIX_MORPHOLOGY_SELECTION_DERIVED_AT_REGISTERED_SCOPE`

## 1. Review roles and parent boundary

This tranche was reviewed through four independent lenses:

1. **Search theory:** make budget mean a charged prefix of a registered search schedule rather than free candidate access.
2. **Optimization:** distinguish the finite-prefix incumbent from the full-space optimum and derive the exact recovery threshold.
3. **Algorithm selection / search bias:** preserve dependence on search order, encoding, and cost schedule rather than laundering them into morphology invariants.
4. **Formal / hostile review:** make empty prefixes, ties, positive-cost assumptions, exact thresholds, and alternate schedules machine-explicit.

Fixed-budget search is established parent territory; for example, Stern, Puzis & Felner (ICAPS 2011) formulate search under a fixed solution-cost budget, and the broader anytime/budgeted-search literature studies solution quality as computation resources increase. The merged GMI Section-E packages #712 and #724 already provide exact finite-budget and cross-search evidence. This tranche does not claim a new search method.

The residual here is a small deterministic theorem/schema connecting a **registered charged search trace** to the morphology observable at each finite search budget.

## 2. Registered objects

Let:

- `M={m_1,...,m_n}` be a finite nonempty morphology set;
- `f:M->Q` be an exact scalar objective to minimize;
- `pi=(pi_1,...,pi_n)` be a complete permutation of `M`;
- `c:M->Q_{>0}` be strictly positive exact candidate-evaluation costs;
- `B in Q_{\ge 0}` be an exact budget.

Define cumulative completion costs

`C_k = sum_{i=1}^k c(pi_i)`.

Strict positivity implies

`0 < C_1 < C_2 < ... < C_n`.

Define

`k(B)=max({k : C_k <= B} union {0})`

and the evaluated prefix

`P_B={pi_1,...,pi_{k(B)}}`.

If `k(B)=0`, the selection terminal is `NO_EVALUATED_CANDIDATE`.

If `k(B)>0`, define the incumbent `I(B)` as the **earliest-seen** member of `P_B` attaining

`q(B)=min_{m in P_B} f(m)`.

Let the global optimum value be

`q*=min_{m in M} f(m)`

and exact regret, where an incumbent exists, be

`r(B)=q(B)-q*`.

## 3. FSB-1 — budgets expose maximal completion prefixes

For each `B`, the evaluated candidates are exactly the first `k(B)` elements of `pi`.

Moreover:

- if `0 <= B < C_1`, the prefix is empty;
- if `C_k <= B < C_{k+1}`, the prefix is exactly the first `k` candidates;
- if `B >= C_n`, the prefix is all of `M`.

### Proof

Because every cost is strictly positive, the cumulative sequence `C_k` is strictly increasing. A candidate at position `k` has completed exactly when its cumulative completion cost `C_k` is at most `B`. Therefore the completed indices form an initial segment, and the largest completed index is exactly `k(B)`. No later index can complete while an earlier cumulative threshold has not been reached. QED.

The positive-cost premise is important: it makes candidate-completion thresholds strictly ordered and excludes zero-cost hidden evaluations.

## 4. FSB-2 — finite-budget morphology is the prefix argmin

For `k(B)>0`,

`I(B) = earliest_pi Argmin_{m in P_B} f(m)`.

For `k(B)=0`, no morphology is selected.

This is a definition-level selection rule, but it closes an important scientific ambiguity: a finite search budget does not license choosing from unevaluated morphologies, and an empty search prefix is not silently mapped to a default architecture.

## 5. FSB-3 — incumbent value and regret are budget-monotone

If `B_1 <= B_2` and both budgets expose at least one candidate, then

`P_{B_1} subseteq P_{B_2}`,

so

`q(B_2) <= q(B_1)`.

Consequently

`0 <= r(B_2) <= r(B_1)`.

Both functions are stepwise constant between candidate-completion thresholds.

### Proof

FSB-1 makes search prefixes nested in budget. The minimum of a function over a superset cannot exceed its minimum over a subset. Since `q*` is the minimum over all of `M`, every prefix minimum is at least `q*`, giving nonnegative regret. Subtracting the same `q*` preserves the monotonic inequality. QED.

This is an incumbent-quality theorem, not a claim that more computation makes every internal search state better.

## 6. FSB-4 — exact global-recovery threshold

Let

`A*=Argmin_{m in M} f(m)`.

Define

`B_star = min { C_i : pi_i in A* }`.

Then

`q(B)=q*  iff  B >= B_star`.

### Proof

**If.** At `B>=B_star`, at least one globally optimal morphology has completed. Its objective value is `q*`, so the prefix minimum is at most `q*`. It cannot be below the global minimum, hence equality.

**Only if.** If `q(B)=q*`, the evaluated prefix contains a morphology whose objective value is global-optimal. Let its position be `i`. Completion requires `C_i<=B`. Since `B_star` is the minimum completion threshold among all global optimizers, `B_star<=C_i<=B`. QED.

Thus a registered deterministic finite search schedule has an exact morphology-recovery budget. The threshold is schedule-dependent, not an intrinsic property of the objective alone.

## 7. FSB-5 — exact incumbent identity-change criterion

Consider a completion threshold `C_k` after an incumbent already exists (`k>=2`). Let the previous incumbent value be `q(C_k^-)`.

Under earliest-seen tie-breaking:

`I(C_k) != I(C_k^-)  iff  f(pi_k) < q(C_k^-)`.

### Proof

There are three cases.

1. `f(pi_k) < q(C_k^-)`: the new candidate is strictly better than every previous minimizer, so it becomes incumbent.
2. `f(pi_k) > q(C_k^-)`: it cannot be an argmin, so the incumbent stays.
3. `f(pi_k) = q(C_k^-)`: it joins the minimizing set, but the previous incumbent appeared earlier in `pi`, so earliest-seen tie-breaking preserves the previous identity.

Therefore identity changes exactly on strict improvement. QED.

The first completion threshold is classified separately as `INITIAL_SELECTION`, not as a change from an invented prior morphology.

## 8. FSB-6 — complete recovery and order dependence coexist

At `B>=C_n`, FSB-1 gives `P_B=M`, so FSB-2 selects a global optimizer.

But finite-budget morphology and `B_star` need not be invariant under a semantics-preserving reordering of the same candidate set.

Exact witness:

- objective: `best=0`, `mid=1`, `bad=2`;
- all evaluation costs: `1`.

Order A:

`(best, mid, bad)` gives `B_star=1` and selects `best` at budget 1.

Order B:

`(bad, mid, best)` gives `B_star=3` and selects `bad` at budget 1.

Both complete searches recover the same unique global optimum. Their finite-budget observed morphology differs.

This is the theorem-level form of the search-prior distinction already evidenced empirically in merged Section-E work.

## 9. Tie hostile — equal value does not force identity promotion

Let:

- order `(a,b,c)`;
- `f(a)=f(b)=0`, `f(c)=1`;
- unit costs.

At budget 1, `a` is incumbent. At budget 2, `b` becomes an additional global optimizer but does not replace `a` under the frozen earliest-seen tie policy.

Therefore:

- global optimum **value** can already be recovered;
- additional optimal morphologies can later be evaluated;
- selected **identity** need not change.

A theorem that equates “new equal optimum became available” with “morphology transition occurred” is false under this registered selector.

## 10. Exact bounded certificate

The executable checker exhaustively enumerates:

- morphology counts `1..4`;
- objective values in `{0,1,2}`;
- positive evaluation costs in `{1,2,3}`;
- every search permutation;
- every integer budget from `0` through total completion cost.

Exact census:

- **162,009** schedule worlds;
- **1,448,631** budget points;
- zero theorem failures;
- more than 100,000 strict incumbent-improvement events;
- more than 160,000 equal-value non-promotion events;
- explicit empty-prefix and zero-regret cases.

The census is a bounded certificate of the implementation. FSB-1 through FSB-6 are established by the analytic finite proofs above, not by extrapolating from enumeration.

## 11. Parent evidence retained, not re-claimed

### #712 / E1

E1 already proves exact finite-budget search/encoding dependence in a frozen affine world. In particular, its one-bit BFS target is not yet verified at a 20-verification cap because the target appears at verification index 21, while alternate parent-owned schedules/encodings differ.

This child does not re-run or re-label E1 as new science.

### #724 / E2

E2 already compares several parent-owned search mechanisms on one frozen world and shows finite-budget recovery dependence on the search mechanism.

Some E2 searchers are stochastic or differentiable. Those results are **outside** the deterministic complete-permutation theorem here and remain parent evidence only.

### #874

#874 proves the global-vs-reachable selection separation. The present theorem refines a different axis: even when a candidate is in the finite search universe, a finite charged search prefix may not yet have evaluated it.

### #395

#395 already states that a normative realization optimum can differ from the morphology found by bounded morphogenesis. This child supplies a narrow exact prefix theorem under stronger registered deterministic assumptions; it does not re-claim the conceptual split.

## 12. Falsifiers and fail-closed conditions

The implementation rejects:

- empty or duplicate morphology universes;
- incomplete, duplicate, or non-permutation search traces;
- missing or extra objective entries;
- floating-point or Boolean objective values;
- missing or extra evaluation costs;
- zero, negative, floating-point, or Boolean costs;
- negative, floating-point, or Boolean budgets.

It returns `NO_EVALUATED_CANDIDATE` rather than fabricating a morphology before the first completion threshold.

A valid counterexample to any FSB theorem under the exact registered premises would falsify this tranche.

## 13. Forbidden extrapolations

This tranche alone does not establish:

- a new search algorithm;
- universal searcher dominance;
- a stochastic-search theorem;
- adaptive or nonstationary-cost search guarantees;
- real optimizer convergence;
- architecture-prior-free recovery;
- prospective held-out morphology-transition prediction;
- P3 recovery;
- complete GMI.

Its only earned conclusion is the finite deterministic search-prefix morphology-selection theorem at the registered scope.
