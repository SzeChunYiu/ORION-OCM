# RV-377-200 — FREEZE: a preregistered empty channel region, and a neutral search for its realization

Frozen BEFORE any run. Rung **B7** of the claim ladder (`GMI_COMPLETENESS_BOUNDARY_THEOREM_V1.md` §4) asks
whether the theory can predict a form of machine intelligence *before* it is built. The master closure
ledger (`research/gmi-grand-unification-v1/MASTER_CLOSURE_LEDGER_V1.md` §7) names the remaining
programme step exactly: "preregister empty operational regions and search for realizations after
predictions are frozen". This record does that with the programme's own neutral search.

## 1. The region

The channel-capability atlas (`GMI_CHANNEL_CAPABILITY_ATLAS_V1.md`) predicts ceilings for channel
configurations, not architectures. The registered microscope already contains one such configuration
that no registered ecology has ever been *searched* under: the `extra_unseen_feedback` intervention,
which after development reveals the target on `UNSEEN[:4]` — an **external store channel** (CL-7)
with coverage `c = 4/8` of the evaluated indices and reliability `rho = 1`.

The world is chosen so that the structure channel (CL-5) is closed: a **random table** `E_rnd(s)`
whose 16 entries are drawn i.i.d. uniform on the integers `[-10, 10]` (fx units, `FX_ONE = 16`),
seeded from `SHA256("GMI-B7-RND|" + freeze_commit + "|" + role + "|" + k)`. No entry is inferable from
any other, so on an index that neither development nor the store reveals every machine is reduced to a
fixed guess. A protected table is drawn only **after** the machine is frozen (the RV-377-123 lesson):
searched machines are frozen on a development table `E_rnd(dev, s)` and adjudicated on 20 protected
tables `E_rnd(prot, k)` that no search ever scored.

Evaluation is the registered `unseen` criterion on the 8 UNSEEN inputs: `cap = 1 − err/1.5`,
`err = mean |answer − target| / FX_ONE`. For a uniform integer `U` on `[-10, 10]`, the minimum
expected absolute deviation of any fixed guess is attained at the median 0: `E|U| = 110/21 = 5.2381` fx.

## 2. Frozen ceilings (CL-7 and CL-1 specialised to this instrument)

* **STORE arm** (`extra_unseen_feedback`): 4 revealed indices can be answered exactly, 4 cannot:
  `cap* = 1 − (4·5.2381/16)/(8·1.5) = 1 − 0.16369 = 0.89087`. This exceeds θ = 0.85, so the region
  "admissible machine on a structureless world with a half-coverage store" is predicted **occupied**.
* **NOSTORE arm** (`standard`): all 8 unrevealed: `cap*₀ = 1 − (8·5.2381/16)/(8·1.5) = 0.78175 < θ`.
  The region "admissible machine on a structureless world without the store" is predicted **empty**.
* Rule-40 control: the best constant on a protected table scores `cap*₀` in expectation, so an attaining
  STORE machine separates it by `0.109` ≈ 2.6 fx units, above the quantization floor.
* Standard error: `sd|U| = 3.04` fx, so one protected table's capability has sd `≈ 0.0079` on the
  STORE arm and `≈ 0.0112` on the NOSTORE arm; over 20 tables the s.e. of the mean is `≈ 0.0018` /
  `≈ 0.0025`. Predicates below use the **measured** s.e. across the 20 protected tables.

These ceilings hold for every machine whose only access to the protected table is development and
the store channel — including machines nobody has built. The search's fitness on the *development*
table is a further channel (selection leaks the development entries), which is why adjudication is on
protected tables and why P5 below is a prediction rather than a nuisance.

## 3. Existence certificate (protocol: existence before search)

The registered zoo parent `exemplar_table` (a TABLE store with INSERT/LOOKUP) is evaluated under both
arms on the 20 protected tables before any search result is read.

* **P0**: `exemplar_table` attains `cap*` within 3 s.e. on the STORE arm and sits at `cap*₀` within 3 s.e.
  on the NOSTORE arm. If P0 fails the instrument, not the theory, is wrong and the run is void.

## 4. Search

The B1 MAP-Elites search (`gmi_microscope/b1.py` loop, R5 grammar, descriptors carrier/size/drift), with
one change made additively in `gmi_microscope/b7_region.py`: candidates are evaluated by
`ecology.run_genotype` under the arm's intervention on the development table (criterion `unseen`).
3 development seeds × 2 arms × 20 000 charged evaluations. From each archive the best elite per carrier
class and the overall best are frozen, atrophied under the arm's intervention (`atrophy_ir.prune_all_interventions`,
rule 32 restricted to the arm), and evaluated on the 20 protected tables under the arm's intervention
**and** under the other arm's intervention (channel ablation).

## 5. Frozen predictions

| id | prediction | falsifier |
|---|---|---|
| **P1 ceiling** | On the STORE arm, no elite's mean protected capability exceeds `cap* + 3 s.e.` | any elite above |
| **P2 realization** | On ≥ 2 of 3 development seeds some STORE-arm elite reaches `cap* − 3 s.e.` on the protected tables: the preregistered region is realized by neutral search | attained on ≤ 1 seed |
| **P3 form** | Every attaining elite has atrophied carrier `TABLE` or `KVSTORE`, and under `standard` (store removed) its mean protected capability falls to ≤ `cap*₀ + 3 s.e.` — capability tracks the channel the machine reads | a DENSE/PROGRAM/NONE attainer, or an attainer that keeps > `cap*₀ + 3 s.e.` without the store |
| **P4 empty region** | On the NOSTORE arm no elite's mean protected capability exceeds `cap*₀ + 3 s.e.`, hence none is admissible: the region predicted empty is empty | any NOSTORE elite above, or admissible on protected tables |
| **P5 selection channel** | On ≥ 2 of 3 seeds the best STORE-arm elite scores at least 0.02 higher on its development table than on the protected mean (the search overfits the 4 unrevealed development entries) | gap < 0.02 on ≥ 2 seeds |

Kill conditions. If P2 fails on 3/3 seeds while P0 holds, the terminal is
`REGION_PREDICTED_OCCUPIED__NOT_REALIZED_BY_NEUTRAL_SEARCH_AT_20K`, attributed by the neutral-search
adequacy rule: the witness is expressible (P0), so the failure is `INCONCLUSIVE_SEARCH`, and one revival
(RV-377-201) at 100 000 evaluations is permitted before the negative is filed. If P1 or P4 fails, a
machine beat a channel ceiling on protected tables: either the table generator leaks (check the seeds) or
CL-7/CL-1 is wrong at this scope — both reportable, neither retuned.

## 6. What a full pass licenses

`B7_PREREGISTERED_REGION_REALIZED_AT_REGISTERED_SCOPE`: the theory named an occupied and an empty
region of channel space before search, gave the occupied region's exact ceiling, and a search that
contains no architecture macro found a machine attaining that ceiling with the predicted carrier class,
while finding nothing in the region predicted empty. This is a prediction about a form defined by its
channels, verified by construction. It is **not** a claim of historical novelty (store-reading memory
machines are a known family), not a claim about architectures a cost-minimising search prefers
(RV-377-121 stands), and holds at one obligation type, one world family, `L = 16`, 8-bit fixed point.

Reserved ids: RV-377-200 (this record), RV-377-201 (budget revival). Receipts:
`microscopes/results/STAGE_B7_REGION_<arm>_S<seed>_{HOST}.json`, certificate
`STAGE_B7_REGION_CERTIFICATE_{HOST}.json`.
