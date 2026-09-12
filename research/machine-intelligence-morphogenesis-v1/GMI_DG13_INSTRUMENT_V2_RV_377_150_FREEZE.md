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
