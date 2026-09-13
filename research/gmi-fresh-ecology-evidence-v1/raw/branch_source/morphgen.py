"""R5 — generic morphology mutation / recombination grammar over the typed IR
(GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1 R5; the morphogenesis operator list of GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1
section 8: add/remove factor, split/merge factor, add/remove edge, change router, change state family, change update law,
change precision, compile/materialize, introduce/remove verifier gate, introduce/remove lineage, clone/specialize factor,
share/unshare parameters, migrate factor across substrate).

Every operator produces a genotype that must pass `morph.typecheck`; a failed proposal is discarded and re-drawn, and the
draws are charged to the search budget, so the grammar's own inefficiency is part of `B_search` (no free proposals).

The clone/specialize operator is the one whose absence blocked neutral recovery in the expression-tree grammar
(RV-377-023 / RV-377-028, diagnosed in RV-377-057): a coordinated multi-node structure cannot be assembled by point
mutations, but it can be cloned from a working one and re-specialized.
"""
from __future__ import annotations

import json
import random

from . import morph

# kinds the generator may introduce, grouped by output type, with the state kinds it may found a machine on
BY_OUT = {}
for _k, (_cls, _ins, _out, _ps) in morph.KINDS.items():
    BY_OUT.setdefault(_out, []).append(_k)
SEEDS = ("DENSE", "TABLE", "KVSTORE", "PROGRAM")
PARAM_CHOICES = {"width": (1, 2, 4, 6, 8, 12), "keybits": (1, 2, 3, 4), "cap": (4, 8, 16, 32), "grammar": (0, 1), "k": (1, 3, 5), "metric": (0, 1),
                 "temp": (1, 2), "fn": (0, 1, 2), "lr": (1, 2, 4, 8), "budget": (16, 64, 256, 2401), "pop": (2, 4, 8), "depth": (1, 4, 8),
                 "value": (0, 4, 8, 16), "rule": (0, 1, 2), "precision": (4, 8), "device": (0, 1)}


def _new_id(g, kind):
    n = 0
    while f"{kind.lower()}{n}" in g["nodes"]: n += 1
    return f"{kind.lower()}{n}"


def _params(rng, kind):
    return {p: rng.choice(PARAM_CHOICES.get(p, (0, 1, 2))) for p in morph.KINDS[kind][3]}


def _sources_of_type(g, t, exclude=()):
    return [i for i, (k, _) in g["nodes"].items() if morph.KINDS[k][2] == t and i not in exclude]


def seed_genotype(rng):
    """a minimal valid machine: INPUT + TARGET + a state node + one execution node + OUTPUT."""
    g = morph.make({"in0": ("INPUT", {"width": 4}), "tgt0": ("TARGET", {}), "out0": ("OUTPUT", {})}, [])
    # RV-377-202: every kind this constructor names is looked up in the LIVE alphabet, so that a
    # leave-one-out ablation of that kind is a genuine test rather than a generator crash
    # (RV-377-118 Lane C: 19 of 33 kinds were STRUCTURAL_TO_GENERATOR for exactly this reason).
    # With the full alphabet every list below is unchanged, so the draw sequence is byte-identical.
    st = rng.choice([k for k in SEEDS if k in morph.KINDS] or [k for k in morph.KINDS if morph.CLASS_OF[k] == "S"])
    g["nodes"][st.lower() + "0"] = (st, _params(rng, st))
    sid = st.lower() + "0"
    if st == "DENSE" and "LINEAR" in morph.KINDS:
        g["nodes"]["linear0"] = ("LINEAR", {}); g["edges"] += [(sid, "linear0", 0), ("in0", "linear0", 1), ("linear0", "out0", 0)]
    elif st == "PROGRAM" and "PROGEXEC" in morph.KINDS:
        g["nodes"]["progexec0"] = ("PROGEXEC", {}); g["edges"] += [(sid, "progexec0", 0), ("in0", "progexec0", 1), ("progexec0", "out0", 0)]
    else:
        choices = [k for k in ("LOOKUP", "NEAREST", "SCORESELECT") if k in morph.KINDS] or \
                  [k for k in morph.KINDS if morph.CLASS_OF[k] == "R" and morph.KINDS[k][2] == morph.SCA]
        kind = rng.choice(choices); nid = kind.lower() + "0"
        g["nodes"][nid] = (kind, _params(rng, kind)); g["edges"] += [(sid, nid, 0), ("in0", nid, 1), (nid, "out0", 0)]
    return g


# ------------------------------------------------------------------------------------------------------- operators
def op_add_node(rng, g):
    kind = rng.choice([k for k in morph.KINDS if k not in ("INPUT", "TARGET", "OUTPUT")])
    nid = _new_id(g, kind); g["nodes"][nid] = (kind, _params(rng, kind))
    for pt, t in enumerate(morph.KINDS[kind][1]):
        srcs = _sources_of_type(g, t, exclude=(nid,))
        if srcs: g["edges"].append((rng.choice(srcs), nid, pt))
    return g


def op_remove_node(rng, g):
    cand = [i for i, (k, _) in g["nodes"].items() if k not in ("INPUT", "TARGET", "OUTPUT")]
    if not cand: return g
    nid = rng.choice(cand); del g["nodes"][nid]
    g["edges"] = [e for e in g["edges"] if e[0] != nid and e[1] != nid]
    return g


def op_rewire(rng, g):
    if not g["edges"]: return g
    i = rng.randrange(len(g["edges"])); a, b, pt = g["edges"][i]
    srcs = _sources_of_type(g, morph.KINDS[g["nodes"][b][0]][1][pt], exclude=(b,))
    if srcs: g["edges"][i] = (rng.choice(srcs), b, pt)
    return g


def op_add_edge(rng, g):
    dsts = [(i, pt, t) for i, (k, _) in g["nodes"].items() for pt, t in enumerate(morph.KINDS[k][1])]
    if not dsts: return g
    b, pt, t = rng.choice(dsts)
    g["edges"] = [e for e in g["edges"] if not (e[1] == b and e[2] == pt)]
    srcs = _sources_of_type(g, t, exclude=(b,))
    if srcs: g["edges"].append((rng.choice(srcs), b, pt))
    return g


def op_change_param(rng, g):
    cand = [i for i, (k, p) in g["nodes"].items() if p]
    if not cand: return g
    nid = rng.choice(cand); k, p = g["nodes"][nid]; key = rng.choice(list(p))
    g["nodes"][nid] = (k, {**p, key: rng.choice(PARAM_CHOICES.get(key, (0, 1, 2)))})
    return g


def op_change_state_family(rng, g):
    """change state family: swap one state node's kind for another with the same output type."""
    cand = [i for i, (k, _) in g["nodes"].items() if morph.CLASS_OF[k] == "S" and k != "CONST"]
    if not cand: return g
    nid = rng.choice(cand); k, _ = g["nodes"][nid]
    alts = [a for a in BY_OUT[morph.KINDS[k][2]] if a != k and morph.CLASS_OF[a] in "SH" and not morph.KINDS[a][1]]
    if alts:
        na = rng.choice(alts); g["nodes"][nid] = (na, _params(rng, na))
    return g


def op_change_update_law(rng, g):
    cand = [i for i, (k, _) in g["nodes"].items() if morph.CLASS_OF[k] == "U"]
    if not cand: return op_add_node(rng, g)
    nid = rng.choice(cand); alts = [k for k in morph.KINDS if morph.CLASS_OF[k] == "U" and k != g["nodes"][nid][0]]
    na = rng.choice(alts); g["nodes"][nid] = (na, _params(rng, na))
    g["edges"] = [e for e in g["edges"] if e[1] != nid]
    for pt, t in enumerate(morph.KINDS[na][1]):
        srcs = _sources_of_type(g, t, exclude=(nid,))
        if srcs: g["edges"].append((rng.choice(srcs), nid, pt))
    return g


def op_insert_verifier(rng, g):
    """introduce a verifier gate: route the served value through ABSTAIN driven by a VERIFY/VERIFYTAB flag."""
    out = [i for i, (k, _) in g["nodes"].items() if k == "OUTPUT"][0]
    fe = [e for e in g["edges"] if e[1] == out]
    if not fe: return g
    if "ABSTAIN" not in morph.KINDS: return g          # RV-377-202: kind-agnostic
    src = fe[0][0]; g["edges"].remove(fe[0])
    aid = _new_id(g, "ABSTAIN"); g["nodes"][aid] = ("ABSTAIN", {})
    flags = _sources_of_type(g, morph.FLAG)
    if not flags:
        if "VERIFY" not in morph.KINDS: return g       # RV-377-202
        vid = _new_id(g, "VERIFY"); g["nodes"][vid] = ("VERIFY", {})
        for pt, t in enumerate(morph.KINDS["VERIFY"][1]):
            s = _sources_of_type(g, t, exclude=(vid,))
            if s: g["edges"].append((rng.choice(s), vid, pt))
        flags = [vid]
    g["edges"] += [(src, aid, 0), (rng.choice(flags), aid, 1), (aid, out, 0)]
    return g


def op_materialize(rng, g):
    """compile / materialize: insert MATERIALIZE + LOOKUP in front of a PROGRAM-fed path."""
    progs = [i for i, (k, _) in g["nodes"].items() if k == "PROGRAM"]
    if not progs or "MATERIALIZE" not in morph.KINDS or "LOOKUP" not in morph.KINDS: return g   # RV-377-202
    mid = _new_id(g, "MATERIALIZE"); lid = _new_id(g, "LOOKUP")
    g["nodes"][mid] = ("MATERIALIZE", _params(rng, "MATERIALIZE")); g["nodes"][lid] = ("LOOKUP", {})
    inp = [i for i, (k, _) in g["nodes"].items() if k == "INPUT"][0]
    g["edges"] += [(rng.choice(progs), mid, 0), (mid, lid, 0), (inp, lid, 1)]
    out = [i for i, (k, _) in g["nodes"].items() if k == "OUTPUT"][0]
    g["edges"] = [e for e in g["edges"] if e[1] != out] + [(lid, out, 0)]
    return g


def op_add_lineage(rng, g):
    tabs = [i for i, (k, _) in g["nodes"].items() if morph.KINDS[k][2] == morph.TAB and morph.CLASS_OF[k] == "S"]
    if not tabs or "VERSIONED" not in morph.KINDS: return g   # RV-377-202
    vid = _new_id(g, "VERSIONED"); g["nodes"][vid] = ("VERSIONED", _params(rng, "VERSIONED"))
    g["edges"].append((rng.choice(tabs), vid, 0))
    return g


def op_clone_specialize(rng, g):
    """clone / specialize factor: duplicate a node together with its incoming wiring and perturb its parameters.
    The coordinated-structure operator (see the module docstring)."""
    cand = [i for i, (k, _) in g["nodes"].items() if k not in ("INPUT", "TARGET", "OUTPUT")]
    if not cand: return g
    src = rng.choice(cand); k, p = g["nodes"][src]; nid = _new_id(g, k)
    np_ = dict(p)
    if np_:
        key = rng.choice(list(np_)); np_[key] = rng.choice(PARAM_CHOICES.get(key, (0, 1, 2)))
    g["nodes"][nid] = (k, np_)
    for a, b, pt in list(g["edges"]):
        if b == src: g["edges"].append((a, nid, pt))
    # wire the clone somewhere that accepts its type
    dsts = [(i, pt) for i, (kk, _) in g["nodes"].items() if i != nid for pt, t in enumerate(morph.KINDS[kk][1]) if t == morph.KINDS[k][2]]
    if dsts:
        b, pt = rng.choice(dsts)
        g["edges"] = [e for e in g["edges"] if not (e[1] == b and e[2] == pt)] + [(nid, b, pt)]
    return g


OPS = (op_add_node, op_remove_node, op_rewire, op_add_edge, op_change_param, op_change_state_family, op_change_update_law,
       op_insert_verifier, op_materialize, op_add_lineage, op_clone_specialize)
OP_NAMES = tuple(f.__name__ for f in OPS)


def mutate(rng, g, tries=12, record=None):
    """apply one operator; retry on a genotype that fails the type check. Every try is charged to the caller.

    `record`, when a list is passed, receives one entry per DRAW: the operator name and whether that draw survived the
    type check. The draw sequence off `rng` is unchanged by the presence of the recorder, so a recorded run and an
    unrecorded run with the same seed produce the same genotype (R7 lineage replay depends on this)."""
    for _ in range(tries):
        f = OPS[rng.randrange(len(OPS))]
        try:
            cand = f(rng, json.loads(json.dumps(g)))   # RV-377-202: an operator that trips on an absent kind is a failed draw, not a crash
            morph.typecheck(cand); _check_servable(cand)
            if record is not None: record.append((f.__name__, True))
            return cand, tries
        except (morph.MorphError, ValueError, KeyError, IndexError):
            if record is not None: record.append((f.__name__, False))
            continue
    return json.loads(json.dumps(g)), tries


def crossover(rng, a, b, tries=12, record=None):
    """graft a random node of b (with its parameters) into a, wired to a's sources. `record` as in `mutate`."""
    for _ in range(tries):
        child = json.loads(json.dumps(a))
        cand = [i for i, (k, _) in b["nodes"].items() if k not in ("INPUT", "TARGET", "OUTPUT")]
        if not cand: return child, tries
        src = rng.choice(cand); k, p = b["nodes"][src]; nid = _new_id(child, k); child["nodes"][nid] = (k, dict(p))
        for pt, t in enumerate(morph.KINDS[k][1]):
            s = _sources_of_type(child, t, exclude=(nid,))
            if s: child["edges"].append((rng.choice(s), nid, pt))
        dsts = [(i, pt) for i, (kk, _) in child["nodes"].items() if i != nid for pt, t in enumerate(morph.KINDS[kk][1]) if t == morph.KINDS[k][2]]
        if dsts:
            d, pt = rng.choice(dsts)
            child["edges"] = [e for e in child["edges"] if not (e[1] == d and e[2] == pt)] + [(nid, d, pt)]
        try:
            morph.typecheck(child); _check_servable(child)
            if record is not None: record.append(("op_graft_recombine", True))
            return child, tries
        except (morph.MorphError, ValueError, KeyError, IndexError):
            if record is not None: record.append(("op_graft_recombine", False))
            continue
    return json.loads(json.dumps(a)), tries


def _check_servable(g):
    """the OUTPUT must be reachable from INPUT or from a state node, so the machine actually serves something."""
    outs = [i for i, (k, _) in g["nodes"].items() if k == "OUTPUT"]
    if len(outs) != 1: raise morph.MorphError("need exactly one OUTPUT")
    ins = {}
    for a, b, pt in g["edges"]: ins.setdefault(b, {})[pt] = a
    if 0 not in ins.get(outs[0], {}): raise morph.MorphError("OUTPUT unbound")
    return True


def random_genotype(rng, steps=6):
    g = seed_genotype(rng)
    for _ in range(steps): g, _ = mutate(rng, g)
    return g
