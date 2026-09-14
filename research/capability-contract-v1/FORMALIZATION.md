# Capability contract V1 — formalization and proof obligations

Issue #602, A4 + F1.

## 0. Claim discipline

This artifact is an **architecture-independent behavioral specification**. It proves structural properties of the specification and defines falsifiable experiments. It does **not** prove that any particular system has any capability, does not prove a universal cognitive ontology, and does not raise #602 above G1 by itself.

Every empirical statement is relative to a registered ecology/task family, allowed information, resource envelope, parent class and protected remints. Internal implementation labels are neither necessary nor sufficient.

## 1. Contract object

For capability `c`, define

\[
C_c=(I_c,A_c,B_c,S_c,R_c,N_c,P_c,F_c).
\]

The coordinates are respectively: admissible inputs/tasks; allowed information; required behavioral predicate; success metric; resource metric; minimal negative twin; strongest registered parent/null; and falsifier. Every machine-readable row also carries scope, assumptions, evidence class and claim ceiling.

An evaluation unit is a protected remint/seed `w_i`. Common task utility is normalized to

\[
u(\pi,w_i)\in[0,1].
\]

Raw capability-specific metrics must still be reported; normalization exists only to support the common finite-sample bound.

## 2. Strongest-parent semantics

Let `Pi_c(B)` be policies admitted by the candidate information contract under resource budget `B`. The parent is not a named architecture. It is a preregistered behavioral null class

\[
\Pi_c^P(B)\subseteq\Pi_c(B).
\]

Its theoretical value is

\[
V_c^P(E,B)=\sup_{\pi\in\Pi_c^P(B)}\mathbb E_E[u(\pi,w)].
\]

This is the **first-refusal** rule: capability credit is available only after the best parent admitted by the registered null class has had the opportunity to explain the effect. In a finite enumerated parent class the supremum can be exact. In an open class an experiment may claim separation only from the *registered searched envelope* and must report search coverage. The best tried baseline may not silently be promoted to a universal optimum.

This is compatible with Blackwell's decision-theoretic comparison of information structures: extra information is credited by decision value, not by an implementation label.

## 3. Resource mathematics

Let the charged resource vector be

\[
r=(r_1,\dots,r_k)\in\mathbb R_{\ge 0}^k.
\]

Define componentwise order

\[
r\preceq s \iff \forall j,\ r_j\le s_j.
\]

A candidate-parent comparison is resource matched only when both obey the same registered budget vector, or when the candidate is componentwise no more expensive for the comparison being claimed. A scalar price `p^T r` is permitted only when nonnegative prices are frozen before scoring; the underlying vector must still be reported.

### Theorem 1 — resource order is a partial order

Reflexivity follows from `r_j <= r_j`. Antisymmetry follows because `r_j <= s_j` and `s_j <= r_j` imply equality in every coordinate. Transitivity follows coordinatewise. Therefore resource fairness can be stated without post-hoc scalarization.

## 4. Positive worlds and minimal negative twins

For each positive evaluation world `w_i+`, a capability row declares a transform `nu_c` producing `w_i-`.

`N0` is a **local minimality contract**:

1. exactly one registered capability-requiring conditional dependency is removed;
2. reward/action semantics, scoring, remint family and non-target resource budgets remain matched;
3. the capability becomes unnecessary, or the registered parent becomes sufficient, in the twin.

The checker proves that every row references `N0`. It cannot prove from prose that a future world generator really changes only one semantic dependency. That must be established by harness-level invariant tests. This separation prevents a schema theorem from masquerading as an empirical causal result.

Let

\[
d_i^+=u(M,w_i^+)-u(P,w_i^+),\qquad
d_i^-=u(M,w_i^-)-u(P,w_i^-).
\]

Capability-specific evidence requires a positive candidate-parent gap in `w+` and collapse of that gap in `w-`. If the gap survives the twin, the isolated dependency has not been identified: the effect may come from a confound, a broader capability or an invalid twin.

## 5. Finite-sample decision rule

Since `u in [0,1]`, paired differences lie in `[-1,1]`. For `n` independent registered evaluation units, Hoeffding's inequality gives

\[
\Pr\{\mathbb E[d] < \bar d-\epsilon\}\le\beta,
\qquad
\epsilon(n,\beta)=\sqrt{\frac{2\ln(1/\beta)}{n}}.
\]

The two gates use Bonferroni `beta=alpha/2`:

\[
\operatorname{LCB}_{\alpha/2}(\bar d^+)>\tau_P,
\]

and

\[
\operatorname{UCB}_{\alpha/2}(|\bar d^-|)
=|\bar d^-|+\epsilon(n,\alpha/2)\le\tau_N.
\]

`alpha`, `tau_P`, `tau_N`, the independence unit and sample-size plan must be frozen before the scored run. Capability-specific protocols may use stricter preregistered tests, but may not weaken these common gates.

### Theorem 2 — simultaneous error control

Each one-sided Hoeffding gate fails with probability at most `alpha/2` under the bounded independent-unit assumption. By the union bound, the probability that either confidence statement fails is at most `alpha`. No Gaussian or asymptotic approximation is required.

## 6. Structural-completeness theorem

Let `K` be the exact 27 A4 capability IDs and `Q` the exact 17 F1 coordinate IDs frozen in `validate.py`. The verifier checks:

- set equality with `K` and `Q`, plus uniqueness;
- all eight mandatory A4 fields for every capability;
- scope, assumptions, evidence class and claim ceiling for every capability;
- all resource references resolve to the global charged-resource ledger;
- all coordinate links resolve;
- every row references common allowed-information contract `A0`, success rule `S0`, one-dependency twin rule `N0`, and first-refusal parent rule `P0`;
- no row raises its claim ceiling above the registry ceiling;
- every F1 coordinate has a definition and reporting contract.

### Theorem 3 — schema omission freedom

If `validate.py` exits zero, then no #602 A4 capability or F1 coordinate is absent, duplicated, or structurally missing any registered mandatory field.

**Proof.** The verifier compares exact ID-set equality against immutable constants, rejects duplicates by cardinality, checks all required keys, resolves resource/coordinate references, enforces common assay references and verifies claim-ceiling order before returning success. Therefore zero exit implies all listed structural predicates. The theorem is intentionally limited to the registry artifact; semantic truth and empirical performance are separate obligations.

## 7. F1 is a vector, not an IQ scalar

For morphology `M`, ecology `E`, resource envelope `R` and history `H`, define

\[
C=\operatorname{Cap}(M,E,R,H)\in\mathcal C_1\times\cdots\times\mathcal C_{17}.
\]

Coordinates have different units and orders. A scalarization

\[
J_p(C)=\sum_j p_j\phi_j(C_j)
\]

is meaningful only for preregistered nonnegative weights/prices `p_j` and registered normalizations `phi_j`. Pareto comparison is the default. This prevents post-hoc weights from compensating an arbitrarily poor capability with an unrelated easy coordinate.

The 17 registered coordinates cover: memory capacity/retention; retrieval efficiency; abstraction/compression; transfer/generalization; compositional depth; planning horizon; exploration/information gain efficiency; causal identifiability/intervention; robustness/invariance; continual-learning plasticity; catastrophic-forgetting susceptibility; tool-use/solver routing; social-model depth; communication capacity; verification/reliability; self-model accuracy; and meta-learning/evolvability.

## 8. Mathematical anchors by capability family

Prediction and reliability use protected pre-outcome information and proper scores. Causal inference uses held-out interventions rather than observational association. Counterfactual reasoning requires factual evidence plus same-unit intervention semantics. Working, episodic and semantic memory are separated by delay, event identity and cross-episode regularity. Hierarchical skill formation requires recurring useful subtrajectories and charged reuse. Exploration requires decision-relevant information gain net of action cost. Metacognition and self-modeling require incremental predictive/control value about the system beyond public task covariates. Communication, teaching, culture and collective cognition isolate private information transfer, learner-conditioned example selection, intergenerational retention and coordination surplus respectively.

## 9. Claim ceiling and open obligations

A4/F1 registration does **not** establish G6 morphology-to-capability prediction, universal completeness of the 27-capability basis, ecological validity outside registered task families, consciousness/phenomenology, or cross-substrate equivalence.

To raise a row above G1, freeze a concrete world generator, parent-search protocol, negative-twin transform, resource ledger, thresholds, remints and external judge, then run the assay prospectively.

## 10. Literature anchors

These are methodological anchors rather than appeals to authority:

1. Blackwell, D. (1953), *Equivalent Comparisons of Experiments*, Annals of Mathematical Statistics 24(2), 265–272. DOI 10.1214/aoms/1177729032.
2. Gneiting, T. & Raftery, A. E. (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*, JASA 102(477), 359–378. DOI 10.1198/016214506000001437.
3. Baddeley, A. (1992), *Working memory*, Science 255(5044), 556–559. DOI 10.1126/science.1736359.
4. McClelland, J. L., McNaughton, B. L. & O'Reilly, R. C. (1995), *Why there are complementary learning systems in the hippocampus and neocortex*, Psychological Review 102(3), 419–457. DOI 10.1037/0033-295X.102.3.419.
5. Sutton, R. S., Precup, D. & Singh, S. (1999), *Between MDPs and semi-MDPs: A framework for temporal abstraction in reinforcement learning*, Artificial Intelligence 112, 181–211. DOI 10.1016/S0004-3702(99)00052-1.
6. Pearl, J. (2013), *Structural Counterfactuals: A Brief Introduction*, Cognitive Science. DOI 10.1111/cogs.12065.
7. Fleming, S. M. & Daw, N. D. (2017), *Self-Evaluation of Decision-Making: A General Bayesian Framework for Metacognitive Computation*, Psychological Review 124(1), 91–114. DOI 10.1037/rev0000045.
8. Shannon, C. E. (1948), *A Mathematical Theory of Communication*, Bell System Technical Journal 27, 379–423 and 623–656.
9. Shafto, P., Goodman, N. D. & Griffiths, T. L. (2014), *A rational account of pedagogical reasoning*, Cognitive Psychology 71, 55–89. DOI 10.1016/j.cogpsych.2013.12.004.
10. Tennie, C., Call, J. & Tomasello, M. (2009), *Ratcheting up the ratchet*, Philosophical Transactions B 364, 2405–2415. DOI 10.1098/rstb.2009.0052.
11. Dean, L. G. et al. (2012), *Identification of the social and cognitive processes underlying human cumulative culture*, Science 335, 1114–1118. DOI 10.1126/science.1213969.
12. Woolley, A. W. et al. (2010), *Evidence for a collective intelligence factor in the performance of human groups*, Science 330, 686–688. DOI 10.1126/science.1193147.
13. Lieder, F. & Griffiths, T. L. (2020), *Resource-rational analysis*, Behavioral and Brain Sciences 43:e1. DOI 10.1017/S0140525X1900061X.
