# PARENT_LEDGER — blind-recovery protocol v2 (GMI #833 / #434)

## Parents absorbed (assimilation-first)

- `research/gmi-833-aj9a-known-family-benchmark-v1` (PR #931) — frozen
  benchmark + prospective no-smuggling contract. v2 keeps the frozen
  fingerprint clauses VERBATIM as the posthoc adjudication standard and
  closes the two channels that contract left open (task source, basis).
- `research/gmi-833-aj9b-k01-blind-recovery-v1` (PR #932) through
  `gmi-833-aj9g-k06-blind-recovery-v1` (PR #937) — the audited v1 series.
  v2 reproduces the OR-task counterfactual with the REAL v1 adjudicator
  (motivation receipt), generalizes it to the complete battery, and repairs
  the adjudicator defects (decorative clause counts; distinctness-as-reuse
  bug; hardcoded expected solutions/state encodings in #933/#934; missing
  K06 adjudicator).
- `research/gmi-833-no-smuggling-audit-v1` (#855) — the A2 semantic
  fingerprint standard: v2 is the first blind-recovery package to WIRE IT IN
  (screen_v2.py) rather than reimplementing a lexical denylist alone.
- Science-audit comments on PRs #931-#934 (the confirmed finding this
  package answers; see AUDIT_FINDING section of PRIOR_DISCLOSURE_V1.md).

## Transfer table

| v1 element | v2 status |
|---|---|
| XOR task (K01) | complete B_BOOL2 battery, all 16 functions |
| basis {ADD, NEG, POS} | tier grid: U_ORD primary (all cuts), U_ALL3 + U_V1 ablations |
| K03 requirement sentence (circular) | complete B_LOCAL class, all 256 rules, site-symmetric model never enforced |
| K02 transition-table basis (260 tables) | M_STATE expression basis, same frozen grid |
| lexical-only screen | lexical + #855 A2 semantic screen, controls both polarities |
| decorative clause count | bijective clause->check map + count assertion |
| distinctness-as-reuse check | skeleton-isomorphism reuse (parameters erased) |
| hardcoded expected solutions (#933/#934) | relabel-invariance self-test + literal scan |

## Deltas earned beyond parents

- Channel-closure manifest with per-channel blindness arguments
  (PRIOR_DISCLOSURE_V1.md), frozen before any search implementation.
- Recovery-boundary measurement: morphology distributions over complete
  neutral classes (separability boundary for K01; lag>=1 for K02;
  non-wiring for K03; selector class for K04) instead of single-task
  verdicts — the family-information content of task authorship, quantified.
- Structural observation: tree cost models underprice reuse-economy
  architectures (class-universal machine bound), recorded with its revival
  lever (counted-once DAG cost model) as the next iteration.
