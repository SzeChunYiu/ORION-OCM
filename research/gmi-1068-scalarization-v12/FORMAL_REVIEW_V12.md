# Independent formal-scope review V12

Verdict: CLEAR after the T5 declaration correction and independent fresh build.
This review covers ScalarLawsV12.lean, FiniteSumsV12.lean and
ScalarizationV12.lean against frozen T1–T6. The reviewer did not author
these Lean modules. The reviewer authored the paper proofs; this is an
independent review of their mechanization, not a second independent paper.
It grants no authority to a later driver, receipt, snapshot or CI result.

## Primitive scalar assumptions

**Assumptions.** Lean's dependent type theory, imported Std, and the explicitly
supplied Scalar structure; no unstated real-number implementation.
**Dependencies.** ScalarLawsV12.lean and its concrete Scalar Int instance.
**Falsifiers.** An assumed vector conclusion, inconsistent scalar interface,
missing nontrivial model or incorrectly identified real-number instance.
**Strongest parents.** Ordinary linearly ordered commutative ring laws;
Lean/Std own the integer arithmetic implementation and foundational rules.

The interface supplies scalar operations, additive group laws, commutative
associative unital multiplication, distributivity, reflexive/transitive/
antisymmetric total order, strict comparison iff weak comparison and inequality,
translation preservation, nonnegative/positive product rules and 0<1.
No field assumes dot-product monotonicity, separator existence, positive-family
order recovery, opposite rankings or Pareto efficiency. Assuming scalar
product positivity is a legitimate ordered-ring premise, not a scalarization
conclusion in disguise. Some laws are redundant; that does not enlarge scope.

Zero and one are genuine interface values; 0<1 plus lt_iff rules out a
collapsed zero ring. The Int instance supplies every field with existing
integer facts or kernel-checked elementary arithmetic. Thus generic statements
are conditional on an interface with a concrete nontrivial instance.
No Real or rational ordered-ring instance is constructed by these modules.

## Finite sums and T1–T2

**Assumptions.** Any universe-polymorphic scalar type with Scalar instance;
any natural dimension n; vectors are functions Fin n→α.
**Dependencies.** Derived scalar difference/multiplication inequalities and
structural induction defining sum, sum_le and sum_strict.
**Falsifiers.** Restricting the theorem to one dimension, assuming sum-order
preservation as an interface field, or overlooking zero-weight strictness.
**Strongest parents.** Finite sum order preservation; the registered
Boyd–Vandenberghe positive scalarization argument.

The sum is defined recursively, not postulated. sum_add, sum_neg, sum_mul,
sum_le and sum_strict are derived. dot_monotone proves T1 with all weights
nonnegative. dot_strict proves the sharper T2: one improving coordinate has
positive weight while the others need only be nonnegative. Neither theorem
silently requires every coordinate to improve or allows a zero-weight-only
improvement to imply strict score order.

Dimensions are arbitrary, not the executable grid 0–4. Fin0 has the actual
empty sum. The strict-sum branch eliminates an impossible Fin0 coordinate;
it does not manufacture a witness or prove all cases from an empty domain.
The mathematical transport from Fin n to another finite indexing set is a
paper reindexing step, not a separately claimed Lean equivalence theorem.

## Constructive separator and T3–T4

**Assumptions.** The primitive scalar interface; classical logic where needed
to select a violated coordinate from a failed universal comparison.
**Dependencies.** magnitude_bounds, except/sum_split, separator_formula,
separator_positive, separator_dot_positive and dot_difference.
**Falsifiers.** Wrong excluded coordinate, nonpositive separator coordinate,
incorrect score sign, or an assumed separator conclusion.
**Strongest parents.** Positive dual-order separation, here with the explicit
division-free witness specified in the V12 freeze.

Magnitude is defined as a if 0<=a and -a otherwise. Its two used bounds are
proved by cases from scalar total order and translation. It is noncomputable
in the generic interface; no extracted decision algorithm is claimed.
Except replaces exactly the selected coordinate by zero. The separator's
selected entry is the sum of other magnitudes plus one; every other entry
is the selected positive difference. Thus all entries are proved positive.

The score formula factors into the selected positive difference times
1 plus the sum of magnitude-and-difference terms outside that coordinate.
Those terms are nonnegative, so the factor is positive. The resulting strict
score direction feeds separating_weight. No division, real completeness,
Archimedean bound, finite weight grid or limiting argument appears.

positive_family_recovers_order proves T3 over ALL positive weight functions.
Incomparable_reversal invokes separation in both orientations. Its existential
weights are ordered oppositely to one prose naming convention, but the two
required strict directions are both present; renaming bound witnesses resolves
that harmless difference. It is not merely the two-coordinate calibration.

## T5–T6 and the corrected reflection contract

**Assumptions.** T5 needs only a totally comparable target relation; T6 needs
an attained minimizer with positive weights over an arbitrary feasible predicate.
**Dependencies.** Total comparison and T2; original frozen T5/T6 statements.
**Falsifiers.** A kernel claim excluding only full equivalence when the freeze
asks to exclude reflection alone, or an unearned existence-of-minimum claim.
**Strongest parents.** Total-versus-partial order logic and the classical
positive-weight Pareto guarantee.

The initial T5 theorem excluded maps satisfying r(a,b) iff score(a)<=score(b).
That was weaker than the registered impossibility of reflection alone,
score(a)<=score(b) implies r(a,b). The actual proof used only that implication.
This exact-scope mismatch was reported to the mechanizer and root for repair;
The corrected declaration now excludes the reflection-only implication. Its
proof applies that implication directly in either total-comparison branch.
The stronger type was independently re-read and instantiated in the probe below.

ParetoEfficient includes feasibility and excludes a feasible coordinatewise
improvement with one strict coordinate. Under total scalar order this is the
usual domination-plus-unequal-vector notion used in the paper. Minimizer
includes feasibility and the universal score comparison; attainment is not
inferred from an arbitrary nonempty feasible set. T6 derives efficiency by
contradicting minimality with dot_strict. It assumes no convexity or finiteness
of the feasible set and does not claim the unsupported converse.

## Verification record and boundary

The source inspection above found no assumed conclusion or scalar-interface
defect. The only identified issue was T5's initially weaker map contract.
The correction has been verified in the actual source and fresh build below.
The Python exhaustive corpus was not rerun for this audit.

Real-valued T1–T6 remain complete paper theorems with explicit scalar premises.
Generic kernel theorems plus Int instantiation are not a kernel construction
of the reals. Do not replace that boundary with a claim of real-number formal
coverage merely because the paper's reals satisfy the interface laws.


Independent laptop replay used pinned Lean4.19.0, warnings as errors, and a
fresh temporary LEAN_PATH. All three modules compiled from source, then an
independent probe compiled four actual specializations: arbitrary-dimensional
Int family/order iff; reflection-only impossibility from Bool equality into
Int order; a nontrivial two-coordinate Int opposite-ranking witness; and
Int minimizer efficiency for any feasible predicate. The probe's coordinate
counterexamples were proved explicitly, without assuming a decider for CoordLE.

Axiom inspection of T1/T2/T6 reports only propext and Quot.sound; T3/T4 also
use Classical.choice. T5 reports no axioms. No sorryAx or additional supplied
scalarization axiom occurred. Generic Scalar laws remain explicit parameters,
not hidden global axioms. These results bind the following inspected files:

| File | SHA256 |
| --- | --- |
| ScalarLawsV12.lean | fc6a14981c710647135e2354616db6170fa7c5e483c61ca3a0e9f58de8887f1e |
| FiniteSumsV12.lean | efaad21772778c70ab2bfea3aedcf26841f9895da104111ba299e9edd7117638 |
| ScalarizationV12.lean | 5371c34c2ab3d12657ebf9471b96b6cd519ce1374b9f8ca636830d1ab3e12c26 |

This independent replay does not replace the integrated receipt's exact-type
registration and source-valid corruption tests; those remain separate gates.
Only FORMAL_REVIEW_V12.md was written in the repository by this review.

The final proof_contract_v12.py was also read: its 17 entries have explicit
expected types, including reflection-only T5, its feasible-domain subtype
specialization and ordinary Int order/strictness. The fresh kernel checker
passes those 17 entries with audit SHA256
f2da29ab236601208c096f320aac24952aacdd2a4fbf2b534769a25f18a00767.
This verifies the registration component, not the full integrated receipt.
