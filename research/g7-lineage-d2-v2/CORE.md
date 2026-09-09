# G7 lineage D2 successor (microscope)

**Terminal:** `PHASED_COGNITIVE_DEVELOPMENT`

Owner: issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) G7 / #151.
Successor to [`research/g7-lineage-v1/`](../g7-lineage-v1/CORE.md), which stopped
at two earned transitions (`EMPTY→OCM_0`, `OCM_0→OCM_1`) on lineage id
`orion-ocm-g7-lineage-v1:microscope-d0-d1` with D2–D6 unrun.

This capsule **does not overwrite** v1 `RESULT.json`. It continues the **same
lineage id** and actually runs a third earned `DevelopmentTransitionV1`
`OCM_1 → OCM_2` / D2 planning / uncertainty / information gathering.

Historical M11 `g0 → g1 → g2 → g2` is **not** relabeled.

```text
T0  EMPTY → OCM_0 / D0 exact interaction
    G2-style one macro acquired (tiny exact token-word search)

T1  OCM_0 → OCM_1 / D1 composition / failure / scope
    G3.2-style scoped failure memory added
    same lineage id; no reset in the principal arm

T2  OCM_1 → OCM_2 / D2 planning / uncertainty / information gathering
    greedy posterior-split probe policy on a disjoint diagnosis family
    T0 MACRO and T1 failure memory retained
    constitution C frozen
```

Unrun (registered, not pretended): `OCM_3` D3 formal mathematics / controlled
language, `OCM_4` D4 coding/tools, `OCM_5` D5 metacognition, `OCM_6` D6
governed self-evolution. D3 formal mathematics did not happen.

## Why T2 is a new family, not a third polynomial trick

D0/D1 remain the polynomial grammar `g7.polynomial-total-arithmetic.v1`
(inc/dec/double/square, MACRO, degree-class nogoods).

D2 is `g7.diagnosis-probe-planning.v1`: 6 modules, hidden 2- or 3-stuck
configurations (35-state closed population), overlapping parity syndrome,
probes that reveal one module, then an ordered replace plan. Fingerprints
do not overlap the polynomial family. The learned object is a
**probe policy**, not another MACRO fragment and not a task-id blacklist.

Conversion if the policy cannot beat round-robin on held-out diagnosis
episodes:

```text
CANNOT_CHECK_D2_PROBE_POLICY_NOT_EARNED
```

v1's root-cause conversion (no `DevelopmentTransitionV1` records) is already
closed by v1. This successor's conversion, if T2 is not earned, is a named
`CANNOT_CHECK`, not a fake `OCM_2` and not a salt retune of T1 traps.

## Persist where earned

The serialised bundle always contains the thirteen G7 slots. After T2 the
earned contents are:

| slot | T0 | T1 | T2 |
|---|---|---|---|
| field state | seed atoms + admitted method | retained | plus probe-policy atom |
| learned methods | one macro | same macro | plus D2 probe policy |
| method schemas | macro-token schema | retained | plus probe-policy schema |
| imported donors | four taught primitives | retained | plus taught probe/replace operators |
| applicability/scope | empty | degree-class restriction | retained |
| failure/counterexample knowledge | empty | `MACRO_AT_EMPTY_PREFIX` | retained |
| representations | taught coefficient normal form | retained | retained |
| support/dependency | training SUPPORT edge | plus RESTRICTS edge | plus D2 SUPPORT edge |
| acquisition strategies | taught exact BFS | retained | retained |
| executive/metareasoning policy | serve+nogood; **do not rewrite C** | retained | family-gated serving; C frozen |
| self-model | known competence list | updated stage | OCM_2; OCM_2 removed from unknown |
| self-change history | admit-macro | admit-failure-memory | admit-d2-probe-policy |
| resource history | T0 work units | T1 work units | T2 work units |

Restart is `persist` then a fresh `LineageStore.load` of the whole bundle.
A mismatched digest raises `DigestTamperError`. Rewriting constitution C
raises `ConstitutionMutationError` and does not persist.

## Comparators (every transition, including T2)

```text
CONTINUED_OCM
RESET_OCM
TASK_SPECIFIC_OCM
STRONG_ADAPTIVE_PARENT
```

T2 reset has its own store root, starts empty, and must re-acquire T0 then T1
then T2. Isolation failure is `IsolationError`. Reset rediscovery is
`INDEPENDENT_REDISCOVERY`. Continued reuses T0/T1 and only pays D2
acquisition, so reset costs more.

Task-specific D2 learns the probe policy without T0/T1. D0/D1 do **not**
cheapen D2 versus that learner; that is recorded, not claimed as
cross-family transfer. The ordinary probe-policy parent may **tie** the T2
mechanism (§12 absorption).

## Origin categories

| object | category |
|---|---|
| inc/dec/double/square, checker, BFS, D2 probes/replace, syndrome windows | `TAUGHT_IMPORTED` |
| T0 macro fragment | `LEARNED_COMPOSITION` |
| T1 degree-class failure/scope | `LEARNED_APPLICABILITY` |
| T2 greedy posterior-split probe policy | `LEARNED_COMPOSITION` |
| reset-arm re-acquired macro / policy | `INDEPENDENT_REDISCOVERY` |

## What this does not claim

- Not D3–D6, not cross-domain transfer, not lifetime payback, not an OCM
  architecture residual over the ordinary parent.
- Not G3.1 independent two-macro composition, not G3.3 representation change,
  not G6 three-generation self-evolution, not production M11.
- `κ`, `Ω`, `χ` are microscope coordinates, not a G6 evolvability law.
- Not `DEVELOPMENTAL_CROSS_FAMILY_TRANSFER_SUPPORTED`: T0/T1 do not reduce
  D2 acquisition cost versus a task-specific diagnosis learner.

## Reproduction

```sh
python -B -m unittest discover -s research/g7-lineage-d2-v2 -p 'test_*.py' -v
python -B research/g7-lineage-d2-v2/experiment.py \
  --out research/g7-lineage-d2-v2/RESULT.json \
  --transitions research/g7-lineage-d2-v2/transitions
```

[RESULT.json](RESULT.json) · [T0](transitions/T0.json) · [T1](transitions/T1.json) ·
[T2](transitions/T2.json) · [schema](schema.json) · v1 frozen
[RESULT.json](../g7-lineage-v1/RESULT.json)
