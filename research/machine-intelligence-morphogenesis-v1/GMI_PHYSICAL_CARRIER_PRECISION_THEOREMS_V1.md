# GMI Physical-Carrier Precision Theorems v1

Status: **FORMAL RESOURCE-ACCOUNTING HARDENING / DOMAIN-NOVELTY CLAIM BOUNDARY**

Status date: 2026-09-12.

Purpose:

> Prevent analog, physical and molecular carriers from hiding arbitrary information in unpriced real-valued precision. Any resource/domain comparison involving continuous state must register the precision needed for the protected semantic obligation.

---

# 1. Scalar precision packing bound

Let a scalar state `x` lie in interval `[0,1]`. Suppose a decoder must reconstruct `x` to worst-case absolute error at most `epsilon`, with

\[
0<\epsilon<\frac12.
\]

## Theorem PC-1 — finite codebook lower bound

Any finite codebook supporting worst-case error at most `epsilon` requires at least

\[
N_\epsilon\ge\left\lceil\frac{1}{2\epsilon}\right\rceil
\]

distinct code states.

Hence at least

\[
B_\epsilon
\ge
\left\lceil
\log_2\left\lceil\frac1{2\epsilon}\right\rceil
\right\rceil
\]

bits are required.

### Proof

Each code state with reconstruction value can cover at most an interval of length `2epsilon`. Covering an interval of total length 1 therefore requires at least `1/(2epsilon)` reconstruction balls. QED.

### Interpretation

One analog scalar is not one free unit of infinite semantic state. Its effective information capacity depends on the precision required and physically supportable.

---

# 2. Multi-dimensional continuous state

Let state lie in unit cube `[0,1]^d` and require worst-case `L_infinity` reconstruction error at most `epsilon` per coordinate.

## Corollary PC-1.1

At least

\[
\left\lceil\frac1{2\epsilon}\right\rceil^d
\]

distinguishable code states are required, hence at least

\[
d\log_2\left(\frac1{2\epsilon}\right)
\]

bits up to integer rounding.

Thus precision burden grows linearly in dimension and logarithmically in inverse tolerance in this simple geometry.

---

# 3. Semantic precision can be much lower than physical precision

Suppose protected obligation depends only on a quotient `q(x)` with `M` possible semantic outcomes. Then exact semantic state needs only

\[
\lceil\log_2M\rceil
\]

bits regardless of finer physical distinctions.

### GMI consequence

Physical carriers should be metered at **task-relevant precision**, not automatically at either ideal real precision or raw device resolution.

This links physical accounting to the semantic quotient theorem.

---

# 4. Precision-sensitive computation can erase apparent analog advantage

Suppose an analog computation maps input to scalar output `y`, but the protected decision separates two legal worlds whose outputs differ by only `Delta`.

## Theorem PC-2 — decision resolution requirement

Any observation/readout method with worst-case absolute error at least `Delta/2` cannot guarantee distinguishing the two worlds.

Therefore a claimed analog capability advantage relying on differences of scale `Delta` must include the resource burden required to preserve and read out precision finer than `Delta/2`.

### Negative twin

If the protected decision only depends on a coarse sign/threshold with a large margin, fine analog precision may be unnecessary; low-precision physical realization can then retain a genuine energy/latency advantage.

---

# 5. Molecular/concentration state accounting

If `m` molecular concentration variables each range over a bounded interval and each requires task-relevant precision `epsilon_i`, the product packing argument yields required distinguishable semantic/measurement capacity at least approximately

\[
\sum_{i=1}^m \log_2\frac1{2\epsilon_i}
\]

bits when all coordinate distinctions are independently required.

If only a lower-dimensional reaction invariant/quotient matters, the semantic bound should use that quotient instead.

---

# 6. Analog versus digital lifecycle comparison

A fair GMI burden vector for a physical/analog candidate must include, where applicable:

```text
state preparation / sensing
precision/noise control
calibration and drift correction
physical evolution time
energy
spatial area/material
readout / digitization
repeat trials needed for reliability
update/reconfiguration
verification/authority
```

A digital parent must be charged its own corresponding costs, but neither side may receive infinite precision for free.

---

# 7. Substrate advantage is not automatically domain advantage

If a physical carrier and a digital/program parent implement the same semantic state/operator law with different constants in energy/latency, that supports a **substrate/resource realization distinction**.

A new structural domain requires a stronger result: under the registered precision/reliability semantics, the parent cannot match the candidate within the accepted H0-H3 overhead class or capability frontier.

---

# 8. Implications for current candidates

```text
analog/photonic:
    must expose task-relevant precision/noise/ADC-DAC burden

reaction/molecular:
    must expose concentration precision, stochastic kinetics and sensing/readout

physical reservoir:
    must expose state-estimation/readout/calibration burden

energy/Ising:
    must expose coupling precision, annealing/repeat reliability and readout

quantum:
    separate nonclassical theory applies, but state preparation, measurement and error correction still belong in lifecycle burden
```

---

# 9. Claim ceiling

These are elementary information/geometry lower bounds. They do not prove physical computing is inefficient or reducible in all regimes. They remove one common loophole: apparent infinite information density from ideal real-valued state.
