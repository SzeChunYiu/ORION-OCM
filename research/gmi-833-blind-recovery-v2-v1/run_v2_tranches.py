"""Blind v2 tranche runner — executes the frozen protocol's search side.

Reads ONLY: NEUTRAL_BATTERY_FREEZE_V1.json (+ the frozen generator module for
derived ablation batteries) and BASIS_GRID_V1.json. Produces
BLIND_OUTCOME_V2_T{1,2,3,4}.json containing candidate constructions, costs,
layer statistics, saturation/cap flags, and raw resource vectors. It contains
no family vocabulary and performs no fingerprint adjudication.

Tranches:
  T1  B_BOOL2 per-task (U_ORD primary, U_V1 contrast, U_ALL3 ablation) +
      class-universal machine (U_ORD + U_V1, PROC1 + PROC2).
  T2  B_DELAY all derived lags, M_STATE pairing search (U_ORD), guard
      ablation D=[-8,8] with l_max derived by the same counting bound.
  T3  B_LOCAL all 256 rules, four independent site expressions per rule
      (U_ORD), class-universal probe.
  T4  B_BOOL3 all 256 functions (U_ORD).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from battery_generate_v1 import delay_battery as delay_battery_by_rule  # noqa: E402
from neutral_search_v2 import (Basis, FastBasis,  # noqa: E402
                               expr_depth, expr_ops, expr_to_postfix,
                               jsonable, load_battery,
                               rows_to_atom_semantics,
                               semantic_cost_layered_dp,
                               semantic_cost_layered_dp_fast,
                               uniform_cost_best_first)


def raw_resources(e):
    ge = [1 for node in walk(e) if node[0] == "un" and node[1].startswith("GE")]
    consts = [1 for node in walk(e) if node[0] == "const"]
    return {"operation_nodes": expr_ops(e), "order_test_sites": len(ge),
            "depth": expr_depth(e), "constant_uses": len(consts)}


def walk(e):
    yield e
    for child in e[1:]:
        if isinstance(child, tuple):
            yield from walk(child)


def t1_bool2(battery):
    b2 = battery["batteries"]["B_BOOL2"]
    out = {"schema": "V2_BLIND_OUTCOME_T1", "tranche": "B_BOOL2", "runs": {}}
    # per-task shared DP per basis variant; the FIRST variant additionally
    # asserts encoded-fast/slow equivalence (same space, order, representatives)
    for tier, guard, tag in (("U_ORD", 3, "U_ORD_g3"), ("U_V1", 3, "U_V1_g3"),
                             ("U_ALL3", 1, "U_ALL3_g1")):
        basis = Basis(tier, guard)
        targets = [tuple(t["required_outputs"]) for t in b2["per_task_tasks"]]
        # shared DP over the shared atom semantics (all tasks share rows)
        atom_sem = rows_to_atom_semantics(b2["per_task_tasks"][0]["inputs"],
                                          ["x0", "x1"])
        res = semantic_cost_layered_dp(atom_sem, basis, targets)
        if tag == "U_ORD_g3":
            fb = FastBasis(tier, guard)
            res_fast = semantic_cost_layered_dp_fast(atom_sem, fb, targets)
            assert [r["cost"] for r in res_fast["targets"]] == \
                   [r["cost"] for r in res["targets"]]
            assert res_fast["layers"] == res["layers"]
        runs = []
        for task, t in zip(b2["per_task_tasks"], res["targets"]):
            entry = {"task_id": task["task_id"],
                     "cost": t["cost"] if t else None,
                     "expr": jsonable(t["expr"]) if t else None,
                     "raw_resources": raw_resources(t["expr"]) if t else None}
            if t and tag == "U_ORD_g3":
                ver = uniform_cost_best_first(atom_sem, basis,
                                              tuple(task["required_outputs"]))
                entry["proc2_verification"] = {
                    "procedure": "UNIFORM_COST_BEST_FIRST",
                    "cost": ver["cost"], "match": ver["cost"] == t["cost"]}
            runs.append(entry)
        out["runs"][tag] = {"tier": tier, "guard": guard,
                            "layers": res["layers"], "saturated": res["saturated"],
                            "cap_bound": res["cap_bound"],
                            "per_task": runs,
                            "per_task_costs": [r["cost"] for r in runs]}
    # class-universal machine
    u = b2["class_universal_task"]
    atom_names = ["t0", "t1", "t2", "t3", "x0", "x1"]
    atom_sem = rows_to_atom_semantics(u["inputs"], atom_names)
    target = tuple(u["required_outputs"])
    # universal-machine width bound: 400k retained semantics per run —
    # laptop-capacity bound (BASIS_GRID machine-capacity discipline),
    # reported as width_bound when hit; certificate = no tree solution
    # below the completed layers
    UNIVERSAL_WIDTH_CAP = 400_000
    for tier, tag in (("U_ORD", "U_ORD_g3"), ("U_V1", "U_V1_g3")):
        basis = FastBasis(tier, 3)
        t0 = time.time()
        res = semantic_cost_layered_dp_fast(atom_sem, basis, [target],
                                            width_cap=UNIVERSAL_WIDTH_CAP)
        dt = time.time() - t0
        rec = res["targets"][0]
        entry = {"tier": tier, "guard": 3, "seconds": round(dt, 2),
                 "layers": res["layers"], "saturated": res["saturated"],
                 "cap_bound": res["cap_bound"],
                 "width_bound": res.get("width_bound", False),
                 "width_cap": UNIVERSAL_WIDTH_CAP,
                 "cost": rec["cost"] if rec else None,
                 "expr": jsonable(rec["expr"]) if rec else None,
                 "raw_resources": raw_resources(rec["expr"]) if rec else None,
                 "postfix": list(expr_to_postfix(rec["expr"])) if rec else None}
        if rec and tag == "U_ORD_g3":
            ver = uniform_cost_best_first(atom_sem, basis, target)
            entry["proc2_verification"] = {
                "procedure": "UNIFORM_COST_BEST_FIRST",
                "cost": ver["cost"],
                "match": ver["cost"] == rec["cost"],
                "expanded": ver.get("expanded"),
                "node_capped": ver.get("node_capped", False),
                "postfix": ver["postfix"]}
        out["runs"].setdefault("class_universal", {})[tag] = entry
    return out


def t2_delay(battery):
    guard = 3
    out = {"schema": "V2_BLIND_OUTCOME_T2", "tranche": "B_DELAY", "runs": []}
    for b_guard, l_max_expected in ((3, 2), (8, 4)):
        import math
        l_max = int(math.floor(math.log2(2 * b_guard + 1)))
        assert l_max == l_max_expected, (l_max, l_max_expected)
        bat = delay_battery_by_rule(l_max)  # same frozen rule, derived battery
        basis = FastBasis("U_ORD", b_guard)
        domain = list(range(-b_guard, b_guard + 1))
        rows = [(s, x) for s in domain for x in (0, 1)]
        atom_sem = {"S": tuple(s for s, x in rows), "X": tuple(x for s, x in rows)}
        dp = semantic_cost_layered_dp_fast(atom_sem, basis, [], layer_cap=12,
                                           return_known=True)
        known = dp["known"]
        by_cost = {}
        for k in known:
            by_cost.setdefault(k["cost"], []).append(k)
        for task in bat["tasks"]:
            padded, required = task["machine_inputs"], task["required_outputs"]
            best = None
            for total in range(0, 13):
                pairs = 0
                for cs in range(0, total + 1):
                    for es in by_cost.get(cs, []):
                        for ey in by_cost.get(total - cs, []):
                            pairs += 1
                            ok, trace = simulate_state_machine(
                                es["expr"], ey["expr"], basis, padded, required)
                            if ok:
                                best = {"total_cost": total,
                                        "update": jsonable(es["expr"]),
                                        "output": jsonable(ey["expr"]),
                                        "pairs_enumerated_at_total": pairs}
                                break
                        if best:
                            break
                    if best:
                        break
                if best:
                    best["pairs_enumerated"] = pairs
                    break
            out["runs"].append({
                "guard": b_guard, "l_max": l_max, "task_id": task["task_id"],
                "lag": task["lag"], "machine": best,
                "state_semantics_known": len(known),
                "dp_layers": dp["layers"], "dp_saturated": dp["saturated"],
                "dp_cap_bound": dp["cap_bound"]})
    return out


def simulate_state_machine(e_s, e_y, basis, padded, required):
    s = 0
    trace = []
    for t, x in enumerate(padded):
        env = {"S": s, "X": x}
        y = expr_eval_local(e_y, env, basis)
        ns = expr_eval_local(e_s, env, basis)
        trace.append((t, s, x, y, ns))
        if y != required[t]:
            return False, trace
        s = ns
    return True, trace


def expr_eval_local(e, env, basis):
    op = e[0]
    if op == "atom":
        return env[e[1]]
    if op == "const":
        return e[1]
    if op == "un":
        return basis.unaries[e[1]][expr_eval_local(e[2], env, basis)]
    return expr_eval_local(e[1], env, basis) + expr_eval_local(e[2], env, basis)


def t3_local(battery):
    out = {"schema": "V2_BLIND_OUTCOME_T3", "tranche": "B_LOCAL", "runs": {}}
    bl = battery["batteries"]["B_LOCAL"]
    basis = FastBasis("U_ORD", 3)
    states = bl["per_rule_tasks"][0]["inputs"]
    atom_sem = rows_to_atom_semantics(states, ["a0", "a1", "a2", "a3"])
    targets, meta = [], []
    for task in bl["per_rule_tasks"]:
        for site in range(4):
            targets.append(tuple(r[site] for r in task["required_outputs"]))
            meta.append((task["task_id"], site))
    t0 = time.time()
    res = semantic_cost_layered_dp_fast(atom_sem, basis, targets)
    dt = time.time() - t0
    per_rule = {}
    for (tid, site), r in zip(meta, res["targets"]):
        per_rule.setdefault(tid, {})[site] = {
            "cost": r["cost"] if r else None,
            "expr": jsonable(r["expr"]) if r else None,
            "raw_resources": raw_resources(r["expr"]) if r else None}
    out["runs"]["per_rule"] = {
        "tier": "U_ORD", "guard": 3, "seconds": round(dt, 2),
        "layers": res["layers"], "saturated": res["saturated"],
        "cap_bound": res["cap_bound"],
        "site_costs_summary": _cost_summary(meta, res),
        "rules": [{"task_id": tid,
                   "site_costs": [per_rule[tid][s]["cost"] for s in range(4)],
                   "sites": [per_rule[tid][s] for s in range(4)]}
                  for tid in sorted(per_rule)]}
    # class-universal probe (heavier; capped)
    u = bl["class_universal_task"]
    out["runs"]["class_universal_probe"] = {
        "status": "DEFERRED_FEASIBILITY_PROBE", "rows_total": len(u["inputs"]),
        "note": "full class-universal machine search executed only if the "
                "per-rule morphology leaves an open question; probe recorded "
                "for cost attribution"}
    return out


def _cost_summary(meta, res):
    costs = [r["cost"] if r else None for r in res["targets"]]
    known = [c for c in costs if c is not None]
    return {"found": len(known), "missing": costs.count(None),
            "min": min(known) if known else None,
            "max": max(known) if known else None,
            "distinct_costs": sorted(set(known))}


def t4_bool3(battery):
    out = {"schema": "V2_BLIND_OUTCOME_T4", "tranche": "B_BOOL3", "runs": {}}
    b3 = battery["batteries"]["B_BOOL3"]
    basis = FastBasis("U_ORD", 3)
    atom_sem = rows_to_atom_semantics(b3["per_task_tasks"][0]["inputs"],
                                      ["i0", "i1", "i2"])
    targets = [tuple(t["required_outputs"]) for t in b3["per_task_tasks"]]
    t0 = time.time()
    res = semantic_cost_layered_dp_fast(atom_sem, basis, targets)
    dt = time.time() - t0
    out["runs"]["per_task"] = {
        "tier": "U_ORD", "guard": 3, "seconds": round(dt, 2),
        "layers": res["layers"], "saturated": res["saturated"],
        "cap_bound": res["cap_bound"],
        "cost_summary": _cost_summary(targets, res),
        "tasks": [{"task_id": t["task_id"],
                   "rank": t["rank"],
                   "cost": (r["cost"] if r else None),
                   "expr": jsonable(r["expr"]) if r else None,
                   "raw_resources": raw_resources(r["expr"]) if r else None}
                  for t, r in zip(b3["per_task_tasks"], res["targets"])]}
    return out


def main():
    battery = load_battery(HERE)
    results = {}
    for name, fn in (("T1", t1_bool2), ("T2", t2_delay),
                     ("T3", t3_local), ("T4", t4_bool3)):
        t0 = time.time()
        res = fn(battery)
        res["tranche_seconds"] = round(time.time() - t0, 2)
        results[name] = res
        path = HERE / f"BLIND_OUTCOME_V2_{name}.json"
        path.write_text(json.dumps(jsonable(res), indent=2, sort_keys=True) + "\n")
        print(json.dumps({"tranche": name, "seconds": res["tranche_seconds"],
                          "path": path.name}))
    print("ALL_TRANCHES_COMPLETE")


if __name__ == "__main__":
    main()
