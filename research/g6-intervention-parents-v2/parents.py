"""Matched G6.1 research parents on the frozen synthetic plant.

Implemented (tiny, stdlib): system identification, structured surrogate,
ATMS/change-impact via production ``impact_cone``, evolutionary search,
program repair.

AutoML/BO is not invented: missing libraries stay ``CANNOT_CHECK_NO_BO_LIBRARY``.
"""
from __future__ import annotations

import importlib
import itertools
import random
from collections import defaultdict
from typing import Any

from ocm.kso.nogoods import NogoodSet
from ocm.kso.revocation import impact_cone
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace

from plant import fail_closed_repair, failed_from_probes, fresh_incident

BO_LIBRARIES = (
    "optuna",
    "skopt",
    "bayes_opt",
    "hyperopt",
    "ax",
    "gpytorch",
    "botorch",
    "emukit",
    "dragonfly",
    "hebo",
)


def automl_bo_status() -> dict[str, Any]:
    """Refuse to stand in a GP/EI loop. No package ⇒ cannot check AutoML/BO."""
    present = []
    missing = []
    for name in BO_LIBRARIES:
        try:
            importlib.import_module(name)
        except Exception:
            missing.append(name)
        else:
            present.append(name)
    if not present:
        return {
            "status": "CANNOT_CHECK_NO_BO_LIBRARY",
            "present": present,
            "tried": list(BO_LIBRARIES),
            "missing": missing,
            "invented": False,
        }
    return {
        "status": "LIBRARY_PRESENT_NOT_RUN",
        "present": present,
        "tried": list(BO_LIBRARIES),
        "missing": missing,
        "invented": False,
        "note": "A BO package exists in this environment; this capsule still does not invent a surrogate optimizer.",
    }


def _n(Lab) -> int:
    return Lab.N_MODULES


def _syndrome_len(transcripts: list[dict[str, Any]]) -> int:
    if not transcripts:
        return 3
    return len(transcripts[0]["syndrome"])


def _rows(transcripts: list[dict[str, Any]], n_modules: int):
    failed = [failed_from_probes(t["probes"], n_modules) for t in transcripts]
    syndromes = [tuple(t["syndrome"]) for t in transcripts]
    return failed, syndromes


# ---------------------------------------------------------------------------
# System identification: GF(2) observation map  s = A f, then min-weight invert
# ---------------------------------------------------------------------------

def gf2_dot(a: tuple[int, ...], x: tuple[int, ...]) -> int:
    return sum(u & v for u, v in zip(a, x, strict=True)) & 1


def gf2_fit_row(failed: list[tuple[int, ...]], bits: list[int], n_modules: int) -> tuple[int, ...]:
    """Min-Hamming-error, then min-weight, linear functional over GF(2)."""
    best: tuple[int, ...] | None = None
    best_key = None
    for bits_a in itertools.product((0, 1), repeat=n_modules):
        a = tuple(bits_a)
        err = sum(gf2_dot(a, f) ^ y for f, y in zip(failed, bits, strict=True))
        wt = sum(a)
        key = (err, wt, a)
        if best_key is None or key < best_key:
            best_key = key
            best = a
    assert best is not None
    return best


def identify_matrix(transcripts: list[dict[str, Any]], n_modules: int) -> list[tuple[int, ...]]:
    failed, syndromes = _rows(transcripts, n_modules)
    width = _syndrome_len(transcripts)
    return [gf2_fit_row(failed, [s[j] for s in syndromes], n_modules) for j in range(width)]


def invert_minweight(matrix: list[tuple[int, ...]], syndrome: tuple[int, ...], n_modules: int) -> tuple[int, ...]:
    target = tuple(syndrome)
    best_f = tuple(0 for _ in range(n_modules))
    best_key = None
    for bits in itertools.product((0, 1), repeat=n_modules):
        f = tuple(bits)
        pred = tuple(gf2_dot(row, f) for row in matrix)
        err = sum(p ^ t for p, t in zip(pred, target, strict=True))
        key = (err, sum(f), f)
        if best_key is None or key < best_key:
            best_key = key
            best_f = f
    return best_f


def fit_system_id(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    matrix = identify_matrix(transcripts, _n(Lab))
    return {"kind": "system_id", "A": [list(row) for row in matrix]}


def order_system_id(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[int]:
    f = invert_minweight([tuple(row) for row in model["A"]], syndrome, n_modules)
    first = [i for i, bit in enumerate(f) if bit]
    rest = [i for i in range(n_modules) if i not in first]
    return first + rest


# ---------------------------------------------------------------------------
# Structured surrogate: per-syndrome-bit main effects, keep 2-factor terms
# ---------------------------------------------------------------------------

def fit_structured_surrogate(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    n_modules = _n(Lab)
    width = _syndrome_len(transcripts)
    failed, syndromes = _rows(transcripts, n_modules)
    factors = []
    effects = []
    for j in range(width):
        scores = []
        for i in range(n_modules):
            on = [f[i] for f, s in zip(failed, syndromes) if s[j] == 1]
            off = [f[i] for f, s in zip(failed, syndromes) if s[j] == 0]
            p_on = (sum(on) / len(on)) if on else 0.0
            p_off = (sum(off) / len(off)) if off else 0.0
            scores.append(p_on - p_off)
        ranked = sorted(range(n_modules), key=lambda i: (-abs(scores[i]), i))
        factors.append(ranked[:2])
        effects.append([round(x, 6) for x in scores])
    return {"kind": "structured_surrogate", "factors": factors, "main_effects": effects}


def order_structured_surrogate(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[int]:
    first: list[int] = []
    for bit, factor in zip(syndrome, model["factors"]):
        if bit:
            for idx in factor:
                if idx not in first:
                    first.append(idx)
    return first + [i for i in range(n_modules) if i not in first]


# ---------------------------------------------------------------------------
# ATMS / change-impact: learned DEPENDENCE graph + production impact_cone
# ---------------------------------------------------------------------------

def _association_graph(transcripts: list[dict[str, Any]], n_modules: int) -> list[list[int]]:
    width = _syndrome_len(transcripts)
    failed, syndromes = _rows(transcripts, n_modules)
    graph = []
    for j in range(width):
        scores = []
        for i in range(n_modules):
            on = [f[i] for f, s in zip(failed, syndromes) if s[j] == 1]
            p_on = (sum(on) / len(on)) if on else 0.0
            scores.append(p_on)
        ranked = sorted(range(n_modules), key=lambda i: (-scores[i], i))
        keep = [i for i in ranked[:2] if scores[i] > 0]
        if not keep:
            keep = ranked[:2]
        graph.append(keep)
    return graph


def build_impact_space(graph: list[list[int]], n_modules: int) -> KnowledgeSpace:
    """Symptom windows depend on modules; system depends on windows.

    ``impact_cone`` of an observed window therefore contains candidate modules
    (change-impact parent, KS-T09). Nogoods of probed-healthy modules are
    tracked separately with ``NogoodSet``.
    """
    width = len(graph)
    atoms = (
        tuple(Atom(f"m{i}", "claim") for i in range(n_modules))
        + tuple(Atom(f"w{j}", "observation") for j in range(width))
        + (Atom("system", "goal"),)
    )
    edges = []
    eid = 0
    for j, modules in enumerate(graph):
        for i in modules:
            edges.append(
                Hyperedge(
                    f"e{eid}",
                    tails=(f"w{j}",),
                    heads=(f"m{i}",),
                    relation_type="DEPENDENCE",
                )
            )
            eid += 1
        edges.append(
            Hyperedge(
                f"e{eid}",
                tails=(f"w{j}",),
                heads=("system",),
                relation_type="DEPENDENCE",
            )
        )
        eid += 1
    return KnowledgeSpace(atoms, tuple(edges))


def fit_atms(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    n_modules = _n(Lab)
    graph = _association_graph(transcripts, n_modules)
    ks = build_impact_space(graph, n_modules)
    return {"kind": "atms_change_impact", "graph": graph, "ks": ks, "n_edges": len(ks.hyperedges)}


def order_atms(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[int]:
    changed = [f"w{j}" for j, bit in enumerate(syndrome) if bit]
    if not changed:
        return list(range(n_modules))
    cone = impact_cone(model["ks"], changed)
    modules = sorted(int(atom[1:]) for atom in cone if atom.startswith("m") and atom[1:].isdigit())
    return modules + [i for i in range(n_modules) if i not in modules]


def atms_nogoods_from_probes(probes: list[dict[str, Any]]) -> NogoodSet:
    """Probed-ok modules cannot jointly be a diagnosis assumption."""
    ng = NogoodSet()
    for probe in probes:
        if probe["ok"]:
            ng = ng.add({probe["index"]})
    return ng


# ---------------------------------------------------------------------------
# Evolutionary search: permutation GA on training transcripts (offline)
# ---------------------------------------------------------------------------

def _perm_cost(perm: list[int], transcripts: list[dict[str, Any]], n_modules: int) -> int:
    total = 0
    for row in transcripts:
        failed = {i for i, bit in enumerate(failed_from_probes(row["probes"], n_modules)) if bit}
        seen: set[int] = set()
        cost = 0
        for index in perm:
            cost += 1
            seen.add(index)
            if index in failed:
                cost += 4
            if failed <= seen:
                break
        total += cost
    return total


def _ox(parent_a: list[int], parent_b: list[int], rng: random.Random) -> list[int]:
    n = len(parent_a)
    i, j = sorted(rng.sample(range(n), 2))
    child = [None] * n
    child[i:j] = parent_a[i:j]
    fill = [x for x in parent_b if x not in child]
    k = 0
    for idx in range(n):
        if child[idx] is None:
            child[idx] = fill[k]
            k += 1
    return [int(x) for x in child]


def fit_evolutionary(transcripts: list[dict[str, Any]], Lab, rng: random.Random) -> dict[str, Any]:
    n_modules = _n(Lab)
    pop_n = 12
    gens = 8
    pop = [rng.sample(range(n_modules), n_modules) for _ in range(pop_n)]
    history = []
    for gen in range(gens):
        scored = sorted(pop, key=lambda p: _perm_cost(p, transcripts, n_modules))
        elite = scored[:4]
        history.append({"gen": gen, "best_cost": _perm_cost(elite[0], transcripts, n_modules)})
        nxt = [list(e) for e in elite]
        while len(nxt) < pop_n:
            child = _ox(rng.choice(elite), rng.choice(elite), rng)
            if rng.random() < 0.4:
                a, b = rng.sample(range(n_modules), 2)
                child[a], child[b] = child[b], child[a]
            nxt.append(child)
        pop = nxt
    best = min(pop, key=lambda p: _perm_cost(p, transcripts, n_modules))
    return {
        "kind": "evolutionary",
        "perm": best,
        "train_cost": _perm_cost(best, transcripts, n_modules),
        "generations": gens,
        "history": history,
    }


def order_evolutionary(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[int]:
    del syndrome
    return list(model["perm"]) + [i for i in range(n_modules) if i not in model["perm"]]


# ---------------------------------------------------------------------------
# Program repair: GenProg-style mutate of replace-patches from traces
# ---------------------------------------------------------------------------

def _mutate_patch(patch: tuple[int, ...], rng: random.Random, n_modules: int) -> tuple[int, ...]:
    body = list(patch)
    op = rng.choice(("insert", "delete", "swap"))
    if op == "insert" or not body:
        cand = [i for i in range(n_modules) if i not in body]
        if cand:
            body.append(rng.choice(cand))
    elif op == "delete" and body:
        body.pop(rng.randrange(len(body)))
    elif len(body) >= 2:
        i, j = rng.sample(range(len(body)), 2)
        body[i], body[j] = body[j], body[i]
    return tuple(dict.fromkeys(body))


def fit_program_repair(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    seeds: list[tuple[int, ...]] = []
    by_syn: dict[tuple[int, ...], list[tuple[int, ...]]] = defaultdict(list)
    for row in transcripts:
        adopted = tuple(row.get("adopted") or [])
        syn = tuple(row["syndrome"])
        seeds.append(adopted)
        by_syn[syn].append(adopted)
    return {"kind": "program_repair", "seeds": seeds[:24], "by_syndrome": {str(k): v for k, v in by_syn.items()}}


def run_program_repair(Lab, incident, model: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Generate a patch from traces, mutate, score on this incident's shadow, then fail-closed."""
    n_modules = _n(Lab)
    syn = incident.hidden.syndrome()
    pool = list(model["seeds"])
    pool.extend(model["by_syndrome"].get(str(syn), []))
    if not pool:
        pool = [()]
    mutants = list(dict.fromkeys(pool))
    for _ in range(8):
        mutants.append(_mutate_patch(rng.choice(mutants) if mutants else (), rng, n_modules))
    # Rank patches by how many training seeds they resemble; actual fitness is
    # paid on this incident via fail-closed after applying the chosen order.
    # Prefer shorter patches that cover historically adopted modules for this syndrome.
    hist = set()
    for patch in model["by_syndrome"].get(str(syn), model["seeds"]):
        hist.update(patch)

    def key(patch: tuple[int, ...]) -> tuple:
        hit = sum(1 for i in patch if i in hist)
        extra = sum(1 for i in patch if i not in hist)
        return (-hit, extra, len(patch), patch)

    chosen = min(mutants, key=key)
    order = list(chosen) + [i for i in range(n_modules) if i not in chosen]
    result = fail_closed_repair(Lab, incident, order)
    result["policy"] = "program_repair"
    result["patch"] = list(chosen)
    result["n_mutants"] = len(mutants)
    return result


# ---------------------------------------------------------------------------
# Learned selector (v1 OCM arm) — comparator, not a new parent
# ---------------------------------------------------------------------------

def fit_learned_selector(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    del Lab
    return _learn_selector(transcripts)


def _learn_selector(transcripts: list[dict[str, Any]]) -> dict[str, Any]:
    table: dict[str, list[int]] = {}
    for row in transcripts:
        key = str(tuple(row["syndrome"]))
        table.setdefault(key, [])
        table[key].extend(row.get("adopted") or [])
    return {
        "kind": "learned_selector",
        "syndrome_to_modules": {k: sorted(set(v)) for k, v in table.items()},
    }


def order_learned_selector(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[int]:
    predicted = list(model["syndrome_to_modules"].get(str(syndrome), []))
    return predicted + [i for i in range(n_modules) if i not in predicted]


def run_ordered(Lab, incident, order: list[int], policy: str) -> dict[str, Any]:
    result = fail_closed_repair(Lab, incident, order)
    result["policy"] = policy
    return result


def run_parent(name: str, Lab, incident, model: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    target = fresh_incident(Lab, incident)
    n_modules = _n(Lab)
    syn = target.hidden.syndrome()
    if name == "program_repair":
        return run_program_repair(Lab, target, model, rng)
    orders = {
        "learned_selector": order_learned_selector,
        "system_id": order_system_id,
        "structured_surrogate": order_structured_surrogate,
        "atms_change_impact": order_atms,
        "evolutionary": order_evolutionary,
    }
    order = orders[name](model, syn, n_modules)
    if name == "atms_change_impact":
        # First probes also register ATMS nogoods for healthy modules.
        result = run_ordered(Lab, target, order, name)
        result["nogoods"] = atms_nogoods_from_probes(target.probes).as_dict()
        return result
    return run_ordered(Lab, target, order, name)
