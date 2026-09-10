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
   "DISPATCHED", "laptop billy (lane RV-B1)",
   "If incremental refinement STILL loses, PARENT_SUFFICIENT is EARNED at a deeper level and is filed as a SUCCESS terminal with the stronger statement, not tuned. Never engineer past a parent that genuinely owns the function.",
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
   "GS-R2: 85,025 of 100,693 distinct T2-viable survivors FAIL T3 generalization - 84.4%.",
   "PR #279, commit b434c55c, results/GS_R2_AGGREGATE.json t3_summary",
   "NOT YET ATTRIBUTED. Four candidates must be discriminated by evidence before any lever is applied: descriptor/representation overfit to T2; gate leakage (GATE_CORRECTNESS 295,871 and GATE_CAPABILITY_FLOOR 64,910 admitting on a T2-correlated criterion); selection pressure (the search optimises distinct-yield, which dedup_promotion raised 2.60x, so higher yield may actively buy more non-generalizers); or genuine non-generalizing morphology.",
   "NONE - attribution is the first deliverable, and applying a lever before attributing would be the diffuse-effort defect the doctrine forbids",
   "DETERMINED BY ATTRIBUTION. Explicitly forbidden: moving a threshold, re-drawing the T3 key, re-splitting after seeing results, or loosening a gate to raise the hold rate.",
   "GSA2_hetero (5062.7 distinct_t2_viable_per_seed, 354,046 morphologies/cpu-hour) and GSA5_surrogate (2233.3, 72,150), plus a shuffle-equal-n null",
   "DISPATCHED", "LUNARC nuc partition (96/96 nodes idle, 7-day limit) - the flagship compute study",
   "An honest 'the 84.4% is real, and here is the mechanism' is a valid and valuable outcome. A proven-structural obstruction plus the adjacent scoped positive is also a success.",
   1,
   "Largest retained negative in the repository. Every claimed improvement needs hold RATE, absolute hold COUNT, and the shuffle null together - a lever that raises the rate by admitting fewer candidates has improved selectivity, not generalization."),

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
      "#165 disposition table; re-attributed against research/functional-neural-absorption-v1/fna4_library_synthesis/ "
      "FNA4_RESULTS.json and FNA4_REPORT.md at origin/main",
      "ADMISSION RULE, not abstraction-search cost. The earlier 'abstraction stage' attribution was taken from the "
      "parent literature by analogy and is REFUTED by our own FNA-4 receipt. In FNA4_RESULTS.json main.arms, the "
      "STITCH arm carries the HIGHEST marginal acquisition of any arm - 240,294,343 units against NO_LIBRARY's "
      "64,305, a factor of 3,737 - and is nevertheless the only arm that pays. Acquisition cost therefore does not "
      "discriminate the paying arm from the failing ones, so it cannot be the failing stage. What does discriminate "
      "is the ADMISSION criterion. Utility-gated admission (STITCH) reaches 327,886 units on the fresh 16-task "
      "stream against the incumbent's 366,072 (-10.5%); recurrence-gated admission is actively HARMFUL on the same "
      "substrate - AU_PAIR (Reynolds lgg) 4,576,312 (+1149%) and EGGRAPH (egg saturation) 5,050,822 (+1279%). The "
      "misfire counts isolate the mechanism exactly: AU_PAIR 451,582 and EGGRAPH 286,120 against STITCH's 16,813 "
      "and the incumbent's 7,166. That is high match cost at near-zero applicability - precisely the quantity "
      "Minton's utility formula charges, Utility = (AvrSavings x ApplicFreq) - AvrMatchCost (AAAI-88 p.566), and "
      "precisely the failure his admission test exists to prevent.",
      "HIGH - established against our own receipts across 8 arms on one frozen substrate, not by analogy. The "
      "discriminating variable is isolated: acquisition cost is anti-correlated with success, admission rule is not.",
      "ALREADY APPLIED AND SUCCESSFUL - there is nothing left to swap. FNA-4's own terminal records it: "
      "PARENT_SUFFICIENT_FOR_EXPERIENCE_CONSOLIDATION_AT_REGISTERED_SCOPE, with C_future(T | E_t) < "
      "C_future(T | E_0) CONFIRMED with every cost charged, 270,829 < 366,072 units on an identical 16-task fresh "
      "stream (-26.0%), by the classical arm STITCH + per-batch nogoods + CEGIS. The lane states the mechanism in "
      "its own words: 'utility-gated admission (Stitch) is load-bearing' and 'recurrence-gated admission (Reynolds "
      "AU, e-graph) is HARMFUL on this substrate'. Note the terminal is PARENT_SUFFICIENT: a classical stdlib-only "
      "non-neural parent owns this function, so no ORION-OCM-specific attribution is available for it.",
      "NOT the lever - the lever is spent. The open quantity is the HORIZON. FNA-4 measures the fresh-stream "
      "per-task inequality at 16 tasks but places break-even for the 240,294,343-unit marginal acquisition at "
      "~6,123 tasks at zero repeat, a 380x extrapolation beyond the measured stream. So H1's per-task inequality "
      "is confirmed at registered scope while H1's LIFETIME repayment claim - the thing "
      "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS actually asserts - remains PROJECTED, not observed. The decisive "
      "re-test is a horizon run on the same frozen substrate long enough to cross or miss 6,123 tasks, with "
      "acquisition and later savings tracked separately, against the same 8 arms.",
      "REVIVAL_ALREADY_EXECUTED_AT_REGISTERED_SCOPE - #165 RECONCILIATION OUTSTANDING",
      "no new run needed for the lever; horizon run to a compute lane (billy-old ran FNA-4)",
      "Any morphology or library atom touching acquisition economics must engage with this negative rather than "
      "talking past it - and must now also engage with FNA-4's registered-scope POSITIVE, which #165's disposition "
      "table does not yet reflect. Reporting H1 as an unqualified capital negative is, as of FNA-4, a defect.",
      2,
      "REGIME BOUNDARY LOCATED, AND IT IS NOT IN THE PARENT LITERATURE. A primary-source sweep of the utility-problem "
      "literature (Minton AAAI-88; Tambe/Newell/Rosenbloom ML 5:299-348 1990; Kennedy & De Jong ICML-2003; Gratch & "
      "DeJong AAAI-92; Greiner & Jurisica AAAI-92) finds a per-rule break-even inequality and formal sample-complexity "
      "conditions for deciding that inequality's SIGN, but no analytic crossover in N. Tambe et al. bound the cost side "
      "structurally and state they give 'no explicit guarantees about the benefits of chunking'; Minton names the gap as "
      "future work, writing that 'there is no such thing as an average domain' and that 'better methods for "
      "characterizing and comparing domains must be developed'. FNA-4 supplies exactly that missing object as a "
      "(mix, horizon) pair: a critical same-family share of 11.8-17.0% of the stream (STITCH alone 17.0% balanced / "
      "24.2% all-F1; combined arm 11.8% / 17.4%; no share pays for CHUNK/AU_PAIR/EGGRAPH) together with the ~6,123-task "
      "break-even horizon. Below the critical share the lane reports NO_LIFETIME_PAYBACK on every horizon. That pair is "
      "the regime boundary to defend and extend, not to rediscover."),
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
