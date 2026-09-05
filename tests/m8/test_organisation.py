"""M8 §1–§8: arms over one space, macro invariant, transport warrant, containment, worlds and
recovery, cross-scale navigation vs flat, learned proposals refuse free complexity."""
from __future__ import annotations

from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.organisation import arms as A
from ocm.organisation import interface as I
from ocm.organisation import navigate as NV
from ocm.organisation import worlds as W


def test_worlds_are_deterministic_and_oracle_recovery_is_exact_for_communities():
    w1, w2 = W.generate("clean_hierarchy"), W.generate("clean_hierarchy")
    assert w1.world_id == w2.world_id and len(w1.latent_regions) == 4 and all(len(r) == 8 for r in w1.latent_regions)
    arm = A.CommunityArm(w1.ks)
    rec = W.partition_recovery(w1.latent_regions, tuple(r.atoms for r in arm.regions()))
    assert rec["exact_regions"] == 4, rec
    hand = A.HandTreeArm(w1.ks, w1.labels)
    assert W.partition_recovery(w1.latent_regions, tuple(r.atoms for r in hand.regions() if r.region_id != "root"))["exact_regions"] == 4
    # misleading labels: the hand tree recovers nothing exactly, communities still do
    wm = W.generate("misleading_hierarchy")
    assert W.partition_recovery(wm.latent_regions, tuple(r.atoms for r in A.HandTreeArm(wm.ks, wm.labels).regions() if r.region_id != "root"))["exact_regions"] == 0
    assert W.partition_recovery(wm.latent_regions, tuple(r.atoms for r in A.CommunityArm(wm.ks).regions()))["exact_regions"] == 4


def test_macro_invariant_transport_warrant_and_containment():
    w = W.generate("clean_hierarchy")
    arm = A.CommunityArm(w.ks)
    r0 = arm.regions()[0]
    m = arm.macro(r0.region_id)
    assert set(m.exported_claims) == set(r0.atoms) and m.warrant_summary.evidence <= w.ks.evidence_universe()
    assert I.macro_liveness(w.ks, m, ()) is Liveness.LIVE
    all_ev = {e for a in r0.atoms for wv in w.ks.atom(a).warrant.lower for e in wv}
    assert I.macro_liveness(w.ks, m, all_ev) is Liveness.DEAD             # every child dead ⇒ macro dead
    one = next(iter(all_ev))
    assert I.macro_liveness(w.ks, m, {one}) is Liveness.UNKNOWN            # partial support ⇒ not LIVE
    assert I.mutant_macro_cache(w.ks, m, Liveness.LIVE) is Liveness.LIVE   # the hostile cache
    tm = I.TransportMap("t", "c0", "c1", {"r0a0": "r1a3"}, ("ctx0",), ("dependence",), ("weights",), WarrantProfile.of({"corr1"}))
    tw = I.transported_warrant(w.ks, tm, "r0a0")
    assert tw.liveness({"corr1"}) is Liveness.DEAD and tw.liveness(()) is Liveness.LIVE
    assert I.mutant_transport_similarity_as_proof(tm, 0.9).liveness({"corr1"}) is Liveness.LIVE   # the hostile
    ok, why = I.containment_consistent([I.Region("a", frozenset({"x", "y"}), ("b",)), I.Region("b", frozenset({"x", "y"}), ("a",))])
    assert not ok and "cycle" in why
    assert not I.containment_consistent([I.Region("a", frozenset({"x", "z"}), ("b",)), I.Region("b", frozenset({"x"}), ())])[0]


def test_cross_scale_navigation_finds_with_fewer_visits_and_reports_refine_required():
    w = W.generate("cross_domain_bridges")
    arm = A.CommunityArm(w.ks)
    fl = NV.flat(w.ks, "r0a0", "r0a4")
    cs = NV.cross_scale(arm, w.ks, "r0a0", "r0a4")
    assert cs.outcome == "FOUND" and fl["outcome"] == "FOUND" and cs.visited <= fl["visited"]
    far = NV.cross_scale(arm, w.ks, "r0a0", "r3a4", max_regions=1)
    assert far.outcome == "REFINE_REQUIRED" and far.missed_region
    # revoking the target's evidence: GAP at every level, never FOUND
    ev = next(iter(next(iter(w.ks.atom("r0a4").warrant.lower))))
    assert NV.cross_scale(arm, w.ks, "r0a0", "r0a4", revoked={ev}).outcome != "FOUND"
    # a certified query answers from the macro without descent; an uncertified one must descend
    mac = NV.cross_scale(arm, w.ks, "r0a0", "r0a4", certified_queries=[f"{arm.regions_of('r0a4')[0]}:r0a4"])
    assert mac.answered_from_macro and not mac.descended
    assert NV.mutant_summary_answers_outside_scope(arm, w.ks, arm.regions_of("r0a4")[0], "r0a4", ()) == "FOUND"   # the hostile


def test_learned_arm_adopts_only_realised_improvements_and_refuses_free_complexity():
    w = W.generate("dynamic_topology")
    arm = A.LearnedArm(w.ks)
    n0 = len(arm.regions())

    def evaluate(regions):
        # objective vector on a task stream: success and navigation cost (fewer visits better)
        org = type("O", (), {"regions": lambda self: regions, "regions_of": lambda self, a: [r.region_id for r in regions if a in r.atoms], "macro": lambda self, rid: I.macro_for(w.ks, next(r for r in regions if r.region_id == rid)), "transports": lambda self: []})()
        succ = vis = 0
        for s, t in w.tasks:
            res = NV.cross_scale(org, w.ks, s, t, max_regions=4)
            succ += int(res.outcome == "FOUND")
            vis += res.visited
        return {"task_success": succ / len(w.tasks), "navigation_cost": -vis / len(w.tasks)}

    base = evaluate(arm.regions())
    props = arm.propose(evaluate)
    assert props and all(p.op in ("split", "merge") for p in props)
    adopted = [arm.adopt(p, evaluate, base_heldout=base) for p in props]
    # every adopted proposal realised a predicted improvement on the held-out vector with no regression;
    # every refused one either predicted no gain, regressed, or only grew the topology
    for h in arm.history:
        if h["adopted"]:
            assert any(h["predicted"][k] > 0 and h["heldout"][k] > base[k] for k in h["heldout"])
            assert not any(h["heldout"][k] < base[k] - 1e-9 for k in h["heldout"])
    assert arm.describe()["learner_cost"] > 0
    # the hostile adopts a split regardless of benefit
    n1 = len(arm.regions())
    split = next(p for p in props if p.op == "split")
    assert A.mutant_reward_complexity(arm, split) and len(arm.regions()) >= n1
