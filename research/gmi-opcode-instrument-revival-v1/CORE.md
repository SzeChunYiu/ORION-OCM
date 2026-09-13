# Opcode instrument revival

The one-line frame-callback assignment repaired all first-call opcode witnesses
on the registered laptop CPython 3.13.12 binary. No timing experiment ran.

- [Result and mechanism](RESULT_AND_MECHANISM_V1.md): original 120/128 complete;
  repaired 128/128, with unchanged candidate bodies and all raw failures retained.
- [Preregistration](PREREGISTRATION_V1.md) and
  [exclusive source/interpreter freeze](OPCODE_REVIVAL_FREEZE_V1.json).
- [Recomputed receipt](OPCODE_REVIVAL_RECEIPT_V2.json);
  [static audit](opcode_audit_v2.py), [independent oracle](opcode_witness_v1.py).
- [Portable replay correction](STATIC_REPLAY_V2.md) and [16 evidence tests](test_opcode_revival_v2.py).
- [Raw source and four executions](raw/): immutable historical parent snapshot,
  reservations and complete subprocess outputs.

This repairs an instrument at one recorded envelope. Frozen V5 remains refused
on its original 3.13 packet; no family, timing or universal substrate result is promoted.
