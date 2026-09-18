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

Sorting by what a row actually costs, rather than by subsection:

**Tier 1 — closable with finite exact-rational constructions (no new instrument).**
The spine of AE1, AE2, AE3, AE4, AE5, AE7, AE10, AE13, AE14, AE15, and the
derivation rows of AE6 and AE8. These read `prove`, `construct the smallest
counterexample`, `separate X from Y`, `derive the conditions under which ...`.
Each is a finite object plus an exact verification, exactly the shape the first
two tranches used. Approximately **72** rows.

**Tier 2 — blocked on a pinned morphology dataset, not on science.**
Every row of the form *does GMI morphology selection predict X*. These are
scattered — AE6 last row, AE7 last row, AE8 two rows, AE9 last row, AE10 row 5,
AE13 last row, AE14 row 5, AE15 row 5. They do not need new mathematics; they
need registered morphology-selection receipts pinned by blob sha. The repo
already carries them: `research/gmi-833-finite-morphology-metrics-v1`,
`research/gmi-833-morphology-selection-v1`,
`research/gmi-833-finite-candidate-space-v1`,
`research/gmi-833-global-vs-reachable-morphology-v1`. **One** later package that
pins those blobs and runs the structure-measure-versus-selection comparison
closes this family together. Approximately **11** rows, and the highest-leverage
single observation in this map.

**Tier 3 — genuinely instrument-blocked.** AE9's training-time representational
measurements (effective rank, circuit/path usage, grokking-style delayed
generalization) require real training runs; AE11's energy rows require hardware
measurement; AE16 requires real datasets spanning vision, language, sequential
control and a scientific domain. These stay **OPEN with a stated instrument
requirement**. Marking them without the instrument would be a shallow mark, and
AE9/AE11/AE16 are precisely where the AE closure rule's `real-system test` arrow
lives. Approximately **21** rows.

**Tier 4 — meta/ledger rows (AE17).** These are obligations *on* the other
tranches: emit assumptions and counterexamples into the gap graph, attack every
scalar with two non-isomorphic counterexample families, pair every positive with
a nearest negative, carry finite tags, pass the #833 D controls, update the
subsumption ledger, reopen on descendant gaps. They close only once enough
Tier-1 packages exist to have something to audit, and they close **as a sweep**
over the emitted receipts rather than one at a time. **7** rows, last.

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

**16 of 122.** Both packages carry a freeze committed before any implementation
blob existed, parent-ownership disclosure with DOIs, named theorem notes, two
materially independent routes, hostiles proved potent before proved detected, a
null the true result beats with the no-alarm case asserted, and a dedicated
workflow.

A third freeze, `gmi-833-ae-ae10-usable-information-v1/FREEZE_V1.md`, is
committed and **not yet implemented**: it is staged prospectively so that the
AE10 tranche cannot be accused of post-hoc scoping. It closes no row until its
executor, oracle, tests and receipt land.

## Batching plan for the remaining 106

Ordered by dependency, not by row number. Each entry is one package.

1. `gmi-833-ae-ae10-usable-information-v1` — **5 rows** (AE10 rows 1, 2, 3, 4, 6;
   row 5 deferred to the morphology sweep). Freeze already committed. Defines
   usable information on a budget lattice, proves monotonicity and the
   full-information ceiling, and exhibits the equal-Shannon/different-usable
   pair. Reuses no AE2 code but pins its receipt. *Ready now; smallest
   remaining package.*
2. `gmi-833-ae-ae3-compression-learning-v1` — **8 rows**. Three compression
   notions separated exactly; a corpus that compresses whose code is useless for
   the target; a useful predictor that is not the shortest description under the
   registered coding language; the Kolmogorov uncomputability boundary stated as
   a forbidden promotion rather than a claim; computable surrogates with their
   language dependence measured across at least two universal-machine remints.
3. `gmi-833-ae-ae4-information-bottleneck-v1` — **8 rows**. Requires AE3's
   coding-language registry. Determines, on finite worlds, when a GMI minimal
   predictive state equals, refines, or is incomparable with an IB-optimal
   representation, with the smallest counterexample blocking unqualified
   identification.
4. `gmi-833-ae-ae5-causal-state-audit-v1` — **6 rows**. Mostly a parent-ownership
   audit against computational mechanics: build processes where predictive-state
   cardinality, linear predictive rank, causal-state entropy and description
   length disagree, then say plainly which GMI state-complexity results are
   already parent-owned. Expect `PARENT_SUFFICIENT` terminals here, which are
   successes, not failures.
5. `gmi-833-ae-ae7-prediction-to-control-v1` — **6 rows** (row 7 to the morphology
   sweep). Extends AE1's control witnesses to a POMDP-style sufficient-state
   formalization with value-of-information conditions under resource cost.
6. `gmi-833-ae-ae13-causality-intervention-v1` — **6 rows** (row 7 to the
   morphology sweep). Extends AE1's confounded triple to a full observational
   equivalence class with differing intervention consequences.
7. `gmi-833-ae-ae15-world-model-necessity-v1` — **6 rows**. Tasks solvable
   optimally with no explicit model; tasks where a model is provably necessary
   under the registered interface; the model-based/model-free phase boundary.
8. `gmi-833-ae-ae14-generalization-taxonomy-v1` — **5 rows** (row 5 to the
   morphology sweep). Operational definitions plus matched tasks with equal
   predictive accuracy and different compositional capability. Row 6 is a
   *forbid* row and closes by the registered forbidden-promotion list.
9. `gmi-833-ae-ae6-geometric-structure-v1` — **7 rows** (row 8 to the morphology
   sweep, and its `real datasets` half to Tier 3). The manifold hierarchy,
   learnable non-manifold distributions, useless low-dimensional manifolds, and
   the locality/symmetry/compositionality derivations.
10. `gmi-833-ae-ae12-fep-audit-v1` — **6 rows**. Free-energy/active-inference
    parent audit with published technical criticisms, and finite discriminating
    tasks against rate-distortion control.
11. `gmi-833-ae-ae11-thermo-separation-v1` — **5 rows** (rows 6, 7 and the
    biological row to Tier 3). Keeps Shannon, algorithmic, statistical-mechanical
    and thermodynamic entropy formally distinct and audits Landauer-style bounds
    and their assumptions; claims nothing energetic without measurement.
12. `gmi-833-ae-morphology-sweep-v1` — **11 rows**, the Tier-2 family, closed
    together. Pins the existing morphology receipts by blob sha and runs one
    comparison of raw information, usable information and a resource-conditioned
    vector against selected morphology.
13. `gmi-833-ae-ae8-cpc-discrimination-v1` — **8 rows**. Last of the science
    packages: needs AE3, AE4, AE7, AE10 and AE12 settled first. The verdict on
    whether CPC is a theorem, a variational principle, a decomposition or a
    slogan, plus preregistered worlds where the candidate master principles
    disagree, plus preserved observational equivalence where no discriminating
    experiment exists.
14. `gmi-833-ae-ae17-recursive-ledger-v1` — **7 rows**, a sweep over everything
    emitted by 1-13.
15. **Not closed this programme without new instruments**: AE9 (7 rows), AE16
    (8 rows), AE11 rows 6-7 and the biological row, AE6's real-dataset half.
    These should be filed with an explicit instrument requirement rather than
    marked.

Running total if 1-14 land: `16 + 5 + 8 + 8 + 6 + 6 + 6 + 6 + 5 + 7 + 6 + 5 +
11 + 8 + 7` = **110** of 122, with the remaining 12 to 21 rows openly
instrument-blocked. That is the honest ceiling for AE without real training
runs, hardware energy measurement and a four-domain dataset programme.
