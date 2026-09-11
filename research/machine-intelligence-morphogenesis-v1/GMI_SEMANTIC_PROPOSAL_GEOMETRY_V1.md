# GMI Semantic Proposal Geometry v1

Status: **CANDIDATE CROSS-PARADIGM CORE OBJECT — HST/SEARCH-THEORY SYNTHESIS**

Refs: #233, #377, #323, `GMI_BIAS_RESOURCE_GEOMETRY_V1.md`, `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`.

## 1. Problem

“Inductive bias” is expressed differently across machine-intelligence forms:

```text
Bayesian system     explicit prior/posterior probability
program search      code length / proposal probability / enumeration order
symbolic system     hypothesis class / agenda / rule ordering
retrieval system    retrieval score/rank
neural model        parameterization + pretrained state + optimizer-induced implicit bias
OCM                 history-conditioned fragment/operator/controller proposal order
```

Comparing these native representations directly is architecture-dependent.

GMI needs an obligation-relative object that asks the same question in every family:

> How difficult is it, *before target success*, for this realization to generate cognition whose semantic effect belongs to a registered useful target set?

---

# 2. Native proposal space and semantic map

For morphology `M` in realization state `z` and task `tau`, let

\[
\mathcal C_M(z,\tau)
\]

be its native candidate-cognition space.

Examples:

```text
next token/action
premise/tactic
rule firing
program candidate
hypothesis
retrieved skill/case
file to inspect
repair proposal
experiment
representation change
```

Let

\[
\psi_{M,\Omega}:\mathcal C_M\to\mathcal C_\Omega
\]

map a native candidate to its protected semantic candidate/effect class for the registered obligation.

`C_Omega` is not necessarily the semantic machine state `S_Omega`; it is the obligation-relative semantic space of candidate cognitive moves/effects being compared.

If no valid semantic correspondence can be defined, the proposed cross-paradigm comparison is `CANNOT_CHECK_SEMANTIC_CANDIDATE_MAP`.

---

# 3. Probabilistic pushforward

If `M` supplies a proposal distribution/kernel

\[
Q_M(c\mid z,\tau),
\]

then the semantic proposal distribution is its pushforward:

\[
\bar Q_M(A\mid z,\tau)
=
Q_M(\psi_{M,\Omega}^{-1}(A)\mid z,\tau)
\]

for measurable semantic candidate sets `A subset C_Omega`.

In a finite setting:

\[
\bar Q_M(s)
=
\sum_{c:\psi(c)=s}Q_M(c).
\]

This removes irrelevant implementation multiplicity: many parameter/program/native candidates that have the same protected semantic effect contribute to the same semantic mass.

---

# 4. Deterministic / ranked search

Not every system has a normalized probability.

For deterministic/ranked search, define a semantic first-hit burden.

For registered target semantic set

\[
A\subseteq\mathcal C_\Omega,
\]

let

\[
T^M_A
\]

be the raw resource vector or prospectively scalarized burden consumed until the first generated/considered candidate `c` with

\[
\psi(c)\in A.
\]

Examples:

```text
first relevant theorem premise rank
first successful tactic/proof-step rank
first useful program candidate
first actual causal fault file inspected
first applicable learned method served
first successful OCM fragment/operator proposal
```

If stochasticity is present, `T_A` is a random variable.

The CDF

\[
G_M(A,b)=P[T_A^M\le b]
\]

is a semantic proposal-geometry object independent of how native candidates are encoded.

For deterministic search it is a step function at the first-hit burden.

---

# 5. Semantic surprisal / rank specializations

When a semantic probability is defined:

\[
I_M(A)=-\log_2 \bar Q_M(A)
\]

is a target-set surprisal.

When only a deterministic order is defined, use:

```text
rank
candidate evaluations
search expansions
verified checks before first hit
```

rather than fabricating probabilities.

A code length or rank may be converted to probability only under an explicitly registered scheduler/coding model.

---

# 6. GMI-SPG1 — realization refinement invariance

Suppose one implementation splits a native candidate `c` into multiple implementation-distinct variants

```text
c1,...,ck
```

that all map to the same semantic candidate `s`.

A semantic pushforward sums their proposal mass into `s`.

Therefore semantically irrelevant candidate duplication does not by itself create a stronger bias claim.

This is the proposal-space analogue of quotienting implementation-distinct states.

---

# 7. GMI-SPG2 — developmental K1 as semantic geometry change

Let history/development change the realization from `M_t,z_t` to `M_(t+1),z_(t+1)`.

For fresh protected target semantic set `A` whose solution/candidate identity was absent from relevant history, K1 cognition-generation capital is directly supported when, under matched controls, the pre-solution semantic proposal geometry improves.

Examples:

\[
I_{t+1}(A)<I_t(A)
\]

or

\[
T_{A,t+1}<T_{A,t}
\]

or stochastic dominance over a registered burden range:

\[
G_{t+1}(A,b)\ge G_t(A,b)
\]

with strict improvement somewhere.

Final success alone is insufficient.

---

# 8. Why this is more general than architecture labels

The same semantic target set can be reached through:

```text
high neural probability
low program description length
high retrieval rank
short symbolic proof search
cheap Bayesian experiment selection
fast OCM fragment/operator proposal
```

The native mechanisms differ, but the target-semantic first-hit burden can be compared under the registered resource semantics.

Thus:

```text
architecture
-> native Q/search
-> semantic proposal geometry
-> verified cognition burden.
```

The semantic geometry is a better candidate for a cross-paradigm developmental invariant than “neural vs symbolic”.

---

# 9. Existing #323 evidence

The existing history-induced search-capital lane is a direct SPG instance.

On its registered authored program-search ecology, continued history moved the eventual verified fresh-target solution earlier in the native proposal order on the large majority of targets and yielded a median positive rank-information shift.

That is evidence that history changed semantic proposal geometry at that scope.

It is not yet evidence that the same geometry law transfers to neural learning, coding or formal mathematics.

---

# 10. Coding E3 mapping

The frozen #208 coding K1 design uses evaluator-private planted causal fault files.

Native candidates:

```text
ordered file inspections / localization hypotheses / repair plans.
```

Semantic target set:

```text
actual injected causal fault file(s).
```

Primary first-hit/coverage burden:

```text
rank by which all causal fault files are inspected.
```

This is an SPG measurement without exposing the fault locations to the solver.

---

# 11. Formal mathematics mapping

Candidate future math SPG measurements:

```text
rank of eventually consumed premise
rank of eventually successful tactic/proof step
proof-state expansions until useful lemma/subgoal
kernel calls until first valid relevant construction
```

The semantic map must distinguish:

```text
formal statement correctness
from
informal statement correspondence.
```

A highly ranked proof of the wrong formalization is not semantic target success.

---

# 12. Neural mapping

For a neural classifier/policy with explicit predictive/action distribution, the output distribution may already live near the semantic action/label space.

For more internal cognition the mapping is harder.

Possible semantic proposal objects include:

```text
output/action probability
candidate decoded plan probability
retrieved premise/tool probability
semantic hypothesis distribution induced by sampling
```

Gradient magnitude or parameter distance is **not** automatically semantic proposal geometry.

A neural cross-paradigm claim requires a justified map from neural outputs/proposals to the same obligation-relative semantic candidates.

---

# 13. Bayesian mapping

If the hypotheses/actions are already semantic objects, the posterior/predictive distribution can directly instantiate `bar Q`.

But model misspecification remains load-bearing:

```text
high posterior confidence within a wrong hypothesis class
```

is not semantic adequacy.

GMI's semantic/verifier contract remains outside the prior/posterior confidence score.

---

# 14. Program search mapping

Prefix-code/program priors supply an explicit native proposal geometry.

If multiple syntactically different programs are semantically equivalent for the obligation, compare the pushforward mass of the semantic class rather than one source string.

This avoids giving credit for syntactic duplication.

---

# 15. Resource-vector issue

`T_A` is naturally a resource vector:

```text
candidate proposals
search expansions
model tokens
checker calls
tool calls
CPU/GPU/wall
```

There is no total order without a registered price/priority relation.

Allowed analyses:

```text
Pareto dominance
coordinate-specific first-hit burden
prospectively frozen scalarization
budget-indexed capability curves.
```

Do not choose weights after target outcomes.

---

# 16. Verification vs proposal

Reaching a promising semantic candidate is not the same as obtaining a verified result.

Keep:

```text
T_proposal(A)
```

separate from

```text
T_verified(A).
```

This permits diagnosis of:

```text
good proposal bias + expensive verification
bad proposal bias + cheap verifier
good rank but invalid candidates
```

and prevents verifier work from being hidden inside “search”.

---

# 17. Negative transfer

History can make semantic proposal geometry worse.

For a target set `A`:

```text
T_after_history(A) > T_reset(A)
```

or

```text
barQ_after_history(A) < barQ_reset(A).
```

This is a first-class harmful-transfer result.

Developmental intelligence must include the ability to avoid, scope or recover from such bias where the ecology requires it.

---

# 18. K2 and K3 extension

K1:

```text
experience improves semantic proposal geometry for future target cognition.
```

K2:

```text
experience improves the process that acquires useful future semantic proposal geometry.
```

Operationally, on fresh family identities:

\[
B(\text{acquire a useful }\bar Q_{new})
\]

falls versus reset/parents.

K3:

```text
experience improves the process that improves K2 / morphology discovery.
```

This connects SPG to HST and governed RSI without changing the definition of K1.

---

# 19. Strong parents

The components are parent-owned by, among others:

```text
search bias / algorithmic probability
Bayesian priors and posterior prediction
proposal distributions in search/SMC/MCTS
ranking/retrieval metrics
PAC/PAC-Bayes and meta-learning
Levin/OOPS bias-optimal search
information theory
hitting-time / stochastic-process analysis
algorithm selection
```

GMI novelty cannot be “proposal distributions exist”.

The possible residual is a unified semantic pushforward + developmental/resource measurement across heterogeneous morphologies/verification regimes.

---

# 20. Falsifiers

```text
SEMANTIC_CANDIDATE_MAP_NOT_IDENTIFIABLE
NATIVE_CANDIDATE_SPACES_NOT_COMPARABLE_AT_REGISTERED_SCOPE
PUSHFORWARD_LOSES_LOAD_BEARING_INFORMATION
FIRST_HIT_BURDEN_DOES_NOT_PREDICT_VERIFIED_CAPABILITY
FAMILY_NATIVE_GEOMETRY_SUFFICIENT
RESOURCE_SCALARIZATION_DOMINATES_RESULT
NO_CROSS_PARADIGM_TRANSFER
```

---

# 21. Immediate experiments

## SPG-E0 — exact finite bias phase

Interpret the current threshold concept fixture in semantic prediction space.

## SPG-E1 — program/search plus Bayesian family

Use explicit proposal probabilities/ranks and semantic-equivalence grouping.

## SPG-E2 — OCM #323 plus a disjoint program family

Freeze a common first-hit/rank-information statistic prospectively.

## SPG-E3 — coding K1

Use the already frozen causal-fault localization burden.

## SPG-E4 — formal math

Use protected premise/tactic target sets after #46 unlock.

## SPG-E5 — neural family

Freeze a semantic-output/proposal target and test whether development shifts its pre-solution geometry on held-out task families.

Only after E2–E5 should any cross-paradigm law be claimed.

---

# 22. Current terminal

```text
SEMANTIC_PROPOSAL_GEOMETRY_SPECIFIED_V1
```

Claim ceiling:

> GMI now has one architecture-neutral language for semantic pre-solution bias: the pushforward/first-hit geometry of native cognition proposals into registered semantic candidate space. Its cross-paradigm predictive usefulness remains empirical.
