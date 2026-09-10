# G7 one persistent developmental lineage (microscope)

**Terminal:** `PHASED_COGNITIVE_DEVELOPMENT`

Owner: issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) G7 / #151. Previous
programme-closure disposition was
`CANNOT_CHECK_ONE_OF_SIX_TRANSITIONS_COMPLETE_AND_THAT_ONE_PARENT_SUFFICIENT`
because no `DevelopmentTransitionV1` records were emitted and no lineage vessel
existed. This capsule improves that root cause by actually persisting **two**
earned transitions on **one** lineage id. It does **not** complete D2–D6. D3
formal mathematics did not happen.

```text
T0  EMPTY → OCM_0 / D0 exact interaction
    G2-style one macro acquired (tiny exact token-word search, N small)

T1  OCM_0 → OCM_1 / D1 composition / failure / scope
    G3.2-style scoped failure memory added
    same lineage id
    no reset in the principal arm
```

Unrun (registered, not pretended): `OCM_2` D2 planning/uncertainty,
`OCM_3` D3 formal mathematics / controlled language, `OCM_4` D4 coding/tools,
`OCM_5` D5 metacognition, `OCM_6` D6 governed self-evolution.

## Persist where earned

The serialised bundle always contains:

| slot | T0 | T1 |
|---|---|---|
| field state | seed atoms + admitted method | retained |
| learned methods | one macro | same macro |
| method schemas | macro-token schema | retained |
| imported donors | four taught primitives | retained |
| applicability/scope | empty | degree-class restriction |
| failure/counterexample knowledge | empty | `MACRO_AT_EMPTY_PREFIX` as `METHOD_FAILURE`, not impossibility |
| representations | taught coefficient normal form | retained |
| support/dependency | training SUPPORT edge | plus RESTRICTS edge |
| acquisition strategies | taught exact BFS | retained |
| executive/metareasoning policy | small domain-general serve+nogood rule | retained |
| self-model | known competence list | updated stage |
| self-change history | admit-macro | admit-failure-memory |
| resource history | T0 work units | T1 work units |

Restart is `persist` then a fresh `LineageStore.load` of the whole bundle.
A mismatched digest raises `DigestTamperError` and does not load.

## Comparators (every transition)

```text
CONTINUED_OCM
RESET_OCM
TASK_SPECIFIC_OCM
STRONG_ADAPTIVE_PARENT
```

The reset arm has its own store root. Loading a path outside that root fails
closed. At T1 reset must re-acquire the macro from scratch and therefore costs
more than continued, which reuses the T0 method. Reset rediscovery is labelled
`INDEPENDENT_REDISCOVERY`. The ordinary library+nogood parent may **tie** the
T1 mechanism; that is §12 absorption, not a claim that reset equals continued.

## Origin categories

| object | category |
|---|---|
| inc/dec/double/square, checker, BFS | `TAUGHT_IMPORTED` |
| T0 macro fragment | `LEARNED_COMPOSITION` |
| T1 degree-class failure/scope | `LEARNED_APPLICABILITY` |
| reset-arm re-acquired macro | `INDEPENDENT_REDISCOVERY` |

Failure records store **no task ids**. Scope is `target_degree_lt`. Higher-degree
D0 tasks keep MACRO (retention). Compatible low-degree trap tasks skip
MACRO-at-empty-prefix (dead-end reduction). Ablation: drop the failure record
and trap search returns to the unpruned grammar.

## What this does not claim

- Not D2–D6, not cross-domain, not lifetime payback, not architecture residual
  over the ordinary parent.
- Not G3.1 independent two-macro composition (already owned by #193).
- Not G3.3 representation change.
- `κ`, `Ω`, `χ` are microscope coordinates (object locality, probes-to-diagnosis,
  remaining enumeration), not a G6 evolvability law.

## Reproduction

```sh
python -B -m unittest discover -s research/g7-lineage-v1 -p 'test_*.py' -v
python -B research/g7-lineage-v1/experiment.py \
  --out research/g7-lineage-v1/RESULT.json \
  --transitions research/g7-lineage-v1/transitions
```

[RESULT.json](RESULT.json) · [T0](transitions/T0.json) · [T1](transitions/T1.json) ·
[schema](schema.json)
