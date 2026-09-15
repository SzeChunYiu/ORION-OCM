# gmi-unseen-form-prediction-v1

Exact finite closure of #602 V6 (unseen-form prediction, 6 boxes) and partial
#592 item 39 (W2/W3 green; W4 not claimed; phase-hole occupant claim refused).

## Artifacts

- `FREEZE_V1.md` — property-first prediction frozen before search
- `FORMALIZATION_V1.md` — theorems, box ledger, claim ceiling
- `unseen_form_prediction_v1.py` — executable witness
- `test_unseen_form_prediction_v1.py` — 13 unit tests
- `RESULT_V1.json` — campaign receipt
- `.github/workflows/gmi-unseen-form-prediction-v1.yml` — CI

## Claim ceiling

```text
UNSEEN_FORM_PREDICTION_SUPPORTED_AT_REGISTERED_SCOPE
NOVEL_INTEL_LADDER_W2_W3_GREEN_AT_EXACT_RQM_SCOPE__W4_NOT_CLAIMED
```

## Run

```bash
python test_unseen_form_prediction_v1.py -v
python unseen_form_prediction_v1.py
```
