# Section H per-family requirement ledger — named results V1

All statements below are about the corpus at `source_main`
`364f29f1b39557a863ce891529927cec8dadfd6f`. They are statements about **what the corpus
contains**, not about machine intelligence. None of them closes a family row, and none of
them earns a family gate.

## Objects

`Rows` is the sequence of 43 unchecked named-family rows of Issue #833 Section H, verbatim
and in body order (`SECTION_H_MIRROR_V1.md`). `J = {R01..R11}` is the eleven-coordinate
requirement list of the Section H preamble (Section 4 of `FREEZE_V1.md`). A **scope**
`sigma = (family row, grammar, ecology, budget, freeze, protected interface)` in the sense of
PR #997 `FGS-2`. A **cell** is `(row, requirement, sigma, status)` with `status` drawn from
the six-value enum of `FREEZE_V1.md` Section 6.

Three scopes carry evidence in the corpus: `SIGMA_4F`
(`research/gmi-833-h-neutral-four-family-v1`), `SIGMA_CENSUS`
(`research/gmi-833-h-obstruction-census-v1`), and `SIGMA_K`
(`research/gmi-833-aj9a..aj9h`).

---

## HRL-1 — the requirement matrix is total and scope-indexed

**Statement.** Every one of the `43 x 11 = 473` (row, requirement) pairs receives at least
one cell, every cell carries exactly one scope id, every `MET_AT_NARROWER_SCOPE` cell carries
a `path:line` citation and an exact `scope_gap`, and every `MISSING_BUILDABLE` cell names the
build. The matrix contains **649** cells: 473 at `SIGMA_CENSUS` (all 43 rows x 11
requirements), 44 at `SIGMA_4F` (4 rows x 11), and 132 at `SIGMA_K` (33 rows x the 4
requirements a blind recovery would bear on).

**Observed status totals.** `MET 0`, `MET_AT_NARROWER_SCOPE 348`, `MISSING_BUILDABLE 169`,
`MISSING_STRUCTURAL 0`, `NOT_APPLICABLE 0`, `SCREENED_NOT_ADJUDICATED 132`.

**Scope.** This is a statement about the corpus's contents at one commit. It does not claim
the adjudication is the only defensible one; it claims the adjudication rule was frozen
before the executor existed (`ADJUDICATION_RULES_V1.json`, freeze commit
`d2a3a4bd17dac4726b8251cb6e7838b9fcbfbdff`) and was applied mechanically.

**Assumptions.** The row-binding rule of `FREEZE_V1.md` Section 6; the two source packages
being the only row-indexed Section H evidence in the corpus (screened by a per-requirement
vocabulary sweep over 5,527 package text files).

**Falsifiers.** A row-indexed Section H certificate in some third package; a `MET` cell that
is genuinely earned for a named historical family; a binding that the rule accepts but a
reader rejects.

**Strongest parents.** `research/gmi-833-h-neutral-four-family-v1/FAMILY_GATE_LEDGER_V1.json`
already does exactly this for 4 rows at 10 gates. The residual contribution here is the
extension to all 43 rows, the split of the collapsed grammar/macro gate into two separately
cited coordinates, and scope as a first-class per-cell field.

**Forbidden extrapolations.** `NAMED_FAMILY_ROW_CLOSED`, `CROSS_SCOPE_GATE_COMPOSITION`.

---

## HRL-2 — the two enumerations resolve at different granularities

**Statement (a), evidence-backed.** The map from the 43 named rows to the census's hallmark
contracts is a **total function onto only 10 distinct contracts**, read verbatim from
`research/gmi-833-h-obstruction-census-v1/FROZEN_FAMILY_REGISTRY_V1.json`. Six rows share
`UNEXCITED_CONTEXT` (H01, H05, H06, H11, H25, H29); six share
`EXTERNAL_PEER_TOOL_CHANNEL`; six share `UPDATE_FEEDBACK_CHANNEL`; five share
`TRIPLE_CONJUNCTION`; five share `HISTORY_STATE_CHANNEL`; four share `TRIPLE_PARITY`; four
share `STOCHASTIC_SOURCE_CHANNEL`; three share `PAIR_PARITY`; three share
`PAIR_CONJUNCTION`; one has `INVERT_SIGNAL`. The 43 target digests collapse to the same 10
values.

**Consequence.** Every census-sourced cell is **contract-specific, not row-specific**. Three
rows as different as `Finite-state/automata intelligence.`, `Attention mechanisms.` and
`Mixture-of-experts/routing systems.` receive one and the same evidence object. The
registry's own boundary applies verbatim: "a hallmark is neither a complete definition nor
proof of full recovery/non-recovery of its historical family", and its mapping status is
`AUTHORED_POSTHOC_EVALUATION_PRIOR`.

**Statement (b), an absence.** **No primary artifact in the corpus binds any K-family
(`K01..K11`) to any named Section H row.** Verified two independent ways, with a control:
(1) no file of the nine `aj9*` / `blind-recovery-v2` packages contains any of the 43 verbatim
row texts; (2) no file of those packages contains the string `Section H`; the control check
confirms the scan reads those files' bytes at all (a scan that cannot hit is not an absence
proof). The single corpus file attaching K evidence to Section H is
`research/gmi-833-checklist-mirror-v1/EVIDENCE_LEDGER_V1.json:1302`, and it attaches it to
the **aggregate** row "Verify that the same neutral grammar can recover several families
without per-family redesign." — not to any named row.

**Statement (c), agent-constructed.** `FAMILY_TO_EVIDENCE_MAP` in `LEDGER_V1.json` supplies
**35 candidate K-to-row edges** over 33 rows, each labelled
`AGENT_CONSTRUCTED_UNADJUDICATED` and each carrying the declared `parent_anchor` or
`posthoc_fingerprint` clause it rests on. `STRONG` edges are those where a K-family's own
declared `parent_anchors` names the row's canonical literature (e.g. `K03 -> H22` on LeCun
1998; `K04 -> H25` and `K04 -> H26` on Vaswani 2017). **Ten rows have no K-family candidate
at all**: `H02` linear regression, `H03` GLMs, `H04` basis/kernel, `H15` model-free RL,
`H31` latent-variable generative, `H32` flow-like transport, `H33` diffusion, `H34`
energy-based, `H37` distributed/collective, `H43` multi-agent emergent communication.
**Two rows have several candidates**: `H11` library-learning (`K08` retrieval and `K10`
program synthesis) and `H19` particle/population inference (`K06` Bayesian and `K09`
evolutionary). `K04` "attention/dynamic-routing" is one-to-many onto `H25`, `H26`, `H29`
and `H38`; it is **not** the same object as the row `Attention mechanisms.`, whose registered
census hallmark is `UNEXCITED_CONTEXT` — a context-excitation probe, not a routing
fingerprint. The K-family and the named row share a word and not an evaluated object.

**Consequence.** Every `SIGMA_K` cell is `SCREENED_NOT_ADJUDICATED` and may never be
promoted. The 11/11 blind recovery of #931–#937/#951 is real at its own declared scopes; it
is simply **not addressed to these rows**, and nothing in the corpus makes it so.

**Falsifiers.** A primary artifact asserting a K-to-named-row binding; a reader rejecting a
`STRONG` edge's anchor reading.

**Forbidden extrapolations.** `K_FAMILY_IS_A_NAMED_ROW`, `NAMED_FAMILY_RECOVERED`.

---

## HRL-3 — the residual, and the correction to the expected residual

**Statement.** Counting met requirements **at the single best scope that covers all eleven
coordinates** (no gluing), the distribution over the 43 rows is:

| met of 11 | rows |
|---|---|
| 10 | **4** (`H01` finite-state/automata, `H02` linear regression/classifiers, `H03` GLMs, `H04` basis/kernel — the four with `SIGMA_4F` evidence) |
| 8 | **5** (`H17` Bayesian, `H20` feed-forward NN, `H22` CNN, `H32` flow-like transport, `H34` energy-based — the `RECOVERED_CONTROL` rows outside the four) |
| 7 | **34** (every remaining row) |
| 0–6, 9, 11 | **0** |

**Residual dominance** (rows at which the requirement is not met, out of 43):

| requirement | missing rows |
|---|---|
| `R11` real-scale test | **43** |
| `R05` negative twin | **39** |
| `R07` resource crossover | **39** |
| `R04` neutral recovery | **34** |
| `R01 R02 R03 R06 R08 R09 R10` | **0** |

**The correction.** The expectation that the residual concentrates in `real-scale test`
**and** `independent search`/replication is **half right and half wrong**, and the wrong half
matters. `R11` is indeed universal: it is missing at 43/43 rows and is the only requirement
that is. But `R10` **independent search** is missing at **0/43** rows — it is met at narrower
scope everywhere, via the source-separated oracles
(`gmi-833-h-obstruction-census-v1/ORACLE_RESULT_V1.json`, "no primary import", covering all
11 target contracts; `gmi-833-h-neutral-four-family-v1/independent_oracle_v1.py` with
`independent_search_audit.all_agree = true`). The zero-instance tier the maturity rescore
found is **`M5` independent *replication*** — "no disjoint-team replication"
(`research/gmi-833-maturity-rescore-v2-v1/MATURITY_RESCORE_V2.md:14`), scored under a rule
that refuses `M5` for intra-package work ("never `M5`: intra-package != independent
replication"). Independent *search* and independent *replication* are different coordinates,
and conflating them mislocates two-fifths of the Section H residual. The real second and
third tiers are `negative twin` and `resource crossover`, each missing at 39/43 — both
supplied at `SIGMA_4F` for the four rows that have it and at no scope for the other 39.

**A note on gluing.** The pooled, scope-blind distribution is **identical** to the per-scope
one (`{10: 4, 8: 5, 7: 34}`), because on all four rows where both scopes carry evidence the
`SIGMA_4F` met-set strictly contains the `SIGMA_CENSUS` met-set. `FGS-2` gluing would
therefore not even change the numbers here — but the ledger still refuses it, and the pooled
figure is emitted only under the label `NON_GLUABLE_UNDER_FGS2`.

**Assumptions.** The frozen adjudication rules; `MET_AT_NARROWER_SCOPE` counted as met for
the purpose of the count, with the gap recorded per cell.

**Falsifiers.** Any row whose best-scope met count differs from the table; any requirement
whose missing count differs.

---

## HRL-4 — the decidability verdict, and why no row is blocked

**Statement.**

| verdict | rows |
|---|---|
| `CLOSABLE_NOW` | **0** |
| `CLOSABLE_AFTER_BUILDABLE_WORK` | **43** |
| `BLOCKED_STRUCTURAL` | **0** |

**Why zero `CLOSABLE_NOW`, citable two ways.** (1)
`research/gmi-833-h-neutral-four-family-v1/RESULT_V1.json:56` —
`family_gate_ledger.open_gate = "real_scale_test"`, with every one of its four rows carrying
`complete: false` and `issue_833_checkbox: "MUST_REMAIN_OPEN"`. (2)
`research/gmi-833-h-obstruction-census-v1/RESULT_V1.json:485` —
`family_gate_audit.eligible_named_family_rows = 0`, reason "this package supplies neither a
complete ten-gate ledger nor real-scale evidence". The two independent evidence bases agree:
nothing is closable today.

**Why zero `BLOCKED_STRUCTURAL`.** No cell anywhere in the matrix is `MISSING_STRUCTURAL`.
The three candidate blockers are each a constraint on *method*, not on *possibility*:

- `FGS-3` proves finite evidence does not **entail** real-scale behaviour. Its own text:
  "a scaling law, structural invariant, continuity assumption, or direct real-scale test can
  add the missing premise; the theorem does not say that transfer is impossible." The
  structural thing is the inference, not the test. `R11` is therefore `MISSING_BUILDABLE` at
  every row, and the checker rejects a ledger that files it structural
  (`HOSTILE_FGS3_OVERREAD`).
- `FGS-4` proves two distinct hidden organizations share identical protected response
  profiles on every finite binary word, so family identity does not follow from operational
  equivalence. Its own text: "It does not block a scoped post-hoc family mapping when
  additional structural observables and the evaluation prior are disclosed." #931–#937/#951
  and #999/#998 `MAP-1` already perform exactly such a mapping. `FGS-4` is recorded as a
  `structural_constraint` on how `R04` may be certified; it makes no cell structural.
- The census's own obstructions (`H-EXP`, `H-RES`, `H-ID`) are proved **at `SIGMA_CENSUS`**
  and, by `FGS-2`, do not transport. Each names its own removal: raise `B` from 3 to 5 for
  `H-RES` (the theorem states the target is expressible in the same grammar at cost five);
  excite the registered context probe for `H-ID`; register the missing channel as a grammar
  leaf for `H-EXP`, for which channel-extension packages already exist
  (`gmi-833-g0-interaction-channels-v1`, `gmi-833-g0-stochastic-update-v1`,
  `gmi-833-g0-governed-self-change-v1`).

**Consequence (the actionable one).** Section H is **not** uniformly impossible, and
reporting it so would be a defect of the same order as closing a row. Every open named row
is decidable-after-buildable-work, and the work is enumerated per cell. The shortest path is
the four `SIGMA_4F` rows, each one requirement from complete at a single declared scope.

**Forbidden extrapolations.** `SECTION_H_UNIFORMLY_IMPOSSIBLE`, `NAMED_FAMILY_ROW_CLOSED`,
`REAL_SCALE_VALIDATION`, `FINITE_EVIDENCE_IMPLIES_REAL_SCALE`.

---

## HRL-5 — soundness observations on the evidence the corpus already has

Recorded because they bear on whether the met cells are as strong as their count suggests.

1. **`R01` and `R08` share one evidence key at both scopes.** At `SIGMA_4F` the ten-gate
   ledger cites the same `FROZEN` key for `property_prediction_from_ecology` and for
   `heldout_frozen_prediction`. At `SIGMA_CENSUS` the same frozen `predicted_disposition`
   serves both. Neither scope witnesses the two coordinates independently, and at
   `SIGMA_CENSUS` the frozen prediction covers exactly the evaluated set — nothing is held
   out from it. By `FGS-1` the coordinates are logically independent; here their
   *measurements* are not.
2. **Custody holds at both source packages**, re-verified here by git add-order:
   `gmi-833-h-obstruction-census-v1` `FREEZE_V1.md` at `d2cbd897` (2026-09-17 09:45:40 +0200)
   precedes `RESULT_V1.json` at `f0734279` (09:58:25); `gmi-833-h-neutral-four-family-v1`
   `FREEZE_V1.md` at `6841981e` precedes `RESULT_V1.json` at `944f85e2`. Neither is a #976
   `POST_HOC_SUSPECT`.
3. **The two-route check earned its keep on coverage, not on values.** Round 1 found 43 cells
   that Route A produced and Route B did not, with **zero** status disagreements on the 606
   cells both produced. Single-stage attribution: Route B's *enumeration* stage, which built
   its per-requirement loop from a package-level presence profile, and `R04` is the one census
   requirement that is per-row dispositional rather than package-level. Recorded verbatim in
   `ROUTE_RECONCILIATION_ROUND1_V1.json` before resolution.
4. **One row carries two opposite verdicts, both true at their own scope.** `H01`
   `Finite-state/automata intelligence.` is `neutral_recovery:
   SUPPORTED_AT_REGISTERED_EXACT_SCOPE` in
   `gmi-833-h-neutral-four-family-v1/FAMILY_GATE_LEDGER_V1.json` and
   `IDENTIFIABILITY_OBSTRUCTION` in `gmi-833-h-obstruction-census-v1/RESULT_V1.json`. There is
   no contradiction and no error: at `SIGMA_4F` the persistent three-class future-response
   quotient is recovered from obligations that excite the state channel, and at
   `SIGMA_CENSUS` the registered context probe `x3` is zero on every point of the eight-point
   ecology, so the target is not identified. This is exactly what `FGS-2` describes, and it is
   why the ledger refuses a scope-blind cell. A matrix without a scope column would have had
   to pick one of the two and would have been wrong either way.

5. **Bit-identical on two hosts and two Python versions** (Darwin/CPython 3.13 and
   laptop-billy Linux/CPython 3.8.10; `RESULT_V1.json` md5
   `f2e5a0015a18912c9ca3e42e134a2530`, `LEDGER_V1.json` md5
   `36a48725f2ff02212b5297ee4b712d11`). Per the corpus's own frozen rule this licenses
   **neither `EV4` nor `M5`**: intra-package is not independent replication.

## Strongest parents and the residual contribution

- `research/gmi-833-h-neutral-four-family-v1` owns the ten-gate ledger form and 4 rows of it.
- `research/gmi-833-h-obstruction-census-v1` owns the 43-row registry, the contract map and
  the four obstruction theorems.
- PR #997 `research/gmi-833-h-family-gate-soundness-v1` owns `FGS-1..FGS-6`; this package
  cites them at blob-pinned commit `4abe5c4f` and writes nothing into that package.
- `research/gmi-833-aj9a..aj9h` own the 11/11 blind recovery at `SIGMA_K`.
- `research/gmi-833-maturity-rescore-v2-v1` owns the `M0..M6` ladder and the corpus fact that
  no `EV4`/`EV5` evidence exists.

Not claimed novel: the gate list, the obstruction theorems, the soundness theorems, the
blind recoveries, the maturity ladder. The residual contribution is (i) the per-row,
per-requirement, scope-indexed status matrix over all 43 open rows, (ii) the evidence-backed
43-to-10 contract collapse and the verified absence of any K-to-row binding, and (iii) the
`R10`-versus-`M5` correction to the expected residual.
