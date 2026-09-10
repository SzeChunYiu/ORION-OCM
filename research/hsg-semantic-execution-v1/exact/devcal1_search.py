"""DEV-CAL-1 search engine: arms, live proposal instrumentation, cost ledger.

Arms (frozen): ORACLE_HISTORY / RESET / SHUFFLED_HISTORY.  OCM_CONTINUED is
omitted-with-reason by the runner (no natural OCM developmental history for
these world families exists in the machinery; fabricating one is forbidden).

Search: candidates = methods (dag, root_slot) over the frozen vocabulary,
sizes 1..MAX_SIZE, smaller sizes first with frozen seeded jitter within a
size class (the proposal distribution).  Each candidate is applied (engine
implementation); value-producing candidates are verified by an INDEPENDENT
verifier (own code path recomputing bottom-up from the raw typed token).
Success = first independently verified match of the world goal.
work_to_first_verified_success = total charged ops up to and including that
verification.

History (ORACLE) = template objects abstracted from the SOURCE world's
solved class: the typed-operator DAG with NO concrete binding (no slot, no
values, no goal) plus its applicability contract.  Retrieval scans objects
(cost), adaptation instantiates slot bindings (cost); adapted instantiations
are PROMOTED to the front of the proposal stream.  In latent_different cells
the template is the wrong class: its products fail, the blind stream then
proceeds as RESET plus overhead.  The search NEVER consults hidden latent
ground truth: promotion is decided by execution + verification only.

Proposal distribution (frozen, recorded in every receipt):
  P_arm(m first) = (1-ALPHA)/N_pool + ALPHA/k  if m is an adapted product
                 = (1-ALPHA)/N_pool           otherwise
with ALPHA=1/2, k = number of adapted products, N_pool = full candidate pool.

All receipt fields under recorded_before_solution_discovery come from the
LIVE event log written as the search runs (RECONSTRUCTED=false).

Python 3.8+ stdlib only.
"""
from __future__ import annotations

import math
import random

from exact.devcal1_worlds import (
    OP_INPUT_CONTRACT, LATENT_SHAPES, dag_root, _all_dags_upto,
    cross_solves,
)
from exact.devcal1_certificates import (
    canonical_json, sha, history_bytes,
)

MAX_SIZE = 4
COST = {  # frozen op table (HDI-14: charged to BOTH arms identically)
    "expand_base": 3, "expand_per_node": 2,
    "verify_base": 2, "verify_per_node": 1,
    "retrieve_per_object": 4, "retrieve_per_probe": 3,
    "adapt_per_binding": 5,
}
ALPHA_PROMOTE = 0.5

_POOL = None  # frozen once: dags up to MAX_SIZE (connected only)

def pool_dags():
    global _POOL
    if _POOL is None:
        _POOL = _all_dags_upto(MAX_SIZE)
    return _POOL

# ---------------------------------------------------- execution (engine) ----
def apply_method(method, world_target):
    """Engine-side application (independent implementation #2).
    Returns (value|None, reject_reason)."""
    shape, slot = method["shape"], method["root_slot"]
    tok = world_target["inputs"][slot]
    root = dag_root(shape)
    if root is None:
        return None, "MALFORMED_DAG"
    vals = {}
    for j in range(len(shape)):  # children < j: forward pass is topological
        op, ch = shape[j]
        if not ch:
            if tok["type"] not in OP_INPUT_CONTRACT[op]:
                return None, "TYPE_VIOLATION"
            base = tok["value"]
        else:
            base = max(vals[c] for c in ch)
        if op == "VERIFY":
            vals[j] = base + 1
        elif op == "REFINE":
            vals[j] = base * 2
        elif op == "REDUCE":
            vals[j] = base + 2
        elif op == "DISTINGUISH":
            vals[j] = base + 3
        else:  # TRANSPORT
            vals[j] = base + 5
    return vals[root], None

def verify_independent(method, world_target):
    """INDEPENDENT verifier (implementation #3): own contract table and own
    semantics; recomputes bottom-up from the raw typed token.  True iff the
    method is type-clean AND its value equals the goal."""
    shape, slot = method["shape"], method["root_slot"]
    inputs, goal = world_target["inputs"], world_target["goal"]
    contract = {"DISTINGUISH": ("STRUCT",), "REFINE": ("ATTR", "STRUCT"),
                "REDUCE": ("REL",), "VERIFY": ("QUANT", "REL", "ATTR"),
                "TRANSPORT": ("REL", "ATTR", "STRUCT")}
    semantics = {"VERIFY": lambda b: b + 1, "REFINE": lambda b: b * 2,
                 "REDUCE": lambda b: b + 2, "DISTINGUISH": lambda b: b + 3,
                 "TRANSPORT": lambda b: b + 5}
    unconsumed = set(range(len(shape)))
    for _, ch in shape:
        unconsumed.difference_update(ch)
    if len(unconsumed) != 1:
        return False
    tok_type = inputs[slot]["type"]
    tok_value = inputs[slot]["value"]
    vals = [None] * len(shape)
    for j in range(len(shape)):
        op, ch = shape[j]
        if not ch:
            if tok_type not in contract[op]:
                return False
            base = tok_value
        else:
            for c in ch:
                if c >= j or vals[c] is None:
                    return False
            base = max(vals[c] for c in ch)
        vals[j] = semantics[op](base)
    return vals[unconsumed.pop()] == goal

# ------------------------------------------------------------- histories ----
def template_object(shape):
    """Reusable abstraction/transport object: typed-operator DAG, no binding,
    no values, no goal -- plus its applicability contract (the token types
    that satisfy EVERY leaf operator, since all leaves bind one token)."""
    leaf_ops = sorted({op for op, ch in shape if not ch})
    inter = set(OP_INPUT_CONTRACT[leaf_ops[0]])
    for op in leaf_ops[1:]:
        inter &= set(OP_INPUT_CONTRACT[op])
    return {
        "kind": "decomposition_template",
        "ops_dag": [[op, list(ch)] for op, ch in shape],
        "applicability_contract": {
            "leaf_operator_types": leaf_ops,
            "acceptable_token_types": sorted(inter),
            "size": len(shape),
        },
    }

def build_histories(world):
    """ORACLE history from the SOURCE class; SHUFFLED = same object kind and
    size, class randomly re-assigned across latent classes (seeded).  The
    shuffle null draws only from classes that do NOT functionally solve the
    target (cross-solve filtered), keeping the null blind-equivalent; if no
    such class exists the fallback is recorded, never silent."""
    src_shape = world["source"]["shape"]
    oracle = {"objects": [template_object(src_shape)]}
    rng = random.Random("DC1:shuffle:%s:%02d" % (world["cell"],
                                                 world["world_index"]))
    others = [s for s in LATENT_SHAPES if list(map(list, s)) !=
              list(map(list, src_shape))]
    safe = [s for s in others if not cross_solves(s, world["target"])]
    pool_hist = safe if safe else others
    shuffled = {"objects": [template_object(rng.choice(pool_hist))]}
    if not safe:
        shuffled["shuffle_fallback_cross_solving"] = True
    return oracle, shuffled

def source_acquisition_cost(world, seed=0):
    """Measured cost of EARNING the history: a blind search on the SOURCE
    world (same machinery); its first verified success exposes the template."""
    tgt_backup = world["target"]
    world["target"] = world["source"]
    try:
        rec = run_search("RESET", world, seed, want_receipt=False)
    finally:
        world["target"] = tgt_backup
    return rec

# --------------------------------------------------------------- search -----
def enumerate_methods(world):
    n_slots = len(world["target"]["inputs"])
    return [{"size": len(d), "shape": d, "root_slot": s}
            for d in pool_dags() for s in range(n_slots)]

def run_search(arm, world, seed, want_receipt=True):
    target = world["target"]
    rng = random.Random("DC1:stream:%s:%s:%02d:%d" % (
        arm, world["cell"], world["world_index"], seed))
    pool = enumerate_methods(world)
    for m in pool:
        m["jitter"] = rng.random()
    pool.sort(key=lambda m: (m["size"], m["jitter"],
                             canonical_json(m["shape"]), m["root_slot"]))
    n_pool = len(pool)

    ledger = {"acquisition": 0, "storage_bytes": 0, "retrieval": 0,
              "rejected_candidates": 0, "verification": 0, "adaptation": 0}
    history = None
    adapted = []
    if arm in ("ORACLE_HISTORY", "SHUFFLED_HISTORY"):
        oracle, shuffled = build_histories(world)
        history = oracle if arm == "ORACLE_HISTORY" else shuffled
        ledger["storage_bytes"] = len(history_bytes(history))
        for obj in history["objects"]:
            ledger["retrieval"] += COST["retrieve_per_object"]
            ledger["retrieval"] += COST["retrieve_per_probe"]
            have = {t["type"] for t in target["inputs"]}
            if set(obj["applicability_contract"]
                   ["acceptable_token_types"]) & have:
                shape = tuple((op, tuple(ch))
                              for op, ch in obj["ops_dag"])
                for slot in range(len(target["inputs"])):
                    ledger["adaptation"] += COST["adapt_per_binding"]
                    adapted.append({"size": len(shape), "shape": shape,
                                    "root_slot": slot, "promoted": True})

    adapted_digests = {canonical_json([list(map(list, m["shape"])),
                                       m["root_slot"]]) for m in adapted}
    blind = [m for m in pool if canonical_json(
        [list(map(list, m["shape"])), m["root_slot"]]) not in adapted_digests]
    stream = list(adapted) + blind
    n_adapted = len(adapted)

    def p_first(m):
        p = (1.0 - ALPHA_PROMOTE) / n_pool
        if n_adapted and canonical_json(
                [list(map(list, m["shape"])), m["root_slot"]]) \
                in adapted_digests:
            p += ALPHA_PROMOTE / n_adapted
        return p

    events = []
    nodes_expanded = 0
    work = 0
    # retrieval + adaptation are compute the history arm spends BEFORE and
    # during the search: they enter work_to_first_verified_success too
    # (never free promotion); storage_bytes stays a separate byte-dimension.
    work += ledger["retrieval"] + ledger["adaptation"]
    failed = 0
    rej_hist = {}
    verif_calls = 0
    entropy_sum = 0.0
    entropy_n = 0
    branch_sum = 0
    branch_n = 0
    m_star = None
    m_star_rank = None
    m_star_surprisal = None
    remaining = len(stream)

    for rank, cand in enumerate(stream, start=1):
        if m_star is not None:
            break
        p_draw = 1.0 / remaining
        events.append({"i": rank,
                       "cand_digest": sha(canonical_json(
                           [list(map(list, cand["shape"])),
                            cand["root_slot"]])),
                       "p_draw": p_draw,
                       "promoted": bool(cand.get("promoted"))})
        entropy_sum += -math.log2(p_draw)
        entropy_n += 1
        branch_sum += len(cand["shape"])
        branch_n += 1
        remaining -= 1
        nodes_expanded += 1
        work += COST["expand_base"] + COST["expand_per_node"] * cand["size"]
        val, reason = apply_method(cand, target)
        if val is None:
            failed += 1
            rej_hist[reason] = rej_hist.get(reason, 0) + 1
            ledger["rejected_candidates"] += 1
            continue
        verif_calls += 1
        work += COST["verify_base"] + COST["verify_per_node"] * cand["size"]
        ledger["verification"] += 1
        if verify_independent(cand, target):
            m_star = cand
            m_star_rank = rank
            m_star_surprisal = -math.log2(p_first(cand))
            events[-1]["success"] = True
        else:
            failed += 1
            rej_hist["VERIFY_FAIL"] = rej_hist.get("VERIFY_FAIL", 0) + 1
            ledger["rejected_candidates"] += 1

    if m_star is None:
        return {"status": "NO_VERIFIED_SUCCESS", "work": work,
                "nodes_expanded": nodes_expanded, "ledger": ledger,
                "m_star_digest": None}
    if not want_receipt:
        return {"status": "OK", "work": work, "ledger": ledger,
                "m_star_digest": sha(canonical_json(
                    [list(map(list, m_star["shape"])),
                     m_star["root_slot"]]))}

    receipt = {
        "status": "OK",
        "arm": arm,
        "world_id": "%s-%02d" % (world["cell"], world["world_index"]),
        "cell": world["cell"],
        "seed": seed,
        "_m_star_shape": list(map(list, m_star["shape"])),
        "_m_star_slot": m_star["root_slot"],
        "m_star_digest": sha(canonical_json([list(map(list, m_star["shape"])),
                                             m_star["root_slot"]])),
        "m_star_identity_class": "typed_operator_dag_binding",
        "m_star_derived_from_history_template": bool(m_star.get("promoted")),
        "recorded_before_solution_discovery": {
            "RECONSTRUCTED": False,
            "event_log_digest": sha(canonical_json(events)),
            "n_events_logged": len(events),
            "eventual_success_rank": m_star_rank,
            "proposal_surprisal_bits": round(m_star_surprisal, 6),
            "proposal_entropy_bits": round(entropy_sum / entropy_n, 6)
            if entropy_n else None,
            "branch_factor": round(branch_sum / branch_n, 6) if branch_n
            else None,
            "nodes_expanded": nodes_expanded,
            "failed_candidates": failed,
            "rejection_reason_histogram": rej_hist,
            "decomposition_structure_digest": sha(canonical_json(
                [list(map(list, m_star["shape"])), m_star["root_slot"]])),
            "information_queries": {"count": 0, "cost": 0,
                                    "note": "no external hints; identical "
                                            "evidence stream across arms"},
            "retrieval_attempts": len(history["objects"]) if history else 0,
            "successful_mappings": 1 if m_star.get("promoted") else 0,
            "representation_refinements": {"count": 0, "digests": []},
            "verification_calls": verif_calls,
            "target_evidence_consumed": {
                "bytes": len(canonical_json(target)), "queries": 1},
            "work_to_first_verified_success": work,
        },
        "cost_ledger": ledger,
        "ecology_axes": {
            "rho": float(world["ecology_axes"]["rho"]),
            "sigma": float(world["ecology_axes"]["sigma"]),
            "d": world["ecology_axes"]["d"],
            "delta": world["ecology_axes"]["delta"],
        },
    }
    receipt["total_burden_incl_acquisition"] = work + ledger["acquisition"]
    return receipt
