"""GS-R0 novelty+viability search (#221 sec 18) — viability is a GATE,
novelty is the DRIVER.  No scalar quality optimization anywhere.

Viability (frozen, hard admissibility ONLY — identical to the zoo's hard
gates, evaluation/invariants.py):
  GATE_CORRECTNESS, GATE_INVARIANTS, GATE_PROTECTED_ISOLATION,
  GATE_REVOCATION_FIDELITY, GATE_CAPABILITY_FLOOR (solved_fraction >= 0.5)

Novelty: mean distance to the k nearest neighbours in the novelty archive
over the frozen GS descriptor space (2 behavioural B dims + 2 structural S
dims, registry bounds used for normalization).  Archive admission is
novelty-gated; the ONLY non-novelty preference allowed is the
simplest-viable tie-break for archive membership between equally-novel
duplicates — minimal-criterion novelty search discipline (Lehman &
Stanley 2011; Mouret & Clune L01 parent), never used to rank or promote.
"""
from __future__ import annotations

import random
import time

import numpy
from typing import Any, Dict, List, Optional, Tuple

from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for
from evaluation.evaluate import evaluate_genome
from morphology.compile import compile_genome
from morphology.mutations import crossover, mutate
from search.failure_memory import append_failure, stage_attribution

# Frozen novelty space (embedded verbatim in GRAND_SEARCH_R1_FREEZE.json by
# hpc/freeze_gs.py, which imports this module — single source of truth).
GS_NOVELTY_REGISTRY = ("B_behavior_2d", "S_structural_2d")
GS_NOVELTY_DIMS: Tuple[str, ...] = (DESCRIPTOR_REGISTRY["B_behavior_2d"]["dims"]
                                    + DESCRIPTOR_REGISTRY["S_structural_2d"]["dims"])
GS_NOVELTY_BOUNDS: Tuple[Tuple[float, float], ...] = (
    DESCRIPTOR_REGISTRY["B_behavior_2d"]["bounds"]
    + DESCRIPTOR_REGISTRY["S_structural_2d"]["bounds"])


def novelty_vector(org, ev) -> Tuple[float, ...]:
    """Concatenated B2d+S2d descriptor vector, normalized to [0,1] per
    frozen registry bounds (deterministic function of phenotype)."""
    out: List[float] = []
    for reg_name in GS_NOVELTY_REGISTRY:
        d = descriptors_for(org, ev, reg_name)
        reg = DESCRIPTOR_REGISTRY[reg_name]
        out.extend((dv - b[0]) / (b[1] - b[0] + 1e-12)
                   for dv, b in zip(d, reg["bounds"]))
    return tuple(out)


def novelty_score(vec: Tuple[float, ...], pool: List[Tuple[float, ...]],
                  k: int = 15) -> float:
    """Mean distance to the k nearest neighbours in pool (archive + cohort).
    Empty pool => 0.0 (first behaviours are admitted by the archive floor)."""
    if not pool:
        return 0.0
    ds = sorted(sum((a - b) ** 2 for a, b in zip(vec, p)) ** 0.5 for p in pool)
    take = ds[: min(k, len(ds))]
    return sum(take) / len(take)


def simplicity_key(rec: Dict[str, Any]) -> Tuple[float, float]:
    """Simplest-viable tie-break: fewer units first, then fewer persisted
    bytes.  Used ONLY to choose between duplicates at IDENTICAL novelty
    (exact-same descriptor vector) — never for ranking or promotion."""
    ev = rec.get("evaluation", {})
    return (float(len(rec.get("genome", {}).get("U", []))),
            float(ev.get("persistent_bytes", 0.0)))


class NoveltyArchive:
    """Fixed-capacity archive of viable behaviours keyed by phenotype
    digest.  Admission: viable, phenotype not already archived, novelty
    above the archive's admission floor once past `floor` members.  When a
    duplicate descriptor vector already exists, the SIMPLER of the two is
    kept (simplicity tie-break at equal novelty).  Cap eviction drops the
    least novel member so early stepping stones persist."""

    def __init__(self, cap: int = 4096, floor: int = 64) -> None:
        self.cap = cap
        self.floor = floor
        self.vecs: List[Tuple[float, ...]] = []
        self.keys: List[str] = []
        self.records: Dict[str, Dict[str, Any]] = {}

    def consider(self, rec: Dict[str, Any], vec: Tuple[float, ...]) -> bool:
        if not rec["feasible"]:
            return False
        key = rec["phenotype_digest"]
        if key in self.records:
            return False
        if vec in self.vecs:
            # exact duplicate behaviour: simplest-viable wins the slot
            i = self.vecs.index(vec)
            cur = self.records[self.keys[i]]
            if simplicity_key(rec) < simplicity_key(cur):
                self.records.pop(self.keys[i])
                self.keys[i] = key
                self.records[key] = dict(rec, novelty=0.0)
            return False
        nv = novelty_score(vec, self.vecs)
        if len(self.vecs) < self.floor or nv > 0.0:
            self.vecs.append(vec)
            self.keys.append(key)
            self.records[key] = dict(rec, novelty=round(nv, 6))
            if len(self.vecs) > self.cap:
                worst = min(range(len(self.vecs)),
                            key=lambda i: novelty_score(self.vecs[i], self.vecs))
                self.records.pop(self.keys.pop(worst))
                self.vecs.pop(worst)
            return True
        return False

    def pool(self) -> List[Tuple[float, ...]]:
        return self.vecs

    def size(self) -> int:
        return len(self.vecs)

    @property
    def impl(self) -> str:
        return "builtin"


class RibsNoveltyArchive:
    """pyribs-backed novelty archive (reuse-first, #221 sec 2a): mature
    ProximityArchive admission (k-nearest-neighbour novelty, static
    novelty_threshold=0.0, capacity=cap, pinned seed) instead of the
    hand-rolled container.  OCM-specific semantics kept in this adapter:
    exact-duplicate behaviours resolved by the simplest-viable tie-break,
    and the records dict for archive dumps.  Requires pyribs >= 0.8
    (ProximityArchive); the builtin archive above is the fallback when
    pyribs is absent — WHICH implementation runs is pinned by
    GRAND_SEARCH_R1_FREEZE.json (env probe at freeze time), never ambient."""

    def __init__(self, cap: int = 4096, floor: int = 64, k: int = 15,
                 seed: int = 0) -> None:
        from ribs.archives import ProximityArchive  # pin at import time
        self.cap, self.floor, self.k = cap, floor, k
        self.arch = ProximityArchive(
            solution_dim=4, measure_dim=4, k_neighbors=k,
            novelty_threshold=0.0, initial_capacity=cap, seed=seed)
        self.vecs: List[Tuple[float, ...]] = []
        self.records: Dict[str, Dict[str, Any]] = {}
        self._by_vec: Dict[Tuple[float, ...], str] = {}

    def consider(self, rec: Dict[str, Any], vec: Tuple[float, ...]) -> bool:
        if not rec["feasible"]:
            return False
        key = rec["phenotype_digest"]
        if key in self.records:
            return False
        if vec in self._by_vec:  # duplicate behaviour: simplest-viable wins
            cur = self.records[self._by_vec[vec]]
            if simplicity_key(rec) < simplicity_key(cur):
                self.records.pop(self._by_vec[vec])
                self._by_vec[vec] = key
                self.records[key] = dict(rec, novelty=0.0)
            return False
        # pyribs 0.12 add() is BATCH-ONLY (1-D arrays are rejected by
        # validate_batch) and returns a DICT {"status": int array,
        # "novelty": float array}, not the (AddStatus, value) tuple of
        # older releases — both shapes probed against the real 0.12.0 on
        # the scoring host; the laptop probe pins builtin so this path
        # never runs there.
        res = self.arch.add(
            solution=numpy.asarray(vec, dtype=float).reshape(1, -1),
            objective=numpy.zeros(1),
            measures=numpy.asarray(vec, dtype=float).reshape(1, -1))
        if isinstance(res, dict):
            code = int(numpy.asarray(res["status"]).reshape(-1)[0])
            nov = float(numpy.asarray(res["novelty"]).reshape(-1)[0])
        else:  # ribs < 0.12: (AddStatus, value)
            st, val = res
            st = numpy.asarray(st).reshape(-1)[0] if hasattr(st, "__len__") else st
            code = int(getattr(st, "value", st))
            nov = float(numpy.asarray(val).reshape(-1)[0])
        if code == 0:  # AddStatus.NOT_ADDED (novelty below threshold)
            return False
        self.vecs.append(vec)
        self._by_vec[vec] = key
        self.records[key] = dict(rec, novelty=round(nov, 6))
        return True

    def pool(self) -> List[Tuple[float, ...]]:
        return self.vecs

    def size(self) -> int:
        return len(self.vecs)

    @property
    def impl(self) -> str:
        return "ribs"


def make_novelty_archive(impl: str = "builtin", cap: int = 4096,
                         floor: int = 64, k: int = 15, seed: int = 0):
    """Factory pinned by the freeze.  Unknown/absent-ribs 'ribs' requests
    raise rather than silently fall back (a frozen campaign must never
    depend on ambient environment)."""
    if impl == "builtin":
        return NoveltyArchive(cap=cap, floor=floor)
    if impl == "ribs":
        try:
            return RibsNoveltyArchive(cap=cap, floor=floor, k=k, seed=seed)
        except ImportError as e:
            raise RuntimeError(
                "freeze pins novelty_archive_impl=ribs but pyribs "
                "ProximityArchive is not importable: %r" % e)
    raise ValueError("unknown archive impl %r" % impl)


def viability_gate(r: Dict[str, Any]) -> bool:
    """Hard admissibility ONLY — the frozen zoo gates, unmodified.  There is
    deliberately no quality term here (GS contract: viability gates,
    novelty drives)."""
    return bool(r.get("feasible"))


def evaluate_novelty_candidate(g, tier: str = "T0") -> Dict[str, Any]:
    """Evaluate one genome and build its novelty-search record, appending a
    FAILURES.jsonl entry automatically on every failure (candidate id,
    tier, counterexample/nogood, one-stage attribution)."""
    from morphology.gs_bound import grammar_signature
    try:
        r = evaluate_genome(g, tier=tier)
    except Exception as e:  # crash-class failures are retained, then raised
        append_failure({
            "candidate_id": g.digest(),
            "tier": tier,
            "stage": "tier_eval",
            "counterexample": "exception:%s" % repr(e)[:180],
            "grammar_signature": grammar_signature(g),
        })
        raise
    rec = {
        "genotype_digest": r["genotype_digest"],
        "phenotype_digest": r["phenotype_digest"],
        "genome": g.to_json_obj(),
        "n_units": len(g.U),
        "gates": r["gates"],
        "feasible": viability_gate(r),
        "evaluation": r["evaluation"],
    }
    if not rec["feasible"]:
        att = stage_attribution(r)
        append_failure({
            "candidate_id": rec["genotype_digest"],
            "phenotype_digest": rec["phenotype_digest"],
            "tier": tier,
            "stage": att["stage"],
            "counterexample": att["counterexample"],
            "grammar_signature": grammar_signature(g),
            "gates": {kk: vv for kk, vv in r["gates"].items()
                      if isinstance(vv, bool) and vv is False},
        })
    return rec


def novelty_vector_of(rec: Dict[str, Any]) -> Tuple[float, ...]:
    return novelty_vector(compile_genome(_genome_of(rec)), rec["evaluation"])


def _lane_draw(lane: str, rng: random.Random):
    from morphology.gs_bound import gs_uniform_sample, lane_sampler
    if lane in ("farch", "obasis"):
        return lane_sampler(lane, rng)
    if lane == "units":
        from morphology.gs_bound import lane_units
        return lane_units(rng)
    if lane == "hetero":
        from morphology.gs_bound import lane_hetero
        return lane_hetero(rng)
    return gs_uniform_sample(rng)


def run_novelty_viability(budget: int = 4000, seed: int = 0, lane: str = "uniform",
                          tier: str = "T0", archive_cap: int = 4096,
                          archive_floor: int = 64, k: int = 15,
                          pop_size: int = 48) -> Dict[str, Any]:
    """Novelty+viability search loop over one sampling lane.  Selection is
    by novelty only; every candidate is evaluated and charged (failures
    included, ledgered in FAILURES.jsonl).  Returns archive + counters."""
    rng = random.Random(seed)
    t0 = time.time()
    draw = lambda r: _lane_draw(lane, r)  # noqa: E731
    arch = NoveltyArchive(cap=archive_cap, floor=archive_floor)
    population: List[Dict[str, Any]] = []
    n_evals = 0
    n_viable = 0
    while n_evals < budget:
        cohort: List[Any] = []
        for _ in range(min(pop_size, budget - n_evals)):
            if population and rng.random() < 0.8:
                parent = _genome_of(rng.choice(population))
                if rng.random() < 0.3 and len(population) > 1:
                    other = _genome_of(rng.choice(population))
                    cohort.append(crossover(parent, other, rng))
                else:
                    cohort.append(mutate(parent, rng))
            else:
                cohort.append(draw(rng))
        recs: List[Dict[str, Any]] = []
        for g in cohort:
            rec = evaluate_novelty_candidate(g, tier=tier)
            recs.append(rec)
            n_evals += 1
            if rec["feasible"]:
                n_viable += 1
        for rec in recs:
            if rec["feasible"]:
                rec["_vec"] = novelty_vector_of(rec)
                arch.consider(rec, rec["_vec"])
        pool = arch.pool() + [r["_vec"] for r in recs if r["feasible"]]
        scored = sorted((r for r in recs if r["feasible"]),
                        key=lambda r: -novelty_score(r["_vec"], pool, k))
        keep = max(2, pop_size // 3)
        population = scored[:keep]
        for r in population:
            r.pop("_vec", None)
        for r in recs:
            r.pop("_vec", None)
    return {
        "algorithm": "GS_novelty_viability", "lane": lane, "seed": seed,
        "tier": tier, "evals": n_evals, "viable_found": n_viable,
        "elapsed_s": round(time.time() - t0, 3),
        "n_archive": arch.size(),
        "archive": [dict(rec) for rec in arch.records.values()],
    }


def _genome_of(rec: Dict[str, Any]):
    from morphology.schema import OCMMorphologyGenomeV1
    return OCMMorphologyGenomeV1.from_json_obj(rec["genome"])
