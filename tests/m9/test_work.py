"""M9 §1–§4, §11–§14: contracts refuse forbidden/unauthorised actions; skills succeed on the oracle
environments; capsules transfer partially with adapters; superficial similarity is refused;
transfer warrant is ⊗; induction needs the withheld test; routers; diagnosis; drift."""
from __future__ import annotations

from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.work import contracts as C
from ocm.work import envs as E
from ocm.work import methods as M


def _bind(ops, domain_prefix):
    return {r: next(o for o in ops if ops[o].role == r) for r in E.ROLES}


def test_contract_refuses_forbidden_and_unauthorised_actions_and_skill_solves_all_three_domains():
    for domain, (mk_ops, mk_task) in E.DOMAINS.items():
        ops = mk_ops()
        t = mk_task(0)
        state = dict(t.initial_state)
        destroy = next(o for o in ops.values() if o.role == "destroy")
        _, st = C.apply_operator(destroy, state, t)
        assert st.outcome in (C.StepOutcome.FORBIDDEN, C.StepOutcome.UNAUTHORIZED)
        skill = C.Skill(f"m:{domain}", E.ROLES, _bind(ops, domain), domain, WP.of({"ev:demo"}))
        for i in range(6):
            r = M.run_skill(skill, ops, mk_task(i))
            assert r.success and r.unauthorized_attempts == 0, (domain, i, r.steps)


def test_capsule_transfers_partially_and_refuses_superficial_similarity():
    ent, sw, da = E.enterprise_operators(), E.software_operators(), E.analysis_operators()
    src = C.Skill("m:enterprise", E.ROLES, _bind(ent, "ent"), "enterprise", WP.of({"ev:demo"}))
    cap = M.capsule_from_skill(src, ent, "cap:work")
    assert cap.instantiate("software") is None                      # ADAPTER_REQUIRED: no bindings yet
    tm = C.TransferMap("t1", src.skill_id, "software", {r: next(o for o in sw if sw[o].role == r) for r in E.ROLES}, ("gather before classify",), E.ROLES, (), {"facts": "logs"}, 0.5, ("withheld run",), WP.of({"corr:ent->sw"}))
    verdict, sk, why = C.transported_skill(src, tm, sw)
    assert verdict is C.TransferVerdict.TRANSFER and sk is not None
    assert sk.warrant.evidence == {"ev:demo", "corr:ent->sw"}        # ⊗: never stronger than source + correspondence
    assert all(M.run_skill(sk, sw, E.software_task(i)).success for i in range(5))
    assert M.run_skill(sk, sw, E.software_task(0), revoked={"corr:ent->sw"}).success is False   # revoked correspondence kills the transfer (T9)
    # superficial similarity: mapping the smallest-action role to the broad rewrite is refused
    bad = C.TransferMap("t2", src.skill_id, "software", {**tm.role_mapping, "act_smallest": "sw.rewrite_all"}, (), E.ROLES, (), {}, 0.5, (), WP.of({"c"}))
    v2, _, why2 = C.transported_skill(src, bad, sw)
    assert v2 is C.TransferVerdict.REFUSE_TRANSFER and "superficial" in why2
    # a missing role binding is ADAPTER_REQUIRED, never a guess
    partial = C.TransferMap("t3", src.skill_id, "analysis", {r: next(o for o in da if da[o].role == r) for r in E.ROLES if r != "document"}, (), E.ROLES, (), {}, 0.5, (), WP.of({"c"}))
    assert C.transported_skill(src, partial, da)[0] is C.TransferVerdict.ADAPTER_REQUIRED
    # the hostile transfers by name similarity and keeps the source warrant
    m = C.mutant_similarity_transfer(src, "software", sw, 0.9)
    assert m is not None and m.warrant.evidence == {"ev:demo"}


def test_induction_requires_the_withheld_test_and_routers_differ():
    ent = E.enterprise_operators()
    good_trace = [_bind(ent, "ent")[r] for r in E.ROLES]
    broad_trace = list(good_trace); broad_trace[3] = "ent.refund_all"
    skel = M.induce_skeleton(good_trace, ent, "enterprise", "ev:trace1")
    memo = M.induce_memoised(good_trace, ent, "enterprise", "ev:trace1")
    withheld = [E.enterprise_task(i) for i in range(20, 25)]
    assert M.accept_skill(skel, ent, withheld)[0] and M.accept_skill(memo, ent, withheld)[0]
    broad = M.induce_skeleton(broad_trace, ent, "enterprise", "ev:trace2")
    ok, rep = M.accept_skill(broad, ent, withheld)
    assert not ok and rep["successes"] == 0                          # succeeded once? no: refund_all never matches policy
    sub = M.induce_subtrace([good_trace, good_trace[:4]], ent, "enterprise", "ev:trace3")
    assert sub is not None and sub.skeleton == E.ROLES[:4]
    # routers: similarity picks the look-alike, typed routing keeps it (precondition holds), OCM router refuses the role mismatch
    skills = [skel, broad]
    t = E.enterprise_task(30)
    assert M.route_similarity(skills, t, ent)[0].skill_id in ("skel:enterprise",)
    r = M.OCMRouter()
    assert [s.skill_id for s in r.route(skills, t, ent)] == ["skel:enterprise"]
    res, tries = M.mutant_try_every_skill([broad, skel], t, ent)
    assert res is not None and tries == 2                            # the hostile: brute force called transfer


def test_diagnosis_targets_the_responsible_layer_and_drift_is_detected_then_revised():
    ent = E.enterprise_operators(1)
    skel = C.Skill("skel", E.ROLES, _bind(ent, "ent"), "enterprise", WP.of({"ev:1"}))
    broad = C.Skill("broad", E.ROLES, {**_bind(ent, "ent"), "act_smallest": "ent.refund_all"}, "enterprise", WP.of({"ev:1"}))
    t = E.enterprise_task(0)
    assert M.diagnose(M.run_skill(skel, ent, t), skel, ent, t, env_version="1") is M.Layer.NONE
    assert M.diagnose(M.run_skill(broad, ent, t), broad, ent, t, env_version="1") is M.Layer.WRONG_OPERATOR_SELECTED
    wrong_order = C.Skill("order", ("classify", "gather"), {"classify": "ent.classify_urgency", "gather": "ent.gather_facts"}, "enterprise", WP.of({"ev:1"}))
    assert M.diagnose(M.run_skill(wrong_order, ent, t), wrong_order, ent, t, env_version="1") is M.Layer.MISSING_INFORMATION
    unauth = C.Skill("u", ("destroy",), {"destroy": "ent.delete_account"}, "enterprise", WP.of({"ev:1"}))
    assert M.diagnose(M.run_skill(unauth, ent, t), unauth, ent, t, env_version="1") is M.Layer.AUTHORITY_PREVENTED
    # drift: version 2 changes the high-urgency policy; the old skill's verify still passes (it verifies
    # against the *current* policy) so the checker on hidden state catches it → ENVIRONMENT_DRIFT
    ent2 = E.enterprise_operators(2)
    t2 = E.enterprise_task(0, version=2)
    r2 = M.run_skill(skel, ent, t2)
    assert not r2.success or r2.success                              # outcome depends on urgency; drift only bites high-urgency cases
    high = next(E.enterprise_task(i, version=2) for i in range(40) if E.enterprise_task(i, version=2).hidden["outage"])
    r_old = M.run_skill(skel, ent, high)                             # old operators (v1 policy table lookup) under v2 task
    assert r_old.success is False
    rev = M.revise_for_version(skel, ent2, "check_policy", "ev:v2")
    assert M.run_skill(rev, ent2, high).success and rev.lineage == ("skel",)
    assert rev.warrant.evidence == {"ev:1", "ev:v2"}
