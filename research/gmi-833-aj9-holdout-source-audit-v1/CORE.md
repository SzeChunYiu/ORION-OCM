# AJ9 — the holdout blind-source audit (START HERE)

AJ9's contract freezes eight forbidden generator inputs. Five AJ9 rows are checked; the one
that asks for those inputs to be *removed from every holdout* was not. This audits all seven
holdouts against that list — and validates the auditor before reporting any absence.

## Headline numbers

| quantity | value |
|---|---|
| holdouts audited | `7` (`aj9b` … `aj9h`) |
| blind artifacts scanned | `21` — the `blind_*` source, `SEARCH_CONFIG_V1.json` and `BLIND_OUTCOME_V1.json` of each |
| **violations** | **`0`** |
| generic-identifier hits, reported and each read | `28` distinct `(package, file, token)` triples |
| exemptions, all inside a holdout's own prohibition statement | `10`, each listed with file, line and text |
| control: family vocabulary found in the post-hoc artifacts, where it is allowed | `237` hits across `20` files |
| planted-positive recall, one per forbidden class | `8 / 8`, both routes |
| custody gaps found | `1` — `aj9g` has no `FREEZE_V1.md` |
| vocabulary derived from the frozen registry | 11 identifiers · 11 names · 27 name tokens · 35 fingerprint clauses · 33 exclusion clauses · 24 observation clauses · 25 parent anchors |

## Why the zero is trustworthy

An empty scan result means nothing on its own. Two things make this one a searched absence:

- the same scanner over the **post-hoc** artifacts, where family vocabulary is permitted,
  returns **237** hits — so it demonstrably sees family vocabulary when it is there;
- **8 of 8** planted positives are detected, one per forbidden class.

That validation earned its keep immediately. The first implementation used `\b` word
boundaries; because `_` is a word character, `def attention_macro(x)` did not match
`\battention\b`, the family-specific-macro plant went undetected, and the run published `RED`
at 7 of 8. Alphabetic boundaries fixed it, and the hostile `boundary_regex_word_only` keeps the
defect from returning.

## What the audit is not

A lexical and structural audit of registered artifacts cannot see information that reached a
search by a route leaving no trace in those files. `ALL_HOLDOUTS_PROVEN_BLIND`,
`BLIND_SEARCH_IS_UNBIASED`, `NO_LEAKAGE_OF_ANY_KIND` and
`RECOVERY_IS_CONFIRMED_BY_THIS_AUDIT` are all in the forbidden set.

## Evidence

- **2 materially independent routes.** Route A scans line by line with regular expressions and
  decides the exemption from line shape. Route B imports nothing from A: it tokenizes Python
  with the standard `tokenize` module so comments and strings are identified structurally, and
  walks parsed JSON as a tree so the exemption is decided by the key a value hangs under.
  The **28 review triples and the 10 exemption triples are identical**, violations are 0 on
  both, recall is 8/8 on both, and both find the same single custody gap.
- **13 hostiles, all detected, each with a clean control**: seven planted forbidden inputs, the
  word-boundary defect, an exemption rule widened to everything, a blind-file rule too narrow to
  reach the configs, a hand-written vocabulary instead of a derived one, post-hoc files treated
  as blind, and a drifted benchmark pin.
- **No-alarm asserted**: 0 violations, every review hit a generic token, every exemption inside
  a declaration field, and the control scan non-empty.

## Reproduce

```
python3 -I -B  research/gmi-833-aj9-holdout-source-audit-v1/aj9_holdout_source_audit_v1.py
python3 -I -B  research/gmi-833-aj9-holdout-source-audit-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-aj9-holdout-source-audit-v1/test_aj9_holdout_source_audit_v1.py
```

Under 2 s each. Stdlib only.

## Files

`FREEZE_V1.md` (committed before any code) · `AJ9_AUDIT_THEOREMS_V1.md` (`AJ9A-1` … `AJ9A-3`) ·
`PARENT_LEDGER.md` · `RESULT_V1.json` · `ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` ·
`MANIFEST_V1.json`.
