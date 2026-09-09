# HOLE-ESSENTIAL-SLOT-CONTROL-01
Cause: the initial source-generation insertion used a textual anchor absent from
the combined statement in test_03. The intended duplicate-slot case was never
inserted, while its documentation claimed that coverage. This was a control and
reporting defect; the independent review established no production-code defect.

Repair: a separate authored test explicitly inserts slot 1, preserves slot 0,
and supplies a target with two different proofs of the same essential statement.
The expected floating nodes are [7,8,9], essential nodes [15,23], and the expected
20-label replacement is written independently in the test. A swapped [23,15]
binding is rejected. Actual inputs, full match/emission/refusal outputs and work
counts are retained, along with source/runtime identities and process costs.

The original eight-control receipt continues to report what actually ran. Its
old standalone qualification statement is superseded by this correction only;
no old source, receipt or summary byte was rewritten. Original before/after pins
agree. No runtime source changed and no other suite or native work was run.
