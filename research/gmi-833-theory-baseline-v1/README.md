# GMI_THEORY_BASELINE_V1

Capstone freeze of ORION-OCM/GMI #833 Section B (line 59): binds the audited
theory corpus — census → audit-close → depgraph v2 → maturity rescores →
claim discipline → corpus passes v2 → terminology migration → blind-recovery
v2 → grammar growth → progress ledger — into one tamper-evident baseline.

- `BASELINE_V1.md` — the baseline: assertions A1–A14 at pinned scope, claim
  ceiling, forbidden promotions, CI-U at re-earned full strength, and the
  OPEN-OBLIGATIONS register (6 open revival tickets, aj-lane residuals, L48
  screen refinement, blind-recovery gaps, U-NEW arrival rule).
- `BASELINE_MANIFEST_V1.json` — machine binding: pinned HEAD SHA
  `c4def870df287a476672e47219134832a0c2f380`; 132 artifacts across 11
  component packages, each {path, sha256, bytes, role}; assertion→artifact
  dependency map A1–A14; revival-ticket register snapshot; arrival-absorption
  rule (0 arrivals at bind).
- `tests/test_theory_baseline_v1.py` (repo `tests/`) — re-derives every hash
  from the live tree, re-derives headline counts from the bound JSONs, and
  fails on any drift or unregistered tracked file in a frozen package.
- `build_manifest_v1.py` — deterministic manifest builder (stdlib-only,
  byte-identical under `-I -B` / `-I -O -B`); asserts every headline count
  against the live artifacts before writing.

Post-freeze rule: no in-place edits to bound artifacts; changes land as
`SUPPLEMENT_<n>_<slug>.md` plus `BASELINE_MANIFEST_V<n>.json` when the
binding changes (BASELINE_V1.md §5).
