# RV-377-140 — FREEZE: K4 revived at the carrier-class level

Frozen BEFORE the fresh runs. Outcomes appended only. Every threshold in this document is also
fixed in `gmi_microscope/class_rate.py` and is not changed after any outcome.

## 1. The negative being revived, and what it does and does not say

`F1` of the boundary theorem, sharpened by `RV-377-120` and `RV-377-121`: cost-minimising neutral
search over the typed IR does **not** converge on GMI's predicted 10-axis property vectors —
0 of 264 cells, invariant under a tenfold budget, and cross-seed agreement **0.0 %** at 20 000,
100 000 and 500 000 evaluations. "Which genotype / property vector arises" is not a function of
its inputs, so it is not a well-posed prediction target (`K4_SELECTION_PRINCIPLE_CAN_BE_PREDICTIVE`
= FALSE).

Two things survive that negative, and both are on record rather than hoped for:

* **T5** — the carrier **class** of a behaviourally non-trivial machine is observable from its
  behaviour: 12 / 12 signatures map to exactly one carrier (`RV-377-116`).
* the class-level **recovery rates** have followed the same ordering in every record since
  `RV-377-058`: the memory class recovered in essentially every run, the program/search class
  sometimes, the coefficient class rarely — and only where a witness exists and the fixed-point
  precision permits it (`RV-377-058`, `-074`, `-083`, `-086`, `-100`, `-103`, `-113`).

## 2. Diagnosis — one stage

Per the #373 revival protocol: diagnose → attribute to ONE stage → minimal justified change →
freeze the new prediction → fresh test.

**Attribution.** The failure of K4 is in the **object predicted**, not in the search, the
grammar, the budget, the ecology or the descriptor — each of those was varied in turn
(`RV-377-058` grammar, `-083` ecology, `-087` descriptor, `-102/-103` exposure, `-109` budget ×10,
`-121` budget ×25) and the verdict never moved. The property vector is a point in a large cheap
region that the search samples at random; the carrier class is the label that region *does*
determine.

**Minimal justified change.** Move the predicted object from the property vector to the
**carrier-class recovery-rate ordering as a function of the ecology's coordinates**. Nothing else
changes: same search (`gmi_microscope.b1`), same grammar, same VM, same interventions, same
θ = 0.85, same 20 000 charged evaluations, same three seeds, same rule-36 / 40 / 32 / 23 / 41
reading.

## 3. The class reading (the instrument)

`gmi_microscope/class_rate.py :: rescore_receipt`. For every carrier elite of a B1 receipt that
is admissible under the standard intervention:

| control | applied as |
|---|---|
| rule 36 | all six registered interventions on the **raw** elite, via `ecology.run_genotype`; the elite counts only if the minimum ≥ θ |
| rule 40 | the minimum over six must beat the ecology's best constant (full fx grid, `eco_axis.best_constant`) by ≥ **1.0 fx unit** of mean absolute error |
| rule 32 | atrophy under **every** intervention (`atrophy_ir.prune_all_interventions`), a deletion accepted only if capability stays ≥ θ under all six |
| rule 23 | the **class label is the carrier of the atrophied genotype** (`b1.carrier_of` on the pruned graph) |
| rule 41 | a survival at zero deletions is recorded `LOAD_BEARING_UNTESTED`; its label is still the (unchanged) carrier |

The **recovered class set** of a run = { atrophied carrier of every elite that clears rules 36 and
40 } \ {NONE}. The memory class is `TABLE ∪ KVSTORE`; the program class is `PROGRAM`; the
coefficient class is `DENSE`. Rates are counted per ecology over seeds.

The reading is applied **uniformly** to every committed B1 receipt on a discriminating ecology
(`STAGE_B1_V33_B1_IR_RECOVERY_E_*`, `STAGE_B1_V42_B1_WITNESS_E_wit1_*`, and the `RV-377-110`
seed-0 baselines `STAGE_B1_ABL_FULL_E_*`) and later to the fresh receipts, so the existing and
the fresh rates are read by one instrument. `E_sym3` is excluded under rule 40 (best constant
0.8750 ≥ θ). Receipt: `STAGE_CLASSRATE_V43_CLASSRATE_DIAG.json`.

## 4. The theory's inputs — closed forms, no search

`gmi_microscope/class_rate.py :: closed_forms`, computed for an ecology **before** any search on
it.

* **Memory.** The theory's own closed forms (`RV-377-059/060/062`): exemplar memory
  cap_S5 = 1 − |k|/12, generalizing memory cap_S5h = (48 − |k|)/48 on the symmetric family. Written
  out for an arbitrary coefficient vector under the registered standard protocol
  (`closed_form_S5`, `closed_form_S5h`: the exemplar table serves 0 on every unseen key; the
  Hamming-1 neighbour average is taken over the four seen neighbours of every unseen key with
  the registered arithmetic-shift averaging). `closed_form_check` verifies the identity with the
  symmetric formulas at k = ±2, ±4, ±6, ±8 exactly — and shows that the IR zoo row
  `hamming_knn_k3` (a k = 3 nearest machine) is **not** that closed form, which is why the analytic
  form and not a replayed zoo row is the law's input. **A_mem(c) = max(cap_S5, cap_S5h).**
* **Program / search.** The registered exact-search row `program_search` (S2a) replayed under all
  six interventions; the obligation is **exact** iff its standard capability is 1.0 (every
  coefficient representable in the S2 grammar {−1, −½, −¼, 0, ¼, ½, 1}).
* **Coefficient.** `RV-377-102`'s hand-built witness scan: `gradient_net(h, lr)` over
  H_GRID × LR_GRID, all six interventions, margin over the best constant in fx units. The
  ecology is **witness-bearing** iff some row clears θ under all six with margin ≥ **1.5 fx**
  (the `E_sym5 | DENSE` margin of `RV-377-113`, the smallest margin any rule-36 coefficient
  recovery in the corpus has had).
* **Best constant** (rule 40) over the full fx grid on the unseen set.

**Resolution.** One fx unit of mean absolute error (1/(1.5·16) = 0.041667 capability) is the
smallest separation the 8-bit instrument can assert (rule 40). A closed form within one fx unit
of θ is therefore *at the quantization floor* and the law **abstains** there, exactly as
`RV-377-059` abstained on the one cell its inputs could not fix. This band is fixed before any
fresh ecology is chosen.

## 5. The law — CRML-1 (class-rate morphology law)

For an ecology with coefficient vector c, best constant bc(c) < θ, three seeds of the B1 search
at 20 000 charged evaluations, read by §3:

> **M (memory).** If A_mem(c) ≥ θ + 1 fx **and** A_mem(c) − bc(c) ≥ 1 fx, the memory class is
> recovered on **≥ 2 of 3** seeds. If A_mem(c) < θ, the memory class is recovered on **≤ 1 of 3**
> seeds. Within one fx unit above θ the law abstains.
>
> **C (coefficient).** Where the ecology is **not** witness-bearing, the coefficient class is
> recovered on **≤ 1 of 3** seeds. Where it is witness-bearing the law predicts no upper bound
> (the class is *permitted*, not promised: `RV-377-103` recovered a coefficient carrier on the
> witness-bearing `E_wit1` that failed rule 36, so the witness confers exposure, not robustness).
>
> **P (program / search).** The program class is recovered on **≤ 1 of 3** seeds on every
> ecology (it is the rarest rule-36-robust class in the record), and on **0 of 3** where the
> exact-search row is itself not rule-36 admissible with a ≥ 1 fx margin.
>
> **O (ordering).** On every ecology where M predicts the memory class present,
> rate(memory) ≥ rate(program) ≥ rate(coefficient) unless the ecology is witness-bearing.

The clauses are written against the existing rates in §7 **before** any fresh ecology is
selected, and are not edited after the fresh outcomes.

## 6. The fresh ecologies — deterministic choice

`gmi_microscope/class_rate.py :: select_fresh(4)`. Walk `RV-377-102`'s discriminating
enumeration (itertools.product over the registered coefficient grid, best constant < θ) in
canonical order; skip every coefficient vector ever B1-searched (`E_wit1`, `E_smooth1`,
`E_smooth3`; `E_sym5` / `E_sym3` are not on the grid and `E_parity` is a table). Add a cell iff it
satisfies at least one of four coverage conditions not yet covered by the chosen set —
**witness-bearing**, **witness-free** (no gradient row clears θ under all six),
**memory-predicted-present**, **memory-predicted-absent** — or every condition is already covered;
stop at four. Every cell examined is written to `STAGE_CLASSRATE_SELECTION_V43_CLASSRATE_SELECT.json`
with its closed forms, so the choice is auditable and could not be steered by a search result.

The chosen ecologies are registered in `ecology.REGISTRY` as `E_cr1..E_cr4` before the run, in
this same commit.

## 7. Existing rates under the class reading (the diagnosis)

`STAGE_CLASSRATE_V43_CLASSRATE_DIAG.json` (sha `11b9c1df…`, 3 439 s on laptop billy, 16 receipts,
every elite replays bit-identically to its committed capability). Per ecology, three seeds of
the primary runs (`V33` / `V42`); the `RV-377-110` seed-0 baselines agree cell for cell with the
`V33` seed-0 receipts and are reported beside them in the receipt.

| ecology | coeffs | bc | A_mem (S5 / S5h) | M says | memory | program | coefficient | classes by seed |
|---|---|---|---|---|---|---|---|---|
| `E_smooth1` | (¼, ½, −¼, ½) | 0.8333 | 0.9167 (0.625 / 0.9167), +1.6 fx over θ, +2.0 fx over bc | present | **0/3** | 0/3 | 0/3 | — / — / — |
| `E_smooth3` | (½, ¼, −½, ⅜) | 0.8125 | 0.9062, +1.35 / +2.25 | present | **2/3** | 1/3 | 0/3 | {KV, TABLE} / {KV, PROGRAM, TABLE} / — |
| `E_sym5` | (5/16)×4 | 0.7917 | 0.8958, +1.1 / +2.5 | present | **3/3** | 0/3 | 0/3 | {KV, TABLE} ×3 |
| `E_wit1` | (−½, −½, −½, −¼) | 0.7083 | 0.8542, +0.1 / +3.5 | **abstain** | 1/3 | 1/3 | 0/3 | — / {KV, TABLE} / {PROGRAM} |

Program-search closed form: `E_smooth1` 1.0 (exact), `E_smooth3` 0.9583, `E_sym5` 0.9375,
`E_wit1` 1.0 (exact) — admissible with margin on all four. Hand-built coefficient witness:
none on `E_smooth1` / `E_smooth3` / `E_sym5` (best rows 0.8281 / 0.8073 / 0.8333 under six);
`E_wit1` witness-bearing (0.8646, 3.751 fx).

**What the reading changes.**

* **The coefficient class is 0 of 12 on the atrophied reading.** Every DENSE-labelled elite
  that clears rule 36 loses its DENSE node(s) under rule-32 atrophy at no capability cost and
  reads TABLE or PROGRAM: `E_sym5` S0 (one deletion, `DENSE`, min over six unchanged at 0.8542),
  S1 (ten deletions → TABLE), S2 (eighteen → TABLE); `E_smooth3` S1 (eleven → PROGRAM);
  `E_smooth1` S1 (eight → TABLE). The `E_sym5 | DENSE` witness of `RV-377-113` (T1, G15 step ii)
  was read on the raw genotype and never atrophied; it is a TABLE machine wearing a DENSE
  label — the `RV-377-074` mis-crediting, again. Recorded as its own record, **`RV-377-141`**
  (id assigned by the lead), and carried into the boundary theorem's V1.3 addendum.
* **Memory is the class the search finds, and rule 40 — not rule 36 — is what it fails on.**
  On `E_smooth1` all three seeds' memory elites clear rule 36 (min 0.8542, `half_events` binding
  on two) and miss the constant by **0.502 fx**: the constant is high there (0.8333) and
  `half_events` costs every evolved memory machine about one fx unit. That is the one existing
  cell where clause M, read off the standard-protocol closed form, is **wrong**, and it is
  recorded here before the fresh test rather than absorbed into a threshold. `E_wit1` sits in the
  abstain band and delivers 1/3.
* **Program is sporadic (2 of 12) and never above 1/3.** Where it appears it is exact or
  flat under all six (`E_smooth3` S1 at 0.9583 ×6; `E_wit1` S2 at 1.0 ×6, an 8-node exact
  program). The `E_smooth1` S1 PROGRAM elite at 1.0 standard falls to 0.5833 under
  `extra_unseen_feedback`.
* Two entire runs (`E_smooth1` S2, `E_smooth3` S2) recover nothing under the family, exactly
  as `RV-377-086` found; robustness clusters by run.

**Score of CRML-1 on the existing record, before the fresh test:** M present-cells 2 of 3
(miss: `E_smooth1`), M absent-cells none available, C 4 of 4, P 4 of 4, O 3 of 3.

## 8. Frozen predictions for the fresh ecologies

`STAGE_CLASSRATE_SELECTION_V43_CLASSRATE_SELECT.json` (sha `0156dc16…`, 1 305 s). The walk
examined canonical indices 0–7 of the discriminating enumeration (index 2 = `E_wit1`, skipped);
the identity check reproduces cap_S5 and cap_S5h at k = ±2, ±4, ±6, ±8 exactly.

| name | canonical idx | coeffs | bc | A_mem (S5h) | excess over θ | margin over bc | program_search (std / min6, exact?) | best hand-built coefficient row (h, lr, min6, margin) | witness-bearing |
|---|---|---|---|---|---|---|---|---|---|
| `E_cr1` | 0 | (−½, −½, −½, −½) | 0.6667 | 0.8333 | **−0.40 fx** | +4.0 | 1.0 / 1.0, exact | (8, 2) 0.8021, 3.25 — below θ | **no** |
| `E_cr2` | 3 | (−½, −½, −½, −⅛) | 0.7292 | 0.8646 | +0.35 fx | +3.25 | 0.9583 / 0.9583 | (3, 1) 0.8698, 3.374 | **yes** |
| `E_cr3` | 6 | (−½, −½, −½, ¼) | 0.7917 | 0.8958 | +1.10 fx | +2.50 | 1.0 / 1.0, exact | (3, 2) 0.8698, 1.874 | **yes** |
| `E_cr4` | 7 | (−½, −½, −½, ⅜) | 0.8125 | 0.9062 | +1.35 fx | +2.25 | 0.9583 / 0.9583 | (3, 2) 0.849, 0.876 — below θ | **no** |

Coverage: `E_cr1` memory-absent + witness-free; `E_cr2` witness-bearing (memory in the
abstain band); `E_cr3` memory-present + witness-bearing; `E_cr4` memory-present + witness-free.
Three seeds each, 20 000 charged evaluations, tag `V43_CLASSRATE_billy`.

| ecology | M (memory) | C (coefficient) | P (program) | O (ordering) | predicted class set (modal) |
|---|---|---|---|---|---|
| `E_cr1` | **≤ 1/3** (closed form 0.8333 < θ) | ≤ 1/3 | ≤ 1/3 | not tested (memory predicted absent) | ∅ or {PROGRAM} on at most one seed |
| `E_cr2` | abstain (+0.35 fx) | no bound (witness-bearing) | ≤ 1/3 | not tested | memory possible, unscored |
| `E_cr3` | **≥ 2/3** | no bound (witness-bearing) | ≤ 1/3 | not tested (witness-bearing) | {KVSTORE, TABLE} on ≥ 2 seeds |
| `E_cr4` | **≥ 2/3** | **≤ 1/3** | ≤ 1/3 | **memory ≥ program ≥ coefficient** | {KVSTORE, TABLE} on ≥ 2 seeds, nothing else on ≥ 2 |

Scoreable cells: M — `E_cr1` (absent), `E_cr3`, `E_cr4` (present); C — `E_cr1`, `E_cr4`;
P — all four; O — `E_cr4`. `E_cr2` scores only P. The predictions are written and committed
**before** any of the twelve units runs.

## 9. Falsifiers (stated once, scored once)

| id | falsifier of | law RED if |
|---|---|---|
| F-M1 | M | the memory class is missing (< 2/3) on **≥ 2** fresh ecologies where M predicts it present |
| F-M2 | M | the memory class is recovered on ≥ 2/3 seeds on **any** fresh ecology where M predicts it absent |
| F-C1 | C | the coefficient class is recovered on **≥ 2/3** seeds on any witness-free fresh ecology |
| F-P1 | P | the program class is recovered on ≥ 2/3 seeds on any fresh ecology, or on ≥ 1/3 where P predicts 0/3 |
| F-O1 | O | the ordering is violated on any fresh ecology where M predicts memory present and the ecology is witness-free |

One falsifier tripped → `CLASS_RATE_MORPHOLOGY_LAW_RED_AT_REGISTERED_SCOPE`, attributed to its
clause, and one revival iteration (`RV-377-142`; `RV-377-141` is the T1 atrophy record) is in
scope: the minimal justified change to that clause only, re-tested on two further fresh
ecologies chosen by the same rule. The candidate lever for clause M is already named by §7:
the rule-40 bar max(θ, bc + 1 fx) rather than θ alone, since the one existing miss failed the
constant and not the threshold. It is **not** adopted here, so the fresh test scores the law
as the theory states it. None
tripped and every M-present, C-free and P clause scored → `CLASS_RATE_MORPHOLOGY_LAW_SUPPORTED_AT_REGISTERED_SCOPE`.
A clause with no scoreable cell among the four is `NOT_TESTED_AT_THIS_SCOPE`, never SUPPORTED.

## 10. Execution

Twelve units, laptop billy only, at most two processes on the host (lead's budget):
`hpc/classrate_units.sh billy E_cr1,E_cr2,E_cr3,E_cr4 0,1,2 20000 V43_CLASSRATE` (one claim-based
worker per invocation), receipts `STAGE_B1_V43_CLASSRATE_billy_E_cr{1..4}_S{0,1,2}.json`, then
`class_rate.py score billy` → `STAGE_CLASSRATE_FRESH_V43_CLASSRATE_billy.json`. Results are
rsynced back and md5-verified; nothing runs on the Mac.

## RV-377-118 Lane B adjudication (atrophied reading)

The nine-seed replication of `G15` step (ii) ran on laptop billy (`U-B001..009`,
`STAGE_B1_V41_G15_REPLICATE_billy_E_sym5_S{1..9}.json`, 20 000 evaluations each; seed 1
reproduces the committed `V33` seed-1 receipt cell for cell). Scored by §3 —
`STAGE_CLASSRATE_V43_LANEB_ATROPHIED.json` (sha `521a2011…`, 613 s); best constant 0.7917.
Interventions are the **V1 family** here (continuity with `RV-377-113`); the leak-free V2 family
of `RV-377-150` is reported in the `_V2AUG` receipt and in the table's last column.

| seed | DENSE std | DENSE min over six (V1) | binding | rule 36 (V1) | rule 40 margin | DENSE after rule-32 atrophy | classes (V1) | DENSE rule 36 (V2) |
|---|---|---|---|---|---|---|---|---|
| S1 | 0.9062 | 0.8646 | `half_events` | ✓ | 1.75 fx | **TABLE** (27 → 17 nodes, both DENSE nodes deleted) | {KV, TABLE} | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |
| S2 | 0.8802 | 0.8594 | `shuffled_events` | ✓ | 1.63 | **TABLE** (30 → 12) | {KV, TABLE} | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |
| S3 | 0.9010 | 0.8281 | `no_revoke` | ✗ | — | — | {KV, TABLE} | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |
| S4 | 0.9688 | 0.7188 | `extra_unseen_feedback` | ✗ | — | — | ∅ (every carrier fails) | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |
| S5 | 0.9583 | 0.7500 | `shuffled_events` | ✗ | — | — | ∅ (every carrier fails) | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |
| S6 | 0.9010 | 0.8698 | `extra_unseen_feedback` | ✓ | 1.87 | **TABLE** (16 → 8, both DENSE nodes deleted) | {KV, TABLE} | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |
| S7 | 0.9115 | 0.8542 | `half_events` | ✓ | 1.50 | **TABLE** (18 → 12, both DENSE nodes deleted) | {KV, TABLE} | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |
| S8 | 0.8854 | 0.8281 | `extra_unseen_feedback` | ✗ | — | — | {KV, TABLE} | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |
| S9 | 0.9062 | 0.8229 | `shuffled_events` | ✗ | — | — | {PROGRAM} (0.9375 ×6, 11-node program) | ✗ (V2: memory_V2 4/9 — S1, S2, S6, S7; program 1/9; coefficient 0/9) |

`RV-377-118`'s predictions, scored on both readings:

| id | prediction | raw descriptor (as frozen) | atrophied reading (rule 23/32) |
|---|---|---|---|
| B1 | DENSE recovered and clears rule 36 on ≥ 3 of 9 seeds | **CONFIRMED** — 4 of 9 (S1, S2, S6, S7), every one separating the constant by ≥ 1.5 fx | **NOT REACHED** — 0 of 9: each of the four loses every DENSE node under rule-32 atrophy at no cost under any intervention and reads TABLE |
| B2 | `half_events` binds on the majority of recovered seeds | **FALSIFIED** — 2 of 4 (S1, S7); `shuffled_events` and `extra_unseen_feedback` bind the other two; over all nine DENSE elites `half_events` binds 2, `shuffled_events` 3, `extra_unseen_feedback` 3, `no_revoke` 1 | same |
| B3 | at least one seed recovers DENSE under `standard` but fails rule 36 | **CONFIRMED** — 5 of 9 (S3, S4, S5, S8, S9); S4 goes 0.9688 → 0.7188 | same |

Class rates over the nine seeds (atrophied reading, V1): **memory 6/9, program 1/9,
coefficient 0/9**; two runs (S4, S5) recover nothing under the family, as `RV-377-086` found
for two of nine earlier runs. With the three `V33` seeds the `E_sym5` record is **12 seeds:
memory 9/12, program 1/12, coefficient 0/12.**

**Consequence for `G15_STEP_TWO_REACHED`** (recorded as `RV-377-141`): on the raw descriptor
the step (ii) rate is 4/9 and `RV-377-118` B1 holds; on the atrophied reading the coefficient
carrier has never been recovered by neutral search on any discriminating ecology in the
corpus — 0 of 12 on `E_sym5`, 0 of 3 on `E_smooth1`, 0 of 3 on `E_smooth3`, 0 of 3 on `E_wit1`.
The terminal moves from TRUE-at-registered-scope to
`REACHED_ON_RAW_DESCRIPTOR_ONLY__NOT_REACHED_ON_ATROPHIED_READING`.

## 11. What this cannot settle

Three seeds per ecology bound a rate coarsely: 2/3 against 1/3 is one seed. Four ecologies test
each clause on at most four cells. The reading labels the machine by the carrier its served
answer reads after atrophy, not by identity (`b1`'s own claim ceiling). The law says nothing
about *which* memory machine arises — that is exactly the object `RV-377-121` showed is not
well-posed, and it is not reintroduced here.


---

# RV-377-140 — ADJUDICATION (receipts `STAGE_CLASSRATE_FRESH_V43_CLASSRATE_billy.json` + `_V2AUG`, `STAGE_B1_V43_CLASSRATE_billy_E_cr{1..4}_S{0,1,2}.json`; lead session after the lane's handover)

Twelve units, 20 000 charged evaluations each, scored by §3 under the V1 family (the frozen law) with the
V2 family reported alongside (RV-377-150/151).

| ecology | memory | program | coefficient | classes by seed (V1) | V2 |
|---|---|---|---|---|---|
| `E_cr1` | 0/3 | 1/3 | 0/3 | S0 {PROGRAM}, S1 ∅, S2 ∅ | same |
| `E_cr2` | 2/3 | **2/3** | 0/3 | S0 {TABLE}, S1 {PROGRAM, TABLE}, S2 {PROGRAM} | memory 1/3 (S0's TABLE fails v2), program 2/3 |
| `E_cr3` | 2/3 | 1/3 | 0/3 | S0 {KVSTORE}, S1 {PROGRAM, TABLE}, S2 ∅ | same |
| `E_cr4` | **0/3** | 1/3 | 0/3 | S0 ∅, S1 {PROGRAM}, S2 ∅ | same |

| falsifier | tripped? | evidence |
|---|---|---|
| F-M1 (memory missing on ≥ 2 ecologies where M predicts present) | no — 1 of 2 (`E_cr4`; `E_cr3` holds) | `E_cr4` S0: the KVSTORE/TABLE elite scores 0.9115 under `standard` and fails **only** `extra_unseen_feedback` (0.8229; 0.8438 under v2) |
| F-M2 (memory ≥ 2/3 where predicted absent) | no | `E_cr1` 0/3 |
| F-C1 (coefficient ≥ 2/3 on a witness-free ecology) | no | 0/3 everywhere; **0/24 over the whole fresh + lane-B record** |
| **F-P1** (program ≥ 2/3 on any fresh ecology) | **YES** | `E_cr2` program 2/3 |
| **F-O1** (ordering violated where memory predicted present, witness-free) | **YES** | `E_cr4`: memory 0 < program 1 |

**Terminal: `CLASS_RATE_MORPHOLOGY_LAW_RED_AT_REGISTERED_SCOPE`**, attributed to clauses **P** and **O**;
clause M survives its falsifier by one ecology but its `E_cr4` miss is diagnosed; clause C holds on every
scoreable cell (coefficient class never recovered: 0/12 fresh, 0/9 lane B, 0/16 diagnosis).

## Root cause — one stage per clause

* **P (program ≤ 1/3 everywhere)** was calibrated from the record's low base rate, not from the theory's
  own closed form. The selection receipt already held the exact-search row's rule-36 replay: `program_search`
  min-over-six 1.0 / 0.9583 / 1.0 / 0.9583 on `E_cr1..4`, admissible with ≥ 3 fx margin on all four. A
  reachable, admissible exact-search parent is exactly the condition under which the program class should be
  *present*, and it was recovered on 1/3, 2/3, 1/3, 1/3. Stage: the predictor.
* **M (memory present iff A_mem(S5h) ≥ θ + 1 fx)** used the Stage D'/E' `S5h` row's *standard-protocol*
  closed form (0.9062 on `E_cr4`). The search runs on the typed IR and is scored under rule 36; the IR
  memory row `hamming_knn_k3` replays at min-over-six **0.8229** on `E_cr4` (0.7708 / 0.7917 / 0.8125 on
  `E_cr1..3`), all below θ, and the recovered `E_cr4` memory elites fail the same bar (`extra_unseen_feedback`).
  The predictor was the wrong object (a different row under a different protocol). Stage: the predictor.
  Its retrodiction is also imperfect in the other direction: `E_cr2`/`E_cr3` recovered memory 2/3 although
  the hand-built memory row is inadmissible there — searched memory elites can beat the hand-built row, so
  a row-based predictor can only license *abstention*, not absence.
* **O** follows M.

## Minimal justified change (frozen as RV-377-142, clause-only)

* **P′**: program class present (≥ 1/3) iff the registered exact-search row is rule-36 admissible with ≥ 1 fx
  margin over the best constant; ≤ 1/3 otherwise. Retrodicts all four fresh ecologies and `E_wit1`/`E_smooth1`/
  `E_smooth3`/`E_sym5` (RV-377-141 table).
* **M′**: memory class present (≥ 2/3) iff the best registered IR memory row is rule-36 admissible with ≥ 1 fx
  margin; otherwise the law **abstains** on memory (a row-based predictor cannot exclude searched elites). On
  the four fresh ecologies M′ abstains everywhere, so it makes no false claim and no claim.
* **C** unchanged. **O′**: program ≥ coefficient wherever P′ predicts program present.

The two further fresh ecologies are chosen by the same deterministic walk (`select_fresh(6)`, tag
`V44_CLASSRATE_SELECT6`), registered as `E_cr5`, `E_cr6`, three seeds each, predictions and falsifiers in
`GMI_K4_CLASS_RATE_REVIVAL_RV_377_142_FREEZE.md` before any run.

## What moves

`K4_CLASS_RATE_LAW`: clause C (coefficient never neutrally recovered, 0/37 across the corpus at 20 000
evaluations, every ecology) is the one class-level regularity that has held everywhere; it is recorded as
`COEFFICIENT_CLASS_NOT_NEUTRALLY_RECOVERED_AT_20K__0_OF_37` and is the class-level restatement of the
protected K4 negative. Clauses M/P/O are RED as frozen and revived as M′/P′/O′.
