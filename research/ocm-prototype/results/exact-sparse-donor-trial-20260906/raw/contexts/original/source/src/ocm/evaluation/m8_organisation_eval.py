"""M8 organisation study receipt (M8 §11–§13): every arm on every synthetic oracle family and on
the language lifetime stream, reporting the metric vector per arm — task success, navigation work,
partition recovery (exact against the oracle), false-no-descent, unnecessary descent, missed
regions, transports, revocation-through-abstraction commutation (macro liveness computed on the
pruned space equals the pruned macro), topology churn and the topology learner's own cost.  The
learned arm's proposals are scored on the dev half of each world's tasks and adopted only if the
improvement is realised on the held-out half.  No scalar objective is reported.  Exit 0 = ran.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from ocm.kso.warrant import Liveness
from ocm.organisation import arms as A
from ocm.organisation import interface as I
from ocm.organisation import navigate as NV
from ocm.organisation import worlds as W
from ocm.organisation.language_stream import language_space


def _org_from_regions(ks, regions):
    return type("O", (), {"regions": lambda self: regions, "regions_of": lambda self, a: [r.region_id for r in regions if a in r.atoms], "macro": lambda self, rid: I.macro_for(ks, next(r for r in regions if r.region_id == rid)), "transports": lambda self: []})()


def evaluate_org(org, ks, tasks, *, revoked=(), certified=()) -> dict[str, Any]:
    succ = vis = missed = unnec = trans = refine = 0
    for s, t in tasks:
        r = NV.cross_scale(org, ks, s, t, revoked=revoked, certified_queries=certified, max_regions=4)
        succ += int(r.outcome == "FOUND")
        vis += r.visited
        missed += int(r.missed_region)
        unnec += r.unnecessary_descents
        trans += r.transports
        refine += int(r.outcome == "REFINE_REQUIRED")
    n = max(1, len(tasks))
    return {"task_success": succ / n, "navigation_work": vis / n, "missed_region_rate": missed / n, "unnecessary_descent_rate": unnec / n, "transports": trans, "refine_required_rate": refine / n, "tasks": len(tasks)}


def flat_eval(ks, tasks, revoked=()) -> dict[str, Any]:
    succ = vis = 0
    for s, t in tasks:
        r = NV.flat(ks, s, t, revoked=revoked)
        succ += int(r["outcome"] == "FOUND")
        vis += r["visited"]
    n = max(1, len(tasks))
    return {"task_success": succ / n, "navigation_work": vis / n, "tasks": len(tasks)}


def commutation(org, ks, revoked) -> dict[str, Any]:
    """abstract(prune_R(K)) vs prune_R(abstract(K)): macro liveness computed on the children after
    revocation must equal the liveness of the macro's exported claims under the same revocation;
    a live macro over dead children is the hard failure."""
    ok = hard_fail = 0
    for r in org.regions():
        m = org.macro(r.region_id)
        lv = I.macro_liveness(ks, m, revoked)
        children = [ks.atom(a).liveness(revoked) for a in m.exported_claims if a in ks.ids]
        expect = Liveness.LIVE if children and all(c is Liveness.LIVE for c in children) else (Liveness.DEAD if children and all(c is Liveness.DEAD for c in children) else Liveness.UNKNOWN)
        ok += int(lv is expect)
        hard_fail += int(lv is Liveness.LIVE and children and all(c is Liveness.DEAD for c in children))
    return {"regions": len(org.regions()), "commuting": ok, "macro_live_over_dead_children": hard_fail}


def run_world(w: W.OracleWorld) -> dict[str, Any]:
    ks = w.ks
    dev, held = w.tasks[::2], w.tasks[1::2]
    arms = {"R0_flat": A.FlatArm(ks=ks), "R1_hand_tree": A.HandTreeArm(ks, w.labels), "R2_communities": A.CommunityArm(ks), "R3_nested": A.NestedArm(ks), "R4_fibred": A.FibredArm(ks)}
    learned = A.LearnedArm(ks)
    t0 = time.perf_counter()
    base = evaluate_org(_org_from_regions(ks, learned.regions()), ks, dev)
    obj = lambda regs: {"task_success": evaluate_org(_org_from_regions(ks, regs), ks, dev)["task_success"], "navigation_cost": -evaluate_org(_org_from_regions(ks, regs), ks, dev)["navigation_work"]}  # noqa: E731
    obj_held = lambda regs: {"task_success": evaluate_org(_org_from_regions(ks, regs), ks, held)["task_success"], "navigation_cost": -evaluate_org(_org_from_regions(ks, regs), ks, held)["navigation_work"]}  # noqa: E731
    base_held = obj_held(learned.regions())
    for p in learned.propose(obj):
        learned.adopt(p, obj_held, base_heldout=base_held)
    learner_wall = time.perf_counter() - t0
    arms["R6_learned"] = learned
    out: dict[str, Any] = {"family": w.family, "world_id": w.world_id, "atoms": len(ks.ids), "arms": {}, "flat_baseline": flat_eval(ks, w.tasks)}
    for name, arm in arms.items():
        regs = arm.regions()
        rec = W.partition_recovery(w.latent_regions, tuple(r.atoms for r in regs if r.region_id != "root"))
        ev = evaluate_org(arm, ks, w.tasks)
        rev = w.revocations[0] if w.revocations else frozenset(next(iter(ks.atom(w.tasks[0][1]).warrant.lower)))
        ev_rev = evaluate_org(arm, ks, w.tasks, revoked=rev)
        comm = commutation(arm, ks, rev)
        out["arms"][name] = {**ev, "partition_recovery": rec, "after_revocation": {"task_success": ev_rev["task_success"], "navigation_work": ev_rev["navigation_work"]}, "revocation_commutation": comm, "describe": arm.describe()}
    out["arms"]["R6_learned"]["learner_wall_s"] = round(learner_wall, 4)
    out["arms"]["R6_learned"]["history"] = learned.history[:12]
    out["cannot_check_arms"] = A.CANNOT_CHECK_ARMS
    return out


def run() -> dict[str, Any]:
    worlds = [run_world(W.generate(f)) for f in W.FAMILIES]
    lang_ks, lang_tasks, lang_labels = language_space()
    lang = {"atoms": len(lang_ks.ids), "tasks": len(lang_tasks), "arms": {}}
    for name, arm in {"R0_flat": A.FlatArm(ks=lang_ks), "R1_hand_tree": A.HandTreeArm(lang_ks, lang_labels), "R2_communities": A.CommunityArm(lang_ks), "R4_fibred": A.FibredArm(lang_ks)}.items():
        ev = evaluate_org(arm, lang_ks, lang_tasks)
        lang["arms"][name] = {**ev, "describe": arm.describe(), "revocation_commutation": commutation(arm, lang_ks, frozenset({"ev:lex:robot"}))}
    lang["flat_baseline"] = flat_eval(lang_ks, lang_tasks)
    return {"receipt": "M8_ORGANISATION_EVAL_V1", "worlds": worlds, "language_stream": lang, "authority": "synthetic oracle worlds (exact recovery/regret) and the Alpha language objects as a lifetime stream; parents: label propagation, hand hierarchy, summaries, fibred scopes; no scalar objective; no novelty claim"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    r = run()
    if a.out:
        from ocm.evaluation.output import write_result
        write_result(Path(a.out), r)
    for w in r["worlds"]:
        print(w["family"], {k: (round(v["task_success"], 2), round(v["navigation_work"], 1), v["partition_recovery"]["exact_regions"], v["revocation_commutation"]["macro_live_over_dead_children"]) for k, v in w["arms"].items()}, "flat", r["worlds"][0]["flat_baseline"]["navigation_work"] if False else round(w["flat_baseline"]["navigation_work"], 1))
    print("language", {k: (round(v["task_success"], 2), round(v["navigation_work"], 1)) for k, v in r["language_stream"]["arms"].items()}, "flat", round(r["language_stream"]["flat_baseline"]["navigation_work"], 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
