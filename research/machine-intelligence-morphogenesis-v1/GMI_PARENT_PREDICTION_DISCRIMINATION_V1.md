# GMI parent-prediction discrimination v1

Status: **PROSPECTIVE PARENT-SUBTRACTION / EXACT-GATE THEORY — NOT A GMI POSITIVE**

Date: 2026-09-12. Fresh-main base: `b7316ad210eb1649cb07bf62e59c044c7ca2e520`.

Refs: #377, #233, #373; `GMI_CLOSURE_GAP_LEDGER_V3.md`; `GMI_KNOWN_FORM_RECURSIVE_REGISTER_V2.md`; `GMI_E1_E3_THEORY_VALIDATION_GATE_V2.md`; `GMI_MECHANISM_NECESSITY_THEOREMS_V1.md`; `GMI_MECHANISM_WITNESS_REGISTRY_V1.md`.

## 0. Why this is the next gate

`GMI_CLOSURE_GAP_LEDGER_V3.md` ranks as B1 the need for a **distinct pre-outcome GMI prediction versus ordinary compression/resource parents**. That gate should be attacked before spending an independent protected split on a tournament that cannot, even in principle, distinguish GMI from its strongest admitted parents.

This document therefore asks a narrower hostile question:

> Do the currently registered **atomic** A2-A5 mechanism-pressure predictions contain any predictive content that is not already reproduced by a product of parent-owned sufficiency, incremental-computation, transaction-recovery and persistence results at the same finite semantic scope?

The answer at the frozen binary scope is allowed to be `PARENT_SUFFICIENT`. A negative here does not defeat the higher Track-B hypothesis; it moves the residual upward to joint interactions, cross-family invariance, developmental acquisition, resource-frontier prediction and ultimately neutral recovery.

## 1. Hostile review lenses

Four complementary lenses were used to choose and bound this attack.

1. **Formal CS / equivalence:** prove when two predictor classes are observationally indistinguishable and prevent a protected experiment from being called discriminative when one comparator contains the other.
2. **Information / resource theory:** distinguish semantic information lower bounds from an implementation preference; give ordinary resource-rational/metareasoning models first refusal for generic lifecycle selection.
3. **Systems / incremental computation:** parent-subtract locality, staging/rollback and history retention against incremental view maintenance, self-adjusting computation, optimistic transactions and persistent data structures.
4. **Scientific-validity / hostile review:** preserve the earlier VLC failure, keep protected C5 independent, and require a frozen prediction difference before protected outcomes are exposed.

No lens supplies a new positive by itself. Their consensus is a **discrimination precondition**, not a new morphology.

## 2. Parent subtraction at the atomic level

### A2 — developmental side information

`GMI_MECHANISM_NECESSITY_THEOREMS_V1.md` already states the exact injectivity requirement: if a serving compilation merges two developmental states that remain distinguishable by a legal future continuation, the realization must retain enough additional information to separate them. The mathematics is elementary sufficiency/injective recovery and conditional coding.

Track-B residual: not the necessity of side information itself, but whether a common GMI law predicts *when and how much* such information becomes lifecycle-frontier relevant across materially different morphology families.

### A3 — incremental-repair opportunity

Database incremental view maintenance computes changes to materialized views from changes to underlying relations rather than unconditionally recomputing from scratch. Self-adjusting computation explicitly tracks dependencies and propagates input changes through affected computation. These parents own the basic locality opportunity.

Primary anchors:

- Gupta, Mumick & Subrahmanian (1993), *Maintaining Views Incrementally*, SIGMOD, DOI `10.1145/170035.170066` (ACM record variants also expose `10.1145/170036.170066`).
- Acar (2005), *Self-adjusting Computation*; dependency tracking + change propagation.

Track-B residual: not “local changes can admit local recomputation,” but a prospective cross-family law that predicts the measured frontier value of that locality after all dependency-tracking, verification, search and maintenance costs are charged.

### A4 — rejection recoverability / speculative isolation

Optimistic transaction parents separate speculative work from final acceptance and retain enough information to survive conflict/rejection. Kung & Robinson (1981), *On Optimistic Methods for Concurrency Control*, ACM TODS 6(2), DOI `10.1145/319566.319567`, explicitly uses transaction backup in optimistic non-locking control.

Track-B residual: not “rejectable work needs recoverability,” but whether the same pre-outcome obligation coordinates predict this semantic mechanism across implementations and morphology families, with resource costs and verifier behavior included.

### A5 — lineage/history persistence

Persistent-data-structure parents explicitly preserve access to old versions after updates. Driscoll, Sarnak, Sleator & Tarjan (1989), *Making Data Structures Persistent*, JCSS 38(1), DOI `10.1016/0022-0000(89)90034-2`, is direct parent territory.

Track-B residual: not “history queries require retained historical distinctions,” but a transferable morphology/resource law, and eventually blind recovery from a neutral basis.

### Generic lifecycle selection

Russell & Wefald (1991), *Principles of Metareasoning*, and later resource-rational work already frame computation choice in terms of benefits versus computational resource costs. Therefore “choose the mechanism with lower complete lifecycle cost” is not itself a Track-B novelty. The residual must be a **specific pre-outcome predictive structure** not obtainable by simply granting the parent comparator the same descriptors and an unrestricted resource-response mapping.

## 3. PPD-1 — predictor-containment non-discrimination theorem [P1]

Let `X` be a finite or measurable pre-outcome descriptor space, `Y` an outcome/prediction space, and let

`g : X -> Y`

be a frozen GMI predictor. Let `P` be the admitted parent predictor class.

If

`g in P`,

then no protected outcome set evaluated only through the predictions can establish a **GMI-specific predictive residual** against `P`: the parent can choose `p = g`, producing identical predictions on every `x` and therefore identical loss under every outcome-dependent scoring rule that scores equal predictions equally.

### Proof

Because `g in P`, choose `p = g`. For all `x`, `p(x)=g(x)`. Hence for every observed outcome `y` and every scoring function `L(prediction,y)`,

`L(p(x),y) = L(g(x),y)`.

No outcome can distinguish the labels “GMI” and “parent” for this predictor pair. QED.

### Consequence

A protected tournament is scientifically discriminative only after at least one of the following is frozen:

- a witness cell where `g_GMI(x)` differs from **every** admitted matched-information parent prediction;
- a narrower parent class justified independently of the protected outcome;
- a stronger object than point prediction, such as an intervention-response law, uncertainty set, cross-family invariance or resource-bound relation that the parent class does not contain.

Weakening the parent after seeing protected outcomes is forbidden by #373.

## 4. PPD-2 — parent-product sufficiency for atomic mechanism predicates [P1 + P2 calibration]

Let the frozen atomic GMI vector be

`g(x) = (A2(x), A3(x), A4(x), A5(x))`.

Suppose for each coordinate there exists an admitted parent predictor `p_k` with

`p_k(x)=A_k(x)`

for every registered cell. Then the direct product predictor

`p(x) = (p_2(x),p_3(x),p_4(x),p_5(x))`

is an admitted composition of parent-owned atomic rules and satisfies `p(x)=g(x)` everywhere.

Therefore the atomic vector has no residual under this product comparator.

This theorem says nothing about **joint interaction terms** that are absent from the product, and nothing about whether any concrete parent implementation jointly attains the full lifecycle frontier. Those are exactly the higher residuals that B1 must now test.

## 5. Frozen exact scope

The companion `GMI_PARENT_PREDICTION_DISCRIMINATION_FREEZE_V1.json` freezes nine independent binary variables, hence 512 truth-table cells:

```text
local_update_cone
local_query_cone
rejectable_update
incumbent_must_remain_available
historical_query_required
serving_compilation_aliases_dev_states
aliased_dev_distinction_future_relevant
high_update_rate
high_reuse
```

The four GMI atomic predicates are prospectively frozen as:

```text
A2 side information required
  = serving_compilation_aliases_dev_states
    AND aliased_dev_distinction_future_relevant

A3 incremental-repair opportunity
  = local_update_cone

A4 rejection recoverability required
  = rejectable_update
    AND incumbent_must_remain_available

A5 lineage persistence required
  = historical_query_required
```

The matched parent-product rules are frozen to the same semantic predicates for the reasons above.

This is deliberately a **semantic pressure/opportunity** scope. It does not assert that A3 is always resource-optimal when the cone is local, that a particular A4 encoding is best, or that A2/A5 require separate physical modules.

## 6. Positive-control hostiles

A checker that only reports equality is too easy to mistrust. Four deliberately wrong shortcut predictors are frozen before execution:

```text
A5_drift_only_proxy = high_update_rate
A3_query_locality_proxy = local_query_cone
A4_update_rate_proxy = high_update_rate
A2_alias_only_proxy = serving_compilation_aliases_dev_states
```

Expected disagreement counts over the 512 independent cells are frozen as:

```text
A5 drift-only       256
A3 query proxy      256
A4 update-rate      256
A2 alias-only       128
```

Any miss invalidates the exact calibration.

## 7. Scientific decision rule

If the exact parent product has zero mismatches while all positive controls hit their predeclared mismatch counts, record:

`ATOMIC_MECHANISM_PREDICTIONS_PARENT_PRODUCT_SUFFICIENT_AT_REGISTERED_BINARY_SCOPE`

Do **not** retune the atomic rules to manufacture novelty.

If any parent-product mismatch appears, preserve the witness and inspect whether the assumed parent reduction is wrong before making any positive claim.

## 8. What B1 must now contain to be worth a protected C5 run

B1 remains open after an atomic parent-sufficient result. The next admissible object must be a **justified residual above the product**, for example one of:

- a quantitatively frozen A3×A4, A1×A3, or other mechanism interaction that strong parents do not already imply;
- a common intervention-response coefficient or monotonic relation that must hold across held-out morphology families while native parent models predict a materially different response;
- a resource-bound relation coupling semantic quotient burden, update geometry, verifier/rejectability and reuse that cannot be represented by the admitted parent class without adding the same GMI structure;
- a developmental-acquisition prediction that distinguishes which mechanism will be *found* from a neutral grammar, not merely which mechanism would be useful if supplied.

A candidate residual is not accepted merely because it is more complicated. Before independent protected generation it must satisfy:

```text
1. strongest-parent first refusal;
2. same pre-outcome information contract for GMI and parents;
3. at least one frozen witness where predictions differ;
4. explicit reason the parent class is not allowed to emulate the GMI relation;
5. numeric prediction / interval or intervention direction frozen before outcomes;
6. negative twins and claim-killing outcomes frozen;
7. independent C5 generator/seed prerequisite preserved.
```

If no scientifically justified relation survives these conditions, the correct B1 terminal is a broader `PARENT_THEORY_SUFFICIENT_<scope>`, not benchmark shopping.

## 9. Relationship to the ultimate Track-B question

This attack intentionally moves **away** from premature “new morphology” claims. The ultimate question still requires all of the following, none of which is established here:

```text
minimal/equivalent adaptive generating basis
resource-bounded derivation of materially different known morphologies
ecology/resource/verifier phase prediction
prospective blind recovery
non-parent-equivalent morphology residual
replication across encodings/searches/ecologies
```

An atomic parent-sufficient result is useful because it prevents later morphology recovery from being credited to GMI for mechanisms already predicted by mature systems/information parents.

## 10. Claim ceiling

Allowed after a green exact calibration:

> At this registered binary semantic-pressure scope, the current A2-A5 atomic GMI predictions are exactly reproduced by a product of parent-owned rules. Therefore those atomics are not a distinct GMI predictive residual and should not consume protected evidence as if they were.

Not allowed:

```text
GMI disproven
GMI phase law established
cross-paradigm basis established
VLC/RQM/VRQM novel morphology established
neutral morphology recovery established
known-form closure established
general machine intelligence theory established
```

The higher B1 gate remains open until a non-parent-product prospective prediction is frozen and independently tested.
