# Grand GMI Symmetry-to-Morphology Theorem V1

Status: **THEOREM WITH FINITE / COMPACT AVERAGING HYPOTHESES AND ATTAINMENT BOUNDARY**
Date: 2026-09-13
Depends on: semantic-state refinement and semantic-cut layers.

## 1. Problem symmetry

Let a group `G` act on admissible histories/states `X`, actions `A`, environments/contexts `E`, and registered resource coordinates. A GMI problem is **G-invariant** when the obligation and every registered evaluation/resource coordinate commute with the action:

\[
L(gx,ga;ge)=L(x,a;e),\qquad \rho_i(gM)=\rho_i(M).
\]

This is a property of the declared ecology/obligation/resource problem. It is not an architectural assumption.

For a behavioral kernel `K(a|x)`, define the group action

\[
(gK)(a|x)=K(g^{-1}a\mid g^{-1}x).
\]

A kernel is equivariant iff `gK=K` for every `g in G`.

## 2. Semantic quotient inherits the symmetry

If the obligation-response profile is G-invariant, semantic equivalence is preserved by the group:

\[
x\equiv_\Omega x' \Longrightarrow gx\equiv_\Omega gx'.
\]

Therefore `G` acts canonically on the semantic quotient `S* = X / equiv_Ω`. Symmetry below semantic resolution is automatically quotiented out; symmetry that moves semantic classes remains operationally real.

**GG19 — quotient-action theorem.** Every declared problem symmetry descends to the operational semantic quotient.

## 3. Randomized symmetrization theorem

### 3.1 Finite groups

Assume:

1. the feasible behavioral-kernel set `C` is nonempty, convex and **G-stable**: `gK in C` for every `K in C` and `g in G`;
2. `G` is finite and acts affinely on kernels;
3. the objective/capability coordinates are affine in `K` and G-invariant;
4. registered resource coordinates are convex and G-invariant.

For any feasible kernel `K`, define its orbit average

\[
\bar K = |G|^{-1}\sum_{g\in G} gK.
\]

Then:

- `bar K` is feasible;
- `bar K` is G-equivariant;
- every affine G-invariant capability coordinate is unchanged;
- every convex G-invariant resource coordinate is no worse:

\[
Q_j(\bar K)=Q_j(K),\qquad \rho_i(\bar K)\le \rho_i(K).
\]

**Proof.** G-stability puts every orbit point in `C`, and convexity puts the finite average there. Multiplication by any `h in G` permutes the averaging terms, so `h bar K = bar K`. Affinity and coordinatewise invariance preserve each `Q_j`; finite Jensen's inequality and invariance give each resource inequality. QED.

Invariance here means **each retained coordinate** satisfies `Q_j(gK)=Q_j(K)`. A group that only permutes ecology-risk coordinates does not meet this hypothesis: averaging may improve one coordinate while worsening another. Likewise, closure of behavioral kernels under mixing must describe the admitted physical/randomization class, including its resource meter.

### 3.2 Compact groups

Finite convexity alone does not justify a Haar average. One sufficient compact-group version has these explicit hypotheses:

1. `G` is a compact Hausdorff group with normalized Haar probability `mu`;
2. feasible kernels form a nonempty **compact convex** subset `C` of a locally convex Hausdorff topological vector space `V`, and `G` acts continuously and affinely on `C`;
3. every retained capability coordinate `Q_j:C -> R` is **continuous**, affine and G-invariant;
4. every retained resource coordinate `rho_i:C -> R` is **lower semicontinuous**, convex and G-invariant.

The topology and its relation to legal measurable kernels are part of the declaration. The continuous action ensures measurable orbit maps; compact convex `C` ensures that their barycenters exist and remain feasible. Define the weak barycenter

\[
\bar K=\int_G gK\,d\mu(g),
\qquad
f(\bar K)=\int_G f(gK)\,d\mu(g)\quad(f\in V').
\]

It satisfies the same feasibility, equivariance, capability and resource conclusions as the finite theorem.

**Proof.** Approximate `mu` weakly by a net of finitely supported probability measures on `G`; their finite orbit barycenters `K_alpha` lie in `C`. Compactness yields a convergent subnet. Testing against each continuous linear functional identifies its limit with the displayed barycenter, and the separating dual makes that barycenter unique. Left invariance of Haar probability and the continuous affine action give `h bar K=bar K`. Finite averages obey `Q_j(K_alpha)=Q_j(K)` and `rho_i(K_alpha)<=rho_i(K)`. Continuity gives the first equality at the limit. Lower semicontinuity gives, in the required direction,

\[
\rho_i(\bar K)\le\liminf_\alpha\rho_i(K_\alpha)\le\rho_i(K).
\]

Equivalently, the convex resource sublevel set at `rho_i(K)` is closed and contains the whole orbit and its closed convex hull. QED.

Global compactness of `C` is sufficient, not necessary. It can be replaced by an explicit existence theorem placing each Haar barycenter in the **feasible closed convex orbit hull**, together with the same continuity/lower-semicontinuity and action hypotheses. Merely asserting that Haar measure exists supplies none of those closure or coordinate-regularity facts.

### 3.3 What the conclusion selects

**GG20 — symmetry-to-morphology theorem.** Under the finite hypotheses, or the compact hypotheses above, every feasible kernel has an equivariant feasible representative with identical retained capabilities and no worse resources. If the starting profile is Pareto, its representative has that same profile and is also Pareto: any strict improvement would contradict the original profile's nondominance.

This does **not** establish that a frontier exists. For example, a trivial group acting on kernels with `P(a=1)=p in (0,1)` and resource `rho=p` meets the finite hypotheses but has no Pareto point. Frontier existence needs a separate attainment result, such as GG49. Equivariance of an available frontier representative can therefore be derived conditionally from task/resource symmetry.

This theorem selects an operational symmetry class, not source syntax. A CNN, GNN, Deep Sets network, tensor program, lookup table or unknown substrate may all implement the same equivariant kernel.

### 3.4 Compact counterexamples and separating witnesses

**Failure of feasible closure.** Let `X` be a singleton, `A=G=S^1`, and let `G` rotate output probability measures. Admit precisely the finitely supported probability measures. This class is convex and G-stable, and constant capability/resource coordinates satisfy all algebraic conditions in the original statement. The Haar average of `delta_0` is uniform probability on the circle, which is not finitely supported. In fact no admitted measure is invariant: an atom of mass `c>0` would force every rotated point to have mass `c`, contradicting total mass one. Thus compactness of the group plus finite convexity does not imply an equivariant feasible representative.

**Failure of coordinate regularity even with feasible closure.** Now admit all probability measures on `S^1` with the weak topology, a compact convex class. Define `rho(nu)` as the total mass of the nonatomic part of `nu`. The unique atomic/nonatomic decomposition makes `rho` affine, convex and rotation-invariant. Each orbit atom and every finite orbit mixture costs `0`, but its Haar barycenter costs `1`. Thus convexity does not suffice for the compact resource inequality. This meter is not weakly lower semicontinuous: uniform measures on `n` equally spaced points converge weakly to Haar probability while their costs remain `0`. Using the same functional as `Q` also shows why algebraic affinity alone does not preserve compact-average capabilities.

**Finite evidence boundary.** The executable microscope represents circle positions by exact rational turns. For each `1<=n<=32`, it constructs the `n`-point orbit average, checks invariance under its finite cyclic subgroup, and separates it from its rotation by `1/(2n)`: the supports are disjoint and total variation is exactly `1`. It also calculates the nonatomic-mass meter on explicit finite-atomic/Haar mixtures. These are exact finite separating witnesses and checks of the model's algebra. They do not machine-prove Haar existence, weak convergence, or the infinite-group theorem; those follow from the analytic arguments above and the cited parent results.

## 4. Unique deterministic optimum corollary

If the feasible class is deterministic and G-stable, the registered selection rule is G-invariant, and the selected optimal deterministic kernel is unique, then uniqueness forces it to be equivariant: every `gK*` is feasible and also optimal, so uniqueness gives `gK*=K*`. Uniqueness means uniqueness of the behavioral kernel; different source programs with the same kernel do not defeat this conclusion.

**GG21 — unique-optimum corollary.** A unique deterministic optimum of a symmetric problem must respect the symmetry.

The executable microscope enumerates all nine small invariant loss tables under a simultaneous state/action swap. Six tables have a unique deterministic optimum; every such optimum is exactly equivariant.

## 5. Deterministic symmetry can fail

Symmetry does **not** imply existence of a deterministic equivariant optimum in general. If a state is fixed by the group but the action orbit has no fixed point, no deterministic equivariant policy exists at that state. An invariant problem can then have multiple symmetry-related deterministic optima while their randomized orbit mixture is equivariant.

Thus the randomized/convex condition is not cosmetic.

## 6. Resource convexity is also load-bearing

Symmetrization need not be resource-no-worse for a nonconvex resource meter. The hostile witness uses an invariant resource that rewards pure/extreme actions: deterministic policies have cost `0`, while their equivariant `1/2-1/2` mixture has cost `1/2`.

Therefore:

`SYMMETRY_IMPLIES_NO_WORSE_EQUIVARIANT_FRONTIER_REPRESENTATIVE`

is valid only with the declared G-stability, convexity/invariance and, at compact scope, barycentric-closure and coordinate-regularity conditions. Existence of any frontier remains separate.

## 7. Consequences for machine-intelligence morphology

This theorem converts familiar architecture motifs into conditional consequences:

- translation/permutation symmetry can justify shared/equivariant computation;
- exchangeable object obligations can justify permutation-equivariant kernels;
- repeated local interaction laws can justify repeated local operators;
- broken symmetries predict where tying/equivariance should stop;
- nonconvex hardware/resource costs can make deliberate symmetry breaking Pareto-optimal.

The theory therefore predicts **when symmetry should appear in an optimal operational morphology and when it need not**. It does not derive a named implementation or claim that every symmetric task has a unique symmetric deterministic architecture.

## 8. Parent boundary

Group averaging, invariant decision problems and equivariant learning are classical parents. Grand GMI claims the composition of those results with obligation-derived semantic quotients, the semantic cut spectrum, transformation complexity and physical morphology/resource frontiers. It does not relabel the parent mathematics as novel.

For primary treatments, see [Berezin and Miftakhov, *On barycenters of probability measures*](https://arxiv.org/abs/1911.07680), especially the weak-barycenter definition, the closure observation and compactness discussion; and [Chen, Dobriban and Lee, *A Group-Theoretic Framework for Data Augmentation*](https://jmlr.org/papers/v21/20-163.html), for orbit averaging in invariant statistical problems. Their settings motivate the declared regularity assumptions; neither source validates undeclared feasibility or hardware resource closure in a GMI instance.
