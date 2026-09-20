# Independent executable/scientific review — V15

Verdict: the reviewed executable now matches the frozen context and separation
scope. One actual construction defect was found, repaired and independently
retested before acceptance. No remaining scientific/API defect was found.
The reviewer authored the paper notes, but did not author production code,
the independent oracle or its tests. This review is independent of those
implementations, not a second independent paper author.

## Actual construction defect and repair

The initial opposite() implementation set high only at b for its first map,
and low elsewhere. The registered theorem uses low only at a and high
elsewhere. These coincide when D={a,b}, but differ on a third history.
An actual laptop probe with D={0,1,2}, a=0,b=1, lo=0,hi=1 and
Allowed={(0,1,1),(1,0,0)} was rejected: the observed candidate was (0,1,0).
The failure was attributed to the evaluator construction stage, not Allowed
or the theorem. Unrestricted-Allowed calibration alone did not expose it.

Production now constructs exactly (low at a, high elsewhere) and
(high at a, low elsewhere) on D. The same concrete probe accepts and receives
exactly (0,1,1) and (1,0,0). The persisted oracle suite includes a positive
registered-indicator class and a negative nonmatching-indicator class.
Both controls and the full selected suite passed independently after repair.

## Domain and observation semantics

Context validates dimensions before use; bool/float aliases are not accepted
as integer dimensions, histories or values. Admission/evaluation flags and
order entries must be actual bools. Definedness has its own flag, with None
required exactly outside E; values in E must lie in the declared codomain.
The order table must be reflexive and transitive, but may be nonantisymmetric.
List/tuple inputs normalize only after validation. No invalid order is repaired
silently by taking its closure.

observe checks admission first, preserving ILLEGAL even when an ambient value
exists; admitted unevaluated histories return UNDEFINED. VALUE(0) remains
different from UNDEFINED even if the external label for value0 is 'UNDEFINED'.
Comparison rejects histories outside D=P∩E rather than assigning false and
claiming a preorder on all H. Empty codomains/domains and equivalent values
are represented explicitly. quotient uses mutual comparison, retains all
classes, and compares representatives only after the preorder is validated.

Allowed receives only the ordered tuple of candidate values on D. It does
not see illegal ambient evaluations. Those outside-D values are preserved in
the returned Context but cannot change evaluator-class membership. Histories,
strict value pairs, a callable membership predicate and actual Boolean True
membership are validated. Changing either admission or definedness is not
part of the opposite-evaluator construction.

## Oracle independence and fixed process

The oracle has no production imports. It enumerates Boolean order tables and
five-way history assignments; induced comparisons use a set of ordered pairs.
Its quotient algorithm computes connected components of mutual comparison
and uses all-member comparison between classes. Production instead picks one
representative and compares it directly, so the algorithms are distinct.
The tests include empty domains and nonantisymmetric value preorders.
The claimed 3625 corpus and 12960 unrestricted reversal counts are primary
suite evidence; this reviewer did not duplicate those exhaustive runs.

The fixed-process witness is the complete one-object C3 category represented
by its object set, indexed arrows with endpoints, identity, full composition
table and admission flags. The test executes 6 unit, 9 endpoint/composition
and 27 associativity equations. Both evaluator models reference the same
complete process object, which also equals a freshly reconstructed payload.
Actual ordering and evaluator values differ while this payload remains fixed.
The unrestricted context corpus is separately identified as domain/evaluation
calibration; its arbitrary admission subsets are not asserted to be categories.

## Independently executed targeted evidence

After repair, ran all four hostile test methods plus the complete-process
method on billy-laptop in normal and optimized Python. All five passed and
their serialized coverage was identical. This includes 81 malformed inputs,
16 failed reversal-premise cases, the actual 42 process-law equations, both
new indicator-class controls, the ambient-domain controls and rejection of
an always-accepting quotient diagnostic on real corrupted candidates.
The explicit three-history Allowed-set probe also passed in both modes.

A separate seed106815 diagnostic generated 160 further contexts with up to
7 histories and 5 values. It formed valid orders by Boolean reachability
closure, used independently varied admission/definedness, mixed list/tuple
containers and possible evaluations on illegal histories. Direct checks of
530 observations, 312 domain pairs and 159 quotient class pairs passed in
both modes with identical counts. Checks used explicit exceptions rather
than assert statements, so optimization did not remove verification.
These diagnostics are not added to the mandatory production receipt counters.

## Remaining scope boundaries

The scalar order and Allowed class are supplied. Separation is conditional
on a strict pair and two permitted actual functions; a constant-only or
observation-collapsed class need not permit it. The quotient captures the
current evaluator's comparisons, not process behavior. No decoder or prior
is inferred from a process lacking enough information to identify its output.

The exact general kernel coverage is reviewed in FORMAL_REVIEW_V15, separately
from the Python execution evidence. Only original R2-001 and R2-004 are
eligible for closure. Semantic nonrecoverability is not probabilistic
independence, and the repaired diagnostic is not an empirical novelty claim.
