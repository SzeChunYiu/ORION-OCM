# NEGATIVES_ROOT_CAUSE_V1 — why the run produced many negatives, and the framework change that makes the economy side measurable

Status: EXPLICITLY_NON_FINAL. Owner issue #277 (TTAC extension); bound to parent issue **#323**
(developmental hardening lane). Written 2026-09-10 from the merged artifacts only (no new runs);
every number cited exists in a committed results file or in #323's inspected-main record.

## 0. The bimodality (the single deepest fact)

Every atom in ATOM_REGISTRY_V1 sorts cleanly into two groups by WHAT KIND of claim it makes:

| Group | Claim kind | Outcome |
|---|---|---|
| A: pointwise invariance / detection / exactness | "revocation equals recomputation", "contamination is detected", "refinement <= n-k", "comorphism reflection holds", "quotienting collapses variants", "conformance 1428/1428" | **holds everywhere measured** (D19 50/50; D21 E1 1.0 detection, E2 0 false alarms, E5 1.0, E6 1.0; D20 CEILING_HELD; D22 30/30; T87 512->1) |
| B: economy / amortisation / transfer | "abstraction beats direct search", "library repays acquisition", "macro pays back", "lineage improves the machine", "morphologies generalize", "ledger beats DB", "OCM kernel beats ordinary kernel" | **fails everywhere measured** (SEM-07, MAQ-02, MAQ-05, MOR-02*, DEV-01, LIF-01, PRF-03, PAR-02, PAR-03, HST-19, HSG-02, HSG-03, PRV-02) |

No atom is a counterexample to the bimodality. The programme's measured comparative advantage is
**exactness as a trust layer** (things no parent can do at all); its measured comparative
disadvantage is **economy** (everything a parent can already do, OCM does at 1.07x-3.5x cost).
\*MOR-02's headline number is itself partially a measurement artifact (RC3 below) — the
decomposition is in section 3.5. Group B did not fail randomly — it failed by three mechanism
classes, each already proven inside the programme, and each was measured at its worst corner BY
CONSTRUCTION.

## 1. Root cause 1 — ecology non-stationarity (the no-free-lunch law, operating as proven)

HST-19 (REFUTED, explicit counterexample): bias learned under one ecology can be strictly worse
than a flat prior on a different ecology — "at the one scale measured, negative transfer is the
MAJORITY outcome". MOR-02: 84.4% of grand-search morphologies fail the generalization holdout.
MAQ-02: macro harms 51 of 64 tasks while strictly winning 13. HSG-02: metric proximity does NOT
transfer burden/reach/invalidation guarantees (4 counterexamples). D27/#323: prospectively frozen
future-cognition signature is ABSENT — related-family burden drop 0.0135 vs unrelated 0.0194
(related − unrelated = −0.0059). **Five lanes, one law: structure acquired on ecology E0 is
valued on E1 sampled as if independent of E0 — no-free-lunch then GUARANTEES the parent ties or
wins.** Our world generators produce one-off puzzles with zero planted recurrence (D21 library
holdout: 2 hits, total_nodes_saved = 0). The sharpest single piece of evidence is RV-8/H1 (#323):
the SAME library is ~55% cheaper on a constructed stream but ~40.5% MORE expensive on natural
draws at the same nominal family mix — a sign flip driven purely by the latent relatedness x
repetition structure of the query ecology. The negatives are NFL measured exactly where NFL
bites; they were read as mechanism failures when they are measurement-regime facts. The DEV-01
class note makes the scale explicit: NO atom carried the DEVELOPMENTAL_LINEAGE class — the
across-ecology causal claim had never even been posed to measurement (now registered as
ATOM-DEV-03, terminal OPEN, no closure claimed — see QUERY_ECOLOGY_AMENDMENT_V1).

## 2. Root cause 2 — the capital-cost floor (the self-defeat law)

D20: every CEGAR round rebuilds the abstraction from the FULL concrete relation — one round
already costs a full concrete sweep. RV_B1 deepened it: the one-time sound build must read every
concrete transition (construction floor = one direct pass), and refinement for exact answering
drives the partition toward discrete (81.2% of states; 6/30 worlds fully discrete), so
post-refinement MARGINAL cost is 12.966 (abstraction) vs 11.738 (direct) — the marginal never
inverts at exactness. D19: substitution (cheapest capital there is) costs 1.07x recomputation —
bookkeeping exceeds savings when recompute depth is one shallow BFS. LIF-01: append-only ledger
loses to a database by three orders of magnitude. MAQ-05: the OCM kernel costs 1.5-1.65x the
ordinary kernel. HSG-03 states the general form: inheritance does not stochastically dominate at
maintenance M>0; only `future_savings > acquisition + maintenance + revision` survives. #323's
HC-7 is the same law in value form: V(h) = P(applicable|future) x expected saved work −
(acquisition+storage/retrieval/matching/adaptation/verification). **The unified law: sound
capital costs >= one direct pass to build, carries bookkeeping on every use, and (at exactness)
must refine toward the concrete anyway. An UNCONDITIONAL economy claim is posed against a law
that forbids it.** The surviving conditional inequality was never measured: the registry had no
axis on which it could flip.
**MEASURED OUTCOME (D30, PR #330): the self-defeat law EXTENDS to the relaxed regime.** The
pre-registered falsifier fired over the FULL delta interval (0,1): no delta at any grid point
makes structural capital beat direct on total cost (grid deltas {0.01,0.05,0.1,0.25} never
serve at all — totals 9312 ops vs direct 570 on the 30 worlds; the delta=1.0 envelope arm,
serve at the FIRST abstract counterexample = the infimum of structural cost over all delta in
(0,1], costs 1938 vs 570 = 3.40x while serving a near-vacuous classification: mean certified
bound 0.875-0.958, actual error mass ~0.52). The boundary clause held exactly — delta=0
reproduces the committed D20 per-world and per-n numbers with zero divergence, so the filed
negative IS the exact boundary of the family. The mechanism is now measured: the certified
bound |U-L|/n (U = full abstract closure, L = certified reachable) stays ~0.92 because the
interleaved lossy partition mixes reachable and unreachable states in every block — certified
uncertainty decays only under the refinement that exact answering itself performs, so
relaxation cannot be bought cheaper than exactness. Per the pre-registered consequence, the
admissible claim shape for structural capital narrows to rho-conditioned only. Registered
prediction preserved verbatim in ECONOMY_FRONTIER_PROTOCOLS_V1.json#D30_delta_dial with the
outcome appended to QUERY_ECOLOGY_AMENDMENT_V1.predictions_registered (amendment discipline:
append, never rewrite).

## 3. Hidden relationships across positives and negatives

1. **MAQ-02 (macro) == D21 E4 (e-graph library) == DC-07 == RV-8/H1**: four independent
   implementations of declarative-capital payback; all negative on non-recurrent draws, and
   RV-8 shows the same object POSITIVE on a constructed recurrent stream. Replication of the
   negative AND of the sign flip — publishable structure.
2. **RV_B1 amortisation ratio falls monotonically (8.41 -> 6.44 -> 4.83 -> 3.58 -> 2.49 across
   Q=1..16)**: the fixed cost IS amortising; the marginal never inverts. Linear fit of the
   published table: direct marginal ~416 ops/query vs incremental ~813 -> pure-repeat lookup
   pays iff novel-region fraction rho < ~0.51; the terminal's own steady-state gives
   rho* = 11.738/12.966 ~ 0.905. Either way **a finite crossover rho* in (0,1) exists and every
   measurement so far ran at rho = 1.0** — the impossible corner. RV-8's constructed stream is
   exactly a rho << 1 ecology — which is where the library won.
   **MEASURED OUTCOME (D29, PR #327): the [0.51, 0.905] bracket is REFUTED on the frozen grid.**
   Q*(rho) = NULL at every rho in {0.0,...,1.0} through Q<=32; even pure-repeat streams do not
   cross within grid (fixed floor ~4.3k ops vs ~53 ops/query marginal saving; off-grid
   projection ~Q=80.7 at rho=0). Measured rho* collapses to (0, 0.25): both derivations above
   over-read the still-flattening Q<=16 segment (true Q=16->32 incremental marginal at rho=1
   is ~497, not ~813). The boundary clause held exactly — the rho=1.0 arm reproduces the
   committed RV_B1 per-Q totals with zero divergence. The surviving law is harsher:
   **amortisation pays only in the pure-repeat limit; the crossover is far off-grid.**
   Registered prediction preserved verbatim in QUERY_ECOLOGY_AMENDMENT_V1.predictions_registered
   with the outcome appended (amendment discipline: append, never rewrite).
3. **T87 quotienting (512 -> 1) is the economy claim that WINS** — its equivalence certificates
   are FREE (given by the rewrite rules), while CEGAR blocks must EARN each merge against the
   concrete function. Compression cost scales with the semantic distance between the
   equivalence certificate and the query: declarative/syntactic equivalence free (positive);
   semantically-earned equivalence bounded below by a direct pass (negative at exactness).
   Free-vs-earned equivalence is the split the framework never made — it maps onto #323 HC-6
   (typed operators with applicability contracts; REDUCE's precondition failure is the
   earned-certificate case).
4. **Every Group-A positive is pointwise** (holds per world, needs no future): exactly the shape
   both root causes cannot touch. Group-B claims are all forward-looking (payback,
   generalization, amortisation). The bimodality IS the two root causes seen from above.
5. **D27's discrete +0.25 block (CONTINUED > RESET) is compatibility activation, not learning**
   (#323 HC-2): methods carry it; schemas/facts/index_built do not; it vanishes above a
   morphology regime. That is solution capital exhibiting a step function at an interface
   boundary — an economy frontier crossed by a compatibility match, consistent with RV-8's sign
   flip being retrieval/applicability-driven, not quantity-driven.

### 3.5 Root cause 3 (of the READINGS, not the runs) — measurement-path failure

GS-R2/RV-A (#323): the 84.4% MOR-02 headline was NOT a generalization measurement — the endpoint
reduced to one capability bit and ranking transformed a checker-bearing viable population into a
checker-depleted survivor population; deleting ranking, the unranked lane used 2.13% of campaign
compute and returned 2.21x the held-out-eligible count (~104x per CPU-hour). An optimiser
manufactured a negative by selecting on a proxy. Same class: EB-F0's first noninterference
formulation was vacuous (kernels declared writes, not reads — a leaking world could PASS); D28
F1 (results outside the freeze chain); TTAC enumeration gap (the central claim class was absent,
so closure machinery looked healthy while never scoring it). **Law (#323 HC-4): a negative is
uninterpretable until the measurement path that produced it has survived hostile attack in BOTH
alarm and no-alarm directions.** MOR-02's number decomposes into (i) a real NFL/regime component
and (ii) a proxy-manufactured component; only (i) belongs to RC1.

### 3.6 The revival ledger is itself frontier evidence (verified on main)

The cross-programme revival census (25 negative rows, every attribution re-checked against live
artifacts) shows the negatives flip under EXACTLY the levers the amendment types — no outcome
tuning anywhere:

- **9 of 25 negatives have an executed revival that flipped or re-scoped them.** The flipping
  lever is always cost-structure or admission, never signal quality: h1-v3 measures
  `break_even_n = 35` on the frozen ledger and recoups library capital at n=48 ("Ordinary parent
  ties OCM" — a MEASURED Q* crossover for declarative capital on a related-task stream, i.e.
  rho < 1); FNA-4's utility-gated admission (STITCH+nogoods+CEGIS) turns +1149%/+1279% losses
  into **−26.0%** on an identical fresh stream ("utility-gated admission is load-bearing"); MSC
  E4/E5 demand-driven scheduling beats the parent 1.16x/1.47x (Q2) and 1.18x/2.16x (Q5) where
  the STATIC construction lost 2.03x/4.05x/12.7x — pay the capital per-query where demanded,
  never upfront: the construction-floor law WITH its lawful revival.
- **The three weakest lanes (SEV, GEF, SPX) never reached mechanism**: SEV-01's frozen
  comparator is `NOT_IMPLEMENTED_ALL_PARENTS`; SEV-02's matched parents 7/8 NOT_RUN; GEF ran 0
  of E0–E10; SPX k<<N is UNBOUND for instrument reasons (registry sweeps with positive
  controls: 0 measurements). Their terminals are measurement-regime facts — an unimplemented
  comparator must yield CANNOT_CLASSIFY, never a negative (#323 HC-4).
- **Two headline numbers died to null discipline**: MOR-02's 84.4% is permanently unquotable
  (RV-6: ranking was a deterministic 1-bit artifact, draw-invariance 0/18; the surviving L1
  2.21x holds at z=382.95); FQ-2's "adaptive beats fixed" was reproduced by a row-shuffle null
  and retracted (surviving: U_*=5 by enumeration + one genuine depth-distribution residual).
  Rule that survives both: every adaptive-beats-fixed claim carries a shuffle-equal-n null;
  every 1-bit endpoint carries a draw-invariance control.

So the bimodality is even sharper than section 0: economy claims are not merely failing — they
are flipping in sign along exactly the (rho, sigma, d, delta, admission) axes the framework
never froze. The frontier is measurable and partially measured already, by the revival chain
itself.

## 4. The framework amendment (definitions, not tuning) — QUERY_ECOLOGY_AMENDMENT_V1.json

F1. **Type the capital** (reconciled with #323 HC-1's four capitals): solution capital splits
    into structural (partitions/abstractions: self-defeat law; admissible claims are
    delta-relaxed or rho<rho* frontier claims), episodic (cached exact answers: pays iff
    recompute depth > bookkeeping constant — D19's 1.07 is the shallow boundary), declarative
    (libraries/lemmas/macros: pays iff cross-ecology recurrence sigma > sigma*); and the
    capitals OCM has NOT yet demonstrated — search, ecological, assay — are the developmental
    ones (#323 HC-1: stop letting solution-capital positives stand in for search-capital
    development).
F2. **Query ecology is a mandatory freeze parameter**: (rho, sigma, d, delta) declared in every
    world-family freeze; generators must plant recurrence at controlled sigma (today they
    generate the worst corner by accident). Operationalizes #323 HDI-1 (environment relativity)
    and HDI-3 (structural relatedness: shared minimal decomposition / operator-support structure
    / valid transport map — never a semantic family label).
F3. **Claim shapes**: unconditional economy claims are deprecated as a shape; frontier endpoints
    Q*(rho,sigma,d,delta), rho*, sigma*, delta* are the admissible objects;
    TRADEOFF_FRONTIER_ONLY atoms get actual swept frontiers.
F4. **Reposition the headline to the trust layer** (replicated, parent-unbeatable
    invariance/detection results); economy modules ride behind the frontier laws; no economy
    claim ships without its measured corner of the frontier.
F5. **Behavioural-receipt rule for developmental claims** (#323 HDI-15 / section 4): history
    must demonstrably alter the search geometry for a target whose solution m* was NOT in
    history — rank_H(t+1)(m*) < rank_H(t)(m*) — else the result is classified reuse, not
    development. Schema: SEARCH_GEOMETRY_RECEIPT_SCHEMA_V1.json.

## 5. Revival studies (pre-registered; SUBORDINATED to DEV-CAL-1)

#323 sets DEV-CAL-1 (oracle-transfer / structural-relatedness calibration) as the immediate
programme priority — no architecture change until transferable headroom is demonstrated and the
failing carrier/stage causally identified. D29-D31 are economy-frontier measurements on EXISTING
machinery (no architecture, no tau, no operator retuning) and are frozen in
ECONOMY_FRONTIER_PROTOCOLS_V1.json:

- D29 crossover frontier: sweep rho x Q on RV_B1 machinery; falsifier = no finite Q*(rho) off
  the rho=1 axis, or Q* non-monotone in rho.
- D30 delta-dial: sweep delta on D20 worlds; delta=0 recovers the D20 negative as the boundary
  of a family; falsifier = no delta in (0,1) at which structural capital beats direct on total
  cost anywhere in the grid.
- D31 episodic depth law: substitution ratio vs recompute depth on D19 machinery; falsifier =
  ratio never drops below 1 with depth.

Each converts a filed negative into the boundary case of a measured law — global recovery by
mechanic/definition change, all costs charged, no outcome tuning.

## 6. Defect classes -> class-level protections (recursive hardening)

Every defect found becomes an invariant, not a local fix — ledgered machine-visibly in
RECURSIVE_HARDENING_V1.json: census derived not hand-copied (gate: derive_census.py + CI),
build-generator divergence fails closed (gate: rebuild-and-diff in CI), frozen-field receipt
schemas emit CANNOT_CHECK rather than silence, duplicate-key JSON banned by schema rule,
frozen artifacts are append-only-verified, results outside a freeze chain are classified
post-freeze-derived or blocked. D28 F1-F7 and B7's four parent-chain defects are the open
inputs; several close in this PR, the rest are owned by task #52.

## 7. What is NOT changing

Frozen worlds, seeds, terminals, claim ceilings, negative findings and the append-only
amendment discipline are untouched; the amendment adds axes, types and gates — it does not
reopen any merged verdict. No tau relaxation, no operator retuning, no safety/adoption gate
weakening (#323 section 11 respected verbatim). The framework stays EXPLICITLY_NON_FINAL.
