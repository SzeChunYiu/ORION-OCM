# Recursive GMI audit — compact symmetry, 2026-09-13

Reviewed baseline: `5622ac45d0261e8fe0a92f4209b1bb782ce43732`.

The review independently reconstructed the finite and compact averaging arguments in GG20 and tested deletion of their hypotheses. The repairs preserve a compact-group theorem under explicit barycenter and coordinate regularity assumptions. They do not claim that arbitrary physical implementation classes satisfy those assumptions.

| Stable gap ID | Counterexample to the earlier claim | Correct replacement | Evidence and status |
|---|---|---|---|
| GMI-AUDIT-SYM-01 | The finitely supported probability measures on the circle are convex and rotation-stable, but averaging an atom over the compact rotation group gives nonatomic Haar probability outside that class. No finite-support probability is rotation invariant. | Finite averaging requires G-stability and convexity. Compact averaging additionally requires that the orbit barycenter exists and is feasible; a continuous affine action on a compact convex subset of a locally convex Hausdorff space suffices. | Analytic counterexample and corrected proof in GG20 §§3.1–3.4; 528 finite subgroup-invariance checks and 32 rational-rotation separating witnesses. The theorem statement is repaired at the declared scope. |
| GMI-AUDIT-SYM-02 | On the compact convex class of all circle probability measures, the nonatomic-mass coordinate is affine and rotation invariant, yet every orbit atom has coordinate 0 and its Haar barycenter has coordinate 1. This can be either an increasing resource or a changed capability. | Continuous affine capability coordinates and lower-semicontinuous convex resource coordinates suffice. More general coordinates require their own integral/closed-sublevel compatibility theorem. | Analytic atomic/nonatomic decomposition and weak-convergence argument; 45 exact affinity calculations in a finite-atomic/Haar-mixture model. The omitted regularity is restored. |
| GMI-AUDIT-SYM-03 | For the trivial group, kernels with `P(a=1)=p in (0,1)`, constant capability and resource `rho=p` satisfy finite averaging hypotheses but have no Pareto point: `p/2` is always feasible and better. | Averaging produces a feasible no-worse representative. A Pareto starting profile yields a Pareto representative with the same coordinates. Existence of a starting Pareto profile requires a separate attainment theorem. | Analytic strict-improvement argument and 256 rational instances. GG20, the intra-family theorem, claim ledger and reduction atlas now preserve this distinction. |

An additional finite deletion witness confirms that convexity alone does not imply G-stability: `p in [0,1/4]` is convex, but the action-swap average of `p=0` is `1/2`, outside the feasible class. The unique deterministic optimum corollary now requires G-stable feasibility and an invariant selection rule explicitly.

## Proof dependencies and physical application boundary

The compact proof fixes one locally convex topology, uses continuous orbit maps and finite-probability approximants to Haar probability, obtains a feasible barycenter by compactness, and tests it against the separating continuous dual. Capability continuity preserves equalities. Resource lower semicontinuity gives `rho(bar K) <= liminf rho(K_alpha) <= rho(K)`; the closed convex resource-sublevel formulation gives the same conclusion. These are analytic statements rather than consequences of the finite checker.

Before applying GG20 to a physical morphology, establish:

- that admitted kernels and randomization resources are closed under the required averaging;
- that the group fixes every retained coordinate, rather than merely permuting ecology coordinates;
- the compact topology, measurability, barycenter existence and coordinate regularity when compact averaging is used;
- a separate attainment argument if a frontier realization is claimed.

Operational equivariance alone does not establish physical parameter sharing or a named architecture.

## Verification record

`python -m unittest discover -s research/gmi-grand-unification-v1 -p test_grand_gmi_substrate_symmetry_v1.py -v`

Result: **9 tests passed**, including the original finite symmetry/substrate checks and four new boundary tests. `GRAND_GMI_SUBSTRATE_SYMMETRY_RECEIPT_V1.json` was regenerated from the checker. `git diff --check` passed.

The compact witness code stores a declared Haar component symbolically and manipulates only finite atomic measures and exact rational weights. It does not prove Haar existence, weak convergence or properties of arbitrary infinite groups by enumeration. The 32 circle witnesses establish exact finite subgroup invariance while a further rotation has disjoint support and total variation 1; no numerical near-equality is promoted to exact compact invariance.

Primary literature consulted: [Berezin and Miftakhov, *On barycenters of probability measures*](https://arxiv.org/abs/1911.07680), especially the weak-integral definition and compact convex feasibility; and [Chen, Dobriban and Lee, *A Group-Theoretic Framework for Data Augmentation*](https://jmlr.org/papers/v21/20-163.html), especially compact Haar averaging and invariant statistical loss. The GMI-specific counterexamples and application conditions above were checked separately.
