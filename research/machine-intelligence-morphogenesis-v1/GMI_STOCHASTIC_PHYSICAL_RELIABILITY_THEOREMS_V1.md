# GMI Stochastic Physical Reliability Theorems v1

Status: **FORMAL LIFECYCLE-ACCOUNTING HARDENING / EXACT PROBABILITY BASE LAWS**

Status date: 2026-09-12.

Purpose:

> Charge the repetition/readout burden required to convert a noisy stochastic physical computation into a protected reliable semantic outcome. This applies to analog, annealing, molecular, probabilistic and quantum subroutines whenever independent or controlled-repeat assumptions are valid.

---

# 1. Repeated binary stochastic computation

Suppose one run returns the correct binary answer with probability

\[
p=\frac12+\gamma,
\qquad
\gamma>0.
\]

Run the primitive independently `n` times and return the majority answer (assume odd `n` for simplicity).

Let `X_i` be indicator of a correct run. Majority fails when

\[
\frac1n\sum_iX_i\le\frac12=p-\gamma.
\]

## Theorem PR-1 — majority amplification bound

Hoeffding's inequality gives

\[
P(\text{majority failure})
\le
\exp(-2n\gamma^2).
\]

Therefore it is sufficient that

\[
\boxed{
n\ge\frac{\ln(1/\delta)}{2\gamma^2}}
\]

(up to odd-integer rounding) to drive failure probability below `delta`.

### GMI consequence

A physical primitive's useful lifecycle burden is not its single-run latency/energy alone. Protected reliability can multiply cost by a factor scaling as

\[
O(\gamma^{-2}\log(1/\delta)).
\]

when simple independent repetition is the available amplification mechanism.

---

# 2. Correlated runs do not receive the same guarantee

PR-1 assumes independent Bernoulli outcomes. If repeated runs share drift, initialization, fabrication defect or correlated environmental noise, Hoeffding's independent-trial bound does not apply.

### GMI registration requirement

Report:

```text
single-run success distribution
repeat independence/correlation evidence
reset/repreparation burden
aggregation rule
protected failure target
```

A system may not claim reliability amplification from nominal repeat count without validating the dependence assumptions.

---

# 3. Gaussian readout discrimination

Consider equal-prior binary worlds whose physical readout is

\[
Y\sim\mathcal N(-\Delta/2,\sigma^2)
\]

or

\[
Y\sim\mathcal N(+\Delta/2,\sigma^2).
\]

The optimal threshold is zero.

## Theorem PR-2 — exact single-shot Gaussian discrimination error

The Bayes error is

\[
P_e
=
\Phi\left(-\frac{\Delta}{2\sigma}\right),
\]

where `Phi` is the standard normal CDF.

### Interpretation

The relevant physical separation is signal-to-noise ratio

\[
\frac{\Delta}{\sigma},
\]

not nominal analog state precision alone.

To reach error target `delta<1/2`, the readout requires

\[
\frac{\Delta}{2\sigma}
\ge
\Phi^{-1}(1-\delta).
\]

---

# 4. Averaging repeated Gaussian readouts

For `n` independent repeated measurements of the same world, the sample mean has variance

\[
\sigma^2/n.
\]

Therefore exact Bayes error becomes

\[
P_e(n)
=
\Phi\left(-\frac{\Delta\sqrt n}{2\sigma}\right).
\]

## Corollary PR-2.1 — repeat count for Gaussian readout

It is sufficient and necessary under this equal-Gaussian model that

\[
n
\ge
\left(
\frac{2\sigma\Phi^{-1}(1-\delta)}{\Delta}
\right)^2
\]

up to integer rounding.

This gives an exact precision/reliability/repetition trade in the registered model.

---

# 5. Lifecycle phase

Suppose one physical trial costs burden vector/scalar `c_trial` plus reset/state-preparation cost `c_reset`, while a digital/alternative realization costs `C_alt` at matched error `delta`.

The physical realization is preferred only after charging

\[
n(c_{trial}+c_{reset})+c_{read/aggregate}
\]

for the required reliability level.

A spectacular single-shot wall-clock or energy number can therefore disappear after reliability amplification.

---

# 6. Reliability can also favor physical realization

The theorem is not anti-physical-computing. If one native physical operation has high margin/low noise so `gamma` is large or `Delta/sigma` is high, only a few repetitions are needed. A matched digital simulation may still be much more expensive.

The point is to compare **protected reliable outcomes**, not raw unstable trajectories.

---

# 7. Application to current domain candidates

```text
annealing / Ising:
    charge repeated runs needed to escape stochastic failure/tails

physical reservoir:
    charge readout noise and calibration repetitions

molecular/reaction:
    charge stochastic-copy/measurement uncertainty

quantum:
    charge measurement shots and state re-preparation where observable estimation requires repeats

analog/photonic:
    charge SNR, calibration and ADC/readout precision
```

Specific quantum amplitude-estimation or error-correction algorithms have different scaling and must be analyzed by their own law rather than forced through majority amplification.

---

# 8. Gap update

Physical/nonclassical lifecycle accounting now has base laws for:

```text
task-relevant precision packing                  CLOSED
binary stochastic repeat amplification          CLOSED
Gaussian readout discrimination                 CLOSED
Gaussian repeat/readout trade                   CLOSED

real device correlation/drift                   OPEN
state preparation/reset burden                  OPEN empirical
energy/latency/precision/reliability frontier   OPEN-BLOCKING
```

---

# 9. Claim ceiling

These are exact/simple probability bounds under independence/Gaussian assumptions. Real devices can have heavy tails, correlated noise, nonstationarity and structured error correction. Those must be measured rather than hidden inside nominal accuracy.
