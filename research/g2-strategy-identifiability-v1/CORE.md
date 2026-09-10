# G4.4 identifiability boxes at a polynomial microscope

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) remaining
machine-decision boxes (G4.4 / #71 unlock preconditions), asked here on the
same tiny polynomial identity world G2 uses — not on the unmerged 142-target
semantic lifetime, and not as a G2.4 close.

G4.4 stays **locked**. This capsule does not train a router.

Process restart is a different capsule (`research/g2-process-restart-v1/`).

## Parents (cite, do not rewrite)

| Parent | Disposition |
|---|---|
| `research/g4-horizon-exact-v1/` | ADOPT the exact-parent ladder (static arms, closed-form threshold, finite DP, residual table). REJECT copying the cache engines. On that toy, analytic residual vs DP was already 0 on known sequences. |
| `research/paid-decision-region-correction-v1/` | ADOPT contained decision-region / common-action stopping as the *safety* parent. After exact admissibility both arms succeed, so the remaining question is value, not a missing safe action. |
| `research/decision-core-successor-repair-v1/` | ADOPT snapshot-the-legal-action-iterable before comparing Q. Finite meta-DP is the oracle here. |
| `research/g2-two-decision-search-v1/` | ADOPT the two-decision consumer idea. REJECT Metamath GetSteps as this microscope (that capsule's GetSteps count is 0; G2.4 cannot be checked there). |

Pinned production source: `src/ocm/learning/methods.py` blob
`50323a33418b8ef8bb6500ddeba4b9d1f795e9e3`. No `src/` edits.

## Tiny exact world

Finite noiseless two-action MDP over four frozen polynomial tasks.

```text
MATCH family     degree 2   (inc, square) and (inc, square, inc)
MISMATCH family  degree 1   (double, inc) and (dec, double)
```

Actions are exclusive complete search arms, not the mixed alternating stream
inside `methods.solve` with a live fragment:

- `PRIMITIVE` — `_primitive_programs` only
- `MACRO` — `_guided_programs` with compiled 2-op fragment `(inc, square)` only

Both arms verify every task (exact admissibility). Cost is integer search
slots. No sampling. Q(s, a) is the exact slot count of arm `a` on task `s`.

Legal pre-outcome feature, registered before search: **polynomial degree**,
read from the task coefficients. A deficient aliasing channel
(`constant_term_nonzero`, true on every task) is recorded as a control.

Closed-form parent, analogue of g4-horizon's `remaining*(rent-hit) > build`:

```text
use MACRO  iff  degree >= 2
```

## What this may CHECK

Only at this four-task microscope:

1. ≥2 distinct legal strategies remain after exact admissibility
2. optimal arm changes across ≥2 legal pre-outcome states
3. counterfactual value of the unused legal arm by exact backup
4. residual of simple exact/analytic parents vs the finite DP
5. whether the registered legal features suffice
6. whether the threshold hypothesis class is adequate *for this world*

If the analytic threshold recovers the DP, the terminal is
`PARENT_SUFFICIENT_AT_SCOPE`. That is not programme failure. It does **not**
unlock G4.4 ML. It does **not** claim G2.4 complete.

## Terminals

```text
PARENT_SUFFICIENT_AT_SCOPE
STRATEGY_SELECTION_RESIDUAL_CONFIRMED
SINGLE_SAFE_STRATEGY_ONLY
OPTIMAL_STRATEGY_CONSTANT
COUNTERFACTUAL_NOT_IDENTIFIABLE
OBSERVATION_CHANNEL_INSUFFICIENT
HYPOTHESIS_CLASS_INADEQUATE
CANNOT_CHECK_LEGAL_FEATURES
```

## Run

```sh
python3 -B -m unittest discover -s research/g2-strategy-identifiability-v1 -p 'test_*.py' -v
python3 -B research/g2-strategy-identifiability-v1/experiment.py --out research/g2-strategy-identifiability-v1/RESULT.json
```
