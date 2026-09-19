# GMI #833 human/external-gate rows — labelled model-proxy discharge, freeze v1

Source `main`: `f7f01e78ae5bfbeea5364166735c5c83b1eca913`.

Committed **before** any executor, oracle, proxy record, protocol run, test or
receipt in `research/gmi-833-human-gate-proxy-v1/` exists. `git log` must show
this commit strictly preceding the first implementation commit of this package,
and every review brief under `briefs/` is part of this same commit: a proxy is
spawned only against a brief whose sha256 is listed in section 9 below.

## 1. Claim ceiling

```
GMI_833_HUMAN_GATE_ROWS_DISCHARGED_BY_LABELLED_MODEL_PROXY_AT_REGISTERED_ARTIFACT_SCOPE
```

Every row this package closes closes with the label
`HUMAN_GATE_BYPASSED__MODEL_PROXY` visible in its reconciliation line. A model
proxy is never presented as an external, human, third-party or independent-team
outcome. The operator's standing directive of 2026-09-04 (human/external gates
close with their strongest legitimate proxy, labelled, never marked as
externally obtained) is the authority for the bypass; the label is the
disclosure.

## 2. The exact rows this tranche may reconcile

Forty rows, in three issue comments, all `### `-anchored. Snapshots of the three
live bodies fetched immediately before this freeze are committed byte-exact under
`snapshots/` (sha256 in section 10). Row text below is verbatim.

### 2.1 Comment `5684819296` (Section Z), 32 rows

> ### Z9 — Blind external prediction protocol

- [ ] Separate theory/prediction team from environment/test team.
- [ ] Test team constructs held-out environments independently.
- [ ] Prediction team receives only preregistered allowed descriptors.
- [ ] Prediction team freezes morphology, capability, crossover and failure predictions.
- [ ] Test team executes without theory tuning.
- [ ] Third party/adjudicator scores predictions.
- [ ] Repeat across multiple independent batches.

Row ids: `Z9-1` .. `Z9-7` in that order.

> ### Z10 — Real-system prospective morphology selection

- [ ] Select at least five materially different real domains.
- [ ] Include language/reasoning.
- [ ] Include planning/control.
- [ ] Include programmatic/scientific reasoning.
- [ ] Include continual/adaptive learning.
- [ ] Include multi-agent or embodied interaction.
- [ ] Predict morphology/resource crossovers before training/evaluation.
- [ ] Measure CPU/GPU/wall-time/memory/I/O/energy/communication where relevant.
- [ ] Compare predicted and observed Pareto fronts.
- [ ] Replicate with independent implementations and hardware where feasible.

Row ids: `Z10-1` .. `Z10-10`.

> ### Z14 — Cross-substrate and natural-intelligence test

- [ ] Test whether the same GMI law predicts across multiple computational substrates.
- [ ] Freeze at least one cross-species natural-cognition prediction without fitting to the held-out species.
- [ ] Use ecology/body/sensor/resource/development descriptors only at the registered scope.
- [ ] Compare predicted capability organization with cognitive-science/behavioral evidence.
- [ ] Include species/ecologies expected to falsify simple anthropocentric stories.
- [ ] Separate functional prediction from biological implementation claims.
- [ ] Do not claim neuroscience mechanism unless independently derived/tested.

Row ids: `Z14-1` .. `Z14-7`.

> ### Z18 — Independent hostile scientific review

- [ ] Recruit/assign independent theorem reviewer(s).
- [ ] Recruit/assign independent experimental-method reviewer(s).
- [ ] Recruit/assign parent-literature reviewer(s).
- [ ] Recruit/assign statistics/causal-inference reviewer(s).
- [ ] Recruit/assign cognitive-science reviewer if natural-intelligence claims remain.
- [ ] Give reviewers authority to reopen any green gate.
- [ ] Resolve every material objection or downgrade the claim.
- [ ] Freeze a final hostile-review report before manuscript submission.

Row ids: `Z18-1` .. `Z18-8`.

### 2.2 Comment `5684607872` (Sections AA/AC/AD), 7 rows

> ### AA. Recursive loophole / logic-gap closure

- [ ] Require independent hostile review before a gap can be marked exhausted.
- [ ] Add proof-assistant/formal-verification targets for the flagship mathematical spine where practical.
- [ ] Run a final recursive hostile sweep before any flagship manuscript freeze.

Row ids: `AA10`, `AA15`, `AA41` (10th, 15th and 41st checklist rows of the section).

> ### AC. Literature saturation / terminology authority

- [ ] For every core GMI construct, collect canonical and modern parent literature before naming it.
- [ ] Maintain citation-backed definitions rather than model-generated definitions.
- [ ] Re-run literature search before manuscript freeze because terminology and neighboring work can change.

Row ids: `AC02`, `AC05`, `AC09` (2nd, 5th and 9th rows of the section).

> ### AD. Recursive research loop

- [ ] Require flagship claims to survive at least one independent hostile team/lane that did not author the original result.

Row id: `AD08` (8th row of the section).

### 2.3 Comment `5693520829` (Section AG), 1 row

> ### AG8 — Recursive foundation descent protocol

- [ ] Require an independent formal-logic/foundations review of the stopping point.

Row id: `AG8-R48` (the caller's label; it is the 49th checklist row of the
live body counted from 1 and the only unchecked row under the AG8 anchor).

**No neighboring row is earned here.** Nothing else in Z1–Z17, nothing else in
AA/AB/AC/AD, nothing else in AG0–AG13, nothing in the issue body. The `## `
prose blocks of the three comments carry no rows.

## 3. What a proxy is, and what it is not

A proxy is a **fresh-session model given only the final artifact**: an agent
spawned with a brief from `briefs/` and nothing else — not this conversation,
not this freeze, not any lane's reasoning, checklist or reconciliation line. It
performs the review or protocol role the row assigns to a person or team, with
exactly the information such a reviewer would receive. Its complete reply is
stored verbatim as `proxies/<ID>.verdict.txt` and never edited. Its verdict is
never re-prompted. If the lane disagrees with a verdict, the disagreement is
recorded beside it (`DISAGREEMENTS_V1.md`); the verdict is not overwritten.

Isolation is by instruction, as in the precedents
`research/independent-authorship-gate-v1` (P1E3) and
`research/m2-traversal-capital-v1/m2p3/authored/PROVENANCE.json`: the agent is
told to read only the listed files and receives the harness's standard global
instruction files, which name projects in passing but carry no result, claim or
assessment of the reviewed artifacts. Each brief forbids citing any
self-assessment found inside the artifacts (ceilings, GREEN verdicts, hostile
tables) as evidence.

Served model: every record carries the model alias requested from the Agent tool
and the model's own self-report. Where a row demands two independent proxies
(`AG8-R48`, `AC05`) the two are spawned from **different model families**
(`opus` and `sonnet`) against the same brief.

Forbidden promotions (never written into any `new` line or receipt):
`EXTERNALLY_REVIEWED`, `INDEPENDENT_TEAM_REPLICATION`, `M5`,
`HUMAN_REVIEW_OBTAINED`, `THIRD_PARTY_ADJUDICATED`, `REAL_SYSTEM_VALIDATED_BY_PROXY`,
`COGNITIVE_SCIENCE_EVIDENCE_OBTAINED`, `CROSS_SPECIES_PREDICTION_CONFIRMED`,
`PROXY_VERDICT_IS_TRUTH`, `MANUSCRIPT_READY`, `COMPLETE_GMI`.

## 4. Proxy set and decision rules (frozen now)

| id | brief | model | rows | decision rule for closure |
|---|---|---|---|---|
| PX-Z18-THM | `BRIEF_Z18_THEOREM_REVIEWER.md` | opus | Z18-1 (+AD08) | record complete with per-claim verdicts |
| PX-Z18-EXP | `BRIEF_Z18_EXPERIMENTAL_METHOD_REVIEWER.md` | opus | Z18-2 (+AD08) | same |
| PX-Z18-LIT | `BRIEF_Z18_PARENT_LITERATURE_REVIEWER.md` | opus | Z18-3 (+AD08) | same |
| PX-Z18-STAT | `BRIEF_Z18_STATISTICS_CAUSAL_REVIEWER.md` | opus | Z18-4 (+AD08) | same |
| PX-Z18-COG | `BRIEF_Z18_COGNITIVE_SCIENCE_REVIEWER.md` | opus | Z18-5 (+AD08) | same; the reviewer first states whether natural-intelligence claims remain |
| PX-Z18-EDIT | `BRIEF_Z18_EDITOR_SYNTHESIS.md` | opus | Z18-7, AD08 | sees the five verdicts and the lane's `RESPONSES_V1.md`; Z18-7 SATISFIED iff every objection it marks material is RESOLVED or DOWNGRADED; AD08 SATISFIED iff no flagship claim's final disposition is OPEN and claim C1 is SURVIVED at original strength |
| PX-AA41 | `BRIEF_AA41_RECURSIVE_HOSTILE_SWEEP.md` | opus | AA41 | proxy verdict; every descendant gap it finds must appear in `SWEEP_FINDINGS_V1.json` |
| PX-AA15 | `BRIEF_AA15_FORMAL_TARGETS.md` | opus | AA15 | proxy names practical targets and writes Lean 4 statement stubs; SATISFIED iff ≥1 target and every stub type-checks under Lean 4.14 core on laptop-billy (`sorry` permitted, exit 0) |
| PX-AG8-A / PX-AG8-B | `BRIEF_AG8_R48_FOUNDATIONS_REVIEW.md` | opus / sonnet | AG8-R48 | SATISFIED iff **both** return SATISFIED; any disagreement keeps the row open with both verdicts recorded |
| PX-AC05-A / PX-AC05-B | `BRIEF_AC05_CITATION_VERIFICATION.md` | opus / sonnet | AC05 | SATISFIED iff both agree every definition row has ≥1 live-source-verified citation and no row rests on a fabricated or mismatched one; the per-row agreement matrix is recorded |
| PX-AC02 | `BRIEF_AC02_PARENT_LITERATURE_COLLECTION.md` | opus | AC02 | proxy verdict |
| PX-AC09 | `BRIEF_AC09_LITERATURE_RERUN.md` | opus | AC09 | proxy verdict; the `new` line states the requirement re-triggers at any manuscript freeze |
| PX-Z10 | `BRIEF_Z10_REAL_SYSTEM_REVIEW.md` | opus | Z10-1..10 | per-row proxy verdict |
| PX-Z14-SUB | `BRIEF_Z14_CROSS_SUBSTRATE_REVIEW.md` | opus | Z14-1 | proxy verdict |
| PX-Z14-COG | `BRIEF_Z14_NATURAL_COGNITION_REVIEW.md` | opus | Z14-2..7 | per-row proxy verdict |
| PX-Z9-T1/T2 | `BRIEF_Z9_TEST_TEAM.md` | sonnet / opus | Z9-2 | environment batch authored from the family spec only |
| PX-Z9-P1/P2 | `BRIEF_Z9_PREDICTION_TEAM.md` | opus / sonnet | Z9-3, Z9-4 | predictions from descriptors + theory only |
| PX-Z9-A1/A2 | `BRIEF_Z9_ADJUDICATOR.md` | sonnet / opus | Z9-6 | scores from predictions + outcomes only |
| (executor) | — | — | Z9-1, Z9-5, Z9-7 | role separation, frozen-oracle execution and two batches are properties of the protocol record, decided by the executor |
| (executor) | — | — | AA10 | exhaustion gate over the live gap graph (section 6) |
| (executor) | — | — | Z18-6, Z18-8 | reopen authority granted in every brief and every REOPEN demand honoured in `REOPENED_GATES_V1.json`; hostile-review report committed with sha256 before any manuscript submission (none exists on `main`) |

A row whose proxy returns `NOT_SATISFIED` or `UNDECIDABLE_FROM_ARTIFACTS` is
listed under `not_closed` with the proxy's verbatim reason. No row closes by a
proxy being re-run. No proxy is asked twice.

## 5. Z9 protocol, registered before any environment or prediction exists

**Environment family (the only thing the test team receives).** An environment
is `(L, target_0, target_1, p, eta, lambdas)`: sequence length `L ∈ {3, 4}`,
all `2^L` binary sequences equiprobable; a mode bit `M ∈ {0,1}` fixed per
episode and visible to the candidate, with `M=1` prevalence `p ∈ [0,1]`; scored
times `t = 1..L-1`; the mode-`m` target at time `t` is `target_m(w_t)` for the
window `w_t = (x_t, x_{t-1}, x_{t-2})` with `x_j = 0` for `j < 0`, from the menu
`CUR, NOT_CUR, PREV, NOT_PREV, PREV2, XOR, XNOR, AND, OR, NAND, XOR2, AND2, OR2,
MAJ3, CONST0, CONST1` (defined in the brief); `eta > 0`; each `lambda > 0`.
Candidate universe, fixed: 16 stateless output tables on `(M, x_t)` and
`256 × 256` one-bit transducers with next-state and output tables on
`(S, M, x_t)`, `S_0 = 0`. Objective
`J = eta·[(1-p)·e_0 + p·e_1] + lambda·state_bits`, `e_m` the exact mean 0/1
error over mode-`m` scored cells. All arithmetic exact.

**Theory (the only thing the prediction team receives beyond descriptors).**
Stated in `BRIEF_Z9_PREDICTION_TEAM.md`: the winner is the argmin of `J` over
both classes; within the stateless class the optimum is cell-wise over
`(M, x_t)`; within the one-bit class the theory asserts the optimum is attained
by machines whose state at time `t` equals `x_{t-1}`, hence cell-wise over
`(M, x_t, x_{t-1})`; crossover `lambda* = eta·[E_stateless − E_onebit]`, tie at
equality. This is the `lambda* = eta·p/2` law of
`gmi-833-heldout-20-transitions-v1` generalized to the family; targets
`PREV2/XOR2/AND2/OR2/MAJ3` reach beyond the window that law was derived on and
can falsify the one-bit clause.

**Order, enforced by git.** (1) this freeze; (2) test-team batch
`z9/batch_<b>/ENVIRONMENTS.json` committed; (3) prediction-team
`z9/batch_<b>/PREDICTIONS.json` committed with its sha256; (4) the frozen exact
oracle (`z9_oracle_a_v1.py` full enumeration, `z9_oracle_b_v1.py`
independent per-next-state-table cell-wise optimisation, both committed before
step 3) executed on laptop-billy — mechanical, no parameter is tunable;
(5) `z9/batch_<b>/OUTCOMES.json` committed; (6) adjudicator record. Two
batches with disjoint agents, `b ∈ {1, 2}`. A wrong prediction is recorded as a
scientific outcome, never repaired.

## 6. AA10 gate, registered now

Over `research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json` (1140 records,
all `status: OPEN` at `source_main`): a record may carry a status in
`{EXHAUSTED, RECURSION_EXHAUSTED, NO_MATERIAL_GAP_REMAINS}` only if it carries an
`independent_hostile_review` object with `reviewer_kind ∈ {EXTERNALLY_REVIEWED,
HUMAN_GATE_BYPASSED__MODEL_PROXY}`, a `reviewer_id` distinct from `owner_role`,
and a `verdict_sha256`. Census at pin: 0 exhausted, 0 violations. A planted
exhausted record without review must fail the gate.

## 7. Hostiles that must be DETECTED, and the null

H1 label removed from a proxy record; H2 verbatim verdict edited (sha mismatch);
H3 brief edited after freeze (sha mismatch); H4 artifact edited after the proxy
read it (blob sha mismatch); H5 a forbidden promotion token in a `new` line;
H6 a row listed as closed whose proxy said NOT_SATISFIED; H7 a two-route row
carried by one record or by two records of the same model family; H8 a planted
exhausted gap without review; H9 Z9 predictions edited after outcomes; H10 a
planted oracle A/B disagreement; H11 an `old` string absent from, or occurring
twice in, the live snapshot; H12 a REOPEN demand missing from
`REOPENED_GATES_V1.json`. Null: 200 seeded random record sets pass integrity
`0/200`; 200 seeded random Z9 predictors match every exhaustive `(environment,
lambda)` winner set `0/200`.

## 8. Two routes

Route A `human_gate_proxy_v1.py` (record integrity, closure set, Z9 scoring
via oracle A, AA10 gate). Route B `independent_oracle_v1.py` (re-derives every
count with separately written parsing, closure set by set equality, Z9 outcomes
via oracle B, AA10 by an independent walk); imports nothing from route A.

## 9. Brief digests (sha256, this commit)

| brief | sha256 | bytes |
|---|---|---:|
| `briefs/BRIEF_AA15_FORMAL_TARGETS.md` | `4bcdff2ef11adba4f3b481bfc0c09e58d849e0c48e99dabdf55634ac8610d8de` | 4905 |
| `briefs/BRIEF_AA41_RECURSIVE_HOSTILE_SWEEP.md` | `fb299385ad66a2048b4c74b96cc1c66fba136b31ccc56c17317f0f35179f6b95` | 4039 |
| `briefs/BRIEF_AC02_PARENT_LITERATURE_COLLECTION.md` | `fb9009f7b9df0adf06614431039f82dc0245fb2a662e6eeda403e6b4167ac712` | 3751 |
| `briefs/BRIEF_AC05_CITATION_VERIFICATION.md` | `b2a33902ae9e25519e8e2aa7f123277047847a8496a7f24e2c1206db0758533a` | 4112 |
| `briefs/BRIEF_AC09_LITERATURE_RERUN.md` | `ac0b28e74a241c5de253f930f80afc0fb9aef8fdaf0fb20cd3bc2a2e8d3878fb` | 3847 |
| `briefs/BRIEF_AG8_R48_FOUNDATIONS_REVIEW.md` | `12770090dd9aae3881cdf687fea763be92b4bf58271e11442d78a6146200b3c9` | 6222 |
| `briefs/BRIEF_Z10_REAL_SYSTEM_REVIEW.md` | `12c2bb0dc8202cb25158b102a78d95ef53405b5f7a481d87a2cb01a1686871ea` | 4167 |
| `briefs/BRIEF_Z14_CROSS_SUBSTRATE_REVIEW.md` | `4244920fe30242f814283c37a3aecb8082f10f23baf6bb273b487cc1e009cec7` | 3935 |
| `briefs/BRIEF_Z14_NATURAL_COGNITION_REVIEW.md` | `6a09ab8613b2843873c0eb240d92e1f28bf90484181d0b1a93e5a980e669c822` | 4727 |
| `briefs/BRIEF_Z18_COGNITIVE_SCIENCE_REVIEWER.md` | `edae81a26fb9f489b290e513b3c23272a6457950d3383f47c1c8dfb5ee0e7000` | 4288 |
| `briefs/BRIEF_Z18_EDITOR_SYNTHESIS.md` | `9f77a6aa3dc112632627a9dc630626f1656b3abe36e4e65fb989b22e3c071597` | 4464 |
| `briefs/BRIEF_Z18_EXPERIMENTAL_METHOD_REVIEWER.md` | `371674b2b474231caa22b02008becdd8965358b4bfec4e84e871a8cbbaabf7b4` | 4440 |
| `briefs/BRIEF_Z18_PARENT_LITERATURE_REVIEWER.md` | `0b9d0c8c4d7383d96ab40bacd14ce2873896ea4f808b599376232d755d895620` | 4384 |
| `briefs/BRIEF_Z18_STATISTICS_CAUSAL_REVIEWER.md` | `b80f2e97b815c78690b94e3b93c56e32861b438f2df1807383e40fc2be22df64` | 4464 |
| `briefs/BRIEF_Z18_THEOREM_REVIEWER.md` | `02778f87e3f2ec13ae1afc56f1742fd405b27559b1da457566e381174cde3b3b` | 4702 |
| `briefs/BRIEF_Z9_ADJUDICATOR.md` | `2b78a67374491ad2a8251eea5edd3e8340f85e9cd026d8f89e6301f5e2dfd391` | 2037 |
| `briefs/BRIEF_Z9_PREDICTION_TEAM.md` | `b38be4db419f6841c129f6d0220353725ec3b7cd7c8a9a8f768c67f28834864f` | 6392 |
| `briefs/BRIEF_Z9_TEST_TEAM.md` | `2fd4442b82fc2db15bac5ec48432ab08911be274c39354937b3f8df8f8a927fd` | 4477 |

## 10. Pins

Snapshot sha256: `5684819296` → `5be745ee8ccdf3a96636550ad0782409f83d04fb9c4586b446ff1072bee8bdf9`
(26,485 bytes); `5684607872` → `f3b967c1afdf1f21ebe774eafebc50ed36d41686248e907e6a6b5a9495d09b3f`
(39,218 bytes); `5693520829` → `ccfcd0a53de04b8f251dfb31a543fef03ebd4bd5f4836cad7f6ab736f7847f08`
(40,503 bytes).

Artifact blob shas at `source_main` (every file any brief hands to a proxy):

| blob sha | path |
|---|---|
| `3558f062008e567ac964f0b8f640e339c5df31e3` | `research/gmi-833-z-z15-decisive-falsifiers-v1/FREEZE_V1.md` |
| `087d74348c9ffb8223bbdd116e1597e74f3fbfc7` | `research/gmi-833-z-z15-decisive-falsifiers-v1/CORE.md` |
| `0a0d306aa97ff14ebfd6c482f0d8c8bd037808de` | `research/gmi-833-z-z15-decisive-falsifiers-v1/FAILED_PREDICTION_REGISTER_V1.json` |
| `195420f90c361338e36ccbd0f6c2d60dae341a44` | `research/gmi-833-z-z15-decisive-falsifiers-v1/PARENT_DISCLOSURE_V1.md` |
| `a13388b4d7f13f5468e18373ee843cc302f0b524` | `research/gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md` |
| `5bf0de0b3fa1efebc399781a9bf82030b57dffa5` | `research/gmi-833-heldout-20-transitions-v1/FREEZE_V1.md` |
| `4db07a0174408c1dc7d7220a27e38713eb8a8cdb` | `research/gmi-833-heldout-20-transitions-v1/full_enumeration_v1.py` |
| `1675edf8076b0b634cbe66507c51d32401386845` | `research/gmi-833-capability-interaction-partition-v1/CAPABILITY_INTERACTION_PARTITION_THEOREMS_V1.md` |
| `1fabcafda2f30f2245f1f7cc38315fcbb33c770c` | `research/gmi-833-capability-interaction-partition-v1/CORE.md` |
| `abfa3f232939c57500c827158cd6bf14545a6b5d` | `research/gmi-833-ag1-descent-stack-v1/AG1_THEOREMS_V1.md` |
| `06ee67d37d4a50a552b794af07495eb4e6fe226a` | `research/gmi-833-ag1-descent-stack-v1/FOUNDATION_DEPENDENCY_DAG_V1.json` |
| `1ecb9ffb3b6e71b29d10aaf36fffcb5ff461c2bf` | `research/gmi-833-ag1-descent-stack-v1/PARENT_LEDGER.md` |
| `3ba02b86c3882ea6b2925f946c86653726291fbb` | `research/gmi-833-ag1-descent-stack-v1/AG8_DESCENT_OBLIGATIONS_V1.json` |
| `1dc3cc210b300c821446718855841ac6a4da8aa2` | `research/gmi-833-aj13-stopping-rule-v1/THEORY.md` |
| `4cca69e81f2a95405d6a15a40353c284326934c7` | `research/gmi-833-aj13-stopping-rule-v1/RESULT_V1.json` |
| `52e906d4035ef76e70df7ab8d337d024bff5f16a` | `research/gmi-833-aj13-stopping-rule-v1/OPEN_GAPS.json` |
| `7e2204ad6aecf12450dce98f90f3255a7022854e` | `research/gmi-833-aj13-stopping-rule-v1/check_aj13.py` |
| `30d76ef656081424c1613822a3ca1484b3a43d94` | `research/gmi-833-aj12-foundation-substrate-relativity-v1/THEORY.md` |
| `6b6b50f9b2b0691e908c8b4644a9766c564432e6` | `research/gmi-833-aj12-foundation-substrate-relativity-v1/OPEN_GAPS.json` |
| `201ee8e8b290f5bfa3e283e6f8be2429ce8eeb78` | `research/gmi-833-theory-baseline-v1/BASELINE_V1.md` |
| `ca5d4d1d8c941078a672a00120da6cd197914f3e` | `research/gmi-833-capability-predictor-evaluation-v1/CORE.md` |
| `a463616de7fcd4b2a2b33e5671e14dd5f55b75fd` | `research/gmi-833-capability-predictor-evaluation-v1/SCOPE_V1.md` |
| `f7f278036d4cc2e18fa3de86989123dbf05ceb9c` | `research/gmi-833-capability-predictor-evaluation-v1/BLINDNESS_V1.md` |
| `2a09bcdad36fdfdf66b5deaf887574002ecb69b8` | `research/gmi-833-capability-predictor-evaluation-v1/PARENT_DISCLOSURE_V1.md` |
| `6c1602ae66b0e5fca26f7bde03982f513805fd09` | `research/gmi-833-capability-predictor-evaluation-v1/REAL_RUNS_V3/REAL_MEASURED_V3.json` |
| `a7ee5b9deeb15a186036a03d35740ff4c9cb104e` | `research/gmi-833-real-transition-receipts-v1/CORE.md` |
| `43497544080d3dc63492a22cd035ba795fbec7c9` | `research/gmi-833-real-transition-receipts-v1/FREEZE_V1.md` |
| `d263526d5717c545484f5a0b6d0686bb372622cf` | `research/gmi-833-real-transition-receipts-v1/FREEZE_V2_AMENDMENT.md` |
| `8f7fec89776f02c369262175e99f9371b06e3bee` | `research/gmi-833-real-transition-receipts-v1/RECEIPTS_V1.json` |
| `79460ceaafa7c50ca6fe724815448e9ec1b14dc9` | `research/gmi-physical-resource-metering-v1/CORE.md` |
| `29bc981a36a860c3ad70ccabfbeb5063fc5f6c95` | `research/gmi-physical-resource-metering-v1/SUMMARY.json` |
| `b1e1346c04f0d047e8369d1542c739a49f5d80db` | `research/gmi-physical-resource-metering-v1/PHYSICAL_METERING_CONTRACT_V1.json` |
| `9f4d25a5f59cdf83f86bc484cda7efb46a8bc054` | `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md` |
| `46ebc61153184bb9077f69c18a56d785925781f7` | `research/gmi-833-ac-lanes-harness-v1/AC_CROSSWALK_ADDENDUM_V1.md` |
| `e4f1116182d16e6e74f971510b0ef883aaf16d15` | `research/gmi-833-tranche-ab-ac-lit/WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md` |
| `2621b889fd6b2e643723b02720a69527b880347b` | `research/gmi-final-target-natural-half-v1/FINAL_TARGET_NATURAL_HALF_THEOREM_V1.md` |
| `beb305f0b74c99a4d1cb71be8d589b093e5df919` | `research/gmi-final-target-natural-half-v1/PREDICTIONS_REGISTRY_V1.json` |
| `f4c3387c7ee5d6b635876c4296deb9ee9b19eb4a` | `research/gmi-biological-bridge-v1/BIOLOGICAL_BRIDGE_CONTRACT_V1.md` |
| `e9f01976f46845d8089fa37323fe87a0dbaec5dd` | `research/gmi-biology-predictions-v1/BIOLOGY_PREDICTIONS_THEOREM_V1.md` |
| `dfff819b423a1f2e103bee584598f13474526f35` | `research/gmi-natural-intelligence-bridge-v1/NATURAL_INTELLIGENCE_BRIDGE_THEOREM_V1.md` |
| `61006b756721c748f8dcc797c755abd25cc42956` | `research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json` |
| `9050c2e01e44347aa2b19710286890be1a5eb21d` | `research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json` |
| `03da1a3566a6e62f8506981c7dde51ebc212cc81` | `research/gmi-833-aa-gap-object-v1/AA_GAP_OBJECT_THEOREMS_V1.md` |
