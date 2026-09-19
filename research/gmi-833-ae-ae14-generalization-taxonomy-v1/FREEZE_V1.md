# GMI #833 Section AE14 — generalization, analogy and reasoning taxonomy: prospective freeze v1

Source `main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`.

This freeze is committed **before** any executor, oracle, test, fixture,
receipt, theorem note or reconciliation file of this package exists in the
tree. The add-order of the blobs is the custody evidence; this commit
touches exactly one file.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE14 — Generalization, analogy, reasoning: do not collapse them by rhetoric`

1. `- [ ] Give architecture-independent operational definitions of memorization, interpolation, extrapolation, systematic generalization, analogy, planning/inference and reasoning.`
2. `- [ ] Determine which are reducible to prediction under a registered specification and which require additional search/composition/control machinery.`
3. `- [ ] Construct matched tasks where predictive accuracy is equal but reasoning/compositional capability differs.`
4. `- [ ] Construct matched tasks where compression is equal but transfer differs.`
5. `- [ ] Test whether GMI predicts which additional computational mechanisms are required.`
6. `- [ ] Forbid the blanket claim that memory/generalization/analogy/reasoning are \`the same mechanism at different scales\` unless a formal reduction theorem is earned.`

**No neighboring row is earned here.** In particular this tranche does not
earn any AE1, AE2, AE3, AE4, AE5, AE6, AE7, AE8, AE9, AE10, AE11, AE12, AE13, AE15, AE16 or AE17 row of issue comment 5692689542, and does not earn any
row of the #833 issue body.

## Registered scope and frozen objects

The registered input space is `X = {0,1}^n` for a frozen `n <= 6` with a frozen
**part decomposition** `X = B1 x ... x Bk` into blocks (the registered
compositional structure). A **task** is a map `t : X -> Y` with `Y` finite, plus a
registered training support `Tr subset X`.

Seven modes are defined as exact predicates over `(task, learner class, training
support)`, each architecture-independent because each is a property of the
function realized and of the support, never of a network, layer or parameter count:

- `MEMORIZATION`: exact on `Tr`, and exactly at the base rate on `X \ Tr`.
- `INTERPOLATION`: exact on the **spanned subcube** `span(Tr)` — the smallest
  subcube of `X` containing `Tr`, i.e. the set of points agreeing with some member
  of `Tr` on every coordinate that is constant across `Tr`.
- `EXTRAPOLATION`: exact on a registered subset of `X \ span(Tr)`.
- `SYSTEMATIC_GENERALIZATION`: exact on every recombination `b1 x ... x bk` of
  block values each of which occurs in `Tr`, including combinations absent from `Tr`.
- `ANALOGY`: exact on the registered relational task `(a : b) :: (c : ?)` whose
  answer is `g . c` where `g` is the unique element of a frozen group `G` acting on
  `X` with `g . a = b`, evaluated on pairs whose `g` never appears in `Tr`.
- `PLANNING_INFERENCE`: exact on targets requiring the composition of at least two
  registered primitive operators, where no single primitive suffices.
- `REASONING`: exact on the deductive closure of a frozen finite rule system, on
  entailments whose shortest derivation has depth at least `2` and which are not
  members of `Tr`.

The registered learner classes are `L0` (lookup: any function constant off `Tr`),
`L1` (the registered depth-bounded rule class of AE1 shape — `k`-juntas computable
by a decision tree of depth at most `d`), `L_lin` (GF(2)-affine functionals),
`L_mod` (block-modular composition of per-block functions) and `L_search[D]`
(closure under composition of the registered primitives to depth at most `D`).
All classes are finite and are enumerated exhaustively.

Compression is measured as an **integer** Kraft-compliant description length in
bits under a frozen prefix-free code over the registered model space; no real-valued
code length is used anywhere.

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

- **Row 1.** The seven definitions above, each emitted as an exact predicate with its
  truth value computed on every member of the registered task roster, and a
  **pairwise distinctness table**: for each ordered pair of modes, a registered task
  on which the first holds and the second fails. A mode with no such witness is
  reported as not separated, never as separated.
- **Row 2.** For each mode, the exact statement of whether some learner in the
  registered **prediction-only** classes (`L0`, `L1`, `L_lin`, `L_mod`) realizes it
  under the registered specification, decided by exhaustive enumeration. For at
  least one mode the answer must be **no**, proved by enumerating the entire class
  and reporting the exact best attainable accuracy, together with the exact accuracy
  of an `L_search[D]` learner on the same task. This is the additional
  search/composition/control machinery the row asks about, named exactly.
- **Row 3.** Two matched tasks with **exactly equal** Bayes predictive accuracy on the
  registered test distribution and **different** exact accuracy on held-out
  recombinations, with all four numbers reported.
- **Row 4.** Two matched tasks with **exactly equal** integer description length under
  the frozen code and **different** exact transfer accuracy to a registered target
  task, with all four numbers reported.
- **Row 5.** A frozen `GMI mechanism predictor` mapping a registered structure type to
  a required mechanism class, registered **before** evaluation; the executor reports
  its exact hit count over the roster, the exact hit count of the frozen null
  (uniform random assignment over the mechanism classes, `200` trials, exact rational
  rate), and whether the predictor strictly beats the largest null hit count. A
  failure on any world is reported as a boundary with the world named.
- **Row 6.** The blanket claim is registered as the forbidden promotion
  `MEMORY_GENERALIZATION_ANALOGY_REASONING_SAME_MECHANISM`, and the row-2
  enumeration is the machine-checked reason: a reduction theorem would require a
  prediction-only learner realizing every mode, and the exhaustive enumeration
  exhibits a mode no member of those classes realizes. The executor additionally
  asserts that no artifact of this package asserts the forbidden string.

## Two materially independent routes

Route A is `ae14_generalization_taxonomy_v1.py`. Route B is `independent_taxonomy_oracle_v1.py`.
Route B contains no executable import of route A and recomputes every
claimed quantity by a materially different algorithm (brute-force enumeration of every function in each registered learner class and of every derivation tree up to the frozen depth, against route A's closed-form span, orbit and deductive-closure computations).
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

`GMI_833_AE14_GENERALIZATION_MODES_OPERATIONALLY_SEPARATED_ON_REGISTERED_FINITE_TASK_ROSTER`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`, `WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`, `ARCHITECTURE_SELECTION_LAW`, `GMI_MORPHOLOGY_PREDICTION`, `ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER`, `REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT`, `MEMORY_GENERALIZATION_ANALOGY_REASONING_SAME_MECHANISM`, `REASONING_REDUCED_TO_PREDICTION`, `ANALOGY_IS_INTERPOLATION`, `SCALE_UNIFIES_GENERALIZATION_MODES`.

## Parent ownership

Compositionality and systematic generalization: Fodor, Pylyshyn (1988), Cognition
28(1-2):3-71, doi:10.1016/0010-0277(88)90031-5; Lake, Baroni (2018), ICML,
arXiv:1711.00350; Hupkes, Dankers, Mul, Bruni (2020), JAIR 67:757-795,
doi:10.1613/jair.1.11674. Analogy as structure mapping: Gentner (1983), Cognitive
Science 7(2):155-170, doi:10.1207/s15516709cog0702_3; Hofstadter (2001), in *The
Analogical Mind*, MIT Press. Interpolation versus extrapolation: Balestriero,
Pesenti, LeCun (2021), arXiv:2110.09485. Memorization versus generalization:
Zhang, Bengio, Hardt, Recht, Vinyals (2017), ICLR, arXiv:1611.03530; Feldman
(2020), STOC, doi:10.1145/3357713.3384290. Learning theory for the rule classes:
Valiant (1984), CACM 27(11):1134-1142, doi:10.1145/1968.1972; Blumer, Ehrenfeucht,
Haussler, Warmuth (1989), JACM 36(4):929-965, doi:10.1145/76359.76371. Juntas and
decision-tree complexity: Mossel, O'Donnell, Servedio (2004), JCSS 69(3):421-434,
doi:10.1016/j.jcss.2004.04.002; O'Donnell (2014), *Analysis of Boolean Functions*,
Cambridge University Press, doi:10.1017/CBO9781139814782. Kraft inequality and MDL:
Kraft (1949), MIT MSc thesis; Rissanen (1978), Automatica 14(5):465-471,
doi:10.1016/0005-1098(78)90005-5; Grunwald (2007), *The Minimum Description Length
Principle*, MIT Press, doi:10.7551/mitpress/4643.001.0001.

Nothing in this package is claimed novel against the parent literature. The
named residual contribution of this tranche is stated in
`PARENT_OWNERSHIP_V1.md` and is the exact finite construction and its
machine-checked verification, never the underlying parent theorems.
