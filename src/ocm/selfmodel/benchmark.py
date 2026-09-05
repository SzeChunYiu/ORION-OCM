"""Controlled self-reorganisation benchmark S1–S7 (M11 §13) on the M9 enterprise environment,
with the true cause known, plus the two parents (parameter search over router/revocation;
reflection-retry over skills) and the OCM diagnose→propose→shadow→assure→adopt→monitor loop.

Every scenario plants one cause into an incumbent *machine* (operator table + skills + router +
revoked set + environment version) by replacing a table entry under its standard operator id, so
that neither router can tell the planted operator from the genuine one by name:

  S1 router fault             the router prefers a role-mismatched broad skill
  S2 operator fault           the smallest-action operator emits a wrong action
  S3 representation ceiling   the urgency classifier is blind to the outage feature
  S4 learning-policy failure  memoised induction froze the demo's literal action
  S5 false structural alarm   one revoked dependency kills every task; reinstating fixes it
  S6 harmful high-level Jump  the operator fails on urgent cases only; an "escalate always" rewrite fixes the target but breaks preservation
  S7 environment drift        policy version 2; the version-1 policy operator is stale

Target suite = outage cases, preservation suite = non-outage cases (the oracle side reads the
protected `hidden` field to *build* suites; the machine never sees it).  The ablation channel
gives the self-model counterfactual runs with one layer changed (the minimum repair at the true
layer, a router swap, and — where the scenario has one — the broad rewrite); the parents get the
same environment but no diagnosis object.  Metrics per scenario: diagnosed vs true layer,
minimum-class correctness, false/missed Jump, assurance verdict, adoption, target and
preservation before/after, exact rollback, refusal of the broad rewrite, prediction realised,
metered proposal cost.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.work import contracts as WC
from ocm.work import envs as E
from ocm.work import methods as WM

from . import diagnose as DG
from . import govern as GV
from . import model as SM
from . import proposal as PR

ROLES = E.ROLES


def good_bindings(ops: dict[str, WC.Operator]) -> dict[str, str]:
    return {r: next(o for o in ops if ops[o].role == r) for r in ROLES}


@dataclass
class Machine:
    ops: dict[str, WC.Operator]
    skills: list[WC.Skill]
    router: str = "ocm"                       # ocm | first | broad_first
    revoked: set = field(default_factory=set)
    env_version: int = 1
    learner: str = "skeleton"                 # skeleton | memoised

    def solve(self, task: WC.TaskContract) -> WM.RunResult | None:
        cands = [s for s in self.skills if s.domain == task.domain]
        if self.router == "ocm":
            chosen = WM.OCMRouter().route(cands, task, self.ops, revoked=self.revoked)
        elif self.router == "broad_first":
            chosen = sorted(cands, key=lambda s: 0 if "broad" in s.skill_id else 1)[:1]
        else:
            chosen = cands[:1]
        return WM.run_skill(chosen[0], self.ops, task, revoked=self.revoked) if chosen else None

    def score(self, tasks: Sequence[WC.TaskContract]) -> int:
        return sum(1 for t in tasks if (r := self.solve(t)) and r.success)


def runner(machine: Machine, tasks: Sequence[WC.TaskContract]) -> dict[str, Any]:
    rs = [machine.solve(t) for t in tasks]
    return {"success": sum(1 for r in rs if r and r.success), "n": len(tasks), "resources": {"steps": sum(r.cost for r in rs if r)}}


def _replace_backend(op: WC.Operator, version: str, backend, *, role: str | None = None) -> WC.Operator:
    return dataclasses.replace(op, version=version, backend=backend, role=role or op.role)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    true_layer: str
    true_class: PR.ChangeClass
    build: Callable[[], Machine]
    fix: Callable[[Machine], Machine]                      # the minimum repair
    broad: Callable[[Machine], Machine] | None = None       # a broad rewrite (S5 benign-but-excessive, S6 harmful)
    obstruction: bool = False                                # a valid certificate exists (S3)


def scenarios() -> list[Scenario]:
    ent = E.enterprise_operators(1)
    ent2 = E.enterprise_operators(2)
    good = good_bindings(ent)
    skel = WC.Skill("skel", ROLES, good, "enterprise", WP.of({"ev:s"}))
    broad_skill = WC.Skill("broad", ROLES, {**good, "act_smallest": "ent.refund_all"}, "enterprise", WP.of({"ev:b"}))
    sa = ent["ent.smallest_action"]
    cl = ent["ent.classify_urgency"]

    def with_op(m: Machine, oid: str, op: WC.Operator, **kw) -> Machine:
        return Machine({**m.ops, oid: op}, list(m.skills), kw.get("router", m.router), set(m.revoked), kw.get("env_version", m.env_version), kw.get("learner", m.learner))

    wrong = _replace_backend(sa, "1-defect", lambda s: {**s, "action": "wrong", "record": {**s.get("record", {}), "action": "wrong"}})
    blind = _replace_backend(cl, "1-blind", lambda s: {**s, "urgency": "low"})
    literal = _replace_backend(sa, "1-memo", lambda s: {**s, "action": "reply_faq", "record": {**s.get("record", {}), "action": "reply_faq"}})
    wrong_high = _replace_backend(sa, "1-defect-high", lambda s: {**s, "action": "wrong" if s["urgency"] == "high" else s["policy"]["smallest"], "record": {**s.get("record", {}), "action": "wrong" if s["urgency"] == "high" else s["policy"]["smallest"]}})
    escalate_always = _replace_backend(sa, "1-jump", lambda s: {**s, "action": "escalate", "record": {**s.get("record", {}), "action": "escalate"}})

    return [
        Scenario("S0_no_fault_control", "none", PR.ChangeClass.C0_PARAMETERS, lambda: Machine(dict(ent), [skel]), lambda m: m),
        Scenario("S1_router_fault", "D1", PR.ChangeClass.C1_ROUTER, lambda: Machine(dict(ent), [broad_skill, skel], router="broad_first"), lambda m: Machine(m.ops, list(m.skills), "ocm", set(m.revoked), m.env_version)),
        Scenario("S2_operator_fault", "D2", PR.ChangeClass.C2_OPERATOR, lambda: Machine({**ent, "ent.smallest_action": wrong}, [skel]), lambda m: with_op(m, "ent.smallest_action", sa)),
        Scenario("S3_representation_ceiling", "D3", PR.ChangeClass.C3_REPRESENTATION, lambda: Machine({**ent, "ent.classify_urgency": blind}, [skel]), lambda m: with_op(m, "ent.classify_urgency", cl), obstruction=True),
        Scenario("S4_learning_policy", "D6", PR.ChangeClass.C4_LEARNING_POLICY, lambda: Machine({**ent, "ent.smallest_action": literal}, [skel], learner="memoised"), lambda m: with_op(m, "ent.smallest_action", sa, learner="skeleton")),
        Scenario("S5_false_structural_alarm", "D2", PR.ChangeClass.C2_OPERATOR, lambda: Machine(dict(ent), [skel], revoked={"ev:s"}), lambda m: Machine(m.ops, list(m.skills), m.router, set(), m.env_version), broad=lambda m: Machine(dict(m.ops), [WC.Skill("skel2", ROLES, good, "enterprise", WP.of({"ev:new"}))], m.router, set(m.revoked), m.env_version)),
        Scenario("S6_harmful_jump", "D2", PR.ChangeClass.C2_OPERATOR, lambda: Machine({**ent, "ent.smallest_action": wrong_high}, [skel]), lambda m: with_op(m, "ent.smallest_action", sa), broad=lambda m: with_op(m, "ent.smallest_action", escalate_always)),
        Scenario("S7_environment_drift", "D2", PR.ChangeClass.C2_OPERATOR, lambda: Machine(dict(ent), [skel], env_version=2), lambda m: with_op(m, "ent.check_policy", ent2["ent.check_policy"])),
    ]


def suites_for(version: int, *, seed: str = "OCM-M11") -> tuple[list[WC.TaskContract], list[WC.TaskContract]]:
    tasks = [E.enterprise_task(i, version=version, seed=seed) for i in range(200)]
    target = [t for t in tasks if t.hidden["outage"]][:6]
    preservation = [t for t in tasks if not t.hidden["outage"]][:6]
    return target, preservation


LAYER_ABLATIONS = {"D1": "swap router", "D2": "restore operator / reinstate dependency", "D3": "new representation", "D6": "re-induce with the skeleton policy"}


def ablation_channel(sc: Scenario, m: Machine, target: Sequence[WC.TaskContract]) -> list[SM.AblationEvidence]:
    out = [SM.AblationEvidence(LAYER_ABLATIONS[sc.true_layer], SM.Layer(sc.true_layer), sc.fix(m).score(target) == len(target), f"ev:abl:{sc.scenario_id}:{sc.true_layer}")]
    if sc.true_layer != "D1":
        alt = Machine(m.ops, list(m.skills), "first", set(m.revoked), m.env_version)
        out.append(SM.AblationEvidence("swap router", SM.Layer.D1_ROUTING, alt.score(target) == len(target), f"ev:abl:{sc.scenario_id}:D1"))
    if sc.broad is not None:
        out.append(SM.AblationEvidence("rewrite organisation", SM.Layer.D7_ORGANISATION, sc.broad(m).score(target) == len(target), f"ev:abl:{sc.scenario_id}:D7"))
    return out


def run_scenario(sc: Scenario, root) -> dict[str, Any]:
    rt = OCMRuntime(root / sc.scenario_id)
    sm = SM.SelfModel(rt)
    m = sc.build()
    target, preservation = suites_for(m.env_version)
    before, pres_before = m.score(target), m.score(preservation)
    if before == len(target):
        # no-alarm case: nothing failed, so no FailureRecord exists and no proposal may be raised
        return {"scenario": sc.scenario_id, "true_layer": sc.true_layer, "diagnosed": None, "diagnosis_correct": sc.true_layer == "none", "weights": {}, "unknown": [], "escalation_allowed": False, "escalation_reason": "no failure", "false_jump": False, "missed_jump": False, "architecture_alarm": False,
                "proposal_class": None, "minimum_class_correct": sc.true_layer == "none", "assurance": None, "assurance_reasons": [], "adopted": False, "target_before": f"{before}/{len(target)}", "target_after": f"{before}/{len(target)}", "preservation_before": f"{pres_before}/{len(preservation)}", "preservation_after": f"{pres_before}/{len(preservation)}",
                "rollback_exact": None, "broad_rewrite": None, "prediction_realised": None, "proposal_cost_meter": 0.0, "no_failure": True}
    ablations = ablation_channel(sc, m, target)
    fr = SM.FailureRecord(f"F:{sc.scenario_id}", "enterprise-target", "enterprise", f"{before}/{len(target)} target tasks succeed", "all target tasks succeed", ("ev:trace",), (SM.Layer.D1_ROUTING, SM.Layer.D2_OPERATOR, SM.Layer.D3_REPRESENTATION, SM.Layer.D6_LEARNING_POLICY, SM.Layer.D7_ORGANISATION), tuple(ablations), {}, "LIVE", "high", len(target) - before, "enterprise")
    failure_eid = sm.ingest_failure(fr)
    cert = None
    if sc.obstruction:
        live = WP.of({"e:attempt"})
        cert = DG.ObstructionCertificate(SM.Layer.D2_OPERATOR, "classify urgency", ("op:classify_blind", "op:classify_by_customer"), (DG.Attempt("op:classify_blind", SM.Layer.D2_OPERATOR, live, False), DG.Attempt("op:classify_by_customer", SM.Layer.D2_OPERATOR, live, False)), {"steps": 8}, ("ceiling: the observable state lacks the outage feature",), "no operator over the current observable state distinguishes urgent cases")
    d = DG.diagnose(fr, certificate=cert)
    esc_ok, esc_why = DG.escalation_allowed(d, cert)
    cls = PR.minimum_class_for(d.minimum_sufficient) if d.minimum_sufficient else PR.ChangeClass.C0_PARAMETERS
    pred = PR.Prediction(("target",), (), {"steps": 0}, ("preservation",), (), ("none",), 0.1)
    prop = PR.SelfChangeProposal(f"p:{sc.scenario_id}", "1", (failure_eid,), f"layer.{d.minimum_sufficient}", d.minimum_sufficient or "D0", "fp-inc", cls, {"fix": sc.scenario_id}, sc.fix, pred, ("preservation",), (), "target", "restore previous machine", "enterprise", "w1", PR.Origin.EXISTING_ALTERNATIVE)
    receipt = GV.register_prediction(rt, prop)                                   # K_self receipt before any outcome access (E5)
    suites = {"target": target, "preservation": preservation}
    sh = GV.shadow_evaluate(rt, m, prop, runner, suites)
    a = GV.assure(prop, sh, protocol_hash="frozen", frozen_protocol_hash="frozen", budget={"steps": 200}, rollback_exists=True, prediction_receipt=receipt, runtime=rt, held_out_task_ids=[t.task_id for t in target + preservation])
    ledger = GV.AdoptionLedger(rt)
    ledger.propose(prop)
    dec = GV.ExternalAdopter("token").decide(prop, a)
    adopted, after, pres_after, rollback_ok = False, before, pres_before, None
    if dec.approved:
        challenger, info = ledger.adopt(prop, dec, m, {"machine": {"artifact": "fp-inc"}})
        adopted = True
        after, pres_after = challenger.score(target), challenger.score(preservation)
        restored, _, ok = ledger.rollback(prop.fingerprint())
        rollback_ok = ok and restored.score(target) == before and rt.state.evidence.liveness([info["stamped_evidence"]]).value == "DEAD"
    broad = None
    if sc.broad is not None:
        bprop = PR.SelfChangeProposal(f"pb:{sc.scenario_id}", "1", (failure_eid,), "organisation", "D7", "fp-inc", PR.ChangeClass.C5_ORGANISATION, {"rewrite": sc.scenario_id}, sc.broad, pred, ("preservation",), (), "target", "restore", "enterprise", "w1", PR.Origin.LEARNED)
        breceipt = GV.register_prediction(rt, bprop)
        shb = GV.shadow_evaluate(rt, m, bprop, runner, suites)
        ab = GV.assure(bprop, shb, protocol_hash="frozen", frozen_protocol_hash="frozen", budget={"steps": 200}, rollback_exists=True, prediction_receipt=breceipt, runtime=rt, held_out_task_ids=[t.task_id for t in target + preservation])
        broad = {"assurance": ab.passed, "reasons": list(ab.reasons), "minimum_sufficient": PR.is_minimum_sufficient(bprop, sc.true_layer), "target": f"{shb.challenger['target']['success']}/{len(target)}", "preservation": f"{shb.challenger['preservation']['success']}/{len(preservation)}", "refused": (not ab.passed) or not PR.is_minimum_sufficient(bprop, sc.true_layer)}
    return {"scenario": sc.scenario_id, "true_layer": sc.true_layer, "diagnosed": d.minimum_sufficient, "diagnosis_correct": d.minimum_sufficient == sc.true_layer, "weights": d.weights, "unknown": list(d.unknown), "escalation_allowed": esc_ok, "escalation_reason": esc_why,
            "false_jump": esc_ok and sc.true_layer in ("D1", "D2", "D6"), "missed_jump": (not esc_ok) and sc.true_layer == "D3", "architecture_alarm": d.architecture_alarm,
            "proposal_class": cls.value, "minimum_class_correct": cls is sc.true_class, "assurance": a.passed, "assurance_reasons": list(a.reasons), "adopted": adopted,
            "target_before": f"{before}/{len(target)}", "target_after": f"{after}/{len(target)}", "preservation_before": f"{pres_before}/{len(preservation)}", "preservation_after": f"{pres_after}/{len(preservation)}",
            "rollback_exact": rollback_ok, "broad_rewrite": broad, "prediction_realised": a.checks.get("prediction_realised"), "proposal_cost_meter": sum(ledger.meter_charges)}


# ------------------------------------------------------------------ parents
def parent_parameter_search(sc: Scenario, target: Sequence[WC.TaskContract], preservation: Sequence[WC.TaskContract]) -> dict[str, Any]:
    """Search over router policies and the revocation toggle only: no diagnosis, no proposal object."""
    m = sc.build()
    best = None
    tried = 0
    for router in ("ocm", "first", "broad_first"):
        for clear in (False, True):
            tried += 1
            cand = Machine(m.ops, list(m.skills), router, set() if clear else set(m.revoked), m.env_version)
            s = cand.score(target)
            if best is None or s > best[0]:
                best = (s, router, clear, cand.score(preservation))
    return {"target": f"{best[0]}/{len(target)}", "preservation": f"{best[3]}/{len(preservation)}", "configurations_tried": tried, "solves": best[0] == len(target)}


def parent_reflection_retry(sc: Scenario, target: Sequence[WC.TaskContract], preservation: Sequence[WC.TaskContract]) -> dict[str, Any]:
    """Reflection: on failure retry with the next registered skill (no layer diagnosis, no repair)."""
    m = sc.build()

    def run(tasks):
        succ = tries = 0
        for t in tasks:
            for sk in m.skills:
                tries += 1
                if WM.run_skill(sk, m.ops, t, revoked=m.revoked).success:
                    succ += 1
                    break
        return succ, tries

    ts, tt = run(target)
    ps, _ = run(preservation)
    return {"target": f"{ts}/{len(target)}", "preservation": f"{ps}/{len(preservation)}", "attempts": tt, "solves": ts == len(target)}
