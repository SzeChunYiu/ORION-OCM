# G7 lineage D6 successor (microscope)

**Terminal:** `PHASED_COGNITIVE_DEVELOPMENT`

Owner: issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) G7 / #151.
Successor to [`research/g7-lineage-d5-v5/`](../g7-lineage-d5-v5/CORE.md), which stopped
at six earned transitions (`EMPTY→OCM_0`, `OCM_0→OCM_1`, `OCM_1→OCM_2`,
`OCM_2→OCM_3`, `OCM_3→OCM_4`, `OCM_4→OCM_5`) on lineage id
`orion-ocm-g7-lineage-v1:microscope-d0-d1` with D6 unrun.

This capsule **does not overwrite** v1, D2, D3, D4, or D5 `RESULT.json`. It
continues the **same lineage id** and actually runs a seventh earned
`DevelopmentTransitionV1` `OCM_5 → OCM_6` / D6 governed self-evolution: propose a
tiny plant repair, shadow-eval it on a clone, and require **external constitution
C** to adopt before live replace, persist, and restart.

Ideas from [`research/g6-intervention-lab-v1/`](../g6-intervention-lab-v1/CORE.md)
(raw traces, shadow quality, restart after adoption, C immutable, independent
scorer). **New files only.** Not a copy of that laboratory and not a retune of
its RESULT.

Not neural. Not Metamath. Not FLT. Historical M11 `g0 → g1 → g2 → g2` is **not**
relabeled. Not an `OperatorSpec` / `src/ocm` import. Not constitution mutation.

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

T4  OCM_3 → OCM_4 / D4 coding / tools / procedural
    RW_* exact replace-all string-rewrite on two-occurrence PQ→QP
    not REGEX/EVAL, not Metamath, not FLT, not M11 relabel
    T0/T1/T2/T3 retained; constitution C frozen

T5  OCM_4 → OCM_5 / D5 metacognition / learning-to-learn
    SEL_* per-cue validation utility table: try TRY_LEFT or TRY_RIGHT first
    not NEURAL/SGD/BACKPROP/LLM, not Metamath, not FLT, not M11 relabel
    T0/T1/T2/T3/T4 retained; constitution C frozen

T6  OCM_5 → OCM_6 / D6 governed self-evolution
    EVOL_* propose plant repair → shadow-eval → external C must adopt → persist → restart
    not M11/JUMP/MUTATE_C/G0/G1/G2/AUTOML/NEURAL, not Metamath, not FLT
    T0/T1/T2/T3/T4/T5 retained; constitution C frozen
```

## Why T6 is a new family, not a seventh polynomial trick

D0/D1 remain the polynomial grammar `g7.polynomial-total-arithmetic.v1`.
D2 remains `g7.diagnosis-probe-planning.v1`.
D3 remains `g7.hilbert-sk-lemma-introduction.v1`.
D4 remains `g7.exact-string-rewrite.v1`.
D5 remains `g7.method-selection-metacognition.v1`.

D6 is `g7.governed-plant-self-evolution.v1`: eight-cell plant, exactly two
contaminated cells, observable gauge (eight overlapping triple parities on a
ring, disjoint from D2's module syndrome). Train invents an invert-gauge repair
of learned width 2 by proposing from the observable and **shadow-evaluating**
on a clone. External C adopts only when shadow quality is 1. Held-out serving
uses the persisted procedure after restart. Replace-all works but costs more.
Propose-without-C never repairs. Fingerprints do not overlap polynomial,
diagnosis, Hilbert, rewrite, or metacognition families. The learned object is a
**named C-adopted invert-gauge repair**, not another MACRO fragment, probe
policy, CUT lemma, rewrite rule, SEL table, or neural net. C is not a writable
slot.

Conversion if the table cannot beat replace-all under external C on held-out
plants:

```text
CANNOT_CHECK_D6_SELF_EVOLUTION_NOT_EARNED
```

This successor's conversion, if T6 is not earned, is a named `CANNOT_CHECK`,
not a fake `OCM_6` and not a salt retune of T5 metacognition.

## Persist where earned

The serialised bundle always contains the thirteen G7 slots. After T6 the
earned contents are:

| slot | T0 | T1 | T2 | T3 | T4 | T5 | T6 |
|---|---|---|---|---|---|---|---|
| field state | seed atoms + admitted method | retained | plus probe-policy atom | plus CUT-lemma atom | plus rewrite atom | plus selection-policy atom | plus evolution-policy atom |
| learned methods | one macro | same macro | plus D2 probe policy | plus D3 CUT lemma | plus D4 rewrite | plus D5 utility table | plus D6 evolution policy |
| method schemas | macro-token schema | retained | plus probe-policy schema | plus CUT-lemma schema | plus rewrite schema | plus selection-policy schema | plus evolution-policy schema |
| imported donors | four taught primitives | retained | plus taught probe/replace operators | plus taught K/S/MP | plus taught substitute/scan | plus already-earned TRY_LEFT/TRY_RIGHT and cue-read | plus observe/propose/shadow-eval/external-C-adopt |
| applicability/scope | empty | degree-class restriction | retained | retained | retained | retained | retained |
| failure/counterexample knowledge | empty | `MACRO_AT_EMPTY_PREFIX` | retained | retained | retained | retained | retained |
| representations | taught coefficient normal form | retained | retained | plus Hilbert/SK representation | plus string-rewrite representation | plus utility-table representation | plus governed-plant representation |
| support/dependency | training SUPPORT edge | plus RESTRICTS edge | plus D2 SUPPORT edge | plus D3 SUPPORT edge | plus D4 SUPPORT edge | plus D5 SUPPORT edge | plus D6 SUPPORT edge |
| acquisition strategies | taught exact BFS | retained | retained | retained | retained | retained | retained |
| executive/metareasoning policy | serve+nogood; **do not rewrite C** | retained | family-gated serving; C frozen | Hilbert family gated; C frozen | rewrite family gated; C frozen | selection family gated; C frozen | plant family gated; C frozen |
| self-model | known competence list | updated stage | OCM_2 | OCM_3 | OCM_4 | OCM_5 | OCM_6; OCM_6 removed from unknown |
| self-change history | admit-macro | admit-failure-memory | admit-d2-probe-policy | admit-d3-cut-lemma | admit-d4-rewrite-rule | admit-d5-selection-policy | admit-d6-evolution-policy |
| resource history | T0 work units | T1 work units | T2 work units | T3 work units | T4 work units | T5 work units | T6 work units |

Restart is `persist` then a fresh `LineageStore.load` of the whole bundle.
A mismatched digest raises `DigestTamperError`. Rewriting constitution C
raises `ConstitutionMutationError` and does not persist.

## Comparators (every transition, including T6)

```text
CONTINUED_OCM
RESET_OCM
TASK_SPECIFIC_OCM
STRONG_ADAPTIVE_PARENT
```

T6 reset has its own store root, starts empty, and must re-acquire T0 then T1
then T2 then T3 then T4 then T5 then T6. Isolation failure is `IsolationError`.
Reset rediscovery is `INDEPENDENT_REDISCOVERY`. Continued reuses T0–T5 and
only pays D6 acquisition, so reset costs more.

Task-specific D6 learns the repair table without T0–T5. D0–D5 do **not**
cheapen D6 versus that learner; that is recorded, not claimed as
cross-family transfer. The ordinary C-adopted repair parent may **tie** the T6
mechanism (§12 absorption).

## Origin categories

| object | category |
|---|---|
| inc/dec/double/square, checker, BFS, D2 probes/replace, K/S/MP, substitute/scan, TRY_LEFT/TRY_RIGHT, cue-read, plant observe/propose/shadow-eval/external-C-adopt | `TAUGHT_IMPORTED` |
| T0 macro fragment | `LEARNED_COMPOSITION` |
| T1 degree-class failure/scope | `LEARNED_APPLICABILITY` |
| T2 greedy posterior-split probe policy | `LEARNED_COMPOSITION` |
| T3 CUT_* named lemma | `LEARNED_COMPOSITION` |
| T4 RW_* named rewrite | `LEARNED_COMPOSITION` |
| T5 SEL_* first-method utility table | `LEARNED_COMPOSITION` |
| T6 EVOL_* C-adopted plant-repair table | `LEARNED_COMPOSITION` |
| reset-arm re-acquired macro / policy / lemma / rewrite / table / evolution | `INDEPENDENT_REDISCOVERY` |

## What this does not claim

- Not Metamath N4 close, not FLT, not cross-domain transfer, not lifetime
  payback, not an OCM architecture residual over the ordinary parent.
- Not G3.1 independent two-macro composition, not G3.3 representation change,
  not production M11, not neural, not three-generation G6 laboratory reuse.
- `κ`, `Ω`, `χ` are microscope coordinates, not a G6 evolvability law.
- Not `DEVELOPMENTAL_CROSS_FAMILY_TRANSFER_SUPPORTED`: T0–T5 do not reduce
  D6 acquisition cost versus a task-specific plant-repair learner.
- Not unscoped `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`. MATH-1 / N4 on Metamath
  stays OPEN.

## Reproduction

```sh
python3 -B -m unittest discover -s research/g7-lineage-d6-v6 -p 'test_*.py' -v
python3 -B research/g7-lineage-d6-v6/experiment.py \
  --out research/g7-lineage-d6-v6/RESULT.json \
  --transitions research/g7-lineage-d6-v6/transitions
```

[RESULT.json](RESULT.json) · [T0](transitions/T0.json) · [T1](transitions/T1.json) ·
[T2](transitions/T2.json) · [T3](transitions/T3.json) · [T4](transitions/T4.json) ·
[T5](transitions/T5.json) · [T6](transitions/T6.json) · [schema](schema.json) · v1 frozen
[RESULT.json](../g7-lineage-v1/RESULT.json) · D2 frozen
[RESULT.json](../g7-lineage-d2-v2/RESULT.json) · D3 frozen
[RESULT.json](../g7-lineage-d3-v3/RESULT.json)
