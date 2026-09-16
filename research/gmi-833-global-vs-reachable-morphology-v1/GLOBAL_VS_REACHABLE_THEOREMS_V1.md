# GMI #833 Global-vs-Reachable Morphology Selection Theorems V1

Status: **FINITE THEOREM / EXACT WITNESS / HOSTILE-CLOSED AT REGISTERED SCOPE**  
Source issue: #874  
Master checklist: #833 Section J, exactly one row: `Separate optimal morphology from reachable morphology.`  
Freeze: `e5b0c534e5d316c90e28dff0678ee6038b25e3a5`  
Source main: `367e14e9296cf79924ce56d89fad34b3769acb5d`

Claim ceiling:

`GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE`

## 1. Review roles and parent boundary

This tranche was checked under four distinct lenses:

1. **Optimization:** keep unconstrained/global and feasible/reachable optima mathematically distinct.
2. **Developmental systems:** treat the reachable set as produced by a registered developmental law/budget, not as an arbitrary post-hoc deletion.
3. **Multiobjective/Pareto:** keep Pareto efficiency relative to the feasible set and do not infer a false frontier-subset law.
4. **Formal/hostile:** make every set relation and quantifier executable and attack ties, empty sets, malformed profiles, and false reachability nesting.

The underlying optimization mathematics is parent-owned. Standard constrained optimization defines optimization over a feasible set (Boyd & Vandenberghe, *Convex Optimization*, Cambridge University Press, 2004). Standard multiobjective optimization defines Pareto/nondominated status relative to the feasible set (e.g. Miettinen, *Nonlinear Multiobjective Optimization*, Kluwer/Springer, 1999). This tranche does not claim those facts as GMI novelty.

The GMI-specific residual is the exact integration of those parent facts with a **registered developmental reachability set**, corrected DRS lifecycle custody, a machine-checkable claim ceiling, and explicit hostiles against common promotion errors.

## 2. Objects and scope

Let:

- `M` be a finite nonempty registered morphology set;
- `R` be a finite nonempty reachable subset, `R ⊆ M`;
- `f : M -> Q` be an exact rational scalar objective to minimize;
- `p : M -> Q^d` be an exact rational resource/profile vector to minimize componentwise.

No theorem below asserts that a real learning/search/evolution process discovers a globally optimal path. The reachable set must come from separately registered developmental evidence.

## 3. GVR-1 — restricting reachability cannot improve the scalar optimum

For nonempty `R ⊆ M`,

\[
\min_{m\in M} f(m) \le \min_{r\in R} f(r).
\]

### Proof

Every element of `R` is also an element of `M`. Therefore the minimum over `M` is no larger than `f(r)` for every `r in R`, and hence no larger than the minimum over `R`. QED.

This is a feasible-set monotonicity fact, not a statement about algorithmic convergence.

## 4. GVR-2 — exact condition for reaching the global optimum value

Let

\[
A^\* = \operatorname{Argmin}_{m\in M} f(m).
\]

Then

\[
\min_{r\in R} f(r) = \min_{m\in M} f(m)
\quad\Longleftrightarrow\quad
R\cap A^\* \ne \varnothing.
\]

### Proof

**If.** If some `r*` lies in both `R` and `A*`, then `f(r*)` is the global optimum value. The reachable minimum is at most `f(r*)`, while GVR-1 says it is at least the global optimum value; equality follows.

**Only if.** If the reachable and global optimum values are equal, choose a reachable minimizer `r*`. Its value equals the global minimum, so `r* in A*`, proving a nonempty intersection. QED.

This is the precise finite separation between “globally optimal” and “developmentally reachable.”

## 5. GVR-3 — equal optimum value does not identify the same optimizer set

The equality in GVR-2 is a **value** statement, not an identity statement.

Counterexample:

- `M={a,b,c}`;
- `f(a)=f(b)=0`, `f(c)=1`;
- `R={b,c}`.

Then both global and reachable optimum values are `0`, but

\[
\operatorname{Argmin}_M f=\{a,b\},\qquad
\operatorname{Argmin}_R f=\{b\}.
\]

Therefore equal best values do not justify “the same morphology was selected.”

## 6. GVR-4 — monotone reachability improves or preserves the best scalar value

For two nonempty reachable sets with

\[
R_1\subseteq R_2\subseteq M,
\]

we have

\[
\min_{r\in R_2} f(r) \le \min_{r\in R_1} f(r).
\]

### Proof

Apply GVR-1 with `R2` as the containing feasible set and `R1` as its nonempty subset. QED.

For a developmental budget family with `Reach_B1 ⊆ Reach_B2`, this means the best reachable **scalar** objective cannot worsen as the feasible set expands. It does not imply that the full lifecycle Pareto frontier shrinks, or that a unique morphology exists.

## 7. GVR-5 — Pareto efficiency is relative to the reachable feasible set

Write `Pareto(S)` for the points in nonempty finite `S` that are not dominated, under componentwise minimization, by another point of `S`.

For `R ⊆ M`,

\[
\operatorname{Pareto}(M)\cap R
\subseteq
\operatorname{Pareto}(R).
\]

### Proof

Take `x in Pareto(M) ∩ R`. If `x` were not Pareto-efficient in `R`, some `y in R` would dominate it. Since `R ⊆ M`, the same `y` would dominate `x` in `M`, contradicting `x in Pareto(M)`. QED.

### The reverse inclusion is false

Let:

- `a=(0,0)`;
- `b=(1,1)`;
- `c=(0,2)`;
- `M={a,b,c}`;
- `R={b,c}`.

Globally, `a` dominates both `b` and `c`, so `Pareto(M)={a}`. After `a` is made unreachable, `b` and `c` are incomparable, so `Pareto(R)={b,c}`.

Thus a morphology can be globally dominated yet become reachable-Pareto-efficient solely because its dominator is unreachable. The forbidden shortcut

`Pareto(R) ⊆ Pareto(M)`

is therefore explicitly false.

## 8. Exact bounded certificates

The executable checker independently enumerates:

- **1,434** finite scalar world/reachable-subset cases for GVR-1 and GVR-2;
- **5,826** nested reachable-set cases for GVR-4;
- **500** finite two-objective world/reachable-subset cases for GVR-5;
- **130** Pareto cases in which restriction creates at least one reachable-only efficient point.

All registered theorem checks have zero failures.

Enumeration is a bounded certificate of the implementation. The analytic proofs above, not the census alone, establish the stated finite set-theoretic implications.

## 9. Corrected DRS parent witness

The current parent authority is:

`research/gmi-grand-unification-v1/GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_RECEIPT_V2.json`

with frozen Git blob:

`8b7acb21cc21d41e54b23c91a9fca75af5612208`.

The parent registers deployment profiles:

- `N_good`: `(2,2)`, reachable from the neutral start at developmental cost 2;
- `P_good`: `(1,1)`, reachable at cost 3;
- `X_ideal`: `(0,0)`, reachable at cost 10.

For a deliberately separate **deployment-only scalar projection** `f=sum(deployment coordinates)`, the reachable best score improves:

- budget 2: `4`, `N_good`;
- budget 3: `2`, `P_good`;
- budget 10: `0`, `X_ideal`.

This child projection illustrates GVR-4 only. It does **not** replace the corrected parent's full lifecycle Pareto result:

- budget 2 frontier: `{N_good}`;
- budget 3 frontier: `{N_good,P_good}`;
- budget 10 frontier: `{N_good,P_good,X_ideal}`.

The distinction matters because development cost remains a protected resource coordinate in the parent lifecycle analysis.

## 10. Falsifiers and fail-closed conditions

The implementation rejects rather than silently interpreting:

- an empty morphology universe;
- an empty reachable set;
- reachable elements outside `M`;
- duplicated morphology identities;
- missing or extra scalar objective entries;
- floating-point or Boolean “exact” objectives;
- a declared reachability expansion where `R1` is not a subset of `R2`;
- missing Pareto profiles;
- empty or dimension-mismatched profile vectors;
- floating-point Pareto coordinates;
- dimension-mismatched dominance comparisons.

A counterexample to any registered analytic implication under these exact finite premises would falsify this tranche.

## 11. Forbidden extrapolations

This tranche alone does not establish:

- that a global optimum is always reachable;
- convergence of any real optimizer;
- unique morphology selection;
- that the reachable Pareto frontier is a subset of the global Pareto frontier;
- unrestricted continuous/Turing-complete optimization;
- prospective morphology-transition prediction;
- P3 recovery;
- complete GMI.

Its only earned conclusion is the finite, registered-scope separation between global and developmentally reachable selection.
