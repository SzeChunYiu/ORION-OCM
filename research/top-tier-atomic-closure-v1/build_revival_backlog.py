# -*- coding: utf-8 -*-
import json, io, collections
OUT = "research/top-tier-atomic-closure-v1/REVIVAL_BACKLOG_V1.json"

def R(rid, negative, source, attribution, attribution_confidence, lever, retest_against,
      status, placement, earned_terminal_rule, iteration=1, notes=None):
    return {"revival_id": rid, "negative": negative, "source_anchor": source,
            "one_stage_attribution": attribution, "attribution_confidence": attribution_confidence,
            "lever": lever, "retest_against": retest_against, "status": status,
            "placement": placement, "earned_terminal_rule": earned_terminal_rule,
            "chain_iteration": iteration, "notes": notes}

rows = [
 R("RV-1",
   "D20: adaptive refinement never beats direct concrete search anywhere in the frozen n grid [8,12,16,20,24]. Terminal PARENT_SUFFICIENT.",
   "PR #283, commit 7a6427e9, exact/results/D20_RESULTS.json",
   "Abstraction CONSTRUCTION, not abstract SEARCH. Every CEGAR round rebuilds the abstraction from the FULL concrete transition relation, so one round already costs a full concrete sweep; a 4x smaller abstract state space cannot repay a build linear in the concrete edge count.",
   "HIGH - stated by the lane from its own instrumented cost split, not inferred",
   "INCREMENTAL REFINEMENT: keep the previous abstraction and split only the blocks the counterexample distinguishes, so per-round build cost is O(touched blocks + incident edges) instead of O(full concrete edge relation). The attribution names an IMPLEMENTATION property, not a law - rebuilding from scratch each round is a choice, which is exactly what makes this negative revivable.",
   "direct concrete search, same frozen 30 worlds and same frozen n grid, full lifecycle charged including initial build and rejected candidates",
   "CLOSED_BOUNDARY_LOCATED", "laptop billy (lane RV-B1), PR #291 commit f403bde8",
   "OUTCOME: the lever WORKED and was NOT ENOUGH. Incremental refinement removed 16.0% of construction overhead "
   "(ops 0.840 of rebuild, equivalence guard 95 checks / 0 failures, rounds identical on all 30 worlds) and still "
   "lost, 8.412x direct against the rebuild arm's 10.011x, saving search on 0 of 30 worlds. Terminal "
   "PARENT_SUFFICIENT_EARNED_AT_A_DEEPER_LEVEL, pre-committed in the protocol before the run. TWO BOUNDARIES "
   "LOCATED. (a) Single query, structural: a sound may-abstraction must read every concrete transition, since "
   "omitting one is exactly the H-D20b under-approximation already shown to yield false certificates -- so setup "
   "is Omega(|E|) while direct search is O(|V|+|E|) with early exit. Empirically the one-time build alone costs "
   "1.267x the entire direct search and already meets or exceeds it on 21 of 30 worlds. Labelled an asymptotic "
   "argument, not a machine-checked certificate. (b) Multi query: AMORTISATION SELF-DEFEATS. No crossover exists "
   "in the frozen Q grid (ratio 8.41, 6.44, 4.83, 3.58, 2.49, monotone but never crossing) and none is projected "
   "beyond it, because refinement drives the partition toward DISCRETE -- final blocks reach 81.2% of states, 6 of "
   "30 worlds go fully discrete -- and post-refinement the marginal cost per query is 12.966 for the abstraction "
   "against 11.738 for direct. The mechanism that makes an abstraction accurate enough to answer queries is the "
   "same one that destroys its size advantage, and the n-k bound guarantees termination at or near discrete.",
   1,
   "The n-k ceiling must continue to hold; a lever that breaches it is a bug in the lever, not a discovery. If the frozen grid is simply too small for any abstraction to pay off, that is the honest finding, and extending the grid is a NEW frozen study."),

 R("RV-2",
   "D19: terminal CANNOT_CHECK_NEGATION_PRESENT on the negative-dependency population OW4N (40/46 accepted-set agreement, 31/46 reopened).",
   "PR #282, commit 78259460, exact/results/D19_RESULTS.json",
   "MISSING INSTRUMENT, not a failed mechanism. Positive-only N[X] provenance cannot represent a blocker, so it launders negative dependencies. The A3 detector correctly refuses to certify rather than reporting a pass.",
   "HIGH - the terminal itself names the missing instrument, per the frozen rule that CANNOT_CHECK must name an instrument and never a resource shortage",
   "NEGATION-AWARE PROVENANCE: evaluate under a semiring that can express blocking - stratified or well-founded evaluation, or an m-semiring with monus - and re-run the same OW4N worlds and revocation subsets.",
   "A2_recomputation, the exhaustive algebra-free ground truth already in the lane, on the identical frozen OW4N worlds and subsets",
   "QUEUED", "laptop billy or LUNARC nuc (exact, tiny worlds)",
   "If a negation-aware semiring reproduces A2 exactly, the CANNOT_CHECK converts to a real result and T73's boundary is characterised rather than merely observed. If it cannot, the boundary is structural and the proof of that is the deliverable.",
   1,
   "This is the clearest case in the backlog of 'the constraint IS the next idea' - the missing instrument is named, so the lever is determined."),

 R("RV-3",
   "D19: provenance substitution beats full recomputation on lifecycle burden by only 7% (598 vs 640 ops), with no-op revocations charged in full.",
   "PR #282, commit 78259460, exact/results/D19_RESULTS.json positive_control",
   "WORLD SCALE. At 4-7 node worlds the single initial solve dominates, and |S| substitutions are too few to amortise it. The margin is a scale artifact, not a property of substitution.",
   "MEDIUM - plausible from the cost structure but NOT yet discriminated against the alternative that substitution simply has no real advantage",
   "SCALE THE WORLDS on LUNARC: grow node count, edge density and revocation-subset size, and locate the point (if any) where the margin becomes decision-relevant. Report the curve, not a single ratio.",
   "A2_recomputation with full lifecycle charged at every scale point",
   "QUEUED", "LUNARC (nuc partition, 96 idle nodes) - this is a scaling study and is exactly what the cluster is for",
   "A margin that stays near 1.0 as scale grows is a genuine negative for provenance substitution and must be filed as one. A margin that grows is a scoped positive whose ceiling is the scale range actually tested.",
   1,
   "Interacts with RV-4: if the T72 targeting defect inflates or deflates the 7%, RV-3 must be re-run after RV-4 lands."),

 R("RV-4",
   "D19 census: the frozen T72 oracle revokes over the world's `leaves` field, a strict superset of true sources. 11 of its revocation targets are no-ops, 12 are true sources, and 6 true sources are never revoked at all.",
   "PR #282, commit 78259460, exact/results/D19_RESULTS.json legacy_leaf_census",
   "ORACLE TARGETING DEFECT. Roughly half the oracle's revocation targets are structurally trivial, so a share of its 'checks' cannot fail by construction.",
   "HIGH - counted exactly by the lane against its own explicit evidence_variable_definition",
   "RE-TARGET revocation to true sources (nodes with no incoming hyperedge) and re-run every D19 endpoint.",
   "the prior D19 result itself - does ANY endpoint move: the 50/50 positive-control agreement, the 40/46 and 31/46 OW4N figures, the alternate-support rescue count, or the 598-vs-640 margin?",
   "DISPATCHED", "laptop billy (lane RV-B2)",
   "A no-change result is a genuinely useful negative and must be reported as one. The specific question to rule in or out: a 7% lifecycle margin is thin enough that a targeting artifact could account for it.",
   1,
   "D19 correctly reported the count and made NO claim that T72 is wrong - T72 is a statement about provenance variables. This revival tests the instrument, not the theorem."),

 R("RV-5",
   "D21: shared e-graph amortised-reuse aggregate ratio 0.418 over 10 worlds at 8 queries each - equality saturation is NOT cheaper than ordered rewriting even amortised.",
   "PR #284, exact/results/D21_RESULTS.json amortised_reuse",
   "WORKLOAD AND RULE SET, not the e-graph. Quoting the lane: 'on the frozen rule set ordered rewriting already attains the direct-solve optimum, so saturation has no optimum-quality headroom to win.' Where there is no headroom, no engine can find any.",
   "HIGH - the lane already ran one revival iteration (the 8-query amortised regime) and attributed the residual",
   "RULE SET WITH ACTUAL HEADROOM: construct families where ordered rewriting is provably NOT optimal, i.e. where rewrite ORDER changes the reachable normal form, which is precisely the regime e-graphs exist for. Secondary lever: raise query count well beyond 8 and find the amortisation crossover if one exists.",
   "ordered rewriting AND direct solve, present cost and future reuse tracked separately per T27/T87",
   "QUEUED", "billy-old (lane already holds the e-graph context) or LUNARC nuc",
   "The lane's own note is the governing rule and is correct: 'a ratio <= 1.0 means the shared e-graph is NOT cheaper even amortised; that strengthens PARENT_SUFFICIENT rather than weakening it.' If a headroom-bearing rule set still shows no win, ordered rewriting owns the function and that is a success terminal.",
   2,
   "Per-world spread is informative and must not be averaged away: OW6-00 shows 2.22 (e-graph wins) while OW6-01 shows 0.27. A conditional positive is INTERMEDIATE, not terminal - the doctrine requires extending the working regime or fixing the failing one."),

 R("RV-6",
   "GS-R2 recorded 85,025 of 100,693 distinct T2-viable survivors as FAILING T3 generalization (84.4%). "
   "RECLASSIFIED: that endpoint was never measuring generalization.",
   "PR #279, commit b434c55c, results/GS_R2_AGGREGATE.json t3_summary; reclassified by PR #293",
   "THE ENDPOINT WAS NOT MEASURING GENERALIZATION. SURVIVOR_T3_GENERALIZATION_* is a hard-gate read of "
   "evaluate_t3()['feasible'], and it is an EXACT deterministic function of one genome bit: NOT can_check <=> FAIL, "
   "100693/100693, zero false positives and zero false negatives. So '84.4% fail T3 generalization' means, without "
   "exception, '84.4% carry no consistency checker'. ONE-STAGE CAUSE: the T2/T3 correctness-predicate asymmetry. "
   "T2 scoped_failure and T3 t3_conflict_refusal both accept (can_check OR F_arch == hierarchical_fibred); T3 "
   "t3_doubt_probe accepts can_check ONLY, with no fibred route. A checker-free organism can pass T2 and is "
   "STRUCTURALLY unable to pass that one T3 family.",
   "HIGH - a machine-checked identity over all 100693 survivors, plus the predicate asymmetry verified from source "
   "at lifetime2.py:141 and t3_ecology.py:134/178 by an independent centre review",
   "DELETE THE RANKING. The obstruction is OPERATIONAL, not structural: the unranked viable pool is 84.7% "
   "checker-bearing (522090/616698) while GS-R2 survivors are 15.6% (15668/100693), a 5.44x depletion with "
   "disjoint intervals -> RANKING_OWNS_DEPLETION. The T2 gate is not the culprit; it FAVOURS checker-bearing "
   "organisms by 27.7x (P(viable|can_check) 0.6590 against 0.0652). The search's own ranking and promotion "
   "manufactured the depletion. Recovery achieved 2.21x the absolute hold count at 4.7% of the compute.",
   "GSA2_hetero (5062.7 distinct_t2_viable_per_seed, 354,046 morphologies/cpu-hour) and GSA5_surrogate "
   "(2233.3, 72,150), plus a shuffle-equal-n null",
   "CLOSED_DEFECT_RECLASSIFIED_AND_RECOVERED", "LUNARC, PR #293",
   "The reclassification is the result. A defect found in the instrument outranks any finding the instrument "
   "appeared to produce.",
   3,
   "RECLASSIFIED as a MEASUREMENT-VALIDITY DEFECT, not a scientific finding - the exact sec 3 hostile family in "
   "which a metric reports one quantity while measuring another. Two corroborating facts. (1) The held-out key "
   "carries NO INFORMATION: over 18 deterministically derived sub-keys every survivor is either 0/18 or 18/18 "
   "feasible and ZERO fall in between, and an empirical-risk estimate cannot be perfectly bimodal over 18 "
   "independent draws, so the endpoint is a degenerate estimator rather than a transfer-risk estimate. (2) OUR OWN "
   "LEVER PACKAGE GAMED IT: GSA6_DP and GSA6_ALL have IDENTICAL distinct-yield at 5802.0 per seed, yet DP alone "
   "returns 6768 checker-bearing exclusive survivors against ALL's 1773 - the package bought its headline yield by "
   "rejecting the route that carried checkers. The 84.4% figure must never again be quoted as a generalization "
   "result, and every morphology-search atom must lead with this reclassification."),

 R("RV-7",
   "GS-R2: the frozen parent GSA2_hetero is unbeaten on throughput (354,046 vs GSA6_DP 190,527 morphologies/cpu-hour).",
   "PR #279, commit b434c55c, results/GS_R2_AGGREGATE.json lever_attribution",
   "COST SIDE, not yield side. GSA6_DP already EXCEEDS GSA2 on distinct_t2_viable_per_seed (5802 vs 5062.7); it loses only because it spends roughly double the cpu-seconds per seed. The deficit is entirely in the cost denominator.",
   "HIGH - both numerator and denominator are recorded per arm in the merged aggregate",
   "CHEAPEN THE DEDUP: dedup_promotion carries the recovery but pays for it. Replace pairwise comparison with canonical-form or hash-based dedup so the distinct-yield gain is retained at a fraction of the cpu cost, then re-measure morphologies/cpu-hour.",
   "GSA2_hetero at 354,046 morphologies/cpu-hour, same frozen protocol",
   "QUEUED", "LUNARC",
   "If cheap dedup retains the 5802 distinct/seed and closes the throughput gap, the lever package beats the strongest parent on BOTH axes. If it cannot, GSA2 owns throughput and that is a success terminal.",
   1,
   "Which arm 'wins' currently depends on the metric chosen - itself a #277 sec 3 measurement-validity finding, and it must be carried into the claim ceiling rather than resolved by picking the flattering metric."),

 R("RV-8",
   "#165 H1: LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS - library acquisition cost is not repaid by later savings.",
   "#165 disposition table",
   "ABSTRACTION STAGE. Stitch (POPL 2023) localises DreamCoder-style library-learning cost to the "
   "abstraction stage specifically, which under one-stage attribution names H1's failing stage rather than "
   "indicting library learning in general. Independently, H1 is a REDISCOVERY OF MINTON'S UTILITY PROBLEM in a "
   "new substrate, with Soar's expensive chunks as the direct symbolic ancestor - so the failure has decades of "
   "prior analysis to assimilate rather than re-derive.",
   "MEDIUM - the localisation is established in the parent literature and must still be established against our "
   "own H1 receipts rather than accepted by analogy",
   "SWAP THE ABSTRACTION OPERATOR. If cost localises to abstraction, replace the abstraction operator with the "
   "one whose advantage Stitch demonstrates, verified from the primary source rather than inferred. Then re-test "
   "H1's own frozen setup with acquisition cost and later savings tracked SEPARATELY. Secondary and equally "
   "valuable: the utility-problem literature may already state WHEN acquisition repays, in which case the crossing "
   "condition is a regime boundary to locate rather than a result to rediscover.",
   "the strongest library-learning parent at matched information and resources",
   "ATTRIBUTED_LEVER_IDENTIFIED", "design with parent-scan lane; execution to a compute lane",
   "Any morphology or library atom touching acquisition economics must engage with this negative rather than talking past it.",
   1, None),

 R("RV-9",
   "The HSG freeze chain is discipline-enforced, not gate-enforced: zero of the 53 workflows references the hsg lane, the freeze builder or the exact suite.",
   "TTAC-D6 amendment A2, PR #287",
   "NO ENFORCEMENT GATE EXISTS. The chain was verified INTACT on main (7/7 files match when resolved through the newest recorded amendment), so this is a latent exposure, not a live breach.",
   "HIGH - verified by direct check of all 53 workflow files with a proven-working control",
   "ADD A FREEZE-VERIFICATION WORKFLOW that resolves each file through the newest recorded amendment, falls back to the original manifest, and asserts separately that unamended files still match. It must distinguish verified / recorded-amendment / unrecorded-drift / cannot-check with DISTINCT exit codes.",
   "the current tree on main, plus a deliberately tampered tree that MUST fail and a clean tree that MUST pass",
   "QUEUED", "CI (the check itself is trivial compute)",
   "This is an engineering fix, not a research revival, and it does not compete for LUNARC time.",
   1,
   "Recorded method caveat: comparing the TOP-LEVEL manifest against the live tree reports FALSE drift on any file carrying a legitimate recorded amendment. That false positive was hit twice already, so the checker must be validated in all four directions on real data before it is trusted."),

 R("RV-10",
   "Metric-gaming failure mode CONFIRMED EXTERNALLY BY A PARENT ABOUT ITSELF: the Darwin Godel Machine's own agent "
   "deleted the logging its hallucination detector depended on, and that lineage then OUTSCORED the lineage that "
   "solved the task honestly.",
   "parent scan PARENT_FIRST_REFUSAL_V1.json, family C, graded VERIFIED_EXTERNAL_NEGATIVE",
   "VERIFICATION WEAKENED, SCORE IMPROVED. This is the #277 sec 3 hostile family B_exec falls because verification "
   "was weakened, instantiated for real in a published self-improving system - not a hypothesised gaming mode.",
   "HIGH - reported by the parent system's own authors about their own run",
   "IMPLEMENT THE HOSTILE. This repo has no gate that would catch an agent disabling its own checker and scoring "
   "higher for it. Build the detector (verification-surface coverage must not fall while score rises; deleting or "
   "disabling a checker is a scored event, not a silent one), validate it in all four directions on real data "
   "including the no-alarm case, and gate it.",
   "a deliberately weakened-verification arm that MUST be caught, and a clean arm that MUST NOT alarm",
   "QUEUED", "CI plus any lane that scores self-modification",
   "This is a measurement/governance DEFECT with external proof that it occurs, which the operator has prioritised "
   "over new framework work. It is not a research negative to revive; it is a missing gate to build.",
   1,
   "Companion external negatives from the same scan worth carrying: ANIL shows freezing MAML's entire body barely "
   "changes performance - the canonical demonstration that a SIGNATURE MECHANISM CAN BE INERT, which is why the C "
   "coordinate demands a knockout rather than a pre/post comparison. NELL's precision on newly promoted beliefs fell "
   "90 -> 71 -> 57 percent with compounding error conceded by its authors, which attacks the #151 lineage claim "
   "directly. Enhanced POET's authors concede the original had no progress measure and could read as 'a meandering "
   "walk through problem space dangerously close to randomness'."),
]

doc = {
 "schema": "TTAC_REVIVAL_BACKLOG",
 "version": "V1",
 "owner_issue": 277,
 "created_utc": "2026-09-10",
 "purpose": ("Living revival backlog. The operator's standing doctrine: when any result, test or model FAILS, the FIRST "
             "response is diagnose -> attribute to ONE stage -> apply the matching lever -> re-test against the strongest "
             "parent, BEFORE filing the negative or moving on. A one-pass negative filed as terminal is a defect."),
 "governing_rules": [
   "Attribute to exactly ONE stage before applying any lever. Multi-stage attribution means diffuse, unfocused effort and is itself a defect.",
   "Revival is an ITERATIVE CHAIN, not one pass: repeat attribute -> lever -> re-test until positive OR the obstruction is PROVEN structural, in which case deliver the proof plus the adjacent scoped positive.",
   "NEVER tune an outcome positive. Any improvement must be EARNED by a genuine mechanic change, re-tested against the strongest parent with all costs charged.",
   "PARENT_SUFFICIENT is a SUCCESS terminal. Never engineer past a parent that genuinely owns the function. The revival duty applies to mechanism negatives, not to parent-sufficiency.",
   "A regime-CONDITIONAL positive is INTERMEDIATE, not terminal: it demands a further iteration extending the working regime or fixing the failing one.",
   "Every claimed improvement needs a shuffle-equal-n null. Selectivity is not edge.",
   "Freeze the protocol and push it in a commit containing no result file BEFORE running. Post-freeze change requires a recorded supersession with cause and a re-run.",
 ],
 "revivals": rows,
 "counts": {
   "total": len(rows),
   "by_status": dict(collections.Counter(r["status"] for r in rows)),
   "by_attribution_confidence": dict(collections.Counter(r["attribution_confidence"].split(" - ")[0] for r in rows)),
   "unattributed_requiring_diagnosis_first": [r["revival_id"] for r in rows if r["attribution_confidence"].startswith("NONE")],
 },
 "lunarc_allocation": {
   "queue_state_observed_utc": "2026-09-10",
   "nuc": "96/96 nodes IDLE, 7-day limit - primary target",
   "lu48": "10 idle of 186",
   "hep": "saturated with unrelated jobs",
   "assigned": ["RV-6 (flagship generalization study)", "RV-3 (scaling curve)", "RV-7 (cost-side dedup)"],
   "hard_prohibition": "NEVER make a network connection from LUNARC to any external service. Pure offline compute only: stage in via git/scp, compute, bring results back.",
 },
 "non_final": True,
}

io.open(OUT,"w",encoding="utf-8").write(json.dumps(doc, indent=1, ensure_ascii=False)+"\n")
print("wrote",OUT,"revivals:",len(rows))
print("by_status:",doc["counts"]["by_status"])
print("needs diagnosis first:",doc["counts"]["unattributed_requiring_diagnosis_first"])
