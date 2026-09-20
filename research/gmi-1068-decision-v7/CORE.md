# Decisions without a world probability prior

This repair supplies a positive, conditional theory of information value.
Worlds, actions, loss, observation rules, admissible policies and costs are
declared. No probability distribution over worlds is used.

A refined deterministic observation preserves every coarse policy's loss
profile. For finite nonempty world/action sets and unrestricted deterministic policies,
this cannot increase the minimum worst-case loss. Conversely, universal improvement over binary decision
problems requires that refinement: a merged pair of distinguishable worlds
produces a counterexample. Buying information helps exactly when the improvement
exceeds its declared constant observation cost.

Read [the proofs](THEORY_V7.md), [formal statements](InformationOrderV7.lean),
and [primary-source ownership](PARENTS_V7.json).
[The reconciliation](../gmi-1068-recursive-audit-v7/RECONCILIATION_V7.md)
states what this contributes to R9/R10 and what remains open.

The finite executable compares all registered loss tables and signal partitions
through two implementations. Those checks instantiate the proved assumptions;
they do not estimate unknown losses or demonstrate generalization from samples.
Agent randomization is distinct from a world prior. Stochastic observations,
restricted policies and sequential adversaries need separate premises.

Reproduce from the repo on billy-laptop with Python >=3.10 and Lean 4.19.0:

```sh
/home/billy/.local/bin/python3.12 -I -B research/gmi-1068-decision-v7/check_decision_v7.py
/home/billy/.local/bin/python3.12 -I -O -B research/gmi-1068-recursive-audit-v7/check_snapshot_v7.py
/home/billy/.elan/bin/lean +leanprover/lean4:v4.19.0 -DwarningAsError=true research/gmi-1068-decision-v7/InformationOrderV7.lean
```

#1068 remains the control plane. #833 remains historical evidence.
This is not a complete theory of every machine intelligence form.
