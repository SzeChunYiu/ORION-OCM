# Exact decision-core corrective capsule

**Ready for root's integration review:** an isolated exact-rational helper,
16 regression controls, and a small adaptive-information lemma patch.
The original PR154 files remain unchanged.

- [decision_core.py](decision_core.py): exact costs and kernels, complete kernel
  validation, reusable iterator inputs, and order-independent action-set checks.
- [test_decision_core_exact_regressions.py](test_decision_core_exact_regressions.py):
  reported witnesses plus positive equality/zero-regret/finite-stopping controls.
- [MATH-ERRATUM.md](MATH-ERRATUM.md): corrected identity and precise model/domain.
- [integration.patch](integration.patch): helper replacement, new tests, and
  bounded replacement of Lemma 8's adaptive identity paragraph.
- [QUALIFICATION.json](QUALIFICATION.json): inputs, environment, commands and
  machine-readable outcomes; [SHA256SUMS](SHA256SUMS) binds capsule files.

**Qualified on billy-laptop:** all 16 new regressions and all 10 original pure-helper controls pass. The patch applies cleanly in a read-only check against the bound source.
No frozen research experiment, native verifier, learner, or protected corpus ran.
The mathematical witness was checked on its two-world finite table.

The patch base is the unchanged four-file content reviewed at PR154 head
`c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd`, tree
`05fef3d2bafe7acd6e6a89fbaf610171381b052c`.
Root must match blob hashes against the integration head; this capsule does not
authorize applying to a changed source or certify all intervening PR additions.

Finite float inputs are accepted as exact stored binary rationals. Approximate
normalization is rejected; exact decimal intent requires explicit fractions.
Outputs are Fraction values. Integration must handle their serialization and
charge exact-arithmetic costs. Arbitrary-real exact computation is not claimed.
