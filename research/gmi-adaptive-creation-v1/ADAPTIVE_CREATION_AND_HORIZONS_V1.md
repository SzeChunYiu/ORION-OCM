# Adaptive row creation and horizons — ARC-5, corrected disposition

**CORRIGENDUM (2026-09-14), #655 / #602 M / #592 item 32.**
The former ARC-5b(ii) general obstruction is retracted. The replacement proof,
exact certificates and counterexamples are in
[ARC-6](../gmi-countable-row-corrigendum-v1/FORMALIZATION_V1.md).

## Visible retractions

1. The former assertion that infinitely many positive weights necessarily
   diverge is false: w_j=1/[j(j+1)] has positive terms and total one.
2. A small fixed positive row allowance does not impose a limiting confidence
   radius floor. ARC-6 proves radius -> 0 for each fixed row as its visits grow.
3. Exceeding a union-bound allocation is not a proof that every conceivable
   method fails. Identical failure events disprove that inference. Independent
   fixed-level row errors do accumulate, but that is a scoped counterexample.

The [original text remains in version history](https://github.com/SzeChunYiu/ORION-OCM/blob/139a123d429d1a800f7fb3e071ec94d773630615/research/gmi-adaptive-creation-v1/ADAPTIVE_CREATION_AND_HORIZONS_V1.md).
It must not be cited as an established all-method impossibility result.

## ARC-5a — retained finite-register result

Freeze a finite potential row set, positive weights with total at most one,
and a creation budget before outcomes. Each created row starts its own visit
counter at zero and uses allowance alpha*w_j/[n(n+1)]. Under ARC-1's predictable
selection and conditional fixed-row-law premises, union over the finite
potential register and all finite visit counts gives a single 1-alpha event.
Adaptive choice among those predeclared rows does not change the argument.
This is inherited from ARC-1, not a new statistical rate.

## ARC-5b(i) — retained sampling-horizon boundary

ARC-1 is already simultaneous over every finite attained sampling visit.
A finite data-dependent stopping time inherits that event. This neither promises
that sampling terminates nor certifies an infinite deployment horizon. Checking
radii at n<=512 is a finite numerical control, not a proof of the infinite claim.

## ARC-5b(ii) — corrected countable-creation result

Predeclare a summable creation-order schedule, such as w_j=1/[j(j+1)]. Freeze
each row's meaning before its own evidence. Conditional Hoeffding concentration
at attained visits and a countable union then cover all created rows at all
finite visits. ARC-6 states the precise stopping-time and conditional-mean
premises, the proof, fixed-row shrinking widths, and the limits under replay,
post-selection, drift, finite resource budgets and deployment horizons.

## Evidence and claim ceiling

The existing model and 11-test receipt are preserved as **historical finite
controls only**. The old receipt's source digest/scope describes its historical
artifact, not this corrected document; it does not prove either retracted
statement. No past host run is relabeled as a run of new code.

The frozen ARC-1–4 unit and its capsule manifest are untouched. New ARC-6 has
its own P1/P3 written argument and P2 exact controls, with a scoped G2 ceiling.
Neither unit establishes physical-sampler authenticity, empirical G6 capability
prediction or all-method impossibility of unlimited creation.
