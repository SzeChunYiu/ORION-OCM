# GMI developmental uncertainty transport V1

Child issue: #748. Parent ledger: #602 Section M.

This capsule proves and exactly checks a registered-scope rule for transporting set-valued uncertainty across developmental updates. The central rule is deliberately fail-closed:

- preregistered transition relation: propagate the source confidence set by exact relational image and add only the registered relation-failure budget;
- missing transition relation: return the full registered target domain and abstain unless the downstream query is constant over that domain;
- never copy raw observations, visits, tokens, sums, or origins into a new developmental version.

Artifacts:

- `FREEZE_V1.md` — pre-implementation authority committed before scored code/results;
- `FORMALIZATION_V1.md` — DT-1..DT-6 proofs, quantifiers, counterexamples, and claim ceiling;
- `developmental_uncertainty_transport_v1.py` — exact finite/rational executor and deterministic receipt generator;
- `test_developmental_uncertainty_transport_v1.py` — main exact/adversarial suite;
- `dependence_certificate_v1.py` / `DEPENDENCE_CERTIFICATE_V1.json` — explicit 200-atom certificate showing the union bound is tight while success events are not independent;
- `test_dependence_certificate_v1.py` — certificate reproduction and hostile checks;
- `RESULT_V1.json` — deterministic registered result receipt.

Claim ceiling:

`SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE`

This does not establish G7 developmental prediction, learn a real transition law, prove sample freshness, or close capability/morphology calibration.
