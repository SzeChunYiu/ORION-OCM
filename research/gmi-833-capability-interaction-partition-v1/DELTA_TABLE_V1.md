# DELTA TABLE V1 — corrected 27x27 capability-interaction census

**GENERATED FILE.** Produced by `emit_receipts_v1.py` from the computed census;
no row is hand-transcribed. All 351 rows also live in `RESULT_V1.json` (`per_pair`).

Accounting: A4 registered fully-shareable/nested regime — every capability using
channel `c` claims the same single unit of `c`, so `B(X) = |R(X)|` and
`joint = |R(X) u R(Y)|` (counting measure on a finite unit set).

## 1. Headline

| quantity | value |
|---|---|
| unordered pairs | 351 |
| shipped census | independent 8, synergistic 161, redundant 182, interfering 0 |
| corrected census | INDEPENDENT 8, REDUNDANT 287, PARTIAL_SHARING 56, INTERFERING 0 |
| labels changed | 217 / 351 |
| **DEF-1** shipped label contradicts Section 1.2's own definition | **56 / 351** |
| **DEF-2** pairs satisfying more than one Section 1.2 label | **287 / 351** |

Two exact set identities (proved in `..._THEOREMS_V1.md`, checked in the tests):

- the DEF-1 set is **exactly** the `PARTIAL_SHARING` class (56 pairs);
- the DEF-2 set is **exactly** the `REDUNDANT` class (287 pairs), because
  `joint = max < sum` satisfies both shipped conditions `joint = max` (Redundant)
  and `joint < sum` (Synergistic).

## 2. Aggregate transition table

| shipped label | channel relation | corrected class | pairs | changed | why |
|---|---|---|---:|:---:|---|
| independent | disjoint | `INDEPENDENT` | 8 | no | `joint = sum`; the shipped label was already correct and uniquely justified. |
| redundant | nested-proper | `REDUNDANT` | 126 | no | `joint = max < sum`; R(X) properly contains R(Y) or conversely. Name unchanged, now uniquely justified by the `max < sum` guard. |
| redundant | non-nested-overlap | `PARTIAL_SHARING` | 56 | yes | **CORRECTION.** `max < joint < sum`, so the shipped label's own defining condition `joint = max` is FALSE here. |
| synergistic | equal | `REDUNDANT` | 161 | yes | `joint = max < sum`. `joint < sum` (Synergistic) held but NOT uniquely: `joint = max` (Redundant) held too. The unique CIP-1 class is REDUNDANT. |

Total: 351 pairs; 217 changed.

## 3. DEF-1 — every pair whose shipped label is FALSE by Section 1.2's own definition (56 pairs)

Shipped label `redundant` is defined `joint = max(individual)`; each row below has
`max < joint`, so the equality fails. Corrected class `PARTIAL_SHARING`.

| # | X | Y | R(X) | R(Y) | B(X) | B(Y) | max | joint | sum | shipped | corrected |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | perception | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 2 | perception | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 3 | perception | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 4 | selective-attention | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 5 | selective-attention | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 6 | selective-attention | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 7 | working-memory | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 8 | working-memory | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 9 | working-memory | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 10 | episodic-memory | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 11 | episodic-memory | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 12 | episodic-memory | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 13 | semantic-memory | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 14 | semantic-memory | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 15 | semantic-memory | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 16 | procedural-memory | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 17 | procedural-memory | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 18 | procedural-memory | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 19 | consolidation | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 20 | consolidation | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 21 | consolidation | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 22 | forgetting | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 23 | forgetting | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 24 | forgetting | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 25 | prediction | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 26 | prediction | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 27 | prediction | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 28 | abstraction-concept | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 29 | abstraction-concept | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 30 | abstraction-concept | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 31 | compositional-reasoning | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 32 | compositional-reasoning | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 33 | compositional-reasoning | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 34 | hierarchical-skill | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 35 | hierarchical-skill | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 36 | hierarchical-skill | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 37 | planning | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 38 | planning | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 39 | planning | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 40 | exploration | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 41 | exploration | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 42 | exploration | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 43 | counterfactual-reasoning | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 44 | counterfactual-reasoning | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 45 | counterfactual-reasoning | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 46 | social-cognition | communication | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 47 | social-cognition | teaching | {S,T} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 48 | social-cognition | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 49 | communication | teaching | {M,S} | {M,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 50 | communication | cultural-accumulation | {M,S} | {S,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 51 | communication | self-modeling | {M,S} | {S,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 52 | teaching | cultural-accumulation | {M,T} | {S,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 53 | teaching | self-modeling | {M,T} | {S,T} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 54 | teaching | coordination | {M,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 55 | cultural-accumulation | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |
| 56 | self-modeling | coordination | {S,T} | {M,S} | 2 | 2 | 2 | 3 | 4 | `redundant` | `PARTIAL_SHARING` |

## 4. Relabelled without contradiction — `synergistic` -> `REDUNDANT` (161 pairs)

These pairs use identical channel sets, so `joint = max < sum`. The shipped label
`synergistic` satisfied its Section 1.2 condition `joint < sum`, but so did
`redundant` (`joint = max`): the shipped taxonomy did not pick one. Under CIP-1 the
unique class is `REDUNDANT`, and the saving content is preserved by
`SAVING = REDUNDANT (disjoint union) PARTIAL_SHARING = {joint < sum}`.

| # | X | Y | R(X)=R(Y) | max | joint | sum | shipped | corrected |
|---:|---|---|---|---:|---:|---:|---|---|
| 1 | perception | selective-attention | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 2 | perception | working-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 3 | perception | episodic-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 4 | perception | semantic-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 5 | perception | procedural-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 6 | perception | consolidation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 7 | perception | forgetting | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 8 | perception | prediction | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 9 | perception | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 10 | perception | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 11 | perception | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 12 | perception | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 13 | perception | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 14 | perception | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 15 | perception | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 16 | perception | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 17 | perception | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 18 | selective-attention | working-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 19 | selective-attention | episodic-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 20 | selective-attention | semantic-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 21 | selective-attention | procedural-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 22 | selective-attention | consolidation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 23 | selective-attention | forgetting | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 24 | selective-attention | prediction | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 25 | selective-attention | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 26 | selective-attention | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 27 | selective-attention | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 28 | selective-attention | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 29 | selective-attention | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 30 | selective-attention | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 31 | selective-attention | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 32 | selective-attention | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 33 | selective-attention | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 34 | working-memory | episodic-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 35 | working-memory | semantic-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 36 | working-memory | procedural-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 37 | working-memory | consolidation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 38 | working-memory | forgetting | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 39 | working-memory | prediction | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 40 | working-memory | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 41 | working-memory | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 42 | working-memory | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 43 | working-memory | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 44 | working-memory | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 45 | working-memory | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 46 | working-memory | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 47 | working-memory | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 48 | working-memory | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 49 | episodic-memory | semantic-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 50 | episodic-memory | procedural-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 51 | episodic-memory | consolidation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 52 | episodic-memory | forgetting | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 53 | episodic-memory | prediction | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 54 | episodic-memory | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 55 | episodic-memory | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 56 | episodic-memory | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 57 | episodic-memory | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 58 | episodic-memory | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 59 | episodic-memory | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 60 | episodic-memory | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 61 | episodic-memory | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 62 | episodic-memory | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 63 | semantic-memory | procedural-memory | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 64 | semantic-memory | consolidation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 65 | semantic-memory | forgetting | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 66 | semantic-memory | prediction | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 67 | semantic-memory | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 68 | semantic-memory | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 69 | semantic-memory | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 70 | semantic-memory | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 71 | semantic-memory | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 72 | semantic-memory | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 73 | semantic-memory | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 74 | semantic-memory | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 75 | semantic-memory | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 76 | procedural-memory | consolidation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 77 | procedural-memory | forgetting | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 78 | procedural-memory | prediction | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 79 | procedural-memory | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 80 | procedural-memory | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 81 | procedural-memory | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 82 | procedural-memory | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 83 | procedural-memory | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 84 | procedural-memory | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 85 | procedural-memory | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 86 | procedural-memory | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 87 | procedural-memory | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 88 | retrieval | tool-use | {M,S,T} | 3 | 3 | 6 | `synergistic` | `REDUNDANT` |
| 89 | consolidation | forgetting | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 90 | consolidation | prediction | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 91 | consolidation | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 92 | consolidation | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 93 | consolidation | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 94 | consolidation | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 95 | consolidation | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 96 | consolidation | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 97 | consolidation | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 98 | consolidation | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 99 | consolidation | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 100 | forgetting | prediction | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 101 | forgetting | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 102 | forgetting | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 103 | forgetting | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 104 | forgetting | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 105 | forgetting | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 106 | forgetting | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 107 | forgetting | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 108 | forgetting | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 109 | forgetting | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 110 | prediction | abstraction-concept | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 111 | prediction | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 112 | prediction | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 113 | prediction | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 114 | prediction | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 115 | prediction | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 116 | prediction | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 117 | prediction | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 118 | prediction | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 119 | abstraction-concept | compositional-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 120 | abstraction-concept | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 121 | abstraction-concept | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 122 | abstraction-concept | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 123 | abstraction-concept | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 124 | abstraction-concept | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 125 | abstraction-concept | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 126 | abstraction-concept | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 127 | compositional-reasoning | hierarchical-skill | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 128 | compositional-reasoning | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 129 | compositional-reasoning | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 130 | compositional-reasoning | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 131 | compositional-reasoning | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 132 | compositional-reasoning | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 133 | compositional-reasoning | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 134 | hierarchical-skill | planning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 135 | hierarchical-skill | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 136 | hierarchical-skill | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 137 | hierarchical-skill | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 138 | hierarchical-skill | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 139 | hierarchical-skill | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 140 | planning | exploration | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 141 | planning | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 142 | planning | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 143 | planning | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 144 | planning | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 145 | exploration | counterfactual-reasoning | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 146 | exploration | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 147 | exploration | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 148 | exploration | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 149 | causal-inference | metacognition | {T} | 1 | 1 | 2 | `synergistic` | `REDUNDANT` |
| 150 | causal-inference | imitation | {T} | 1 | 1 | 2 | `synergistic` | `REDUNDANT` |
| 151 | causal-inference | self-improvement | {T} | 1 | 1 | 2 | `synergistic` | `REDUNDANT` |
| 152 | counterfactual-reasoning | social-cognition | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 153 | counterfactual-reasoning | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 154 | counterfactual-reasoning | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 155 | metacognition | imitation | {T} | 1 | 1 | 2 | `synergistic` | `REDUNDANT` |
| 156 | metacognition | self-improvement | {T} | 1 | 1 | 2 | `synergistic` | `REDUNDANT` |
| 157 | social-cognition | cultural-accumulation | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 158 | social-cognition | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 159 | communication | coordination | {M,S} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |
| 160 | imitation | self-improvement | {T} | 1 | 1 | 2 | `synergistic` | `REDUNDANT` |
| 161 | cultural-accumulation | self-modeling | {S,T} | 2 | 2 | 4 | `synergistic` | `REDUNDANT` |

## 5. Unchanged labels (134 pairs)

| shipped = corrected | channel relation | pairs |
|---|---|---:|
| `independent` | disjoint | 8 |
| `redundant` | nested-proper | 126 |

The 8 `disjoint` pairs are the **no-alarm control**: they classify `INDEPENDENT`
under both the channel-overlap predicate and the burden classification, and they
are not flagged by the DEF-1 detector.

