# PR #150 measurement audit — protocol, frozen before outcomes

**E2 EXPLORATORY. This audit tests a measurement path, not a cognitive claim.**

Programme: #143. Constitution: #144. Theory under test: PR #150.
Source audited: `research/evolvability-theory-v0/synthetic_evolvability.py` at
`bb70e79050dea04bd0bff8f228fda1dc72dcd09f`, copied verbatim to `pr150_source.py`.

This file is committed **before** the audit is executed. Its predictions are checkable against the
git history; a prediction edited after an outcome is visible in the diff.

## Relationship to the independent codex session

That session (`research/independent-factorization-20260908`) found a scoring-soundness
counterexample in `discover_factorization` / `local_search`: on structured two-bit components a
context-dependent edge is missed, the search reports 0.825 while its final state truly evaluates to
0.325. It then stated plainly:

> The original continuously random NK sweep was NOT rerun and its published numbers are not
> declared corrupt.

That is the gap this audit closes. The counterexample shows the mechanism *can* misreport. It does
not establish whether PR #150's own published sweep *does*. Nothing here re-litigates their result.

## THEORY QUESTION

Is the quality PR #150 reports for its factorized arm an independent measurement of that arm's final
state, and is it measured the same way as the quality it reports for the comparator?

## The mechanism at issue

Two findings from reading the source, both structural rather than incidental:

1. **Measurement asymmetry.** `evolutionary_search` calls `land.fitness(y)`, a true oracle
   evaluation. `local_search` returns `sum(comps) / land.n`, where `comps` is a vector maintained
   incrementally from `inferred` edges and is never re-checked against the oracle. If `inferred` is
   incomplete, `comps` drifts from truth and the returned number is a self-report. The two arms of
   PR #150's headline comparison are therefore not scored by the same instrument.

2. **One-bit staleness check.** In the drift branch of `lifetime`, staleness is tested by perturbing
   **one** randomly chosen bit at **one** random context and comparing the observed component set to
   `inferred[bit]`. A drift-induced scope change affecting any of the other `n-1` bits is not
   detected, so `inferred` can remain stale for whole generations.

## PREDICTION (frozen)

- **P1.** With continuous random tables and `drift = 0.0`, `discover_factorization` recovers the
  true structure with probability approaching one, so reported quality equals true quality to within
  1e-9, and structure recall and precision are both 1.0.
- **P2.** With `drift > 0`, the one-bit check misses scope changes on other bits, so `inferred` goes
  stale in some generations. Reported quality will **exceed** true quality by a strictly positive
  mean margin, and that margin will be larger at `drift = 0.10` than at `drift = 0.03`.
- **P3.** If P2 holds, PR #150's reported factorized quality under drift is inflated, so its stated
  conclusion that drift erases the advantage is directionally correct but **understated**.
- **P4.** The comparator needs no correction because it is oracle-evaluated, so any inflation is
  one-sided and favours the factorized arm.

## STRONGEST PARENT

Not applicable in the usual sense: this audit compares a reported number to an exact oracle on the
same finite landscape. The oracle is `NK.fitness` from the audited source itself, so the comparison
uses PR #150's own definition of quality and imports no alternative standard.

## RED COUNTEREXAMPLE

Already supplied by the codex session at two bits with structured components. This audit asks
whether that counterexample bites on the continuous-random landscapes PR #150 actually swept.

## MECHANISM

A faithful re-implementation of `local_search` that additionally returns the final state `x`. It is
gated: on identical RNG streams and identical landscapes it must return a score and cost **bit
identical** to the original function, and a test asserts this. Only then is `NK.fitness(x)` computed
as the true quality.

## CAUSAL ABLATION

Compare, per generation and per regime: reported quality, true quality, structure recall, structure
precision, and whether the staleness check fired. The ablation of interest is stale versus fresh
`inferred`: generations where the check missed a scope change should carry the inflation.

## RESOURCE VECTOR

Full-evaluation-equivalent cost as PR #150 defines it, plus the oracle calls this audit adds, which
are charged to the audit and never to either arm.

## FALSIFIER

If reported quality equals true quality in **every** regime including drift, then the measurement
asymmetry is harmless in this harness, PR #150's published numbers stand as reported, and this audit
returns a defence of them rather than an attack. That outcome is registered as an acceptable and
publishable result.

## CLAIM CEILING

This audit can establish, at most, that a number in an exploratory synthetic harness is or is not an
independent measurement. It cannot establish anything about OCM, about factorization as a cognitive
strategy, or about PR #150's central hypothesis, which concerns a machine learning a factorization
of its own cognition and is untouched here. Every existing negative in the programme is preserved
unchanged.
