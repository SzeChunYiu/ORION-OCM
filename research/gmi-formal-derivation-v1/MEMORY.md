# Memory, retention and revision

Status: analytic constructions with an explicit distinction between retained
records and externally warranted claims. Uses [AXIOMS](AXIOMS.md).

## MEM1: state roles and sufficient retention

Write a configuration as \((w,k,c)\): temporary working state, persistent
executable knowledge, and control/remaining-resource state. These are roles
fixed by reset and retention maps, not intrinsic material kinds. An ordinary
episode reset discards \(w\) but preserves \(k\); a knowledge-reset intervention
also replaces \(k\). Changing \(k\) counts as learning only if earlier experience
causally affects later protected behavior or development through it.

For a fixed continuation-closed protected response map \(Q_h\), a deterministic
retention map \(m(h)\) preserves that entire map iff
\[
m(h)=m(h')\ \Longrightarrow\ Q_h=Q_{h'}.
\]
**Proof.** Necessity: the common decoder sees the same memory, hence must
produce the same profile. Sufficiency: define its value at \(m(h)\) as \(Q_h\);
the implication makes it well-defined. Measurable realizability and recursive
updates require the extra hypotheses in [REPRESENTATION](REPRESENTATION.md).
The condition concerns the full protected profile. For mere relational success,
one common acceptable action may solve different response profiles, so this
is not an unconditional task-memory lower bound.

If there are \(N\) pairwise distinct required profiles, exact deterministic
fixed-width memory needs at least \(\lceil\log_2N\rceil\) bits. Otherwise two
profiles receive the same code by the pigeonhole principle. An enumerated
lookup encoding attains the information width, with decoder storage/work
separately charged. Continuous exact distinctions need not fit finite memory.

## MEM2: forgetting and its precise decision consequence

Suppose \(M'\) is obtained from memory \(M\) by a known randomized channel
independent of the hidden target conditional on \(M\). Every decision rule
using \(M'\) is reproducible using \(M\): sample that channel, then run the
same rule. Hence, with no extra simulation restriction or charge, the attainable
risk set using \(M\) includes the one using \(M'\). This proves that garbling
cannot improve the *optimal* statistical risk for a fixed decision problem.
It says nothing about an arbitrary fixed, possibly overfitted learning rule.
Charged simulation, storage and limited execution can reverse net utility.

Example: retain a bit \(X\) solely for a future exact query with probability
\(p\), incremental benefit \(b\) over the best discard policy conditional on
that query, and scalar retention charge \(c\). This baseline includes any
admitted guessing; \(b\) is not automatically the full reward for a correct bit.
Under declared independent query arrival and no alternative acquisition,
retention's incremental expected utility is \(pb-c\). It is preferable iff
\(pb>c\). This is an expectation calculation, not a hard resource guarantee.

For a finite known model, lossless preservation of the *whole protected response
map* is exactly MEM1. Zero task loss alone can require less: acceptable action
sets \(\{a,b\}\) and \(\{a,c\}\) can share one memory and output \(a\).
For unbounded future tasks learned from finitely many observations, that
condition cannot generally be certified: two worlds can have identical observed
prefixes and differ on the first later query about the discarded bit. A supplied
continuation model or a limited probabilistic/finite-horizon obligation repairs
the question. Experience alone cannot certify every future continuation.

## MEM3: conflict, revision and dependency closure

An evidence record has an identity, content, source/event identifiers, model
version and scope. A claim certificate additionally states premises and a
sound derivation rule. Storing both \(p\) and \(\neg p\) as reported records
does not assert both as current facts. Evidence observations may be noisy;
truth and confidence are properties of a specified interpretation.

For finite acyclic dependency graphs, let \(B_t\) be currently admissible base
premises. A derived node is active iff its rule passes verification, its
versions/scopes match and at least one complete support set is active. Start
from \(B_t\) and evaluate nodes in topological order. To revise a base premise,
recompute its descendants; unrelated ancestors remain untouched. Alternative
supports are retained rather than indiscriminately deleting the claim.

**Theorem.** If every base premise in \(B_t\) is true in one common declared
interpretation and each admitted rule preserves truth, every active derived
claim is true in that interpretation.
**Proof.** Induct along a topological ordering. An active leaf is a true base
premise. Each active internal node has a complete true support and a sound
rule, hence is true. Revision restores the same inductive condition by
recomputing every potentially affected descendant. The graph traversal and
verification work, retained alternatives and transient memory are charged.

If a supposedly sound rule derives both a proposition and its negation under
one classical interpretation, at least one premise, scope or verification
assumption has failed. Mark that support inconsistent and withhold its use;
do not invoke explosion to make unrelated claims admissible. Cyclic support
requires grounded least-fixed-point semantics or a separate proof and must not
authorize a premise solely from itself.

Probabilistic base certificates fit this theorem on one simultaneous coverage
event. Reuse does not consume another statistical draw. A new model version
cannot inherit a certificate for the old parameter without a proved transport
bound. This is the bridge from [ADAPTIVE](ADAPTIVE.md) to
[COMPOSITION](COMPOSITION.md), not a claim that provenance guarantees truth.

## MEM4: ordinary Bayesian revision and its limits

With a declared finite hypothesis set, prior \(p_0(\theta)\), and conditional
likelihood \(L_t(y_t\mid\theta,h_{t-1},a_t)\), retain unnormalized weights
\[
w_t(\theta)=p_0(\theta)\prod_{s\le t}
L_s(y_s\mid\theta,h_{s-1},a_s),\qquad
p_t(\theta)=w_t(\theta)/\sum_\vartheta w_t(\vartheta).
\]
The factorization of the joint law and cancellation in conditional probability
prove this update whenever the denominator is positive. Conditional likelihoods
may encode dependent observations; multiplying repeated marginal evidence does
not implement this factorization. Zero prior weight remains zero. If all weights
vanish, conditioning is undefined: record model failure and explicitly expand
or replace the model, rather than silently renormalizing zeros. Posterior
certainty is not a frequentist confidence guarantee or causal identification.

## Parent relation

MEM1 specializes sufficient-state factorization. MEM2 proves the garbling
direction of [Blackwell's comparison of experiments](https://doi.org/10.1214/aoms/1177729032).
MEM3 is dependency-directed truth maintenance with external certificate scopes;
its resource extension connects to the existing
[shared-memory reuse theorem](../gmi-grand-unification-v1/SHARED_DEPENDENCY_MEMORY_REUSE_THEOREM_V1.md).
MEM4 is conditional probability, not a newly discovered Bayesian learning law.
