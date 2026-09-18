# FREEZE — gmi-833-ae-ae5-causal-state-audit-v1

**Committed before any implementation blob of this package exists.** The git
history must show this file's commit strictly preceding the first commit that
introduces `ae5_causal_state_audit_v1.py`, `independent_process_oracle_v1.py`,
`test_ae5_causal_state_audit_v1.py`, `RESULT_V1.json`, `MANIFEST_V1.json`,
`AE5_THEOREMS_V1.md`, `PARENT_OWNERSHIP_V1.md`, `CORE.md` or
`ISSUE_833_RECONCILIATION_AE5_CAUSAL_STATE_AUDIT_V1.json`.

- issue: `833`
- issue comment: `5692689542` (Section AE)
- source_main: `349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`
- section map consumed: `research/gmi-833-ae-section-map-v1/AE_SECTION_MAP_V1.md`,
  batching-plan item **3**

## Claim ceiling

```
GMI_833_AE5_PREDICTIVE_STATE_PARENT_OWNERSHIP_AUDITED_ON_A_REGISTERED_FINITE_DYADIC_PROCESS_FAMILY
```

## The EXACT rows this tranche may reconcile — and no others

**Five** of AE5's six rows, under anchor `### AE5 — Predictive-state / causal-state unification audit`, byte-exact from a live fetch of
comment `5692689542` at `source_main`:

1. `- [ ] Relate GMI predictive equivalence to computational-mechanics causal states / epsilon-machines at the exact applicable scope.`
2. `- [ ] Compare GMI minimal sufficient predictive state with statistical complexity and predictive information/excess entropy.`
3. `- [ ] Determine whether existing GMI state-complexity results are already parent-owned by causal-state/minimal-predictor theory.`
4. `- [ ] Construct processes where predictive-state cardinality, linear predictive rank, entropy of causal state, and description length disagree.`
5. `- [ ] Extend beyond finite horizon only with explicit measurable/infinite-horizon assumptions; otherwise preserve OPEN gaps.`

**AE5's fifth row —**
`- [ ] Determine which quantity, if any, predicts morphology/resource cost under GMI.`
**— is NOT closed here.** It is closed in this same tranche by
`research/gmi-833-ae-morphology-sweep-v1` (`SWEEP-6`), and appears exactly once
across the two reconciliation files.

**No neighboring row is earned here.**

## Registered harness (frozen before results)

- The process family is **length-4 binary GF(2)-linear-plus-fresh processes**:
  each `X_i` is either a fresh fair coin or a GF(2) linear combination of
  `X_1..X_{i-1}` given by a mask. The family has
  `2 * 3 * 5 * 9 = 270` members and is enumerated exhaustively.
- **Every probability in the family is dyadic** — a power of `1/2` — because the
  causal states are cosets of GF(2) subspaces of the fresh-coin seed space.
  Consequently every entropy is `sum_i 2^-a_i * a_i`, an exact rational, and
  **no logarithm is ever evaluated**. This dyadic restriction is the price of
  exactness and is declared here, not discovered later.
- Quantities compared: predictive-state cardinality `|S|`, the rational Hankel
  (observable-operator) rank, the causal-state entropy `C_mu`, the excess
  entropy `E`, and a registered generative description length.

## Named results this tranche may claim

- `AE5-1` GMI horizon-`H` predictive equivalence is exactly the causal-state
  partition truncated to horizon `H`; the sequence refines monotonically and
  stabilises at an exactly computed `H*`, with a counterexample proving an
  unqualified identification at `H = 1` is false.
- `AE5-2` exact `|S|`, `C_mu`, `E` table; `E <= C_mu` verified on every member;
  strict crypticity exhibited.
- `AE5-3` the parent-ownership verdict for GMI state-complexity results, with
  `PARENT_SUFFICIENT` treated as a **success terminal**, and the narrow residual
  named.
- `AE5-4` the four-quantity disagreement matrix, with both equal-value
  disagreements and strict order reversals.
- `AE5-6` the finite-horizon scope statement, the explicit infinite-horizon
  assumption list, a registered forbidden promotion, a machine-checked
  gap-preservation guard, and a proved horizon-truncation loss.

## Forbidden promotions

```
INFINITE_HORIZON_EQUIVALENCE_PROVED
STATIONARY_ERGODIC_PROCESS_THEOREM
NON_DYADIC_ENTROPY_COMPARISON
CONTINUOUS_STATE_EPSILON_MACHINE
GMI_STATE_COMPLEXITY_NOVELTY
UNIVERSAL_PREDICTOR_MINIMALITY
COMPLETE_GMI
```
