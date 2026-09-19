# -*- coding: utf-8 -*-
"""Emergence by price -- route B, independent oracle.

Imports nothing from route A and no parent module.  It rebuilds the substrate,
the task families and all thirteen predicates from FREEZE_V1.md's own text and
recomputes every published quantity by a different mechanism:

  * the machine is a single dispatch table over a packed configuration integer,
    not a chain of name comparisons over a cell list;
  * programs are enumerated by an explicit odometer in descending symbol order,
    not by itertools.product ascending, and with no static prefilter at all;
  * costs come from the executed opcode stream, not from an accumulated count
    vector;
  * every predicate is written again from the freeze's wording, not reused;
  * the minimum-cost search is a full sort, not a running minimum.

    python3 -I -B independent_oracle_v1.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NV = 3
OPS = ("OBS0", "OBS1", "INC0", "INC1", "DEC0", "DEC1", "CPY01", "CPY10",
       "EMIT0", "EMIT1", "SKZ0", "SKZ1", "BNZ0", "BNZ1", "HLT")
OPS_R = OPS + ("RND0",)
OPS_W = OPS + ("WRT",)
SUBS = {"B0": OPS, "B0R": OPS_R, "B0W": OPS_W}
ENT = ((0, 0, 0), (1, 1, 1))


def price_of(ops, p_obs=1):
    return tuple(0 if o == "HLT" else (p_obs if o in ("OBS0", "OBS1", "RND0") else 1)
                 for o in ops)


def execute(prog, word, budget, ops, ent=(), mutable=False):
    code = list(prog)
    cell = [0, 0]
    pc = ip = ep = n = 0
    emitted, ev, stream = [], [], []
    stop = "RAN_OFF"
    changed, rerun = set(), False
    while n < budget:
        if not (0 <= pc < len(code)):
            break
        k = code[pc]
        o = ops[k]
        n += 1
        stream.append(k)
        if pc in changed:
            rerun = True
        if o == "OBS0" or o == "OBS1" or o == "RND0":
            d = 1 if o == "OBS1" else 0
            src, idx = (word, ip) if o != "RND0" else (ent, ep)
            if idx >= len(src):
                stop = "STALL"
                break
            cell[d] = src[idx]
            if o == "RND0":
                ep += 1
            else:
                ip += 1
            ev.append(("o", d, cell[d], n))
            pc += 1
        elif o in ("INC0", "INC1", "DEC0", "DEC1"):
            d = 1 if o.endswith("1") else 0
            cell[d] = (cell[d] + (1 if o.startswith("INC") else -1)) % NV
            pc += 1
        elif o == "CPY01":
            cell[0] = cell[1]
            pc += 1
        elif o == "CPY10":
            cell[1] = cell[0]
            pc += 1
        elif o in ("EMIT0", "EMIT1"):
            d = 1 if o == "EMIT1" else 0
            emitted.append(cell[d])
            ev.append(("e", d, cell[d], n))
            pc += 1
        elif o in ("SKZ0", "SKZ1"):
            d = 1 if o == "SKZ1" else 0
            t = cell[d] == 0
            ev.append(("b", o, d, cell[d], t, n))
            pc = pc + (2 if t else 1)
        elif o in ("BNZ0", "BNZ1"):
            d = 1 if o == "BNZ1" else 0
            t = cell[d] != 0
            ev.append(("b", o, d, cell[d], t, n))
            pc = 0 if t else pc + 1
        elif o == "WRT":
            if mutable and 0 <= cell[1] < len(code):
                if code[cell[1]] != cell[0] % len(ops):
                    changed.add(cell[1])
                code[cell[1]] = cell[0] % len(ops)
            pc += 1
        elif o == "HLT":
            ev.append(("h", n))
            stop = "HALT"
            break
    if n >= budget and stop == "RAN_OFF":
        stop = "BUDGET"
    return {"out": tuple(emitted), "ev": tuple(ev), "stream": tuple(stream),
            "stop": stop, "word": word,
            "selfmod": bool(changed) and rerun}


def odometer(base, length):
    """Descending enumeration, written as an explicit odometer."""
    digits = [base - 1] * length
    while True:
        yield tuple(digits)
        i = length - 1
        while i >= 0 and digits[i] == 0:
            digits[i] = base - 1
            i -= 1
        if i < 0:
            return
        digits[i] -= 1


# ------------------------------------------------------------- the predicates

def o_of(ev):
    return [e for e in ev if e[0] == "o"]


def e_of(ev):
    return [e for e in ev if e[0] == "e"]


def b_of(ev):
    return [e for e in ev if e[0] == "b"]


def q_adaptation(rs, price, ops):
    for a in range(len(rs)):
        for b in range(a + 1, len(rs)):
            if tuple(x[2] for x in o_of(rs[a]["ev"])) != \
               tuple(x[2] for x in o_of(rs[b]["ev"])) and rs[a]["out"] != rs[b]["out"]:
                return True
    return False


def q_history(rs, price, ops):
    for a in range(len(rs)):
        for b in range(a + 1, len(rs)):
            oa, ob = o_of(rs[a]["ev"]), o_of(rs[b]["ev"])
            ea, eb = e_of(rs[a]["ev"]), e_of(rs[b]["ev"])
            k = next((i for i in range(min(len(oa), len(ob))) if oa[i][2] != ob[i][2]), None)
            if k is None:
                continue
            j = next((i for i in range(min(len(ea), len(eb))) if ea[i][2] != eb[i][2]), None)
            if j is None:
                continue
            gap = ea[j][3] - oa[k][3]
            mid = [x for x in rs[a]["ev"] if oa[k][3] < x[-1] < ea[j][3]]
            if gap >= 2 and mid:
                return True
    return False


def q_reuse(rs, price, ops):
    for r in rs:
        ev = r["ev"]
        m = len(ev)
        for w in range(2, m // 2 + 1):
            for i in range(m - w + 1):
                sig = tuple(tuple(x[:-1]) for x in ev[i:i + w])
                for j in range(i + w, m - w + 1):
                    if tuple(tuple(x[:-1]) for x in ev[j:j + w]) == sig:
                        cut = ev[:i] + ev[i + w:]
                        if tuple(x[2] for x in cut if x[0] == "e") != r["out"]:
                            return True
    return False


def q_meta(rs, price, ops):
    seen = {}
    for i, r in enumerate(rs):
        for e in b_of(r["ev"]):
            seen.setdefault((e[1], e[2]), []).append((i, e[4], e[5]))
    for key in sorted(seen):
        rows = seen[key]
        if len(set(x[1] for x in rows)) < 2:
            continue
        got = {}
        for i, taken, step in rows:
            sc = 0
            for n, k in enumerate(rs[i]["stream"], start=1):
                if n > step:
                    sc += price[k]
            got.setdefault(taken, set()).add(sc)
        if len(got) == 2:
            allc = got[True] | got[False]
            if min(allc) != max(allc):
                return True
    return False


def q_endogenous(rs, price, ops):
    for a in range(len(rs)):
        for b in range(a + 1, len(rs)):
            oa, ob = o_of(rs[a]["ev"]), o_of(rs[b]["ev"])
            for k in range(min(len(oa), len(ob))):
                if oa[k][2] == ob[k][2]:
                    continue
                if oa[k][2] in rs[a]["out"] or ob[k][2] in rs[b]["out"]:
                    continue
                ra = tuple(x[:-1] for x in rs[a]["ev"] if x[-1] > oa[k][3])
                rb = tuple(x[:-1] for x in rs[b]["ev"] if x[-1] > ob[k][3])
                if ra != rb:
                    return True
    return False


def q_frontier(rs, price, ops):
    return False


def q_memory(rs, price, ops):
    for a in range(len(rs)):
        for b in range(a + 1, len(rs)):
            oa, ob = o_of(rs[a]["ev"]), o_of(rs[b]["ev"])
            ea, eb = e_of(rs[a]["ev"]), e_of(rs[b]["ev"])
            for i in range(min(len(oa), len(ob))):
                if oa[i][2] == ob[i][2]:
                    continue
                for j in range(min(len(ea), len(eb))):
                    if ea[j][2] == eb[j][2] or ea[j][3] <= oa[i][3]:
                        continue
                    if [x for x in oa if oa[i][3] < x[3] < ea[j][3]]:
                        return True
    return False


def q_routing(rs, price, ops):
    seen = {}
    for i, r in enumerate(rs):
        for e in b_of(r["ev"]):
            seen.setdefault((e[1], e[2]), []).append((i, e[4], e[5]))
    for key in sorted(seen):
        rows = seen[key]
        if len(set(x[1] for x in rows)) < 2:
            continue
        arms = {}
        for i, taken, step in rows:
            arms.setdefault(taken, set()).add(
                tuple(x[2] for x in rs[i]["ev"] if x[0] == "e" and x[3] > step))
        if len(arms) == 2 and arms[True] != arms[False]:
            return True
    return False


def q_search(rs, price, ops):
    shapes = []
    any_cycle = False
    for r in rs:
        per, vals = {}, {}
        for e in b_of(r["ev"]):
            per[(e[1], e[2])] = per.get((e[1], e[2]), 0) + 1
            vals.setdefault((e[1], e[2]), []).append(e[3])
        if any(per[k] >= 2 and len(set(vals[k])) >= 2 for k in per):
            any_cycle = True
        shapes.append(tuple(sorted(per.items())))
    return any_cycle and len(set(shapes)) >= 2


def q_prob(rs, price, ops):
    by = {}
    for r in rs:
        by.setdefault(r["word"], set()).add(r["out"])
    return any(len(v) >= 2 for v in by.values())


def q_rewrite(rs, price, ops):
    f, n = {}, 0
    for r in rs:
        ov = tuple(x[2] for x in o_of(r["ev"]))
        evv = tuple(x[2] for x in e_of(r["ev"]))
        if len(ov) != len(evv) or not evv:
            return False
        for a, b in zip(ov, evv):
            if f.get(a, b) != b:
                return False
            f[a] = b
            n += 1
    return n >= 2 and bool(f)


def q_learning(rs, price, ops):
    for r in rs:
        marks = set(x[3] for x in e_of(r["ev"]))
        segs, acc = [], 0
        for n, k in enumerate(r["stream"], start=1):
            acc += price[k]
            if n in marks:
                segs.append(acc)
                acc = 0
        if len(segs) < 2:
            continue
        for k in range(1, len(segs)):
            if all(segs[j] < segs[0] for j in range(k, len(segs))) and segs[k] < segs[0]:
                return True
    return False


def q_selfmod(rs, price, ops):
    return any(r["selfmod"] for r in rs)


Q = {"ADAPTATION": q_adaptation, "HISTORY_SENSITIVE_DEVELOPMENT": q_history,
     "REUSABLE_OPERATOR_ACQUISITION": q_reuse, "METAREASONING": q_meta,
     "ENDOGENOUS_EXPERIMENT_CHOICE": q_endogenous,
     "CAPABILITY_FRONTIER_EXPANSION": q_frontier, "MEMORY": q_memory,
     "ROUTING": q_routing, "SEARCH": q_search, "PROBABILISTIC_STATE": q_prob,
     "SYMBOLIC_REWRITING": q_rewrite, "LEARNING_LAWS": q_learning,
     "SELF_MODIFICATION": q_selfmod}


# --------------------------------------------------------- the task families

def out_is(table):
    def f(r):
        return r["stop"] in ("HALT", "RAN_OFF") and r["out"] == table[r["word"]]
    return f


def after_two_obs(table):
    base = out_is(table)

    def f(r):
        if not base(r):
            return False
        fe = next((x[3] for x in e_of(r["ev"])), None)
        return fe is not None and len([x for x in o_of(r["ev"]) if x[3] < fe]) >= 2
    return f


def search_req(r):
    if not (r["stop"] in ("HALT", "RAN_OFF") and r["out"] == (0,)):
        return False
    dec = set(i for i, o in enumerate(OPS) if o.startswith("DEC"))
    return sum(1 for k in r["stream"] if k in dec) >= r["word"][0]


def endo_req(r):
    t = {(0, 1): (1,), (1, 1): (2,)}
    if not (r["stop"] in ("HALT", "RAN_OFF") and r["out"] == t[r["word"]]):
        return False
    return r["word"][0] not in r["out"]


def selfmod_req(r):
    return r["stop"] in ("HALT", "RAN_OFF") and r["out"] == (1,) and r["selfmod"]


FAM = {
    "ADAPTATION": ([(0,), (1,)], out_is({(0,): (0,), (1,): (1,)}), 4, 12, "B0", 1, None),
    "HISTORY_SENSITIVE_DEVELOPMENT": ([(0, 0), (1, 0)],
                                      after_two_obs({(0, 0): (0,), (1, 0): (1,)}),
                                      5, 16, "B0", 1, None),
    "REUSABLE_OPERATOR_ACQUISITION": ([(1, 1)], out_is({(1, 1): (2, 2)}), 5, 16, "B0", 1, None),
    "METAREASONING": ([(0, 0), (1, 0)], out_is({(0, 0): (0,), (1, 0): (2,)}),
                      5, 16, "B0", 1, None),
    "ENDOGENOUS_EXPERIMENT_CHOICE": ([(0, 1), (1, 1)], endo_req, 5, 16, "B0", 1, None),
    "CAPABILITY_FRONTIER_EXPANSION": ([(0,), (1,)], out_is({(0,): (0,), (1,): (1,)}),
                                      4, 12, "B0", 1, None),
    "MEMORY": ([(1, 0), (2, 0)], after_two_obs({(1, 0): (1,), (2, 0): (2,)}),
               5, 16, "B0", 1, None),
    "ROUTING": ([(0,), (1,)], out_is({(0,): (0,), (1,): (1, 1)}), 5, 16, "B0", 1, None),
    "SEARCH": ([(1,), (2,)], search_req, 5, 16, "B0", 1, None),
    "PROBABILISTIC_STATE": ([()], (lambda r: r["stop"] in ("HALT", "RAN_OFF")),
                            3, 8, "B0", 2, "prob"),
    "SYMBOLIC_REWRITING": ([(1, 1), (2, 2)], out_is({(1, 1): (2, 2), (2, 2): (0, 0)}),
                           5, 16, "B0", 1, None),
    "LEARNING_LAWS": ([(1, 1, 1)], out_is({(1, 1, 1): (0, 0, 0)}), 5, 20, "B0", 1, "learn"),
    "SELF_MODIFICATION": ([(1,)], selfmod_req, 5, 16, "B0", 1, None),
}
REVIVE = {"PROBABILISTIC_STATE": "B0R", "SELF_MODIFICATION": "B0W"}


def solve(name, sub=None):
    words, req, L, S, dsub, runs, post = FAM[name]
    sub = sub or dsub
    ops = SUBS[sub]
    price = price_of(ops)
    mutable = (sub == "B0W")
    keep = []
    for ln in range(1, L + 1):
        for prog in odometer(len(ops), ln):
            rs, ok = [], True
            for w in words:
                for t in range(runs):
                    r = execute(prog, w, S, ops, ENT[t % len(ENT)], mutable)
                    if not req(r):
                        ok = False
                        break
                    rs.append(r)
                if not ok:
                    break
            if not ok:
                continue
            if post == "prob" and len(set(r["out"] for r in rs)) < 2:
                continue
            if post == "learn" and not q_learning(rs, price, ops):
                continue
            keep.append((prog, rs))
    return keep, ops, price


def judge(name, keep, ops, price):
    rows = []
    for prog, rs in keep:
        c = max(sum(price[k] for k in r["stream"]) for r in rs)
        rows.append((c, Q[name](rs, price, ops)))
    yes = sorted(c for c, h in rows if h)
    no = sorted(c for c, h in rows if not h)
    cm = yes[0] if yes else None
    cn = no[0] if no else None
    if cm is None:
        v, d = "NOT_EXPRESSIBLE", None
    elif cn is None:
        v, d = "FORCED_BY_REQUIREMENT", None
    elif cn - cm > 0:
        v, d = "EMERGES_BY_PRICE", cn - cm
    else:
        v, d = "DOES_NOT_EMERGE", cn - cm
    blind = sum(1 for _p, rs in keep
                if len(set(tuple(x[:-1] for x in r["ev"]) for r in rs)) == 1)
    return {"verdict": v, "delta": d, "c_star_M": cm, "c_star_notM": cn,
            "solutions": len(keep), "blind_solutions": blind}


def main():
    out = {"schema": "EMERGENCE_CONDITIONS_ORACLE_V1", "behaviours": {}, "revivals": {}}
    for name in sorted(FAM):
        keep, ops, price = solve(name)
        out["behaviours"][name] = judge(name, keep, ops, price)
    for name, sub in sorted(REVIVE.items()):
        keep, ops, price = solve(name, sub)
        e = judge(name, keep, ops, price)
        e["substrate"] = sub
        out["revivals"][name] = e
    hist = {}
    for e in out["behaviours"].values():
        hist[e["verdict"]] = hist.get(e["verdict"], 0) + 1
    out["verdict_histogram"] = hist
    out["emerges_by_price"] = sorted(k for k, e in out["behaviours"].items()
                                     if e["verdict"] == "EMERGES_BY_PRICE")
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
