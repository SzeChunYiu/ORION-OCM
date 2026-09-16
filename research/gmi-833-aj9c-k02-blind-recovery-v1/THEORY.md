# AJ9c — blind recovery of the registered K02 family

## Question

Can the frozen GMI/AJ process programme recover a persistent causal state mechanism from a temporal requirement without generation/search/evaluation receiving a recurrent-family label, equation, macro, or K02 fingerprint?

This tranche tests only `K02`; AJ9 remains open.

## Frozen blind problem

At freeze the search sees binary input/output traces and the requirement: emit the immediately preceding input, with initial required output 0. Candidate capacity is generic process organization capacity: either no persistent cell or one binary persistent cell. No named architecture is supplied.

The complete registered candidate universe contains:

- 4 zero-cell deterministic input/output maps;
- 256 one-cell deterministic `(internal,input)->(next_internal,output)` maps;
- 260 total organizations.

Two materially different procedures are registered:

1. full table enumeration in row-table presentation;
2. partial-table constraint filtering in packed-bitstring presentation.

## Blind outcome

Across all 260 organizations:

- zero stateless organizations satisfy the full frozen delayed-copy trace suite;
- exactly one one-cell organization satisfies it;
- the constraint search visits 25 partial nodes, prunes 18, and reaches the same unique table.

The recovered table is:

```text
(internal=0,input=0) -> (next=0,output=0)
(internal=0,input=1) -> (next=1,output=0)
(internal=1,input=0) -> (next=0,output=1)
(internal=1,input=1) -> (next=1,output=1)
```

Equivalently at this finite scope, the next internal value becomes the current input and the output is the preceding internal/input value. That equivalence is explanatory and is not supplied to the search.

## Post-hoc adjudication

Only after `BLIND_OUTCOME_V1.json` is frozen does the adjudicator read the AJ9a K02 fingerprint. It verifies:

- internal value 1 is reachable and persists across external steps as a causal machine variable;
- under the same current input 0, reachable prior internal values 0 and 1 produce different protected outputs;
- the internal value is updated;
- an update is read on a later external step and changes the protected response;
- there is a concrete update cycle `0 --input1--> 1 --input0--> 0`;
- protected delayed-copy I/O is exact on the frozen complete trace suite.

Both registered search presentations pass, so the post-hoc terminal is `RECOVERED`.

## Scope boundary

This is structural/causal recovery of the registered recurrent/stateful family fingerprint. It does not derive a named RNN equation, recurrent neural training, long-horizon continuous state, stochastic recurrence, or universal recurrence optimality. No pre-search morphology-selection prediction was frozen, so `PREDICTED_SELECTED` is forbidden.

## Claim ceiling

`AJ9C_K02_BLIND_STATEFUL_RECOVERY_AT_FROZEN_FINITE_SCOPE`
