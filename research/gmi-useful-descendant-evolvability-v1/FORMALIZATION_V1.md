# Prospective useful-descendant / evolvability prediction — formalization V1

Issue #779; parent ledger #602 V5; parent theory HST-T10 / #233. Pre-implementation authority: `FREEZE_V1.md`, commit `a050f592b3a2b9eb20b12bdfc7670d42bb22ae39`.

## 1. Claim boundary

Claim ceiling:

```text
USEFUL_DESCENDANT_EVOLVABILITY_PREDICTION_VALIDATED_AT_REGISTERED_FINITE_SCOPE
```

This artifact concerns only the probability mass that fixed proposal kernels assign to frozen useful-descendant sets on `X={0,1}^6`, and the implied iid proposal count to first useful descendant. It does not establish universal evolvability, open-ended evolution, real-world calibration, or wall-clock improvement.

The parent mathematics is elementary finite probability and the geometric distribution. HST-T10 already owns the definition

```text
Ev_Q(U)=P_{z~Q}[z in U].
```

Repository-specific evidence is the freeze-first continued/reset/shuffled developmental comparison, exact held-task predictions, semantic-remint control and negative-transfer discipline.

Evidence classes:

- EV-1, EV-2 and EV-3: P1 finite mathematical statements;
- 64-point enumeration, exact prediction cells and hostiles: P2 exact computation.

## 2. Registered kernels and held utilities

Every arm has identical current object `000000`, identical descendant universe `X={0,1}^6`, identical admissibility and the same exact membership verifier for a held utility. Only proposal probabilities differ.

Product Bernoulli parameters are

```text
RESET            (1/2,1/2,1/2,1/2,1/2,1/2)
CONTINUED        (3/4,3/4,1/2,1/2,1/2,1/2)
SHUFFLED_HISTORY (1/2,1/2,1/2,1/2,3/4,3/4).
```

Developmental history contains only predicates `z_0=1` and `z_1=1` separately. The protected held utilities are the unseen conjunction `U_AND`, shifted negative twin `U_ANTI`, and coordinate-remint control `U_45`; none is extensionally identical to either history predicate.

## 3. EV-1 — exact useful-descendant mass [P1]

For finite `X`, probability kernel Q and useful set U,

```text
Ev_Q(U)=sum_{z in U} Q(z).
```

For independent Bernoulli coordinates with probabilities `p_i` and a conjunction fixing coordinates `I` to values `a_i`,

```text
Ev_Q(U)= product_{i in I} p_i^(a_i) (1-p_i)^(1-a_i).
```

### Proof

Independence factorizes the joint mass of the fixed coordinates. All unfixed coordinates are summed over their full binary support, and for each such coordinate `p_i+(1-p_i)=1`, so they contribute multiplicative factor one. The remaining fixed factors are exactly the expression above. QED.

The executable computes every registered mass both by direct summation of all 64 exact rational point masses and by this factorized formula and requires equality.

## 4. Frozen prospective prediction results [P1/P2]

### U_AND — unseen composition

For `z_0=z_1=1`:

```text
RESET:            (1/2)(1/2)=1/4
CONTINUED:        (3/4)(3/4)=9/16
SHUFFLED_HISTORY: (1/2)(1/2)=1/4.
```

Thus CONTINUED assigns 2.25x the useful-descendant mass of RESET even though the exact conjunction was absent from developmental history.

### U_ANTI — shifted ecology

For `z_0=z_1=0`:

```text
RESET:            (1/2)(1/2)=1/4
CONTINUED:        (1/4)(1/4)=1/16
SHUFFLED_HISTORY: (1/2)(1/2)=1/4.
```

The same history that helps U_AND therefore harms the preregistered flipped ecology by a factor four in useful mass. This is the load-bearing negative-transfer control against `continued development always improves evolvability`.

### U_45 — semantic remint

For `z_4=z_5=1`:

```text
RESET:            1/4
CONTINUED:        1/4
SHUFFLED_HISTORY: 9/16.
```

The winner follows semantic alignment of the biased coordinates rather than global concentration.

## 5. EV-2 — iid first-useful proposal count [P1]

Let each independent proposal be useful with fixed probability `p>0`, and let T be the 1-indexed first success. Then

```text
P(T=k)=(1-p)^(k-1)p.
```

Using the tail-sum identity for a positive integer-valued variable,

```text
E[T]
= sum_{k>=0} P(T>k)
= sum_{k>=0} (1-p)^k
= 1/p.
```

Hence the exact expected proposal counts are:

```text
U_AND:  RESET 4, CONTINUED 16/9, SHUFFLED 4
U_ANTI: RESET 4, CONTINUED 16,   SHUFFLED 4
U_45:   RESET 4, CONTINUED 4,    SHUFFLED 16/9.
```

This is proposal count. One proposal and one membership verification event are registered per draw, but no wall-clock, CPU, energy or total lifecycle scalar is inferred.

If `p=0`, no finite k has positive success probability and T is almost surely infinite. V1 therefore returns `UNREACHABLE_ZERO_USEFUL_MASS` rather than a finite numeric burden.

## 6. EV-3 — same-concentration semantic-remint theorem [P1/P2]

CONTINUED and SHUFFLED_HISTORY contain the same multiset of Bernoulli parameters:

```text
{3/4,3/4,1/2,1/2,1/2,1/2}.
```

They differ only by a coordinate permutation. A coordinate permutation is a bijection of `{0,1}^6`, so it permutes the 64 joint point masses and leaves the sorted mass multiset unchanged.

For independent Bernoulli coordinates, Shannon entropy is

```text
H(Q)=sum_i h(p_i),
h(p)=-p log p -(1-p) log(1-p).
```

Since the parameter multiset is identical, this sum is identical. The machine certificate checks exact equality of the parameter multiset and the exact sorted rational point-mass multiset; no floating logarithm is needed to establish the entropy equality.

Therefore CONTINUED beating SHUFFLED on U_AND and losing to it on U_45 cannot be explained by one kernel simply being globally more concentrated.

## 7. Current-competence / solution-reuse subtraction

All arms begin at the same `x0` and share all descendants, admissibility and verifier semantics. No arm is initialized at a previously solved descendant. The held conjunction `U_AND` is not one of the two developmental obligations. The measured quantity is entirely `Q(U)`—mass of future proposals—not current task score or a warm-started phenotype.

This directly distinguishes the evidence from the already-merged history-to-unseen-morphology rank result in #743: #743 showed proposal-order search burden changes; #779 validates HST-T10's explicit useful-descendant-mass prediction.

## 8. Zero-mass hostile [P2]

A point-mass kernel on `000000` assigns exactly zero probability to `U_AND`. The executor reports

```text
Ev=0
first_hit_burden=UNREACHABLE_ZERO_USEFUL_MASS.
```

This blocks silent division-by-zero, finite clipping or the interpretation that every finite state space gives finite expected first hit under every proposal kernel.

## 9. Falsifiers and scope

The claim fails if any kernel does not normalize; enumeration and factorized mass disagree; any one of the nine frozen held predictions changes; U_AND is not improved by CONTINUED; U_ANTI does not reverse the benefit; U_45 does not transfer the benefit to SHUFFLED; a held task duplicates a history predicate; current state/search space/verifier differs between arms; CONTINUED and SHUFFLED differ in concentration/entropy signatures; zero mass receives a finite burden; normal and optimized execution differ; or the result is promoted to universal/open-ended/real-world/complete-GMI wording.

Strongest permitted terminal:

```text
USEFUL_DESCENDANT_EVOLVABILITY_PREDICTION_VALIDATED_AT_REGISTERED_FINITE_SCOPE
```
