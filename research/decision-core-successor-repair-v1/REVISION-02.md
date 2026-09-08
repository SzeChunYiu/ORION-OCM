# Iterator/STOP correction receipt — revision 02

The independent review identified destructive membership testing against a
one-shot good-action iterator in decision_regions. The old candidate produced
empty a and b regions for one state accepting only b. The tuple control remained
correct. The original witness is owned by the reviewer:
`independent-review/FOCUSED-WITNESS-01.json`, SHA256
`06826d3e524b52501ed8c4abef2443aaf82314f9a9e87d6469590c7968ea5405`.

## Correction

The function snapshots each state's good-action iterable as a frozenset once,
then tests candidate actions against that snapshot. The new regression checks
the tuple and iterator cases, expected region membership, and agreement with
common_actions/contained_decision_actions using fresh equivalent inputs.

The helper docstring and MATH-ERRATUM now state that supplied action contracts
do not automatically cover finite_meta_dp's separate Stop(s). Combined use
requires block-preserved stop outputs and costs, or an explicitly modeled and
checked STOP contract. This is needed for the block-constant V_0 induction base.

## Qualification and custody

- Before changing the helper, the new iterator case failed and the tuple control
  passed: [RED-02.json](RED-02.json), [log](RED-02.txt).
- After correction, the new equivalence regression and the original common-action
  containment control passed. The final focused run checked exactly these two.
- [FOCUSED-03.json](FOCUSED-03.json) records child PID 1942545, actual cwd and
  imported decision_core.__file__, plus source/test hashes before and after.
- No other test suite, study, learner, native verifier, or protected corpus ran.
  The settled prior suite was not rerun for this narrow revision.
- Current patch applicability was checked read-only against the bound original
  source; [PATCH-CHECK-02.json](PATCH-CHECK-02.json) records the patch hash.

[HISTORY-01.json](HISTORY-01.json) binds the exact prior candidate and receipts
preserved under history/01-before-good-action-iterator. The original qualification,
patches, logs and SHA256SUMS are retained unchanged. Current records distinguish
that historical 16+10 qualification from this revision's focused two controls.

Only owned capsule files were modified. ROOT-LIVE-SOURCE-MATCH-01.json and
independent-review/ were left untouched. The current manifest deliberately
excludes those independently owned records. Independent reviewer closure follows
this freeze and is separate from the implementation receipt.
