# Shared messages for independent relational obligations

A shared encoder can compress two independent acceptable-action obligations
more than two separately optimal encoders. This is an application of SC-1
and finite set cover, with complete coverage of the declared protocol class.

| Supplied relation | Local alphabets | Separate product | Shared optimum | Packed fixed bits |
|---|---:|---:|---:|---:|
| Three actions, output must differ from input | 2, 2 | 4 | 3 | 2 → 2 |
| Five input points covered by the five C5 independent pairs | 3, 3 | 9 | 8 | 4 → 3 |

The obligations and full Cartesian input domain stay independent. The shared
message is allowed to depend on both inputs. The existing product-machine
frontier theorem and exact-function alphabet multiplicativity remain valid.
Only the classical fixed message alphabet and its packed binary width are
optimized; no physical Pareto, program-size or lifetime superiority is claimed.

- [Exact theorem and witnesses](JOINT_RELATIONAL_COMPOSITION_THEOREM_V1.md)
- [Primary parents, scope and all-cost obligations](PARENTS_AND_COSTS_V1.md)
- [Validation and replay](VALIDATION_V1.md)
- [Complete finite receipt](JOINT_RELATIONAL_COMPOSITION_RECEIPT_V1.json)
- [Source bindings](SOURCE_PARENTS_V1.json), [packet manifest](MANIFEST.json)
