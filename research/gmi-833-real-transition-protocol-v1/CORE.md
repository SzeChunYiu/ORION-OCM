# gmi-833-real-transition-protocol-v1

Machine-checkable fail-closed protocol for the final #833 Section-J real-system transition row.

The protocol explicitly does **not** earn the scientific row. Current qualifying real-system receipt count is zero; synthetic/protocol fixtures cannot count toward five.

Reproduce:

```bash
python -I -B research/gmi-833-real-transition-protocol-v1/test_real_transition_protocol_v1.py -v
python -I -O -B research/gmi-833-real-transition-protocol-v1/test_real_transition_protocol_v1.py -v
python -I -B research/gmi-833-real-transition-protocol-v1/real_transition_protocol_v1.py
```

Protocol claim ceiling: `GMI_REAL_SYSTEM_TRANSITION_VALIDATION_PROTOCOL_MACHINE_CHECKABLE`.
