# Deferred predictions — frozen now, executed later

Status: **PREREGISTERED, DELIBERATELY NOT EVALUATED IN THIS COMMIT**
Date: 2026-09-13

`ECOLOGY_PREDICTION_V1.md` is an *independent recomputation*: its predictions
and their verification land together, so it carries no temporal priority. That
is a real weakness of that unit and this file is the repair.

The predictions below are stated now. **No checker in this commit computes
their winners.** The accompanying test asserts the deferral: it verifies that
the deferred contracts are disjoint from every contract the suite evaluates,
and that this table's digest is the frozen one. Execution happens in a later
commit, against this frozen text.

## Frozen ecologies

| id | prices that differ from unit |
|---|---|
| `D1_MEMORY_BOUND` | normalization 2, projection 11 |
| `D2_ORACLE_CHEAP` | likelihood eval 1/7, gradient eval 3 |
| `D3_ENUMERATION_TAXED` | enumeration 97, comparison 2 |

## Predictions not evaluated here

| # | capabilities | ecology | predicted law |
|---|---|---|---|
| D-P1 | differentiable, Euclidean, simplex | `D1_MEMORY_BOUND` | `MIRROR_DESCENT` |
| D-P2 | differentiable, simplex, likelihood, finite hypotheses | `D2_ORACLE_CHEAP` | `BAYES_UPDATE` |
| D-P3 | discrete programs, ordinal comparison | `D3_ENUMERATION_TAXED` | `ORDINAL_HILL_CLIMB` |

## What would falsify each

A prediction fails if the later execution returns a different law, returns
`UNDETERMINED_TIE`, or returns `INFEASIBLE_AT_CONTRACT`. A failed prediction is
recorded as failed; the table is not edited after execution, and a changed
prediction starts a new version rather than continuing this one.

## What this does not claim

It does not claim the parity V5/V6 workflow's status: that machinery executes on
recorded hosts and interpreters. This is a frozen analytic prediction over an
exact finite model, and its only prospective content is that the answer is not
computed here.
