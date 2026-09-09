# Literature saturation addendum V2 — lifetime advice, costly prediction, and objective specification

**Status:** parent-map closure for the post-Phase-2B R0B lane / no novelty claim /
no ML authorization.

The earlier literature passes saturated the common decision-theory, state
abstraction, online-investment, early-exit and proof-scheduling parents.  The
randomized unknown-horizon result exposed a narrower remaining question: what
future-lifetime information is structurally useful, how robustly can it be used,
and when is acquiring it worth its complete cost?

A second issue then separated from lifetime prediction entirely: a controller
cannot be called price-independent if the resource objective itself has not been
registered.

## A. Advice complexity: ask how much future information is actually necessary

Classical online algorithms with advice measure the information about the future
needed to achieve a target competitive ratio.  For ordinary ski rental, the
optimal static rent/buy decision can be encoded by one bit.  More recent
**untrusted advice** work explicitly studies the robustness/consistency tradeoff
when that bit or larger advice string may be wrong.

Direct parent:

- Angelopoulos, Dürr, Jin, Kamali & Renault, *Online Computation with Untrusted
  Advice*, ITCS 2020 / JCSS 2024.  For ski rental they give a Pareto-optimal
  single-bit advice algorithm and lower bounds on trusted/untrusted tradeoffs.

Adopted OCM consequence:

```text
first identify the decision region or loss distinction the advice must convey;
do not train a full-horizon predictor merely because H is the hidden variable.
```

`LIFECYCLE_ADVICE_GATE_V1.md` instantiates this parent on the exact finite R0B
threshold matrix.

## B. Learning-augmented online algorithms: prediction must retain a fallback

The learning-augmented literature uses predictions without abandoning an online
worst-case guarantee.

Direct parents include:

- Purohit, Svitkina & Kumar, *Improving Online Algorithms via ML Predictions*,
  NeurIPS 2018;
- Gollapudi & Panigrahi, *Online Algorithms for Rent-Or-Buy with Expert Advice*,
  ICML 2019;
- Wang, Li & Wang, multi-shop ski rental with learned predictions, AAMAS/NeurIPS
  2020 line;
- Shin, Lee, Lee & An, randomized learning-augmented multi-option ski rental,
  ICML 2023 and later TOALG;
- Sun et al., *Online Algorithms with Uncertainty-Quantified Predictions*, ICML
  2024.

Adopted OCM consequence:

```text
an empirical lifetime predictor, if one is ever admitted, must be compared with
an exact robust advice-conditioned parent; prediction failure must fall back to
a protected exact strategy rather than becoming authority.
```

## C. Costly predictions: prediction acquisition is itself metareasoning

The most directly relevant parent for DEV6/X1-style accounting is:

- Drygala, Nagarajan & Svensson, *Online Algorithms with Costly Predictions*,
  AISTATS 2023.

Their framing makes three questions algorithmic even in ski rental:

```text
whether to ask for a prediction
when to ask for it
how many predictions to ask for
```

They explicitly analyze delaying a prediction query so that short instances can
finish without paying the prediction cost.

Adopted OCM consequence:

`PAID_HORIZON_INFORMATION_PROTOCOL_V1.md` treats a lifetime signal as a paid
cognitive action and implements the exact finite analogue:

```text
use inverse for d demands;
only if the session survives, acquire Z;
condition the remaining switch decision on Z;
charge acquisition on the surviving paths.
```

A predictor that saves search work but costs more to acquire is a negative result,
not a successful router.

## D. Bayesian/distributional horizon state: survival updates the prior for free

Recent distributional ski-rental work makes the posterior state explicit.

Direct parent:

- Kang, Park & Fan, *Learning-Augmented Ski Rental with Discrete Distribution: A
  Bayesian Approach*, AAAI 2026.  The discrete Bayesian rule conditions on the
  episode having survived to the current day and compares purchase with expected
  remaining rental burden.

Additional 2026 work studies full distributional predictions and robust handling
of unknown-quality distributional advice.  These are later-stage robustness
parents; they do not establish that OCM currently owns a lawful lifetime prior.

Adopted OCM consequence:

```text
age/survival is already a free observation;
P(H | H>d) is the baseline posterior;
a new signal gets credit only for decision value beyond that posterior.
```

`DISTRIBUTIONAL_LIFECYCLE_STATE_V1.md` also proves an important correction: the
single probability

```text
P(eventual semantic-static-win)
```

is not generally a sufficient Bayes state.  Two priors can have the same region
probability and require disjoint optimal switch thresholds.  A larger model on
that same scalar cannot repair the representation loss.

## E. Blackwell/value of information remains the signal-comparison language

A candidate signal is useful because it lowers protected decision risk, not
because it carries many Shannon bits.  If `Z_2` is a garbling of `Z_1`, Blackwell
comparison says `Z_1` can simulate every `Z_2` policy before acquisition cost.

The exact finite OCM quantity is

```text
R_K(pi,0) = sum_z min_tau sum_H pi_H K(z|H) C_tau(H).
```

Then

```text
gross VOI = R_0(pi) - R_K(pi,0)
net VOI   = gross VOI - complete signal cost.
```

Perfect horizon identity supplies an upper bound.  If even perfect information
cannot repay acquisition under a registered objective, terminate before feature
engineering.

## F. Objective uncertainty is not prediction uncertainty

The R0B experiments publish raw resources because no universal exchange rate has
been established.  This creates a separate decision-context variable:

```text
w = prospectively registered resource price / objective.
```

For candidate raw vector `C` and static-arm vectors `A,B`, the elementary robust
identity proved in `PRICE_OBJECTIVE_CONFLICT_V1.md` is

```text
sup_{w>=0,w!=0} (w.C)/min(w.A,w.B)
 = max_i C_i/min(A_i,B_i).
```

Basis prices make the worst-coordinate bound necessary as well as sufficient.
Therefore the coordinate-stacked minimax game is exactly the robust game over
all nonnegative linear scalarizations.

The frozen donor contains a real objective conflict: even with **perfect horizon
knowledge**, a price-blind randomized one-way threshold has certified optimum
above 1.05 at H=5,6,7, peaking near 1.163222 at H=6.

Adopted OCM consequence:

```text
do not ask a learned model to infer an unstated objective.
Either register w prospectively or report Pareto/robust-price results.
```

This is logically orthogonal to whether H is predictable.

## G. Revised saturation map

The current R0B problem now decomposes into mature parent questions:

```text
future target identity / structure
  -> legal-feature regret floor / ordinary algorithm selection only if payable

unknown effective lifetime
  -> randomized online stopping, advice complexity, Bayesian survival state

possible lifecycle forecast
  -> Blackwell/value of information + robust/untrusted advice

forecast acquisition
  -> costly-prediction metareasoning

unspecified resource objective
  -> Pareto / robust scalarization; register objective rather than predict it

misspecified lifetime model
  -> robust fallback / calibration / distribution shift, not confidence authority
```

This pass is saturated enough to stop searching for a new named mechanism.  The
remaining work is machine-specific admission:

```text
Where would a legitimate effective-lifetime prior or signal come from?
When is it observable?
Does it predict the cost-relevant posterior state rather than a convenient label?
Does its net value survive complete acquisition/lifecycle cost?
Which objective is actually registered?
```

Until those questions have source custody, the learned-router lane remains
closed.
