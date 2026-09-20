# Independent implementation and scientific-scope review

The reviewer authored the V26 paper derivations and optional ledger, and independently
reviewed root's production/driver/custody and the oracle's calibration design.
This is independent code/proof review, not a second independent paper authorship.
All execution described here used billy-laptop. Frozen parents were not modified.

## Actual production source reviewed

core_v26 loads actual V25 syntax/evaluation and V19 category types; it rejects a
cached same-name module from a different source path. checked_path validates every
word entry before execution, including later entries after a would-be failed join.
Functor validates both categories, total strict maps, endpoints, identities and
legal source composites. It does not assume object injection or reflected joins.
Total-map tree translation preserves all nesting and both leaf maps; malformed
later descendants are not hidden by semantic short-circuit. Responses retain and
validate their actual endpoint bundle instead of accepting an arrow ID alone.

Wide restriction tests exactly the original identities and inherited composites.
It sorts supplied unique arrow IDs, retains every object, and remaps only arrows.
Its returned actual functor exposes all labels and is checked against actual V19
category laws. A nonidentity idempotent is not silently substituted as an identity.
The implementation's missing-identity and missing-composite cases are separate.

ResourceLift validates every declared cost and all additive laws, constructs the
full bounded-balance subcategory, and orders arrows by (baseArrow,initialBalance).
Its projection is allowed to collapse objects. lift_path follows the actual supplied
word with coherent balances; it does not replace it by a shortest path or by its
composite. Empty paths retain anchors/balance. Ill-typed and unaffordable words
return None after full structural validation; these causes stay distinct in tests.
No semantic production defect was found in this source review.

## Directly executed frozen named controls

The reviewer independently constructed the four-arrow indiscrete two-object category
and its functor to the terminal category. Every fixed Hom is a singleton, so the
functor is fully faithful, yet the unequal Empty-anchor pair fails before mapping
and succeeds afterward. This executes the stronger equivalence counterexample
outside exhaustive stratum A, without inflating A's candidate/tree counts.
The C2→terminal control confirms that object injection permits full transport
while distinct successful arrows collapse. The declared chain resource control
confirms raw unequal-balance failure and exact same-word balance1/balance2 revival.
These are three named, preregistered control families, not a new sampled corpus.

Script: /tmp/gmi-v26-independent-probe.py
SHA256: 28c2fa1015531b536bdb8a4bd9b37a0643f815fb28065d96ad39bcf25924a6eb
Normal and -O executions both passed all three families with identical JSON.
Receipt SHA256: e2fb795bdef41b292582d5cf0e41fa5d2f74d124addc595c36b0afb7d41ad775
Records: /tmp/gmi-v26-independent-normal.json and -optimized.json.

## Actual custody and six-row evidence

Both named-control executions also ran actual custody.verify and audit_optional.verify
against this repository. They verified551 distinct source bindings and all six
original component/status rows in their exact order. The freeze is an ancestor,
contains no V26 outcomes, and has the expected43 direct parent pins.
Inherited receipt inputs are dereferenced to actual current files, not accepted
solely because a historical receipt exists. The two V16 qualified IDs remain
003@r1/007@r1, with their exact science/ledger binding and no original atom closure.

The optional ledger correctly separates no-tensor on an unchanged category from
no-braiding for a chosen tensor. It retains V14 support assumptions and concrete
probability loss, branches rather than a selector, and equality2-homs rather than
arbitrary higher information. Closed admission does not infer a physically correct
predicate or recover its values on excluded ambient arrows. The guard validates
schema/source/row identity; it does not prove arbitrary natural-language text.

## Driver, oracle and disposition

The independent oracle derives endpoint assignments, recursion and resource traversal
separately. The reviewer inspected its actual A and C tests, confirming accepted-map
rather than all-map tree counts, explicit two-Empty witnesses and literal path
projection. Exhaustive primary runs belong to the canonical RESULT; they were not
repeated or counted as this review's three independent named controls.
The driver binds exact original006 title, mandatory modules/counters and fresh
kernel replay before emitting VERIFIED_AT_REGISTERED_SCOPE. Its Z1 wording was
corrected from V26 to actual V25 tree responses; this was a label correction only.
The15 boundaries preserve conditional resource semantics, literal object names,
optional-data retention,33/189/2/187 prospective accounting and no whole-R1 claim.
FORMAL_REVIEW and canonical RESULT separately record final proof and integrated outcomes.
