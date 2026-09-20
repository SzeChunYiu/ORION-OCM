# Independent V9 governance review

Verdict: **CLEAR at the original eight R0 governance requirements** after the
authority-metadata repairs below. This does not certify mathematical truth,
literature saturation, or the scientific descendants of R0.

## Reproduced findings and resolutions

The review read the actual original FREEZE_V1.md, all historical registry
artifacts, the successor auditor/constants/tests and its adjudication.
The genuine historical bundle passed before and after the repair.

Before repair, semantic validate() accepted all of the following isolated
changes to the real bundle:

- T-TWO-FACTOR evidence replaced by an empty string.
- The same evidence replaced by "FULL_GMI proven by authoritative source".
- P10 source_type replaced by "PEER_REVIEWED_THEOREM".
- An extra theorem-registry scientific_truth_certified=true field.

These were semantic-validation gaps, not end-to-end audit bypasses:
evaluate() already rejected the changed bytes through historical custody.
The author added r0_schema_v9.py, enforcing exact object keys and field types,
the three original theorem evidence strings, the four original source types,
and the original atomic-registry doctrine. The review then repeated these
cases and broader missing/changed-field variants against semantic validate()
alone; all were rejected before hashes could be consulted.

The freeze prose checks are selected explicit markers plus exact trusted
custody, not a natural-language contradiction detector. Appending a contrary
claim while retaining those markers can pass the marker predicates, but
fails the full audit's byte binding. The review does not describe the marker
check as independently proving the meaning of arbitrary replacement prose.

## Independent runnable reconstruction

[test_independent_review_v9.py](test_independent_review_v9.py) contains four
unittest tests and exports COVERAGE for the combined V9 driver. It imports
the subject auditor but constructs its own mutations from actual input;
it does not import the author's mutation list or expected verdict helpers.

Measured in both normal and optimized Python3.12:

| Check | Outcome |
|---|---|
| Genuine semantic baseline and reordered control | 2 passed |
| ID, schema/source_issue alias and DAG self-cycle mutations | 255 rejected |
| Changed/missing authority metadata and extra truth flag | 18 rejected |
| Historical introduction blobs versus live bytes and pinned digest | 8 matched |
| unittest cases | 4 passed, zero errors/failures |

The 255-mutation sweep changes each of 205 atom IDs, each of 13 parent IDs,
each of nine theorem IDs, each of 17 DAG nodes to a self-cycle, and 11
schema/source_issue fields to a Boolean. The ID replacements preserve counts.
The 18 metadata mutants cover three theorem evidence fields with two
replacements plus deletion each, four source_type fields with replacement
plus deletion each, and one injected authority field.

During both semantic mutation suites and the positive controls, sha256 is
patched to raise if called. An unexpected exception explicitly fails the
test; only the auditor's checked-invalid exception counts as a rejection.
The separate introduction test uses /usr/bin/git show to read each pinned
introduction blob, compares exact bytes with the current original file, and
then checks its declared digest. All eight actual introduction blobs match.
Missing-source/unavailable-Git versus invalid-data handling was also reviewed
in the author's dedicated CLI tests; no additional discrepancy was found.

## Requirement-level conclusion and boundaries

The eight original requirements concern freezing and delivering a constitution,
a candidate hypothesis, atomic/theorem/parent registries, a dependency DAG,
merge rules, and an invariant checker. The successor now supplies independent
validation while preserving the original 205 initial registry rows and
seventeen-round scope. It may record those eight governance judgments in a
successor snapshot. The other 214 current programme requirements receive no
automatic status promotion. The candidate fixed point stays CONJECTURE.

Source identifiers and registered ownership are audited as frozen records.
This is not a claim to have checked every theorem in every cited publication.
The merge policy's delivery is distinct from proving every future execution
will obey it. Custody relies on trusted constants and review of this auditor;
rewriting verifier and anchors together is outside this trust boundary.

Reproduce on the laptop, from the repository root:

```sh
/home/billy/.local/bin/python3.12 -I -B research/gmi-1068-r0-foundation-repair-v9/test_independent_review_v9.py
/home/billy/.local/bin/python3.12 -O -I -B research/gmi-1068-r0-foundation-repair-v9/test_independent_review_v9.py
```

This review found no remaining defect within that audited governance scope.
The combined driver, custody snapshot and exact-head CI still govern merge.
