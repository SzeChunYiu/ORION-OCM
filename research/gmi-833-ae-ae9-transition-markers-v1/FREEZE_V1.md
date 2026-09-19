# GMI #833 Section AE9 — architecture-independent representation-change markers on non-neural systems: prospective freeze v1

Source `main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`.

This freeze is committed **before** any executor, oracle, test, fixture,
receipt, theorem note or reconciliation file of this package exists in the
tree. The add-order of the blobs is the custody evidence; this commit
touches exactly one file.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE9 — Learning as representation restructuring`

1. `- [ ] Define measurable representation-change quantities during learning that do not depend on neural architecture names.`
2. `- [ ] Distinguish smooth quantitative improvement from genuine qualitative computational transition.`
3. `- [ ] Re-audit \`emergence\` terminology: thresholded metric artifact vs phase-like internal reorganization vs grokking-like delayed generalization.`

**No neighboring row is earned here.** In particular this tranche does not
earn any AE1, AE2, AE3, AE4, AE5, AE6, AE7, AE8, AE10, AE11, AE12, AE13, AE14, AE15, AE16 or AE17 row of issue comment 5692689542, and does not earn any
row of the #833 issue body.

This tranche explicitly does **not** close AE9's four measurement rows
(`For neural systems, measure representational geometry, effective rank/dimension,
clustering, linear separability, invariances, circuit/path usage and information flow
across training.`, `Freeze prospective markers of a representation transition before
observing the capability transition.`, `Test whether internal transition markers predict
new capability onset better than parameter count/training loss alone.` and `Compare
neural transition results with non-neural systems to test whether the law is
architecture-general.`). They require training runs on real neural systems and stay
OPEN with a stated instrument requirement.

## Registered scope and frozen objects

A **representation** is a map `phi : X -> Z` from the registered finite input space
`X = {0,1}^n`, `n <= 5`, to a finite code set. Every marker below is a function of
the **induced partition** `ker(phi) = { phi^{-1}(z) }` and of the registered readout
class, never of an architecture, layer or parameter count; this is what makes the
markers architecture-independent, and the property is proved rather than asserted.

Registered markers, all exact integers or exact rationals:

- `CELLS(phi)`: the number of non-empty cells of `ker(phi)` (an integer effective
  rank that needs no eigenvalue).
- `REFINEMENT(phi, psi)`: the exact integer pair (cells merged, cells split) taking
  `ker(phi)` to `ker(psi)`, and the exact rational normalized partition distance.
- `SEPARABILITY(phi, t)`: the exact rational fraction of registered label pairs
  separable by a GF(2)-affine functional of `phi`.
- `INVARIANCE(phi)`: the integer order of the largest subgroup of the registered
  coordinate-permutation group under which `ker(phi)` is invariant.
- `READOUT_ARITY(phi, t)`: the least integer `k` such that some `k`-junta readout of
  `phi` realizes `t` exactly, or the registered symbol `NONE`.
- `USABLE(phi, t, R)`: the exact rational best accuracy of the registered budgeted
  readout class on `phi`.

The registered **learners** are non-neural by construction: an exact GF(2) Gaussian
elimination learner, a greedy decision-list learner and an exact lookup learner. A
**trajectory** is the sequence of representations these learners induce as the
training sample count `m` runs over a frozen range; every accuracy along it is the
exact rational expectation over all `m`-subsets, not a sampled estimate.

A **structural invariant** is a marker taking values in a finite discrete set
(`CELLS`, `INVARIANCE`, `READOUT_ARITY`); a **graded quantity** is a marker taking
values in the rationals (`SEPARABILITY`, `USABLE`, accuracy). The distinction between
a smooth improvement and a qualitative transition is defined on structural
invariants, so it cannot be manufactured by thresholding a graded quantity.

## Exact-arithmetic discipline

Every quantity entering a claim is an exact `fractions.Fraction` or a Python
`int`. No float appears in any claim, receipt, test assertion or hostile.
Registered worlds are designed so that each information-theoretic quantity
entering a claim is exactly rational: probabilities that must be logged are
restricted to non-negative integer powers of `1/2`, code lengths are
Kraft-compliant **integers**, rate constraints are stated as **codebook
cardinalities** rather than as real-valued mutual-information budgets, and
Landauer-type statements are carried in units of `k_B T ln 2` with an
**integer** coefficient. Where a comparison genuinely requires the logarithm
of a non-dyadic rational, it is decided only by certified exact rational
bounds: `log2(a/b) >= u/v` is decided by the integer comparison
`a^v >= 2^u * b^v`. Non-separating bounds are reported as `NOT_DECIDED`,
never as equality. Equality of a logarithmic quantity is claimed only in the
exactly dyadic case where the logarithm is an integer.

## Bound-vacuity discipline

Every bound this package states is emitted as a record carrying `kind`
(`upper` or `lower`), `bound_value`, `range_lo` and `range_hi` **derived from
the definition of the bounded quantity, never from the roster's observed
extremes, with the derivation stated in the record**, a `vacuous` flag
(`upper` is vacuous iff `bound_value >= range_hi`; `lower` is vacuous iff
`bound_value <= range_lo`), a separate `attained_by` witness, and a
`violated_by` witness: an object in an explicitly relaxed class that breaks
the bound. A bound with no `violated_by` witness is reported as
`UNFALSIFIED_BOUND` and is not used to close a row. Attainment is recorded
but is **not** accepted as evidence of non-vacuity.

## Required evidence and falsifiers

- **Row 1 (definitional).** The six markers above computed exactly on the registered
  roster; an **architecture-independence proof requirement**: two materially different
  learners that induce the **same** partition must yield exactly equal marker values
  on every marker, and a re-encoding of the code set by an arbitrary injection must
  leave every marker exactly unchanged; while a genuine change of partition must move
  at least one marker. Both directions are asserted, so the markers are shown to be
  neither degenerate nor architecture-dependent.
- **Row 3.** Two registered trajectories: one on which accuracy rises strictly and
  every structural invariant is **constant** (smooth quantitative improvement), and
  one on which accuracy is exactly at the base rate until a frozen `m*` and then
  jumps, with `READOUT_ARITY` jumping in the same step (genuine qualitative
  computational transition). All accuracies exact rationals; the invariant values
  exact integers; `m*` exact.
- **Row 4.** Three registered witnesses for the `emergence` re-audit, together with a
  classifier that assigns each to its class and is validated on real roster data in
  both directions: (a) **thresholded metric artifact** — an exactly smooth underlying
  accuracy whose registered `k`-item exact-match transform `acc^k` shows a sharp knee,
  with the exact per-step increments of both reported and the structural invariants
  constant throughout; (b) **phase-like internal reorganization** — the row-3 jump
  trajectory, where a structural invariant moves; (c) **grokking-like delayed
  generalization** — a trajectory with exact training accuracy `1` from a frozen small
  `m` while exact held-out accuracy stays at the base rate until a later `m**`, then
  jumps. The classifier must show recall on each planted positive **and** the no-alarm
  case on the clean smooth trajectory, and the receipt reports its exact confusion
  counts over the roster and over a randomized null.
- Every marker-versus-capability statement is scoped to the registered non-neural
  systems. The forbidden promotion `NEURAL_RESULT_FROM_NON_NEURAL_ROSTER` is
  registered and asserted absent from every artifact of this package.

## Two materially independent routes

Route A is `ae9_transition_markers_v1.py`. Route B is `independent_marker_oracle_v1.py`.
Route B contains no executable import of route A and recomputes every
claimed quantity by a materially different algorithm (independent partition construction by explicit equivalence-class closure, independent subgroup enumeration and independent brute-force readout search, against route A's canonical-labelling and incremental refinement algebra).
The test parses route B's AST and asserts the absence of any import of route A.

## Hostiles, null and no-alarm

Each hostile is a deliberately broken variant of a registered object. Two
assertions are required per hostile, in order: **potency** (the perturbed
quantity differs from the true quantity) and **detection** (the checker flags
the perturbed object). A hostile that cannot move the quantity it perturbs is
a package defect, not a pass. A null of randomized controls drawn from a
registered exact-rational sampler must fail the property the true witnesses
pass, at a reported rate, and the **no-alarm case must be asserted on the
known-clean registered witnesses**.

## Registered constants and prospective predictions

Every constant this package treats as registered — rosters, grids, thresholds,
integer description lengths, predicted orderings and predicted disagreement
sets — is carried in `PROSPECTIVE_REGISTER_V1.json` of this package. That file
is committed in the commit **immediately following this freeze** and before any
executor, oracle, test, fixture or receipt blob of this package exists, so its
custody is provable from the git order exactly as this freeze's is. The
executor recomputes the SHA-256 of the register's canonical serialization,
compares it with the digest the register carries for itself, and refuses to emit
a receipt on mismatch. No registered constant may be introduced or changed after
a result has been seen, and a prediction the evaluation refutes is reported as
`REFUTED` with its exact values rather than edited.

## Determinism

`RESULT_V1.json` is byte-identical under `python3 -I -B` and
`python3 -I -O -B`, and across CPython 3.8 and 3.12. Determinism is
structural: every collection is sorted before serialization, no set is
iterated into output, and serialization is a single
`json.dumps(..., sort_keys=True, indent=2)`. Tests use `unittest` assertion
**methods**, never the bare `assert` statement, so that no check is stripped
by `-O`.

## Claim ceiling

`GMI_833_AE9_ARCHITECTURE_INDEPENDENT_TRANSITION_MARKERS_DEFINED_AND_EMERGENCE_CLASSES_SEPARATED_ON_NON_NEURAL_REGISTERED_SYSTEMS`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`, `WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`, `ARCHITECTURE_SELECTION_LAW`, `GMI_MORPHOLOGY_PREDICTION`, `ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER`, `REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT`, `EMERGENCE_IS_ALWAYS_A_METRIC_ARTIFACT`, `EMERGENCE_IS_ALWAYS_A_PHASE_TRANSITION`, `NEURAL_RESULT_FROM_NON_NEURAL_ROSTER`, `TRANSITION_MARKER_PREDICTS_CAPABILITY_ONSET`.

## Parent ownership

Emergence claims and their measurement critique: Wei, Tay, Bommasani, Raffel,
Zoph, Borgeaud et al. (2022), *Emergent Abilities of Large Language Models*, TMLR,
arXiv:2206.07682; Schaeffer, Miranda, Koyejo (2023), *Are Emergent Abilities of
Large Language Models a Mirage?*, NeurIPS, arXiv:2304.15004. Grokking: Power,
Burda, Edwards, Babuschkin, Misra (2022), arXiv:2201.02177; Nanda, Chan, Lieberum,
Smith, Steinhardt (2023), ICLR, arXiv:2301.05217. Representational-geometry
measurement this package deliberately does **not** perform on neural systems:
Kriegeskorte, Mur, Bandettini (2008), Frontiers in Systems Neuroscience 2:4,
doi:10.3389/neuro.06.004.2008; Raghu, Gilmer, Yosinski, Sohl-Dickstein (2017),
NIPS, arXiv:1706.05806; Kornblith, Norouzi, Lee, Hinton (2019), ICML,
arXiv:1905.00414. Partition-based information measures: Meila (2007), Journal of
Multivariate Analysis 98(5):873-895, doi:10.1016/j.jmva.2006.11.013. Usable and
computationally bounded information: Xu, Zhao, Song, Stewart, Ermon (2020), ICLR,
arXiv:2002.10689. Boolean junta learning and exact readout arity: Mossel,
O'Donnell, Servedio (2004), JCSS 69(3):421-434, doi:10.1016/j.jcss.2004.04.002.

Nothing in this package is claimed novel against the parent literature. The
named residual contribution of this tranche is stated in
`PARENT_OWNERSHIP_V1.md` and is the exact finite construction and its
machine-checked verification, never the underlying parent theorems.
