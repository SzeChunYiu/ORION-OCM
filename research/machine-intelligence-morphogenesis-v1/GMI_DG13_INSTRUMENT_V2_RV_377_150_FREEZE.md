# RV-377-150 — FREEZE: DG-13 closed additively (V2 instruments), predictions before any run

DG-13 (`GMI_DG13_INSTRUMENT_DEFECTS_RV_377_114.md`, boundary theorem F6) left two registered
instruments unrepaired because repairing them in place re-points historical claims:

1. `extra_unseen_feedback` trains on `UNSEEN[:4]` and then scores all 8 `UNSEEN` inputs — a 50 % leak in one
   of the six bars rule 36 requires.
2. `ecology.REGISTRY["E_parity"]`'s target is the identity `0..15`, not parity.

## Root cause (one stage each, from the code)

* (2) is a **constructor** defect: `spec_table(smooth.make_parity_target(), …)` iterates the target
  *dict*, whose keys are `0..15`; `make_parity_target()` itself is correct parity (`fx(1)` on odd popcount).
* (1) is a **scoring** defect: the intervention adds development on four unseen inputs but the criterion
  still scores those same inputs.

## Repair — additive, V1 untouched

* `INTERVENTIONS["extra_unseen_feedback_v2"] = {extra: True, score: "unrevealed"}`: same extra feedback on
  `UNSEEN[:4]`, capability scored on `UNSEEN[4:]` only. `INTERVENTION_FAMILY_V2` = the five trustworthy V1
  interventions + V2.
* `REGISTRY["E_parity_v2"]` = the parity *values* (`fx 0 / 16`) under a new name with criterion `all` (see P2 for why
  `unseen` is degenerate for parity); `E_parity` keeps its historical table and gains `deprecated_reason`.
* `test_gmi_dg13_v2.py` pins all three facts and that V1 objects are byte-identical.

## Frozen predictions

| id | prediction | falsifier |
|---|---|---|
| **P1** | Re-scoring the 9 registered zoo rows on the 4 rule-40 discriminating ecologies (36 row×ecology cells) under family V2 instead of V1 changes the rule-36 admissibility verdict on **≤ 10 %** of cells (RV-377-114 recomputed T1 on the leak-free five and found it unchanged; the leak was not load-bearing) | > 10 % of cells change |
| **P2** | The registered split is parity-separating: every `TRAIN` input has even popcount and every `UNSEEN` input odd, so on the `unseen` criterion the parity target is the constant `fx(1)` (best constant = 1.0, DEGENERATE by rule 45). `E_parity_v2` is therefore registered with criterion `all`, where the best constant on the 16 inputs is exactly `1 − (8·16/16)/(16·1.5) = 0.6667` (rule-40 discriminating), and **no registered zoo row is admissible** under family V2 (no row is XOR-closed; RV-024's GF(2) occupant is not in the zoo) | best constant on UNSEEN ≠ 1.0, best constant on ALL ≠ 0.6667, or a zoo row admissible |
| **P3** | On the historical `E_parity` (identity table) the exemplar/knn rows that were WITHIN_QUANTIZATION in RV-377-108 keep their V1 numbers to the digit under the V1 family (regression guard) | any V1 capability changes |

Kill condition: if P1 fails, the leak WAS load-bearing for the zoo verdicts and every rule-36 verdict in the
corpus taken under V1 must carry the qualification "under the leaky V1 family"; that is recorded, not
retuned. Receipt `microscopes/results/STAGE_DG13_V2_{HOST}.json`. Ledger row RV-377-150. Terminal names:
`DG13_CLOSED_ADDITIVELY__V2_INSTRUMENTS_REGISTERED__ZOO_VERDICTS_STABLE` /
`…__ZOO_VERDICTS_MOVE_<n>_OF_36`.

---

# RV-377-150 — ADJUDICATION (receipt `STAGE_DG13_V2_old.json`, sha `0cd94d356c22d538…`, billy-old)

| id | outcome |
|---|---|
| **P1** | **HELD** — 3 of 36 cells (8.33 %) change rule-36 admissibility under family V2: `E_smooth1 | hamming_knn_k3` (min 0.8646 → 0.8438), `E_smooth3 | soft_retrieval` (0.8542 → 0.8438), `E_sym5 | hamming_knn_k3` (0.8542 → 0.8021). All three are **store-reading rows losing admissibility once the leak is closed**; no row gains. |
| **P2** | **HELD** — best constant on `UNSEEN` for the parity values is exactly 1.0 (constant 16: every unseen input has odd popcount), so the `unseen` criterion is DEGENERATE for parity; on `ALL` the best constant is exactly 0.6667 (constant 0); no registered zoo row is admissible on `E_parity_v2` (best row 0.6667 = the constant). |
| **P3** | **HELD by construction** — the V1 objects are byte-identical (test pinned); the historical `E_parity` block reproduces RV-377-108's classification (hamming_knn 0.8333 = best constant 0.8333, WITHIN_QUANTIZATION; program_search / compiled_search 0.9583 admissible on the identity table). |

## What the closure changes

`GMI-DA9` (RV-377-085/086) recorded that the store rows' capability **rises** under `extra_unseen_feedback`
on some ecologies and used it as evidence that exactness buys intervention robustness while stores are
fragile to `extra_unseen_feedback`. Under the leak-free V2, the rise is the leak: the three rows whose
V1 admissibility depended on being scored on inputs they had just been fed are inadmissible under V2.
Every rule-36 verdict in the corpus taken under V1 therefore carries the qualification "admissible under
the V1 family, whose sixth bar leaked"; the qualification moves 3 of 36 registered-zoo cells and no
searched-genotype verdict was re-scored here (owed: RV-377-113's seven carrier recoveries and the
lane-B nine seeds under V2 — a mechanical rescoring, queued for the class-rate lane's atrophy pass).

Terminal: `DG13_CLOSED_ADDITIVELY__V2_INSTRUMENTS_REGISTERED__ZOO_VERDICTS_MOVE_3_OF_36`.
Boundary-theorem terminals: `ALL_REGISTERED_INTERVENTIONS_MEASURE_WHAT_THEY_CLAIM` → **TRUE for family V2**
(FALSE for V1, preserved); `ALL_REGISTERED_ECOLOGIES_ARE_WHAT_THEY_ARE_NAMED` → **TRUE with E_parity_v2
registered** (`E_parity` keeps its deprecated_reason). New finding for rule 45: the registered
TRAIN/UNSEEN split is parity-separating, so any parity-type obligation is degenerate on the `unseen`
criterion — a construction fact that explains RV-377-108's WITHIN_QUANTIZATION reading of E_parity.
