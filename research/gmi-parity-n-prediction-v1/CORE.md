# Parity-n cost audit: current reading

Read the [current interval correction](INTERVAL_COST_CORRECTION_V1.md) first.

The [original preregistration and appended reports](PARITY_N_PREDICTION_PREREGISTRATION_V1.md)
remain byte-exact. They include reported executions; those reports are retained
evidence, with execution provenance and chronology unresolved by this unit.
The [original formula script](parity_n_derivation_v1.py) computes and prints
predictions only; it does not reproduce the reported candidate executions.

- A native **lower bound** can certify XOR is cheaper; it cannot certify
  delegation is cheaper or that equal lower endpoints are an exact tie.
- With the supplied lower bound 2n+1, XOR is certified for n<5.
- If native cost is instead declared **exactly** 2n+1 in the same additive units,
  the conditional crossover is XOR below5, tie at5, delegation above5.
- Neither 2n+1 nor a native-to-Python unit conversion is certified empirically.
  The authored count n+(n−1)+1 equals2n.

[Exact interval controls](test_parity_n_intervals_v1.py) ·
[model](parity_n_interval_model_v1.py) · [operations](OPERATIONS_V1.md) ·
[repair receipt](INTERVAL_REPAIR_RECEIPT_V1.json) ·
[original source bindings](raw/pr573-8bd474de/SOURCE_BINDINGS_V1.json)

No new candidate, campaign, timing or measurement is performed. This unit
remains outside the grand replay capsule and changes none of its inputs.
