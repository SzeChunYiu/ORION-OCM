# V19 independent scientific and executable review

Reviewer role: author of the paper derivations, independent of the production
and oracle implementations. This is not a second independent authorship review
of the paper. The separate FORMAL_REVIEW_V19.md reports kernel inspection.

## Actual implementation inspected

Read partial_v19.py, categories_v19.py and responses_v19.py in the V19 worktree,
then oracle_v19.py and the table, recovery, witness and hostile tests.
The partial operation stores None distinctly from every arrow index. The unit
predicate checks the self-product and both conditional neutrality clauses.
The associativity check compares Option outcomes; coherence is a separate check.
Reconstruction computes unique units and endpoints before constructing Typed,
then independently validates the resulting category laws and full definedness.

The finite Typed representation labels arrows globally and records both endpoints.
flatten preserves this actual indexed composition table; bundles and
bundled_product additionally expose and check the source/target/arrow triples.
The paper's dependent-type transport is handled in Lean, not inferred from this
finite indexing convention. Empty tables and categories are admitted. Invalid
shape and Boolean-as-integer aliases are rejected before indexing or deduplication.

All word symbols are validated before evaluating any product. Thus an invalid
suffix cannot be hidden by an already failed prefix. Query represents every raw
nonempty word and every candidate empty anchor; illegal cases return None after
validating the query instead of disappearing from its type. The derived empty
response uses the actual table's unit predicate.

## Separately executed bounded probes

Executed on billy-laptop with Python 3.12, once normally and once with -O;
serialized counts were byte-identical. Checks used explicit failures, so Python
optimization did not disable them. The probe independently constructed groupoids
with 0–3 objects and cyclic arrow groups of orders 1–3, including 27-arrow
examples outside the exhaustive size-three-table corpus.

| Actual check | Count |
| --- | ---: |
| Typed category constructions and both table roundtrips | 12 |
| Actual bundled-product comparisons | 180 |
| Independently evaluated raw words, lengths through 12 | 540 |
| Relabeled word and anchored-empty comparisons | 624 |
| Malformed suffix rejections after failed prefixes | 7 |
| Weak-associativity control law and triple checks | 29 |

The construction used arrows (a,b,g) and multiplication
(a,b,g)(b,c,h)=(a,c,g+h modulo k), deriving expected results independently.
A fixed seed 106819 selected the bounded words and permutations. These counts
are supplementary review evidence and are not inserted into the primary receipt
as additional exhaustive-corpus counts. No full primary corpus was rerun here.

## Finite oracle and counting audit

The primary oracle computes law flags and, separately, the typed reconstruction
criterion: unique endpoint identities, exact matching, composite endpoints and
typed associativity. The exhaustive test compares this criterion with the
three-law predicate on every registered table. Its accepted counts therefore
come from actual enumeration, not a hard-coded list of category templates.
It checks every accepted table's raw words through length four, every anchor,
all arrow permutations and object permutations. Counters increment inside the
actual loops; the coverage guard requires exact module/key sets and integer
counts, rejecting Boolean aliases. Recovery tests enumerate actual decoder
outputs on binary code spaces and use the real length-two queries to extract
products, including models that do not satisfy the category laws.

The witness tests contain the actual three-element weak-law countermodel,
not a test label asserting that such a countermodel exists. The two-element
coherence failure, three-element associativity failure, projection controls,
fresh-bottom comparison, C4/V4 products and nonunital idempotent map are distinct
failure mechanisms. The small total-unital associativity search does not claim
a bound for all partial algebras.

## Scope and custody audit

Read check_reconstruction_v19.py, custody_v19.py, and successor CORE and
RECONCILIATION_V19. The source checker binds the committed preregistration and
verifies it preceded outcomes; it checks ancestry without serializing current
HEAD. It dereferences inherited receipt inputs and their source bindings,
checks the two historical qualified IDs, and retains historical count authority.
Missing files or unavailable git evidence have a distinct cannot-check path.
The final receipt must bind the exact independent modules and typed proof
inventory; a pending file or theorem name by itself is not verification.

The driver now explicitly requires ROUNDTRIPS_V19.md and CONTROLS_V19.md
because substantive proofs live there; this addition was re-read and verified.
Its full input inventory also hashes these details. Successor wording preserves all original records and reports
20/202 original counts with two qualified readings separately leaving 200 active.
It does not create a new amendment or silently promote original minimality.

No executable semantic defect was found in the inspected production or bounded
probes. The paper records the weaker parent-unit reading as a precise premise
limitation and proves the stronger side-specific identity mapping directly.
Final formal and integrated replay conclusions belong to their own evidence;
they are not implied by this code review.
