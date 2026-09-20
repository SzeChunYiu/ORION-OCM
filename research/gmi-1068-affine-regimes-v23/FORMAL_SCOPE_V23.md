# V23 formal scope
Only original R3-008 is eligible. Read CORE and FREEZE before this inventory.
Kernel proofs, paper rational analysis and finite Python calibration are
distinct evidence; no full theory or physical-transition claim is made.

## Fresh replay and assumptions
18 source modules:7 immutable dependencies and11 new modules.
122 exact typed declarations, including concrete operation/constructor bindings.
Lean4.19.0 with Std, warningAsError, isolated SOURCE compilation, then a
static typed AUDIT and printed registered dependency inspection.
Registered dependencies are within propext, Classical.choice and Quot.sound.
No new postulates or proof gaps are present. Runtime registration does not
discover its expected types from the source being checked.

From this package on laptop:
```sh
GMI_LEAN_BIN=/home/billy/.elan/bin/lean /home/billy/.local/bin/python3.12 -c 'import json, check_lean_v23; print(json.dumps(check_lean_v23.evaluate(), sort_keys=True))'
```
The checker stages every listed source into a fresh temporary directory and
sets LEAN_PATH there. SOURCE and AUDIT failures differ from an unavailable
compiler/input. The repository driver supplies isolated sibling-module loading.
Immutable sources are V12 ScalarLaws/FiniteSums, V15 PartialContext,
V17 ContextMaps, and V20 FrontierOrder/GuardedMaps/PartialPostcontext.
Their exact paths and bytes are included in the replay receipt.

Generic scalar theorems use the actual V12 Scalar interface: primitive
ordered commutative ring operations/laws, total order and 0<1.
They do not assume endpoint, root, optimum or decoder conclusions.
The actual inherited Int instance and concrete integer controls are registered.
There is no kernel Real, rational field, division or density instance here.
Classical finite filtering is explicit; no effective decision procedure for
arbitrary predicates or arbitrary scalar presentations follows.

## Arithmetic and whole intervals
AffineArithmeticV23 constructs affine(a,b,t)=a+b*t and derives multiplication
monotonicity for nonnegative factors, reversal for nonpositive factors,
strict positive-factor monotonicity, and affine difference identities.
lerp(s,x,y)=(1-s)*x+s*y is constructed by the actual ring operations.
Its endpoint/self identities, affine interpolation identity and interval
bounds are proved, with nonnegative normalized coefficients where needed.

AffineIntervalsV23 proves endpoint laws on the ENTIRE closed interval.
For each pair of lines, the difference is affine; its slope is either
nonnegative or nonpositive by scalar totality.
Compare the difference at t to its value at lo or hi accordingly.
Thus weak endpoint dominance implies weak dominance at every lo<=t<=hi;
strict dominance at both endpoints implies strict dominance throughout.
interval_le_iff/interval_lt_iff include lo<=hi for the converse, since
both endpoints must belong to the interval.
No division or representation of t as a normalized interpolation is used.
These results apply to Int and other nondense ordered rings.
Interpolation-specific weak/strict results are also independently derived.

The generic ordered-ring interpolation identity does NOT imply all interval
points are represented by normalized s in that ring. The concrete Int
control has lo=0,hi=2,t=1 and no suitable integral interpolation coefficient.

## Actual common-value Contexts and all IDs
AffineContextsV23 fixes admission P, evaluator domain E and coefficients.
active means P AND E. Context values are actual pairs (i,score_t(i)),
with one common preorder reversing scalar cost order and ignoring identity.
context is an actual V15 Context record, preserving E and its subtype domain.
Image uses actual V20 Attained, not a replacement image predicate.
pair_attained identifies exactly the active identity/score pairs.
maximal_pair and maximal_identity_projection equate actual full maxima to
every minimizing identity. They use scalar totality, not an assumed optimum.
Distinct IDs with equal scores remain distinct values and tied winners.
Neither a quotient by equal score nor an arbitrary tie-breaking rule appears.
For arbitrary infinite I these equivalences do not assert a winner exists.

Winner contains active membership plus weak dominance over every active ID.
UniqueWinner contains Winner and uniqueness of its identity among ALL winners.
StrictWinner contains active membership and strict dominance over every
OTHER active identity. Their equivalence is derived, including ties.
tied_winner proves that an active equal-score identity remains a winner.

## Actual code/decoder bridge
codedContext is an actual V15 Context with value i and score-induced preorder.
decode_t(i) is constructed as (i,score_t(i)), not supplied as a black box.
AffineDecodersV23 proves injectivity by first projection and exact comparison
reflection between the coded order and the common value order.
actual_postcompose is equality of the actual V17 postcomposition record
with the pair-valued context, including its evaluator and domain.
decoded_image and decoded_maximal_image prove both directions of image
and full maximal-image correspondence; no alias is silently dropped.
decoded_observe uses actual V17 post_observe and preserves ILLEGAL,
UNDEFINED and decoded VALUE. ConstructorBindings supplies each tag directly.
E-true/P-false ambient evaluation stays defined but yields an illegal admitted
observation, as required by the original partial-context distinction.

The generic code carrier is I; the finite implementation uses indices and
a checked mapping to unique external labels. Its serialization/label mapping
is finite test evidence, not a general kernel refinement proof of Python.
A parameter-indexed decoder may assign a different score to the same code.
The concrete parameter_dependent_decode control demonstrates this.
Winner comparisons across contexts use fixed identity; numeric value
comparisons use the common decoded space, not bare reused integer codes.

## Universal and finite winner statements
AffineWinnersV23.universal_winner proves, for lo<=hi:
an identity wins weakly at every parameter iff it wins at both endpoints.
universal_unique_explicit proves the exact stronger statement:
the same identity uniquely wins everywhere iff it is active and strictly
beats every other active ID at BOTH endpoints.
A singleton intersection of weak endpoint winner sets is not this condition.
The actual 0 and t lines tie at0, although their endpoint intersection is
a singleton. weak_intersection_singleton/tie_at_zero/not_unique_at_zero
bind and prove that control.
No-active, singleton-active and zero-width cases have explicit theorems.

FiniteWinnersV23 constructs activeList by filtering and winnerList by the
actual immutable V20 full frontier, with the score-induced reverse order.
For a complete finite roster, winner_mem proves exact all-winner membership.
finite_winner derives existence when the active roster is nonempty.
The finite list may repeat an ID; the result is membership semantics,
not a claim about raw list cardinality or canonical Python output ordering.
Distinct active IDs with equal scores are all retained.

PossibleWinnersV23 defines the existential-parameter possible-ID family.
singleton_possible proves that this family is exactly {i} iff i uniquely
wins everywhere, for a complete finite roster and nonempty closed interval.
Its proof invokes actual finite_winner at each parameter.
No separate nonempty-active premise is hidden: either side supplies an
active i, while the finite-roster premise supplies minima elsewhere.
This kernel corollary is about all parameters. Equality of the possible
family with a computed rational diagram's sampled union remains below.

## Earned conditional root certificates
RootCertificatesV23 proves affine_delta, then factorization from a supplied
checked equality at c. pair_root_factor explicitly gives slope*(t-c).
crossing_left/right derive strict ordering on either side when slopes are
strictly ordered. root_unique proves uniqueness under that slope condition.
Swapping the two lines supplies the opposite slope orientation.
parallel_root proves equal-slope lines meeting once have equal intercepts.
The equality at c is an algebraic premise, not assumed sign constancy.
These theorems do NOT establish existence of c in the carrier, a dense set
of parameters, root sorting or completeness of a rational diagram.
integral_root_gap proves an actual Int sign reversal without an integral root.

## Paper and finite boundaries
General Q/R root existence, interval root enumeration, ordered boundary
coverage, midpoint completeness and the full rational diagram correctness
argument are PAPER proofs plus exact Fraction independent calibration.
The independent oracle's weak-halfline intersection algorithm and its
whole-cell checks are not Lean-formalized.
The diagram sample union/intersection correspondence uses those paper
completeness facts; it is not implied by the integer consistency instance.
A lower-envelope change is a change of inducing IDs, not every pair crossing.
Numeric values can vary while the winner-ID set stays constant.

Nonlinear/intervention-dependent objectives or changed P/E do not satisfy
the fixed affine-family premises. A concrete nonlinear endpoint failure
is kernel checked; other named rational/codec controls are finite evidence.
Legacy affine helper comparisons and original R3 switch replay do not prove
all historical Gamma/Pref/SEL transports. R3-009 stays outside this result.
No compact-graph complexity, thermodynamic interpretation or novelty follows.

ConstructorBindings registers operations, contexts, decoders, active/winner
predicates, actual filters/frontiers and outcome equations.
ProofTargets supplies independent endpoint_contract,
decoder_maximal_contract and universal_winner_contract leaf statements.
Source-valid True replacements must compile SOURCE then fail typed AUDIT.
Python parser correctness, exact measured coverage and canonical returned
data have independent executable evidence; they are not kernel conclusions.
