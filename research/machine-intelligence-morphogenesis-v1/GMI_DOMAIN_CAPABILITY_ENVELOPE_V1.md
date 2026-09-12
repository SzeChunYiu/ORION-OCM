# GMI Domain Capability Envelope v1

Status: **PROSPECTIVE QUANTITATIVE THEORY / CALIBRATION PROGRAMME**

Status date: 2026-09-12.

Purpose:

> Predict how capable each structural machine-intelligence domain can become under resources and ecology, including domains that remain intrinsically weak, narrow or uneconomic even when scaled.

---

# 1. Capability is a frontier, not a scalar

For domain `D`, ecology/obligation descriptor `X`, developmental history `H`, and resource budget vector `b`, define the domain capability envelope

\[
\mathcal C_D(X,H,b)
=
\sup_{M\in D:\rho(M)\preceq b}
Y_{protected}(M;X,H).
\]

Equivalent loss form:

\[
\mathcal L_D^*(X,H,b)
=
\inf_{M\in D:\rho(M)\preceq b}
L_{protected}(M;X,H).
\]

`b` should include at least:

```text
development compute
data/labels
search/tuning
interventions
memory/storage
communication
serving compute/latency
update/maintenance
verification
human effort
energy
precision
external tools/substrates
```

---

# 2. Multi-dimensional capability vector

Report at least:

\[
Y=(Q,Gen,Rob,Adapt,Ret,Exact,Cal,Transfer,Serve,Update,Risk),
\]

where:

```text
Q        protected task adequacy
Gen      held-family generalization
Rob      perturbation/distribution robustness
Adapt    adaptation speed/burden
Ret      retention/lineage preservation
Exact    exactness/certifiability when relevant
Cal      uncertainty/evidence calibration
Transfer cross-task/ecology reuse
Serve    serving efficiency
Update   maintenance/update efficiency
Risk     protected failure / false-adoption burden
```

No universal scalar ordering is assumed.

---

# 3. Domain scaling response

For scalar resource coordinate `R` within a frozen regime, fit competing monotone response laws such as

\[
L_D(R)
=
L_{\infty,D}+A_DR^{-\alpha_D}
\]

only where empirically justified.

Interpretation:

```text
L_inf      apparent irreducible/structural floor in the registered ecology
alpha      resource elasticity / scaling exponent
A          finite-resource difficulty
```

Do not assume power laws universally. Compare against logarithmic, exponential-to-floor, thresholded, piecewise and saturating alternatives.

Modern neural scaling studies are calibration parents, not universal templates.

---

# 4. Weak-domain taxonomy

A structurally distinct domain can be weak in several different ways.

## W1 — hard semantic ceiling

\[
L_{\infty,D}>L_{required}.
\]

Even unlimited registered resources within the native domain cannot reach required adequacy without importing another domain.

## W2 — poor scaling elasticity

\[
\alpha_D\approx0
\]

or marginal capability gain per additional burden approaches zero too early.

## W3 — prohibitive constant burden

The domain eventually performs well but only after a startup/development cost that is never amortized in realistic horizons.

## W4 — exponential/combinatorial blow-up

For some ecology coordinate `n`,

\[
\rho_D(n)\in\Omega(c^n)
\]

while a competing domain is polynomial/subexponential.

## W5 — narrow-niche intelligence

High capability exists only on a small ecology region.

## W6 — fragile intelligence

Performance collapses under remint, noise, distribution shift, damage or substrate repricing.

## W7 — non-transferable intelligence

The domain repeatedly relearns rather than amortizing developmental state.

## W8 — verification/precision bottleneck

The domain's raw capability is high but admissibility cost dominates.

---

# 5. Domain capability ceiling must be predicted pre-outcome

For ecology descriptor

\[
X=(\Psi(O),P,H),
\]

GMI should predict a distribution over envelope parameters:

\[
p(\Theta_D\mid X),
\]

where `Theta_D` may include:

```text
asymptotic floor/ceiling
scaling exponent(s)
threshold/crossover resources
memory exponent
communication exponent
search branching factor
update interference coefficient
transfer coefficient
verification burden
robustness sensitivity
```

Post-hoc curve fitting does not count as predictive theory.

---

# 6. Capability dominance and catch-up test

For domains `A,B`, define a registered resource path `b(t)`.

If

\[
\mathcal C_A(X,b(t))<\mathcal C_B(X,b(t))
\]

for all protected `t` and theory predicts no finite crossover under the allowed resource class, then `A` is dominated on that ecology.

If a crossover exists,

\[
t^*=\inf\{t:\mathcal C_A(X,b(t))\ge\mathcal C_B(X,b(t))\},
\]

predict `t*` before protected evaluation.

This directly answers whether a weak domain merely needs scaling or is structurally disadvantaged.

---

# 7. Cross-domain scaling matrix

For every registered domain, estimate response to independent interventions in:

```text
problem size
sample/data size
compute
memory
communication
query volume/reuse
update rate
intervention availability
verification price
precision requirement
noise
regime-shift hazard
```

The output is a domain × ecology scaling tensor, not one curve.

---

# 8. Existing-domain calibration predictions

These are initial directional hypotheses to freeze and attack.

## D1 coefficient/function-field

Expected strengths:

```text
regularity compression
amortized prediction
hardware-efficient dense computation
neural subclass can scale broadly
```

Expected weaknesses:

```text
volatile local facts can require global update
exact compositional obligations may be inefficient
large training capital
```

## D2 exemplar/memory-indexed

Expected strengths:

```text
near-zero-cost local insertion
high fidelity for stored instances
rapid factual updates
```

Expected weaknesses:

```text
storage/query burden grows with retained exemplars
interpolation quality depends on metric/index
poor abstraction unless augmented
```

Prediction: capability improves sharply with coverage but may saturate on extrapolation/compositional transfer.

## D3 probabilistic-belief

Expected strengths:

```text
uncertainty/evidence integration
latent alternatives
calibrated decisions
```

Expected weaknesses:

```text
inference complexity can explode with graph/treewidth/latent dimension
model misspecification ceiling
```

## D4 symbolic/program

Expected strengths:

```text
exactness
compositional reuse
verification
systematic extrapolation under correct rules
```

Expected weaknesses:

```text
acquisition/search brittleness
noisy high-dimensional perception
combinatorial induction
```

## D5 search/frontier

Expected strengths:

```text
test-time deliberation
exact/near-exact combinatorial reasoning
anytime behavior with verifier/evaluator
```

Expected weaknesses:

```text
branching-factor explosion
latency
poor repeated-query economics without compilation
```

Prediction: capability is highly elastic to inference budget until frontier explosion dominates.

## D6 dynamical-state

Expected strengths:

```text
history compression
online control
continuous temporal adaptation
```

Expected weaknesses:

```text
stability/observability limits
long-term information retention
sensitivity to state dimension/noise
```

## D7 collective/distributed

Expected strengths:

```text
parallel information acquisition
private/local knowledge integration
fault/niche specialization
```

Expected weaknesses:

```text
communication lower bounds
coordination failure
Byzantine/authority costs
```

## D8 morphogenetic/self-rewriting

Expected strengths:

```text
regime-shift adaptation
structural plasticity
long-life ecology matching
```

Expected weaknesses:

```text
search/switch cost
meta-overfitting
verification of self-change
slow benefit amortization
```

These directional statements are not closed until quantitative response laws survive held-domain/held-ecology tests.

---

# 9. Capability estimation experiment design

For each domain `D`:

1. choose canonical strong parent implementations;
2. generate ecology factorials varying one hypothesized structural advantage at a time;
3. allocate logarithmically spaced resource budgets;
4. tune each domain with equal legal information and charged search;
5. fit response laws on D/V ecologies;
6. freeze envelope and crossover predictions;
7. evaluate on protected ecology families and resource ranges;
8. inspect residuals for systematic structure;
9. refine theory only on a fresh protected split.

---

# 10. Extrapolation discipline

No “scale forever” claim is accepted from a finite range.

A capability extrapolation must include:

```text
model uncertainty over functional form
credible/confidence interval
known bottleneck coordinates
possible phase transition
out-of-range warning
negative twin
```

Scaling laws are useful empirical regularities, but architecture/domain-specific deviations are expected.

---

# 11. Capability potential of an undiscovered domain

For a newly generated carrier/operator family before full training, predict a prior capability envelope from structural descriptors:

\[
\hat \Theta_D=f_{GMI}(Z,\mathcal A,\Psi(O),P,H).
\]

Descriptors may include:

```text
state capacity / distinguishability
composition depth
native locality
parallelism
update locality
uncertainty representation
exactness
search branching
communication requirement
memory growth
precision sensitivity
self-modification capacity
```

The purpose is to decide whether the candidate is likely:

```text
strong general domain
strong niche domain
weak but structurally distinct domain
dominated/reducible realization
```

before expensive scaling.

---

# 12. Weak-domain prediction challenge

Create synthetic ecologies where GMI predicts a candidate domain is structurally valid but weak.

Examples:

```text
memory-indexed domain on smooth extrapolative function families
search domain under huge branching factor and weak heuristic
collective domain under extreme communication prices
morphogenetic domain in stationary short-lifetime ecology
symbolic domain under noisy unstructured high-dimensional perception
coefficient domain under high-volatility exact provenance-heavy facts
```

Success means predicting both **where the domain loses** and the shape/cause of its loss.

---

# 13. Domain capability scorecards

For each domain publish:

```text
best protected capability by ecology
resource response curves
asymptotic/finite-range ceiling estimate
scaling elasticity
crossover points
niche width
transfer coefficient
robustness profile
adaptation/retention profile
full lifecycle Pareto frontier
prediction error vs observed envelope
```

---

# 14. Theory closure condition

A domain's capability theory is provisionally closed at registered scope only when:

```text
C1 held-resource interpolation is accurate
C2 held-resource extrapolation stays within frozen uncertainty
C3 held-ecology niche/crossover predictions survive
C4 negative twins behave as predicted
C5 strongest parent implementations are included
C6 systematic residual structure is absent at registered resolution
C7 domain reductions/compilers are accounted for
```

Terminal:

`DOMAIN_CAPABILITY_ENVELOPE_CLOSED_AT_REGISTERED_SCOPE`

---

# 15. Claim ceiling

Current allowed claim:

> GMI now defines a quantitative programme for predicting domain capability ceilings, scaling response, niche width and structural weakness.

Not allowed yet:

```text
existing-domain capability envelopes are calibrated
new-domain capability can be predicted accurately
asymptotic ceilings have been established empirically
all resource scaling laws are power laws
```
