# Revocation-Complete Learning V0

**Programme:** ORION Cognitive Machine, ORION-V2 #194  
**Execution master:** ORION-V2 #197  
**Base:** `7ae422075a782cbee743fe0eaac176c81dbab08b`  
**Date:** 2026-09-03  
**Terminal:** `NEW_THEORETICAL_RESIDUAL_CANDIDATE__EXTERNAL_NOVELTY_NOT_ESTABLISHED`

## 1. Research question

Ordinary learning asks whether a reusable operator is correct now. Ordinary proof-carrying execution asks whether one supplied execution is justified now. Ordinary provenance and truth maintenance update a known dependency object. Ordinary unlearning receives a deletion request and tries to remove its influence.

**Revocation-Complete Learning (RCL)** asks a joint question:

> Can a learner acquire reusable operator semantics together with enough counterfactual warrant structure to remain exact after later evidence, checker, scope, rule, or authority changes—without retaining unsupported skills, deleting independently supported skills, or hiding the cost in a verifier or replay oracle?

The key property is **Counterfactual Warrant Completeness (CWC)**. A transcript is CWC for an admitted intervention family when it contains, or can reconstruct at a charged cost, enough information to decide every future retain/retract/abstain obligation in that family.

The elementary theorems below establish a real gap between a proof that is valid today and a transcript that is complete for tomorrow. They do **not** establish external novelty. Their purpose is to freeze a correct object that can now be attacked against the strongest parent product.

## 2. Expert-cell synthesis

### Learning–unlearning theory

Generic future-deletion memory lower bounds, ticketed memory, and memory/deletion-capacity/computation trade-offs are parent-owned. The candidate residual must not reduce to “receive a subset of examples to delete.” The intervention may instead invalidate a data identity, checker version, authority edge, scope, derivation rule, or certificate class; the learner must preserve all independently warranted operator behavior.

### Provenance and dynamic computation

Alternative derivations, dependency-directed invalidation, provenance polynomials, truth-maintenance systems, and self-adjusting computation already own exact update over a **known** dependency object. RCL must therefore learn the operator and the warrant object jointly, or prove a frontier created by incomplete warrant acquisition.

### Formal verification and authority

A valid certificate is existential: it proves that at least one current warrant works. Future exact retention is extensional over all surviving warrants. Soundness of one proof does not imply completeness of the proof family. Generator and checker identities, versions, scopes, and authority must be explicit; neither may self-authorize.

### Complexity theory

The finite lower bounds use standard counting and decision-tree arguments. The candidate new object is a conditional intervention dimension and a joint storage–proof-query–recourse–false-authority frontier, not the counting lemma by itself.

### Architecture theory

A recurrent/looped Transformer with the same memory, proof-query interface, verifier, tools, and time can implement the finite algorithms here. The current result is architecture-neutral. “Post-Transformer” remains blocked unless a separate resource obstruction survives parity compilation.

### Language and compositional learning

A useful later theorem must learn primitive operators and demonstrate held-out/reminted composition after revocation. A formal warrant theorem alone does not establish natural-language competence.

### ORION epistemics

ORION’s plausible residual is that evidence identity, dependence, scope, authority, expiry, failure knowledge, and `reopen_on_change` become part of the learned object rather than post-hoc logging fields. That claim becomes scientific only if the information changes a learnability or update frontier.

### Hostile novelty referee

The strongest reduction is:

```text
computational-trace learner
+ exact monotone-DNF / hidden-hypergraph learner
+ ticketed or system-aware exact unlearning
+ provenance semiring / truth maintenance / self-adjusting computation
+ proof-carrying execution
+ authority-revocation and provenance-to-forget-set machinery
+ recurrent Transformer implementation
```

Most ingredients are owned. The only admissible residual is a theorem about their **joint learning-and-revision interface** that this product does not already entail at equal information and resources.

## 3. Formal model

Let `E={1,...,n}` be finite evidence atoms. A learned skill has an antichain of inclusion-minimal sufficient warrants

\[
\mathcal J \subseteq 2^E.
\]

Antichain means no distinct `J,K in mathcal J` satisfy `J subset K`. After revocation `R subseteq E`, the skill is live exactly when one full warrant survives:

\[
\operatorname{Live}_{\mathcal J}(R)=1
\quad\Longleftrightarrow\quad
\exists J\in\mathcal J: J\cap R=\varnothing.
\]

Equivalently, for active evidence `A=E\setminus R`, define the monotone function

\[
f_{\mathcal J}(A)=1 \Longleftrightarrow \exists J\in\mathcal J:J\subseteq A.
\]

The **revocation signature** is

\[
\sigma_{\mathcal J}=(\operatorname{Live}_{\mathcal J}(R))_{R\subseteq E}.
\]

A transcript map `tau` may expose endpoints, raw execution, one or more positive proof witnesses, or a revocation-complete summary. A summary `q(tau(mathcal J))` is exact without later access when it determines `sigma_mathcal J`.

### Revocation-shattering dimension

For a profile class `Phi`, transcript map `tau`, and admitted revocations `Gamma`, define `RSD(Phi,tau,Gamma)` as the largest `k` for which there exist a transcript value `t` and revocations `R_1,...,R_k in Gamma` such that every bit vector `b in {0,1}^k` is realized by some `mathcal J in Phi` with `tau(mathcal J)=t` and

\[
\operatorname{Live}_{\mathcal J}(R_i)=b_i
\quad (i=1,...,k).
\]

RSD measures future revision ambiguity left after the current transcript, not present-task predictive complexity.

