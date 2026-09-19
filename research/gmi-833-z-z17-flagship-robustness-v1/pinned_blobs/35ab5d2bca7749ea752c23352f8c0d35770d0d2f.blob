# Z6 named results — theory discrimination against strongest parents

Scope for every result below, and never wider: the registered `65552`-candidate
binary mechanism universe, `404` worlds in three declared-accounting families
(`E-LIN` `60`, `E-SKEW` `324`, `E-COD` `20`), and two readouts — `R1`, the
property class (`STATELESS` / `PERSISTENT_STATE` / `TIE`), and `R2`, the argmin
risk summary. Ground truth in every world is the argmin of **that world's own
declared accounting**. Every quantity is an exact integer or `Fraction`.

Claim ceiling:

```
GMI_833_Z6_PREREGISTERED_PARENT_DISCRIMINATION_AND_PROVED_OBSERVATIONAL_EQUIVALENCE_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

---

## `DS-1` — the competing-prediction registry

**Statement.** Thirteen parent theories, covering every family the Z6 row names,
are registered as explicit selection rules and evaluated on all `404` worlds.
Seven adopt the world's declared accounting (`T02_BAYES`, `T03_BOUNDED`,
`T04_ALGSEL`, `T05_NAS`, `T06_ACTINF`, `T07_RLCTRL`, `T08_PROGSYN`); three
impose their own (`T09_MDL`, `T10_OCCAM_HARD`, `T12_SRM`); two abstain on the
selection question (`T11_INFOTHEORY`, `T13_EVOPEN`); one is the registered GMI
closed form (`T01_GMI`).

The registry is not a list of opinions: each rule is executable, each prediction
is emitted for each of the `404` worlds before the worlds are adjudicated, and
the whole table is in `RESULT_V1.json`.

**Scope note.** `T10_OCCAM_HARD` is labelled a folk rule. The Occam's-razor
theorems of Blumer, Ehrenfeucht, Haussler & Warmuth (1987) require a *consistent*
hypothesis and no stateless candidate is consistent on the delayed channel, so
this package's result about `T10_OCCAM_HARD` is not a result about that
literature. Forbidden promotion: `OCCAM_RAZOR_LITERATURE_REFUTED`.

---

## `DS-2` — preregistered environments where GMI and a strongest parent disagree

**Statement.** Disagreement is not hypothetical and is not manufactured:

| parent | `R1` disagreements with `T01_GMI` (abstentions excluded) | `E-LIN` losses out of `60` |
|---|---:|---:|
| `T09_MDL` | `220` of `384` | `40` |
| `T10_OCCAM_HARD` | `220` of `384` | `40` |
| `T12_SRM` | `226` of `384` | `40` |
| `T02..T08` (declared-cost) | `108` of `384` | `0` |
| `T11_INFOTHEORY`, `T13_EVOPEN` | `0` — they abstain in all `404` | n/a |

`20` worlds are excluded from every comparison because `T01_GMI`, read as the
registered closed form, is not defined on `E-COD`: that family declares no
`(eta, p)`. Abstentions are never counted as agreement — null `N3` scores an
always-abstaining theory at `0` wins, `0` losses and `0` equivalences.

**Falsifier.** If every parent had agreed with `T01_GMI` everywhere, rows 2 and 4
would not close and the package would say so.

---

## `DS-3` — wins, losses, observational equivalences

Adjudicated by each world's own accounting; `win` includes correctly-called exact
ties, which are counted separately.

| theory | `E-LIN` (60) | `E-SKEW` (324) | `E-COD` (20) |
|---|---|---|---|
| `T01_GMI` (registered closed form) | `60` win, `0` loss, `20` exact ties | `216` win, **`108` loss** | `20` abstain |
| `GMI_REPAIRED` | `60` win, `0` loss, `20` ties | **`324` win, `0` loss**, `12` ties | `20` win, `0` loss, `1` tie |
| `T02..T08` (declared cost) | `60` win, `0` loss | `324` win, `0` loss | `20` win, `0` loss |
| `T09_MDL` | `20` win, `40` loss | `72` win, `252` loss | **`20` win, `0` loss** |
| `T10_OCCAM_HARD` | `20` win, `40` loss | `240` win, `84` loss | `6` win, `14` loss |
| `T12_SRM` | `20` win, `40` loss | `198` win, `126` loss | `1` win, `19` loss |
| `CTRL_SHIFTED_2LAMBDA` (negative control) | `20` win, **`40` loss** | `72` win, `252` loss | `20` abstain |

On `R2`, the finer readout, `T02..T08` reproduce the declared-cost argmin set in
**all `404`** worlds (`0` mismatches each), while `T09_MDL` mismatches in `384`,
`T12_SRM` in `186` and `T10_OCCAM_HARD` in `144`.

**Honest reading of the `E-LIN` column.** `T01_GMI` winning all `60` `E-LIN`
worlds is a **consistency check, not a discovery**: `lambda* = eta*p/2` is the
analytic argmin of the `E-LIN` accounting, so it could not have lost there
without an arithmetic error. The scientific content of the table is the
`E-SKEW` column and the parent losses.

---

## `DS-4` — the registered flagship law is refuted outside uniform inputs

**Statement.** `T01_GMI`, the registered closed form `lambda* = eta*p/2`, is
**wrong on `108` of the `324` `E-SKEW` worlds**. The first witness: `q = 1/5`,
`p = 2/5`, `eta = 1`, `lambda = 3/25`; the registered law predicts
`PERSISTENT_STATE`, the declared accounting selects `STATELESS`.

**Why.** The derivation of `eta*p/2` assumes uniform independent input bits,
which is exactly what makes the stateless delayed-error rate `1/2`. Under
`Bernoulli(q)` inputs the best stateless delayed predictor is the constant
majority bit, whose error rate is `min(q, 1-q) < 1/2`, so the true boundary sits
strictly below the registered one and the registered law over-predicts
`PERSISTENT_STATE` in the band between them.

This is published in `FAILED_PREDICTION_REGISTER_V1.json` and retires the
unqualified form of the law. It is the second independent dimension along which
`eta*p/2` has been found to be a special case; the first is
`lambda*(A) = eta*p*(1 - 1/A)` in alphabet size `A`, found by
`research/gmi-833-z-z5-critical-phenomena-v1` (branch `research/833-sec-z2`,
PR #1034, not on `main` at this package's `source_main`).

**Forbidden extrapolation.** `FLAGSHIP_LAW_VALIDATED_BEYOND_UNIFORM_INPUTS`.

---

## `DS-5` — the repaired law, and what it unifies

**Statement.** The law

```
lambda*(env) = eta * p * R0(env)
```

where `R0` is the **minimum delayed-channel error rate attainable without
state** under the environment's own input law, is correct on `R1` in **all `404`
worlds**: `60/60` `E-LIN` (with `20` exact ties called as ties), `324/324`
`E-SKEW` (with `12` exact ties), `20/20` `E-COD` (with `1` exact tie).

It reduces to the registered `eta*p/2` at `q = 1/2`, where `R0 = 1/2`, and to
`eta*p*(1 - 1/A)` for a uniform `A`-ary alphabet, which is Z5's independently
found form. On `E-COD`, where no `(eta, p)` is declared, the same mechanism
reads as "state is bought iff its price is below the code the stateless optimum
must pay for its delayed errors", `ceil_log2(binom(16,8)) = 14` bits, and is
correct in all `20` worlds.

**Forbidden extrapolation.** `REPAIRED_LAW_IS_UNIVERSAL`. This is a statement
about `404` registered worlds over one finite universe, confirmed along two
independent dimensions, not a universal law.

---

## `DS-6` — proved observational equivalence, and where it does not hold

**Statement.** `GMI_REPAIRED` is `R1`-identical to `T02_BAYES`, `T03_BOUNDED`,
`T04_ALGSEL`, `T05_NAS`, `T06_ACTINF`, `T07_RLCTRL` and `T08_PROGSYN` in **all
`404` worlds** — `0` disagreements each, with no abstentions on either side
outside the `20` `E-COD` worlds where only `T01_GMI` abstains.

**Why it is proved and not assumed.** All seven are argmins of a positive affine
function of the same declared cost, and a positive affine reparameterization
preserves argmins; the executor nevertheless recomputes each of them
independently over the full point set of every world rather than invoking the
theorem, and Route B recomputes the declared-cost optimum again by a two-stage
block scan and re-derives the boundary analytically. The equivalence is
therefore both proved and exhaustively verified.

**The row-6 statement, for each parent, at this scope:**

- **Bayesian decision theory, bounded/resource rationality, algorithm selection,
  NAS with a resource regularizer, active inference, RL/control and program
  synthesis**: *no discriminating experiment exists at this scope.* GMI's
  repaired selection law is not empirically distinguishable from any of them
  over the registered universe and the `404` registered worlds at either
  readout. The residual content of the GMI law is that it is a **closed form**
  that names the boundary without search, not that it selects differently.
- **Information theory (Shannon)**: abstains on the selection question in all
  `404` worlds; it constrains feasibility (zero-error delayed recall needs at
  least one bit) and says nothing about price. *No discriminating experiment
  exists at this scope.*
- **Evolutionary / open-ended search**: abstains on the optimum in all `404`
  worlds; it predicts search dynamics, not the argmin. *No discriminating
  experiment exists at this scope.*
- **MDL/compression, the folk Occam rule, and structural risk minimization**:
  these **are** distinguishable, and each is adjudicated wrong on `40` of the
  `60` `E-LIN` worlds by the declared accounting, for the same structural
  reason — each substitutes its own price for the one the environment declares.
  `T09_MDL` is correct on all `20` `E-COD` worlds, where the declared accounting
  *is* a two-part code, which is the control that shows the failure is
  environment-relative rather than a defect of MDL.

**Forbidden extrapolations.** `GMI_TRUER_THAN_MDL`, `PARENT_THEORIES_REFUTED`,
`UNIVERSAL_OBSERVATIONAL_EQUIVALENCE`.

---

## `DS-7` — the instruments

**Null `N1` (the equivalence is not an artifact of a coarse readout).** `200`
pseudo-random positive rational monotone rules over `(rate_now, rate_delay,
bits)`, seeds `6100..6299`: **`0`** are `R1`-equivalent to `T01_GMI` across all
`404` worlds. Equivalence at `R1` is therefore not something a random scoring
rule achieves, and the `DS-6` equivalences are a property of the seven parents,
not of the readout.

**Null `N2` (the test can falsify).** The deliberately shifted boundary
`2*lambda*` loses `40` of `60` `E-LIN` worlds and `252` of `324` `E-SKEW`.

**Null `N3` (abstention is not agreement).** An always-abstaining theory records
`0` wins, `0` losses, and is excluded from all `404` comparisons rather than
counted as equivalent.

**Hostiles, all detected.** `HS1` a planted ground-truth reader — the leakage
guard re-evaluates every registered theory against a permuted truth array and
flags only the planted one, and no registered theory moves; `HS2` every world
has a non-empty candidate set; `HS3` the abstainer is not counted as equivalent;
`HS4` disagreement counts exclude abstentions and report the excluded count
(`20`); `HS5` the shifted control's misses are non-zero; `HS6` all `20`
exact-boundary `E-LIN` worlds are reported as `TIE` on both sides rather than
mapped to a class.

---

## What none of these results establish

No claim that GMI is truer than MDL as a theory; no claim that any parent
theory is refuted; no universal observational equivalence; nothing about real or
trained systems; no validation of the registered law beyond uniform inputs — the
opposite is shown; and no re-earning of the transition law's own rows, which
belong to `research/gmi-833-heldout-20-transitions-v1`.
