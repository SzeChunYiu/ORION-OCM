# Objective information and price conflict — a separate lower bound from horizon uncertainty

**Status:** exact finite lower-bound reduction / no ML / no claim that deployment
must be price-blind.

## 1. Why this note is necessary

R0B reports raw resource coordinates before scalarization.  Phase 2B2 then asked
for one threshold distribution that is robust across the registered coordinates.
That is a valid price-independent research parent, but it combines two different
unknowns:

```text
H = effective future lifetime / demand uncertainty
w = resource objective / exchange-rate specification
```

`H` is a world variable that may genuinely be unknown at runtime.  `w` is usually
a design-time objective that should be frozen prospectively.  If `w` is not
registered, the scientific result is a Pareto/robust-price statement, not a
reason to train a predictor for `w`.

This note proves that the two uncertainties are distinct in the frozen donor.

## 2. Exact robust-price identity

Fix one realized horizon `H`.  Let a candidate policy have nonnegative expected
raw cost vector

```text
C in R_+^d
```

and let the two static exact arms have raw vectors `A,B`.  Assume every registered
benchmark coordinate is positive.  For a nonzero nonnegative price vector `w`,
compare the candidate with the better static arm under that price:

```text
rho_w(C;A,B) = (w.C) / min(w.A, w.B).
```

Define coordinate ratios

```text
rho_i = C_i / min(A_i,B_i)
alpha = max_i rho_i.
```

### Theorem 2.1 — robust price ratio equals the worst coordinate ratio

```text
sup_{w>=0, w!=0} rho_w(C;A,B)
=
max_i C_i / min(A_i,B_i).
```

### Proof

For every coordinate,

```text
C_i <= alpha min(A_i,B_i).
```

Multiply by `w_i>=0` and sum:

```text
w.C
<= alpha sum_i w_i min(A_i,B_i)
<= alpha min(w.A,w.B),
```

because the coordinatewise minimum vector is componentwise no larger than both
`A` and `B`.  Therefore `rho_w <= alpha` for every nonnegative `w`.

Now choose basis price `w=e_j` for any coordinate `j` attaining `alpha`.  Then

```text
rho_{e_j} = C_j / min(A_j,B_j) = alpha.
```

So the upper bound is attained and equality holds. QED.

### Consequence

The coordinate-stacked game in `RANDOMIZED_TIME_ONLY_MINIMAX_V1.md` is not merely
a sufficient conservative proxy.  For the declared class of **all nonnegative
linear scalarizations**, it is the exact robust-price game.

For a randomized threshold distribution `p`, use its expected raw vector `C(p)`;
the same identity applies by linearity of expectation.

## 3. Perfect horizon does not eliminate objective conflict

Suppose the controller is told the exact realized horizon before choosing its
threshold distribution, but is not given/frozen a price vector.  For each `H`
solve

```text
G(H)
 = min_p max_r
     E_{tau~p}[ C_{r,tau}(H) ]
     / min(I_r(H), S_r(H)).
```

By Theorem 2.1 this is exactly the best competitive ratio at that horizon against
**all** nonnegative linear price vectors, inside the current randomized one-way
threshold family.

The frozen source-derived donor gives:

| H | exact robust-price minimax | optimal threshold mixture |
|---:|---:|---|
| 1 | 1.000000 | tau=1 |
| 2 | 1.000000 | tau=2 |
| 3 | 1.000000 | tau=3 |
| 4 | 1.033708135 | 0.048833 at tau=0; 0.951167 at tau=4 |
| 5 | **1.161619762** | 0.375566 at tau=0; 0.624434 at tau=5 |
| 6 | **1.163222032** | 0.660921 at tau=0; 0.339079 at tau=6 |
| 7 | **1.095289088** | 0.864525 at tau=0; 0.135475 at tau=7 |
| 8 | 1.004075212 | ~0.995594 at tau=0; ~0.004406 at tau=8 |
| >=9 | 1.000000 on the frozen range | tau=0 |

The worst perfect-horizon robust-price value is therefore

```text
max_H G(H) = 1.1632220323971705 at H=6.
```

Thus the frozen `1.05` joint terminal is **impossible** for a price-blind
controller at horizons 5, 6 and 7 even if a perfect oracle reveals `H` for free.

This is a lower bound on objective specification, not on prediction quality.

## 4. Primal/dual witness at the hardest horizon

At `H=6`, the optimal candidate mixes

```text
P(tau=0) = 0.6609209900682271
P(tau=6) = 0.33907900993177287.
```

Its normalized coordinate ratios are

```text
transitions                 1.1632220323971705
arithmetic additions        1.0182746574435606
arithmetic multiplications  1.1632220323971705.
```

A matching dual adversary mixes only the two basis-price coordinates

```text
transitions                 0.3390790099317728
arithmetic multiplications  0.6609209900682271.
```

with value `1.1632220323971705`.  Weak duality plus the matching value certifies
optimality of the finite game.  `PRICE_OBJECTIVE_CONFLICT_CERTIFICATE_V1.json`
freezes the H=5/6/7 primal/dual witnesses, and `price_conflict_verify.py`
recomputes them from the source-derived regime artifact without importing an LP
solver.

## 5. Interpretation: do not ask ML to infer an unstated objective

There are two legitimate experiment designs.

### Registered scalar objective

Freeze `w` before outcome.  Then compare policies under that declared objective,
while still publishing raw resources.  Horizon information may have value under
that objective and can be studied using `PAID_HORIZON_INFORMATION_PROTOCOL_V1.md`.

### No single scalar objective

Do not pretend there is one universal winner.  Report Pareto dominance/frontiers
or the robust-price minimax result.  The `H=5..7` lower bound is then a real
multiobjective conflict.

What is *not* legitimate is to choose `w` after seeing which policy won, or to
train a selector whose hidden purpose is to reproduce an unstated retrospective
scalarization.

## 6. State-sufficiency consequence

The registered decision context should be written as

```text
sigma = (V, s, d, objective)
```

where `objective` includes either a frozen price vector or an explicitly declared
Pareto/robust criterion.  Omitting it can alias states that have disjoint optimal
action sets under different objectives.

This is the same feature-collision theorem already used for observations: if two
objectives induce disjoint optimal strategy sets while the policy cannot
distinguish the objectives, no larger policy model can be optimal for both.

## 7. Research ordering correction

The Phase 2B2 value `1.559190999...` should now be interpreted as the cost of
**both** unknown horizon and robust price ambiguity.  A perfect horizon oracle
can reduce the robust-price worst case only to `1.163222032...`; the remaining
~16.3% is not horizon-prediction opportunity.

Therefore:

```text
first:  freeze/declare the resource objective, or accept Pareto/robust-price output
then:   value lawful lifetime information under that objective
then:   charge prediction/signal cost
last:   consider learned lifetime prediction if a payable residual remains
```

This prevents a learned router from being credited for solving an ill-posed
objective rather than a genuinely hard decision problem.

## 8. Research terminal

For the price-independent 1.05 claim, the correct terminal is now

```text
PRICE_OBJECTIVE_CONFLICT_BEFORE_LEARNING_R0B
```

This does not kill R0B.  It sharpens the next experiment: choose the actual
objective prospectively, then measure the value of horizon information under it.
