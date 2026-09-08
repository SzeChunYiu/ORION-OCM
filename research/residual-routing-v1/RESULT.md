# RESIDUAL_ROUTING_OPPORTUNITY_V1 — result

**Terminal: `EXACT_POLICY_SUFFICIENT`.** #71 stays blocked at
`LEARNED_ROUTER_NOT_YET_AUTHORIZED`.

- Issue: [#152](https://github.com/SzeChunYiu/ORION-OCM/issues/152)
- Commit: `47d706ab42d8528060356c7d4a267e1454ce9e7a`
- Protocol commitment: `2e1fcf1e94fceac847e62af63db52a543f11d98105f6f7d5d17532a734ab9706`
- Receipts: `results/RRO_RAW_V1.json` (raw), `results/RESIDUAL_ROUTING_OPPORTUNITY_V1.json` (derived)
- No ML, NN, bandit or router was implemented, proposed as code, or run.

## Population

Every `compose_stage` invocation reached by the repository's own test suite at the
frozen commit: **96 selection points across 70 independent test sources**. The
suite was run once without the instrument and once with it, with identical
outcomes (1301 passed, 2 skipped, 6 pre-existing `test_distribution.py`
collection errors), so the instrument perturbed nothing.

| quantity | value |
|---|---|
| selection points | 96 |
| `\|A^E\| = 0` | 38 |
| `\|A^E\| = 1` | 36 |
| `\|A^E\| > 1` | **22 (22.9%)** |
| queries producing an answer | 44 |
| of those, first passing candidate at index 0 | **44 (all)** |
| queries with 2 passing candidates | 20 |
| `rho_R` | **0.0** |

## Two findings, with different scopes

**1. Order-invariance — independent of any workload.**
`compose_stage` and `check_stage` have no early exit at this commit; only
`decide` selects, and it returns `passed[0]`. Incumbent work is therefore a sum
over the admissible set with order-independent summands, so **Δ(q) under any pure
reordering is identically zero for every query the runtime can be given**. A
router that only reorders cannot save work at any rate on any ecology; with
positive inference cost it strictly increases work on every query. A test checks
this against `solve.py` rather than trusting the prose.

**2. Zero routing residual — dependent on this population.**
On all 44 answering queries the first admissible candidate is the one that
passes, so no work is spent before the answer. All **40 recoverable verification
calls** lie *after* it and are taken by stopping at the first pass — an exact
policy that preserves decision, answer and chosen operator under contract C1 and
needs no learner. Plausibly an artifact of fixtures supplying the intended
operator first; a real ecology could place the passing candidate later.

**Why the terminal survives that caveat.** Even then, recovering pre-answer work
requires stopping early, and the runtime does not. Reordering alone still saves
nothing. A router remains unable to help until an exact early-exit policy exists —
at which point the exact policy has already taken the *after* work, and the
residual must be re-measured on the real ecology.

## Counterfactual identifiability

Route 3 of #152, an **exact finite reference**, at zero extra cost: because the
incumbent composes and checks *every* admissible candidate, every alternative's
outcome is a recorded fact of the incumbent run. No shadow execution, no
propensities, no off-policy estimator, no untried action inferred. 94 of 96
records are fully identified; the 2 that are not come from a test calling
`compose_stage` without `check_stage`, are named in the receipt, and contribute
zero to every Δ.

The same exhaustiveness is why the routing opportunity is empty. Identification
is free and routing is impossible for one reason.

## Selection-policy contracts

Three registered, differing only in what they protect. `C1_ANSWER_EQUIVALENCE`
permits early exit and forbids reordering. `C2_TRACE_EQUIVALENCE` permits
nothing. `C3` permits reordering only where at most one candidate passes. On this
population the 22 multi-candidate queries with an answer all have **two** passing
candidates, so reordering there would change which operator `decide` returns —
outside every contract, a violation rather than an opportunity.

## Unlock conditions (#152)

| # | condition | met |
|---|---|---|
| 1 | material fraction with `\|A^E\|>1` | yes (22.9%) |
| 2 | alternative value independently identifiable | yes |
| 3 | candidates not merely incomparable | **no** — 20/20 multi-candidate answers have 2 passes |
| 4 | repeated demand | not established |
| 5 | material savings at matched capability | **no** — routing-specific Δ = 0 |
| 6 | positive lifetime denominator | **no** — budget 0/query |
| 7 | exact/guarded/`p/c` policies do not explain it | **no** — an exact policy explains all of it |

Four conditions fail. **#71 stays blocked.**

## Preserved

Supplied-key sparse lookup is not cognition; exact indexing wins are not a neural
opportunity; guarded-rule wins are not evidence for routing; method discovery is
not sufficient for useful reuse; parent-sufficient lanes are not failed science.
