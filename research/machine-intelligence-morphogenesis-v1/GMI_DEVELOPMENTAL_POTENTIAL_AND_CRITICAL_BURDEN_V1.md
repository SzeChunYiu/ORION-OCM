# GMI Developmental Potential and Critical Burden v1

Status: **FOUNDATIONAL THEORY / PROSPECTIVE PREDICTION CONTRACT**

Status date: 2026-09-12.

Purpose:

> Replace vague labels such as "weak domain" with an obligation-relative theory of how far a species can develop, what resource burden is required to reach a registered intelligence threshold, and how narrow components can combine into a strong composite species.

---

# 1. Species, domain and development are distinct levels

A domain is a carrier/operator realization class. A species is a concrete developmental organism that may combine several domains. Therefore a domain that is weak in isolation may still be essential inside a strong species.

Let a species state be

\[
S=(M_1,\ldots,M_k,\Xi,\Gamma,H),
\]

where `M_i` are domain-specific modules, `Xi` their composition/authority contracts, `Gamma` the morphology-changing law, and `H` developmental history.

---

# 2. Reachable developmental set

For initial species state `S_0`, ecology `e`, legal development protocol `D`, and resource budget vector `b`, define

\[
\operatorname{Reach}(S_0,e,D,b)
\]

as the set of species states reachable by legal updates, search, interventions, compilation and morphogenesis whose total lifecycle development burden does not exceed `b`.

The key object is not current capability but **reachable future capability**.

---

# 3. Protected capability envelope of a species

For protected obligation family `E` and outcome vector `Y`, define

\[
\mathcal C_S(E,b)
=\sup_{S'\in\operatorname{Reach}(S_0,E,D,b)}
Y_{protected}(S';E).
\]

For a scalarized registered adequacy score `Q_E` this becomes

\[
C_S(E,b)=\sup_{S'\in\operatorname{Reach}}Q_E(S').
\]

This is a budget-indexed development curve, not a single intrinsic IQ.

---

# 4. Serious-intelligence threshold is registered, not universal

A registered serious-intelligence constitution is

\[
\Theta=(E,\mu,q_*,\beta_*,r_*,\pi),
\]

where:

```text
E      protected ecology/obligation distribution
mu     weighting over obligations/families
q_*    minimum adequacy per admitted obligation
beta_* required breadth/coverage fraction
r_*    maximum protected risk/failure burden
pi     resource-price/scalarization map
```

For budget vector `b`, define breadth

\[
B_S(b)=
\mu\{e\in E:C_S(e,b)\ge q_*(e)\}.
\]

Species `S` satisfies the constitution at budget `b` iff

\[
B_S(b)\ge\beta_*,
\]

all required risk constraints hold, and every hard constitutional obligation is admissible.

There is no universal threshold independent of ecology and resource prices; no-free-lunch prevents such a domain-free scalar.

---

# 5. Critical developmental burden

Define the **critical developmental burden**

\[
B^*_{dev}(S;\Theta)
=
\inf\{\pi^\top b:
S\text{ can satisfy }\Theta\text{ within }b\}.
\]

If no legal finite development reaches the threshold,

\[
B^*_{dev}=\infty.
\]

This is the cleanest scalar answer to

> "Can this species develop serious intelligence?"

under a registered constitution.

Given available priced budget `B_avail`, define the dimensionless development margin

\[
M_{dev}(S;\Theta)
=
\frac{B_{avail}}{B^*_{dev}(S;\Theta)}.
\]

Interpretation:

```text
M_dev > 1   threshold is reachable within available resources
M_dev = 1   boundary
M_dev < 1   threshold not reachable within current resource context
M_dev = 0   B*_dev = infinity / structurally impossible at registered scope
```

This margin is constitution-relative, never universal.

---

# 6. Developmental potential spectrum

A scalar threshold can hide mechanism. Therefore report the vector

\[
\Pi_S=(C_{now},C_{best},\eta,B^*_{dev},B_{breadth},R_{adapt},R_{ret},R_{risk}),
\]

where:

```text
C_now       current protected capability
C_best      best proven/reachable capability under registered horizon
eta         local resource elasticity of protected improvement
B*_dev      critical developmental burden
B_breadth   obligation breadth at target budget
R_adapt     adaptation burden under ecology shift
R_ret       retention/lineage burden
R_risk      protected failure / false-adoption burden
```

`eta` may be estimated locally as

\[
\eta=-\frac{d\log L}{d\log R}
\]

only in regimes where a smooth scaling law is empirically supported.

---

# 7. Theorem DP-1 — a weak component domain can be necessary for a strong species

Let an obligation decompose into independent protected sub-obligations

\[
O=(O_A,O_B)
\]

with additive loss

\[
L=L_A+L_B.
\]

Suppose domain family `A` can achieve

\[
L_A\le \epsilon_A
\]

but every pure-`A` realization satisfies

\[
L_B\ge \delta_B
\]

with

\[
\epsilon_A+\delta_B>L_*.
\]

Suppose a narrow domain family `B` can realize only `O_B`, with

\[
L_B\le\epsilon_B
\]

and a composition `A\oplus B` preserves the `A` result while adding `B`, with

\[
\epsilon_A+\epsilon_B\le L_*.
\]

Then no pure-`A` species can meet the serious-intelligence threshold `L_*`, while the composite species can.

### Proof

Immediate from the two inequalities. QED.

### Consequence

A domain may have low standalone breadth and still be indispensable to a high-breadth species. Therefore **never prune domains solely by standalone capability**.

Examples of possible narrow but essential roles include exact proof checking, authoritative factual memory, high-precision arithmetic, verification, or intervention control.

---

# 8. Theorem DP-2 — development threshold as reachability

Let `A_Theta` be the set of species states satisfying constitution `Theta`. Then

\[
B^*_{dev}(S;\Theta)
=
\inf_{S'\in A_\Theta}\operatorname{CostReach}(S_0\to S').
\]

Thus developmental potential is formally a shortest-path / optimal-control problem in developmental-state space, with update/search/morphogenesis actions as edges and lifecycle burden as edge cost.

This allows lower bounds from information, search, communication, verification and construction constraints to lower-bound `B^*_{dev}`.

---

# 9. Structural impossibility vs empirical weakness

A species/domain is **structurally below threshold** only when a theorem or certified lower bound proves

\[
C_S(E,b)<q_*
\]

for all registered legal `b`, or proves `B^*_{dev}=\infty`.

Finite scaling curves alone cannot prove this because finite observations do not identify asymptotic ceilings without structural assumptions.

Use these labels instead of `weak domain`:

```text
NARROW-BUT-ESSENTIAL
RESOURCE-INEFFICIENT-AT-SCOPE
HARD-CEILING-PROVED
LOW-ELASTICITY-OBSERVED
NICHE-SPECIALIST
REDUCED-TO-PARENT
OPEN-POTENTIAL
```

---

# 10. Prediction requirements

Before expensive scaling of a candidate species, GMI should predict:

```text
P1  whether B*_dev is finite under registered constitution
P2  a bracket/lower-upper bound on B*_dev
P3  which burden coordinate dominates near threshold
P4  which domain/module becomes the bottleneck
P5  whether another domain becomes necessary before threshold
P6  capability gain from adding each narrow component
P7  negative twin where that component becomes unnecessary
P8  expected crossover against known species
```

Protected experiments then test these predictions.

---

# 11. Claim ceiling

The theory now has a formal value for obligation-relative developmental viability:

`B*_dev` and the derived margin `M_dev`.

It does not claim a universal scalar threshold for "serious intelligence" independent of ecology, risk constitution and resource prices.