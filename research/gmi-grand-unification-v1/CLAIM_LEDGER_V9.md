# Grand GMI Claim Ledger V9 — measurable / continuous process scope

Status date: 2026-09-12. Additive to V1–V8.

| ID | Claim | Status | Scope |
|---|---|---|---|
| GG47 | Grand GMI extends to standard-Borel stochastic process models under declared measurable kernels, policies, interventions and probes without changing its semantic definitions. | THEOREM / INSTANTIATION | standard-Borel Markov process scope |
| GG48 | Exact response equivalence remains a well-defined semantic quotient on infinite history spaces, but convenient measurable/standard-Borel structure of the quotient must be proved rather than assumed. | THEOREM / REGULARITY BOUNDARY | infinite exact semantic state |
| GG49 | Every nonempty compact finite-dimensional attainable profile set contains a Pareto point; any minimizer of a strictly positive weighted sum is nondominated. | THEOREM | compact `Y subset R^d` |
| GG50 | Infimum does not imply an attaining morphology; a noncompact attainable set can have an empty Pareto frontier. | COUNTEREXAMPLE / THEOREM BOUNDARY | noncompact profile image |
| GG51 | `kappa` and `tau` are infima by default; replacing them by minima requires a separate attainment theorem. | NORMATIVE THEOREM | general process/resource classes |
| GG52 | If the response metric space is totally bounded, every nonzero tolerance admits a finite semantic cover; compact metric semantic spaces are therefore finite-complexity at finite resolution. | THEOREM | declared response metric |

## Exact hostile evidence

- all 255 nonempty subsets of `{0,1}^3`: every minimizer under weights `(1,2,4)` is Pareto-nondominated.
- sequence `{1/n}`: 256 exact successor-dominance checks; every sampled point has a strictly better successor and the infinite family has infimum `0` not attained.
- adding `0` restores a unique Pareto point in every checked compactified prefix.
- exact grid covering numbers decrease or stay fixed as response tolerance grows; examples `[5,2,1,1]`, `[9,3,2,2]`, `[13,5,3,2]`.

Aggregate terminal:

`GRAND_GMI_MEASURABLE_CONTINUOUS_TRANCHE_ALL_GREEN`.

## Boundary

This tranche does not assert automatic measurable quotient structure, optimizer existence, frontier stability under discretization, or effective computability for arbitrary infinite systems. Stochastic-control and topological existence theorems are parent regularity results imported when their hypotheses hold.