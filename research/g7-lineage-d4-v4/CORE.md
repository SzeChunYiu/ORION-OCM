# G7 lineage D4 successor (microscope)

**Terminal:** `PHASED_COGNITIVE_DEVELOPMENT`

Owner: issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) G7 / #151.
Successor to [`research/g7-lineage-d3-v3/`](../g7-lineage-d3-v3/CORE.md), which stopped
at four earned transitions (`EMPTY→OCM_0`, `OCM_0→OCM_1`, `OCM_1→OCM_2`,
`OCM_2→OCM_3`) on lineage id `orion-ocm-g7-lineage-v1:microscope-d0-d1` with
D4–D6 unrun.

This capsule **does not overwrite** v1, D2, or D3 `RESULT.json`. It continues the
**same lineage id** and actually runs a fifth earned `DevelopmentTransitionV1`
`OCM_3 → OCM_4` / D4 coding/tools: tiny exact string-rewrite (replace-all `PQ→QP`).

Not Metamath. Not FLT. Historical M11 `g0 → g1 → g2 → g2` is **not** relabeled.
Not an `OperatorSpec` / `src/ocm` import.

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
```

Unrun (registered, not pretended): `OCM_5` D5 metacognition, `OCM_6` D6
governed self-evolution. D5 metacognition did not happen.

## Why T4 is a new family, not a fifth polynomial trick

D0/D1 remain the polynomial grammar `g7.polynomial-total-arithmetic.v1`.
D2 remains `g7.diagnosis-probe-planning.v1`.
D3 remains `g7.hilbert-sk-lemma-introduction.v1`.

D4 is `g7.exact-string-rewrite.v1`: source/target token strings over `{P,Q,R,S}`,
taught single-symbol substitute (depth 3 cannot finish two 2-gram edits), invent
a `RW_*` named rewrite that is not `REGEX`/`EVAL` and not a Hilbert `CUT_*`,
apply replace-all `PQ→QP` once, reuse on held-out atoms. Fingerprints do not
overlap the polynomial, diagnosis, or Hilbert families. The learned object is a
**named rewrite rule**, not another MACRO fragment, not a probe policy, and not
a CUT lemma.

Conversion if the rewrite cannot beat primitive substitute on held-out strings:

```text
CANNOT_CHECK_D4_REWRITE_NOT_EARNED
```

This successor's conversion, if T4 is not earned, is a named `CANNOT_CHECK`,
not a fake `OCM_4` and not a salt retune of T3 Hilbert.

## Persist where earned

The serialised bundle always contains the thirteen G7 slots. After T4 the
earned contents are:

| slot | T0 | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| field state | seed atoms + admitted method | retained | plus probe-policy atom | plus CUT-lemma atom | plus rewrite atom |
| learned methods | one macro | same macro | plus D2 probe policy | plus D3 CUT lemma | plus D4 rewrite |
| method schemas | macro-token schema | retained | plus probe-policy schema | plus CUT-lemma schema | plus rewrite schema |
| imported donors | four taught primitives | retained | plus taught probe/replace operators | plus taught K/S/MP | plus taught substitute/scan |
| applicability/scope | empty | degree-class restriction | retained | retained | retained |
| failure/counterexample knowledge | empty | `MACRO_AT_EMPTY_PREFIX` | retained | retained | retained |
| representations | taught coefficient normal form | retained | retained | plus Hilbert/SK representation | plus string-rewrite representation |
| support/dependency | training SUPPORT edge | plus RESTRICTS edge | plus D2 SUPPORT edge | plus D3 SUPPORT edge | plus D4 SUPPORT edge |
| acquisition strategies | taught exact BFS | retained | retained | retained | retained |
| executive/metareasoning policy | serve+nogood; **do not rewrite C** | retained | family-gated serving; C frozen | Hilbert family gated; C frozen | rewrite family gated; C frozen |
| self-model | known competence list | updated stage | OCM_2 | OCM_3 | OCM_4; OCM_4 removed from unknown |
| self-change history | admit-macro | admit-failure-memory | admit-d2-probe-policy | admit-d3-cut-lemma | admit-d4-rewrite-rule |
| resource history | T0 work units | T1 work units | T2 work units | T3 work units | T4 work units |

Restart is `persist` then a fresh `LineageStore.load` of the whole bundle.
A mismatched digest raises `DigestTamperError`. Rewriting constitution C
raises `ConstitutionMutationError` and does not persist.

## Comparators (every transition, including T4)

```text
CONTINUED_OCM
RESET_OCM
TASK_SPECIFIC_OCM
STRONG_ADAPTIVE_PARENT
```

T4 reset has its own store root, starts empty, and must re-acquire T0 then T1
then T2 then T3 then T4. Isolation failure is `IsolationError`. Reset
rediscovery is `INDEPENDENT_REDISCOVERY`. Continued reuses T0/T1/T2/T3 and
only pays D4 acquisition, so reset costs more.

Task-specific D4 learns the rewrite without T0/T1/T2/T3. D0/D1/D2/D3 do **not**
cheapen D4 versus that learner; that is recorded, not claimed as
cross-family transfer. The ordinary rewrite parent may **tie** the T4
mechanism (§12 absorption).

## Origin categories

| object | category |
|---|---|
| inc/dec/double/square, checker, BFS, D2 probes/replace, K/S/MP, substitute/scan | `TAUGHT_IMPORTED` |
| T0 macro fragment | `LEARNED_COMPOSITION` |
| T1 degree-class failure/scope | `LEARNED_APPLICABILITY` |
| T2 greedy posterior-split probe policy | `LEARNED_COMPOSITION` |
| T3 CUT_* named lemma | `LEARNED_COMPOSITION` |
| T4 RW_* named rewrite | `LEARNED_COMPOSITION` |
| reset-arm re-acquired macro / policy / lemma / rewrite | `INDEPENDENT_REDISCOVERY` |

## What this does not claim

- Not D5–D6, not Metamath N4 close, not FLT, not cross-domain transfer, not
  lifetime payback, not an OCM architecture residual over the ordinary parent.
- Not G3.1 independent two-macro composition, not G3.3 representation change,
  not G6 three-generation self-evolution, not production M11.
- `κ`, `Ω`, `χ` are microscope coordinates, not a G6 evolvability law.
- Not `DEVELOPMENTAL_CROSS_FAMILY_TRANSFER_SUPPORTED`: T0/T1/T2/T3 do not reduce
  D4 acquisition cost versus a task-specific rewrite learner.
- Not unscoped `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`. MATH-1 / N4 on Metamath
  stays OPEN.

## Reproduction

```sh
python3 -B -m unittest discover -s research/g7-lineage-d4-v4 -p 'test_*.py' -v
python3 -B research/g7-lineage-d4-v4/experiment.py \
  --out research/g7-lineage-d4-v4/RESULT.json \
  --transitions research/g7-lineage-d4-v4/transitions
```

[RESULT.json](RESULT.json) · [T0](transitions/T0.json) · [T1](transitions/T1.json) ·
[T2](transitions/T2.json) · [T3](transitions/T3.json) · [T4](transitions/T4.json) ·
[schema](schema.json) · v1 frozen [RESULT.json](../g7-lineage-v1/RESULT.json) ·
D2 frozen [RESULT.json](../g7-lineage-d2-v2/RESULT.json) · D3 frozen
[RESULT.json](../g7-lineage-d3-v3/RESULT.json)
