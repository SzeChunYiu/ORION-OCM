# FNA-5 / D7 results V1 — non-neural routing first refusal

Receipts: `FNA5_RESULTS_V1.json` (scored run, full config, deterministic under the frozen
salt) and `FNA5B_RESULTS_V1.json` (revival pass 1). Tests 16/16 green on the execution
host before the scored run. Evidence class E1/L1 (one authored world, one population,
one author). Research-only: nothing deployed, `src/` untouched, #71 stays
`LEARNED_ROUTER_NOT_YET_AUTHORIZED`.

## Headline

**Terminal: `NO_FUNCTIONAL_PARITY_ROUTING` (no arm sufficient). First-refusal arm: none.
Mechanism (revival pass 1, proven structural at this scope): `ACQUISITION_COST_DOMINATES`
— the minimum information price of safe routing exceeds the entire routing budget, and
the routing residual itself.**

Protected EVAL, 923 queries, oracle exec mean 58.36, budget (1+eps) 61.28:

| arm | fam agr | op agr | first-pass | fallback | exec | overhead | total |
|---|---|---|---|---|---|---|---|
| A0 ORACLE (labelled) | 1.000 | 1.000 | 1.000 | 0 | 58.4 | 0 | 58.4 |
| BASELINE_INCUMBENT | 0.219 | 0.219 | 1.000 | 0 | 96.1 | 0 | 96.1 |
| A1 ANALYTIC_GUARDED | 0.518 | 0.518 | 0.996 | 0.004 | 71.4 | 697.6 | 769.0 |
| A2 COST_MODEL | 0.668 | 0.622 | 0.899 | 0.101 | 72.6 | 1002.5 | 2594.1 |
| A3a KNN | 0.670 | 0.652 | 0.820 | 0.180 | 84.8 | 12260.7 | 12370.4 |
| A3b LOGISTIC | 0.680 | 0.661 | 0.887 | 0.113 | 79.3 | 824.4 | 15937.1 |
| A4 TREE | 0.735 | 0.722 | 0.926 | 0.074 | 71.0 | 704.0 | 6575.2 |
| A5 LINUCB | 0.637 | 0.628 | 0.933 | 0.067 | 76.6 | 1525.6 | 3776.3 |
| A6 NEURAL_REF (diagnostic) | 0.612 | 0.599 | 0.831 | 0.169 | 85.7 | 1238.0 | 103406.8 |

Sufficiency (frozen: total <= 1.05 x oracle exec AND first-pass >= 0.98): every arm fails
`cost_ok`; every learned arm also fails `pass_ok`. A1 passes the floor (0.996) and fails
cost.

## Null controls (all honest, signal present)

| arm | real fam agr | null fam agr |
|---|---|---|
| A2 | 0.668 | 0.205 |
| A3a | 0.670 | 0.512 |
| A3b | 0.680 | 0.560 |
| A4 | 0.735 | 0.520 |
| A5 | 0.637 | 0.180 |
| A6 | 0.612 | 0.372 |

Every learned arm beats its null; the legal surface carries real routing signal. The null
floor is the cost-aware marginal policy (arms retain declared costs — public knowledge),
not the constant-modal policy; formulation amended pre-outcome and pinned by
`test_null_control_is_honest`.

## Drift (frozen catalogue mutation; oracle 64.28)

Baseline 93.0 (fp 1.000); A1 drift 773.5 total but **fp 1.000, exec 72.2** — the declared
rule re-derives for free and never fails after drift; learned arms' refits are charged
(label re-acquisition at oracle identify cost, bandit at own online exec): A2 2105.2,
A4 3168.2, A5 2614.9 (A5 drift agreement collapses to 0.441 — the frozen bandit does not
transfer across the mutation).

## Negative-results directive: attribution -> lever -> re-test

Attribution (one stage): **information acquisition dominates.** The charged 12-feature
extraction costs ~697/query — 11x the entire 61.28 budget — before any operator runs; a
perfect router paying the full surface totals ~755. Secondary: declared-only routing's
exec penalty (71.4 vs oracle 58.4, agreement capped ~0.52 by declared-vs-realized law
offsets) alone also exceeds the budget; the learned arms' pass-floor misses are
operational, not representational — A1's declared guard reaches fp 0.996 with zero
fitting, and A4 (best learner, 0.735 agreement) still lands at exec 71.0.

Lever (`fna5b.py`, frozen in `FREEZE_FNA5B_ADDENDUM_V1.json` before its run): shrink the
information contract to the minimum the guarded rule reads — 24-atom subsampled
dispersion + 15-pair subsampled alias, single pass, every counted op charged; world
physics still evaluates on TRUE dispersion/alias. Also measured the **perfect-router
bound**: oracle exec + minimal extraction + 2 ops inference.

Re-test: A1B insufficient (agreement 0.413, fp 0.925, exec 84.9, total 214.9 — subsample
noise costs both precision and cost). **Perfect-router bound 182.36 > budget 61.28**:
even a perfect router paying the minimum honest information price (122/query) lands at
3.0x budget, and the decision value itself (baseline 96.11 − oracle 58.36 = 37.75/query)
is 3.2x smaller than that price. The obstruction is structural at this scope: knowing
enough about a query to route it safely costs more than routing is worth. Terminal stands;
mechanism recorded as `ACQUISITION_COST_DOMINATES`.

## Reading for the ladder question (#214 FNA-5: which class would own a routing residual?)

- At this scope **no selector class — neural included — pays back under whole-lifecycle
  charging**; the blocking stage is information acquisition, not representation or
  learning capacity (A6 diagnostic: total 103k, worst of all arms).
- The **pass floor is reachable without learning** (declared guard, fp 0.996, robust to
  drift at fp 1.000): safety comes from the declared law + exact-family fallback, not from
  a fitted model. Any future authorized router should be guard-first.
- Where acquisition is already sunk (features exist for other reasons) the ladder order
  would be: A4 tree-class first (best agreement 0.735 at exec 71.0), then A3b/A2 — but
  that regime is outside this study's frozen scope.
- #71's residual-opportunity question is unchanged: this study fixes the selector-class
  answer conditionally, and shows the residual must clear the acquisition price before
  any class matters.

## Limitations (frozen pre-outcome)

One authored world (E1/L1); exact O(1) checker (failures always caught); boundary noise
gives a Bayes-irreducible gap that eps must absorb; A6 is a 1-hidden-layer diagnostic
bounding nothing about neural capacity; wall/CPU numbers are single-host descriptive.
