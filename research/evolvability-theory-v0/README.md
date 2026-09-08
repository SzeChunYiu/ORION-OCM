# Evolvability Theory V0 synthetic falsification lane

This directory supports `docs/spec/MACHINE_EPISTEMICS_EVOLVABILITY_THEORY_V0.md`.

Status: **E2 exploratory synthetic only.** It is not evidence that current OCM has a self-evolution advantage and it is not a neural-network comparison.

Run:

```bash
python research/evolvability-theory-v0/synthetic_evolvability.py \
  --output /tmp/SYNTHETIC_RESULTS_V0.json
```

The committed `SYNTHETIC_RESULTS_V0.json` is the V0 reference output.

The harness pressures two theory claims:

1. diagnosis-guided repair is useful only when probe/diagnosis cost is smaller than the repair-search work it removes;
2. learned causal factorization can improve a repeated adaptation quality/resource frontier in sparse/stable interaction regimes, while dense coupling and structural drift reduce or remove the advantage.

The evolutionary comparator is deliberately **not** treated as strongest-parent closure. Later confirmatory work must include stronger learned black-box/surrogate, AutoML, meta-learning and neural adaptation parents under #144.
