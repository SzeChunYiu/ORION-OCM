# Terminology substitution, disclosed

The repository's paper-facing terminology gate
(`research/gmi-833-ab-terminology-harness-v1`) bans two phrases that issue
#833's own requirement list uses to name requirements `R05` and `R09`. This
package's markdown originally carried those two phrases in four places, three
of them inside `FREEZE_V1.md`.

Each occurrence was replaced by the gate's own registered replacement:

- for `R05`, the gate's `matched negative control`;
- for `R09`, the gate's `independent regeneration`.

**Nothing else changed.** The substitution is vocabulary only: no scope, no
prediction, no budget, no falsifier, no applicability condition, no number.
The pre-substitution text of `FREEZE_V1.md` and `FREEZE_V1_ADDENDUM.md` is
preserved verbatim in commits `c7332460` and `3f0f64db`, both of which predate
every implementation artifact of this package, so the custody record is
unaffected and independently checkable with `git show`.

`RESULT_V1.json` and `ISSUE_833_RECONCILIATION_H3_V1.json` are unchanged by
this substitution: they carry requirement identifiers (`R05`, `R09`), not
requirement prose.
