# G7 lineage D3 successor (microscope)

**Terminal:** `PHASED_COGNITIVE_DEVELOPMENT`

Owner: issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) G7 / #151.
Successor to [`research/g7-lineage-d2-v2/`](../g7-lineage-d2-v2/CORE.md), which stopped
at three earned transitions (`EMPTY→OCM_0`, `OCM_0→OCM_1`, `OCM_1→OCM_2`) on lineage id
`orion-ocm-g7-lineage-v1:microscope-d0-d1` with D3–D6 unrun.

This capsule **does not overwrite** v1 or D2 `RESULT.json`. It continues the **same
lineage id** and actually runs a fourth earned `DevelopmentTransitionV1`
`OCM_2 → OCM_3` / D3 formal mathematics: miniature Hilbert/SK named-lemma
introduction from [`research/math-n4-subgoal-v2/`](../math-n4-subgoal-v2/CORE.md).

Not Metamath. Not FLT. Historical M11 `g0 → g1 → g2 → g2` is **not** relabeled.

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

T3  OCM_2 → OCM_3 / D3 formal mathematics / controlled language
    CUT_* lemma invented on compose-second Hilbert/SK goals
    not PREFIX/SWAP, not Metamath, not FLT
    T0/T1/T2 retained; constitution C frozen
```

Unrun (registered, not pretended): `OCM_4` D4 coding/tools, `OCM_5` D5
metacognition, `OCM_6` D6 governed self-evolution. D4 coding did not happen.

## Why T3 is a new family, not a fourth polynomial trick

D0/D1 remain the polynomial grammar `g7.polynomial-total-arithmetic.v1`.
D2 remains `g7.diagnosis-probe-planning.v1`.

D3 is `g7.hilbert-sk-lemma-introduction.v1`: positive implicational Hilbert
calculus (K, S, MP), combinatory SK terms as proofs, invent a `CUT_*` named
lemma that is not the goal and not a frozen `PREFIX`/`SWAP` identity, finish
compose-second, reuse on held-out atoms. Fingerprints do not overlap the
polynomial or diagnosis families. The learned object is a **named lemma**,
not another MACRO fragment, not a probe policy, and not a task-id blacklist.

Conversion if the CUT lemma cannot beat primitive K/S on held-out theorems:

```text
CANNOT_CHECK_D3_LEMMA_INTRODUCTION_NOT_EARNED
```

This successor's conversion, if T3 is not earned, is a named `CANNOT_CHECK`,
not a fake `OCM_3` and not a salt retune of T2 diagnosis.

## Persist where earned

The serialised bundle always contains the thirteen G7 slots. After T3 the
earned contents are:

| slot | T0 | T1 | T2 | T3 |
|---|---|---|---|---|
| field state | seed atoms + admitted method | retained | plus probe-policy atom | plus CUT-lemma atom |
| learned methods | one macro | same macro | plus D2 probe policy | plus D3 CUT lemma |
| method schemas | macro-token schema | retained | plus probe-policy schema | plus CUT-lemma schema |
| imported donors | four taught primitives | retained | plus taught probe/replace operators | plus taught K/S/MP |
| applicability/scope | empty | degree-class restriction | retained | retained |
| failure/counterexample knowledge | empty | `MACRO_AT_EMPTY_PREFIX` | retained | retained |
| representations | taught coefficient normal form | retained | retained | plus Hilbert/SK representation |
| support/dependency | training SUPPORT edge | plus RESTRICTS edge | plus D2 SUPPORT edge | plus D3 SUPPORT edge |
| acquisition strategies | taught exact BFS | retained | retained | retained |
| executive/metareasoning policy | serve+nogood; **do not rewrite C** | retained | family-gated serving; C frozen | Hilbert family gated; C frozen |
| self-model | known competence list | updated stage | OCM_2 | OCM_3; OCM_3 removed from unknown |
| self-change history | admit-macro | admit-failure-memory | admit-d2-probe-policy | admit-d3-cut-lemma |
| resource history | T0 work units | T1 work units | T2 work units | T3 work units |

Restart is `persist` then a fresh `LineageStore.load` of the whole bundle.
A mismatched digest raises `DigestTamperError`. Rewriting constitution C
raises `ConstitutionMutationError` and does not persist.

## Comparators (every transition, including T3)

```text
CONTINUED_OCM
RESET_OCM
TASK_SPECIFIC_OCM
STRONG_ADAPTIVE_PARENT
```

T3 reset has its own store root, starts empty, and must re-acquire T0 then T1
then T2 then T3. Isolation failure is `IsolationError`. Reset rediscovery is
`INDEPENDENT_REDISCOVERY`. Continued reuses T0/T1/T2 and only pays D3
acquisition, so reset costs more.

Task-specific D3 learns the CUT lemma without T0/T1/T2. D0/D1/D2 do **not**
cheapen D3 versus that learner; that is recorded, not claimed as
cross-family transfer. The ordinary CUT-lemma parent may **tie** the T3
mechanism (§12 absorption).

## Origin categories

| object | category |
|---|---|
| inc/dec/double/square, checker, BFS, D2 probes/replace, K/S/MP | `TAUGHT_IMPORTED` |
| T0 macro fragment | `LEARNED_COMPOSITION` |
| T1 degree-class failure/scope | `LEARNED_APPLICABILITY` |
| T2 greedy posterior-split probe policy | `LEARNED_COMPOSITION` |
| T3 CUT_* named lemma | `LEARNED_COMPOSITION` |
| reset-arm re-acquired macro / policy / lemma | `INDEPENDENT_REDISCOVERY` |

## What this does not claim

- Not D4–D6, not Metamath N4 close, not FLT, not cross-domain transfer, not
  lifetime payback, not an OCM architecture residual over the ordinary parent.
- Not G3.1 independent two-macro composition, not G3.3 representation change,
  not G6 three-generation self-evolution, not production M11.
- `κ`, `Ω`, `χ` are microscope coordinates, not a G6 evolvability law.
- Not `DEVELOPMENTAL_CROSS_FAMILY_TRANSFER_SUPPORTED`: T0/T1/T2 do not reduce
  D3 acquisition cost versus a task-specific Hilbert learner.
- Not unscoped `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`. MATH-1 / N4 on Metamath
  stays OPEN.

## Reproduction

```sh
python -B -m unittest discover -s research/g7-lineage-d3-v3 -p 'test_*.py' -v
python -B research/g7-lineage-d3-v3/experiment.py \
  --out research/g7-lineage-d3-v3/RESULT.json \
  --transitions research/g7-lineage-d3-v3/transitions
```

[RESULT.json](RESULT.json) · [T0](transitions/T0.json) · [T1](transitions/T1.json) ·
[T2](transitions/T2.json) · [T3](transitions/T3.json) · [schema](schema.json) ·
v1 frozen [RESULT.json](../g7-lineage-v1/RESULT.json) · D2 frozen
[RESULT.json](../g7-lineage-d2-v2/RESULT.json)
