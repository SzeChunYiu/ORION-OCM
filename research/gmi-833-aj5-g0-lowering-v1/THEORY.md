# AJ5 — derive G0 as a presentation over the operational/process layer

AJ5 consumes merged AJ1–AJ4. It does **not** reinterpret the named G0 opcodes as elementary intelligence units. It treats them as a syntax/presentation compiled from lower interaction, state-transform, test/routing and terminal process roles.

## Lower role basis at this registered scope

The first lowering uses generic typed roles over a natural-number register carrier and explicit interaction channels:

- `NEXT_INPUT : InputStream -> Nat × InputStream`
- `LOAD/STORE : RegisterStore × Address <-> Nat`
- `SUCC : Nat -> Nat`
- `IS_ZERO : Nat -> Bool`
- `PRED_POS : Nat_{>0} -> Nat`
- `SELECT : Bool × Label × Label -> Label`
- `APPEND_OUTPUT : OutputStream × Nat -> OutputStream`
- `TERMINAL : Config -> Halted`
- ordinary sequential composition and the AJ4 persistent configuration channel.

None is called a neuron, layer, planner, memory architecture, search algorithm, or other known MI family.

The current G0 instruction classes lower as follows:

| G0 surface | Lower construction | AJ5 status |
|---|---|---|
| `READ r,L` | `NEXT_INPUT ; STORE(r) ; goto L` | `DERIVED` |
| `EMIT r,L` | `LOAD(r) ; APPEND_OUTPUT ; goto L` | `DERIVED` |
| `INC r,L` | `LOAD(r) ; SUCC ; STORE(r) ; goto L` | `DERIVED` |
| `DECJZ r,L+,L0` | `LOAD(r) ; IS_ZERO ; SELECT`; on nonzero additionally `PRED_POS ; STORE(r)` | `DERIVED` |
| `HALT` | choose terminal/no-successor configuration in the lower semantics | `PRESENTATION_ONLY` |

Thus the named opcodes are convenient macros/presentation elements. AJ5 does not claim the generic notions of interaction, transformation, testing, composition or termination were invented by GMI.

## Two materially different lower presentations

### P-FUN — functional event/state-transform presentation

A configuration is updated by deterministic generic functions implementing the lower roles above. One G0 transition is a composition of 1–5 lower operations.

### P-REL — relational small-step presentation

The same configuration interface is represented by a relation between pre/post configurations. `READ`, mutation, zero/nonzero tests, routing, output events and terminality are composed as relations. The registered G0 fragment is deterministic, but the semantic carrier is relational and does not assume functions as the only process model.

The checker enumerates all 121 two-label/one-register G0 programs made from the 11 registered instruction instances and four input words `(), (0), (1), (2)`, for 484 executions. Parent G0 execution, P-FUN and P-REL must agree on terminal, output, final register and G0-level step count under the same eight-step budget.

## Overhead theorem at this scope

For every successfully lowered G0 step:

- `HALT <= 1` lower operation;
- `READ <= 2` when input exists (underflow is one observed interaction attempt);
- `EMIT <= 2`;
- `INC <= 3`;
- `DECJZ <= 5`.

Therefore a trace of `t` G0 steps uses at most `5t` registered lower operations. A static expansion assigning the maximum branch body per instruction has size at most `5|P|`. These are presentation-relative accounting bounds, not universal hardware costs.

## Theorem transfer / non-transfer

Semantic preservation transfers parent G0 results whose conclusions depend only on protected execution semantics at this registered scope, including protected I/O behavior and the bounded embeddings that use those semantics.

It does **not** automatically transfer:

- G0 instruction-count descriptions;
- grammar-relative description-length statistics;
- G0 mutation/search distance;
- search order or reachability geometry;
- exact runtime/hardware cost.

Those quantities must be translated with the compiler/resource map. This prevents a semantics-preserving compiler from being misreported as representation-neutral search.

## Parent ownership

Operational/structural semantics, register-machine instruction decompositions, relational semantics, event/state-transform systems and compiler correctness are parent mathematics. AJ5's contribution is the explicit reduction of the repository's current G0 presentation into the AJ operational spine, two-presentation finite preservation certificate, primitive-status ledger and transfer boundary.

## Claim ceiling

`AJ5_G0_LOWERED_TO_OPERATIONAL_ROLES_WITH_TWO_PRESENTATIONS_AT_REGISTERED_SCOPE`

Forbidden: `G0_IS_THE_OPERATIONAL_BOTTOM`, `UNIQUE_LOWEST_INSTRUCTION_BASIS`, `COMPILER_MAKES_SEARCH_BIAS_INVARIANT`, `ALL_MACHINE_MODELS_COMPILED`, `COMPLETE_GMI`.
