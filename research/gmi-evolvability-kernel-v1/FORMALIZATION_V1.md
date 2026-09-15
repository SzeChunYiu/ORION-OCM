# FORMALIZATION V1 — finite useful-descendant evolvability prediction

Issue #779; parent #602 V5; formal parent HST-T10/#233. `FREEZE_V1.md` is the pre-outcome authority.

## Registered objects

Let `X` be a finite descendant set, `Q:X→[0,1]∩Q` a normalized exact-rational proposal kernel,
and `U⊆X` a frozen useful set. Define

```text
Ev_Q(U) = Σ_{z∈U} Q(z).
```

For the registered assay, `X={0,1}^6`; every descendant is admissible and all arms have the same current
object `x0=000000`, verifier and state space.

## EV-T1 — exact finite useful-descendant mass [P1 definition / P2 certificate]

For `Z~Q`,

```text
P(Z∈U) = Σ_{z∈U} Q(z) = Ev_Q(U).
```

This follows from finite additivity over the disjoint singleton events `{Z=z}`. The executable certificate
enumerates all 64 descendants, verifies exact normalization, and sums the useful singleton masses.

For a factorized Bernoulli kernel

```text
Q(z)=Π_i p_i^{z_i}(1-p_i)^{1-z_i},
```

and a conjunction requiring values `z_i=a_i` on coordinate set `J`, marginalizing unrestricted coordinates
gives

```text
Ev_Q(U_J) = Π_{i∈J} P_Q(z_i=a_i).
```

because for every unrestricted coordinate `j`, its marginal factor sums to `p_j+(1-p_j)=1`.
The registered result requires exact equality between this closed form and independent 64-state summation.

## EV-T2 — iid first-useful proposal count [P1]

Assume proposals `Z_1,Z_2,...` are iid from one fixed `Q`, with every proposal independently *drawn* from
`Q` and then evaluated by the same deterministic useful-set membership test. Let

```text
p = Ev_Q(U),
T = min{t>=1 : Z_t∈U}.
```

If `0<p<=1`, then for every integer `k>=0`,

```text
P(T>k) = (1-p)^k.
```

**Proof.** `T>k` iff the first `k` iid draws all lie outside `U`. Each has probability `1-p`; iid sampling
makes the product `(1-p)^k`. ∎

For a positive integer-valued random variable,

```text
E[T] = Σ_{k=0}^∞ P(T>k),
```

so

```text
E[T] = Σ_{k=0}^∞ (1-p)^k = 1/p.
```

This is a proposal-count expectation only. It is not wall time, energy, verification latency, or full
lifecycle burden unless those coordinates are separately charged.

If `p=0`, then `P(T<∞)=0`; the correct terminal is

```text
UNREACHABLE_ZERO_USEFUL_MASS.
```

Assigning any finite expected first-hit count in that case is unsound.

## EV-T3 — exact registered predictions [P1 arithmetic + P2 enumeration]

### CONTINUED

The biased coordinates are 0 and 1 with `P(z_i=1)=3/4`.

```text
Ev_C(U_AND)  = (3/4)(3/4) = 9/16,
Ev_C(U_ANTI) = (1/4)(1/4) = 1/16,
Ev_C(U_45)   = (1/2)(1/2) = 1/4.
```

Hence first-useful proposal means are `16/9`, `16`, and `4` respectively.

### RESET

Every coordinate is fair, so every registered two-coordinate conjunction has mass

```text
(1/2)(1/2)=1/4
```

and mean proposal count `4`.

### SHUFFLED_HISTORY

The same `3/4,3/4` bias is moved to coordinates 4 and 5:

```text
Ev_S(U_AND)  = 1/4,
Ev_S(U_ANTI) = 1/4,
Ev_S(U_45)   = 9/16.
```

Thus the same concentration profile helps a different held utility after semantic reminting.

## EV-T4 — equal-concentration remint theorem [P1]

Let `π` be a coordinate permutation. If

```text
Q_S(z) = Q_C(π^{-1}z),
```

then `π` is a bijection on the finite state space, so the multisets

```text
{Q_C(z): z∈X}
and
{Q_S(z): z∈X}
```

are identical. Consequently every symmetric functional of the probability multiset—including Shannon
entropy

```text
H(Q) = -Σ_z Q(z) log Q(z)
```

—is identical. No floating logarithm is needed for the executable certificate: equality of the complete
sorted exact-rational probability multisets is a stronger finite certificate of equal entropy.

Therefore the different masses assigned to `U_AND` versus `U_45` are due to which states receive the mass,
not a difference in concentration magnitude.

## EV-T5 — harmful-transfer/reset negative twin [P1/P2]

The frozen pair `U_AND` / `U_ANTI` changes only which values of coordinates 0 and 1 are useful.
CONTINUED places more mass than RESET on `11` and less on `00`:

```text
9/16 > 1/4,
1/16 < 1/4.
```

Hence continuation is strictly better in one held ecology and strictly worse in its matched value-flip twin.
This is an exact counterexample to `CONTINUED_DEVELOPMENT_ALWAYS_BETTER`.

## EV-T6 — history-task nonidentity and claim boundary [contract]

Developmental obligations are the single-coordinate predicates `D0:z0=1` and `D1:z1=1`.
Protected utilities are two-coordinate conjunctions `U_AND`, `U_ANTI`, and `U_45`. Their complete truth
tables over all 64 descendants are not identical to either `D0` or `D1`. The executable checker verifies
this extensionally rather than by comparing labels.

This establishes only that the scored held task definition is not a reused development task. It does not
prove distributional independence, broad transfer, real-world causality, or open-ended evolution.

## Strongest-parent subtraction

Finite mass summation, product Bernoulli marginals, geometric first-hit time and coordinate-permutation
entropy invariance are standard probability facts. HST-T10 already defines local useful-descendant mass.
The repository residual is the freeze-first continued/reset/remint experiment and exact negative-transfer
discipline.

## Claim ceiling

`USEFUL_DESCENDANT_EVOLVABILITY_PREDICTION_VALIDATED_AT_REGISTERED_FINITE_SCOPE`.

Forbidden: universal evolvability, real-world calibration, open-ended evolution, or universal preference for
continued development.
