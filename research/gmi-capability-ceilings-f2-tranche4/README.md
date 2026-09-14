# GMI capability ceilings — #602 F2 tranche 4

Final two bounded G2 F2 theorem rows:

1. information-acquisition budget -> uncertainty-resolution ceiling;
2. social observation -> theory-of-mind identifiability ceiling.

Together with merged #640, #641 and #642, these complete the **eleven listed F2 bounded ceiling/lower-bound rows**. This is theorem-registry closure at G2, not the G6 morphology-to-capability map.

Run:

```bash
python3 -I -B research/gmi-capability-ceilings-f2-tranche4/test_capability_ceilings_tranche4_v1.py -v
python3 -I -O -B research/gmi-capability-ceilings-f2-tranche4/test_capability_ceilings_tranche4_v1.py -v
```

Artifacts:

- `F2_TRANCHE4_CEILINGS_V1.json` — exact theorem/parent/falsifier rows;
- `FORMALIZATION_V1.md` — proofs, parent subtraction, counterexamples and claim boundary;
- `capability_ceilings_tranche4_v1.py` — exact finite witnesses;
- `test_capability_ceilings_tranche4_v1.py` — constructive and hostile controls.
