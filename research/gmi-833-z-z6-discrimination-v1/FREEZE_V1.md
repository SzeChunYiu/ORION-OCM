# GMI #833 Section Z / Z6 — theory discrimination against strongest parents:
# pre-implementation freeze

Committed **before** any executor, oracle, test, receipt or result file of this
package exists, and therefore before any outcome it adjudicates has been
computed. Every prediction below is stated now; none was read off an
enumeration.

- `source_main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`
- issue: SzeChunYiu/ORION-OCM#833, Section Z, issue comment `5684819296`
- branch: `research/833-sec-z3`

## 0. Claim ceiling

```
GMI_833_Z6_PREREGISTERED_PARENT_DISCRIMINATION_AND_PROVED_OBSERVATIONAL_EQUIVALENCE_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

**No neighboring row is earned here.** This tranche may reconcile exactly the
six `- [ ] ` rows under the `### Z6 — Theory discrimination against strongest parents`
anchor of issue comment `5684819296`, reproduced verbatim:

```
- [ ] For every flagship prediction, list competing predictions from MDL/compression, Bayesian decision theory, information theory, bounded/resource rationality, algorithm selection, NAS, active inference, RL/control, program synthesis, computational learning theory, evolutionary/open-ended search and other relevant parents.
- [ ] Construct preregistered environments where GMI and at least one strongest parent disagree.
- [ ] Freeze all theories' predictions before outcomes.
- [ ] Run discriminating experiments.
- [ ] Report wins, losses and observational equivalences.
- [ ] If no discriminating experiment exists at a scope, explicitly state that GMI is not empirically distinguishable from that parent there.
```

## 1. The flagship prediction under test

From `research/gmi-833-heldout-20-transitions-v1` (freeze commit
`ddb3df7a44a6a4fb47fdc362a1fa02e34b7a3a75`), over the registered `65552`-candidate
binary mechanism universe: with declared cost

```
C(c) = eta*p*rate_delay(c) + eta*(1-p)*rate_now(c) + lambda*bits(c)
```

the property-level selection boundary is `lambda* = eta*p/2`, i.e.
`PERSISTENT_STATE` below it and `STATELESS` above it. The derivation assumes
**uniform independent input bits**, which is what makes the stateless delayed
error rate exactly `1/2`.

This package neither re-derives that law nor touches its rows. It asks what the
named parent theories predict about the same object, and where they and the
registered law can be told apart.

## 2. Three environment families, fixed now

- **`E-LIN`** — the registered accounting. `p in {1/5,2/5,1/2,3/5,4/5}`,
  `eta in {1,2,3,4}`, `lambda in {lambda*/2, lambda*, 3*lambda*/2}`, uniform
  inputs. `5*4*3 = 60` worlds.
- **`E-SKEW`** — identical accounting, **non-uniform** input bits: each of the
  three input bits is independently `1` with probability `q`, and sequence
  weights are the exact rational products. `q in {1/5, 1/4, 1/3, 2/3, 3/4, 4/5}`,
  `p in {2/5, 1/2, 3/5}`, `eta in {1, 2}`, `lambda` swept over the nine exact
  values `k * eta * p / 10` for `k = 1..9`. `6*3*2*9 = 324` worlds. `E-SKEW`
  lies **outside** the uniform-input assumption of the registered derivation and
  is included so that the registered law can lose.
- **`E-COD`** — an independently specified accounting in integer bits: a model
  pays `c_state` bits per state bit, and the data pays an exact two-part
  exception code `ceil_log2(binom(16, k_now)) + ceil_log2(binom(16, k_delay))`
  where `k` is the integer error count on that channel. `c_state in 1..20`,
  uniform inputs. `20` worlds. Integer arithmetic throughout.

Total `404` worlds. Every world's accounting is part of the world, declared by
the world and not by any theory; the world's own accounting is the referee.

## 3. The theory registry, fixed now

Each theory is a function from a world to a predicted property class
(`STATELESS`, `PERSISTENT_STATE`, `TIE`, or `ABSTAIN`), and where it is defined,
to a predicted argmin risk summary `(k_now, k_delay, bits)`.

| id | parent | selection rule as registered here |
|---|---|---|
| `T01_GMI` | this programme | `PERSISTENT_STATE` iff `lambda < eta*p/2`, `TIE` at equality — the registered closed form, applied verbatim in every world |
| `T02_BAYES` | Bayesian decision theory (Savage 1954; Berger 1985) | argmin of the world's declared expected cost |
| `T03_BOUNDED` | bounded / resource rationality (Simon 1955; Russell & Subramanian 1995) | argmin of declared cost under a positive affine reparameterization `a*C + b`, `a = 3`, `b = 7` |
| `T04_ALGSEL` | algorithm selection (Rice 1976) | argmin of the world's declared performance measure |
| `T05_NAS` | NAS with a resource regularizer (Zoph & Le 2017) | argmin of `loss + w*resource` with `w` set to the world's declared state price |
| `T06_ACTINF` | active inference (Friston 2010) | argmin of declared cost plus a complexity term that is constant under the registered uninformative prior |
| `T07_RLCTRL` | RL / optimal control | argmin of declared expected cost over the candidate set |
| `T08_PROGSYN` | syntax-guided program synthesis (Alur et al. 2013) | argmin of declared cost over the same grammar-enumerated candidate set |
| `T09_MDL` | MDL two-part code (Rissanen 1978) | argmin of **its own** code length: `c_state` bits of model code (`c_state = 1` unless the world declares otherwise) plus the exact exception code, ignoring any declared price |
| `T10_OCCAM_HARD` | the folk "prefer the simplest model" rule | lexicographic argmin of `(bits, declared error)`; price-independent |
| `T11_INFOTHEORY` | Shannon channel/feasibility | predicts only that zero-error delayed recall requires at least one bit of state; `ABSTAIN` on the property-class question whenever both classes are feasible |
| `T12_SRM` | computational learning theory / structural risk minimization (Vapnik 1998) | argmin of `declared error + kappa * sqrt-surrogate`, with the registered exact surrogate `kappa * bits` (only two complexity levels exist, so the square root is a relabeling) |
| `T13_EVOPEN` | evolutionary / open-ended search (Lehman & Stanley 2008) | `ABSTAIN` on the optimum; predicts only that a hill-climb from a registered start reaches a local optimum |

`T10_OCCAM_HARD` is labelled a **folk rule**, not a literature result: the
Occam's-razor theorems of Blumer, Ehrenfeucht, Haussler & Warmuth (1987) require
a *consistent* hypothesis, and no stateless candidate is consistent on the
delayed channel. It is registered because it is the position most often
attributed to compression-first reasoning, and it must be scored as such rather
than strawmanned away.

## 4. The two readouts, fixed now

- **`R1`** — the property-class readout: `STATELESS` vs `PERSISTENT_STATE`.
  This is the resolution at which the flagship prediction is stated.
- **`R2`** — the risk-summary readout: which `(k_now, k_delay, bits)` summary is
  the argmin. Strictly finer than `R1`.

Ground truth for both is the argmin of **the world's own declared accounting**,
computed by exhaustive enumeration over all `65552` candidates.

## 5. Frozen hypotheses — each may be refuted by the enumeration

| id | statement | falsifier |
|---|---|---|
| `D1` | `T02, T03, T04, T05, T06, T07, T08` agree with `T01_GMI` on `R1` in **all** `404` worlds — observational equivalence at the flagship's own resolution | any disagreement |
| `D2` | at least one of `T02..T08` disagrees with `T01_GMI` on the finer readout `R2` in at least one world | none does |
| `D3` | `T09_MDL` disagrees with `T01_GMI` on `R1` in at least one `E-LIN` world, and the world's declared accounting adjudicates against `T09_MDL` there | no disagreement, or `T09_MDL` is right wherever they differ |
| `D4` | `T10_OCCAM_HARD` disagrees with `T01_GMI` on `R1` in at least one `E-LIN` world and is adjudicated wrong there | as above |
| `D5` | `T01_GMI` is **correct on `R1` in every `E-LIN` world** — the consistency check, since the registered law is the analytic argmin of the `E-LIN` accounting | any `E-LIN` miss |
| `D6` | `T01_GMI` is **incorrect on `R1` in at least one `E-SKEW` world**, because the registered derivation assumes uniform inputs | `T01_GMI` is correct in all `324` |
| `D7` | the repaired law `lambda*(q) = eta*p*min(q, 1-q)` is correct on `R1` in **every** `E-SKEW` world and reduces to `eta*p/2` at `q = 1/2` | any `E-SKEW` miss |
| `D8` | `T09_MDL` is correct on `R1` in every `E-COD` world (its own accounting is the declared one there) | any miss |
| `D9` | `T01_GMI`, read as the registered closed form, is not defined on `E-COD` — the world declares no `(eta, p)` — and must `ABSTAIN` rather than guess; the mechanism-faithful reading (`PERSISTENT_STATE` iff the state price is below the error cost the stateless optimum pays on the delayed channel) is correct in every `E-COD` world | the faithful reading misses |
| `D10` | `T11_INFOTHEORY` and `T13_EVOPEN` abstain on `R1` in every world, so no discriminating experiment against them exists at this scope | either emits a class prediction |

`D6` is the hypothesis this package most wants to be true, because a registered
law that cannot lose anywhere has not been tested. If `D6` is refuted the
package says so and the `E-SKEW` family is reported as non-discriminating.

## 6. Nulls

- `N1` (equivalence is not an artifact): `200` pseudo-random monotone scoring
  rules over `(rate_now, rate_delay, bits)` from seeds `6100..6299` — each a
  positive rational combination with a random exponent pattern — are scored on
  `R1` across all `404` worlds. The number that come out `R1`-equivalent to
  `T01_GMI` everywhere is reported. If most random rules are equivalent too, the
  `D1` equivalence is an artifact of a coarse readout and must be reported as
  such rather than as a finding.
- `N2` (the test can falsify): a deliberately shifted threshold `2*lambda*`
  replaces the registered one; the number of `E-LIN` worlds it gets wrong is
  reported and must be non-zero.
- `N3` (abstention is not agreement): a theory that abstains everywhere is
  scored; it must record `0` wins and `0` losses and must **not** appear as
  `R1`-equivalent to `T01_GMI`.

## 7. Hostiles — each must be shown able to fire

| id | deliberate defect | the check that must flag it |
|---|---|---|
| `HS1` | a theory that reads the world's ground truth before predicting | outcome-leakage guard: perfect score on every world including `E-SKEW`, where the registered law provably misses |
| `HS2` | an "environment" whose candidate set is empty | world-validity guard |
| `HS3` | abstention counted as agreement | the `N3` null must separate them |
| `HS4` | a disagreement counted where one side abstains | disagreement counter must exclude abstentions and report the excluded count |
| `HS5` | the shifted-threshold control silently scored as the registered law | `N2` must report a non-zero miss count |
| `HS6` | a tie mapped to a class rather than reported as a tie | tie-handling guard: exact-boundary worlds must be reported as `TIE` on both sides |

## 8. Two materially independent routes

Route A (`z6_discrimination_v1.py`) simulates every candidate over the eight
sequences in both modes, weights sequences by the world's exact input
distribution, and decides every theory, readout, world and null by scanning the
resulting list.

Route B (`independent_discrimination_oracle_v1.py`) does not import Route A. It
reconstructs the universe in a different order, compresses it to exact risk
summaries by a different key, recomputes every world's argmin over the summary
set rather than over candidates, and re-derives the boundary analytically rather
than by minimisation. Both routes must agree exactly on every reported number.

## 9. Arithmetic and forbidden promotions

Exact integers and `fractions.Fraction` only; no float in any claim; stdlib only;
`python3 -I -B` and `python3 -I -O -B` on Python 3.8.

```
GMI_TRUER_THAN_MDL
PARENT_THEORIES_REFUTED
UNIVERSAL_OBSERVATIONAL_EQUIVALENCE
REAL_SYSTEM_DISCRIMINATION
FLAGSHIP_LAW_VALIDATED_BEYOND_UNIFORM_INPUTS
OCCAM_RAZOR_LITERATURE_REFUTED
ABSTENTION_COUNTED_AS_AGREEMENT
PARENT_RESULTS_RE_EARNED_HERE
REPAIRED_LAW_IS_UNIVERSAL
```

The repaired law of `D7`, if it survives, is a statement about this universe and
this input family only, and is published in the same register as the
`lambda*(A) = eta*p*(1-1/A)` finding of
`research/gmi-833-z-z5-critical-phenomena-v1`: a registered law shown to be the
special case of a wider one, not a new universal.
