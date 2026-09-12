from __future__ import annotations

"""Seed-dependent successor to the exposed deterministic K4 palette scaffold.

V1 (`gmi_k4_search.py`) is preserved as DEVELOPMENT-EXPOSED: its deterministic outcome was
inspected while engineering the harness, so it must not be called protected evidence.

V2 keeps the already-frozen semantic class and candidate palette but generates a fresh quantitative
world inside that class from the protected seed. The seed affects only nuisance/phase coordinates
that the family prediction claims to survive (reuse, volatility, dependence density, heterogeneity,
rank fraction, error correlation, checker ratio, goal reuse, jointness/manifold fraction, etc.). It
does not read `name_key` and it does not use the target property vector in ranking.

This still does NOT close IG-5 primitive-selection independence: the palette is same-authored.
"""

import hashlib
import json
import random

import gmi_k4_search as v1


def _u(seed: int, tag: str, lo: float, hi: float) -> float:
    h = hashlib.sha256(f"{seed}:{tag}".encode()).digest()
    x = int.from_bytes(h[:8], "big") / float(2**64 - 1)
    return lo + (hi - lo) * x


def world_profile(seed: int, task: str, scale: int) -> dict:
    return {
        "reuse_multiplier": _u(seed, task + ":reuse", 0.70, 1.35),
        "volatility": _u(seed, task + ":vol", 0.55, 1.00),
        "dependence_density": _u(seed, task + ":dep", 0.15, 0.90),
        "heterogeneity": _u(seed, task + ":het", 0.55, 1.00),
        "router_noise": _u(seed, task + ":router", 0.00, 0.16),
        "rank_fraction": _u(seed, task + ":rank", 0.05, 0.35),
        "error_correlation": _u(seed, task + ":corr", 0.00, 0.45),
        "checker_ratio": _u(seed, task + ":check", 0.03, 0.30),
        "goal_reuse": _u(seed, task + ":goal", 2.0, 12.0),
        "model_error": _u(seed, task + ":modelerr", 0.00, 0.08),
        "jointness": _u(seed, task + ":joint", 0.55, 1.00),
        "manifold_fraction": _u(seed, task + ":manifold", 0.08, 0.35),
        "sequence_dependency": _u(seed, task + ":seq", 0.55, 1.00),
        "symmetry_break": _u(seed, task + ":symbreak", 0.00, 0.10),
        "scale": scale,
    }


def _semantic_adjust(base: float, form, task: str, twin: bool, p: dict) -> float:
    c = set(form.caps)
    s = base
    if twin:
        # Twins destroy the property that gave the predicted mechanism its niche. The base V1 semantics
        # already encode the structural twin; these terms only make the fresh quantitative cell nondegenerate.
        if task in ("linear", "basis") and "exact_lookup" in c: s += 0.02 * p["volatility"]
        if task in ("content", "sparse_content") and "content_route" in c: s -= 0.04 * p["dependence_density"]
        if task == "modes" and "mode_partition" in c: s -= 0.08 * p["heterogeneity"]
        if task == "lowrank" and "low_rank_revision" in c: s -= 0.10 * (1.0 - p["rank_fraction"])
        if task == "ensemble" and "variance_reduce" in c: s -= 0.08 * (1.0 - p["error_correlation"])
        if task == "model_based" and "world_model" in c: s -= 0.03 * p["goal_reuse"] / 12.0
        if task == "latent_gen" and "latent_compress" in c: s -= 0.10 * (1.0 - p["manifold_fraction"])
        return max(0.0, min(1.0, s))

    # Positive worlds vary *within* the declared niche. These corrections are small enough not to invent a
    # completely different obligation but can expose a phase prediction that was too absolute.
    if task == "content" and "dense_pair" in c: s -= 0.025 * (1.0 - p["dependence_density"])
    if task == "sparse_content" and "sparse_pair" in c: s -= 0.03 * max(0.0, p["dependence_density"] - 0.55)
    if task == "modes" and "mode_partition" in c: s -= p["router_noise"]
    if task == "ensemble" and "variance_reduce" in c: s -= 0.04 * p["error_correlation"]
    if task == "verify" and "checker" in c: s -= 0.02 * max(0.0, p["checker_ratio"] - 0.20)
    if task == "model_based" and "world_model" in c: s -= 0.5 * p["model_error"]
    if task == "ordered_gen" and "ordered_factorization" in c: s -= 0.03 * p["jointness"]
    if task == "joint_gen" and "iterative_denoise" in c: s -= 0.03 * (1.0 - p["jointness"])
    if task == "latent_gen" and "latent_compress" in c: s -= 0.04 * max(0.0, p["manifold_fraction"] - 0.25)
    if task == "equivariant" and "equivariant" in c: s -= 0.4 * p["symmetry_break"]
    return max(0.0, min(1.0, s))


def _lifecycle_adjust(cost: dict, form, task: str, p: dict) -> dict:
    c = set(form.caps)
    out = dict(cost)
    reuse = p["reuse_multiplier"]

    # Reuse amortizes development/description relative to serving.
    out["development_compute"] /= reuse
    out["description_compiler_burden"] /= max(0.8, reuse)

    if "exact_lookup" in c:
        out["update_retraining"] *= max(0.35, 1.15 - 0.8 * p["volatility"])
        out["state_storage"] *= 0.9 + 0.3 * p["volatility"]
    if "content_route" in c:
        out["serve_compute_latency"] *= 0.75 + 0.55 * p["dependence_density"]
        out["communication"] *= 0.75 + 0.70 * p["dependence_density"]
    if "mode_partition" in c:
        out["development_compute"] *= 0.80 + 0.45 * p["heterogeneity"]
        out["communication"] *= 1.0 + 2.0 * p["router_noise"]
    if "low_rank_revision" in c:
        f = max(0.08, min(1.0, p["rank_fraction"] * 3.0))
        out["state_storage"] *= f
        out["update_retraining"] *= f
    if "variance_reduce" in c:
        out["serve_compute_latency"] *= 1.0 + 0.5 * p["error_correlation"]
    if "checker" in c:
        out["verification"] *= p["checker_ratio"]
    if "world_model" in c:
        out["development_compute"] /= max(1.0, p["goal_reuse"] / 2.0)
        out["serve_compute_latency"] *= 1.0 + 2.0 * p["model_error"]
    if "direct_policy" in c:
        out["development_compute"] *= 1.0 + 0.12 * max(0.0, p["goal_reuse"] - 2.0)
    if "ordered_factorization" in c:
        out["serve_compute_latency"] *= 0.85 + 0.45 * p["jointness"]
    if "iterative_denoise" in c:
        out["serve_compute_latency"] *= 1.15 - 0.25 * p["jointness"]
    if "latent_compress" in c:
        out["state_storage"] *= 0.55 + p["manifold_fraction"]
        out["serve_compute_latency"] *= 0.75 + p["manifold_fraction"]
    if "equivariant" in c:
        out["state_storage"] *= 1.0 + 3.0 * p["symmetry_break"]
    if "sequence_state" in c:
        out["state_storage"] *= 0.85 + 0.35 * p["sequence_dependency"]
    return out


def run_cell(family: str, grammar: str, cell: str, *, freeze: dict, seed: int, budget: int = 1_000_000):
    fr = dict(freeze); fr.pop("name_key", None)
    if family not in fr.get("families", {}):
        return {"verdict": "INCONCLUSIVE_GRAMMAR", "reason": "unknown family id", "family": family, "grammar": grammar, "cell": cell}
    spec = fr["families"][family]
    task = v1.OBLIGATION_KIND.get(spec["obligation_class"])
    if task is None:
        return {"verdict": "INCONCLUSIVE_GRAMMAR", "reason": "no obligation generator", "family": family, "grammar": grammar, "cell": cell}
    scale = int(cell[1:])
    profile = world_profile(seed, task, scale)

    old_sem = v1.semantic_score
    old_life = v1.lifecycle
    def sem(form, task_, scale_, twin=False):
        return _semantic_adjust(old_sem(form, task_, scale_, twin), form, task_, twin, profile)
    def life(form, grammar_, scale_, knob):
        return _lifecycle_adjust(old_life(form, grammar_, scale_, knob), form, task, profile)
    try:
        v1.semantic_score = sem
        v1.lifecycle = life
        out = v1.run_cell(family, grammar, cell, freeze=fr, seed=seed, budget=budget)
    finally:
        v1.semantic_score = old_sem
        v1.lifecycle = old_life
    out["schema"] = "GMIK4CellResultV2"
    out["world_profile"] = profile
    out["protected_engine"] = "gmi_k4_search_v2"
    out["predecessor_engine_status"] = "V1_DEVELOPMENT_EXPOSED_NOT_PROTECTED"
    return out
