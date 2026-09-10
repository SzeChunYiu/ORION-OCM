import json, collections

OUT = "research/top-tier-atomic-closure-v1/IN_FLIGHT_COORDINATE_MAP_V1.json"

def L(lane, issue, title, status, world, coords, endpoint, guard, anchor, notes=None):
    return {"lane_id": lane, "owner_issue": issue, "title": title, "status": status,
            "frozen_world": world, "readiness_coordinates_targeted": coords,
            "primary_endpoint": endpoint, "duplication_guard": guard,
            "evidence_anchor": anchor, "notes": notes}

lanes = [
 L("D12", 233, "five-arm calibration", "LANDED_AND_SCORED", None, ["M"],
   "calibration of the five-arm comparison",
   "Do not re-run the five-arm calibration; cite the scored result.",
   "#233 comment 'D12 five-arm calibration: ALL LANDED + SCORED'",
   "Internal replay of a landed study never exceeds R=2 under the frozen ladder."),

 L("D13", 233, "atlas expansion / mechanism cross-index V1 (12-term vocabulary + coverage-matrix OPEN-cell routing)",
   "MERGED", None, ["T", "G"],
   "mechanism vocabulary + coverage matrix with OPEN-cell routing",
   "Do not re-derive the 12-term vocabulary or rebuild the coverage matrix; extend it.",
   "PR #266, commit 833e1f10"),

 L("D15", 233, "arm A6 protocol-frozen log/receipts, then reveal + verdicts", "MERGED", None, ["M", "C"],
   "cross_partition_probe_share MEASURED; verdicts revealed post-freeze",
   "Do not re-open D15 scoring; the reveal already happened against a pre-registered freeze. Re-scoring after reveal is a defect.",
   "PR #273 commit e5dcfb28 (pre-reveal log); PR #274 commit 5a222768 (reveal + verdicts)"),

 L("D16", 233, "freeze HSG-v4 semantic-execution capsule V1 (T65-T94, worlds, hostiles, parents)",
   "MERGED", "OW1-OW10 defined here", ["T", "P"],
   "frozen theorem/world/hostile/parent capsule",
   "OW1-OW10 are FROZEN. Define no competing world set; instantiate these.",
   "PR #272, commit 72a2c43b"),

 L("D16b", 233, "parent primary-source verification (25/25) + FREEZE amendment V1.1", "MERGED", None, ["P"],
   "25/25 parent claims verified against primary sources",
   "Do not re-verify these 25 parents; cite them and extend to new parents only.",
   "PR #276, commit 65ded44e",
   "IMPORTANT CEILING: source verification confirms what a parent CLAIMED. The frozen schema requires a "
   "faithful parent RUN at matched information/resources/checker access before P can reach 3. "
   "D16b therefore does NOT lift P to 3 for any atom. NOT_RUN stays 1."),

 L("D17", 233, "machine-check the elementary theorem tranche", "MERGED", "OW1", ["T"],
   "exact machine checks over the elementary tranche",
   "Reuse exact/engine.py, worlds.py, oracles_d17.py, run_all.py. Do not fork a second exact engine.",
   "PR #275, commit 84b127a7"),

 L("D18", 233, "common obligation-hypergraph / semiring engine", "MERGED", "OW1", ["T", "M"],
   "semiring obligation engine with receipts",
   "The semiring engine is the shared substrate for D19-D22. Extend it; do not reimplement.",
   "PR #275, commit 84b127a7"),

 L("D19", 233, "provenance + revocation worlds", "MERGED", "OW4", ["T", "M"],
   "exact agreement of accepted/reopened obligations (primary); touched-state and lifecycle burden (secondary)",
   "LANDED. Do not re-run; extend. OW4/OW4N generators and the A1/A2/A3 arms are frozen.",
   "PR #282, commit 78259460; results at exact/results/D19_RESULTS.json",
   "verdict EXACT_AGREEMENT on the positive control (OW4, 8 worlds, zero blockers, 50 revocation subsets "
   "exhausted: 50/50 accepted and 50/50 reopened). On the negative-dependency population (OW4N, 46 subsets) "
   "the terminal is CANNOT_CHECK_NEGATION_PRESENT (40/46 accepted, 31/46 reopened) because positive-only "
   "N[X] launders the blocker - a legitimate CANNOT_CHECK naming a missing instrument, not a resource "
   "shortage. evidence_class CONFIRMATORY_FIXED; claim ceiling P2 finite certificate, never universal. "
   "Lifecycle burden is nearly a wash: substitution 598 ops vs recomputation 640, a 7 percent margin with "
   "no-op revocations charged in full. Incidental scope caveat on the frozen T72 oracle: it revokes over "
   "the world's leaves field, a superset of true sources, so 11 of its revocation targets are no-ops and "
   "6 true sources are never revoked; D19 reports the count and makes no claim that T72 is wrong. Both "
   "hostiles flipped and both clean controls stayed silent. Prior attempt at this lane died holding "
   "uncommitted work and left no recoverable artifact (host copy verified byte-identical to main)."),

 L("D20", 233, "abstraction/refinement/CEGAR worlds", "MERGED", "OW5", ["M", "C", "S"],
   "refinement count, n-k exact ceiling, states distinguished, search saved/added, verification cost, false abstraction certificates",
   "LANDED. Do not re-run; extend. The n grid [8,12,16,20,24] and the 30 worlds are frozen.",
   "PR #283, commit 7a6427e9; results at exact/results/D20_RESULTS.json",
   "primary endpoint CEILING_HELD: refinement count <= n-k on 30 worlds at every n, zero violations, zero "
   "conclusive-verdict mismatches against direct search. THE SUBSTANTIVE RESULT IS THE NEGATIVE: terminal "
   "PARENT_SUFFICIENT - adaptive refinement does not beat direct concrete search anywhere in the frozen n "
   "grid; direct concrete search already owns the function at this scale. One-stage attribution: abstraction "
   "CONSTRUCTION, not abstract SEARCH - every CEGAR round rebuilds from the full concrete transition "
   "relation, so one round already costs a full concrete sweep and a 4x smaller abstract state space cannot "
   "repay a build that is linear in the concrete edge count. evidence_class CONFIRMATORY_FIXED for the "
   "ceiling and EXPLORATORY_ADAPTIVE for refinement-cost regions (never headline). All three hostiles "
   "flipped, all three clean controls silent. Recorded supersession S1: the frozen H-D20b instantiation had "
   "an empty drop-candidate set on 7 of 15 concretely-UNSAFE worlds, making them structurally immune to the "
   "plant; re-instantiated exhaustively, affected arms re-run, frozen result retained, no world, seed, grid, "
   "endpoint or clean control altered. 'false abstraction certificates' is a construct-validity endpoint, "
   "not a performance one - it is the M contribution."),

 L("D21", 233, "reduction + equality-saturation worlds", "IN_FLIGHT", "OW6", ["P", "S"],
   "direct solve vs one-shot rewrite vs ordered rewriting vs Knuth-Bendix vs equality saturation vs learned reduction library; "
   "single injected unsound rewrite must be caught",
   "Owned by an active lane on host billy-old, branch hsg/d21-d22-labs. Do not start a second reduction lane.",
   "dispatched 2026-09-10",
   "This lane is a genuine parent-subtraction lane: its arms ARE the strongest parents for reduction. "
   "Present cost and future reuse must be tracked separately per T27/T87."),

 L("D22", 233, "heterogeneous-logic transport", "IN_FLIGHT", "OW7", ["T", "G"],
   "satisfaction conditions, consequence preservation, model-expansiveness, hostile incomplete model images",
   "Owned by the same active lane (billy-old, hsg/d21-d22-labs). Lean/SMT adapters stay OUT — N4 is locked.",
   "dispatched 2026-09-10"),

 L("D23", 233, "language semantic round-trip laboratory", "PARTIALLY_LEGAL_N2_LOCKED", "OW3", ["M", "E"],
   "I/R/J coverage, protected round-trip error, ambiguity-set size, clarification value, abstention, latency, B_exec",
   "Synthetic/frozen semantic tuples are legal NOW. Protected N2 outcomes are LOCKED — do not touch them.",
   "#233 FREEZE_V1 locks N2",
   "The metric contract must be fixed BEFORE N2 unlocks. Inventing a metric after seeing fluency is the "
   "exact gaming failure #277 sec 3 targets."),

 L("D24", 233, "math/proof laboratory", "PARTIALLY_LEGAL_N4_LOCKED", None, ["T", "P"],
   "proof DAGs, lemma reuse, proof-neutral sets, SMT fragments, rewrite/e-graph algebra, proof-carrying candidate admission",
   "Synthetic finite theorem worlds are legal now. Lean/miniF2F-style protected N4 outcomes are LOCKED; "
   "do not bypass #42 to reach them early.",
   "#233 FREEZE_V1 locks N4"),

 L("D25", 233, "general problem-solving laboratory", "NOT_STARTED", "OW8", ["G", "S"],
   "search phase diagrams across flat STRIPS / verified reductions / HTN / POMDP belief-state / options-macros, after complete cost",
   "Not started. Hierarchy-NEGATIVE regions must be retained explicitly when it runs.",
   "#233 comment 'D25 — general problem-solving laboratory'"),

 L("D26", 233, "cross-domain operator-transfer test", "NOT_STARTED", "OW9", ["G"],
   "transfer of the invariant contract for DISTINGUISH / REFINE / REDUCE / VERIFY across >=3 materially different domains",
   "Not started. G is its sole target - D22 and D25 touch G alongside other coordinates, but this is the only lane devoted to it.",
   "#233 comment 'D26 — cross-domain operator-transfer test'",
   "Load-bearing: a general operator claim requires transfer of the invariant CONTRACT, not reuse of the name. "
   "Every 'general operator' atom is gated on this lane."),

 L("D27", 233, "developmental semantic execution", "NOT_STARTED", "OW10", ["C", "P", "S"],
   "CONTINUED vs RESET vs strongest persistent parent: B_exec, first-useful-solution hitting time, new information required, "
   "counterexamples required, verification calls, active k / total N",
   "Not started. This is the direct bridge from semantic competence to the developmental thesis.",
   "#233 comment 'D27 — developmental semantic execution'",
   "Highest-value uncovered lane: it is the causal knockout for DEVELOPMENTAL_LINEAGE atoms, whose closure "
   "profile demands C>=4. Nothing else in flight can raise C for those atoms."),

 L("D28", 233, "fresh-context hostile/claims review + downstream integration", "NOT_STARTED", None, ["A", "R"],
   "independent replay of theorem proofs/certificates, parent claims, freeze chain, negative results, coverage, cross-issue hooks",
   "Not started. Must run AFTER D19-D27, and no locked milestone criterion may be changed retroactively.",
   "#233 comment 'D28 — fresh-context hostile/claims review'"),

 L("CONT-CORE", 221, "HSG continuous calibration core V1 (uncertainty ledger, executable router, bank builder, sweep runner, scheduler)",
   "MERGED", None, ["M", "S"], "calibrated uncertainty ledger + executable routing",
   "Do not build a second scheduler or router; extend this one (#277 sec 6 asks it to schedule by weakest high-value coordinate).",
   "PR #268, commit 2aa550ef"),

 L("CONT-SCHED", 221, "scheduler sbatch time limit + failed-submit resilience", "MERGED", None, ["S"],
   "scheduler robustness", "Do not re-fix; extend.", "PR #269, commit b309e704"),

 L("CONT-CAL", 221, "authoritative LUNARC calibration evidence (CONT-CAL-01/02/03, determinism-verified)",
   "MERGED", None, ["M", "R"], "determinism-verified calibration on LUNARC",
   "Do not re-run CONT-CAL-01/02/03; cite them.",
   "PR #271, commit d4fe94db",
   "Determinism verification across hosts is a genuine step toward R, but cross-host determinism of the same "
   "implementation is NOT disjoint replication. R stays capped at 2 for atoms resting only on this."),

 L("GSA6", 221, "GSA6 revival levers (novelty-gated allocation, promotion dedup, holdout-MAE fix, cumulative surrogate)",
   "MERGED", None, ["M"], "levers landed, flags default-off except the NaN fix",
   "Do not re-land the levers.", "PR #270, commit ad046014"),

 L("GS-R2", 221, "Grand Search round 2 (5 arms x 6 seeds, 30/30 receipts)", "MERGED", None, ["P", "S"],
   "LEVER_PACKAGE_BEATS_SURROGATE_PARENT_ONLY; dedup_promotion owns the distinct-yield recovery vs the SURROGATE parent only",
   "Do not re-run GS-R2 under the same freeze; a re-run requires a new frozen protocol.",
   "PR #279, commit b434c55c; GRAND_SEARCH_R2_FREEZE.json sha 55a96624",
   "EVIDENCE CLASS IS EXPLORATORY_ADAPTIVE -> caps at readiness 2 PERMANENTLY under the frozen ladder; "
   "confirmation requires a NEW frozen study. RETAINED NEGATIVES, read from the merged artifact rather than "
   "from a lane summary: (a) the frozen parent GSA2_hetero is unbeaten on throughput (354,046 vs GSA6_DP "
   "190,527 morphologies/cpu-hour) though GSA6_DP does exceed it on distinct_t2_viable_per_seed "
   "(5802 vs 5062.7) at roughly double the cpu-seconds per seed - so which arm wins depends on the metric, "
   "which is itself a sec-3 measurement-validity finding; (b) two of three levers did not carry the recovery "
   "(GSA6_NG 2202, GSA6_SC 1723 distinct/seed, both below the GSA5P_fixed replication at 2251); "
   "(c) 85,025 of 100,693 distinct survivors FAIL T3 generalization (84.4%). Any morphology-search atom must "
   "lead with (c), not with the 2.60x. terminal_rule_id=LEVER_PACKAGE_BEATS_SURROGATE_PARENT_ONLY, "
   "terminal_vocab=MORPHOLOGY_SEARCH_COST_DOMINATES."),

 L("TTAC-D5", 277, "external cognitive input / autonomy ledger", "MERGED", None, ["A"],
   "audit separating externally supplied cognition from internal discovery",
   "Do not open a second autonomy ledger; append to this one.",
   "PR #280, commit 7c90dc8c",
   "Verdict is NEGATIVE: zero audited inputs changed the OCM's F/O/Pi, so A cannot be lifted by the ledger."),
]

cov = collections.Counter()
for l in lanes:
    if l["status"] in ("IN_FLIGHT", "PARTIALLY_LEGAL_N2_LOCKED", "PARTIALLY_LEGAL_N4_LOCKED"):
        for c in l["readiness_coordinates_targeted"]:
            cov[c] += 1
allcov = collections.Counter()
for l in lanes:
    for c in l["readiness_coordinates_targeted"]:
        allcov[c] += 1

COORDS = ["T", "P", "M", "C", "G", "S", "R", "A", "E"]

doc = {
  "schema": "TTAC_IN_FLIGHT_COORDINATE_MAP",
  "version": "V1",
  "d_step": "TTAC-D6",
  "owner_issue": 277,
  "built_utc": "2026-09-10",
  "purpose": ("#277 sec 9 D6: map current #233 D17-D28 and #221 continuous jobs onto readiness coordinates "
              "so they are counted, not duplicated. This artifact assigns NO readiness values — assignment is D2."),
  "rule": "A lane is mapped to the coordinates its PRIMARY ENDPOINT can move, not to every coordinate it touches incidentally.",
  "lanes": lanes,
  "coordinate_coverage_all_lanes": {c: allcov.get(c, 0) for c in COORDS},
  "coordinate_coverage_in_flight_or_legal_now": {c: cov.get(c, 0) for c in COORDS},
  "uncovered_by_any_in_flight_lane": [c for c in COORDS if cov.get(c, 0) == 0],
  "findings": [
    ("R (replication) is targeted by NO lane that is in flight or legal now. D28 is the only lane naming it and "
     "it has not started. Under the frozen ladder internal replay never exceeds 2, so every atom resting on "
     "in-repo replay is capped at R=2 today. E4 disjoint replication has no owner."),
    ("E (external/ecological validity) is targeted only by D23, which is gated on the N2 unlock. No lane can "
     "raise E for any atom right now."),
    ("A (autonomy) is targeted only by TTAC-D5 and by D28, which has not started. D5's verdict is negative, so "
     "A is gated rather than raised. DEVELOPMENTAL_LINEAGE closure needs A>=4 (clean-room); nothing in flight "
     "can reach it."),
    ("C (causal evidence) is targeted in flight only by D20, and only for abstraction/refinement. The causal "
     "knockout that DEVELOPMENTAL_LINEAGE atoms need (C>=4) belongs to D27, which has not started. D27 is "
     "therefore the highest-value unstarted lane."),
    ("G (generalization) is targeted in flight only by D22 (logic transport). The operator-contract transfer "
     "test that general-operator claims need is D26, unstarted."),
    ("G is further undercut by a landed result, not only by missing lanes: GS-R2 records 85,025 of 100,693 "
     "distinct survivors FAILING T3 generalization (84.4%). Generalization is not merely unmeasured in the "
     "morphology area; where it HAS been measured it is largely negative, and that negative is retained."),
    ("Landed studies carrying evidence_class EXPLORATORY_ADAPTIVE (GS-R2) cap at readiness 2 permanently under "
     "the frozen ladder. D2 must not score them at 3 on the strength of their sample size or receipt count."),
    ("P (strongest-parent subtraction) has real in-flight coverage via D21 (its arms ARE the parents) and "
     "landed coverage via GS-R2. But D16b verified parent SOURCES, not parent RUNS: under the frozen rule "
     "NOT_RUN stays 1, so P is far weaker across the registry than the 25/25 verification suggests."),
  ],
  "consequence_for_D3": ("The blocker DAG should treat R, E and A as structurally unowned, and D27 (causal knockout) "
                         "and D26 (operator transfer) as the two unstarted lanes with the largest downstream unlock. "
                         "D3 selects the critical path; this map only reports what is and is not currently owned."),
  "amendments": [
    {"id": "A1", "utc": "2026-09-10",
     "cause": "D19 and D20 landed on main after this map was first built; their rows are refreshed from IN_FLIGHT to MERGED and their terminals recorded from the merged result files, not from PR bodies.",
     "rows_changed": ["D19", "D20"],
     "readiness_values_assigned": "none - this map still assigns no readiness values; scoring remains D2",
     "coverage_note": "in-flight coverage necessarily falls as lanes land; the structural gaps R, A and E are unchanged, since neither landing targets them"},
    {"id": "A2", "utc": "2026-09-10",
     "cause": "governance finding added after verifying the freeze chain against main",
     "finding_added": "freeze_chain_enforcement"}
  ],
  "freeze_chain_enforcement": {
    "verified_utc": "2026-09-10",
    "state_on_main": "INTACT - 7 of 7 recorded files match when each is resolved through the newest recorded amendment (2 via the D19/D20 amendment S1, 5 via prior_manifest as untouched); zero unrecorded drift",
    "finding": "ZERO of the 53 workflows in .github/workflows references the hsg lane, the freeze builder or the exact suite. The freeze chain is DISCIPLINE-ENFORCED, NOT GATE-ENFORCED.",
    "why_it_matters": "A frozen artifact can come to assert something false with nothing to catch it. Live instance: FREEZE_D19_D20_V1.json records prior_manifest_sha256_observed for EXPERIMENT_REGISTRY_V1.json and HOSTILE_REGISTRY_V1.json plus prior_unamended_files_still_match_v1_0=true; the pending D21/D22 amendment V1.2 modifies both files, which would falsify that assertion silently. The owning lane was asked to record the supersession from its own side before merging, rather than editing another lane's landed freeze artifact.",
    "verification_method_caveat": "Comparing the TOP-LEVEL manifest_sha256 against the live tree reports FALSE drift on any file carrying a legitimate recorded amendment. Resolve each file through the newest amendment naming it, fall back to the original manifest, and assert separately that unamended files still match. This false positive was hit and fixed once by the D19/D20 lane's own builder and once by an ad-hoc check here - recorded because the checker was wrong before it was right.",
    "disposition": "OPEN defect, recorded rather than silently dropped: an integrity mechanism with no enforcement gate. Candidate D4 hostile family - 'a freeze assertion becomes false and no gate notices'."
  },
  "non_final": True
}

with open(OUT, "w") as fh:
    json.dump(doc, fh, indent=1)
    fh.write("\n")
print("wrote", OUT)
print("lanes:", len(lanes))
print("coverage in-flight/legal-now:", {c: cov.get(c, 0) for c in COORDS})
print("uncovered by in-flight:", [c for c in COORDS if cov.get(c, 0) == 0])
