# Interaction-channel theorems v1

## Expert review lanes

- **Concurrency / distributed semantics:** FIFO channel identity and state isolation.
- **Interactive systems:** explicit request/response boundary.
- **Epistemic authority:** external data is not verification or authorization.
- **Hostile verification:** channel leakage, malformed identities, queue order, agent relabeling and forged tool responses.

## COMM-1 — destination isolation

`SEND(src,dst,m)` appends only to the named queue. It does not mutate any agent-local register. The finite census checks all 12 directed-channel/message cases with zero destination, broadcast or local-state leakage.

## COMM-2 — FIFO and explicit application

For every directed channel and every two-message word over `{0,1}`, two receives return exactly the sent order: 24/24 cases. `RECV` alone does not modify local state; only explicit `APPLY_RECEIVED` changes the named destination register. Empty receive returns typed `NO_MESSAGE`, distinct from message `0`.

## COMM-3 — agent-remint covariance

Transport local states and every directed queue under an arbitrary bijection of the three agent IDs. Sending before transport equals transport before sending on the transported channel. All `6 channels × 2 messages × 6 permutations = 72` checks agree exactly.

## EXT-1 — explicit external calls

`CALL(tool,arg)` returns `ExternalData(tool,arg,value,status=EXTERNAL_DATA)`. Registered tools `ROT` and `DOUBLE` are exhaustively checked on `Z3`: six exact calls. `ROT→DOUBLE` and `DOUBLE→ROT` produce distinct full tables, confirming call order is observable.

## EXT-2 — authority boundary

A call return does not modify machine state and is not marked verified or authorized. Local state changes only through `APPLY_EXTERNAL`. A forged response whose value does not match the frozen external registry is rejected. Verification/adoption remains owned by a later authority tranche.

## RES-1 — raw interaction resources

Raw vector:

`(message_writes,message_reads,local_reads,local_writes,external_calls,external_input_units,external_output_units)`.

- SEND `(1,0,0,0,0,0,0)`
- RECV `(0,1,0,0,0,0,0)`
- APPLY `(0,0,1,1,0,0,0)`
- CALL `(0,0,0,0,1,1,1)`

No hidden channel/tool work is scalarized away.

## Falsifiers

Any implicit local mutation, cross-channel copy, FIFO failure, agent-remint mismatch, accepted malformed agent/message/tool, `NO_MESSAGE==0`, or automatic verification/authority promotion makes the tranche RED.
