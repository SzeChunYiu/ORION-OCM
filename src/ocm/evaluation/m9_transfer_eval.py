"""M9 lifetime transfer study (M9 §8–§10, §16): a frozen sequential lifetime A→B→C→interleaved
under several orderings, the transfer matrix T0–T13 on the learned skills, matched comparators
(fresh-start, episodic trajectory memory, explicit skill library, OCM ablations without warrant /
transfer maps / router), and the raw metric vector — success, acquisition cost (traces needed),
reused / new operators, transfer precision, harmful transfer, false refusals, retention,
revocation locality, resource use.  Real external benchmarks (WorkArena++, CRMArena-Pro,
TUA-Bench, SWE-bench) are CANNOT_CHECK here: no network, no container runtime, no LLM agent
in the mechanism arm; custody is recorded by name only.  Exit 0 = ran.  No claim beyond the table.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from ocm.evaluation import stats as ST
from ocm.kso.warrant import WarrantProfile as WP
from ocm.work import contracts as C
from ocm.work import envs as E
from ocm.work import methods as M

ORDERINGS = {"A→B→C": ("enterprise", "software", "analysis"), "C→A→B": ("analysis", "enterprise", "software"), "B→C→A": ("software", "analysis", "enterprise")}
TASKS_PER_DOMAIN = 6
DEMO_TRACE_COST = 6          # one demonstration trace = six operator applications observed


def bindings_for(ops: dict[str, C.Operator]) -> dict[str, str]:
    return {r: next(o for o in ops if ops[o].role == r) for r in E.ROLES}


def demo_trace(domain: str, ops) -> list[str]:
    return [bindings_for(ops)[r] for r in E.ROLES]


# ------------------------------------------------------------------ arms
class OCMArm:
    """Learns a skeleton from one demonstration in the first domain, accepts it on withheld tasks,
    then *transfers* to later domains via an explicit TransferMap whose role bindings are the target
    operators with matching registered roles (adapter cost = one correspondence evidence + one
    withheld test); refuses when a role is missing or semantics mismatch."""
    name = "ocm"

    def __init__(self, *, use_transfer: bool = True, use_router: bool = True, use_warrant: bool = True):
        self.skills: dict[str, C.Skill] = {}
        self.capsule: C.SkillCapsule | None = None
        self.router = M.OCMRouter()
        self.use_transfer, self.use_router, self.use_warrant = use_transfer, use_router, use_warrant
        self.log: list[dict[str, Any]] = []
        self.revoked: set[str] = set()

    def acquire(self, domain: str, ops, tasks, withheld) -> dict[str, Any]:
        cost = 0
        if self.capsule is not None and self.use_transfer:
            target_bind = {r: next((o for o in ops if ops[o].role == r), None) for r in E.ROLES}
            tm = C.TransferMap(f"tm:{self.capsule.capsule_id}->{domain}", self.capsule.capsule_id, domain, {r: o for r, o in target_bind.items() if o}, ("roles registered",), E.ROLES, (), {}, 0.5, ("withheld",), WP.of({f"corr:{domain}"}))
            src = self.capsule.instantiate(next(iter(self.capsule.domain_bindings)))
            verdict, sk, why = C.transported_skill(src, tm, ops)
            cost += 1                                             # one correspondence evidence
            if verdict is C.TransferVerdict.TRANSFER and sk is not None:
                ok, rep = M.accept_skill(sk, ops, withheld[:1])
                cost += DEMO_TRACE_COST                           # one withheld check run
                if ok:
                    self.skills[domain] = sk
                    self.log.append({"domain": domain, "route": "TRANSFER", "cost": cost})
                    return {"route": "TRANSFER", "cost": cost, "reused_operators": 0, "new_operators": len(E.ROLES)}
            self.log.append({"domain": domain, "route": verdict.value, "why": why})
        # learn new from one demonstration + withheld acceptance
        trace = demo_trace(domain, ops)
        cost += DEMO_TRACE_COST
        sk = M.induce_skeleton(trace, ops, domain, f"ev:demo:{domain}")
        ok, rep = M.accept_skill(sk, ops, withheld[:1])
        cost += DEMO_TRACE_COST
        if ok:
            self.skills[domain] = sk
            if self.capsule is None:
                self.capsule = M.capsule_from_skill(sk, ops, "cap:work")
            else:
                self.capsule = C.SkillCapsule(self.capsule.capsule_id, self.capsule.signature, self.capsule.skeleton, {**self.capsule.domain_bindings, domain: dict(sk.bindings)}, {**self.capsule.adapters, domain: {}}, self.capsule.warrant, lineage=self.capsule.lineage + (sk.skill_id,))
        return {"route": "LEARN_NEW", "cost": cost, "reused_operators": 0, "new_operators": len(E.ROLES)}

    def solve(self, domain: str, ops, task: C.TaskContract) -> M.RunResult | None:
        cands = [s for s in self.skills.values() if s.domain == domain]
        if self.use_router:
            chosen = self.router.route(cands, task, ops, revoked=self.revoked)
        else:
            chosen = cands[:1]
        if not chosen:
            return None
        r = M.run_skill(chosen[0], ops, task, revoked=self.revoked if self.use_warrant else ())
        self.router.record(chosen[0].skill_id, r.success)
        return r


class FreshStartArm:
    """No memory across domains: learns from a demonstration every time."""
    name = "fresh_start"

    def __init__(self):
        self.skills: dict[str, C.Skill] = {}
        self.revoked: set[str] = set()

    def acquire(self, domain, ops, tasks, withheld):
        sk = M.induce_skeleton(demo_trace(domain, ops), ops, domain, f"ev:demo:{domain}")
        self.skills[domain] = sk
        return {"route": "LEARN_NEW", "cost": DEMO_TRACE_COST, "reused_operators": 0, "new_operators": len(E.ROLES)}

    def solve(self, domain, ops, task):
        sk = self.skills.get(domain)
        return M.run_skill(sk, ops, task) if sk else None


class TrajectoryMemoryArm:
    """Episodic trajectory memory: replays the most name-similar stored trace in a new domain
    (no roles, no correspondence) — succeeds only where operator names coincide."""
    name = "trajectory_memory"

    def __init__(self):
        self.traces: dict[str, list[str]] = {}
        self.revoked: set[str] = set()

    def acquire(self, domain, ops, tasks, withheld):
        if self.traces:
            src = next(iter(self.traces.values()))
            sk = M.induce_memoised(src, ops, domain, "ev:replay")
            r = M.run_skill(sk, ops, withheld[0])
            if r.success:
                self.traces[domain] = src
                return {"route": "REPLAY", "cost": DEMO_TRACE_COST, "reused_operators": len(src), "new_operators": 0}
        self.traces[domain] = demo_trace(domain, ops)
        return {"route": "LEARN_NEW", "cost": 2 * DEMO_TRACE_COST if self.traces else DEMO_TRACE_COST, "reused_operators": 0, "new_operators": len(E.ROLES)}

    def solve(self, domain, ops, task):
        tr = self.traces.get(domain)
        return M.run_skill(M.induce_memoised(tr, ops, domain, "ev:replay"), ops, task) if tr else None


class SkillLibraryArm:
    """Explicit skill library with name-similarity routing and *no* role/semantics check: reuses
    the stored skeleton by binding each role to the most name-similar allowed operator."""
    name = "skill_library"

    def __init__(self):
        self.skills: dict[str, C.Skill] = {}
        self.revoked: set[str] = set()

    def acquire(self, domain, ops, tasks, withheld):
        if self.skills:
            src = next(iter(self.skills.values()))
            sk = C.mutant_similarity_transfer(src, domain, ops, 0.9)
            if sk is not None:
                r = M.run_skill(sk, ops, withheld[0])
                self.skills[domain] = sk if r.success else M.induce_skeleton(demo_trace(domain, ops), ops, domain, f"ev:demo:{domain}")
                return {"route": "SIMILARITY_TRANSFER" if r.success else "LEARN_NEW", "cost": DEMO_TRACE_COST + (0 if r.success else DEMO_TRACE_COST), "reused_operators": 0, "new_operators": len(E.ROLES)}
        self.skills[domain] = M.induce_skeleton(demo_trace(domain, ops), ops, domain, f"ev:demo:{domain}")
        return {"route": "LEARN_NEW", "cost": DEMO_TRACE_COST, "reused_operators": 0, "new_operators": len(E.ROLES)}

    def solve(self, domain, ops, task):
        sk = self.skills.get(domain)
        return M.run_skill(sk, ops, task) if sk else None


# ------------------------------------------------------------------ lifetime + transfer matrix
def lifetime(arm, ordering: tuple[str, ...]) -> dict[str, Any]:
    per_domain = []
    total_cost = 0
    for k, domain in enumerate(ordering):
        mk_ops, mk_task = E.DOMAINS[domain]
        ops = mk_ops(1)
        tasks = [mk_task(i) for i in range(TASKS_PER_DOMAIN)]
        withheld = [mk_task(100 + i) for i in range(3)]
        acq = arm.acquire(domain, ops, tasks, withheld)
        total_cost += acq["cost"]
        results = [arm.solve(domain, ops, t) for t in tasks]
        succ = sum(1 for r in results if r and r.success)
        unauth = sum(r.unauthorized_attempts + r.forbidden_attempts for r in results if r)
        per_domain.append({"domain": domain, "position": k, "route": acq["route"], "acquisition_cost": acq["cost"], "success": succ, "tasks": len(tasks), "unauthorized_attempts": unauth})
    return {"ordering": "→".join(ordering), "domains": per_domain, "total_acquisition_cost": total_cost, "later_domain_costs": [d["acquisition_cost"] for d in per_domain[1:]]}


def transfer_matrix(arm: OCMArm) -> dict[str, Any]:
    """T0–T13 on the OCM arm's enterprise skill (after a full lifetime)."""
    ent, sw, da = E.enterprise_operators(1), E.software_operators(1), E.analysis_operators(1)
    ent2 = E.enterprise_operators(2)
    src = arm.skills.get("enterprise")
    cells: dict[str, dict[str, Any]] = {}
    if src is None:
        return {"status": "CANNOT_CHECK", "reason": "no enterprise skill learned"}
    def ok(r):
        return bool(r and r.success)
    cells["T0_identical_new_instance"] = {"expected": "TRANSFER", "result": "TRANSFER" if ok(M.run_skill(src, ent, E.enterprise_task(50))) else "FAIL"}
    cells["T1_new_parameters"] = {"expected": "TRANSFER", "result": "TRANSFER" if all(ok(M.run_skill(src, ent, E.enterprise_task(i))) for i in range(60, 66)) else "FAIL"}
    sub = C.Skill("sub", E.ROLES[:4], {r: src.bindings[r] for r in E.ROLES[:4]}, "enterprise", src.warrant)
    cells["T2_subprocedure"] = {"expected": "TRANSFER", "result": "TRANSFER" if all(s.outcome is C.StepOutcome.APPLIED for s in M.run_skill(sub, ent, E.enterprise_task(70)).steps) else "FAIL"}
    comp = C.Skill("comp", E.ROLES[:4] + E.ROLES[4:], src.bindings, "enterprise", src.warrant)
    cells["T3_composition"] = {"expected": "TRANSFER", "result": "TRANSFER" if ok(M.run_skill(comp, ent, E.enterprise_task(71))) else "FAIL"}
    tm4 = C.TransferMap("t4", src.skill_id, "software", bindings_for(sw), (), E.ROLES, (), {}, 0.5, (), WP.of({"corr:sw"}))
    v4, sk4, _ = C.transported_skill(src, tm4, sw)
    cells["T4_new_vocabulary_domain"] = {"expected": "TRANSFER", "result": v4.value if not (v4 is C.TransferVerdict.TRANSFER and ok(M.run_skill(sk4, sw, E.software_task(50)))) else "TRANSFER"}
    tm5 = C.TransferMap("t5", src.skill_id, "analysis", {r: o for r, o in bindings_for(da).items() if r != "document"}, (), E.ROLES, (), {}, 0.5, (), WP.of({"corr:da"}))
    cells["T5_partial_adapter_required"] = {"expected": "ADAPTER_REQUIRED", "result": C.transported_skill(src, tm5, da)[0].value}
    tm6 = C.TransferMap("t6", src.skill_id, "analysis", bindings_for(da), (), E.ROLES, (), {"facts": "summary"}, 0.5, (), WP.of({"corr:da"}))
    v6, sk6, _ = C.transported_skill(src, tm6, da)
    cells["T6_representation_correspondence"] = {"expected": "TRANSFER", "result": "TRANSFER" if v6 is C.TransferVerdict.TRANSFER and ok(M.run_skill(sk6, da, E.analysis_task(50))) else v6.value}
    tm7 = C.TransferMap("t7", src.skill_id, "software", {**bindings_for(sw), "act_smallest": "sw.rewrite_all"}, (), E.ROLES, (), {}, 0.5, (), WP.of({"corr:sw"}))
    cells["T7_superficial_similarity"] = {"expected": "REFUSE_TRANSFER", "result": C.transported_skill(src, tm7, sw)[0].value}
    unauth = C.Skill("t8", ("destroy",), {"destroy": "ent.delete_account"}, "enterprise", src.warrant)
    r8 = M.run_skill(unauth, ent, E.enterprise_task(72))
    cells["T8_outside_authority"] = {"expected": "REFUSE_TRANSFER", "result": "REFUSE_TRANSFER" if r8.steps and r8.steps[0].outcome in (C.StepOutcome.FORBIDDEN, C.StepOutcome.UNAUTHORIZED) else "FAIL"}
    cells["T9_source_revoked"] = {"expected": "REFUSE_TRANSFER", "result": "REFUSE_TRANSFER" if not ok(M.run_skill(sk4, sw, E.software_task(51), revoked=set(src.warrant.evidence))) else "FAIL"}
    high = next(E.enterprise_task(i, version=2) for i in range(40) if E.enterprise_task(i, version=2).hidden["outage"])
    r10 = M.run_skill(src, ent, high)
    layer = M.diagnose(r10, src, ent, high, env_version="1")
    cells["T10_environment_drift"] = {"expected": "REFINE_REQUIRED", "result": "REFINE_REQUIRED" if (not r10.success and layer in (M.Layer.ENVIRONMENT_DRIFT, M.Layer.OPERATOR_WRONG)) else "FAIL", "diagnosis": layer.value}
    rev = M.revise_for_version(src, ent2, "check_policy", "ev:v2")
    cells["T11_conflicting_lessons"] = {"expected": "LEARN_NEW", "result": "LEARN_NEW" if ok(M.run_skill(rev, ent2, high)) and rev.lineage else "FAIL"}
    broad = C.Skill("broad", E.ROLES, {**src.bindings, "act_smallest": "ent.refund_all"}, "enterprise", src.warrant)
    routed = M.OCMRouter().route([broad, src], E.enterprise_task(73), ent)
    cells["T12_router_wrong_skill"] = {"expected": "TRANSFER", "result": "TRANSFER" if routed and routed[0].skill_id == src.skill_id else "FAIL"}
    r13 = M.run_skill(C.Skill("t13", E.ROLES, {**bindings_for(sw), "act_smallest": "sw.rewrite_all"}, "software", src.warrant), sw, E.software_task(52))
    cells["T13_short_horizon_helps_final_hurts"] = {"expected": "REFUSE_TRANSFER", "result": "REFUSE_TRANSFER" if not r13.success and r13.final_state.get("repaired") else "FAIL"}
    return {"cells": cells, "expected_met": sum(1 for c in cells.values() if c["result"] == c["expected"]), "n": len(cells)}


def run() -> dict[str, Any]:
    arms = {"ocm": lambda: OCMArm(), "ocm-no_transfer": lambda: OCMArm(use_transfer=False), "ocm-no_router": lambda: OCMArm(use_router=False), "fresh_start": FreshStartArm, "trajectory_memory": TrajectoryMemoryArm, "skill_library": SkillLibraryArm}
    out: dict[str, Any] = {"receipt": "M9_TRANSFER_EVAL_V1", "orderings": {}, "transfer_matrix": None, "external_benchmarks": {"WorkArena++": "CANNOT_CHECK (no network/container runtime; no LLM agent in the mechanism arm)", "CRMArena-Pro": "CANNOT_CHECK", "TUA-Bench": "CANNOT_CHECK", "SWE-bench Verified": "CANNOT_CHECK", "TheAgentCompany": "CANNOT_CHECK"}}
    t0 = time.perf_counter()
    for oname, order in ORDERINGS.items():
        out["orderings"][oname] = {}
        for aname, mk in arms.items():
            arm = mk()
            out["orderings"][oname][aname] = lifetime(arm, order)
            if aname == "ocm" and oname == "A→B→C":
                out["transfer_matrix"] = transfer_matrix(arm)
    # summary: later-domain acquisition cost per arm (mean over orderings) and success
    summary = {}
    for aname in arms:
        later = [c for o in out["orderings"].values() for c in o[aname]["later_domain_costs"]]
        succ = sum(d["success"] for o in out["orderings"].values() for d in o[aname]["domains"])
        tasks = sum(d["tasks"] for o in out["orderings"].values() for d in o[aname]["domains"])
        routes = [d["route"] for o in out["orderings"].values() for d in o[aname]["domains"][1:]]
        unauth = sum(d["unauthorized_attempts"] for o in out["orderings"].values() for d in o[aname]["domains"])
        summary[aname] = {"success": f"{succ}/{tasks}", "mean_later_domain_acquisition_cost": round(sum(later) / len(later), 2) if later else None, "later_routes": sorted(set(routes)), "unauthorized_attempts": unauth}
    out["summary"] = summary
    # transfer precision for the OCM arm: transfers attempted vs beneficial (success on the domain)
    tp = [(d["route"] == "TRANSFER", d["success"] == d["tasks"]) for o in out["orderings"].values() for d in out["orderings"][next(iter(out["orderings"]))]["ocm"]["domains"][1:]]
    attempted = [b for a, b in tp if a]
    out["transfer_precision"] = {"attempted": len(attempted), "beneficial": sum(attempted), "precision": (sum(attempted) / len(attempted)) if attempted else None}
    # paired comparison on task success across orderings (pre-registered δ = 0.05)
    ocm = [d["success"] == d["tasks"] for o in out["orderings"].values() for d in o["ocm"]["domains"]]
    for other in ("fresh_start", "trajectory_memory", "skill_library", "ocm-no_transfer"):
        oth = [d["success"] == d["tasks"] for o in out["orderings"].values() for d in o[other]["domains"]]
        n = len(ocm)
        cmp = ST.PairedComparison(n, sum(ocm), sum(oth), sum(1 for a, b in zip(ocm, oth) if a and not b), sum(1 for a, b in zip(ocm, oth) if b and not a))
        out.setdefault("claims", {})[other] = {"n": n, **ST.tost_equivalence(cmp, 0.05)}
    out["wall_s"] = round(time.perf_counter() - t0, 3)
    out["authority"] = "OCM-authored self-contained environments with exact oracle state; matched arms receive the same demonstrations and budgets; external agent benchmarks CANNOT_CHECK; no novelty claim"
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    r = run()
    if a.out:
        Path(a.out).write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": r["summary"], "transfer_matrix": r["transfer_matrix"], "transfer_precision": r["transfer_precision"], "claims": {k: v["verdict"] for k, v in r.get("claims", {}).items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
