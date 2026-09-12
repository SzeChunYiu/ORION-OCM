# GMI Operational Completeness Theorem V1

Status: **THEOREM AT DECLARED FINITE OPERATIONAL SCOPE**  
Date: 2026-09-12  
Base: `main@19bc38f588e5af10f97dfd9fd75ca507d602c018`

## 0. Why the target changes

The executed GMI record has already falsified a stronger and unnecessary target: a theory of intelligence cannot, in general, be required to recover one unique architecture or one computable canonical source-level normal form. Fine architecture can be below operational probe resolution, multiple morphologies can share one frontier profile, and unrestricted observational equivalence over a Turing-complete IR is undecidable.

Those are boundary theorems, not incomplete work. The scientifically meaningful completeness target is therefore **operational**:

> Given a declared ecology, obligation, channel contract, finite operational resolution and resource meter, determine the attainable capability set, its Pareto frontier, the operational equivalence/fiber of optimal realizations, and—under a declared finite development process—the reachable part of that frontier.

This document closes that target for finite registered scopes.

## 1. Finite operational universe

A finite GMI operational problem is the tuple

\[
\mathfrak G=(W,H,A,Y,Z,K,V,C,\rho,\Theta),
\]

where all alphabets and the horizon are finite, `K` is a finite registered set of legal transition/action kernels (or a finite exact rational grid), `V,C` are decidable verifier/constitution predicates, `rho` is an exactly computable resource vector, and `Theta` is the finite registered intervention/context set.

A machine is identified operationally only by the trace distribution it induces on this tuple plus its registered resource vector. Source spelling, parameter permutation, graph isomorphism below probe resolution and other unobserved implementation details are intentionally quotiented out.

## 2. FOC-1 — exact capability-set theorem

Because every component is finite, the set of legal deterministic operational machines is finite. For every such machine `M`, its complete protected trace distribution and resource vector are computable exactly by finite summation.

Therefore the attainable set

\[
\mathcal A_{\mathfrak G}=\{(Q(M),\rho(M)):M\text{ legal}\}
\]

is exactly enumerable, and its nondominated subset is exactly computable.

**Terminal:** `FINITE_OPERATIONAL_CAPABILITY_SET_EXACT = TRUE`.

No statistical estimation is required.

## 3. FOC-2 — exact Pareto-frontier theorem

For any finite family of exact capability/resource coordinates, pairwise dominance is decidable. Removing every dominated attainable point yields the exact operational Pareto frontier

\[
\mathcal F_{\mathfrak G}=\operatorname{Pareto}(\mathcal A_{\mathfrak G}).
\]

The accompanying microscope enumerates a two-bit finite world, all 16 deterministic policies and the exact frontier; the best achievable accuracy is `3/4`.

**Terminal:** `FINITE_OPERATIONAL_FRONTIER_EXACT = TRUE`.

## 4. FOC-3 — exact optimal-fiber theorem

Let `p` be any point on the exact frontier. The set

\[
\Phi(p)=\{M:(Q(M),\rho(M))=p\}
\]

is finite and exactly enumerable. Consequently GMI can return **all** operationally optimal morphologies at the declared resolution without pretending that one syntactic representative is privileged.

This closes the old false dilemma “unique architecture or incomplete theory.”

**Terminal:** `FINITE_OPERATIONAL_OPTIMAL_FIBER_EXACT = TRUE`.

## 5. FOC-4 — bounded developmental reachability theorem

Let a development/search process have finite state, a finite legal move set and a finite budget `B`. Its complete search/reachability tree is finite. Exhaustive traversal therefore decides exactly which operational machines/frontier points are reachable within `B`, together with minimum step/resource cost when edge costs are nonnegative exact rationals.

Thus

\[
\mathcal F^{reach}_{\mathfrak G,B}
=\mathcal F_{\mathfrak G}\cap Reach(B)
\]

is exactly computable.

**Terminal:** `FINITE_BUDGET_DEVELOPMENTAL_REACHABILITY_EXACT = TRUE`.

This is intentionally not a theorem about unrestricted unbounded architecture search.

## 6. FOC-5 — finite stochastic extension

If a finite stochastic policy/kernel family is explicitly registered, exact rational transition probabilities make protected expected capability/resource coordinates finite rational sums, so the same enumeration theorem applies.

For standard finite fully observed finite-horizon control with linear expected criteria, the stronger continuous-randomization closure is parent theory: occupancy-measure linear programming gives the exact optimum. GMI claims specialization and typing, not invention of that result.

**Terminal:** `FINITE_REGISTERED_STOCHASTIC_CONTROL_EXACT = TRUE`.

## 7. Completeness statement

> **GMI Finite Operational Completeness Theorem.** For any finite GMI operational problem with decidable legal-machine semantics, exact rational/provably-computable trace and resource quantities, and finite registered development budget, GMI can compute exactly: (i) the attainable capability/resource set, (ii) its Pareto frontier, (iii) every operational realization fiber on that frontier, and (iv) the frontier subset reachable by the declared bounded development process.

This is a full theorem, not a partial empirical result.

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
