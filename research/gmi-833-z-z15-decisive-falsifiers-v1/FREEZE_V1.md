# GMI #833 Section Z / Z15 — decisive falsifiers, freeze v1

Source `main`: `91c6d2876ba80c517a186e28fce3bdbe4e3fc218`.

Committed **before** any falsifier checker, planted control, register or test in
`research/gmi-833-z-z15-decisive-falsifiers-v1/` exists. `git log` must show this
commit strictly preceding the first implementation commit of this package.

## Claim ceiling

```
GMI_833_Z15_FOUR_EXECUTABLE_DECISIVE_FALSIFIERS_FOR_THE_FLAGSHIP_MORPHOLOGY_SELECTION_THEORY_AT_REGISTERED_FINITE_SCOPE
```

## The exact rows this tranche may reconcile

Section Z lives in issue comment `5684819296`, subsection
`### Z15 — Decisive falsifiability`. The six rows are, verbatim:

1. `- [ ] Reduce the flagship theory to 3–5 simple decisive falsifiers understandable without the whole repository.`
2. `- [ ] Include systematic morphology-selection failure as a falsifier.`
3. `- [ ] Include architecture-uncommitted recovery outside the predicted set as a falsifier where appropriate.`
4. `- [ ] Include capability miscalibration beyond registered uncertainty as a falsifier.`
5. `- [ ] Include invariance failure under transformations claimed irrelevant as a falsifier.`
6. `- [ ] Publish failed preregistered predictions alongside successful ones.`

(Row 1 contains an en-dash in `3–5`; reconciliation must be byte-exact.)

**No neighboring row is earned here.** Nothing in Z1–Z14 or Z16–Z18, nothing in
the issue body, nothing in any other Z comment. The trailing
`## Groundbreaking flagship closure rule` prose block carries no rows.

## The flagship theory, stated without the repository

Row 1 demands falsifiers that a reader can understand without reading the
corpus. The flagship theory is therefore restated here in four sentences, and
every falsifier below refers only to this statement:

> A machine's *morphology* is whether it carries persistent internal state.
> Given a task in which some outputs must depend on an earlier input, and a
> price `lambda` charged per bit of persistent state, the theory predicts which
> morphology a resource-bounded search will select: stateless when
> `lambda > eta·p/2`, persistent when `lambda < eta·p/2`, and a tie exactly at
> `lambda = eta·p/2`, where `p` is the probability that a scored moment requires
> the earlier input and `eta` weights that requirement. The prediction is made
> from the task's parameters alone, before any search is run, and the search
> itself never sees an architecture name.

## The four falsifiers (registered now, thresholds included)

Each falsifier is a *decision procedure* with a fixed threshold, an executable
checker, a **planted positive** proving the checker can fire, and a **clean
no-alarm case** on real data. A falsifier that cannot fire tests nothing.

### `F1` — systematic morphology-selection failure  *(row 2)*

> *Plain statement:* run the exhaustive search on each registered world and look
> at which morphology actually wins. If the theory's prediction is wrong on even
> one of the 40 registered endpoint worlds, the boundary law is false.

- Quantity: number of endpoint worlds where the predicted morphology class
  differs from the exhaustively computed argmin class.
- Threshold: **fires iff count > 0**.
- Clean case: the 40 endpoints of the 20 registered `(p, eta)` worlds.
- Planted positive: the deliberately shifted boundary `2·lambda*`, registered in
  `gmi-833-heldout-20-transitions-v1` as a control. It must fire.

### `F2` — architecture-uncommitted recovery outside the predicted set  *(row 3)*

> *Plain statement:* the search is given opaque candidate identifiers and no
> architecture names. If what it recovers is not inside the set the theory
> predicted, the theory is false.

- Quantity: number of registered worlds (all 60, endpoints and boundaries) whose
  exhaustive winner class set is **not** contained in the predicted set.
- Threshold: **fires iff count > 0**.
- Clean case: all 60 registered worlds.
- Planted positive: a predicted set artificially narrowed to `{STATELESS}` at a
  world with `lambda < lambda*`. It must fire.

### `F3` — capability miscalibration beyond registered uncertainty  *(row 4)*

> *Plain statement:* the capability predictor does not emit a single number; it
> emits a *set* of values it claims the truth lies in, and abstains when the set
> has more than one member. Registered uncertainty is therefore exactly "the
> truth is inside the set". If the truth falls outside even one emitted set, the
> capability law is false.

- Quantity: number of frozen capability prediction records whose externally
  computed truth set is not contained in the frozen prediction set.
- Threshold: **fires iff count > 0**.
- Clean case: the 480 records of the pinned capability-evaluation population.
- Planted positive: one covering set with a truth element removed. It must fire.

### `F4` — invariance failure under transformations claimed irrelevant  *(row 5)*

> *Plain statement:* two changes are claimed to be irrelevant — renaming the
> candidates, and measuring both the error weight and the state price in a
> different unit. If either changes which morphology wins, the theory is false.

- Transformation `T_a` (**claimed irrelevant**): a permutation of candidate
  surface identifiers. Quantity: number of registered worlds whose winner class
  set changes under any of 200 seeded permutations. Threshold: fires iff `> 0`.
- Transformation `T_b` (**claimed irrelevant**): common positive rational
  rescaling `(eta, lambda) -> (c·eta, c·lambda)` for a registered ladder of `c`.
  Quantity: number of `(world, c)` pairs whose winner class set changes.
  Threshold: fires iff `> 0`.
- Planted positive for `T_a`: a pseudo-remint that also permutes the error
  counts, i.e. changes semantics while pretending to be a relabelling.
- Planted positive for `T_b`: rescaling `eta` **only**, which is *not* claimed
  irrelevant and must move the boundary. This pair is the point: the checker
  must stay silent on the genuinely irrelevant transformation and fire on the
  relevant one, so it is not merely a constant `False`.

Four falsifiers, inside the row's registered range of three to five.

## Row 6 — failed preregistered predictions

A `FAILED_PREDICTION_REGISTER_V1.json` publishes the programme's real failed and
falsified preregistered predictions **alongside** the successes, each pinned by
repository path, git blob sha and a verbatim anchor string that must occur
exactly once in the pinned file. The register is machine-checked: a missing
file, a changed blob, or an anchor occurring zero or more than one time fails the
run. Entries registered now, before the checker exists:

| id | what failed | pinned in |
|---|---|---|
| `FP-KE3D` | three prospectively frozen registration laws for real trained systems, each falsified by its own pre-registered falsifier; the row stays open | `gmi-833-capability-predictor-evaluation-v1/CORE.md` |
| `FP-939-OVERSTRONG` | the one confirmed OVERSTRONG corpus finding (capability-interactions universal phrasing) | `gmi-833-theory-baseline-v1/BASELINE_V1.md` |
| `FP-REV-OPEN` | six open revival tickets carried as obligations, not acceptable terminals | `gmi-833-theory-baseline-v1/BASELINE_V1.md` |
| `FP-SHIFTED-BOUNDARY` | the deliberately wrong boundary `2·lambda*`, falsified in all 20 cases — a registered negative control, labelled as such and not as a surprise | `gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md` |
| `FP-Z12-CAL-V1` | this programme's own Z12 calibration instrument, frozen at record level, found mis-specified and repaired before its numbers were used | `gmi-833-z-z12-prediction-scoring-v1/FREEZE_V1_AMENDMENT_2.md` |

A successes register is published beside it so the comparison is visible rather
than asserted.

## Two materially independent routes

- **Route A** `z15_decisive_falsifiers_v1.py`: evaluates every falsifier from the
  closed-form boundary law plus a direct per-candidate scan.
- **Route B** `independent_falsifier_oracle_v1.py`: rebuilds the candidate
  universe by a different decomposition — a multiplicity histogram over
  `(state_bits, e_now, e_delay)` reduced to integer objective coefficients — and
  re-decides every falsifier from that histogram. It imports nothing from route A
  and nothing from the Z12 package.

## Null the true result must beat

200 randomized boundary laws `lambda*_rand = r·eta·p/2` with `r` drawn from a
seeded rational ladder excluding `r = 1`. Each must be **caught** by `F1`.
Target: `200/200` random boundaries falsified, `0/200` surviving. If any survives
undetected, `F1` is not decisive and the result is reported as a failure.

## Forbidden promotions

`FALSIFIER_SET_IS_COMPLETE`, `THEORY_VERIFIED_BY_SURVIVING_FALSIFIERS`,
`REAL_SYSTEM_FALSIFICATION`, `UNIVERSAL_MORPHOLOGY_LAW`,
`ALL_FAILED_PREDICTIONS_ENUMERATED`, `COMPLETE_GMI`,
`NEGATIVE_CONTROL_IS_A_DISCOVERED_FAILURE`.

## Falsifiers of this package itself

- Any registered falsifier whose planted positive does not fire.
- Any registered falsifier that fires on the clean case.
- Route A and route B disagreeing on any falsifier verdict or count.
- Any register entry whose pinned blob sha or anchor count does not check out.
- Any randomized boundary surviving `F1`.
