# Ecology-conditioned learning-law predictions

Status: **ANALYTIC PREDICTIONS + INDEPENDENT RECOMPUTATION; NOT A TEMPORAL PREREGISTRATION**
Date: 2026-09-13

Ledger item 8 asks for predictions of the form "under ecology `E1`, A should win;
under `E2`, B should win". LLS-3 makes those derivable. Each prediction below is
derived by hand from the charge table, then recomputed by an independent
exhaustive minimiser that does not read this document.

**Honesty of status.** Prediction and verification land in the same commit, so
this is an *independent recomputation*, not a claim of temporal priority. The
repository's temporal-preregistration machinery is the parity V5/V6 workflow;
this unit does not borrow its status.

## Registered ecologies

| id | ecology | prices that differ from unit |
|---|---|---|
| `E1_SAMPLE_SCARCE` | evidence is expensive to obtain, arithmetic is cheap | likelihood eval 5, gradient eval 1 |
| `E2_MODEL_KNOWN` | a correct likelihood is supplied, gradients cost more | likelihood eval 1, gradient eval 5 |
| `E3_ENUMERABLE` | the program space is small and fully enumerable | enumeration 1/2 |
| `E4_COMPARISON_ONLY` | only ordinal feedback is available cheaply | comparison 1/2 |
| `E5_PROJECTION_CHEAP` | a Euclidean projection is cheap | projection 1/3 |
| `E6_NORMALISATION_CHEAP` | simplex normalisation is cheap | normalisation 1/3 |

## Predictions, derived before recomputation

| # | capabilities | ecology | predicted law | why |
|---|---|---|---|---|
| P1 | differentiable, simplex, likelihood, finite hypotheses | `E1_SAMPLE_SCARCE` | `MIRROR_DESCENT` | both admissible; gradient eval is cheaper than likelihood eval |
| P2 | same as P1 | `E2_MODEL_KNOWN` | `BAYES_UPDATE` | the same capabilities, reversed prices |
| P3 | discrete programs, ordinal comparison | `E3_ENUMERABLE` | `EXACT_SEARCH` | enumeration undercuts comparison |
| P4 | same as P3 | `E4_COMPARISON_ONLY` | `ORDINAL_HILL_CLIMB` | comparison undercuts enumeration |
| P5 | differentiable, Euclidean, simplex | `E5_PROJECTION_CHEAP` | `GRADIENT_STEP` | projection undercuts normalisation |
| P6 | same as P5 | `E6_NORMALISATION_CHEAP` | `MIRROR_DESCENT` | normalisation undercuts projection |

P1 and P2 are the pair the ledger item names directly: the same machine, the
same capabilities, and a different ecology selects Bayesian updating rather than
gradient-style learning.

## Falsifiers

Each prediction fails if the independent minimiser returns a different law, if
the two ecologies in a pair return the same law, or if any named capability set
turns out to admit a law not listed. A prediction whose pair does not separate
is recorded as failed rather than reinterpreted.
