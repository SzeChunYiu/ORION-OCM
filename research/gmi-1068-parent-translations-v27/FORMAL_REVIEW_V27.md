# V27 independent formal review

This reviewer wrote the paper derivations and parent ledgers, but did not write
the Lean sources, expected-type contract or checker. This is independent review
of those implementations and their correspondence to the paper, not a second
independent paper authorship claim. Production review is in REVIEW_V27.md.

## Observed fresh replay

Independently ran check_lean_v27.evaluate on billy-laptop with the pinned
/home/billy/.elan/bin/lean +leanprover/lean4:v4.19.0. The checker built every
source in a new temporary directory, then elaborated the fixed typed audit.
Observed PASS: 48 sources, 282 registrations, 39.165 seconds.
No exhaustive Python corpus was repeated for this review.

Independent receipt: /tmp/gmi-v27-independent-kernel.json.
Receipt SHA256: 8e339bad183f5feae830d87384071e84673849c5436fd96a772ec48287c208c7.
Generated audit SHA256: d13dea7dd694988fc6bdbdaeb7fbf9cde03b804c5d0dd8876d1688ab4dd9c357.
proof_contract_v27.py SHA256: ee5f1b6aaafcf876dadc7baa519cab25c7f719e0b78e5c9d21fd872104c9fe00.
check_lean_v27.py SHA256: 20dd0c3bcf81fc4857be1bae4b82d6ded697e354c39e3c4f08bb8f64874a7ca9.
FORMAL_SCOPE_V27.md SHA256: f92ced185741b4284d6d4428aee1f63208fa4d87dd1df0a6780065cd3ce5da98.
The receipt binds each actual source hash; it is not merely a compiler exit flag.

## Assumptions and registration review

Read all 19 new modules, the final static signatures, checker and 158-line scope.
The 29 immutable imports are rebuilt in the same isolated dependency order.
Exact expected signatures are supplied independently of runtime type discovery.
They bind both theorem conclusions and actual constructor/operation equations.
Constructor registrations for SetEndo, System, OrderedWeight, Event, Test and
Encoder expose their primitive premises; no category, matrix-composition bound,
path-lift or task-domain conclusion is smuggled into those primitive records.

The checker rejects source proof holes/axiom declarations/unsafe constructs,
then prints the axioms of each registered declaration and rejects sorryAx.
Standard classical logic and choice remain permitted logical assumptions;
this is not a constructive implementation or an effective-selection claim.
Missing compiler/source conditions remain CANNOT_CHECK, distinct from invalid
source or AUDIT failure. Source-valid weakening controls are the independent
root test module's responsibility; their canonical outcomes belong to RESULT.
A source hash alone would not replace those exact expected-type checks.

Also read root's actual /tmp/gmi-v27-root-mutants.log and guard implementation:
one test passed in 116.893 seconds, covering all-source-empty plus the three
full leaf statements weakened to True. The test requires AUDIT failure for
each of four cases, after all changed sources compile. This was root's run,
not a second execution by this reviewer; canonical integration remains separate.

## AA1 and AA2

The powerset image, relation decoder, Forward/Back predicates and graph relation
are actual definitions. Hom equivalence proves both inclusions of the square.
Graph generators retain labels; singleton recovery is relative to the supplied
label type. Python's endpoint graph still needs its declared LTS edge registry.
The path map uses actual V11 Path and preserves nil, cons, append and labels.
lift_path concludes equality of dependent endpoint/path bundles, not only a
word-label or terminal-state comparison. Forward is retained alongside Back.
No duplicate-edge multigraph, infinite lift, uniqueness or effective lift is proved.

SetEndo has only type/function operations and functor laws. The System category
is derived from commuting carrier maps. Faithful forgetting is homwise; actual
Bool-output singleton systems show its object collapse and failed-join revival.
The tagged target retains System objects and all carrier functions, so its
object-identity map earns V26 raw transport without an equivalence claim.
The general paper interpretation into any lawful category is wider than the
registered map_eval, which interprets into the actual target path category.

## AA3 and AA4

Arbitrary Rel uses existential composition; TotalRel inclusion is faithful
and has its stronger totality requirement. Empty input carriers are valid.
The Weight interface retains 1≠0, zero-sum-free addition and no zero divisors.
OrderedWeight adds a nonnegative monotone partial order and mul_comm.
Finite sums and matrix row bounds are derived from those laws.
Actual Event matrices form a category; normalized inclusion and both slice
roundtrips preserve coefficients. No normalization is inserted into Event comp.

Test.mk requires raw component matrices and normalized aggregate only.
The component Event bound is proved from that premise. Actual paired outcome
coefficients, nested-sum aggregate equation and normalization are registered.
Zero and equal-valued outcomes remain present; paired encoders retain IDs.
Empty-outcome impossibility uses inherited 1≠0 and an inhabited input.
The empty-input constructor supplies the complementary nonvacuous boundary.
There is no global strict category of arbitrarily reassociated labelled tests.

Basis observations recover every classical matrix entry and separate Events.
Closed scalar composition is multiplication. Nat supplies a genuine generic
interface instance, while fractional controls are exact Rat arithmetic only.
They are not a generic Event Rat/Test Rat model. The inherited concrete V14
rational matrix model, paper nonnegative Real/Rat interpretations and Python
Fraction calibration are explicitly different evidence levels.

## AA5 and parent boundaries

Canonical tasks use actual Dom/Ran subtypes and decode exactly. The regular
bridge is a label-preserving inclusion graph, and the resulting arrow retains
Dom R and declared Ran S. Actual range containment is not promoted to equality.
The five-label countermodel uses the specified relations and proves the failed
strong-associativity condition of inferred exact-image regularity. Declared
interfaces supply a different well-typed observer with retained unused outputs.

Possibility is supplied identity/composition closure through actual V26
restriction. The closed identity-only class and excluded swap with included
square separate composite possibility from factor possibility. The nonclosed
candidate and actual resource wrong-balance/same-path controls remain distinct.
No physical repeatability, bridge feasibility or resource law is inferred.
General monoidal reduct extraction and measurable/quantum parent interpretations
remain paper-level; the source does not pretend to construct those full theories.

## Verdict

No unresolved proof, assumption or registration mismatch was found.
THEOREM_LEDGER names actual final registered declarations and keeps paper-only
extensions explicit. Fresh kernel PASS supports exactly FORMAL_SCOPE; finite
correspondence, hostile controls and successor closure are separate gate records.
Only original R1-009 is eligible. This review does not promote whole R1 or GMI.
