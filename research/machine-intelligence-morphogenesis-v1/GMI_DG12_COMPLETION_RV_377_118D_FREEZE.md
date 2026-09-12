# RV-377-118 Lane D — FREEZE: DG-12 completion on the twelve unaudited modules

Frozen BEFORE any unit of lane `RV118-D` runs. This record is what flips the twelve `U-D-*` units of
`GMI_WORK_MANIFEST_V1.json` from `frozen: false` to `frozen: true`; `gmi_work.py run` refuses them
otherwise.

## What was frozen before this record, and is restated unchanged

`GMI_DISTRIBUTED_BATCH_RV_377_118_FREEZE.md` §Lane D, verbatim:

> **Prediction D1:** at least one further degenerate or near-degenerate obligation is found
> among the 12. `e1_scdi` regime B was degenerate on 57.7 % of its coefficient space, and
> nothing suggests it is unique.

The twelve modules are the set `RV-377-112` (`GMI_DG12_OBLIGATION_DEGENERACY_RV_377_112.md`
§"What this audit does NOT cover") listed as **not covered** and "listed as uncovered rather than
presumed clean":

```
axis_a.py   b1x.py   b2_common.py   b2_depth.py   b2_norm.py   b2_prenorm.py
e1_cp.py    e1_iql.py   e1_lmhm.py   e1_vgsc.py   e1_vlc.py   refine_f.py
```

## The falsifier

D1 **fails** if every obligation that any of the twelve modules declares or scores, over its own
registered evaluation set, is `NON_DEGENERATE` (or at most `SKEWED_BINARY`) under the `RV-377-112`
classifier. A failed D1 is a preserved negative with a diagnosis. It is never re-run to flip it.

## The adjudication rule, fixed now

* Classifier: `degeneracy_audit._classify`, byte-identical to `RV-377-112`. One distinct answer →
  `DEGENERATE__OBLIGATION_IS_A_CONSTANT`; best constant agrees on ≥ 85 % →
  `NEAR_DEGENERATE__CONSTANT_AGREES_ON_>=85%`; binary with the minority class ≤ max(1, n/10) →
  `SKEWED_BINARY`; otherwise `NON_DEGENERATE`.
* Scope of a verdict: a module's **own** obligation over its **registered** evaluation set — the set
  the module's `run()` scores capability on, at the coefficients / stream / grid it scores them at.
  Rows computed on a larger informational set (the complete query space, the unscored first half of a
  stream, development-time coefficients) are reported and do **not** decide. Rows a module merely
  **inherits** from `ecology.REGISTRY` (`b1x`) are reported as inherited and do not count as
  "further": they were already audited in `RV-377-112`.
* `SKEWED_BINARY` does not count toward D1, exactly as `RV-377-112` did not count it as
  near-degenerate.
* A module with no obligation of this shape (an instrument library; a separation instrument whose
  verdict is candidate-vs-parent agreement) is recorded `NOT_APPLICABLE` with the reason, not
  presumed clean and not presumed degenerate.
* D1 **HELD** iff at least one module's verdict is `DEGENERATE_OBLIGATION_FOUND` or
  `NEAR_DEGENERATE_OBLIGATION_FOUND`. Otherwise **FAILED**.
* Rule 40's best-constant control is reported alongside every registered row, in the metric the
  module actually scores with (exact agreement within 0 or 1 fx; the B1 mean-absolute-error
  capability for the inherited smooth rows), on the same coefficient vectors `constant_control.py`
  (`RV-377-108`) uses. It is informational for D1; rule 45 decides on the distinct-answer count.

## Where each module's obligation is read from (declared now, before the run)

| module | obligation (truth function) | registered evaluation set | metric |
|---|---|---|---|
| `axis_a` | `truth(mode, stream(T, seed=0))`, modes ACC / PARITY / MAXV | the scored second half `t ∈ [T/2, T)` of each stream, `T ∈ {4, 8, 16, 32, 64}` | exact |
| `b1x` | none of its own — `ecology.REGISTRY` targets via `b1.evaluate` | `smooth.UNSEEN` (criterion `unseen`) | MAE capability (inherited, RV-377-112) |
| `b2_common` | none — instrument library | — | NOT_APPLICABLE |
| `b2_depth` | `obligation(x)`: input band of 4 | `GRID`, 256 states | exact class |
| `b2_norm` | `obligation(x, F)`: input band of 4 | `Fixed(t, f).grid()` for `(8,4) (12,6) (16,8)` | exact class |
| `b2_prenorm` | `obligation(x)`: input band of 4 | `GRID`, 256 states | exact class |
| `e1_cp` | `truth_regime` A / B / C | `e1_vlc.EVAL_QUERIES` (24) at the coefficients after the cell's U revision windows, per cell (PPLUS, N1, N2, N3; N3 serves B/C from independent coefficients) | A within 1 fx; B, C exact |
| `e1_iql` | `target_vector(d)`: 25 interventional answers | the 25 answers, at each of the 16 ground-truth orientations | exact |
| `e1_lmhm` | `e1_vlc.truth` | `EVAL_QUERIES` after 16 heterogeneous rounds | within 1 fx |
| `e1_vgsc` | `e1_vlc.truth` | `EVAL_QUERIES` after the cell's 16-step sequence, per `PA*` cell | within 1 fx |
| `e1_vlc` | `truth` | `EVAL_BY_SIZE[scope]` after the cell's `U`/`cone` revisions, per `CELLS` and `COLLISION_CELLS` | within 1 fx |
| `refine_f` | its own `REGIME_E` (`_f6_truth`) plus the imported `e1_scdi.truth_regime` A–D, as `suite_f6` serves them | `EVAL_QUERIES` at the registered coefficients | exact; other suites NOT_APPLICABLE (agreement verdicts) |

The E1 coefficient replays (`_coeffs_cp`, `_coeffs_lmhm`, `_coeffs_vgsc`, `_coeffs_vlc`,
`_alias_targets`) are **reused** from `constant_control.py`, not re-implemented, so the DG-12 count and
the rule-40 control are computed on identical vectors. The `e1_cp` receipt also carries the
`RV-377-112` coefficient-space sweep (65 536 assignments) on `e1_cp`'s own `truth_regime`.

## What was added after the RV-377-118 freeze

Only instrument code and bookkeeping:

* `gmi_microscope/degeneracy_audit.py`: `audit_module(name, host)` and `audit_all_modules(host)`.
  `_classify` and the RV-377-112 functions are untouched.
* `GMI_WORK_MANIFEST_V1.json` / `gen_work_manifest_v2.py`: the twelve `U-D-*` units flipped to
  `frozen: true` (`revival_id: RV-377-118`), receipt paths
  `microscopes/results/STAGE_DG12_COMPLETION_<name>_{HOST}.json`, `host='{HOST}'` passed explicitly.
* This record. No prediction, threshold, classifier or evaluation set was changed.

## Receipts

Per module: `microscopes/results/STAGE_DG12_COMPLETION_<name>_{HOST}.json` (deterministic; the
sha256 of every source file that determines the obligation is recorded under `inputs_sha256`;
`content_sha256` excludes host and timing so two hosts must agree byte-for-byte on it).
Aggregate: `microscopes/results/STAGE_DG12_COMPLETION_{HOST}.json`, which adjudicates D1 by the rule
above. Host for this lane: `old` (laptop billy-old), one niced process.

## Adjudication (2026-09-12, after the run; nothing above this line is edited)

Run on laptop billy-old from freeze commit `3e91942e` (tree rsynced and md5-verified both ways), one
niced process, through `gmi_work.py claim/run --host old`; the 12 `U-D-*` units are marked `done`.
A first invocation via `audit_all_modules("old")` and the `gmi_work.py` re-execution produced
**byte-identical `content_sha256`** on all 12 receipts. `test_gmi_dg12_degeneracy_audit.py` +
`test_gmi_microscope.py`: 68 passed on the same host. Aggregate receipt
`microscopes/results/STAGE_DG12_COMPLETION_old.json`, `content_sha256 af33d844…`.

### D1 — **HELD**

Findings in **3 of 11** auditable modules (`b2_common` is `NOT_APPLICABLE`): **11** own-registered rows
`DEGENERATE` or `NEAR_DEGENERATE`, 10 of them beyond the `e1_scdi` construction.

| module | verdict | own registered rows | finding (module's own obligation, registered evaluation set) | rule 40 already knew? |
|---|---|---|---|---|
| `axis_a` | **DEGENERATE_OBLIGATION_FOUND** | 15: 6 DEG, 2 SKEWED, 7 NON | `MAXV` is the constant 15 (12 at T = 4) on the scored second half at **every** T ∈ {4, 8, 16, 32, 64}; `PARITY` at T = 4 is the constant 0 (2 scored events). `ACC` T = 4 and `PARITY` T = 8 are `SKEWED_BINARY` (2- and 4-event windows). | yes, incidentally: the RV-377-072 receipt voids exactly these cells (`rule22_void_modes = [MAXV, PARITY]`, 36 of 90 cells) |
| `b1x` | inherited only | 0 (12 inherited, all NON) | no obligation of its own; `ecology.REGISTRY` targets under criterion `unseen`, already `RV-377-112` | — |
| `b2_common` | NOT_APPLICABLE | 0 | instrument library, no obligation | — |
| `b2_depth` | all NON_DEGENERATE | 1 | 4 bands × 64 over 256 states, best constant 0.25 | — |
| `b2_norm` | all NON_DEGENERATE | 3 | 4 equal bands at (8,4), (12,6), (16,8) | — |
| `b2_prenorm` | all NON_DEGENERATE | 1 | 4 bands × 64 over 256 | — |
| `e1_cp` | **NEAR_DEGENERATE_OBLIGATION_FOUND** | 10: 3 NEAR, 7 NON | regime **B** at the final coefficients: 21/24 identical (`PPLUS`, `N2_DENSE_ACTIVITY`), 23/24 (`N3_NO_SHARED_SEMANTICS`); at the development coefficients regime B is `DEGENERATE` 24/24, exactly `e1_scdi`; its coefficient space is degenerate on **37 824 / 65 536 = 0.5771** (same function, same count); regime C 73/65 536, regime A 0. | yes: RV-377-108 `B_shared` 0.875 and `B_N3_independent` 0.9583 `NON_DISCRIMINATING` |
| `e1_iql` | all NON_DEGENERATE | 16 | best constant 0.52–0.64 over the 25 answers at every orientation | — |
| `e1_lmhm` | all NON_DEGENERATE | 1 | 5 distinct / 24 after 16 rounds, best constant 0.2917 | — |
| `e1_vgsc` | all NON_DEGENERATE | 5 | all `PA*` cells | — |
| `e1_vlc` | all NON_DEGENERATE | 9: 7 NON, 2 SKEWED | `CQU2` / `CQU4` global-scope sets are `SKEWED_BINARY` 3:1 over **4** queries (best constant 0.75 < θ; not counted) | — |
| `refine_f` | **DEGENERATE_OBLIGATION_FOUND** | 5: 2 DEG, 3 NON | `suite_f6` regime **E** (refine_f's own fifth serving regime, 1 iff the scope sum > 0) is the constant 1 on all 24 `EVAL_QUERIES`; regime B (re-imported from `e1_scdi`) likewise. Regimes A, C, D non-degenerate. Seven other suites `NOT_APPLICABLE` (agreement verdicts, no truth-scored obligation). | no: refine_f takes no verdict against a truth, so nothing could have caught E |

### What the findings do to standing claims (bounded, per module)

* **`RV-377-072` (axis_a).** Nothing new is voided. The module already excluded `MAXV` at every T and
  `PARITY` at T = 4 from the rule-22-valid cells and reports frontier occupancy on valid cells
  separately. What changes is the reading: those obligations are not "easy for a constant", they
  **are** constants on the scored window. The `ITERMAP == TAB_RMW` equality is a served-answer
  comparison and does not depend on the obligation carrying information.
* **`RV-377-033` (e1_cp).** A constant emitter of 1 is admissible in regime B on `PPLUS`, `N2` and
  `N3` (0.875 / 0.875 / 0.9583 ≥ 0.85), so the regime-B clause of the every-regime admissibility rule
  binds nothing, and the cross-regime transfer reading (CP-5 / ability B1) in regime B rests on 3
  (`PPLUS`, `N2`) or 1 (`N3`) of 24 queries. Regime C (11 : 13) remains the informative transfer regime.
* **`RV-377-070` (refine_f).** `P13` (SCDI vs UNIVERSAL) splits first on `OVERFLOW` and the verdict
  stands. The `COMPOSITIONAL_UNSEEN` demand's 24 differing cells are candidate 1 vs parent abstention
  on a constant obligation: the demand witnesses **abstention**, not derivation. The regime-B and
  regime-E parts of the `ABSTAIN_OBLIGATION` `B_risk` score (48 of 120 scored cells per pair) carry no
  information. `P12` and `P14` are `EQUAL` on every demand and unaffected.

### Terminal

| terminal | value |
|---|---|
| `DG-12_CLOSED` | **TRUE** as an audit, at registered scope (12 of 12 modules: 11 audited, 1 NOT_APPLICABLE with reason) |
| `NO_DEGENERATE_OBLIGATION_AT_REGISTERED_SCOPE` | **FALSE**, now on 4 modules (`e1_scdi`, `axis_a`, `e1_cp`, `refine_f`) rather than 1 |
| `REGISTERED_SMOOTH_TABLE_OBLIGATIONS_NON_DEGENERATE` | **TRUE**, 12 of 12 (unchanged; `b1x` inherits them) |
| `RV-377-118D_D1` | **HELD** |

### Residual gap (named, not claimed)

The degenerate constructions are not repaired here: a repair (a τ or coefficient grid for regime B, a
sign regime over signed factors for E, a scored window that starts before the running max saturates
for `MAXV`) re-points historical claims and is DG-13-class work. Rule 45 is still enforced by a
post-hoc receipt, not by a precondition inside each module's `run()`.

Ledger: `REVIVAL_LEDGER.jsonl` row `RV-377-118D`. Theorem: `GMI_COMPLETENESS_BOUNDARY_THEOREM_V1.md`
addendum V1.3 (RV-377-118D).
