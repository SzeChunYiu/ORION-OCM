# GMI developmental uncertainty transport V1

Child issue: #748. Parent ledger: #602 Section M.

The base theorem/proof capsule was merged by #749. This directory now also carries the post-merge hostile hardening that makes its no-relation path provenance-bound and makes the no-independence claim executable.

Core rule:

- preregistered transition relation: propagate the source confidence set by exact relational image and add only the registered relation-failure budget;
- missing transition relation: return the full registered target domain and abstain unless the downstream query is constant over that domain;
- never copy raw observations, visits, tokens, sums, or origins into a new developmental version.

Key artifacts:

- `FREEZE_V1.md` — pre-implementation authority;
- `FORMALIZATION_V1.md` — DT-1..DT-6 proofs, quantifiers, counterexamples, and claim ceiling;
- `developmental_uncertainty_transport_v1.py` — exact finite/rational executor;
- `test_developmental_uncertainty_transport_v1.py` — exact/adversarial suite;
- `dependence_certificate_v1.py` / `DEPENDENCE_CERTIFICATE_V1.json` — 200-atom witness where the union bound is tight although success events are not independent;
- `test_dependence_certificate_v1.py` — certificate reproduction/hostile checks;
- `AUDIT_V1.md` — post-merge hostile review and custody defect repair;
- `CLAIM_DISPOSITION.md` — exact #602 consequence and non-claims;
- `RESULT_V1.json` — unchanged deterministic registered result receipt.

Claim ceiling remains:

`SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE`
