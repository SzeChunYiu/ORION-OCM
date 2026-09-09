# MSC V1 Report — Minimum Sufficient Cognition, frozen execution

Issue SzeChunYiu/ORION-OCM#216 ([FNA-Q1]). Scope: the frozen MSC V1 experiment
(issue S5-S8). Donor provenance (ledger identities QG-30/QG-31, commit b8a8ff6 on
`research/q216-donor`) and parent maps live in the sibling lanes; this lane consumes
them as fixed inputs. No file outside `research/quantum-structural-ocm-v1/` was touched.

## 0. Provenance

| Artifact | Pointer |
|---|---|
| Freeze | `msc/FREEZE_MSC_V1.json` (schema `ocm.q216.minimum-sufficient-cognition.freeze.v1`; frozen before the first scored run: 8 file sha256s, salts, 13 frozen arms, engineering-chain policy) |
| Protocol | `MINIMUM_SUFFICIENT_COGNITION_PROTOCOL_V1.md` + `.json` |
| Results | `msc/MSC_V1_RESULTS.json` (base pass + `engineering_chain` E4/E5); superseded defect run preserved as `msc/MSC_V1_RESULTS_DEFECTRUN_F6FA0B6.json` |
| Tests | `msc/test_msc.py` — 20/20 pass (closure mirror = production `ocm.kso.navigation.gated_closure`, quotient exactness, confirmation soundness, hostile pair, shuffle null, freeze presence) |
| Commits | base pass `f004ec6` -> E4 `ab32a25` -> E5 `e228f55` -> this report |
| Ground truth | production `gated_closure` at stream state, external judge, never charged to arms |

All execution on laptop `billy` (python 3.12.14); Mac used for git/edits only.

## 1. Frozen setup

Population 480 atoms / 1,280 edges / 24 evidence, production CORE_ATOM_TYPES and
warrant profiles; stream 32 D1 tasks + 10 update events (admissions/revocations);
salts in the freeze file; every arm replays the SAME stream against the same judge.
Charge units frozen in `msc/arms.py`: objects_touched (atom-equivalents, incl. the
per-event quotient charges), edges_touched, probes, verifier/reopen calls, lifetime
work, persistent bytes. Arms: Q0 full scan; Q1 exact typed/indexed (strongest parent);
Q2 counting-block quotient (FQ-1); Q3 local subspace (FQ-3); Q4 adaptive conditional
probe (FQ-2); Q5 composition; ablations Q5_NO_QUOTIENT / Q5_NO_CONE / Q5_NO_PROBE /
Q5_COMPOSED_NAIVEORDER; E1 incremental variants; Q4_SHUFFLE_NULL control.

## 2. Base-pass results (32/32 exact on every arm)

| Arm | objects (mean) | edges (mean) | probes (mean) | lifetime build+maint | persistent bytes |
|---|---|---|---|---|---|
| Q0_FULL_SCAN | 767.9 | 365,807.7 | 0 | 0 | 0 |
| Q1_INDEXED (parent) | 767.9 | 1,010.5 | 0 | 25,460 | 19,170 |
| Q2_QUOTIENT | 1,561.3 | 4,092.8 | 0 | 26,690 | 244,360 |
| Q2_QUOTIENT_E1 | 1,556.6 | 4,086.4 | 0 | 4,422 + 104,296 | 244,360 |
| Q3_SUBSPACE | 1,120.7 | 5,655.0 | 0 | 0 | 0 |
| Q4_PROBE | 284.3 | 429.4 | 119.1 | 13,345 | 0 |
| Q5_COMPOSED | 1,561.3 | 4,088.8 | 8.3 | 40,035 | 244,360 |
| Q5_COMPOSED_E1 | 1,556.6 | 4,083.2 | 7.3 | 17,767 + 104,296 | 244,360 |
| Q5_COMPOSED_NAIVEORDER | 1,561.3 | 4,088.8 | 8.3 | 40,035 | 244,360 |
| Q5_NO_QUOTIENT | 284.3 | 429.4 | 119.1 | 13,345 | 0 |
| Q5_NO_CONE | 1,516.3 | 4,088.8 | 253.1 | 40,035 | 244,360 |
| Q5_NO_PROBE | 1,561.3 | 4,092.8 | 0 | 26,690 | 244,360 |

Mechanism counters (causal gate S7, all pass): Q2 13 refutations + 19 confirmations
consumed; Q3 32 cone restrictions; Q4 19 probe early-stops; Q5 13 + 19 + 19 cone
restrictions; no hidden neural/LLM machinery (imports: stdlib + production ocm.kso).
Ablation deltas: removing the quotient costs +1,277.0 objects/task (Q5 -> Q4 profile);
removing the cone costs -44.9; removing the probe changes nothing in the base schedule
(0.0) — the probe lever pays only under the E4/E5 schedule below.

## 3. Function questions

**FQ-1 quotient economy (base).** Standalone, the quotient LOSES: 1,561.3 objects vs
parent 767.9 (2.03x worse), 4,092.8 edges vs 1,010.5 (4.05x worse). Structural cause
(measured, not tuned): production-random population is nearly incompressible — 482
blocks over 488 atoms, 1,308 qedges; the serialized quotient is 244,360 bytes vs the
parent index's 19,170 (12.7x): at this population the quotient buys NO state
compression, and its win must come from per-query work — which the base full-scan
schedule squanders. This negative was engineered, not filed (section 4).

**FQ-2 adaptive probe value.** Q4 is exact 32/32 at 284.3 objects (2.70x fewer than
parent) and 429.4 edges (2.35x fewer), 119.1 probes mean, 19/19 positives confirmed by
monotone early stop; negatives closed by frontier exhaustion at k/N = 0.346. Registered
against the mandatory shuffle-equal-n null AT Q4's own per-task budget: null is wrong on
7/32 tasks (21.9%; tasks 0, 19, 21, 26, 27, 29, 30 — all true positives lost). The
null's raw means are LOWER (objects 196.4, probes 81.9; margin dict preserved verbatim
in the JSON) because under-investing and erring is cheap: the registered value is
EXACTNESS AT EQUAL BUDGET, not mean probe economy. Adaptive value = the conditional
rarity-ordered policy converts the same probe budget into correctness.

**FQ-3 local subspace.** Static a-priori subspace restriction (Q3) LOSES at this scope:
1,120.7 objects (1.46x parent) and 5,655.0 edges (5.60x parent), because the reachability
cone at scored scale covers ~a third of the field (k/N ~ 0.25-0.35) so subsetting saves
little and pays boundary bookkeeping. No positive terminal is issued for the static
form; the subspace value is realised only when the subspace is built DEMAND-DRIVEN —
which is exactly Q4's probe frontier and E4's tail-incidence worklist (both positive
below). Q3 is subsumed, not abandoned.

**FQ-4 resource responsibility.** The layer that actually controls end-to-end cost was
identified twice, and both diagnoses paid: (a) EXACTNESS is controlled by head-admission
semantics — the defect run (S7) showed one dead-head-block skip false-refutes a true
positive; (b) COST is controlled by the witness-extraction stage, not counting
(decomposition in S4: 839.34 = 540.94 counting + 8.66 fetch + 289.75 fallback). State
responsibility: the quotient's persistent state is 12.7x the parent index — quotient
value must be argued in per-query work plus missing-coordinate detection, never in
state compression, at this population.

**FQ-5 hostile (mandatory).** See S5.

**FQ-6 ordering.** All three checks identical (Q2 rebuild vs E1; Q5 rarity vs naive;
Q5 rebuild vs E1): decisions are order-independent; `ORDERING_DEPENDENCE_REQUIRES_
RICHER_STATE` NOT triggered.

**D1 lifetime (E1).** Incremental quotient maintenance has NO_LIFETIME_PAYBACK at this
update volume: 4,422 build + 104,296 maintenance = 108,718 lifetime vs 26,690 for full
rebuild on demand (Q5 variant: 122,063 vs 40,035). Ten updates do not amortise
maintenance; per-query rebuilds win. Re-scoped, not retried at this volume.

## 4. Engineering chain (negative -> positive, coordinator rule)

Recorded in `results.engineering_chain`; every pass re-runs the SAME frozen stream,
asserts per-task decision equality vs the frozen base BEFORE recording (exit 3, nothing
written, on divergence), and carries its own code sha256 + commit. Costs stay fully
charged; nothing outcome-facing was tuned.

| Pass | objects | edges | vs parent (767.9 / 1,010.5) |
|---|---|---|---|
| Q2 base | 1,561.3 | 4,092.8 | 2.03x / 4.05x WORSE |
| E4 worklist (Q2) | 839.3 | 470.9 | objects +9%, edges 2.15x better |
| **E5 cone confirm (Q2)** | **663.8** | **687.0** | **1.16x / 1.47x BETTER** |
| **E5 cone confirm (Q5)** | **651.4** | **467.0** | **1.18x / 2.16x BETTER** (probes 110.5, 16 early stops, 0 fallbacks) |

- **E4 stage attribution:** per-query counting-closure schedule — full-scan fixpoint +
  eager all-block liveness. **Lever:** work-list enabling over a tail-incidence index
  (one examination per count-growth event, fire-once) + lazy memoized block liveness.
  Least-fixpoint equivalence argued in `lever_e4.py` and asserted per task.
- **E5 stage attribution (component decomposition, measured):** E4's 839.34 objects =
  540.94 counting + 8.66 path-member fetch + 289.75 charged full-closure fallback
  (488 atoms x 19 positive tasks / 32 — reconciles exactly). Counting alone already beat
  the parent; 19/19 positives fell back because the fully-inside induced-subfield
  restriction drops any derivation edge with a side-head outside the extracted region.
  **Lever:** witness region = the counted cone (every block with count > 0 at early
  stop), confirmed under the production-faithful tail projection (edge kept when all
  tails are in-region; heads admitted individually). A firing in the projection is a
  firing in the full field, so confirmation never affirms a non-derivation; refutation
  is untouched (count([t]) == 0 is exact). Result: 0 fallbacks, 19/19 confirmed, both
  arms beat the strongest parent on objects AND edges, exactness 32/32 preserved.

## 5. Hostile FQ-5 (same quotient state, different correct D2)

Twins with identical bulk signature, identical spectrum, different indexed response —
the donor's QG-30/QG-31 structure. Serialized quotient on F_A and F_B: byte-identical
(241,024 bytes, `quotient_isomorphic_witness: isomorphic = true`).

| Arm | status | state bytes | members fetched |
|---|---|---|---|
| Q0 / Q1 / Q3 | NATIVE_IDENTITY | 35 / 61 / 35 | 2 |
| Q4_PROBE | NATIVE_IDENTITY_VIA_PROBES | 95 | 2 |
| Q2_QUOTIENT, Q5_COMPOSED | REPRESENTATION_INSUFFICIENT__MISSING_COORDINATE_FOUND | 241,024 | 2 |

The quotient-consuming arms return the mandated verdict on the compressed state, then
reopen with the missing coordinate (custody identity) charged (`insufficient_then_
reopened: true`) and answer correctly on both fields. The gate passes for all arms:
natives decide D2 from identity; quotient arms detect insufficiency instead of guessing.
This is the load-bearing negative: compression that erases a decision-relevant
coordinate MUST self-report, and it does.

## 6. Defect run, superseded (record discipline)

First scored attempt (commit f6fa0b6): the causal gate's zero-margin exactness item
failed — every quotient-consuming arm false-refuted exactly one true positive (31/32;
task idx 30, s=v125 t=v258). Root cause attributed to ONE stage: `counting_closure`
skipped a whole qedge when any HEAD block was dead, while production `gated_closure`
fires the edge and admits live heads individually. Fixed with corrected head gating +
regression tests (`test_dead_head_block_still_admits_live_heads`,
`test_split_regroups_classes_never_merges`, `test_q2_exact_at_scored_scale`); a second
latent unsoundness (split-regroup merging into a summed-multiset qedge) was fixed and
regression-tested in the same audit. The defective results are preserved, never edited;
the scored base pass was re-run after the fix. The freeze file records all of this.

## 7. Terminals (issue S8 vocabulary only)

**Issued (scoped):**
1. `QUANTUM_STRUCTURAL_FUNCTION_RECONSTRUCTED_NON_NEURALLY_AT_SCOPE` — the donor's
   transferable functions (bulk-signature counting over a typed quotient; exact
   refutation; witness reconstruction; indexed-vs-bulk discriminability handling via
   self-reported insufficiency) are reconstructed in stdlib-only non-neural code and
   match production ground truth exactly on the frozen stream. Scope: this population
   class (480/1,280, production types/warrants), these task types (D1 + hostile D2).
2. `MINIMUM_SUFFICIENT_COGNITION_SUPPORTED_AT_REGISTERED_SCOPE` — the minimum
   sufficient instrument set at this scope is: typed index (D1, parent-sufficient) OR
   quotient + worklist + cone confirmation (beats the index on work AND carries
   missing-coordinate detection) OR adaptive probe frontier (cheapest exact D1, zero
   persistent state). No neural component is needed for exactness anywhere in the loop.
3. `PARENT_SUFFICIENT_FOR_exact_typed_indexed_D1_retrieval` — Q1 alone is 32/32 exact
   at 767.9 objects / 1,010.5 edges / 19,170 bytes; success terminal per policy.
4. `ADAPTIVE_PROBE_VALUE_SUPPORTED_AT_REGISTERED_SCOPE` — S3/FQ-2, registered on the
   Q4-minus-null exactness margin at equal budget (32/32 vs 25/32).
5. `REPRESENTATION_INSUFFICIENT__MISSING_COORDINATE_FOUND` — S5, issued by
   construction and demonstrated.
6. `NO_LIFETIME_PAYBACK` — E1 incremental maintenance at this update volume.
7. `RESOURCE_RESPONSIBILITY_DIAGNOSIS_USEFUL_AT_REGISTERED_SCOPE` — both S4 diagnoses
   (head admission controls exactness; witness extraction controls cost) were
   decision-relevant: they produced the E5 lever and the defect fix.

**Explicitly NOT issued:** static subspace value (FQ-3 negative-in-place, subsumed by
the demand-driven positives); `ORDERING_DEPENDENCE_REQUIRES_RICHER_STATE` (gate passed);
`QUOTIENT_MAINTENANCE_DOMINATES` / `PROBE_COST_DOMINATES` / `STATE_SEARCH_COST_DOMINATES`
(no stage dominates after E4+E5; probes are 110-119 mean against 284-651 total objects);
`NO_FUNCTIONAL_PARITY_*` (all arms 32/32).

**Vocabulary check:** the issue S8 forbidden claim tokens appear in this lane only
inside the protocol's verbatim forbidden-list rule; nowhere as claims (verified
programmatically over the report, results and freeze files: zero occurrences).
"Quantum-structural" is used only as the donor ledger's name for the transferred
signature, never as a capability claim.

## 8. Reading order

`FREEZE_MSC_V1.json` -> `MINIMUM_SUFFICIENT_COGNITION_PROTOCOL_V1.md` -> this report ->
`msc/MSC_V1_RESULTS.json` (numbers; `engineering_chain` for the levers) ->
`msc/lever_e4.py`, `msc/lever_e5.py` (lever code + equivalence arguments) ->
`msc/test_msc.py` (invariants). Everything re-runnable on laptop billy from repo root:
`python3.12 -m unittest discover -s research/quantum-structural-ocm-v1/msc -p 'test_*.py'`.
