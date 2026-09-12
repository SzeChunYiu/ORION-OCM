# GMI Empirical Frontier Identifiability Boundary v1

Status: **FORMAL NO-GO / EXTERNAL-EVIDENCE BOUNDARY**

Date: 2026-09-12.

Some remaining blockers cannot be removed by adding more internal theory, because the sign of the frontier comparison depends on an unmeasured world variable.

Let all theory-visible pre-outcome descriptors be `X`. Let hidden external quantity `theta` represent, for example:

```text
hardware preparation energy
compiler/runtime constant
network communication cost
physical noise/coherence
real workload distribution
manufacturing/maintenance burden
```

Suppose two admissible worlds `w1,w2` have the same observable descriptor `X` but different hidden quantities `theta`. Let the nonempty sets of optimal admissible realizations be

\[
\mathcal A_i = \arg\min_R C(R;X,\theta_i), \qquad i\in\{1,2\}.
\]

The collision condition is

\[
\boxed{\mathcal A_1\cap\mathcal A_2=\varnothing.}
\]

Different named minimizers alone are insufficient. For example, cost rows `(A=0,B=0)` and `(A=0,B=1)` admit different named minimizers but share the optimal predictor `A`. This correction preserves the intended no-go result while excluding a tied-optimum counterexample.

## EF-1 — unmeasured-frontier collision theorem, tie-corrected

A deterministic **single-realization selector** using only `X` must select the same realization in both worlds. Under the disjoint-optimal-set condition, it is therefore suboptimal in at least one world.

For a randomized selector over a finite or countable registered realization set, zero suboptimality probability in each world requires probability one on each optimal set, hence probability one on their intersection. Disjointness makes this impossible.

More generally, for finitely many compatible worlds `W(X)` and tolerance `epsilon >= 0`, define

\[
\mathcal A_\epsilon(w)=\{R:C(R;w)\leq\min_Q C(Q;w)+\epsilon\}.
\]

A single realization with regret at most `epsilon` in every compatible world exists **if and only if**

\[
\boxed{\bigcap_{w\in W(X)}\mathcal A_\epsilon(w)\ne\varnothing.}
\]

The deterministic selector chooses an element of this intersection. Conversely, any uniformly acceptable selector lies in it. A randomized selector has almost-sure regret at most `epsilon` in every world exactly when its distribution assigns probability one to this intersection. The finite-world restriction avoids an invalid inference from uncountably many separate probability-one events to their joint intersection.

For more than two worlds, pairwise intersections alone are insufficient: the sets `{A,B}`, `{B,C}`, `{A,C}` overlap pairwise but have empty total intersection. A set-valued prediction can contain an acceptable realization for every world without identifying a single implementable winner; it must be reported as unresolved selection rather than point-prediction success.

Therefore a universal sign claim requires at least one of:

1. measure or bound `theta`;
2. prove the frontier ordering is invariant over the entire admissible interval of `theta`;
3. abstain / report an interval containing both regimes.

This is the exact reason physical/nonclassical superiority, real-runtime frontiers and unseen workload transfer cannot be completed by symbolic derivation alone.

## EF-2 — independent-authorship gate is not self-certifiable

If an evidence constitution requires a generator/meter/encoding to be independently authored, work produced solely by the same authoring process cannot satisfy that gate by additional self-review. It can specify the protocol, create auditable interfaces and freeze tests, but the independence event itself requires an external author/process.

This is an evidence-governance condition, not a missing mathematical lemma.

## Consequence

The recursive programme should distinguish:

```text
FORMAL GAP:
    can in principle be closed by proof/counterexample/exact computation

MEASUREMENT GAP:
    requires an external quantity whose value changes the prediction

INDEPENDENCE GAP:
    requires evidence from a separately authored process

REAL-TRANSFER GAP:
    requires untouched real tasks/episodes beyond the development ecology
```

Once a residual is classified into the last three categories with a frozen protocol, endlessly adding theory is not closure; acquiring the missing evidence is.

## Claim ceiling

This does not waive any evidence gate. It proves why those gates are irreducible without their registered external information.
