# Real-system validation — named results

**Freezes:** `FREEZE_V1.md` @ `808054d9` (pre-implementation),
`FREEZE_V2_REVIVAL.md` @ `bdf2cdab`, `FREEZE_V3_REVIVAL.md` @ `8ada2a53`.
**Parent ownership:** `PARENT_OWNERSHIP_V1.md` — read it first.
**Claim ceiling:**
`GMI_833_REAL_SYSTEM_UPDATE_LAW_AND_DEVELOPMENTAL_VALIDATION_AND_DERIVED_INVENTION_LIBRARY_CONDITIONS_AT_REGISTERED_SCOPE`
**Evidence level:** EV5 (real-scale prospective validation with the licensed band
demonstrated on both sides) for `RV-2`, `CLV-1`–`CLV-4`; EV2 for `RV-1` and
`RV-3`. **Maturity M6 at registered scope only** — six ecologies and fourteen
sequences, not a population.
**Domain tags:** `forall_fin[U]` marks complete enumeration of a finite
registered universe; `sample[P,n]` marks a measured sample of `n` registered
real systems. **No `sample` statement below may be rewritten as `forall`.**

---

## RV-1 — the ecology objects are real-data-computable

**Statement.** `forall_fin[six registered ecologies]`. Every input of `beta*`,
`chi*`, `pistar*` and `tau*`, and every one of UL-11's fourteen
`REQUIRED_KEYS`, is computable from (registered design) x (sha256-bound real
byte source) by the registered derivation, **with no trained artifact as
input**. Concretely: `alpha_gain` from the exact posterior over real candidate
tables; `mu` from the registered retrieval map applied to real contexts; `Dmin`
and `cover` from consistent covering subsets of the registered production space
over real training instances; `Bmin`, `Tsteps`, `Vglob`, `Vloc` from ascent on
exact rational training accuracies of real candidates; `H'`, `r` from which
candidates realize the target on the real stream.

**Scope.** Six ecologies, `M = 9`, `T = 64`, `nq = 64`, `K = 4`.
**Assumptions.** The registered rule is the intervention and the bits are real,
following #903. Exact rational arithmetic; `eps` registered per ecology.
**Certificate.** The executor reproduces the frozen tables of `FREEZE_V1.md`
sections 2.5–2.8 exactly from the six sources: **0 reproduction errors**, all
six sha256 matched.
**Falsifiers.** Any invariant, threshold, coefficient vector or UL-11 label
that does not reproduce; any quantity that turns out to require a trained
model; any float in a claimed value.
**Strongest parent.** #1018 owns all seven thresholds and UL-11; #903 owns the
real-source protocol. Neither is claimed here.
**Forbidden extrapolations.** Not a claim that *every* ecology object is
real-data-computable, only these fourteen keys at this registered shape.
**Why it matters.** This is what unblocked the row. Two previous tranches
reported the row unclosable because real telemetry is float and real systems do
not hand you `H`, `RS`, `retr` or description lengths. They do once the ecology
is *derived from* the data rather than declared.

## RV-2 — UL-11 tested on real trained systems

**Statement.** `sample[registered real ecologies, 6] x forall_fin[8 anchored prices]`.
Over the 48 frozen (ecology, price) cells, with predictions committed at
`808054d9` before any training code existed and observation blind to family:
**20 HIT, 20 MISS, 8 ABSTAIN_MATCHED, 0 ties, 0 ABSTAIN_UNMATCHED.**

**Both sides of the licensed band are exercised and both were predicted.**
Positive: six distinct families are predicted across the registry
(`SIG-W`, `SIG-X`, `SIG-L`, `SIG-P`, `SIG-T`, `SIG-S`). Negative: `SIG-W` is
predicted never to win on X3/X5/X6 (`beta* <= 0`), `SIG-T` never on five of six
(`tau* = 0`, the `r = 0` converse), `SIG-R` never anywhere; and X4 is predicted
to abstain at every price, which it does, on all eight.

**Disclosure made before the outcome** (`FREEZE_V1.md` 2.1): #1018 records
UL-11's own synthetic held-out verdict as a MISS with 260 mismatches, and
`select_v2` as a disclosed revival whose 794/0 score is not UL-11's. A low hit
rate here was an anticipated outcome. The row says *Test*; the row is earned by
executing it and reporting hits and misses exactly.

**Falsifiers.** Any cell scored against a de-anonymised candidate; any argmin
over the unranked comparators; any post-hoc change to a frozen label.
**Forbidden extrapolations.** `UL_11_VINDICATED` and
`SELECT_V2_RESULTS_ATTRIBUTED_TO_UL_11` are forbidden promotions. Where
`SIG-S` is predicted or observed it is an artifact of seven-way ranking with
`BASE-0` excluded, **not** evidence that self-modification pays: the inherited
accounting leaves the loss coordinate invariant to `mut`, so `s* = 0`
identically.

## RV-3 — the misses attribute to one stage (EARNED-BY-COUNTEREXAMPLE)

**Statement.** `forall_fin[52 measured realizations]`. The 20 misses are not a
failure of UL-11's decision logic, which is a strict argmin and provably sound
given its coefficient vectors. They attribute to a single upstream stage: **the
analytic accounting `a_i(E)` is not a faithful model of what a real trained
realization of signature `i` actually spends.** Every one of the nine
signatures diverges from its analytic vector in at least one coordinate, and
**29 of 52** realizations differ from the analytic law in the **loss**
coordinate — the coordinate that carries the held-out error count.

**Consequence.** A selector ranking analytic signature costs cannot be tested
against real systems without either (i) an accounting function validated
against measured realizations, or (ii) measured vectors as the selector's
input. Either is a revival, not a re-score, and neither is performed here:
this package reports the gap and leaves the repair to a successor with its own
freeze.
**Falsifiers.** A realization whose measured vector equals its analytic vector
in every coordinate across all six ecologies would weaken the attribution.
**Forbidden extrapolations.** Not a claim that `tuple_vector` is wrong as an
*accounting contract*; only that it does not predict measured spend.

## CLV-1 — HIST-1 on real continual learners

**Statement.** `sample[registered real sequences, 14]`. HIST-1A is instantiated
with `c` = the priced proposal budget in optimizer steps, `h` = the priced
policy overhead, and `p0 = Q0(U)`, `pH = QH(U)` the exact rational proposal
masses over `N = 24` registered seeds, on a held-out discovery task `U` measured
disjoint from the stored solution set. The verdict is computed at two
registered overhead regimes frozen before any run.

**CL3-P3 holds 14/14:** on every real sequence the verdict at `h_high` is not
`HISTORY_STRICTLY_IMPROVES`. The overhead flip — same measured masses, two
registered prices, opposite verdicts — is demonstrated on real systems.
**CL3-P1 (raw direction) 10/14:** 7/7 on NEG, 3/7 on POS.
**Assumptions.** Both laws on one carrier; `U` disjoint from stored solutions
(measured, see CLV-2); registered prices frozen before any run, per foundation
`R-2`. **HIST-1 itself is #909/#908's and is not amended by any outcome here.**

## CLV-2 — CAPITAL-1's disjointness gate, measured on real systems

**Statement.** `forall_fin[14 sequences]`. Every stored per-task solution was
evaluated **directly on `U` with no further training**. No stored solution
reached criterion on any of the fourteen sequences, so
`solution_capital = false` everywhere and **no cell is contaminated**: the
2x2's `CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION` terminal fires 0 times.
`SEARCH_POLICY_CAPITAL` is returned on exactly the sequences where
`law_changed` and HIST-1 strictly improves (T02, T04, T05) and
`NO_SEARCH_POLICY_CAPITAL` elsewhere.

This is the load-bearing distinction the row demands: a system that merely
**stores** earlier solutions cannot produce these verdicts, because every
stored solution was tested and none solves `U`.
**Contrast with V1:** under `FREEZE_V1.md` the discovery task was easy enough
that stored solutions *did* reach it on five of eight sequences and the gate
correctly refused to identify. The gate's no-alarm case and its alarm case are
both exhibited on real data.

## CLV-3 — the matched structural control (the positive result)

**Statement.** `forall_fin[7 matched pairs]`. For each of seven real sources,
two sequences were run that are identical in source, discovery task, proposal
budget, seeds, criterion, net and split, and differ **only** in the four
sequence task offsets — low-offset XOR pairs sharing the structure `U` needs
(POS) versus the same structure class on offsets `U` never reads (NEG).

**CL3-P8 holds 7/7.** `pH(POS) > pH(NEG)` on every source, with
`pH(NEG) = 0/24` on all seven against `pH(POS)` in
`{7, 9, 9, 12, 17, 19, 22}/24`.

**Reading.** Sequence structure, not the quantity of history, is the operative
variable. The same amount of continual training on unrelated structure does not
merely fail to help — it drives the useful proposal mass to exactly zero.
**Falsifier.** Any pair with `pH(POS) <= pH(NEG)`.
**Forbidden extrapolations.** Seven registered sources, one task family, one
net shape. `CONTINUAL_LEARNING_GENERAL_CLAIM` is a forbidden promotion.

## CLV-4 — DP-1A budget monotonicity on real systems

**Statement.** `forall_fin[14 sequences x 2 laws]`. With the protected
capability score `s_c` the integer count of correct held-out predictions and
`C_pot(B) = max s_c` over the 24 proposals at budget `B`,
`C_pot(B1) <= C_pot(B2)` holds for both laws on every sequence: **14/14**.

## CLV-5 — the reported negatives, attributed

**CL3-P5b (DP-1B) misses on all seven POS sequences (7/14 overall, all NEG).**
Attribution, one stage: DP-1B is an **existence** claim — there exist states
with equal current capability and different headroom — and it was instantiated
as *exact equality of a graded 0..128 score between two independently drawn
states*, which two independent draws essentially never satisfy. The theorem is
not falsified; the instantiation was wrong. Two genuine DP-1B witnesses are
present in the frozen V3 record and reported in `RESULT_V1.json` under
`section_L_DP1B_posthoc_witnesses`: **T06** (`C_now = 70` for both laws,
headroom 58 vs 52) and **T15** (`C_now = 65` for both, headroom 63 vs 33).
These are identified **post hoc** and are labelled as such; they are not
counted as hits and do not enter any tally.

**CL3-P6 (EV-1A band) 5/14.** Nine cells are `CENSORED` because `pH = 0` leaves
a first-hit block empty — seven of them the NEG sequences, where `pH = 0` is
itself the predicted outcome. A censored cell is never counted as a hit.

**CL3-P1 (raw direction) misses on 4/7 POS.** History harms on T01, T03, T07
and ties on T06 even though the sequence shares structure. CLV-3 shows the
structural contrast is real and total; the raw direction is therefore
*necessary-condition* evidence only. Under the stopping rule frozen in
`FREEZE_V3_REVIVAL.md` there is no V4: this is reported as the measured
boundary of the effect, not repaired.

## Chain of custody

1. `FREEZE_V1.md` @ `808054d9` — complete pre-outcome predictions; the commit
   contains that file and nothing else.
2. `1e4fba1c` — V1 implementation and outcomes. Every V1 POS prediction missed;
   attributed to one stage (discovery task at ceiling, `p0 = pH = 24/24`).
3. `FREEZE_V2_REVIVAL.md` @ `bdf2cdab` — registered revival, committed alone,
   with the p0-only difficulty pilot disclosed.
4. `50db5224` — V2 outcomes. One clean full hit; four POS misses with
   `pH = 0/24`; attributed to one stage (sequence budget over-specializes the
   carried body — HIST-1's own omitted-overhead falsifier).
5. `FREEZE_V3_REVIVAL.md` @ `8ada2a53` — second registered revival, committed
   alone, over a **newly registered** matched-pair registry, with the full
   per-source pilot grid tabulated and three ceiling sources excluded by name.
6. `b93af038` — V3 outcomes. 84 HIT / 28 MISS; matched control 7/7; capital
   gate clean 14/14.

No freeze was edited after its outcomes. No result was re-scored. `git log`
proves the order and CI asserts it.
