# Cross-paradigm potential/drift reduction v1

Status: **exact calibration + parent subtraction.**

## Result

Three deliberately different toy morphology families from the previous Track-B calibration can be written in the same first-hitting form once each family supplies its natural potential.

### Program search

Let `X_t=1` while the target program has not yet been proposed and `0` after success. If each independent proposal succeeds with probability `q`, then

\[
E[X_t-X_{t+1}\mid X_t=1]=q,
\]

so the exact expected first-hit time is

\[
E[T]=1/q.
\]

For the registered morphologies this gives `4` versus `16` proposals.

### Bayesian update

Let the potential be the remaining log-odds gap to a frozen posterior-confidence threshold. In the exact toy, each observation supplies a fixed log-likelihood-ratio increment `delta=2`, so

\[
T=\Phi_0/\delta,
\]

giving `2` versus `4` observations.

### Quadratic gradient descent

Let the potential be the remaining log-error gap to the registered error tolerance. Under the chosen quadratic/contraction fixture each step reduces that potential by exactly `delta=2`, yielding `4` versus `18` gradient steps.

## Common form

All three can therefore be represented as

\[
\boxed{T\approx \Phi_0/\delta}
\]

in the registered constant-drift coordinates.

This is useful conceptually: a morphology defines both

```text
where the target starts in its own developmental coordinates (Phi_0)
how much useful progress its legal update/search step makes (delta)
```

and ecology changes which targets/coordinates matter.

## Why this is not GMI novelty

This is precisely the territory of additive/multiplicative/variable drift and first-hitting-time analysis.

The hard part is not the theorem

```text
potential + drift -> hitting time
```

but obtaining a **useful pre-outcome potential and drift from actual machine structure**.

For arbitrary Markov processes, one can even use expected remaining hitting time itself as a perfect potential, which makes a post-hoc “geometry” definition tautological.

Therefore the cross-paradigm result earns the terminal:

```text
CROSS_PARADIGM_POTENTIAL_DRIFT_FORM_EXACT__DRIFT_ANALYSIS_PARENT_SUFFICIENT
```

## Stronger residual

The surviving scientific object is a restricted map

\[
\Psi(M,H,E)
\to
(\widehat\Phi_0,\widehat\delta,\widehat C,\widehat P)
\]

computed from morphology structure, legal history and pre-target ecology features, where:

- `Phi_0` predicts target mismatch/surprisal;
- `delta` predicts useful progress per legal update/search action;
- `C` predicts raw resource cost per action;
- `P` predicts plasticity/retention under repeated development.

A useful theory must predict these quantities before protected outcomes and should do so without a complete simulator of the learner.

## Connection to known paradigms

Likely parent-specific constructions include:

```text
program/search    Phi ~ code/search surprisal; delta ~ proposal hazard / search progress
Bayesian           Phi ~ posterior/log-odds gap; delta ~ expected information gain
neural             Phi ~ loss/error/parameter mismatch; delta ~ curvature-conditioned optimization progress
symbolic/proof     Phi ~ proof/subgoal obligation; delta ~ expected heuristic/search reduction
evolutionary       Phi ~ fitness/distance potential; delta ~ mutation-selection drift
OCM                Phi ~ proposal/search burden; delta ~ history-induced rank/probe/search gain
```

The labels differ, but drift theory only becomes predictive after those paradigm-specific mappings are supplied.

## Decisive next question

Can Track B derive a **shared restricted signature family** from structure that predicts `Phi/delta/cost` across at least two morphology paradigms better than each paradigm's simple baseline?

If not, the honest terminal is:

```text
NO_USEFUL_CROSS_PARADIGM_STRUCTURE_TO_DRIFT_SIGNATURE_AT_SCOPE
```

and the general theory should remain a parent-backed metrology framework rather than a new law of intelligence.
