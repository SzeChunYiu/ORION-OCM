"""Did the clean arm actually exercise the decision the theorem is about?

BIO-T1 asserts protected assay state is not an ancestor of birth/death or
resource-transition decisions. A clean world with no births at all satisfies
that condition vacuously: the instrument passes because the decision never
happened, not because it was uncontaminated.

Empirically, in the frozen micro-Earth reproduction is reachable ONLY when
leak is on AND a cell already holds the useful method, because harvest (+1)
exactly cancels maintenance (-1) and the birth threshold is never reached
without the leak's assay-conditioned harvest bonus. So the BIO-T1 clean arm is
structurally birth-free.

A pass that cannot distinguish "uncontaminated" from "never happened" is not
evidence. This module gives that case its own status.
"""
from __future__ import annotations

import worlds as W

VACUOUS = "VACUOUS_PASS_DECISION_NEVER_EXERCISED"
LIVE = "PASS_ON_LIVE_DECISION"
CANNOT = "CANNOT_CHECK_NO_CONDITIONS_ENUMERATED"


def _events(me_mod, spec: W.WorldSpec, ticks: int) -> dict:
    e = W.build(me_mod, spec)
    for _ in range(ticks):
        e.step()
        e.observer_assay()
    kinds = {}
    for h in e.history:
        kinds[h[0]] = kinds.get(h[0], 0) + 1
    return {"events": kinds, "n_alive": len(e.alive()),
            "births": kinds.get("birth", 0), "deaths": kinds.get("death", 0),
            "interferes": e.assay_interferes()}


def birth_reachability(me_mod, n: int, n_conditions: int = 400,
                       ticks: int = W.DEFAULT_TICKS,
                       mode: str = "MULTISET") -> dict:
    """Across enumerated initial conditions, when can reproduction happen?"""
    conds = W.initial_conditions(n, n_conditions, mode)
    clean = {"n": 0, "with_birth": 0, "witness": None}
    leaky = {"n": 0, "with_birth": 0, "witness": None}
    for (g, m, social, leak, regime) in conds:
        spec = W.WorldSpec(n, g, m, social, leak, regime, W.ALL_ON)
        r = _events(me_mod, spec, ticks)
        bucket = leaky if leak else clean
        bucket["n"] += 1
        if r["births"]:
            bucket["with_birth"] += 1
            if bucket["witness"] is None:
                bucket["witness"] = {"spec": spec.key(), **r}
    if clean["n"] == 0 and leaky["n"] == 0:
        status = CANNOT
    elif clean["with_birth"] == 0:
        status = VACUOUS
    else:
        status = LIVE
    return {
        "instrument": "birth_reachability",
        "n_org": n, "ticks": ticks, "mode": mode,
        "clean_arm": clean, "leaky_arm": leaky,
        "status": status,
        "can_fail": True,
        "finding": (
            "Reproduction is reachable only through the assay-leak channel: "
            "harvest (+1) cancels maintenance (-1), so the birth threshold is "
            "unreachable unless leak raises harvest and lowers the threshold."
            if status == VACUOUS else
            "Clean arm exercises reproduction; BIO-T1 pass is non-vacuous."),
        "consequence": (
            "BIO-T1's clean control holds because no birth/death decision "
            "occurs, not because an occurring decision was uncontaminated. "
            "K_birthdeath, K_mut and K_inherit are therefore unexercisable in "
            "clean primary runs of this world."
            if status == VACUOUS else None),
    }


def kernel_exercisability(me_mod, n: int, n_conditions: int = 400,
                          ticks: int = W.DEFAULT_TICKS,
                          mode: str = "MULTISET") -> dict:
    """Which kernels are reachable at all, and under which arm?"""
    conds = W.initial_conditions(n, n_conditions, mode)
    downstream = ("K_birthdeath", "K_mut", "K_inherit")
    seen = {k: {"clean": 0, "leak": 0} for k in downstream}
    for (g, m, social, leak, regime) in conds:
        spec = W.WorldSpec(n, g, m, social, leak, regime, W.ALL_ON)
        r = _events(me_mod, spec, ticks)
        if r["births"]:
            for k in downstream:
                seen[k]["leak" if leak else "clean"] += 1
    rows = []
    for k, v in seen.items():
        if v["clean"] == 0 and v["leak"] == 0:
            st = "UNREACHABLE_IN_ENUMERATED_CONDITIONS"
        elif v["clean"] == 0:
            st = "REACHABLE_ONLY_UNDER_LEAK"
        else:
            st = "REACHABLE_IN_CLEAN_ARM"
        rows.append({"kernel": k, "status": st, **v})
    return {
        "instrument": "kernel_exercisability",
        "n_org": n, "rows": rows,
        "leak_only": [r["kernel"] for r in rows
                      if r["status"] == "REACHABLE_ONLY_UNDER_LEAK"],
        "can_fail": True,
    }
