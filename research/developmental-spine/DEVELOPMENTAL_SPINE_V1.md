# DEVELOPMENTAL_SPINE_V1

**GENERATED FILE — edit `spine.py`, then run `python spine.py`.**

DEV-D1 and DEV-D8 of [#151](https://github.com/SzeChunYiu/ORION-OCM/issues/151).

> 0 of 6 developmental transitions are complete. Every one is blocked on the same two things: no lane has run a CONTINUED arm that carried state across a stage boundary, and no lane has run a RESET arm to compare it with. The existing receipts are stage evidence, not transition evidence, and the difference is the whole of #151.

| transition | complete | receipts | arms present | blocking |
|---|---|---|---|---|
| D0 → D1 | False | 5 | STRONG_ADAPTIVE_PARENT | no CONTINUED_OCM, RESET_OCM, TASK_SPECIFIC_OCM arm exists for this transition; w… |
| D1 → D2 | False | 3 | STRONG_ADAPTIVE_PARENT | no CONTINUED_OCM, RESET_OCM, TASK_SPECIFIC_OCM arm exists for this transition; w… |
| D2 → D3 | False | 2 | STRONG_ADAPTIVE_PARENT | no CONTINUED_OCM, RESET_OCM, TASK_SPECIFIC_OCM arm exists for this transition; w… |
| D3 → D4 | False | 0 | — | no CONTINUED_OCM, RESET_OCM, STRONG_ADAPTIVE_PARENT, TASK_SPECIFIC_OCM arm exist… |
| D4 → D5 | False | 0 | — | no CONTINUED_OCM, RESET_OCM, STRONG_ADAPTIVE_PARENT, TASK_SPECIFIC_OCM arm exist… |
| D5 → D6 | False | 0 | — | no CONTINUED_OCM, RESET_OCM, STRONG_ADAPTIVE_PARENT, TASK_SPECIFIC_OCM arm exist… |

## Required arms (DEV-D8)

- **CONTINUED_OCM** — full earned prior developmental state
- **RESET_OCM** — same immutable architecture and current-stage information, no prior competence
- **STRONG_ADAPTIVE_PARENT** — strongest faithful parent with matched information, memory, tools and adaptation permissions
- **TASK_SPECIFIC_OCM** — built for this stage alone; bounds how much of any gain is generality

## What is actually missing

- A machine that acquires competence at D0 and then meets D1 carrying it. Every current receipt either holds one stage's tasks with no acquisition across a boundary, or draws its tasks independently so nothing is carried.
- A reset arm. Without it a lower cost at D1 is equally explained by D1 being easier, which #151 section 6 names as the thing not to claim development from.
- Reuse execution witnesses across a boundary. No object identity in the repository is currently observed being acquired at one stage and invoked at the next.

## Cheapest first transition

D0 to D1 on the exact game families already built. D0 acquires periodic-rule methods; D1 requires composing two of them, which the SUBNIM family in games.py already supports because neither the one-heap nor the Nim training family contains the combined solution. That is DEV-D10 and it needs no new domain.

## The field added beyond #151's list

`cheaper_because` — #151 section 3 states the decisive question is not whether the older machine scores higher but whether prior experience causally made the next competence cheaper. A receipt recording only the score would satisfy the listed fields and still not answer that, so the causal attribution is a required field here.

## Evidence map

| receipt | stage | supplies | note |
|---|---|---|---|
| `SCALING_PILOT_V1.json` | D0 | 7 fields | carries state across scales without reset, so its k and byte measurements are lineage measurements. It has no reset arm and no acquisition of new competence, so it is stage evidence, not transition evidence. |
| `SUBSPACE_E1_V1.json` | D0 | 5 fields | same lineage discipline; adds the relevance-key degradation measurement. |
| `REINDEX_E9_V1.json` | D0 | 3 fields | an engineering fix to one coordinate; contributes maintenance cost only. |
| `DEPEND_E3_V1.json` | D0 | 3 fields | revocation across a growing store; supplies revision cost. |
| `FAILURE_PILOT_V1.json` | D1 | 4 fields | scope and failure knowledge, which is D1 material, but each world is independent so nothing is carried from D0. |
| `DIAGNOSIS_E2_V1.json` | D2 | 3 fields | probe selection under hidden cause, which is D2 material. |
| `ESCALATION_INDEPENDENT_E4_V1.json` | D2 | 2 fields | obstruction versus search-more, which is D2 material. |