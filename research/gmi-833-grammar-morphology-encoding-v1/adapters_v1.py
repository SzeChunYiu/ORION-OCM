#!/usr/bin/env python3
"""Grammar adapters for GMI #833 B48 (`gmi-833-grammar-morphology-encoding-v1`).

Each adapter reads a REAL merged corpus grammar and emits the uniform cost object
frozen in FREEZE_V1.md section 2:

    {grammar_id, package, source_citation, declared_target, target_citation,
     presentations: [{pid, leaves, cost, sem}], composites, disclosure}

`leaves` are STRING-valued named productions only (Amendment A1). Grammars with no
production structure emit `leaves = []` and are handled by R2/R3 alone; they must never
emit a presentation identity as a pseudo-production.

Every `declared_target` is quoted verbatim from the owning package's own frozen document
with a file:line citation. Nothing is inferred.

stdlib only; exact integers; deterministic (sorted iteration everywhere). Python 3.8-safe.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from itertools import product
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[2]
RESEARCH = REPO / "research"

SCHEMA = "GMI_833_GRAMMAR_MORPHOLOGY_ADAPTERS_V1"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _cite(rel: str, line: int, verbatim: str) -> Dict[str, object]:
    return {"path": rel, "line": line, "verbatim": verbatim}


def _str_leaves(obj) -> List[str]:
    """Amendment A1: string-valued atoms only; numeric atoms are parameters."""
    out = []  # type: List[str]
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, str):
            out.append(cur)
        elif isinstance(cur, (list, tuple)):
            stack.extend(list(cur))
        elif isinstance(cur, dict):
            stack.extend(sorted(cur.keys(), key=repr))
            stack.extend([cur[k] for k in sorted(cur.keys(), key=repr)])
    return sorted(out)


def _pres(pid: str, leaves, cost: int, sem: str) -> Dict[str, object]:
    if not isinstance(cost, int):
        raise TypeError("cost must be an exact int, got %r" % (cost,))
    return {"pid": pid, "leaves": sorted(leaves), "cost": cost, "sem": sem}


# --------------------------------------------------------------------------- #891
def adapter_cost_privilege() -> List[Dict[str, object]]:
    """#891 gmi-833-g0-cost-privilege-v1: the registered structural-bias pair GA/GB.

    Frozen source lines 148-167 of g0_cost_privilege_v1.py define the counterexample:
    GA has ALPHA=(1,1), BETA=(3,2); GB has ALPHA=(3,2), BETA=(1,1). Coverage is equal.
    These are bare cost tables: NO production structure (Amendment A1) -> leaves = [].
    """
    rel = "research/gmi-833-g0-cost-privilege-v1/g0_cost_privilege_v1.py"
    mod = _load(RESEARCH / "gmi-833-g0-cost-privilege-v1" / "g0_cost_privilege_v1.py",
                "gmi833_cost_privilege")
    w = (1, 1)

    def scalar(p) -> int:
        return w[0] * p.L + w[1] * p.d

    out = []  # type: List[Dict[str, object]]
    # GA / GB exactly as registered in structural_bias_counterexample().
    ga = [("ga_a", "ALPHA", 1, 1), ("ga_b", "BETA", 3, 2)]
    gb = [("gb_a", "ALPHA", 3, 2), ("gb_b", "BETA", 1, 1)]
    for gid, rows, line in (("cost_privilege_GA", ga, 150), ("cost_privilege_GB", gb, 154)):
        out.append({
            "grammar_id": gid,
            "package": "gmi-833-g0-cost-privilege-v1",
            "source_citation": "%s:%d" % (rel, line),
            "declared_target": "ALPHA",
            "target_citation": _cite(
                "research/gmi-833-g0-cost-privilege-v1/COST_PRIVILEGE_THEOREMS_V1.md", 60,
                "Under `w=(1,1)`, grammar `GA` assigns `ALPHA=(1,1)` and `BETA=(3,2)`, "
                "selecting `ALPHA`."),
            "presentations": [_pres(pid, [], w[0] * L + w[1] * d, sem)
                              for pid, sem, L, d in rows],
            "composites": [],
            "production_structure": "NONE",
            "disclosure": {
                "declared": True, "charged": True,
                "evidence": ["research/gmi-833-g0-cost-privilege-v1/"
                             "COST_PRIVILEGE_THEOREMS_V1.md:BIAS-1"],
            },
            "weight": list(w),
        })
    # The registered 6-presentation object (label-blindness / isometry scope).
    reg = []  # type: List[Dict[str, object]]
    for p in mod.BASE:
        reg.append(_pres(p.presentation_id, [], scalar(p), p.semantic_class))
    out.append({
        "grammar_id": "cost_privilege_REGISTERED",
        "package": "gmi-833-g0-cost-privilege-v1",
        "source_citation": "%s:%d" % (rel, 36),
        "declared_target": None,
        "target_citation": None,
        "presentations": reg,
        "composites": [],
        "production_structure": "NONE",
        "disclosure": {"declared": True, "charged": True, "evidence": []},
        "weight": list(w),
    })
    return out


# ------------------------------------------------------------- cross-grammar four family
def adapter_cross_grammar() -> List[Dict[str, object]]:
    """gmi-cross-grammar-four-family-v1: 4 families x 2 independently structured grammars.

    Presentations are the candidates that are EXACT for the package's own positive ecology
    (its `_score` filter); `sem` is the package's own post-run `classify()`; `cost` is the
    package's own per-family cost function. Nothing is re-invented.
    """
    pkg = "gmi-cross-grammar-four-family-v1"
    rel = "research/%s/cross_grammar_four_family_v1.py" % pkg
    m = _load(RESEARCH / pkg / "cross_grammar_four_family_v1.py", "gmi_cross_grammar")

    targets = {
        "state": ("RECURRENT_STATE", 44),
        "local": ("SHARED_LOCAL_UPDATE", 45),
        "routing": ("INPUT_INDEXED_ROUTING", 46),
        "storage": ("KEYED_STORAGE", 47),
    }
    verbatim = {
        "state": '"state": "RECURRENT_STATE",',
        "local": '"local": "SHARED_LOCAL_UPDATE",',
        "routing": '"routing": "INPUT_INDEXED_ROUTING",',
        "storage": '"storage": "KEYED_STORAGE",',
    }

    specs = []  # type: List[Tuple[str, str, object, object, object, object, int]]

    # --- state ---------------------------------------------------------------
    positive_state = tuple(int(n % 2 == 0) for n in range(7))
    twin_state = (1,) * 7
    specs.append(("state", "A", m._state_a_candidates(),
                  lambda c: m._state_a_trace(c) == positive_state,
                  lambda c: m._state_a_trace(c) == twin_state,
                  lambda c: 2 * c[0], 66))
    specs.append(("state", "B", tuple(product(m.STATE_EXPRESSIONS, repeat=2)),
                  lambda c: m._state_b_trace(c) == positive_state,
                  lambda c: m._state_b_trace(c) == twin_state,
                  lambda c: sum(n.startswith("not_") for n in c), 66))

    # --- local ---------------------------------------------------------------
    local_a = tuple(product(("triple", "configuration"), ("shared", "site")))
    specs.append(("local", "A", local_a,
                  lambda c: m._local_a_fit(c, False) is not None,
                  lambda c: m._local_a_fit(c, True) is not None,
                  lambda c: len(m._local_a_fit(c, False) or m._local_a_fit(c, True) or {}),
                  135))
    shared = tuple(("shared", (e,)) for e in m.LOCAL_EXPRESSIONS)
    site = tuple(("site", es) for es in product(m.LOCAL_EXPRESSIONS, repeat=4))
    specs.append(("local", "B", shared + site,
                  lambda c: m._local_b_exact(c, False),
                  lambda c: m._local_b_exact(c, True),
                  lambda c: sum(0 if isinstance(e, str) else 1 for e in c[1]), 135))

    # --- routing -------------------------------------------------------------
    routing_a = ((0,), (1,), (2,), (3,), ("from_input",))
    routing_b = (tuple(("read", i) for i in range(4))
                 + tuple(("branches", lv) for lv in product(range(4), repeat=4)))

    def _apply_a(c, ptr, data):
        return data[ptr] if c[0] == "from_input" else data[c[0]]

    def _apply_b(c, ptr, data):
        return data[c[1][ptr]] if c[0] == "branches" else data[c[1]]

    twin_cases = tuple((0, d) for d in product((0, 1), repeat=4))
    specs.append(("routing", "A", routing_a,
                  lambda c: all(_apply_a(c, p, d) == d[p] for p, d in m.ROUTING_CASES),
                  lambda c: all(_apply_a(c, p, d) == d[0] for p, d in twin_cases),
                  lambda c: 3 if c[0] == "from_input" else 1, 157))
    specs.append(("routing", "B", routing_b,
                  lambda c: all(_apply_b(c, p, d) == d[p] for p, d in m.ROUTING_CASES),
                  lambda c: all(_apply_b(c, p, d) == d[0] for p, d in twin_cases),
                  lambda c: 3 if c[0] == "branches" else 1, 157))

    # --- storage -------------------------------------------------------------
    weighted = tuple(("weighted", w, b)
                     for w in product(range(-2, 3), repeat=3) for b in range(-2, 3))
    rows = tuple(("rows", v) for v in product((0, 1), repeat=8))
    storage_a = weighted + rows
    programs = tuple(("expression", v) for v in m._boolean_program_signatures())
    lv = tuple(("leaves", v) for v in product((0, 1), repeat=8))
    storage_b = programs + lv

    def _out_a(c):
        if c[0] == "rows":
            return c[1]
        _k, w, b = c
        return tuple(int(sum(x * y for x, y in zip(k, w)) + b >= 0) for k in m.KEYS)

    twin_storage = tuple(k[0] for k in m.KEYS)
    specs.append(("storage", "A", storage_a,
                  lambda c: _out_a(c) == m.UNSTRUCTURED,
                  lambda c: _out_a(c) == twin_storage,
                  lambda c: 8 if c[0] == "rows" else 4, 204))
    specs.append(("storage", "B", storage_b,
                  lambda c: c[1] == m.UNSTRUCTURED,
                  lambda c: c[1] == twin_storage,
                  lambda c: 8 if c[0] == "leaves" else 2, 204))

    out = []  # type: List[Dict[str, object]]
    for family, gname, cands, exact, twin_exact, cost, line in specs:
        # Amendment A3.1: union over the package's OWN registered ecologies
        # (positive + matched negative twin), deduplicated by candidate.
        pres = []  # type: List[Dict[str, object]]
        for c in sorted(cands, key=repr):
            ecos = []
            if exact(c):
                ecos.append("positive")
            if twin_exact(c):
                ecos.append("twin")
            if not ecos:
                continue
            row = _pres(repr(c), _str_leaves(c), int(cost(c)),
                        m.classify(family, gname, c))
            row["ecologies"] = ecos
            pres.append(row)
        tgt, tline = targets[family]
        vocab = sorted(set(x for p in pres for x in p["leaves"]))
        out.append({
            "grammar_id": "cross_grammar_%s_%s" % (family, gname),
            "package": pkg,
            "source_citation": "%s:%d" % (rel, line),
            "declared_target": tgt,
            "target_citation": _cite("research/%s/RESULT_V1.json" % pkg, tline,
                                     verbatim[family]),
            "presentations": pres,
            "composites": [],
            "production_structure": "NAMED" if vocab else "NUMERIC_ONLY",
            "disclosure": {
                "declared": True, "charged": True,
                "evidence": [
                    "research/%s/CROSS_GRAMMAR_RECOVERY_V1.md:#protocol "
                    "(two independently structured grammars, candidate spaces not in "
                    "one-to-one correspondence, no shared evaluator)" % pkg,
                    "research/%s/RESULT_V1.json:positive_twin_flips=8 "
                    "(matched negative twin ecologies)" % pkg,
                ],
            },
        })
    return out


# ---------------------------------------------------------------------- grammar growth
def _encodings(word: Tuple[str, ...], lib: Dict[str, Tuple[str, ...]],
               allowed: Tuple[str, ...]) -> List[Tuple[str, ...]]:
    """All encodings of `word` over `allowed` symbols, given expansions `lib`."""
    expand = {}  # type: Dict[str, Tuple[str, ...]]
    for s in allowed:
        cur = (s,)
        while any(x in lib for x in cur):
            nxt = []  # type: List[str]
            for x in cur:
                nxt.extend(lib[x] if x in lib else (x,))
            cur = tuple(nxt)
        expand[s] = cur
    n = len(word)
    memo = {}  # type: Dict[int, List[Tuple[str, ...]]]

    def go(i: int) -> List[Tuple[str, ...]]:
        if i == n:
            return [()]
        if i in memo:
            return memo[i]
        acc = []  # type: List[Tuple[str, ...]]
        for s in allowed:
            e = expand[s]
            if word[i:i + len(e)] == e:
                for rest in go(i + len(e)):
                    acc.append((s,) + rest)
        memo[i] = acc
        return acc

    return go(0)


def adapter_grammar_growth() -> List[Dict[str, object]]:
    """#897 gmi-833-g0-grammar-growth-v1: the grown library grammar G2.

    Base tokens a/b/c plus the deterministically invented recursive library
    m1 -> a b, m2 -> m1 m1 (CORE.md). Presentations are the encodings of the package's
    own frozen held-out words; cost is symbol count (the package's own description
    burden); the semantic classes are the package's own two declared held-out
    populations.
    """
    pkg = "gmi-833-g0-grammar-growth-v1"
    fx = json.loads((RESEARCH / pkg / "FROZEN_FIXTURES_V1.json").read_text())
    lib = {"m1": ("a", "b"), "m2": ("m1", "m1")}
    base = tuple(fx["base_token_order"])
    allowed = tuple(sorted(base) + ["m1", "m2"])

    populations = (("heldout_reuse_positive", "REUSE_POSITIVE"),
                   ("heldout_unrelated_control", "UNRELATED_CONTROL"))
    pres = []  # type: List[Dict[str, object]]
    for key, sem in populations:
        for wi, w in enumerate(fx[key]):
            wt = tuple(w)
            for ei, enc in enumerate(_encodings(wt, lib, allowed)):
                pres.append(_pres("%s#%d#%d" % (key, wi, ei), list(enc), len(enc), sem))
    return [{
        "grammar_id": "grammar_growth_G2",
        "package": pkg,
        "source_citation": "research/%s/CORE.md:5" % pkg,
        "declared_target": "REUSE_POSITIVE",
        "target_citation": _cite(
            "research/%s/CORE.md" % pkg, 7,
            "a strict charged held-out discovery-burden reduction on unseen "
            "reuse-positive targets with a preserved negative control"),
        "presentations": pres,
        "composites": ["m1", "m2"],
        "production_structure": "NAMED",
        "disclosure": {
            "declared": True, "charged": True,
            "evidence": [
                "research/%s/CORE.md:10 (K_total=6 charged; kappa=1)" % pkg,
                "research/%s/CORE.md:11 (H- control net +1178; regression preserved)" % pkg,
                "research/%s/CORE.md:12 (0/200 randomized-admission nulls better)" % pkg,
            ],
        },
    }]


# ------------------------------------------------------------------------ grammar bias
def adapter_grammar_bias() -> List[Dict[str, object]]:
    """#875 gmi-833-g0-grammar-bias-v1: the frozen 126-presentation G0-reg-v1 slice.

    Emitted so PRED-2 (`NO_DECLARED_TARGET`) is testable rather than asserted: this
    package MEASURES bias, it does not recover a family, so it declares no target
    morphology. Productions are the instruction-class opcodes of each presentation.
    """
    pkg = "gmi-833-g0-grammar-bias-v1"
    m = _load(RESEARCH / pkg / "grammar_bias_core_v1.py", "gmi833_grammar_bias")
    presentations = m.enumerate_presentations()
    adjacency = m.build_adjacency(presentations)
    dist = m.bfs_distances(adjacency, (m.start_node(presentations),))
    pres = []  # type: List[Dict[str, object]]
    for pid in sorted(presentations):
        payload = json.loads(pid)
        leaves = [str(instr[0]) for instr in payload[1:]]
        sem = m.semantic_key(m.semantic_signature(presentations[pid]))
        pres.append(_pres(pid, leaves, int(payload[0]) + int(dist[pid]), sem))
    return [{
        "grammar_id": "grammar_bias_G0_slice",
        "package": pkg,
        "source_citation": "research/%s/grammar_bias_core_v1.py:79" % pkg,
        "declared_target": None,
        "target_citation": None,
        "presentations": pres,
        "composites": [],
        "production_structure": "NAMED",
        "disclosure": {"declared": True, "charged": True, "evidence": []},
    }]


# ------------------------------------------------------------------- registered control
def adapter_clean_control() -> List[Dict[str, object]]:
    """Registered CLEAN control grammar for validation V3(b).

    Every semantic class is realized by presentations over the SAME production vocabulary
    at the same costs, so no production can be target-exclusive. Any flag here is a
    detector false positive.
    """
    pres = []  # type: List[Dict[str, object]]
    vocab = ("p", "q", "r")
    for sem in ("CLS0", "CLS1", "CLS2"):
        for i, combo in enumerate(sorted(product(vocab, repeat=2))):
            pres.append(_pres("%s#%d" % (sem, i), list(combo), 2, sem))
    return [{
        "grammar_id": "clean_control_NEUTRAL",
        "package": "gmi-833-grammar-morphology-encoding-v1",
        "source_citation": "research/gmi-833-grammar-morphology-encoding-v1/adapters_v1.py:"
                           "adapter_clean_control",
        "declared_target": "CLS0",
        "target_citation": _cite(
            "research/gmi-833-grammar-morphology-encoding-v1/FREEZE_V1.md", 0,
            "registered clean/neutral grammar (validation V3b)"),
        "presentations": pres,
        "composites": [],
        "production_structure": "NAMED",
        "disclosure": {"declared": True, "charged": True, "evidence": []},
    }]


ADAPTERS = (
    ("gmi-833-g0-cost-privilege-v1", adapter_cost_privilege),
    ("gmi-cross-grammar-four-family-v1", adapter_cross_grammar),
    ("gmi-833-g0-grammar-growth-v1", adapter_grammar_growth),
    ("gmi-833-g0-grammar-bias-v1", adapter_grammar_bias),
    ("gmi-833-grammar-morphology-encoding-v1", adapter_clean_control),
)


def load_all() -> List[Dict[str, object]]:
    out = []  # type: List[Dict[str, object]]
    for _pkg, fn in ADAPTERS:
        out.extend(fn())
    out.sort(key=lambda g: g["grammar_id"])
    return out


if __name__ == "__main__":
    gs = load_all()
    for g in gs:
        print("%-34s pres=%-6d classes=%-3d target=%s" % (
            g["grammar_id"], len(g["presentations"]),
            len(set(p["sem"] for p in g["presentations"])), g["declared_target"]))
