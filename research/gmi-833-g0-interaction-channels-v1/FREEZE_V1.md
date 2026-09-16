# GMI #833 E5 — communication/external-call freeze v1

**Parent:** #833 Section E  
**Child:** #887  
**Source main:** `88d8ac811f80dd3f5c0b1a20f53fdf7259e3ca9c`  
**Status:** pre-implementation theorem/evidence freeze

## Boundary

This tranche adds explicit finite interaction channels only. It does not claim emergent communication, multi-agent learning, consensus, tool-use intelligence, autonomous agency, external-response truth, or authority delegation.

## Carrier

- agents `A={0,1,2}`;
- local register per agent in `Z3`;
- message alphabet `M={0,1}`;
- six directed FIFO queues `(src,dst)` for `src!=dst`;
- tool registry `ROT(x)=x+1 mod3`, `DOUBLE(x)=2x mod3`.

## Operators

- `SEND(src,dst,m)`: append only to queue `(src,dst)`; self-send invalid.
- `RECV(src,dst)`: pop oldest queue entry or return typed `NO_MESSAGE`; it does not mutate local registers.
- `APPLY_RECEIVED(dst,m)`: explicit local update `x_dst <- (x_dst+m) mod3`.
- `CALL(tool,arg)`: return typed `ExternalData(tool,arg,value)`; unknown tool/invalid argument fails closed. Call return is data, not verification/authority.
- `APPLY_EXTERNAL(agent,data)`: explicit local update using `data.value`; no implicit adoption.

## Exact finite certificate

1. One-send agent-remint covariance: all `6 channels * 2 messages * 6 permutations = 72` cases.
2. FIFO: all `6 channels * 4 two-message sequences = 24` cases.
3. Destination isolation: every one-send case changes exactly one queue and no local register.
4. No broadcast: message appears on exactly the named channel.
5. Receive/apply split: receive alone changes only queue/read result; explicit apply changes only named receiver register.
6. Tool table: `2 tools * 3 arguments = 6` exact calls; composed `ROT -> DOUBLE` and `DOUBLE -> ROT` remain order-sensitive controls.
7. Agent-remint covariance is checked for queue/local-state transport; tool results are agent-independent external data.

## Raw resource vector

`(message_writes,message_reads,local_reads,local_writes,external_calls,external_input_units,external_output_units)`.

- SEND: `(1,0,0,0,0,0,0)`
- RECV hit: `(0,1,0,0,0,0,0)`; empty receive also charges one read attempt.
- APPLY_RECEIVED: `(0,0,1,1,0,0,0)`
- CALL: `(0,0,0,0,1,1,1)`
- APPLY_EXTERNAL: `(0,0,1,1,0,0,0)`

## Hostiles

Reject self-send, out-of-carrier agent, bad message, malformed/unknown channel, malformed queue state, non-bijective agent remint, unknown tool, invalid tool argument, forged external-data object/tool/value mismatch. `NO_MESSAGE` is not message zero. External data is never marked VERIFIED/AUTHORIZED by this tranche.

## Claim ceiling

`GMI_FINITE_EXPLICIT_COMMUNICATION_AND_EXTERNAL_CALL_OPERATORS_AT_REGISTERED_SCOPE`

Forbidden: `EMERGENT_COMMUNICATION`, `MULTI_AGENT_LEARNING_DERIVED`, `DISTRIBUTED_CONSENSUS_DERIVED`, `TOOL_USE_INTELLIGENCE_DERIVED`, `EXTERNAL_RESPONSE_IS_TRUTH`, `AUTHORITY_DELEGATED_TO_TOOL`, `AUTONOMOUS_AGENCY`, `COMPLETE_GMI`.

## Reconciliation

Only after exact-head PR CI is green may this child change:

- `Add communication/multi-agent operators.`
- `Add external tool/environment calls.`
