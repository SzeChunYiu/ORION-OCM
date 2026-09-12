# GMI Developmental Potential Theorems v2

Status: **FORMAL DEVELOPMENTAL-POTENTIAL HARDENING / PROSPECTIVE REAL-WORLD CALIBRATION**

Status date: 2026-09-12.

Purpose:

> Turn critical developmental burden from a definition into a set of exact composition, allocation and impossibility laws. In particular, prove why a narrow/weak standalone domain can be essential to a strong species.

---

# 1. Critical burden for independent hard obligations

Let a serious-intelligence constitution contain hard sub-obligations `O_1,...,O_m`. For species `S`, define

\[
b_j^*(S)
\]

as the minimum priced developmental burden required for `S` to satisfy the threshold on `O_j`, holding the registered composition assumptions fixed.

## Theorem DP2-1 — independent-obligation critical burden

If:

1. the sub-obligations require disjoint developmental resources/state;
2. satisfying one does not improve or damage another;
3. burdens add;

then satisfying all hard obligations requires exactly

\[
B^*_{dev}(S)=\sum_{j=1}^m b_j^*(S).
\]

If any `b_j^*(S)=infinity`, then `B^*_{dev}(S)=infinity`.

### Interpretation

A species can have excellent average capability but zero developmental viability under a constitution if one mandatory obligation is structurally unreachable.

---

# 2. Exact composition gain from a narrow module

Let broad species/module `A` face obligation set `E`. Let narrow module `B` handle subset `J subset E`. Write

```text
C_A(E)       minimum burden for A to satisfy all E
C_A(E\J)     minimum burden for A after B takes responsibility for J
C_B(J)       burden for B to satisfy J
C_comp       composition/routing/authority burden
```

## Theorem DP2-2 — narrow-module adoption criterion

The composite `A+B` has lower critical developmental burden than pure `A` iff

\[
C_A(E\setminus J)+C_B(J)+C_{comp}<C_A(E).
\]

Equivalently, the burden saved by removing `J` from `A` must exceed the cost of the narrow module plus composition:

\[
C_A(E)-C_A(E\setminus J)>C_B(J)+C_{comp}.
\]

### Strong case

If `C_A(E)=infinity` because `A` cannot satisfy one mandatory obligation in `J`, while the right-hand composite terms are finite, then adding the narrow module changes

\[
B^*_{dev}: \infty \to \text{finite}.
\]

A domain that is useless for most obligations can therefore be **necessary** for serious composite intelligence.

### Examples of the structural role

```text
broad approximate predictor + exact verifier
broad neural model + authoritative volatile memory
perception model + symbolic constraint solver
world model + exact planner/controller
language model + arithmetic/proof tool
```

The theorem is architecture-neutral.

---

# 3. Marginal developmental value and optimal resource allocation

Suppose a composite species has modules `i=1,...,k`. Allocate nonnegative developmental resource `b_i` to each module. Let weighted protected loss contribution be

\[
w_i L_i(b_i)
\]

with differentiable decreasing `L_i`, and let resource price per unit be `pi_i>0`.

Minimize

\[
\sum_i w_iL_i(b_i)
\]

subject to

\[
\sum_i\pi_i b_i\le B.
\]

## Theorem DP2-3 — equal marginal value per priced resource

For any interior optimum with active resource constraint and `b_i>0`, KKT conditions imply

\[
-\frac{w_i L_i'(b_i)}{\pi_i}=\lambda
\]

for the same multiplier `lambda` across all active modules.

### Definition — marginal developmental value

Define

\[
V_i(b_i)= -\frac{w_iL_i'(b_i)}{\pi_i}.
\]

At an optimum, active modules equalize marginal developmental value. A narrow module can deserve substantial resource if its marginal protected benefit per cost is high, even if its standalone breadth is tiny.

### Boundary rule

A module with marginal value below the active `lambda` at zero allocation receives no resource in the smooth convex case. This is a resource-allocation statement, not a domain deletion rule: its value can become positive in a different ecology or after another module changes the composition state.

---

# 4. Finite versus infinite developmental potential

For obligation `j`, let the best reachable loss under burden `b` be

\[
L_j^*(b)
\]

and threshold be `tau_j`.

## Theorem DP2-4 — irreducible-floor impossibility

If

\[
\inf_{b<\infty}L_j^*(b)>\tau_j
\]

for any mandatory obligation `j`, then

\[
B^*_{dev}=\infty.
\]

No amount of scaling within the current species realization class can satisfy the constitution.

### Consequence

This distinguishes two superficially similar failures:

```text
resource-limited:
    threshold is reachable, but B_available < B*_dev

structurally limited:
    B*_dev = infinity inside the current realization class
```

The second case calls for composition/morphogenesis/domain change, not more scaling.

---

# 5. Breadth threshold as a selection problem

Suppose there are `m` independent optional obligation families, each with equal weight, and the serious-intelligence constitution requires passing at least fraction `beta` of them. Let `c_j` be the minimum burden to pass family `j`.

## Theorem DP2-5 — equal-weight breadth burden

Let

\[
k=\lceil\beta m\rceil.
\]

If obligations are independent and no family is mandatory beyond the breadth rule, the minimum burden to satisfy the breadth requirement is the sum of the `k` smallest values among `c_1,...,c_m`.

### Proof

Any feasible species must pay for at least `k` families. Choosing the `k` cheapest is feasible and no other `k`-subset has lower sum. QED.

### Weighted extension

With nonuniform ecology weights, the problem becomes a minimum-cost coverage/knapsack problem. Thus breadth itself has a resource geometry; it should not be collapsed into a single average benchmark score.

---

# 6. Morphology-switch threshold from developmental regret

Let current morphology `A` incur future per-use burden/loss `c_A(t)` and candidate morphology `B` incur `c_B(t)` after a one-time switch/development cost `C_switch`.

## Theorem DP2-6 — exact finite-horizon switch criterion

Switching from `A` to `B` over future horizon `H` is beneficial iff

\[
\sum_{t=1}^{H}\big(c_A(t)-c_B(t)\big)>C_{switch}.
\]

For stationary per-use difference `Delta c>0`, this becomes

\[
H>\frac{C_{switch}}{\Delta c}.
\]

### Interpretation

Developmental potential depends on future horizon. A species can rationally remain structurally simple in a short-lived ecology even when a more capable morphology exists.

---

# 7. Complementarity value of a domain/module

For constitution `Theta`, define the critical burden without module family `D` as

\[
B^*_{-D}
\]

and with `D` legally available as

\[
B^*_{+D}.
\]

## Definition — developmental complementarity value

\[
\Delta_D(\Theta)=B^*_{-D}-B^*_{+D}.
\]

Interpretation:

```text
Delta_D > 0:
    access to D lowers the minimum burden to serious intelligence

Delta_D = 0:
    D is redundant at this constitution/resource scope

Delta_D = infinity:
    serious intelligence is impossible without D but finite with it
```

This is a better quantity than standalone domain strength when asking whether a narrow domain matters to a strong species.

`Delta_D` is ecology- and composition-relative and must include routing, verification and maintenance costs.

---

# 8. Development margin revisited

Given available priced burden `B_available`, retain

\[
M_{dev}=\frac{B_{available}}{B^*_{dev}}.
\]

But report it together with:

\[
(\Delta_D)_D,
\quad
(V_i)_i,
\quad
B^*_{dev},
\quad
\text{breadth},
\quad
\text{risk/retention constraints}.
\]

No single scalar should be used to prune domains before composition tests.

---

# 9. Zero-prior species-generation consequence

In a world with GMI but no historical machine architectures, the derivation procedure should therefore:

1. derive the hard/weighted obligation decomposition;
2. determine which obligations have finite critical burden under each available carrier/operator family;
3. detect structural-infinity gaps;
4. search for narrow modules that convert infinite/high burden to finite/lower burden;
5. allocate resources by marginal developmental value;
6. add composition/routing/authority burden;
7. predict morphology switches only when future regret exceeds switch cost.

This naturally generates hybrid species without assuming their historical names.

---

# 10. Claim ceiling

These results make developmental potential mathematically sharper but do not supply the real module loss curves `L_i(b)` or all real composition interactions. Those must be prospectively measured/predicted.

The key correction is formal:

> low standalone breadth is not a valid rejection criterion for a domain. What matters is its effect on the composite species' critical developmental burden and protected capability frontier.
