# Minimum Sufficient Cognition V1 — protocol frozen before execution

**Issue #216 §5–§8 (execution child of #214). Base `b801a0324e758b7e040d79e4beeaaab1c8aeb9be`, branch `research/q216-msc`.**
Sibling artifacts (donor ledger, donor atlas, classical-parent maps) are owned by agents A/B; this
file and `msc/` are the only files this lane creates.

**Evidence class E1 / L1.** One existing production world, one frozen population and stream, one
author. No quantum computation, no quantum claim, no neural arm, no QPU.

## World choice (issue §5: prefer an existing current-main exact world)

**Chosen: the #115 factorized KnowledgeSpace world, `src/ocm/kso` on main.** Justification by
information-surface match to the frozen experiment:

| Contract requirement | Where `src/ocm/kso` has it |
|---|---|
| persistent objects with exact identity/provenance | `Atom`/`Hyperedge` frozen dataclasses: `WarrantProfile` evidence intervals, `Authority` lattice, `Scope`, epoch, `content_hash`, `digest()` |
| typed retrieval | registered relation vocabulary (10 types) + `ExtractionIndex` with build-work vs query-work accounting |
| exact verifier | `gated_closure`/`fixed_point` over exact `Fraction` warrant homomorphism (KS-T21), `checks` self-check suite |
| exact revocation/reopening | `revocation.py`: `prune`, `impact_cone` (KS-T09), `reopening_report` (KS-T22 REOPEN/RECHECK/UNAFFECTED) |
| tasks with ground truth | decision = membership in the gated closure; ground truth by production code |

Rejected alternatives: `verified-scientific-field-v0` (docs only, no runnable world),
`residual-strategy-regime-v1` (checker-census world, no quotientable persistent field),
`machine-epistemics-lifetime-v1` (benchmark harness, no field objects),
`native-indexed-deduction-evidence-v1` (Knuth/Nederhof parser world — cold compilation dominates
and there is no query-relative persistent field), and the FNA-1 planted world (already
manufactured for a different question; reuse would manufacture a favorable benchmark).

Population: production `ocm.kso.checks.random_space` scaled by parameter (the generator is
parameterized on `n_atoms`/`n_edges`; it is the production generator, not one authored here),
seeded by a frozen salt. Two hostile twin-blocks are **planted, declared here as planted**, and are
adversarial to the quotient mechanism (not to the parent arms) — the mandatory FQ-5 hostile.

## Frozen decision semantics

Field state `F_t = (atoms, hyperedges)` evolves over a frozen stream of updates. At task time the
current revocation set is `R_t`.

- **D1 (reachability decision, the protected decision):** `D1(s,t) = SUPPORTED` iff
  `t ∈ gated_closure(F_t, [s], R_t)`. Ground truth is always production `gated_closure`.
- **D2 (member-selection hostile decision):** given witness block `B` (the penultimate block of a
  D1 derivation), `D2 = ACT(<member>)` where `<member>` is the unique member of `B` with authority
  coordinate `custody >= 2`; `NO_UNIQUE_MEMBER` otherwise. This decision needs the identity↔authority
  mapping, which is exactly the distinction the quotient discards for D1.

## Arms — same frozen tasks, same information surface, different consumption

All arms replay the identical frozen stream. Information surface = the field + stream events;
what differs is how much each arm consumes and pays for. No free preprocessing: every index,
quotient or summary build is charged to the arm that uses it, at build time and again at
maintenance time.

- **Q0 FULL_SCAN.** No index, no quotient: examine every atom (warrant) and every edge
  (tails/heads/warrant), decide by fixpoint over the full structure. The no-structure baseline.
- **Q1_INDEXED.** Current exact typed/indexed retrieval: production `ExtractionIndex` +
  production closure over indexed adjacency. **Strongest-parent arm.** The production index is
  snapshot-bound: every structural update forces a rebuild, charged (honest, not hidden).
- **Q2_QUOTIENT.** Exact decision-sufficient quotient (FQ-1): classical partition refinement of
  the field by `(atom_type, warrant signature, quarantined)` with s and t protected as singleton
  blocks, refined by outgoing-edge signatures (relation, edge warrant signature, head classes,
  co-tail classes) to fixpoint. Quotient edges carry **counting-block (Petri-style) semantics**:
  a quotient edge with tail multiset `{B: m}` is enabled when `m` distinct members of `B` are
  counted reached. Soundness direction used for negatives: `C(s) ⊆ C_q` (class-level counting
  closure), so `[t] ∉ C_q ⇒ t ∉ C(s)` — **exact negative refutation without touching the bulk**.
  Positives are confirmed by minimal concrete witness extraction (a reopen of exactly the blocks
  on one quotient derivation path, charged). Discarded distinctions (declared list):
  within-block identity, per-member `Authority`/`meta`/`content_ref`, edge multiplicity detail.
  Discarded distinctions are reopenable exactly (members live in the persistent field).
- **Q3_SUBSPACE.** Local active-subspace traversal (FQ-3): the exact query region is
  `ungated_closure(F_t, [s]) ∩ backward-plain(F_t, t)` — forward reachability by production
  `ungated_closure`, backward reachability via the production incident adjacency — and the
  production closure runs on the induced subfield. (Production `impact_cone` is forward-only
  and dependency-type-filtered, so it is *not* an exact query subspace; it keeps its
  production role in the revocation/reopen path.) Parent: program slicing / dependency
  closure (KS-T09 is the production ancestor of the region idea).
- **Q4_PROBE.** Adaptive probe acquisition (FQ-2): adjacency is hidden behind a probe API
  (one probe reveals one atom's outgoing postings; warrant observations counted). Cheap first
  summary = per-channel edge counts (charged). Non-oracle probe order = rarest-channel-first,
  the same selectivity heuristic `operator_index`/FNA-1 use — parent-owned. Early stop on
  SUPPORTED the moment `t` is admitted (admissions are monotone; further information cannot
  flip a SUPPORTED decision). Negatives must exhaust the frontier — no early stop is sound there
  without a quotient.
- **Q4_SHUFFLE_NULL (control, mandatory).** Shuffle-equal-n null: the identical probe machinery
  with the SAME per-task probe budget Q4 consumed, but the next probe chosen uniformly at random
  from the live frontier instead of conditionally. Q4 adaptive value is registered ONLY on the
  Q4-vs-null margin (probes-to-decision, expansions, false candidates at equal budget and equal
  correctness). If the null reproduces Q4's numbers, the effect is budget selectivity, not
  adaptive probing, and is reported as PARENT_SUFFICIENT / no adaptive value — never as an
  FQ-2 positive.
- **Q5_COMPOSED.** Quotient + local subspace + adaptive probe: decide on the quotient with lazy
  probing; negatives stop at quotient-level refutation; positives stop at first quotient
  admission of `[t]` followed by one minimal concrete witness confirmation (verifier call).

## Frozen population and stream (salts recorded in FREEZE_MSC_V1.json)

`N` atoms, `E` edges via production `random_space(salt rng)`; `T` D1 tasks (half supported, half
not, chosen by ground truth at stream state, frozen order); `2` hostile D2 tasks on planted twin
blocks; `U` updates interleaved (admissions of salted edge batches; revocations of evidence ids
chosen to flip at least one liveness). Same stream replayed by every arm.

## Mandatory hostile (FQ-5), executable

Two concrete fields `F_A`, `F_B` differing ONLY in which member of the same twin block carries
`custody >= 2` have **isomorphic quotient states** but **different correct D2 decisions**.
Quotient-consuming arms (Q2, Q5) must return
`REPRESENTATION_INSUFFICIENT__MISSING_COORDINATE_FOUND` when serving D2 from the quotient state
alone, then reopen (charged) and answer exactly. Full-state arms (Q0, Q1, Q3, Q4) carry the
coordinate natively and separate the pair by construction; their identity-carrying cost is the
price measured. Every arm's hostile outcome is reported.

## Causal gate (issue §7) — executable form

1. Protocol + code frozen (sha256) and committed before the first scored run; salts recorded.
2. Same task-relevant information for all arms (same stream replay).
3. Mechanism actually consumed at the decisive step: per-arm counters for
   `quotient_refutations_used`, `quotient_confirmations_used`, `cone_restrictions_applied`,
   `probe_early_stops`. A run where a claimed mechanism was never consumed cannot claim its effect.
4. Protected capability preserved with zero frozen margin: exact arms must be 100% correct on all
   tasks; any divergence → `CANNOT_CHECK_<...>_DIVERGED` and nothing downstream is interpretable.
5. Build/update/maintenance/reopen work fully charged per arm (no amortization without a counter).
6. Ablation destroys the registered effect: `Q5_NO_QUOTIENT`, `Q5_NO_CONE`, `Q5_NO_PROBE` rerun
   the whole stream; the metric delta each mechanism claims must vanish when it is removed.
7. Strongest-parent comparison: Q1 is the parent arm; a mechanism-level positive requires Q5/Q2/Q3/Q4
   to beat Q1 on a registered metric with the effect ablatable (item 6).
8. No hidden LLM/neural/quantum computation: stdlib + production `ocm.kso` only.
9. Revocation/reopening exact: after every update, every arm's decision is re-derived and must
   equal production ground truth; the hostile reopen is checked to produce the updated decision.
10. Development/protected evaluation separate: the harness ground-truth judge is external to the
    arms and never charged to them.

## Engineering duty (operator directive, pre-registered levers)

A negative arm result is not terminal until one genuine revival pass. Pre-registered levers, each
a real mechanism improvement with costs still fully charged:

- **E1 incremental quotient maintenance.** On an update, re-refine only blocks incident to
  changed atoms/edges instead of a full rebuild; charge the incremental work.
- **E2 quotient-level negative pruning before concrete probing** (folded into Q5 by design).
- **E3 probe batching.** Reveal a frontier atom's full posting list per probe instead of per-edge.

Chain documented as attribute(stage) → lever → re-run → outcome. Only after a failed revival may
the §8 negative terminal be drawn. Outcomes are never tuned: population, tasks, salts and margins
are frozen before the first run and are not revised to rescue an exposed result.

## Terminals

Only issue §8 terminals are available. Forbidden: any quantum-advantage/cognition claim,
`TRANSFORMER_REPLACED`, `LLM_EQUIVALENT`, `AGI`, `GENERAL_SUPERIORITY`.

## Donor grounding (identities from the `research/q216-donor` ledger, commit b8a8ff6)

- **FQ-1 precedent — QG-31** (`research/extensions/orion-qg/QG31_QUERY_INDEXED_ABSTRACTION_RESULTS.json`,
  blob `39234e2cfd06491317a86348136bb924200d5704`): query-indexed abstraction ladder, indexed local
  response injective on 715 orbits, with the `same_spectrum_same_bulk_different_indexed_response`
  witness (joint cheap summaries cannot recover indexed identity). This is the donor shape for
  query-relative quotienting with reopenability.
- **FQ-5 precedent — QG-30** (`research/extensions/orion-qg/QG30_BULK_COARSE_GRAIN_RESULTS.json`,
  blob `4de0a0a9e980`, pinned commit `645fd929...`): bulk geometry compresses exactly to 45
  signature counts while defect information remains — first information-loss witness: common bulk
  signature `[2,2,2,2]` with representatives `[0,0,0,0,1,1]` vs `[0,0,0,0,1,2]` (same compressed
  state, different downstream defect profile). The hostile below is the OCM reconstruction of
  exactly this witness class.
- **FQ-2 motivation — unresolved-obligation structure ONLY.** The ORION fixed-vs-adaptive
  observation-cost ladder (#933/#942: adaptive 3 < conditioned-fixed 4 < universal-fixed 5) is
  **RETRACTED on ORION main** (null-reproducible: the 85/92 and 708/715 identities are histogram
  artifacts reproducible under shuffle) and is NOT used as donor motivation anywhere in this
  study. Consequence, enforced below: any claim that adaptive probing beats fixed probe sets
  **must survive a shuffle-equal-n null arm** — same probe budget, randomized probe choice. An
  adaptive advantage that a shuffled-probe arm reproduces is selectivity from the budget, not
  adaptive value, and is reported as such.

## Declared limitations, before seeing outcomes

- E1/L1: one production world, one population, one stream, one author.
- The quotient is an over-approximation at class level by construction; only the negative
  direction is decision-exact without confirmation. Positive tasks always pay one confirmation.
- A field whose random structure yields few bisimulation twins will collapse little; that is a
  property of the production random population and is reported, not tuned away.
- The counting-block semantics caps per-block counts at block size; over-counting beyond the cap
  is impossible by construction.
- No approximate VSA/HDC arm, no neural arm (those belong to #214 later tranches).
