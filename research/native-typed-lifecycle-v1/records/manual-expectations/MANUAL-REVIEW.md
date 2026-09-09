# Independent review of manual trace expectations

Confirmed as conditional, by-hand source reasoning. No correction is required to
TYPED-LIFECYCLE-MANUAL-EXPECTATIONS.md at SHA256
aa5187161d4bb30d5c40cc27eb2b06014fe1fcd6f27c405f375082dc70ee03a8.
This note is not a candidate selector or runtime acceptance filter.

The unchanged uncompressed recipes have20 and25 label positions. Under the declared
one-node-per-token trace semantics, training-0 has semantic roots14,15,18,19 and
syntax root3; training-1 has semantic roots17,18,21,22,24 and syntax root6.
These positions agree with the supplied ordinary contract result types. Native
acceptance and the adapter's actual source-bound trace remain prerequisites.

The extractor inspects semantic nodes except the final source root. Inner syl and
simpr each reach one semantic application and therefore fail the declared minimum.
The proper surviving roots are15 in training-0 and18/22 in training-1:

| Occurrence | Reached original nodes | Semantic nodes | Body nodes |
|---|---|---:|---:|
| training-0 root15 |5 through15 inclusive |2 |7 |
| training-1 root18 |8 through18 inclusive |2 |7 |
| training-1 root22 |3 through22 inclusive |4 |10 |

For each two-application occurrence, sorted traversal first emits three floating
leaves, H0, then H1, followed by syl and jca. Repeated float leaves share the same
canonical kind/output key. Repeated H0 shares its canonical hole slot/output key.
The extractor does not merge distinct application nodes. Native source labels are
absent from hole bodies and floating labels are absent from float bodies, so both
occurrences have the same typed body after rebasing and canonicalization.

The larger body inserts wa before the essential leaves and retains syl, jca, simpr
and outer syl: three floats, two holes and five application nodes. It is proper
only in training-1. Its matching full-source root is excluded in training-0.
Ordered premises establish V0,V1,V2 in the stated order for both body shapes.

Leaf sharing does not shorten the emitted normal proof automatically: emission
recurses on every ordered input occurrence. Thus the common body expands to11
labels and the larger body to20. The counts are distinct from unique DAG nodes.

Two occurrences versus one does not itself establish the registered joint-meaning
support result. The larger boundary has the exposed direct syl alias, while this
review predicts no full-catalogue alias disposition for the common body. Actual
bridge results, all candidate rows and every matching/refusal outcome must be retained.

No fixture builder, constructor, extractor, emitter, alias matcher, native verifier,
bridge or learner was executed. Source files were read only. The source binding uses
the live merged GitHub tree119e35b2 == the previously reviewed935ce5e tree; both are
bbd413419638cf98984fbcbd7430b61987375b8b. A failed direct local merged-object path
read is preserved in MANUAL-SOURCE-BINDING.json rather than treated as source absence.
No change to the fixture packet, root note or lead implementation was made.
