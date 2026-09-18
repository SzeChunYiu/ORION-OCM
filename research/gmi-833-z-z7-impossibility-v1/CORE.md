# GMI #833 Section Z / Z7 — prospective impossibility and failure prediction

Closes the six rows of `### Z7` in issue comment `5684819296`.

## What it establishes

Over the registered `65552`-candidate binary mechanism universe and the `60`
frozen worlds, with every hypothesis and ceiling committed before the enumeration
that adjudicates it:

- **an impossible capability** `IM-1`: at `bits = 0`, zero-error delayed recall
  is impossible and the whole family sits at exactly `e_delay = 8 = N/2`, so
  delay accuracy is capped at exactly `1/2`. The same task is solved with `0`
  errors at `bits = 1`: the impossibility is resource-dependent, not
  task-dependent;
- **exact impossibility regions** `IM-2`: `286` of `289` attainability-lattice
  cells unreachable at `bits = 0` and `146` at `bits = 1`; `3656` of the `7680`
  frozen cost-grid cells infeasible, split `2976` at `b = 0` and `680` at `b = 1`;
- **frozen qualitative failure modes** `IM-3`: `Q1`, `Q2`, `Q3`, `Q5` confirmed;
  the `[NAIVE]` scarcity hypothesis `Q4` **refuted** with an explicit witness
  (`nxt = 68`, `table = 13`, `(e_now, e_delay) = (16, 0)`);
- **frozen capability ceilings** `IM-4`: `C1`–`C4`, `C6` each valid **and** tight;
  `C4 = 16` and `C5 = 143` had their form frozen and their value measured, and
  are labelled so;
- **broad families** `IM-5`: all `65552` candidates plus six named structural
  families, with a structural finding — the Moore family cannot reach fewer than
  `8` copy-channel errors (frontier `{(8,0)}`) while the Mealy family reaches `0`
  (frontier `{(0,0)}`) at identical state budget;
- **counterexample and repair** `IM-6`: the failed assumption ("one bit of state
  must be shared between channels") is named, the repair is recorded (the mode bit
  indexes disjoint table entries), and the witness is re-scored by both routes;
- **a discriminating null** `IM-7`: `153/153` witness soundness, and `6/200`
  random impossibility claims true-and-tight against `5/5` frozen ceilings.

## What it does not establish

No universal impossibility, nothing about real or trained systems, no complete
enumeration of failure modes, no substrate-independent resource accounting, and
nothing about MLP/CNN/Transformer families. The Moore/Mealy separation is a
statement about this registered transducer universe only.

Claim ceiling:

```
GMI_833_Z7_EXACT_RESOURCE_DEPENDENT_IMPOSSIBILITY_REGIONS_AND_PROSPECTIVELY_FROZEN_CAPABILITY_CEILINGS_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z7-impossibility-v1/independent_impossibility_oracle_v1.py
python3 -I -B  research/gmi-833-z-z7-impossibility-v1/z7_impossibility_v1.py
python3 -I -B  research/gmi-833-z-z7-impossibility-v1/test_z7_impossibility_v1.py -v
python3 -I -O -B research/gmi-833-z-z7-impossibility-v1/test_z7_impossibility_v1.py -v
```

Stdlib only. Both routes run in under two seconds on one core.

## The instrument failed first

The freeze states the cost grid has `19200` cells; the frozen axes give `7680`,
and the stated total was an arithmetic slip. The always-infeasible target set was
first aggregated across state budgets, which made it vacuous in a subsection
about resource-dependent impossibility; it is now reported per budget. Both are
recorded in `FREEZE_V1_AMENDMENT_1.md`, committed before the receipt.
