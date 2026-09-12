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

---

# RV-377-107 — ADJUDICATION (appended; nothing frozen above was edited)

Sweep executed: 22 families × 3 grammars × 4 cells = **264 cells**, budget 20 000,
development seed `0x4B345035`, 4-way parallel, all 264 completed with status `OK`,
zero errors.

## The headline is not any of my four predictions

```
verdicts
  THEORY_RED                   159   (60.2%)
  THEORY_RED_NULL_DOMINATES     69   (26.1%)
  INCONCLUSIVE_GRAMMAR          36   (13.6%)

GREEN cells: 0 of 264
target_vector_match: False on 228, None on 36  -- True on ZERO
```

> **Not one cell in the entire K4 grid recovered its frozen target vector.**

The three failure modes, each with its single verbatim reason string:

| n | verdict | reason |
|---|---|---|
| 159 | `THEORY_RED` | "concrete admissible non-target frontier is cheaper than frozen target witness" |
| 69 | `THEORY_RED_NULL_DOMINATES` | "an inert hard-coded null is admissible and strictly cheaper than the frozen target witness; registered obligation does not require development" |
| 36 | `INCONCLUSIVE_GRAMMAR` | "frozen target vector lacks an admissible measured-resource witness" |

The 159 matter most. K4's core claim is that the frozen family's property vector is
what a cost-minimising search *converges on* under the obligation. On 159 cells the
search found an **admissible candidate that is cheaper and is not the target**. That
is a found object: more budget cannot un-find it.

## Predictions, scored

| id | prediction | outcome |
|----|-----------|---------|
| Q1 | ≥ 60% of cells `THEORY_RED_NULL_DOMINATES` | **FALSIFIED** — 26.1% (69/264) |
| Q2 | not 100% — at least one family resists | **CONFIRMED** |
| Q3 | `NULL_FIXED_NUMERIC` or `NULL_FIXED_TABLE` dominates in a majority of RED cells | **CONFIRMED, marginally** — 36/69 = 52.2% on the disjunctive reading I wrote; on a single-null reading the top is `NULL_FIXED_NUMERIC` at 34.8%, which would **fail**. Recorded both ways; the margin is one cell wide and I do not claim this as a real confirmation. |
| Q4 | protected beacon run reproduces these verdicts | **PENDING** |

**Q1 was wrong, and wrong in the direction that matters.** I predicted null dominance
would be the dominant failure. It is not — it is the *minority* failure at 26.1%. The
dominant failure is worse than null dominance: on 60.2% of cells a **developed,
non-target** candidate beats the target. Null dominance says the obligation is too
weak to require development; the 159 say that even when development is required, the
frozen answer is not the one development finds. My prediction underestimated how badly
K4 does.

The full null breakdown among the 69, which I did not predict:

```
NULL_FIXED_NUMERIC            24  (34.8%)
NULL_FIXED_VERIFIED_PROGRAM   24  (34.8%)
NULL_FIXED_TABLE              12  (17.4%)
NULL_FIXED_WORLD_MODEL         9  (13.0%)
```

`NULL_FIXED_VERIFIED_PROGRAM` tying for first was not anticipated by anyone: a
hard-coded program that passes its own verifier beats the developed witness as often
as a fixed number does.

## The grammar axis is verdict-inert

| | |
|---|---|
| family × cell combos where all three grammars agree on the verdict | **88 / 88** |
| combos where any grammar disagrees | **0** |
| combos where the *target cost* is identical across grammars | 12 / 88 |
| combos where the *null cost* is identical across grammars | 64 / 88 |

The three grammars — typed tensor dataflow, register machine, FSM message passing —
produce **different numbers and identical verdicts, every time**. They do real work
arithmetically and none adjudicatively.

Consequence: the 3× grammar replication supplies no independent evidence. **The
effective sample is 88 family × cell combos, not 264 cells**, and every count above
should be read at one third its nominal weight for purposes of independence. The
freeze's `grammar_independence_note` claims more than this data supports and is
recorded as overstated. This is registered as a new gap:

> **DG-11 — the grammar axis has never been shown to change an adjudication.** Until
> a cell is exhibited whose verdict differs between two grammars, grammar is a
> presentation variable, not an independent probe, and any claim resting on
> cross-grammar agreement is circular.

## Scope and budget — what this does and does not establish

This is a **development-scope result and is not protected evidence**, by the lane's
own frozen rule. Budget was 20 000 against the frozen `green_rule`'s requirement of
≥ 10⁶ scored candidates — **50× under-resourced**. Honest accounting of what survives
that gap:

| finding | budget-robust? |
|---|---|
| 0 of 264 target vectors recovered | **No.** More search could recover some. |
| 159 cells have a cheaper admissible non-target | **Partly.** The cheaper non-target is found and cannot be un-found, so the target is not *uniquely* cost-minimal at this scope. But more budget could also find a cheaper target witness and flip the comparison. |
| 69 cells lose to an inert null | **Partly.** The null's cost is hard-coded and budget-independent — it is a fixed bar. The target witness's cost is search-dependent, so more budget could clear it. |
| 36 cells have no admissible witness at all | **No.** Most budget-sensitive of the three. |
| grammar is verdict-inert on 88/88 | **No**, but it is the cleanest signal here, and divergence at higher budget would itself be a reportable surprise. |

None of these is claimed as a protected result. Q4 stands frozen: the protected beacon
run is predicted to reproduce these verdicts on these cells, and if it does not, that
falsification is recorded against me.

## What this costs GMI

At development scope the K4 engine — the lane's strongest instrument for showing that
GMI's property axes are what cost-minimisation discovers — recovers **none** of its 22
frozen families under **any** of its 3 grammars at **any** of its 4 cells. The
predominant reason is not that the obligation is too weak (that is only 26.1%) but
that the frozen answer is not what the search converges on.

`K4_PROPERTY_PREDICTION_GREEN_AT_REGISTERED_SCOPE` is **FALSE at development scope**,
with the protected verdict pending and predicted by Q4 to be the same.

---

## RV-377-107 — CORRECTION to the grammar-inertness table (self-reported)

Two numbers in the DG-11 table above were wrong. The error is mine, in the
*analysis* script, not in the Codex lane's engine.

**The mistake.** My sweep script recorded the receipt's top-level
`scalar_lifecycle_cost` under the column name `target_cost`. That field is the
**search winner's** cost, not the frozen-target witness's. The witness's cost lives
in `expressibility_witness.scalar_lifecycle_cost`, and the null-vs-witness
comparison is `null_vs_target_witness_margin`. Separately, my identity test counted
two missing values as equal, inflating the "identical" counts.

**Corrected table:**

| quantity | identical across all three grammars | as first reported |
|---|---|---|
| **verdict** | **88 / 88** | 88 / 88 — *unchanged* |
| search winner cost | **0 / 76** | wrongly given as "target cost 12 / 88" |
| best admissible null cost | **0 / 24** | wrongly given as 64 / 88 |
| null-vs-target-witness margin | **0 / 24** | not reported |

Cross-grammar spread in the null-vs-witness margin is nonzero on **24 of 24**
combos where it is defined, reaching 158.52 on `K4-A15 | w8`.

**DG-11 is strengthened, not weakened.** The corrected reading is sharper than the
one I published: the grammar changes **every numeric quantity on every combo where
that quantity is defined — 0/76 and 0/24 identical — and changes a verdict on none
of 88.** The claim that the grammar axis is verdict-inert stands on better evidence
than the table I first wrote.

**The Codex adjudicator was checked for a real inconsistency and is correct.** Three
cells (`K4-A19` at `w8`, all three grammars) carry a *negative* null-vs-witness
margin, i.e. the null is **not** cheaper. All three are adjudicated `THEORY_RED`,
none as `THEORY_RED_NULL_DOMINATES`. The engine does not claim null dominance where
the margin does not support it. The apparent contradiction I chased — cells whose
`null_cost` exceeded their `target_cost` — was entirely an artefact of my column
naming.

No verdict count, no prediction score (Q1–Q4), and no other statement in the
adjudication above depended on the two wrong numbers.
