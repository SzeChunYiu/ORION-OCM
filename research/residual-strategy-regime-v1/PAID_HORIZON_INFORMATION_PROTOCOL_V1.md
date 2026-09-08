# Paid horizon information — protocol and exact decision calculus for R0B

**Status:** prospective protocol / exact finite decision theory / no lifetime
predictor registered / no ML authorization.

## 1. Research question

Phase 2B established that elapsed time plus private randomization leaves a large
unknown-lifetime gap, while cold target-specific legal features leave very little
economic regret.  The next question is therefore not "which target is this?" but:

```text
Is there any lawful observation Z available before the investment decision that
contains useful information about how long reusable state will remain valuable,
and is buying/maintaining Z cheaper than the work it avoids?
```

This protocol treats a forecast as a **paid cognitive action**, not free input.
It adopts standard Bayesian decision/value-of-information reasoning, Blackwell
comparison of experiments, and the costly-prediction perspective from online
algorithms.

No OCM-specific novelty is claimed for those parent theories.

## 2. What counts as effective lifetime

Let `H` be the number of demands that arrive before the current reusable semantic
state becomes unusable for the declared reason.  A terminal event can be:

- normal session completion;
- reset/restart;
- invalidation or scope drift;
- revocation of the state/certificate that permits reuse;
- process/runtime loss if no admissible restore preserves the contract.

Nominal wall-clock uptime is not the target.  The target is **remaining protected
reuse opportunity before invalidation**.

The event definition must be frozen before collecting or scoring a signal.
Different invalidation semantics define different random variables and must not
be silently pooled.

## 3. Current admission status

`FROZEN_PROTOCOL_V1.json` provides a synthetic IID target population and
prospective reset/checkpoint sweeps.  It does **not** register an empirical or
operational distribution for session termination/invalidation, nor a lawful
forecast channel for it.

Therefore the current empirical terminal for this lane is:

```text
DEMAND_SIGNAL_SOURCE_NOT_ESTABLISHED_R0B_PHASE2C0
```

This is a data/admission terminal, not a claim that horizon information has no
value.

Synthetic priors may be used only for theorem/unit tests and hostile sensitivity
analysis.  They may not be described as deployment evidence.

## 4. Exact no-signal Bayes parent

For one registered resource objective, let the exact one-way threshold cost from
`RANDOMIZED_TIME_ONLY_MINIMAX_V1.md` be

```text
C_tau(H).
```

Let a prospectively frozen lifetime prior be

```text
pi_H = P(H=H),  H in {1,...,M}.
```

With no observation other than elapsed survival, every deterministic time-only
one-way policy is characterized by its first switch time `tau`; randomization
cannot improve fixed-prior expected cost because expected cost is linear in the
mixture over `tau`.

The exact Bayes risk is therefore

```text
R_0(pi) = min_tau sum_H pi_H C_tau(H).
```

This is the first parent to beat.  Do not compare a predictor only with always
inverse or always semantic.

### Proposition 4.1 — randomization does not improve fixed-prior Bayes risk

For any distribution `p_tau`,

```text
sum_tau p_tau [sum_H pi_H C_tau(H)]
```

is a convex combination of deterministic threshold risks and hence is at least
their minimum. QED.

This does not contradict Phase 2B2: randomization helped there because the
objective was minimax over an unknown/adversarial horizon, not Bayes expectation
under one fixed prior.

## 5. A prospective horizon signal

A finite signal channel is a kernel

```text
K(z|H) = P(Z=z | H),
```

where `Z` is observed legally before the relevant switch decision.

The channel is a *model of a prospectively observable variable*.  It is not
permission to peek at future `H`.  Every proposed `Z` must specify:

```text
source system / field
observation time
acquisition path
what information is unavailable at that time
calibration/training split
invalidation/drift semantics
raw acquisition/inference/storage/update costs
```

A future-outcome label, evaluation-run identifier, target fingerprint lookup, or
post-hoc session length is not a legal signal.

## 6. Exact value of a free signal at session start

For a free signal, after observing `z` the controller chooses the best threshold
for the conditional population.  It is convenient to avoid explicit posterior
normalization and write the joint Bayes risk as

```text
R_K(pi,0)
  = sum_z min_tau sum_H pi_H K(z|H) C_tau(H).
```

The gross value of information is

```text
VOI_K(pi) = R_0(pi) - R_K(pi,0).
```

### Theorem 6.1 — information cannot hurt when it is free and ignorable

```text
VOI_K(pi) >= 0.
```

**Proof.**  Let `tau_0` minimize the no-signal risk.  For each signal outcome,

```text
min_tau sum_H pi_H K(z|H) C_tau(H)
<=
sum_H pi_H K(z|H) C_{tau_0}(H).
```

Sum over `z` and use `sum_z K(z|H)=1`.  The right side becomes `R_0(pi)`.
QED.

### Perfect-horizon upper bound

The identity signal `Z=H` gives

```text
R_perfect(pi) = sum_H pi_H min_tau C_tau(H).
```

Every signal is a garbling of perfect horizon identity, so

```text
R_perfect(pi) <= R_K(pi,0) <= R_0(pi).
```

Thus

```text
R_0(pi) - R_perfect(pi)
```

is the absolute gross upper bound on what *any* horizon signal could save inside
the current threshold action family before signal costs.

This is the first number to compute after a legitimate lifetime prior is frozen.
If it is tiny, stop before building a predictor.

## 7. Predictions are paid cognitive actions

Let acquisition/inference cost of one signal query be raw resource vector
`c_Z`.  For a prospectively registered scalar price vector `w`, the paid risk is

```text
R_K(pi,c_Z) = w.c_Z + R_K(pi,0).
```

At session start, buying the signal is economically justified only if

```text
VOI_K(pi) > w.c_Z.
```

For raw-vector reporting, publish both the avoided-work vector and the signal
cost vector; do not choose `w` after seeing results.

A predictor can be decision-useful yet economically dominated.  This is exactly
the distinction exposed by DEV6 and X1.

## 8. Delay before asking for a signal

A mature costly-prediction parent asks a stronger question: perhaps the system
should **wait** before paying for a prediction.  Many sessions will end before
the signal is needed.

Fix delay `d>=0`.  The controller uses inverse for the first `d` demands.  If the
session ends by then, no signal is purchased.  If `H>d`, it pays for `Z` and then
chooses an additional one-way threshold `tau_z` on the residual lifetime
`H-d`.

For scalar signal cost `c`, the exact expected cost is

```text
R_{K,d}(pi,c)
 = sum_{H<=d} pi_H I(H)
 + sum_z min_tau [
       sum_{H>d} pi_H K(z|H)
         ( I(d) + c + C_tau(H-d) )
   ].
```

The `c` term appears only on paths that survive to acquisition.  Equivalently it
is weighted by `P(H>d)`.

The best policy in the family that may ignore the signal entirely is

```text
R_optional(pi,K,c)
 = min( R_0(pi), min_d R_{K,d}(pi,c) ).
```

This formalizes three separate decisions emphasized in the costly-predictions
literature:

```text
whether to ask
when to ask
what action to take after the answer
```

All three are metareasoning decisions and all costs must be charged.

## 9. Conditional survival is already information

Reaching age `d` reveals the event `H>d`.  Therefore the legal posterior before
buying any additional signal is

```text
P(H=h | H>d) = pi_h / P(H>d),  h>d.
```

A predictor must beat a baseline that already exploits this free survival
information.  It must not be credited for merely rediscovering that a session
which is still alive at age `d` did not end earlier.

For non-memoryless lifetime distributions, this posterior can materially change
remaining-horizon economics.  For memoryless distributions it may not.

## 10. Signal comparison and Blackwell order

If signal `Z_2` is generated by garbling `Z_1` without looking at `H` again, then
`Z_1` is Blackwell-more-informative.  With equal acquisition cost, its optimal
Bayes risk cannot be larger because the controller may simulate/ignore the extra
information.

This gives a clean engineering rule:

- do not compare signals by mutual information alone;
- compare **decision risk after the signal**;
- then subtract complete signal lifecycle cost.

A high-bit signal can have zero decision value, and a low-bit signal can be
valuable if it crosses the investment boundary.

## 11. Robustness / misspecification gates

A prior-conditioned policy is only as authoritative as the declared demand
model.  Prior concentration is not a protected correctness argument.

Before any deployable lifetime signal is admitted, run at least:

1. held-out calibration of the event `H` under the exact invalidation semantics;
2. temporal/drift splits, including resets and software/config changes;
3. worst-case or distribution-shift fallback to the certified time-only parent;
4. signal removal/corruption hostiles;
5. acquisition/inference timeout/failure accounting;
6. checkpoint/replay and state-loss accounting where the signal depends on
   persistent statistics;
7. a no-signal fallback that preserves protected output/lifecycle correctness.

Learning-augmented robustness/consistency results are relevant only after a
lawful prediction variable and error measure exist.

## 12. Required empirical ladder

Once a real lifetime source exists, execute in this order:

```text
H0  exact empirical prior only; no extra signal
H1  perfect-H oracle upper bound
H2  cheap existing metadata signals, one at a time
H3  exact coarsenings / calibrated bins / survival covariates
H4  paid delayed-query policy
H5  robust distributional or point-prediction parent
H6  ordinary statistical lifetime prediction
H7  learned OCM-specific predictor only if H6 leaves payable residual
```

At every stage report:

```text
gross value of information
signal acquisition + inference cost
net value
raw resource vector
coverage / calibration / drift
protected fallback behavior
```

A successful negative terminal is:

```text
PERFECT_HORIZON_INFORMATION_NOT_ECONOMIC
SIGNAL_ACQUISITION_DOMINATES
EXISTING_METADATA_SUFFICIENT
DEMAND_SIGNAL_NOT_IDENTIFIABLE
```

## 13. Literature parent map

This protocol deliberately applies existing work:

- Blackwell comparison of statistical experiments and decision-relative value;
- Bayesian finite-horizon stopping / posterior conditioning;
- Drygala, Nagarajan & Svensson, *Online Algorithms with Costly Predictions*,
  AISTATS 2023: predictions may have acquisition cost, and when/whether/how many
  predictions to query are algorithmic decisions;
- Purohit, Svitkina & Kumar, NeurIPS 2018, and later robustness-consistency work:
  use predictions only with explicit degradation guarantees;
- Sun et al., ICML 2024: uncertainty-quantified predictions require algorithms
  designed around the uncertainty channel, not blind point estimates;
- Kang, Park & Fan, AAAI 2026: discrete Bayesian ski rental conditions on survival
  and acts using the posterior horizon distribution;
- 2026 distributional-advice work: relevant only after OCM has a defensible
  distributional prediction source.

The gap OCM must fill is not another generic ski-rental theorem.  It is the
machine-specific proof that a proposed lifetime signal is legally observable,
calibrated for the protected invalidation event, and worth its complete cost.
