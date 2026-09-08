# Correction and retained qualification

[The current closure](review/current/CLOSURE-02.json) accepts successor-02-metadata. [The original blocker](review/original/REVIEW.json) remains explicit. An earlier unissued acceptance candidate is retained in RAW under cache-source/independent-source-review-01/history; it was superseded before the blocker receipt and is not acceptance authority.

| Generation | Authored controls | PID | File pins / module entries |
|---|---:|---:|---|
| Original prototype, defective UNKNOWN branch | 12 passed | 2329276 | 799 / 126 |
| Metadata repair | 3 passed | 2359629 | 799 / 124 |

The original 12 controls did not cover mutation of returned UNKNOWN metadata. Their pass is not evidence that the defect was absent. The affected run explicitly reproduces the old source's false complete-nonmembership transition, then checks that the repair preserves repeated UNKNOWN, zero entries/two misses and detached deadline-refusal metadata.

The independent reviewer reconciled actual child/parent/cwd/Python/module identities and pre/post/current pins. All original bytes remain unchanged; the repair modifies one production line and preserves the nine other sources. [Original receipt](records/original/QUALIFICATION.json) · [repair receipt](records/current/QUALIFICATION.json) · [affected observations](records/current/qualification-01/CONTROLS.json)

The original suite was not replayed for this repair. These are authored source controls, not retained-proposal screening, native admission or performance experiments. Earlier source assertions and pre-repair cost wording remain historical; the current closure and successor README identify their correction. No source qualification creates an execution gate.
