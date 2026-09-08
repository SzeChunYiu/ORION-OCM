# DEVELOPMENTAL_SPINE_V1

**GENERATED FILE — edit `spine.py`, then run `python spine.py`.**

DEV-D1 and DEV-D8 of [#151](https://github.com/SzeChunYiu/ORION-OCM/issues/151).

> 1 of 6 developmental transitions are complete. D0 to D1 is measured: DEV1_D0_TO_D1_V1 runs a lineage that carries its D0 store across the boundary, a reset arm with the same architecture and the same D1 stream that does not, a clairvoyant parent, and a task-specific arm. Its verdict is CONDITIONAL, not a win -- the lineage beats reset at 1024 bits and loses at 256 -- and 'complete' here means MEASURED WITH ALL FOUR ARMS AND ALL REQUIRED FIELDS, never 'succeeded'. The remaining five are still blocked on the same two things: no lane has run a CONTINUED arm across those boundaries and no lane has run a RESET arm to compare it with. The existing receipts for them are stage evidence, not transition evidence, and that difference is the whole of #151.

| transition | complete | receipts | arms present | blocking |
|---|---|---|---|---|
| D0 → D1 | True | 6 | CONTINUED_OCM, RESET_OCM, STRONG_ADAPTIVE_PARENT, TASK_SPECIFIC_OCM | … |
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

- Four more machines that acquire competence at one stage and meet the next carrying it. D0 to D1 now has one; D1 to D2 onward have none, and their current receipts either hold one stage's tasks with no acquisition across a boundary or draw their tasks independently so nothing is carried.
- Reset arms for those transitions. Without one, a lower cost at the later stage is equally explained by that stage being easier, which #151 section 6 names as the thing not to claim development from.
- A transition that holds at every store budget. The one that exists does not: at 256 bits the D0 store saturates and the lineage loses, which is a real limit on the claim rather than a gap in the evidence.

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
| `DEV1_D0_TO_D1_V1.json` | D1 | 30 fields | the first receipt in the repository written for a TRANSITION rather than a stage: one lineage carries its D0 store across the boundary, a reset arm with the same architecture and the same D1 stream does not, a clairvoyant parent bounds the claim, and a task-specific arm bounds how much of the gain is generality. It counts only for D0 to D1, and its own terminal is CONDITIONAL: the lineage wins at 1024 bits and loses at 256, so this transition is complete in the sense of being MEASURED, not in the sense of being won everywhere. |