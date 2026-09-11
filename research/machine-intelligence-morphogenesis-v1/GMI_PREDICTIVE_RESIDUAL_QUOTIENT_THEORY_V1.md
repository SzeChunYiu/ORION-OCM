# GMI Predictive Residual Quotient Theory v1

Status: **FORMAL SYNTHESIS / PROSPECTIVE MORPHOLOGY DERIVATION — NOT AN ESTABLISHED NEW-FORM CLAIM**

Status date: 2026-09-12.

Refs:

- `GMI_THEORY_V1.md`
- `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`
- `GMI_NEURAL_PREDICTION_TO_INTELLIGENCE_THEOREMS_V1.md`
- `GMI_NEURAL_MACHINE_INTELLIGENCE_DERIVATION_V1.md`
- `GMI_MECHANISM_NECESSITY_THEOREMS_V1.md`
- `GMI_CAUSAL_MECHANISM_PHASE_THEORY_V1.md`

This document asks a narrower question than “why can predictive neural networks be intelligent?”

> If a learned predictive state already preserves most—but not all—distinctions required by a target cognitive obligation, what additional state is *necessarily* required, and what realization morphology should become favorable?

The answer produces a quantitative property-first candidate form rather than a generic “neuro-symbolic hybrid” label.

---

# 1. Objects

Let `H` be the registered set of reachable histories/developmental situations at the scope under study.

Let

\[
q_P:H\to S_P
\]

be the predictive quotient induced by equality of the registered future observational law.

Let

\[
q_O:H\to S_O
\]

be the target semantic/developmental quotient induced by the full registered intelligence obligation `O`.

Examples of target distinctions not necessarily present in `S_P` include:

```text
causal/interventional state
provenance / authority state
historical lineage
legal permissions
rollback/adoption state
protected retention state
counterfactual response
future-learning state
```

The previous prediction-to-intelligence theorem gives the zero-residual case:

\[
q_O=g\circ q_P
\]

iff the predictive partition refines the target partition.

The present document studies the non-zero-residual case.

---

# 2. Residual code

A **target residual code** is a map

\[
r:H\to R
\]

for which there exists a decoder

\[
d:S_P\times R\to S_O
\]

such that

\[
q_O(h)=d(q_P(h),r(h))
\]

for every registered reachable `h`.

The residual is not required to be symbolic, discrete in implementation, externally stored, or human-readable.

It is defined only by information that must remain recoverable *in addition to* the predictive quotient.

Therefore implementations such as

```text
small neural side state
explicit ledger
retrieval memory
persistent branch state
causal graph fragment
rule table
transaction log
program object
latent continuous code at registered precision
```

can all instantiate the same residual requirement.

---

# 3. PRQ-1 — exact finite worst-case residual lower bound

For each predictive class `p in S_P`, define the target multiplicity

\[
m(p)
=
\left|
\{q_O(h):q_P(h)=p\}
\right|.
\]

That is, `m(p)` counts how many target-semantic states are observationally predictive-equivalent inside predictive class `p`.

## Theorem

Any exact residual code with a single reusable residual alphabet `R` must satisfy

\[
|R|\ge \max_{p\in S_P}m(p).
\]

Therefore any fixed-length binary residual code requires at least

\[
B_{res}^{wc}
\ge
\left\lceil
\log_2 \max_p m(p)
\right\rceil
\]

bits in the worst case.

## Proof

Fix a predictive class `p`.

For any two histories `h,h'` in that class with

\[
q_O(h)\ne q_O(h'),
\]

we have the same predictive input to the decoder:

\[
q_P(h)=q_P(h')=p.
\]

Therefore exact decoding requires

\[
r(h)\ne r(h').
\]

So at least `m(p)` distinct residual values are required within that predictive class. Since a global residual alphabet must work for every class,

\[
|R|\ge\max_p m(p).
\]

The fixed-bit bound follows immediately.

QED.

Parent mathematics: elementary conditional coding / distinguishability. The GMI contribution here is its use as a morphology-demand derivation between predictive and target semantic quotients.

---

# 4. PRQ-2 — average residual information

Put a registered distribution on reachable histories and define random variables

\[
P=q_P(H),\qquad S=q_O(H).
\]

If the residual uses a uniquely decodable or prefix code conditionally on predictive state `P`, standard source-coding arguments give

\[
E[L(R)]\ge H(S\mid P)
\]

bits, with ordinary integer-code overhead for achievable prefix codes.

Thus

\[
H(S_O\mid S_P)
\]

is the natural average **semantic residual burden** beyond prediction at the exact finite/discrete scope.

This is not a claim that neural networks literally store Shannon-optimal codes. It is an implementation-independent lower bound on recoverable target distinction.

---

# 5. PRQ-3 — zero-residual equivalence

The following are equivalent:

1. `m(p)=1` for every reachable predictive class;
2. `H(S_O|S_P)=0` for every full-support distribution on the reachable set;
3. no target residual state is required;
4. there exists a map `g` with
   \[
   q_O=g\circ q_P.
   \]

Therefore the earlier predictive-transfer theorem is exactly the zero-residual boundary of this stronger theory.

---

# 6. PRQ-4 — residual necessity is target-relative

The same predictive model may have zero residual burden for one obligation and large residual burden for another.

Example:

```text
O1: answer ordinary observational questions
O2: answer the same questions + exact source provenance
O3: O2 + as-of historical queries
O4: O3 + intervention/counterfactual queries
```

Even if all four share the same observational predictive state,

\[
H(S_{O1}|S_P)
\le
H(S_{O2}|S_P)
\le
H(S_{O3}|S_P)
\le
H(S_{O4}|S_P)
\]

need not be equal.

This predicts why adding retrieval, provenance, causal state or lineage memory can improve some obligations without implying that those mechanisms are universally required for intelligence.

---

# 7. PRQ-5 — prediction-only impossibility as a resource lower bound

Suppose there exists a predictive class with `m(p)>1`.

Then an exact target realization that exposes only `q_P` to its future decision mechanism is impossible.

This strengthens the qualitative prediction-only no-go:

```text
PREDICTIVE_ALIAS_EXISTS
=>
EXTRA_TARGET_INFORMATION_REQUIRED
```

and quantifies at least how many residual identities must remain distinguishable.

The residual may enter through:

```text
training data that breaks the alias
online intervention
retrieval/tool access
explicit persistent state
external authority/provenance channel
additional modality
human feedback
```

but it cannot be conjured from an observational state that mathematically identifies the aliased cases.

---

# 8. Approximate/stochastic extension

For approximate target loss `d(s,\hat s)` and allowed distortion `D`, the natural parent object is a conditional rate-distortion problem with predictive state available as side information:

\[
R_{S|P}(D).
\]

GMI interpretation:

> `R_{S|P}(D)` measures the minimum additional target-semantic information rate beyond the predictive substrate needed to achieve registered distortion `D`, subject to the assumptions of the chosen rate-distortion parent model.

This is a programme target, not a universal theorem for arbitrary continuous deep representations.

Required before strong use:

```text
registered distortion semantics
precision assumptions
reachable-state distribution
legal side information
coding/realization assumptions
```

---

# 9. Predicted morphology: Residual Quotient Machine (RQM)

The theorem predicts a property-first realization family when all of the following hold:

```text
1. a broad predictive substrate already captures substantial reusable structure;
2. target obligations contain a smaller set of prediction-aliased distinctions;
3. those residual distinctions are cheaper to preserve separately than to force into the whole predictive substrate;
4. residual state changes on a different timescale or authority regime from broad predictive state;
5. target queries can compose predictive state with residual state through a stable interface.
```

Call the resulting predicted property complex a **Residual Quotient Machine (RQM)**.

A generic state decomposition is

\[
Z_{RQM}
=
(Z_P,Z_R,Z_A,Z_C)
\]

where:

- `Z_P` — broad predictive/representation substrate;
- `Z_R` — target residual state sufficient to split relevant predictive aliases;
- `Z_A` — optional authority/provenance/adoption state when required;
- `Z_C` — routing/composition/compiled serving state.

The definition is behavioral/informational, not architectural.

An RQM may be implemented with neural nets, retrieval, rules, databases, programs, graphs or mixtures.

---

# 10. RQM is not just “RAG” or “neuro-symbolic AI”

Existing retrieval-augmented, modular, causal, memory-augmented and neuro-symbolic systems receive first refusal as parent realizations.

RQM makes a narrower prospective claim:

> the *need* for a separate augmentation should track measured target residual structure inside predictive equivalence classes, and its minimum semantic information burden should track conditional residual complexity—not architecture identity.

A generic hybrid does not predict that.

Strong RQM support therefore requires interventions on residual multiplicity while holding predictive difficulty as fixed as possible.

---

# 11. Predicted regime boundaries

## RQM-1 — pure predictor region

When

\[
H(S_O|S_P)\approx0
\]

and no independent authority/history/update mechanism is demanded, adding residual machinery should not improve the verified Pareto frontier after its burden is charged.

## RQM-2 — sparse residual region

When

\[
0<H(S_O|S_P)\ll H(S_O),
\]

an architecture preserving a broad predictor plus compact residual state should dominate strategies that either:

```text
(a) discard the reusable predictor and rebuild the full target state explicitly; or
(b) repeatedly rewrite the whole predictor to encode sparse changing residual distinctions.
```

This is the central prospective regime.

## RQM-3 — residual-dominant region

When target residual complexity approaches target complexity and predictor reuse is low, the predictor-plus-residual decomposition can lose its advantage.

A direct structured/causal/authoritative realization may become frontier-preferred.

## RQM-4 — dynamic residual region

If residual distinctions change frequently but predictive structure remains stable, GMI predicts local update boundaries around `Z_R`.

If rejectability/retention is strict, A4 speculative isolation becomes favorable.

If historical residual states remain queryable, A5 persistence becomes favorable.

This yields a stronger derived form below.

---

# 12. Predicted form: Versioned Residual Quotient Mesh (VRQM)

Combine the PRQ theorem with the independent VLC mechanism derivation.

A **Versioned Residual Quotient Mesh** is predicted in the regime:

```text
large reusable predictive substrate
+ sparse target residual distinctions
+ local residual dependency cones
+ frequent residual revision
+ rejectable updates / strong verifier
+ strict retention or historical lineage
+ long predictor reuse horizon.
```

Expected property vector:

```text
PREDICTIVE CORE      broad reusable learned substrate
RESIDUAL FACTORS     target-alias distinctions stored separately
A2                   authoritative residual state != disposable serving view
A3                   dependency-tracked local residual repair
A4                   verify-before-adopt candidate isolation when rejectable
A5                   lineage/persistence only when obligation demands old states
A6                   stable semantic composition boundary to predictive core
A7                   heterogeneous residual realizations allowed
```

Crucially, the theory predicts **where versioned locality should concentrate**: in the residual layer when broad predictive state is stable and residual state is the revision bottleneck.

That is stronger than predicting an everywhere-modular or everywhere-versioned machine.

---

# 13. Exact hostiles

The following must be part of the protected validation portfolio.

## H1 — zero residual

Construct `q_O=g(q_P)` exactly.

Prediction:

```text
minimum residual identities = 1
minimum residual bits = 0
RQM machinery has no semantic necessity
```

## H2 — one-bit alias

Every predictive class is target-homogeneous except one class split into two target states.

Prediction:

```text
B_res^wc = 1 bit
```

## H3 — heterogeneous fibers

Predictive classes split into target multiplicities `[1,2,3,5,...]`.

Prediction:

\[
B_{res}^{wc}=\lceil\log_2 5\rceil=3.
\]

## H4 — causal alias

Two latent worlds induce the same registered observational predictive law but differ under an allowed intervention.

Prediction:

```text
observational predictor alone cannot be exact
interventional residual/anchor required
```

## H5 — provenance alias

Identical content/future-text law, different legal source authority.

Prediction:

```text
content prediction can be identical
provenance obligation still forces residual distinction
```

## H6 — lineage alias

Same current/future ordinary behavior, different legal as-of history.

Prediction:

```text
ordinary prediction can merge histories
historical obligation forces lineage residual
```

## H7 — residual rewrite locality

Keep `Z_P` fixed while changing only one residual factor.

Prediction:

```text
full-core rewriting should become dominated as update rate/reuse rises,
provided local composition overhead stays below saved rewrite burden.
```

---

# 14. New measurements

Add the following architecture-neutral quantities to the experimental programme as derived response/demand descriptors, not silently to `Xi_obl` until identifiability is established:

\[
\mathcal R_{P\to O}
=
(H(S_O|S_P),\max_p m(p),\text{residual dependency geometry},\text{residual revision law}).
\]

For finite exact microscopes these are directly computable.

For real tasks they require estimators and must report uncertainty/identifiability class.

Do not estimate them using candidate-family identity or protected final outcomes.

---

# 15. Falsifiers

The residual-quotient explanation is weakened or killed at a registered scope if any of the following survives hostile replication:

```text
PRQ_BOUND_FAILS_IN_EXACT_ENUMERATION
ZERO_RESIDUAL_BUT_SEPARATE_RESIDUAL_STATE_IS_SEMANTICALLY_NECESSARY
NONZERO_RESIDUAL_RECOVERED_WITHOUT_ANY_LEGAL_EXTRA_INFORMATION
RESIDUAL_MULTIPLICITY_DOES_NOT_PREDICT_REQUIRED_TARGET_STATE_UNDER_MATCHED_INTERVENTION
RQM_ADVANTAGE_PERSISTS_WHEN_RESIDUAL_IS_REMINTED_TO_ZERO_AFTER_ALL_COSTS_ARE_CHARGED
RQM_ADVANTAGE_DISAPPEARS_WHEN_RESIDUAL_BURDEN_RISES_BUT_PARENT_RESOURCE_FACTORS_ARE_MATCHED
```

The first three would attack the formalization itself. The latter three attack its use as a morphology-selection law.

---

# 16. Claim ceiling

At v1 this document establishes:

```text
an exact finite residual distinguishability lower bound;
a conditional-entropy interpretation under ordinary coding assumptions;
a quantitative bridge from predictive insufficiency to extra target state;
a prospective RQM/VRQM property prediction.
```

It does **not** establish:

```text
that current LLM hidden states equal the predictive quotient;
that semantic quotients are directly measurable in unrestricted real domains;
that RQM or VRQM is empirically novel relative to every parent architecture;
that conditional entropy alone predicts total implementation cost;
that a protected neutral search has recovered the predicted form.
```

Those are experimental questions.

The scientific terminal for a strong new-form claim remains locked until neutral recovery, implementation-equivalence tests, parent first-refusal, disjoint protected replication and bounded parent-reduction survive.