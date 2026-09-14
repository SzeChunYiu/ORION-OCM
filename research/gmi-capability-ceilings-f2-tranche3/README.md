# GMI capability ceilings — #602 F2 tranche 3

Three exact bounded G2 ceilings:

1. planning resource -> guaranteed exhaustive horizon;
2. unstructured search budget -> worst-case verified-solution class;
3. verification budget -> false-adoption floor.

Artifacts:

- `F2_TRANCHE3_CEILINGS_V1.json` — machine-readable theorem/falsifier registry;
- `FORMALIZATION_V1.md` — proofs, parent subtraction, nearest counterexamples and claim boundaries;
- `capability_ceilings_tranche3_v1.py` — exact arithmetic and finite adversarial witnesses;
- `test_capability_ceilings_tranche3_v1.py` — constructive + hostile controls.

Run:

```bash
python3 -I -B research/gmi-capability-ceilings-f2-tranche3/test_capability_ceilings_tranche3_v1.py -v
python3 -I -O -B research/gmi-capability-ceilings-f2-tranche3/test_capability_ceilings_tranche3_v1.py -v
```

Claim ceiling: **G2**. This does not establish a G6 morphology-to-capability predictor.
