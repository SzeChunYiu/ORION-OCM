# AJ11 freeze — bounded complete atlas / unbounded openness

## Finite registered universe

This tranche freezes the AJ4 binary process-organization universe as the candidate universe:
- 4 stateless binary transducers;
- all 256 one-bit binary Mealy transducers;
- initial state 0;
- total 260 presentations.

The registered protected task family is frozen before atlas construction:
1. `IDENTITY1`: one-step identity on both binary inputs;
2. `NOT1`: one-step negation on both binary inputs;
3. `DELAY1_H3`: delay-one output with initial previous bit 0 on all binary words of lengths 1..3;
4. `PARITY_H3`: cumulative XOR output on all binary words of lengths 1..3.

Raw atlas coordinates are task error counts plus `(state_cells, truth_rows)`. No scalar utility is privileged. Four strictly-positive frozen scalar probes are used only as secondary preference queries: BALANCED, DELAY_HEAVY, RESOURCE_HEAVY, PARITY_HEAVY.

Development is a finite graph on presentations. Legal one-edit edges are:
- one truth-table bit change within the same presentation type;
- add/drop one state cell only through the canonical stateless embedding whose next state is fixed to zero and whose outputs duplicate the stateless map.
The registered development atlas includes the complete graph and the exact radius-2 reachability set from constant-zero stateless seed.

Operational duplicate collapse uses AJ4 all-word protected I/O equivalence. Because operationally equivalent presentations can have different resources/reachability, the atlas retains presentation-level resource/development records and projects rather than erasing them.

## Unbounded boundary

At ordinary unbounded Turing-complete scope, syntax may be enumerable while nontrivial semantic properties, halting and extensional program equivalence are undecidable in general. AJ11 therefore forbids a terminating complete semantic catalogue at that scope. The accepted target is open generativity + scoped recovery/prediction + explicit UNKNOWN/boundaries.

Claim ceiling if the finite census is exact: `AJ11_COMPLETE_BOUNDED_MACHINE_CAPABILITY_DEVELOPMENT_ATLAS_AND_UNBOUNDED_SEMANTIC_OPENNESS_AT_REGISTERED_SCOPE`.

Allowed finite terminal: `COMPLETE_GMI_ATLAS_AT_BOUND_B` only for this explicitly frozen 260-presentation universe/task/resource/development frame.

Forbidden: `ALL_MACHINE_INTELLIGENCES_COMPLETELY_CLASSIFIED` at unbounded standard-computation scope; `COMPLETE_GMI`.
