# GMI #833 Section AE8 — `Compression + Prediction + Control` master-principle test: prospective freeze v1

Source `main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`.

This freeze is committed **before** any executor, oracle, test, fixture,
receipt, theorem note or reconciliation file of this package exists in the
tree. The add-order of the blobs is the custody evidence; this commit
touches exactly one file.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE8 — \`Compression + Prediction + Control\` master-principle test`

1. `- [ ] Formalize candidate CPC principle(s) without choosing weights post hoc.`
2. `- [ ] Determine whether CPC is a theorem, variational principle, decomposition, heuristic, or merely descriptive slogan.`
3. `- [ ] Search for a minimal objective that reproduces multiple existing GMI laws as corollaries.`
4. `- [ ] Prove which GMI phenomena cannot be reduced to CPC without additional terms (verification, development, communication, history, uncertainty, etc.).`
5. `- [ ] Compare CPC against alternative master principles: MDL, rate-distortion, bounded rationality, predictive information, free-energy/active-inference formulations, control-as-inference, algorithm selection and resource-rational computation.`
6. `- [ ] Construct preregistered worlds where these principles make different predictions.`
7. `- [ ] Preserve observational equivalence where no discriminating experiment exists.`
8. `- [ ] Do not call CPC the GMI master law unless it beats the bag-of-laws baseline and survives parent discrimination.`

**No neighboring row is earned here.** In particular this tranche does not
earn any AE1, AE2, AE3, AE4, AE5, AE6, AE7, AE9, AE10, AE11, AE12, AE13, AE14, AE15, AE16 or AE17 row of issue comment 5692689542, and does not earn any
row of the #833 issue body.

## Registered scope and frozen objects

The registered **model space** `M` is a finite set of candidate models over a
registered world roster; each model `m` carries an exact **term vector**
`v(m) = (cost(m), predloss(m), ctrlloss(m))` of exact rationals, where `cost` is the
**integer** Kraft-compliant description length in bits under a frozen prefix-free
code, `predloss` is exact `0-1` predictive risk and `ctrlloss` is exact control
regret against the registered optimum.

The **CPC objective family** is
`J_lambda(m) = l_C * cost(m) + l_P * predloss(m) + l_K * ctrlloss(m)` with
`lambda = (l_C, l_P, l_K)` ranging over a **frozen grid** `LGRID` of exact rational
triples, with a frozen total order on `M` for tie-breaking. No weight is chosen after seeing a result: every claim is reported
over the **whole** grid, and any claim holding only on a sub-region reports that
region explicitly.

The **registered alternative master principles**, each an exact model selection rule on
`M`: `MDL` (minimize integer code length plus integer data-code length), `RATE_DISTORTION`
(minimize expected distortion subject to a frozen **codebook cardinality**, log-free),
`BOUNDED_RATIONALITY` (maximize utility subject to a frozen integer deliberation
budget), `PREDICTIVE_INFORMATION` (maximize exact dyadic past-future mutual information),
`ACTIVE_INFERENCE` (minimize expected free energy on the registered dyadic agent
worlds), `CONTROL_AS_INFERENCE` (maximize exact rational posterior optimality odds),
`ALGORITHM_SELECTION` (minimize expected per-instance registered cost under the frozen
selector), `RESOURCE_RATIONAL` (maximize utility minus the frozen integer computation
price).

The **bag-of-laws baseline** is the per-world lookup rule that applies whichever
registered GMI law covers that world. Its description cost is the frozen integer
`sum_i len(law_i)` under the same prefix-free code; the CPC objective's cost is the
frozen integer `len(J_lambda)`. Both integers are frozen in the register described
below, before evaluation, so the penalty cannot be tuned to produce a verdict.

`LGRID`, the frozen total order on `M`, the frozen integer description lengths of the
CPC objective and of each registered GMI law, and the frozen predicted disagreement
sets are all carried in `PROSPECTIVE_REGISTER_V1.json` of this package, committed in
the commit immediately following this freeze and **before any executor, oracle, test
or receipt blob of this package exists**, so that no weight and no description-length
penalty can be chosen after a verdict is seen. The executor recomputes the SHA-256 of
the register's canonical serialization, compares it with the digest the register
carries for itself, and refuses to emit a receipt on mismatch.

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

- **Row 1.** The objective family and its frozen grid, with every claim reported over
  the whole grid and every sub-region stated explicitly. The receipt carries the grid
  and the per-lambda selections; a claim true only at one lambda is reported as such.
- **Row 2.** An exact classifier with criteria registered here: `THEOREM` if the CPC
  argmin equals the independently defined GMI-preferred model on **every** registered
  world for **every** lambda in `LGRID`; `VARIATIONAL_PRINCIPLE` if some single lambda
  achieves that; `DECOMPOSITION` if agreement holds only under stated extra
  conditions; `HEURISTIC` if the best lambda's exact agreement fraction strictly
  exceeds the null but is below `1`; `SLOGAN` if no lambda beats the null. The verdict
  is whatever the exact counts give, and is reported with those counts.
- **Row 3.** An exhaustive search over the registered objective space — every subset of
  the term basis crossed with `LGRID` — for the minimum-cardinality objective whose
  argmin reproduces each registered GMI law's choice on that law's registered
  worlds. The receipt lists, per law, `COROLLARY` with the witnessing objective, or
  `NOT_A_COROLLARY` with the exact disagreement count.
- **Row 4.** The irreducibility result. For every objective in the registered term
  basis and every lambda in `LGRID`, `J_lambda` is by construction a function of the
  term vector `v(m)` alone; hence any two models with **equal** term vectors are
  CPC-indistinguishable. The evidence is a search for **term-vector collisions** — pairs
  `m1 != m2` with `v(m1) = v(m2)` exactly — on which the independently registered GMI
  preference is **strict**. Each collision found is a proof at the registered scope
  that the corresponding phenomenon cannot be reduced to CPC without an additional
  term, and the missing term is named from the frozen list
  (`verification`, `development`, `communication`, `history`, `uncertainty`). A
  phenomenon for which no collision exists is reported as **not proved irreducible**,
  never as reducible.
- **Row 5.** The full pairwise agreement matrix between CPC (at each lambda) and each
  of the eight registered alternative principles, as exact integer counts over the
  world roster, plus the exact rational agreement fractions.
- **Row 6.** The preregistered discriminating worlds, frozen here with the digest, on
  which named principle pairs are predicted to disagree; the executor reports per
  prediction `CONFIRMED` or `REFUTED` with the exact selections. Refutations are
  reported as refutations.
- **Row 7.** Every principle pair agreeing on **every** registered world is emitted as
  `OBSERVATIONALLY_EQUIVALENT_AT_REGISTERED_SCOPE`, with the explicit statement that
  observational equivalence at a finite registered scope is not identity and licenses
  no promotion of either member over the other.
- **Row 8.** The comparison the row demands, run exactly: CPC's best exact agreement
  count against the bag-of-laws baseline's exact agreement count, at their frozen
  integer description costs, reported as a Pareto verdict; and parent discrimination —
  the exact count of registered worlds on which CPC's choice differs from every
  registered parent principle's choice. The row closes on the **verdict**, whatever
  it is. If either test fails, the receipt emits the registered terminal
  `CPC_MASTER_LAW_CLAIM_WITHHELD` and the manifest carries `CPC_IS_THE_GMI_MASTER_LAW`
  as a forbidden promotion; withholding is the closure the row asks for, and it is not
  to be reported as evidence against the parents.
- Every bound and threshold in this package carries the bound-vacuity record, with
  `range_lo`/`range_hi` derived from the definition of the bounded quantity and a
  `violated_by` witness from an explicitly relaxed class.

## Two materially independent routes

Route A is `ae8_cpc_discrimination_v1.py`. Route B is `independent_cpc_oracle_v1.py`.
Route B contains no executable import of route A and recomputes every
claimed quantity by a materially different algorithm (independent brute-force evaluation of every principle on every (world, model) pair by direct definition, independent lexicographic argmin with a differently implemented tie-break, and an independent term-vector collision search by pairwise comparison, against route A's indexed objective algebra).
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

`GMI_833_AE8_CPC_CLASSIFIED_AND_DISCRIMINATED_AGAINST_REGISTERED_MASTER_PRINCIPLES_ON_A_FINITE_PREREGISTERED_WORLD_ROSTER`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`, `WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`, `ARCHITECTURE_SELECTION_LAW`, `GMI_MORPHOLOGY_PREDICTION`, `ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER`, `REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT`, `CPC_IS_THE_GMI_MASTER_LAW`, `CPC_MASTER_LAW_CLAIM_WITHHELD_IS_A_NEGATIVE_RESULT_ABOUT_PARENTS`, `CPC_IS_A_THEOREM`, `SINGLE_OBJECTIVE_EXPLAINS_ALL_GMI_LAWS`, `OBSERVATIONAL_EQUIVALENCE_IMPLIES_IDENTITY`.

## Parent ownership

Minimum description length and its predecessors: Solomonoff (1964), Information
and Control 7(1):1-22, doi:10.1016/S0019-9958(64)90223-2; Rissanen (1978),
Automatica 14(5):465-471, doi:10.1016/0005-1098(78)90005-5; Grunwald (2007), *The
Minimum Description Length Principle*, MIT Press,
doi:10.7551/mitpress/4643.001.0001; Wallace, Boulton (1968), The Computer Journal
11(2):185-194, doi:10.1093/comjnl/11.2.185. Rate-distortion and the
information-bottleneck line: Shannon (1959), IRE National Convention Record
7:142-163; Berger (1971), *Rate Distortion Theory*, Prentice-Hall; Tishby, Pereira,
Bialek (1999), Allerton, arXiv:physics/0004057. Predictive information: Bialek,
Nemenman, Tishby (2001), Neural Computation 13(11):2409-2463,
doi:10.1162/089976601753195969; Crutchfield, Young (1989), Physical Review Letters
63(2):105-108, doi:10.1103/PhysRevLett.63.105; Shalizi, Crutchfield (2001),
Journal of Statistical Physics 104:817-879, doi:10.1023/A:1010388907793. Bounded
and resource-rational computation: Simon (1955), Quarterly Journal of Economics
69(1):99-118, doi:10.2307/1884852; Russell, Subramanian (1995), JAIR 2:575-609,
doi:10.1613/jair.133; Lieder, Griffiths (2020), Behavioral and Brain Sciences
43:e1, doi:10.1017/S0140525X1900061X; Gershman, Horvitz, Tenenbaum (2015),
Science 349(6245):273-278, doi:10.1126/science.aac6076. Control as inference and
free energy: Todorov (2009), PNAS 106(28):11478-11483,
doi:10.1073/pnas.0710743106; Levine (2018), arXiv:1805.00909; Friston, FitzGerald,
Rigoli, Schwartenbeck, Pezzulo (2017), Neural Computation 29(1):1-49,
doi:10.1162/NECO_a_00912. Algorithm selection and no-free-lunch: Rice (1976),
Advances in Computers 15:65-118, doi:10.1016/S0065-2458(08)60520-3; Wolpert,
Macready (1997), IEEE Transactions on Evolutionary Computation 1(1):67-82,
doi:10.1109/4235.585893; Kotthoff (2016), in *Data Mining and Constraint
Programming*, Springer, doi:10.1007/978-3-319-50137-6_7.

Nothing in this package is claimed novel against the parent literature. The
named residual contribution of this tranche is stated in
`PARENT_OWNERSHIP_V1.md` and is the exact finite construction and its
machine-checked verification, never the underlying parent theorems.
