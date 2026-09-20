# V18 formal scope

Read [CORE.md](CORE.md), the preregistration [FREEZE_V18.md](FREEZE_V18.md),
[THEORY_V18.md](THEORY_V18.md), and [CONTEXTS_V18.md](CONTEXTS_V18.md).
The kernel record supports specified parts of original R2-008.
It does not close R1-006, R2-003/007/009, or the whole GMI programme.

## Replay and custody

`check_lean_v18.py` reads the ten paths in `proof_contract_v18.py`,
stages their exact bytes in one fresh temporary directory, and builds them in
dependency order with Lean 4.19.0 and warnings treated as errors.
Its generated audit registers 75 explicit typed terms and prints their
kernel assumptions. It does not discover theorem types from the replayed source.
Imports resolve from the isolated directory, including the freshly built
immutable V5, V12 and V15 sources; installed project build caches are not used.

The dependency inventory is:
- V5 `AdmissibilityV5.lean`;
- V15 `PartialContextV15.lean`;
- V12 `ScalarLawsV12.lean` and `FiniteSumsV12.lean`;
- V18 `PrefixWrapperV18.lean`, `ShortestCodesV18.lean`,
  `FiniteMarginsV18.lean`, `LowerFiniteV18.lean`,
  `ExpectationContextsV18.lean`, and `FreeMonotonesV18.lean`.

A source-valid replacement of a registered conclusion by `True` must fail
at the separate typed audit. Parent-owned tests exercise that requirement.
Missing tools or source inputs are CANNOT_CHECK; a checked invalid source
or typed registration is invalid evidence. Neither means a mathematical
counterexample to a correctly stated theorem.

## Prefix parsing and shortest descriptions

`Program` is an actual `List Bool`.
`Machine α` is a function from programmes to `Option α`.
`None` denotes an undefined result of this mathematical denotation.
It is not a kernel implementation of Turing-machine divergence or a
termination detector for an arbitrary programme.

`stripOnes` recursively consumes exactly L leading true bits.
`pad` concatenates L true bits with the base programme.
`wrapper` recognizes the exact singleton false programme as its target case,
otherwise runs the base denotation on the parsed suffix, or returns None.
The registered `pad_binding` and `wrapper_binding` fix these implementations.

`strip_iff`, `wrapper_simulates`, `wrapper_empty`, and `success_iff`
derive parsing, compilation, empty-input rejection and the complete successful
domain. For every L>0, `wrapper_prefix_free` proves domain prefix freedom
from prefix freedom of the base domain. Padding need not be at least two
for that syntax theorem; L≥2 serves the separate concentration margin.

`IsShortest U x p` means that U(p)=some x and p has no longer length than
any other successful programme for x.
`MinimumLength` is existence of such a programme with the specified length.
Both definitions have registered explicit logical equations.
`minimum_exists` uses natural-number well-founded induction on an existing
successful programme; `minimum_unique` derives uniqueness of its length.

`target_minimum` establishes the actual target minimum of one.
`nontarget_exists` transports existence in both directions.
`shortest_forward` and `shortest_backward` transport minimum witnesses.
`nontarget_minimum_iff` gives the exact L+k length shift for a different
output, including the correct absence-of-description case.
No primitive complexity-shift hypothesis supplies these results.
Distinct outputs are an explicit premise of the nontarget theorems.

The kernel proves a compiler equation for the actual prefix transformation.
Computability of a wrapper around a partial computable machine and inherited
Turing universality are paper arguments. There is no implemented universal
Turing-machine interpreter in this package.
The countable environmental codebook, prefix Kraft inequality, dyadic weights,
real infinite sums and all-reference-machine envelope theorem are paper proofs.

## Finite score and residual-weight bounds

`FiniteMarginsV18` uses the actual Int instance of V12's primitive scalar laws.
Its score is the finite weighted sum; its masks select actual coordinates.
`score_mask_split` and `score_split` derive exact decompositions.
`score_bounds` gives 0≤score≤B times total weight for nonnegative weights
and coordinate values between zero and B.

`omitted_bound` bounds the omitted score by B times omitted weight.
`target_window` bounds the full score between the target contribution and
that contribution plus B times nontarget weight.
`strict_separation` proves strict score ordering when the target weighted
gap exceeds this residual bound. Its conclusion is not a premise.
Dimension zero has the actual empty sum; target-indexed statements require
a `Fin n` witness and consequently do not instantiate at n=0.

These are finite integer theorems. Exact rational data with common positive
denominators can be scaled to their premises; the scaling interpretation and
the countable real extension are paper mathematics, not a Lean Real instance.
The kernel does not prove Kraft's bound or derive residual weight from a
universal machine. The paper connects that independently proved weight bound
to the score inequality. Python's Fraction checks are separate finite evidence.

## Declared expectation and lower-envelope contexts

`Probability α n` contains a finite weight vector, pointwise nonnegativity,
and its actual sum equal to one.
The scalar interface assumes primitive linearly ordered commutative ring laws,
including 0<1. It assumes no weighted-average or minimum theorem.

`expected` is the actual dot product.
`expected_monotone` and `expected_constant` derive monotonicity and
constant preservation. `no_empty_probability` derives the impossibility of
a normalized empty vector from 0≠1.

`LowerFiniteV18.lower` recursively computes the minimum of a nonempty
finite family using comparisons. Its order bounds, monotonicity,
constant/singleton equations and attained-coordinate theorem are proved.
`envelope` applies this minimum to the family's actual expectations.
The family has type `Fin (m+1) → Probability α n`; nonemptiness is explicit.

`expectation` and `lowerContext` are actual V15 Context records.
Their registered domain, evaluation, active comparison and observation
equations preserve the caller's E and the admission restriction P∩E.
Illegal, undefined and evaluated outcomes are retained without fallback values.
The evaluator equations bind the finite weighted sums and the actual minimum,
not merely a constructor name or its return type.

The generic laws are kernel checked under the primitive Scalar interface.
`intDirac` and `int_dirac_value` give an actual consistent Int instance.
Normalized nonnegative integer weights only provide deterministic selections;
this does not establish a nontrivial rational or Real distribution instance.
Exact fractional calibration and the paper Real interpretation are separate.
The nonrectangular conditioning example and its rectangular repair are paper
and executable finite evidence, not a general kernel dynamic-consistency result.

## Free-process resource contexts

`Can C F a b` means an actual F-admitted arrow a→b exists.
`can_refl` uses the supplied category identity and free identity premise.
`can_trans` uses actual composition and the supplied closure premise.
`resourceOrder.le a b` is Can b a, so more convertible resources are higher.

Each `targetContext C F z` is a total Bool Context on the category's objects.
Its value is true exactly when an F-admitted arrow reaches z.
The observation equation uses total admission and evaluation.
`target_monotone` proves false≤true monotonicity in the stated orientation.
`target_family_complete` reconstructs conversion from all target comparisons
by choosing the destination as target and using its free identity.

This complete family uses every object as a target.
It does not recover hidden illegal/undefined objects from restricted observations,
force antisymmetry between distinct objects, supply the free-arrow predicate,
or construct a tensor. No single canonical scalar follows.
The target-family construction is classical parent mathematics.

## Trust and exclusions

Classical reasoning is used for arbitrary predicates, minimum comparisons and
existence arguments; finite parsing itself is executable.
The audit permits the standard Lean logical foundations and inspects assumptions;
there are no unproved placeholders or new asserted mathematical assumptions.
No proof establishes Python/Lean implementation equivalence, efficient execution
of the infinite envelope, effective environment enumeration, computability of K,
a unique intelligence ranking, or all-family architecture derivation.
