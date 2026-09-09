"""PDEV-4 matched search arms (16) + the quality-diversity archive.

Arms are matched on budget and information surface: every arm sees the same
frozen history (measured raw vectors of previous waves, no labels beyond the
registered coordinates), the same grammar, and proposes the same per-wave
quota.  Arms differ ONLY in how they choose.

Declared implementations (frozen before any outcome; PROTOCOL.json):

* ``tpe_stdlib``  a minimal Parzen estimator over per-dimension value
  frequencies: good set = top gamma=0.25 of history by the registered scalar
  objective, score(x) = prod_dim (p_good(x_d)+eps)/(p_bad(x_d)+eps),
  eps=1e-3; the proposal is the argmax over 64 sampled completions of
  sampled-per-dimension candidates.  No external library.
* ``evolutionary``  population = non-dominated configs of history (cap 24,
  deterministic trim by digest); crossover = per-dimension uniform pick from
  two parents; mutation = one random dimension redrawn; parents chosen by
  Pareto rank then digest order.
* ``learned_policy``  per-dimension value bandit: value score = mean
  (n-success, -work) over history configs containing that value, epsilon=0
  greedy with deterministic tie-break; proposal = argmax composition, plus
  forced exploration of untried values.
* ``qd``  MAP-Elites: empty/rare descriptor cells targeted by a config prior
  that maps each descriptor axis to morphology choices; candidate accepted as
  elite iff integrity-admissible and better on the registered scalar
  objective than the sitting occupant.

Scalar objective (declared, used ONLY by scalar arms and elite replacement):
lexicographic minimize (n_tasks - success, work).  The Pareto/admissibility
machinery (PDEV-8) never collapses to this scalar.

Python 3.8+ stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import random
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import pdev_grammar as G

SCHEMA = "pdev217.search.v1"

ARMS: Tuple[str, ...] = (
    "qd", "random", "tpe_stdlib", "evolutionary", "repair", "reflection",
    "human", "incumbent", "ocm_alternatives", "ocm_composition",
    "ocm_representation", "ocm_index", "ocm_acquisition", "ocm_resource",
    "ocm_donor214", "learned_policy",
)

ARM_ORIGINS: Dict[str, str] = {
    "qd": "quality_diversity",
    "random": "search",
    "tpe_stdlib": "automl_variant",
    "evolutionary": "evolutionary",
    "repair": "program_repair",
    "reflection": "reflection_retry",
    "human": "human",
    "incumbent": "incumbent_control",
    "ocm_alternatives": "existing_alternative",
    "ocm_composition": "ocm_composition",
    "ocm_representation": "ocm_representation",
    "ocm_index": "ocm_index",
    "ocm_acquisition": "ocm_acquisition",
    "ocm_resource": "ocm_resource",
    "ocm_donor214": "donor_transfer",
    "learned_policy": "learned_policy",
}

TPE_GAMMA = 0.25
TPE_EPS = 1e-3
TPE_DRAWS = 64
POP_CAP = 24


# ---------------------------------------------------------------------------
# history / objective
# ---------------------------------------------------------------------------

def scalar_objective(row: Mapping[str, Any]) -> Tuple[int, int]:
    """Declared scalar: lexicographic (failures, work). Lower is better."""
    return (int(row["n"]) - int(row["success"]), int(row["work"]))


def load_history(path) -> List[Dict[str, Any]]:
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _legal_novel(config: Mapping[str, Any], parent: Mapping[str, Any],
                 seen_digests: Iterable[str]) -> bool:
    if G.validate(config):
        return False
    if G.is_noop(config, parent):
        return False
    return G.digest(config) not in seen_digests


def _admit(config: Mapping[str, Any], parent: Mapping[str, Any], seen: set
           ) -> Optional[Dict[str, Any]]:
    """Normalize, validate, dedupe; return the canonical config or None."""
    config = _normalized(config)
    if _legal_novel(config, parent, seen):
        seen.add(G.digest(config))
        return config
    return None


def _normalized(config: Mapping[str, Any]) -> Dict[str, Any]:
    """Neutralize dimension combinations the grammar declares meaningless so
    structural variants collapse to their legal canonical form."""
    out = dict(config)
    if out.get("s_unit") != "feature":
        out["s_feature"] = "prefix9"
        out["s_choose"] = False
        out["s_reindex"] = False
    elif out.get("s_reindex") and not out.get("s_choose"):
        out["s_reindex"] = False
    return out


# ---------------------------------------------------------------------------
# QD descriptor space (frozen bins)
# ---------------------------------------------------------------------------

DESCRIPTOR_AXES: Tuple[str, ...] = (
    "acq_share", "retrieval_share", "revision_share", "bytes_vs_incumbent",
    "s_form", "d_form", "composite",
)
BEHAVIOUR_BOUNDS: Dict[str, Tuple[float, float]] = {
    "acq_share": (0.20, 0.50),
    "retrieval_share": (0.20, 0.50),
    "revision_share": (0.05, 0.30),
    "bytes_vs_incumbent": (0.75, 1.50),
}
DESCRIPTOR_SPACE_SIZE = (3 * 3 * 3 * 3) * len(G.S_UNITS) * len(G.D_UNITS) * 2


def _bin3(value: float, bounds: Tuple[float, float]) -> int:
    low, high = bounds
    if value < low:
        return 0
    if value < high:
        return 1
    return 2


def descriptor_of(config: Mapping[str, Any], raw: Mapping[str, Any],
                  incumbent_bytes: int) -> Dict[str, int]:
    """Descriptor from measured raw vector + morphology dims (never the
    claimed objective)."""
    work = max(1, int(raw.get("work", 1)))
    acq = (int(raw.get("index_build_work", 0)) +
           int(raw.get("index_maintenance_work", 0))) / work
    retrieval = int(raw.get("query_work", 0)) / work
    revision = int(raw.get("revision_work", 0)) / work
    ratio = (int(raw.get("persistent_bytes", 1))
             / max(1, incumbent_bytes))
    composite = 0 if (config.get("s_composite") == "none"
                      and config.get("d_composite") == "none") else 1
    return {
        "acq_share": _bin3(acq, BEHAVIOUR_BOUNDS["acq_share"]),
        "retrieval_share": _bin3(retrieval, BEHAVIOUR_BOUNDS["retrieval_share"]),
        "revision_share": _bin3(revision, BEHAVIOUR_BOUNDS["revision_share"]),
        "bytes_vs_incumbent": _bin3(ratio, BEHAVIOUR_BOUNDS["bytes_vs_incumbent"]),
        "s_form": G.S_UNITS.index(str(config.get("s_unit", "feature"))),
        "d_form": G.D_UNITS.index(str(config.get("d_unit", "lazy"))),
        "composite": composite,
    }


def descriptor_cell(desc: Mapping[str, int]) -> str:
    return "|".join("%s=%d" % (axis, desc[axis]) for axis in DESCRIPTOR_AXES)


class DiversityArchive:
    """MAP-Elites archive persisted across generations (DIVERSITY_ARCHIVE_V1)."""

    def __init__(self, path: Optional[str] = None):
        self.cells: Dict[str, Dict[str, Any]] = {}
        self.history: List[Dict[str, Any]] = []
        self.failed_niches: List[Dict[str, Any]] = []
        if path:
            self.load(path)

    def offer(self, config: Mapping[str, Any], raw: Mapping[str, Any],
              incumbent_bytes: int, origin: str, integrity_ok: bool,
              reason: str = "") -> Dict[str, Any]:
        desc = descriptor_of(config, raw, incumbent_bytes)
        cell = descriptor_cell(desc)
        obj = (int(raw.get("n", 0)) - int(raw.get("success", 0)),
               int(raw.get("work", 0)))
        sitting = self.cells.get(cell)
        event = {"cell": cell, "descriptor": desc, "digest": G.digest(config),
                 "origin": origin, "objective": list(obj),
                 "generation": raw.get("generation"),
                 "accepted": False}
        if not integrity_ok:
            self.failed_niches.append({"cell": cell, "digest": G.digest(config),
                                       "origin": origin, "reason": reason or
                                       "integrity hostiles failed"})
            event["rejected_reason"] = reason or "integrity hostiles failed"
            self.history.append(event)
            return event
        if sitting is None or obj < tuple(sitting["objective"]):
            self.cells[cell] = {"digest": G.digest(config), "config": dict(config),
                                "descriptor": desc, "objective": list(obj),
                                "raw": dict(raw), "origin": origin,
                                "generation": raw.get("generation")}
            event["accepted"] = True
        elif sitting["digest"] == G.digest(config):
            event["accepted"] = True
        else:
            event["rejected_reason"] = "objective not better than sitting elite"
        self.history.append(event)
        return event

    def occupancy(self) -> Dict[str, int]:
        return {"cells_occupied": len(self.cells),
                "space_size": DESCRIPTOR_SPACE_SIZE}

    def save(self, path: str) -> None:
        with open(path, "w") as handle:
            json.dump({"schema": "pdev217.diversity_archive.v1",
                       "descriptor_axes": list(DESCRIPTOR_AXES),
                       "behaviour_bounds": {k: list(v) for k, v
                                            in BEHAVIOUR_BOUNDS.items()},
                       "space_size": DESCRIPTOR_SPACE_SIZE,
                       "cells": self.cells,
                       "history": self.history[-4000:],
                       "failed_niches": self.failed_niches[-2000:]},
                      handle, indent=1, sort_keys=True)

    def load(self, path: str) -> None:
        with open(path) as handle:
            payload = json.load(handle)
        if payload.get("schema") != "pdev217.diversity_archive.v1":
            raise ValueError("unknown archive schema")
        self.cells = payload["cells"]
        self.history = payload.get("history", [])
        self.failed_niches = payload.get("failed_niches", [])


# ---------------------------------------------------------------------------
# deterministic arm RNG
# ---------------------------------------------------------------------------

def arm_rng(salt: str, arm: str, generation: int, wave: int) -> random.Random:
    seed = hashlib.sha256(("|".join((salt, arm, str(generation), str(wave)))
                           ).encode()).hexdigest()[:16]
    return random.Random(int(seed, 16))


def _dimension_values() -> Dict[str, Sequence[Any]]:
    return {name: list(values) for name, values in G.DIMENSIONS}


def _random_legal(rng: random.Random, parent: Mapping[str, Any],
                  seen: set) -> Optional[Dict[str, Any]]:
    options = _dimension_values()
    for _ in range(200):
        config = {}
        for name, values in options.items():
            config[name] = rng.choice(values)
        config = _normalized(config)
        if _legal_novel(config, parent, seen):
            return config
    return None


# ---------------------------------------------------------------------------
# individual arms
# ---------------------------------------------------------------------------

def arm_random(rng, parent, history, seen, quota):
    out = []
    for _ in range(quota):
        config = _random_legal(rng, parent, seen)
        if config is not None:
            seen.add(G.digest(config))
            out.append(config)
    return out


def arm_tpe_stdlib(rng, parent, history, seen, quota):
    options = _dimension_values()
    if len(history) < 8:
        return arm_random(rng, parent, history, seen, quota)
    ranked = sorted(history, key=lambda r: scalar_objective(r))
    n_good = max(1, int(TPE_GAMMA * len(ranked)))
    good, bad = ranked[:n_good], ranked[n_good:]

    def freqs(rows):
        out = {name: {v: 0 for v in options[name]} for name in options}
        for row in rows:
            config = row["config"]
            for name in options:
                if name in config:
                    out[name][config[name]] += 1
        return out

    fg, fb = freqs(good), freqs(bad)
    proposals = []
    for _ in range(max(TPE_DRAWS, 32 * quota)):
        config = {}
        score = 1.0
        for name, values in options.items():
            if rng.random() < 0.5:
                value = rng.choice(values)
            else:
                pool = good if rng.random() < 0.5 else bad
                configs = [r["config"].get(name) for r in pool]
                configs = [c for c in configs if c in options[name]]
                value = rng.choice(configs) if configs else rng.choice(values)
            pg = (fg[name][value] + TPE_EPS) / (len(good) + TPE_EPS)
            pb = (fb[name][value] + TPE_EPS) / (len(bad) + TPE_EPS)
            score *= pg / pb
            config[name] = value
        config = _normalized(config)
        if _legal_novel(config, parent, seen):
            proposals.append((score, G.digest(config), config))
    proposals.sort(key=lambda t: (-t[0], t[1]))
    out = []
    for _score, digest, config in proposals[:quota]:
        seen.add(digest)
        out.append(config)
    return out if out else arm_random(rng, parent, history, seen, quota)


def _nondominated(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = sorted(history, key=scalar_objective)[:POP_CAP]
    return rows


def arm_evolutionary(rng, parent, history, seen, quota):
    if len(history) < 4:
        return arm_random(rng, parent, history, seen, quota)
    pop = _nondominated(history)
    options = _dimension_values()
    out = []
    attempts = 0
    while len(out) < quota and attempts < 400:
        attempts += 1
        pa, pb = rng.choice(pop)["config"], rng.choice(pop)["config"]
        child = {}
        for name in options:
            child[name] = pa.get(name, parent[name]) if rng.random() < 0.5 \
                else pb.get(name, parent[name])
        if rng.random() < 0.7:
            name = rng.choice(list(options))
            child[name] = rng.choice(options[name])
        child = _normalized(child)
        if _legal_novel(child, parent, seen):
            seen.add(G.digest(child))
            out.append(child)
    return out


def arm_repair(rng, parent, history, seen, quota):
    """Program repair: enumerate single-dimension repairs of the parent."""
    out = []
    for child in G.enumerate_neighbourhood(parent, structural_only=True):
        if len(out) >= quota:
            break
        if _legal_novel(child, parent, seen):
            seen.add(G.digest(child))
            out.append(child)
    for child in G.enumerate_neighbourhood(parent, structural_only=False)[:64]:
        if len(out) >= quota:
            break
        if _legal_novel(child, parent, seen):
            seen.add(G.digest(child))
            out.append(child)
    return out


def arm_reflection(rng, parent, history, seen, quota):
    """Reflection/retry: take the best REJECTED config of history and change
    one dimension adjacent to its failing coordinate."""
    rejected = [r for r in history if r.get("disposition") == "REJECTED"]
    if not rejected:
        return arm_repair(rng, parent, history, seen, quota)
    options = _dimension_values()
    out = []
    ranked = sorted(rejected, key=scalar_objective)
    for row in ranked:
        base = dict(row["config"])
        for name in options:
            for value in options[name]:
                child = dict(base)
                child[name] = value
                if _legal_novel(child, parent, seen):
                    seen.add(G.digest(child))
                    out.append(child)
                    if len(out) >= quota:
                        return out
    return out


HUMAN_LIBRARY: Tuple[Dict[str, Any], ...] = (
    {"s_unit": "feature", "s_feature": "prefix9", "s_choose": True,
     "s_reindex": True, "s_bucket": 4, "s_growth": 1, "s_composite": "none",
     "d_unit": "lazy", "d_composite": "none"},                     # discovering
    {"s_unit": "feature", "s_feature": "prefix9", "s_choose": True,
     "s_reindex": False, "s_bucket": 4, "s_growth": 1, "s_composite": "none",
     "d_unit": "lazy", "d_composite": "none"},                     # fixed-feature
    {"s_unit": "scan", "s_feature": "prefix9", "s_choose": False,
     "s_reindex": False, "s_bucket": 4, "s_growth": 1, "s_composite": "none",
     "d_unit": "recompute", "d_composite": "none"},                # exact parents
    {"s_unit": "vector", "s_feature": "prefix9", "s_choose": False,
     "s_reindex": False, "s_bucket": 4, "s_growth": 1, "s_composite": "none",
     "d_unit": "cooc", "d_composite": "none"},                     # retrieval/cooc
    {"s_unit": "feature", "s_feature": "prefix9", "s_choose": False,
     "s_reindex": False, "s_bucket": 2, "s_growth": 1, "s_composite": "none",
     "d_unit": "learned", "d_composite": "escalate_on_stale"},     # tight buckets
)


def arm_human(rng, parent, history, seen, quota):
    out = []
    for base in HUMAN_LIBRARY:
        if len(out) >= quota:
            break
        if _legal_novel(base, parent, seen):
            seen.add(G.digest(base))
            out.append(dict(base))
    return out


def arm_incumbent(rng, parent, history, seen, quota):
    """Control: re-measure the incumbent itself (no self-change)."""
    return []  # the incumbent is always measured separately as the baseline


def arm_ocm_alternatives(rng, parent, history, seen, quota):
    out = []
    for unit in G.S_UNITS:
        child = _admit({**parent, "s_unit": unit}, parent, seen)
        if child:
            out.append(child)
        if len(out) >= quota:
            return out
    for unit in G.D_UNITS:
        child = _admit({**parent, "d_unit": unit}, parent, seen)
        if child:
            out.append(child)
        if len(out) >= quota:
            return out
    return out


def arm_ocm_composition(rng, parent, history, seen, quota):
    out = []
    for s_comp in G.S_COMPOSITES:
        for d_comp in G.D_COMPOSITES:
            child = _admit({**parent, "s_composite": s_comp,
                            "d_composite": d_comp}, parent, seen)
            if child:
                out.append(child)
            if len(out) >= quota:
                return out
    return out


def arm_ocm_representation(rng, parent, history, seen, quota):
    out = []
    features = list(G.S_FEATURES)
    step = max(1, len(features) // max(1, quota))
    for feature in features[::step]:
        child = _admit({**parent, "s_unit": "feature", "s_feature": feature},
                       parent, seen)
        if child:
            out.append(child)
        if len(out) >= quota:
            break
    return out


def arm_ocm_index(rng, parent, history, seen, quota):
    out = []
    for bucket in G.BUCKET_BOUNDS:
        for choose in (True, False):
            for reindex in (True, False):
                child = _admit({**parent, "s_unit": "feature",
                                "s_bucket": bucket, "s_choose": choose,
                                "s_reindex": reindex}, parent, seen)
                if child:
                    out.append(child)
                if len(out) >= quota:
                    return out
    return out


def arm_ocm_acquisition(rng, parent, history, seen, quota):
    out = []
    for growth in G.GROWTH_SCHEDULES:
        for choose in (True, False):
            child = _admit({**parent, "s_growth": growth, "s_choose": choose},
                           parent, seen)
            if child:
                out.append(child)
            if len(out) >= quota:
                return out
    return out


def arm_ocm_resource(rng, parent, history, seen, quota):
    """Minimal-footprint forms: no index, no search, smallest structures."""
    out = []
    for unit in ("scan", "vector"):
        for d_unit in ("recompute", "all_evidence"):
            child = _admit({**parent, "s_unit": unit, "s_feature": "prefix9",
                            "s_choose": False, "s_reindex": False,
                            "s_composite": "none", "d_unit": d_unit,
                            "d_composite": "none"}, parent, seen)
            if child:
                out.append(child)
            if len(out) >= quota:
                return out
    return out


def arm_ocm_donor214(rng, parent, history, seen, quota):
    """#214 donor transfer: first-refusal routing compositions and
    follow-ups (escalation), with provenance recorded at emission."""
    out = []
    for s_comp in ("in_store_first_refusal",):
        for base_s in ("feature", "vector", "scan"):
            child = _admit({**parent, "s_unit": base_s, "s_composite": s_comp,
                            "d_composite": "escalate_on_stale"}, parent, seen)
            if child:
                out.append(child)
            if len(out) >= quota:
                return out
    return out


def arm_learned_policy(rng, parent, history, seen, quota):
    if len(history) < 6:
        return arm_random(rng, parent, history, seen, quota)
    options = _dimension_values()
    stats = {name: {v: [0, 0.0, 0] for v in options[name]} for name in options}
    for row in history:
        config = row["config"]
        fails, work = scalar_objective(row)
        for name in options:
            value = config.get(name)
            if value in stats[name]:
                stats[name][value][0] += 1
                stats[name][value][1] += fails
                stats[name][value][2] += work

    def greedy_child(rank_bias: int) -> Dict[str, Any]:
        child = {}
        for name, values in options.items():
            def key(v):
                cnt, fails, work = stats[name][v]
                if cnt == 0:  # exploration: untried values first on odd bias
                    return (0 if rank_bias else 1, -1 if not rank_bias else 0,
                            0, str(v))
                return (1 if rank_bias else 0, fails / cnt,
                        work / max(1, cnt), str(v))
            child[name] = min(values, key=key)
        return _normalized(child)

    out = []
    for i in range(quota):
        child = greedy_child(i % 2)
        if not _legal_novel(child, parent, seen):
            child = _random_legal(rng, parent, seen)
        if child is not None and _legal_novel(child, parent, seen):
            seen.add(G.digest(child))
            out.append(child)
    return out


def arm_qd(rng, parent, history, seen, quota, archive: DiversityArchive,
           incumbent_bytes: int):
    """Illumination: target empty or rare cells with a morphology prior."""
    out = []
    empty_targets = []
    for acq in range(3):
        for ret in range(3):
            for rev in range(3):
                for byt in range(3):
                    for s_form in range(len(G.S_UNITS)):
                        for d_form in range(len(G.D_UNITS)):
                            for comp in range(2):
                                cell = "|".join(
                                    "%s=%d" % (axis, value) for axis, value in
                                    zip(DESCRIPTOR_AXES,
                                        (acq, ret, rev, byt, s_form, d_form, comp)))
                                if cell not in archive.cells:
                                    empty_targets.append(
                                        (cell, (acq, ret, rev, byt,
                                               s_form, d_form, comp)))
    rng.shuffle(empty_targets)
    for _cell, target in empty_targets[: max(4, quota * 4)]:
        acq, ret, rev, byt, s_form, d_form, comp = target
        for _attempt in range(24):
            config = {"s_unit": G.S_UNITS[s_form], "d_unit": G.D_UNITS[d_form],
                      "s_feature": rng.choice(G.S_FEATURES),
                      "s_choose": rng.choice((True, False)),
                      "s_reindex": False,
                      "s_bucket": rng.choice(G.BUCKET_BOUNDS),
                      "s_growth": rng.choice(G.GROWTH_SCHEDULES),
                      "s_composite": ("in_store_first_refusal" if comp == 1
                                      and rng.random() < 0.6 else "none"),
                      "d_composite": ("escalate_on_stale" if comp == 1
                                      and rng.random() < 0.5 else "none")}
            if acq == 0:  # low acquisition share -> avoid search-heavy forms
                config["s_choose"] = False
            if acq == 2:  # high acquisition share -> search + re-index
                config["s_choose"] = True
                config["s_reindex"] = True
            if ret == 2:  # high retrieval share -> unindexed scan unit
                config["s_unit"] = "scan"
            if byt == 0:  # small footprint -> tight buckets
                config["s_bucket"] = min(G.BUCKET_BOUNDS)
            config = _normalized(config)
            if _legal_novel(config, parent, seen):
                seen.add(G.digest(config))
                out.append(config)
                break
        if len(out) >= quota:
            break
    while len(out) < quota:
        config = _random_legal(rng, parent, seen)
        if config is None:
            break
        seen.add(G.digest(config))
        out.append(config)
    return out


ARM_FNS = {
    "random": arm_random, "tpe_stdlib": arm_tpe_stdlib,
    "evolutionary": arm_evolutionary, "repair": arm_repair,
    "reflection": arm_reflection, "human": arm_human,
    "incumbent": arm_incumbent, "ocm_alternatives": arm_ocm_alternatives,
    "ocm_composition": arm_ocm_composition,
    "ocm_representation": arm_ocm_representation, "ocm_index": arm_ocm_index,
    "ocm_acquisition": arm_ocm_acquisition, "ocm_resource": arm_ocm_resource,
    "ocm_donor214": arm_ocm_donor214, "learned_policy": arm_learned_policy,
}


def propose_wave(salt: str, generation: int, wave: int,
                 parent: Mapping[str, Any], history_path: str,
                 archive_path: Optional[str], quota_per_arm: int,
                 incumbent_bytes: int) -> List[Dict[str, Any]]:
    """One wave's candidate batch: every arm contributes its quota.

    Returns candidate records (config + arm + origin + change class + size
    accounting), deduplicated by digest, deterministic given the salt.
    """
    history = load_history(history_path) if history_path else []
    seen = {G.digest(parent)}
    seen.update(row["digest"] for row in history if "digest" in row)
    archive = None
    if archive_path:
        try:
            archive = DiversityArchive(archive_path)
        except FileNotFoundError:
            archive = DiversityArchive()
    if archive is None:
        archive = DiversityArchive()
    out: List[Dict[str, Any]] = []
    for arm in ARMS:
        rng = arm_rng(salt, arm, generation, wave)
        if arm == "qd":
            configs = arm_qd(rng, parent, history, seen, quota_per_arm,
                             archive, incumbent_bytes)
        else:
            configs = ARM_FNS[arm](rng, parent, history, seen, quota_per_arm)
        for config in configs:
            record = {"candidate_id": "g%d.w%d.%s.%d" % (generation, wave, arm,
                                                         len(out)),
                      "config": config, "digest": G.digest(config),
                      "arm": arm, "origin": ARM_ORIGINS[arm],
                      "change_class": G.infer_change_class(config, parent),
                      "size": G.size_accounting(config, parent),
                      "rollback_plan": G.rollback_plan(config)}
            out.append(record)
    return out
