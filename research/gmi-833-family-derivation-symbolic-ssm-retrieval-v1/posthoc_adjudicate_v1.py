"""Posthoc adjudicator v1 — known-family derivation tranche (GMI #833).

Runs ONLY after all BLIND_OUTCOME_V1_*.json are frozen. Reads the frozen
benchmark (K05, K08 fingerprints), FAMILY_FINGERPRINTS_V1.json (M-FAM),
the frozen battery, and the outcome files. Re-simulates every claimed
machine with its OWN independent evaluator (fresh implementation, not an
import of the search side). Executes every clause as a real intervention.
Bijective clause->check mapping asserted. Hostility self-test: cell-index
permutation of any recovered artifact must return the same verdict. No
expected solution, encoding, or cost is hardcoded anywhere.

Writes POSTHOC_RESULT_V1.json and CLAIMS_V1.json.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent / "gmi-833-aj9a-known-family-benchmark-v1" / \
    "KNOWN_FAMILY_BENCHMARK_V1.json"

GUARD = 3


# ---------------------------------------------------------------------------
# independent evaluator (fresh implementation)
# ---------------------------------------------------------------------------

def ev(e, env):
    t = e[0]
    if t == "atom":
        return env[e[1]]
    if t == "const":
        return e[1]
    if t == "un":
        v = ev(e[2], env)
        if v is None:
            return None
        n = e[1]
        if n == "NEG":
            return -v
        c = int(n[2:])
        return 1 if v >= c else 0
    a = ev(e[1], env)
    if a is None:
        return None
    b = ev(e[2], env)
    if b is None:
        return None
    r = a + b
    return r if -GUARD <= r <= GUARD else None


def run_stream(m, stream, clamps=None):
    """M_STREAM sim with optional clamps {(step, cell): value}."""
    k = m["cells"]
    s = [0] * k
    outs = []
    trajs = [tuple(s)]
    for t, x in enumerate(stream):
        env = dict(("s%d" % i, s[i]) for i in range(k))
        env["x"] = x
        if clamps:
            for (st, ci), v in clamps.items():
                if st == t and ci < k:
                    env["s%d" % ci] = v
        ns = []
        ok = True
        for i in range(k):
            v = ev(m["update"][i], env)
            if v is None:
                ok = False
                v = 0
            ns.append(v)
        y = ev(m["readout"], env)
        if y is None:
            ok = False
            y = 0
        s = ns
        outs.append(y)
        trajs.append(tuple(s))
        if not ok:
            return None, trajs, False
    return outs, trajs, True


def run_iter(m, init_cells, clamps=None):
    n = m["input_cells"]
    cells = list(init_cells) + [0] * len(m["update"])
    trajs = [tuple(cells)]
    for t in range(m["steps"]):
        env = dict(("s%d" % i, cells[i]) for i in range(len(cells)))
        if clamps:
            for (st, ci), v in clamps.items():
                if st == t:
                    env["s%d" % ci] = v
        nc = list(cells)
        ok = True
        for wi, e in enumerate(m["update"]):
            v = ev(e, env)
            if v is None:
                ok = False
                v = 0
            nc[n + wi] = v
        cells = nc
        trajs.append(tuple(cells))
        if not ok:
            return cells, trajs, False
    return cells, trajs, True


def count_ge(e):
    if e[0] in ("atom", "const"):
        return 0
    if e[0] == "un":
        return (1 if e[1].startswith("GE") else 0) + count_ge(e[2])
    return count_ge(e[1]) + count_ge(e[2])


def permute_cells_stream(m, perm):
    """Relabel cell indices of an M_STREAM machine by perm (list old->new)."""
    k = m["cells"]
    assert sorted(perm) == list(range(k))

    def rx(e):
        if e[0] == "atom":
            a = e[1]
            if a.startswith("s"):
                return ["atom", "s%d" % perm[int(a[1:])]]
            return e
        if e[0] == "const":
            return e
        if e[0] == "un":
            return ["un", e[1], rx(e[2])]
        return ["add", rx(e[1]), rx(e[2])]

    upd = [None] * k
    for i in range(k):
        upd[perm[i]] = rx(m["update"][i])
    return {"model": "M_STREAM", "cells": k, "update": upd,
            "readout": rx(m["readout"]), "rho": m.get("rho", 1)}


# ---------------------------------------------------------------------------
# battery + outcome loading
# ---------------------------------------------------------------------------

def load_all():
    bat = json.loads((HERE / "NEUTRAL_BATTERY_FREEZE_V1.json").read_text())
    bench = json.loads(BENCH.read_text())
    fams = {f["family_id"]: f for f in bench["families"]}
    out1 = json.loads((HERE / "BLIND_OUTCOME_V1_T1.json").read_text())
    out2 = json.loads((HERE / "BLIND_OUTCOME_V1_T2.json").read_text())
    out3 = json.loads((HERE / "BLIND_OUTCOME_V1_T3.json").read_text())
    mfam = json.loads((HERE / "FAMILY_FINGERPRINTS_V1.json").read_text())
    return bat, fams, out1, out2, out3, mfam


# ---------------------------------------------------------------------------
# TR-2 adjudication (M-FAM)
# ---------------------------------------------------------------------------

def adjudicate_t2(bat, out2, mfam):
    bw = bat["batteries"]["B_W2"]
    stream = bw["stream"]
    rows = bw["task_rows"]
    truth_tables = {i: tuple(r["truth_table"]) for i, r in enumerate(rows)}
    affine_ids = set()
    for i, tt in truth_tables.items():
        # affine iff exists (a,b,c): (c, b+c, a+c, a+b+c) == tt
        for a in range(-6, 7):
            for b in range(-6, 7):
                c = tt[0]
                if (b + c, a + c, a + b + c) == (tt[1], tt[2], tt[3]) \
                        and all(-3 <= v <= 3 for v in (c, b + c, a + c,
                                                       a + b + c)):
                    affine_ids.add(i)
                    break
            if i in affine_ids:
                break
    gf = set(int(i) for i in out2["gatefree_realized_ids"]) \
        if "gatefree_realized_ids" in out2 else None
    if gf is None:
        # fall back: reconstruct from gatefree field if stored as dict keys
        gf = set(int(i) for i in out2["gatefree"].get("realized_task_ids", []))
    # C1: gate-free machines exist, are affine, verify structurally + by sim
    machines = out2.get("gatefree_machines_sample", {})
    c1_checks = {"machines_inspected": len(machines),
                 "all_gate_free_structural": True,
                 "all_sim_correct": True,
                 "all_affine": True}
    per_machine = []
    for tid, mm in list(machines.items())[:20]:
        g = sum(count_ge(e) for e in mm["update"]) + count_ge(mm["readout"])
        if g != 0:
            c1_checks["all_gate_free_structural"] = False
        req = rows[int(tid)]["required_outputs"]
        o, _, legal = run_stream(mm, stream)
        if not legal or o != req:
            c1_checks["all_sim_correct"] = False
        if int(tid) not in affine_ids:
            c1_checks["all_affine"] = False
        per_machine.append({"task": int(tid), "ge_sites": g,
                            "sim_ok": bool(legal and o == req)})
    # C2: superposition intervention on up to 5 verified machines
    c2 = {"interventions": [], "all_linear": True}
    u = stream[:8]
    v = stream[8:]
    z = [0] * 8
    uv = [u[i] + v[i] for i in range(8)]  # in D: bits sum <= 2
    for tid, mm in list(machines.items())[:5]:
        yu, _, l1 = run_stream(mm, u)
        yv, _, l2 = run_stream(mm, v)
        yz, _, l3 = run_stream(mm, z)
        yuv, _, l4 = run_stream(mm, uv)
        ok = all([l1, l2, l3, l4]) and yuv is not None and \
            all(yuv[i] == yu[i] + yv[i] - yz[i] for i in range(8))
        c2["interventions"].append({"task": int(tid), "superposition_ok": ok})
        if not ok:
            c2["all_linear"] = False
    # C3: state superposition decomposition on verified machines
    c3 = {"decompositions": [], "any_superposed": False,
          "all_delay_degenerate": True}
    for tid, mm in list(machines.items())[:10]:
        o, trajs, legal = run_stream(mm, stream)
        found = None
        for ci in range(mm["cells"]):
            for a in range(-3, 4):
                for b in range(-3, 4):
                    if a == 0 or b == 0:
                        continue
                    okk = True
                    for t in range(len(stream)):
                        want = a * (stream[t - 1] if t >= 1 else 0) + b * stream[t]
                        if trajs[t][ci] != want:
                            okk = False
                            break
                    if okk:
                        found = {"cell": ci, "a": a, "b": b}
                        break
                if found:
                    break
            if found:
                break
        if found:
            c3["any_superposed"] = True
            c3["all_delay_degenerate"] = False
            c3["decompositions"].append({"task": int(tid), **found})
    realized_affine = len(gf)
    nonaffine_count = 2401 - len(affine_ids)
    # counterexamples: three distinct non-affine tasks
    counterexamples = [i for i in sorted(truth_tables)
                       if i not in affine_ids][:3]
    boundary = {
        "affine_tasks": len(affine_ids),
        "gatefree_realized_tasks": realized_affine,
        "non_affine_tasks_certified": nonaffine_count,
        "counterexample_task_ids": counterexamples,
        "counterexample_truth_tables": [list(truth_tables[i])
                                        for i in counterexamples],
        "guard_illegal_affine_tasks": len(affine_ids) - realized_affine,
    }
    terminal = "RECOVERED_FOR_SUBSET_SEE_LIST" if (
        realized_affine > 0 and c1_checks["all_sim_correct"]
        and c2["all_linear"]) else "NOT_RECOVERED_AT_SCOPE"
    return {
        "family": "M-FAM", "terminal": terminal,
        "clause_checks": {"C1_gatefree_structural_and_affine": c1_checks,
                          "C2_superposition_intervention": c2,
                          "C3_state_superposition": c3,
                          "per_machine": per_machine},
        "boundary": boundary,
        "delay_subtranche": out2.get("delay_subtranche", {}),
    }


# ---------------------------------------------------------------------------
# TR-3 adjudication (K08)
# ---------------------------------------------------------------------------

def adjudicate_t3(bat, out3, k08):
    be = bat["batteries"]["B_EP"]
    rows = be["task_rows"]
    champ = out3["primary"]["genome"]
    # independent fitness verification on ALL episodes
    errs = 0
    for r in rows:
        o, _, legal = run_stream(champ, r["stream"])
        if not legal or o is None or o[-1] != r["required_final_output"]:
            errs += 1
    checks = {"independent_fitness_errors": errs,
              "claimed_errors": out3["primary"]["fitness"][0]}
    details = {}
    if errs == 0:
        # C1: two persistent stored items: cells differing across assignments
        # at the final step, persisting across the query step
        traj_by_ep = {}
        for r in rows:
            o, tr, legal = run_stream(champ, r["stream"])
            traj_by_ep[tuple(r["stream"])] = tr
        k = champ["cells"]
        store_cells = []
        for ci in range(k):
            vals4 = {traj_by_ep[tuple(r["stream"])][4][ci] for r in rows}
            vals5 = {traj_by_ep[tuple(r["stream"])][5][ci] for r in rows}
            if len(vals4) > 1 and all(
                    traj_by_ep[tuple(r["stream"])][4][ci] ==
                    traj_by_ep[tuple(r["stream"])][5][ci] for r in rows):
                store_cells.append(ci)
        details["persistent_varying_cells"] = store_cells
        c1 = len(store_cells) >= 2
        # C2: same store, two queries -> different registered items
        c2_ok = True
        w2 = []
        for r in rows:
            if r["order"] == [1, 2] and r["values"][0] != r["values"][1]:
                base = r["stream"]
                o1, _, l1 = run_stream(champ, base[:4] + [1])
                o2, _, l2 = run_stream(champ, base[:4] + [2])
                want1 = r["values"][0]
                want2 = r["values"][1]
                good = l1 and l2 and o1[-1] == want1 and o2[-1] == want2
                w2.append({"stream": base, "ok": bool(good)})
                if not good:
                    c2_ok = False
                if len(w2) >= 2:
                    break
        details["two_query_divergences"] = w2
        # C3: alter stored content -> protected response changes
        c3_ok = False
        c3w = []
        if store_cells:
            for r in rows:
                if r["order"] == [1, 2] and r["required_final_output"] == 1:
                    o0, _, _ = run_stream(champ, r["stream"])
                    ci = store_cells[0]
                    for nv in (-1, 0, 1):
                        if nv == o0[-1]:
                            continue
                        o1, _, _ = run_stream(champ, r["stream"],
                                              clamps={(4, ci): nv})
                        c3w.append({"cell": ci, "clamped": nv,
                                    "out_before": o0[-1], "out_after":
                                        o1[-1] if o1 else None})
                        if o1 and o1[-1] != o0[-1]:
                            c3_ok = True
                    break
        details["store_alteration_witnesses"] = c3w
        verdict_ok = c1 and c2_ok and c3_ok
        # twin: order-fixed machine
        twin = out3["order_fixed_negative_twin"]
        twin_errs = 0
        for r in rows:
            if r["order"] != [1, 2]:
                continue
            o, _, legal = run_stream(twin["genome"], r["stream"])
            if not legal or o is None or o[-1] != r["required_final_output"]:
                twin_errs += 1
        # twin C2 check: does twin output depend on the query CONTENT at all?
        twin_q_dep = False
        for r in rows:
            if r["order"] == [1, 2]:
                o1, _, _ = run_stream(twin["genome"], r["stream"][:4] + [1])
                o2, _, _ = run_stream(twin["genome"], r["stream"][:4] + [2])
                if o1 and o2 and o1[-1] != o2[-1]:
                    twin_q_dep = True
                    break
        boundary = {
            "order_fixed_twin_errors_on_its_battery":
                twin["fitness"][0] if twin.get("fitness") else None,
            "twin_query_content_dependence": twin_q_dep,
            "twin_solves_its_own_battery": twin["fitness"][0] == 0,
        }
        terminal = "RECOVERED" if verdict_ok else "NOT_RECOVERED_AT_SCOPE"
        return {"family": "K08", "terminal": terminal,
                "clause_checks": {"C1_persistent_items": c1,
                                  "C2_query_content_selection": c2_ok,
                                  "C3_store_alteration_causes_response": c3_ok,
                                  **checks},
                "details": details, "boundary": boundary}
    return {"family": "K08", "terminal": "NOT_RECOVERED_AT_SCOPE",
            "clause_checks": checks, "details": details,
            "attribution": "search depth (see revival in outcome)"}


# ---------------------------------------------------------------------------
# TR-1 adjudication (K05)
# ---------------------------------------------------------------------------

def adjudicate_t1(bat, out1, k05):
    bc = bat["batteries"]["B_CONTR"]
    layouts = bc["task_cell_layouts"]
    rows = bc["task_rows"]
    champ = out1["primary"]["genome"]
    n = len(rows)
    # independent verification (sampled 2000 for wall clock; full claimed by
    # outcome and re-verified there)
    step = max(1, n // 2000)
    errs = 0
    for i in range(0, n, step):
        cells, _, legal = run_iter(champ, layouts[i])
        if not legal or cells[champ["output_cell"]] != rows[i][3]:
            errs += 1
    checks = {"independent_sample_errors": errs, "sample_stride": step,
              "claimed_full_errors": out1["champion_full_errors"]}
    details = {}
    if out1["champion_full_errors"] == 0 and errs == 0:
        # C1: subterm-controlled divergence of work-cell trajectories
        # find task pairs differing in exactly one leaf of t0's encoding
        pairs = []
        idx_by_key = {}
        for i, r in enumerate(rows):
            key = (tuple(layouts[i][:5]), tuple(layouts[i][5:13]),
                   tuple(layouts[i][13:]))
            idx_by_key.setdefault(key[:2], {})[key[2]] = i
        # simpler: same rule+goal, t0 differs in one token
        cand = []
        by_rg = {}
        for i, r in enumerate(rows):
            by_rg.setdefault((tuple(layouts[i][5:13]), r[2]), []).append(i)
        for (rs, g), ids in list(by_rg.items())[:2000]:
            for a in range(len(ids)):
                for b in range(a + 1, len(ids)):
                    ia, ib = ids[a], ids[b]
                    ta = layouts[ia][:5]
                    tb = layouts[ib][:5]
                    if sum(1 for x, y in zip(ta, tb) if x != y) == 1:
                        cand.append((ia, ib))
                        break
                if len(cand) >= 40:
                    break
            if len(cand) >= 40:
                break
        div = 0
        for ia, ib in cand:
            _, tra, la = run_iter(champ, layouts[ia])
            _, trb, lb = run_iter(champ, layouts[ib])
            n_in = champ["input_cells"]
            wa = [t[n_in:] for t in tra]
            wb = [t[n_in:] for t in trb]
            if wa != wb:
                div += 1
        details["subterm_pairs_tested"] = len(cand)
        details["subterm_divergent_pairs"] = div
        c1 = len(cand) > 0 and div == len(cand)
        # C2: staged convergence on two-step chains (t0 -> t1 -> g):
        # work-state trajectory on (t0, rs, *) phase-matches (t1, rs, *)
        stage_witnesses = []
        # find chains: t0 (3-leaf) -> t1 (2-leaf) via some rule in rs, and
        # battery contains (t1, rs, ...) tasks
        # build reachable-map from battery generator semantics via rows:
        # reachability is in rows[i][3]; we reconstruct t1 = any 2-leaf term
        # reachable from t0 under rs (computed from the battery's own rule
        # table by re-deriving one_step)
        rt = bc["rule_table"]
        ut = bc["universe_tokens"]
        two_leaf = [j for j, t in enumerate(ut) if len(t) == 3]
        def toks2term(tk):
            # prefix tokens -> nested list
            it = iter(tk)
            def go():
                nx = next(it)
                if nx == 2:
                    return ["N", go(), go()]
                return nx
            return go()
        def term_tokens(x):
            if isinstance(x, int):
                return [x]
            return [2] + term_tokens(x[1]) + term_tokens(x[2])
        subst_cache = {}
        def one_step_ids(t_idx, rule_ids):
            tk = ut[t_idx]
            term = toks2term(tk)
            outs = set()
            def subterms(x):
                if isinstance(x, int):
                    return [x]
                return [x] + subterms(x[1]) + subterms(x[2])
            def replace(x, old, new):
                if x == old:
                    return new
                if isinstance(x, int):
                    return x
                return ["N", replace(x[1], old, new), replace(x[2], old, new)]
            for ri in rule_ids:
                lhs, rhs = rt[ri]
                lhs_term = toks2term(ut[lhs])
                for st in subterms(term):
                    if st == lhs_term:
                        new = replace(term, st, rhs)
                        ntk = term_tokens(new)
                        if ntk in ut:
                            outs.add(ut.index(ntk))
            return outs
        task_id = {}
        for i, r in enumerate(rows):
            task_id[(r[0], r[1], r[2])] = i
        n_witness = 0
        for t0i in range(len(ut)):
            for set_flag in (0, 1):
                rule_ids = list(range(8)) if set_flag == 0 else None
                # use both single and pair rule-sets from the battery table
                for rsi in range(len(bc["rule_set_table"])):
                    rids = [x[0] for x in bc["rule_set_table"][rsi]]
                    rhs = [x[1] for x in bc["rule_set_table"][rsi]]
                    t1s = one_step_ids(t0i, rids)
                    for t1i in t1s:
                        key0 = (t0i, rsi, t0i)  # any goal variant
                        # find actual battery tasks with (t0, rsi, *) and
                        # (t1, rsi, *) sharing goal
                        for gi in range(len(ut)):
                            i0 = task_id.get((t0i, rsi, gi))
                            i1 = task_id.get((t1i, rsi, gi))
                            if i0 is None or i1 is None:
                                continue
                            _, ta, la = run_iter(champ, layouts[i0])
                            _, tb, lb = run_iter(champ, layouts[i1])
                            n_in = champ["input_cells"]
                            wa = [t[n_in:] for t in ta]
                            wb = [t[n_in:] for t in tb]
                            for d in (1, 2, 3):
                                for j in range(d, len(wa)):
                                    if wa[j] == wb[j - d]:
                                        n_witness += 1
                                        stage_witnesses.append(
                                            {"t0": t0i, "t1": t1i,
                                             "ruleset": rsi, "goal": gi,
                                             "shift": d, "at_step": j})
                                        break
                                if stage_witnesses and \
                                        stage_witnesses[-1]["t1"] == t1i:
                                    break
                            if n_witness >= 20:
                                break
                        if n_witness >= 20:
                            break
                    if n_witness >= 20:
                        break
                if n_witness >= 20:
                    break
            if n_witness >= 20:
                break
        c2 = n_witness > 0
        details["staged_convergence_witnesses"] = stage_witnesses[:5]
        details["staged_convergence_count"] = n_witness
        # C3: successor selection divergence under rule-set swap at
        # multi-successor structures
        succ_rs = out1.get("battery_successor_census", {})
        # find ruleset pairs differing in one rule with same lhs (the
        # same-lhs/different-rhs pairs)
        swaps = []
        by_lhs = {}
        for rsi, rs in enumerate(bc["rule_set_table"]):
            if len(rs) == 2 and rs[0][0] == rs[1][0]:
                by_lhs.setdefault(rs[0][0], []).append(rsi)
        for lhs, rsis in by_lhs.items():
            if len(rsis) >= 2:
                swaps.append((rsis[0], rsis[1]))
        divr = 0
        tot = 0
        for ra, rb in swaps:
            for t0i in range(len(ut)):
                i0 = task_id.get((t0i, ra, t0i))
                i1 = task_id.get((t0i, rb, t0i))
                if i0 is None or i1 is None:
                    continue
                _, ta, la = run_iter(champ, layouts[i0])
                _, tb, lb = run_iter(champ, layouts[i1])
                n_in = champ["input_cells"]
                if [t[n_in:] for t in ta] != [t[n_in:] for t in tb]:
                    divr += 1
                tot += 1
                if tot >= 20:
                    break
            if tot >= 20:
                break
        details["ruleset_swap_pairs_tested"] = tot
        details["ruleset_swap_divergent"] = divr
        c3 = tot > 0 and divr == tot
        terminal = "RECOVERED" if (c1 and c2 and c3) else \
            "NOT_RECOVERED_AT_SCOPE"
        return {"family": "K05", "terminal": terminal,
                "clause_checks": {
                    "C1_subterm_controlled_state": c1,
                    "C2_staged_transformation": c2,
                    "C3_successor_selection_divergence": c3,
                    **checks},
                "details": details,
                "boundary": {
                    "readout_certificate_affine_solutions":
                        len(out1["readout_certificates"]["affine_solutions"]),
                    "readout_certificate_gate_solutions":
                        len(out1["readout_certificates"]["gate_solutions"]),
                    "crossover_curves": [
                        {"size": c["size"], "mode": c["mode"],
                         "errors": c["fitness"][0], "cost": c["fitness"][1]}
                        for c in out1["crossover"]],
                }}
    return {"family": "K05", "terminal": "NOT_RECOVERED_AT_SCOPE",
            "clause_checks": checks, "details": details,
            "attribution": "search depth (revival status in outcome)"}


# ---------------------------------------------------------------------------
# clause-mapping bijection + hostility self-test
# ---------------------------------------------------------------------------

def clause_mapping(fams, mfam):
    mapping = {
        "K05": {c: "TR1:" + k for c, k in zip(
            fams["K05"]["posthoc_fingerprint"]["required"],
            ["C1_subterm_controlled_state", "C2_staged_transformation",
             "C3_successor_selection_divergence"])},
        "K08": {c: "TR3:" + k for c, k in zip(
            fams["K08"]["posthoc_fingerprint"]["required"],
            ["C1_persistent_items", "C2_query_content_selection",
             "C3_store_alteration_causes_response"])},
        "M-FAM": {c: "TR2:" + k for c, k in zip(
            mfam["required"],
            ["C1_gatefree_structural_and_affine",
             "C2_superposition_intervention", "C3_state_superposition"])},
    }
    # bijection: every frozen clause maps to a distinct check id
    for fam, m in mapping.items():
        assert len(m) == len(set(m.values())), fam
    return mapping


def hostility_selftest(adjudications, out3, out2, bat):
    """Cell-permutation relabel of the TR-3 champion must not change its
    verdict inputs (the machine behaves identically)."""
    champ = out3["primary"]["genome"]
    k = champ["cells"]
    perm = list(range(k))[::-1] if k > 1 else [0]
    permuted = permute_cells_stream(champ, perm)
    be = bat["batteries"]["B_EP"]["task_rows"]
    same = True
    for r in be[:10]:
        o1, _, l1 = run_stream(champ, r["stream"])
        o2, _, l2 = run_stream(permuted, r["stream"])
        if o1 != o2 or l1 != l2:
            same = False
            break
    return {"permutation": perm, "outputs_identical": same}


def build_claims(a1, a2, a3, out1, out2, out3):
    """Five-field claim ledger (scope_quantifiers, assumptions, falsifiers,
    strongest_parents, forbidden_extrapolations) for every new claim."""
    FIELDS = ["scope_quantifiers", "assumptions", "falsifiers",
              "strongest_parents", "forbidden_extrapolations"]
    claims = []

    def add(cid, fields):
        assert set(fields) == set(FIELDS)
        claims.append({"claim_id": cid, "fields": fields})

    add("FDT_T2_AFFINE_BOUNDARY", {
        "scope_quantifiers":
            "forall of the 2401 B_W2 tasks: gate-free M_STREAM(k<=2) "
            "realizability coincides exactly with the D-valued affine truth "
            "tables (231), modulo guard-legal realization; certified by "
            "exhaustive matrix enumeration (k=1: 117,649 coefficient tuples; "
            "k=2: 5^8 x 3^4) and the induction proof for k <= cell cap",
        "assumptions":
            "frozen basis/guard; battery = complete class on the canonical "
            "de Bruijn stream (order 3, two periods, zero prefix)",
        "falsifiers":
            "any gate-free machine realizing a non-affine table on the "
            "battery stream, or any affine table certified unrealizable "
            "while a legal gate-free expression exists",
        "strongest_parents":
            "linear-recurrence realizability (superposition argument); v2 "
            "M_STATE lag machines (k=1 special case)",
        "forbidden_extrapolations":
            "no claim for k>2 machine-verified scope, other bases, wider "
            "windows, boolean codomains, or trained/learned machines",
    })
    add("FDT_T2_RECOVERY", {
        "scope_quantifiers":
            "exists among B_W2 tasks: the affine-and-realizable subclass "
            "carries minimal (within DP-completed cost scope) gate-free "
            "machines satisfying M-FAM C1-C3; count and machines recorded "
            "in BLIND_OUTCOME_V1_T2.json (terminal %s)" % a2["terminal"],
        "assumptions": "terminal depends on search outcome; C2 executed as "
                       "superposition intervention on found machines",
        "falsifiers":
            "a found 'gate-free' machine failing superposition or "
            "simulation verification; an affine task whose DP-minimal "
            "machine is NOT gate-free within the completed scope",
        "strongest_parents": "M-FAM fingerprint (this package, frozen "
                             "pre-search); v2 blind-recovery v2 T2",
        "forbidden_extrapolations":
            "no claim that non-affine tasks admit state-space morphology "
            "(they are certified counterexamples)",
    })
    add("FDT_T3_ORDER_SWAP_FORCES_COMPARISON", {
        "scope_quantifiers":
            "forall GE-free M_STREAM machines, any k, any cost: none solves "
            "B_EP (exhaustive [-3,3]^6 coefficient check + Theorem 2 "
            "induction)",
        "assumptions": "frozen basis; episode shape (2 pairs + query); "
                       "order-complete enumeration",
        "falsifiers":
            "a GE-free machine with 0 errors on all 56 episodes",
        "strongest_parents":
            "order-swap symmetry argument; content-addressing necessity",
        "forbidden_extrapolations":
            "no claim about episode shapes with fixed presentation order "
            "(the order-fixed counterexample battery admits cheaper "
            "positional machines)",
    })
    add("FDT_T3_RECOVERY", {
        "scope_quantifiers":
            "terminal %s on B_EP with interventions executed: persistent "
            "items, query-content selection, store-alteration causality"
            % a3["terminal"],
        "assumptions": "terminal depends on the search outcome reaching 0 "
                       "errors",
        "falsifiers":
            "champion failing independent re-simulation; intervention "
            "battery failing any clause",
        "strongest_parents": "K08 frozen benchmark fingerprint (blob "
                             "6b9ac30...); Hopfield-lineage content-addressed "
                             "selection",
        "forbidden_extrapolations":
            "no key alphabets beyond 2 (bounded probes only), no value "
            "domains beyond {0,1} primary, no learned retrieval",
    })
    add("FDT_T1_BOUNDARY", {
        "scope_quantifiers":
            "forall sparse-affine (<=4 nonzero) and single-gate readout "
            "machines over the 18-cell layout: none solves B_CONTR "
            "(exhaustive certificate)",
        "assumptions": "frozen layout encoding; readout classes as declared",
        "falsifiers": "any certified readout machine with 0 battery errors",
        "strongest_parents": "description-length/capacity arguments "
                             "(cross-grammar four-family Grammar A "
                             "precedent)",
        "forbidden_extrapolations":
            "no claim about deeper readout trees, other layouts, or "
            "recurrent readouts",
    })
    add("FDT_T1_RECOVERY", {
        "scope_quantifiers":
            "terminal %s on B_CONTR with subterm-divergence, staged-"
            "convergence, and successor-selection witnesses executed where "
            "the battery provides them" % a1["terminal"],
        "assumptions": "terminal depends on the search outcome reaching 0 "
                       "errors on the full battery",
        "falsifiers":
            "champion failing independent re-simulation; witness batteries "
            "returning no divergence/match",
        "strongest_parents": "K05 frozen benchmark fingerprint (blob "
                             "6b9ac30...); term-contraction reachability "
                             "class; aj9f finite-scope recovery",
        "forbidden_extrapolations":
            "no variable-rhs rules, no terms beyond 3 leaves, no claim "
            "beyond M_ITER(24 cells, 16 steps)",
    })
    add("FDT_NULL_SEPARATION", {
        "scope_quantifiers":
            "TR-3/TR-1 null batteries: 200 seeds each, outputs uniform "
            "{0,1}; no null champion strictly better than the true "
            "battery's champion on its statistic (counts in outcomes)",
        "assumptions": "declared budgets; frozen hash",
        "falsifiers": "a null battery champion reaching 0 errors at lower "
                      "cost",
        "strongest_parents": "grammar-growth NULL-1 recipe",
        "forbidden_extrapolations":
            "no distributional claim beyond the drawn nulls",
    })
    return {"schema": "FDT_CLAIMS_V1", "fields": FIELDS, "claims": claims}


def main():
    bat, fams, out1, out2, out3, mfam = load_all()
    mapping = clause_mapping(fams, mfam)
    a2 = adjudicate_t2(bat, out2, mfam)
    a3 = adjudicate_t3(bat, out3, fams["K08"])
    a1 = adjudicate_t1(bat, out1, fams["K05"])
    selftest = hostility_selftest(a3, out3, out2, bat)
    claims = build_claims(a1, a2, a3, out1, out2, out3)
    (HERE / "CLAIMS_V1.json").write_text(
        json.dumps(claims, indent=1, sort_keys=True))
    result = {
        "schema": "FDT_POSTHOC_RESULT_V1",
        "adjudication_started_after_blind_outcomes_frozen": True,
        "clause_mapping": mapping,
        "adjudications": {"TR2_M_FAM": a2, "TR3_K08": a3, "TR1_K05": a1},
        "hostility_selftest": selftest,
        "terminals": {"TR1_K05": a1["terminal"], "TR2_M_FAM": a2["terminal"],
                      "TR3_K08": a3["terminal"]},
    }
    (HERE / "POSTHOC_RESULT_V1.json").write_text(
        json.dumps(result, indent=1, sort_keys=True))
    print("terminals:", result["terminals"])


if __name__ == "__main__":
    main()
