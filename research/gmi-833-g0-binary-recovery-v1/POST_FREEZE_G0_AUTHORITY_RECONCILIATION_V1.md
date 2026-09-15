# Post-freeze reconciliation to merged G0-reg-v1 authority

The scientific target of this tranche was frozen at `302ad7fed43b0e310b6e22252ceb21260edd865b`, before the Section-E G0 register/control core was merged.

Concurrent #833 work subsequently merged PR #873 as main `367e14e9296cf79924ce56d89fad34b3769acb5d`, with claim ceiling:

`GMI_G0_REGISTER_CORE_AND_FINITE_EMBEDDINGS_AT_DECLARED_SCOPE`.

That result is now the current Section-E authority for the registered operational G0 core. It supplies a finite register/control language with `READ`, `INC`, `DECJZ`, `EMIT`, and `HALT`, exact small-step semantics, raw resource accounting, requirement-relative instruction-class irredundancy, and exact finite Mealy/counter embeddings. It explicitly retains a register/control representation prior and does not claim unique universal grammar, unbiased search, grammar-remint invariance, or independent morphology rediscovery.

## Relationship of this tranche to G0-reg-v1

This tranche is **not** a competing universal G0 proposal and does not supersede `G0-reg-v1`.

Its NAND-only and NOR-only languages are bounded Boolean grammar twins used as an independent finite semantic microscope for one recovery question:

> Given a binary sequence ecology and an optional generic one-bit state carrier, does architecture-name-free exhaustive/controlled search recover persistent state exactly when the behavioral requirement makes current-input-only realization impossible?

The NAND/NOR pair therefore serves the #833 alternate-encoding / grammar-twin / recovery-control programme. `G0-reg-v1` serves the broader operational Section-E register/control grammar programme.

The two results are consistent at their declared scopes:

1. `G0-reg-v1` can embed finite binary Mealy transducers, which includes the semantic class of the recovered two-state delayed-copy transducer.
2. This tranche does not claim the NAND/NOR surface syntax is the preferred or minimal G0 encoding.
3. This tranche's positive result is recovery of an implementation-invariant **state property** under two low-level Boolean encodings, not a universality theorem.
4. `G0-reg-v1` explicitly leaves grammar remints, alternate search algorithms, and morphology selection as separate obligations; this tranche supplies one small controlled experiment on precisely those axes.
5. Neither result licenses broad P3 known-form closure, universal search neutrality, or ontological completeness.

## Authority rule

For future #833 work:

- cite `research/gmi-833-g0-register-core-v1/` as the current Section-E operational G0 core;
- cite this tranche only for its scoped NAND/NOR grammar-twin state-property recovery and robustness evidence;
- do not use the label `G0 binary grammar` to imply that NAND/NOR has become the canonical G0 substrate.

The original frozen filenames/claim string are preserved for custody. Paper-facing interpretation follows this reconciliation.

## New-main merge gate

This tranche may merge only if the PR merge ref contains the merged `G0-reg-v1` result and its claim ceiling is GREEN, in addition to the already required scientific and #863 robustness checks. This forces the final PR head to be verified against the new authority rather than relying on checks from the earlier base.
