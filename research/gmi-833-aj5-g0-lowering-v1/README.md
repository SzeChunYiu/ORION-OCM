# gmi-833-aj5-g0-lowering-v1

AJ5 closure package: derives the current `G0-reg-v1` instruction surface from lower operational roles and checks two lower presentations.

Reproduce:

```bash
python3 -I -B research/gmi-833-aj5-g0-lowering-v1/check_aj5.py
python3 -I -O -B research/gmi-833-aj5-g0-lowering-v1/check_aj5.py
```

Expected: 121 bounded programs × 4 input words = 484 semantic executions, zero mismatches for both the functional event/state-transform lowering and the relational small-step lowering.

Claim ceiling: `AJ5_G0_LOWERED_TO_OPERATIONAL_ROLES_WITH_TWO_PRESENTATIONS_AT_REGISTERED_SCOPE`.
