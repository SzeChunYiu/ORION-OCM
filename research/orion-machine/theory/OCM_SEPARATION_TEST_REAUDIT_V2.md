# Separation claim — re-audit for freezability against the registered non-rectangular class

**Claim status: `NOT_ESTABLISHED`.** **Test status: `NOT_FROZEN__CONDITION_1_UNSATISFIABLE_CLASS_INDEPENDENT`.**
Nothing was run. No arm exists.

Date: 2026-09-04 · Umbrella: #194 · Execution master: #197 · Predecessor: `OCM_SEPARATION_TEST_DESIGN_V1.md`
(audit `FAILED_REACHABILITY_AND_COMPARATOR_MATCHING`) · Machine-readable twin: `OCM_SEPARATION_TEST_REAUDIT_V2.json`

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** The V1 design listed five conditions a freezable
test would need and named condition (1) — a registered non-rectangular natural class — as the
missing object. That object now exists (`OCM_NONRECTANGULAR_CLASS_V1.md`: `VSW(SINGLETONS_5)`,
non-rectangular, non-decomposable, certified `I = 1`). This re-audit asks whether the five
conditions now hold. They do not, and the reason is independent of the class.

## 1. Condition (1) as written, and what it asks for

> a registered non-rectangular natural class on which a **non-cardinality lower bound separates
> learners at equal information**

The class half is met. The bound half cannot be met by any class:

**Theorem N2 (class-independence of the reachability obstruction).** Let `Omega` be any finite
lifecycle class, `O` any observation interface, and `π`, `α` two zero-error learners given the same
transcript `O(w)` and the same oracle access. (i) The set of target coordinates each can answer at
observation `o` is the same — those constant on the fibre `O^{-1}(o)` (fibre criterion, lane #200
Thm B). (ii) If `α` ranges over all programs of the same resource class as `π`, then `α` may be `π`,
so no verdict `π PASS ∧ α FAIL` is reachable. (iii) If `α` ranges over a proper sub-class that
excludes `π`'s strategy, the test measures the restriction, not the class of problems.

*Proof.* (i) is the fibre criterion applied to each learner. (ii) is the definition of "same
resource class". (iii): the only difference between the arms is then the sub-class definition. ∎

*Parents.* Mitchell 1980 (*The need for biases in learning generalizations*): what a learner can do
beyond the data is its bias, and bias is information; Wolpert 1996 (no-free-lunch). `PARENT_OWNED`.

So condition (1) conflates two different objects: a **class property** (non-rectangularity, now
satisfied) and a **comparator restriction** (what `α` may not do). No class property can supply the
second. The V1 audit's two failure routes are exactly (ii) and (iii): `VACUOUS_CONTRAST` and
`HANDICAPPED_COMPARATOR`.

## 2. The five conditions against `VSW(SINGLETONS_5)`

| # | condition (V1 §5) | state against the registered class |
|---|---|---|
| 1 | non-rectangular natural class with a non-cardinality lower bound separating learners at equal information | class: **met**. bound: **unsatisfiable** for unrestricted `α` (N2 ii); for restricted `α` it exists but is a restriction result (N2 iii) — see §3 |
| 2 | bounded, matched exposure and matched interface; `α` = capacity-matched untyped learner of the same interface | statable: both arms read the same certified examples, both may issue membership and liveness queries; under (2) the arms are the same learner up to bias (N2) |
| 3 | pre-registered margin derived from the bound in (1) | none for the separation; **one query** is derivable for the restricted-comparator frontier of §3 (`I = 1`, certified) |
| 4 | planted controls: laundering `π` fails E1; `α` given closure certificates passes E1 | plantable on the substrate (S1 laundering; S3 closure) — not the blocker |
| 5 | endpoint dynamic range on the substrate | at matched interface both arms answer every coordinate (N2 i): **no dynamic range** — `DEGENERATE_PROBE_STATISTIC` binds as in V1 |

**Result: NOT_FROZEN.** The class was not the blocker; the comparator definition is, for every class.

## 3. The one honest reading with a margin — and what it is not

There is a registered, certified, one-query separation on `VSW(SINGLETONS_5)`:

> at equal information, any learner that determines the concept **before** issuing a liveness
> query needs 9 queries; the joint learner needs 8.

This is a *restricted-comparator frontier*, of lane #202's kind: the restriction is an **ordering
constraint** ("behaviour first"), and it is a fair description of what "approximates outputs from
large-scale exposure and then must reconstruct warrant" does — but it is a restriction, named as
such, not the directive's claim, and it is owned by Angluin 1988 (subset queries are strictly more
powerful than membership queries on singletons). It could be frozen as a frontier study with the
comparator manifest "B-first strategies" and margin 1; it cannot be frozen as the separation, and
freezing it would not establish the directive's claim. It is recorded here so that a later reader
does not mistake it for one.

## 4. Failure-ledger audit (delta from V1)

All 26 retained root-ledger classes were re-read. Bindings unchanged from V1
(`STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE`, `HANDICAPPED_COMPARATOR`, `VACUOUS_CONTRAST`,
`DONOR_PRODUCT_TIE`, `NONIDENTIFIABLE`, `FORECLOSED_FAILURE_MODE`, `DEGENERATE_PROBE_STATISTIC`
bind; the run-time, custody and literature classes remain n/a — nothing was run). One addition to
the OCM ledger: `PRESENTATION_DEPENDENT_OBSTRUCTION` — the V1 clause "until (1) exists" named a
class property as the blocker when the blocker was the comparator definition; the same shape as the
lane-200 obstruction naming rectangularity when the content was decomposability.

## 5. Terminal and non-consequences

```text
SEPARATION_CLAIM = NOT_ESTABLISHED
SEPARATION_TEST  = NOT_FROZEN__CONDITION_1_UNSATISFIABLE_CLASS_INDEPENDENT (Theorem N2)
FREEZABLE_ONLY_AS = restricted-comparator frontier (ordering restriction; margin 1 on VSW(SINGLETONS_5); Angluin 1988) — not the claim
```

Nothing here shows the directive's claim false. It shows the claim is not a separation between
learners at equal information for *any* problem class, and that what remains testable is a
resource frontier against a named restriction. No training, protected evaluation, language,
quantum, superiority or novelty claim is authorised; no checkbox in #197 is closed.
