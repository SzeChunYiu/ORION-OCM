# Matched parent comparison plan

No parent trajectory was executed in this lane. Missing comparisons stay
`NOT_RUN`, not weak stand-ins.

Each parent must receive the same development information, candidate library,
checker/probe access, adaptation permissions, budget and stopping rules as OCM.

## Required parents (issue #149 / G6.1 / P4)

| Parent | Role | Status |
|---|---|---|
| Finite catalogue identity / ordered search | Same 10 C1 alternatives and 8-probe budget | Recorded on `d793f3f` as `AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION`; **not rerun here** |
| Random search | Matched library, same stopping | NOT_RUN |
| Bayesian optimization / AutoML | Configuration search over the same edits | NOT_RUN |
| Evolutionary search | Population over C0–C5 write set | NOT_RUN |
| Program repair | Generate patches from traces, not catalogue lookup | NOT_RUN — blocked until F1/F5/F6 traces exist |
| System identification | Fit intervention→effect map; predict held-out incidents | NOT_RUN — missing disjoint unlabeled transcripts |
| Structured surrogate | Low-order effect model / ANOVA-style factorization | NOT_RUN |
| ATMS / change-impact | `ocm.kso.revocation.impact_cone` is the in-repo parent for locality | Mechanism exists; **not** run as a self-evolution selector |
| Learned selector / meta-learning | Predict useful candidate from unlabeled history | NOT_RUN |
| Reflection / retry | M11 `reflection-retry` parent on planted S0–S7 only | NOT a real-incident parent |
| Human / Claude-designed repair | Explicit origin `HUMAN`; polynomial semantic-reuse is already tagged human-supplied | NOT_RUN as a matched G6 arm |

Neural continual-adaptation trajectories remain out of this tranche (#149).

## Entry conditions before any parent run

1. Recover original F1/F5/F6 traces; keep F2 and F3 as one observation until
   independent receipts exist.
2. Freeze an unlabeled proposer channel (numeric allowlist only).
3. Register probe language and cost vector before seeing outcomes.
4. Hold out at least one disjoint incident family for effect prediction.
5. Charge rejected probes, shadows, adoption and rollback.

Until those exist, claiming a parent residual is `CANNOT_CHECK`.
