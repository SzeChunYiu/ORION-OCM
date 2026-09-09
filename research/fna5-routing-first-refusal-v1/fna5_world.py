"""FNA-5/D7 task world: routing among applicable operators on the real catalogue surface.

Hooks the SAME production objects research/operator_selection_scaling.py uses —
``ocm.runtime.solve.OperatorSpec`` as the catalogue record and
``SolveOperatorIndex.select()`` as the structural-applicability query surface — but with a
catalogue in which several METHOD FAMILIES compete for one obligation and differ in counted
execution work and checker outcome. The scaling study cannot express a routing decision
(exactly one applicable operator per query by construction); this module extends the world
additively, inside this capsule only.

Everything is deterministic under the frozen salt: all randomness flows through
sha256-derived seeds, all iteration over unordered collections is sorted, and no ``hash()``
call is used. Python 3.8 stdlib only.

Declared physics (frozen BEFORE any outcome access; see PROTOCOL.md):
- scan      exact, always applicable (empty input set), work = base + 1/atom looped.
- probe     exact, work = base + bucket loop ~ log2(n) + anchor slice.
- window    approximate, work = base + W;  PASS iff disp + 0.12*(u-0.5) <= theta1_eff(W).
- deepwindow approximate, work = base + W*log2(W)/4; PASS iff disp - 0.10*(u-0.5) >= theta2
                                              AND alias + 0.10*(u-0.5) <= theta3.
- sample    approximate, work = base + k;   PASS iff alias + 0.12*(u-0.5) <= theta3s
                                              AND disp in [theta4, theta7] band.
Realized thetas are seeded draws around DECLARED design centres (0.35, 0.55, 0.30, 0.42,
0.65); only the declared centres are public to non-oracle arms. The checker is exact and
O(1) (declared simplification: failures are always caught, never delivered). A failed
attempt is charged, then the runtime falls back to scan (portfolio-recovery convention).
"""
from __future__ import annotations

import hashlib
import math
import random
import statistics
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from ocm.runtime.operator_index import SolveOperatorIndex
from ocm.runtime.solve import OperatorSpec

SALT = "fna5-routing-first-refusal-v1::3f9c217a"
SCHEMA = "ocm.fna.fna5-routing-first-refusal.v1"
FAMILIES = ("scan", "probe", "window", "deepwindow", "sample")
EXACT_FAMILIES = ("scan", "probe")   # always-PASS families (legal safe fallback)
VERIFY_WORK = 5  # O(1) exact-certificate check, charged per execution
FEATURES = ("log2_n", "disp", "alias", "type_entropy", "n_applicable", "rarest_postings",
            "min_window_w", "mean_w", "skew_w", "ndup", "task_flag", "scan_cost_est")


def derive_seed(*parts: str) -> int:
    digest = hashlib.md5((SALT + "::" + "::".join(parts)).encode("utf-8")).hexdigest()
    return int(digest, 16)


def split_of(qid: str) -> str:
    """Frozen DEV/EVAL/DRIFT assignment by salted hash — disjoint by construction."""
    bucket = int(hashlib.md5((SALT + "::split::" + qid).encode("utf-8")).hexdigest(), 16) % 10
    return "DEV" if bucket <= 3 else ("EVAL" if bucket <= 7 else "DRIFT")


# ---------------------------------------------------------------------------------------------
# world parameters and declaration
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class WorldParams:
    n_queries: int = 2400
    n_atoms: int = 240
    tiny: bool = False

    @staticmethod
    def tiny_params() -> "WorldParams":
        return WorldParams(n_queries=120, n_atoms=60, tiny=True)


@dataclass
class Instance:
    op_id: str
    family: str
    anchor: Optional[str]                      # None = empty input set (always applicable)
    param: int                                  # W for window/deepwindow, k for sample
    base_cost: float
    unit_cost: float
    realized: Dict[str, float] = field(default_factory=dict)  # declared+realized law constants
    spec: Optional[OperatorSpec] = None

    def declared_cost_estimate(self, q: "Query", state: Dict[str, float]) -> float:
        """Closed-form cost prediction from the DECLARED law (legal for any arm).
        Mirrors execute_instance's physics exactly, modulo int truncation."""
        n = max(q.n, 2)
        m = 1.1 if q.task_flag else 1.0
        base = self.base_cost * m
        if self.family == "scan":
            sm = state["scan_version_mult"]
            return base * sm + self.unit_cost * sm * q.n
        if self.family == "probe":
            return base + self.unit_cost * (2 * (math.log2(n) + 3) + min(q.n, 12))
        if self.family == "window":
            return base + self.unit_cost * self.param
        if self.family == "deepwindow":
            return base + self.unit_cost * (self.param * math.log2(self.param) / 4.0)
        return base + self.unit_cost * self.param


@dataclass
class Query:
    qid: str
    atoms: Tuple[str, ...]                     # sorted active atom ids
    n: int
    weights: Tuple[float, ...]                 # sorted-descending weights of active atoms
    task_flag: int                             # 0 = AGG, 1 = THRESH
    u: float                                   # per-query latent noise U(0,1)
    features: Optional[List[float]] = None
    feature_work: int = 0

    @property
    def active_set(self) -> frozenset:
        return frozenset(self.atoms)

    @property
    def disp(self) -> float:
        return self.features[1]

    @property
    def alias(self) -> float:
        return self.features[2]


def _sample(rng: random.Random, population: Sequence[str], k: int) -> Tuple[str, ...]:
    return tuple(sorted(rng.sample(list(population), k)))


def build_world(params: WorldParams) -> Dict:
    """Atoms, realized law constants, catalogue instances, and the real operator index."""
    rng = random.Random(derive_seed("world"))
    atom_ids = ["atom:%03d" % i for i in range(params.n_atoms)]
    types = {a: ["alpha", "beta", "gamma", "delta"][i % 4] for i, a in enumerate(atom_ids)}
    # per-type weight ranges give queries a real dispersion spread: alpha tight (low disp),
    # beta wide (high disp), delta near-degenerate (high alias when active-heavy)
    wrange = {"alpha": (0.2, 0.4), "beta": (0.2, 1.0), "gamma": (0.2, 0.8), "delta": (0.47, 0.53)}
    weights = {a: round(rng.uniform(*wrange[types[a]]), 4) for a in atom_ids}
    common = {"common:0": 0.5, "common:1": 0.5, "common:2": 0.5}
    for a in common:
        types[a] = "common"
    weights.update(common)

    realized = {
        "theta1": 0.35 + rng.uniform(-0.08, 0.08),   # window centre (declared 0.35)
        "theta2": 0.55 + rng.uniform(-0.06, 0.06),   # deepwindow floor (declared 0.55)
        "theta3": 0.30 + rng.uniform(-0.05, 0.05),   # deepwindow alias ceiling (declared 0.30)
        "theta3s": 0.32 + rng.uniform(-0.05, 0.05),  # sample alias ceiling (declared 0.32)
        "theta4": 0.42 + rng.uniform(-0.05, 0.05),   # sample band floor (declared 0.42)
        "theta7": 0.65 + rng.uniform(-0.04, 0.04),   # sample band ceiling (declared 0.65)
    }
    # family anchors: fixed per-anchor presence probabilities, 0.55..0.95
    anchors = list(_sample(rng, atom_ids, 7)) + ["drift:0"]
    weights["drift:0"] = 0.5
    types["drift:0"] = "delta"
    presence = {a: round(rng.uniform(0.55, 0.95), 3) for a in anchors}
    presence["common:1"] = 0.85
    presence["common:2"] = 0.70

    def inst(op_id, family, anchor, param, base, unit):
        return Instance(op_id, family, anchor, param, base, unit, dict(realized))

    catalogue: List[Instance] = [
        inst("probe:0", "probe", "common:1", 0, 18.0, 2.2),
        inst("probe:1", "probe", "common:2", 0, 18.0, 2.2),
        inst("window:12", "window", anchors[0], 12, 10.0, 1.4),
        inst("window:28", "window", anchors[1], 28, 10.0, 1.4),
        inst("window:60", "window", anchors[2], 60, 10.0, 1.4),
        inst("deepwindow:48", "deepwindow", anchors[3], 48, 12.0, 0.5),
        inst("deepwindow:96", "deepwindow", anchors[4], 96, 12.0, 0.5),
        inst("sample:16", "sample", anchors[5], 16, 20.0, 2.0),
        inst("sample:32", "sample", anchors[6], 32, 20.0, 2.0),
        inst("scan", "scan", None, 0, 40.0, 1.0),
    ]
    state: Dict[str, float] = {"scan_version_mult": 1.0, **realized}
    world = {"params": params, "types": types, "weights": weights, "realized": realized,
             "anchors": anchors, "presence": presence, "catalogue": catalogue,
             "state": state, "index": None, "index_build_work": 0}
    rebuild_index(world)
    return world


def rebuild_index(world: Dict) -> None:
    """(Re)build the REAL SolveOperatorIndex over the current catalogue; charge build work."""
    state = world["state"]
    collector = {"work": 0}

    def backend_for(instance: Instance) -> Callable:
        def backend(ks, operator_id, ctx):
            work, passed = execute_instance(instance, ctx["query"], state)
            collector["work"] += work
            return {"value": instance.declared_cost_estimate(ctx["query"], state) if passed
                    else -1.0, "passed": passed, "exec_work": work}
        return backend

    ops = []
    for it in world["catalogue"]:
        inputs = () if it.anchor is None else (it.anchor,)
        it.spec = OperatorSpec(it.op_id, "1", backend_for(it), inputs)
        ops.append(it.spec)
    world["index"] = SolveOperatorIndex(tuple(ops))
    world["index_build_work"] = sum(world["index"].build_work.values())
    world["collector"] = collector


def applicable(world: Dict, q: Query) -> Tuple[List[Instance], Dict[str, int]]:
    """Real structural-applicability surface: SolveOperatorIndex.select over active atoms."""
    sel = world["index"].select(q.atoms)
    by_id = {it.op_id: it for it in world["catalogue"]}
    insts = [by_id[op.operator_id] for op in sel.operators]
    return insts, dict(sel.work)


# ---------------------------------------------------------------------------------------------
# execution physics (counted loops; the backend closures above run through OperatorSpec)
# ---------------------------------------------------------------------------------------------


def execute_instance(it: Instance, q: Query, state: Dict[str, float]) -> Tuple[int, bool]:
    """Counted work + deterministic checker outcome for one execution. Work is real loop
    iterations (the repo's logical-work-counter convention), not wall time."""
    mult = 1.0 if q.task_flag == 0 else 1.1
    base = int(it.base_cost * mult)
    if it.family == "scan":
        sm = state["scan_version_mult"]
        work = base + int(it.unit_cost * sm * q.n)
        for _ in range(int(it.unit_cost * sm * q.n)):   # the real aggregation loop
            pass
        return work, True
    if it.family == "probe":
        buckets = int(math.log2(max(q.n, 2))) + 3
        loop = int(it.unit_cost * (2 * buckets + min(q.n, 12)))
        work = base + loop
        for _ in range(loop):
            pass
        return work, True
    if it.family == "window":
        loop = int(it.unit_cost * it.param)
        work = base + loop
        for _ in range(loop):
            pass
        theta_eff = state["theta1"] + (it.param - 28) * 0.002
        return work, q.disp + 0.12 * (q.u - 0.5) <= theta_eff
    if it.family == "deepwindow":
        loop = int(it.unit_cost * it.param * math.log2(it.param) / 4)
        work = base + loop
        for _ in range(loop):
            pass
        ok = (q.disp - 0.10 * (q.u - 0.5) >= state["theta2"]
              and q.alias + 0.10 * (q.u - 0.5) <= state["theta3"])
        return work, ok
    loop = int(it.unit_cost * it.param)
    work = base + loop
    for _ in range(loop):
        pass
    ok = (q.alias + 0.12 * (q.u - 0.5) <= state["theta3s"]
          and q.disp - 0.08 * (q.u - 0.5) >= state["theta4"]
          and q.disp + 0.08 * (q.u - 0.5) <= state["theta7"])
    return work, ok


def execute_via_spec(world: Dict, it: Instance, q: Query) -> Tuple[int, bool]:
    """Route one execution through the real OperatorSpec backend callable."""
    out = it.spec.backend(None, it.op_id, {"query": q, "inputs": () if it.anchor is None
                                           else (it.anchor,)})
    return out["exec_work"], out["passed"]


# ---------------------------------------------------------------------------------------------
# query generation and the legal feature surface
# ---------------------------------------------------------------------------------------------


def make_query(world: Dict, idx: int) -> Query:
    params: WorldParams = world["params"]
    qid = "q:%05d" % idx
    rng = random.Random(derive_seed("query", qid))
    n = rng.randint(30, 160) if not params.tiny else rng.randint(15, 60)
    pools: Dict[str, List[str]] = {"alpha": [], "beta": [], "gamma": [], "delta": []}
    for a, t in world["types"].items():
        if t in pools:
            pools[t].append(a)
    for lst in pools.values():
        lst.sort()
    # latent type mix m(q) ~ Dirichlet(1,1,1,1): full support over alpha/beta/gamma/delta
    # dominant mixes, so dispersion AND alias both span their declared law ranges
    gam = [-math.log(rng.random() + 1e-12) for _ in range(4)]
    tot = sum(gam)
    atoms: List[str] = []
    for t, p in zip(("alpha", "beta", "gamma", "delta"), (g / tot for g in gam)):
        atoms.extend(_sample(rng, pools[t], min(int(n * p) + 1, len(pools[t]))))
    for anchor, p in sorted(world["presence"].items()):
        if rng.random() < p:
            atoms.append(anchor)
    atoms = sorted(set(atoms))
    weights = tuple(sorted((world["weights"][a] for a in atoms), reverse=True))
    q = Query(qid=qid, atoms=tuple(atoms), n=len(atoms), weights=weights,
              task_flag=rng.getrandbits(1), u=rng.random())
    q.features, q.feature_work = extract_features(world, q)
    return q


def extract_features(world: Dict, q: Query) -> Tuple[List[float], int]:
    """12 legal features: query + DECLARED catalogue constants only. Never a label.
    Returns counted extraction work (float ops actually performed)."""
    w = q.weights
    work = 0
    mean = sum(w) / len(w); work += len(w)
    stdev = math.sqrt(sum((x - mean) ** 2 for x in w) / len(w)); work += 2 * len(w)
    disp = min(max(stdev / 0.30, 0.0), 1.2); work += 3
    rng = random.Random(derive_seed("pairs", q.qid))
    active = list(q.atoms)
    pairs = min(60, len(active) * (len(active) - 1) // 2)
    ndup = 0
    for _ in range(pairs):
        a, b = rng.sample(active, 2)
        if abs(world["weights"][a] - world["weights"][b]) < 0.02:
            ndup += 1
        work += 3
    alias = ndup / max(pairs, 1); work += 2
    counts = {"alpha": 0, "beta": 0, "gamma": 0, "delta": 0, "common": 0}
    for a in q.atoms:
        counts[world["types"][a]] += 1
    work += len(q.atoms)
    ent = -sum((c / q.n) * math.log2(c / q.n) for c in counts.values() if c); work += 8
    med = statistics.median(w); work += len(w)
    skew = (mean - med) / mean if mean else 0.0; work += 2
    insts, sel_work = applicable(world, q)
    n_applicable = sel_work["structural_candidates"]
    rarest = float(sel_work["postings_examined"]); work += 2
    min_w = min([it.param for it in insts if it.family == "window"] or [0]); work += 4
    scan_mult = world["state"]["scan_version_mult"]
    scan_est = 40.0 * scan_mult + 1.0 * scan_mult * q.n; work += 4
    feats = [math.log2(q.n), round(disp, 5), round(alias, 5), round(ent, 5), n_applicable,
             rarest, min_w, round(mean, 5), round(skew, 5), ndup, q.task_flag, round(scan_est, 3)]
    return feats, work


# ---------------------------------------------------------------------------------------------
# arms that need no fitting: incumbent baseline, oracle, analytic guarded rule
# ---------------------------------------------------------------------------------------------


def cheapest(instances: Sequence[Instance], q: Query, state: Dict[str, float],
             family: Optional[str] = None) -> Optional[Instance]:
    cands = [it for it in instances if family is None or it.family == family]
    if not cands:
        return None
    return min(cands, key=lambda it: (it.declared_cost_estimate(q, state), it.op_id))


def run_oracle(world: Dict, q: Query, insts: Sequence[Instance]) -> Dict:
    """A0: try everything (identification work reported separately), pick cheapest PASS."""
    state = world["state"]
    outcomes: Dict[str, Tuple[int, bool]] = {}
    identify_work = 0
    for it in insts:
        w, ok = execute_via_spec(world, it, q)
        identify_work += w + VERIFY_WORK
        outcomes[it.op_id] = (w, ok)
    passing = [(outcomes[it.op_id][0], it) for it in insts if outcomes[it.op_id][1]]
    best_w, best = min(passing, key=lambda t: (t[0], t[1].op_id))
    return {"choice": best, "exec_work": best_w + VERIFY_WORK, "identify_work": identify_work,
            "family": best.family, "outcomes": outcomes}


def run_baseline(world: Dict, q: Query, insts: Sequence[Instance]) -> Dict:
    """Incumbent policy: supplied catalogue order, first PASS wins (compose→check→decide)."""
    total = 0
    choice = None
    for it in insts:                            # index select preserves supplied order
        w, ok = execute_via_spec(world, it, q)
        total += w + VERIFY_WORK
        if ok:
            choice = it
            break
    return {"choice": choice, "exec_work": total, "family": choice.family if choice else None,
            "inference_work": 0, "feature_work": 0, "fallback": False,
            "passed_first": choice is not None}


ANALYTIC_MARGIN = 0.06  # frozen safety margin on declared centres


def analytic_choice(world: Dict, q: Query, insts: Sequence[Instance]) -> Tuple[Instance, int]:
    """A1: guarded rule from DECLARED centres only — cannot know realized deltas (tested)."""
    state = world["state"]
    disp, alias = q.features[1], q.features[2]
    work = 2
    target: Optional[str] = None
    if disp <= 0.35 - ANALYTIC_MARGIN:
        target = "window"; work += 1
    elif disp >= 0.55 + ANALYTIC_MARGIN and alias <= 0.30 - ANALYTIC_MARGIN:
        target = "deepwindow"; work += 2
    elif 0.42 + ANALYTIC_MARGIN <= disp <= 0.65 - ANALYTIC_MARGIN and alias <= 0.32 - ANALYTIC_MARGIN:
        target = "sample"; work += 3
    # no-branch / guarded-refusal fallback: cheapest ALWAYS-PASS (exact) family, never an
    # approximate family that can fail and then pay the scan fallback on top
    exact = min((it for it in insts if it.family in EXACT_FAMILIES),
                key=lambda it: (it.declared_cost_estimate(q, state), it.op_id))
    exact_cost = exact.declared_cost_estimate(q, state)
    work += 3
    if target is not None:
        cand = cheapest(insts, q, state, target)
        if cand is not None:
            work += 3
            if cand.declared_cost_estimate(q, state) < exact_cost:
                return cand, work
    return exact, work


def run_arm_choice(world: Dict, q: Query, insts: Sequence[Instance], choice: Instance,
                   inference_work: int, feature_work: int) -> Dict:
    """Charge one routed query: exec + verify + fallback-to-scan on FAIL + overheads."""
    w, ok = execute_via_spec(world, choice, q)
    exec_work = w + VERIFY_WORK
    fallback = False
    if not ok:
        scan = next(it for it in insts if it.family == "scan")
        w2, _ = execute_via_spec(world, scan, q)
        exec_work += w2 + VERIFY_WORK
        fallback = True
    return {"choice": choice, "family": choice.family, "exec_work": exec_work,
            "fallback": fallback, "passed_first": ok,
            "inference_work": inference_work, "feature_work": feature_work}
