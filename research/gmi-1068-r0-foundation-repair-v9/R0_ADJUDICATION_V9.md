# Original R0: independent governance adjudication

Scope: original GMI2-R0-001 through GMI2-R0-008 only. These are governance
requirements, not mathematical propositions about intelligence. V9 can earn
these eight delivery/validation requirements without earning their scientific
descendants. The fixed point remains a conjecture; full closure remains OPEN.

## What is actually checked

The source is `research/gmi-1068-grand-unified-v2-r0/`, containing its freeze
and seven delivered artifacts. Historical files and initial statuses are
unchanged. The independent successor reads those actual files; synthetic
fixtures cannot substitute for the real baseline.

`r0_audit_v9.validate(bundle)` validates semantic fields without comparing
file digests. `read_bundle(repository)` returns parsed input and raw bytes.
`evaluate(repository)` additionally checks immutable content and Git custody.
Constants contain independently specified per-record fields, vocabularies,
canonical dependencies and fixed ancestry/content anchors; checks traverse
records and relations instead of comparing a serialized registry wholesale.
Closed key schemas and exact field types reject undeclared authority fields.
The three optional theorem evidence strings and four parent source_type
labels are pinned on exactly their registered rows; omitted or inflated
labels fail. The registered doctrine is also preserved.
Order is immaterial for semantic rows, nodes, dependencies and vocabularies.
Historical byte order remains material for custody. Free text in the freeze
and historical checker is fully protected by custody bindings. Selected
freeze-token checks do not constitute a general natural-language verifier.

The semantic audit enforces all original 205 IDs, per-round identities and
counts, titles, owners, registered evidence kinds, NOT_STARTED states and
literal false closes_by_prose. The counts for R0 through R16 are respectively
8, 10, 9, 10, 10, 10, 15, 13, 14, 9, 10, 13, 17, 11, 14, 18, 14.
It checks all 17 nodes, every canonical dependency, acyclicity, unknown and
duplicate edges; all 13 source/ownership/lane records; all nine theorem
records and seven-status vocabulary; eight merge rules and four nonpositive
terminals; and the historical result's computed counts and authority ceiling.
The original theorem file has no source_issue field; the audit respects this
actual schema rather than inventing a required field.

## Evidence by original atom

| Original ID | Original requirement | Successor evidence |
|---|---|---|
| GMI2-R0-001 | freeze programme constitution | Original source ancestry, freeze-only tree, forbidden promotions and unchanged delivery verified. |
| GMI2-R0-002 | freeze candidate fixed point as hypothesis | Original freeze explicitly says working hypothesis and does not establish the fixed point; candidate registry status remains CONJECTURE. |
| GMI2-R0-003 | build atomic registry | All 205 exact original identities, titles, owners, evidence kinds and initial states checked. |
| GMI2-R0-004 | build theorem status registry | All nine original records, authority vocabulary and ownership checked; unsupported promotion rejected. |
| GMI2-R0-005 | build parent registry | All 13 original source anchors, titles, ownership roles and lanes checked; no novelty reassignment permitted. |
| GMI2-R0-006 | build dependency DAG | All 17 nodes and exact registered edges checked, including acyclicity and final parents. |
| GMI2-R0-007 | freeze merge gate | All eight original rules and four nonpositive outcomes checked. |
| GMI2-R0-008 | verify R0 registry invariants | Independent semantic and custody audits pass; real-data hostile controls exercise the former checker omissions. |

These judgments concern the registered artifacts, not the truth of cited
papers, universal sufficiency of a merge policy, or execution of every future
merge rule. A registry can correctly identify a conjecture without proving it.
Historical NOT_STARTED fields are not rewritten. The successor snapshot is
where these eight governance judgments are recorded. All 214 other original
requirement statuses must remain unchanged by this adjudication.

## Custody and reproducible receipts

Original source main: `74e7b889eab2e16a5fb1f7c8183bce2e5d179c82`.
Original freeze: `852b7665f86798c334bfd0eccafb5cfb0de463c5`.
Fixed H baseline: `67e42e93ce89aa5e3a1c94193bb925b8568dfc77`.
The source precedes the freeze. The freeze tree contains only FREEZE_V1.md
under the original package. Each outcome was added strictly after that
freeze; all eight introduction commits and SHA256 bindings are declared in
`constants_v9.py` and included in the successful receipt.

The audit requires the H baseline, original freeze and all introduction
commits to be ancestors of the current checkout; each bound introduction
must be a file addition. It verifies the current original bytes against the
pinned bindings. Current HEAD is used for ancestry checks but excluded from
the receipt, as are timestamps: committing or merging the successor does
not change successful receipt contents.

This is an audit against trusted frozen anchors, not an authenticity system
for an attacker allowed to rewrite both the audit and its trust anchors.
The successor's own review and content bindings remain necessary.

## Falsification and attribution

The tests execute the original check_r0.py **complete main**, with its load
function reading isolated mutations of the actual baseline. Both the valid
baseline and each of these four defects return success in that old checker:

- atomic status changed to ABSOLUTE_TRUTH;
- atomic evidence kind changed to INVALID_EVIDENCE;
- parent ownership role changed to GMI_NOVELTY;
- candidate fixed point promoted from CONJECTURE to PROVED.

The successor rejects all four via semantic predicates, before custody
hashes are consulted. The defect belongs to missing semantic validation in
the historical checker, not absent original source artifacts. Row deletion
is not claimed as a complete-main bypass: the old result-count comparison
can catch it even though the old validate function alone misses it.

Additional independent mutations cover lost rows/owners, duplicate IDs,
wrong rounds/titles, Boolean/int aliases, evidence reassignment, DAG cycles,
unknown/duplicate/lost edges, lost final parents, invalid or changed parent
sources/roles/lanes, theorem vocabularies, merge rules and authority metadata.
The independent review additionally found missing semantic checks on optional
evidence/source-type fields and undeclared keys; closed schemas and pinned
optional fields now reject those actual mutations. Custody already rejected
their changed bytes; these were semantic-layer gaps, not whole-audit bypasses.
A reordered semantic control passes. A byte-only change passes semantics
but fails custody. Wrong ancestry fails custody. Missing inputs, unreadable
inputs and unavailable repository evidence are distinguished from invalid
JSON or a violated invariant.

Run on the laptop using Python 3.12, normally and with optimization:

```sh
python3.12 -I -B research/gmi-1068-r0-foundation-repair-v9/test_r0_audit_v9.py
python3.12 -O -I -B research/gmi-1068-r0-foundation-repair-v9/test_r0_audit_v9.py
python3.12 -I -B research/gmi-1068-r0-foundation-repair-v9/r0_audit_v9.py
```

Standalone exit codes: 0 verified; 1 read and invalid; 2 CANNOT_CHECK.
No assert statement implements an audit gate, so optimization cannot disable
validation. The independent tests and combined V9 receipt are the executable
witnesses; this document alone closes nothing.
