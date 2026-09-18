# Named results — gmi-833-h-real-scale-revival-v1

Every result below is stated at one registered scope and at no other. No result
here is composed with any certificate of any parent package; `FGS-2` forbids it
and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scopes, from `FREEZE_V1.md` section 3 as amended by `FREEZE_V2_ADDENDUM.md`
section 4. A scope is the tuple (family row, grammar, ecology, budget, freeze,
protected interface).

- `SIGMA_R02` — row `Linear regression / linear classifiers.`; grammar `G_S`;
  ecology `F02`, gap-1 autoregression on the sha256-bound `D2` PCM, design
  `(x_t, ..., x_{t+31})`, response `x_{t+33}`; 438,739 fitted rows, 87,747
  held-out rows.
- `SIGMA_R03B` — row `GLMs.`; grammar `G_S`; ecology `F03`, token-by-file
  occurrence counts on the sha256-bound `D3` CPython sources; 189,745 fitted
  rows, 37,948 held-out rows.
- `SIGMA_R04B` — row `Basis/kernel methods.`; grammar `G_S`; ecology `F04b`,
  strictly-positive-frame census on `D2`, design `(x_{t+1}, ..., x_{t+32})`,
  response `#{i in [t, t+31] : x_i > 0}`; 438,739 fitted rows, 87,747 held-out
  rows.

Of the three rows this tranche was permitted to reconcile, **one closes** at
11 of 11 (`RSR-3`) and **two are reported open**, each at 8 of 11 (`RSR-1`,
`RSR-4`). Four registered predictions failed — `Q2a`, `Q2h`, `Q3a`, `Q3i` —
and every one is named with its attribution below. Twelve hostiles all fire and
are all caught, none raises a false alarm on clean input, and the checker's
verdict is `GREEN`, which reports internal soundness and is explicitly not a
statement that any row closed.

---

## `RSR-3` — a response additive in a per-input non-affine transform recovers a lifted basis at `SIGMA_R04B`

**Statement.** At `SIGMA_R04B` the exhaustive family-blind enumerative search
over the 6,324 semantically distinct `(BODY, HEAD)` pairs of `G_S` chooses
`STEP(ARG) | MUL(BIAS,S)`, which the post-hoc classifier — reading expression
trees and never a family label — names `LIFTED_BASIS`, because `BODY` is not
affine in `ARG`. Fitted on 438,739 real rows and evaluated on 87,747 disjoint
held-out rows in exact rational arithmetic, its squared error is
`93262934797005291/3906250000000000`, while the affine arm fitted on the same
rows of the same real design is
`10409365429879412550444510356147/1073741824000000000000000000`, larger by a
factor of 406.046. The held-out
squared error is strictly positive, as registered: one summand of the
response, `[x_t > 0]`, lies outside the design, so the response is not exactly
attainable and the gate cannot be won by an identity. The chosen program is
minimal in the enumerated set — 2 `BODY` nodes and 3 `HEAD` nodes, each the
least node count achieving its denotation among 116 and 1,075 raw expressions.
The charged cost of a landmark arm first exceeds the compact lifted program's
at exactly `q* = 2`, 198 against 132, with 99 against 132 at `q* - 1`, and the
landmark arm's held-out exact squared error at `q*`,
`255404867735924132047/31250000000000000`, is larger than the lifted program's
by a factor of 342.318. The
independent regeneration on the disjoint slices recovers the same class. The
support-admissibility rule demoted 603 of 6,324 enumerated candidates here, so
it was neither inert nor total.

**Quantifiers.** This scope only. Nothing is claimed about basis or kernel
methods on ecologies whose response is not additive in a per-input non-affine
transform — see `RSR-5`, the matching boundary.

**Assumptions.** The `D2` digest holds at run time; the slice rule of
`FREEZE_V1.md` section 4; the fixed-denominator rationalisation of the
arithmetic addendum; the out-of-sample ranking of the V3 addendum; the charged
cost model of `grammar_s_v1`.

**Falsifiers.** A different chosen class; a lifted arm not strictly better than
the affine arm; a zero held-out squared error; no `q*` at or below 4,096; a
regeneration class that differs; a `SIGMA_R02` control that also chooses
`LIFTED_BASIS`.

**Strongest parents.** Aizerman, Braverman and Rozonoer 1964 for the lifted
feature map; Williams & Seeger 2001 and Rahimi & Recht 2007 for landmark
approximations and their cost trade-off; Koza 1992 and Schmidt & Lipson 2009
for search over an expression grammar. None of it is claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`REAL_SCALE_VALIDATION_COMPLETE`; `INDEPENDENT_TEAM_REPLICATION`; `M5`;
`EV4`; `EV5`; any statement about `SIGMA_4F`, `SIGMA_H04` or any parent scope.
In particular, no claim that a *weighted* per-input basis is recovered: `G_S`
has a three-node `BODY` budget, so `MUL(STEP(ARG),PARAM)` is outside the
enumerated set, and what is recovered is an unweighted per-input lifting with a
scalar head coefficient. `R05` at this scope rests on the cross-ecology matched
control alone; no randomised control was registered here, and none is claimed.

**Dependencies.** `grammar_s_v1.py` for the enumeration, the semantic quotient, the post-hoc classifier and the charged cost model; `FREEZE_V1.md` sections 3 to 8; `FREEZE_V1_ARITHMETIC_ADDENDUM.md` for the rationalisation operator; `FREEZE_V2_ADDENDUM.md` sections 3 to 5; `FREEZE_V3_ADDENDUM.md` section 2 for the out-of-sample ranking. It depends on no artifact of any parent package. Receipt: `REAL_RUNS/scope_R04.json`, `RESULT_V1.json` rows `R04`.

---


## `RSR-1` — at `SIGMA_R02` the class is recovered and the expression is not identified

**Statement, and the row is reported open.** The registered prediction `Q2a`
(`FREEZE_V1.md` section 8 `P2a`) is a conjunction: the chosen `BODY` is
semantically `MUL(ARG,PARAM)`, the chosen `HEAD` is semantically
`ADD(S,BIAS)`, the class is `AFFINE_SCORE`, and there is no `STATE`
dependence. **It failed.** The family-blind search chooses
`MUL(ARG,PARAM) | ADD(S,S)`: the body clause holds, the class clause holds,
and the head clause does not — `ADD(S,S)` is `2S`, a linear head with no
intercept, which is a different denotation from `ADD(S,BIAS)`. `R01` and `R04`
are therefore reported **open** at `SIGMA_R02` — and `R03` with them, for the
separate reason given below — and the row
`Linear regression / linear classifiers.` is **not closed**, at 8 of 11.

**What the failure is about, stated exactly.** The top eight ranked candidates
are all `AFFINE_SCORE` and all of the form (affine score, linear head), and
their out-of-sample squared errors on 26,325 ranking-score rows lie within
26,489 parts per billion of one another — 2.6 parts in 100,000: 5.40444 for
`ADD(S,S)`, 5.40457 for `ADD(BIAS,S)`, 5.40458 for the bare `S`. The fitted
intercept of the affine head was 0 at the registered rationalisation in the
first run, so this ecology has no intercept to recover. The **class** is identified and is
stable — it survives the regeneration on disjoint slices, and it survived the
V3 correction that moved the chosen expression. The **expression within the
class** is not identified at this scope: the ecology has no intercept to find,
so every linear head is the same function up to a rescaling of the per-index
parameters, and which one wins is decided by a margin far below any
meaningful resolution.

**The single-stage attribution.** The prediction, not the mechanism. `P2a`
registered an expression identity where the ecology can only identify a class.
A successor scope should register the class-level prediction — which held,
twice, under two different ranking procedures — and register an expression
identity only on an ecology whose response actually has an intercept to
recover.

**Why the clause that held is not substituted for the conjunction.**
`RESULT_V1.json` reports the three clauses of `Q2a` separately, labelled a
diagnostic. Reporting the class clause as if it were the prediction would be
`POST_HOC_FALSIFIER_REPLACEMENT`, which is in `forbidden_promotions` and is
the exact error this package was built to avoid repeating.

**A second registered prediction failed here, and it is reported too.** `Q2h`
asserted that the support-admissibility rule is inert at this scope **and**
that the chosen program is byte-identical to the first run's. The inertness
clause held — 0 of 6,324 enumerated candidates were demoted. The identity
clause did not: the first run chose `ADD(BIAS,S)` and the corrected run chose
`ADD(S,S)`, because the V3 ranking correction moved it. `Q2h` is scored as a
conjunction and fails, which leaves `R03` open at this scope alongside `R01`
and `R04`.

**What is nonetheless earned at `SIGMA_R02`, and stated as such.** Eight of the
eleven coordinates hold: the grammar, the matched controls including the
certified randomised control of `RSR-2`, the exact minimality of the chosen
program, the resource crossover at `m* = 5` (29 against the tabulated
alternative's 37, with 24 against 20 at `m* - 1`), the held-out frozen numbers
— exact squared error at 14,612,806 parts per billion of the best constant
arm's over 87,747 held-out rows, and 12,395 sign-decision errors against the
majority-sign arm's 40,324 — the regeneration, the independent search and the
real-scale thresholds of 438,739 fitted and 87,747 held-out rows. Eight of
eleven closes nothing. It is recorded so a successor lane knows exactly what
remains.

**Assumptions.** The `D2` digest holds at run time; the slice rule of `FREEZE_V1.md` section 4; the fixed-denominator rationalisation; the out-of-sample ranking of the V3 addendum. The claim that the head is unidentified assumes only that the reported out-of-sample losses are the ones the registered procedure produces, which the committed receipt replays exactly.

**Dependencies.** `grammar_s_v1.py` for the enumeration, the semantic quotient, the post-hoc classifier and the charged cost model; `FREEZE_V1.md` sections 3 to 8; `FREEZE_V1_ARITHMETIC_ADDENDUM.md` for the rationalisation operator; `FREEZE_V2_ADDENDUM.md` sections 3 to 5; `FREEZE_V3_ADDENDUM.md` section 2 for the out-of-sample ranking. It depends on no artifact of any parent package. Receipt: `REAL_RUNS/scope_R02.json`, `REAL_RUNS/controls.json`, `RESULT_V1.json` rows `R02`.

**Falsifiers.** A chosen class other than `AFFINE_SCORE` at this scope, which would make the failure a class failure rather than an expression failure; a top-eight out-of-sample spread wide enough to identify one head, which would make the expression identifiable after all; a non-zero fitted intercept, which would give the ecology an intercept to recover.

**Strongest parents.** Legendre 1805 and Gauss 1809 for least squares; Makhoul 1975 for linear prediction of a sampled waveform; Koza 1992 and Schmidt & Lipson 2009 for search over an expression grammar. The identifiability observation is elementary and is not claimed novel.

---


## `RSR-2` — a control is evidence only when it is certified to have bitten

**Statement.** At `SIGMA_R02`, 200 response-permutation controls were built
under seed 20260918: the response column was permuted across the 438,739-row
fit slice, the same program was refitted by the same routine, and each refit
was scored on the untouched 87,747-row held-out slice. All 200 landed inside
the registered applicability band `[9/10, 11/10]` of the best constant arm's
exact held-out squared error, which is what certifies that the permutation
destroyed the design-response relation. 0 of 200 beat the chosen arm, which
sits strictly outside the band the controls occupy. The exact ratios are in
`REAL_RUNS/controls.json` and are reproduced in `RESULT_V1.json` under `Q2d`.

**Why the certificate is the content.** `gmi-833-h-real-scale-classical-v1`
registered a control that refitted least squares on a *permuted design* and
compared it with the best constant arm. That control **nests** the arm it is
compared with — at zero slopes it *is* the constant arm — so 98 of its 200
controls beat the constant arm by coin flip and the comparison carried no
information in either direction. The defect is of the same kind as a hostile
that cannot fire. The remedy is not a better outcome but a **stated
applicability condition that fails the run when the control does not bite**,
and that is what is registered and met here.

**Scope note.** This result holds at `SIGMA_R02`, whose row is reported open by
`RSR-1`. A methodological result does not need its row to close, and it does
not license closing it.

**Falsifiers.** Fewer than 200 controls inside the band — which fails the run,
not merely the prediction; any control at or below the chosen arm; a chosen arm
inside the band.

**Forbidden extrapolations.** `REGISTERED_CONTROL_SUBSTITUTION` — the earlier
package's informative diagnostic is not imported here and is not offered as a
falsifier, there or here.

**Assumptions.** The permutation is drawn under the registered seed 20260918; the fit and held-out slices are disjoint by the rule of `FREEZE_V1.md` section 4; the refit uses the same routine and the same rationalisation as the arm it is compared with.

**Dependencies.** `grammar_s_v1.py` for the enumeration, the semantic quotient, the post-hoc classifier and the charged cost model; `FREEZE_V1.md` sections 3 to 8; `FREEZE_V1_ARITHMETIC_ADDENDUM.md` for the rationalisation operator; `FREEZE_V2_ADDENDUM.md` sections 3 to 5; `FREEZE_V3_ADDENDUM.md` section 2 for the out-of-sample ranking. It depends on no artifact of any parent package. Receipt: `REAL_RUNS/controls.json`, `RESULT_V1.json` prediction `Q2d`.

**Strongest parents.** Permutation testing is classical and is not claimed novel. That an unconstrained least-squares fit nests the intercept-only model is textbook regression, not a finding here.

---


## `RSR-4` — at `SIGMA_R03B` the link's admissibility is recovered and the link itself is not

**Statement, and it is a negative.** The registered prediction `Q3a` failed and
the row `GLMs.` is **reported open**.

What held, all of it registered before the outcome: the ecology is admissible
by its pre-fit condition — minimum response 1, 333 distinct responses, exact
variance-to-mean ratio 75.756 over 189,745 fit rows. On 37,948 held-out rows
the log-link arm is strictly closer to the real count than the identity-link
arm on 22,278 rows against 15,670, with 0 ties, and emits 0 negative predicted
means against the identity arm's 779. **That is the criterion
`gmi-833-h-real-scale-classical-v1` failed, carried over unchanged, and it
holds here** on a response bounded below by one — which is what the ecology
lever of `FREEZE_V2_ADDENDUM.md` was for.

What failed: the family-blind search chooses `STEP(ARG) | MUL(BIAS,RECIP(S))`,
classified `LIFTED_BASIS`, where `NONLINEAR_LINK` was registered. The first run
had chosen `MUL(ARG,PARAM) | ADD(BIAS,S)`, `AFFINE_SCORE`. The single lever —
a generic support-admissibility rule demoting candidates that emit predictions
outside the registered one-sided response support — fired, demoting 484 of
6,324 enumerated candidates, and did remove the affine score. It did not
produce a link.

**The second attribution.** Under a generic squared loss on a real
over-dispersed count response, non-negativity is cheaper to buy by lifting the
**input** than by bending the **link**: a per-input indicator makes the fold
value non-negative before the head is applied, so the whole admissible region
is reachable without a non-affine map of `S`. The classifier's registered
priority then names the result `LIFTED_BASIS`, correctly. The regeneration on
the disjoint slices chooses `MUL(ARG,PARAM) | ABS(RECIP(S))`, `NONLINEAR_LINK`
— a different class, which fails `R09` and shows the two routes to
admissibility are close in loss at this scope.

**What this negative licenses.** That the *link* of a generalized linear model
is not identified by a family-blind search that ranks by out-of-sample squared
error and respects support, on this ecology. It does **not** license any claim
that the link is unidentifiable in general. Identifying it plausibly requires a
loss that is proper for counts — and a proper scoring rule is exactly the
family information the search may not receive. Naming that tension is the
useful part of the result, and it is a concrete instruction for a successor
scope: the open question is whether a *generic* criterion exists that separates
a link from a lifting without being told the response is a count.

**Not attempted again here.** `FREEZE_V2_ADDENDUM.md` section 6 fixed, before
the outcome, that one revival is permitted per failure and a second failure is
reported rather than iterated. `ECOLOGY_ITERATION_UNTIL_POSITIVE` is in
`forbidden_promotions` and the first-run receipts remain committed under
`REAL_RUNS_V1/`.

**Assumptions.** The `D3` digest holds at run time; the ecology's pre-fit admissibility condition is checked on the fit slice only and before any arm exists; the two fitted arms use the same design, the same slices and the same rationalisation.

**Dependencies.** `grammar_s_v1.py` for the enumeration, the semantic quotient, the post-hoc classifier and the charged cost model; `FREEZE_V1.md` sections 3 to 8; `FREEZE_V1_ARITHMETIC_ADDENDUM.md` for the rationalisation operator; `FREEZE_V2_ADDENDUM.md` sections 3 to 5; `FREEZE_V3_ADDENDUM.md` section 2 for the out-of-sample ranking. It depends on no artifact of any parent package. Receipt: `REAL_RUNS/scope_R03.json`, `REAL_RUNS_V1/scope_R03.json` for the first outcome, `RESULT_V1.json` rows `R03`.

**Falsifiers.** A chosen class of `NONLINEAR_LINK` under the registered procedure, which would close the row; a regeneration that recovers the same class as the main run, which would remove the instability this result reports; a log-link arm that is not strictly closer on a majority of held-out rows, or that emits a negative predicted mean, either of which would falsify the part that held.

**Strongest parents.** Nelder & Wedderburn 1972 and McCullagh & Nelder 1989 for the link and for the admissibility argument; Cameron & Trivedi 2013 for over-dispersion and exposure. The negative result is about a search procedure, not about generalized linear models, which are theirs and are not in question.

---


## `RSR-5` — the boundary of lifted-basis recovery, earned by two counterexamples

**Statement.** Lifted-basis recovery at `SIGMA_R04B` is conditional on the
ecology, and the condition is sharp enough to fail twice in the record.

1. `gmi-833-h-real-scale-classical-v1` registered an ecology whose response is
   the energy of the *next* window. That response is not additive in any
   per-input non-affine transform, and a squared affine score approximates it
   well; its family-blind search over an equivalent grammar returned a
   non-affine head, not a lifted basis. A real ecology on which recovery fails.
2. This package's own first registration, `F04`, counted frames with
   `x_i >= 0`. The only per-input indicator `G_S` contains is strict,
   `STEP(a) = 1 iff a > 0`, and `D2` carries 65,023 exactly-zero frames out of
   614,266 — 10.585 per cent — so the two counts differ on 119,860 of 614,233
   rows by 3.386 of 32 on average and by as much as 32. The response was
   therefore not additive in any transform the grammar can express and the
   search returned `AFFINE_SCORE`. `REAL_RUNS_V1/scope_R04.json` is that
   receipt, still committed.

**What the pair maps.** Recovery holds when the response is additive in a
per-input transform **the grammar actually contains**, and fails both when the
response is not of that form at all (1) and when it is of that form for a
transform just outside the grammar's reach (2). The second is the sharper
boundary, because it shows the condition is on the ecology-grammar pair and not
on the ecology alone.

**Label.** `EARNED_BY_COUNTEREXAMPLE`. A boundary, not an impossibility: both
obstructions name their own removal.

**Assumptions.** Both counterexamples are read from committed receipts: the parent's own `RESULT_V1.json` for (1), read as a published outcome and not as evidence for any gate here, and this package's `REAL_RUNS_V1/scope_R04.json` for (2). The zero-frame count is a property of the `D2` bytes under their registered digest.

**Dependencies.** `grammar_s_v1.py` for the enumeration, the semantic quotient, the post-hoc classifier and the charged cost model; `FREEZE_V1.md` sections 3 to 8; `FREEZE_V1_ARITHMETIC_ADDENDUM.md` for the rationalisation operator; `FREEZE_V2_ADDENDUM.md` sections 3 to 5; `FREEZE_V3_ADDENDUM.md` section 2 for the out-of-sample ranking. It depends on no artifact of any parent package. Receipts: `REAL_RUNS_V1/scope_R04.json` and `REAL_RUNS/scope_R04.json`.

**Falsifiers.** A lifted basis recovered on an ecology whose response is not additive in any per-input transform the grammar contains, which would show the condition is not necessary; a grammar extension that recovers a lifted basis on the `x_i >= 0` response without changing the response, which would move the boundary from the pair to the ecology alone.

**Strongest parents.** Aizerman, Braverman and Rozonoer 1964 for the lifted feature map. The boundary itself is this package's, earned by counterexample and claimed no more widely than the two ecologies that produced it.

---


## `RSR-7` — an in-sample ranking stage rewards capacity, measurably

**Statement.** A two-stage family-blind search whose ranking stage refits and
scores its survivors on the same rows systematically favours candidates with
more state. At `SIGMA_R02`, on 87,747 rows of the search slice, the stateful
candidate `MUL(ARG,PARAM) | ADD(S,STATE)` attains squared error 8.29877 against
the affine `MUL(ARG,PARAM) | ADD(BIAS,S)` at 8.30709 — a 0.100 per cent
in-sample win. Refitted and scored on 100,000 disjoint fit rows the same two
give 20.7657 against 6.68889 — a factor of 3.105 the other way. The in-sample
winner also flipped with the block size, 20,000 rows choosing the affine head
and 87,747 the stateful one.

**Consequence, and it is the reason this package has fewer closures.** The
correction registered in `FREEZE_V3_ADDENDUM.md` — score the ranking stage out
of sample inside the search slice — moved the chosen expression at
`SIGMA_R02` from `ADD(BIAS,S)` to `ADD(S,S)` and thereby falsified `Q2a`,
turning a row that the uncorrected procedure would have closed into the open
row of `RSR-1`. The correction was registered before the re-run and its
direction was not known when it was registered.

**Why it is stated as a result.** Any package in this programme that ranks
grammar candidates in sample, on a grammar containing a delay cell, is exposed
to the same bias, and the bias is small enough in sample to be invisible and
large enough out of sample to decide a row.

**Falsifier.** An out-of-sample comparison at this scope that does not reverse
the in-sample ordering.

**Strongest parents.** Out-of-sample model comparison is classical; Rissanen
1978 for the description-length view of the same problem. Not claimed novel.

**Assumptions.** Both arms are fitted by the same generic routine with the same ridge and the same convergence budget; the 100,000-row comparison slice is disjoint from the 87,747-row search slice by the rule of `FREEZE_V1.md` section 4.

**Dependencies.** `grammar_s_v1.py` for the enumeration, the semantic quotient, the post-hoc classifier and the charged cost model; `FREEZE_V1.md` sections 3 to 8; `FREEZE_V1_ARITHMETIC_ADDENDUM.md` for the rationalisation operator; `FREEZE_V2_ADDENDUM.md` sections 3 to 5; `FREEZE_V3_ADDENDUM.md` section 2 for the out-of-sample ranking. It depends on no artifact of any parent package. The measurement itself is reproduced by refitting the two named candidates on the two named slices; the corrected ranking is what every receipt under `REAL_RUNS/` was produced by.

---


## `RSR-6` — no certificate here rests on a parent's

**Statement.** Of the 33 gate certificates this package emits, every one
carries the `sigma` of its own row and none carries `SIGMA_4F`, `SIGMA_H01`,
`SIGMA_H02`, `SIGMA_H03`, `SIGMA_H04` or `SIGMA_CENSUS`. No parent
`RESULT_V1.json` is read by the checker. Both facts are asserted by tests and
by a CI step, and a registered hostile confirms that a certificate stamped with
a parent scope, or citing a parent artifact as evidence, is caught.

**Why it is stated as a result.** `gmi-833-h-family-requirement-ledger-v1`
`HRL-1` and PR #997 `FGS-2` establish that a coordinate earned at one scope may
not be conjoined with coordinates earned at another. Two packages already hold
ten of eleven for these rows. The tempting move — supply the eleventh at a new
scope and declare the conjunction — is exactly what `FGS-2` forbids, so the
absence of any imported certificate is part of what makes the one closure here
admissible, and is therefore recorded rather than assumed.

**Assumptions.** The gate ledger in `RESULT_V1.json` is the complete set of certificates this package emits; the checker's own reachable paths are confined to the package directory, which a test asserts by scanning its string literals.

**Dependencies.** `RESULT_V1.json` for the certificates; `test_real_scale_revival_v1.py` and `ci_gates_v1.py` for the assertions; `PARENT_LEDGER.md` for what is taken from each parent and what is not. It depends on no parent certificate, which is the content of the result.

**Falsifiers.** Any gate certificate carrying a scope other than its own row's; any evidence string naming a parent scope or a parent artifact; any path in the checker that reaches outside the package directory. A registered hostile, `H_PARENT_GATE_IMPORT`, plants each of the first two and is caught.

**Strongest parents.** `gmi-833-h-family-requirement-ledger-v1` `HRL-1` and PR #997 `FGS-2`, which establish the scope-gluing no-go this result complies with.

