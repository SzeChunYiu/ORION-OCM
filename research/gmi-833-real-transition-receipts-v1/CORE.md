# gmi-833-real-transition-receipts-v1

First real-system evidence package for the #833 Section-J row `Validate at least 5 transitions on real systems` (#903). Executes the fail-closed protocol from `gmi-833-real-transition-protocol-v1` against real trained systems.

Chain of custody:

1. `FREEZE_V1.md` @ `cd6196aa5` — complete pre-outcome predictions (task family, per-system registered grid, law, controls), pushed before any training.
2. Machinery smoke exposed the uniform-bit premise failure on real sources (stateless floor is data-derived, not `1/2`).
3. `FREEZE_V2_AMENDMENT.md` @ `c3fbf5b11` — registered revival: empirical stateless floor, amended blind classification rule, exact licensed transition band `1/8 < E0 < 3/8`; V1 predictions unchanged.
4. Full-scale training of six registered real systems (torch, CPU, registered seeds), then deterministic receipt building.

Reproduce (no torch needed):

```bash
python -I -B research/gmi-833-real-transition-receipts-v1/test_real_transition_receipts_v1.py -v
python -I -O -B research/gmi-833-real-transition-receipts-v1/test_real_transition_receipts_v1.py -v
python -I -B research/gmi-833-real-transition-receipts-v1/real_transition_receipts_v1.py
```

The deterministic stage rebuilds per-setting evaluation artifacts from committed `REAL_RUNS/` and byte-compares against `RESULT_V1.json` in CI. Scientific row status is decided solely by the protocol terminal recorded in `RESULT_V1.json`.
