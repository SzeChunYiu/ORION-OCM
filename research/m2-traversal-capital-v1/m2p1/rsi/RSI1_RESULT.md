# RSI-1 — active causal self-diagnosis: `CANNOT_CHECK_DIAGNOSER_UNCALIBRATED`

The RSI spine's first runnable stage, and it returns a defect in **this study's own
instrument** rather than a finding about active diagnosis.

## The benchmark is real

Eight cases, every one a failure (or healthy run) that actually occurred in this lane and
was later explained by analysis. The explanation is hidden ground truth; the packet
exposes only internally computable features — the hidden motif set and the admission law
are **evaluator-side and excluded by construction**, which is what makes this a
self-diagnosis test rather than a lookup.

| case | true cause | composability | tokens needed | held-out win rate |
|---|---|---|---|---|
| FOREIGN_M1 | C3 unstructured | 0.65 | 3 | 18/40 |
| E3_16motifs | C1 incomplete recovery | 0.72 | 2 | 10/29 |
| E7_longhorizon | C1 incomplete recovery | 0.40 | 3 | 5/10 |
| D1_m12k4 | C2 arrangement depth | 0.77 | **4** | 8/30 |
| D2_m12k4 | C2 arrangement depth | 0.63 | **4** | 9/30 |
| E5 / E8 / E6 | **C0 no failure** | **1.00** | 3 | **100 %** |

`C0` is the clean no-alarm control: a diagnoser that invents a cause on a healthy run is
as defective as one that misses a real cause, so healthy runs are **scored, not excluded**.

## The result

| arm | accuracy | mean cost | cost per correct |
|---|---|---|---|
| SCRIPTED | 0.281 | 6.07 | 21.59 |
| RANDOM | ~0.28 | ~6 | ~21 |
| **VOI** | **0.250** | 4.88 | 19.50 |

Chance is 0.20 over five causes. **VOI answers `C1` for every single case, including all
three healthy controls.** A constant answer is not a diagnosis, so the cost advantage is
meaningless and no claim about active diagnosis can be made either way.

```text
TERMINAL: CANNOT_CHECK_DIAGNOSER_UNCALIBRATED
```

## Root cause, and why it is not fixed by tuning

The likelihood tables `P(observation | cause)` were **hand-specified from intuition**.
Fitting them against eight cases whose answers are known would be exactly the
outcome-driven tuning this programme forbids, and would produce a diagnoser that works on
these eight cases and nothing else.

## What the failure actually localises — a missing probe

The features separate most classes cleanly:

- `C0` is trivially separable — composability 1.00 and a 100 % win rate;
- `C2` is trivially separable — `tokens_needed = 4`, and independently confirmed by
  `ORACLE_FAMILY` *also* failing on D1/D2 (103 vs RESET 104; 100 vs 99), which is exactly
  the signature of depth rather than library quality.

**`C3` versus `C1` is the genuinely hard pair, and the probe set cannot separate them**:
FOREIGN_M1 (unstructured) sits at composability 0.65 while E3 (incomplete recovery) sits
at 0.72 — overlapping. Distinguishing them requires asking *whether any latent structure
exists at all*, which none of the six probes measures.

The missing probe is a **structure-existence / compressibility test** — for example the
MDL gain of describing the target set through a candidate vocabulary versus primitives.
That is the internally computable counterpart of `V_H(E) > 0` from
[../THEORY_GAPS.md](../THEORY_GAPS.md) §2.4, and it is also the missing `Ĉ_t` coverage
estimator of §2.5.

## What this contributes to the RSI spine

RSI-0/RSI-1 are runnable on this lane's own history, and the first attempt already yields
a concrete, mechanism-derived requirement rather than a vague one:

> before an OCM self-model can diagnose *why* development failed, it needs a probe that
> answers *whether the world had learnable structure at all* — without consulting the
> evaluator.

Next: implement the MDL structure-existence probe, derive likelihoods from mechanism
rather than intuition, and re-run against the same sealed packet with the cause labels
still hidden.
