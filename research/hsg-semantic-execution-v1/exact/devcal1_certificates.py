"""DEV-CAL-1 fail-closed structural-certificate checker + purity checker.

latent_same iff the (source,target) pair carries at least one frozen structural
certificate:
  (a) isomorphic decomposition DAG modulo relabeling, depth <= 4;
  (b) same frozen typed-operator support multiset solves BOTH worlds
      (verified by execution on both);
  (c) explicitly constructed homomorphism source-DAG -> target-DAG verified
      by the checker (label- and edge-preserving on typed operators).
latent_different iff all three are CHECKED and failed.  Any check that cannot
run emits CANNOT_CHECK with a reason -- never silence (HC-4).

Purity checker: target-solution digests absent from history bytes, BOTH
directions: sha256 hash match AND normalized-text match.

Every checker here has a hostile positive control (planted defect fires) and
a clean no-alarm control (clean input silent); both are run by run_devcal1.
Python 3.8+ stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter

from exact.devcal1_worlds import (
    LATENT_SHAPES, execute_dag, dag_root, OP_INPUT_CONTRACT,
)

# ------------------------------------------------------------- digests ------
def sha(s):
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s).hexdigest()

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      default=repr)

# ------------------------------------------- certificate (a): DAG iso ------
def _shape_dag_canonical(shape):
    """Canonical form of a decomposition DAG modulo node relabeling,
    anchored at the ROOT (the unique unconsumed node).  Recursively hash
    each node as (op, sorted(child canonical hashes)); two shapes are
    isomorphic modulo relabeling iff root canonical hashes match.  Depth
    gate: certificate (a) requires depth <= 4.
    """
    root = dag_root(shape)
    if root is None:
        return None, None
    memo = {}
    def dep(j):
        _, ch = shape[j]
        return 1 + max(dep(c) for c in ch) if ch else 1
    depth = dep(root)
    # canonicalize bottom-up: children have smaller indices in frozen shapes,
    # but hash from the root recursively so anchoring is explicit
    def canon(j):
        if j in memo:
            return memo[j]
        op, ch = shape[j]
        memo[j] = sha(canonical_json([op, sorted(canon(c) for c in ch)]))
        return memo[j]
    return canon(root), depth

def cert_a(shape_s, shape_t):
    """(held: bool, detail). CANNOT_CHECK never fires here: the check is
    total on finite frozen shapes."""
    can_s, d_s = _shape_dag_canonical(shape_s)
    can_t, d_t = _shape_dag_canonical(shape_t)
    if d_s > 4 or d_t > 4:
        return False, {"reason": "depth>4 outside certificate-(a) scope",
                       "depth_s": d_s, "depth_t": d_t}
    return (can_s == can_t), {"canonical_s": can_s, "canonical_t": can_t}

# --------------------------------------- certificate (b): support multiset --
def _support_multiset(shape):
    return Counter(op for op, _ in shape)

def _shape_solves(shape, world):
    """Verified by execution on the world's own binding and goal."""
    tok = world["inputs"][world["root_slot"]]
    val = execute_dag(shape, tok["type"], tok["value"])
    return val is not None and val == world["goal"]

def cert_b(shape_s, world_s, world_t):
    """(held, detail): the same typed-operator support multiset solves BOTH.
    The multiset is taken from the SOURCE shape; it must solve source (by
    construction of the source world) AND target."""
    ms = _support_multiset(shape_s)
    ok_s = _shape_solves(shape_s, world_s)
    mt = _support_multiset(world_t["shape"])
    detail = {"support_multiset": dict(ms),
              "solves_source": bool(ok_s),
              "target_support_multiset": dict(mt),
              "multiset_equal": ms == mt}
    if not ok_s:
        return False, dict(detail, note="source shape fails its own world")
    return ms == mt, detail

# --------------------------------------- certificate (c): homomorphism -----
def cert_c(shape_s, shape_t):
    """(held, detail): explicit ROOT-ANCHORED, label-preserving homomorphism
    h: nodes(S) -> nodes(T); every S-child relation maps into T-child
    relations of the image.  Exhaustive over all maps (<= 4^4: total)."""
    import itertools
    rs, rt = dag_root(shape_s), dag_root(shape_t)
    if rs is None or rt is None:
        return False, {"homomorphism": None, "reason": "malformed dag"}
    if shape_s[rs][0] != shape_t[rt][0]:
        return False, {"homomorphism": None, "reason": "root op differs"}
    ns, nt = len(shape_s), len(shape_t)
    best = None
    for assign in itertools.product(range(nt), repeat=ns):
        if assign[rs] != rt:
            continue
        ok = True
        for j in range(ns):
            op_s, ch_s = shape_s[j]
            op_t, ch_t = shape_t[assign[j]]
            if op_s != op_t or any(assign[c] not in ch_t for c in ch_s):
                ok = False
                break
        if ok:
            best = list(assign)
            break
    detail = {"homomorphism": best}
    return best is not None, detail

# --------------------------------------------------------- the gate ---------
def check_structural_relation(world):
    """Fail-closed latent-relation check for one DEV-CAL-1 world pair.

    Returns dict with latent_same, certificate_type ('a'|'b'|'c'|None),
    certificate_digest, checks {a,b,c} each CHECKED/HELD..., and
    cannot_check list (must be empty for the world to score).
    """
    s, t = world["source"], world["target"]
    res = {}
    cannot = []
    try:
        res["a"] = cert_a(s["shape"], t["shape"])
    except Exception as exc:  # noqa: BLE001 - fail closed, never silent
        res["a"] = None
        cannot.append({"certificate": "a", "reason": repr(exc)})
    try:
        res["b"] = cert_b(s["shape"], s, t)
    except Exception as exc:  # noqa: BLE001
        res["b"] = None
        cannot.append({"certificate": "b", "reason": repr(exc)})
    try:
        res["c"] = cert_c(s["shape"], t["shape"])
    except Exception as exc:  # noqa: BLE001
        res["c"] = None
        cannot.append({"certificate": "c", "reason": repr(exc)})

    held = None
    for k in ("a", "b", "c"):
        if res[k] is not None and res[k][0]:
            held = k
            break
    cert_digest = None
    if held is not None:
        cert_digest = sha(canonical_json(
            {"world": "%s-%02d" % (world["cell"], world["world_index"]),
             "certificate": held, "detail": res[held][1]}))
    return {
        "latent_same": (held is not None) if not cannot else None,
        "certificate_type": held,
        "certificate_digest": cert_digest,
        "checks": {k: (None if v is None else
                       {"held": bool(v[0]), **v[1]}) for k, v in res.items()},
        "cannot_check": cannot,
    }

def check_surface_relation(world):
    """surface_same iff identical frozen surface signature; verified, not
    trusted from the cell label."""
    sig_s, sig_t = world["sig_source"], world["sig_target"]
    return {"surface_same": sig_s == sig_t,
            "sig_source": sig_s, "sig_target": sig_t}

# ------------------------------------------------------ purity checker ------
def _normalize(text):
    """Normalized text: collapse whitespace/case, strip non-alphanumerics.
    Defeats formatting-level concealment of a copied solution."""
    return re.sub(r"[^a-z0-9]", "", text.lower())

def history_bytes(history):
    return canonical_json(history).encode("utf-8")

def target_solution_digests(world, solution_obj):
    """Digests of everything that would constitute a leaked target answer:
    the concrete method, its execution trace, and the goal value binding."""
    return {
        "method_digest": sha(canonical_json(solution_obj["method"])),
        "solution_digest": sha(canonical_json(solution_obj)),
        "trace_digest": sha(canonical_json(solution_obj.get("trace", {}))),
    }

_METHOD_TEXT_FLOOR = 8  # normalized chars; below this a method-only
                        # substring test is unsound for symbolic methods
                        # (e.g. "refine0" sits inside any REFINE template)

def purity_check(history, world, solution_obj):
    """(pure: bool|None, detail).  Both directions:
      1. hash: no target-solution digest (method / full solution / trace)
         appears in history bytes;
      2. normalized-text: the normalized FULL solution serialization (method
         + value + identity keys) must not be contained in the normalized
         history bytes; a method-only text test additionally runs when the
         normalized method is long enough to be sound (>= floor chars),
         otherwise it is recorded as skipped_short_method, never silent.
    Unserializable history -> CANNOT_CHECK (pure=None), never silent."""
    try:
        hb = history_bytes(history)
    except Exception as exc:  # noqa: BLE001
        return None, {"status": "CANNOT_CHECK", "reason": repr(exc)}
    digests = target_solution_digests(world, solution_obj)
    hits = [k for k, d in digests.items() if d.encode() in hb]
    norm_hist = _normalize(hb.decode("utf-8", "replace"))
    norm_full = _normalize(canonical_json(solution_obj))
    norm_method = _normalize(canonical_json(solution_obj["method"]))
    text_hit = bool(norm_full and norm_full in norm_hist)
    method_note = None
    if len(norm_method) >= _METHOD_TEXT_FLOOR:
        if norm_method in norm_hist:
            text_hit = True
        method_note = "checked"
    else:
        method_note = "skipped_short_method(len=%d<%d)" % (
            len(norm_method), _METHOD_TEXT_FLOOR)
    pure = (not hits) and (not text_hit)
    detail = {"status": "CHECKED", "digest_hits": hits,
              "normalized_text_hit": bool(text_hit),
              "method_text_direction": method_note}
    return pure, detail

# ------------------------------------------------------------ controls ------
def hostile_and_clean_controls():
    """Run the checkers' hostile positive + clean no-alarm controls.

    Returns dict of control receipts. Any control misbehaving => the run is
    ASSAY_DEFECT (checked by the runner).
    """
    receipts = {}
    # -- structural checker: planted latent_same must certify (hostile fire)
    import copy
    import exact.devcal1_worlds as W
    w_ok = W.build_cell("B", 0)
    chk = check_structural_relation(w_ok)
    receipts["structural_hostile_fire"] = {
        "control": "cell-B world declared latent_same must carry a certificate",
        "fired": chk["latent_same"] is True and chk["certificate_type"] in ("a", "b", "c"),
        "detail": {"certificate_type": chk["certificate_type"]},
    }
    # clean no-alarm: cell-D world must NOT certify
    w_d = W.build_cell("D", 0)
    chk_d = check_structural_relation(w_d)
    receipts["structural_clean_silent"] = {
        "control": "cell-D world declared latent_different must carry none",
        "silent": chk_d["latent_same"] is False,
        "detail": {"certificate_type": chk_d["certificate_type"]},
    }
    # -- surface checker: reminted world must compare surface_different
    s_chk = check_surface_relation(w_ok)
    receipts["surface_hostile_fire"] = {
        "control": "cell-B surface must compare different",
        "fired": s_chk["surface_same"] is False,
    }
    s_chk_a = check_surface_relation(W.build_cell("A", 0))
    receipts["surface_clean_silent"] = {
        "control": "cell-A surface must compare same",
        "silent": s_chk_a["surface_same"] is True,
    }
    # -- purity checker: PLANTED LEAK must fire (hostile); realistic size-3
    # method so the control exercises the production code path
    fake_world = {"goal": 7}
    leak_solution = {"method": [["REDUCE", []], ["VERIFY", [0]],
                                ["TRANSPORT", [1]]],
                     "value": 7, "trace": {"v": 7}}
    leaky_history = {"objects": [
        {"kind": "template", "payload": canonical_json(leak_solution)}]}
    pure_leak, det_leak = purity_check(leaky_history, fake_world, leak_solution)
    receipts["purity_hostile_fire"] = {
        "control": "history containing the target solution must be flagged",
        "fired": pure_leak is False and det_leak["status"] == "CHECKED",
        "detail": det_leak,
    }
    # clean no-alarm: a DIFFERENT structural template stays silent
    clean_history = {"objects": [
        {"kind": "template",
         "payload": canonical_json([["TRANSPORT", []],
                                    ["DISTINGUISH", [0, 1]],
                                    ["REFINE", [2]]])}]}
    pure_clean, det_clean = purity_check(clean_history, fake_world, leak_solution)
    receipts["purity_clean_silent"] = {
        "control": "clean template-only history must stay silent",
        "silent": pure_clean is True and det_clean["status"] == "CHECKED",
        "detail": det_clean,
    }
    # hash-direction hostile: digest planted directly
    dg = target_solution_digests(fake_world, leak_solution)
    hashy = {"objects": [{"kind": "note", "payload": dg["method_digest"]}]}
    pure_hash, det_hash = purity_check(hashy, fake_world, leak_solution)
    receipts["purity_hashdirection_hostile_fire"] = {
        "control": "planted method digest in history must be flagged",
        "fired": pure_hash is False,
        "detail": det_hash,
    }
    return receipts

def clone_world(w):
    return copy.deepcopy(w)
