# FNA-5 / D7 protocol — non-neural routing first refusal (frozen before execution)

**Issue #214 work package FNA-5, deliverable FNA-D7, aligned with #71. Base commit
`b801a0324e758b7e040d79e4beeaaab1c8aeb9be`. Research-only: production `src/` untouched, no
router deployed, #71 remains `LEARNED_ROUTER_NOT_YET_AUTHORIZED`, no #165 box touched.**

## What this study is and is not

#71 asks whether a *residual* routing opportunity exists on the incumbent runtime under its
registered ecology (`RESIDUAL_ROUTING_OPPORTUNITY_V1`). That is #71's own unlock study and
this capsule does **not** perform it. What FNA-5 needs — and what #214 §4 FNA-5 registers —
is the *selector-class ladder itself*: if a routing residual is ever conceded, which
smallest non-neural selector class would own it? This study freezes a routing **task world**
and runs the ladder on it, so the answer is a measured parent-ownership claim, not an
architecture preference.

Evidence class: one authored task world, one population, one author — E1/L1, like FNA-1.
Not E3. Nothing here licenses deployment; a deployed router still needs #71's unlock gate.

## Task world (hooked into the existing matched world, extended additively)

`research/operator_selection_scaling.py` times *exact structural selection* (scan vs
`SolveOperatorIndex`) on catalogues where exactly one operator is ever applicable. It cannot
express a routing decision: no query ever has a choice to make. So the world is extended
**additively in this capsule** (no shared file edited): same `OperatorSpec` catalogue
objects, same `SolveOperatorIndex.select()` query surface, but a catalogue in which several
*method families* compete for the same obligation and differ in execution cost and checker
outcome. This is the smallest honest extension that makes "which applicable operator should
run?" a question at all.

- Obligation per query: aggregate the active atoms' weighted mass (two task types, AGG /
  THRESH, differing cost constants). Backends do real bounded loops over their slice; work
  is counted loop iterations, exactly (the repo's own convention: logical work counters).
- Families: `scan` (exact, always applicable via empty input set — the same always-candidate
  pattern the scaling study's `global_hostile` uses), `probe` (exact indexed), `window` /
  `deepwindow` / `sample` (approximate; PASS iff a declared success law over legal query
  features holds). Realized success-law parameters are seeded draws around *declared design
  centres*; per-query latent noise `u(q)` softens boundaries (Bayes-irreducible band).
- The checker is exact with an O(1) certificate (declared simplification: failures are
  always caught, never delivered). A failed attempt is charged, then the runtime falls back
  to `scan` — the portfolio-recovery convention.
- All seeds derive from one frozen salt via sha256 chains; no set-iteration order anywhere
  (sorted iteration only), no `hash()` dependence, deterministic under seed.

## Legal feature surface (12 features, extraction charged)

log2|A|, dispersion, alias intensity, type entropy, n applicable (from index select work),
rarest-anchor postings, min applicable window W, mean atom weight, weight skew, near-dup
pair count, task-type flag, declared scan-cost estimate. Features see the query and the
*declared* catalogue constants only — never realized success outcomes. A structural test
pins that the extractor's inputs cannot carry labels.

## Arms, in first-refusal order

| arm | class | authority |
|---|---|---|
| BASELINE_INCUMBENT | first-PASS in supplied catalogue order (what `compose→check→decide` does: `passed[0]`), charged per attempt | clean baseline — the exact incumbent, never degraded |
| A0 ORACLE | evaluates all applicable, picks cheapest PASS | upper bound; labelled ORACLE, never a result |
| A1 ANALYTIC_GUARDED | guarded thresholds from **declared design centres** ± frozen safety margin 0.06; cheapest instance of the chosen family | derived from the frozen mechanism declaration; cannot know the seeded realization deltas — provably non-oracle (tested) |
| A2 COST_MODEL | Rice-1976 algorithm-selection parent: per-family ridge cost regression + binned success-rate estimates on dev; pick argmin predicted total cost incl. fallback expectation | conventional portfolio/cost-model parent |
| A3a KNN / A3b LOGISTIC | k=15 standardized kNN vote; multinomial logistic (12→5) | legal-surface learners |
| A4 TREE | CART, entropy, depth ≤ 3, min-leaf by 5-fold CV **on dev only** | rule learner, frozen depth |
| A5 BANDIT | LinUCB (disjoint, α=0.5) trained on the dev stream, then **frozen**; eval never feeds back | contextual bandit |
| A6 NEURAL_REF | tiny MLP 12→16→5, diagnostic only | **no adoption authority**; measures surviving representation gap only |

First refusal = the smallest arm among A1…A5 meeting the frozen sufficiency criterion.
Later arms still run and are reported, but only as gap measurement. A6 is never eligible.

## Splits, protected evaluation, drift

2400 seeded queries, assigned by `md5(salt::split::qid)` buckets: DEV 40% (all tuning,
CV, bandit stream), EVAL 40% (protected; no arm output feeds back into any fit), DRIFT_EVAL
20% (after a frozen catalogue mutation: one window instance removed, one sample instance
added, scan cost law bumped ×1.6, one regime parameter re-drawn). Maintenance is charged:
the shared index rebuild bills everyone; learned arms additionally pay label re-acquisition
over a 240-query maintenance window (executing all applicable per query — the real price of
retraining); A1 pays zero (re-derives from the declared spec).

## Measurements

Per arm on EVAL and DRIFT_EVAL: family/op selection agreement vs oracle, first-attempt pass
rate, fallback rate, execution+verification work, feature+inference overhead, build and
maintenance work amortized, persistent model bytes, wall/CPU seconds (descriptive).
Regret is defined **before outcomes** as per-query charged work (exec + verify + fallback +
features + inference) minus oracle's exec-only work; lifecycle amortization is added on top
as a separate line, never hidden.

## Frozen sufficiency and terminals

SUFFICIENT@scope iff on protected EVAL: mean total charged (incl. amortized lifecycle) ≤
(1+ε)·mean oracle exec work with **ε = 0.05**, and first-attempt pass rate ≥ 0.98.

- A1 sufficient → `PARENT_SUFFICIENT_FOR_ROUTING` (analytic/guarded rule).
- A2 sufficient → `PARENT_SUFFICIENT_FOR_ROUTING` (algorithm-selection cost model).
- only A3/A4/A5 sufficient → `NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE`.
- none sufficient but A6 sufficient → `REPRESENTATION_INSUFFICIENT`.
- none at all → `NO_FUNCTIONAL_PARITY_ROUTING`.
- machinery failure → `CANNOT_CHECK_<reason>`.
- sufficiency that appears only when lifecycle amortization is excluded additionally flags
  `ACQUISITION_COST_DOMINATES` (side-flag, reported alongside).

## Controls

- **Shuffle-equal-n null**: seeded permutation of dev feature→outcome rows (marginals kept,
  routing information destroyed), each learned arm retrained identically. Each arm retains
  its legal declared-cost prior (declared costs are public knowledge), so the null's floor is
  the cost-aware marginal policy, not the constant-modal one; the pinned test asserts (i) no
  arm's null massively exceeds its real run (no information injected by the null pipeline)
  and (ii) at least one learned arm beats its null (the surface carries real routing signal).
  The bandit's feedback is its own executions, so its null is a context shuffle (features
  permuted within applicability strata, rewards real).
- **Clean baseline**: every arm is compared against the incumbent first-PASS policy and the
  oracle — never against a degraded arm.
- **Prior-information accounting** (#214 §6): each arm reports the bytes of authored policy
  source (A1's rule text) and the bytes of its fitted model state, so a hand-authored rule
  cannot hide its prior.

## Declared limitations, before seeing outcomes

One authored world (E1/L1); the exact checker makes failures always-caught (worlds with
leaky checkers are harsher); boundary noise makes a measurable Bayes gap irreducible by
construction, so ε must absorb it; wall/CPU numbers are descriptive single-host; A6 is a
1-hidden-layer reference, not a frontier neural model — it bounds nothing about neural
capacity in general. The negative-results directive applies: a failing arm gets one-stage
failure attribution and a revive iteration in a *new* file (fna5b.py, own freeze addendum),
never a silent edit of frozen fna5*.py.
