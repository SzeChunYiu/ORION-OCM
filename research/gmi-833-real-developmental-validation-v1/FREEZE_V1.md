# GMI #833 — real-system validation of update-law and developmental predictions,
# and derived operator-invention / library-formation conditions — FREEZE

**Package:** `gmi-833-real-developmental-validation-v1`
**Issue:** #833. **Worktree branch:** `research/833-real-l`.
**`source_main`:** `91cff402303be751e464eb8a8001d2258d0e05a2`
**Claim ceiling (pre-committed, may not be widened by any later file):**
`GMI_833_REAL_SYSTEM_UPDATE_LAW_AND_DEVELOPMENTAL_VALIDATION_AND_DERIVED_INVENTION_LIBRARY_CONDITIONS_AT_REGISTERED_SCOPE`

**Custody.** This file is the complete pre-outcome prediction artifact. It is
committed and pushed **before any implementation file of this package exists**.
Every executor, oracle, test, receipt, workflow and `REAL_RUNS/` artifact is
created only in descendant commits. CI pins this freeze commit and asserts that
none of those paths is reachable from it.

---

## 0. The EXACT issue rows this tranche may reconcile

Verbatim from the live #833 body at `source_main` (fetched with
`gh issue view 833 --repo SzeChunYiu/ORION-OCM --json body -q .body`):

Under anchor `# I. Learning-law derivation without algorithm priors`:

```
- [ ] Test on realistic learning systems.
```

Under anchor `# L. Development, morphogenesis, and evolvability`:

```
- [ ] Derive operator invention.
- [ ] Derive library formation.
- [ ] Validate developmental predictions on continual-learning systems.
```

**No neighboring row is earned here.** In particular this tranche claims **no**
part of, and must not be read as touching:

- `- [ ] Derive representation changes that reduce future search cost.` (PR #1019)
- `- [ ] Compare mutation, local search, GP/CGP, evolutionary, gradient, NAS-like, and meta-search dynamics.` (PR #1019)
- `- [ ] Test whether P4 recursive grammar growth discovers mechanisms absent from `G0`.` (PR #1019)
- `- [ ] Predict evolvability on genuinely future task families.` — its obstruction is
  **custody**: futurity cannot be manufactured in-session. Deliberately left open.
- `- [ ] Derive developmental phase transitions.`, `- [ ] Derive path dependence and hysteresis.`,
  `- [ ] Derive conditions for escaping local developmental traps.`,
  `- [ ] Prove/measure reachability mass for predicted morphologies.` (#910 / PR #924)
- every remaining Section I row (#1014 / PR #1018 own them).

### 0.1 Record correction carried into this freeze

A tranche brief asserted that `Derive operator invention.` and
`Derive library formation.` were already closed citing #897. That is **wrong**.
`research/gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V2.json`
carries anchor `# E. Universal architecture-neutral machine grammar` for all three
of its replacements and never targeted a Section L row. #897 owns the Section E
row `Implement recursive library formation / primitive invention.`; the two
Section L rows above are unchecked at `source_main` and unclaimed. PR #1019's
`FREEZE_V1.md` §0.1 records the same correction, and its forbidden promotion #10
reads `"No claim on 'Derive operator invention.' or 'Derive library formation.'"`.

---

## 1. Parent pins (path + blob sha at the commit actually read)

| parent | ref | path | blob sha |
|---|---|---|---|
| #897 grammar growth theorems (T3 burden identity, INV-1, kappa ablation, `RECURSIVE_LIBRARY_CYCLE`) | `origin/main` | `research/gmi-833-g0-grammar-growth-v1/GRAMMAR_GROWTH_THEOREMS_V1.md` | `098aec5e60e4205aa9ebaa8206c58dc38206cf69` |
| #909/#908 developmental potential (DP-1, EV-1, HIST-1, CAPITAL-1) | `origin/main` | `research/gmi-833-developmental-potential-evolvability-v1/DEVELOPMENTAL_POTENTIAL_THEOREMS_V1.md` | `5588d7b490b3bf5bffa9f452a8cab5a260985162` |
| #903 real-system receipt protocol (the bar this package must clear) | `origin/main` | `research/gmi-833-real-transition-receipts-v1/FREEZE_V1.md` | `43497544080d3dc63492a22cd035ba795fbec7c9` |
| #837 foundation schema (result required fields, EV/M ladders) | `origin/main` | `research/gmi-833-foundation-v1/FOUNDATION_SCHEMA_V1.json` | `8a956962c4127f50f7533b0a615bd404479264c5` |
| #1018 update-law regimes freeze (`beta*`, `chi*`, `pistar*`, `tau*`, UL-11) | `origin/research/833-i-rest` @ `a51e30bed97d30217074b968976e8b70b9eac183` | `research/gmi-833-update-law-regimes-v1/FREEZE_V1.md` | `15adc55205c49f85ec9650084ae4317383fe65b5` |
| #1018 executor (the accounting function `tuple_vector`, `select`) | same | `research/gmi-833-update-law-regimes-v1/update_law_regimes_v1.py` | `a5ae95b27a5de1e0508ab61330e5f54a886c8a3b` |
| #1019 developmental reuse theorems (REP-1/REP-2 — **concurrent prior art, disclosed, not depended on**) | `origin/research/833-l-dev` @ `cfd18a5145f6a2f699867932496bcf81a373f05b` | `research/gmi-833-developmental-reuse-v1/DEVELOPMENTAL_REUSE_THEOREMS_V1.md` | `a34c3ec337f90fbdfd36029e1c86d680b9ffa012` |

#1018 and #1019 are **unmerged branches**. Section 4's derivation is stated so
that it rests only on `origin/main` parents (#897 T3); #1019 is cited as
concurrent prior art whose overlap is disclosed in §4.1 and on which no step of
§4 depends. Section 2 deliberately *does* depend on #1018's frozen selector,
because the row is a test of that selector; the pins above make the exact text
used recoverable if #1018 moves.

---

## 2. Section I — `Test on realistic learning systems.`

### 2.0 What #1018 pre-committed, quoted

`research/gmi-833-update-law-regimes-v1/FREEZE_V1.md` §0:

> **Pre-committed abstention.** `Test on realistic learning systems` is expected to
> remain OPEN. It is listed above only because it is in this tranche's scope; the
> rule pre-committed here is: **it closes only on real trained systems with
> sha256-bound real data sources and predictions frozen before outcomes, following
> `research/gmi-833-real-transition-receipts-v1` (#903). Synthetic data may not
> close it.**

`REAL_SYSTEM_VALIDATION` is entry 12 of #1018's `forbidden_promotions[]` — a
forbidden promotion **for #1018**, which did not reach real systems. This package
does reach them and therefore claims exactly, and only, what #1018's own rule
licenses.

### 2.1 Disclosure made BEFORE any outcome: UL-11's known held-out MISS

Predictions below come from **UL-11 as frozen by #1018**, never from
`select_v2`. #1018 records, on its own synthetic held-out set, that UL-11's
`HO-P2` verdict is a **MISS with 260 mismatches, 260/260 attributed, 0
unattributed**, and that `select_v2` is a disclosed post-freeze revival whose
794/0 score is **not** UL-11's. A low real-system hit rate here is therefore an
**anticipated** outcome. The row says *Test*, not *vindicate*: this package
earns it by executing the test honestly and reporting hits and misses exactly,
whatever they are. No threshold, price, ecology or selector may be changed after
an outcome is seen; a miss is attributed to one stage and, if revived, re-tested
against a **newly frozen** held-out registry, never against the one that
revealed the problem.

### 2.2 Inherited structural limitations, disclosed pre-outcome

1. **`SIG-S` loss is invariant to the `mut` coordinate.** In #1018's accounting
   the emitted predictor does not read `mut`, so `a_{SIG-S}` equals `a_{BASE-0}`
   in every coordinate except `p_mut`, where it is strictly larger, and
   `s* = 0` identically. This package reproduces that accounting faithfully.
   Where UL-11 returns `SIG-S` below it is because `BASE-0` is not one of the
   seven ranked signatures — it is **not** evidence that self-modification pays.
   `SIG-S` is never counted as a predicted-negative earned from ecology.
2. **`tau*`'s `r = 0` converse fires on five of six ecologies** because the
   registered target rule is realized by no candidate, so `H' = H`. That is the
   faithful #1018 definition (its D3 behaves the same way). `tau* > 0` is
   exercised on exactly one ecology (X5), where the target *is* a candidate.
3. **`cover` is measured here, not hardcoded.** #1018 hardcodes `cover = 2*T`.
   This package measures `cover = 2 * |covered training instances|` and records
   `compression_strict = (Dmin < cover)` per ecology. X4 is registered
   `chi*`-inadmissible in advance (`Dmin` undefined, `compression_strict` false).
4. **`disc*` / `psi*`** (rule induction) are not instantiated here; `SIG-R`'s
   competitiveness is exercised only through UL-11's argmin.

### 2.3 Registered real data sources (sha256-bound)

Every ecology is bound to a real byte source on the execution host
(laptop-billy, python3 3.8.10, torch 2.4.1+cpu). Bits are the raw file bytes,
MSB-first. A file the package generated is not a real source and none is used.

| id | primary source | sha256 (recorded at freeze) | pre-registered fallback |
|---|---|---|---|
| X1 | Project Gutenberg ebook 1342 (`https://www.gutenberg.org/files/1342/1342-0.txt`, fetched to `~/ocm-scratch/real-l/sources/g1342.txt`) | `81300b79e8a8d65ac530a97578417d06137e3bbc90622a10a65e5036183d2500` | `/usr/share/dict/american-english` |
| X2 | `/usr/share/sounds/alsa/Noise.wav` | `0d897df3862192ea078efc1dd8fdc4f51fae9e93d3ed4c15e049829b0386729e` | `/usr/share/sounds/alsa/Rear_Left.wav` |
| X3 | `/usr/lib/python3.8/json/__init__.py` | `41c4abb6840b6eeca85e7ea5e9b08bba71dc529725a415cc826ca940be4c79b2` | `/usr/lib/python3.8/ast.py` |
| X4 | `/usr/share/dict/american-english` | `f6c94d35691b9c356f7e5072f94d23f127b168cf9b04f0f5b26e0cb1f6ef4414` | `/usr/share/dict/swedish` |
| X5 | Project Gutenberg ebook 84 (`https://www.gutenberg.org/files/84/84-0.txt`, fetched to `~/ocm-scratch/real-l/sources/g84.txt`) | `06c37d2c52d208d3d81eb12c3b10b5edbd7728b73554325ddceadbe2fb427e77` | `~/ocm-scratch/real-l/sources/g2701.txt` (Gutenberg 2701) |
| X6 | `/usr/bin/python3.8` (ELF) | `298a9e830ed52f36c299427565485d717d1ce0179c0597cc16560513eb780b06` | `/usr/bin/git` |

### 2.4 Registered ecology shape

`M = 9` candidates (candidate `i` predicts `b[z-(i+1)]`, `i = 0..8`);
`T = 64` training positions and `nq = 64` held-out query positions per episode;
`K = 4` episodes taken as consecutive disjoint blocks of the real stream;
`k0 = 1`; ascent-start order `STARTS = (4,5,6,7,3,8,2,1,0)`; breadth grid
`1..9`; neighbour relation `i ~ j iff |i-j| = 1`, `max_degree = 2`;
`Vfun(i)` = exact rational training accuracy of candidate `i` on the real bits;
`Vloc` = score of the terminal reached by breadth-1 ascent from `STARTS[0]`;
`Vglob` = global registered score; `Bmin` = least breadth whose start prefix
reaches `Vglob`; `Tsteps` = ascent step count (floored at 1).

**Target rule.** Following #903, the *data* is real and the *rule* is the
registered intervention: `y_z = rule(b[z-o] : o in offsets)`. Retrieval
`retr` maps each query to the most recent training position with the same
`ctxk`-bit real context (last training index if none). Production space `RS`:
all 1-, 2- and 3-offset patterns over the registered offset set with
`len = |O| + 2`; `Dmin` = least total `len` over consistent covering subsets of
size `<= 3`; `disc = |RS| * T`. `Dmin_L = max(1, Dmin - (Hocc*Delta - Kdef))`.

| id | rule(offsets) | eps | ctxk | RS offsets |
|---|---|---|---|---|
| X1 | `AND(1,2)` | `3/8` | 3 | `(1,2,3,4)` |
| X2 | `AND(1,2)` | `3/8` | 3 | `(1,2,3,4)` |
| X3 | `OR(1,2)` | `7/16` | 4 | `(1,2,3,4)` |
| X4 | `MAJ(1,2,3)` | `7/16` | 4 | `(1,2,3,4)` |
| X5 | `COPY(2)` | `1/4` | 3 | `(1,2)` |
| X6 | `OR(2,4)` | `1/4` | 5 | `(1,2,3,4)` |

### 2.5 FROZEN invariants derived from the real sources

Derived pre-freeze by `derive_ecologies_v1.py`,
sha256 `75e83500817b9ccf2ccf34d9cfb2b717be5db3d29357d48275702911677041a9`
(kept off-repo; recorded here so a later divergence separates mis-transcription
from a changed derivation). The committed executor must reproduce this table
**exactly** from the sha256-bound sources; CI asserts it and the package fails
closed otherwise.

| id | `Mprime` | `r` | `mu` | `Dmin` | `Dmin_L` | `cover` | `|RS|` | `Bmin` | `Tsteps` | `alpha_gain` | `target_in_H` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| X1 | 9 | 0 | 7 | 10 | 1 | 128 | 128 | 7 | 1 | 10 | false |
| X2 | 9 | 0 | 8 | 10 | 1 | 128 | 128 | 5 | 1 | 6 | false |
| X3 | 9 | 0 | 14 | 10 | 1 | 128 | 128 | 7 | 1 | 0 | false |
| X4 | 9 | 0 | 15 | — | — | 96 | 128 | 5 | 1 | 15 | false |
| X5 | 1 | 8 | 7 | 6 | 1 | 128 | 16 | 7 | 1 | 0 | true |
| X6 | 9 | 0 | 6 | 10 | 1 | 128 | 128 | 1 | 1 | 0 | false |

### 2.6 FROZEN threshold values

`beta* = alpha_gain/((M-1)T)`; `chi*` = the exact rational root of
`<a_X - a_R, pi> = 0` in `p_store` with every other price at the unit
numeraire; `pistar* = (Vglob-Vloc)/((Bmin-1)Tsteps)`, `0` when the denominator
vanishes; `tau* = r*T*(K-k0)/(|H'|K)`.

| id | `beta*` | `chi*` | `pistar*` | `tau*` | `Vglob` | `Vloc` | `compression_strict` |
|---|---|---|---|---|---|---|---|
| X1 | `5/256` | `16787/896` | `1/192` | `0` | `45/64` | `43/64` | true |
| X2 | `3/256` | `4165/256` | `5/256` | `0` | `51/64` | `23/32` | true |
| X3 | `0` | `1135/128` | `11/384` | `0` | `47/64` | `9/16` | true |
| X4 | `15/512` | — (`UNDETERMINED_NO_CONSISTENT_COVER`) | `1/32` | `0` | `49/64` | `41/64` | false |
| X5 | `0` | `1931/896` | `7/128` | `384` | `1` | `43/64` | true |
| X6 | `0` | `4229/192` | `0` | `0` | `7/8` | `7/8` | true |

Both sides are exercised by construction: `beta* > 0` on X1/X2/X4 and the
`alpha_gain <= 0` converse fires on X3/X5/X6; `pistar* > 0` on X1..X5 and the
`Bmin = 1` degenerate converse on X6; `tau* > 0` on X5 only and the `r = 0`
converse on the other five; `chi*` defined on five and typed-undetermined on X4.

### 2.7 FROZEN UL-11 predictions (the pre-outcome labels)

UL-11 is applied exactly as #1018 froze it: five steps, seven ranked signatures
`{SIG-W, SIG-X, SIG-R, SIG-L, SIG-P, SIG-T, SIG-S}`, strict argmin of
`<a_i, pi>`, three typed abstentions and no fourth, no tie-break into a regime.

Registered anchored price vectors over `(p_test, p_carry, p_store, p_build,
p_branch, p_meta, p_mut, lam)`; unlisted coordinates are `1`:

- `A1-unit` — all 1.
- `A2-carry-cheap` — `p_carry = 1/256`; `p_store, p_build, p_branch, p_meta, p_mut, lam = 256`.
- `A3-store-cheap` — `p_store = 1/256`; `p_carry, p_build, p_branch, p_meta, p_mut, lam = 256`.
- `A4-build-cheap` — `p_build = 1/256`, `p_test = 1/4096`; `p_carry, p_store, p_branch, p_meta, p_mut, lam = 256`.
- `A5-branch-cheap` — `p_branch = 1/256`; `p_carry, p_store, p_build, p_meta, p_mut, lam = 256`.
- `A6-meta-cheap` — `p_meta = 1/256`; `p_carry, p_store, p_build, p_branch, p_mut, lam = 256`.
- `A7-mut-cheap` — `p_mut = 1/256`; `p_carry, p_store, p_build, p_branch, p_meta, lam = 256`.
- `A8-loss-dominant` — `lam = 4096`, all structural coordinates 1.

**The 48 frozen labels.** `ABS` = `ABSTAIN_UNDERDETERMINED` with
`missing = coefficients:SIG-R`.

| id | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 |
|---|---|---|---|---|---|---|---|---|
| X1 | SIG-S | SIG-W | SIG-X | SIG-L | SIG-P | SIG-P | SIG-P | SIG-X |
| X2 | SIG-S | SIG-W | SIG-X | SIG-L | SIG-P | SIG-P | SIG-P | SIG-X |
| X3 | SIG-S | SIG-W | SIG-X | SIG-L | SIG-P | SIG-P | SIG-P | SIG-X |
| X4 | ABS | ABS | ABS | ABS | ABS | ABS | ABS | ABS |
| X5 | SIG-T | SIG-T | SIG-X | SIG-L | SIG-L | SIG-L | SIG-L | SIG-T |
| X6 | SIG-S | SIG-W | SIG-X | SIG-L | SIG-P | SIG-P | SIG-P | SIG-X |

Six distinct predicted families plus a typed abstention. The predicted-negative
side is equally frozen: `SIG-W` is predicted **never** to win on X3/X5/X6 at any
positive price (`beta* <= 0`), `SIG-T` never on X1/X2/X3/X4/X6 (`tau* = 0`), and
`SIG-R` never anywhere (dominated by `SIG-L` at equal loss and lower `p_build`).

### 2.8 FROZEN analytic coefficient vectors

Order `(p_test, p_carry, p_store, p_build, p_branch, p_meta, p_mut, lam)`.
The eighth coordinate is the analytic law's exact integer held-out error count.

```
X1 SIG-W [2560,2304,0,0,0,0,0,6]      SIG-X [2048,0,1792,0,0,0,0,2]
   SIG-R [35584,0,0,40,0,0,0,0]       SIG-L [33280,0,0,4,0,0,0,0]
   SIG-P [11008,0,0,0,24,0,0,16]      SIG-T [2560,256,0,0,0,36,0,16]
   SIG-S [2560,256,0,0,0,0,4,16]      BASE-0 [2560,256,0,0,0,0,0,16]  NULL-0 [1792,0,0,0,0,0,0,21]
X2 SIG-W [2560,2304,0,0,0,0,0,10]     SIG-X [2304,0,2048,0,0,0,0,0]
   SIG-R [35584,0,0,40,0,0,0,0]       SIG-L [33280,0,0,4,0,0,0,0]
   SIG-P [7936,0,0,0,16,0,0,16]       SIG-T [2560,256,0,0,0,36,0,16]
   SIG-S [2560,256,0,0,0,0,4,16]      BASE-0 [2560,256,0,0,0,0,0,16]  NULL-0 [1792,0,0,0,0,0,0,22]
X3 SIG-W [2560,2304,0,0,0,0,0,18]     SIG-X [3840,0,3584,0,0,0,0,4]
   SIG-R [35584,0,0,40,0,0,0,0]       SIG-L [33280,0,0,4,0,0,0,0]
   SIG-P [11008,0,0,0,24,0,0,18]      SIG-T [2560,256,0,0,0,36,0,18]
   SIG-S [2560,256,0,0,0,0,4,18]      BASE-0 [2560,256,0,0,0,0,0,18]  NULL-0 [1792,0,0,0,0,0,0,38]
X4 SIG-W [2560,2304,0,0,0,0,0,0]      SIG-X [4096,0,3840,0,0,0,0,0]
   SIG-R null                         SIG-L null
   SIG-P [7936,0,0,0,16,0,0,16]       SIG-T [2560,256,0,0,0,36,0,15]
   SIG-S [2560,256,0,0,0,0,4,15]      BASE-0 [2560,256,0,0,0,0,0,15]  NULL-0 [1792,0,0,0,0,0,0,26]
X5 SIG-W [2560,2304,0,0,0,0,0,0]      SIG-X [2048,0,1792,0,0,0,0,2]
   SIG-R [5888,0,0,24,0,0,0,0]        SIG-L [4608,0,0,4,0,0,0,0]
   SIG-P [11008,0,0,0,24,0,0,0]       SIG-T [1024,256,0,0,0,4,0,0]
   SIG-S [2560,256,0,0,0,0,4,0]       BASE-0 [2560,256,0,0,0,0,0,0]   NULL-0 [1792,0,0,0,0,0,0,29]
X6 SIG-W [2560,2304,0,0,0,0,0,1]      SIG-X [1792,0,1536,0,0,0,0,0]
   SIG-R [35584,0,0,40,0,0,0,0]       SIG-L [33280,0,0,4,0,0,0,0]
   SIG-P [3328,0,0,0,4,0,0,1]         SIG-T [2560,256,0,0,0,36,0,1]
   SIG-S [2560,256,0,0,0,0,4,1]       BASE-0 [2560,256,0,0,0,0,0,1]   NULL-0 [1792,0,0,0,0,0,0,3]
```

### 2.9 The real trained systems and the observed side

For each ecology, seven **real trained systems** are built on the same
sha256-bound real stream, one realizing each signature. Registered
realizations, registered seeds `{s, s+1000}` per system, median held-out error
count across seeds scored, seed spread recorded:

- `SIG-W` — real torch ensemble: `M` one-hidden-layer MLPs (width 8, ReLU,
  sigmoid), one per delay feature, plus a trainable mixture logit vector; Adam
  `lr = 0.01`, 3 passes over the train stream in chunks of 16; emits the
  mixture-weighted majority.
- `BASE-0` — a single real MLP on the argmax-selected delay feature (same
  optimizer/budget). Recorded, not ranked.
- `NULL-0` — the single registered incumbent candidate. Recorded, not ranked.
- `SIG-X` — real exemplar learner: stores the retrieved training instances and
  emits the retrieved label (non-parametric, fitted to the real train stream).
- `SIG-R` — real rule induction: exhaustive search of the registered `RS` for a
  minimum-description consistent cover of size `<= 3` on the real train stream.
- `SIG-L` — the same search with the library-compressed description length.
- `SIG-P` — real population search: `Bmin` (at least 2) MLPs trained by
  mutation + selection only, no gradients, registered mutation scale and budget.
- `SIG-T` — real meta-learner: one MLP body carried across the `K` real
  episodes with a per-episode head, restricted to the registered `H'` index set.
- `SIG-S` — real self-modifying learner: `BASE-0`'s body with a registered
  successor-set change applied between episodes.

**Measured, as exact integers:** evaluations performed, candidate-indexed slots
carried x steps, instances stored x steps, description symbols constructed,
additional parallel candidates x steps, cross-episode slots x episodes, changes
of the admissible successor set, and the **held-out 0/1 error count** on the
protected query stream. No float enters any claim; training uses floats
internally exactly as #903's did.

**Scoring is blind.** Observed charge `<a_obs, pi>` is computed over opaque
candidate IDs; the argmin stage never sees a family name. Ties return
`ABSTAIN_TIE` and the cell is recorded as non-identifying, never resolved.

### 2.10 Closure condition (fail-closed)

The row `- [ ] Test on realistic learning systems.` is earned iff:
1. all six ecologies are instantiated from their registered primary or
   pre-registered fallback source, with sha256 recorded at run time;
2. the committed executor reproduces §2.5–§2.8 **exactly** from those sources;
3. all seven real systems train and are measured on every non-abstaining
   ecology, with no unregistered substitution;
4. every (ecology, price) cell yields a recorded verdict in
   `{HIT, MISS, ABSTAIN_MATCHED, ABSTAIN_UNMATCHED, TIE_NONIDENTIFYING}`;
5. the frozen abstention cells (X4, all eight prices) are observed to abstain
   for the registered reason.

The row is earned by **executing the test**, not by any hit-rate threshold.
The hit count is reported as measured. If fewer than six ecologies qualify the
terminal is `INSUFFICIENT_REAL_ECOLOGY_EVIDENCE` and the row stays open.

---

## 3. Section L — `Validate developmental predictions on continual-learning systems.`

### 3.1 What continual learning means here

A **real** system trained on a **sequence** of real tasks, where the
developmental prediction concerns what happens **across** the sequence. Eight
registered sequences; each is `K_seq = 4` tasks trained in order on a
sha256-bound real bit stream, the network body carried across tasks and the
readout re-initialized per task.

| id | real source | sha256 | sequence family | held-out discovery task `U` | predicted |
|---|---|---|---|---|---|
| S1 | Gutenberg 1342 | `81300b79…d2500` | POS: delays `(1,2,3,4)` | `AND(1,2)` | history improves |
| S2 | `Noise.wav` | `0d897df3…6729e` | POS: delays `(1,2,3,4)` | `OR(1,2)` | history improves |
| S3 | `/usr/lib/python3.8/json/__init__.py` | `41c4abb6…c79b2` | POS: delays `(1,2,3,4)` | `AND(1,3)` | history improves |
| S4 | `/usr/share/dict/american-english` | `f6c94d35…f4414` | POS: delays `(1,2,3,4)` | `MAJ(1,2,3)` | history improves |
| S5 | Gutenberg 84 | `06c37d2c…27e77` | POS: delays `(1,2,3,4)` | `OR(1,3)` | history improves |
| S6 | `/usr/bin/python3.8` | `298a9e83…780b06` | NEG: delays `(12,13,14,15)` | `AND(1,2)` | history does NOT improve |
| S7 | `/usr/share/sounds/alsa/Rear_Left.wav` | recorded at run time | NEG: delays `(12,13,14,15)` | `OR(1,2)` | history does NOT improve |
| S8 | `/usr/share/dict/swedish` | recorded at run time | NEG: constant-label tasks | `AND(1,2)` | history does NOT improve |

The NEG sequences are the licensed band's other side, exactly as #903 registered
three systems predicted **not** to transition: their task sequences are
structurally unrelated to `U` (features drawn from delays the discovery task
never reads, or degenerate constant tasks), so a history-conditioned proposal
law should carry no advantage.

### 3.2 The registered HIST-1 instantiation

Symbols follow the delivered #909/#908 theorem note (`a` in the note, `h` in the
freeze/reconciliation form; identical scalar):

- a **proposal** = one registered fine-tuning run on `U`: `B_prop = 300`
  optimizer steps from a drawn initialization, then evaluation on the protected
  20% split of `U`;
- `Q0` (baseline law) = body re-initialized from scratch at the drawn seed;
- `QH` (history law) = body initialized from the sequence-trained weights, head
  re-initialized at the same drawn seed;
- `U` = the success set: held-out error count `<= theta * N_eval` with registered
  `theta = 1/4`;
- `N = 24` registered proposal seeds per law per sequence; `p0` and `pH` are
  exact `Fraction(successes, 24)`;
- registered price vector `pi`: 1 per optimizer step. Hence `c = pi . r = 300`
  exactly, and `h` is the priced history-policy overhead;
- two registered overhead regimes, frozen before any run:
  `h_low = 0` and `h_high = 4 * K_seq * B_prop = 4800` (the full priced cost of
  building the sequence-trained body).

### 3.3 The CAPITAL-1 assay, designed before the freeze

`CAPITAL-1` is load-bearing: a system that merely **stores** earlier solutions
is not demonstrating search-policy improvement. The assay is #909/#908's exact
2x2 on two orthogonal booleans, with the `stored ∩ U` test **measured on the
real system**:

- `stored_set` = the `K_seq` final per-task parameter vectors of the sequence;
- each stored solution is evaluated **directly, with no further training**, on
  the protected split of `U`; `solution_capital = true` iff any reaches the
  success criterion;
- `law_changed = (QH != Q0)` holds structurally (different initialization law).

If `solution_capital` is true the cell returns
`CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION` and contributes **no** evidence
— the disjointness premise has failed and the sequence is rejected, not
reinterpreted. Only `stored ∩ U = empty` plus `law_changed` plus
`HISTORY_STRICTLY_IMPROVES` yields `SEARCH_POLICY_CAPITAL`.

### 3.4 The frozen predictions

- **CL-P1 (direction).** On every POS sequence, `pH > p0` strictly. On every NEG
  sequence, `pH <= p0`.
- **CL-P2 (HIST-1 at `h_low = 0`).** POS: verdict `HISTORY_STRICTLY_IMPROVES`
  (`0 + 300/pH < 300/p0`). NEG: verdict in `{TIE, HISTORY_HARMS,
  BOTH_UNREACHABLE}` — **not** `HISTORY_STRICTLY_IMPROVES`.
- **CL-P3 (overhead flip at `h_high = 4800`).** On every POS sequence the
  verdict is **not** `HISTORY_STRICTLY_IMPROVES` once the full policy overhead is
  charged. This is the both-sides demonstration on the same real system: the
  same measured masses, two registered prices, opposite verdicts. (The boundary
  is `h* = 300/p0 - 300/pH`; the prediction is `h* < 4800`.)
- **CL-P4 (CAPITAL-1).** On every POS sequence `stored ∩ U = empty` (no stored
  solution reaches criterion on `U` without training) and the classification is
  `SEARCH_POLICY_CAPITAL` at `h_low`.
- **CL-P5 (DP-1 non-identification).** At zero further development both laws'
  draws are below criterion on `U`, so `C_now` is matched at `0`; yet
  `C_pot(B_prop)` differs, i.e. `H_dev^H(B_prop) > H_dev^0(B_prop)` on every POS
  sequence and not on any NEG sequence. Equal current capability, different
  potential — measured on a real system.
- **CL-P6 (EV-1A first-hit burden).** With `p = pH > 0`, the measured mean
  one-indexed first-hit index over the registered proposal order lies in the
  registered band `[1/p - 2*sqrt((1-p)/p^2), 1/p + 2*sqrt((1-p)/p^2)]`,
  evaluated in exact rational arithmetic by comparing squares. `p = 0` returns
  the exact terminal `UNREACHABLE_ZERO_USEFUL_MASS`, never a finite number.
- **CL-P7 (EV-1 typing).** `Ev_Q(U) = Q(U)` is reported as an exact `Fraction`
  and never as a float, and is kept a distinct typed object from `C_now`,
  `C_pot` and `stored_set`.

### 3.5 Closure condition (fail-closed)

The row is earned iff all eight sequences run on their registered real sources,
every prediction CL-P1..CL-P7 is recorded as HIT or MISS with exact numbers, at
least five POS sequences pass the CAPITAL-1 disjointness gate, and every NEG
sequence's predicted non-improvement is checked. Misses are reported, attributed
to one stage, and never repaired by editing this freeze.

---

## 4. Section L — `Derive operator invention.` and `Derive library formation.`

### 4.1 Parent ownership and the exact residual

**#897 (merged, on main) owns the built mechanism.** Its `INV-1` implements
deterministic corpus-only invention with admission gain
`gain = o(b-1) - b - kappa > 0`, forms `m1 -> a b` (11 occurrences, gain 8 at
`kappa = 1`) then `m2 -> m1 m1` (4 occurrences, gain 1), charges
`K_total(L) = sum_{m in L} (|body_m| + kappa)`, stops by saturation at derived
depth `D_reg = S_0 = 23`, derives `kappa = 1` by ablation over `{0..8}`, and
measures held-out burden `50,052 -> 1,307` (net `-48,739`) with a preserved
control regression `+1,178` and `0/200` nulls. It reconciles **Section E**
rows; its verb is *Implement*.

**#1019 (unmerged, disclosed prior art) owns the representation-change
criterion.** `REP-1` is the rank-free band on `Phi(n,l) = sum_{j=1..l} n^j`:
`GUARANTEED_REDUCTION iff Phi(n',l1) <= Phi(n,l0-1)`,
`GUARANTEED_INCREASE iff Phi(n',l1-1) >= Phi(n,l0)`, else `RANK_DECIDED`;
`REP-2` adds the portfolio net with `K_total(L)` charged. Both compare
`G1 = G0 u L` against `G0`.

**The residual claimed here, stated so it cannot be confused with either:**

1. #897 measured that a library helps. It did **not** derive the condition under
   which admitting an operator pays, nor whether its corpus-symbol admission
   rule agrees with the burden frame at all. §4.3 derives that condition and
   maps where the two frames **disagree**.
2. #1019 compares **library against no library**. It never compares **one shared
   library of `k` members against `k` separate single-member grammars**. That is
   precisely what `Derive library formation.` asks — *"when does accumulating a
   set of reusable operators beat keeping them separate, including the
   interaction between members"* — and it is the comparison
   `Phi(n+k, l_L)` versus `Phi(n+1, l_j)`, disjoint from `Phi(n',l1)` versus
   `Phi(n,l0)`.
3. Under #897's own charge `K_total(L)`, the maintenance charge is **identical**
   in both regimes (same members, same bodies), so it cancels. Library formation
   versus separate keeps is therefore a **charge-free** decision — exactly where
   `REP-2`, in which `K_total` is decisive, has nothing to say.

No step of §4 depends on #1019. The burden identity used is #897's `T3`
(`B_G(w) = Phi(n, l*-1) + rank + 1`, `rank in [0, n^{l*}-1]`), which is on
`origin/main`.

### 4.2 Registered setting (inside the #837 realization contract)

Alphabet `A` with `n = |A| >= 2`; `Phi(n,l) = sum_{j=1..l} n^j`, `Phi(n,0) = 0`;
`l*_G(w)` the minimal program length for target `w` under grammar `G`;
`B_G(w)` the breadth-by-length discovery burden. Charges are carried in the
14-coordinate lifecycle vector (`search_discovery`, `build_acquisition`,
`maintenance`) and scalarized only by a **prospectively frozen** price vector,
per foundation `R-1`/`R-2`. Every statement carries a `forall[D]` or
`forall_fin[U]` domain tag and the thirteen `result_required_fields` of
`FOUNDATION_SCHEMA_V1.json`. Evidence level EV1 (deductive) plus EV2 (exact
finite certificate). **Not EV3, EV4 or EV5** for §4.

### 4.3 Named results to be delivered (statements frozen here)

- **`OI-1` (invention affordance).** For a workload `T` of targets with exact
  rational weights, the exact charge threshold `Theta_inv(o)` below which
  admitting `o` strictly reduces total priced burden, in the `Phi` frame, with
  `o`'s discovery charge `D(o)` and maintenance `|body| + kappa` both charged.
- **`OI-2` (one-symbol compression is never guaranteed to pay).** For every
  `n >= 2` and `l >= 1`, `Phi(n+1, l-1) >= Phi(n, l-1)`; hence a compression of
  depth `gamma = 1` is **never** in the guaranteed-reduction band, whatever the
  charge. `forall[D]`.
- **`OI-3` (guaranteed-loss depth).** `L*(n) := min{ l : Phi(n+1,l-1) >= Phi(n,l) }`
  exists for every `n >= 2`, is computed exactly on the registered range, and is
  bracketed `n+2 <= L*(n) <= 1 + ceil(n(n^2-n+1)/(n-1))`. At depth `>= L*(n)` a
  `gamma = 1` admission strictly loses at **every** nonnegative charge — the
  matched converse.
- **`OI-4` (frame divergence, EARNED-BY-COUNTEREXAMPLE).** Explicit witnesses
  that #897's corpus-symbol admission rule `o(b-1) - b - kappa > 0` is **neither
  necessary nor sufficient** for burden reduction in the `Phi` frame, plus the
  exact structural side-condition that repairs it.
- **`LF-1` (library-versus-separate band).** The rank-free three-way verdict
  `LIBRARY_GUARANTEED_BETTER iff Phi(n+k, l_L) <= Phi(n+1, l_j - 1)`,
  `LIBRARY_GUARANTEED_WORSE iff Phi(n+k, l_L - 1) >= Phi(n+1, l_j)`, else
  `RANK_DECIDED`; bands proved mutually exclusive.
- **`LF-2` (charge neutrality).** Under `K_total(L) = sum_m (|body_m| + kappa)`
  the maintenance charge of the shared library equals that of the `k` separate
  single-member grammars, so `LF-1` decides the row **without any charge term**.
- **`LF-3` (no-composition converse).** If the composition gain
  `gamma_w = l_j(w) - l_L(w)` is `0` for every `w` then, for `k >= 2`, both
  endpoints of the library band strictly exceed the corresponding endpoints of
  the separate band and the exact same-rank dilution tax is
  `Phi(n+k, l-1) - Phi(n+1, l-1) > 0`. **Library formation is not a search-charge
  phenomenon without member composition.**
- **`LF-4` (minimum composition depth).** `gamma*(n,k,l_j) :=
  min{ gamma : Phi(n+k, l_j-gamma) <= Phi(n+1, l_j-1) }`, computed exactly on
  the registered range, monotone in `k`, with `gamma* >= 2` always (by `LF-3`'s
  `gamma = 1` case) and `gamma*` undefined at `l_j = 2`.
- **`IND-1` / `IND-2` (independence).** Two explicit exact witnesses: a workload
  where invention pays and no library of `k >= 2` is favoured, and a workload
  where library formation is favoured over separate keeps while **no** further
  operator passes `OI-1`. Together they prove the two rows are logically
  independent.

### 4.4 Routes, hostiles, nulls

Route A computes every verdict from the closed-form integer comparisons above.
Route B is an independently written oracle that **enumerates** programs over the
explicit operator semantics, recomputes minimal lengths and frontier
cardinalities by brute force, and derives the same signs without importing
Route A. Registered hostiles the checker must DETECT: (H1) a `gamma = 0`
operator declared inventable; (H2) a `gamma = 0` library declared favoured;
(H3) the dilution off-by-one (`n` in place of `n+1`, or `n+1` in place of
`n+k`); (H4) an inadmissible compression `l' > l`; (H5) a cyclic library
dependency, which must return `RECURSIVE_LIBRARY_CYCLE` with the grammar
object unchanged. Registered null: a randomized sign predictor over the same
census, which the derived bracket must strictly beat (target `0/200`).

---

## 5. Forbidden promotions

```
REAL_SYSTEM_VALIDATION_BEYOND_REGISTERED_ECOLOGIES
FRONTIER_OR_LARGE_MODEL_VALIDATION
UL_11_VINDICATED
SELECT_V2_RESULTS_ATTRIBUTED_TO_UL_11
SELF_MODIFICATION_FAVOURED_BY_ECOLOGY
UNIVERSAL_BEST_UPDATE_LAW
SECTION_I_COMPLETE
CONTINUAL_LEARNING_GENERAL_CLAIM
OPEN_ENDED_EVOLVABILITY
FUTURE_TASK_FAMILY_PREDICTION
SOLUTION_CAPITAL_COUNTED_AS_SEARCH_POLICY_CAPITAL
REPRESENTATION_CHANGE_ROW_OWNED_HERE
SEARCH_DYNAMICS_COMPARISON_OWNED_HERE
P4_NOVELTY_ROW_OWNED_HERE
GRAMMAR_GROWTH_OWNED_HERE
LIBRARY_IMPLEMENTATION_NOVEL_HERE
INVENTION_MECHANISM_NOVEL_HERE
CONTINUOUS_OR_INFINITE_SCOPE
SECTION_L_COMPLETE
COMPLETE_GMI
```

## 6. Fail-closed semantics

Any unregistered substitution, any missing measurement, any float in a claimed
quantity, any tie resolved into a regime, any post-hoc edit of a frozen
threshold, label or prediction, or any stored-solution contamination of a
CAPITAL-1 cell rejects the affected receipt. Rows whose closure conditions are
not met are reported OPEN by name in `CORE.md` and in the reconciliation JSON's
`rows_not_closed`. A negative is diagnosed to one stage and revived against a
**newly frozen** registry, or delivered as a proven structural obstruction with
its counterexample, labelled EARNED-BY-COUNTEREXAMPLE.
