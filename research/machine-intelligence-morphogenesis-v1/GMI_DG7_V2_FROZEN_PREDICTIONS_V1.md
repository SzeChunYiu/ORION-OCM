# DG-7 V2 — predictions frozen BEFORE execution

Lane: `worker-dg7-audit`. Base: `claude/gmi-d0-d1-research-dnbp8i` at `b6da57aa`.
Governing rules: 38, 39, 40, 42, 43 (`GMI_GAP_LEDGER_EXECUTED_V1.md` §5) and `GMI-DA11`.

This file is committed **before** any of the five experiments below is executed. Nothing in it may be edited after the
first run; failures are recorded verbatim in `GMI_DG7_INDEX_AUDIT_V2.md` alongside the frozen text.

Unit convention (rule 40): one `fx` unit = `1/(1.5*16) = 0.0416667` capability. A margin strictly below one fx unit is
`WITHIN_QUANTIZATION` and may not separate two mechanisms.

---

## DG7-X1 — `RV-377-077`, the programme's headline negative, on the SEED index

**The defect, established by inspection before any run.** `STAGE_B4_PRETEST_V1.json` — the receipt behind
`NO_UNKNOWN_FORM_AT_SCOPE__ALL_7_RECOVERED_MACHINES_ARE_EXACTLY_DEVELOPMENTALLY_EQUAL_TO_A_KNOWN_PARENT` — consumes
`STAGE_B1_ATROPHY_V1.json`, whose `receipts_examined` field reads

```
["STAGE_B1_ATROPHY_V1.json", "STAGE_B1_V33_B1_IR_RECOVERY_S0.json", "STAGE_B1_V33_B1_IR_RECOVERY_S1.json"]
```

— **two** seeds, under the pre-repair filenames that `RV-377-058` records as having been silently overwritten across
ecologies and later recovered from git history. Neither file exists on disk today. The ecology-keyed atrophy receipt
for the same ecology, `STAGE_B1_ATROPHY_SMOOTH3.json`, examines **three** receipts
(`..._E_smooth3_S0/S1/S2.json`) and carries **10** elites against V1's **7**.

**The run.** `gmi_microscope.atrophy_ir.b4_pretest(tag="DG7V2", eco_name="E_smooth3", catalogue_tag="V1",
atrophy_tag="SMOOTH3")`. Same catalogue, same instrument, same ecology, same theta, same code. The only index moved is
the one held at a default: the seed.

**Frozen prediction.**

1. `n_candidates` = **10**, not 7.
2. The number of DISTINCT response signatures among the candidates is **at most 3**.
3. `n_novel_at_response_resolution` = **0** — the headline negative survives the seed index.

**Frozen falsifier.** If (3) fails — any candidate whose final served answer vector matches no admissible parent's —
then `NO_UNKNOWN_FORM_AT_SCOPE` falls on the seed index exactly as `E_smooth2`'s `NOT_OBSERVABLE` fell on the parameter
axis, and the programme's headline negative is overturned by a run that changes no parameter of the experiment.

**Frozen consequence if (3) holds.** The terminal still may not keep the word `ALL_7`. Under rule 29 the count is
meaningless outside its triple, and under rule 39 the record must name the seed index. The honest restatement is
"N distinct developmental responses recovered on one ecology from three seeds", where N is the measured count of
distinct response signatures, not the row count of the receipt.

---

## DG7-X2 — `RV-377-069`, the exhaustive census, against the rule-40 null

`RV-377-069` enumerates 336 242 type-correct genotypes to size 7 on `E_sym5`, criterion `unseen`, 8 development
events, theta = 0.85, and reports a capability ceiling of **0.7917** at sizes 6 and 7 (`counts_by_size` in
`STAGE_G8_SIZE_CENSUS_LOWER_BOUNDS_V1.json`: 0.5833 / 0.6354 / 0.7188 / 0.7917 / 0.7917 at sizes 3–7). Rules 40 and 43
did not exist when it was recorded and it carries no null control.

**The run.** `gmi_microscope.constant_control.best_constant` on the `E_sym5` target over `smooth.UNSEEN`.

**Frozen prediction.** The best constant on `E_sym5|unseen` is **0.7917**, so the census's maximum over all 336 242
genotypes at sizes 6 and 7 exceeds the best machine that ignores its input and its feedback by **exactly 0.0000 fx
units** — `WITHIN_QUANTIZATION`, and in fact exact equality.

**Frozen falsifier.** A best constant strictly below 0.7917 by one fx unit or more, which would mean the census did
find structure the null does not have.

---

## DG7-X3 — the DG-9 constant-control audit is itself under-swept on the SIGN index

`gmi_microscope/constant_control.py::audit` sweeps `E_sym(k)` for `k = 0..16` — **non-negative k only**.
`RV-377-060` adjudicates 2 640 predicted cells on `E_sym(k)` for `k in {1, -1, -2, -3, -4, 10, 12, 13}`, criterion
`unseen` (read from `STAGE_DE_SMOOTH_V34_SYM1_H.json`'s own `ecology` block). `RV-377-101` names seven records as
touching the non-discriminating region — `RV-377-035, -039, -040, -085, -089, -089b, -100` — and `RV-377-060` is not
among them.

**The run.** `best_constant` on `E_sym(k)` for `k = -16..16` under both criteria.

**Frozen prediction.**

1. The best-constant capability is **exactly symmetric** under `k -> -k` for every k and both criteria.
2. Therefore `E_sym(-1)`, `E_sym(-2)`, `E_sym(-3)` are `NON_DISCRIMINATING` on the `unseen` criterion and `E_sym(-4)`
   is `NON_DISCRIMINATING` on `all` only.
3. **4 of `RV-377-060`'s 8 ecologies** (`k = 1, -1, -2, -3`) are `NON_DISCRIMINATING` under the criterion the record
   itself ran, so `RV-377-060` is an **eighth** record touching the contaminated region and `RV-377-101`'s
   record-attribution is incomplete.

**Frozen falsifier.** Any asymmetry between `k` and `-k` in the best-constant capability, which would mean the
symmetry argument is wrong and the negative-k half must be reported on its own.

---

## DG7-X4 — best-constant controls that have never been computed at all

`constant_control.audit` covers 42 ecology-criterion pairs, all inside `ecology.REGISTRY` plus the `E_sym(k)` sweep.
The following ecologies carry class-level negative terminals in the DG-7 population and appear in **no** DG-9 row:

| ecology | records |
|---|---|
| `E_smooth2` (`smooth.COEFFS_V2`) | `RV-377-009`, `-014`, `-088` (and `-005` by inheritance) |
| `E_smooth8` (256 inputs, 8 coefficients) | `RV-377-011`, `-015`, `-016` |
| `E_smooth8_div` (four targets) | `RV-377-023`, `-028` |

**The run.** `best_constant` on each, using each ecology's own evaluation set (`all_x`) and its own
`1 - mean|out - y|/1.5` metric; `E_smooth8_div` scored as the mean over its four declared targets, as `run_candidate_div` does.

**Frozen prediction.** All are `DISCRIMINATING` (best constant strictly below theta = 0.85):
`E_smooth2` in **[0.68, 0.80]** on both criteria; `E_smooth8` in **[0.58, 0.74]**; `E_smooth8_div` in **[0.58, 0.74]**.

**Frozen falsifier.** Any best constant at or above 0.85 — which would make the corresponding `NOT_OBSERVABLE` /
`NO_WINNER_AT_THETA` terminals false as written, since a constant would then be an admissible row they missed.

---

## DG7-X5 — the DG-7 population is itself an index held at a default

`GMI_DG7_INDEX_AUDIT_V1.md` opens with "38 terminals match the negative pattern", from "a keyword triage over the full
text of every ledger record". The pattern is not recorded anywhere, so the population of the audit is an inherited
default in exactly the sense rule 39 forbids.

**The run.** Count records in `REVIVAL_LEDGER*.jsonl` whose `result_terminal` contains any of
`NO_`, `NOT_`, `FALSIF`, `FAIL`, `REFUT`, `NEGATIVE`, `BOUNDED`, `CEILING`, `INADMISS`, `ABSENT`, `UNREACH`,
`IMPOSSIB`, `CANNOT`, `ZERO_` (case-insensitive) and are **not** among the declared 38.

**Frozen prediction.** At least **20** such records exist, so the declared 38 is a strict subset of the negative
terminals in the corpus and DG-7 cannot close by discharging 38 rows.

**Frozen falsifier.** Fewer than 20 — the triage was near-complete and the population defect is cosmetic.

---

## What is NOT run here, and why

* `RV-377-077` on an ecology other than `E_smooth3` (the `DG-7` §1.1 target) — needs a 20 000-evaluation B1 recovery
  run per seed per ecology. Specified in V2 as `REQUIRES_RUN`, not executed.
* The `DG-8` off-diagonal sample of `A x d x p x F` — not affordable, specified only.
* Re-running the size census past 7 nodes — exponential; the cost must be registered before it is spent
  (`RV-377-069`'s own discharge note).

## Standing constraint

No RED result, failed clause, or negative terminal anywhere in this repository is deleted, softened or reworded by
this lane. Where a terminal is narrowed, the original text is preserved verbatim beside the narrowing, as
`result_terminal` / `result_terminal_narrowed` already does in the ledger.
