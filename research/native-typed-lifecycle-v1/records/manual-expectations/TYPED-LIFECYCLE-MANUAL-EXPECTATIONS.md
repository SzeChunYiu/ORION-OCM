# Independent manual expectations for the authored lifecycle

Prospective source reasoning, 8 September 2026. No native checker, learner, registered
bridge, alias matcher or corpus execution performed. This note is an audit aid only;
it must not become a candidate selector, fixture field or runtime acceptance filter.
The implementation must retain its generic enumeration and every actual outcome.

Inputs: the unchanged FIXTURES.json and ASSERTIONS.json from the independently
reviewed native-typed-wff-fixtures-v1 packet; published typed_extract.py and
typed_constructor.py at main119e35b2b527a78c5862844f0e40cca7dd3b0d62.
This reasoning assumes native acceptance and the declared uncompressed proof-token
trace semantics. A native refusal remains a refusal and does not become acceptance
because the following hand calculation predicts a trace.

## Source traces

One node per ordinary proof token, zero-based IDs, no saved-reference events:

| Authored task | Expected nodes | Semantic applications, in source order | Syntax application |
|---|---:|---|---|
| training-0 | 20 | 14:syl, 15:jca, 18:simpr, 19:syl | 3:wa |
| training-1 | 25 | 17:syl, 18:jca, 21:simpr, 22:syl, 24:jaoi | 6:wa |

Both traces use ordered source premises H0:ph→ps and H1:ps→ch. The inner syl
derives ph→ch; jca combines H0 with that result to derive ph→(ps∧ch).
simpr derives (ps∧ch)→ch, so the outer syl derives ph→ch.
The second source then applies jaoi to that result and H1, deriving (ph∨ps)→ch.
The wa syntax constructor supplies the composite middle formula to outer syl.

## Generic proper fragments

The extractor examines semantic nodes except the full source root and keeps
fragments with 2–8 reached semantic applications and all three boundary parameters.
The inner syl and simpr each have one semantic application and fall below that
declared bound. No semantic application is hidden inside the one syntax node.

The hand prediction is therefore three occurrences, with two structural bodies:

| Source root | Reached source nodes | Reached semantic count | Canonical body nodes |
|---|---|---:|---:|
| training-0:15 | 5 through15 inclusive | 2 | 7 |
| training-1:18 | 8 through18 inclusive | 2 | 7 |
| training-1:22 | 3 through22 inclusive | 4 | 10 |

The first two occurrences have the same body: three floating leaves, two ordered
essential leaves, inner syl and jca. Repeated floating/H0 pushes are deduplicated
by the extractor; distinct semantic applications are not merged by that leaf rule.
Canonical parameters V0,V1,V2 follow first appearance in the ordered premises.
Its boundary is V0→V1, V1→V2 ⊢ V0→(V1∧V2). Its expanded proof uses11 labels.

The third occurrence has the same two premise slots and query V0→V2. Its body
has three floating leaves, two essential leaves, wa, inner syl, jca, simpr and
outer syl. Its expanded proof uses20 labels. This is a proper fragment only in
training-1; the same full proof is the excluded source root in training-0.

Thus the two-application body has two distinct source-task occurrences; the
four-application body has one. Source occurrence count is not the joint-meaning
support result. Only the unchanged registered bridge establishes the latter under
its declared canonicalization. The fixture packet's arithmetic note addresses
complete joint signatures, not any hypothetical validity-only signature.

No ordinary-catalogue alias result is predicted for the two-application body.
For the four-application boundary, the exposed ordinary syl contract already
provides the sequent. This does not bypass the actual catalogue matcher, and this
body's single source occurrence remains a separate support limitation.

## How to use a discrepancy

Compare the actual source-bound trace and complete occurrence table after the
fixed execution. First distinguish a hand-calculation mistake, trace-interface
difference, extraction defect and support/canonicalization difference. Preserve
the result and attribute any failure to its actual stage before a separate repair.
Never replace observed rows with this prediction, suppress unexpected candidates,
or edit the authored routes to obtain the predicted terminal.
