# Adaptive row creation — ARC-7

Parents: [ARC-1–4](../gmi-adaptive-row-confidence-v1/ADAPTIVE_ROW_CONFIDENCE_THEOREM_V1.md),
[ARC-6](../gmi-countable-row-corrigendum-v1/FORMALIZATION_V1.md).
Issue #655 / #602 M / #592 item 32. Date: 2026-09-14.

**Scope:** rows created dynamically during observation, adaptive creation policy,
countably many creation steps, conditional fixed row laws, bounded scores in
[0,1], predictable sampling. **Evidence:** P1 written proof, P3 conditional
probability bound, P2 exact numerical certificates and small-world controls.

ARC-6 fixes the countable-creation stationary-weight case. ARC-7 adds the
missing piece: the agent decides *when* to create rows based on observed data,
and the confidence event remains valid simultaneously over every row at every
visit, including rows born after the process starts.

## 1. Setting and notation

Fix alpha in (0,1) before any observation. A filtration (F_t) for integer
t >= 0 contains every revealed outcome, controller choice and source of
randomness. Row creation indices j = 1, 2, ... are unique and never recycled.

Row j is born at a stopping time tau_j (possibly infinite); only finitely many
rows are born by any finite t. Its conditional mean mu_j in [0,1] and its
finite alphabet are F_tau_j-measurable and frozen thereafter. At step t >= 1,
select R_t from already-born rows or select no row, using only F_(t-1). If
R_t = j, a score X_t in [0,1] is received with

    E[X_t | F_(t-1)] = mu_j    on {R_t = j}.

The conditional-mean premise is load-bearing. Global iid sampling, independent
row choices, and a finite potential set of row meanings are not required.
The creation policy pi: (F_(t-1)) -> {born rows} union {none} is part of the
model, not an assumption about its form.

## 2. Geometric budget allocation

Reserve at each step t >= 1 a creation budget

    alpha_t = alpha / [t(t+1)].

The telescoping identity sum_{t=1}^T 1/[t(t+1)] = T/(T+1) gives

    sum_{t=1}^infty alpha_t = alpha    (exact).

If row j is born at step t_j, its per-row confidence budget is alpha_j = alpha_t_j.
Rows born at the same step share their slot's budget (at most one creation per
step). If no row is born at step t, the budget alpha_t is unused; it is not
reallocated. The total budget across all rows ever created is at most alpha.

This is strictly more conservative than ARC-6's fixed index allocation
w_j = 1/[j(j+1)] because the geometric allocation must cover the *possibility*
of creation at every step, not merely the rows that are actually created.
ARC-7 therefore subsumes ARC-6 as a special case (pre-committed creation
schedule).

## 3. Per-row e-process

For a row born at step t_j, define its post-birth visit times T_{j,n} and
empirical mean hat_mu_{j,n} as in ARC-6. For any fixed lambda, conditional
Hoeffding for [0,1] variables gives

    E[exp(lambda (X_s - mu_j)) | F_(s-1)] <= exp(lambda^2 / 8)

on steps s where R_s = j. Hence

    M_j(n) = exp(lambda S_{j,n} - lambda^2 n / 8)

is a nonneg supermartingale at attained visits n, where S_{j,n} = sum of
(X_s - mu_j) over the first n post-birth visits. This is a standard
Hoeffding-type e-process: under the conditional-mean null, M_j is a
supermartingale starting at 1.

Choosing lambda = 4e for the upper tail and lambda = -4e for the lower tail,
conditional Markov gives

    P(T_{j,n} < infinity and |hat_mu_{j,n} - mu_j| > e) <= exp(-2ne^2).

Set the per-row radius e_j(n) so that

    2 exp(-2n e_j(n)^2) <= alpha_j / [n(n+1)]

for n >= 1, with e_j(0) = 1. This is the same per-row certificate as ARC-6
with alpha_j = alpha_t_j substituted.

## 4. ARC-7 theorem [P1/P3]

With probability at least 1 - alpha, for every row j ever created, at every
finite attained post-birth visit n,

    TV(P_j, hat_P_{j,n}) <= e_j(n),

simultaneously, where the quantifier ranges over all creation indices, all
visit counts, and all realizations of the creation policy.

**Proof.** Condition on the birth history (tau_1, ..., tau_J) for any finite J.
For each created row j with budget alpha_j, the per-row e-process bounds

    P_j(failure at some visit n) <= sum_{n>=1} alpha_j / [n(n+1)] = alpha_j.

The last equality uses the telescoping identity. Taking the union over all J
created rows:

    P(union failure) <= sum_{j=1}^J alpha_j <= sum_{t=1}^infty alpha_t = alpha.

The first inequality is subadditivity. The second holds because each alpha_j
equals alpha_{t_j} for its creation step, and distinct rows have distinct
creation steps. The bound is uniform in J, the creation policy pi, and the
choice of which row to sample at each step. QED.

**Consequence.** The single event G = {all rows within radii at all visits}
satisfies P(G) >= 1 - alpha. Every finite data-dependent stopping time,
row-selection policy, and comparison made from these simultaneously valid
intervals can use them together under the inherited ARC-2 / FMT transfer.
Data-dependent transformations need their own deterministic soundness argument
but not an additional union over already covered choices.

## 5. Comparison with ARC-1-4 and ARC-6

| Property | ARC-1-4 | ARC-6 | ARC-7 |
|---|---|---|---|
| Row register | Fixed before data | Countably infinite, fixed order | Adaptive, data-dependent |
| Budget per row | alpha w_r | alpha / [j(j+1)] | alpha / [t_j(t_j+1)] |
| Total budget | sum w_r <= 1 | sum 1/[j(j+1)] = 1 | sum 1/[t(t+1)] = 1 |
| Creation policy | None (pre-registered) | Pre-declared order | Adaptive (data-dependent) |
| Per-row shrinking | Yes (fixed register) | Yes (fixed j) | Yes (fixed t_j) |
| Simultaneous event | Yes | Yes | Yes |
| Requires budget allocation | Yes (alpha w_r) | Yes (alpha/j(j+1)) | Yes (alpha/t(t+1)) |

ARC-7 is the most general. When the creation policy is nonadaptive (e.g.,
create row j at step j), it reduces to ARC-6. When the register is fully
pre-committed, it reduces to ARC-1-4.

## 6. Boundaries and limitations

**No infinite-horizon guarantee.** G covers all finite attained visits; it gives
no sure safety, no nontrivial infinite-horizon risk bound, and no bound on
unbounded cumulative deployment cost.

**Creation budget is a proof tool, not a deployment constraint.** The geometric
allocation is chosen so that its sum is exactly alpha regardless of how many
rows are created. A process that creates rows at every step spends the full
budget; one that creates none spends zero. Both are valid.

**Conditional-mean premise remains load-bearing.** Reusing a cached draw,
drifting conditional means, or omitting support outcomes violates the hypothesis.
A metadata field claiming freshness cannot prove it.

**No physical sampler certification.** The theorem covers the mathematical
event; it does not authenticate the physical process generating observations.

**Countable, not uncountable.** The argument covers countably many creation
steps; uncountably many independently indexed rows are not covered.

## 7. Verification

`test_row_creation.py` has 15 controls: telescoping identities, per-row
certificate validity, simultaneous confidence under adaptive creation, uniform
allocation failure, unlimited-horizon checks at T = 10, 100, 1000, and
negative controls. `row_creation_witness.py` provides exact computation on a
small Bernoulli world with dynamic row creation. These are finite P2 checks;
none is advertised as an exhaustive proof over an infinite process.
