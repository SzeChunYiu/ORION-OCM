# RV-8 protocol — the H1 library-acquisition horizon — frozen before execution

**Target: `LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS`, currently PROJECTED, NOT
OBSERVED.** Evidence class E1 / L1, inherited unchanged from FNA-4. No neural arm is
run. Research-only; no production source is modified.

## What is already settled and is NOT re-derived here

A sibling lane refuted the standing attribution for H1 against our own receipts in
`research/functional-neural-absorption-v1/fna4_library_synthesis/FNA4_RESULTS.json`:

- The abstraction stage is **not** the failing stage. STITCH carries the highest
  marginal acquisition of any arm (240,294,343 units against the incumbent's 64,305)
  and is still the only arm that pays. Acquisition cost is anti-correlated with success.
- The failing stage is the **admission rule**. Utility-gated admission reaches −10.4%
  on the fresh 16-task stream (327,886 against 366,072); recurrence-gated admission is
  harmful at +1150% (Reynolds lgg, 4,576,312) and +1280% (e-graph saturation,
  5,050,822). Misfires isolate it: 451,582 and 286,120 against STITCH's 16,813.
- The lever was applied and worked. FNA-4's terminal is
  `PARENT_SUFFICIENT_FOR_EXPERIENCE_CONSOLIDATION_AT_REGISTERED_SCOPE`:
  270,829 < 366,072 units, −26.0%, every cost charged. A classical stdlib-only parent
  (Stitch + misfire nogoods + CEGIS) owns this function, so no ORION-OCM-specific
  attribution is available and none is manufactured.

## The one open question

Every one of those numbers is a **per-task** comparison at 16 tasks. Break-even is
**projected** at ~6,123 tasks (`repeat_rate_sweep_frozen_axis.r0_economics`:
240,294,343 marginal acquisition / 39,246.8 saving per task). That is a **380×
extrapolation**. This study runs the horizon.

It is a scale question, not a lever question. The lever question is closed.

## Frozen substrate — reused, not rebuilt

`rv8_horizon.py` **imports** `fna4`, `fna4_solver`, `fna4_learners` and `run_fna4`.
It defines no world, no solver, no learner, no cost term. Unchanged: the typed data
algebra, the 23-entry catalogue, the production `SolveOperatorIndex` selection path,
`WarrantProfile` meet admission, `INCUMBENT_CAP=1000000`, `DOMAIN_CAP=24`,
`MAX_LIBRARY=6`, `MAX_PATTERN_LEN=5`, the acquisition stream (4 F1 + 4 F2 at
`SALT_ACQ=620001`, solved `collect_all=True`), and the one commensurable integer unit
per simulation / checker call / posting read / learner step. Macro bodies still charge
one simulation per internal step; hole-domain enumeration, misfire probes, rejected
candidates and CEGIS refinements are all still charged. **A burden number that drops a
term is a defect, not an improvement.**

## Frozen axes

**Horizon.** One stream per cell, read as a ladder of prefixes:
16, 64, 256, 1024, 4096, 16384, 32768, 65536, **131072**.

`N_FULL = 131072` is sized before any scored cell from two pre-existing sources:

| source | STITCH saving/task at m=0.50 balanced | implied N\* |
|---|---|---|
| FNA-4 frozen per-family deltas | 11,922 | 17,257 |
| unscored timing probe, salt 999001, 3 draws/family | 1,184 | ~203,000 |

They disagree by more than 10× because FNA-4's per-family deltas rest on 8/4/4 draws of
a heavy-tailed cost distribution. 131,072 contains the first with ~7.6× margin and
reaches well into the second. **If no crossing appears by 131,072 the answer is "no
crossover within the horizon reached", stated with that horizon and never extrapolated
further.**

**Same-family mix.** F2 (MERGE-AC) is the only family on which the library pays in
FNA-4's frozen per-task deltas, so the same-family share is the F2 share:

`0.00, 0.05, 0.10, 0.12, 0.15, 0.17, 0.20, 0.25, 0.35, 0.50, 0.75, 1.00`

This spans below, through and past the claimed critical band (STITCH_NOGOOD_CEGIS
balanced 0.1176 to STITCH balanced 0.1696) and past the all-F1 edges (0.1740, 0.2417).
The claimed boundary is a `(mix, horizon)` pair, so the deliverable is the **surface**.

**Non-F2 composition.** FNA-4's own two conventions: `balanced` (F1:F3 = 1:1) and
`f1_only` (all F1, its worst case).

**Seeds.** Stream seeds 0-4. Null-library seeds 0-2.

## Frozen stream construction

Family assignment uses a **prefix-preserving deficit allocator**: at every prefix
length the realised family shares match the targets to within one task, so the ladder
is readable off one stream without the mix drifting. Ties break by the frozen order
`F2, F1, F3`.

**Declared difference from FNA-4, with its reason.** FNA-4 draws a stream from one
shared `random.Random`; this study seeds a fresh `random.Random` per position from
`(SALT_RV8=810001, mix_idx, composition, seed, pos)`. The marginal draw distribution is
identical — the same `gen_task` over the same parameter spaces — but any worker can
regenerate any prefix independently, which is what makes a 131,072-task ladder
parallelisable and prefix-reproducible. `SALT_RV8` is disjoint from every FNA-4 salt,
so acquisition and stream stay disjoint.

**No parameter tuple is ever forced.** FNA-4's sweep builder fills its uncovered quota
from `_f1_param_space()` in *product order*, so at r=0 its twelve F1 tasks are
near-identical draws from one corner of a 648-tuple space. These are natural draws.
The difference is measured, not assumed — see the replication gate.

## Frozen arms

| arm | admission rule | horizon |
|---|---|---|
| `NO_LIBRARY` | none (incumbent baseline) | full |
| `STITCH` | utility-gated (`uses×(body−1) − definition`) | full |
| `STITCH_NOGOOD_CEGIS` | utility-gated + nogoods + CEGIS — **holds `PARENT_SUFFICIENT`** | full |
| `NOGOOD_ONLY_per_batch` | failed-experience only, no library | full |
| `CHUNK` | exact-match caching | reduced |
| `AU_PAIR` | recurrence-gated (Reynolds lgg, ≥2 pair observations) | reduced |
| `EGGRAPH` | recurrence-gated (e-class ≥2 uses, MDL>0) | reduced |
| `SHUFFLE_NULL` | shape-matched random library, nulls `STITCH` | full |
| `SHUFFLE_NULL_NC` | shape-matched random library + nogoods + CEGIS, nulls `STITCH_NOGOOD_CEGIS` | full |

**The classical parent is the thing to beat and it may well still win. That is a
success terminal, not a failure.**

**Pre-registered reduced horizon** (`N_REDUCED = 4096`). An arm runs the reduced
horizon iff FNA-4's frozen per-family deltas make its saving/task negative at *every*
grid point under *both* compositions, so no horizon can cross. Recomputed and asserted
in `preflight()`, never asserted by hand:

| arm | F1 | F2 | F3 | max saving/task over the grid |
|---|---|---|---|---|
| `CHUNK` | +856 | +47,980 | −96 | −380 |
| `AU_PAIR` | +29,904 | +986,944 | +5,808 | −17,856 |
| `EGGRAPH` | +20,492 | +1,126,800 | +3,403 | −11,947 |

The independent timing probe agrees on all three (AU_PAIR 15×, EGGRAPH 12×, CHUNK 1.7×
the incumbent's F2 cost). The sign is established with a tight CI on a 4,096-task
prefix of the *same paired stream*; the freed budget goes to the arms where a crossover
is possible. **Pre-registered escalation:** if any reduced arm's measured saving/task
CI includes zero at any grid point, that arm is escalated to the full horizon in a
**new frozen study**, never by extending this grid.

## Frozen null — shuffle-equal-n

`SHUFFLE_NULL` matches its learned counterpart on macro **count**, body **length** per
macro, hole **positions**, hole **domain sizes** (hence the number of enumerated
assignments — the real per-attempt burden) and **type coherence**. It randomises which
catalogue families and constants fill those slots, and it **pays the same acquisition
it nulls**: the question is whether the library's *content* earns the saving, not
whether acquisition can be skipped.

Matching enumeration burden and not merely macro count is the point: 24-element domains
cost far more per attempt than 2-element ones, so a count-only match would make the
null look artificially bad and the "not selectivity" conclusion unearned. The
per-macro match, including any domain shortfall, is recorded in the preflight receipt
so the null is auditable rather than assumed.

**A crossover reproduced by a shape-matched random library is selectivity, not
payback.**

## Frozen hard gates — no number is filed if one fails

1. **Selection mirror.** The production `SolveOperatorIndex` counts must equal brute
   force, or `CANNOT_CHECK_SELECTION_MIRROR_DISAGREES_WITH_PRODUCTION_INDEX`.
2. **Acquisition reproduction.** Acquisition is deterministic and must reproduce FNA-4
   run 3 **exactly**, or `CANNOT_CHECK_ACQUISITION_DRIFT`:

   | arm | acquisition total_units | learner_steps (marginal) |
   |---|---|---|
   | `NO_LIBRARY` | 13,549,261 | 64,305 |
   | `CHUNK` | 13,550,768 | 65,812 |
   | `AU_PAIR` | 14,684,038 | 1,199,082 |
   | `EGGRAPH` | 13,565,306 | 80,350 |
   | `STITCH` | 253,779,299 | 240,294,343 |
   | `NOGOOD_ONLY_per_batch` | 13,495,472 | 173,186 |
   | `STITCH_NOGOOD_CEGIS` | 253,725,510 | 240,403,224 |

   Acquisition shares **one** `Work` across the acquisition solves and the learner call
   (so the marginal figure includes the `collect_all` bookkeeping the solver charges),
   and **one** `MisfireRegistry` carried into every later task — `run_arm`'s structure,
   reproduced rather than re-invented.
3. **Frozen-receipt replication.** FNA-4's repeat-rate sweep r=0 point must reproduce
   exactly — `no_library_total` 1,711,950, with-library test work 770,026, saving
   941,924, 19 macro hits — or `CANNOT_CHECK_FROZEN_SWEEP_REPLICATION_DRIFT`. This
   certifies that the ~6,123 projection and this study's numbers come from one machine.
   The same library is then run over a **natural-draw** stream at the same mix and
   length, and both are reported side by side.

## Frozen endpoints

- **Present cost**: acquisition, in both of FNA-4's accountings (full and marginal).
- **Future reuse**: cumulative **paired** saving, arm vs `NO_LIBRARY` on the same task
  at the same position. **Reported separately from present cost, never netted before
  both are shown.** That separation is what the whole H1 question is about.
- **Crossover N\***: smallest N with cumulative saving ≥ acquisition, against both
  accountings, with a 95% CI on the mean saving/task inverted to a CI on N\*, reported
  as "> N_max, none observed" when no crossing occurs. The CI is a bootstrap (2,000
  resamples, seed 815001) for samples of ≤20,000 tasks and a normal approximation above
  that: per-task cost has bounded support because `INCUMBENT_CAP` truncates the tail, so
  the variance is finite and the CLT applies, and resampling 655,360 draws 2,000 times
  buys no extra information.
- **Critical mix**: zero-crossing of saving/task in the mix, with a CI. Below it no
  horizon pays, so N\* has a vertical asymptote there. **The surface carries two
  different quantities on its two halves and both are reported as such** — cells
  reading "no crossover" below the critical mix are the correct answer there, not a
  failed run.
- **Windowed saving/task** in eight disjoint windows, to separate a stationary
  crossover from a decaying transient: the misfire registry saturates and CEGIS domains
  shrink monotonically, so the stateful arms have a real transient.
- **Capped tasks**, per arm per cell, as a first-class endpoint, plus a pre-registered
  sensitivity pass recomputing every endpoint excluding them. `INCUMBENT_CAP` was sized
  from 4 F2 draws (hardest: 382,353 expansions); at 131,072 draws the tail is sampled
  far deeper, and a capped task's cost is *truncated*, which biases the baseline down
  and understates the library's saving. The cap is kept for parent parity.
- **Null**: learned vs shape-matched random library at every grid point.

## Registered predictions, before any scored cell

- **R1** The frozen sweep replication reproduces exactly, and the natural-draw stream at
  the same mix and length gives a **materially smaller** saving/task than 39,246.8,
  because the sweep's F1 half is a product-order corner rather than a draw.
- **R2** `STITCH` and `STITCH_NOGOOD_CEGIS` have positive saving/task only above a
  critical mix; the measured critical mix will have a CI wide enough to make the
  11.8-17.0% band a point estimate from 16 draws rather than a boundary.
- **R3** The measured N\* at m=0.50 exceeds the projected 6,123 — the projection was
  computed on a constructed stream.
- **R4** `CHUNK`, `AU_PAIR` and `EGGRAPH` have negative saving/task at every grid point;
  no horizon crosses.
- **R5** `SHUFFLE_NULL` has negative saving/task everywhere; the learned library's
  saving is not reproduced by a shape-matched random one.
- **R6** Capped tasks are rare at low mix and non-negligible at m ≥ 0.5; excluding them
  moves saving/task **up** for the library arms.

## Outcomes, all three legitimate

- Crossover **observed** near ~6,123 → the projection is confirmed and H1 becomes an
  observed negative with a measured boundary.
- Crossover observed **elsewhere** → the projection was wrong; report by how much and
  why.
- **No crossover** within the tested horizon → acquisition never repays in this regime,
  a stronger negative than the projected one, stated with the horizon actually reached.

**Never tune an outcome positive.** The mix grid, the stream construction, the horizon
ladder and the arms are frozen in this commit, which contains **no result file**. A
post-freeze change requires a recorded supersession with cause and a re-run.

## Declared limitations, before seeing outcomes

Planted worlds, one author: E1/L1, not E3. Inherited from FNA-4: the catalogue is small
and the families shallow relative to program-synthesis benchmarks; the claim scope is a
mechanism class on this substrate, not a benchmark result. `INCUMBENT_CAP` truncates the
deep tail and is kept for parity. The mix axis has three families, so "same-family
share" is F2 share and nothing broader. Human prior enters only through the frozen
family generators, identically for every arm including `NO_LIBRARY`.

## Execution — LUNARC, offline

`ssh lunarc` (`cosmos3.int.lunarc`). **No network connection is made from LUNARC to any
external service**; code is staged in by `scp` with an md5 check on arrival, compute is
pure offline, results are pulled back.

**Recorded deviation, with cause.** The assigned `nuc` partition rejects this project:

```
sbatch: error: Your project is not allowed to run on the nuc partition.
sbatch: error: Batch job submission failed: Invalid account or account/partition combination specified
```

`scontrol show partition nuc` reports `AllowAccounts=ALL`, so this is a submit-plugin
rule, not a partition ACL. Work runs on `lu48` instead (186 nodes, 8,928 cores, 7-day
limit) under account `lu2026-2-51`. `hep` is avoided: it is saturated with the
operator's unrelated jobs. Sibling lanes `form-oracle` and `rv-a-generalization` and
their directories are not touched.

Cells write progressively every 4,096 tasks, so a timed-out or crashed cell still
yields a usable, honestly-labelled prefix. Defect runs are preserved and never edited.
