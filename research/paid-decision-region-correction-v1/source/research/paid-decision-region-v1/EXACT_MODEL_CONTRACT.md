# Exact DRD successor contract

The helper minimizes worst-case cost over finite terminating decision trees on a
finite, nonempty admitted hypothesis set. It is conventional decision theory.
The true world must remain in that set for common-action safety to hold.

## Numeric and state domain

`exact_numeric.py` reuses the qualified PR159 `_rational` and `_items` function
bodies verbatim. Numeric inputs are built-in int, Fraction or finite built-in
float, interpreted as their exact stored binary rational. Boolean, Decimal,
string and nonfinite numeric inputs refuse. Results are Fraction values.
No decimal intent, rounding tolerance or arbitrary-real computation is inferred.

Action costs may be signed and finite. Probe costs must be nonnegative and are
validated before uninformative probes are skipped. Hypothesis IDs are distinct,
hashable and mutually sortable, as required by the original version-space code.
Safe-action/probe IDs are distinct and hashable; None is reserved for no stopping
action. Finite iterables are materialized before recursive reuse. Deterministic
probe outcomes must be available for each probe/hypothesis and be hashable.
Inputs remain stable throughout a call. Tied minimum action IDs must support the
original tie order `(str(action), action)`; exact ties between STOP and a probe
retain STOP. No result here establishes protected-model adequacy.

## Proper terminating policy

Each retained probe partitions the current set into strictly smaller nonempty
sets. An uninformative probe has nonnegative cost and cannot improve a terminating
policy, so it is omitted. This yields finite recursion even at zero probe cost.
It does not assign a value to arbitrary policies that loop forever. The displayed
Bellman equation in the formal note is interpreted in this proper finite-tree
class, not as an unqualified fixed-point selection theorem.

The recurrence uses min/max worst-case cost. It is not PR159's expectation-based
finite-allowance DP; only the shared numeric/domain foundation is reused.
The fixed-prefix unanimity lower bound assumes an unstructured verdict oracle
whose unseen suffix admits the alternative completions in its proof. It does
not exclude cheaper structural inference or already-paid information.

## Declared source custody and execution scope

`donor_custody.py` checks the digest of `DONOR_SOURCE_PINS.json`, then exact byte,
SHA256 and Git-blob identities for its three declared donor/runner/plan modules.
The adapter and runner call this before their donor imports; imported module
paths and the donor function's exact source digest are checked as well. Drift
refuses instead of advertising a constant as observed authority. That inventory
is deliberately not a full transitive closure or study requalification.
The unresolved historical DEV6 ref is preserved separately in source custody.

The existing sweep runner's receipt schema becomes v2 only to make this bounded
source assertion explicit. No v2 result has been produced. No donor, sweep,
native verifier or learner was executed to qualify this correction. The existing
workflow is unchanged and still invokes donor simulations/full sweep; it has not
been triggered or newly qualified by this capsule.

The short-circuit change remains a D1 tariff correction: the donor already exits
at first disagreement, and both versions copy the survivor tail. Its modeled
work excludes D0 and gives storage bit-steps zero price. Source-check overhead,
Fraction arithmetic/serialization and complete runtime/lifetime costs still need
accounting during any later integration. No previous aggregate result changes.
