# GMI Operational Completeness Theorem V1

Status: **THEOREM AT FINITE OPERATIONAL SCOPE WITH DECIDABLE COMPARISONS AND COST-LABEL REACHABILITY**
Date: 2026-09-13
Base: `main@19bc38f588e5af10f97dfd9fd75ca507d602c018`

## 0. Why the target changes

The executed GMI record has already falsified a stronger and unnecessary target: a theory of intelligence cannot, in general, be required to recover one unique architecture or one computable canonical source-level normal form. Fine architecture can be below operational probe resolution, multiple morphologies can share one frontier profile, and unrestricted observational equivalence over a Turing-complete IR is undecidable.

Those are boundary theorems, not incomplete work. The scientifically meaningful completeness target is therefore **operational**:

> Given a declared ecology, obligation, channel contract, finite operational resolution and resource meter with decidable exact comparisons, determine the attainable capability set, its Pareto frontier and operational realization fibers. Under a declared finite development process, separately determine which global optima are reachable and which reachable realizations are optimal within the development constraint.

This document closes that target for finite registered scopes.

## 1. Finite operational universe

A finite GMI operational problem is the tuple

\[
\mathfrak G=(\mathcal M,W,H,A,Y,Z,K,V,C,\rho,\Theta),
\]

where `mathcal M` is an explicitly registered, finite, effectively enumerable domain of admitted **operational realizations**. All alphabets and the horizon are finite, `K` is a finite registered set of legal transition/action kernels (or a finite exact rational grid), `V,C` are decidable verifier/constitution predicates, and `Theta` is the finite registered intervention/context set. Trace probabilities and resource coordinates must have effective exact arithmetic and decidable equality/order for every comparison used below. Exact rationals suffice; effectively represented real algebraic numbers also suffice. Another representation requires supplied total decision procedures for the required predicates. Mere computability of a real-valued coordinate is insufficient.

One sufficient registration is a finite candidate table with its resource meters. Another is all operational transition tables over fixed finite state/history domains, with a fixed finite kernel menu and a resource meter determined by each table. Any additional physical implementation alternatives or resource overhead must also be restricted by the finite registration; they are not automatically bounded by the observable alphabets.

Two registered realizations are equivalent for capability/resource comparison when they induce the same protected trace distribution and resource vector. Their finite register may still retain distinct operational tables, allowing realization fibers to contain more than one candidate. Unprotected source spellings or parameter permutations are not an invitation to enumerate arbitrary source programs: fibers below refer only to `mathcal M`, or to an explicitly supplied finite effective representative register.

### Finiteness of responses does not imply finiteness of resource profiles

Let every protected alphabet be a singleton, the protected horizon be one and the legal behavior have one kernel. Admit implementations `M_n`, `n>=0`, all giving that same response but carrying `n` units of invisible physical burden, for example `n` inert extra elements. With `rho(M_n)=n`, there are infinitely many attainable trace/resource profiles despite the one-point response set. Their scalar Pareto minimum exists at `n=0`; this does not make the full attainable set finitely enumerable or justify exhaustive finite enumeration.

A finite hard-bounded resource grid can restrict the number of **possible profiles**. That alone does not decide which profiles are realizable or enumerate all implementations in a profile's fiber. Such a variant needs effective membership/construction procedures and an explicitly finite representative domain if it claims FOC-3's finite fiber enumeration. The theorem below uses the stronger finite domain `mathcal M` directly.

## 2. FOC-1 — exact capability-set theorem

The domain `mathcal M` is finite by registration, independently of the size of its protected response set. Decidable legality selects its legal deterministic realizations. For every selected `M`, its complete protected trace distribution is computed by finite summation, and its resource vector by the registered effective meter.

Therefore the attainable set

\[
\mathcal A_{\mathfrak G}=\{(Q(M),\rho(M)):M\in\mathcal M,\ M\text{ legal}\}
\]

is exactly enumerable, and its nondominated subset is exactly computable.

**Terminal:** `FINITE_OPERATIONAL_CAPABILITY_SET_EXACT = TRUE`.

No statistical estimation is required.

## 3. FOC-2 — exact Pareto-frontier theorem

For the finite exact capability/resource coordinates with the comparison procedures declared in §1, pairwise dominance is decidable. Removing every dominated attainable point yields the exact operational Pareto frontier

\[
\mathcal F_{\mathfrak G}=\operatorname{Pareto}(\mathcal A_{\mathfrak G}).
\]

The accompanying microscope enumerates a two-bit finite world, all 16 deterministic policies and the exact frontier; the best achievable accuracy is `3/4`.

**Terminal:** `FINITE_OPERATIONAL_FRONTIER_EXACT = TRUE`.

## 4. FOC-3 — exact optimal-fiber theorem

Let `p` be any point on the exact frontier. The set

\[
\Phi(p)=\{M\in\mathcal M:M\text{ legal},\ (Q(M),\rho(M))=p\}
\]

is finite and exactly enumerable because it is a decidable subset of the finite register `mathcal M`. Consequently GMI can return **all registered** operationally optimal realizations without pretending that one syntactic representative is privileged. It does not enumerate every physically possible implementation or every source program sharing that profile.

This closes the old false dilemma “unique architecture or incomplete theory.”

**Terminal:** `FINITE_OPERATIONAL_OPTIMAL_FIBER_EXACT = TRUE`.

## 5. FOC-4 — bounded developmental reachability theorem

### 5.1 Finite label closure, including zero-cost cycles

Register a finite directed development graph with state set `S`, initial states `I`, finitely many legal edges, and a computable output map from terminal states into `mathcal M`. Its terminal output image is finite independently of whether a larger physical implementation universe is infinite. The state must contain all information determining future legal moves and terminal output. Assign each edge an additive nonnegative rational cost vector in `Q^q`, and fix finite componentwise rational budgets `B in Q^q_{>=0}`, with `q>=1`. Histories may be merged only when this registered state and their accumulated cost labels agree.

A finite budget does **not** make the path-history tree finite. A zero-cost self-loop can be traversed arbitrarily many times. Instead, compute reachability in the graph of pairs `(s,c)`, where `c` is an accumulated cost vector satisfying `c<=B`.

**Proof of termination and exactness.** Choose a positive integer `L` clearing all edge-cost denominators. Every accumulated coordinate is an integer multiple of `1/L`. Hence at most

\[
|S|\prod_{i=1}^q(\lfloor LB_i\rfloor+1)
\]

state/label pairs are possible. Start from `(s,0)` for `s in I`, repeatedly add legal successor pairs within budget, and expand each pair once. Every added pair has a witnessing path. Conversely induction on path length shows that every budget-feasible path's final pair is eventually included; nonnegative costs ensure its prefixes remain within budget. The closure therefore terminates and is exact even with zero-cost cycles. QED.

Breadth-first traversal of this finite expanded graph additionally gives minimum step counts to each label; a shortest path never repeats an expanded vertex. Scalar minimum development cost is the minimum of the reachable scalar labels. For a vector cost retain its Pareto set: coordinatewise minima from different paths need not form a realizable label. Equality-deduplicated nondominated labels can also be used when only feasibility and cost-optimal labels are requested, since appending the same edge preserves componentwise order. This pruning is not a method for listing every path history or every dominated cost label.

The assumptions are substantive. Negative costs/refunds, history-dependent moves not represented in `S`, or unbounded/unregistered cost coordinates require a different termination argument. With an explicit finite step horizon, the history tree itself is finite; this is a separate sufficient condition.

### 5.2 Reachability restriction precedes Pareto selection

Let `M_feas subseteq mathcal M` be the registered operational machines satisfying all hard capability/resource gates, and let `p(M)=(Q(M),rho(M))`. If there are no additional hard gates, `M_feas` is the legal-machine set of FOC-1. Define

\[
\mathcal A_{feas}=\{p(M):M\in M_{feas}\},\qquad
\mathcal A_B=\{p(M):M\in M_{feas}\cap Reach(B)\}.
\]

The **constrained reachable frontier** is

\[
\mathcal F^{reach}_{\mathfrak G,B}
=\operatorname{Pareto}(\mathcal A_B).
\]

The distinct object **accessible global-optimum profiles** is

\[
\mathcal F^{access}_{\mathfrak G,B}
=\operatorname{Pareto}(\mathcal A_{feas})\cap\mathcal A_B.
\]

Both are exactly computable, and `F^access subseteq F^reach`. To see the inclusion, a reachable profile globally undominated cannot become dominated when the comparison set is restricted. The inclusion can be strict: suppose equally adequate machines `r,u` have scalar operating costs `2,1`, respectively, and only `r` is reachable. Then the global frontier contains only `u`'s profile, so `F^access` is empty, while `F^reach={p(r)}`. Filtering the global frontier would erase the best attainable development-constrained solution.

For each constrained frontier point `p`, the reachable realization fiber is `{M in M_feas intersect Reach(B):p(M)=p}`. Profiles and machines must not be intersected without the profile map. If accumulated development cost is itself a selected coordinate, retain terminal `(state,cost-label)` realizations and their joint declared lifecycle profile before taking Pareto; do not attach an unattainable vector of separate coordinate minima to a machine.

**Terminal:** `FINITE_BUDGET_DEVELOPMENTAL_REACHABILITY_EXACT = TRUE`.

This is intentionally not a theorem about unrestricted unbounded architecture search.

## 6. FOC-5 — finite stochastic extension

If a finite stochastic policy/kernel family is explicitly registered, exact rational transition probabilities make protected expected capability/resource coordinates finite rational sums, so the same enumeration theorem applies.

For standard finite fully observed finite-horizon control with linear expected criteria, the stronger continuous-randomization closure is parent theory: occupancy-measure linear programming gives the exact optimum. GMI claims specialization and typing, not invention of that result.

**Terminal:** `FINITE_REGISTERED_STOCHASTIC_CONTROL_EXACT = TRUE`.

## 7. Completeness statement

> **GMI Finite Operational Completeness Theorem.** For any GMI operational problem with §1's finite effectively enumerable realization domain `mathcal M`, finite trace model, exact arithmetic and decidable comparisons, and a finite development graph into `mathcal M` with §5.1's nonnegative rational additive costs and finite component budgets, GMI can compute exactly: (i) the attainable capability/resource set within that register, (ii) its Pareto frontier, (iii) every registered operational realization fiber on that frontier, and (iv) the reachable feasible set, its own constrained frontier and reachable realization fibers, and the separately identified accessible global-optimum profiles.

This is a full theorem, not a partial empirical result.

### Exact-order boundary for computable reals

Given a program `P`, let `x_P=2^{-t}` if it halts for the first time at step `t>=1`, and `x_P=0` if it never halts. This real is uniformly computable: to error at most `2^{-n}`, simulate `n` steps; output its exact value if it halted and otherwise output zero. A later halt contributes less than `2^{-n}`. But deciding whether `x_P=0` would decide nonhalting, and hence halting. Thus a finite set of machines with merely computable real coordinates does not supply a general exact equality/dominance algorithm. For example, profiles `0` and `x_P` are tied exactly when `P` never halts; otherwise the latter is strictly dominated.

Certified intervals can support approximate or separated comparisons, but an unresolved equality must remain undecided unless the declared arithmetic class supplies a decision procedure. The finite delayed-halting witnesses below illustrate this boundary; the undecidability conclusion is the analytic reduction, not a result of bounded simulation.

## 8. What is no longer a “gap”

The following are not requirements of a complete operational theory and must not be silently reintroduced:

- unique source syntax for an operational behavior;
- a computable canonical normal form over unrestricted Turing-complete programs;
- architecture identity below the declared probe resolution;
- historical novelty of every optimal mechanism;
- unbounded developmental closure from a finite experiment.

They are either non-identifiable, parent-owned or mathematically impossible at unrestricted scope.

## 9. Executable witness

`gmi_microscope/run_gmi_operational_closure_v1.py` contains the finite frontier microscope. `test_gmi_operational_closure_v1.py` re-runs it together with the channel-composition and neural-compilation checks.

`../gmi-grand-unification-v1/grand_gmi_operational_reachability_checks_v1.py` and its companion test add independent bounded checks for reachable-frontier selection, exact state/cost-label closure with zero-cost cycles, resource-label tradeoffs, the computable-real comparison boundary, and response cardinality versus resource-profile cardinality. Their scope and correction IDs are recorded in `../gmi-grand-unification-v1/RECURSIVE_AUDIT_OPERATIONAL_REACHABILITY_V1.md`; the historical operational-closure receipt is retained unchanged.

The graph algorithms are parent theory; see [Dijkstra, *A Note on Two Problems in Connexion with Graphs* (1959)](https://ir.cwi.nl/pub/9256/9256D.pdf) for exact shortest-path reasoning. The finite cost-label and constrained-frontier proofs here state the additional resource and feasibility hypotheses explicitly; they do not infer correctness for arbitrary search histories from the finite-state label result.
