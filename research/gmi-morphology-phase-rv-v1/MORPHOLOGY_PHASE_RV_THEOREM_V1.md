# Morphology Phase Law: R/V Axes Extension v1

Status: **formal extension of idealized morphology phase theorem to explicit resource and ecology-complexity axes.**

Refs #592 item 24, IDEALIZED_MORPHOLOGY_PHASE_THEOREM_V1.

## Motivation

The idealized morphology phase theorem (IDEALIZED_MORPHOLOGY_PHASE_THEOREM_V1) decomposes morphology burden as:

\[
C_i(N,P)=B_i+N\left[H(P)+D_{KL}(P\Vert Q_i)\right]
\]

This treats ecology E as the sole axis, with resource cost B_i as a scalar parameter and no explicit ecology-complexity dimension. In practice:

1. **R (Resource Abundance)** determines how much storage, compute, and bandwidth is available. Low R means resource pressure dominates; high R means resource cost is negligible.
2. **V (Ecology Complexity)** determines how much the ecology demands generalization. High V means the ecology is complex, uncertain, and rewards morphologies whose bias aligns with the target distribution. Low V means simple ecologies where build cost dominates.

Making R and V explicit axes turns the 1D ecology sweep into a 3D phase space (E, R, V) where morphology winners are predicted jointly.

## Definitions

### R-axis: Resource Abundance

\[
R \in \mathbb{R}_+
\]

R is a scalar representing aggregate resource availability (storage + compute + bandwidth). Higher R means more resources available, reducing resource pressure on all morphologies.

### V-axis: Ecology Complexity

\[
V \in [0, 1]
\]

V measures how complex and uncertain the ecology is. At V=0, the ecology is trivially simple and build cost dominates. At V=1, the ecology is maximally complex and ecology-bias alignment (KL penalty) dominates.

### Morphology Burden Parameterization

For morphology archetype M with bias distribution Q_M, the R/V-parameterized burden is:

\[
\mathbf{B}_M(\mathbf{E}, R, V) = 
\underbrace{B_{build}(M)}_{\text{one-time}} +
\underbrace{\frac{N}{H} \cdot D_{KL}(P\Vert Q_M) \cdot (1 + V \cdot \alpha_v)}_{\text{amortized inference, amplified by complexity}} +
\underbrace{\alpha_r \cdot \max\left(0, \frac{R_M}{R} - 1\right)}_{\text{resource pressure}} +
\underbrace{D_{adopt}(M)}_{\text{adoption cost}}
\]

where:
- \(B_{build}(M)\) is the one-time construction/training cost
- \(D_{KL}(P\Vert Q_M)\) is the ecology-bias mismatch (from the idealized theorem)
- \(R_M\) is the morphology's intrinsic resource requirement
- \(\alpha_v\) is the complexity amplification factor (how much V amplifies KL cost)
- \(\alpha_r\) is the resource pressure weight
- \(D_{adopt}(M)\) is the adoption/discovery cost

### Winner Criterion

Morphology M_i wins at \((\mathbf{E}, R, V)\) iff:

\[
\mathbf{B}_{M_i}(\mathbf{E}, R, V) = \min_{M'} \mathbf{B}_{M'}(\mathbf{E}, R, V)
\]

## Theorem 1 — Two-Morphology R/V Phase Condition

Morphology M_1 has lower burden than M_2 at \((\mathbf{E}, R, V)\) iff:

\[
\boxed{
\Delta B_{build} + \Delta B_{amort}(V) + \Delta B_{res}(R) + \Delta D_{adopt} < 0
}
\]

where:
- \(\Delta B_{build} = B_{build}(M_1) - B_{build}(M_2)\)
- \(\Delta B_{amort}(V) = \frac{N}{H}\left[D_{KL}(P\Vert Q_1) - D_{KL}(P\Vert Q_2)\right] \cdot (1 + V \cdot \alpha_v)\)
- \(\Delta B_{res}(R) = \alpha_r \cdot \left[\max\left(0, \frac{R_1}{R} - 1\right) - \max\left(0, \frac{R_2}{R} - 1\right)\right]\)
- \(\Delta D_{adopt} = D_{adopt}(M_1) - D_{adopt}(M_2)\)

### Proof

Direct from the winner criterion: M_1 wins iff \(\mathbf{B}_1 < \mathbf{B}_2\), which rearranges to the stated condition. QED.

## Theorem 2 — R/V Phase Boundary (2D Sweep at Fixed E)

Fix ecology E (hence H(P) and D_KL terms). The phase boundary between M_1 and M_2 in the \((R, V)\) plane is the curve:

\[
\boxed{
\Delta B_{build} + \frac{N}{H}\left[D_{KL}(P\Vert Q_1) - D_{KL}(P\Vert Q_2)\right] \cdot (1 + V \cdot \alpha_v) + \Delta B_{res}(R) + \Delta D_{adopt} = 0
}
\]

This is a piecewise-linear boundary with up to 2 segments (one per morphology's resource pressure becoming active).

### Corollary 1 — Corner Regimes

| Region | Condition | Winner |
|--------|-----------|--------|
| Low V, Low R | Simple ecology, scarce resources | **Symbolic/Algorithmic** (low build cost, low resource needs) |
| Mid V, Mid R | Moderate complexity, moderate resources | **Probabilistic** (moderate costs, moderate alignment) |
| High V, High R | Complex ecology, abundant resources | **Neural-like** (high build cost amortized, excellent alignment) |
| High V, Low R | Complex ecology, scarce resources | **Symbolic or Probabilistic** (resource pressure prevents neural) |

### Corollary 2 — R-axis Monotonicity

As R increases (more resources available), the winner transitions from resource-efficient (symbolic) to ecology-aligned (neural), all else equal. The crossover R* depends on V:

\[
R^*(V) = \frac{\alpha_r \cdot (R_{neural} - R_{symbolic})}{\Delta B_{build} + \frac{N}{H}\left[KL_1 - KL_2\right](1 + V\alpha_v) + \Delta D_{adopt}}
\]

### Corollary 3 — V-axis Monotonicity

As V increases (more complex ecology), the winner transitions from build-cost-efficient (symbolic) to ecology-aligned (neural), all else equal. The crossover V* depends on R:

\[
V^*(R) = \frac{B_{build}(neural) - B_{build}(symbolic) + \alpha_r(\max(0, R_{neural}/R - 1) - \max(0, R_{symbolic}/R - 1))}{\frac{N}{H}(KL_{symbolic} - KL_{neural}) \cdot \alpha_v}
\]

### Corollary 4 — Three-Morphology Phase Diagram

With three archetypes (neural, symbolic, probabilistic), the R/V plane partitions into up to three regions:

1. **Symbolic region**: V < V*_1(R) — build cost dominates
2. **Probabilistic region**: V*_1(R) < V < V*_2(R) — moderate alignment wins
3. **Neural region**: V > V*_2(R) — ecology alignment dominates

The boundaries V*_1 and V*_2 are piecewise-linear curves in the (R, V) plane.

## Held-Out Prediction Protocol

To test the R/V phase law on a disjoint ecology slice:

1. **Freeze** the morphology archetype parameters from observed ecologies.
2. **Choose** a disjoint ecology E' not used in parameter fitting.
3. **Predict**: for each (R, V) cell, compute which morphology wins before measuring.
4. **Verify**: run the actual measurement, compare predicted vs actual winner.
5. **Accuracy metric**: fraction of (R, V) cells where prediction matches actual.

With frozen archetypes on a deterministic world, held-out accuracy is 100% (the model computes from fixed parameters, not fitting data). Non-trivial prediction requires noise or parameter uncertainty.

## Information-Theoretic Bound

When resource pressure is inactive (\(\alpha_r = 0\)), the R/V phase law reduces to:

\[
D_{KL}(P\Vert Q_1) - D_{KL}(P\Vert Q_2) < \frac{B_2 - B_1}{\frac{N}{H}(1 + V\alpha_v)}
\]

At V=0 this is the idealized theorem baseline. As V increases, the threshold tightens: morphologies must have better ecology alignment to win, because the KL mismatch is amplified.

## Witness Verification

The file `phase_rv_witness.py` computes the exact phase grid for three registered archetypes on an 8x8 R/V sweep. The file `test_phase_rv.py` contains 23 unittest controls verifying:

- Phase boundary correctness at known crossover points
- Held-out prediction accuracy = 100% (frozen archetypes, deterministic world)
- Negative twins: each morphology loses where predicted
- R and V axes each independently affect the winner
- Three morphologies appear in the grid
- Edge cases at extreme R and V
- Resource and complexity pressure activation

Run: `python3 -I -B test_phase_rv.py -v`

## Terminal

```text
MORPHOLOGY_PHASE_LAW_RV_EXTENSION_DERIVED
```

This is a **formal extension**, not an ORION novelty claim. The mathematics are standard constrained optimization; the content is the morphology-specific parameterization and phase predictions.
