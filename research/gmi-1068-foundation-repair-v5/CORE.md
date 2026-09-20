# #1068 foundation repair: start here

This successor corrects two foundational claims without changing frozen history.

- Admissible processes form a wide subcategory only if they contain identities
  and are closed under composition. Resource constraints can violate closure.
  Carrying remaining resources in the configuration restores a compositional
  model under explicit additive-cost assumptions.
- A scalar comparison across contexts needs a declared aggregation rule.
  It need not use probabilities: minimum and maximum are counterexamples.
  Expected utility remains the specialization that supplies weights.

Read [the proofs](THEORY_V5.md), [parent attribution](PARENTS_V5.json) and
[the Lean statements](AdmissibilityV5.lean). The independent finite oracle and
hostiles are replayed by `check_foundation_v5.py`; kernel checking is separate.

[R0–R17 reconciliation](../gmi-1068-recursive-audit-v5/RECONCILIATION_V5.md)
records the reverse dependency impact. Local repairs do not close entire rounds
or derive every machine intelligence family. #833 remains historical evidence.

Reproduce with Python >=3.10 and Lean 4.19.0. On billy-laptop, from the repo:

```sh
/home/billy/.local/bin/python3.12 -I -B research/gmi-1068-foundation-repair-v5/check_foundation_v5.py
/home/billy/.local/bin/python3.12 -I -O -B research/gmi-1068-recursive-audit-v5/check_snapshot_v5.py
/home/billy/.elan/bin/lean +leanprover/lean4:v4.19.0 -DwarningAsError=true research/gmi-1068-foundation-repair-v5/AdmissibilityV5.lean
```

The replay driver loads reviewed sibling modules explicitly; it is the isolated
Python entry point. The host's default Python 3.8 cannot run this package.
