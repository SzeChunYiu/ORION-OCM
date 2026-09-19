# GMI #833 Section AE6 — manifold hypothesis and geometric structure hierarchy: prospective freeze v1

Source `main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`.

This freeze is committed **before** any executor, oracle, test, fixture,
receipt, theorem note or reconciliation file of this package exists in the
tree. The add-order of the blobs is the custody evidence; this commit
touches exactly one file.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE6 — Manifold hypothesis and geometric structure`

1. `- [ ] Replace loose \`data lie on a manifold\` language with a hierarchy: low intrinsic dimension, union/stratification of manifolds, sparse/compositional latent structure, symmetry/orbit structure, graph/topological structure, and non-geometric algorithmic structure.`
2. `- [ ] Construct learnable distributions that violate a smooth-manifold assumption.`
3. `- [ ] Construct low-dimensional manifolds that are statistically/causally useless for the target task.`
4. `- [ ] Derive when locality/smoothness should favor local/shared operators.`
5. `- [ ] Derive when symmetry/equivariance should favor parameter sharing.`
6. `- [ ] Derive when compositional latent factors should favor modular/hierarchical representations.`

**No neighboring row is earned here.** In particular this tranche does not
earn any AE1, AE2, AE3, AE4, AE5, AE7, AE8, AE9, AE10, AE11, AE12, AE13, AE14, AE15, AE16 or AE17 row of issue comment 5692689542, and does not earn any
row of the #833 issue body.

## Registered scope and frozen objects

The registered ambient space is `X = {0,1}^n` for a frozen `n <= 6` with Hamming
distance, so `geometry` is exact and combinatorial rather than approximate.
A **registered source** is a distribution `P` on `X` with exact-rational masses and
a target `Y = t(X)`.

Six structure classes are defined as exact predicates on the support `supp(P)`:

- `LOW_INTRINSIC_DIMENSION[k]`: `supp(P)` is contained in a coset of a GF(2)-linear
  subspace of dimension `k`.
- `UNION_OR_STRATIFICATION[r, k]`: `supp(P)` is a union of at most `r` such cosets of
  dimension at most `k` each, and is **not** contained in any single coset of
  dimension `k`.
- `SPARSE_COMPOSITIONAL[b]`: `supp(P)` factorizes as a product over the frozen block
  decomposition with per-block support of size at most `b`.
- `SYMMETRY_ORBIT[G]`: `supp(P)` is a union of orbits of a registered nontrivial
  subgroup `G` of the coordinate-permutation group, and `P` is `G`-invariant.
- `GRAPH_TOPOLOGICAL[g]`: the Hamming-`1` graph induced on `supp(P)` is connected and
  has cycle rank exactly `g`, a property no dimension count records.
- `NON_GEOMETRIC_ALGORITHMIC`: `supp(P)` is the accepting set of a registered small
  Boolean circuit, has full GF(2)-affine dimension `n`, trivial symmetry group and
  cycle rank outside the registered geometric range.

The architecture classes for rows 4-6 are the frozen exactly-enumerable families
`M_local[k]` (functions determined by some `k`-subset of coordinates),
`M_shared[G]` (functions invariant under `G`, realized by orbit-averaged parameters),
`M_modular` (block-wise composition `g(h1(B1), ..., hk(Bk))`) and `M_monolithic[q]`
(arbitrary functions at description budget `q` **integer** bits under the frozen
Kraft-compliant code). Cost is the integer description length; accuracy is exact
rational.

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

- **Row 1.** The six classes above evaluated exactly on a registered source roster,
  with a **strictness table**: for each ordered pair of classes, a registered source
  in the first and not in the second, or an explicit statement that the pair is not
  separated on the roster. The hierarchy is emitted as a partial order with the
  witnesses attached, replacing the phrase `data lie on a manifold` with a checked
  object.
- **Row 2.** A registered source that is `UNION_OR_STRATIFICATION` with two cosets of
  **different** dimensions, hence not a single smooth manifold at the registered
  scope, on which a member of the registered rule class attains exact accuracy `1`.
  Both facts exact.
- **Row 3.** A registered source whose support lies in a coset of GF(2)-dimension `1`
  — maximally `low-dimensional` — and whose exact mutual information with `Y` is `0`
  bits and whose exact interventional effect on `Y` is `0`, while a full-dimension
  coordinate carries the label exactly. Dimension is thereby shown to be neither
  statistically nor causally sufficient.
- **Rows 4-6.** Each is a **derivation** with an exact rational condition, in the shape
  `if <exact condition on the source> then <the named architecture class> attains the registered
  optimum at integer cost <c1> while the comparator attains at most <exact accuracy>
  at the same budget`, plus the matched **failure** counterexample in which the
  condition fails and that same architecture class is strictly worse, with the exact accuracy
  drop. Every threshold is emitted as a bound record with `range_lo`/`range_hi`
  derived from the definition of the bounded quantity, a `vacuous` flag, a separate
  `attained_by`, and a `violated_by` witness from an explicitly relaxed class. A
  condition that never fails on the roster is reported as `UNFALSIFIED_CONDITION` and
  does not close its row.

## Two materially independent routes

Route A is `ae6_geometric_structure_v1.py`. Route B is `independent_geometry_oracle_v1.py`.
Route B contains no executable import of route A and recomputes every
claimed quantity by a materially different algorithm (exhaustive enumeration over the registered support sets, the full symmetric-group subgroup search and brute-force affine-closure tests, against route A's GF(2) rank, orbit-partition and block-factorization algebra).
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

`GMI_833_AE6_GEOMETRIC_STRUCTURE_HIERARCHY_SEPARATED_AND_MORPHOLOGY_CONDITIONS_DERIVED_ON_REGISTERED_FINITE_ROSTER`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`, `WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`, `ARCHITECTURE_SELECTION_LAW`, `GMI_MORPHOLOGY_PREDICTION`, `ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER`, `REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `LOW_DIMENSION_IMPLIES_LEARNABILITY`, `GEOMETRIC_STRUCTURE_IMPLIES_TASK_RELEVANCE`, `SYMMETRY_ALWAYS_JUSTIFIES_PARAMETER_SHARING`.

## Parent ownership

Manifold hypothesis and intrinsic dimension: Tenenbaum, de Silva, Langford (2000),
Science 290(5500):2319-2323, doi:10.1126/science.290.5500.2319; Roweis, Saul (2000),
Science 290(5500):2323-2326, doi:10.1126/science.290.5500.2323; Fefferman, Mitter,
Narayanan (2016), JAMS 29(4):983-1049, doi:10.1090/jams/852; Pope, Zhu, Abdelkader,
Goldblum, Goldstein (2021), ICLR, arXiv:2104.08894. Union-of-manifolds and
stratification: Vidal (2011), IEEE Signal Processing Magazine 28(2):52-68,
doi:10.1109/MSP.2010.939739; Brown, Caterini, Ross, Cresswell, Loaiza-Ganem (2023),
ICLR, arXiv:2207.02862. Invariance, equivariance and weight sharing: LeCun, Bottou,
Bengio, Haffner (1998), Proceedings of the IEEE 86(11):2278-2324,
doi:10.1109/5.726791; Cohen, Welling (2016), ICML, arXiv:1602.07576; Bronstein,
Bruna, Cohen, Velickovic (2021), arXiv:2104.13478; Elesedy, Zaidi (2021), ICML,
arXiv:2102.10333. Compositionality and depth separations: Poggio, Mhaskar, Rosasco,
Miranda, Liao (2017), International Journal of Automation and Computing
14(5):503-519, doi:10.1007/s11633-017-1054-2; Telgarsky (2016), COLT,
arXiv:1602.04485. Boolean analysis for the exact combinatorial substrate:
O'Donnell (2014), *Analysis of Boolean Functions*, Cambridge University Press,
doi:10.1017/CBO9781139814782.

Nothing in this package is claimed novel against the parent literature. The
named residual contribution of this tranche is stated in
`PARENT_OWNERSHIP_V1.md` and is the exact finite construction and its
machine-checked verification, never the underlying parent theorems.
