# FNA-4 report — library/synthesis learner parent suite for #62

**Issue #214 work package FNA-D6, target #62 (experience consolidation). Base
`86ddd9bcedfb48de804fbb68d599f00ebd8316ba`. Evidence class E1 / L1: planted task
worlds, one author, one population, stdlib-only non-neural parents over main's own
composition substrate (`SolveOperatorIndex`, `WarrantProfile` meet, misfire
nogoods). No neural arm exists. Execution: billy-old, Python 3.14.4.**

## Terminal

```text
PARENT_SUFFICIENT_FOR_EXPERIENCE_CONSOLIDATION_AT_REGISTERED_SCOPE
   C_future(T | E_t) < C_future(T | E_0) CONFIRMED with every cost charged:
   270,829 < 366,072 units on an identical 16-task fresh stream (-26.0%),
   by the classical arm STITCH + per-batch nogoods + CEGIS.
   Qualifiers (measured, not assumed): pays only above a critical same-family
   share (F2 >= 11.8-17.0% of the stream); break-even horizon ~6.1k tasks at
   zero repeat; recurrence-gated admission (Reynolds AU, e-graph) is HARMFUL
   on this substrate; utility-gated admission (Stitch) is load-bearing.
```

No claim beyond this scope. Nothing here licenses any neural-superiority,
neural-necessity or general-capability statement (asserted by test).

## Main comparison (scored run 3, all 16/16 solved, every unit charged)

| arm | fresh 16-task cost | vs incumbent | marginal total* | macro hits | misfires |
|---|---:|---:|---:|---:|---:|
| NO_LIBRARY (incumbent) | 366,072 | — | 430,377 | 0 | 7,166 |
| CHUNK (Soar cache) | 564,453 | +54% | 630,265 | 1 | 28,551 |
| AU_PAIR (Reynolds lgg) | 4,576,312 | **+1149%** | 5,775,394 | 0 | 451,582 |
| STITCH (utility, guide-less) | 327,886 | **−10.5%** | 240,622,229 | 9 | 16,813 |
| EGGRAPH (egg saturation) | 5,050,822 | **+1279%** | 5,131,172 | 3 | 286,120 |
| NOGOOD per_op | 562,354 | +54% | 8,626,690 | 0 | 0 |
| NOGOOD per_batch | 362,647 | −0.9% | 535,833 | 0 | 0 |
| **STITCH+NOGOOD(per_batch)+CEGIS** | **270,829** | **−26.0%** | 240,674,053 | 9 | 2,286 |
| ORACLE teleport (labelled bound) | 162 | −99.96% | — | 16 | 0 |

\* marginal = consolidation-only units (learner/bookkeeping) + stream; full
accounting (exhaustive acquisition search + stream) is in FNA4_RESULTS.json for
every arm. Both were pinned in addendum V1 before any scored number existed.

Per-task delta vs incumbent by family (the decomposition that explains everything):

| arm | F1 | F2 (merge-AC) | F3 (held out) |
|---|---:|---:|---:|
| STITCH | +11,153 | **−34,998** | +3,146 |
| STITCH+NOGOOD+CEGIS | +9,594 | **−45,550 (−53%)** | +2,552 |
| AU_PAIR | +29,904 | +986,944 | +5,808 |
| EGGRAPH | +20,492 | +1,126,800 | +3,403 |
| NOGOOD per_batch | 0 (exact) | −857 | 0 (exact) |

## Five findings

**1. Utility-gated admission is load-bearing; recurrence-gated admission is
harmful.** The frozen corpus (1,533 chains the incumbent actually ran) is dominated
by coincidence compositions — the checker accepts any goal-reaching chain, so
shallow coincidences recur heavily. Parents admitting by recurrence (AU: skeleton
observed twice; EG: saturated e-class with positive compression) admit long
coincidence shapes: every AU macro misfired 83,328 times on 16 fresh tasks with
zero hits. The parent admitting by usefulness (Stitch compression = uses×(body−1)
− definition, corpus rewritten top-down) admitted short fragments that fire. This
is the in-suite revival chain for the AU/EG negative: one-stage attribution
(admission stage: recurrence ≠ transfer), lever (utility gate), re-test (the
STITCH arm — same budget, same corpus, same cap) — measured, not asserted.

**2. The OCM-shaped combination compounds.** Library (−10.5%) + per-batch nogoods
+ CEGIS domain refinement = −26.0%. CEGIS refinements: 2 (one task); misfire
re-enumeration ÷7.4 (16,813 → 2,286). Nogood granularity pair (revival of run 1's
finding on the fixed harness): per_batch saves 3,425 units and is exactly neutral
on untouched families (F1 +2, F3 +1 units); per_op pays 8,064,336 acquisition
probes and still costs +196,282 on the stream itself — refuted as deployable at
1:1 charge.

**3. The payback structure: family mix binds, repeat rate does not.** On the
frozen r=0 sweep stream (zero task-level coverage) the library still saved 941,924
of 1,711,950 units (−55%): fragments fire by family structure, parameters ride in
the holes. So the break-even is a horizon (6,123 tasks at marginal acquisition
240,294,343) and a mix (critical F2 share 17.0% balanced / 24.2% all-F1 for
STITCH; 11.8% / 17.4% for the combined arm; no share pays for CHUNK/AU/EG).
Below the critical share NO_LIFETIME_PAYBACK holds on every horizon. The P6
revival sweep (below) sharpens this: the repeat rate itself produces no boundary
in either direction — what the r-axis measured is heavy-tail variance.

**4. Governance behaved exactly as specified.** Revocation of `ev:fam:filter`:
cone exact (every dependent macro dead, 0 stale survivors, 0 collateral dead),
independent macros kept firing (2 hits on F2/F3 after revocation). Ablation:
library removed mid-stream regresses to NO_LIBRARY exactly (346,722 = 346,722,
byte-identical work dicts). Determinism: identical.

**5. The guide-less parent's selection cost is the story of the margin.** 240.3M
of the 240.7M marginal units are Stitch's exhaustive usefulness search (segment
pair enumeration over the 1,533-chain corpus, 8 rounds, each comparison charged).
The 26% fresh-cost win is real but amortises over ~6.1k tasks because the
classical search for what to learn costs three orders of magnitude more than what
it saves per task. That is a cost-structure fact about the parent on this
substrate at this corpus scale — no claim about any other learner class.

## Prediction outcomes (all registered pre-score in FNA4_FREEZE.json)

- **P1 CHUNK 0 fresh hits — FALSIFIED as stated**: 1 hit (T-F3-2, an exact
  parameter repeat; the parameter spaces are small). The mechanism claim stands:
  the cache costs +54% overall despite its hit.
- **P2 STITCH >= AU — CONFIRMED decisively. "Both reach finite break-even" —
  half-falsified**: STITCH's is finite (6,123 tasks); AU's is not (harmful at
  every mix).
- **P3 EG = AU on F1, EG > AU on F2 — FALSIFIED both halves** (cost: EG 183,288
  vs AU 258,582 on F1 — both harmful; EG 4,850,567 vs AU 4,291,143 on F2 — EG
  worse). AC canonicalization did not help: the corpus is coincidence-dominated,
  so e-classes of merge variants are classes of coincidences.
- **P4 held-out F3: zero hits, bounded waste, no capability loss — waste and
  capability CONFIRMED** (all arms 16/16; F3 cost bounded at +3.1k/task), **hits
  FALSIFIED**: 1 coincidental fragment hit each for CHUNK/STITCH/EG (shared
  fragments, not family leakage — F3's zip family appears in no library).
- **P5 revocation cone exact — CONFIRMED exactly** (0 stale, 0 collateral).
- **P6 critical repeat rate r* — UNMEASURABLE as frozen, and the revival axis
  shows NO r\* EXISTS**: frozen axis (r>0 streams non-constructible: task-level
  single-macro coverage is empty for a fragment library) → declared revival
  iteration (addendum V3, axis moved to composition-level repeat: a task is
  repeat-covered iff a chain the incumbent actually ran reproduces its goal).
  Revival results (receipts/FNA4_SWEEP_R2_RECEIPTS.json): low-r streams are
  themselves non-constructible — the 1,507 exhibited chains composition-cover
  9 of 12 F2 parameter tuples and all but 3–4 draws of the 648-tuple F1 space,
  so no stream can hold the 6–12 uncovered tasks per family that r ≤ 0.5
  demands (got_need tuples in the receipts). At the constructible r=0.75/1.0
  the library LOSES −1.31M/−1.33M per stream, with 15/18 and 15/15 of its hits
  landing on covered tasks. The
  one-stage attribution (probe, deterministic stream rebuild reproducing the
  scored totals exactly: probes/probe_r2attr_output.txt) kills the
  repeat-rate reading: the r=1.0 inversion is ONE heavy-tail task
  (R2-F2-4-1: incumbent 649,368, with-library 2,747,069, +2,097,701 alone);
  the other 23 tasks net-SAVE 766,330 — so the library "hurts at r=1.0" only
  through one task whose incumbent search it lengthened. Mechanism: a macro is a first-class
  catalogue entry, so its entry-combo × assignment × body enumeration is charged
  at every search expansion — the macro lane's cost scales with the incumbent's
  own search length. It is a variance amplifier on the heavy tail, not a
  repeat-rate boundary. NO_LIFETIME_PAYBACK holds against the 240.3M marginal
  acquisition at every measured r and every mix (best observed stream saving
  941,924; worst −1,331,371). The identified lever — depth/budget-gated macro
  application, stopping the per-expansion macro charge after a bound — is an
  OCM-side design change outside FNA-4's frozen parent set; recorded here as the
  next lever, not tuned in-suite.
- **P7 NOGOOD saves on repeats, loses nothing on F3 — CONFIRMED for per_batch**
  (exactly neutral off-family), **refuted for per_op** (2.3).

## Engineering the harness: three defects, preserved, never edited

Run 1 (`defect_runs/FNA4_DEFECT_RUN1_RECEIPTS.json.gz`, sha256 b0acd3c5…):
(a) macro application was state-oblivious — identical enumeration re-charged per
search state (EG: 3,721 states × 2 assignments, all misfiring) and derived-atom
entries could never fire; fixed by entry-combo enumeration over the live state.
(b) experience recording kept only the incumbent's FIRST chain, so every learner
saw a coincidence-shaped corpus and P2/P3/P6 were unmeasurable by construction;
fixed by collect_all (record every checker-passing chain the paid search ran).
(c) the ablation compared a F1-only half against a F2+F3 half; fixed with
same-mix references. All three fixes + attributions were frozen in addendum V1
BEFORE run 2. Run 1 also falsified P1 on its own (CHUNK 2 hits), which carried
into run 3's confirmation.

Run 2 (`defect_runs/FNA4_DEFECT_RUN2_PARTIAL.json.gz`, sha256 059b4b31…):
learn_au crashed on the full corpus (TypeError: None < str ranking hole-bearing
skeletons — unreachable on run 1's 8-chain corpus). Fixed per addendum V2
(incremental accumulator, None-safe ordering, lazy admission with identical
admitted set: 0.7 s vs >12 min on the 1,533-chain corpus, probe-validated
pre-score). The charge change (1 unit per admitted macro, not per candidate) is
declared in V2; neither variant was ever scored before.

P6 revival (addendum V3, declared before the re-test): run 3 proved the frozen
sweep's coverage axis empty at every r>0 for a fragment library, so the stream
builder could not build any r>0 stream. The revival re-defines the axis at the
composition level (a task is repeat-covered iff a chain the incumbent actually
ran reproduces that task's goal on its own payload), reusing every frozen
mechanism. Receipts: `receipts/FNA4_SWEEP_R2_RECEIPTS.json`.

## What this does not establish

Planted world, one author, one population (E1/L1, not E3). Small catalogue,
shallow families relative to program-synthesis benchmarks; the claim scope is the
mechanism class on THIS substrate. Acquisition corpus = 8 tasks (1,533 chains);
corpus-scale effects on learner cost are reported at that scale only. No
maintenance-under-edit beyond revocation (the catalogue is immutable during a
run). The 240M-unit learner cost is the exhaustive guide-less variant of the
parent; nothing here measures any guided variant, and nothing here licenses
`TRANSFORMER_REPLACED`, `LLM_EQUIVALENT`, or any general-capability claim — a
test asserts no artifact contains them.

## Files

`FNA4_PROTOCOL.md` · `FNA4_SOURCE_LEDGER.json` · `FNA4_FREEZE.json` ·
`FNA4_FREEZE_ADDENDUM_V1/V2/V3.json` · `fna4.py` (world, macros, warrants) ·
`fna4_solver.py` (incumbent, charged search, nogoods) · `fna4_learners.py`
(parents) · `run_fna4.py` (scored suite) · `run_fna4_sweep_r2.py` (P6 revival) ·
`distill_results.py` · `test_fna4.py` (16 tests, green on billy-old py3.14.4) ·
`FNA4_RESULTS.json` · `receipts/FNA4_RUN3_RECEIPTS.json` (+.gz; raw sha256
06a72a5e87d33c6681332a9a06477a06b5b5962768a33e172638023dfe628d5b) ·
`receipts/FNA4_SWEEP_R2_RECEIPTS.json` · `defect_runs/` · `FNA4_REPO_STATE.json`

```bash
# off-Mac host, capsule dir:
python3 test_fna4.py                      # 16 tests
python3 run_fna4.py <out_dir>             # scored suite (~30 min)
python3 run_fna4_sweep_r2.py <out_dir>    # P6 revival sweep
python3 distill_results.py                # rebuild FNA4_RESULTS.json from receipts
```
