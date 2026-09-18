# Section AE structural map and tranche plan v1

Source: issue #833 comment `5692689542`, fetched live at `source_main`
`91c6d2876ba80c517a186e28fce3bdbe4e3fc218`. **122** unchecked rows across
**17** subsections, **0** previously checked. Every row string is unique in the
comment, so each is safely addressable as a verbatim `old`.

Note for the orchestrator: the subsection headings in the live comment use
**three** hashes (`### AE1 — ...`), not two. All reconciliation `anchor` fields
in this tranche use the live three-hash form.

## Row census

| subsection | rows | dominant demand |
|---|---:|---|
| AE1 — define `exploitable structure` | 8 | construct + prove separations |
| AE2 — information-theoretic learnability boundary | 8 | prove + construct fixtures |
| AE3 — compression is not automatically learning | 8 | construct + parent subtraction |
| AE4 — Information Bottleneck / relevant information | 8 | formalize + smallest counterexamples |
| AE5 — predictive-state / causal-state audit | 6 | parent-ownership audit + disagreement construction |
| AE6 — manifold hypothesis and geometric structure | 8 | construct + derive + **one prospective empirical row** |
| AE7 — from prediction to control | 7 | prove + derive + **one prospective prediction row** |
| AE8 — CPC master-principle test | 8 | classify + discriminating-world construction |
| AE9 — learning as representation restructuring | 7 | **training-time measurement** — instrument-blocked |
| AE10 — resource-bounded usable information | 6 | define + exact separation + **one morphology row** |
| AE11 — thermodynamics and physical information | 8 | separate + audit + **hardware energy measurement** |
| AE12 — free-energy / active-inference audit | 6 | parent audit + discriminating tasks |
| AE13 — causality and intervention | 7 | prove + construct + **one morphology row** |
| AE14 — generalization, analogy, reasoning | 6 | define + matched-task construction + **one morphology row** |
| AE15 — world-model necessity boundary | 6 | define + construct + derive phase boundary |
| AE16 — real-world empirical programme | 8 | **real datasets across four domains** — instrument-blocked |
| AE17 — recursive loophole extraction | 7 | meta/ledger obligations riding on the others |
| **total** | **122** | |

## Row taxonomy

Every one of the 122 rows is assigned to exactly one tier. The per-row
assignment is committed as `AE_ROW_TIER_ASSIGNMENT_V1.json` in this directory,
so the table below is auditable rather than a hand-wave. The tier totals sum to
122 by construction.

| subsection | rows | T1 finite construction | T2 morphology receipts | T3 instrument-blocked | T4 ledger |
|---|---:|---:|---:|---:|---:|
| AE1 | 8 | 8 | 0 | 0 | 0 |
| AE2 | 8 | 8 | 0 | 0 | 0 |
| AE3 | 8 | 8 | 0 | 0 | 0 |
| AE4 | 8 | 8 | 0 | 0 | 0 |
| AE5 | 6 | 5 | 1 | 0 | 0 |
| AE6 | 8 | 6 | 1 | 1 | 0 |
| AE7 | 7 | 7 | 0 | 0 | 0 |
| AE8 | 8 | 8 | 0 | 0 | 0 |
| AE9 | 7 | 3 | 0 | 4 | 0 |
| AE10 | 6 | 5 | 1 | 0 | 0 |
| AE11 | 8 | 5 | 0 | 3 | 0 |
| AE12 | 6 | 6 | 0 | 0 | 0 |
| AE13 | 7 | 6 | 1 | 0 | 0 |
| AE14 | 6 | 6 | 0 | 0 | 0 |
| AE15 | 6 | 6 | 0 | 0 | 0 |
| AE16 | 8 | 0 | 0 | 8 | 0 |
| AE17 | 7 | 0 | 0 | 0 | 7 |
| **total** | **122** | **95** | **4** | **16** | **7** |

**Tier 1 — closable with finite exact-rational constructions (95 rows).** The
spine of the section: `prove`, `construct the smallest counterexample`,
`separate X from Y`, `derive the conditions under which ...`. Each is a finite
object plus an exact verification, the shape the first three tranches used.
**21 are already closed**, leaving **74**.

**Tier 2 — blocked on pinned morphology receipts, not on science (4 rows).**
AE5's *which quantity predicts morphology/resource cost under GMI*, AE6's
*derive when manifold assumptions fail and another morphology should be
selected*, AE10's *raw versus usable information versus a resource-conditioned
vector*, and AE13's *does causal structure change selected morphology*. These
need no new mathematics, only registered morphology-selection receipts pinned
by blob sha — and the repo already carries them on `main`:
`research/gmi-833-finite-morphology-metrics-v1`,
`research/gmi-833-morphology-selection-v1`,
`research/gmi-833-finite-candidate-space-v1`,
`research/gmi-833-global-vs-reachable-morphology-v1`. **One** package pinning
those blobs and running a single structure-measure-versus-selection comparison
closes all four at once. It is small, and it is the only place in the section
where four rows fall to one piece of work.

**Tier 3 — genuinely instrument-blocked (16 rows).** All 8 of AE16 (real
datasets spanning vision, language, sequential control and a scientific
domain — every row of that subsection presupposes the corpus); 4 of AE9
(training-time representational measurement, prospective marker freezing
against observed capability onset, and the non-neural comparison); 3 of AE11
(hardware energy measurement, the information-savings-to-energy-savings test,
and the biological separation); and AE6's prospective test on real datasets.
These should stay **OPEN with a stated instrument requirement**. Marking them
without the instrument would be exactly the shallow mark this tranche is meant
to avoid, and they are where the AE closure rule's `real-system test` arrow
lives.

Note that AE9 is **not** wholesale blocked: its definitional row (measurable
representation-change quantities that do not depend on architecture names), its
smooth-versus-qualitative-transition row and its `emergence` re-audit are
Tier 1 and can be earned on finite non-neural systems.

**Tier 4 — AE17's 7 ledger rows.** Obligations *on* the other tranches: emit
assumptions and counterexamples into the gap graph, attack every scalar with
two non-isomorphic counterexample families, pair every positive with a nearest
negative, carry finite tags, pass the #833 D controls, update the subsumption
ledger, reopen on descendant gaps. They close as a **sweep** over the emitted
receipts, and only once there is enough to audit.

## Cheap obligations versus genuine science

Within Tier 1 the split matters for sequencing:

- *Cheap obligations* (register/freeze/name a artifact whose property is then
  machine-checked): AE2 rows 5-8 (the four control sources), AE6 rows 2-3,
  AE8 row 7, AE12 row 3, AE17 rows 4 and 6. These are cheap **only** if the
  asserted property is verified exactly rather than asserted in prose — the
  first tranche's fixture roster is the pattern.
- *Genuine science* (a theorem or a boundary must be earned): AE1 row 7
  (impossibility of a budget-independent scalar), AE2 rows 1-2 (the boundary and
  its quantitative generalization), AE3 rows 2-3 and 6-8 (the
  compression-versus-learning separations and the Kolmogorov boundary), AE4 rows
  2-3 (equivalence-or-refinement against IB optima), AE5 rows 3-5 (whether GMI
  state-complexity results are already parent-owned), AE7 rows 1-2 and 4-6,
  AE8 rows 2-4 (is CPC a theorem, a variational principle, or a slogan),
  AE13 rows 1-4, AE14 rows 2-3 and 6, AE15 rows 2-4.

The single hardest row in the section is AE8 row 8 — *do not call CPC the GMI
master law unless it beats the bag-of-laws baseline and survives parent
discrimination*. It is a comparison against every other master principle and
should be attempted only after AE3, AE4, AE7, AE10 and AE12 have each fixed
their own parent boundary; otherwise the comparison has nothing stable to stand
on.

## Delivered in this tranche

| package | rows closed | subsection |
|---|---:|---|
| `gmi-833-ae-ae1-structure-separation-v1` | 8 | AE1 (all) |
| `gmi-833-ae-ae2-predictive-boundary-v1` | 8 | AE2 (all) |
| `gmi-833-ae-ae10-usable-information-v1` | 5 | AE10 (row 5 deferred) |

**21 of 122.** All three packages carry a freeze committed before any implementation
blob existed, parent-ownership disclosure with DOIs, named theorem notes, two
materially independent routes, hostiles proved potent before proved detected, a
null the true result beats with the no-alarm case asserted, and a dedicated
workflow.

AE10's freeze names its five target rows and the one row it explicitly does
**not** close, so the deferral was declared before the result existed rather
than after.

## Batching plan for the remaining 101

Ordered by dependency. Each entry is one package; the row counts are Tier-1
counts from the table above unless noted, and they sum exactly.

| # | package | rows | notes |
|---:|---|---:|---|
| 1 | `gmi-833-ae-ae3-compression-learning-v1` | 8 | three compression notions separated exactly; a corpus that compresses whose code is useless for the task; a useful predictor that is not the shortest description; the Kolmogorov uncomputability boundary stated as a forbidden promotion, not a claim; computable surrogates with their language dependence measured across at least two universal-machine remints |
| 2 | `gmi-833-ae-ae4-information-bottleneck-v1` | 8 | needs AE3's coding-language registry. When a GMI minimal predictive state equals, refines, or is incomparable with an IB optimum, with the smallest counterexample blocking unqualified identification |
| 3 | `gmi-833-ae-ae5-causal-state-audit-v1` | 5 | a parent-ownership audit against computational mechanics. Expect `PARENT_SUFFICIENT` terminals — those are successes |
| 4 | `gmi-833-ae-ae7-prediction-to-control-v1` | 7 | extends AE1's control witnesses to POMDP-style sufficient states with value-of-information conditions under resource cost |
| 5 | `gmi-833-ae-ae13-causality-intervention-v1` | 6 | extends AE1's confounded triple to a full observational-equivalence class with differing intervention consequences |
| 6 | `gmi-833-ae-ae15-world-model-necessity-v1` | 6 | tasks solvable with no explicit model; tasks where a model is provably necessary; the model-based/model-free phase boundary |
| 7 | `gmi-833-ae-ae14-generalization-taxonomy-v1` | 6 | operational definitions plus matched tasks with equal predictive accuracy and different compositional capability; the `forbid` row closes by the registered forbidden-promotion list |
| 8 | `gmi-833-ae-ae6-geometric-structure-v1` | 6 | the manifold hierarchy, learnable non-manifold distributions, useless low-dimensional manifolds, and the locality/symmetry/compositionality derivations |
| 9 | `gmi-833-ae-ae12-fep-audit-v1` | 6 | free-energy/active-inference parent audit with published technical criticisms, and finite discriminating tasks against rate-distortion control |
| 10 | `gmi-833-ae-ae11-thermo-separation-v1` | 5 | keeps Shannon, algorithmic, statistical-mechanical and thermodynamic entropy distinct and audits Landauer-style bounds; claims nothing energetic without measurement |
| 11 | `gmi-833-ae-ae9-transition-markers-v1` | 3 | the non-neural half of AE9: architecture-independent representation-change quantities, smooth-versus-qualitative transitions, and the `emergence` re-audit |
| 12 | `gmi-833-ae-morphology-sweep-v1` | 4 (T2) | pins the existing morphology receipts by blob sha and runs one comparison of raw information, usable information and a resource-conditioned vector against selected morphology. Closes AE5, AE6, AE10 and AE13's morphology rows together |
| 13 | `gmi-833-ae-ae8-cpc-discrimination-v1` | 8 | last of the science packages: needs 1, 2, 4, 9 and this tranche's AE10 settled first |
| 14 | `gmi-833-ae-ae17-recursive-ledger-v1` | 7 (T4) | a sweep over everything emitted by 1-13 |
| | **total** | **85** | |

`21 + 85 = 106`. The remaining **16** are Tier 3 and stay OPEN with a stated
instrument requirement: AE16 entire (8), AE9's four measurement rows, AE11's
three physical rows, AE6's real-dataset test. **106 of 122 is the honest
ceiling for AE** without real training runs, hardware energy measurement and a
four-domain dataset programme.

The hardest single row in the section is AE8's last — *do not call CPC the GMI
master law unless it beats the bag-of-laws baseline and survives parent
discrimination*. It is a comparison against every other master principle, and
should be attempted only after AE3, AE4, AE7, AE10 and AE12 have each fixed
their own parent boundary; otherwise the comparison has nothing stable to stand
on.

## Machine-readable output

`ISSUE_833_COMMENT_RECONCILIATION_V1.json` in this directory carries all 21
earned replacements for comment `5692689542`, each with the live anchor, the
byte-exact `old` row and the `- [x]` `new` row, plus the declared `not_closed`
entries. Every `old` string was verified to occur exactly once in the live
comment body fetched at `source_main`.
