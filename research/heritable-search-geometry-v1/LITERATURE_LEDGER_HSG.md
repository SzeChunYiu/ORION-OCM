# HSG Literature Ledger V1 (per rung)

Same rule as the HST ledger: every claimed lift states what the parent already owns.
Class: **OWNS** (parent theorem covers the lifted statement; HSG instantiates) ·
**ADAPTS** (HSG adds a named condition/specialization) · **RESIDUAL** (HSG-specific).
Citations marked ⚠ must be verified against primary sources by the citing lane before
any PARENT_SUFFICIENT verdict cites them (marker `PARENT_STATEMENT_UNVERIFIED_TEXT` in
the artifact otherwise).

| rung | parent | what it owns | class |
|---|---|---|---|
| R2 | Kolmogorov; first-order stochastic dominance (standard) | measures, expectation, stochastic orders | OWNS |
| R3 | Blackwell 1951/1953 | comparison of experiments; garbling ⇒ value order for every decision problem | OWNS |
| R3 | Dobrushin 1956 ⚠ | ergodic coefficient δ(K); contraction of Markov kernels in TV | OWNS |
| R4 | Kantorovich 1942; Villani (survey) | optimal transport cost W_d, duality | OWNS |
| R4 | Birkhoff 1957 ⚠ | Hilbert-metric contraction of positive maps | OWNS |
| R4 | Chentsov 1972 ⚠; Amari (survey) | information geometry of statistical families; Fisher uniqueness | OWNS |
| R4 | hypervolume indicator literature (EMO: Zitzler–Thiele 1999 ⚠) | archive quality monotonicity caveats | OWNS |
| R5 | Perron–Frobenius; Koopman 1931 ⚠ | spectral/transfer-operator view of iterated kernels | OWNS |
| R5 | ergodic theory (von Neumann, Birkhoff 1931) | time averages = space averages under ergodicity | OWNS |
| R5 | #145 transformation semigroups (project) | closure ⟨O⟩, generator structure, reach algebra | OWNS (project) |
| R5 | renewal-reward theorem (standard) ⚠ | amortized cost under random use processes | OWNS |
| R6 | Schmidhuber OOPS/PowerPlay | incremental reuse of solutions; solver/task co-development | OWNS |
| R6 | Schmidhuber Gödel Machines | conditional optimality of proved self-changes | OWNS |
| R6 | PAC-Bayes chain/sequential bounds (Dziugaite–Roy, etc.) ⚠ | data-dependent prior movement | OWNS (context) |
| R7 | Simon 1962 | near-decomposability of hierarchical systems | OWNS |
| R7 | open Markov processes (compositional Markov; Baez–Fong 2015 ⚠) | boundary fluxes, non-conservation | OWNS |
| R7 | Wolpert–Macready NFL + sharpenings (already in HST ledger) | averaging limits at every rung | OWNS |

**HSG residual (all this capsule may claim as its own):** the atom table itself (the
locating of every HST atom on the ladder), the survival/conditional/fail verdicts at OCM
scope, the minimal counterexample constructions, and the rung-indexed issue-hook bridge
into #145/#149/#151/#217/#221. Where a lift is PARENT_SUFFICIENT the artifact says so in
the first sentence — an HSG proof that silently re-proves Dobrushin is a defect, not a
result.
