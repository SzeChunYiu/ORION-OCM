# HSG coverage matrix V1 (per-(atom, rung))

Remediation of D6' finding 2 (MED, C6): per-rung coverage was surfaced nowhere.
Grid: 35 atoms (G01–G17 concept, A_T01–A_T18 theorem) × rungs R1–R7. Cell kinds:
`assigned` (verdict row), `OPEN_PENDING_LANE_G_CONCEPT_ROWS` (concept content routed R6+ that lane G
has not landed — lane G holds zero concept rows), `OPEN_PENDING_LADDER_QUESTION_HALF` (the atom's
ladder question names this rung but no verdict row landed), `unrouted` (no lane document registers a
ladder question for this atom at this rung; not a coverage claim).
Totals: 51 assigned rung rows + 1 rung-`all` row (A_T15, SURV) = 52 verdict rows; 21 open-pending
cells (10 concept + 11 ladder-question halves); A_T10/A_T11 whole-atom OPEN; 173 unrouted.
Assigned census incl. the all-row matches HSG_SURVIVAL_V1.json overall (SURV 5 / COND 22 / FAIL 6 / PAR 12 / N/A 7).

| atom | R1 | R2 | R3 | R4 | R5 | R6 | R7 |
|---|---|---|---|---|---|---|---|
| G01 | · | · | COND | · | · | · | · |
| G02 | · | · | COND | · | · | · | · |
| G03 | · | · | SURV | PAR | N/A | · | · |
| G04 | · | COND | · | · | · | · | · |
| G05 | · | · | COND | · | · | OPEN-G | OPEN-G |
| G06 | · | · | COND | · | · | · | · |
| G07 | · | · | SURV | · | · | · | OPEN-G |
| G08 | · | SURV | · | · | · | OPEN-G | OPEN-G |
| G09 | · | · | COND | COND | PAR | · | · |
| G10 | · | · | COND | FAIL | PAR | · | · |
| G11 | · | · | COND | PAR | N/A | OPEN-G | · |
| G12 | PAR | · | · | N/A | FAIL | · | · |
| G13 | · | FAIL | · | · | · | · | OPEN-G |
| G14 | PAR | · | · | FAIL | N/A | · | OPEN-G |
| G15 | · | COND | · | FAIL | SURV | · | · |
| G16 | · | · | COND | N/A | PAR | · | OPEN-G |
| G17 | · | · | COND | COND | N/A | OPEN-G | · |
| A_T01 | · | OPEN-LQ | · | FAIL | · | · | · |
| A_T02 | · | · | · | N/A | COND | · | · |
| A_T03 | · | OPEN-LQ | · | COND | · | · | · |
| A_T04 | · | · | OPEN-LQ | · | · | COND | · |
| A_T05 | · | · | · | · | PAR | · | OPEN-LQ |
| A_T06 | · | · | · | PAR | · | · | OPEN-LQ |
| A_T07 | · | · | · | PAR | · | OPEN-LQ | · |
| A_T08 | · | · | OPEN-LQ | OPEN-LQ | · | COND | · |
| A_T09 | · | · | · | · | · | COND | · |
| A_T10 | · | · | · | · | · | · | · | **atom OPEN**
| A_T11 | · | · | · | · | · | · | · | **atom OPEN**
| A_T12 | · | · | · | · | PAR | · | · |
| A_T13 | · | · | · | · | · | COND | · |
| A_T14 | · | · | OPEN-LQ | OPEN-LQ | · | PAR | · |
| A_T15 | · | · | · | · | · | · | · | (+all=SURV)
| A_T16 | · | · | · | · | OPEN-LQ | COND | · |
| A_T17 | · | · | · | · | · | · | COND |
| A_T18 | · | · | · | · | · | · | COND |

Key: SURV=LIFT_SURVIVES, COND=LIFT_CONDITIONAL, FAIL=LIFT_FAILS, PAR=PARENT_SUFFICIENT, N/A=NOT_APPLICABLE, · = unrouted.
