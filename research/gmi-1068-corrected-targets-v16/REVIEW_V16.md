# Independent science/API review — V16

The current production and independent finite tests respect the frozen
qualified-reading scope. No concrete scientific/API defect was found.
The reviewer authored the paper notes and preregistration but did not author
production Python, the independent oracle or its tests. This is independent
implementation review, not independent authorship of the target statements.
Final kernel and amendment authority checks remain separately documented.

## Typed history and extraction boundary

Read history_v16.py, oracle_v16.py and test_history_v16.py. Graph retains an
explicit vertex count and indexed edges, allowing parallel edges with equal
endpoints. Strict integer validation rejects Boolean/float aliases before
indexing. validate_history keeps a start vertex and checks every edge source
against the preceding target; it returns the actual terminal vertex.
Empty paths require a valid start, so an empty graph has no fictitious object.
Admission validates an exact Boolean mask before testing all path edges.

Singleton decoding queries the actual typed singleton for each indexed edge.
It intentionally does not certify that a callback is a generated full domain.
The hostile callback accepting paths of length<=1 extracts the all-true edge
mask yet rejects a legal two-edge admitted path. This is retained as a concrete
premise failure, not counted as an API error or hidden by changing the theorem.
An evaluator-defined empty subdomain likewise cannot replace the full source.

The independent enumeration constructs all registered graph/admission pairs
and traverses endpoint-correct paths without calling production validators.
For admitted subgraphs, the test explicitly forgets/reindexes edges, restores
them, checks endpoints with production validation, and compares the entire
lifted path set with the independently selected admitted ambient path set.
Thus subtype correspondence is exercised on actual paths, not selector labels.
The generic arbitrary-graph correspondence is separately a formal proof.

## Actual group composition and contextual equality

Read algebra_v16.py and test_algebra_v16.py. Monoid validates an actual square
composition table, in-range labels, both identity laws and associativity.
C4 and V4 build different tables; fold uses each supplied table and its unit.
context returns parity of that actual product. No context-specific selector
is supplied in place of composition. The independent oracle instead uses total
label sum modulo4 and parity counts of the two bits, respectively.

The primary test checks products, units, associativity and the parity
homomorphism, then the registered word corpus. Separate controls verify
nonconstancy, the changed composition at(1,1) and different evaluation kernels
on [1,1] versus[2]. Reindexing one operation without transporting the observation
is a negative control. Python's left fold and Lean's recursively associated
fold are justified by the proven associative unit laws; no certified extraction
between these implementations is claimed.

## Exact linear computation and its limits

Read linear_v16.py and test_linear_v16.py. Vectors/results must be actual
Fraction values in canonical tuples; dimensions and callbacks are validated.
weighted is the finite dot product and retains exact off-grid results.
nonnegative and normalized concern coefficient vectors, not arbitrary functions.
basis_coefficients checks callback result types at zero/basis inputs and extracts
values; it deliberately does not certify additivity or homogeneity.
representation_at checks one actual supplied profile only.

The tests enumerate registered coefficient/profile inputs and compare exact
scores with a separate loop oracle. Ordered-profile checks, negative-coordinate
witnesses, additive shifts and several rational scales exercise the declared
weighted functions. These computations do not prove arbitrary callback linearity.
The stored nonlinear impostor matches basis and ones while failing an actual
additivity/representation probe. The zero-dimensional constant-one callback
also exposes the distinction between extraction and linearity. Callback OSError
propagates as unavailable evidence rather than a successful mathematical check.

## Independently executed bounded diagnostics

On billy-laptop, independently ran four selected methods: typed-domain hostiles,
algebra hostiles, nonlinear boundaries and malformed linear inputs. All passed
in normal and optimized Python, with identical serialized coverage. They include
37 history,23 algebra and39 linear malformed-input rejections; the nongenerated
path callback; min/max exact controls; nonlinear and n=0 impostors; and two
callback-unavailability controls. The main exhaustive corpus was not duplicated.

A separate seed106816 diagnostic checked 80 words of lengths7..90 against
independent sum/bit-count products and parity, 60 coefficient/profile cases in
dimensions4..6 for basis recovery, additivity and monotonicity, and 60 random
typed paths of length0..10 on a three-vertex graph with parallel arrows for
endpoints, admission and singleton decoding. These passed identically in normal
and optimized modes. Explicit exceptions performed checks, so optimization
could not remove assertions. Counts are review diagnostics, not extra mandatory
receipt coverage or an expanded scientific claim.

## No scope promotion

P1 assumes an exact generated full raw source; it cannot validate arbitrary
source callbacks or infer physical law. P2 compares full raw-domain contexts,
not process-dependent quotient histories. P3 assumes full-domain additivity and
all-scalar homogeneity; finite basis probes cannot supply those assumptions.
The general kernel theorem, actual Int consistency, Real/Rat paper interpretation
and Fraction calibration must remain separately described in FORMAL_REVIEW.

The originals remain UNKNOWN and their V15 snapshot remains unchanged.
Qualified replacement attestation belongs to the new sidecar; it is not an
original CLOSED disposition. The separate governance gate and source-valid
proof-corruption controls must pass before the replacement is authoritative.
