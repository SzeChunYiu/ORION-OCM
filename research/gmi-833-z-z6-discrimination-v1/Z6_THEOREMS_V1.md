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

**Assumptions.** The registered `65552`-candidate universe and the `404` worlds
of `FREEZE_V1.md` section 2, each refereed by its own declared accounting. Each
parent is represented by the single executable rule registered for it in
`FREEZE_V1.md` section 3, with `T12_SRM` as amended by
`FREEZE_V1_AMENDMENT_1.md` (`kappa_SRM = 1/4`); several are narrow readings,
stated as such (the uninformative-prior reading of active inference,
`T10_OCCAM_HARD` as a folk rule).

**Dependencies.** The universe and the registered law `lambda* = eta*p/2` of
`research/gmi-833-heldout-20-transitions-v1` (pinned in `MANIFEST_V1.json`) for
`T01_GMI`; the registry of `FREEZE_V1.md` section 3 and its amendment; the
readouts `R1` and `R2` of section 4; the per-theory `scores` in
`RESULT_V1.json`, with those of `T01_GMI`, `T02_BAYES`, `T09_MDL`,
`T10_OCCAM_HARD`, `T12_SRM` and `GMI_REPAIRED` recomputed by route B in
`ORACLE_RESULT_V1.json`.

**Falsifiers.** A registered rule flagged by the `HS1` leakage guard, which
re-evaluates every theory against a permuted truth array, would show a
prediction depending on the outcome and void the frozen registry; none is
flagged. A parent family named in the Z6 row with no executable rule in
`FREEZE_V1.md` section 3 would leave row 1 open.

**Strongest parents.** The literature owners listed per rule in
`PARENT_DISCLOSURE_V1.md` section 1: Savage (1954) and Berger (1985), Simon
(1955) and Russell & Subramanian (1995), Rice (1976), Zoph & Le (2017), Friston
(2010), Sutton & Barto (2018), Alur et al. (2013), Rissanen (1978), Shannon
(1948), Vapnik (1998), and Lehman & Stanley (2008). Blumer et al. (1987) is
explicitly not tested; the registry encodes these positions and is not a new
theory.

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

**Assumptions.** The registry of `DS-1` and the `404` worlds; `T01_GMI` is the
registered closed form applied verbatim, so it abstains on the `20` `E-COD`
worlds that declare no `(eta, p)`. Disagreements are counted on `R1` with
abstentions excluded and the excluded count reported (`HS4`), never as agreement
(`N3`).

**Dependencies.** The executable registry of `DS-1`; hypotheses `D3` and `D4`
(`FREEZE_V1.md` section 5) and `D11` (`FREEZE_V1_AMENDMENT_1.md`), recorded as
`DP-5` `CONFIRMED` in `FAILED_PREDICTION_REGISTER_V1.json`; the null `N3` and
the hostiles `HS3` and `HS4`; `vs_T01_GMI` in `RESULT_V1.json`, with the
underlying `T01_GMI`, `T09_MDL`, `T10_OCCAM_HARD` and `T12_SRM` scores
recomputed by route B.

**Strongest parents.** Rissanen (1978) for MDL and Vapnik (1998) for structural
risk minimization own two of the three disagreeing positions; `T10_OCCAM_HARD`
is a folk rule with no literature owner, and Blumer et al. (1987) is not tested.
`research/gmi-833-heldout-20-transitions-v1` owns the law they disagree with
(`PARENT_DISCLOSURE_V1.md`).

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

**Assumptions.** Each world is adjudicated by its own declared accounting,
computed by exhaustive enumeration over all `65552` candidates (`FREEZE_V1.md`
section 4); a `win` includes a correctly called exact tie. `GMI_REPAIRED` is the
repaired law of `DS-5`, `CTRL_SHIFTED_2LAMBDA` is the negative control `N2`, and
`R2` compares each predicted argmin risk summary `(k_now, k_delay, bits)` with
the declared-cost argmin set.

**Dependencies.** The registry and readouts of `DS-1`; the repaired law of
`DS-5` for the `GMI_REPAIRED` row; hypotheses `D5`, `D6`, `D8` and `D9`
(`FREEZE_V1.md` section 5); `scores` and `R2_disagreements_vs_declared_truth` in
`RESULT_V1.json`, which route B recomputes for `T01_GMI`, `GMI_REPAIRED`,
`T02_BAYES`, `T09_MDL`, `T10_OCCAM_HARD` and `T12_SRM` over exact risk summaries
rather than candidates.

**Falsifiers.** Registered in `FREEZE_V1.md` section 5: an `E-LIN` miss by
`T01_GMI` (`D5`, the consistency check), an `E-COD` miss by `T09_MDL` (`D8`) or
by the mechanism-faithful reading (`D9`), and any cell on which the two routes
disagree. The shifted control must lose (`N2`, `HS5`); a control that did not
lose would show that the table cannot register a loss.

**Strongest parents.** The owners of the scored rules in
`PARENT_DISCLOSURE_V1.md` section 1, and
`research/gmi-833-heldout-20-transitions-v1`, which owns the registered law and
the `2*lambda*` negative control. The `E-LIN` column restates that parent's
analytic argmin rather than discovering it, as the honest reading above says.

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

**Assumptions.** The `E-SKEW` family of `FREEZE_V1.md` section 2: the registered
accounting unchanged, each of the three input bits independently `1` with
probability `q in {1/5, 1/4, 1/3, 2/3, 3/4, 4/5}`, sequence weights exact
rational products, `324` worlds; `T01_GMI` applied verbatim. The refutation
concerns the unqualified law outside its uniform-input assumption, not the law
on `E-LIN`.

**Dependencies.** Hypothesis `D6` (`FREEZE_V1.md` section 5), recorded as `DP-1`
`REFUTED` in `FAILED_PREDICTION_REGISTER_V1.json`; the registered law of
`research/gmi-833-heldout-20-transitions-v1` and its uniform-input derivation;
the `E-SKEW` column of `DS-3`; route A's exact input-weighted simulation and
route B's recomputation over risk summaries.

**Falsifiers.** Registered as the falsifier of `D6`: `T01_GMI` correct on all
`324` `E-SKEW` worlds. Concretely, the first witness (`q = 1/5`, `p = 2/5`,
`eta = 1`, `lambda = 3/25`) would be withdrawn if exhaustive enumeration under
the declared accounting returned `PERSISTENT_STATE` there, and the `108` count
would be withdrawn if the two routes disagreed on it.

**Strongest parents.** `research/gmi-833-heldout-20-transitions-v1`, which owns
the law under test, and `research/gmi-833-z-z5-critical-phenomena-v1` (branch
`research/833-sec-z2`, PR #1034), which first found it to be a special case
along the alphabet-size dimension and whose failed-prediction register pattern
is reused (`PARENT_DISCLOSURE_V1.md`).

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

**Assumptions.** `R0(env)` is the minimum delayed-channel error rate attainable
without state under the environment's own input law: `min(q, 1-q)` on `E-SKEW`
and `1/2` for uniform inputs. On `E-COD`, which declares no `(eta, p)`, the law
is read through its mechanism (state is bought iff its price is below the
`14`-bit code the stateless optimum pays for its delayed errors); the claim is
on `R1` over the `404` registered worlds only.

**Dependencies.** Hypotheses `D7` and `D9` (`FREEZE_V1.md` section 5), `D7`
recorded as `DP-2` `CONFIRMED` in `FAILED_PREDICTION_REGISTER_V1.json`; the
diagnosis of `DS-4`; the `GMI_REPAIRED` scores in `RESULT_V1.json`, with route B
re-deriving the boundary analytically; for the reduction to `eta*p*(1 - 1/A)`,
the finding of `research/gmi-833-z-z5-critical-phenomena-v1`.

**Falsifiers.** Registered as the falsifiers of `D7` and `D9`: any `E-SKEW` miss
by the repaired law, or any `E-COD` miss by the mechanism-faithful reading. A
miss on any of the `60` `E-LIN` worlds, or an exact tie not reported as a tie
(`HS6`), would equally refute the `404`-world claim.

**Strongest parents.** `research/gmi-833-heldout-20-transitions-v1` (the
registered law it generalizes) and `research/gmi-833-z-z5-critical-phenomena-v1`
(the alphabet-size form it unifies). Because the repaired law is `R1`-identical
to the declared-cost argmin (`DS-6`), Savage (1954) and Berger (1985) own its
decision-theoretic content, and its residual is only the closed form
(`PARENT_DISCLOSURE_V1.md`).

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

**Assumptions.** The `404` worlds and the registry of `DS-1`; the seven parents
`T02`..`T08` are the declared-cost rules of `FREEZE_V1.md` section 3, each an
argmin of a positive affine function of the world's declared cost (including
`T05_NAS` with its weight set to the declared state price and `T06_ACTINF` with
a complexity term constant under the uninformative prior). "No discriminating
experiment exists" is stated at this scope and for these two readouts only.

**Dependencies.** The invariance of argmins under positive affine
reparameterization; the repaired law of `DS-5`; the executor check
`D12_repaired_law_R1_equivalent_to_declared_cost_parents` and `vs_GMI_REPAIRED`
in `RESULT_V1.json`, with route B's two-stage block scan; hypothesis `D10` for
the two abstaining parents and `D3`, `D4`, `D11` for the three distinguishable
ones; null `N1` (`DS-7`) for the claim that the equivalence is not a readout
artifact.

**Falsifiers.** One world in which `GMI_REPAIRED` and any of `T02`..`T08` issue
different `R1` predictions refutes the equivalence for that parent; a class
prediction from `T11_INFOTHEORY` or `T13_EVOPEN` (the falsifier of `D10`)
creates a discriminating experiment against it; and an `E-COD` miss by `T09_MDL`
(`D8`) would turn the environment-relative reading of its `E-LIN` losses into a
defect of the rule.

**Strongest parents.** Savage (1954) and Berger (1985), of whose argmin of
declared expected loss the equivalence is a property, together with the other
declared-cost owners Simon (1955), Russell & Subramanian (1995), Rice (1976),
Zoph & Le (2017), Friston (2010), Sutton & Barto (2018) and Alur et al. (2013);
Shannon (1948) and Lehman & Stanley (2008) for the abstaining parents; Rissanen
(1978) and Vapnik (1998) for the distinguishable ones (`PARENT_DISCLOSURE_V1.md`
section 1).

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

**Assumptions.** The `404` worlds and the `R1` readout; `N1` draws `200`
positive rational monotone scoring rules over `(rate_now, rate_delay, bits)`
from seeds `6100..6299`, `N2` is the `2*lambda*` threshold, and `N3` is a theory
that abstains in every world. Each hostile is a planted defect that must be
shown able to fire (`FREEZE_V1.md` section 7).

**Dependencies.** The nulls and hostiles frozen in `FREEZE_V1.md` sections 6-7;
the `DS-6` equivalences that `N1` tests and the `DS-3` table that `N2` and `N3`
calibrate; the `N1_*`, `N2_*`, `N3_*`, `HS1_leakage_flags` and `hostiles`
entries of `RESULT_V1.json`, asserted by `test_z6_discrimination_v1.py`.

**Falsifiers.** Registered in `FREEZE_V1.md` section 6: most random rules
`R1`-equivalent to `T01_GMI` would make the equivalence a coarse-readout
artifact; a shifted threshold with zero `E-LIN` misses would show that the test
cannot falsify; an always-abstainer with any win or loss, or counted as
equivalent, would show abstention leaking into agreement. A hostile that does
not fire voids its guard.

**Strongest parents.** `research/gmi-833-heldout-20-transitions-v1`, which owns
the `2*lambda*` negative control reused as `N2` (recorded as `DP-PARENT-SHIFTED`
in `FAILED_PREDICTION_REGISTER_V1.json`); none registered beyond
`PARENT_DISCLOSURE_V1.md`.

---

## What none of these results establish

No claim that GMI is truer than MDL as a theory; no claim that any parent
theory is refuted; no universal observational equivalence; nothing about real or
trained systems; no validation of the registered law beyond uniform inputs — the
opposite is shown; and no re-earning of the transition law's own rows, which
belong to `research/gmi-833-heldout-20-transitions-v1`.
