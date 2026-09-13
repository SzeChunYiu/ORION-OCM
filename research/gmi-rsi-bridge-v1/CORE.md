# GMI ↔ RSI recursive-evolvability bridge v1

**Terminal:** `SCOPED_RECURSIVE_EVOLVABILITY_BRIDGE_LEDGER_TERMINAL_WITH_INHERITED_AND_OPEN_EMPIRICAL_NONCLAIMS`

**Claim authority:** formal/operational bridge + deterministic synthetic protocol tests.  **No claim of empirical ORION R3/R4/R5, no claim that G6 is positively closed, no claim that G7 D6 has run, no claim of open-ended RSI, recursive acceleration, or intelligence explosion.**

## Result

This capsule closes the conceptual interface between GMI developmental evolvability and the modern RSI literature by making the missing recursive object explicit:

\[
X_t=(M_t,D_t,A_t;C),\qquad X_{t+1}=\mathcal R_C(X_t,e_t).
\]

G6 asks whether a governed machine can make useful verified changes to itself.  The RSI bridge asks the higher-order question: **can the machinery that generates future improvements (`D`) itself be diagnosed, changed, evaluated and inherited?**  G7 supplies the lineage vessel needed to show that such meta-changes actually persist.

The integration spine is therefore

```text
G1–G5 competence
    ↓
G6 developmental evolvability
    ↓
R3 recursive evolvability: verified improvement of D itself
    ↓
G7 registered lineage / heredity
    ↓
R4 heritable recursive development
```

R3 feeds back into G6 because a better `D` is intended to improve future evolvability.  This feedback is measured by descendant outcomes, not inferred from self-reference alone.

## What is newly closed

1. **Placement:** RSI is a recursive closure of developmental evolvability, not an unrelated G8 capability.
2. **Self boundary:** every claim registers modification surface `Σ`; external constitution `C` is not silently absorbed into the mutable self.
3. **Recursion criterion:** repeated self-editing under a fixed updater is R2 at most.  R3 requires an earned intervention on `D`.
4. **No infinite module regress:** `D` is addressable state inside `X`; the transition process can operate on the representation of the process that generates later transitions.
5. **Meta-evolvability:** the existing `(κ, Ω, χ)` triad applies recursively to `D` as `(κ_D, Ω_D, χ_D)`.
6. **Performance/metaproductivity separation:** current quality is not a proxy theorem for descendant-production value.
7. **Causal admission:** same root, held-out ecology, matched resource vectors, frozen-`D` comparator, frozen/shadow evaluator and no hidden human intervention are required for R3.
8. **Heredity:** R4 requires the changed `D` state to persist into a later registered descendant.
9. **Stepping stones:** a temporarily worse intermediate may be valid if preregistered descendant evidence is better; monotone present-score selection is not assumed.
10. **Evaluator reflexivity:** a mutable judge cannot certify its own improvement without a protected shadow/external reference.
11. **RSI/acceleration separation:** R3/R4 does not imply recursive acceleration.
12. **R5 discipline:** finite transfer/generations never get renamed general/open-ended RSI.
13. **Recursive gap stopping rule:** every D0–D14 family is decomposed into definition/mechanism/observable/test/counterexample/boundary leaves; every leaf has a terminal disposition in `CLAIM_LEDGER.json`.

## What remains inherited or empirically open

The bridge intentionally cannot manufacture evidence absent upstream:

- G6 still lacks source-bound raw intervention transcripts, a third nontrivial earned self-change, and real self-change estimates of `κ`, `Ω`, and calibrated `χ`.
- G7 currently demonstrates only its earned early lineage transitions; its governed self-evolution stage remains unrun.
- General cross-domain improvement competence and open-endedness remain R5 empirical/theoretical nonclaims.

These are not dangling gaps: they are explicit terminal negatives/nonclaims with reopen conditions.  Positive promotion requires new evidence, not document edits.

## Falsification / downgrade rules

Downgrade an R3/R4 claim to R2 or below if any of the following is true:

- `D` never changed, or the alleged change was cosmetic/not executed by descendants;
- the mutable and frozen arms differ materially in compute, data, evaluator effort or human engineering;
- a human supplied an unregistered intervention/root-cause label;
- the evaluator proxy changed without an external frozen/shadow evaluator;
- the same benchmark used to choose edits is the only evidence of descendant advantage;
- lineage/provenance cannot bind the meta-change to the descendant;
- the candidate changes its own admission authority in a way not independently governed by `C`;
- present task score is substituted for descendant metaproductivity;
- a finite run is relabelled “open-ended”.

## Executable witness

`test_protocol.py` hostile-tests the definitions.  The deterministic synthetic assay contains:

- `FROZEN_D`: matched fixed-updater baseline;
- `MUTABLE_D`: a temporary regression followed by better descendants, with `D1` inherited;
- `FIXED_D_SELF_EDIT`: repeated persistent self-edits that correctly stop at R2;
- `EVALUATOR_GAMING`: internal score rises while frozen-shadow evidence does not, therefore R3 is refused;
- `EXTRA_COMPUTE`: stronger descendants under a mismatched resource budget, therefore causal R3 comparison is refused.

The witness validates protocol semantics only.  It is not evidence that ORION itself is recursively self-improving.

## Files

- `DEFINITIONS.md` — formal objects and R0–R5 claim grammar
- `PARENTS.md` — donor/result boundary
- `GAP_GRAPH.md` / `CLAIM_LEDGER.json` — recursive D0–D14 closure ledger
- `MODIFICATION_SURFACES.md` — self-boundary registration
- `METAPRODUCTIVITY.md` — descendant metric and GMI resource-profile compatibility
- `RSI_ASSAY.md` — causal experiment contract
- `COUNTEREXAMPLES.md` — hostile constructions
- `UNKNOWN.md` — inherited/open empirical obligations
- `INTEGRATION_MAP.md` — exact G6/G7/Grand-GMI interfaces
- `model.py`, `experiment.py`, `test_protocol.py`, `RESULT.json` — executable protocol microscope
