# GMI biosphere layers R7–R11 — executed (V1)

Status: **EXECUTED_EXACT_AT_SCOPE.** Five layers built as executable modules with deterministic JSON receipts, on the
branch `claude/gmi-biosphere-r7-r11`, continuing the R0–R6 stack (`morph.py`, `vm.py`, `equiv.py`, `ecology.py`,
`zoo.py`, `morphgen.py`, `qd.py`/`b1.py`). Issue #422.

Status date: 2026-09-12.

Refs: `GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md`, `GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1.md`,
`GMI_BIOSPHERE_SCALING_AND_TRIAGE_V1.md`, `GMI_GAP_LEDGER_EXECUTED_V1.md`.

---

## 0. A naming conflict, resolved in the open

`GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md` §20 names the roadmap layers:

```text
R7  D/V/P split manager
R8  distributed search runner
R9  species classifier / parent-reduction harness
R10 real-task adapters
R11 meta-morphogenesis layer
```

The working brief for this lane named R7–R11 differently (lineage/descent, cost-bounded triage, census, invasion,
open-world harness). The two lists are not the same list. Rather than pick one and silently drop the other, each module
implements the protocol's named role **and** the brief's falsifiable content where they can be reconciled, and says in
its docstring which reading it took:

| layer | protocol §20 | this lane | how they were reconciled |
|---|---|---|---|
| R7 | D/V/P split manager | lineage and descent | both are provenance over a search. `lineage.py` carries the stream manager (`Streams`, D free / V budgeted / P refuses) **and** the descent ledger with its exact replay audit. |
| R8 | distributed search runner | cost-bounded triage | a runner is a runner because it does not pay full fidelity for everything; the scaling document is the rulebook for that. `triage.py` is the fidelity ladder F0/F2/F5 with an audited screen. |
| R9 | species classifier | census by size | a census is the classifier run exhaustively instead of on a search's leftovers. `census.py` reports configurations, isomorphism classes and response classes separately. |
| R10 | real-task adapters (stage B7) | invasion / competition | **not reconciled, and not faked.** B7 needs LLM-scale compute and stays `REGISTERED_FOR_EXPERIMENT` in the gap ledger; an 8-bit microscope cannot host it. `invasion.py` implements the brief's reading, and the receipt says in its own `layer_reading` field that the protocol's R10 is not built here. |
| R11 | meta-morphogenesis (stage B9) | open-world harness (stage B4) | `biosphere.py` is the B4 episode driver, and the thing it is used to measure is the B9 comparison: fixed Γ against a learned ecology-conditioned Γ, with `Delta_B_meta` between them. |

---

## 1. What each layer does, its receipt, its claim level and its claim ceiling

### R7 — lineage and descent (`gmi_microscope/lineage.py`)

**Does.** Records, for every evaluated genotype: parent fingerprint, the R5 operator applied, the integer proposal seed,
the number of charged proposal draws (failed type checks included), the charged development cost, the capability and the
archive descriptor. Reconstructs the descent chain of any elite and **replays it**: re-seeding `random.Random` on the
recorded proposal seed and re-applying the recorded operator to the recorded ancestor must re-derive every intermediate
canonical fingerprint and the elite's own, exactly. It does this twice per elite — from the founder as recorded, and from
a **reminted** copy of the founder. Also carries the D/V/P stream manager: the protected stream raises on any query and
the receipt reports the count (0).

Replay is possible because every genotype in this layer is stored in *canonical genotype* form (`canon_geno`, rebuilt
straight out of `morph.canonical`), so an operator's result does not depend on node identifiers and the whole chain is
remint-invariant.

**Receipt.** `microscopes/results/STAGE_R7_LINEAGE_V1.json` (schema `StageR7LineageDescentV1`).
Self-verifying: `replay_witness` carries whole chains (founder seed, per-step proposal seeds, expected fingerprints) so
a reader can re-derive an elite without re-running the search. Test: `test_r7_lineage_descent_replays_from_the_committed_receipt`.

**Claim level.** `PROVED_AT_SCOPE` for the replay property on the executed run (0 failures is a property of the executed
chains, checked, not asserted); `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT` for everything else in the receipt.

**Claim ceiling.** One ecology, one seed, one grammar. "Replays exactly" is a statement about this recorder and this
operator set. It is *not* evidence that the search found anything: the archive is small by design. A declared search
bound (`MAX_CANON_WIDTH`) refuses genotypes whose exact canonical tie-break would be too wide, so the reachable set is
narrower than the IR's; the receipt reports how many proposals that refused.

### R8 — cost-bounded triage with an audited screen (`gmi_microscope/triage.py`)

**Does.** The scaling document's fidelity ladder: F0 static validity (type/interface validity, servability, exact
duplicate collapse under canonicalization), F2 cheap screen (development truncated from 16 events to 4), F5 exact
confirmation (the registered 16-event protocol). Promotion is diversity-preserving (best screen score per behavioural
cell, everything above τ, plus a random audit sample of the *rejected*), never naive top-k.

**Protocol rule 18 is enforced as a precondition, not reported as a courtesy.** The rule exists because a functional-
equivalence cache assigned candidates a fitness they had not earned and mis-scored 34.65 % of them (RV-377-061,
`STAGE_F_FEC_AUDIT_V1.json`). So: τ is frozen on a calibration sample against a false-rejection **budget declared before
calibration**; the two error rates are then measured on a **disjoint** audit sample and reported separately, overall,
per mechanism family and per declared sub-population; and `triage.main` **raises** if the audit receipt is missing or
RED, citing its `receipt_sha256` in the run receipt when it is green.

The only cache this lane uses is keyed by the exact canonical form, i.e. by isomorphism — sound by construction, which
is what the FEC also claimed, so the audit **measures** it: maximum exact-score spread within a canonical-form group,
which must be 0.0.

**Receipts.** `STAGE_R8_SCREEN_AUDIT_V1.json` (schema `StageR8ScreenSoundnessAuditV1`) and
`STAGE_R8_TRIAGE_V1.json` (schema `StageR8TriageRunV1`, citing the audit hash).
Test: `test_r8_triage_screen_was_audited_before_use_and_its_cells_replay`.

**Claim level.** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT`.

**Claim ceiling.** One ecology, one grammar, one screen. The rates are rates of *this* screen on the *declared* audit
population (half uniform grammar draws, half 1–3 step mutational neighbours of the R4 parents — uniform draws alone are
about 1 % admissible, so they cannot measure a false-rejection rate at all; the two sub-populations are reported
separately so neither hides inside the other). A bounded false-rejection rate makes the search **cheap, not complete**:
the missed-species bound is that rate, and it is not zero.

### R9 — census by size (`gmi_microscope/census.py`)

**Does.** Counts three different things at each genotype size and never lets them be confused:

```text
N_CONFIG(n)     type-correct CONFIGURATIONS in the declared census universe
N_CANONICAL(n)  distinct canonical fingerprints — isomorphism classes
N_RESPONSE(n)   distinct exact developmental RESPONSE signatures on one registered ecology
```

The receipt carries a `three_counts_are_different_things` block stating, in the record itself, that none of the three
is a species count — `N_RESPONSE` is a **lower** bound on the species count at the registered scope, because a second
ecology or intervention can only split these classes further, never merge them (scaling document §12).

Exhaustive to size 5; size 6 is stratified by node-type composition with each drawn stratum enumerated exhaustively, so
`N_CONFIG` carries a Horvitz–Thompson estimate with a standard error while class counts stay counts *within the sampled
strata*, never extrapolated. Two invariants the rest of the lane leans on are measured here, not assumed: the
developmental response is a function of the canonical form (0 disagreements), and remint changes no count.

**Receipt.** `STAGE_R9_CENSUS_V1.json` (schema `StageR9CensusV1`).
Test: `test_r9_census_counts_three_different_things_and_the_small_sizes_reproduce`.

**Claim level.** `PROVED_AT_SCOPE` for the exhaustive sizes within the declared universe; `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT`
for the stratified size.

**Claim ceiling.** One ecology, one intervention, one declared sub-alphabet with one frozen parameter setting per kind,
and declared universe restrictions (one INPUT, one OUTPUT, OUTPUT port 0 bound, no dead nodes except OUTPUT and the
update laws, acyclic). Enlarging the alphabet or the parameter grid can only raise `N_CONFIG`; enlarging the registered
ecology family can only raise `N_RESPONSE`. At size 6 the response count is over a uniform subsample of the isomorphism
classes and the receipt says how many were evaluated.

### R10 — invasion and competition (`gmi_microscope/invasion.py`)

**Does.** Two carriers develop in the **same** ecology out of **one** shared charge pool and **one** shared stream of
feedback events. The resident pays an establishment head start; thereafter the machine with the lower cumulative charge
takes the next event and the other does not see it, so a cheap machine buys more development out of the same pool and an
expensive one starves. Evaluation is on the architecture-neutral protected endpoint and is charged to each machine's own
ledger but **not** deducted from the contested pool. Outcomes are reported as a resident × invader matrix per pool with
the exact charged budgets, event counts and allocation string.

**The falsifiable claim.** Occupancy under a shared budget is not a function of the solo scores: some ordered pair of
distinct carriers must disagree with the ranking they get when each is developed alone with the whole pool. Diagonal
cells (a carrier against a copy of itself, which the head start alone can split) are counted separately and the
prediction is adjudicated off-diagonal. If the off-diagonal count were 0 the receipt would say
`COMPETITION_ADDS_NOTHING_AT_THIS_SCOPE` in those words.

**Receipt.** `STAGE_R10_INVASION_V1.json` (schema `StageR10InvasionCompetitionV1`).
Test: `test_r10_invasion_cells_replay_and_competition_is_not_independent_scoring`.

**Claim level.** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT`.

**Claim ceiling.** One ecology, one basis, one allocation rule, one head start, three declared pools, the R4 parent
library as the carrier set. The allocation rule is a **modelling choice** — "lower cumulative charge takes the next
event" is one way to make a budget contested, not the way ecology works — and a different rule can reorder outcomes, so
it is reported as part of the result. This layer is **not** the protocol's R10 (real-task adapters, stage B7), which
remains unbuilt and `REGISTERED_FOR_EXPERIMENT`.

### R11 — open-world biosphere harness (`gmi_microscope/biosphere.py`)

**Does.** Runs a stage-B4 episode end to end behind one receipt: ecology sampling from a declared development pool of
generated smooth ecologies (generated worlds are development worlds, biosphere §20, and the R7 stream manager gates
every access), development on the exact charged VM, charging, the R8 screen then exact confirmation, MAP-Elites
archiving keyed per ecology (so niche breadth is measured), R7 lineage recording with an elite replay audit, fossil
retention, and an R9 census for context. Checkpoints the archive, the lineage, the policy counters and the master random
state; a resumed episode must equal a straight-through one, and the receipt asserts it.

The episode exists to run the protocol's **stage B9** comparison through identical charged machinery: a **fixed** Γ (the
R5 operator drawn uniformly, the control) against a **learned** Γ (per ecology and parent carrier, sample the operator
proportional to measured success), with the learned policy's consultations, updates and counter description **charged**
to `B_search` — an unmetered policy is exactly the hidden-capital channel biosphere §22 forbids.
`Delta_B_meta = B_fixed − B_learned` at a milestone declared before the run (an admissible genotype in at least two
distinct carrier classes). An arm that never reaches the milestone reports `None` and no delta is computed: a missing
milestone is not a win for the other arm.

**Receipt.** `STAGE_R11_BIOSPHERE_V1.json` (schema `StageR11BiosphereEpisodeV1`), plus the context census
`STAGE_R9_CENSUS_V1_R11_CONTEXT.json` and per-arm checkpoints `CKPT_R11_BIOSPHERE_V1_<arm>_S<seed>.json`.
Test: `test_r11_biosphere_episode_is_deterministic_resumable_and_cites_its_screen_audit`.

**Claim level.** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT`.

**Claim ceiling.** One episode family, two arms, the listed seeds, one grammar, one screen, one ecology pool.
`Delta_B_meta` here is a statement about this operator set and this policy parameterization on this pool; stage B9 asks
for it on untouched regime **sequences**, which this lane does not have. **Nothing in this receipt is evidence of
open-endedness**: biosphere §21 lists what an open-endedness claim would have to measure (new viable species rate, new
occupied niches, mechanism-vector entropy, parent-reduction distance trend, major transition count) and this episode
measures the archive, the lineage and the charge over a fixed budget.

---

## 1a. What the executed runs measured

Every number below is from the committed receipt named beside it; every receipt's `receipt_sha256` is reproduced by its
own code.

### R7 — `STAGE_R7_LINEAGE_V1.json` (`3cbbda5315f45e25`), terminal `R7_LINEAGE_REPLAYS_EXACTLY`

```text
4 000 evaluations, 146 s, 36 archive cells, 14 952 charged proposal draws, 159 867 415 charged development units
descent depth: max 22, mean 7.45
replay audit: 72 chains (36 elites x {as recorded, from a reminted founder}), 760 steps, 0 failures
remint: 900 fingerprint checks, 0 changed; 0 replays failed from a reminted founder
D/V/P: protected queries 0; the two protected specs recorded by hash only
```

The receipt carries 5 fully replayable descent chains (1–6 steps each) so the property can be re-checked from the
receipt alone. That is what the committed test does.

### R8 — `STAGE_R8_SCREEN_AUDIT_V1.json` (`56d9d805941bcba4`) and `STAGE_R8_TRIAGE_V1.json` (`1e612d91d6ec2d80`)

Audit (150 calibration + 250 disjoint audit draws), declared false-rejection budget 0.05, τ frozen at 0.2083:

```text
false rejection 0.0000 (0 of 43 admissible)     <- within the declared budget: SCREEN_AUDITED_GREEN
false promotion 0.8170 (192 of 235 promoted)
screen charge / exact charge                    0.0909
canonical-form cache: 231 groups, 10 shared, max exact-score spread within a group 0.0  <- sound, MEASURED
remint: 40 draws checked at both fidelities, 0 changed
per mechanism family (false rejection): KVSTORE 0.0 (20 admissible), PROGRAM 0.0 (21), TABLE 0.0 (2), DENSE/NONE no admissible
```

**The honest negative result of this layer.** The screen is cheap (9 % of exact) but almost undiscriminating at a tight
budget: at τ = 0.2083 it promotes 94 % of the audit sample, so the ladder costs **more** than confirming everything.
The budget sweep in the audit receipt makes the trade explicit (each row's τ fitted on calibration, measured on audit):

| declared budget | τ | promoted | measured false rejection | cost vs full fidelity | pays for itself |
|---|---|---|---|---|---|
| 0.00 | 0.2083 | 0.940 | 0.0000 | 1.031 | no |
| 0.05 | 0.2083 | 0.940 | 0.0000 | 1.031 | no |
| 0.10 | 0.2083 | 0.940 | 0.0000 | 1.031 | no |
| 0.20 | 0.2083 | 0.940 | 0.0000 | 1.031 | no |
| 0.40 | 0.5208 | 0.856 | 0.2791 | 0.947 | yes |

The triage run (603 drawn → 591 screened → 567 promoted → 1 confirmed admissible) measures the same thing on its own
population with a measured, not extrapolated, full-fidelity reference: **saving −0.1345**, verdict
`TRIAGE_COSTS_MORE_THAN_FULL_FIDELITY_AT_THE_DECLARED_BUDGET`. A 5 % saving is available only at a 28 % false-rejection
rate, i.e. bought with completeness. In-run triage-bias audit: 3 rejected candidates promoted anyway, 0 of them
admissible.

*(An earlier draft of this receipt estimated the full-fidelity reference from the audit sample's mean exact charge and
reported a 99 % saving. That was an instrument error — the audit population is half parent-neighbours, whose exact
confirmations cost two orders of magnitude more than a uniform grammar draw's — and the reference is now measured on the
run's own population.)*

### R9 — `STAGE_R9_CENSUS_V1.json` (`958d03d70e9c2313`), terminal `R9_CENSUS_EXECUTED`

| size | mode | N_CONFIG | N_CANONICAL | response classes | config→canonical | canonical→response |
|---|---|---|---|---|---|---|
| 3 | exhaustive | 6 | 6 | 1 | 1.0000 | 0.1667 |
| 4 | exhaustive | 227 | 227 | 4 | 1.0000 | 0.0176 |
| 5 | exhaustive | 12 987 | 8 593 | 4 | 0.6617 | 0.0005 |
| 6 | stratified (200 of 1 001 strata) | 234 760 enumerated; estimate **1 174 974 ± 429 698** | 96 648 in the sampled strata | 5 over 9 000 evaluated representatives | 0.4117 | 0.0006 |

The collapse is the result: at size 5, 12 987 type-correct configurations are 8 593 isomorphism classes and **4**
distinct developmental responses. Both invariants held: 0 disagreements between two labellings of the same canonical
form, 0 counts changed by remint. *None of the three columns is a species count* — the receipt says so in a
`three_counts_are_different_things` block, and `N_RESPONSE` is a lower bound at the registered scope.

### R10 — `STAGE_R10_INVASION_V1.json` (`a5366e7d832fe1d7`), verdict `COMPETITION_REORDERS_OCCUPANCY`

8 R4 carriers × 8 × 3 pools = 192 cells. Outcomes by pool:

```text
pool  20 000: RESIDENT_HOLDS 29  INVADER_REPLACES 29  COEXIST 6
pool  60 000: RESIDENT_HOLDS 36  INVADER_REPLACES 26  COEXIST 2
pool 200 000: RESIDENT_HOLDS 34  INVADER_REPLACES 28  COEXIST 2
```

**45 off-diagonal cells** (plus 20 diagonal, counted separately) disagree with the independent-scoring baseline, so the
registered prediction holds: occupancy under a shared budget is not a function of the solo scores. Reminting either
competitor changed nothing in 12 checked competitions.

### R11 — `STAGE_R11_BIOSPHERE_V1.json` (`aa047bad696ea1fd`), terminal `R11_BIOSPHERE_EPISODE_EXECUTED`

Four episodes (2 arms × 2 seeds), 2 000 evaluations each, one screen, one ecology pool of three generated development
ecologies:

| arm | seed | archive cells | admissible cells | best | total charge | charge to milestone |
|---|---|---|---|---|---|---|
| fixed | 0 | 57 | 12 | 0.8594 | 39 370 826 | 470 197 |
| fixed | 1 | 56 | 19 | 0.8958 | 26 521 112 | 2 028 770 |
| learned | 0 | 50 | 4 | 0.8594 | 28 477 256 | 6 123 689 |
| learned | 1 | 51 | 0 | 0.8333 | 9 551 659 | never reached |

```text
Delta_B_meta (seed 0) = 470 197 - 6 123 689 = -5 653 492
verdict FIXED_MORPHOGENESIS_CHEAPER_ON_1_OF_2_SEEDS
resume determinism: identical (checkpoint at 200, run to 400)
protected queries: 0 in every run; elite replay failures: 0 in every run
```

**The honest negative result of this layer.** The learned, ecology-conditioned Γ **lost** — on the one seed where both
arms reached the declared milestone it needed 13× the charge, and at the fixed evaluation budget it filled fewer
admissible cells on both seeds. `Delta_B_meta` is defined only on the seeds where both arms reached the milestone, so
seed 1 contributes nothing and is not counted as a win for the fixed arm.


---

## 2. Invariants asserted in every receipt

* **Exact arithmetic** in the 8-bit fixed-point universe (`TOTAL_BITS` 8, `FRAC_BITS` 4). No layer declares a wide
  instrument.
* **Deterministic receipt hash**: every receipt's `receipt_sha256` is `gmi_microscope.core.sha256_of` over all fields
  except that key.
* **Remint invariance (H5)**: `morph.remint` changes no reported quantity, and each receipt carries the check that
  proves it for its own quantities — fingerprints and whole replayed chains (R7), both fidelity scores (R8), every
  count (R9), every competition record (R10), and through R7/R8 for the episode (R11).
* **D/V/P firewall**: the protected ecologies are never evaluated by any layer; R7 and R11 report
  `protected_queries: 0` and record the frozen protected spec hashes.
* **Rule 18**: no screen is used before its own audit receipt exists and is green; the audit's hash is cited in the
  run receipt.

## 3. What was changed in the already-built layers

Two additive changes, both behaviour-neutral for the committed R0–R6 receipts:

* `morphgen.mutate` / `morphgen.crossover` take an optional `record` list that receives the operator name of every draw.
  The draw sequence off the random stream is unchanged, so a recorded and an unrecorded run with the same seed produce
  the same genotype (checked).
* `morph` gained `_wl_classes` (the Weisfeiler–Lehman refinement, factored out of `canonical`/`canonical_labels`
  verbatim) and `canonical_search_width`, which reports how many labellings the exact canonical tie-break would have to
  enumerate. R7 and R11 use it to refuse a proposal before paying for it. The existing IR, VM and B0 tests still pass
  and `STAGE_B0_EQUIVALENCE_METERING_V1.json` still reproduces its committed hash.

## 4. What is still open

* The protocol's **R10 (real-task adapters / stage B7)** is not built and is not claimed. It stays
  `REGISTERED_FOR_EXPERIMENT` in `GMI_GAP_LEDGER_EXECUTED_V1.md` §4.
* The R8 screen's false-rejection rate is measured on a declared population, not on the population a long campaign would
  actually produce. Closing that needs the rate re-measured *under selection*, mid-campaign — the same residual the FEC
  audit carries (`STAGE_F_FEC_AUDIT_V1.json`, claim ceiling).
* R9's response classes come from one ecology under one intervention. The R2 species relation quantifies over a
  registered family; a census over the full (E, J\*) family is the closure experiment for turning `N_RESPONSE` into a
  species count at scope.
* R10's allocation rule is unreplicated: one rule, one head start. A second allocation rule is the cheapest test of
  whether the reordering it reports is about competition or about that rule.
