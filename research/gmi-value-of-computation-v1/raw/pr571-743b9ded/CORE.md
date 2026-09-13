# Value of computation and exact stopping: read first

Ledger item 10. Makes the choice of *which computation or experiment to run next*
a metalevel decision with the deliberation's own charge booked to the resource
ledger, and supplies the termination and exactness certificates that decision
needs.

- [Theorem VOC-1–6](VALUE_OF_COMPUTATION_THEOREM_V1.md)
- [Exact witnesses](test_value_of_computation_v1.py) — rational counterexamples;
  they freeze the refutations, they do not prove the analytic theorems.

Closes the three gaps that [`metareasoning-parent-review-v1`](../metareasoning-parent-review-v1/CORE.md)
recorded as open tasks: the termination-assumption gap (**VOC-1/2/3**), the
exactness-certification gap (**VOC-6**) and the contradictory stopping guidance
(**VOC-5**). The stopping rule is *derived* in VOC-3 — continue iff the value of
computation strictly exceeds its charge — rather than assumed.

Status: **NOT REGISTERED IN THE REPLAY CAPSULE.** Deliberately outside
`research/gmi-grand-unification-v1/`. Mechanisms are inherited from Hay–Russell–
Tolpin–Shimony, Bertsekas, Russell–Wefald and the ski-rental literature; the
contribution is the finite certificate set, not the metareasoning idea.
