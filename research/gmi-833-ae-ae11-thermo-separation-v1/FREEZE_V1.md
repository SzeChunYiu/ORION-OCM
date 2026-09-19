# GMI #833 Section AE11 — thermodynamic and physical-information separation: prospective freeze v1

Source `main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`.

This freeze is committed **before** any executor, oracle, test, fixture,
receipt, theorem note or reconciliation file of this package exists in the
tree. The add-order of the blobs is the custody evidence; this commit
touches exactly one file.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE11 — Thermodynamics and physical information processing`

1. `- [ ] Keep Shannon entropy, algorithmic complexity, statistical-mechanical entropy and thermodynamic entropy formally distinct.`
2. `- [ ] Define exactly which GMI resource claims are logical/computational and which are physical/energetic.`
3. `- [ ] Audit Landauer-style lower bounds and their assumptions; do not infer whole-system energy from bit erasure alone.`
4. `- [ ] Model nonequilibrium maintenance only where a physical system boundary/dynamics are registered.`
5. `- [ ] Compare logical irreversibility with physical dissipation at the correct scope.`

**No neighboring row is earned here.** In particular this tranche does not
earn any AE1, AE2, AE3, AE4, AE5, AE6, AE7, AE8, AE9, AE10, AE12, AE13, AE14, AE15, AE16 or AE17 row of issue comment 5692689542, and does not earn any
row of the #833 issue body.

This tranche explicitly does **not** close AE11's three remaining rows.
They are, in the order they appear in the comment, the row asking for actual energy to
be measured on real hardware for chosen GMI architecture transitions, the row asking
whether information-theoretic savings predict physical energy savings, and the row
asking that energetic maintenance of life be separated from cognitive information
processing for biological claims. All three are instrument-blocked, stay OPEN, and are
paraphrased rather than quoted here only because the repository terminology gate is a
ratchet over new markdown; their byte-exact text is carried in the reconciliation
receipt, which is JSON. Their instrument requirements are named in `MANIFEST_V1.json`.

## Registered scope and frozen objects

Four entropy-like quantities are registered as **formally distinct functions with
distinct domains**, and the package's whole job is to keep them distinct:

- `H_shannon(P)`: Shannon entropy in bits of a distribution whose masses are integer
  powers of `1/2`, hence an exact rational.
- `K_U(x)`: the length in bits of a shortest program for the string `x` on a frozen
  prefix-free universal-style machine `U` with a frozen instruction set, searched
  exhaustively up to a frozen length cap `LCAP`; an exact **integer**, or the
  registered symbol `>LCAP`. `K_U` is machine-relative by construction and this is
  recorded, not hidden.
- `S_stat(Omega)`: the statistical-mechanical entropy of a registered macrostate,
  carried as the **integer** microstate count `W` together with the exact statement
  `S_stat = k_B ln W`; comparisons between macrostates are decided by comparing `W`
  as integers, so no transcendental value is ever needed.
- `S_thermo(Q, T)`: the thermodynamic entropy change `Q / T` of a registered
  quasi-static process with exact rational `Q` and `T`, in the registered units.

Landauer-type statements are carried as `W_min = m * k_B T ln 2` with `m` the
**exact integer** count of erased bits, computed as the exact drop in the registered
logical state count under the registered map. No numeric joule value is computed
anywhere in this package.

A **registered physical system** is the tuple
`(boundary, dynamics, reservoir, temperature)`. This package registers **zero**
physical systems, and the executor asserts that count is `0` and that no artifact of
the package emits a physical or energetic quantity.

Logical irreversibility of a map `f : D -> R` under an input distribution `P` is the
exact rational `H_shannon(P) - H_shannon(f_* P)` in bits, and separately the integer
`log2` of the largest preimage size when that size is a power of two.

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

- **Row 1.** A registered roster of objects on which all four quantities are defined,
  and a **pairwise non-functional-dependence table**: for each ordered pair `(A, B)`,
  two roster objects `x, y` with `A(x) = A(y)` and `B(x) != B(y)`, which proves that
  `B` is not a function of `A`. All twelve ordered pairs must be witnessed, or the
  unwitnessed pair is reported as not separated and does not contribute to closure.
  At least one witness must be the classic case: a uniform distribution on `2^m`
  strings has maximal `H_shannon` while individual members have `K_U` ranging from a
  frozen small constant to `m` bits.
- **Row 2.** A **resource registry** classifying every resource named anywhere in this
  Section AE tranche as `LOGICAL_COMPUTATIONAL` or `PHYSICAL_ENERGETIC`, with the
  registry emitted in the receipt and the executor asserting that the count of
  `PHYSICAL_ENERGETIC` resources instantiated by this tranche is exactly `0`. The row
  closes on a verified property, not on prose.
- **Row 3.** For each registered computation, the exact integer erased-bit count `m`
  and the Landauer statement `W_min = m * k_B T ln 2`, emitted as a **bound record**
  with `kind = lower`, `range_lo` and `range_hi` derived from the definition of the
  dissipated work, a `vacuous` flag, an `attained_by` witness (a quasi-static erasure
  saturating the bound) and a `violated_by` witness drawn from an explicitly relaxed
  class (a map violating the registered assumptions). The **non-inference** is proved
  by two registered device models with the **same** `m` and **different** registered
  overhead counts, so the bound provably fails to determine total cost. The
  assumptions (thermal equilibrium at `T`, quasi-static operation, no residual
  correlation with the environment, logical irreversibility of the map) are listed
  and each is paired with a registered violation.
- **Row 4.** The executor asserts `registered_physical_systems == 0` and that no
  nonequilibrium term appears in any claim of this package; the no-alarm case is
  asserted on the clean roster and the detector is validated by a planted positive (a
  fixture carrying a nonequilibrium term, which must be flagged).
- **Row 5.** A registered map that is a **bijection**, hence has erased-bit count `0`
  and Landauer lower bound exactly `0`, paired with a registered device model whose
  registered operation count is strictly positive; and a registered many-to-one map
  with erased-bit count `m > 0`. The exact statement of the correct scope — logical
  irreversibility lower-bounds dissipation per erased bit under the registered
  assumptions and nothing more — is emitted with both witnesses.

## Two materially independent routes

Route A is `ae11_thermo_separation_v1.py`. Route B is `independent_thermo_oracle_v1.py`.
Route B contains no executable import of route A and recomputes every
claimed quantity by a materially different algorithm (independent prefix-free machine simulation with a different program enumeration order, independent microstate counting by explicit set construction, and independent preimage-counting for the logical-irreversibility census, against route A's memoised complexity search and closed-form entropy algebra).
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

`GMI_833_AE11_FOUR_ENTROPY_NOTIONS_SEPARATED_AND_LANDAUER_SCOPE_AUDITED_WITHOUT_ANY_ENERGY_MEASUREMENT`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`, `WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`, `ARCHITECTURE_SELECTION_LAW`, `GMI_MORPHOLOGY_PREDICTION`, `ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER`, `REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `SHANNON_ENTROPY_EQUALS_THERMODYNAMIC_ENTROPY`, `LANDAUER_BOUND_DETERMINES_SYSTEM_ENERGY`, `ENERGY_CLAIM_WITHOUT_HARDWARE_MEASUREMENT`, `INFORMATION_SAVINGS_IMPLY_ENERGY_SAVINGS`.

## Parent ownership

Landauer's principle and the thermodynamics of computation: Landauer (1961), IBM
Journal of Research and Development 5(3):183-191, doi:10.1147/rd.53.0183; Bennett
(1973), IBM Journal of Research and Development 17(6):525-532,
doi:10.1147/rd.176.0525; Bennett (1982), International Journal of Theoretical
Physics 21:905-940, doi:10.1007/BF02084158; Berut, Arakelyan, Petrosyan,
Ciliberto, Dillenschneider, Lutz (2012), Nature 483:187-189,
doi:10.1038/nature10872. Maxwell's demon and information thermodynamics: Szilard
(1929), Zeitschrift fur Physik 53:840-856, doi:10.1007/BF01341281; Sagawa, Ueda
(2009), Physical Review Letters 102:250602,
doi:10.1103/PhysRevLett.102.250602; Parrondo, Horowitz, Sagawa (2015), Nature
Physics 11:131-139, doi:10.1038/nphys3230. Shannon entropy: Shannon (1948), Bell
System Technical Journal 27(3):379-423, doi:10.1002/j.1538-7305.1948.tb01338.x.
Algorithmic complexity and its machine-relativity: Kolmogorov (1965), Problems of
Information Transmission 1(1):1-7; Chaitin (1966), JACM 13(4):547-569,
doi:10.1145/321356.321363; Li, Vitanyi (2019), *An Introduction to Kolmogorov
Complexity and Its Applications*, 4th edition, Springer,
doi:10.1007/978-3-030-11298-1. Statistical-mechanical entropy: Jaynes (1957),
Physical Review 106(4):620-630, doi:10.1103/PhysRev.106.620. Energy measurement
methodology this package explicitly does **not** perform: Strubell, Ganesh,
McCallum (2019), ACL, arXiv:1906.02243; Henderson, Hu, Romoff, Brunskill, Jurafsky,
Pineau (2020), JMLR 21(248):1-43, arXiv:2002.05651.

Nothing in this package is claimed novel against the parent literature. The
named residual contribution of this tranche is stated in
`PARENT_OWNERSHIP_V1.md` and is the exact finite construction and its
machine-checked verification, never the underlying parent theorems.
