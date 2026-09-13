# Adaptive row confidence

The fixed-N model-confidence result now permits unequal, history-dependent
row counts and adaptive stopping within one supplied finite model contract.
One simultaneous confidence event supports all later finite-horizon policy
choices under the existing FMT transfer theorem.

- [Proof and precise sampling assumptions](ADAPTIVE_ROW_CONFIDENCE_THEOREM_V1.md)
- [Exact evidence](ADAPTIVE_ROW_CONFIDENCE_RECEIPT_V1.json)
- [Execution, parents and cost scope](OPERATIONS_V1.md)
- [Registered assumptions](ASSUMPTIONS_V1.json)
- [Complete packet binding](MANIFEST.json)

This is an application of established confidence-sequence and finite-alphabet
concentration methods. Its rational implementation is conservative. Fresh
conditional row laws, supplied support and sufficient state remain premises;
the checker does not authenticate a physical sampler or infer those facts.

Original fixed-look procedures remain valid at their fixed looks. An explicit
optional-monitoring counterexample and repair show what changes when the
data determine when to stop.
