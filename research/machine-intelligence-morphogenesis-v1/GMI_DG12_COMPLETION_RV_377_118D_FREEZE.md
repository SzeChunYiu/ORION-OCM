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

## Adjudication

Filled in after the run. Nothing above this line is edited.
