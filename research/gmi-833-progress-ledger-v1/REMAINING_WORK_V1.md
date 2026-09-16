# GMI #833 Progress Ledger v1 — Remaining-Work Queue

**Schema:** `GMI_833_PROGRESS_LEDGER_REMAINING_WORK_V1`
**Basis:** unticked #833 boxes as of the 2026-09-16 consolidation pass (body at post-edit state; adjudication pin `f068ea19`). Every unticked box appears below with its precise residual and owning lane. Lanes: `ours` = audit/consolidation lane; `aj` = aj-lane (`gmi-833-aj*` packages + AJ contracts); `other` = the candidate-space/ecology/families/cognitive lanes (open PRs listed); `either` = unassigned.

## Section A (foundation and claim discipline)

| Box | Residual | Lane |
|---|---|---|
| L25 terminology | Migrate the 35 remaining gate hits in 12 `gmi-833-aj*` packages (per-package table in `research/gmi-833-terminology-migration-v1/MIGRATION_LOG_V2.md`); then hold migration-at-landing-time for future packages. Completes ceiling `TERMINOLOGY_MIGRATION_AT_GMI_833_PAPER_FACING_SCOPE`. | aj |
| L34 claim-discipline registration | Retrofit machine-readable assumptions/falsifiers/strongest-parents/forbidden-extrapolations for legacy objects (0/173 today; gaps quantified per object in `THEOREM_SCORES_V2.json`); register falsifiers for the 7 G6 deductive proofs stuck below EV1; resolve the 2 crosshanded quantifier-overreach flags. In flight — do not duplicate. | ours |

## Section B (corpus audit close)

| Box | Residual | Lane |
|---|---|---|
| L42 duplicates under different terminology | Build the terminology-aware duplicate detector: normalize statements through the migration crosswalk's legacy→new token map (R# rules), re-hash, adjudicate the resulting new groups under the frozen #939 taxonomy. Existing content-hash + DUPID classes are done (#949). | ours |
| L44 finite-enum where analytic possible | New adjudicator population: for each EXACT_FINITE_CERTIFICATE-support claim (49 at rescore v2), read for analytic-possibility; verdict + reason per object. | ours |
| L45 analytic claims supported only by computation | New adjudicator population over ANALYTIC_PROOF-typed rows (63): verify each has non-computational support. | ours |
| L46 computational claims w/o independent implementation | Census the corpus's computational claims; flag those lacking the `independent_oracle_v1.py`/two-route pattern (the g0-* and AJ9 packages have it; legacy likely not). | ours |
| L47 post-hoc assumptions | Corpus-wide pass beyond the one registered instance (`INSTANCE-CONFIG-FREEZE-SEPARATION`): commit-order/config-vs-freeze audit across packages. | ours |
| L48 grammar encodes target | The AJ9 no-smuggling contract response (task-authorship + primitive-basis channels; `INSTANCE-AJ9-NOSMUGGLING-SCOPE` RED/HIGH, inherited by K04–K06). | aj |
| L49 cost forces winner | Corpus-wide cost-model audit disposition (per-package tooling exists: #855 A3, #891). | ours |
| L50 hidden macros / privileged operators | Corpus-wide run of the A1/A2 denylist + semantic-operator detectors as census dispositions. | ours |
| L51 hidden iid/stationarity | New detector + corpus pass. | ours |
| L52 hidden finite-horizon | New detector + corpus pass. | ours |
| L53 alternative resource accounting | Corpus pass re-running claims under alternate scalarizations (#863 R4 pattern). | ours |
| L54 encoding sensitivity | Corpus remint pass beyond the #875 registered slice. | ours |
| L55 search sensitivity | Corpus pass with materially distinct search replicas (#863 R3 pattern). | ours |
| L56 parent rediscovery only | Compare each claim against its registered strongest parents for strict containment (PARENT_LEDGERs exist; the comparison does not). | ours |
| L58 downgrade/retract | Apply the registered OVERSTRONG disposition to `research/gmi-capability-interactions-unified-v1/CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1.md` (reword the universal phrasing to the registered 27x27 finite-classification scope or attach the mandatory joint-burden caveat), manifest note, re-verify with controls. FIN2UNIV population: nothing to do (0 downgrades). | ours |
| L59 freeze `GMI_THEORY_BASELINE_V1` | Capstone: requires L34 retrofit + Section-B corpus-wide passes (L42–L56) + L58 applied. Next round. | ours |

## Section C — candidate space (L137–L152)

Open: PR #966 (research(#956)) — M(G0,B) formalization, semantic equivalence classes, morphology descriptors, exact enumeration, scalable sampling, 10^6 → 10^8 candidates (or certified equivalent coverage), duplicate-collapse rate, reachable fraction, Pareto-front density, post-hoc clustering, blind family mapping, UNKNOWN cluster, non-syntactic novelty, semantic/resource/developmental distances, remint/metric stability. **Lane: other.**

## Section D — ecologies (L156–L178)

Open: PR #959 (research(#957)) — architecture-neutral ecology generator, the 19 vary-dimensions, matched positive/negative twins, non-circular family design, sampling-bias quantification. **Lane: other.**

## Section E/H — known families (L184–L226, L228)

Each family row requires the full Section-H contract (property prediction, P3/P4 grammar, no family macros, neutral recovery, negative twin, lower bound, resource crossover, held-out frozen prediction, remint, independent search, real-scale test). Open: PR #960 (one neutral grammar across four known-form rows). L228: beyond-11 cannot-recover quantification. **Lane: other.**

## Section I — learning laws (L232–L242, L244–L247)

Unticked: admissible-update-law space formalization, the nine "derive conditions favoring X" rows, prospective learning-law selector, neutral-search recovery of selected laws, held-out crossover boundaries, realistic-system tests. NFL boundary row already ticked (#870). **Lane: either.**

## Sections J–M

- L265 real-system transition validation: needs a real-system substrate; nothing merged touches it. **either**
- L275–L285 capability predictor `C_hat`: unbuilt (abstention row ticked via #916/#913; bounds/interference ticked via #907/#906). **either**
- L293–L303 developmental derivations: representation-change→search-cost, operator invention, library formation, phase transitions, path dependence, trap escape, search-dynamics comparison, reachability mass, P4 unseen-mechanism test (L301 — #945 explicitly forbids `UNSEEN_FORM_DISCOVERY` at its scope), future-task evolvability prediction, continual-learning validation. **either**
- L310–L317 cognitive re-audits: hierarchy/skills, planning/stopping, causal, metacognition, social, communication, imitation/teaching, cultural accumulation. Open: PR #927, #924. (AJ13's stopping rule #967 is recursive-descent epistemics, NOT the L311 planning/stopping row.) **other**

## Standing dispatch notes

1. Do not tick in-flight items: L34 (registration, ours), L48 (AJ9 contract, aj), everything under open PRs #946/#952–#966/#927/#924.
2. Every future tick re-verifies the live artifact at a pinned SHA before the body edit (shelf-life rule).
3. Body edits are toggle-only with the diff gate + post-edit byte-verify (this round's procedure is the template).
