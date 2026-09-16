# AJ1 operational process base

## Status and scope

This tranche defines the **minimum typed process structure required by the frozen finite AJ microscopes**. `minimum` is relative to the registered requirements below. It is not a unique ontology theorem.

For substrate/law model `S`, define an operational process frame

`O_S = (Obj, Proc, composition, tensor, I, id, Adm_S, Obs_S)`.

- `Obj`: interface/system types.
- `Proc(A,B)`: process descriptions from input interface `A` to output interface `B`.
- `g composition f`: typed sequential composition for `f:A->B`, `g:B->C`.
- `f tensor g`: parallel composition `A tensor C -> B tensor D`.
- `I`: monoidal/trivial interface; `id_A:A->A` are identity processes.
- `Adm_S(p)`: admissibility relative to the registered computational/physical substrate/laws `S`.
- `Obs_S`: registered observations of closed/admissible experimental composites. AJ2 will use this to construct contextual equivalence.

For the finite microscopes we use a strict monoidal presentation: associators/unitors are suppressed. This is presentation convenience, not an ontology claim.

### Frozen laws required at this scope

1. Sequential composition is typed and associative when defined.
2. Identities are left/right units.
3. Parallel composition is associative with unit `I`.
4. Interchange holds whenever well typed.
5. `Adm_S` is explicitly substrate-relative. Closure under a composition is required only for composition classes registered legal by `S`; arbitrary mathematical processes need not be physically admissible.
6. `Obs_S` is defined only through registered operational outcome semantics; it need not be deterministic or scalar.

Symmetry/swap is **not** placed in the common minimum because some process models have ordered/non-symmetric composition. It may be registered as additional structure.

## Relative-minimality requirements

The AJ1 finite microscope requires: `TYPE`, `SEQUENCE`, `PARALLEL`, `NO_CHANGE`, `SUBSTRATE_ADMISSIBILITY`, and `OPERATIONAL_OBSERVATION`.

Removing each corresponding component destroys at least one frozen requirement by construction. This establishes only requirement-relative signature irredundancy.

## Shared parent structure

The comparison ledger supports a deliberately weak invariant: typed/role-delimited processes, lawful composition/interaction, semantics of allowable behaviour or observations, and explicit model/substrate assumptions.

Sequential+parallel monoidal structure is directly native to process theories and operational probabilistic theories; relations and stochastic kernels instantiate it naturally; LTS/coalgebra formalisms are state/dynamics-first and require an interface/compositional wrapper to instantiate the full AJ1 frame; constructor theory is possibility/transformation-first and maps most directly to `Adm_S` plus composable tasks, without supplying the whole AJ1 observation/probability structure by itself.

Therefore no parent formalism is declared *the* absolute process ontology.

## Claim ceiling

`AJ1_TYPED_OPERATIONAL_PROCESS_FRAME_AT_FINITE_REGISTERED_SCOPE`

Forbidden: `ABSOLUTE_PROCESS_ONTOLOGY_PROVEN`.
