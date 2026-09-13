# RV-377-180 — FREEZE: B6 cross-paradigm developmental morphogenesis (GMI-T12)

Frozen BEFORE the run. Outcomes appended only. Reserved ids RV-377-180…189.

## The question

Issue #377 §19 asks the meta-level question once known-morphology recovery succeeds (it has: `RV-377-113`,
G15 step (ii) reached at registered scope):

> Does developmental history make finding the *next useful morphology or learning law* easier?
> `B_morph,g` = complete resources until the first verified useful morphology change at generation g;
> track `B_morph,g+1 < B_morph,g` on fresh ecology shifts, with quality preserved and all failed
> candidates charged.

The boundary theorem (`GMI_COMPLETENESS_BOUNDARY_THEOREM_V1.md` §4) lists rung B6 as **BLOCKED (GMI-T12)**.
This record executes GMI-T12 at the registered scope of the boundary theorem: the 36-kind typed alphabet,
depth 1, 8-bit precision, the R5 grammar, θ = 0.85, the six registered interventions (of which
`extra_unseen_feedback` leaks 50 %, DG-13 — retained because rule 36 as written requires all six; the
five-intervention reading is recorded alongside).

## The objects

**Developmental history** = the MAP-Elites archive produced by the unchanged B1 search (`gmi_microscope/b1.py`,
`search`, default path) on a SOURCE ecology `E_a`, 20 000 charged evaluations, seed `s`. The full archive
(every occupied cell with its genotype) is saved by `b6_development.run_source`; the committed B1 receipts keep
only the best genotype per carrier and cannot seed a population.

**Three arms** on a fresh TARGET ecology `E_b`, identical charged budget (20 000 evaluations, seed placements
charged like any other) and identical seed integers:

| arm | initial population | what it is |
|---|---|---|
| RESET | 400 fresh random genotypes (the committed default) | generation g from scratch |
| CONTINUED | the elites of `E_a`'s archive | the developmental arm, generation g+1 |
| TWIN | the elites of the archive of a randomised table ecology `E_twin<s>`, **carrier-matched** to the CONTINUED seed set | the matched negative: "any warm start", no history on any structured ecology |

Carrier matching (`matched_populations`): per raw-carrier class c, `k_c = min(n_a[c], n_twin[c])`; both seed sets
take the top-`k_c` elites of their archive by capability, so the two seed sets have identical size and identical
carrier histograms. Raw carrier is the archive's own descriptor; rule 23 governs recovery *claims*, and no claim is
made about a seed. The mutation loop is untouched: parents are drawn uniformly from the archive as before.

**Measurement per run** — the first admissible machine on `E_b`, found by a post-hoc ordered scan of every
θ-crossing placement recorded by the search (`trace`), each candidate verified in evaluation order:

1. rule 36: capability ≥ θ under all six registered interventions (`ecology.run_genotype`); 6 replays;
2. rule 40: min over six − best constant ≥ 1 fx unit (`eco_axis.best_constant`, unseen criterion);
3. rule 42: fixed-function null — distinct final served-answer vectors over the five registered smooth probe
   targets ≥ 3 (RV-377-103 C4); extractor validated on `constant_emitter` (must read 1) and `gradient_net(3,1)`
   (must read ≥ 3) before any candidate is read; 5 replays;
4. rules 23/32: atrophy under all six interventions (`atrophy_ir.prune_all_interventions`) with the floor
   `max(θ, best_constant + 1 fx)` so the atrophied genotype still clears rule 40 by construction; rule 42 re-read on
   the atrophied genotype; every deletion trial charged once per intervention.

`B_search` = search evaluations up to that placement (failed phenotypes included). `B_verify` = every control
replay spent on that candidate and on every earlier θ-crossing candidate that failed. **`B_morph = B_search +
B_verify`** is the primary measure. Also recorded: `B_dense`, the same measure restricted to candidates whose
ATROPHIED carrier is DENSE (the coefficient carrier), scanned independently; final best capability (standard) and
final best per carrier at 20 000; the atrophied carrier class of the first admissible machine; its lineage root
(which seed it descends from).

The source's own 20 000 evaluations are generation g's burden and are not charged to g+1: that is what §19's
inequality compares.

## The ecology pairs — deterministic rule

Occupancy oracle: `GMI_RV_377_113_INTERVENTION_SCAN.json` (committed), read as: occupant class of an ecology =
the set of carriers admissible under all six interventions at 20 000 evaluations, seed 0.

| ecology | all-six occupants | rule 40 | reading |
|---|---|---|---|
| `E_smooth1` | KVSTORE, PROGRAM, TABLE | 0.502 fx (within quantization) | memory-occupied, no separation |
| `E_smooth3` | KVSTORE, PROGRAM, TABLE | 1.126 fx | memory-occupied, separating |
| `E_sym5` | DENSE, KVSTORE, PROGRAM, TABLE | 1.500 fx | coefficient-witness-bearing (and memory) |
| `E_wit1` | none | — | no all-six occupant |

Rule: (i) `E_b` must carry a rule-36 **and** rule-40 occupant at 20 000 evaluations, else "first admissible" is
undefined at this budget → `E_b ∈ {E_smooth3, E_sym5}`. (ii) SAME-PARADIGM: memory-occupied → memory-occupied,
source = the other memory-occupied registered ecology. (iii) CROSS-PARADIGM: memory-occupied → the
coefficient-witness-bearing ecology. (iv) DISJOINT: no shared structure. The registry contains no ecology without
bit-linear structure (`E_parity`'s target is the identity, DG-13; every smooth target is linear in the input bits;
`RV-377-102`'s enumeration is the linear class), so the DISJOINT source is a **seeded random table**: 16 values
uniform on the fx range spanned by the smooth targets, [−24, 24], seed 4242 + s (`E_rnd<s>`); the TWIN sources
use the same generator with seed 7001 + s (`E_twin<s>`). The DISJOINT target is `E_sym5`, so CROSS and DISJOINT
share one RESET baseline (RESET does not depend on `E_a`) and the coefficient-carrier delay can be read against
a structured and a structure-free history on the same target and seeds.

| pair | `E_a` | `E_b` |
|---|---|---|
| SAME | `E_smooth1` | `E_smooth3` |
| CROSS | `E_smooth3` | `E_sym5` |
| DISJ | `E_rnd<s>` | `E_sym5` |

Seeds 0, 1, 2. Units: 12 sources (`E_smooth1`, `E_smooth3`, `E_rnd<s>`, `E_twin<s>` × 3) + 24 arms
(SAME 9, CROSS 9, DISJ 6) = 36 searches of 20 000 evaluations.

## Frozen predictions, derived from the theory's own results

Derivations used: **BR-1** (`GMI_BASIN_RESTART_DEVELOPMENT_THEOREM_V1.md`): expected independent starts until a
productive initialization = 1/p, so any change to the initialization measure μ that raises the productive-basin
mass p of the target's occupant class lowers the expected burden, and any change that lowers it raises the burden;
**CL-1** (`RV-377-123`): a memorizing machine knows only the indices revealed to it, so a memory carrier's *content*
is re-developed on `E_b` within its 16 events and only its *mechanism* (store + read-out + their parameters)
transfers; **T5** (`RV-377-116`): the carrier is an observable class, so "occupant class" is a measurable property
of an archive; **RV-377-074** (rule 23): raw descriptors mis-credit carriers, so every class statement below is on
the atrophied genotype; **RV-377-113**: on `E_sym5` the memory carriers are admissible at the same 1.5 fx margin
as DENSE, so the *first* admissible machine there is not expected to be the coefficient carrier under any arm.

| id | prediction | falsifier |
|----|-----------|-----------|
| D1a | SAME: `B_morph`(CONTINUED) < `B_morph`(RESET) on ≥ 2/3 seeds. (BR-1: `E_smooth1`'s memory elites are already in `E_smooth3`'s productive basin — the mechanism transfers by CL-1 — so p → ~1.) | CONTINUED ≥ RESET on ≥ 2/3 seeds |
| D1b | SAME residual over "any warm start helps": `B_morph`(CONTINUED) < `B_morph`(TWIN) on ≥ 2/3 seeds. (The twin's memory elites were selected on a structure-free target where the unseen criterion cannot be learned, so their read-out parameters — k, metric, temperature — were selected on noise; `E_smooth1`'s were selected on a smooth linear target and carry over.) | TWIN ≤ CONTINUED on ≥ 2/3 seeds → the parents (OOPS / PowerPlay / bias-optimal warm start) predict everything and B6's terminal is PARENT_SUFFICIENT_OOPS |
| D1s | (strong form, reported, not load-bearing) TWIN does **not** beat RESET on ≥ 2/3 seeds. **Predicted to FAIL**: CL-1 says the mechanism transfers whatever the source content, so a warm start from any memory-bearing archive is expected to help. Recorded so the parent's prediction is scored too. | TWIN < RESET on ≥ 2/3 seeds (= the parent is right) |
| D2a | CROSS: `B_morph`(CONTINUED) < `B_morph`(RESET) on ≥ 2/3 seeds and the atrophied class of the first admissible machine is memory (TABLE / KVSTORE / PROGRAM) on ≥ 2/3 seeds — the memory history buys the memory occupant of `E_sym5`, not the coefficient carrier. | CONTINUED ≥ RESET, or first class DENSE on ≥ 2/3 seeds |
| D2b | **The committed sign: harmful transfer for the coefficient carrier.** `B_dense`(CONTINUED) > `B_dense`(RESET) on every seed where both are determined (both reach an atrophied-DENSE admissible machine within 20 000). BR-1: a memory-adapted archive shifts μ away from the DENSE basin (its DENSE cells were selected on `E_smooth3`, where DENSE is inadmissible at 0.8125 — the dead region of BR §4), and uniform parent selection over a memory-dominated archive lowers p for DENSE; RESET's random init founds one machine in four on DENSE. A seed where either arm never reaches atrophied-DENSE within budget is recorded UNDETERMINED for D2b, not scored either way. | CONTINUED ≤ RESET on ≥ 2/3 determined seeds |
| D2c | Continuous form of the sign, always determined: CONTINUED's final best DENSE-cell capability (standard) on `E_sym5` ≤ RESET's on ≥ 2/3 seeds. | CONTINUED > RESET on ≥ 2/3 seeds |
| D2d | The delay is class-conditioned, not "any warm start": `B_dense`(DISJ-CONTINUED) is within the RESET seed spread (|difference| ≤ max − min of RESET's `B_dense` over the three seeds) or UNDETERMINED, on ≥ 2/3 seeds — a structure-free archive neither helps nor hurts the coefficient carrier. | DISJ-CONTINUED delays DENSE as much as CROSS-CONTINUED on ≥ 2/3 seeds → the sign is a warm-start artefact, D2b is not GMI content |
| D3a | DISJ: no ordering between CONTINUED and TWIN: |`B_morph`(CONTINUED) − `B_morph`(TWIN)| ≤ RESET's seed spread on ≥ 2/3 seeds (the two are exchangeable by construction; this calibrates the twin instrument). | a consistent ordering on 3/3 seeds |
| D3b | DISJ: `B_morph`(CONTINUED) < `B_morph`(RESET) on ≥ 2/3 seeds — the parent-predicted mechanism transfer (CL-1) from a structure-free archive; reported as the parent's prediction. | CONTINUED ≥ RESET on ≥ 2/3 seeds |
| D4 | Quality preserved: CONTINUED's final best capability (standard) ≥ RESET's on the same seed, on every pair, on ≥ 2/3 seeds per pair. | CONTINUED < RESET on ≥ 2/3 seeds on any pair |
| D5 | SAME: the atrophied carrier class of CONTINUED's first admissible machine ∈ `E_smooth1`'s occupant set {KVSTORE, PROGRAM, TABLE} on ≥ 2/3 seeds, and its lineage root is a seed elite (not a fresh random genotype). | class DENSE or NONE, or root not a seed, on ≥ 2/3 seeds |

**Kill condition.** If D1a fails on all three seeds, B6 is `DEVELOPMENTAL_MORPHOGENESIS_NOT_OBSERVED_AT_SCOPE`
(preserved negative) and one revival iteration `RV-377-181` runs with the single minimal justified change: longer
source development (50 000 evaluations on `E_smooth1`), attributed to ONE stage — the source archive's depth —
before any other lever is touched.

**Terminal register.** B6 is `DEVELOPMENTAL_MORPHOGENESIS_OBSERVED_AT_SCOPE` only if D1a **and** D1b hold. If D1a
holds and D1b fails, the terminal is `PARENT_SUFFICIENT_OOPS` (see below). D2b's outcome moves the sign row of the
boundary theorem addendum whichever way it lands, including UNDETERMINED.

## Parent subtraction — what OOPS / PowerPlay / bias-optimal warm starts already predict

*OOPS (Schmidhuber, bias-optimal incremental problem solving)* and *PowerPlay* own: an accumulated repertoire of
solutions / a learned proposal bias makes later problem solving cheaper on related tasks, and the repertoire grows.
Applied here they predict, without any GMI content: **CONTINUED < RESET on every pair whose source archive contains
working learners** (D1a, D2a, D3b), **TWIN < RESET** (D1s's failure), and **quality preserved** (D4) since the
archive keeps the best. They are silent on the *class* of what transfers: they predict a speed-up, not which
carrier appears first or whether a class-mismatched history delays a specific carrier.

What GMI adds, and what this record tests as the residual: (1) D1b — a history on a *structured* ecology beats a
carrier-matched history on a structure-free one, i.e. what transfers is not only the repertoire but the
ecology-selected read-out; (2) D2b/D2d — the **class-conditioned sign**: a memory-adapted archive *delays* the
coefficient carrier while a structure-free archive of the same carrier composition does not. These are statements
about the carrier classes of `RV-377-116` (T5) and the basin masses of BR-1, which the parents do not index.

**Honest terminal if the parents predict everything:** if D1b fails and D2b/D2d do not both hold, B6 is
`PARENT_SUFFICIENT_OOPS` — warm starts help, GMI adds no class-conditioned content at this scope — and it is
recorded as such without hedging.

## Calibration disclosed before the freeze (protocol rule 17)

Run on billy-old before this freeze was committed; nothing in the predictions above was changed after it ran.

1. **Byte-identity of the default path.** The committed `b1.search` (origin/main `99e4db13`, file placed beside
   the patched one as `b1_orig_tmp`) and the patched search produce the same 200-evaluation archive on `E_smooth3`
   seed 0 — digest `11f0c9cd24b7b674` for the committed file, the patched file, and the patched file with a trace
   list attached. Pinned in `test_b6_development.py`.
2. **The verifier reproduces `RV-377-113`.** Replayed on the 13 committed best-by-carrier genotypes of the
   `ABL_FULL` seed-0 receipts: min-over-six and binding intervention agree with `GMI_RV_377_113_INTERVENTION_SCAN.json`
   on **13 of 13**; `E_smooth1` × 3 fail rule 40 at 0.502 fx, `E_wit1` × 3 fail rule 36 at 0.8333, `E_smooth3` × 3
   and `E_sym5` × 4 pass at 1.126 / 1.500 fx; the rule-42 extractor reads 1 on `constant_emitter` and 4 on
   `gradient_net(3,1)`. **Seen and disclosed:** under atrophy with the rule-40 floor, `E_sym5`'s committed DENSE
   genotype (12 nodes, 0.9115) reads **TABLE** at 11 nodes — the coefficient recovery of `RV-377-113` is a raw-descriptor
   reading; on the atrophied genotype `E_sym5`'s seed-0 occupants are {KVSTORE, TABLE}. This makes an atrophied-DENSE
   first admissible machine rare, so D2b is expected to land UNDETERMINED on some or all seeds; D2c/D2d carry the
   sign in that case. D2b's text is unchanged.
3. **Timing.** 2 000-evaluation source searches: 68 s (`E_twin0`) and 87 s (`E_smooth3`); a 2 000-evaluation seeded
   arm: 128 s (search 124.5 s, verification 3.3 s: 599 θ-crossing placements, 3 scanned, first pass at trace index 2,
   `B_morph` 81 = 11 search + 70 verify, class TABLE — pilot numbers, not evidence). The committed 20 000-evaluation
   baselines took 1 040–1 490 s (superlinear as the archive fills), so 36 runs ≈ 15 core-hours ≈ 4 h wall at 4
   processes. **Three seeds are kept**; no scope reduction.
4. Pilot receipts carry the host token `PILOT`, are not read as evidence and are not committed. The carrier-matched
   seed set in the pilot had k = 4 per carrier (20 seeds); the NONE class is matched like any other.

## Execution

billy-old, `nice -n 10`, ≤ 4 processes; `gmi_b6_driver.py <host> sources 4` then `arms 4`; receipts
`microscopes/results/STAGE_B6_DEV_SRC_<eco>_S<s>_old.json` and `STAGE_B6_DEV_<pair>_<arm>_S<s>_old.json`,
rsync'd back and md5-verified both sides. Nothing runs on the Mac. No parameter is retuned after any outcome.

---

# RV-377-180-Z — a SEPARATE prospective registration, made with 7 of 24 arms in hand

**Not part of the frozen D-table above.** D1a–D5 are untouched and are still scored exactly as frozen.
This section registers a different question that the first seven arm receipts raised, and it is written
**before** the remaining seventeen arms exist so that it is a prediction rather than a reading. It is
scored separately and its outcome cannot change any D verdict.

## What prompted it

The corpus carries `COEFFICIENT_CLASS_NOT_NEUTRALLY_RECOVERED_AT_20K__0_OF_43`: across ten distinct
ecologies, neutral search at 20 000 charged evaluations has never once recovered the coefficient class
**under the atrophied reading** (rule 23). Lane B is the sharpest case — raw descriptor 4/9 DENSE,
atrophied reading 0/9.

`first_of_class(..., cls=("DENSE",))` in this lane applies that same bar: full `verify_candidate`
(rule 36 over six interventions, rule 40 ≥ 1 fx over the best constant, rule 42 raw and atrophied,
atrophy under all six with floor `max(θ, bc + fx)`) **and** `carrier_atrophied == "DENSE"`. So the arms
measure the identical quantity the invariant counts, at the identical budget.

Observed in the first seven arms, on the SAME pair whose target is `E_smooth3`:

| arm | initial condition | atrophied-DENSE admissible | DENSE cell reached |
|---|---|---|---|
| RESET S0 | cold random init | **no** | 0.8125 |
| TWIN S0 | warm, structure-free archive | **no** | 0.9010 (raw; fails the controls) |
| CONTINUED S0 | warm, structured archive | **yes**, min6 0.8542, +1.001 fx | 0.9062 |
| CONTINUED S1 | warm, structured archive | **yes**, min6 0.8542, +1.001 fx | 0.9583 |

Two facts make this worth registering rather than reporting. First, `E_smooth3`'s registered occupant set
is `(KVSTORE, PROGRAM, TABLE)`: **DENSE is not an occupant**, and D2b's own derivation calls it "the dead
region of BR §4", inadmissible at 0.8125 — which is exactly the value the cold arm reached. Second, both
recoveries have `origin = ["seed", k]` with `n_eval_search` of 18 595 and 3 827, so they are descendants
produced during the search from a warm-started lineage, not seed elites handed over at initialisation.

## Registered predictions (scored only when all 24 arms exist)

| id | prediction | what it would mean |
|---|---|---|
| **Z1** | SAME/CONTINUED reaches an admissible atrophied-DENSE machine on ≥ 2/3 seeds | the registered-unoccupied coefficient cell of `E_smooth3` is reachable from a developed archive |
| **Z2** | SAME/RESET reaches one on **0/3** seeds | the corpus invariant replicates at matched ecology, budget and bar — the cold-start arm is a within-lane control for the 43 |
| **Z3** | SAME/TWIN reaches one on ≤ 1/3 seeds | the lift is specific to history selected on a *structured* source, i.e. a residual over "any warm start helps" |
| **Z4** | no dead-region claim is available on CROSS | its target `E_sym5` lists DENSE as a registered occupant, so a DENSE recovery there is expected under any arm and is reported, not counted |

## Falsifiers, stated once

| id | registration is RED if |
|---|---|
| F-Z1 | SAME/CONTINUED reaches atrophied-DENSE on ≤ 1/3 seeds — the two hits were seed-luck |
| F-Z2 | SAME/RESET reaches it on ≥ 1 seed — the cell is reachable cold, so the observation is about *speed*, not reachability, and it does not touch the 0-of-43 invariant |
| F-Z3 | SAME/TWIN matches CONTINUED (≥ 2/3 seeds) — then any developed archive suffices, the effect is parent-owned (OOPS / bias-optimal warm start), and the honest terminal for the coefficient result is `PARENT_SUFFICIENT_OOPS`, recorded without hedging |

## What this cannot claim even if every prediction holds

It would be a statement about **one** target ecology at **one** budget under **one** generator. It would
not overturn the 0-of-43 invariant, which is about cold-start neutral search: it would *scope* that
invariant to its initial condition, which is a different and smaller claim than "the coefficient class is
recoverable". Nor would it license any capability claim — the recovered machines clear the rule-40 line by
1.001 fx, the minimum the bar admits, and that marginality is corpus-wide rather than special to DENSE.

---

## Instrument disclosure: the CROSS and DISJ twin arms are one experiment, not two

Found by a duplicate-experiment detector added to `b6_adjudicate` after `CROSS|TWIN|S0` and
`DISJ|TWIN|S0` returned identical `B_morph` (7 906), identical `final_best` (0.974), identical elite
fingerprints and identical `first_dense_admissible`. They are two distinct receipt files holding the
same computation.

**Mechanism.** The TWIN arm seeds from the randomised-table archive `E_twin<s>`, carrier-matched to
that pair's CONTINUED seed set. CROSS and DISJ share the target `E_sym5` and the same twin archive, and
on seed 0 the match **saturated in both pairs**: the twin archive holds
`DENSE 9 / KVSTORE 10 / NONE 4 / PROGRAM 9 / TABLE 10`, and both reference archives are at least that
large in every carrier (CROSS `10/18/6/24/23`, DISJ `9/15/6/20/20`), so `matched_k_per_carrier` equals
the whole twin archive in both cases. Same 42 seed fingerprints, same source receipt digest, same
target, same seed — therefore the same run. The receipts differ only in `pair`, `source_ecology`,
`history`, wall-clock and digest.

**Consequence, stated plainly.** The carrier-matched twin is pair-specific only when the twin archive
is *larger* than the reference archive in at least one carrier. When it is not, the "matched" control
degenerates to "the entire twin archive" and stops distinguishing the pairs. So the campaign's 24
receipt files contain **21 distinct experiments**: three `DISJ|RESET` files are the freeze's documented
shared baseline (one file read under two labels), and three `CROSS|TWIN` ≡ `DISJ|TWIN` pairs are one
computation reported twice. Any statement that counts warm-start arms on `E_sym5` as independent
evidence must use the distinct count, not the file count.

**What it does not affect.** D3a compares `DISJ|CONTINUED` against `DISJ|TWIN`, and its premise is that
the two are exchangeable by construction — `E_rnd<s>` and `E_twin<s>` are both structure-free random
tables feeding the same target. That premise is untouched, and the two arms give different numbers
(4 536 vs 7 906 on seed 0), so D3a remains a live test. No D or Z prediction is rescored because of
this disclosure; it changes how the evidence is *counted*, not what any arm measured.

`b6_adjudicate` now reports `duplicate_experiments`, separating `shared_baseline_by_design` (one receipt
file, two labels) from `duplicate_computation` (two files, same computation), and prints the distinct
count alongside the file count.

### Z control executed: admissibility was not inherited

The obvious deflation of the Z observation is that the warm-started arms did not *find* an admissible
coefficient machine at all — they were simply handed one in the archive they inherited. That control is
now run and it fails to deflate anything.

Every DENSE cell held by each source archive was replayed against the **target** ecology under the arm's
exact `verify_candidate` (rule 36 over the six interventions, rule 40 ≥ 1 fx over the target's best
constant, rule 42 raw and atrophied, atrophy under all six with floor `max(θ, bc + fx)`, and
`carrier_atrophied == "DENSE"`). Receipt: `STAGE_B6_DENSE_INHERITANCE_CONTROL_billy.json`, script
`gmi_microscope/b6_dense_inheritance_control.py`.

| source → target | seed | DENSE cells | admissible on target | source's own best DENSE cap | failure mode |
|---|---|---|---|---|---|
| `E_smooth1` → `E_smooth3` | 0 | 9 | **0** | 0.8333 | rule 36 ×9 |
| `E_smooth1` → `E_smooth3` | 1 | 19 | **0** | 0.8958 | rule 36 ×19 |
| `E_smooth1` → `E_smooth3` | 2 | 10 | **0** | 0.8333 | rule 36 ×10 |
| `E_smooth3` → `E_sym5` | 0 | 10 | **0** | 0.8125 | rule 36 ×10 |
| `E_smooth3` → `E_sym5` | 1 | 16 | **0** | 0.9583 | rule 36 ×14, atrophies off DENSE ×2 |
| `E_smooth3` → `E_sym5` | 2 | 8 | **0** | 0.8125 | rule 36 ×8 |

**72 inherited coefficient machines tested, 0 admissible on the target.** Capability on the source does
not rescue them: the `E_smooth3` seed-1 archive holds a DENSE cell at 0.9583 on its own ecology and it
still fails rule 36 on `E_sym5`. So the admissible atrophied-DENSE machines the CONTINUED arms reached
were produced by the warm-started search, not carried over ready-made — consistent with their recorded
lineage (`origin = ["seed", k]`, first placed at evaluations 18 595 and 3 827, i.e. descendants).

Two of the 72 pass every capability control and then **atrophy off DENSE** onto PROGRAM and TABLE. That
is rule 23 operating exactly as `RV-377-074` says it must: the raw descriptor mis-credits the carrier,
and reading the class on the atrophied genotype removes the credit. It is the same effect that separates
lane B's raw 4/9 from its atrophied 0/9, observed here on independent material.

This control constrains, and does not establish, Z1–Z3: it removes the inheritance explanation. Whether
the lift is specific to structured history (Z3) or belongs to any developed archive still depends on the
TWIN arms, which are unrun on seeds 1 and 2.
