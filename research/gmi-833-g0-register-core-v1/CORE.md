# gmi-833-g0-register-core-v1

Small #868 / #833 Section-E derivation tranche.

`G0-reg-v1` is a five-instruction labelled register/control operational core:

```text
READ, INC, DECJZ, EMIT, HALT
```

Its “minimality” is explicitly relative to five frozen operational requirements, with one analytic necessity invariant and bounded hostile census per instruction class.

Exact evidence:

- 34/34 tests in normal and `python -O`;
- all 256 two-state binary Mealy machines × 15 words = 3,840 exact compiler comparisons;
- second independent interpreter: 3,840/3,840;
- 49/49 two-label deterministic counter-program identity checks;
- 392 bounded class-removal programs, zero invariant violations;
- exact resource trace recounts;
- composition, recurrence and static register storage controls;
- deterministic byte-identical receipts.

Claim ceiling: `GMI_G0_REGISTER_CORE_AND_FINITE_EMBEDDINGS_AT_DECLARED_SCOPE`.

The supplied register/control representation is a disclosed prior. No unbiased-search, unique-universal-grammar, neural/probabilistic derivation, grammar-remint invariance or morphology-selection result is claimed.
