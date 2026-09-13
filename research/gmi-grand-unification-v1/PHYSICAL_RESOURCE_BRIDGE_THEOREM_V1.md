# Grand GMI Physical Resource Bridge Theorem V1

Status: **THEOREM WITH EXPLICIT SUBSTRATE-LAW CONDITIONS + EXACT FINITE WITNESSES**  
Date: 2026-09-12

## 1. Scope

Grand GMI determines obligation-relative semantic distinctions, causal-cut requirements and local transformation requirements. It does not manufacture the laws of thermodynamics, electronics, optics, mechanics or quantum dynamics. A physical substrate supplies those laws.

The bridge problem is therefore:

\[
(S^*,\kappa,\tau) + \mathbf P + \rho_{\mathbf P}
\quad\Longrightarrow\quad
\text{physical lower bounds and morphology frontiers}.
\]

This document formalizes that composition without equating semantic compression with thermodynamic erasure.

## 2. Distinguishability-capacity bridge

Let a semantic cut `C` require simulation of an ideal classical identity channel on `m` symbols: a single protected readout must return the chosen message exactly for every message in the alphabet. The physical boundary includes any declared receiver-side resource used in that readout. In particular, with pre-shared entanglement, the relevant received state is the transmitted carrier together with the receiver's share.

The required readout distinguishes all `m` encoded states with zero error. In particular the encoding must be injective, but injectivity alone is insufficient in a process theory such as quantum mechanics: distinct nonorthogonal states need not be perfectly distinguishable.

**GG37 — physical distinguishability theorem.** Any exact physical realization of a protected `m`-symbol identity channel must expose at least `m` physical received states distinguishable by one admissible readout under the declared resource contract.

For a binary digital carrier with `b` independent ideal logical bits and no additional message-bearing side resource,

\[
2^b\ge m,
\qquad
\boxed{b\ge\lceil\log_2m\rceil}.
\]

This bridges the Semantic Cut Theorem to physical memory/channel capacity when the implementation realizes its classical cut alphabet through that protected readout. SC-1's minimum classical alphabet size is not, by itself, a globally distinguishable code-size lower bound for arbitrary quantum implementations of a task with downstream side information. Such implementations may use different measurements for different side-information values. The exact 14-input witness in [the quantum/classical boundary audit](QUANTUM_CLASSICAL_CUT_BOUNDARY_AUDIT_V1.md) requires five classical symbols but only a four-dimensional unassisted quantum carrier. The task and its acceptable actions survive a substrate change; the optimum within a chosen message process class need not.

The exact checker verifies the binary bound for every `m=1,...,64` and enumerates every set partition through six physical microstates to confirm that semantic response classes can never outnumber available physical microstates.

## 3. Substrate resource monotones

Let a substrate theory `P` assign a proved lower-bound functional or resource monotone

\[
\mu_{\mathbf P}(R)
\]

to implementing a required physical distinction, channel or transformation `R`. If a GMI obligation proves that every adequate machine must realize requirement `R`, then every physical adequate realization obeys

\[
\rho_{\mathbf P}(M)\succeq \mu_{\mathbf P}(R).
\]

For several simultaneously necessary requirements, the valid composition rule is the one supplied by the substrate theory: additive, max-type, network-flow, spacetime-volume, free-energy, or another proved rule. GMI must not assume additivity when the physics does not provide it.

**GG38 — necessity transport theorem.** A proved GMI semantic/transformation necessity transports into a physical resource lower bound only through a declared valid substrate lower-bound map. The resulting bound is substrate dependent even when the semantic necessity is substrate invariant.

This is the formal link between `kappa/tau` and measured hardware/physics.

## 4. Conditional Landauer bridge

A common substrate law is the Landauer erasure bound. Under the conventional idealized isothermal memory-reset setting—thermal bath temperature `T`, a cyclic/symmetric memory model with `m` equiprobable distinguishable logical states and a reset to one standard logical state—the minimum ideal work/heat scale for erasing the logical uncertainty is

\[
\boxed{k_B T\ln m}.
\]

For `m=2`, this is the familiar `k_B T ln 2` scale.

Grand GMI uses this only conditionally:

> If the declared physical implementation and cycle boundary require an irreversible reset that maps `m` equiprobable protected logical states to one standard state under the standard Landauer assumptions, then the substrate law supplies the corresponding thermodynamic lower bound.

General nonequilibrium, asymmetric-energy, correlated, quantum or nonuniform memories require the appropriate generalized thermodynamic bound; the simple expression above is not universal.

**GG39 — conditional erasure bridge.** Landauer cost attaches to an actual declared physical reset/entropy-reduction operation, not merely to the existence of a smaller GMI semantic quotient.

## 5. Semantic compression is not physical erasure

A semantic quotient says that some distinctions need not be retained for the obligation. It does **not** say the hardware must erase those distinctions.

Exact parity witness:

- semantic obligation: output `z=x XOR y`;
- irreversible logical realization: `(x,y) -> z`, a four-state input mapped to two equiprobable output states, losing one logical bit for uniform inputs;
- reversible embedding: `(x,y,0) -> (x,y,x XOR y)`, which preserves the full input information while producing the identical protected semantic output.

Both have the same external GMI capability. Only the first map necessarily discards a logical distinction at that step. The reversible embedding may carry extra history/garbage state and pay memory/time costs instead. If a finite cyclic device later resets that retained information, the reset must then be accounted for at that later physical boundary.

**GG40 — semantic/thermodynamic separation theorem.** GMI semantic equivalence and semantic state reduction do not determine thermodynamic dissipation. Two response-equivalent machines can have different logical irreversibility schedules and different physical resource vectors.

This is consistent with reversible-computation results: useful computation can be embedded into logically reversible dynamics by retaining and later uncomputing history, while erasure/reset is where the conventional Landauer obligation enters.

## 6. Space–time–energy tradeoff

The parity witness gives a general morphology lesson. Avoiding immediate erasure can require retaining additional physical state. Thus an energy lower bound cannot be optimized independently of memory and time.

Grand GMI therefore keeps

\[
\rho=(E,T,M,BW,\text{matter},\text{precision},\ldots)
\]

as a vector. A reversible realization may move a point toward lower dissipation but higher memory/time; an irreversible realization may trade memory reuse against heat/work.

A scalar energy-only optimum is not the universal morphology optimum unless the other coordinates are explicitly unconstrained or scalarized.

## 7. Cyclic operation and garbage

For an indefinitely reused finite machine, retained history cannot grow without bound. The machine must eventually:

1. uncompute it reversibly using still-available correlations/inputs;
2. export it across the declared boundary;
3. store it in an expanding external resource;
4. or reset/erase it physically.

Each choice moves cost to a different registered resource coordinate/cut. Grand GMI therefore treats "garbage" as a resource-routing choice, not as free disappearance.

**GG41 — finite-cycle bookkeeping theorem.** In a declared finite cyclic implementation, information needed to make a logically irreversible step injective must eventually be uncomputed, exported, retained in a counted resource, or physically reset. It cannot vanish from the physical accounting while the substrate dynamics remain well typed.

## 8. Relation to thermodynamics of computation

Parent theory supplies the physical laws:

- Landauer (1961): erasure and heat generation in physical computation;
- Bennett (1973, 1982): reversible computation and the central role of erasure rather than measurement;
- Sagawa (2013): generalized Landauer inequalities and the distinction between logical and thermodynamic reversibility;
- Wolpert (2019): stochastic thermodynamics of computation beyond simple bit erasure.

Grand GMI does not claim those results as new. Its contribution is the typed composition:

\[
\boxed{
\text{obligation}
\to
\text{semantic distinctions/cuts/transformations}
\to
\text{physical requirements}
\to
\text{substrate resource lower bounds}
\to
\text{morphology frontier}.
}
\]

## 9. Consequence

The physical layer completes a missing bridge in the master chain. GMI can derive *what* distinctions and transformations an intelligent process must support; physical law determines *what they cost in a substrate*. Neither side can replace the other.

The theorem does not claim a universal joules-per-bit or joules-per-inference constant. Such a claim would contradict the dependence of thermodynamic cost on implementation, distributions, kinetics, control protocol and substrate boundary conditions.
