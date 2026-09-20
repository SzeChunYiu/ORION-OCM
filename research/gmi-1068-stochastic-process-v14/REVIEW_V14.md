# Independent V14 scientific and API review

Verdict: no unresolved scientific/API defect found in the reviewed implementation.
Reviewer wrote THEORY/ADJUDICATION/PARENTS/CORE, but did not write the production
Python, independent oracle or tests. Independence concerns those implementations;
this is not a second independent author of the mathematical paper.
Formal evidence and its remaining boundaries are in FORMAL_REVIEW_V14.md.

## Production representation and assumptions

Kernel stores both source and target dimensions, so empty arrays do not identify
0→0 with 0→1. Rows normalize to exact Fraction values. Scalar admission rejects
bool, floats, negative entries and nonunit row sums. Dimensions are exact
nonnegative integers; map targets and relation entries have strict index types.
Relation rejects empty rows for every actual source, while empty-source arrows
remain valid. List/tuple rows and permitted relation set containers normalize
without changing the mathematical arrow. Raw list entries are validated before
relation deduplication, preserving rejection of Boolean aliases.

compose_kernel validates the arrow types and matching middle dimension before
forming the first-then-second matrix product. The output constructor checks
normalization again. No projection onto the finite input grid occurs. There
are therefore no hidden rounding or grid-closure premises in composition.
compose_relation has the same typing guard and existential reachability meaning.
Dirac and graph constructions preserve explicit dimensions, including 0→0.

support uses exact positivity, not floating-point conversion or a numerical
threshold. For validated nonnegative rational inputs, positivity agrees with
nonzero support used in the generic proof. uniformize returns the declared
uniform row law, but neither its API nor the paper claims it is a functor.
The explicit nonfunctoriality witness prevents treating relation composition
as a uniquely selected probability law.

## Independent oracle and corpus design

Read independent_oracle_v14.py and all mathematical/hostile tests. The oracle
imports no production implementation. Its kernel oracle sums products over
complete intermediate-state assignments, rather than invoking or nesting the
production matrix product. The relation oracle propagates reachable sets.
Their source/target dimensions are retained in returned tuples.

The grid enumeration filters complete rows by exact sum one, then independently
forms every matrix for dimensions 0,1,2. Its empty products correctly include
empty-source arrows and exclude nonempty-source arrows into an empty target.
Every typed pair/triple is tested against the independent semantics. Off-grid
products are counted and retained; the grid is not claimed to be a category.
All total relations and deterministic maps on those dimensions are covered.
Embedding tests check identity, composition, faithfulness and three-stage chains.

The distinct seven-arrow witness is closed. Its composition is compared against
actual matrix arithmetic and its interpreted matrices are pairwise distinct.
The tests separately establish the actual 1/3 versus 2/3 event probabilities
and equal full support. Four arrows are deterministic. This supplies a genuine
probability example; a generic natural-number model alone would not suffice.

## Hostile controls and scope

The actual asymmetric reset/flip pair detects reversed composition. A positive
rational of magnitude 1/10^400 remains supported, while a float-based mutant
loses it. Empty carriers, wrong middle dimensions, alias scalars, negative or
nonnormalized rows, bad map targets and nontotal relations are rejected.

Signed cancellation is tested both without and with row normalization. The
coordinatewise N×N scalar control isolates zero divisors while retaining
zero-sum-free addition; the modular control also exhibits a zero-divisor failure.
The paper does not claim modular arithmetic isolates only that hypothesis.
Uniformizing R then T yields (1/2,1/4,1/4), whereas uniformizing R;T yields
(1/3,1/3,1/3). The relation and kernel constructions preserve possibility but
supply different information; no lossless equivalence is asserted.

The generic Weight interface admits Boolean weights. Its matrix normalization
therefore does not make every {0,1}-valued row deterministic. The paper correctly
restricts that characterization to ordinary rational/real probabilities and
uses exactly-one-supported-entry for the generic Dirac criterion.

## Bounded executed review probes

Executed on billy-laptop with Python3.12, normally and with -O. Four selected
existing tests passed in each mode: closed rational witness, malformed inputs,
empty/exact boundaries, and assumption/functor countermodels. Their deterministic
outputs agreed. This repeated the small 49-pair/343-triple closed witness,
83 malformed-input rejections and stated boundary controls; it did not rerun
the primary exhaustive kernel/relation corpus.

Additional temporary probes generated 40 exact rational three-arrow chains
(seed 106814), with dimensions 1–4 and weights formed from random integer rows.
A separately written distribution-propagation calculation agreed with both
composition bracketings and with support composition for every chain.
All 850 enumerated event masses lay in [0,1]. Three further empty-dimension
checks used 0→5, an empty intermediate object, and rejection of 5→0.
Normal and optimized outputs were identical. These probes are diagnostic
review evidence, not additional counts in the registered driver receipt.

The final exact kernel audit, source-valid corruption controls, snapshot bindings
and exact-head CI remain separate integration gates. This review earns no
architecture recovery, unique prior, infinite measure-theory or full-GMI claim.
