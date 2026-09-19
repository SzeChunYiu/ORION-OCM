# GMI #833 — Known-family derivation tranche: symbolic logic, state-space, retrieval-augmented (K05 / SSM / K08)

Builds on the blind-recovery protocol v2 (`research/gmi-833-blind-recovery-v2-v1/`):
coverage-complete neutral batteries, tier-declared primitive bases, prior-disclosure
manifest, bijective clause-mapping adjudicator, A2 semantic screen. This package
runs the derivation tranche for three #833 census families that the prior lanes did
NOT cover (theirs: threshold logic, shift registers, local rules, selectors, neural):

- **S — symbolic logic systems** (census row "Symbolic logic systems"; K05
  symbolic/rewrite/search fingerprint, posthoc-only).
- **M — state-space models** (census row "State-space models"; linear-recurrence
  machine morphology — distinct from the shift-register treatment of K02).
- **R — retrieval-augmented systems** (census row "Retrieval-augmented systems";
  K08 retrieval/memory fingerprint, posthoc-only).

Per family: (1) formalism — machine space in the registered G0-style substrate,
semantic equivalence class, morphology descriptor (no architecture names in the
search-visible surface); (2) derivation — family-neutral coverage-complete battery +
tier-declared basis per the v2 prior-disclosure standard, blindness argued per
channel, recovery run + honest boundary; (3) empirical bar — 200-seed nulls, error
bars, designed negative controls, zero arbitrary constants (every threshold
derived/ablated), sha256-pinned receipts; (4) claim-discipline fields for every new
claim (235-object corpus standard).

STATUS: outcomes frozen on the compute host (billy-laptop), adjudicated
posthoc; see BLIND_OUTCOME_V1_T1/T2/T3.json, REMINT_OUTCOME_V1.json,
POSTHOC_RESULT_V1.json, CLAIMS_V1.json, RESULT_V1.json (checker).

## Reproduce

- battery regeneration (byte-deterministic):
  `python3 -B battery_generate_v1.py`
- search + certificates + nulls (compute host, numpy):
  `python3 -B run_tranches_v1.py t2|t3|t1` then
  `python3 -B run_remint_v1.py`
- CI side (stdlib only): `python3 -B screen_v1.py &&
  python3 -B posthoc_adjudicate_v1.py && python3 -B check_v1.py`

## Custody

Freeze commit 98bd9369 (prior disclosure + basis + batteries + generator +
parent ledger; no implementation). Implementation landed only after the
freeze; outcomes only after implementation; the adjudicator reads the frozen
benchmark only after outcomes. Battery sha256 pinned in check_v1.py.
