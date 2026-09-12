# DG-7 V2 — the index audit of every class-level negative terminal in the corpus

**Supersedes:** `GMI_DG7_INDEX_AUDIT_V1.md` in its *classification* only. Every measurement, every failed clause, every
RED terminal and every narrowing recorded in V1 and in `REVIVAL_LEDGER*.jsonl` stands verbatim and is untouched.
**Governed by:** `GMI-DA11` (domain algebra §16) and protocol rules 36, 38, 39, 40, 42, 43.
**Predictions for the five experiments below were frozen in commit `ade178e8`** (`GMI_DG7_V2_FROZEN_PREDICTIONS_V1.md`)
**before any of them was executed.** Nothing in that file was edited afterwards. Two of its numeric predictions are
recorded below as FAILED and are not repaired.

Unit convention (rule 40): one `fx` unit = `1/(1.5·16) = 0.0416667` capability. A margin strictly below one fx unit is
`WITHIN_QUANTIZATION` and may not separate two mechanisms.

---

## 0. What V2 changes, and the one exemption it withdraws

V1 established, correctly, that the corpus records negative terminals without saying what they searched. V2 does three
things V1 did not:

1. It classifies **all 38** declared terminals into exactly one of `DISCHARGED` / `UNDER_SWEPT` / `VACUOUS` /
   `REQUIRES_RUN`, naming the index in every case.
2. It runs five cheap local experiments, four of which attack this lane's own instruments rather than the corpus's
   older records.
3. **It withdraws V1 §1's exemption of `RV-377-088` as a "triage false positive".** V1 excused `RV-377-088` and
   `RV-377-089b` on the ground that their terminals contain the word `FALSIFIED` because they *did* the falsifying.
   That reasoning does not survive rule 36. `RV-377-088`'s overturn is carried by its clause C1, *"the dense class
   DOES contain an admissible member on `E_smooth2` at the registered theta"* — an unqualified **admissibility**
   claim about a **class**, which is precisely what rules 36, 38 and 40 bind. A record that overturns a negative by
   asserting a positive inherits every sweep obligation the positive carries. §1.1 below is the result.

### 0.1 Two bookkeeping defects in V1 itself

* V1 §3a lists **six** discharges, one of which — `RV-377-030` — is **not among the 38** it declares in §2. The
  effective discharge count against the declared population is therefore **five**, not six.
* V1 §0 says "twelve name no index at all; of those twelve, four are triage false positives", but its §2 `0 of 5` row
  lists twelve records of which only two (`-092`, `-097`) are marked as false positives; the other two
  (`-088`, `-089b`) are named in §1 and never appear in the table. The population arithmetic closes only as
  36 listed + `-088` + `-089b` = 38.

---

## 1. Executed this session — five experiments, verbatim

### 1.1 `DG7-X1` — `RV-377-077`, the programme's headline negative, on the SEED index

**What was wrong, found by inspection.** `STAGE_B4_PRETEST_V1.json` — the receipt behind
`NO_UNKNOWN_FORM_AT_SCOPE__ALL_7_RECOVERED_MACHINES_ARE_EXACTLY_DEVELOPMENTALLY_EQUAL_TO_A_KNOWN_PARENT` — consumes
`STAGE_B1_ATROPHY_V1.json`, whose own `receipts_examined` field reads:

```
["STAGE_B1_ATROPHY_V1.json", "STAGE_B1_V33_B1_IR_RECOVERY_S0.json", "STAGE_B1_V33_B1_IR_RECOVERY_S1.json"]
```

Three entries, of which the first is the receipt's own output file and carries an `error` row, and the other two are
the **pre-repair filenames** that `RV-377-058`'s `measurement_validity_status` records as having silently overwritten
each other across ecologies before the harness was fixed to key filenames on the ecology. Neither exists on disk
today. The correctly keyed receipt for the same ecology, `STAGE_B1_ATROPHY_SMOOTH3.json`, examines **three** recovery
receipts (`..._E_smooth3_S0/S1/S2.json`) and carries **10** elites against V1's **7**.

The headline negative was therefore computed over **two of the three available seeds on its own ecology**, while the
three-seed receipt already existed.

**Run.** `atrophy_ir.b4_pretest(tag="DG7V2", eco_name="E_smooth3", catalogue_tag="V1", atrophy_tag="SMOOTH3")`. Same
catalogue, same instrument, same ecology, same theta, same code. Verbatim:

```
  S0 KVSTORE ->KVSTORE  cap 0.8698 struct_known=False equal_to=['hamming_knn_k3']
  S0 PROGRAM ->KVSTORE  cap 0.8698 struct_known=False equal_to=['hamming_knn_k3']
  S0 TABLE   ->TABLE    cap 0.8698 struct_known=False equal_to=['hamming_knn_k3']
  S1 DENSE   ->PROGRAM  cap 0.9583 struct_known=False equal_to=['compiled_search', 'program_search']
  S1 KVSTORE ->KVSTORE  cap 0.8698 struct_known=True equal_to=['hamming_knn_k3']
  S1 PROGRAM ->PROGRAM  cap 0.9583 struct_known=True equal_to=['compiled_search', 'program_search']
  S1 TABLE   ->TABLE    cap 0.8698 struct_known=False equal_to=['hamming_knn_k3']
  S2 KVSTORE ->KVSTORE  cap 0.8698 struct_known=True equal_to=['hamming_knn_k3']
  S2 PROGRAM ->KVSTORE  cap 0.8698 struct_known=False equal_to=['hamming_knn_k3']
  S2 TABLE   ->TABLE    cap 0.8698 struct_known=False equal_to=['hamming_knn_k3']
novel at STRUCTURAL resolution: 7/10 | novel at RESPONSE resolution: 0/10
terminal: NO_UNKNOWN_FORM__EVERY_RECOVERED_MACHINE_IS_EXACTLY_DEVELOPMENTALLY_EQUAL_TO_A_KNOWN_PARENT

n_candidates = 10
distinct response signatures among candidates = 2
   344c3b6b69d7  n=2  ['E_smooth3_S1|DENSE', 'E_smooth3_S1|PROGRAM']
   3b42e95a24cc  n=8  ['E_smooth3_S0|KVSTORE', 'E_smooth3_S0|PROGRAM', 'E_smooth3_S0|TABLE', 'E_smooth3_S1|KVSTORE',
                       'E_smooth3_S1|TABLE', 'E_smooth3_S2|KVSTORE', 'E_smooth3_S2|PROGRAM', 'E_smooth3_S2|TABLE']
n_novel_at_response_resolution = 0
n_novel_at_structural_resolution = 7
terminal = NO_UNKNOWN_FORM__EVERY_RECOVERED_MACHINE_IS_EXACTLY_DEVELOPMENTALLY_EQUAL_TO_A_KNOWN_PARENT
receipt_sha256 = 9969578470f28b9030fd56a25d28d7c0ff0acb36ae364c95f648b16cf5f03ac9
```

**Adjudication against the frozen text.** All three frozen clauses **HOLD**: `n_candidates = 10`; distinct response
signatures = 2 (predicted "at most 3"); `n_novel_at_response_resolution = 0`. **The headline negative survives the
seed index.** That is a real upholding and it is recorded as such.

**What it costs the terminal anyway.** The words `ALL_7_RECOVERED_MACHINES` do not survive. Ten rows over three seeds
collapse to **two distinct developmental responses**, and eight of the ten are the *same* response. The negative is
not "seven machines were checked"; it is "two behaviours were produced, on one ecology, at one budget, and both are
known parents". Under rule 29 a count is meaningless outside its triple; the auditable statement is
**2 distinct responses / 3 seeds / 1 ecology / 20 000 evaluations**.

**Instrument note (new).** `b4_pretest` hashes its own wall-clock `seconds` field into `receipt_sha256`, so the
receipt is *not* byte-reproducible: two identical runs in this session produced
`88ae743bf76ee5f855d9a746f4bc4208332b64585349db6b1637fea9f25af234` and
`9969578470f28b9030fd56a25d28d7c0ff0acb36ae364c95f648b16cf5f03ac9`. Every other field was identical. This affects
`STAGE_B4_PRETEST_*`, `STAGE_B4_CATALOGUE_*` and `STAGE_B1_ATROPHY_*`.

**Rule-40 margins for `RV-377-077`'s own catalogue**, computed here because the record predates rule 40
(`E_smooth3 | unseen`, best constant `0.8125` at fx 4, DISCRIMINATING):

```
admissible PARENTS of the reference catalogue:
   compiled_search    cap 0.9583   margin over null 0.1458     =  3.4992 fx units
   hamming_knn_k3     cap 0.8698   margin over null 0.0573     =  1.3752 fx units
   particles_p4       cap 0.8958   margin over null 0.0833     =  1.9992 fx units
   program_search     cap 0.9583   margin over null 0.1458     =  3.4992 fx units
   soft_retrieval     cap 0.8542   margin over null 0.0417     =  1.0008 fx units

recovered CANDIDATES:
   response 344c3b6b69d7  cap 0.9583   margin over null 0.1458     =  3.4992 fx units
   response 3b42e95a24cc  cap 0.8698   margin over null 0.0573     =  1.3752 fx units
```

Nothing here is `WITHIN_QUANTIZATION`, but `soft_retrieval` — one of the five parents the novelty claim is measured
against — clears the null by **exactly one quantization step** (1.0008 fx units). The reference catalogue is one
rounding decision wide at its bottom edge.

### 1.2 `DG7-X2` — `RV-377-069`'s exhaustive census against the rule-40 null

```
E_sym5 | unseen : best constant capability = 0.7917  at constant fx = 5
census ecology block: {"coeffs": [0.3125, 0.3125, 0.3125, 0.3125], "criterion": "unseen", "n_events": 8, "name": "E_sym5", "theta": 0.85}

 size  genotypes    canon   resp  best_cap  margin_over_null  fx_units
    3          1        1      1    0.5833           -0.2084   -5.0016
    4         15       15      4    0.6354           -0.1563   -3.7512
    5        220      159      7    0.7188           -0.0729   -1.7496
    6       7323     3233     25    0.7917               0.0       0.0
    7     336242    84767    127    0.7917               0.0       0.0

P4_ADMISSIBLE realized at each size: {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0}
P3_GENERALIZES realized at each size: {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0}
```

**Frozen prediction HOLDS, exactly.** The maximum capability attained by **any** of the 336 242 type-correct servable
genotypes of size ≤ 7 over the declared 19-kind alphabet is `0.7917` — **exactly** the score of the best machine that
reads neither its input nor its feedback. Margin **0.0000 fx units**. Every genotype of size ≤ 5 is strictly *worse*
than the null.

`RV-377-069`'s four exact lower bounds are unaffected — they are theorems about which *structures* realize
`P1_DISTINGUISHES` and `P2_LEARNS`, and they stand exactly as measured. What is withdrawn is any reading of its
**capability ceiling** as a fact about the alphabet: the ceiling is the null's score, and under rules 40 and 43 a
ceiling that coincides with the constant control does not separate the alphabet from a machine that ignores the
world. V1 recorded this record as `discharged` on the size index. It is re-opened here on the **null index**, which
its own `dg7_index_block` names as absent (`"null controls": "none (rules 40 and 42 did not exist)"`) and which V1
discharged anyway.

### 1.3 `DG7-X3` — the DG-9 constant-control audit is itself under-swept on the SIGN index

`constant_control.audit()` sweeps `E_sym(k)` for `k = 0..16` — **non-negative k only**. `RV-377-060` adjudicates
2 640 predicted cells on `E_sym(k)` for `k ∈ {1, −1, −2, −3, −4, 10, 12, 13}`, criterion `unseen` (read from its own
receipt's `ecology` block). `RV-377-101` names seven records as touching the contaminated region —
`RV-377-035, -039, -040, -085, -089, -089b, -100` — and `RV-377-060` is not among them.

```
   k       all  c_all  disc_all    unseen  c_uns  disc_unseen
  -5    0.8438    -10      True    0.7917    -15         True
  -4     0.875     -8     False    0.8333     -4         True
  -3    0.9062     -6     False     0.875     -9        False
  -2    0.9375     -4     False    0.9167     -6        False
  -1    0.9688     -2     False    0.9583     -1        False
   0       1.0      0     False       1.0      0        False
   1    0.9688      2     False    0.9583      3        False
   2    0.9375      4     False    0.9167      2        False
   3    0.9062      6     False     0.875      3        False
   4     0.875      8     False    0.8333     12         True
   5    0.8438     10      True    0.7917      5         True
  10    0.6875     20      True    0.5833     30         True
  12     0.625     24      True       0.5     12         True
  13    0.5938     26      True    0.4583     39         True

k values where best constant differs between +k and -k: []  (empty = exactly symmetric)
RV-377-060 ecologies k = [1, -1, -2, -3, -4, 10, 12, 13], criterion 'unseen' (from its own receipt)
  NON_DISCRIMINATING under 'unseen': [1, -1, -2, -3]   -> 4 of 8
  NON_DISCRIMINATING under 'all'   : [1, -1, -2, -3, -4]   -> 5 of 8
```

**Instrument note (new, found while re-deriving the audit).** The committed receipt
`STAGE_DG9_CONSTANT_CONTROL_V1.json` records `n_ecology_criterion_pairs: 40`. Re-running `constant_control.audit()`
today yields **42**, because `RV-377-103` added `E_wit1` to `ecology.REGISTRY` *after* the DG-9 audit ran. The
committed receipt is therefore **stale with respect to the registry it claims to sweep**, and the one ecology on which
the programme's first genuinely learning coefficient carrier was recovered is not in the audit that certifies
admissibility claims. The two rows it would gain are `E_wit1|all` 0.75 (fx −16) and `E_wit1|unseen` 0.7083 (fx −8),
both DISCRIMINATING, and none of the original 40 rows changes — the 9 non-discriminating pairs are unchanged. **The
committed receipt has been left byte-identical** (`receipt_sha256 d25071f349b12908eabac29acb6694211213b44060f1137b856532b789e89a4b`);
regenerating it would silently rewrite another record's evidence. The staleness is recorded here instead.

**All three frozen clauses HOLD.** The best constant is exactly symmetric in `k`, so the negative half of the family
inherits the contamination; **4 of `RV-377-060`'s 8 ecologies are `NON_DISCRIMINATING` under the criterion it
actually ran**. `RV-377-060` is an **eighth** ledger record touching the contaminated region, and the DG-9
record-attribution of `RV-377-101` is incomplete. `RV-377-060`'s `OCCUPANCY_RULE_EXACT_ON_1980_OF_1980_CELLS_GIVEN
_THE_TRUE_ADMISSIBLE_SET` and its `ADMISSIBILITY_MODEL_FALSIFIED_IN_THREE_WAYS` both stand as measurements; what may
not stand is any admissibility-based reading of the four contaminated ecologies at theta = 0.85.

### 1.4 `DG7-X4` — best-constant controls that appear in no DG-9 row at all

```
E_smooth2 (COEFFS_V2 (0.5, -0.5, 0.25, 0.75)) | all   : best constant 0.7083  at fx 8  DISCRIMINATING
E_smooth2 (COEFFS_V2 (0.5, -0.5, 0.25, 0.75)) | unseen: best constant 0.75    at fx 8  DISCRIMINATING
E_smooth8 (256 inputs, coeffs (0.375, -0.625, 0.875, -0.375, 0.125, -0.125, 0.125, 0.125)) | all 256:
                                                best constant 0.6641  at fx 4  DISCRIMINATING
E_smooth8_div (4 targets, mean) | all 256:      best constant 0.4521  at fx 2  DISCRIMINATING
  per-target scores of that constant: [0.6582, 0.6582, 0.2461, 0.2461]
```

**Qualitative prediction HOLDS** — all three are DISCRIMINATING, so the blind-recovery negatives are about real
regions and not about nulls. **One frozen numeric prediction FAILS and is recorded, not repaired:** `E_smooth8_div`
was predicted in `[0.58, 0.74]` and measures `0.4521`, below the frozen band. The cause is visible in the per-target
line — the diversity ecology's four sign-flipped targets have no common constant, which is exactly the property
`RV-377-023` built it for, and the frozen band was reasoned from the single-target `E_smooth8` figure.

Margins over the null for the negatives these ecologies carry:

| record | reported best | null | margin | fx units |
|---|---|---|---|---|
| `RV-377-009` (`E_smooth2`, 16 ev) | 0.7578 | 0.7083 | 0.0495 | 1.19 |
| `RV-377-014` (`E_smooth2`, 48 ev) | 0.8411 | 0.7083 | 0.1328 | 3.19 |
| `RV-377-088` overturn (16 ev) | 0.9271 | 0.7083 | 0.2188 | 5.25 |
| `RV-377-016` (`E_smooth8` plateau) | 0.7676 | 0.6641 | 0.1035 | 2.48 |
| `RV-377-023` (`E_smooth8_div`) | 0.7346 | 0.4521 | 0.2825 | 6.78 |
| `RV-377-028` (clean re-run) | 0.7441 | 0.4521 | 0.2920 | 7.01 |

None is `WITHIN_QUANTIZATION`. The blind-recovery family of negatives survives rule 40 intact.

### 1.5 `DG7-X5` — the DG-7 population is itself an index held at an inherited default

```
ledger records total: 103
declared DG-7 population: 38
records whose result_terminal matches the negative token set: 75
matched but NOT in the declared 38: 41
in the declared 38 but not matched by this token set: ['RV-377-031', 'RV-377-056', 'RV-377-070', 'RV-377-092']
```

**Frozen prediction HOLDS** (predicted ≥ 20; measured **41**). Among the 41 are records that are unambiguously
class-level negatives and are not in the audit at all: `RV-377-018` (`SEARCH_REACHABILITY_BOUNDED_FAILURE_AT_1E5x3`),
`RV-377-020` and `-022` (`PH5_NEGATIVE_CONTROL_HOLDS__NOTHING_DEVELOPS`), `RV-377-040`
(`ALL_THREE_QUANTITATIVE_CLAUSES_FAILED`), `RV-377-062` (`NOT_FOR_THE_COEFFICIENT_CARRIER`), `RV-377-085`
(`ADMISSIBILITY_UNDER_THE_STANDARD_INTERVENTION_IS_NOT_ADMISSIBILITY`), `RV-377-086`, `RV-377-087`
(`CLAUSE_1_FAILS_0_OF_3`), `RV-377-090` (`NO_UNIVERSAL_TOKENIZER_SIZE_CONFIRMED`), `RV-377-098`
(`PRE_NORM_IS_NOT_UNIFORMLY_MORE_STABLE_AT_DEPTH`) and `RV-377-100` (`C1_FAILS`).

**DG-7's own population was fixed by an unrecorded keyword triage — the exact defect rule 39 forbids, committed by
the document that enforces rule 39.** The audit cannot close on 38 rows while the corpus contains at least 41 more
negative-shaped terminals that were never triaged into it, and it cannot even reproduce its own 38 from a stated
pattern: four of the declared 38 do not match the token set used here, so two different regexes give two different
populations and neither is written down.

---

## 2. The 38-terminal table

Index legend: `A` = alphabet / row parameters · `d` = structure depth · `p` = arithmetic instrument · `F` = ecologies ·
`J` = intervention set · `S` = seeds · `B` = budget · `N` = null controls (rule 40 best constant, rule 42
fixed-function) · `Z` = size / capacity bound · `H` = reuse horizon.

| # | record | terminal (abbrev., unaltered in the ledger) | indices SWEPT | index DEFAULTED | class | cheapest discharge |
|---|---|---|---|---|---|---|
| 1 | `RV-377-005` | `NOT_OBSERVABLE_AT_SCOPE` | none — and the narrowing says so | all, each named in its own `dg7_index_block` | **DISCHARGED** | done (narrowed); `N` now attached: `E_smooth1` 0.7917 all / 0.8333 unseen, DISCRIMINATING |
| 2 | `RV-377-009` | `E_SMOOTH2_NOT_OBSERVABLE__NO_ADMISSIBLE_ROW_AT_16_EVENTS` | `A` (35 cells h×LR), columns (6), lengths (16, 48), `F` (3 as controls) — by `RV-377-088` | — (terminal withdrawn) | **DISCHARGED** | done by re-run; class max 0.9271 against the 0.7578 recorded. **The discharging record is itself `REQUIRES_RUN` on `J` — see row 34** |
| 3 | `RV-377-011` | `007_NEGATIVE_NO_WINNER_AT_12000` | `B` (12 000+160), `S` (1), canonicalization | `d` of the update grammar (2) | **VACUOUS** | the quantified region is empty: `RV-377-015` measured max update-expression depth **2** over 20 000 random candidates, and the planted 4-coefficient learner scores **0.0** (diverges) at that depth. No admissible dense-numeric member exists to be found |
| 4 | `RV-377-014` | `E_SMOOTH2_D48_NOT_OBSERVABLE_SECOND_TIME` | as row 2 | — (terminal withdrawn) | **DISCHARGED** | done by re-run; class max 0.8802 against 0.8411 — four times the 0.0089 shortfall it reported |
| 5 | `RV-377-015` | `PLANTED_EXISTENCE_FALSIFIED__DENSE_FORM_NOT_REPRESENTABLE_IN_FROZEN_GRAMMAR__RUN5_NOT_RUN` | update-grammar depth (2 vs 3), learning rate (1, 1/2, 1/4), k (1..4) — class max **0.9258** reported | `F`, `p`, `J`, `N` | **DISCHARGED** | none needed: the terminal already carries its index (`IN_FROZEN_GRAMMAR`) and states `RUN5_NOT_RUN`. The one record in the population whose terminal was rule-39 compliant before rule 39 existed |
| 6 | `RV-377-016` | `SEARCH_REACHABILITY_BOUNDED_FAILURE_AT_SCOPE__EXISTENCE_CERTIFIED__NO_FURTHER_ESCALATION` | `d` (2 and 3, both plateau 0.7676), `S` (RUN4, RUN6) | `B`, `F`, `J` — all three now **named as declined** | **DISCHARGED** | done (narrowed); `N` now attached: `E_smooth8` null 0.6641, plateau is 2.48 fx units above it |
| 7 | `RV-377-023` | `DIVERSITY_GRADIENT_CONFIRMED__ASSEMBLY_NOT_REACHED_AT_1E5x3` | `B` (1e5/seed), `S` (3) | `A`, `d`, `p`, `F` (1), `J`, `N` — all named | **DISCHARGED** | done (narrowed); `N` now attached: `E_smooth8_div` null 0.4521, bests 6.78 fx units above it |
| 8 | `RV-377-028` | `NO_WINNER_AT_THETA_CONFIRMED_BUT_THE_REPORTED_PLATEAU_IS_A_CACHE_ARTEFACT` | `B` (1e6), cache on/off (the decisive index, swept) | **`S`** — seed 6 OOM-killed at 6.7e5/1e6; the clean replacement RUN11 ran on **seed 5 alone** | **REQUIRES_RUN** | `blind.main_evolve(seed=6, evaluations=1_000_000, diversity=True)` and `seed=7`, FEC disabled (RUN11 configuration), genotype cache on, checkpoints every 5e4; ~35–40 min/seed, one core, ≥ 5 GB RSS headroom. Report the class maximum over the three sound seeds, not the per-seed best |
| 9 | `RV-377-029` | `PROBABILISTIC_ROW_INADMISSIBLE_EVERYWHERE_UNDER_NATIVE_SEMANTICS` | columns (6), K ladder (4, 16) | **`F`** — only ecology (i) of the three declared was executed; (ii) and (iii) "were not run" | **UNDER_SWEPT** | none: `RV-377-031` already falsifies the word `EVERYWHERE` (REF `S7 = 0.875 ≥ theta`). Narrow the terminal to ecology (i) at 6 events under the corrected `NORMALIZE` macro |
| 10 | `RV-377-031` | `PROBABILISTIC_ROW_ADMISSIBLE_ONLY_AT_FULL_OBSERVATION_AND_NEVER_THE_OCCUPANT` | `F` (3), columns (6), K (4, 16 — cap justified by a stated 8-bit underflow argument) | **`J`** (rule 36) and **`N`** | **UNDER_SWEPT** | name `J` as declined (free). A real discharge needs the `smooth.py` rows ported to `ecology.run_genotype`; see row 34 for the same adapter |
| 11 | `RV-377-038` | `NATIVE_COLUMN_DEPTH_1_CLAUSE_FAILED_BY_DESCRIPTION_AMORTIZATION` | cells (3), rows (3), columns (6), depth (1, 8) | **`H`** — one headline reuse horizon, 64, while the record's own diagnosis puts the crossover at `H* = 169` | **UNDER_SWEPT** | re-run `e1_lineage` over `H ∈ {64, 128, 169, 256}`, everything else fixed; ~5 min. This is a DG-2 instance inside a DG-7 row |
| 12 | `RV-377-042` | `UNVERIFIED_SPECULATION_INADMISSIBLE_BELOW_PA_1` | `p_a` (5), λ (3), `H` (3), columns (6) | `J`, `N`, `F` (one `E_factored`) | **UNDER_SWEPT** | compute the abstention-aware null for `E_factored` (a constant answerer and an always-abstain row) and report the SPEC row's margin; seconds |
| 13 | `RV-377-046` | `DENSE inadmissible in all 144 cells` (clause 7) | `L` (4), rule (4), `n_dev` (9), rows (4) | **`B`** — the record's own declared 16-trajectory `DENSE` training cap, which it labels "open, non-blocking" | **UNDER_SWEPT** | promote the record's own post-hoc diagnostic to a swept index: re-run `dc_field` `DENSE` at trajectory caps {16, 64, 256}. It already measured 0.5 / 0.9375 / **1.0** at `L = 8` — so the clause is known to invert at 256 and is unswept, not wrong. ~3 min |
| 14 | `RV-377-051` | `PRECISION_GATED_EXACTLY_AT_COUNTER_RANGE_8` + `POSET_NOJOIN` twin negatives | `w` (4), `L` (3), instruments (2), interleavings (2), columns (2) | **poset seed** — one declared poset per cell, LCG seed 53; the record names this itself | **UNDER_SWEPT** | re-run `dn_partialorder` at poset seeds {53, 59, 61}; ~15 min. Reports the class max over draws instead of one draw |
| 15 | `RV-377-052` | `SERVE_LAW_FALSIFIED_OUT_OF_SAMPLE_AT_W6_L6` | `w ∈ {2,3,4,6,12}`, `L ∈ {4,6,8,12}`, 2 columns, 2 instruments, 2 interleavings — out of sample in both coordinates, both sides of the boundary | poset seed, **named** in its own `measurement_validity_status` | **DISCHARGED** | none: the grid was declared before the run, tested the law in both directions, and the one remaining index is named |
| 16 | `RV-377-056` | `DYNAMIC_ROUTING_NEVER_ON_THE_FRONTIER_AT_UNIT_DISCOVERY_PRICE` | `c_s` (6 prices), cells (9), budgets (17), **full enumeration of 14 792 inputs** | **`k`** — the source count is pinned at 16, and the arm set (5) is declared rather than parent-maximal | **UNDER_SWEPT** | sweep `k ∈ {8, 16, 32}` in `b2_route`; full enumeration, under a minute |
| 17 | `RV-377-058` | `MEASURED_RECOVERY_RATES_ARE_D2_6_OF_6__D4_D5_2_OF_6__D1_ZERO_OF_6` | encodings (typed IR), `S` (6 runs) | `A`, `d`, `p`, `F` (2), `J`, `N` — all named | **DISCHARGED** | done (narrowed); its silence about `D1` is explained by `RV-377-089`'s ceiling rather than by search |
| 18 | `RV-377-060` | `ADMISSIBILITY_MODEL_FALSIFIED_IN_THREE_WAYS__SIGN_SYMMETRY_REFUTED_FOR_THE_GRADIENT_CARRIER` | `F` (8 ecologies), `H` (1..128), `r` (6), columns (6), rows (5) — 2 640 cells | **`N`** — 4 of its 8 ecologies are NON_DISCRIMINATING under its own `unseen` criterion (`DG7-X3`) | **UNDER_SWEPT** | done in part by `DG7-X3`; remaining: re-tally the 1 980 occupancy cells restricted to `k ∈ {−4, 10, 12, 13}`. Pure re-read of committed receipts, seconds |
| 19 | `RV-377-063` | `PROGRAMME_FORM_OF_THE_DISCRIMINATING_CLAIM_FALSIFIED_AND_REPLACED` | orientations (16, exhaustive), budgets (4), prices (2), columns (5) — 13 440 cells | **`F`** — one `E_alias` skeleton, one nuisance layout | **UNDER_SWEPT** | a second declared causal skeleton in `e1_iql` (e.g. a 6-node path with two nuisance nodes); ~5 min |
| 20 | `RV-377-064` | `DISCRETE_THRESHOLD_CLAUSE_FAILED_BY_A_CYCLE_PHASE_EFFECT` | `G` (4), columns (4), rows (6) | **schedule** — the record's own limitation says the composition is "exact for the declared rotation only" | **UNDER_SWEPT** | a second declared rotation in `e1_scdi`; ~5 min |
| 21 | `RV-377-065` | `NO_DEPTH_GATED_KINGDOM_AT_EXECUTED_DEPTHS__PARENT_MAXIMAL_OPPONENT_OCCUPIES_EVERY_CELL_TO_DEPTH_6` | `d` (1–6), code families (2), widths (2), seeds (3), rows (6) — 48 cells, 96 decisions | **`d > 6`**, `p`, `F`, `J`; and the theta gate silences **34 of 96** decisions, which is a null-control failure the record reports but does not index | **UNDER_SWEPT** | extend `dk_depth` to `d = 7, 8` at `D = 64`, one seed (minutes); and report the 34 silenced XOR cells as `VOID` under rule 22 rather than as decisions the parent won |
| 22 | `RV-377-067` | `STOCHASTIC_CARRIER_OCCUPIES_0_OF_336_CELLS_AT_BOTH_DECLARED_RELIABILITIES` | reliability `q` (2 declared indices), 30 R-top cells re-executed from scratch, columns (6), exact Clopper-Pearson intervals | frontier rule — **named** (rule 17, R-top, held identical for like-for-like re-adjudication) | **DISCHARGED** | none: the decisive index (`q`) is swept and both endpoints reported |
| 23 | `RV-377-069` | `EXHAUSTIVE_CENSUS_REACHES_SIZE_7_EXACTLY__CEILING_0_7917` | `Z` (exhaustive to 7 over the declared alphabet), development length (8, 16, 32), one alphabet parameter | **`N`** — named as absent in its own index block and discharged by V1 anyway | **UNDER_SWEPT** (re-opened from V1's `discharged`) | done by `DG7-X2`: the ceiling equals the best constant, margin **0.0000 fx units**. Remaining obligation is to restate the ceiling as "no genotype of size ≤ 7 beats a constant", which is free |
| 24 | `RV-377-070` | `F_REFINEMENT_SPLITS_10_OF_14_EQUALITY_CERTIFICATES__3_SURVIVE_THE_KNOWN_GATES` | `F` (5 new interventions × 2 new obligations × 14 pairs, 9 800 cells) | `A`, `d`, `p` (V1 §5) | **UNDER_SWEPT** | the three splits "no known gate explains" are the load-bearing residual: re-run those three pairs at a second declared capacity point in `refine_f`; ~20 min |
| 25 | `RV-377-074` | `THE_COEFFICIENT_CARRIER_IS_NOT_RECOVERED_OVER_THE_IR` | atrophy instrument (exact), elites (7) | `S` (2 of 3) **and** `F` (1) | **UNDER_SWEPT** | the `S` half is **discharged here as a by-product of `DG7-X1`**: seed 2 on `E_smooth3` yields KVSTORE, KVSTORE, TABLE — no coefficient carrier, so the terminal holds over three seeds. `F` remains at one ecology; `RV-377-083` and `-103` address it on other ecologies |
| 26 | `RV-377-075` | `PRECISION_GATED_KINGDOM_FALSIFIED_FOR_WANT_OF_A_PARENT_MAXIMAL_OPPONENT_ON_TWO_OF_THREE_DECLARED_EVENT_SEQUENCES` | `F` (2), event sequences (3), instruments (4), rows (3), machine seeds (2) | **state-representation index of the other rows** — rule 24 is this record's own rule and it was applied only to the log row | **UNDER_SWEPT** | apply the max-subtraction renormalization to the ten linear rows in `dk_precision_log` and report their class maximum; ~2 min |
| 27 | `RV-377-076` | `PRECISION_BUYS_DESCRIPTION_AND_EXECUTION_COST_NOT_CAPABILITY__AT_SCOPE` | `p` (7 instruments), rows (13), event sequences (5), price vectors (2), description bases (2), both frontier rules | **`F` (2 only)**, `A`, `d` — named in V1 §5 | **UNDER_SWEPT** | add a third declared ecology to `dk_precision_residual`; ~5 min. This is the `p` axis of the four-axis kingdom negative and its ecology index is two points wide |
| 28 | `RV-377-077` | `NO_UNKNOWN_FORM_AT_SCOPE__ALL_7_RECOVERED_MACHINES_ARE_EXACTLY_DEVELOPMENTALLY_EQUAL_TO_A_KNOWN_PARENT` | catalogue atrophied by the same instrument (rule 26), response resolution (rule 25), **`S` (3) — discharged here** | **`F` (one, `E_smooth3`)**, **`B` (20 000)**, `A` (zoo defaults), `J` | **REQUIRES_RUN** | `b1.main` at 20 000 charged evaluations × seeds {0,1,2} on `E_wit1` (the one registered DISCRIMINATING ecology with an exhibited intervention-robust coefficient witness), then `atrophy_ir.main` and `b4_pretest` against a catalogue re-atrophied on `E_wit1`. ~10–25 min per run, 3 runs, plus 2 min of pre-test. Until then the terminal reads **2 distinct developmental responses on one ecology at one budget** |
| 29 | `RV-377-079` | `EXPONENTIAL_SEPARATION_IS_AGAINST_A_DOMINATED_SEARCH_PARENT` + twin-admissibility failures | cells (10), rows (5) | **twin functional draw** (one per cell) and **column** (B0 only) | **REQUIRES_RUN** | `dn_obstruction` with a declared ensemble of 8 twin draws per cell (the `RV-377-055` registered experiment, never executed); ~8 min × 8 = ~1 h. Enlarging the evaluation set is proven to be the wrong index — see row 30 |
| 30 | `RV-377-080` | `TWIN_ADMISSIBILITY_IS_A_TWIN_DRAW_PROPERTY_NOT_INSTANCE_SAMPLING_NOISE` | evaluation-set size (8 → 16) — and the record proves this was the **wrong** index | **twin functional draw**, still one per cell | **REQUIRES_RUN** | as row 29. This record is the cleanest executed proof in the corpus that sweeping the wrong index buys nothing |
| 31 | `RV-377-081` | `THE_COEFFICIENT_CARRIER_HAS_NO_KNOWN_ADMISSIBLE_WITNESS_ON_EITHER_B1_ECOLOGY` | the two ecologies the six B1 runs used, both registered coefficient rows, exact charged replay | — | **DISCHARGED** | none: this record *is* an index audit. It names the index (ecology), reports the class values (0.7604–0.8021, 0.7188–0.7500) and corrects its own lane's denominator against its own interest |
| 32 | `RV-377-082` | `THE_FAILURE_ON_THE_OTHER_TWO_ECOLOGIES_IS_A_CEILING_NOT_A_MISSING_SETTING_OVER_68_ROWS` | `A` (68 rows, h × lr) × `F` (3); class maxima reported (0.8438, 0.8385) | — both halves indexed; the witness half is superseded on `J` by rule 36 and says so | **DISCHARGED** | none: ceiling confirmed to `h = 32` over 80 rows by `RV-377-089`; witness restated as `REACHED_UNDER_STANDARD_INTERVENTION_ONLY` |
| 33 | `RV-377-083` | `THE_COEFFICIENT_CARRIER_IS_NOT_RECOVERED_EVEN_WHERE_A_WITNESS_EXISTS__0_OF_3_GENUINE_TRIALS_ON_E_smooth1` | `S` (3), encoding (2: typed IR vs expression tree) | **`F` within the witness-bearing class** — `E_smooth1` was the only witness-bearing ecology known; `RV-377-102` has since found 4 720 DISCRIMINATING ecologies and 200 separating intervention-robust coefficient rows among the first 400 of them | **UNDER_SWEPT** | `RV-377-103` executes the `E_wit1` point and C1 holds there, so the terminal is superseded at one point of the index and unswept over the class. Cheapest remaining: 3 seeds on a second witness-bearing ecology from `eco_axis`'s enumeration, ~30 min |
| 34 | `RV-377-088` | `BOTH_NOT_OBSERVABLE_TERMINALS_ON_E_SMOOTH2_ARE_OVERTURNED__THE_DENSE_CLASS_HAS_AN_ADMISSIBLE_MEMBER_AT_BOTH_DEVELOPMENT_LENGTHS` | `A` (35 cells h × LR), columns (6), lengths (16, 48), `F` (3 as controls) | **`J` — the intervention set, and it is not merely defaulted, it is unnamed.** `STAGE_DE_SMOOTH_V30_DENSE_PARENT_MAXIMAL.json` contains **no occurrence of the string "intervention"**, and its `claim_ceiling` enumerates the seed index and the column index while omitting `J` entirely. Rule 36 was opened by `RV-377-085`, **three records earlier in the same lane** | **REQUIRES_RUN** | write an adapter exposing `smooth.S4Net` through `ecology.run_genotype` (`E_smooth2` = `spec_smooth(COEFFS_V2)`, `n_events` 16 and 48, criterion as the receipts used), then re-score the four admissible cells — `h3_lr0.25`, `h4_lr0.125`, `h6_lr0.125`, `h16_lr0.0625` — and the 16-event winner under all six registered interventions (`standard`, `no_revoke`, `double_revoke`, `half_events`, `shuffled_events`, `extra_unseen_feedback`). ~120 charged runs, under two minutes once the adapter exists. Report `min` over the six, per rule 36 |
| 35 | `RV-377-089` | `NO_COEFFICIENT_WITNESS_ON_E_SMOOTH3_OR_E_SYM5_OVER_80_ROWS_TO_H_32` | `A` (80 rows to h = 32), `F` (3), **`J` (all six registered interventions)** | `F` — truncated to 3 of 5, and recorded as such in its own `superseded_in_part_by` | **DISCHARGED** | none: both the parameter and the intervention indices are swept, the class maxima are reported, and the one truncated index is named by the record itself |
| 36 | `RV-377-089b` | `SIX_COEFFICIENT_ROWS_ON_E_SYM3_ARE_ADMISSIBLE_UNDER_ALL_SIX_INTERVENTIONS_WITH_MARGIN` | `A` (80 rows), `F` (all 5 registered), `J` (all six) | `N` — supplied afterwards by `RV-377-100`/`-101`: margin **+0.0156 = 0.375 fx units**, `WITHIN_QUANTIZATION`, on a NON_DISCRIMINATING ecology | **DISCHARGED** | none: every index is either swept or named by `narrowed_by`. The measurements stand; the reading does not |
| 37 | `RV-377-092` | `B2_4_EXECUTED_AT_SCOPE__14_OF_14_CLAUSES_HOLD` | k (3), budgets (2), representations (4), relation sets (6), every set partition enumerated | — | **VACUOUS** | not a class-level negative: a triage false positive, as V1 §2 marks it. The only universally quantified clause (`INDEPENDENT_OF_SEQUENCE_LENGTH`) is a positive invariance measured exhaustively over its declared index |
| 38 | `RV-377-097` | `B2_9_EXECUTED_AT_SCOPE__10_OF_14_CLAUSES_HOLD__THE_DISTINCT_STATE_COUNT_FAILS_BOTH_READINGS` | depths (5), drifts (4), precisions (3), arms (6), **every representable state enumerated** (256 / 4 096 / 65 536) | — | **VACUOUS** | not a class-level negative: a triage false positive. C1/C2/C7 are falsifications this record performed on its own frozen predictions, over an exhaustively enumerated index |

---

## 3. Counts

| classification | count | records |
|---|---|---|
| **DISCHARGED** | **13** | `-005`, `-009`, `-014`, `-015`, `-016`, `-023`, `-052`, `-058`, `-067`, `-081`, `-082`, `-089`, `-089b` |
| **UNDER_SWEPT** | **17** | `-029`, `-031`, `-038`, `-042`, `-046`, `-051`, `-056`, `-060`, `-063`, `-064`, `-065`, `-069`, `-070`, `-074`, `-075`, `-076`, `-083` |
| **VACUOUS** | **3** | `-011`, `-092`, `-097` |
| **REQUIRES_RUN** | **5** | `-028`, `-077`, `-079`, `-080`, `-088` |
| total | **38** | |

Movement against V1: V1 recorded 5 discharges against the declared population (6 listed, one of which is outside it).
V2 records 13, of which 8 are newly adjudicated from the corpus and 1 (`RV-377-074`, seed index) was discharged by a
run executed here. **One V1 discharge is withdrawn** — `RV-377-069`, on the null index — and **one V1 exemption is
withdrawn** — `RV-377-088`, on the intervention index.

### 3.1 Running score of the DG-7 rule itself

V1 §4 recorded "two negatives overturned, one upheld". V2's score, counting only indices actually re-run:

| index re-run | outcome |
|---|---|
| `A` on `E_smooth2` (`RV-377-088`) | **two negatives overturned** — *conditional on `J`, which was never swept (row 34)* |
| `A` to `h = 32` (`RV-377-089`) | one negative **upheld** |
| `F` from 3 to 5 (`RV-377-089b`) | one negative overturned, then **narrowed to `WITHIN_QUANTIZATION`** by `RV-377-100` |
| `S` on `E_smooth3` (`DG7-X1`, here) | the headline negative **upheld**, and its count reduced from 7 machines to 2 responses |
| `N` on `E_sym5` (`DG7-X2`, here) | one V1 discharge **withdrawn**; the census ceiling is the null |
| sign of `k` (`DG7-X3`, here) | the DG-9 audit's own attribution **found incomplete**; an eighth record enters the contaminated region |
| the DG-7 population (`DG7-X5`, here) | **41 negative-shaped terminals outside the declared 38** |

The rule is no longer "a rule that only ever overturns". Of the four indices re-run this session, three tightened a
negative or invalidated a discharge and none overturned a negative. That is what makes it a measuring instrument.

---

## 4. What DG-7 still blocks

**DG-7 as specified in V1 §3 blocks nothing, and that is the finding.** Its closure criterion is *"every record carries
an explicit index block — swept range or held default, per index — and every confirmed high-priority target has either
been re-run over the unswept index or has had its terminal narrowed in wording"*, with the note that **"narrowing the
wording is a full discharge"**. Under that criterion all 17 `UNDER_SWEPT` rows above can be closed by editing
sentences, without measuring anything. A gap that can be closed by wording cannot block a claim.

What DG-7 *does* block, once the criterion is read against rules 36, 38, 40 and 42 rather than against V1 §3:

1. **`B4` / `G10` — "predict a new form".** `RV-377-077` is `REQUIRES_RUN`. After `DG7-X1` its honest content is
   *two distinct developmental responses, on one ecology, at one budget, both equal to a known parent*. The ecology
   index is one point wide. `RV-377-102` has since enumerated the ecology axis completely over its declared class —
   6 561 targets, of which **4 720 are DISCRIMINATING** — and found, within the first 400 of them in canonical order,
   **200 coefficient-carrier rows that are admissible under all six registered interventions and separate from the
   best constant by at least one fx unit**. `E_smooth3`, the one ecology `B4` searched, carries **none** of them:
   `RV-377-089` swept 80 rows to `h = 32` there and found no coefficient witness at any setting. No unknown-form
   claim, positive or negative, may be made at programme scope until the pre-test has been run on at least one
   witness-bearing DISCRIMINATING ecology.
2. **The `E_smooth2` overturn, and with it DG-7's own credibility as a rule.** `RV-377-088` is `REQUIRES_RUN` on the
   intervention index. `RV-377-085` measured that **5 of 8 registered rows change admissibility status** between
   `standard` and the full family on `E_smooth1`, and `RV-377-082`'s structurally identical dense witness there fell
   from 0.8906 to 0.8281 / 0.7448 / 0.5260 under the family. Until the four admissible `E_smooth2` cells are scored
   under all six interventions, `BOTH_NOT_OBSERVABLE_TERMINALS_ON_E_SMOOTH2_ARE_OVERTURNED` is a
   standard-intervention-only claim, and the two original `NOT_OBSERVABLE` terminals of `RV-377-009` and `RV-377-014`
   are **not** safely withdrawn.
3. **Every capability ceiling reported without its null.** `DG7-X2` shows the corpus's largest exhaustive measurement
   — 336 242 genotypes — has a ceiling identical to a constant. Any other ceiling in the corpus reported before
   rule 40 is in the same position until its null is computed. The cheapest systematic closure is to extend
   `constant_control.audit()` from `ecology.REGISTRY` to **every ecology any receipt uses**, including `E_smooth2`,
   `E_smooth8`, `E_smooth8_div`, `E_bind16`, `E_rolefill`, `E_factored`, `E_spatial`, `E_causal`, `E_alias`,
   `E_obstruct` and the `B2` families. Four of those are supplied in §1.4; the rest are not.
4. **The negative-`k` half of the `E_sym` family.** `DG7-X3` shows the DG-9 audit swept `k ≥ 0` only and that its
   list of contaminated records omits `RV-377-060`. Every admissibility-shaped claim on `E_sym(k)` for `|k| ≤ 3` on
   either criterion, and `|k| = 4` on `all`, is void at theta = 0.85.
5. **DG-7's own population.** `DG7-X5` finds **41** negative-shaped terminals outside the declared 38, and finds that
   four of the declared 38 do not match the token set used here — so two regexes give two populations and neither is
   recorded. DG-7 cannot be declared closed until the triage predicate is written down and the population is derived
   from it.

DG-7 does **not** block: the `A`, `d`, `p`, `F` one-axis kingdom negatives (those are `DG-8`'s business, unchanged);
the blind-recovery negatives `RV-377-016`, `-023`, `-028` at the null level (§1.4 clears all three by 2.5 to 7.0 fx
units); or the `N10`/`N11`/`DC` reduction verdicts, whose defaulted indices are draw and capacity indices rather than
the indices their terminals quantify over.

---

## 5. The four kingdom-axis negatives and `DG-8` — unchanged

§5 of V1 stands verbatim and is not restated here. Its conclusion — *no cell off the diagonal of `A × d × p × F` has
ever been searched*, recorded as gap `DG-8` — is untouched by this audit. V2 adds one observation to it: the `p` axis
row (`RV-377-076`) sits at **two** ecologies, and `DG7-X3` shows the ecology index of this corpus is contaminated at
theta = 0.85 over an entire sub-family, so the off-diagonal sample `DG-8` calls for must draw its `F` coordinate from
the DISCRIMINATING set of `RV-377-102`'s enumeration and not from `ecology.REGISTRY`.

---

## 6. Preservation statement

No RED result, no failed clause, no negative terminal, no `FALSIFIED` verdict and no `result_terminal` string anywhere
in this repository has been deleted, softened, reworded or re-scoped by this lane. `REVIVAL_LEDGER*.jsonl` is not
modified by this commit. The V1 real-transfer RED endpoint, the grammar-bias and developmental falsifications, and
every one of `RV-377-046`'s five partial clause failures, `RV-377-060`'s three admissibility failures, `RV-377-063`'s
clause 4, `RV-377-065`'s five failed clauses, `RV-377-069`'s three failed clauses, `RV-377-075`'s refutation of this
programme's own precision-gated kingdom, `RV-377-079`'s and `-080`'s twin failures, `RV-377-097`'s four failed
clauses, `RV-377-100`'s `C1_FAILS` and `RV-377-102`'s `C2_FALSIFIED` stand exactly as written.

One of this lane's own frozen predictions is recorded as failed and is not repaired: the `E_smooth8_div` numeric band
in `DG7-X4` (predicted `[0.58, 0.74]`, measured `0.4521`). The other eleven frozen clauses held. In particular
`DG7-X1`'s falsifier did **not** fire: the headline negative this lane set out to attack on the seed index survived
the attack, and that is recorded here as an upholding rather than buried as a null result.
