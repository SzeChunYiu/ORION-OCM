# Grand GMI Symmetry-to-Morphology Theorem V1

Status: **THEOREM WITH EXPLICIT CONVEXITY/UNIQUENESS CONDITIONS**  
Date: 2026-09-12  
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

Assume:

1. the feasible behavioral-kernel set `K` is convex;
2. `G` is finite (or compact with a normalized Haar measure);
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

Hence every attainable behavioral point has an equivariant representative that is Pareto-no-worse under these conditions.

**GG20 — symmetry-to-morphology theorem.** At convex randomized behavioral scope, problem symmetry implies existence of an equivariant frontier representative. Equivariance/weight sharing can therefore be *derived* from task/resource symmetry rather than inserted as an architecture prior.

This theorem selects an operational symmetry class, not source syntax. A CNN, GNN, Deep Sets network, tensor program, lookup table or unknown substrate may all implement the same equivariant kernel.

## 4. Unique deterministic optimum corollary

If the feasible class is deterministic, the problem is G-invariant, and the optimal deterministic kernel is unique, then uniqueness forces it to be equivariant: every `gK*` is also optimal, so uniqueness gives `gK*=K*`.

**GG21 — unique-optimum corollary.** A unique deterministic optimum of a symmetric problem must respect the symmetry.

The executable microscope enumerates all nine small invariant loss tables under a simultaneous state/action swap. Six tables have a unique deterministic optimum; every such optimum is exactly equivariant.

## 5. Deterministic symmetry can fail

Symmetry does **not** imply existence of a deterministic equivariant optimum in general. If a state is fixed by the group but the action orbit has no fixed point, no deterministic equivariant policy exists at that state. An invariant problem can then have multiple symmetry-related deterministic optima while their randomized orbit mixture is equivariant.

Thus the randomized/convex condition is not cosmetic.

## 6. Resource convexity is also load-bearing

Symmetrization need not be resource-no-worse for a nonconvex resource meter. The hostile witness uses an invariant resource that rewards pure/extreme actions: deterministic policies have cost `0`, while their equivariant `1/2-1/2` mixture has cost `1/2`.

Therefore:

`SYMMETRY_IMPLIES_NO_WORSE_EQUIVARIANT_FRONTIER_REPRESENTATIVE`

is valid only with the declared convexity/invariance conditions.

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