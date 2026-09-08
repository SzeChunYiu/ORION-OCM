# Exact decision-core corrective capsule

**Iterator correction ready for independent recheck.** Decision regions now
snapshot each state's acceptable-action iterable before checking candidate actions.
The erratum and bisimulation docstring explicitly require block-preserved STOP
outputs/costs when combining bisimulation with finite_meta_dp.

Read [revision receipt](REVISION-02.md), [math/domain erratum](MATH-ERRATUM.md),
and [integration.patch](integration.patch). The patch modifies only the helper,
adds its regression file, and corrects the adaptive-information lemma.

Current focused qualification: **2 affected controls pass** on billy-laptop:
the tuple/iterator/containment equivalence regression and the original common-action
control. [FOCUSED-03.json](FOCUSED-03.json) records actual child PID, cwd, imported
module path, and equal source hashes before/after the run.

The prior candidate and all exact receipts are preserved under
[history/01-before-good-action-iterator](history/01-before-good-action-iterator/).
Its 16-regression/10-control results remain historical results on that candidate.
Only affected tests were rerun for this revision; no broader result is implied.
[QUALIFICATION.json](QUALIFICATION.json) and [SHA256SUMS](SHA256SUMS) bind the
current owned artifacts and preserved records. Root metadata and independent
review files are outside this manifest's ownership.

The patch base is the four-file content reviewed at PR154 head
`c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd`, tree
`05fef3d2bafe7acd6e6a89fbaf610171381b052c`.
Root must match those source blobs against the integration head.

Finite floats mean their exact stored binary rationals; normalization is exact.
Outputs use Fraction, whose serialization and lifecycle costs need integration
accounting. No arbitrary-real exactness, frozen research result, full-PR repair,
unbounded stopping theorem, or automatic coverage of omitted STOP contracts is claimed.
