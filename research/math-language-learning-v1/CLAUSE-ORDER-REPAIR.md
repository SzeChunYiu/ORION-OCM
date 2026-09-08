# Clause donor: premise-order repair

This is an authored software-correctness successor to the
[negative development result](CLAUSE-REVIVAL-RESULT.md).
The donor remains default off. The earlier exploratory comparison and finite
applicability diagnosis are unchanged and were not rerun on this source.

## Observed failure

Reordering the same checked training premises put the complementary clause first.
Acquisition then raised `DEPENDENCY_ROLE_BINDING` in both actual adapters.
The retained regression has five failures and five clean controls: three affected
premise permutations and both adapters' reversed-order training.

The generic clause matcher returned its first clause-equivalent substitution.
That substitution need not preserve the specific observed pivot/residual roles;
aliasing can supply several equivalent substitutions. The independent role checker
correctly rejected it, but acquisition treated the first rejection as total failure.
The original authored training fixtures placed `every` before `no`, masking this.

## Minimal repair and costs

The existing finite matcher exposes `matches(...)` as a lazy enumeration.
`match(...)` keeps its existing first-match behavior for application. Derivation
checks candidate bindings until the independent support checker accepts the observed
roles. Only `DEPENDENCY_ROLE_BINDING` skips a candidate; every other refusal still
propagates. The schema, support and use checkers are unchanged.

`dependency_binding_candidates` counts each support-check attempt, and
`dependency_role_binding_rejections` counts the role mismatches skipped.
The existing match, normalization, substitution and verifier work remains charged
for every actually visited candidate. No query solve or new rule template is added.

## Current qualification

The repaired targeted run has 11 passes. It covers all six premise permutations,
actual admission/restore/use/revocation in both adapters in both premise orders,
additional candidate-work accounting, and a non-role checker failure that must escape.
The selected combined successor has 113 passes, no failures/errors/skips,
6.136038440 seconds and 386 identical source inputs before/after.

The earlier scoped source/95-control review and 104-control integration remain
historical. They do not independently review this successor. No final tasks,
registered draws, training/development matrix rerun or new scientific run occurred.

Raw records are external at
`/home/billy/orion-director-work/20260907/unary-clause-order-qualification-v1/`:
`01-red`, `02-green-order`, and `03-focused` retain original commands, source
snapshots, stdout/stderr, JUnit and process costs. Earlier revival raw and its
compact evidence proposal remain unchanged.

Current source map SHA256: ac270fc0a600cf728a44db71365b6593c9d1ade25a57c652f45a6a7fb36fc98d.
