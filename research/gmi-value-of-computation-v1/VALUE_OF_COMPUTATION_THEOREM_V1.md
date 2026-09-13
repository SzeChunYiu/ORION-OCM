# Value of computation and exact stopping — VOC-1–6

Status: **THEOREM AT DECLARED FINITE SCOPE + EXACT RATIONAL WITNESSES**
Date: 2026-09-13

Ledger item 10. Closes the three gaps left open by
[`metareasoning-parent-review-v1`](../metareasoning-parent-review-v1/CORE.md),
which recorded them as "open implementation/review tasks, not completed fixes":
a termination-assumption gap (T1), an exactness-certification gap (T2) and
contradictory stopping guidance (T3).

The mechanisms are inherited, not claimed novel.

| Donor | What is inherited | What is *not* inherited |
|---|---|---|
| Hay, Russell, Tolpin, Shimony (2012) | metalevel decision process; explicit computation/stop alternatives; strictly positive computation cost | their Bayesian utility model; Theorem 5 bounds *expected* computation count, not a per-path bound |
| Bertsekas (2017, 2020 rev.) | properness = finite total cost **and** finite steps to termination; under nonnegative costs, optimal-over-all-policies and Bellman fixed points need not coincide | Proposition 7's conditions (eq. 16 / finite `W`); no OCM transfer theorem follows |
| Russell, Wefald (1991) | computation valued through its effect on external action | myopic single-step valuation as a decision rule |
| Lotker, Patt-Shamir, Rawitz (2008/2010) | unknown-horizon investment framing | competitive guarantees; the reduction must be qualified, never imported by analogy |

## 1. Register

A finite metalevel register is `(Sigma, h, k)`: deliberation state `Sigma`,
demand horizon `h`, cognitive allowance `k`. Two action kinds are admitted:

- **certified actions** `a in A(Sigma)` with rational cost `c(a) >= 0`, which
  terminate the episode;
- **cognitive actions** `g in G(Sigma)` with rational charge `e(g) >= 0`, which
  move to `Sigma'` and terminate nothing.

`min(empty) = +infinity`. Every charge is booked to the resource ledger `R`;
A4 forbids an uncharged cognitive step.

## 2. VOC-1 — the bare recurrence does not define a stopping value

> **VOC-1.** There is a register in which the unaugmented recurrence
> `J(Sigma) = min( min_a c(a), min_g [ e(g) + J(Sigma') ] )`
> has a continuum of solutions, so it determines neither the value nor whether
> the selected policy ever acts.

Proof. Take one state with a certified action of cost `1` and one cognitive
action of charge `0` returning to the same state. The recurrence reduces to
`J = min(1, J)`, satisfied by **every** `J in [0,1]`. If eventual action is
required the intended value is `1`; if an unbounded zero-charge cognitive loop
is admitted as a policy, the machine never serves the demand. QED.

This is the T1 defect, stated as a theorem rather than a review note. Bertsekas
is the parent: under nonnegative costs a Bellman equality alone does not supply
properness.

## 3. VOC-2 — a well-founded rank restores uniqueness

> **VOC-2.** Require every cognitive transition to strictly decrease `k`, and
> let `G(Sigma, 0) = empty`. Then `J` is unique, is computed by backward
> induction on `k`, and every optimal policy terminates within `k` cognitive
> steps.

Proof. Induct on `k`. At `k = 0` no cognitive action is admitted, so
`J(Sigma, h, 0) = min_a c(a)`, a minimum over a finite set, `+infinity` if
empty. For `k > 0`, every cognitive successor is evaluated at `k - 1`, already
unique by hypothesis, so the right-hand side is a finite minimum of determined
quantities. Well-foundedness of `k` forbids the VOC-1 loop. QED.

## 4. VOC-3 — a strictly positive charge gives properness without a rank bound

> **VOC-3.** If every cognitive charge satisfies `e(g) >= epsilon > 0` and some
> certified action has cost `C < infinity`, then no optimal policy takes more
> than `floor(C / epsilon)` cognitive steps, and `J` is the unique bounded
> solution.

Proof. A policy taking `m` cognitive steps pays at least `m * epsilon`. If
`m > C / epsilon` its cost exceeds `C`, which is attainable immediately, so it
is not optimal. The optimal policy therefore lies in a finite-depth class, on
which VOC-2's induction applies. QED.

This is the deterministic-cost analogue of Hay et al.'s Theorem 5 shape
(computation count bounded by value over cost). Theirs bounds an *expectation*;
this bounds every admitted path, because the charges here are deterministic.

**The stopping rule is now derived, not assumed.** Continue deliberating from
`Sigma` iff some `g` satisfies `e(g) + J(Sigma') < min_a c(a)`; equivalently iff
the value of computation `min_a c(a) - J(Sigma')` strictly exceeds its charge
`e(g)`.

## 5. VOC-4 — myopic value of computation is not a valid stopping rule

> **VOC-4.** There is a register where every single cognitive step has
> non-positive value of computation, yet a two-step deliberation strictly
> improves the achievable cost.

Witness in §7. Single-step lookahead stops and pays `10`; the optimal policy
pays `3`. Russell and Wefald's framing of computation value is inherited; the
myopic *rule* is refused.

## 6. VOC-5 — a common safe action does not license economic stopping

> **VOC-5.** Existence of an action that is adequate for every surviving model
> makes full identification unnecessary for *safety*, and does not imply that
> stopping is *economically* optimal.

Witness in §7: the common safe action costs `10`; a cost-`1` probe distinguishes
the models and unlocks a model-specific action costing `1`, total `2`. Stopping
must be decided by the charged comparison of VOC-3, whether or not a common safe
action exists. This is the T3 repair.

## 7. Exact witnesses

**W1 (VOC-1).** `c = 1`, cognitive charge `0` to the same state. Fixed-point set
is the whole interval `[0, 1]`; the recurrence is satisfied by `0` and by `1`.

**W2 (VOC-4, myopia).** Certified action available now costs `10`. Two probes
each charge `1`. Either probe alone leaves the best certified cost at `10`, so
each single-step value of computation is `10 - 10 = 0`, never exceeding its
charge `1`. Both probes together unlock a certified action of cost `1`. Myopic
rule: stop, pay `10`. Optimal: `1 + 1 + 1 = 3`.

**W3 (VOC-5, T3).** Two surviving models; common safe action costs `10`; probe
costs `1`; model-specific protected action costs `1`. Immediate action `10`;
probe-then-act `2`.

**W4 (VOC-6, T2).** Two states in one bucket with action pairs
`(1, 1 + 2^-42)` and `(1 + 2^-42, 1)`. Both values are exactly representable in
binary floating point. The exact argmin sets are opposite singletons, so the
true collision count is `2`; `math.isclose(rel_tol=1e-12)` reports "tie" for
both and records `0`.

## 8. VOC-6 — exactness is a precondition, not a presentation detail

> **VOC-6.** A tolerance-based tie test does not compute an exact argmin. An
> instrument that labels tolerance ties as exact optimum sets can report a
> collision count that differs from the exact one, as W4 exhibits.

Repair, inherited from the review's own prescription: certify action-gap signs
with exact scaled integers or rationals, or publish outward error intervals and
label any unresolved action `NUMERICALLY_UNRESOLVED`. Retain raw signed
residuals before any display clamp. An epsilon-optimal set is legitimate only if
the protocol, the lemma application and every output name use that relaxed
meaning.

## 9. Failure taxonomy

| Failure | Symptom | Repair |
|---|---|---|
| unbounded cognition | zero-charge cognitive cycle; continuum of fixed points | well-founded rank (VOC-2) or positive charge (VOC-3) |
| myopic stopping | single-step VOC non-positive while multi-step improves | lookahead to the admitted allowance |
| safety/economics conflation | stop because a common safe action exists | charged comparison of VOC-3 |
| false exactness | tolerance ties reported as exact optima | exact rationals or explicit refusal (VOC-6) |
| uncharged deliberation | cognition consumes an unpriced resource | book every charge to `R` per A4 |

## 10. Falsifiers and boundaries

VOC-1 is falsified by a proof that the bare recurrence has a unique solution on
the W1 register. VOC-2 is falsified by an optimal policy exceeding `k` cognitive
steps under a strictly decreasing rank. VOC-3 is falsified by an optimal policy
taking more than `floor(C / epsilon)` cognitive steps under its premises. VOC-4
and VOC-5 are falsified by recomputing their registers and obtaining the myopic
or stop-immediately value as optimal.

This unit does **not** establish: stochastic or Bayesian metalevel optimality,
a competitive guarantee under unknown horizon, a bound over arbitrary programming
languages or physical machines, the correctness of any particular frozen
population label, or that any existing collision count in the reviewed source is
numerically wrong. No such computation was performed here.
