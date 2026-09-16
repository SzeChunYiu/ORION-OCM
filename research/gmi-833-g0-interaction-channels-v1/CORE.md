# GMI #833 E5 — explicit communication and external calls

This capsule adds two architecture-family-free interaction channels to the G0 programme: directed FIFO message queues between finite agents, and explicit external request/response calls.

Communication never mutates another agent's local state implicitly; a received message must be explicitly applied. External call results are tagged `EXTERNAL_DATA` and do not become verified/authorized by returning from a tool.

The exact finite certificate covers all six directed channels, both messages and all six agent relabelings, all two-message FIFO sequences, and both registered tools on all three inputs.

Claim ceiling:

`GMI_FINITE_EXPLICIT_COMMUNICATION_AND_EXTERNAL_CALL_OPERATORS_AT_REGISTERED_SCOPE`
