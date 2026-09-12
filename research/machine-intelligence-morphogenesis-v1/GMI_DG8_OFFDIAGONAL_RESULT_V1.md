# DG-8 — the first search off the diagonal of `A × d × p × F`

**Gap:** `DG-8` (`GMI_GAP_LEDGER_EXECUTED_V1.md` §3, `GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` §16.6,
`GMI_DG7_INDEX_AUDIT_V1.md` §5).
**Governed by:** `GMI-DA7` (the four axes and the monotonicity of `K(A, d, p, F)`), `GMI-DA11` (a negative is a claim
about a **region**; monotonicity protects positives and gives negatives nothing), protocol rule 39 (the sweep
obligation applies to every index, and the record names which were swept and which were defaulted), protocol rule 40
(every admissibility claim carries the best-constant control, margins in fx units, one fx unit = `1/(1.5·16)` =
`0.0416667`).

**Freeze commit:** `693ef303a8ac69324f9989d6802e3115e2baf6d0` — the sample, the predictions and the coverage census
were registered **before** anything in §5 was run. Frozen file `GMI_DG8_OFFDIAGONAL_SAMPLE_V1.json`, sha256
`0bdc6769c9ca8335d6b63d877727ea7c3ff7d9c6d1d13c1ac55b2539b212839b`.
**Receipt:** `microscopes/results/STAGE_DG8_OFFDIAGONAL_V1.json`, sha256
`73370b223455c5b52a4d10aee7fd35a2b560601af9f9aa563835c03b0bd0ffb1`.
**Module:** `gmi_microscope/dg8_offdiag.py`.

**Terminal:**

`DG8_OFF_DIAGONAL_SAMPLE_EXECUTED__TRUE_COVERAGE_BEFORE_THE_RUN_541_OF_120960_WITH_ZERO_CELLS_CROSSING_d_OR_p_WITH_ANY_OTHER_AXIS__900_CELL_HALTON_SAMPLE_ALL_EVALUATED__56_ADMISSIBLE_OF_WHICH_50_SIT_ON_A_NON_DISCRIMINATING_ECOLOGY__4_RULE_40_VALID_WITNESSES__RV_377_089_S_E_SYM5_CEILING_FALSIFIED_AS_A_REGION_CLAIM_AT_fx10_ON_A_ROW_INSIDE_ITS_OWN_GRID__E_SMOOTH3_CEILING_SURVIVES_BY_0_0010__55_OF_56_ADMISSIBLE_CELLS_ARE_UNREACHABLE_FROM_THE_DEFAULT_POINT_BY_MOVING_ANY_SINGLE_AXIS__ZERO_INTERVENTION_ROBUST_WITNESSES_ON_THE_FIVE_PRE_E_WIT1_ECOLOGIES__TWO_NEW_INTERVENTION_ROBUST_WITNESSES_ON_E_WIT1_BOTH_OFF_DIAGONAL__TWO_DEFECTS_FOUND_IN_THE_REGISTERED_HARNESS__NO_RED_RESULT_DELETED_OR_WEAKENED`

---

## 1. The lattice, and what "the diagonal" means

`GMI-DA7` §10 indexes the bounded reduction `≼_B` by four declared parameters and writes `K(A, d, p, F)` for the set
of `≼_B`-classes. `GMI-DA7` part 3 proves `K` monotone in all four. `GMI-DA11` then proves the asymmetry that makes
this document necessary: monotonicity carries a **positive** upward from any cell to every refinement, and does
nothing whatever for a **negative**, which is universally quantified over a region and is falsified by a single point
anywhere in it.

Every ladder below is the ladder an executed registered sweep actually used. None is invented for this run.

| axis | ladder | size | provenance |
|---|---|---:|---|
| `A` | `H_GRID × LR_GRID`, `h ∈ {1,2,3,4,6,8,12,16,24,32}`, `lr ∈ {1,2,3,4,6,8,12,16}` | 80 | `gmi_microscope/witness_dg7.py`, the grid `RV-377-089`/`-089b` executed |
| `d` | structure depth `d1`…`d6` | 6 | `RV-377-065`, `STAGE_DK_V1_DEPTH_GATED.json` |
| `p` | `fx8, fx10, fx12, fx16, fx24, fx32, wide` | 7 | `RV-377-076`, `STAGE_DK_V5_PRECISION_RESIDUAL_V1.json` |
| `F` | 6 registered ecologies × 6 registered interventions | 36 | `ecology.REGISTRY` × `ecology.INTERVENTIONS` |

**Total: 80 × 6 × 7 × 36 = 120 960 cells.**

The **registered default point** is

```
A0 = (h = 2, lr = 4)          zoo.gradient_net()'s declared defaults
d0 = 1                        GMI-DA7 section 10: "d = 1 for every executed candidate"
p0 = fx8                      GMI-DA7 section 10: 8-bit fixed point, FRAC_BITS = 4
F0 = (E_smooth1, standard)    the frozen original D'/E' ecology (smooth.COEFFS_V1), registered protocol
```

A cell is **on the diagonal** iff at most **one** coordinate differs from the default — the union of the four one-axis
lines through the default point, which is exactly what the four sweeps covered. **126 cells** are on the diagonal;
**120 834** are off it.

---

## 2. The true coverage before this run

`DG-8`'s wording is "**no cell off the diagonal of `A × d × p × F` has ever been searched**". Measured against the
lattice above, that is *slightly too strong* and the accurate statement is sharper. Census procedure and cells are in
the frozen file under `coverage_before_the_run`; it is reproducible by `dg8_offdiag.coverage_census()`.

| quantity | value |
|---|---|
| lattice cells | **120 960** |
| cells ever evaluated | **541** |
| **true coverage fraction** | **541 / 120 960 = 0.00447255 (0.4473 %)** |
| diagonal cells covered | 84 of 126 (66.67 %) |
| off-diagonal cells covered | 457 of 120 834 (**0.378 %**) |
| off-diagonal coverage by stratum | `AF`: **457**. Every other stratum: **0** |
| distinct `d` ever evaluated anywhere in this lattice | **`{1}`** |
| distinct `p` ever evaluated anywhere in this lattice | **`{fx8}`** |
| off-diagonal cells in which `d` or `p` is off default **together with** anything else | **0** |

Contributing receipts: `STAGE_B1_V31_DG7_COEFFICIENT_WITNESS.json` (265 cells),
`STAGE_B1_V31b_DG7_COEFFICIENT_WITNESS_ALL5.json` (535), `STAGE_ECO_V32_ECO_AXIS.json` (6),
`STAGE_RULE36_INTERVENTION_ADMISSIBILITY_V1.json` (10).

**The corrected statement of the gap.** The corpus *has* searched off the diagonal — 457 cells of it — but every one
of those lies in the `AF` plane at `(d = 1, p = fx8)`. That plane is exactly where `RV-377-089b` found its
off-diagonal witness, which is why the gap was opened. The depth ladder was executed on `E_rolefill` and the
instrument ladder on the `dk_precision` ambiguous/noisy ecologies — **two obligation families that lie outside this
lattice entirely**. Crossed with nothing, they say nothing about it. Before this run, the `d` and `p` axes of this
lattice had been crossed with **no** other axis, at any point, ever. **118 069 of the 120 834 off-diagonal cells lie
in that never-touched region.**

---

## 3. The frozen design

**Construction.** A 4-dimensional Halton sequence in bases 2, 3, 5, 7, indices 1, 2, 3, … in order; coordinate `k` of
point `i` is the radical inverse `φ_b(i)` mapped by `floor(u · |ladder|)` onto the declared ladder order.
Deterministic: no seed, no randomness, no discretion. A point is kept iff it is off the diagonal, affordable, never
previously evaluated (against the frozen 541-cell coverage set), and not already drawn. 900 cells were drawn from
1 287 Halton indices.

**The affordable sub-region.** Charged replay cost is driven by the genotype's declared parameter count
`P(h, d) = 5h + (d−1)·h·(h+1) + (h+1)`, known before a cell is run. The sample is declared over `P ≤ 400`, which
admits **84 546 of the 120 834** off-diagonal cells (**69.97 %**). The complement is **not** sampled and is **not**
spoken about anywhere in this document.

**Hit probability, as `DG-8`'s closure criterion requires.** Sampling is without replacement, so the
with-replacement bound `1 − (1 − μ)^900` is conservative.

| relative measure `μ` of a kingdom-bearing sub-region | cells | hit probability ≥ |
|---|---:|---:|
| 0.1 % | 84 | 0.594 |
| 0.2 % | 169 | 0.835 |
| 0.5 % | 422 | **0.989** |
| 1 % | 845 | 0.9999 |

**Rule 39 index block.** *Swept:* `A` (both `h` and `lr`), `d`, `p`, `F` (both ecology and intervention).
*Held at a default and named as such:* basis column `B0_LOCAL_ADAPTIVE_TRANSDUCERS`, seed 0, 16 development events,
the `unseen` criterion, `θ = 0.85`, and the carrier family itself (the registered coefficient row, generalized in
depth). **No claim in this document extends to those six.**

**Rule 40.** Every verdict carries the best constant for its own `(p, F)` cell, computed exactly (the mean-absolute-
error optimum is a median of the evaluation targets, so scanning the target values attains it at every instrument).
Margins are in **registered** fx units, `0.0416667` of capability, at every instrument — using the instrument's own
finer unit would flatter a witness for being handed more bits, which is the opposite of a control. A cell is a
**valid witness** only if it is admissible **and** its ecology is discriminating at `θ` **and** it beats the best
constant by at least one registered fx unit.

**Self-checks that had to pass before the machinery was trusted** (all four `holds = true`, in the frozen file):

| check | what it asserts |
|---|---|
| `depth1_identity` | `deep_gradient_net(h, lr, 1)` has the **same canonical fingerprint** as `zoo.gradient_net(h, lr)` for all 80 `A`-cells. Raising `d` is composition over the same alphabet; no new kind is introduced. |
| `fx8_identity` | at `fx8` the rebound universe reproduces the unpatched registered one on the **full response signature**, not merely the capability, for all 36 `F`-cells. |
| `constant_control_agreement` | the exact median best constant equals `constant_control.best_constant`'s `fx8` grid scan on all six ecologies. |
| `registered_target_reconstruction` | at `fx8` the instrument-aware target equals the registered target for all six ecologies. |

**Independent cross-validation against the negative under attack.** 30 cells at `(d = 1, fx8, standard)` were
re-evaluated through this module and compared against the capabilities `STAGE_B1_V31b_DG7_COEFFICIENT_WITNESS_ALL5`
recorded for the same rows: **30 of 30 identical to four decimal places**, across all five ecologies, including
`grad_h6_lr4` on `E_sym5` (0.5260 — the row §6.1 turns on) and `grad_h3_lr1` on `E_sym5` (0.8385 —
`RV-377-082`'s reported ceiling). Separately, stage 3 of the run recomputed `grad_h6_lr2` on `E_smooth1` as a shadow
and obtained **0.8906**, `RV-377-082`'s witness, to the digit. This module reproduces the corpus's own numbers
exactly, so the disagreements reported below are disagreements about **region**, not about measurement.

**Disclosed.** 47 cells were executed **before** the freeze to measure the cost of one cell and size the sample, all
at `p = fx12`, `lr = 2`, `F = (E_smooth3, no_revoke)`. They are listed in the frozen file. Predictions C3, C4 and C8
are informed by them, and §7 grades them accordingly.

---

## 4. The frozen predictions

Quoted from the freeze commit. Falsifiers are in the frozen file.

| clause | prediction, as frozen |
|---|---|
| **C2** | the `E_smooth3`/`E_sym5` ceiling **falls** off the diagonal: at least one sampled cell there reaches `θ`. |
| **C3** | median capability at `d ≥ 4` exceeds median at `d = 1`. |
| **C4** | **precision hurts**: mean capability at `fx24/fx32/wide` is below `fx8/fx10`, because the 8-bit instrument's saturation is load-bearing for a deep net. |
| **C5** | DG-8's own premise: some off-diagonal cell is admissible while **every** one of its one-axis shadows is not. |
| **C6** | between 1 and 25 rule-40 valid witnesses on the five pre-`E_wit1` ecologies. |
| **C7** | admissible fraction in `[0.04, 0.22]`. |
| **C8** | the frozen per-cell predictor scores balanced accuracy ≥ 0.70. |

---

## 5. The run

900 of 900 cells evaluated; **0 not reached**; primary stage **1 519.5 s**, follow-up stages **14.1 s**; nothing
skipped for budget.

### 5.1 Scorecard

| clause | measured | verdict |
|---|---|---|
| **C2** | 1 admissible of 298 cells sampled on `E_smooth3`/`E_sym5` | **HOLDS** |
| **C3** | median `d ≥ 4` = **0.72755** (n = 364) vs median `d = 1` = **0.6165** (n = 213) | **HOLDS** |
| **C4** | mean `fx24/fx32/wide` = **0.456877** (n = 383) vs mean `fx8/fx10` = **0.748471** (n = 259) | **HOLDS** |
| **C5** | **55 of 56** admissible cells have every one-axis shadow inadmissible | **HOLDS** |
| **C6** | **2** valid witnesses on the five pre-`E_wit1` ecologies (predicted 1–25) | **HOLDS** |
| **C7** | 56 admissible of 900 = **0.062222** (predicted 0.04–0.22) | **HOLDS** |
| **C8** | balanced accuracy **0.7475** (TPR 0.9643, TNR 0.5308, TP 54 / FP 396 / TN 448 / FN 2) | **HOLDS** |

### 5.2 What "admissible" is worth here, before anything else is said

Of the **56 admissible cells, 50 sit on `E_sym3`**, whose best constant is **0.8750 — above `θ`**. On that ecology a
machine that ignores its input and its feedback is admissible, so admissibility there certifies nothing. This is
`DG-9`'s point, and rule 40 is what keeps it from contaminating this record.

| | count |
|---|---:|
| admissible cells | 56 |
| …on a **non-discriminating** ecology (a constant also clears `θ`) | **50** |
| …on a **discriminating** ecology | 6 |
| …**rule-40 valid witnesses** (admissible + discriminating + margin ≥ 1 registered fx unit) | **4** |
| …of those, **intervention-robust** under all six (stage 2) | **2**, both on `E_wit1` |
| …intervention-robust on one of the **five pre-`E_wit1`** ecologies | **0** |

### 5.3 By axis

| depth `d` | cells | admissible | mean capability | best |
|---|---:|---:|---:|---:|
| 1 | 213 | 6 | 0.5522 | 0.9115 |
| 2 | 170 | 10 | 0.5743 | 0.8815 |
| 3 | 153 | 13 | 0.6227 | 0.8750 |
| 4 | 128 | 6 | 0.6077 | 0.8854 |
| 5 | 130 | 15 | 0.6672 | 0.8750 |
| 6 | 106 | 6 | 0.7005 | 0.8880 |

| instrument `p` | cells | admissible | mean capability | best |
|---|---:|---:|---:|---:|
| `fx8` | 129 | 13 | **0.7510** | 0.9115 |
| `fx10` | 130 | 11 | 0.7460 | 0.8880 |
| `fx12` | 126 | 14 | 0.7352 | 0.8893 |
| `fx16` | 132 | 8 | 0.6653 | 0.8750 |
| `fx24` | 125 | 3 | 0.5042 | 0.8750 |
| `fx32` | 132 | 3 | 0.4313 | 0.8783 |
| `wide` | 126 | 4 | **0.4368** | 0.8750 |

| ecology | cells | admissible | mean | best | best constant |
|---|---:|---:|---:|---:|---:|
| `E_smooth1` | 151 | 1 | 0.6225 | 0.8646 | 0.8333 |
| `E_smooth3` | 151 | **0** | 0.6495 | 0.8490 | 0.8125 |
| `E_sym3` | 150 | 50 | 0.6768 | 0.9115 | **0.8750 (non-discriminating)** |
| `E_sym5` | 147 | 1 | 0.6067 | 0.8698 | 0.7917 |
| `E_parity` | 149 | 2 | 0.6392 | 0.8893 | 0.8333 |
| `E_wit1` | 152 | 2 | 0.4688 | 0.8711 | 0.7083 |

| intervention | cells | admissible | mean | best |
|---|---:|---:|---:|---:|
| `standard` | 151 | 12 | 0.6094 | 0.8815 |
| `no_revoke` | 145 | 6 | 0.5940 | 0.8750 |
| `double_revoke` | 152 | 4 | 0.6052 | 0.8750 |
| `half_events` | 149 | 7 | 0.5841 | 0.9115 |
| `shuffled_events` | 151 | 14 | 0.6352 | 0.8958 |
| `extra_unseen_feedback` | 152 | 13 | 0.6329 | 0.8893 |

### 5.4 By stratum (which coordinates are off default)

| stratum | cells | admissible | valid witnesses | best capability |
|---|---:|---:|---:|---:|
| `AF` | 27 | 3 | 0 | 0.9115 |
| `Ad` | 4 | 0 | 0 | 0.7500 |
| `Ap` | 5 | 0 | 0 | 0.7293 |
| `dF` | 2 | 0 | 0 | 0.8021 |
| `pF` | 3 | 0 | 0 | 0.6976 |
| `AdF` | 96 | 10 | 0 | 0.8750 |
| `Adp` | 17 | 0 | 0 | 0.8055 |
| `ApF` | 178 | 3 | **3** | 0.8893 |
| `dpF` | 11 | 0 | 0 | 0.8229 |
| `AdpF` | 557 | 40 | **1** | 0.8880 |

---

## 6. The falsifications, recorded verbatim

### 6.1 `RV-377-089`'s ceiling on `E_sym5` — **FALSIFIED as a region claim**

The negative, quoted from `REVIVAL_LEDGER.jsonl`, record `RV-377-089`, and **left standing**:

> `RV_377_082_S_CEILING_IS_CONFIRMED_AND_PROPERLY_SWEPT__NO_COEFFICIENT_WITNESS_ON_E_SMOOTH3_OR_E_SYM5_OVER_80_ROWS_TO_H_32__…`

and its `claim_movement`:

> "RV-377-082's CEILING on E_smooth3 and E_sym5 moves from an unswept assertion to PROVED_AT_SCOPE over 80 rows to
> h = 32 — the first DG-7 audit CONFIRMS its target rather than overturning it, which is the outcome that makes the
> audit credible."

**The contradicting cell, verbatim from the receipt:**

| A = (h, lr) | d | p | ecology | intervention | capability | best constant | margin (registered fx units) | separates | stratum |
|---|---:|---|---|---|---:|---:|---:|---|---|
| **(6, 4)** | 1 | **`fx10`** | `E_sym5` | `extra_unseen_feedback` | **0.8698** | 0.7917 | **+1.874** | yes | `ApF` |

`h = 6` is **inside** `RV-377-082`'s own width grid `(1, 2, 3, 4, 6, 8)` and `lr = 4` is the zoo default. This is not
a row the sweep missed. It is a row the sweep **evaluated and found inadmissible** — this module reproduces its
recorded `fx8` value, `0.5260`, exactly — and which clears `θ` when the arithmetic instrument moves by **two bits**.

**The control does not move with the instrument.** Across the run, the best constant is **identical at all seven
instruments for all six ecologies — 42 of 42 `(ecology, instrument)` pairs**: `E_smooth1` 0.8333, `E_smooth3`
0.8125, `E_sym3` 0.8750, `E_sym5` 0.7917, `E_parity` 0.8333, `E_wit1` 0.7083. These targets are exactly
representable at every instrument, so the rule-40 bar does not shift underneath the comparison. **The margin gained
in this cell is gained by the machine, not by the yardstick.**

**Scope now explicitly narrowed, without deleting anything.** `RV-377-089`'s 80 measured rows stand exactly as
measured. What falls is the unstated quantifier. The entitled wording is:

> No coefficient witness on `E_smooth3` or `E_sym5` over 80 rows to `h = 32`, **at structure depth `d = 1` and at the
> registered 8-bit instrument `fx8`, under the standard intervention and under the six-intervention family for rows
> clearing `θ` under standard.** Off that pair of defaults the claim is not established, and on `E_sym5` at `fx10` it
> is false.

### 6.2 `E_smooth3`'s ceiling — **UPHELD, by 0.0010**

**0 of 151** sampled cells on `E_smooth3` reach `θ`. The best is `(6, 16)`, `d = 1`, `fx12`,
`extra_unseen_feedback`: **0.8490**, short of `θ = 0.85` by **0.0010**, which is **0.024 registered fx units** —
about a fortieth of one quantization step.

| A | d | p | intervention | capability | vs θ | margin (fx units) | stratum |
|---|---:|---|---|---:|---:|---:|---|
| (6, 16) | 1 | `fx12` | `extra_unseen_feedback` | 0.8490 | −0.0010 | +0.876 | `ApF` |
| (4, 2) | 2 | `fx8` | `half_events` | 0.8333 | −0.0167 | +0.499 | `AdF` |
| (4, 2) | 5 | `fx16` | `extra_unseen_feedback` | 0.8236 | −0.0264 | +0.266 | `AdpF` |
| (8, 1) | 5 | `fx8` | `extra_unseen_feedback` | 0.8229 | −0.0271 | +0.250 | `AdF` |

A ceiling upheld to within one part in eight hundred is not a comfortable ceiling, but it is upheld, and it is
recorded as upheld. **A rule that only ever overturns measures nothing.**

### 6.3 `RV-377-102`'s five-ecology fragility — **NOT falsified**

The invariant, quoted and left standing:

> "INTERVENTION-ROBUSTNESS OF AN APPROXIMATE CARRIER IS A PROPERTY OF THE (CARRIER, ECOLOGY) PAIR, NOT OF THE
> CARRIER. The coefficient carrier is fragile on all five registered ecologies and robust with margin on at least 200
> others drawn from the same declared grid."

Two off-diagonal cells are rule-40 valid witnesses on a pre-`E_wit1` ecology under their own sampled intervention:

| A | d | p | ecology | intervention | capability | best constant | margin |
|---|---:|---|---|---|---:|---:|---:|
| (6, 4) | 1 | `fx10` | `E_sym5` | `extra_unseen_feedback` | 0.8698 | 0.7917 | +1.874 |
| (24, 12) | 1 | `fx12` | `E_parity` | `extra_unseen_feedback` | 0.8893 | 0.8333 | +1.344 |

Stage 2 charged the **full six-intervention family** on both. **Neither survives.**

| A | d | p | ecology | min over six | admissible under all six | margin of the min |
|---|---:|---|---|---:|---|---:|
| (6, 4) | 1 | `fx10` | `E_sym5` | 0.7396 | **no** | −1.250 |
| (24, 12) | 1 | `fx12` | `E_parity` | 0.6328 | **no** | −4.812 |

`RV-377-102`'s invariant therefore **stands**, off the diagonal as well as on it: **0 of 900 sampled off-diagonal
cells is an intervention-robust rule-40 valid witness on any of the five registered ecologies.** The fragility claim
was searched on the diagonal and this run extends it, rather than breaking it.

### 6.4 Two new intervention-robust witnesses on `E_wit1`, both off the diagonal

| A | d | p | ecology | sampled intervention | capability | min over six | all six | margin of the min |
|---|---:|---|---|---|---:|---:|---|---:|
| (4, 2) | **3** | `fx12` | `E_wit1` | `standard` | 0.8711 | **0.8555** | **YES** | **+3.533** |
| (16, 12) | 1 | `fx16` | `E_wit1` | `shuffled_events` | 0.8708 | **0.8584** | **YES** | **+3.600** |

These falsify nothing — `E_wit1` was constructed by `RV-377-102` precisely because witnesses live there — but both
are **product-effect** cells (§6.5), and both **vanish at the defaults**: collapsed to `(d = 1, fx8)` they score
**0.2500** and **0.7083** respectively. The second is exactly the best constant, i.e. no separation at all.

### 6.5 The product effect — DG-8's own premise, executed

For every admissible cell, stage 3 evaluated its **one-axis shadows**: the diagonal cells that keep one off-default
coordinate and return the other three to their registered defaults. **62 distinct diagonal shadow cells were
evaluated; exactly 1 of them is admissible.**

> **55 of 56 admissible off-diagonal cells are unreachable from the default point by moving any single axis.**

The single exception is instructive and is recorded in full: `(6, 2)`, `d = 5`, `fx12`, `E_sym3, double_revoke`
= 0.8659, whose `A`-shadow `(6, 2)`, `d = 1`, `fx8`, `E_smooth1, standard` = **0.8906** *is* admissible — and that
shadow is `RV-377-082`'s own witness, recovered here independently.

Four product-effect cells are rule-40 valid witnesses:

| A | d | p | ecology | intervention | capability | margin | shadows (all inadmissible) |
|---|---:|---|---|---|---:|---:|---|
| (6, 4) | 1 | `fx10` | `E_sym5` | `extra_unseen_feedback` | 0.8698 | +1.874 | A 0.7812 · p 0.6276 · F 0.7500 |
| (24, 12) | 1 | `fx12` | `E_parity` | `extra_unseen_feedback` | 0.8893 | +1.344 | A 0.7188 · p 0.6185 · F 0.7552 |
| (4, 2) | 3 | `fx12` | `E_wit1` | `standard` | 0.8711 | +3.907 | A 0.7812 · d 0.7917 · p 0.6185 · F 0.6562 |
| (16, 12) | 1 | `fx16` | `E_wit1` | `shuffled_events` | 0.8708 | +3.900 | A 0.7188 · p 0.6156 · F 0.6875 |

This is the `RV-377-089b` pattern reproduced **deliberately** rather than by accident, and on three axes rather than
two.

---

## 7. The post-freeze controls, disclosed

These were **not** in the freeze. Every one was chosen to **weaken** this run's headline. All are reported.
Receipt: `microscopes/results/STAGE_DG8_OFFDIAGONAL_CONTROLS_V1.json`, sha256 `4ba09da19943b320…`; reproducible with
`python3 -m gmi_microscope.dg8_offdiag controls`.

### 7.1 Is the instrument doing the work, or the intervention?

| A | d | p | ecology | intervention | capability | admissible |
|---|---:|---|---|---|---:|---|
| (6, 4) | 1 | `fx10` | `E_sym5` | `extra_unseen_feedback` | **0.8698** | **yes** — the C2 falsifier |
| (6, 4) | 1 | **`fx8`** | `E_sym5` | `extra_unseen_feedback` | 0.8021 | no |
| (6, 4) | 1 | `fx10` | `E_sym5` | **`standard`** | 0.8411 | no |
| (6, 4) | 1 | **`fx8`** | `E_sym5` | **`standard`** | **0.5260** | no — `RV-377-089`'s own region |
| (24, 12) | 1 | `fx12` | `E_parity` | `extra_unseen_feedback` | **0.8893** | **yes** |
| (24, 12) | 1 | **`fx8`** | `E_parity` | `extra_unseen_feedback` | 0.8229 | no |
| (24, 12) | 1 | `fx12` | `E_parity` | **`standard`** | 0.7812 | no |
| (24, 12) | 1 | **`fx8`** | `E_parity` | **`standard`** | 0.7292 | no |

**Neither coordinate alone suffices, for either cell.** The instrument carries `+0.0677` on the first cell and
`+0.0664` on the second; the intervention carries `+0.0287` and `+0.1081`. Both are needed to cross `θ`. This is a
genuine two-coordinate product effect, not a relabelled one-axis effect.

One further control, reported because it cuts the other way: at `(24, 12)`, `d = 1`, **`fx8`**, `E_parity` under
`shuffled_events` the row scores **0.8542**, which clears `θ` at the *default* instrument. It is **not** a valid
witness — the best constant there is 0.8333, so the margin is `+0.501` fx units, below the rule-40 bar of one — but
it shows that `E_parity`'s `θ` is crossable on the diagonal-adjacent `AF` plane and that §6.3's `E_parity` entry owes
its *rule-40* status, not its bare admissibility, to the instrument.

### 7.2 A leak in the registered intervention, and what it does to §6.1

`extra_unseen_feedback` feeds the machine the true labels of `smooth.UNSEEN[:4] = [1, 2, 4, 7]`. The `unseen`
criterion scores on `smooth.UNSEEN = [1, 2, 4, 7, 8, 11, 13, 14]`. **Four of the eight inputs the capability is
scored on are handed to the machine as training data by the intervention itself.** This is a property of the
registered intervention family, not of this run; it means **every** single-intervention admissibility number taken
under `extra_unseen_feedback` anywhere in this corpus is scored half on inputs it was just trained on.

That weakens §6.1 as stated. The full `fx10` intervention family for the same cell repairs it:

| intervention | capability at `fx8` | capability at `fx10` |
|---|---:|---:|
| `standard` | 0.5260 | 0.8411 |
| `no_revoke` | 0.7656 | **0.8542 — admissible, margin +1.500, no leak** |
| `double_revoke` | 0.5677 | 0.7917 |
| `half_events` | 0.6771 | 0.7943 |
| `shuffled_events` | 0.7604 | 0.7396 |
| `extra_unseen_feedback` | 0.8021 | **0.8698 — admissible, margin +1.874, leaking** |

`no_revoke` involves **no leak of any kind** and clears `θ` at `fx10` with a **1.500 fx-unit** margin over the best
constant, while scoring **0.7656** at `fx8`. §6.1 therefore stands on a leak-free intervention, and stands **more
strongly** than the frozen sample alone showed: at `fx10` the coefficient carrier clears `θ` on `E_sym5` under **two**
of the six registered interventions, one of them clean, and reaches 0.8411 under `standard`.

---

## 8. Two defects found in the registered harness, neither repaired

### 8.1 `ecology.REGISTRY["E_parity"]` is not a parity target

`ecology.spec_table` is called with the **dict** returned by `smooth.make_parity_target()` and stores
`[int(v) for v in table]`, which iterates the dict's **keys**. The stored table is the identity list `0..15`, so
`ecology.target_of` returns `{x: x}`. **Every claim taken on `E_parity` through the registry is a claim about the
binary-weighted linear target `y = x/16`, not about parity.**

Confirmed independently by a receipt that predates this work: `STAGE_DG9_CONSTANT_CONTROL_V1` reports `E_parity`'s
best constant as **0.8333**, which is the identity target's value on the unseen set. The true parity target's best
constant on that set is **1.0**, because all eight unseen inputs have odd parity — i.e. a genuinely parity-targeted
`E_parity` would be **non-discriminating**, and the corpus has been recording it as discriminating.

`smooth.py`'s own parity runs are unaffected: they pass `make_parity_target()` straight to `smooth.main` and never go
through the registry. **Nothing is repaired here.** Repairing it would change what `E_parity` means and make these
cells incomparable with every prior claim on that name. This run reproduces the registered semantics exactly
(asserted by `registered_target_reconstruction_check`, and by the 30-of-30 cross-validation in §3) and records the
defect. The `E_parity` valid witness in §6.3 is therefore a witness on `y = x/16`.

### 8.2 `extra_unseen_feedback` leaks half the evaluation set

See §7.2. Recorded, not repaired.

---

## 9. What this does **not** establish

* **It is not a kingdom claim.** Nothing here exhibits a carrier that resists bounded reduction. `GMI-DA7`'s
  monotonicity theorem is **untouched** — it is proved, not measured. What this run measures is that *admissibility
  verdicts recorded on the diagonal do not transport off it*, which is `GMI-DA11`'s point and not `GMI-DA7`'s.
* **One carrier family only.** The registered coefficient row, generalized in depth. Nothing is claimed about the
  memory, program, search or population carriers.
* **One basis column, one seed, 16 events, the `unseen` criterion, `θ = 0.85`.** Named in §3 as defaults; not
  searched.
* **30 % of the off-diagonal region was never eligible.** The affordability bound `P ≤ 400` excludes 36 288 of the
  120 834 off-diagonal cells. Those are **unsearched**, not negative.
* **`d` and `p` are not refinements of a fixed genotype.** `GMI-DA7` part 3 says raising `p` can only *add classes* —
  a statement about the expressible set. It does **not** say a fixed genotype's capability is monotone in `p`, and
  §5.3 shows it emphatically is not: mean capability falls from 0.7510 at `fx8` to 0.4368 at `wide`. The same
  genotype at a wider instrument is a **different machine**, because the registered 8-bit universe's saturation is
  part of its semantics and is doing real work for a deep net. Any future reading of "raise `p` and the domain should
  become non-empty" (`GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` §10b) must be read as being about **re-searching** at the
  wider instrument, not about carrying an existing row up to it.

## 10. Grading the predictions honestly

Seven of seven scored clauses held, which is a suspicious-looking record and is graded here rather than celebrated.

| clause | how risky it actually was |
|---|---|
| **C2** | **genuinely risky.** Decided by **1 cell out of 298**, and that cell needed both an off-default instrument and an off-default intervention. Had the Halton sequence not placed a point at `(6, 4) × fx10 × (E_sym5, extra_unseen_feedback)`, C2 would have failed. |
| **C5** | **genuinely risky** in form, but the measured result (55 of 56) is so lopsided that the real information is in the *margin*, not the verdict: the diagonal is nearly barren — 1 admissible cell in 62. |
| **C3** | **cheap.** The pre-freeze cost grid already showed `d = 1` worst at almost every `h`. Disclosed at freeze time. |
| **C4** | **cheap.** The pre-freeze probe already showed capability 0.0000 at `fx32`/`wide` where `fx8` gave 0.8073. Disclosed at freeze time. The *size* of the effect (0.7485 → 0.4569) was not known. |
| **C6** | **weak.** The interval `[1, 25]` spans a factor of 25 and the outcome (2) sits near its floor. |
| **C7** | **weak.** The interval `[0.04, 0.22]` spans a factor of 5.5. |
| **C8** | **weak, and barely cleared.** 0.7475 against a 0.70 threshold, with TNR of only 0.5308 and 396 false positives. The predictor is good at finding admissible cells (TPR 0.9643) and near-useless at excluding them. |

The honest summary: **C2 and C5 carried the record; C3 and C4 were informed by disclosed pre-freeze measurements;
C6, C7 and C8 were set loose enough that passing them says little.**

## 11. What stands unchanged

No RED or negative result has been deleted, weakened or rewritten by this run. Specifically:

* `RV-377-082`'s and `RV-377-089`'s **measured points stand exactly as measured** — reproduced here to four decimal
  places, 30 of 30.
* `RV-377-089`'s ceiling on **`E_smooth3` is upheld** over 151 additional off-diagonal cells.
* `RV-377-102`'s **five-ecology fragility invariant is upheld** over 900 additional off-diagonal cells: zero
  intervention-robust rule-40 valid witnesses on any of the five.
* `GMI-DA7` parts 1–3 are untouched; they are proved, not measured.
* `DG-9`'s point is corroborated hard: **50 of 56** admissible cells in this sample sit on a non-discriminating
  ecology and would have been counted as evidence without the rule-40 control.

The single narrowing is §6.1, and it narrows **wording**, not measurement.

## 12. What `DG-8` still needs

1. The remaining **98.85 %** of the off-diagonal region. Counting the 900 sampled cells, the 62 distinct diagonal
   shadow cells, the stage-2 intervention families and the 10 post-freeze controls, this work adds **953 cells** that
   had never been evaluated. Coverage moves from **541 / 120 960 (0.4473 %)** to **1 494 / 120 960 (1.2351 %)** of
   the lattice, and off-diagonal coverage from **457 / 120 834 (0.378 %)** to **1 389 / 120 834 (1.1495 %)**. The
   number of off-diagonal cells in which `d` or `p` is off default together with anything else moves from **0** to
   **893**, and the off-diagonal strata reached move from `{AF}` alone to all ten:

   | stratum | `AF` | `Ad` | `Ap` | `dF` | `pF` | `AdF` | `Adp` | `ApF` | `dpF` | `AdpF` |
   |---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
   | before | 457 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
   | after | 496 | 4 | 5 | 2 | 3 | 96 | 17 | 193 | 11 | 562 |
2. The **36 288 unaffordable cells** (`P > 400`), which include every deep wide net — precisely where the depth trend
   of §5.3 points.
3. The **other carriers**. This lattice was searched with one carrier family. The memory, program, search and
   population carriers each have their own `A`-parameter family and have never been crossed with `d` or `p` at all.
4. A decision on the two defects in §8. Both change the meaning of existing receipts and neither can be repaired
   without re-adjudicating every claim that used them.
