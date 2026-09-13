# Deferred predictions: executed, all three held

Status: **PREREGISTERED THEN CONFIRMED; 3 OF 3 HELD**
Date: 2026-09-14

`DEFERRED_PREDICTIONS_V1` registered three predictions and deliberately did not
evaluate them. It merged to `main` in that state. This unit executes them.

## 1. The registration was genuinely unevaluated

Before execution, on merged `main`:

- `learning_law_selection_v1.py` — **0** mentions of the deferred ecologies;
- `test_ecology_prediction_v1.py` — **0**;
- only the deferral test named them, to assert disjointness.

No price table for `D1_MEMORY_BOUND`, `D2_ORACLE_CHEAP` or
`D3_ENUMERATION_TAXED` existed anywhere in the sector, so no checker could have
computed an answer and no edit could have backfilled one without changing the
frozen text.

Frozen digest: `38493781de864856409a607ff75afea80a3f51ad89d5c8b947a66d77a6f84787`.

## 2. The executor reads the registration, not the author

`execute_deferred_v1.py` **parses** the merged document for both the ecology
price tables and the prediction rows. Nothing is hardcoded. An unrecognised
capability word or price clause raises rather than defaulting.

## 3. Outcome

| tag | ecology | predicted | observed | terminal | charged costs |
|---|---|---|---|---|---|
| `D-P1` | `D1_MEMORY_BOUND` | `MIRROR_DESCENT` | `MIRROR_DESCENT` | `SELECTED` | gradient step 12, mirror 3 |
| `D-P2` | `D2_ORACLE_CHEAP` | `BAYES_UPDATE` | `BAYES_UPDATE` | `SELECTED` | bayes 8/7, mirror 4 |
| `D-P3` | `D3_ENUMERATION_TAXED` | `ORDINAL_HILL_CLIMB` | `ORDINAL_HILL_CLIMB` | `SELECTED` | exact search 97, hill climb 2 |

Terminal: `ALL_DEFERRED_PREDICTIONS_HELD`, 3 of 3.

Each prediction had three registered ways to fail — a different law, an
`UNDETERMINED_TIE`, or `INFEASIBLE_AT_CONTRACT`. None occurred.

## 4. A parser defect found and fixed during execution

The first executor scoped its ecology pattern to the whole document. Because a
prediction row also contains a backticked ecology id, the pattern read that
row's law cell as a price clause and raised. Both parsers are now scoped to
their own section. This is the same over-matching error as a substring
classifier: a pattern that matches more than the thing intended.

It is recorded because it happened during execution, not before it.

## 5. What this does and does not establish

Established: the ecology-conditioned selection law made three predictions that
were frozen on `main`, unevaluated, and all three held when executed against
the frozen text.

Not established: anything about physical machines, runtimes, or learning
systems outside this exact finite model. The parity V5/V6 workflow executes on
recorded hosts and interpreters; this does not, and does not claim that status.
The predictions are consequences of a registered charge table, so holding
confirms the table's consequences were correctly derived — not that the table
describes any real cost.
