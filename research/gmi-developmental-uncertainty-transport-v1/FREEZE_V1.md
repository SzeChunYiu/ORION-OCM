# #748 freeze — developmental uncertainty transport V1

Date: 2026-09-15. Parent ledger: #602 section M. Child issue: #748.

This is the pre-implementation authority. No executor, scored receipt, or hostile test for this tranche exists on this branch before this commit.

## Claim boundary

Target only:

```text
SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE
```

This tranche may prove that a confidence/set-valued uncertainty object can be transported through a preregistered developmental relation without losing its inherited coverage except for explicitly budgeted transition-relation failure. It may also prove that, without such a relation, the only generally sound target set is the full registered target domain.

It may not claim a learned G7 developmental predictor, universal calibration, physical sample freshness, validity of a misspecified relation, raw-evidence inheritance, real-world developmental accuracy, or that developmental uncertainty is small.

## Strongest parents

No novelty is claimed over set-valued analysis, interval analysis, reachable-set propagation, elementary confidence-set image logic, or the union bound. In-repository source confidence remains owned by ARC-6 / #655 and the replay-resistant F1 adapter / #657. The registered developmental change labels are owned by #628 `research/gmi-developmental-taxonomy-v1/`.

Literature anchors to cite in the formalization:

- R. E. Moore, *Methods and Applications of Interval Analysis* (set-valued mappings / rigorous interval enclosures);
- J.-P. Aubin and H. Frankowska, *Set-Valued Analysis*;
- M. Althoff, G. Frehse and A. Girard (2021), *Set Propagation Techniques for Reachability Analysis*, Annual Review of Control, Robotics, and Autonomous Systems 4:369–395.

## Frozen theorem DT-1 — exact relation image preserves source coverage

Let `theta_0` take values in registered domain `X_0`. Let random set `C_0 subseteq X_0` satisfy

```text
P(theta_0 in C_0) >= 1-alpha.
```

For developmental step `t`, preregister a relation

```text
R_t subseteq X_(t-1) x X_t.
```

If the true transition satisfies `(theta_(t-1), theta_t) in R_t` surely, define recursively

```text
C_t = R_t(C_(t-1))
    = { y in X_t : exists x in C_(t-1) with (x,y) in R_t }.
```

Then, for every finite registered chain,

```text
P(theta_t in C_t for all t <= T) >= 1-alpha.
```

No independence is required. The result can be conservative; it is a coverage theorem, not a sharpness theorem.

## Frozen theorem DT-2 — uncertain relations and failure-budget composition

For each step `t`, let `H_t` be the event that the true transition belongs to the registered relation `R_t`, with

```text
P(H_t^c) <= beta_t.
```

No independence among `C_0`, `H_1`, ..., `H_T` is assumed. Then

```text
P(theta_t in C_t for all t <= T)
>= 1 - alpha - sum_(t=1)^T beta_t.
```

If a countable sequence uses the frozen allocation

```text
beta_t = beta / [t(t+1)],  t=1,2,...
```

then `sum_t beta_t = beta`, so every finite attained developmental step is simultaneously covered with probability at least

```text
1 - alpha - beta.
```

The executor will only account for registered failure budgets; it does not manufacture or empirically validate the events `H_t`.

## Frozen theorem DT-3 — ignorance is the full target domain

Suppose the only registered information about an update is

```text
theta_(t-1) in X_(t-1),
theta_t in X_t
```

with no restriction coupling source to target. Equivalently the admissible relation is `X_(t-1) x X_t`. For every nonempty source set, its relational image is exactly `X_t`.

Therefore a missing transition relation must not copy the source set forward. The fail-closed target uncertainty set is the full target domain. A downstream Boolean/query decision is identifiable only if it is constant on that full set; otherwise terminal is `CANNOT_IDENTIFY_NO_RELATION`.

Nearest false generalization: keeping `C_t=C_(t-1)` across an arbitrary developmental change can have zero target coverage even when source coverage is one.

## Frozen theorem DT-4 — no evidence inheritance

Transported objects contain a target uncertainty set and confidence-failure budget only. They do not inherit raw observations, visit counts, sums, tokens, or origin IDs from the source developmental version. Any target-version empirical update must enter through the target version's own registered evidence mechanism.

This complements #657 RR-5: #657 forbids silent statistical evidence inheritance; #748 provides the separate mechanism by which an explicitly registered semantic relation can transport a **set-level claim**.

## Frozen registration semantics

A `TransportCampaign` has:

```text
source_version
source_domain
source_failure_budget alpha
registered developmental contracts
locked flag
```

Every `TransportContract` freezes before source activation:

```text
name
from_version
to_version
change_kind in {INFO, RECODE, SKILL, LAW, MORPH}
source_domain
target_domain
finite relation R
relation_failure_budget beta_t
```

Rules:

1. all domains and relation pairs are finite exact tuples of `Fraction` values;
2. every relation source is in the source domain and every target is in the target domain;
3. every source-domain point must have at least one registered successor for a registered relation;
4. versions form the registered chain exactly; skips/back-edges are rejected in V1;
5. transport contracts are frozen before `activate_source`;
6. after source activation, contract registration/modification is rejected;
7. source uncertainty must be a nonempty subset of source domain;
8. propagation never copies source evidence counters;
9. a missing next relation returns the full supplied target domain with `CANNOT_IDENTIFY_NO_RELATION` and does not claim a relation-failure budget;
10. all failure budgets are exact `Fraction`s in `[0,1]`; total reported failure is capped at 1.

## Frozen exact A3 five-kind chain

Use exact source domain and confidence set

```text
X0 = {-2,-1,0,1,2}
C0 = {-1,0,1}
alpha = 1/20
```

Register, before source activation, these exact zero-beta developmental relations:

### INFO v0 -> v1

```text
X1 = {-1,0,1,2,3}
y = x + 1
```

Expected image: `{0,1,2}`.

### RECODE v1 -> v2

```text
X2 = X1
y = x
```

Expected image: `{0,1,2}`. This is an abstract-content-preserving recode control.

### SKILL v2 -> v3

```text
X3 = {-1,0,1,2,3,4}
y in {x, x+1}
```

Expected image: `{0,1,2,3}`.

### LAW v3 -> v4

```text
X4 = {-2,-1,0,1,2,3,4,5}
y in {x-1, x, x+1}
```

Expected image: `{-1,0,1,2,3,4}`.

### MORPH v4 -> v5

```text
X5 = {0,1,4,9,16,25}
y = x^2
```

Expected image: `{0,1,4,9,16}`.

Expected failure budget remains exactly `1/20` through all five exact relations. Every target object's raw/inherited evidence count is zero.

## Frozen interval-affine exact control

Implement a separate exact interval helper for

```text
x in [1/4, 3/4]
y in -2*x + 3 + [-1/10, +1/10].
```

Expected smallest interval hull:

```text
[7/5, 13/5].
```

The test must independently enumerate the four endpoint/error corners and reproduce the same extrema. This is a deterministic set enclosure only; no probability is assigned to the additive error interval.

## Frozen nonlinear finite-relation control

For

```text
C = {-1,0,1}
y in {x^2-1, x^2, x^2+1}
```

expected exact image is

```text
{-1,0,1,2}.
```

This prevents the implementation from only handling affine maps.

## Frozen uncertain-relation budget controls

With source `alpha=1/20`, two registered uncertain relations having

```text
beta_1 = 1/100
beta_2 = 1/200
```

must report cumulative failure budget

```text
1/20 + 1/100 + 1/200 = 13/200
```

and coverage lower bound `187/200`.

For countable allocation with `beta=1/20`, exact arithmetic must verify for every tested `N` that

```text
sum_(t=1)^N beta/[t(t+1)] = beta*N/(N+1) < beta,
```

including `N=1,2,5,1000`, and report infinite-horizon combined lower bound

```text
1 - 1/20 - 1/20 = 9/10.
```

## Frozen ignorance and identifiability controls

With no registered next relation and target domain `{0,1,2}`, propagation must return exactly `{0,1,2}` with terminal `CANNOT_IDENTIFY_NO_RELATION`.

For query `q(x) = (x > 0)`, this full set is nonconstant and therefore `CANNOT_IDENTIFY`.

For constant query `q(x)=True`, the result may be `IDENTIFIED_TRUE` even on the full domain; this demonstrates that ignorance about state does not imply ignorance about every query.

## Frozen adversarial controls

At minimum the suite must demonstrate:

1. post-source-activation relation registration is rejected;
2. an incomplete relation omitting a source-domain point is rejected;
3. out-of-domain relation endpoints are rejected;
4. version skips/back-edges are rejected;
5. malformed budgets (`<0`, `>1`, float) are rejected;
6. source uncertainty outside the source domain is rejected;
7. exact zero-beta relations preserve the source failure budget;
8. uncertain relation budgets add by union bound and never use independence;
9. no relation returns the full target domain rather than copying the source set;
10. a counterexample shows source-set copying can fail completely: source truth/set `{0}` with certainty, target domain `{0,1}`, actual arbitrary update to `1`; copied set `{0}` misses with probability one while the full target domain covers;
11. every A3 change kind appears in the exact chain and produces the frozen image;
12. finite relational-image implementation matches an independently enumerated comprehension on a rational test family;
13. interval-affine helper matches exhaustive corner enumeration;
14. nonlinear finite relation matches the frozen exact image;
15. transported objects expose zero inherited/raw evidence;
16. normal Python and `python -O` produce the same deterministic receipt.

## Frozen falsifiers

This tranche fails if any of the following occurs:

- a target outside the registered relational image is omitted while being admissible under the frozen relation;
- reported failure budget is smaller than `alpha + sum beta_t` without a separately proved shared-event argument;
- any proof invokes independence between source and transition-relation events;
- a missing relation copies the source interval/set instead of returning the full target domain;
- raw visits/sums/tokens/origins are inherited into a new version;
- a post-activation transport relation is accepted;
- the five-kind chain disagrees with the frozen exact images;
- interval output misses an enumerated corner;
- optimized mode changes the receipt;
- wording upgrades the result to G7 or to empirical transition-law calibration.

No #602 checkbox is to change merely because this freeze exists. Closure requires implementation, exact/adversarial tests, proof formalization, deterministic receipt reproduction, repository CI, merge, and checklist reconciliation.