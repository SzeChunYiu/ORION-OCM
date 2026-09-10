"""G6.1 remainder parents: 1-parameter surrogate, random ES, G&T repair, authored plant.

v2 already compared GF(2) system-id, 2-factor ANOVA, permutation GA, GenProg
mutate, and a trained syndrome table. This module does not retrain that selector
and does not invent AutoML/BO.
"""
from __future__ import annotations

import importlib
import importlib.util
import itertools
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

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

# Authored observation map from research/g6-intervention-lab-v1/world.py
# (three overlapping XOR windows). Human-designed repair is this plant, charged
# as prior — not recovered from hidden.stuck.
AUTHORED_WINDOWS: tuple[tuple[int, int], ...] = ((0, 1), (2, 3), (4, 5))


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
            "grid_search_is_not_bo": True,
        }
    return {
        "status": "LIBRARY_PRESENT_NOT_RUN",
        "present": present,
        "tried": list(BO_LIBRARIES),
        "missing": missing,
        "invented": False,
        "grid_search_is_not_bo": True,
        "note": "A BO package exists in this environment; this capsule still does not invent a surrogate optimizer.",
    }


def load_v2_parents():
    """Import v2 ATMS helpers by path so v3 `parents` is not shadowed."""
    v2 = Path(__file__).resolve().parents[1] / "g6-intervention-parents-v2" / "parents.py"
    name = "g6_intervention_parents_v2_parents"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, v2)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load v2 parents {v2}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


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


# ---------------------------------------------------------------------------
# 1-parameter structured surrogate (not v2's 2-factor ANOVA; θ-grid is not BO)
# ---------------------------------------------------------------------------

def fit_one_parameter_surrogate(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    """First-order main-effect design; one integer θ = how many top modules to front-load.

    Structure M[j][i] is the empirical P(module i failed | syndrome bit j = 1).
    The sole fitted parameter is θ ∈ {0, …, N}, chosen by exhaustive integer
    enumeration on unlabeled training cost. That grid is labeled not-BO.
    """
    n_modules = _n(Lab)
    width = _syndrome_len(transcripts)
    failed, syndromes = _rows(transcripts, n_modules)
    design: list[list[float]] = []
    for j in range(width):
        scores = []
        for i in range(n_modules):
            on = [f[i] for f, s in zip(failed, syndromes, strict=True) if s[j] == 1]
            scores.append((sum(on) / len(on)) if on else 0.0)
        design.append(scores)

    def order_for(theta: int, syndrome: tuple[int, ...]) -> list[int]:
        scores = [
            sum(syndrome[j] * design[j][i] for j in range(width))
            for i in range(n_modules)
        ]
        ranked = sorted(range(n_modules), key=lambda i: (-scores[i], i))
        first = ranked[:theta]
        return first + [i for i in range(n_modules) if i not in first]

    best_theta = 0
    best_cost: int | None = None
    grid = []
    for theta in range(0, n_modules + 1):
        cost = 0
        for row, syn in zip(transcripts, syndromes, strict=True):
            cost += _perm_cost(order_for(theta, syn), [row], n_modules)
        grid.append({"theta": theta, "train_cost": cost, "not_bo": True})
        if best_cost is None or cost < best_cost or (cost == best_cost and theta < best_theta):
            best_cost = cost
            best_theta = theta
    return {
        "kind": "one_parameter_structured_surrogate",
        "theta": best_theta,
        "n_parameters": 1,
        "design": [[round(x, 6) for x in row] for row in design],
        "train_cost": best_cost,
        "theta_fit": "exhaustive integer grid over {0..N}; labeled not-BO / not-AutoML",
        "grid": grid,
    }


def order_one_parameter_surrogate(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[int]:
    width = len(model["design"])
    scores = [
        sum(syndrome[j] * model["design"][j][i] for j in range(width))
        for i in range(n_modules)
    ]
    ranked = sorted(range(n_modules), key=lambda i: (-scores[i], i))
    first = ranked[: int(model["theta"])]
    return first + [i for i in range(n_modules) if i not in first]


# ---------------------------------------------------------------------------
# Random evolutionary search: (1+λ) swap-mutation ES, no crossover
# ---------------------------------------------------------------------------

def _swap_mutate(perm: list[int], rng: random.Random) -> list[int]:
    child = list(perm)
    n = len(child)
    for _ in range(rng.randint(1, 3)):
        a, b = rng.sample(range(n), 2)
        child[a], child[b] = child[b], child[a]
    return child


def fit_random_evolutionary(transcripts: list[dict[str, Any]], Lab, rng: random.Random) -> dict[str, Any]:
    n_modules = _n(Lab)
    lambd = 8
    gens = 10
    parent = rng.sample(range(n_modules), n_modules)
    parent_cost = _perm_cost(parent, transcripts, n_modules)
    history = [{"gen": -1, "best_cost": parent_cost, "kind": "random_init"}]
    for gen in range(gens):
        candidates = [(parent_cost, parent)]
        for _ in range(lambd):
            child = _swap_mutate(parent, rng)
            candidates.append((_perm_cost(child, transcripts, n_modules), child))
        candidates.sort(key=lambda kv: (kv[0], kv[1]))
        parent_cost, parent = candidates[0]
        history.append({"gen": gen, "best_cost": parent_cost, "lambda": lambd})
    return {
        "kind": "random_evolutionary",
        "perm": list(parent),
        "train_cost": parent_cost,
        "generations": gens,
        "lambda": lambd,
        "crossover": False,
        "history": history,
    }


def order_random_evolutionary(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[int]:
    del syndrome
    return list(model["perm"]) + [i for i in range(n_modules) if i not in model["perm"]]


# ---------------------------------------------------------------------------
# Generate-and-test program repair: enumerate a finite patch set (power set)
# ---------------------------------------------------------------------------

def _finite_patches(n_modules: int) -> list[tuple[int, ...]]:
    patches: list[tuple[int, ...]] = []
    for k in range(0, n_modules + 1):
        patches.extend(itertools.combinations(range(n_modules), k))
    return patches


def fit_generate_and_test(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    n_modules = _n(Lab)
    patches = _finite_patches(n_modules)
    freq: Counter[tuple[int, ...]] = Counter()
    by_syn: dict[tuple[int, ...], Counter[tuple[int, ...]]] = defaultdict(Counter)
    for row in transcripts:
        adopted = tuple(sorted(row.get("adopted") or []))
        freq[adopted] += 1
        by_syn[tuple(row["syndrome"])][adopted] += 1
    return {
        "kind": "generate_and_test_program_repair",
        "n_patches": len(patches),
        "max_size": n_modules,
        "finite": True,
        "freq": {str(list(k)): v for k, v in freq.items()},
        "by_syndrome": {
            str(list(syn)): {str(list(p)): c for p, c in counts.items()}
            for syn, counts in by_syn.items()
        },
    }


def _ordered_patches(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[tuple[int, ...]]:
    syn_key = str(list(syndrome))
    syn_freq = model.get("by_syndrome", {}).get(syn_key, {})
    glob = model.get("freq", {})

    def key(patch: tuple[int, ...]) -> tuple:
        label = str(list(patch))
        return (len(patch), -int(syn_freq.get(label, 0)), -int(glob.get(label, 0)), patch)

    return sorted(_finite_patches(n_modules), key=key)


def run_generate_and_test(Lab, incident, model: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Enumerate the finite catalogue; test each patch on a shadow; stop at first repair."""
    del rng
    n_modules = _n(Lab)
    target = fresh_incident(Lab, incident)
    syn = target.hidden.syndrome()
    patches = _ordered_patches(model, syn, n_modules)
    total_cost = 0
    n_tested = 0
    probes_all: list[dict[str, Any]] = []
    interventions_all: list[dict[str, Any]] = []
    chosen: tuple[int, ...] | None = None
    failed_final: list[int] = []
    quality = 0
    for patch in patches:
        shadow = Lab.World(target.hidden)
        failed: list[int] = []
        for index in patch:
            obs = shadow.probe(index)
            probes_all.append({**obs, "phase": "gat_test"})
            total_cost += obs["cost"]
            if not obs["ok"]:
                rec = shadow.intervene(index)
                interventions_all.append({**rec, "phase": "gat_test"})
                total_cost += rec["cost"]
                failed.append(index)
        n_tested += 1
        if all(shadow.modules):
            chosen = patch
            failed_final = failed
            quality = int(all(shadow.restart_clone().modules))
            break
    target.probes.extend(probes_all)
    target.interventions.extend(interventions_all)
    if chosen is None:
        leftover = fail_closed_repair(Lab, target, list(range(n_modules)))
        leftover["cost"] += total_cost
        leftover["policy"] = "generate_and_test_program_repair"
        leftover["n_tested"] = n_tested
        leftover["n_patches"] = len(patches)
        leftover["catalogue_exhausted"] = True
        leftover["patch"] = []
        return leftover
    target.adopted = tuple(failed_final)
    truth = Lab.independent_truth(target.hidden)
    identified = frozenset(failed_final) == truth
    return {
        "quality": quality,
        "identified": int(identified),
        "cost": total_cost,
        "kappa": len(truth),
        "omega": (1.0 if identified else 0.0) / max(1, len(target.probes)),
        "chi": len(patches),
        "n_probes": len(target.probes),
        "n_replaced": len(failed_final),
        "order": list(chosen),
        "adopted": list(failed_final),
        "policy": "generate_and_test_program_repair",
        "patch": list(chosen),
        "n_tested": n_tested,
        "n_patches": len(patches),
        "catalogue_exhausted": False,
    }


# ---------------------------------------------------------------------------
# Human-designed repair = authored plant windows, charged as prior
# ---------------------------------------------------------------------------

def authored_prior_cost(Lab) -> int:
    """One-time design capital: 3 authored windows over the N-module plant."""
    return len(AUTHORED_WINDOWS) * _n(Lab) * Lab.REPLACE_COST


def fit_human_designed(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    for row in transcripts:
        assert "stuck" not in row
        assert "hidden" not in row
    return {
        "kind": "human_designed_authored_plant",
        "windows": [list(w) for w in AUTHORED_WINDOWS],
        "source": "research/g6-intervention-lab-v1/world.py",
        "prior_cost": authored_prior_cost(Lab),
        "charged_as_prior": True,
        "n_parameters_fit": 0,
    }


def order_human_designed(model: dict[str, Any], syndrome: tuple[int, ...], n_modules: int) -> list[int]:
    first: list[int] = []
    for bit, window in zip(syndrome, model["windows"], strict=True):
        if bit:
            for idx in window:
                if idx not in first:
                    first.append(idx)
    return first + [i for i in range(n_modules) if i not in first]


def run_ordered(Lab, incident, order: list[int], policy: str) -> dict[str, Any]:
    result = fail_closed_repair(Lab, incident, order)
    result["policy"] = policy
    return result


def run_parent(name: str, Lab, incident, model: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    target = fresh_incident(Lab, incident)
    n_modules = _n(Lab)
    syn = target.hidden.syndrome()
    if name == "generate_and_test_program_repair":
        return run_generate_and_test(Lab, target, model, rng)
    if name == "atms_change_impact":
        v2 = load_v2_parents()
        return v2.run_parent("atms_change_impact", Lab, target, model, rng)
    orders = {
        "one_parameter_structured_surrogate": order_one_parameter_surrogate,
        "random_evolutionary": order_random_evolutionary,
        "human_designed_repair": order_human_designed,
    }
    order = orders[name](model, syn, n_modules)
    return run_ordered(Lab, target, order, name)


def fit_atms_v2(transcripts: list[dict[str, Any]], Lab) -> dict[str, Any]:
    return load_v2_parents().fit_atms(transcripts, Lab)
