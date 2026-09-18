# SUPPLEMENT 1 — the baseline substitution was wrong; corrected

`FREEZE_V1.md` §3 records that
`research/gmi-833-theory-baseline-v1/BASELINE_V1.md` does not exist at this
package's pinned `source_main`, and substitutes
`research/gmi-833-foundation-v1/FOUNDATION_THEOREMS_V1.md` §§1, 2, 9, 10, 11 as
the governing baseline. **That absence claim is false.** The freeze is not
edited in place; this supplement is the correction.

## What was checked, and how

The file exists at this package's own pinned
`source_main` `c70dd24eeade46a3afe8322c1a0e0c16a648311e`, 12,351 bytes, and on
`main`. Verified two independent ways, per the rule that an absence claim needs
a search whose scope is justified rather than a search that merely returned
nothing:

| check | result |
| --- | --- |
| `git ls-tree -r --name-only <source_main> -- research/gmi-833-theory-baseline-v1/BASELINE_V1.md` | returns the path |
| `git show <source_main>:research/gmi-833-theory-baseline-v1/BASELINE_V1.md` | returns 12,351 bytes of content |
| repository-wide basename search for `BASELINE_V1.md` on `main` | exactly one path — this one |
| directory listing of `research/gmi-833-theory-baseline-v1/` on `main` | 19 files, including `BASELINE_V1.md` |

The baseline at that pin carries assertions A1–A14 with per-assertion evidence
paths, the claim ceiling and an explicit statement of what the baseline does
**not** assert, CI-U at re-earned strength, the OPEN-OBLIGATIONS register,
freeze governance, and the component inventory.

## What the correction changes

`MANIFEST_V1.json.missing_reference` now records
`CORRECTED__EXISTS_AT_SOURCE_MAIN`, names
`research/gmi-833-theory-baseline-v1/BASELINE_V1.md` as the governing baseline,
and retains the foundation sections as **supplementary** rather than as a
substitute. `BASELINE_ABSENCE_CLAIMED_WITHOUT_SCOPE_JUSTIFIED_SEARCH` is added
to the package's forbidden promotions.

## What it does not change

**No KP result moves.** The substituted foundation sections were used for the
realization-contract objects `(M, E, R, H, D, U)`, which the baseline does not
redefine — the baseline asserts corpus-level facts and governance, not the
contract. Every theorem, census count, gate and receipt field is unaffected,
and `RESULT_V1.json` is untouched by this supplement.

The residual exposure is therefore a **provenance defect, not a scientific
one**: a later auditor reading the manifest would have been told the programme's
frozen baseline did not exist, and would have had to re-derive the governing
authority. That is now corrected at the source.
