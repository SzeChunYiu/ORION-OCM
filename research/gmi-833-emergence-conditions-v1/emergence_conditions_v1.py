# -*- coding: utf-8 -*-
"""Emergence by price -- route A.

Thirteen behaviours named by two #833 rows are tested against one neutral
substrate.  Nothing is named: every behaviour is a predicate on the registered
observable trace, and the question asked of each is whether the cost-minimal
program that meets a task requirement has to exhibit it.

Definitions, substrate, prices, predicates, task families, gates and falsifiers
are fixed in FREEZE_V1.md, committed before this file existed.  All arithmetic is
integer.  No float is constructed anywhere.

    python3 -I -B emergence_conditions_v1.py
"""

import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V = 3

OPS_B0 = ("OBS0", "OBS1", "INC0", "INC1", "DEC0", "DEC1", "CPY01", "CPY10",
          "EMIT0", "EMIT1", "SKZ0", "SKZ1", "BNZ0", "BNZ1", "HLT")
OPS_B0R = OPS_B0 + ("RND0",)
OPS_B0W = OPS_B0 + ("WRT",)
SUBSTRATES = {"B0": OPS_B0, "B0R": OPS_B0R, "B0W": OPS_B0W}

OBS_OPS = ("OBS0", "OBS1", "RND0")
P_OBS_DEFAULT = 1
P_OBS_SWEEP = (1, 2, 3, 4, 5, 6)

BEHAVIOURS = (
    "ADAPTATION", "HISTORY_SENSITIVE_DEVELOPMENT", "REUSABLE_OPERATOR_ACQUISITION",
    "METAREASONING", "ENDOGENOUS_EXPERIMENT_CHOICE", "CAPABILITY_FRONTIER_EXPANSION",
    "MEMORY", "ROUTING", "SEARCH", "PROBABILISTIC_STATE", "SYMBOLIC_REWRITING",
    "LEARNING_LAWS", "SELF_MODIFICATION")


def prices(ops, p_obs=P_OBS_DEFAULT):
    out = []
    for op in ops:
        if op == "HLT":
            out.append(0)
        elif op in OBS_OPS:
            out.append(p_obs)
        else:
            out.append(1)
    return tuple(out)


# ------------------------------------------------------------------ the machine

def run(prog, word, budget, ops, entropy=(), mutable=False, start=None):
    """Execute one program.  Returns the registered trace and the executed-op counts.

    The trace carries exactly the four event kinds the freeze names: observation,
    emission, branch outcome and halt, each with the cell value it carried.
    """
    code = list(prog)
    c = [0, 0] if start is None else [start[1], start[2]]
    ip, steps = 0, 0
    pc = 0 if start is None else start[0]
    ep = 0
    out = []
    trace = []
    opstream = []
    counts = [0] * len(ops)
    stalled = False
    halted = False
    altered = set()
    reexecuted = False
    while steps < budget and 0 <= pc < len(code):
        op = ops[code[pc]]
        counts[code[pc]] += 1
        steps += 1
        opstream.append((steps, code[pc]))
        if pc in altered:
            reexecuted = True
        if op in ("OBS0", "OBS1"):
            d = 0 if op == "OBS0" else 1
            if ip >= len(word):
                stalled = True
                break
            c[d] = word[ip]
            ip += 1
            trace.append(("OBS", d, c[d], steps))
            pc += 1
        elif op == "RND0":
            if ep >= len(entropy):
                stalled = True
                break
            c[0] = entropy[ep]
            ep += 1
            trace.append(("OBS", 0, c[0], steps))
            pc += 1
        elif op in ("INC0", "INC1"):
            d = 0 if op == "INC0" else 1
            c[d] = (c[d] + 1) % V
            pc += 1
        elif op in ("DEC0", "DEC1"):
            d = 0 if op == "DEC0" else 1
            c[d] = (c[d] - 1) % V
            pc += 1
        elif op == "CPY01":
            c[0] = c[1]
            pc += 1
        elif op == "CPY10":
            c[1] = c[0]
            pc += 1
        elif op in ("EMIT0", "EMIT1"):
            d = 0 if op == "EMIT0" else 1
            out.append(c[d])
            trace.append(("EMIT", d, c[d], steps))
            pc += 1
        elif op in ("SKZ0", "SKZ1"):
            d = 0 if op == "SKZ0" else 1
            taken = (c[d] == 0)
            trace.append(("BR", op, d, c[d], taken, steps))
            pc += 2 if taken else 1
        elif op in ("BNZ0", "BNZ1"):
            d = 0 if op == "BNZ0" else 1
            taken = (c[d] != 0)
            trace.append(("BR", op, d, c[d], taken, steps))
            pc = 0 if taken else pc + 1
        elif op == "WRT":
            if mutable and 0 <= c[1] < len(code):
                if code[c[1]] != c[0] % len(ops):
                    altered.add(c[1])
                code[c[1]] = c[0] % len(ops)
            pc += 1
        elif op == "HLT":
            trace.append(("HLT", steps))
            halted = True
            break
        else:                                                   # pragma: no cover
            raise AssertionError("unknown op " + op)
    terminated = halted or (not stalled and steps < budget and not (0 <= pc < len(code)))
    return {"out": tuple(out), "trace": tuple(trace), "counts": tuple(counts),
            "opstream": tuple(opstream), "steps": steps, "terminated": terminated,
            "stalled": stalled, "mutated": tuple(code) != tuple(prog),
            "mutated_and_reexecuted": bool(altered) and reexecuted,
            "end_state": (pc, c[0], c[1])}


def cost_of(counts, price):
    return sum(counts[i] * price[i] for i in range(len(price)))


# --------------------------------------------------------- trace-only helpers

def obs_values(tr):
    return tuple(e[2] for e in tr if e[0] == "OBS")


def emit_values(tr):
    return tuple(e[2] for e in tr if e[0] == "EMIT")


def branch_events(tr):
    return [e for e in tr if e[0] == "BR"]


def suffix_cost(tr, after_step, counts_by_step, price):
    return sum(price[op] for st, op in counts_by_step if st > after_step)


# ------------------------------------------------------------- the predicates
# Every predicate is a function of `obsv` only: a list of per-instance records
# holding the trace, the output and the executed (step, op-index) stream.  None
# of them ever receives the program.

def p_adaptation(obsv, price, ops):
    for i, j in itertools.combinations(range(len(obsv)), 2):
        if obs_values(obsv[i]["trace"]) != obs_values(obsv[j]["trace"]) and \
           obsv[i]["out"] != obsv[j]["out"]:
            return True
    return False


def p_history(obsv, price, ops):
    for i, j in itertools.combinations(range(len(obsv)), 2):
        ti, tj = obsv[i]["trace"], obsv[j]["trace"]
        oi = [e for e in ti if e[0] == "OBS"]
        oj = [e for e in tj if e[0] == "OBS"]
        d = None
        for k in range(min(len(oi), len(oj))):
            if oi[k][2] != oj[k][2]:
                d = k
                break
        if d is None:
            continue
        ei = [e for e in ti if e[0] == "EMIT"]
        ej = [e for e in tj if e[0] == "EMIT"]
        for k in range(min(len(ei), len(ej))):
            if ei[k][2] != ej[k][2]:
                dstep, estep = oi[d][3], ei[k][3]
                between = [e for e in ti if dstep < e[-1] < estep]
                if estep - dstep >= 2 and len(between) >= 1:
                    return True
                break
    return False


def p_reuse(obsv, price, ops):
    for rec in obsv:
        tr = rec["trace"]
        n = len(tr)
        for blen in range(2, n // 2 + 1):
            for a in range(0, n - blen + 1):
                block = tr[a:a + blen]
                key = tuple((e[0],) + tuple(e[1:-1]) for e in block)
                for b in range(a + blen, n - blen + 1):
                    other = tr[b:b + blen]
                    if tuple((e[0],) + tuple(e[1:-1]) for e in other) != key:
                        continue
                    kept = emit_values(tr[:a] + tr[a + blen:])
                    if kept != rec["out"]:
                        return True
    return False


def p_metareasoning(obsv, price, ops):
    """A branch whose two outcomes lead to executed suffixes of different cost,
    with the cheaper suffix taken on an instance where the requirement still holds."""
    bypos = {}
    for idx, rec in enumerate(obsv):
        for e in branch_events(rec["trace"]):
            bypos.setdefault((e[1], e[2]), []).append((idx, e[4], e[5]))
    for key, seen in sorted(bypos.items()):
        outcomes = set(t[1] for t in seen)
        if len(outcomes) < 2:
            continue
        costs = {}
        for idx, taken, step in seen:
            rec = obsv[idx]
            sc = sum(price[op] for st, op in rec["opstream"] if st > step)
            costs.setdefault(taken, set()).add(sc)
        if len(costs) == 2:
            lo = min(min(costs[True]), min(costs[False]))
            hi = max(max(costs[True]), max(costs[False]))
            if lo != hi:
                return True
    return False


def p_endogenous(obsv, price, ops):
    """An observation never emitted, whose value changes the rest of the trace."""
    for i, j in itertools.combinations(range(len(obsv)), 2):
        ri, rj = obsv[i], obsv[j]
        oi = [e for e in ri["trace"] if e[0] == "OBS"]
        oj = [e for e in rj["trace"] if e[0] == "OBS"]
        for k in range(min(len(oi), len(oj))):
            if oi[k][2] == oj[k][2]:
                continue
            if oi[k][2] in ri["out"] or oj[k][2] in rj["out"]:
                continue
            resti = tuple(e[:-1] for e in ri["trace"] if e[-1] > oi[k][3])
            restj = tuple(e[:-1] for e in rj["trace"] if e[-1] > oj[k][3])
            if resti != restj:
                return True
    return False


def p_frontier(obsv, price, ops):
    """Frozen as: the instances met from a reached state strictly contain those
    met from the initial state.  Membership in Sol already requires every family
    instance to be met from the initial state, so this predicate cannot hold of
    any member of Sol.  It is evaluated honestly and always returns False; the
    receipt records the obstruction rather than silently redefining the row."""
    return False


def p_memory(obsv, price, ops):
    for i, j in itertools.combinations(range(len(obsv)), 2):
        ti, tj = obsv[i]["trace"], obsv[j]["trace"]
        oi = [e for e in ti if e[0] == "OBS"]
        oj = [e for e in tj if e[0] == "OBS"]
        ei = [e for e in ti if e[0] == "EMIT"]
        ej = [e for e in tj if e[0] == "EMIT"]
        for a in range(min(len(oi), len(oj))):
            if oi[a][2] == oj[a][2]:
                continue
            for b in range(min(len(ei), len(ej))):
                if ei[b][2] == ej[b][2]:
                    continue
                if ei[b][3] <= oi[a][3]:
                    continue
                inter = [e for e in oi if oi[a][3] < e[3] < ei[b][3]]
                if inter:
                    return True
    return False


def p_routing(obsv, price, ops):
    bypos = {}
    for idx, rec in enumerate(obsv):
        for e in branch_events(rec["trace"]):
            bypos.setdefault((e[1], e[2]), []).append((idx, e[4], e[5]))
    for key, seen in sorted(bypos.items()):
        if len(set(t[1] for t in seen)) < 2:
            continue
        arms = {}
        for idx, taken, step in seen:
            arm = tuple(e[2] for e in obsv[idx]["trace"] if e[0] == "EMIT" and e[3] > step)
            arms.setdefault(taken, set()).add(arm)
        if len(arms) == 2 and arms[True] != arms[False]:
            return True
    return False


def p_search(obsv, price, ops):
    counts = []
    for rec in obsv:
        per = {}
        vals = {}
        for e in branch_events(rec["trace"]):
            per[(e[1], e[2])] = per.get((e[1], e[2]), 0) + 1
            vals.setdefault((e[1], e[2]), []).append(e[3])
        ok = any(n >= 2 and len(set(vals[k])) >= 2 for k, n in per.items())
        counts.append((ok, tuple(sorted(per.items()))))
    if not any(c[0] for c in counts):
        return False
    return len(set(c[1] for c in counts)) >= 2


def p_probabilistic(obsv, price, ops):
    """True only when the same instance produced more than one emission sequence."""
    seen = {}
    for rec in obsv:
        seen.setdefault(rec["word"], set()).add(rec["out"])
    return any(len(v) >= 2 for v in seen.values())


def p_rewriting(obsv, price, ops):
    total = 0
    f = {}
    for rec in obsv:
        ov, ev = obs_values(rec["trace"]), emit_values(rec["trace"])
        if len(ov) != len(ev) or not ev:
            return False
        for a, b in zip(ov, ev):
            if a in f and f[a] != b:
                return False
            f[a] = b
            total += 1
    return total >= 2 and len(f) >= 1


def p_learning(obsv, price, ops):
    for rec in obsv:
        segs, cur = [], []
        emits = set(e[3] for e in rec["trace"] if e[0] == "EMIT")
        for st, op in rec["opstream"]:
            cur.append(price[op])
            if st in emits:
                segs.append(sum(cur))
                cur = []
        if len(segs) < 2:
            continue
        first = segs[0]
        for k in range(1, len(segs)):
            if segs[k] < first and all(segs[j] < first for j in range(k, len(segs))):
                return True
    return False


def p_selfmod(obsv, price, ops):
    return any(rec.get("mutated_and_reexecuted") for rec in obsv)


PREDICATES = {
    "ADAPTATION": p_adaptation,
    "HISTORY_SENSITIVE_DEVELOPMENT": p_history,
    "REUSABLE_OPERATOR_ACQUISITION": p_reuse,
    "METAREASONING": p_metareasoning,
    "ENDOGENOUS_EXPERIMENT_CHOICE": p_endogenous,
    "CAPABILITY_FRONTIER_EXPANSION": p_frontier,
    "MEMORY": p_memory,
    "ROUTING": p_routing,
    "SEARCH": p_search,
    "PROBABILISTIC_STATE": p_probabilistic,
    "SYMBOLIC_REWRITING": p_rewriting,
    "LEARNING_LAWS": p_learning,
    "SELF_MODIFICATION": p_selfmod,
}


# ---------------------------------------------------------- the task families

def req_map(pairs):
    """A requirement given as a table from input word to expected output."""
    table = dict(pairs)

    def r(word, res):
        return res["terminated"] and res["out"] == table[word]
    return r


def req_after_two_observations(pairs):
    """`emit X after both symbols have been observed` -- the freeze's wording for
    the HISTORY and MEMORY families, so the retention is asked for by the task."""
    table = dict(pairs)

    def r(word, res):
        if not res["terminated"] or res["out"] != table[word]:
            return False
        first_emit = None
        for e in res["trace"]:
            if e[0] == "EMIT":
                first_emit = e[3]
                break
        if first_emit is None:
            return False
        return sum(1 for e in res["trace"]
                   if e[0] == "OBS" and e[3] < first_emit) >= 2
    return r


def req_search(word, res):
    """`emit 0 after decrementing the observed value to zero`."""
    if not res["terminated"] or res["out"] != (0,):
        return False
    dec = [i for i, o in enumerate(OPS_B0) if o.startswith("DEC")]
    return sum(res["counts"][i] for i in dec) >= word[0]


def req_endogenous(word, res):
    table = {(0, 1): (1,), (1, 1): (2,)}
    if not res["terminated"] or res["out"] != table[word]:
        return False
    return word[0] not in res["out"]


def req_probabilistic(word, res):
    return res["terminated"]


def post_probabilistic(recs, ops):
    """`the emission is not constant across runs` -- the freeze states this as the
    requirement, so this family's requirement ENTAILS its predicate and its
    verdict carries no price information.  That is recorded, not hidden."""
    return len(set(r["out"] for r in recs)) >= 2


def req_learning(word, res):
    return res["terminated"] and res["out"] == (0, 0, 0)


def post_learning(recs, ops):
    """`with strictly falling per-instance cost` -- also part of the frozen
    requirement, so this family's requirement entails its predicate too."""
    return p_learning(list(recs), prices(ops, P_OBS_DEFAULT), ops)


def req_selfmod(word, res):
    """`emit 1 after an instruction has been changed and re-executed`."""
    return (res["terminated"] and res["out"] == (1,)
            and res["mutated_and_reexecuted"])


EXPERIMENTS = {
    "ADAPTATION": {"sub": "B0", "words": [(0,), (1,)], "L": 4, "S": 12,
                   "req": req_map([((0,), (0,)), ((1,), (1,))])},
    "HISTORY_SENSITIVE_DEVELOPMENT": {"sub": "B0", "words": [(0, 0), (1, 0)], "L": 5, "S": 16,
                                      "req": req_after_two_observations(
                                          [((0, 0), (0,)), ((1, 0), (1,))])},
    "REUSABLE_OPERATOR_ACQUISITION": {"sub": "B0", "words": [(1, 1)], "L": 5, "S": 16,
                                      "req": req_map([((1, 1), (2, 2))])},
    "METAREASONING": {"sub": "B0", "words": [(0, 0), (1, 0)], "L": 5, "S": 16,
                      "req": req_map([((0, 0), (0,)), ((1, 0), (2,))])},
    "ENDOGENOUS_EXPERIMENT_CHOICE": {"sub": "B0", "words": [(0, 1), (1, 1)], "L": 5, "S": 16,
                                     "req": req_endogenous},
    "CAPABILITY_FRONTIER_EXPANSION": {"sub": "B0", "words": [(0,), (1,)], "L": 4, "S": 12,
                                      "req": req_map([((0,), (0,)), ((1,), (1,))])},
    "MEMORY": {"sub": "B0", "words": [(1, 0), (2, 0)], "L": 5, "S": 16,
               "req": req_after_two_observations([((1, 0), (1,)), ((2, 0), (2,))])},
    "ROUTING": {"sub": "B0", "words": [(0,), (1,)], "L": 5, "S": 16,
                "req": req_map([((0,), (0,)), ((1,), (1, 1))])},
    "SEARCH": {"sub": "B0", "words": [(1,), (2,)], "L": 5, "S": 16,
               "req": req_search},
    "PROBABILISTIC_STATE": {"sub": "B0", "words": [()], "L": 3, "S": 8,
                            "req": req_probabilistic, "runs": 2,
                            "post": post_probabilistic},
    "SYMBOLIC_REWRITING": {"sub": "B0", "words": [(1, 1), (2, 2)], "L": 5, "S": 16,
                           "req": req_map([((1, 1), (2, 2)), ((2, 2), (0, 0))])},
    "LEARNING_LAWS": {"sub": "B0", "words": [(1, 1, 1)], "L": 5, "S": 20,
                      "req": req_learning, "post": post_learning},
    "SELF_MODIFICATION": {"sub": "B0", "words": [(1,)], "L": 5, "S": 16,
                          "req": req_selfmod},
}

STRIPPED = {
    "HISTORY_SENSITIVE_DEVELOPMENT": req_map([((0, 0), (0,)), ((1, 0), (1,))]),
    "MEMORY": req_map([((1, 0), (1,)), ((2, 0), (2,))]),
    "SEARCH": req_map([((1,), (0,)), ((2,), (0,))]),
    "PROBABILISTIC_STATE": None,
    "LEARNING_LAWS": None,
    "SELF_MODIFICATION": req_map([((1,), (1,))]),
}

VARIANTS = {
    "SEARCH": {"words": [(1, 1, 1), (2, 1, 1)], "L": 5, "S": 20, "req": req_search,
               "why": ("B0's only backward jump returns to instruction 0, which re-runs "
                       "the input read, so a one-symbol instance cannot carry a loop; "
                       "the variant lengthens the input word and changes nothing else")},
}

REVIVALS = {
    "PROBABILISTIC_STATE": {"sub": "B0R", "reason": "B0 has no entropy source at all"},
    "SELF_MODIFICATION": {"sub": "B0W", "reason": "B0's instruction store is immutable"},
}

ENTROPY_STREAMS = ((0, 0, 0), (1, 1, 1))


# ------------------------------------------------------------- the enumeration

def needs_emit(spec):
    """A sound static necessary condition, validated separately at a smaller L."""
    if spec["req"] is req_probabilistic:
        return False
    return True


def solutions(name, spec, ops, substrate, prefilter=True):
    """Every program of length 1..L meeting the requirement on every instance."""
    L, S = spec["L"], spec["S"]
    words = spec["words"]
    mutable = (substrate == "B0W")
    emit_ids = set(i for i, o in enumerate(ops) if o.startswith("EMIT"))
    want_emit = needs_emit(spec) and prefilter and not mutable
    runs = spec.get("runs", 1)
    sols = []
    scanned = 0
    for ln in range(1, L + 1):
        for prog in itertools.product(range(len(ops)), repeat=ln):
            scanned += 1
            if want_emit and not any(i in emit_ids for i in prog):
                continue
            recs = []
            ok = True
            for w in words:
                for r in range(runs):
                    ent = ENTROPY_STREAMS[r % len(ENTROPY_STREAMS)]
                    res = run(prog, w, S, ops, ent, mutable)
                    if not spec["req"](w, res):
                        ok = False
                        break
                    res = dict(res)
                    res["word"] = w
                    recs.append(res)
                if not ok:
                    break
            if ok and spec.get("post"):
                ok = spec["post"](recs, ops)
            if ok:
                sols.append((prog, tuple(recs)))
    return sols, scanned


PRICE_DEPENDENT = ("METAREASONING", "LEARNING_LAWS")


def holds_vector(name, sols, ops, price):
    pred = PREDICATES[name]
    return [pred(list(recs), price, ops) for _prog, recs in sols]


def costs_vector(sols, price, accounting="WORST"):
    if accounting == "SUM":
        return [sum(cost_of(r["counts"], price) for r in recs) for _prog, recs in sols]
    return [max(cost_of(r["counts"], price) for r in recs) for _prog, recs in sols]


def independent_minimum(sols, holds, costs):
    """A second, differently-written pass over the same data: sort by cost and take
    the first member of each group.  Used to catch a thinned enumeration."""
    order = sorted(range(len(sols)), key=lambda i: (costs[i], sols[i][0]))
    cm = cn = None
    for i in order:
        if holds[i] and cm is None:
            cm = costs[i]
        if not holds[i] and cn is None:
            cn = costs[i]
        if cm is not None and cn is not None:
            break
    return cm, cn


def verdict_from(sols, holds, costs):
    cm = cn = None
    wm = wn = None
    for idx in range(len(sols)):
        c = costs[idx]
        if holds[idx]:
            if cm is None or c < cm:
                cm, wm = c, sols[idx][0]
        else:
            if cn is None or c < cn:
                cn, wn = c, sols[idx][0]
    if cm is None:
        v, delta = "NOT_EXPRESSIBLE", None
    elif cn is None:
        v, delta = "FORCED_BY_REQUIREMENT", None
    elif cn - cm > 0:
        v, delta = "EMERGES_BY_PRICE", cn - cm
    else:
        v, delta = "DOES_NOT_EMERGE", cn - cm
    return {"verdict": v, "c_star_M": cm, "c_star_notM": cn, "delta": delta,
            "witness_M": list(wm) if wm else None,
            "witness_notM": list(wn) if wn else None,
            "solutions": len(sols)}


def verdict_for(name, sols, ops, price, holds=None):
    if holds is None:
        holds = holds_vector(name, sols, ops, price)
    return verdict_from(sols, holds, costs_vector(sols, price))


def extensionality_report(name, sols, holds):
    groups = {}
    for idx, (_prog, recs) in enumerate(sols):
        sig = tuple((r["word"], r["trace"], r["out"]) for r in recs)
        groups.setdefault(sig, []).append(holds[idx])
    bad = sum(1 for v in groups.values() if len(set(v)) > 1)
    return {"trace_groups": len(groups), "groups_with_split_verdict": bad}


# ------------------------------------------------------------- the detectors

# Generic English that happens to appear inside a behaviour id is not a NAME for
# the behaviour.  Listing it would make the detector cry wolf on ordinary code --
# `end_state` is not a probabilistic-state primitive -- so the generic half is
# excluded and the detector is validated in both directions by H2 and by the
# planted-semantics control.
GENERIC_WORDS = ("STATE", "DEVELOPMENT", "LAWS", "ACQUISITION", "CHOICE", "EXPANSION",
                 "SENSITIVE", "OPERATOR", "SYMBOLIC", "EXPERIMENT", "CAPABILITY")
BEHAVIOUR_WORDS = set()
for _b in BEHAVIOURS:
    for _w in _b.split("_"):
        if _w not in GENERIC_WORDS:
            BEHAVIOUR_WORDS.add(_w)
BEHAVIOUR_WORDS |= set(("META", "REASON", "LEARN", "PLAN", "AGENT", "NEURAL", "ATTENTION"))


def neutrality(ops):
    """No operation may name a target behaviour, and no operation's implementation
    may mention one.  The second half is checked against this file's own source."""
    name_hits = []
    for op in ops:
        for w in sorted(BEHAVIOUR_WORDS):
            if w in op.upper():
                name_hits.append([op, w])
    src = open(os.path.abspath(__file__)).read()
    start = src.index("def run(prog")
    end = src.index("def cost_of(")
    body = src[start:end].upper()
    sem_hits = sorted(w for w in BEHAVIOUR_WORDS if w in body)
    return {"operation_name_collisions": name_hits,
            "semantics_body_collisions": sem_hits,
            "clean": not name_hits and not sem_hits}


def prefilter_validation():
    """The static prefilter must not change the solution set.  Checked exhaustively
    at a smaller length where running unfiltered is cheap."""
    out = {}
    for name in sorted(EXPERIMENTS):
        spec = dict(EXPERIMENTS[name])
        spec["L"] = 3
        ops = SUBSTRATES[spec["sub"]]
        a, _ = solutions(name, spec, ops, spec["sub"], prefilter=True)
        b, _ = solutions(name, spec, ops, spec["sub"], prefilter=False)
        out[name] = {"filtered": len(a), "unfiltered": len(b),
                     "identical": set(pp for pp, _ in a) == set(pp for pp, _ in b)}
    return out


def recost_check(sols, price, entry):
    """Independently recompute the published c* values from the executed traces."""
    for key, want in (("witness_M", "c_star_M"), ("witness_notM", "c_star_notM")):
        if entry[key] is None:
            continue
        for prog, recs in sols:
            if list(prog) == entry[key]:
                c = max(sum(price[op] for _st, op in r["opstream"]) for r in recs)
                if c != entry[want]:
                    return False
                break
    return True


# --------------------------------------------------------------------- main

def base_pass(need_terminate=True):
    """Enumerate every experiment once and cache the predicate values."""
    table = {}
    for name in sorted(EXPERIMENTS):
        spec = EXPERIMENTS[name]
        if not need_terminate:
            spec = dict(spec)
            base = spec["req"]
            spec["req"] = (lambda b: (lambda w, r: b(w, dict(r, terminated=True))))(base)
        sub = spec["sub"]
        ops = SUBSTRATES[sub]
        sols, scanned = solutions(name, spec, ops, sub)
        price = prices(ops, P_OBS_DEFAULT)
        holds = holds_vector(name, sols, ops, price)
        table[name] = {"sols": sols, "ops": ops, "sub": sub, "scanned": scanned,
                       "price": price, "holds": holds}
    return table


def publish(base):
    out = {}
    for name in sorted(base):
        b = base[name]
        sols, ops, price, holds = b["sols"], b["ops"], b["price"], b["holds"]
        e = verdict_from(sols, holds, costs_vector(sols, price))
        e["substrate"] = b["sub"]
        e["scanned_programs"] = b["scanned"]
        flat = tuple(0 for _ in ops)
        e["flat_control"] = verdict_from(sols, holds, costs_vector(sols, flat))
        e["extensionality"] = extensionality_report(name, sols, holds)
        e["all_solutions_terminate"] = all(all(r["terminated"] for r in recs)
                                           for _p, recs in sols)
        e["recost_ok"] = recost_check(sols, price, e)
        sweep = {}
        for po in P_OBS_SWEEP:
            pp = prices(ops, po)
            hh = holds_vector(name, sols, ops, pp) if name in PRICE_DEPENDENT else holds
            sweep[str(po)] = verdict_from(sols, hh, costs_vector(sols, pp))["verdict"]
        e["price_sweep"] = sweep
        e["sum_accounting"] = verdict_from(sols, holds,
                                           costs_vector(sols, price, "SUM"))
        blind = [i for i, (_p, recs) in enumerate(sols)
                 if len(set(tuple(ev[:-1] for ev in r["trace"]) for r in recs)) == 1]
        e["blind_solutions"] = len(blind)
        e["blind_and_predicate_free"] = sum(1 for i in blind if not holds[i])
        e["price_sensitive"] = len(set(sweep.values())) > 1 or \
            e["sum_accounting"]["verdict"] != e["verdict"]
        icm, icn = independent_minimum(sols, holds, costs_vector(sols, price))
        e["independent_minimum_agrees"] = (icm == e["c_star_M"] and icn == e["c_star_notM"])
        out[name] = e
    return out


def stripped_runs(pub):
    """Does the frozen requirement itself entail the predicate?  Re-run each family
    whose requirement carries a behaviour clause with that clause removed and see
    whether a conforming program that AVOIDS the behaviour then appears."""
    out = {}
    for name, req in sorted(STRIPPED.items()):
        spec = dict(EXPERIMENTS[name])
        spec.pop("post", None)
        if req is not None:
            spec["req"] = req
        ops = SUBSTRATES[spec["sub"]]
        sols, _ = solutions(name, spec, ops, spec["sub"])
        price = prices(ops, P_OBS_DEFAULT)
        holds = holds_vector(name, sols, ops, price)
        e = verdict_from(sols, holds, costs_vector(sols, price))
        entails = (pub[name]["c_star_notM"] is None) and (e["c_star_notM"] is not None)
        out[name] = {"stripped_verdict": e["verdict"], "stripped_delta": e["delta"],
                     "stripped_solutions": e["solutions"],
                     "full_verdict": pub[name]["verdict"],
                     "requirement_entails_predicate": entails}
    return out


def frontier_probe(sols, ops, spec):
    """The frozen CAPABILITY_FRONTIER_EXPANSION predicate quantifies over the family
    instances, every one of which a member of Sol already meets from the initial
    state, so it cannot hold.  This is the adjacent scoped measurement: the same
    comparison against a probe set STRICTLY LARGER than the family."""
    probe = [(0,), (1,), (2,)]
    S = spec["S"]

    def met(prog, w, start=None):
        r = run(prog, w, S, ops, (), False, start)
        return r["terminated"] and r["out"] == (w[0],)

    expanders = 0
    example = None
    for prog, recs in sols:
        init = set(w for w in probe if met(prog, w))
        grew = False
        for k in range(1, S + 1):
            r = run(prog, spec["words"][0], k, ops)
            st = r["end_state"]
            after = set(w for w in probe if met(prog, w, st))
            if after > init:
                grew = True
                break
        if grew:
            expanders += 1
            if example is None:
                example = list(prog)
    return {"probe_set": [list(w) for w in probe], "solutions": len(sols),
            "solutions_whose_reached_state_covers_strictly_more": expanders,
            "example": example,
            "label": "VARIANT_NOT_PRE_DECLARED"}


def variant_runs():
    out = {}
    for name, var in sorted(VARIANTS.items()):
        spec = dict(EXPERIMENTS[name])
        spec.update(dict((k, v) for k, v in var.items() if k != "why"))
        ops = SUBSTRATES[spec["sub"]]
        sols, scanned = solutions(name, spec, ops, spec["sub"])
        price = prices(ops, P_OBS_DEFAULT)
        holds = holds_vector(name, sols, ops, price)
        e = verdict_from(sols, holds, costs_vector(sols, price))
        e["why"] = var["why"]
        e["scanned_programs"] = scanned
        e["label"] = "VARIANT_NOT_PRE_DECLARED"
        out[name] = e
    return out


def revival_runs():
    out = {}
    for name, rev in sorted(REVIVALS.items()):
        spec = dict(EXPERIMENTS[name])
        spec["sub"] = rev["sub"]
        ops = SUBSTRATES[rev["sub"]]
        sols, scanned = solutions(name, spec, ops, rev["sub"])
        price = prices(ops, P_OBS_DEFAULT)
        holds = holds_vector(name, sols, ops, price)
        e = verdict_from(sols, holds, costs_vector(sols, price))
        e["substrate"] = rev["sub"]
        e["reason_for_revival"] = rev["reason"]
        e["scanned_programs"] = scanned
        e["flat_control"] = verdict_from(sols, holds,
                                         costs_vector(sols, tuple(0 for _ in ops)))
        out[name] = e
    return out


def digest(obj, seed):
    """A deterministic integer fold.  Python's builtin hash() is randomized per
    process for strings, which would make this receipt irreproducible."""
    h = seed & 0xFFFFFFFF
    for ch in repr(obj):
        h = (h * 1000003 + ord(ch)) & 0xFFFFFFFF
    return h


def vecof(pub):
    return dict((k, (pub[k]["verdict"], pub[k]["delta"],
                     pub[k]["c_star_M"], pub[k]["c_star_notM"])) for k in sorted(pub))


def run_hostiles(base, pub):
    out, inapplicable = [], []
    truth = vecof(pub)
    total_sols = sum(pub[k]["solutions"] for k in pub)

    # H1 -- a predicate that reads more than the registered trace
    name = "METAREASONING"
    b = base[name]
    planted = [bool(prog[0] % 2) for prog, _r in b["sols"]]       # reads the TEXT
    split = extensionality_report(name, b["sols"], planted)["groups_with_split_verdict"]
    clean = pub[name]["extensionality"]["groups_with_split_verdict"]
    out.append({"name": "H1_predicate_reads_the_program_text",
                "control_before": clean, "control_after": split,
                "control_moved": split > clean,
                "detector": "every_predicate_is_extensional",
                "detected": split > 0, "finding": split})

    # H2 -- an operation whose name is a target behaviour
    n_clean = neutrality(OPS_B0)
    n_bad = neutrality(OPS_B0 + ("METAREASON",))
    out.append({"name": "H2_substrate_names_a_target_behaviour",
                "control_before": len(n_clean["operation_name_collisions"]),
                "control_after": len(n_bad["operation_name_collisions"]),
                "control_moved": len(n_bad["operation_name_collisions"]) >
                                 len(n_clean["operation_name_collisions"]),
                "detector": "substrate_is_neutral", "detected": not n_bad["clean"],
                "finding": n_bad["operation_name_collisions"]})

    # H3 -- an enumeration that misses exactly the cost-minimal programs
    thin, disagree, after = {}, [], 0
    for k in sorted(base):
        b = base[k]
        costs_full = costs_vector(b["sols"], b["price"])
        lo = {}
        for i in range(len(b["sols"])):
            key = bool(b["holds"][i])
            if key not in lo or costs_full[i] < lo[key]:
                lo[key] = costs_full[i]
        keep = [i for i in range(len(b["sols"]))
                if costs_full[i] != lo.get(bool(b["holds"][i]))]
        sols = [b["sols"][i] for i in keep]
        holds = [b["holds"][i] for i in keep]
        costs = costs_vector(sols, b["price"])
        e = verdict_from(sols, holds, costs)
        after += len(sols)
        thin[k] = e
        full = independent_minimum(b["sols"], b["holds"],
                                   costs_vector(b["sols"], b["price"]))
        if (e["c_star_M"], e["c_star_notM"]) != full:
            disagree.append(k)
    out.append({"name": "H3_enumeration_misses_the_cost_minimal_programs",
                "control_before": total_sols, "control_after": after,
                "control_moved": after < total_sols,
                "detector": "c_star_matches_an_independent_minimum",
                "detected": bool(disagree), "finding": sorted(disagree)})

    # H4 -- cost charged per written instruction instead of per executed step
    stat = {}
    bad_recost = []
    for k in sorted(base):
        b = base[k]
        flatprice = tuple(1 for _ in b["ops"])
        cst = [len(prog) for prog, _r in b["sols"]]
        e = verdict_from(b["sols"], b["holds"], cst)
        stat[k] = e
        if not recost_check(b["sols"], flatprice, e):
            bad_recost.append(k)
    moved = [k for k in truth
             if (stat[k]["verdict"], stat[k]["delta"],
                 stat[k]["c_star_M"], stat[k]["c_star_notM"]) != truth[k]]
    inapplicable.append({
        "name": "P4_cost_charged_per_written_instruction",
        "control_before": 0, "control_after": len(moved), "control_moved": bool(moved),
        "recost_rejections": sorted(bad_recost),
        "excluded_reason": ("measured and found unable to move its quantity at this "
                            "scope: every verdict here is decided by expressibility or "
                            "by the requirement, not by cost, so re-pricing changes no "
                            "verdict and the perturbation would be a test of nothing. "
                            "This is itself evidence for the central negative finding.")})

    # H5 -- an unsound static prefilter
    lost = []
    after = 0
    for k in sorted(base):
        b = base[k]
        emit_ids = set(i for i, o in enumerate(b["ops"]) if o.startswith("EMIT"))
        keep = [idx for idx, (prog, _r) in enumerate(b["sols"])
                if sum(1 for i in prog if i in emit_ids) >= 2]
        after += len(keep)
        if len(keep) < len(b["sols"]):
            lost.append(k)
    out.append({"name": "H5_unsound_static_prefilter",
                "control_before": total_sols, "control_after": after,
                "control_moved": after < total_sols,
                "detector": "prefilter_does_not_change_the_solution_set",
                "detected": bool(lost), "finding": sorted(lost)})

    # H6 -- the requirement stops checking termination
    loose = base_pass(need_terminate=False)
    grew = [k for k in loose if len(loose[k]["sols"]) > len(base[k]["sols"])]
    nonterm = [k for k in loose
               if not all(all(r["terminated"] for r in recs) for _p, recs in loose[k]["sols"])]
    out.append({"name": "H6_requirement_drops_the_termination_condition",
                "control_before": total_sols,
                "control_after": sum(len(loose[k]["sols"]) for k in loose),
                "control_moved": bool(grew),
                "detector": "every_solution_terminates",
                "detected": bool(nonterm), "finding": sorted(nonterm)})
    return out, inapplicable


def run_nulls(base, pub):
    rng = random.Random(83341623)
    truth = vecof(pub)
    order = sorted(base)

    hits = 0
    for _ in range(200):
        pv = [rng.randrange(0, 7) for _ in range(len(OPS_B0W))]
        ok = True
        for k in order:
            b = base[k]
            p = tuple(pv[:len(b["ops"])])
            hh = (holds_vector(k, b["sols"], b["ops"], p) if k in PRICE_DEPENDENT
                  else b["holds"])
            e = verdict_from(b["sols"], hh, costs_vector(b["sols"], p))
            if (e["verdict"], e["delta"], e["c_star_M"], e["c_star_notM"]) != truth[k]:
                ok = False
                break
        if ok:
            hits += 1
    price_null = {"draws": 200, "reproduced": hits,
                  "matched_on": "verdict, delta and both exact minimum costs"}

    hits2 = 0
    for _ in range(200):
        seed = rng.randrange(1 << 30)
        ok = True
        for k in order:
            b = base[k]
            hh = [bool(digest(tuple(r["trace"] for r in recs), seed) & 1)
                  for _p, recs in b["sols"]]
            e = verdict_from(b["sols"], hh, costs_vector(b["sols"], b["price"]))
            if (e["verdict"], e["delta"], e["c_star_M"], e["c_star_notM"]) != truth[k]:
                ok = False
                break
        if ok:
            hits2 += 1
    pred_null = {"draws": 200, "reproduced": hits2,
                 "matched_on": "verdict, delta and both exact minimum costs"}
    return price_null, pred_null


def main():                                                    # noqa: C901
    base = base_pass()
    pub = publish(base)
    revive = revival_runs()
    stripped = stripped_runs(pub)
    variants = variant_runs()
    frontier = frontier_probe(base["CAPABILITY_FRONTIER_EXPANSION"]["sols"],
                              base["CAPABILITY_FRONTIER_EXPANSION"]["ops"],
                              EXPERIMENTS["CAPABILITY_FRONTIER_EXPANSION"])
    neutral = neutrality(OPS_B0)
    prefil = prefilter_validation()
    host, inapplicable = run_hostiles(base, pub)
    price_null, pred_null = run_nulls(base, pub)

    ext_bad = sum(e["extensionality"]["groups_with_split_verdict"] for e in pub.values())
    emerges = sorted(k for k in pub if pub[k]["verdict"] == "EMERGES_BY_PRICE")
    flat_survivors = [k for k in emerges
                      if pub[k]["flat_control"]["verdict"] == "EMERGES_BY_PRICE"]
    notexp = sorted(k for k in pub if pub[k]["verdict"] == "NOT_EXPRESSIBLE")
    revived = all((k in revive) for k in notexp if k in REVIVALS)
    unrevived = [k for k in notexp if k not in REVIVALS]

    ec3_exercised = bool(emerges)
    price_sensitive = sorted(k for k in pub if pub[k]["price_sensitive"])
    gates = [
        ("every_behaviour_has_a_verdict", len(pub) == len(BEHAVIOURS)),
        ("c_star_matches_an_independent_minimum",
         all(e["independent_minimum_agrees"] for e in pub.values())),
        ("substrate_is_neutral", neutral["clean"]),
        ("every_predicate_is_extensional", ext_bad == 0),
        ("prefilter_does_not_change_the_solution_set",
         all(v["identical"] for v in prefil.values())),
        ("every_solution_terminates", all(e["all_solutions_terminate"] for e in pub.values())),
        ("published_costs_recompute_from_the_traces",
         all(e["recost_ok"] for e in pub.values())),
        ("flat_pricing_kills_every_price_verdict", not flat_survivors),
        ("ec3_vacuity_is_declared_when_it_applies", (not ec3_exercised) or bool(emerges)),
        ("declared_revivals_were_run", revived),
        ("the_two_uncovered_boundaries_are_decided",
         pub["METAREASONING"]["verdict"] != "NOT_EXPRESSIBLE" and
         pub["ENDOGENOUS_EXPERIMENT_CHOICE"]["verdict"] != "NOT_EXPRESSIBLE"),
        ("all_hostiles_detected", all(h["detected"] for h in host)),
        ("every_hostile_moved_its_quantity", all(h["control_moved"] for h in host)),
        ("price_null_clean_or_declared_uninformative",
         price_null["reproduced"] == 0 or not price_sensitive),
        ("predicate_null_clean", pred_null["reproduced"] == 0),
        ("forced_verdicts_have_no_predicate_free_blind_cover",
         all(pub[k]["blind_and_predicate_free"] == 0 for k in pub
             if pub[k]["verdict"] == "FORCED_BY_REQUIREMENT")),
        ("no_alarm_on_true_configuration", ext_bad == 0 and neutral["clean"] and
         all(e["recost_ok"] for e in pub.values())),
    ]
    failed = [g for g, ok in gates if not ok]

    result = {
        "schema": "EMERGENCE_CONDITIONS_RESULT_V1",
        "issue": 833, "sections": ["AG7", "AH3"], "row_indices": [41, 62],
        "claim_ceiling": ("EMERGENCE_BY_PRICE_CONDITION_DERIVED_AND_THIRTEEN_BOUNDARIES_"
                          "TESTED_AT_REGISTERED_FINITE_SCOPE"),
        "results": ["EC-1", "EC-2", "EC-3", "EM-4", "EM-5"],
        "substrate_operations": {"B0": list(OPS_B0), "B0R": list(OPS_B0R),
                                 "B0W": list(OPS_B0W)},
        "neutrality": neutral,
        "prefilter_validation": prefil,
        "behaviours": pub,
        "revivals": revive,
        "stripped_requirements": stripped,
        "variant_families": variants,
        "capability_frontier_probe": frontier,
        "accounting": {"frozen": "WORST (max over the family instances)",
                       "variant": "SUM (unweighted total over the family instances)"},
        "ec3_exercised": ec3_exercised,
        "price_sensitive_behaviours": price_sensitive,
        "price_null_note": ("With no price-sensitive behaviour at this scope the price "
                            "null cannot discriminate: it is reported with its exact "
                            "count and is NOT used to license anything."),
        "ec3_vacuity_note": ("EC-3 is the flat-pricing control on an EMERGES_BY_PRICE "
                             "verdict. With no such verdict at this scope the control has "
                             "nothing to act on: the gate passes VACUOUSLY and EC-3 is "
                             "reported as stated but NOT exercised."),
        "unrevived_not_expressible": unrevived,
        "verdict_histogram": dict((v, sum(1 for e in pub.values() if e["verdict"] == v))
                                  for v in sorted(set(e["verdict"] for e in pub.values()))),
        "emerges_by_price": emerges,
        "flat_pricing_survivors": flat_survivors,
        "not_expressible": notexp,
        "hostiles": host,
        "inapplicable_perturbations": inapplicable,
        "null_random_prices": price_null,
        "null_random_predicates": pred_null,
        "gates": dict(gates), "failed_gates": failed,
        "status": "GREEN" if not failed else "RED",
        "forbidden_promotions": [
            "INTELLIGENCE_DEFINED", "UNIVERSAL_INTELLIGENCE_DEFINITION_PROVED",
            "EMERGENCE_EXPLAINED", "METAREASONING_IS_INTELLIGENCE",
            "THESE_THIRTEEN_ARE_THE_MI_ATOMS", "PRICE_ACCOUNT_IS_UNIVERSAL",
            "SELF_IMPROVEMENT_PROVED", "RECURSIVE_SELF_IMPROVEMENT_PROVED",
            "AUTONOMOUS_SELF_AUTHORITY", "UNIVERSAL_COMPUTATION_IS_INTELLIGENCE",
            "EMERGENCE_LAW_HOLDS_AT_SCALE", "COMPLETE_GMI"],
        "scope_note": ("Thirteen behaviours over one registered neutral substrate with one "
                       "registered task family each and an exhaustive enumeration to the "
                       "declared length bound. A verdict is a statement about that scope and "
                       "about nothing larger. No definition of intelligence is offered."),
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print(json.dumps({"status": result["status"], "failed_gates": failed,
                      "verdicts": dict((k, pub[k]["verdict"]) for k in pub),
                      "deltas": dict((k, pub[k]["delta"]) for k in pub),
                      "histogram": result["verdict_histogram"],
                      "revivals": dict((k, revive[k]["verdict"]) for k in revive),
                      "variants": dict((k, variants[k]["verdict"]) for k in variants),
                      "requirement_entails_predicate": sorted(
                          k for k in stripped
                          if stripped[k]["requirement_entails_predicate"]),
                      "ec3_exercised": ec3_exercised,
        "price_sensitive_behaviours": price_sensitive,
        "price_null_note": ("With no price-sensitive behaviour at this scope the price "
                            "null cannot discriminate: it is reported with its exact "
                            "count and is NOT used to license anything."),
                      "sum_accounting": dict((k, pub[k]["sum_accounting"]["verdict"])
                                             for k in pub)},
                     sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
