# GMI Neural Prediction-to-Intelligence Theorems v1

Status: **FORMAL SYNTHESIS THEOREMS — PARENT PREDICTIVE-STATE MATHEMATICS, GMI TRANSFER INTERPRETATION**

Refs: `GMI_NEURAL_MACHINE_INTELLIGENCE_DERIVATION_V1.md`, `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`, `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`.

## 0. Purpose

A central empirical fact of modern neural learning is that systems trained on predictive objectives can acquire representations useful for many tasks that were not explicitly labeled during development.

The weak explanation is:

> prediction requires understanding.

That statement is too vague to be a theory.

This document gives the exact condition under which predictive sufficiency transfers to a registered machine-intelligence obligation, and the exact condition under which it cannot.

The core object is a relation between two quotients:

```text
predictive quotient induced by the development stream
vs
semantic developmental quotient induced by the target obligation.
```

---

# 1. Finite stochastic setup

Let `H` be a finite set of legal observed histories reachable at a registered prediction time.

Let `X` be a finite observation alphabet. Let future finite continuations be strings

\[
w\in X^*.
\]

For each `h in H`, the environment induces conditional continuation probabilities

\[
P(w\mid h).
\]

Let a target machine-intelligence obligation `O` induce protected future semantic trace distributions

\[
P_{\mathcal O}(y\mid h,j)
\]

for legal protected intervention/probe `j in J_O` and semantic trace `y`.

Everything below extends conceptually to measurable spaces, but finite scope keeps the statements exact.

---

# 2. Predictive equivalence

Define

\[
h\sim_{pred}h'
\iff
\forall w\in X^*:
P(w\mid h)=P(w\mid h').
\]

Let

\[
S_{pred}=H/\sim_{pred}
\]

with canonical map

\[
q_{pred}:H\to S_{pred}.
\]

This quotient is the minimal exact state partition for unconditional future-observation prediction under the registered observational process.

Parent status: predictive-state / causal-state style mathematics.

---

# 3. Target semantic equivalence

Define

\[
h\sim_{\mathcal O}h'
\]

iff every legal protected intervention has the same target-semantic future distribution:

\[
\forall j\in J_{\mathcal O},\forall y:
P_{\mathcal O}(y\mid h,j)
=
P_{\mathcal O}(y\mid h',j).
\]

Let

\[
S_{\mathcal O}=H/\sim_{\mathcal O}
\]

with canonical map `q_O`.

This is the history-restricted form of the GMI semantic developmental quotient.

---

# 4. NPI-1 — quotient-transfer theorem

## Statement

The following are equivalent:

1. predictive equivalence refines target semantic equivalence:

\[
h\sim_{pred}h'\Rightarrow h\sim_{\mathcal O}h';
\]

2. every predictive equivalence class is contained in one target semantic class;
3. there exists a unique map

\[
g:q_{pred}(H)\to S_{\mathcal O}
\]

such that

\[
q_{\mathcal O}=g\circ q_{pred}.
\]

## Proof

`1 => 3`:

For a predictive class `s=q_pred(h)`, define

\[
g(s)=q_{\mathcal O}(h).
\]

If `q_pred(h)=q_pred(h')`, then `h~pred h'`; by assumption `h~O h'`, hence `q_O(h)=q_O(h')`. Therefore `g` is well-defined. It is unique because every reachable predictive state has a representative `h` and `q_O(h)` is fixed.

`3 => 1`:

If `h~pred h'`, then `q_pred(h)=q_pred(h')`. Applying `g` gives

\[
q_{\mathcal O}(h)=g(q_{pred}(h))
=g(q_{pred}(h'))
=q_{\mathcal O}(h'),
\]

so `h~O h'`.

Equivalence with 2 is ordinary partition refinement.

QED.

## Interpretation

If NPI-1 holds, exact predictive state contains all state distinctions required by the target obligation. A downstream decoder/controller may still be difficult to learn, but there is no information-theoretic target distinction missing from predictive state.

This is the precise sense in which self-supervised prediction can create a reusable intelligence substrate.

---

# 5. NPI-2 — predictive collision no-go

## Statement

If there exist histories `h,h'` such that

\[
h\sim_{pred}h'
\quad\text{and}\quad
h\not\sim_{\mathcal O}h',
\]

then no representation `r(h)` that is a function only of exact predictive state

\[
r=\phi\circ q_{pred}
\]

can be sufficient for exact target semantic state `S_O`.

## Proof

Because `h~pred h'`,

\[
q_{pred}(h)=q_{pred}(h').
\]

Therefore

\[
r(h)=r(h').
\]

But `h not~O h'`, so the target requires distinct semantic states.

Any downstream computation seeing only `r` receives the same state on both histories and therefore cannot reproduce two different required exact target-semantic future laws.

QED.

Terminal:

```text
PREDICTIVE_STATE_ALIASES_TARGET_SEMANTIC_DISTINCTION
```

---

# 6. NPI-3 — exact next-step conditionals determine all finite continuation laws

Let the observation process be autoregressive over alphabet `X`.

Suppose for every legal history `h` the exact next-symbol conditional is known:

\[
p(x\mid h)=P(X_{t+1}=x\mid h).
\]

For any finite continuation

\[
w=(x_1,\ldots,x_k),
\]

the chain rule gives

\[
P(w\mid h)
=
\prod_{i=1}^{k}
p(x_i\mid h x_{1:i-1}).
\]

Therefore equality of exact next-step conditional functions on every reachable extended history implies equality of every finite continuation distribution.

## Corollary

An exact all-history next-token model determines the exact finite-horizon predictive quotient of the sequence process.

This gives a rigorous bridge from a local autoregressive loss to global observational predictive state.

## Qualification

Practical language models do not satisfy the ideal assumptions:

```text
finite data;
finite context;
approximate optimization;
approximate probability model;
limited precision;
distribution shift;
training support holes.
```

The theorem explains the ideal target of the training objective, not the guarantee of a finite training run.

---

# 7. NPI-4 — why latent world structure can be forced into a predictor

Let an environment have latent state `Z` and observed history `H`.

Suppose there are latent states `z,z'` that induce different future observation distributions after some reachable histories:

\[
P(X_{t:}\mid h,z)
\ne
P(X_{t:}\mid h',z').
\]

Then any exact minimal predictive state must distinguish the corresponding predictive classes whenever the difference survives conditioning on legal history.

Thus if latent variables such as

```text
entity identity;
object permanence;
syntax;
speaker intention;
code semantics;
mathematical relation;
physical regularity;
discourse state;
```

systematically change future observation statistics, predictive sufficiency pressures the model to preserve information about them.

This does **not** imply a human-readable internal variable or unique representation.

Many implementation encodings can realize the same predictive distinction.

---

# 8. NPI-5 — target-task transfer is a partition question

Let a downstream task label/action variable `Y` induce task equivalence

\[
h\sim_Y h'
\iff
P(Y\mid h)=P(Y\mid h').
\]

Then exact predictive state is sufficient for `Y` exactly when

\[
\sim_{pred}\ \subseteq\ \sim_Y.
\]

Equivalently, `q_Y` factors through `q_pred`.

This is the cleanest possible criterion for whether a downstream task is, in principle, recoverable from perfect predictive representation.

It avoids vague claims about "emergence".

A new capability may appear after pretraining because the representation already contains the distinction and only a low-burden decoder/prompt/controller is missing.

---

# 9. NPI-6 — predictive sufficiency does not imply causal/interventional sufficiency

Pure observational prediction may identify two histories that have the same future observation law under the passive data process but different consequences under an intervention.

Let legal action/intervention `a` produce controlled future law

\[
P(w\mid h,a).
\]

Define action-conditioned predictive equivalence

\[
h\sim_{cpred}h'
\iff
\forall a\in\mathcal A,\forall w:
P(w\mid h,a)=P(w\mid h',a).
\]

Then

\[
\sim_{cpred}
\]

is generally finer than passive `~pred`.

A control/causal obligation can factor through passive prediction only if passive state already preserves every action-relevant distinction.

Otherwise the correct development target is controlled prediction, intervention-rich data, causal structure, experimentation, tools, or another mechanism.

This is a direct GMI reason that observational language modeling alone need not identify every action consequence or causal variable.

---

# 10. NPI-7 — controlled predictive-state transfer theorem

Let `S_cpred` be the quotient under action-conditioned predictive equivalence.

If

\[
h\sim_{cpred}h'
\Rightarrow
h\sim_{\mathcal O}h',
\]

then

\[
q_{\mathcal O}=g\circ q_{cpred}
\]

for a unique map on reachable controlled predictive states.

This is the natural transfer theorem for interactive agents.

Parent relationship: predictive-state representations already use action-conditional predictions as state. GMI uses the refinement test against an independently registered semantic-developmental obligation.

---

# 11. NPI-8 — provenance and authority are separate unless they affect prediction

Suppose two information states yield identical observable predictive distributions but differ in source authority, provenance, license, evidence admissibility or constitutional permission.

If those properties do not alter the prediction stream used in development, passive predictive state may merge them.

Yet a target obligation with external verifier/constitution may require them to remain distinct.

Therefore:

```text
probabilistic predictive correctness
!=
epistemic authority / admissibility.
```

A neural predictor may need retrieval receipts, signed sources, proof objects, external databases or other authority-bearing state to satisfy the stronger quotient.

This formalizes why fluent predictive models can be useful cognitive engines without becoming self-authorizing sources of truth.

---

# 12. NPI-9 — historical lineage is separate unless history changes future observations

Two current states can have the same passive future distribution but differ in legally protected historical lineage:

```text
which version was authoritative at time t;
which branch produced a result;
what source existed before a cutoff;
which data must be deleted or retained.
```

If the future observational stream is insensitive to those facts, `S_pred` may discard them.

A lineage-aware obligation cannot.

Thus the `beta_lin` dimension introduced in typed GMI is not derivable from generic next-token prediction unless lineage affects the training/prediction law or is explicitly represented in the target.

---

# 13. NPI-10 — developmental-state transfer is stronger than current-task transfer

Suppose histories `h,h'` produce the same current predictive output but different future learning responses after legal teaching event `e` because the learner has different optimizer, replay, uncertainty or plasticity state.

If future development is protected, then

\[
h\not\sim_{\mathcal O}h'
\]

even when current predictions match.

Therefore a frozen representation evaluated only by current prediction can be insufficient for developmental intelligence.

The state passed to future learning must preserve every distinction that changes protected update behavior.

This is why GMI includes optimizer/learning state in `Z` when development is in scope.

---

# 14. NPI-11 — approximate transfer requires an error calculus, not naive epsilon classes

For real neural systems, exact equality is unrealistic.

Let

\[
d_{pred}(h,h')
\]

measure distance between predictive continuation laws, and

\[
d_{\mathcal O}(h,h')
\]

measure protected semantic future distance.

A useful approximate transfer condition is a registered modulus

\[
d_{\mathcal O}(h,h')
\le
\omega(d_{pred}(h,h'))
\]

for relevant histories, where `omega(r)->0` as `r->0`.

Then predictive approximation error controls semantic approximation error.

This is stronger and safer than declaring

```text
h ~ h' when d(h,h') <= epsilon
```

because fixed-radius closeness need not be transitive.

A practical neural transfer claim should therefore register:

```text
predictive metric;
target semantic metric;
transfer modulus or calibration relation;
protected support;
confidence interval / uncertainty.
```

---

# 15. NPI-12 — information bottleneck corollary

Any exact representation `R(h)` sufficient for target semantic state must distinguish all target quotient classes.

If prediction-to-target transfer holds and `R` is an exact minimal predictive representation, then compressing `R` further is safe only if the compression does not merge predictive classes that map to different target classes.

Thus an information bottleneck is obligation-safe only relative to the distinctions that remain protected.

This connects predictive compression to GMI semantic quotient preservation without claiming that a particular information-bottleneck objective automatically discovers the right semantics.

---

# 16. NPI-13 — in-context learning is stateful execution, not necessarily weight learning

For a Transformer-like model with frozen parameters `theta`, a prompt/context `c` can change the conditional function implemented on the next input.

Define temporary execution state

\[
z_{ctx}=Enc_\theta(c).
\]

Then outputs are generated by

\[
Q_\theta(y\mid x,z_{ctx}).
\]

If `theta` is unchanged, this is a change in execution state and conditional computation, not automatically a within-morphology parameter update `U`.

GMI therefore separates:

```text
weight-space development;
context-space adaptation;
external-memory retrieval;
morphology change.
```

All can produce behavioral adaptation but have different persistence, retention and resource properties.

---

# 17. NPI-14 — predictive pretraining can reduce downstream sample complexity without solving the downstream task

Suppose target semantic state factors through predictive state:

\[
q_{\mathcal O}=g\circ q_{pred}.
\]

A pretrained model may have already learned a representation approximating `q_pred`.

Downstream development then needs only to learn/implement `g` rather than relearn the raw history-to-target map.

If `g` lies in a much lower-burden function class than the raw target map, downstream sample/compute burden can be dramatically smaller.

This is a clean GMI account of transfer learning:

```text
pretraining pays the cost of a broad predictive quotient once;
many downstream tasks reuse projections of that quotient.
```

It also yields a failure prediction: tasks whose distinctions do not factor through predictive state should receive much less transfer benefit unless new information is supplied.

---

# 18. NPI-15 — shared predictive state explains multi-task reuse

Let target tasks `O_1,...,O_m` each satisfy

\[
q_{\mathcal O_i}=g_i\circ q_{pred}.
\]

Then one shared predictive representation can support all tasks through task-specific maps `g_i`.

The total lifecycle burden may be lower than training `m` independent task-specific representations when

\[
B(q_{pred})+\sum_i B(g_i)
<
\sum_i B(q_{\mathcal O_i}\ from\ raw\ history).
\]

This is a formal reuse condition for foundation-model-style pretraining.

The advantage grows with:

```text
number of downstream tasks;
shared predictive structure;
reuse count;
low cost of task-specific decoding;
stability of the predictive representation.
```

---

# 19. Canonical hostiles

## H1 — passive observational alias

Same passive future distribution, different action consequence.

Expected result:

```text
passive S_pred merges;
controlled/target quotient separates.
```

## H2 — provenance alias

Same text/prediction statistics, different source authority.

Expected result:

```text
prediction-only state insufficient for authority-sensitive obligation.
```

## H3 — lineage alias

Same current/future serving distribution, different protected historical branch.

Expected result:

```text
prediction-only state insufficient for lineage obligation.
```

## H4 — developmental alias

Same current outputs, different future update response.

Expected result:

```text
current predictive state insufficient for developmental obligation.
```

## H5 — reminted latent structure

Rename/re-encode surface symbols while preserving the predictive/semantic structure.

Expected result:

```text
mechanism-level transfer remains;
world-ID memorization fails.
```

## H6 — target outside predictive support

Downstream distinction never affects any training-stream continuation.

Expected result:

```text
pretraining does not force the distinction;
new supervision/intervention is required.
```

---

# 20. What these theorems explain about neural language models

They explain why a sufficiently capable predictive neural system can acquire representations useful for many tasks:

1. autoregressive conditionals determine finite continuation laws in the ideal limit;
2. latent distinctions that change continuation laws must be represented by an exact sufficient predictor;
3. many downstream tasks are projections of those same distinctions;
4. one large predictive state can therefore be amortized across many tasks;
5. attention/depth provide a flexible neural realization of the predictive map;
6. gradient training provides scalable credit assignment for approximating it.

They also explain why language modeling does **not** logically guarantee every form of intelligence:

```text
causal/control distinctions may require interventions;
provenance may require external evidence state;
historical obligations may require explicit lineage;
continual-development competence may require update-state distinctions;
exact formal semantics may require exact mechanisms;
OOD target distinctions may be absent from the training predictive quotient.
```

This replaces both extremes:

```text
"next-token prediction is just autocomplete"
```

and

```text
"perfect prediction automatically implies universal intelligence"
```

with an exact partition/refinement condition.

---

# 21. Parent-literature subtraction

GMI does not claim novelty for:

- predictive-state representations;
- causal-state / computational-mechanics minimal prediction state;
- sufficient-statistic factorization;
- autoregressive chain-rule factorization;
- controlled predictive state;
- transfer through sufficient representation.

The GMI contribution is to connect those parent objects to an independently registered **semantic developmental quotient**, external verifier/constitution, lifecycle resources, and morphology selection.

The novel empirical question is not whether prediction can contain useful state. It is:

> For which protected intelligence obligations, ecologies and development protocols does the learned predictive state actually refine the required semantic-developmental state at lower total burden than competing realizations?
