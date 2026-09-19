# Parent ownership — gmi-833-ae-ae5-causal-state-audit-v1

This package is an **audit**, so parent ownership is the point of it, not a
preliminary. `PARENT_SUFFICIENT` is recorded as a success terminal.

## Literature parents

- **Causal states and the ε-machine.** Crutchfield & Young 1989,
  doi:10.1103/PhysRevLett.63.105. Causal states, statistical complexity
  `C_μ = H[S]`.
- **Minimality and sufficiency.** Shalizi & Crutchfield 2001,
  doi:10.1023/A:1010388907793. Theorem 1 (causal states are the minimal
  sufficient statistic of the past for the future) and Theorem 3 (the ε-machine
  is minimal among prescient rivals). **Everything GMI says about minimal
  predictive states at this scope is an instance of these.**
- **Predictive information / excess entropy.** Bialek, Nemenman & Tishby 2001,
  doi:10.1162/089976601753195969; Crutchfield & Feldman 2003,
  doi:10.1063/1.1530990, which owns `E ≤ C_μ` and the crypticity
  `χ = C_μ − E`.
- **Observable operator models and the Hankel rank.** Jaeger 2000,
  doi:10.1162/089976600300015411; Hsu, Kakade & Zhang 2012,
  doi:10.1016/j.jcss.2011.12.025; the Carlyle–Paz / Fliess theorem that the
  Hankel rank is the minimal linear-automaton dimension. The rank ≤ state-count
  bound is theirs.
- **Computational mechanics reviews.** Crutchfield 2012,
  doi:10.1038/nphys2190.

## Repository parents (pinned by blob sha at `source_main`)

| parent | what it owns | pin |
|---|---|---|
| `gmi-833-theory-baseline-v1` | the section's baseline vocabulary | `201ee8e8…` |
| `gmi-833-foundation-v1` | the #833 formalization scope | `c0c574c4…` |
| `gmi-833-ae-ae1-structure-separation-v1` | task-relative exploitable structure | `ceb77f5b…` |
| `gmi-833-ae-ae2-predictive-boundary-v1` | the predictive-information learnability boundary | `cd1e1d5f…` |
| `gmi-833-ae-ae10-usable-information-v1` | budgeted usable information | `69aafebe…` |

## What is NOT claimed novel

The causal-state construction, its minimality, statistical complexity, excess
entropy, the `E ≤ C_μ` bound, crypticity, and the Hankel-rank theory. The audit
returns `PARENT_SUFFICIENT` on four of five statements and records
`novelty_claimed_for_gmi_state_complexity: false` in the machine-readable
receipt.

## The residual contribution

Two narrow things:

1. the **horizon-indexed refinement sequence** of GMI predictive equivalence,
   with its exact stabilisation horizon and a counterexample proving that the
   identification with causal states must carry its horizon — computational
   mechanics works at the semi-infinite future and does not index by horizon;
2. the **exactly-dyadic process family** that makes `C_μ` and `E` exact
   rationals with no logarithm evaluated, which is what lets the bound and the
   crypticity be *verified* rather than cited.

The resource-priced model selection of a predictor — the other thing computational
mechanics does not do — is exercised by `gmi-833-ae-morphology-sweep-v1` in this
same tranche, and AE5's fifth row is closed there, not here.
