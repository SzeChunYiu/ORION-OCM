# Grand GMI Robust Decision Precision Claims V1

Status date: 2026-09-13. Uses `RDP-*` identifiers independently of the moving master `GG*` ledger.

| ID | Claim | Status | Scope |
|---|---|---|---|
| RDP-1 | A finite robust action score is 1-Lipschitz under coordinatewise finite uniform loss error `delta`; infinite-score actions admit order inequalities only. | THEOREM | nonempty ecology, finite scores for absolute differences |
| RDP-2 | An estimated minimizer has true regret at most `2 delta`; certified selection slack `alpha` adds `alpha` to the bound. | THEOREM + 2,985,984 EXACT CASES | nonempty finite actions, finite precision, at least one finite score |
| RDP-3 | A unique finite robust optimum with margin `Delta > 2 delta` is preserved by exact estimated minimization; singleton actions use `Delta=+infinity`. | THEOREM + 107,163 EXACT APPLICABLE CASES | finite uniform precision; add selector slack for approximate minimization |
| RDP-4 | The factor `2` is sharp without additional structure: below the boundary the wrong action can win; at equality a tie can be forced. | THEOREM + EXACT WITNESSES | sup-norm error model |
| RDP-5 | Finite regret tolerance `epsilon` is guaranteed by `2 delta<=epsilon` for exact estimated minimization, or `2 delta+alpha<=epsilon` with certified selection slack. | COROLLARY | finite nonnegative precision/tolerance and finite optimum |
| RDP-6 | Precision and selection-error bounds provide sufficient admissibility gates before resource Pareto selection; outside this gate, direct adequacy evidence may still suffice. | DERIVED MORPHOLOGY LAW | valid profiles and certified selection accuracy |

Aggregate terminal: `GRAND_GMI_ROBUST_DECISION_PRECISION_TRANCHE_ALL_GREEN`.

Additive domain/boundary terminal: `GRAND_GMI_DECISION_FINITE_SCORES_TRANCHE_ALL_GREEN`. The additive checks do not certify arbitrary infinite ecologies from finite samples.

No universal sample count, precision technology, metric or stochastic estimator is claimed. Those come from the declared observation/substrate model used to certify `delta`.
