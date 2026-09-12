# GMI Finite Portfolio Selection Bound v1

Status: **FORMAL REAL-TRANSFER SELECTION BOUND / R8**

Date: 2026-09-12.

The V1 real pilot deliberately used an exact retrospective sample-best endpoint and went RED on all four datasets. That failure is preserved. This theorem defines the statistically correct successor target without touching that protected split.

Let `M` candidate development procedures be frozen before validation. Candidate `i` has true bounded loss
\[
R_i\in[0,1],
\]
validation empirical loss `Rhat_i`, and a resource penalty `p_i` computed without validation labels.

Define
\[
J_i=R_i+p_i,\qquad \hat J_i=\hat R_i+p_i.
\]

Select
\[
\hat i\in\arg\min_i\hat J_i.
\]

## FP-1 — finite-portfolio true-objective regret

By Hoeffding plus a union bound, with probability at least `1-delta`,
\[
\max_i|\hat R_i-R_i|
\le
\epsilon_v
=
\sqrt{\frac{\log(2M/\delta)}{2n_v}}.
\]

On this event,
\[
\boxed{
J_{\hat i}-\min_iJ_i
\le 2\epsilon_v.
}
\]

Proof:
\[
J_{\hat i}\le\hat J_{\hat i}+\epsilon_v
\le\hat J_{i^*}+\epsilon_v
\le J_{i^*}+2\epsilon_v.
\]

## FP-2 — observable fresh-test diagnostic

Let a fresh untouched test sample of size `n_t` estimate each candidate's risk with simultaneous radius
\[
\epsilon_t=
\sqrt{\frac{\log(2M/\delta_t)}{2n_t}}.
\]

If the validation event and test event both hold, the observed test-objective regret of the validation-selected candidate relative to the retrospective test-best candidate is at most
\[
\boxed{
2\epsilon_v+2\epsilon_t.
}
\]

This is conservative but prospectively testable.

## Consequence

Exact equality to the sample-best test model is **not** a valid universal success requirement for finite held-out samples. The right target is a frozen regret/confidence statement.

Resource penalties are permitted only when they are determined without validation/test labels and are charged equally in selection and evaluation.

## Claim ceiling

This theorem does not show that a GMI-derived selector is scientifically superior. It provides a valid finite-sample gate for a frozen candidate portfolio.
