# AJ9A-1 … AJ9A-3 — what the holdout blind-source audit establishes

Stated at the scope fixed in `FREEZE_V1.md`. Every number is reproduced by `RESULT_V1.json`
(route A), `ORACLE_RESULT_V1.json` (route B) and `TEST_RESULT_V1.json`.

---

## AJ9A-1 — No registered blind artifact carries any forbidden input

**Statement.** Across all seven holdout packages `aj9b` … `aj9h`, no blind artifact contains a
family identifier, a family name, a post-hoc fingerprint clause, an exclusion clause, an
observation-test clause, a parent anchor, or a reference to the frozen benchmark, outside a
declaration of what that holdout itself forbids.

**Quantifiers.** 21 blind artifacts — three per holdout: the `blind_*` source, its
`SEARCH_CONFIG_V1.json` and its `BLIND_OUTCOME_V1.json`. The search vocabulary is derived from
the frozen registry pinned at blob `6b9ac3095c90d74e2717671a70ad7cc18955310c`: 11 identifiers,
11 names, 27 name tokens, 35 fingerprint clauses, 33 exclusion clauses, 24 observation clauses
and 25 parent anchors.

**Result.** `violations = 0`, by both routes, on the same 21 files.

**What was found instead.** 28 distinct `(package, file, token)` triples matched a single
generic word — `search` in search-procedure identifiers, `local` in `local_options` and
`legal_local_transforms`, `synthesis` in `MINIMUM_DEPENDENCY_SYNTHESIS`, `program` in "bad
postfix program", `control` in `GENERIC_BOOLEAN_CONTROL_SEARCH_CONFIG_V1`. All 28 are listed in
the receipt and each was read. None is a family name. They are reported, never gated on.

10 further hits lie inside a holdout's own `forbidden` list or a `hidden_from_*` /
`benchmark_blob_required_after_generation_only` field — a statement of what is prohibited, not
a use of it. Every exemption applied is listed with its file, line and text, so no exemption is
silent.

**Assumptions.** This is a lexical and structural audit of the registered artifacts. It cannot
see information that reached a search by a route that leaves no trace in those files.

**Falsifier.** One violation in one blind artifact voids the row, and the receipt names the
file and the line.

**Forbidden extrapolation.** `ALL_HOLDOUTS_PROVEN_BLIND`, `BLIND_SEARCH_IS_UNBIASED`,
`NO_LEAKAGE_OF_ANY_KIND`, `RECOVERY_IS_CONFIRMED_BY_THIS_AUDIT`.

**Dependencies.** The eight forbidden classes quoted from `forbidden_generator_inputs` in
`gmi-833-aj9a-known-family-benchmark-v1/HOLDOUT_CONTRACT_V1.json` and the vocabulary derived
from `KNOWN_FAMILY_BENCHMARK_V1.json`, both pinned by blob in `MANIFEST_V1.json`; the
blind-artifact rule, declaration exemption and severity levels of `FREEZE_V1.md` sections 3–5;
AJ9A-2, without which the zero would be an unvalidated empty output; `violations`,
`per_holdout` and `vocabulary` in `RESULT_V1.json`, with the review and exemption triples
matched by route B in `ORACLE_RESULT_V1.json`.

**Strongest parents.** `gmi-833-aj9a-known-family-benchmark-v1`, which owns the family
registry and the forbidden-input list the audit quotes; `gmi-833-aj10-prospective-unknown-v1`,
whose `blind_source_forbidden_hits` field established the shape of a source audit that this
package generalizes; the seven holdout packages `aj9b` … `aj9h`, which own the blind searches
(`PARENT_LEDGER.md`). Static source auditing is ordinary practice and is not claimed novel.

---

## AJ9A-2 — The auditor was validated before any absence was reported

**Statement.** The absence in AJ9A-1 is a searched absence, not an empty output.

**Result.** Two independent validations, both required before the audit's verdict is admitted.

*Recall.* One planted positive per forbidden class, eight in all — benchmark contents, family
identifier, paper name, fingerprint clause, target property vector, family-specific macro,
family-specific cost bonus, parent anchor. **8 of 8 detected**, by both routes.

*The scan demonstrably works.* Running the same scanner over the post-hoc artifacts, where
family vocabulary is permitted, returns 237 hits across 20 files. A scanner that found nothing
there would have been broken, and its silence on the blind artifacts would have meant nothing.

**A defect this validation caught.** The first implementation used `\b` word boundaries.
Because `_` is a word character, `def attention_macro(x)` did not match `\battention\b` and the
family-specific-macro plant went undetected — 7 of 8, published `RED`. Alphabetic boundaries
fixed it. The hostile `boundary_regex_word_only` now keeps that defect from returning: it
asserts 0 hits under the word boundary, 1 under the alphabetic boundary, and a live detection
by the auditor.

**Forbidden extrapolation.** That recall on eight planted classes is recall on every possible
leak. It is not.

**Assumptions.** Recall is measured with one planted positive per forbidden class, eight in
all, and sensitivity with the 20 post-hoc artifacts of `FREEZE_V1.md` section 3, where family
vocabulary is permitted. The validation covers those planted shapes and those control files
only, as the forbidden extrapolation states.

**Dependencies.** The derived vocabulary and forbidden-class list of AJ9A-1; the recall and
control gates of `FREEZE_V1.md` section 6; `planted_positive_recall` and
`planted_positives_detected` (8 of 8 in both routes) and `control_family_hits_in_posthoc` in
`RESULT_V1.json`; the `plant_*` hostiles, `boundary_regex_word_only` and
`posthoc_treated_as_blind` in `TEST_RESULT_V1.json`.

**Falsifiers.** Registered in `FREEZE_V1.md` section 7: a missed planted positive voids the
audit, and a control scan that finds no family vocabulary in the post-hoc artifacts means no
absence claim may be made. The word-boundary defect above is the observed instance (7 of 8,
published `RED`), and `boundary_regex_word_only` fails if it returns.

**Strongest parents.** The standard verification practice of proving a checker's recall on
planted positives and its sensitivity on known-positive data before reporting an absence,
which `PARENT_LEDGER.md` states is not claimed novel; `gmi-833-aj9a-known-family-benchmark-v1`
for the classes that are planted. No external parent is registered in `MANIFEST_V1.json`.

---

## AJ9A-3 — One custody gap, published rather than absorbed

**Statement.** `gmi-833-aj9g-k06-blind-recovery-v1` has no `FREEZE_V1.md`.

**Result.** `coverage_gaps` carries exactly one entry, agreed by both routes. Every other
holdout carries a freeze, a `blind_*` source, a search config, a blind outcome and at least two
post-hoc artifacts. `aj9g` also has no `posthoc_adjudicate_v1.py`, its adjudication being
folded into `check_aj9g.py`, which is why its post-hoc control count is 9 rather than the 31–52
of its siblings.

**Reading.** This does not change AJ9A-1: `aj9g`'s three blind artifacts were scanned and are
clean. It is a custody gap in a merged package, and it belongs in the open register rather than
in a footnote.

**Falsifier.** A `FREEZE_V1.md` appearing in that package removes the gap and the audit will
say so on its next run.

**Assumptions.** Custody is read from the file names present in each holdout's package
directory at the audited checkout, against the audit's four checks: a matched blind artifact,
a `blind_*` source, a `FREEZE_V1.md` and a post-hoc artifact. The gap is the absence of that
one file; this tranche neither re-runs nor re-judges the holdout (`PARENT_LEDGER.md`).

**Dependencies.** The coverage-gap falsifier of `FREEZE_V1.md` section 7 and the file rules of
section 3; AJ9A-1, whose clean scan of `aj9g`'s three blind artifacts is unaffected;
`coverage_gaps` and `per_holdout` in `RESULT_V1.json`, agreed by route B in
`ORACLE_RESULT_V1.json`.

**Strongest parents.** `gmi-833-aj9g-k06-blind-recovery-v1` itself, which owns its search,
outcome and recovery verdict, and `gmi-833-aj9a-known-family-benchmark-v1`, whose contract the
holdouts follow; none registered beyond `PARENT_LEDGER.md`. The finding is about custody, not
a new result about the holdout.
