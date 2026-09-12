# DG-9 — the best-constant control on the E1 and E3 ecology families

Status: **FROZEN PREDICTION RECORDED; AUDIT NOT YET RUN**

Date: 2026-09-12. Gap: `DG-9`. Protocol rules: 40 (best-constant control is mandatory for every admissibility claim),
42 (two nulls), 43 (prefer a skill-referenced metric; where a raw threshold is used, rule 40's control is the manual
substitute).

Source: `RV-377-104` closed `E_ambig` and `E_noisy` in closed form and named what remained:

> "DG-9's remaining uncovered surface is the E1/E3 ecology families, which use their own metrics and have not been
> checked." — `REVIVAL_LEDGER.jsonl`, `RV-377-104`, field `claim_movement`

This record executes that. It is written in two commits: **this one freezes the enumeration and the predictions
before any number is computed**; the second records the outcome verbatim, whether or not the prediction held.

---

# 1. A premise correction, recorded before the work rather than after it

The task as handed over said "enumerate every ecology in the E1 and E3 families **in the registry**". Read against
the code, that premise is wrong in three separate ways, and each one matters for what the audit can claim.

**1. There is exactly one ecology registry and neither family is in it.** `gmi_microscope/ecology.py` defines
`REGISTRY` with six entries — `E_wit1`, `E_smooth3`, `E_sym3`, `E_sym5`, `E_parity`, `E_smooth1` — and its `family`
field takes only the values `"smooth"` and `"table"`. There is no `E1` family and no `E3` family in it. A grep of
the whole corpus for an ecology registry finds no second one: `seed_census.ECOLOGIES`, `smooth_dense_max.ECOLOGIES`,
`b2_memory.ECOLOGIES` and `predict_sym2.ECOLOGIES` are module-local lists of names already covered by
`RV-377-101`'s sweep or by the B2 layer, which uses exactness (`THETA = 1`) rather than a raw capability threshold.

**2. "E1" and "E3" are programme STAGES, not registry families.** `E1` is the stage of exact-layer ability
microscopes for the predicted forms (`gmi_microscope/e1_*.py`, records `RV-377-032/033/038/042/043/063/064`). `E3`
is the real-mathematics / code / language / science validation gate of `GMI_ESTABLISHMENT_MATRIX_V1.json`. Their
ecologies are declared **inside their own modules**, each with its **own capability metric**, which is precisely why
`RV-377-101`'s audit could not reach them.

**3. `constant_control.py` contains no `E_ambig`/`E_noisy` coverage to "keep intact".** `RV-377-104` closed those
two algebraically — their Brier **skill** metric puts the best constant at exactly 0.0 by construction — and
recorded the closure in the ledger and the gap ledger, not in this module. The existing `audit()` covers the six
registered ecologies and the `E_sym(k)` sweep, and is left byte-for-byte unchanged by this work.

Consequence for the instrument: `best_constant(target, eval_set)` as written is hard-wired to the B1 layer's
**mean-absolute-error** capability, `cap = max(0, 1 - err/1.5)` in fx units. Every E1 ecology scores by
**exact agreement** instead — a fraction of evaluated queries, sometimes within a 1 fx tolerance and sometimes
exactly. The extension therefore computes the best constant under **each family's own metric**; reusing
`best_constant` verbatim on them would have produced a number that means nothing.

---

# 2. Enumeration (read off the code, frozen before the run)

## 2.1 E1 — executed Stage-E1 ability microscopes

| # | module | ecology | obligation variant | metric | tol |
|---|---|---|---|---|---|
| 1 | `e1_vlc` | `E_factored` | scope 2, coeffs after `U=8, cone=1` (`RSTAR`/`T3`/`T4`) | agreement over 24 q | 1 |
| 2 | `e1_vlc` | `E_factored` | scope 2, coeffs after `U=0` (`T1_STATIONARY`) | agreement over 24 q | 1 |
| 3 | `e1_vlc` | `E_factored` | scope 2, coeffs after `U=8, cone=4` (`T2_DENSE_CONE`) | agreement over 24 q | 1 |
| 4 | `e1_vlc` | `E_factored` | scope 1, `U=8, cone=1` (`CQU1`) | agreement over 16 q | 1 |
| 5 | `e1_vlc` | `E_factored` | scope 4, `U=8, cone=1` (`CQU2`) | agreement over 4 q | 1 |
| 6 | `e1_vlc` | `E_factored` | scope 1, `U=8, cone=4` (`CQU3`) | agreement over 16 q | 1 |
| 7 | `e1_vlc` | `E_factored` | scope 4, `U=8, cone=4` (`CQU4`) | agreement over 4 q | 1 |
| 8 | `e1_cp` | `E_factored3` | regime A, shared coefficients | agreement over 24 q | 1 |
| 9 | `e1_cp` | `E_factored3` | regime B (boolean, `sum > 0.75`), shared | agreement over 24 q | 0 |
| 10 | `e1_cp` | `E_factored3` | regime C (argmax), shared | agreement over 24 q | 0 |
| 11 | `e1_cp` | `E_factored3` | regime B, `N3` independent coefficients | agreement over 24 q | 0 |
| 12 | `e1_cp` | `E_factored3` | regime C, `N3` independent coefficients | agreement over 24 q | 0 |
| 13 | `e1_scdi` | `E_factored` | regime A (exact sum), no revision | agreement over 24 q | 0 |
| 14 | `e1_scdi` | `E_factored` | regime B (boolean threshold) | agreement over 24 q | 0 |
| 15 | `e1_scdi` | `E_factored` | regime C (argmax) | agreement over 24 q | 0 |
| 16 | `e1_scdi` | `E_factored` | regime D (quantized sum, `>> 2`) | agreement over 24 q | 0 |
| 17 | `e1_lmhm` | `E_factored` | after 16 heterogeneous revision rounds | agreement over 24 q | 1 |
| 18–22 | `e1_vgsc` | `E_factored` | five step-sequence cells `PA000…PA100` | agreement over 24 q | 1 |
| 23 | `e1_lineage` | `E_factored` | current target, `U=8` (`E_EPHEMERAL`) | agreement over 24 q | 1 |
| 24 | `e1_lineage` | `E_factored` | as-of target, depth 1 (`P_PERSISTENT_D1`) | agreement over 24 q | 1 |
| 25 | `e1_lineage` | `E_factored` | as-of target, depth 8 (`P_PERSISTENT_D8`) | agreement over 24 q | 1 |
| 26–41 | `e1_iql` | `E_alias` | the 25-query interventional obligation at each of the 16 ground-truth orientations | agreement over 25 q | 0 |

**41 E1 variants.**

## 2.2 E3

`E3` splits into two things the corpus calls by that name, and they have opposite audit status:

- **E3 proper** (real formal mathematics / execution-verified code, `GMI_E3_*`): **zero executed ecologies.**
  `GMI_E3_EXECUTION_GATES_V1.json` records `LOCKED_BY_ISSUE_46_PREDECESSOR_RULE` for mathematics and no protected
  outcome access for coding; `GMI_E3_STATUS_V1.md` states in terms that this is "a **design/schema result**, not real
  capability evidence". Its admissibility rule is a **boolean external-verifier pass** (`admissible_result` in
  `map_proof_replay_to_gmi_e3.py` / `map_code_h0_trace_to_gmi_e3.py`), not a capability compared to a raw θ. There
  is therefore no ecology, no answer alphabet and no θ on which a best constant is even definable, and no positive
  admissibility claim in the E3 lane for this audit to void.
- **"E3-lite"** — the name the corpus uses for the neutral-search recovery lane (`GMI_THEORY_CORE_V3_EXECUTED.md`
  §341, `GMI_PARENT_LITERATURE_LEDGER_V2.md`) implemented in `gmi_microscope/blind.py` and `qd.py`. This lane
  **does** carry raw-threshold admissibility claims and is audited here.

| # | module | ecology | metric | θ |
|---|---|---|---|---|
| 42 | `blind` | `E_bind` (4 inputs) | label accuracy, `out > 0.5` | 1.0 |
| 43 | `blind` | `E_smooth` (16 inputs) | mean-abs-error capability | 0.85 |
| 44 | `blind` | `E_bind16` (16 inputs, `run3`) | label accuracy | 1.0 |
| 45 | `blind` | `E_smooth8` (256 inputs, `run4`) | mean-abs-error capability | 0.85 |
| 46 | `blind` | `E_smooth8_div` (4 targets, mean) | mean of four mean-abs-error capabilities | 0.85 |

**5 E3-lite variants. Total: 46 ecology variants.**

## 2.3 The two criteria

Mirroring `constant_control.audit()`, every variant is scored under both criteria the corpus uses:

- **`unseen`** — the registered evaluation set of that ecology (the unseen-pattern queries for the E1 factored
  ecologies; `all_x \ train` for the E3-lite smooth ecologies);
- **`all`** — every query in the ecology's full input × scope space.

For `E_alias` the obligation **is** the complete 25-query set, so the two criteria coincide by construction; both
rows are still emitted so the table has no holes.

**46 variants × 2 criteria = 92 rows.**

## 2.4 Units

Rule 40's declared conversion, one fx unit = 1/(1.5·16) = 0.0416667 capability, is a unit of **mean absolute
error**. It is the right unit for the B1 and E3-lite mean-abs-error metrics. It is **not** the quantum of the E1
exact-agreement metrics, whose own quantum is 1/|eval set| (0.0417 at 24 queries, 0.0625 at 16, 0.04 at 25, 0.25 at
4). Every row therefore reports the margin in capability, in rule-40 fx units, **and** in units of the metric's own
quantum, and a margin under one quantum of the metric actually used is flagged `WITHIN_QUANTIZATION`.

---

# 3. Frozen predictions (recorded before any number is computed)

| id | prediction |
|---|---|
| **P1** | **5 of the 46** E1/E3 ecology variants are NON_DISCRIMINATING at θ = 0.85 under at least one criterion. |
| **P2** | **6 of the 92** (variant, criterion) rows are NON_DISCRIMINATING. |
| **P3** | Every NON_DISCRIMINATING variant is a **non-exact serving regime** — the boolean threshold B, the argmax C, or the quantized D — of `E_factored` or `E_factored3`. No exact-sum (tolerance-1 fx) variant is contaminated. |
| **P4** | `E_alias` is DISCRIMINATING at **all 16** orientations; the best constant there does not exceed 0.65. |
| **P5** | All **5** E3-lite ecologies are DISCRIMINATING. |

Reasoning behind P1–P3, recorded so that a hit cannot be claimed as insight after the fact: the evaluated inputs of
the factored ecologies are exactly the unseen `(1,1)` patterns, where every in-scope factor takes its **largest**
value, so a boolean obligation of the form "is the scope sum above 0.75" is expected to be nearly all-ones there and
a constant 1 should score close to 1.0. The exact-sum regimes spread their targets over many fx values and a single
constant should not cover 85 % of them. `E_alias` answers `v_j` under `do(v_i = 1)`; the all-ones count is the sum
of descendant-set sizes over a 5-node path, maximised at 15 of 25, so the best constant should sit near 0.6.

No number in this document was computed before this commit. The audit code is written against this enumeration and
is run only after it.

---

# 4. Scope ceiling, declared up front

This audit closes the **rule-40 (constant-answer) half** of DG-9 for the E1 and E3-lite families. It does **not**
close the **rule-42 fixed-function half**: no fixed-function null has ever been run on any E1 or E3-lite ecology,
and a machine that reads its input but ignores its feedback is not caught by anything here. That residual is
recorded as open, not as closed.

A DISCRIMINATING verdict is **necessary, not sufficient**: it says only that a machine emitting one number cannot
clear θ there. It says nothing about whether a claim on that ecology is otherwise sound.
