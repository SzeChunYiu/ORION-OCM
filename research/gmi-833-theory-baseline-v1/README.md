# GMI_THEORY_BASELINE_V1 (in progress — scaffold)

Capstone freeze of ORION-OCM/GMI #833 Section B: bind the audited theory corpus
(census -> depgraph v2 -> maturity rescores -> claim discipline -> corpus passes v2
-> terminology migration -> blind-recovery v2 -> grammar growth -> progress ledger)
into a single tamper-evident baseline.

Artifacts landing here:
- `BASELINE_V1.md` — human-readable baseline: assertions, scope, claim ceiling,
  forbidden promotions, OPEN-OBLIGATIONS register.
- `BASELINE_MANIFEST_V1.json` — machine-readable binding: pinned HEAD SHA,
  per-artifact {path, sha256, role}, interdependencies, revival-ticket register,
  arrival-absorption rule.
- `tests/test_theory_baseline_v1.py` (repo tests/) — re-derives every hash from
  live main and FAILS on drift.

Pinned HEAD at scaffold: c4def870df287a476672e47219134832a0c2f380 (to be confirmed at bind time).
