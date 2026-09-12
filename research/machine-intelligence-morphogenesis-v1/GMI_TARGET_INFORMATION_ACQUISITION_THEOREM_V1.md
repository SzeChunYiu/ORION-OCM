# GMI target-information acquisition theorem v1

Status: **FORMAL CORRECTION AFTER K4 DEVELOPMENT FAILURE**

Date: 2026-09-12.

Motivation: the K4 development sweep recovered zero frozen property vectors. A principal failure mode is that the evaluator can award semantic adequacy to a hard-coded realization without representing **how target-specific information entered the machine**. A fixed algorithm may legitimately solve a query when the query contains the whole instance; a fixed answer may not legitimately know a protected target drawn after the machine was frozen. The current ten-axis vector does not distinguish those cases.

This document adds no historical architecture name and does not repair any failed K4 split. It identifies the missing causal variable and gives a fresh successor condition.

## 1. Information-source normal form

Let a protected world variable be `W`, drawn only after the pre-world machine design `P` is frozen.

A realization may receive information about `W` through declared channels:

- `D`: developmental evidence / feedback before serving;
- `Q`: the serve-time query or problem instance;
- `A`: declared external authority available at serve time;
- `R`: private randomness independent of `W`.

The served answer is

\[
Y = F(P,D,Q,A,R).
\]

The pre-world design constitution requires

\[
I(W;P)=0,
\]

unless target-specific information included in `P` is explicitly charged as post-draw development/external intervention rather than treated as a free prior.

The missing property coordinate is therefore

```text
target_information_source
```

with a set-valued measurement such as

```text
GENERAL_RULE_ONLY
DEVELOPMENT
QUERY
EXTERNAL_AUTHORITY
DEVELOPMENT+QUERY
DEVELOPMENT+EXTERNAL_AUTHORITY
QUERY+EXTERNAL_AUTHORITY
MIXED
```

The coordinate is measured by intervention: remove or remint each channel and determine which protected distinctions collapse. It is not a historical architecture label.

## 2. Theorem TI-1 — no free protected target information

Let `W` be uniform on a finite set of `M` protected worlds. Assume `P` and `R` are independent of `W`. Suppose the final response permits an estimator `What` whose world-identification error is at most `epsilon` from the machine's accessible semantic state `(Z,Q,A)`, where

\[
Z = G(P,D,R).
\]

Then Fano's inequality gives

\[
\boxed{
I(W;Z,Q,A)
\ge
\log_2 M
-h_2(\epsilon)
-\epsilon\log_2(M-1)
}.
\]

For exact identification, `epsilon=0`, so

\[
I(W;Z,Q,A)\ge\log_2 M.
\]

Because `P` and `R` are independent of `W`, target information must arrive through the registered development/query/authority channels. Randomness alone cannot supply it.

### Consequence

A fixed answer with no `D`, no informative `Q`, and no informative `A` has zero mutual information with a post-freeze `W`. Under a uniform `M`-world exact-identification obligation its maximum success probability is at most

\[
\boxed{1/M}.
\]

Therefore a benchmark that grants such a fixed realization perfect semantic score has leaked protected target information or has defined a degenerate one-world obligation.

## 3. Theorem TI-2 — conditional acquisition burden

If the serve-time query and external authority already reveal information about the protected world, the internal developmental state need only carry the residual distinctions.

For exact identification,

\[
\boxed{
I(W;Z\mid Q,A)
\ge
H(W\mid Q,A)
}
\]

whenever `(Z,Q,A)` determines `W` exactly.

More generally, under a distortion constitution the appropriate lower bound is the conditional semantic rate-distortion quantity

\[
R_{W\mid Q,A}(D).
\]

This is the information-theoretic bridge among:

- learned internal state: residual information enters through `D`;
- exact query-time algorithms: the instance may be carried primarily by `Q`;
- retrieval/authority systems: volatile distinctions may arrive through `A`;
- hybrids: the residual is shared across channels.

## 4. Theorem TI-3 — target-specific description is not free prior structure

Suppose a code `C(W)` is inserted into the machine **after** the protected world is selected and permits exact identification of `W` among `M` equiprobable worlds. Any uniquely decodable code satisfies

\[
\mathbb E[|C(W)|]\ge H(W)=\log_2 M.
\]

Therefore a hard-coded post-draw table/program/parameter vector must be charged to development or external intervention by its target-specific information content. It may not be counted as a fixed pre-world morphology at zero acquisition burden.

This does **not** penalize a general solver compiled before the world draw. A general SAT solver, search routine, interpreter, or algebraic procedure may remain fixed if the problem instance itself arrives in `Q`; its target-information source is `QUERY`, not hidden target-specific description.

## 5. Matched examples

### Fixed-answer negative

`W` is a uniformly random `k`-bit target, query is constant, no development evidence is supplied.

Any fixed answer succeeds with probability exactly at most

\[
2^{-k}.
\]

### Query-complete solver

`Q=W`. A fixed identity/general solver can be exact with no developmental state. This is legitimate because all target information arrives through `Q`.

### Development-complete learner

`D=W`, query is constant. Exact response is possible after development because `D` carries all `k` protected bits.

### Split information

`Q` reveals `r` independent bits and `D` reveals `d` other independent bits of a `k`-bit protected world. Exact reconstruction is possible iff all `k` distinctions are covered; when `r+d<k`, at least `2^{k-r-d}` worlds remain aliased.

## 6. Correction to K4 interpretation

The 264-cell K4 V5 development sweep remains a valid falsification of its **own** registered frontier rule: its abstract semantic evaluator found cheaper non-target forms or nulls in 228 cells and no frozen target-vector recovery.

It is **not** evidence that known forms are intrinsically wrong or unnecessary. The experiment confounds morphology with free target knowledge because semantic capability is assigned from form motifs rather than acquired on a concrete post-freeze target.

Accordingly:

```text
K4_PROPERTY_PREDICTION_GREEN_AT_REGISTERED_OLD_SCOPE = FALSE
OLD_K4_STATIC_SEMANTIC_EVALUATOR_RETIRED_FOR_KNOWN_FORM_CLOSURE
```

The failure is preserved. It is not repaired on the same split.

## 7. Fresh successor requirements

A successor known-form rediscovery benchmark must enforce all of the following before any result:

1. **mechanism freeze before target draw** — candidate grammar and generic development law cannot contain protected target parameters;
2. **fresh protected world draw** after the freeze;
3. **explicit information channels** `D,Q,A`;
4. **actual task execution**, not a capability rubric, to determine admissibility;
5. **target-information accounting** — any target-specific description injected after the draw is charged as development/external intervention;
6. **development-dependence nulls** — fixed answer, fixed table, fixed program and other inert controls are evaluated with only the information they are legally given;
7. **held-out serving** on distinctions not used to select the final state whenever the family claims learning/generalization;
8. **channel ablations** to measure `target_information_source`;
9. preserve the old K4 failures permanently;
10. freeze all predictions and scoring before the new protected draw.

## 8. Claim ceiling

This theorem closes the missing information-provenance atom and explains why a fixed solver can be legitimate while a fixed protected answer is not.

It does **not** make the known-form terminal green. A fresh post-target-draw developmental benchmark is still required.

`KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE = FALSE`
