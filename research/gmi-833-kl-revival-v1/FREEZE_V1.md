# FREEZE_V1 — `gmi-833-kl-revival-v1`

Committed and pushed **before any implementation, population module, bridge
code, prediction stream, fetcher, training run, receipt, scorer, oracle or test
of this package exists**. `git log --reverse` over this directory must return
this commit first, carrying only `FREEZE_V1.md` and `FREEZE_ROWS_V1.json`.
`check_freeze_order_v1.py` will re-derive that in CI with a negative control
(the #976 `POST_HOC_SUSPECT` failure class).

- **`source_main`** = `f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`
  (`fix(#833): my gate scoping crashed the harness on an argument position (#1051)`).
- **Claim ceiling** =
  `GMI_833_KL_REVIVAL_SET_VALUED_BRIDGE_AND_POSTERIOR_DATED_FUTURITY_AT_REGISTERED_FINITE_SCOPE`.
- **Issue body fetch** pinned in `FREEZE_ROWS_V1.json` by sha256
  `d5cd0248ea2f7121d6ad52b0e0a07e832969134add95681ca36c1a6a85261fbd`
  (27,554 bytes) — byte-identical to the fetch the parent lane
  `gmi-833-body-residual-akl-v1` froze, so both rows are unchanged since.

## 1. The exact rows this tranche may reconcile

Two, and only two, pinned verbatim with per-row sha256 in `FREEZE_ROWS_V1.json`:

| id | anchor | `old` |
|---|---|---|
| `ROW_K` | `# K. Capability theory upgrade` | `- [ ] Test predictor on real trained systems.` |
| `ROW_L` | `# L. Development, morphogenesis, and evolvability` | `- [ ] Predict evolvability on genuinely future task families.` |

**No neighboring row is earned here.** No other row of sections K or L, and no
row of any other section, is in scope. This package **never edits the issue
body**; its only issue-facing artifact is
`ISSUE_833_RECONCILIATION_KL_REVIVAL_V1.json`.

## 2. Why this lane exists — the two attributions it inherits

`gmi-833-body-residual-akl-v1` (`BR-1`/`BR-2`/`BR-3`, `FC-1`/`FC-2`) left both
rows OPEN under rules fixed in advance, with good evidence:

- **K.** Under any bridge *truthful by construction* the parent predictor `F`
  emits **0 non-degenerate world-invariant points on 155,520 inputs** across the
  three real populations, while the same counter returns 1,680 / 3,408 / 3,472
  under the parent's registered law. The failing stage is the **bridge design**:
  a bridge that asserts nothing has no image; a bridge that asserts a total point
  law was falsified three times (19/32 → 28/32 → 26/32) and the parent's
  `FREEZE_V3_ADDENDUM` §6 terminal forbids a fourth fitted point law.
- **L.** 0 of 6 in-session candidates pass `FFA-1`; every tracked path is a
  repository blob. The failing stage is **custody of futurity**: futurity cannot
  be constructed in-session. The same lane named the lever: *a dated external
  source published after a frozen prediction qualifies.*

This lane applies exactly one lever per row and re-tests on **new** material.
**Neither of the parent lane's revealing sets is re-scored:** `SIGMA_REAL`,
`SIGMA_REAL2`, `SIGMA_REAL3` carry no part of row K's disposition here, and no
repository blob is a row-L candidate.

## 3. `ROW_K` — the set-valued bridge with typed abstention

### 3.1 Parents, and what is not touched

`gmi-833-capability-predictor-v1` (#1012) owns `F`, `survivor_mask`, `predict`,
`emit`, the four dispositions and the typed uncertainty constructors `U-1a
FeasibleSet` / `U-1b ConfidenceSet` (#851). **`F` is not modified, re-derived or
re-fitted.** The registered universe is substituted only through the parent
evaluation package's `install_universe`, which proves in-process that `F`'s code
is unchanged. `gmi-833-capability-predictor-evaluation-v1` owns the real-system
training protocol (`REAL_SOURCE`, `REAL_WORD_LEN = 12`, windows `(0,6000)` /
`(6000,8000)`, Adam `lr = 1/1000`, 400 epochs, batch 256, one thread, the seed
rule), the 99/100 band of `FREEZE_V3_ADDENDUM` §3, the external evaluator, and
the three receipts `REAL_MEASURED_V1/V2/V3.json`. **The protocol is reused
byte-for-byte; nothing about training changes.**

### 3.2 The bridge family `SB` (registered now)

A **set-valued bridge** assigns to each machine `m = (mech, size, w, h)` and each
head `j ∈ {0,1,2}` an **interval of admissible bands** `β_j(m)` over the
two-band lattice `UNSOLVED < SOLVED` (band boundary = the parent's registered
99/100 exact-accuracy band on the protected split). The three possible
intervals are `{UNSOLVED}`, `{SOLVED}` and the full interval
`{UNSOLVED, SOLVED}` — the last is a **typed abstention** for that head. The
admissible solved-bit set of `m` is the product `Adm(m) = ∏_j β_j(m)`, and its
admissible contract-value set is `V_c(m) = { cap_c(b) : b ∈ Adm(m) }` with
`cap_c(b) = Σ_{j verified by c, bit j of b} μ_j`, `μ = MU_REAL = (8/17, 6/17, 3/17)`.

`SB` contains the parent lane's `CB-PROTO` (every trained head abstains) and the
parent's point laws (no head abstains) as its two extremes. **The lever is the
middle:** commit where the evidence is unanimous, abstain where it is not.

### 3.3 The commitment rule `CR-1` (mechanical; derives the bridge from the receipts)

Input: the parent's three real receipts, read as (mech, size, w, task) → exact
trained accuracy and untrained accuracy. A head is *measured SOLVED* iff its
exact accuracy `>= 99/100`. Cells:

1. **Untrained head** (`bit j of h = 0`): `β_j = {UNSOLVED}` — the protocol
   clause of `CB-PROTO`, inherited; additionally required to be unanimous over
   every untrained head measured in the receipts (it is: 72 of 72 below the band,
   maximum `909/1000`).
2. **`T0` trained**, any mech, any size: commit `{SOLVED}` iff unanimous over
   `>= 4` measured heads spanning `>= 2` distinct widths; else abstain.
3. **`MLP`, `T1` / `T2` trained**: commit `{UNSOLVED}` under the same
   unanimity rule; else abstain.
4. **`GRU`, `T_j` trained (`j ∈ {1,2}`)**: let `s*_j` be the **smallest measured
   width** such that every measured `GRU` `T_j` head at width `>= s*_j` is
   SOLVED and those heads number `>= 4` across `>= 2` widths. If `s*_j` exists:
   `β_j = {SOLVED}` for `size >= s*_j` and `{UNSOLVED, SOLVED}` (abstain) for
   `size < s*_j`. If no such `s*_j` exists: abstain at every width.

Applied to the receipts at `source_main` the rule yields `SB-L*`:

| cell | evidence in V1–V3 receipts | `β` |
|---|---|---|
| any untrained head | 72/72 below band | `{UNSOLVED}` |
| `T0` trained | 24/24 SOLVED over widths 2,4,8,12,16,32 | `{SOLVED}` |
| `MLP` `T1` trained | 12/12 UNSOLVED (max `1259/2000`) | `{UNSOLVED}` |
| `MLP` `T2` trained | 12/12 UNSOLVED (max `769/1000`) | `{UNSOLVED}` |
| `GRU` `T1` trained, `size >= 12` | 6/6 SOLVED at 12, 16, 32 → `s*_1 = 12` | `{SOLVED}` |
| `GRU` `T1` trained, `size < 12` | 2/6 SOLVED at 2, 4, 8 | abstain |
| `GRU` `T2` trained, any size | `s*_2` undefined (`197/200` at `(16, w=1)`; only 2 heads at 32) | abstain |

The executor **re-derives this table from the receipts** and CI asserts
equality with the table above; the table is not hand-authored input.

**Relation to the parent's §6 terminal.** `SB-L*` is **not** a fourth
registration law: it is not total (it abstains on 3 of the 7 cell classes), it
is not fitted to the V1/V2/V3 counterexamples (it abstains exactly *where* they
occurred), and it takes the parent's terminal — *exact-band solvability is not a
function of the structural coordinates* — as a premise, committing only where
the receipts never disagreed. Whether its commitments hold is the prospective
question this lane asks, on a population none of the receipts contain.

### 3.4 The new population `SIGMA_REAL4` (registered now, never trained before)

Same machine shape as the parent: `mech ∈ {MLP, GRU}`, `w ∈ {0,1}`,
`h ∈ {1,3,5,7}`, **widths `REAL4_SIZES = (6, 48)`** — 6 lies in the abstention
band of `GRU T1` (between the measured 4 and 8) and 48 lies **beyond every
width ever trained** (32), so the `MLP T1/T2 = UNSOLVED` and `GRU T1 = SOLVED`
commitments are tested by extrapolation in the direction that could break them.
32 machines. Descriptor: `rho = (size, 1+w, 1+popcount(h), 15 + [mech = GRU])`
— `rho[3] ∈ {15,16}` separates it from every registered population
(`0`, `{1,2}`, `{3,4}`, `{5,6}`, `{7,8}`, `{9,10}`, `{11,12}`, `{13,14}`), backed
by the parent's exhaustive pairwise descriptor certificate; expressivity class
`k = 0` (MLP), `1` (GRU, `size < 12`), `2` (GRU, `size >= 12`);
`dev = size + popcount(h) + w + 2·[GRU]`; `obs = (1+w, [GRU])`; search rank by
`(rho[0], rho[3], size, w, h)`; `U1` selector `w = 0`. Grid:
budgets `((6,1,2,15), (48,2,3,16), (48,2,4,16))`, charges
`((0,0,0,0), (1,0,0,0))`, `d ∈ (10, 14, 99)`, `b ∈ (0,8,16,24,32)`,
`h ∈ ("NO_OBSERVATION", (1,0), (2,1))`, `τ ∈ (3/17, 8/17, 11/17, 1)`, both
contracts — 51,840 inputs, the parent's shape. Seeds by the parent's rule
`8317 + 101·mech_index + 17·size + 3·w + task_index`.

### 3.5 Set-valued emission semantics and the non-degeneracy ladder

For an input `x` with survivor set `S(x)` (world-independent — `survivor_mask`
never reads `CAP`), resource-admissible `A(x) = S ∩ Res(R)` and refused
`Rf(x) = S \ Res(R)`, the **set-valued emission** is

```
S(x) = ∅            → INCONSISTENT (as F)
I(x) = { UNSATISFIED if Rf(x) ≠ ∅ } ∪ ⋃_{i ∈ A(x)} V_c(i)
|I(x)| = 1          → POINT : F emits IDENTIFIED(v) in every admissible world, same v
|I(x)| >= 2         → SET   : typed abstention, CANNOT_IDENTIFY(I(x)) under U-1a
```

`I(x)` is exactly the union over the admissible world product of `F`'s
identified sets (KP-1A image exactness), so it is computable structurally
(route A) and observable black-box (route B). The `SET` case carries a
`FeasibleSet` premise (U-1a): no probability is attached, and every value `F`
would emit in any admissible world is inside it.

- **`ND-2` (non-degenerate point):** `|I(x)| = 1` and the value is a strictly
  positive rational. `{0}` and `{UNSATISFIED}` are degenerate (the parent's
  standard).
- **`ND-1` (informative set):** `I(x) ⊊ I_PROTO(x)` where `I_PROTO` is the
  image under `CB-PROTO` at the same input, **and** `I(x)` contains at least one
  strictly positive rational. A set that only restates the protocol clause, or
  contains no positive value, is degenerate.
- **Soundness on the real world:** with `b_real(i)` the measured solved bits of
  machine `i` from the new receipt and `extcap` the parent's external
  definition, a **violation** at `x` is `extcap(x, b_real) ∉ I(x)`.
- **Truthfulness of the bridge:** machine `i` is truthful iff `b_real(i) ∈ Adm(i)`.

### 3.6 Decision rule (registered now)

`ROW_K` closes **iff all of**:

1. `ND-2 >= 1` on `SIGMA_REAL4` (the set-valued bridge yields at least one
   non-degenerate world-invariant point — the quantity the parent lane found to
   be 0 under every truthful-by-construction bridge);
2. **0 soundness violations** over every input with `S(x) ≠ ∅`, both contracts;
3. `SB-L*` is truthful on **32 of 32** machines;
4. routes A and B agree on `ND-1`, `ND-2`, the violation count and the
   truthfulness count;
5. the null of §3.8 is beaten.

Any failure leaves the row OPEN with the failing clause named and the failing
stage attributed to **one** of: the commitment rule (a committed cell
falsified — report which cell and at which machines), the population design
(`ND-2 = 0` because no survivor set resolves), or the counter (positive control
fails).

**Registered expectation.** `ND-2 >= 1` is expected: every `MLP` machine is
fully resolved under `SB-L*` and has `V_{E_full} = {8/17}`, so any input whose
admissible survivors are `MLP`-only yields a point `8/17`. Truthfulness on 32/32
is the genuine risk of this test and is **not** expected with confidence: the
width-48 `MLP` cells are extrapolations. If the measurement contradicts either,
the measurement wins.

### 3.7 Two routes, positive controls

- **Route A (structural)** never enumerates a world: it computes `I(x)` from the
  bridge and the parent's masks.
- **Route B (black-box)** installs concrete worlds on the registration surface
  through `install_universe`, runs the parent's `predict` end to end, and takes
  the union of the emitted identified sets over the **value-index worlds**
  (world `t` gives machine `i` its `t mod |Adm(i)|`-th admissible bit vector) —
  each admissible vector of each machine appears in at least one such world —
  plus seeded random product worlds on which every emitted identified set must
  lie inside route A's `I(x)`. Route B imports nothing from route A and
  recomputes `extcap`, violations and truthfulness from the receipt with its own
  code.
- **Positive control `PK-1`:** the parent's V3 point law installed as a
  bridge on `SIGMA_REAL4` must give an `ND-2` count strictly greater than
  `SB-L*`'s (a fully resolved bridge can only add points). **Positive control
  `PK-2`:** `CB-PROTO` on `SIGMA_REAL4` must give `ND-1 = ND-2 = 0` (the parent
  lane's theorem, re-derived on a fourth population).

### 3.8 Null and hostiles

**`NULL_RANDOM_COMMIT`** — 200 seeded bridges in `SB` with exactly the same set
of committed `(machine, head)` cells as `SB-L*`, each committed band drawn
uniformly from `{SOLVED, UNSOLVED}`, evaluated for truthfulness on the new
receipt. Registered requirement: `SB-L*` truthful on 32/32 while **at most 2 of
200** null bridges are truthful on 32/32. (The null is by construction not
truthful-by-design; it shows the truthfulness count is a property of the
commitments, not of the counter.) The `ND-2` distribution of the null is
reported beside it and is **not** a requirement.

| id | planted defect | quantity it must move / `applicable` condition |
|---|---|---|
| `HK1` | drop the protocol clause (untrained heads free) | `ND-1` and `ND-2` must fall |
| `HK2` | count `{0}` and `{UNSATISFIED}` as `ND-2` | `ND-2` must rise |
| `HK3` | flip `MLP T1` commitment to `{SOLVED}` | truthfulness must flag `>= 1` machine; **applicable iff** some `MLP` machine with head 1 trained measures UNSOLVED |
| `HK4` | complement one machine's measured bits in the receipt | violations must appear; **applicable iff** that machine is an admissible survivor at some `ND-1` input (the executor picks the first such machine, and fails if none) |
| `HK5` | drop one value from route A's `I(x)` at one input | route B must report a disagreement |
| `HK6` | path typo in the freeze-order gate's required-file list | the gate's negative control must fail |
| `HK7` | mutate the parent `F` blob | blob-sha mismatch refused |

A hostile whose `applicable` flag is false is reported as such and **fails the
run** if its inapplicability was not caused by the true result itself (`HK3`).

## 4. `ROW_L` — futurity by posterior-dated external custody

### 4.1 Parents, and what is not touched

`gmi-833-real-developmental-validation-v1` owns the continual-learning
instrument: `train_continual_v3.py` (net, `NFEAT = 16`, `WIDTH = 6`,
`T_TRAIN/T_EVAL = 512/128`, criterion `<= 16` errors, `N_PROP = 24`,
`SEQ_STEPS = 120`, `K_SEQ = 4`, seeds, the DP-1 ladder `B1 = B_prop/3`,
`B2 = B_prop`), the quantitative evolvability `Ev_Q(U) = Q(U)` (#909/#908, the
row `Define evolvability quantitatively`), the matched-control design
(`POS = XOR(1,3),(2,4),(1,4),(2,3)`; `NEG = XOR(12,13),(13,14),(14,15),(12,15)`;
`U = XOR(1,2)`), and `CL3-P8`. `gmi-833-body-residual-akl-v1` owns `FFA-1`. The
instrument is reused **byte-for-byte** except for the source table and the
output directory; nothing about training, seeds or scoring changes.

### 4.2 The task-family generator `G` (registered now)

`G` maps a byte string `D` to the matched task-family pair `(POS(D), NEG(D))`
exactly as `train_continual_v3.py` does: bits MSB-first from the first
`(K_SEQ+1)·(T_TRAIN+T_EVAL) + NFEAT + 64 = 3,280` bits (410 bytes); the four
sequence tasks and the discovery task `U` are the registered XOR rules on those
real bits. `G` has **no free parameter chosen after seeing `D`** except
`B_prop`, fixed by the parent's pilot rule made explicit:

**Pilot rule `PR-1`.** Run the baseline law only (`use_history = False`) at
budgets `(60, 90, 120, 180, 240, 360, 540)`; `B_prop` = the **smallest** budget
with `p0 ∈ [9/24, 21/24]`. If none exists the source is `AT_FLOOR_OR_CEILING`,
excluded by name and **not scored**. (This rule reproduces all seven of the
parent's registered budgets from its disclosed pilot grid: 180, 90, 120, 90,
180, 120, 120.) The pilot never constructs a history-conditioned law and cannot
reveal what is predicted.

### 4.3 The frozen evolvability prediction `EP-1`

For every admissible posterior family `D`:

- **`EP-1` (primary, the load-bearing prediction):** `Ev_Q(U)` under the POS
  history strictly exceeds `Ev_Q(U)` under the NEG history —
  `pH(POS(D)) > pH(NEG(D))`. A tie is a MISS.
- **`EP-2` (secondary, reported, not load-bearing):** `pH(NEG(D)) = 0/24`
  (the parent observed this on 7/7 sources).
- **`EP-3` (secondary, reported):** `pH(POS(D)) > p0(POS(D))` (`CL3-P1`,
  which the parent hit on only 3/7 — expected to be **unreliable**, frozen so
  that both a hit and a miss are on record).

The predictor is the parent's mechanism, not a fitted model: shared low-offset
XOR structure raises the useful proposal mass, unrelated far-offset structure
drives it to zero. It is frozen here **before any posterior byte exists**.

### 4.4 Custody criterion `FFA-1P` (the provenance reading of `FFA-1`)

A candidate family `D` is admissible iff **all four** hold:

1. **Dated.** `D` carries a timestamp `T(D)` recorded by a party outside this
   programme, in that party's own permanent record.
2. **Posterior.** `T(D)` is strictly later than the committer timestamp of
   **this freeze commit** plus a 60-second guard.
3. **Exogenous.** `D` was not authored, generated, parameterized or selected by
   hand by this programme; it is chosen only by the mechanical rule of §4.5
   fixed here; and `D` is not reachable as a blob from this freeze commit
   (`git ls-tree -r <freeze>`), nor from any commit of this repository dated
   before `T(D)`.
4. **Independently attested.** The evidence for clauses 1–2, **and the
   content itself**, is bound to the outside party's record: the party's own
   content hash of the revision must equal the hash of the bytes this lane
   scores.

*Relation to `FFA-1`.* Clause 3 is stated by **provenance**, not by current
location: material whose origin is attested outside the repository does not
lose exogeneity if a later commit records its hash or a short prefix. `FFA-1`'s
in-session reading ("not a blob at all") guarded against in-programme
authorship; clause 4's outside content hash is the stronger guard and replaces
it. Every `FFA-1` rejection remains an `FFA-1P` rejection. The full source
bytes are **kept off-repository** (laptop scratch), as the parent did; the
package commits only revision ids, timestamps, the outside hash, this lane's
sha256, the byte length and the first 80 bytes.

### 4.5 The posterior source rule `PS-1` (mechanical)

Source: English Wikipedia, `list=recentchanges&rctype=new&rcnamespace=0&rcshow=!redirect`,
`rcdir=newer`, `rcstart = freeze committer time + 60 s`. Candidates are the
page-creation revisions in **ascending creation order** with `newlen >= 2000`
bytes. For each, in order, fetch the **creation revision itself** (by `revid`,
never the latest revision) with `rvprop=timestamp|sha1|size|content`; a
candidate is **admitted** iff the fetch succeeds, the revision's `sha1`
(Wikimedia's own record) equals `sha1` of the fetched UTF-8 wikitext bytes, and
the bytes number `>= 410`; otherwise it is recorded `REJECTED_<clause>` and the
next candidate is taken. Stop at **`k = 6` admitted** sources. The fetch is a
single pass at one recorded time `T_fetch`; no candidate is skipped by choice.
The wikitext bytes are the task-family input `D`; every registered detail of
the recentchanges entry and the revision record is kept in
`POSTERIOR_SOURCES_V1.json` beside sha256 of the API response bytes.

Every admitted source is then re-checked against `FFA-1P` by the executor and
independently by route B (a second query form: `prop=revisions&revids=` against
`prop=info`-style `pageid` lookup, ISO timestamps compared as strings after
normalisation, and the freeze time read from `git show -s --format=%cI`).

### 4.6 Decision rule (registered now)

`ROW_L` closes **iff all of**:

1. `>= 6` sources pass `FFA-1P` under a checker validated in both directions
   (recall on a planted admissible candidate; no-alarm on the parent lane's six
   rejected candidates and on the hostiles of §4.7);
2. every admitted source passes `PR-1` (interior baseline) — a source at floor
   or ceiling is excluded by name and replaced by the next admitted candidate
   **only if** the replacement's creation time is also posterior; the count of
   exclusions is reported;
3. `EP-1` is scored on every scored source and hits on **every** one of them
   (`k/k`), so the label-permutation null probability is `2^-k <= 1/64`;
4. routes A and B agree on every `p0`, `pH`, verdict and custody clause.

If clause 1 cannot be met inside this lane's window (too few pages created
after the freeze at `T_fetch`), the row stays OPEN **with the freeze in place**
and the count obtained is reported: a freeze awaiting posterior data is the
registered intermediate state. If `EP-1` misses on any scored source the row
stays OPEN, the miss is reported exactly, and the failing stage is attributed
to one of: the prediction (mechanism does not transfer to this byte structure —
report the bit statistics), the pilot (`p0` at a boundary), or custody.

**Registered expectation.** `EP-1` holds on every admissible source (the parent
observed 7/7 with `pH(NEG) = 0` throughout). If the measurement contradicts
this, the measurement wins.

### 4.7 Null and hostiles

**`NULL_LABEL_PERMUTATION`:** under exchangeability of the POS/NEG labels each
source's `EP-1` sign is a fair coin; the probability of `k/k` is `2^-k`,
reported exactly. **`NULL_RANDOM_SIGN` (200 seeds):** 200 random sign
assignments over the `k` sources; the count matching `k/k` is reported and must
be `<= 200·2^-k + 5`.

| id | planted defect | must be |
|---|---|---|
| `HL1` | candidate with a creation timestamp before the freeze | rejected at clause 2 |
| `HL2` | candidate that is a repository blob at the freeze | rejected at clause 3 |
| `HL3` | candidate whose recorded outside `sha1` mismatches its bytes | rejected at clause 4 |
| `HL4` | a receipt with `pH(POS)` and `pH(NEG)` swapped | `EP-1` must flip to MISS |
| `HL5` | a receipt with `pH(POS) = pH(NEG)` | `EP-1` must score MISS (tie) |
| `HL6` | freeze time read from the wrong commit (a later one) | every real source must be rejected at clause 2 |

## 5. Named results this package may assert

`SB-1` (set-valued emission semantics and the derived bridge `SB-L*`),
`SB-2` (the `SIGMA_REAL4` census: `ND-1`, `ND-2`, positive controls, null),
`SB-3` (real-system soundness and truthfulness on `SIGMA_REAL4`),
`FP-1` (posterior custody: the `FFA-1P` verdicts with their attestations),
`FP-2` (the `EP-1`/`EP-2`/`EP-3` scores on the admitted posterior families).
No other identifier may appear in the receipt. Each carries scope, quantifiers,
assumptions, falsifiers, strongest parents and forbidden extrapolations in
`KL_REVIVAL_THEOREMS_V1.md`.

## 6. Falsifiers

- `SB-1`: the derived table differs from §3.3; an input where route A's `I(x)`
  differs from the black-box union.
- `SB-2`: `PK-1` not above `SB-L*`; `PK-2` not zero; a null seed count above 2.
- `SB-3`: any violation; any machine outside `Adm`.
- `FP-1`: an admitted source with `T(D)` not posterior, or whose outside hash
  does not match, or which is a blob at the freeze.
- `FP-2`: any scored source with `pH(POS) <= pH(NEG)`.

## 7. Order of commits (registered now; CI asserts it)

1. **This commit**: `FREEZE_V1.md`, `FREEZE_ROWS_V1.json` only.
2. Population module `heldout_universes_real4_v1.py` (population + `CR-1` +
   `SB-L*`), `freeze_predictions_real4_v1.py` and the frozen set-valued
   prediction stream `FROZEN_PREDICTIONS_REAL4_V1.json` (+ sample TSV) —
   **before any `SIGMA_REAL4` training exists**; the L fetcher and the
   posterior source record `POSTERIOR_SOURCES_V1.json` (fetched after this
   freeze's committer time, before any L training exists).
3. Training receipts: `REAL_RUNS_V4/REAL_MEASURED_V4.json` (laptop-billy,
   torch 2.4.1+cpu, one thread) and `REAL_RUNS_L4/cl4_*.json`.
4. Executor, oracle, tests, gates, receipts, notes, manifest, reconciliation.

No file of commits 1–2 is edited after commit 3 exists.

## 8. Forbidden promotions

`FOURTH_REGISTRATION_LAW` (a total point law fitted to the counterexamples),
`F_IS_DEFECTIVE`, `KE_3_INVALIDATED`, `BRIDGE_TRUTHFUL_IN_GENERAL`,
`CAPABILITY_PREDICTION_SOLVED`, `PREDICTOR_TESTED_BEYOND_SIGMA_REAL4`,
`REVEALING_SET_RESCORED`, `FUTURE_TASK_FAMILY_CONSTRUCTED`,
`OUT_OF_SAMPLE_EQUALS_FUTURE`, `EVOLVABILITY_MECHANISM_GENERAL`,
`CONTINUAL_LEARNING_GENERAL_CLAIM`, `WIKIPEDIA_CONTENT_ENDORSED`,
`SECTION_K_COMPLETE`, `SECTION_L_COMPLETE`, `M5`,
`INDEPENDENT_TEAM_REPLICATION`, `REAL_SCALE_VALIDATION`,
`CHECKLIST_CLOSURE_IMPLIES_COMPLETENESS`.

## 9. What is not claimed

Nothing here is a claim about whether any GMI theorem is true. `F`, the
registration protocol, the continual-learning instrument, `Ev_Q`, `CL3-P8` and
`FFA-1` are parent-owned and are not amended. The residual contribution of this
tranche is two levers applied under rules fixed here, each measured on material
that did not exist when the parent lane filed its dispositions.
