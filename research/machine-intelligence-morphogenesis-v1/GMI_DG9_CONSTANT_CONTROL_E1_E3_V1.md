# DG-9 — the best-constant control on the E1 and E3 ecology families

Status: **EXECUTED.** 3 of 46 E1/E3 ecology variants are NON_DISCRIMINATING; 116 previously-positive admissibility
verdicts are void. The frozen prediction was **WRONG on both of its quantitative clauses** (it over-predicted the
contamination) and right on all three of its structural clauses.

Receipt: `microscopes/results/STAGE_DG9_CONSTANT_CONTROL_E1_E3_V1.json` (sha256 `182a8f3861b6e0b3…`).
Instrument: `gmi_microscope/constant_control.py`, `audit_e1_e3()`. Run: `python3 -m gmi_microscope.constant_control e1e3`.

Sections 1–4 below are **unchanged from the freeze commit** (`ccddad09`), which was made before any number was
computed. Sections 5 onward are the outcome.

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

---

# 5. Outcome — the frozen predictions, adjudicated

| id | prediction | actual | verdict |
|---|---|---|---|
| **P1** | 5 of the 46 variants NON_DISCRIMINATING | **3 of 46** | **FAILS.** Over-predicted by two. |
| **P2** | 6 of the 92 rows NON_DISCRIMINATING | **3 of 92** | **FAILS.** Over-predicted by three. |
| **P3** | every NON_DISCRIMINATING variant is a non-exact serving regime (B / C / D) of `E_factored` or `E_factored3`; no exact-sum variant contaminated | all three are **regime B**, the boolean threshold; no exact-sum variant contaminated | **HOLDS.** |
| **P4** | `E_alias` DISCRIMINATING at all 16 orientations, best constant ≤ 0.65 | all 16 DISCRIMINATING; best constant ranges 0.5200 – **0.6400** | **HOLDS.** |
| **P5** | all 5 E3-lite ecologies DISCRIMINATING | all 5 DISCRIMINATING | **HOLDS.** |

**Two of five clauses failed, and both of the failures are the numeric ones.** The structural guess — that the
contamination would sit in the non-exact serving regimes and nowhere else — was right; the quantity was wrong. The
error is in a specific direction and worth naming: I predicted that the **argmax** regime C would join the boolean
regime B, on the reasoning that an argmax obligation on the all-`(1,1)` evaluation inputs would also be imbalanced.
It is not. `C_shared` tops out at 0.7500 and `C_N3_independent` at 0.6250: comparing two factor values stays
near-balanced on exactly the inputs where comparing their **sum** to a threshold degenerates. I also expected the
quantized regime D to be a candidate; it is the least contaminated regime in the whole audit at 0.4167.

---

# 6. The three NON_DISCRIMINATING rows

| rank | row | best constant | c | θ | margin | metric |
|---|---|---|---|---|---|---|
| 1 | `e1_scdi \| E_factored \| regime_B \| unseen` | **1.0000** | 1 | 0.85 | −0.1500 cap (−3.600 quanta) | exact equality over 24 q |
| 2 | `e1_cp \| E_factored3 \| B_N3_independent \| unseen` | **0.9583** | 1 | 0.85 | −0.1083 cap (−2.599 quanta) | exact equality over 24 q |
| 3 | `e1_cp \| E_factored3 \| B_shared \| unseen` | **0.8750** | 1 | 0.85 | −0.0250 cap (−0.600 quanta) | exact equality over 24 q |

The first row is the sharpest instance of DG-9 anywhere in the corpus, sharper than `E_sym3`'s 0.8750 that opened the
gap. **The obligation of `e1_scdi`'s regime B is the constant 1 on its entire registered evaluation set.** Verified
directly:

```text
[e1_scdi.truth_regime(coeffs, x, s, "B") for x, s in EVAL_QUERIES]
  = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
```

The mechanism is exactly the one the freeze predicted for B and wrongly extended to C: regime B asks "is the scope
sum above 0.75", the registered evaluation inputs are precisely the unseen `(1,1)` patterns where every in-scope
factor takes its largest value, and two such factors always sum above 0.75. There is no input in the evaluation set
on which the correct answer is 0. A machine that emits `1` forever scores **1.0000**, which is not merely admissible
but a **perfect score**, and is indistinguishable by this metric from every row the receipt certifies.

---

# 7. Voided positive claims

Rule 40: *an ecology whose best constant already clears θ is NON_DISCRIMINATING, and a row scoring above θ there has
demonstrated nothing.* Every positive admissibility verdict below is therefore void **as an admissibility claim**.
Counting unit: one `(cell, column, row)` verdict as the receipt records it.

## 7.1 `RV-377-064` / F6 Self-Compiling Developmental Intelligence — `e1_scdi`

| receipt | void verdicts | residual separation from the constant |
|---|---|---|
| `STAGE_E1_V36_F6_SCDI.json` | **60** regime-B `admissible: true` verdicts, every one at capability **exactly 1.0000** | **NONE. Zero.** The best constant also scores exactly 1.0000. |
| `STAGE_E1_V36_F6_SCDI.json` | the same **60** row-level `admissible: true` verdicts at `G ≥ 2` (row-level admissibility is `all(per_regime[g]["admissible"])`, so each one contains the void regime-B component) | partial: their A / C / D components stand |
| `STAGE_E1_CALIB_F6_SCDI.json` | **20** regime-B verdicts at capability exactly 1.0000, and the same **20** row-level verdicts | **NONE** for the regime-B half |

**80 regime-B positive verdicts are void with no residual whatsoever**: the certified rows and a constant emitter
achieve the identical, perfect score. This is the strongest form the DG-9 failure can take — not "a constant also
passes" but "a constant ties the winner exactly".

Downstream occupancy: the SCDI frontier is computed over the admissible set, so **43** non-empty frontier entries at
`G ≥ 2` in `V36` and **15** at `G = 2` in `CALIB` — **58** occupancy entries — inherit the contamination.

Clean and untouched: the **11** `G = 1` frontier entries and every `G = 1` verdict, because `G = 1` activates regime
A only and `regime_A` is DISCRIMINATING (best constant 0.4167).

## 7.2 `RV-377-033` / Cognitive Polyphenism — `e1_cp`

| cell | positive claims | status |
|---|---|---|
| `PPLUS` | **18** (`INTERP`, `EAGER`, `CP` × 6 columns) | **VOID as admissibility.** Verdict requires regime B ≥ θ on a NON_DISCRIMINATING ecology. |
| `N2_DENSE_ACTIVITY` | **18** (`INTERP`, `EAGER`, `CP` × 6 columns) | **VOID as admissibility**, same reason. |
| `N1_ONE_REGIME` | 24 | **CLEAN.** Regime A only; `A_shared` best constant 0.5000. |

**36 void.** Residual that survives, recorded so this audit does not overclaim: those rows score **1.0000** in regime
B against a best constant of **0.8750**, a separation of 3 metric quanta (0.125 capability). The *admissibility*
statement is void; a *separation from the constant* statement survives and could be re-derived. That is a different
and weaker claim than the one the receipt makes, and it is the only thing left standing there.

Downstream: **108** of the 216 CP frontier entries sit on `PPLUS` / `N2_DENSE_ACTIVITY`.

## 7.3 Total

> **116 previously-positive `(cell, column, row)` admissibility verdicts, across three receipts, rest on a
> NON_DISCRIMINATING ecology and are void as admissibility claims.** Of those, **80 have zero residual separation**
> — the certified row and a constant emitter score identically — and **36 retain a 3-quantum separation** that is a
> weaker surviving claim. **166** downstream frontier/occupancy entries are computed over the contaminated
> admissible sets.

---

# 8. Flagged but NOT void, and the negatives that get stronger

## 8.1 WITHIN_QUANTIZATION (rule 40's quantization clause)

| row | best constant | θ | margin | why it is flagged |
|---|---|---|---|---|
| `e1_vlc \| E_factored \| CQU2_GLOBAL_Q \| unseen` | 0.7500 | 0.85 | +0.400 metric quanta | evaluation set is **four queries**; the achievable capabilities are 0, 0.25, 0.5, 0.75, 1.0 |
| `e1_vlc \| E_factored \| CQU4_GLOBAL_Q \| unseen` | 0.7500 | 0.85 | +0.400 metric quanta | same |
| `blind \| E_smooth \| unseen` | 0.8333 | 0.85 | +0.401 fx units | below rule 40's one-fx-unit bar |

The two collision cells are DISCRIMINATING — a constant genuinely cannot pass — but the **entire** separation between
the best constant and an admissible row is **one query on a four-query evaluation set**. The **36** positive claims
at `CQU2` and `CQU4` in `STAGE_E1_V17_E1_CQU.json` (18 each) are therefore **flagged, not void**: they may not be
called separations under rule 40, because the margin does not resolve at the metric's own quantum. `CQU1` and `CQU3`
(16-query local evaluation) are unaffected, as is `blind`'s `E_smooth` under its **registered** `all` criterion
(best constant 0.7917, margin 1.400 fx units).

## 8.2 Negative results, preserved verbatim and in two cases strengthened

Nothing below is weakened, softened, rewritten or removed.

- The **12** regime-B `admissible: false` cells in `STAGE_E1_V36_F6_SCDI.json` and **4** in the calibration receipt,
  all at capability 0.0, stand exactly as recorded.
- `N3_NO_SHARED_SEMANTICS` in `STAGE_E1_V14_E1_CP.json` — nobody admissible — stands, and **gets stronger**. Its
  rows score **0.9167** in regime B against a best constant of **0.9583**: on that cell the machines are *worse than
  a constant*. The receipt recorded them as failing θ; they were also failing the null. The negative deepens.
- `INDEP`, the CP no-sharing control, scores 0.1250 in regime B under `PPLUS` / `N2` against a best constant of
  0.8750 — **far below** the null. Recorded, not softened: the negative twin is not merely uninformative there, it
  is anti-informative, and that was never noticed because no null was ever computed.
- `RV-377-057` / `RV-377-071`'s E3-lite admissibility claims (0.8809 and 0.8796 on `E_smooth8`) **stand**: the best
  constant on `E_smooth8` is 0.6641 / 0.6663, a margin of 4.4 fx units. `E_smooth8_div` is cleaner still at 0.4521.
- `E_alias` (`RV-377-063` / F4) is **clean at all 16 orientations**, best constant 0.5200 – 0.6400, margins of 5.0
  to 7.9 fx units. Every IQL admissibility claim stands.

---

# 9. Full table — 92 rows, both criteria, each under its own metric

Sorted by verdict, then family, ecology and variant. A negative margin means the constant **beats** θ.

| ecology | variant | criterion | n eval | metric | best constant | c | theta | margin (cap) | margin (fx units) | margin (metric quanta) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `e1_scdi`/`E_factored` | regime_B | unseen | 24 | exact equality | **1.0000** | 1 | 0.85 | -0.1500 | -3.600 | -3.600 | NON_DISCRIMINATING |
| `e1_cp`/`E_factored3` | B_N3_independent | unseen | 24 | exact agreement within 0 fx | **0.9583** | 1 | 0.85 | -0.1083 | -2.599 | -2.599 | NON_DISCRIMINATING |
| `e1_cp`/`E_factored3` | B_shared | unseen | 24 | exact agreement within 0 fx | **0.8750** | 1 | 0.85 | -0.0250 | -0.600 | -0.600 | NON_DISCRIMINATING |
| `e1_vlc`/`E_factored` | CQU2_GLOBAL_Q(U=8,cone=1,scope=4) | unseen | 4 | exact agreement within 1 fx | **0.7500** | 47 | 0.85 | +0.1000 | +2.400 | +0.400 | WITHIN_QUANTIZATION |
| `e1_vlc`/`E_factored` | CQU4_GLOBAL_Q(U=8,cone=4,scope=4) | unseen | 4 | exact agreement within 1 fx | **0.7500** | 55 | 0.85 | +0.1000 | +2.400 | +0.400 | WITHIN_QUANTIZATION |
| `blind`/`E_smooth` | registered | unseen | 8 | mean-abs-error capability, cap = max(0, 1 - err/1.5) | **0.8333** | 8 | 0.85 | +0.0167 | +0.401 | +0.401 | WITHIN_QUANTIZATION |
| `e1_iql`/`E_alias` | d=0000 | all | 25 | exact equality | **0.6000** | 1 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0000 | unseen | 25 | exact equality | **0.6000** | 1 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0001 | all | 25 | exact equality | **0.5200** | 0 | 0.85 | +0.3300 | +7.920 | +8.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0001 | unseen | 25 | exact equality | **0.5200** | 0 | 0.85 | +0.3300 | +7.920 | +8.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0010 | all | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0010 | unseen | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0011 | all | 25 | exact equality | **0.5600** | 0 | 0.85 | +0.2900 | +6.960 | +7.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0011 | unseen | 25 | exact equality | **0.5600** | 0 | 0.85 | +0.2900 | +6.960 | +7.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0100 | all | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0100 | unseen | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0101 | all | 25 | exact equality | **0.6400** | 0 | 0.85 | +0.2100 | +5.040 | +5.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0101 | unseen | 25 | exact equality | **0.6400** | 0 | 0.85 | +0.2100 | +5.040 | +5.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0110 | all | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0110 | unseen | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0111 | all | 25 | exact equality | **0.5200** | 0 | 0.85 | +0.3300 | +7.920 | +8.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=0111 | unseen | 25 | exact equality | **0.5200** | 0 | 0.85 | +0.3300 | +7.920 | +8.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1000 | all | 25 | exact equality | **0.5200** | 0 | 0.85 | +0.3300 | +7.920 | +8.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1000 | unseen | 25 | exact equality | **0.5200** | 0 | 0.85 | +0.3300 | +7.920 | +8.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1001 | all | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1001 | unseen | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1010 | all | 25 | exact equality | **0.6400** | 0 | 0.85 | +0.2100 | +5.040 | +5.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1010 | unseen | 25 | exact equality | **0.6400** | 0 | 0.85 | +0.2100 | +5.040 | +5.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1011 | all | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1011 | unseen | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1100 | all | 25 | exact equality | **0.5600** | 0 | 0.85 | +0.2900 | +6.960 | +7.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1100 | unseen | 25 | exact equality | **0.5600** | 0 | 0.85 | +0.2900 | +6.960 | +7.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1101 | all | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1101 | unseen | 25 | exact equality | **0.6000** | 0 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1110 | all | 25 | exact equality | **0.5200** | 0 | 0.85 | +0.3300 | +7.920 | +8.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1110 | unseen | 25 | exact equality | **0.5200** | 0 | 0.85 | +0.3300 | +7.920 | +8.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1111 | all | 25 | exact equality | **0.6000** | 1 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_iql`/`E_alias` | d=1111 | unseen | 25 | exact equality | **0.6000** | 1 | 0.85 | +0.2500 | +6.000 | +6.250 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | CQU1_LOCAL_Q(U=8,cone=1,scope=1) | all | 1024 | exact agreement within 1 fx | **0.2500** | -1 | 0.85 | +0.6000 | +14.400 | +614.400 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | CQU1_LOCAL_Q(U=8,cone=1,scope=1) | unseen | 16 | exact agreement within 1 fx | **0.6250** | 19 | 0.85 | +0.2250 | +5.400 | +3.600 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | CQU2_GLOBAL_Q(U=8,cone=1,scope=4) | all | 256 | exact agreement within 1 fx | **0.1406** | 41 | 0.85 | +0.7094 | +17.026 | +181.606 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | CQU3_LOCAL_Q(U=8,cone=4,scope=1) | all | 1024 | exact agreement within 1 fx | **0.2500** | -1 | 0.85 | +0.6000 | +14.400 | +614.400 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | CQU3_LOCAL_Q(U=8,cone=4,scope=1) | unseen | 16 | exact agreement within 1 fx | **0.5000** | 11 | 0.85 | +0.3500 | +8.400 | +5.600 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | CQU4_GLOBAL_Q(U=8,cone=4,scope=4) | all | 256 | exact agreement within 1 fx | **0.1016** | 39 | 0.85 | +0.7484 | +17.962 | +191.590 | DISCRIMINATING |
| `e1_lineage`/`E_factored` | E_EPHEMERAL(current) | all | 1536 | exact agreement within 1 fx | **0.2500** | 19 | 0.85 | +0.6000 | +14.400 | +921.600 | DISCRIMINATING |
| `e1_lineage`/`E_factored` | E_EPHEMERAL(current) | unseen | 24 | exact agreement within 1 fx | **0.5000** | 23 | 0.85 | +0.3500 | +8.400 | +8.400 | DISCRIMINATING |
| `e1_lmhm`/`E_factored` | HETEROGENEOUS(U=16) | all | 1536 | exact agreement within 1 fx | **0.1667** | 11 | 0.85 | +0.6833 | +16.399 | +1049.549 | DISCRIMINATING |
| `e1_lmhm`/`E_factored` | HETEROGENEOUS(U=16) | unseen | 24 | exact agreement within 1 fx | **0.2917** | 31 | 0.85 | +0.5583 | +13.399 | +13.399 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA000 | all | 1536 | exact agreement within 1 fx | **0.1458** | 13 | 0.85 | +0.7042 | +16.901 | +1081.651 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA000 | unseen | 24 | exact agreement within 1 fx | **0.4167** | 39 | 0.85 | +0.4333 | +10.399 | +10.399 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA025 | all | 1536 | exact agreement within 1 fx | **0.1458** | 13 | 0.85 | +0.7042 | +16.901 | +1081.651 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA025 | unseen | 24 | exact agreement within 1 fx | **0.4167** | 39 | 0.85 | +0.4333 | +10.399 | +10.399 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA050 | all | 1536 | exact agreement within 1 fx | **0.1667** | 19 | 0.85 | +0.6833 | +16.399 | +1049.549 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA050 | unseen | 24 | exact agreement within 1 fx | **0.3750** | 39 | 0.85 | +0.4750 | +11.400 | +11.400 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA075 | all | 1536 | exact agreement within 1 fx | **0.1667** | 19 | 0.85 | +0.6833 | +16.399 | +1049.549 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA075 | unseen | 24 | exact agreement within 1 fx | **0.3750** | 39 | 0.85 | +0.4750 | +11.400 | +11.400 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA100 | all | 1536 | exact agreement within 1 fx | **0.1458** | 13 | 0.85 | +0.7042 | +16.901 | +1081.651 | DISCRIMINATING |
| `e1_vgsc`/`E_factored` | PA100 | unseen | 24 | exact agreement within 1 fx | **0.4167** | 39 | 0.85 | +0.4333 | +10.399 | +10.399 | DISCRIMINATING |
| `e1_lineage`/`E_factored` | P_PERSISTENT_D1(as-of v=7) | all | 1536 | exact agreement within 1 fx | **0.1875** | 19 | 0.85 | +0.6625 | +15.900 | +1017.600 | DISCRIMINATING |
| `e1_lineage`/`E_factored` | P_PERSISTENT_D1(as-of v=7) | unseen | 24 | exact agreement within 1 fx | **0.2500** | 23 | 0.85 | +0.6000 | +14.400 | +14.400 | DISCRIMINATING |
| `e1_lineage`/`E_factored` | P_PERSISTENT_D8(as-of v=0) | all | 1536 | exact agreement within 1 fx | **0.1458** | 13 | 0.85 | +0.7042 | +16.901 | +1081.651 | DISCRIMINATING |
| `e1_lineage`/`E_factored` | P_PERSISTENT_D8(as-of v=0) | unseen | 24 | exact agreement within 1 fx | **0.4167** | 39 | 0.85 | +0.4333 | +10.399 | +10.399 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | RSTAR_T3_T4(U=8,cone=1) | all | 1536 | exact agreement within 1 fx | **0.2500** | 19 | 0.85 | +0.6000 | +14.400 | +921.600 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | RSTAR_T3_T4(U=8,cone=1) | unseen | 24 | exact agreement within 1 fx | **0.5000** | 23 | 0.85 | +0.3500 | +8.400 | +8.400 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | T1_STATIONARY(U=0) | all | 1536 | exact agreement within 1 fx | **0.1458** | 13 | 0.85 | +0.7042 | +16.901 | +1081.651 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | T1_STATIONARY(U=0) | unseen | 24 | exact agreement within 1 fx | **0.4167** | 39 | 0.85 | +0.4333 | +10.399 | +10.399 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | T2_DENSE_CONE(U=8,cone=4) | all | 1536 | exact agreement within 1 fx | **0.1458** | 13 | 0.85 | +0.7042 | +16.901 | +1081.651 | DISCRIMINATING |
| `e1_vlc`/`E_factored` | T2_DENSE_CONE(U=8,cone=4) | unseen | 24 | exact agreement within 1 fx | **0.4167** | 39 | 0.85 | +0.4333 | +10.399 | +10.399 | DISCRIMINATING |
| `e1_scdi`/`E_factored` | regime_A | all | 1536 | exact equality | **0.1458** | 12 | 0.85 | +0.7042 | +16.901 | +1081.651 | DISCRIMINATING |
| `e1_scdi`/`E_factored` | regime_A | unseen | 24 | exact equality | **0.4167** | 40 | 0.85 | +0.4333 | +10.399 | +10.399 | DISCRIMINATING |
| `e1_scdi`/`E_factored` | regime_B | all | 1536 | exact equality | **0.6562** | 1 | 0.85 | +0.1938 | +4.651 | +297.677 | DISCRIMINATING |
| `e1_scdi`/`E_factored` | regime_C | all | 1536 | exact equality | **0.5000** | 0 | 0.85 | +0.3500 | +8.400 | +537.600 | DISCRIMINATING |
| `e1_scdi`/`E_factored` | regime_C | unseen | 24 | exact equality | **0.5417** | 1 | 0.85 | +0.3083 | +7.399 | +7.399 | DISCRIMINATING |
| `e1_scdi`/`E_factored` | regime_D | all | 1536 | exact equality | **0.1458** | 3 | 0.85 | +0.7042 | +16.901 | +1081.651 | DISCRIMINATING |
| `e1_scdi`/`E_factored` | regime_D | unseen | 24 | exact equality | **0.4167** | 10 | 0.85 | +0.4333 | +10.399 | +10.399 | DISCRIMINATING |
| `e1_cp`/`E_factored3` | A_shared | all | 1536 | exact agreement within 1 fx | **0.2500** | 19 | 0.85 | +0.6000 | +14.400 | +921.600 | DISCRIMINATING |
| `e1_cp`/`E_factored3` | A_shared | unseen | 24 | exact agreement within 1 fx | **0.5000** | 23 | 0.85 | +0.3500 | +8.400 | +8.400 | DISCRIMINATING |
| `e1_cp`/`E_factored3` | B_N3_independent | all | 1536 | exact agreement within 0 fx | **0.6771** | 1 | 0.85 | +0.1729 | +4.150 | +265.574 | DISCRIMINATING |
| `e1_cp`/`E_factored3` | B_shared | all | 1536 | exact agreement within 0 fx | **0.7500** | 1 | 0.85 | +0.1000 | +2.400 | +153.600 | DISCRIMINATING |
| `e1_cp`/`E_factored3` | C_N3_independent | all | 1536 | exact agreement within 0 fx | **0.6354** | 0 | 0.85 | +0.2146 | +5.150 | +329.626 | DISCRIMINATING |
| `e1_cp`/`E_factored3` | C_N3_independent | unseen | 24 | exact agreement within 0 fx | **0.6250** | 0 | 0.85 | +0.2250 | +5.400 | +5.400 | DISCRIMINATING |
| `e1_cp`/`E_factored3` | C_shared | all | 1536 | exact agreement within 0 fx | **0.6250** | 0 | 0.85 | +0.2250 | +5.400 | +345.600 | DISCRIMINATING |
| `e1_cp`/`E_factored3` | C_shared | unseen | 24 | exact agreement within 0 fx | **0.7500** | 0 | 0.85 | +0.1000 | +2.400 | +2.400 | DISCRIMINATING |
| `blind`/`E_bind` | registered | all | 4 | label accuracy (served value thresholded at fx(0.5)) | **0.7500** | 9 | 1.0 | +0.2500 | +6.000 | +1.000 | DISCRIMINATING |
| `blind`/`E_bind` | registered | unseen | 4 | label accuracy (served value thresholded at fx(0.5)) | **0.7500** | 9 | 1.0 | +0.2500 | +6.000 | +1.000 | DISCRIMINATING |
| `blind`/`E_bind16` | registered | all | 16 | label accuracy (served value thresholded at fx(0.5)) | **0.5000** | -128 | 1.0 | +0.5000 | +12.000 | +8.000 | DISCRIMINATING |
| `blind`/`E_bind16` | registered | unseen | 16 | label accuracy (served value thresholded at fx(0.5)) | **0.5000** | -128 | 1.0 | +0.5000 | +12.000 | +8.000 | DISCRIMINATING |
| `blind`/`E_smooth` | registered | all | 16 | mean-abs-error capability, cap = max(0, 1 - err/1.5) | **0.7917** | 8 | 0.85 | +0.0583 | +1.399 | +1.399 | DISCRIMINATING |
| `blind`/`E_smooth8` | registered | all | 256 | mean-abs-error capability, cap = max(0, 1 - err/1.5) | **0.6641** | 4 | 0.85 | +0.1859 | +4.462 | +4.462 | DISCRIMINATING |
| `blind`/`E_smooth8` | registered | unseen | 240 | mean-abs-error capability, cap = max(0, 1 - err/1.5) | **0.6663** | 4 | 0.85 | +0.1837 | +4.409 | +4.409 | DISCRIMINATING |
| `blind`/`E_smooth8_div` | registered | all | 256 | mean over 4 declared targets of the mean-abs-error capability | **0.4521** | 2 | 0.85 | +0.3979 | +9.550 | +9.550 | DISCRIMINATING |
| `blind`/`E_smooth8_div` | registered | unseen | 240 | mean over 4 declared targets of the mean-abs-error capability | **0.4521** | 2 | 0.85 | +0.3979 | +9.550 | +9.550 | DISCRIMINATING |

---

# 10. What this closes, and what it does not

**Closed.** DG-9's rule-40 constant-answer control now covers every ecology the corpus executes:

| surface | record | status |
|---|---|---|
| the six registered B1 ecologies + the `E_sym(k)` sweep | `RV-377-101` | 9 of 40 pairs NON_DISCRIMINATING |
| `E_ambig` / `E_noisy` | `RV-377-104` | clean in closed form; best constant exactly 0.0 by construction |
| the **E1** family (41 variants, 7 microscopes) | **this record** | **3 NON_DISCRIMINATING, all regime B** |
| **E3** proper (real mathematics / code) | **this record** | **no executed ecology; no capability metric; no θ; nothing to void** |
| **E3-lite** (neutral-search recovery, 5 ecologies) | **this record** | **all 5 DISCRIMINATING** |

**Not closed, and not to be reported as closed.**

1. **The rule-42 fixed-function null has never been run on any E1 or E3-lite ecology.** Every verdict above is a
   constant-answer verdict only. A machine that reads its input but ignores its feedback — the failure mode rule 42
   exists for — passes everything here untouched. `RV-377-102` built and validated such an extractor for the B1
   layer; nothing equivalent exists for E1 or E3-lite.
2. **A DISCRIMINATING verdict is necessary, not sufficient.** It says a one-number machine cannot clear θ. It says
   nothing about whether a claim on that ecology is otherwise sound.
3. **`e1_scdi`'s regime B needs a new evaluation set, not a new θ.** Raising θ does not help when the obligation is
   literally constant on the evaluated inputs: no threshold discriminates on a constant target. The registered
   evaluation set is all-`(1,1)` patterns by design, for the *exact-sum* regime A where that choice is sound; the
   boolean regime B inherited it and degenerates. Per rule 43, the right repair is a **skill-referenced** metric
   against the base rate, which would have reported these 80 verdicts as **zero skill** the first time they were
   computed — exactly as `dk_precision`'s Brier skill score did for `E_ambig`.
4. The `e1_lineage`, `e1_lmhm`, `e1_vgsc`, `e1_vlc` (scope 1 and 2) and `e1_iql` claims are clean under this control
   and this control alone.

**Ledger effect.** DG-9's remaining surface named by `RV-377-104` is now measured. The gap's closure condition —
"re-adjudicate every admissibility/recovery/occupancy claim taken on [a non-discriminating ecology]" — is
**executed for E1/E3 and returns 116 void verdicts and 166 contaminated occupancy entries**, which is a larger
correction than the B1 layer's and is the point of running it.

---

# 11. Incidental finding, disclosed rather than acted on

`audit()` was re-run unchanged as a control, to confirm this work did not perturb it. It does not reproduce its own
committed receipt byte-for-byte, and the reason is benign but worth recording: `microscopes/results/STAGE_DG9_CONSTANT_CONTROL_V1.json`
carries **40** ecology-criterion pairs, while the current `ecology.REGISTRY` yields **42**. `E_wit1` was added to the
registry by `RV-377-103` *after* `RV-377-101` wrote that receipt.

Regenerating it changes exactly two things: it adds `E_wit1|all` (best constant 0.7500, c = −16) and `E_wit1|unseen`
(0.7083, c = −8), both **DISCRIMINATING**, and it leaves `n_non_discriminating = 9` and every other row identical.
No verdict anywhere moves.

**The stale receipt has been left exactly as committed and was restored after the control run.** Regenerating
another revival record's hashed receipt is that record's business, not this one's. It is noted here so that the
discrepancy is on the record rather than discovered later as a reproduction failure.
