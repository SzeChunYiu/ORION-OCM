# RV-377-106 — FREEZE: the DG-10 measurement panel cannot separate its own reference laws

Frozen BEFORE the repair run. Nothing below may be edited after the run;
outcomes are appended verbatim in the adjudication commit.

## 1. What was received

`gmi/k4-dg10-hardening-v5` (head `bd875488`, 21 commits) responds to the two
findings recorded in PR #445: it derives the K4 `state_scales_with` /
`serve_scales_with` axes from *measured* resource traces instead of copying
them out of the candidate token (DG-10), and it repairs the three hostile
tests that died on the no-admissible-candidate early return.

The design is right. A candidate carries two independently selected integer
resource expressions; the public axis labels are recovered only by executing
each expression on a fixed probe panel and matching the numeric trace against
the preregistered reference laws, with `UNCLASSIFIED_*_LAW` fallbacks.

## 2. The defect

`gmi_k4_resource_native_v4.py` raises on **import**, at its own self-check:

```
File ".../gmi_k4_resource_native_v4.py", line 125, in <module>
    raise AssertionError("state measurement panel aliases reference laws")
```

Every importer is affected — `gmi_k4_search_v4.py`, `gmi_k4_search_v5.py`,
`gmi_k4_null_frontier_v5.py`, `test_gmi_k4_resource_native_v4.py` — and because
pytest fails at *collection*, the branch's entire suite is blocked, not merely
the K4 tests. The 8 newest commits (null-aware K4 V5, its freeze JSON, the
LUNARC sizing, the beacon, the aggregate, the renderer/submitter) are therefore
built on a module that has never once executed.

### Root cause (mechanical, not environmental)

`_probe_env(i)` assigns every resource variable

```python
env = {v: 2 + ((j * 7 + i * 11) % 13) for j, v in enumerate(_RESOURCE_VARS)}
```

where `j` is the variable's index in the sorted variable list. There are **39**
variables but the modulus is **13**. Since 7 is invertible mod 13, `j*7 mod 13`
depends only on `j mod 13`, so the variables at indices `j`, `j+13` and `j+26`
receive *identical* values. The `i*11` term shifts every variable by the same
amount, so no probe can ever break the tie: the aliasing holds simultaneously on
all 19 probes. Only `search_branch`, `window` and `rank` escape, because they are
explicitly overridden afterwards.

Measured consequence on the received code:

- 39 resource variables collapse to **16** distinct value-traces
- 22 `STATE_REFERENCE` laws collapse to **16** distinct signatures
- 21 `SERVE_REFERENCE` laws collapse to **19** distinct signatures

Colliding state pairs: `n_retained_sections`/`n_hypotheses`,
`n_records`/`hidden_width`, `n_constraints`/`kernel_size`,
`program_size`/`edge_features`, `state_dim`/`dynamics_model_size`,
`corpus_size`/`score_model_size`. Colliding serve pairs:
`n_retained_sections`/`n_hypotheses`, `policy_size`/`sequence_length`.

This is not cosmetic. The entire DG-10 argument is that the axis label is
*recovered by measurement* rather than carried in the token. A panel that
cannot separate 6 of 22 state laws does not recover the label; it would have
mislabelled silently had the self-check not been there. The self-check is the
one part of this module that worked, and it is what makes the lane's own claim
auditable. Credit where due — it fired correctly.

### A second leak the self-check does not cover

The module builds `STATE_SIG_TO_LABEL` from `STATE_REFERENCE` only, then asserts
only reference-vs-reference injectivity. It never checks the **distractors**.
On the received panel, `STATE_DISTRACTORS[1] = V("positions")` aliases the
reference law `dynamics_model_size = V("dynamics")`, so a candidate selecting a
deliberate non-target law would be reported as having hit a frozen target
coordinate. That is the DG-10 failure mode in reverse — a leak *into* the answer
key rather than out of it — and it is currently unguarded.

## 3. Minimal justified change

Raise the probe modulus above the variable count, keeping the multiplier coprime
to it, and add the missing distractor guard. Nothing else in the module changes:
no reference law is added, removed or rewritten, no candidate generation or
ranking is touched, the probe count stays 19.

```python
_PROBE_MOD = 41   # prime, > len(_RESOURCE_VARS) == 39
env = {v: 2 + ((j * 7 + i * 11) % _PROBE_MOD) for j, v in enumerate(_RESOURCE_VARS)}
```

plus a fourth assertion: no `STATE_DISTRACTORS` / `SERVE_DISTRACTORS` element may
carry a signature present in the corresponding reference table.

## 4. Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| P1 | With `_PROBE_MOD = 41`, `gmi_k4_resource_native_v4` imports with no assertion. | any assertion on import |
| P2 | All 39 resource variables receive distinct value-traces; all 22 state and all 21 serve reference laws receive distinct signatures. | any collision |
| P3 | No distractor aliases any reference law, so the new fourth assertion passes as written rather than needing the distractor set changed. | a distractor collision forcing an edit to `*_DISTRACTORS` |
| P4 | **The V4/V5 test files will show at least one further failure beyond the import error.** A module this size that has never executed is not correct on first run. | the V4/V5 tests pass first time |
| P5 | The 245 tests green before this merge stay green; the fix changes no result outside the K4 V4/V5 line. | any previously-green test turns red |

P4 is the prediction that costs something. It is stated against the Codex lane's
work and against the convenient outcome. If P4 is falsified — if the whole V4/V5
stack runs clean the moment the panel is widened — that is recorded as a win for
the lane, not quietly dropped.

## 5. What this does NOT do

This repairs the *instrument*. It does not adjudicate DG-10. Whether the measured
axes actually break the family bijection is a separate question, answerable only
after the module runs, and is not claimed here.

No RED result is touched. No earlier failure is rewritten.

---

# RV-377-106 — OUTCOMES (appended after the repair run; nothing above was edited)

## Repair applied

`_PROBE_MOD = 41` (prime, > 39 variables), with an assertion that the modulus
exceeds the variable count, plus the two missing distractor guards. No reference
law added, removed or rewritten; probe count unchanged at 19; candidate generation
and ranking untouched.

## Results, verbatim

```
P1 IMPORT OK, probes=19 mod=41 vars=39
P2 distinct variable traces: 39/39
P2 state signatures: 22/22
P2 serve signatures: 21/21
P3 state distractor->reference: [None, None, None]
P3 serve distractor->reference: [None, None, None]
P3 measure of distractors: ['UNCLASSIFIED_STATE_LAW', 'UNCLASSIFIED_STATE_LAW',
  'UNCLASSIFIED_STATE_LAW'] ['UNCLASSIFIED_SERVE_LAW', 'UNCLASSIFIED_SERVE_LAW',
  'UNCLASSIFIED_SERVE_LAW']
```

```
$ python3 -m pytest test_gmi_k4_resource_native_v4.py -q
........                                                                 [100%]
8 passed in 2.84s
```

| id | outcome |
|----|---------|
| P1 | **CONFIRMED** |
| P2 | **CONFIRMED** — 39/39, 22/22, 21/21 |
| P3 | **CONFIRMED** — the new assertion passes as written; no distractor edit needed |
| P4 | **FALSIFIED** |
| P5 | pending full-suite run |

### P4 was falsified, and that is a win for the Codex lane

I predicted the V4/V5 tests would show at least one further failure beyond the
import error, on the reasoning that a module of this size that has never once
executed will not be correct first time. All 8 tests passed on the first run.
The prediction was wrong and the lane's code was right. Recorded as stated, not
dropped: the defect was confined to the probe panel's modulus, and everything the
panel feeds was correct.

## Two findings that stand regardless

**F1 — the V5 stack has no tests.** `gmi_k4_search_v5.py` and
`gmi_k4_null_frontier_v5.py` have no test file; `test_gmi_k4_resource_native_v4.py`
covers V4 only. Eight commits — the null-aware successor, its freeze JSON, the
LUNARC sizing, the beacon, the aggregate, the renderer and the submitter — rest
on untested modules that, until this repair, could not be imported.

**F2 — DG-10's status was asserted, not demonstrated.**
`GMI_K4_NULL_AWARE_SUCCESSOR_FREEZE_V5.json` records
`"DG-10": "CLOSED_BY_MEASURED_FACTORISED_RESOURCE_AXES_AT_V5_SCOPE"`. At the time
that was written the mechanism said to close DG-10 raised on import and had never
run. After this repair the *instrument* demonstrably separates all 22 state and
all 21 serve laws, so the mechanism now exists — but DG-10 is closed only when the
protected V5 run actually recovers the measured target vector. The freeze's
own status line remains ahead of its evidence and is left in place, unedited,
with this narrowing recorded against it.

## What was checked and found clean

The commit `55e94109 "size LUNARC from null-aware K4 V5 development sample"` was
audited for fabricated numbers, since no development sample could have been taken
from a module that raised on import. It changes only the probe *script*; no
`LUNARC_ENV_PROBE_V1.json` with numbers was committed, the sizing is computed at
run time on LUNARC, and every field is tagged
`DEVELOPMENT_ONLY_MEASURED_NOT_SUBMITTED` /
`"Development verdict and null audit are never protected evidence."` The commit
title overstates ("from ... development sample" implies a sample was taken) but
no result is fabricated. This lane is disciplined about the evidence line.

---

# RV-377-107 — FREEZE: first execution of the V5 null frontier returns RED

Frozen BEFORE the development sweep. Appended outcomes only.

## The triggering observation

With the panel repaired, `gmi_k4_search_v5.run_cell` executes for the first time.
On the first family/grammar cell, at both budgets tried:

```
budget=  2000 wall=   0.19s verdict='THEORY_RED_NULL_DOMINATES' best_null=NULL_FIXED_NUMERIC
budget= 20000 wall=   1.86s verdict='THEORY_RED_NULL_DOMINATES' best_null=NULL_FIXED_NUMERIC
```

`NULL_FIXED_NUMERIC` reaches `semantic_score: 1.0` with
`development_compute: 0.0` and `update_retraining: 0.0` both forced to zero, for a
scalar lifecycle cost of 32.914 — strictly below the admissible developed witness.
Per the lane's own frozen rule this is RED **even if the 10-axis vector matches**,
"because the obligation failed to distinguish developed from hard-coded behavior."

This is rule 42 firing exactly as it was written to fire. A hard-coded answer beats
a developed one, so the obligation on this cell certifies nothing about
intelligence.

## Scope discipline

This is a DEVELOPMENT result at a development seed. The V5 freeze states: "No V5
protected task may execute until the one-shot V5 public beacon receipt exists. Any
V4/V5 development smoke result is excluded from the protected aggregate." It is
therefore **not protected evidence** and is not counted as one. It is recorded
here as the basis of a falsifiable prediction about the protected run.

## Frozen predictions for the 264-cell development sweep

Grid: 22 families x 3 grammars x 4 cells (w1,w2,w4,w8), budget 20000, development seed.

| id | prediction | falsifier |
|----|-----------|-----------|
| Q1 | **>= 60% of the 264 cells return `THEORY_RED_NULL_DOMINATES`.** | fewer than 158 cells RED |
| Q2 | It is **not** 100% — at least one family resists null dominance, because obligations requiring stochastic serve, retrieval or external authority should not be satisfiable by a fixed numeric answer. | all 264 cells RED |
| Q3 | `NULL_FIXED_NUMERIC` or `NULL_FIXED_TABLE` is the dominating null in the majority of RED cells. | a different null dominates most |
| Q4 | The protected beacon run will reproduce the same RED verdict on the cells RED here. | protected run turns those cells GREEN |

Q1 and Q4 are predictions **against** GMI. If they hold, the K4 obligation set is
largely non-discriminating and a large block of the K4 programme certifies nothing.
That is the outcome this sweep is designed to expose rather than avoid.

Q2 is the prediction that can save something: if some families resist, those are
the cells where the obligation genuinely demands development, and they are the only
K4 cells whose verdicts mean anything.
