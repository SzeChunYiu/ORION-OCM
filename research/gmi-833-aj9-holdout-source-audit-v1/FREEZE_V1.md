# FREEZE — `gmi-833-aj9-holdout-source-audit-v1`

Committed **before** any auditor, oracle, test, receipt or workflow file of this package.

## Custody

| field | value |
|---|---|
| `source_main` | `5e57d4292266bccf435136e1f7d72caa32e920a0` |
| issue | `SzeChunYiu/ORION-OCM#833` |
| section | AJ9 (one row) |
| comment | `5693954852` |
| claim ceiling | `AJ9_HOLDOUT_BLIND_SOURCE_AUDITED_AGAINST_THE_FROZEN_FORBIDDEN_INPUT_LIST` |

## The exact row this tranche may reconcile

Byte-exact from comment `5693954852` at `source_main`, under the anchor
`### AJ9 — Blind derivation of all registered known MI families — OPEN`:

```
- [ ] Remove architecture names, semantic macros, family-specific operators/cost bonuses and evaluator leakage for every holdout.
```

**No neighboring row is earned here.** AJ9's five already-checked rows are untouched, as is
every AJ10–AJ16 row and every AG, AH and AF row.

## What is frozen

### 1. The audit taxonomy is the parent's, not this tranche's

The eight forbidden classes are taken verbatim from `forbidden_generator_inputs` in the merged
`gmi-833-aj9a-known-family-benchmark-v1/HOLDOUT_CONTRACT_V1.json`. They are not re-worded here:

benchmark contents · `family_id` or `paper_name` · post-hoc fingerprint clauses ·
family-specific target property vector · family-specific macro or operator ·
family-specific cost bonus or penalty · taxonomy label supplied to the evaluator ·
post-outcome family classifier feedback into search.

### 2. The forbidden vocabulary is derived, not authored

Every search pattern is extracted programmatically from the frozen
`KNOWN_FAMILY_BENCHMARK_V1.json`, pinned by its git blob
`6b9ac3095c90d74e2717671a70ad7cc18955310c`: the eleven family identifiers, the eleven paper
names and their word tokens, every `posthoc_fingerprint` clause, every
`exclusions_near_neighbors` entry, every `minimum_observation_tests` entry and every
`parent_anchors` entry. If the registry changes, the vocabulary changes with it and the audit
must be re-run.

### 3. What is audited, and what is not

**Blind artifacts**, which must be free of all eight classes: any file whose name begins with
`blind_`, plus `SEARCH_CONFIG_V1.json` and `BLIND_OUTCOME_V1.json`, in each of the seven
holdout packages `aj9b` … `aj9h`.

**Post-hoc artifacts**, which are permitted to name families: `posthoc_adjudicate_v1.py`,
`POSTHOC_RESULT_V1.json`, `check_aj9*.py`, and all prose. They are scanned only to confirm the
auditor can see family vocabulary where it is allowed to be — that is the control that proves
the scan works, so an empty blind result cannot be read as a broken scanner.

### 4. Declaration exemption, fixed before any run

A holdout's own statement of what it forbids is not leakage. A hit is exempt when it lies
inside a declaration field — a JSON value under a key named `forbidden`,
`hidden_from_generator`, `hidden_from_search`, `hidden_from_evaluator`, `no_family_score`,
`meaning_hidden_from_search`, or `benchmark_blob_required_after_generation_only` — or inside a
Python comment or docstring line that states a prohibition. Every exemption applied is listed
in the receipt with its file, line and text, so no exemption is silent.

### 5. Severity, fixed before any run

`VIOLATION` — a family identifier, a multi-word family name, a fingerprint clause, an exclusion
clause, an observation-test clause, a parent anchor, or a benchmark reference, outside a
declaration.
`REVIEW` — a single generic word that also occurs in ordinary technical prose. Reported with
file and line, never gated on, and every one is listed so it can be read.

A false positive is worse than a miss here: an auditor that cries wolf on its first real run
gets switched off. The receipt therefore publishes both counts and the full `REVIEW` list.

### 6. The gates

`GREEN` requires: zero `VIOLATION` hits across all blind artifacts of all seven holdouts; the
control scan finding family vocabulary in the post-hoc artifacts, so the scanner is proven to
work; every planted positive detected, one per forbidden class; the no-alarm case asserted on
the unmodified sources; and route A and route B agreeing on every published count.

### 7. Falsifiers

- One `VIOLATION` in any blind artifact means the row is not earned, and the receipt names the
  file and line.
- If the control scan finds no family vocabulary in the post-hoc artifacts, the scanner is not
  working and no absence claim may be made from it.
- If any planted positive is missed, the auditor's recall is incomplete and the audit is void.
- If a blind artifact of some holdout is not scanned because its name does not match the rule,
  that is a coverage gap and must be published, not absorbed.

## Forbidden promotions

`ALL_HOLDOUTS_PROVEN_BLIND`, `BLIND_SEARCH_IS_UNBIASED`, `NO_LEAKAGE_OF_ANY_KIND`,
`RECOVERY_IS_CONFIRMED_BY_THIS_AUDIT`, `COMPLETE_GMI`. A lexical and structural audit of
registered artifacts is not a proof that no information reached a search by any route; it is a
check that the frozen forbidden list is respected in the registered sources.

## What is not claimed novel

Static source auditing, token scanning and holdout discipline are ordinary practice. The
forbidden list, the family registry and the blind-recovery results are owned by the merged AJ9
packages. The residual contribution is the audit itself: a derived vocabulary, an exemption
rule that is published rather than implicit, planted-positive recall for all eight classes, and
a control that proves the scan works before any absence is reported.
