"""FNA-8/D9 task world WL1: one obligation surface solved at every ladder rung.

Hooks the SAME production objects the FNA-1/FNA-5 capsules hook —
``ocm.runtime.solve.OperatorSpec`` as the catalogue record and
``ocm.runtime.operator_index.SolveOperatorIndex.select()`` as the structural
applicability query surface — with a catalogue in which several method families
compete for one numeric obligation (weighted-mass AGG / THRESH) and differ in
counted execution work and checker outcome. Additive extension inside this
capsule only; no shared file is edited. World idiom follows fna5_world.py
(dict world, callable backends, collector-counted work).

Everything is deterministic under the frozen salt: all randomness flows through
md5-derived seeds, all iteration over unordered collections is sorted, and no
``hash()`` call is used. Capsule code is Python 3.8-syntax stdlib only (plus the
two incumbent imports).

Declared physics (frozen BEFORE any outcome access; see PROTOCOL.md):
- scan    exact, always applicable (empty input set), work = base*m*sm + unit*sm*n.
- probe   exact, anchor-conditional (index select), work = base + unit*(2*(log2 n + 3) + min(n,12)).
- window  approximate, work = base + unit*W;  PASS iff disp + 0.12*(u-0.5) <= theta1_eff(W).
- sample  approximate, work = base + unit*k;  PASS iff alias + 0.12*(u-0.5) <= theta3s
                                                      AND disp in [theta4, theta7] band.
Realized thetas are seeded draws around DECLARED design centres; only the
declared centres are public to every arm (model arms included). The checker is
exact with an O(slice) certificate: it recomputes the true weighted mass once
and compares exactly (failures are always caught, never delivered). A failed
attempt is charged, then the frozen portfolio-recovery fallback executes scan.

Drift event (frozen): after EVAL, catalogue mutation — window:40 removed,
sample:24 added, scan law x1.6. Revocation event (frozen): REV_ATOM evidence
voided (weight 0); queries whose slice contains it are re-answered on REV.
"""
from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable, Dict, List, Optional, Tuple

from ocm.runtime.operator_index import SolveOperatorIndex
from ocm.runtime.solve import OperatorSpec

SALT = "fna8-privilege-ladder-v1::b41d7e2c"
SCHEMA = "ocm.fna.fna8-privilege-ladder.v1"
FAMILIES = ("scan", "probe", "window", "sample")
EXACT_FAMILIES = ("scan", "probe")  # always-PASS families (legal safe fallback)
VERIFY_WORK_PER_ATOM = 1            # exact certificate: one pass over the slice
COMMIT_GATE_WORK = 4                # incumbent commitment-gate accounting
TYPE_POOLS = ("alpha", "beta", "gamma", "delta")
WEIGHT_RANGES = {"alpha": (0.20, 0.40), "beta": (0.20, 1.00),
                 "gamma": (0.20, 0.80), "delta": (0.47, 0.53)}
DECLARED_CENTRES = {"theta1c": 0.35, "theta3s": 0.30, "theta4": 0.42, "theta7": 0.65}


def derive_seed(*parts: str) -> int:
    digest = hashlib.md5((SALT + "::" + "::".join(parts)).encode("utf-8")).hexdigest()
    return int(digest, 16)


def split_of(qid: str) -> str:
    """Frozen DEV/EVAL/DRIFT assignment by salted hash — disjoint by construction."""
    bucket = int(hashlib.md5((SALT + "::split::" + qid).encode("utf-8")).hexdigest(), 16) % 10
    return "DEV" if bucket <= 2 else ("EVAL" if bucket <= 7 else "DRIFT")


@dataclass(frozen=True)
class WorldParams:
    n_queries: int = 240
    n_atoms: int = 120
    tiny: bool = False

    @staticmethod
    def tiny_params() -> "WorldParams":
        return WorldParams(n_queries=40, n_atoms=48, tiny=True)


@dataclass
class Atom:
    atom_id: str
    pool: str
    weight: Fraction          # exact rational weight (2-decimal draws)
    revoked: bool = False


@dataclass
class Query:
    qid: str
    slice_ids: Tuple[str, ...]
    task_flag: bool           # True = AGG (report mass), False = THRESH (vs theta_q)
    theta_q: Optional[Fraction]
    anchor_probe0: str        # probe:0 anchor (structural applicability input)
    anchor_probe1: str
    n: int = 0
    disp: float = 0.0
    alias: float = 0.0
    u: float = 0.0            # per-query latent noise in the boundary band

    def true_mass(self, atoms: Dict[str, Atom]) -> Fraction:
        total = Fraction(0)
        for aid in self.slice_ids:
            a = atoms[aid]
            if not a.revoked:
                total += a.weight
        return total

    def exact_answer(self, atoms: Dict[str, Atom]):
        m = self.true_mass(atoms)
        if self.task_flag:
            return ("AGG", m)
        return ("THRESH", m, m >= self.theta_q)


@dataclass
class Instance:
    op_id: str
    family: str
    anchor: Optional[str]     # None = empty input set (always applicable)
    param: int                # W for window, k for sample, 0 otherwise
    base_cost: float
    unit_cost: float
    realized: Dict[str, float] = field(default_factory=dict)
    spec: Optional[OperatorSpec] = None

    def declared_cost_estimate(self, q: Query, state: Dict[str, float]) -> float:
        """Closed-form prediction from the DECLARED law (legal for any arm)."""
        n = max(q.n, 2)
        m = 1.1 if q.task_flag else 1.0
        base = self.base_cost * m
        if self.family == "scan":
            sm = state["scan_version_mult"]
            return base * sm + self.unit_cost * sm * q.n
        if self.family == "probe":
            return base + self.unit_cost * (2 * (math.log2(n) + 3) + min(n, 12))
        if self.family in ("window", "sample"):
            return base + self.unit_cost * self.param
        raise ValueError(self.family)


def _theta1_eff(w: int, realized: Dict[str, float]) -> float:
    """Declared window law: effectiveness grows with W, saturating at theta1c+0.18."""
    return realized["theta1c"] + 0.18 * (1.0 - math.exp(-w / 40.0))


def _catalogue(state: Dict[str, float], anchors: Tuple[str, str]) -> List[Instance]:
    cat = [
        Instance("probe:0", "probe", anchors[0], 0, 16.0, 2.4),
        Instance("probe:1", "probe", anchors[1], 0, 20.0, 2.0),
        Instance("window:16", "window", None, 16, 8.0, 1.3),
        Instance("window:40", "window", None, 40, 9.0, 1.1),
        Instance("sample:12", "sample", None, 12, 14.0, 2.2),
        Instance("scan", "scan", None, 0, 34.0, 1.0),
    ]
    if state.get("drift", False):
        cat = [i for i in cat if i.op_id != "window:40"]
        cat.append(Instance("sample:24", "sample", None, 24, 15.0, 2.0))
    for inst in cat:
        rng = random.Random(derive_seed("realize", inst.op_id,
                                        "drift" if state.get("drift") else "main"))
        realized = dict(DECLARED_CENTRES)
        realized["theta1c"] = rng.uniform(DECLARED_CENTRES["theta1c"] - 0.08,
                                          DECLARED_CENTRES["theta1c"] + 0.08)
        realized["theta3s"] = rng.uniform(DECLARED_CENTRES["theta3s"] - 0.05,
                                          DECLARED_CENTRES["theta3s"] + 0.05)
        realized["theta4"] = rng.uniform(DECLARED_CENTRES["theta4"] - 0.05,
                                         DECLARED_CENTRES["theta4"] + 0.05)
        realized["theta7"] = rng.uniform(DECLARED_CENTRES["theta7"] - 0.04,
                                         DECLARED_CENTRES["theta7"] + 0.04)
        inst.realized = realized
    return cat


def build_world(params: WorldParams) -> Dict:
    """Deterministic world dict: atoms, queries, catalogue, index, counted build work."""
    rng_atoms = random.Random(derive_seed("atoms"))
    atoms: Dict[str, Atom] = {}
    for i in range(params.n_atoms):
        pool = TYPE_POOLS[i % len(TYPE_POOLS)]
        lo, hi = WEIGHT_RANGES[pool]
        w = Fraction(round(rng_atoms.uniform(lo, hi), 2)).limit_denominator(100)
        atoms["a%04d" % i] = Atom("a%04d" % i, pool, w)
    rng_anchor = random.Random(derive_seed("anchors"))
    anchors = tuple(sorted(rng_anchor.sample(sorted(atoms.keys()), 2)))
    queries: List[Query] = []
    for j in range(params.n_queries):
        qid = "q%04d" % j
        rng = random.Random(derive_seed("query", qid))
        size = rng.randint(6, 24)
        ids = sorted(rng.sample(sorted(atoms.keys()), size))
        task_flag = rng.random() < 0.5
        n = len(ids)
        weights = sorted(float(atoms[a].weight) for a in ids)
        mean = sum(weights) / n
        disp = sum(abs(w - mean) for w in weights) / (mean * n) if mean else 0.0
        dup = sum(1 for a, b in zip(weights, weights[1:]) if abs(a - b) < 1e-9)
        alias = dup / max(n - 1, 1)
        theta_q = None
        if not task_flag:
            tm = float(sum(atoms[a].weight for a in ids))
            theta_q = Fraction(round(rng.uniform(tm * 0.85, tm * 1.15), 2)).limit_denominator(100)
        queries.append(Query(qid=qid, slice_ids=tuple(ids), task_flag=task_flag,
                             theta_q=theta_q, anchor_probe0=anchors[0], anchor_probe1=anchors[1],
                             n=n, disp=disp, alias=alias, u=rng.random()))
    main_state = {"scan_version_mult": 1.0, "drift": False}
    world = {"params": params, "atoms": atoms, "queries": queries, "anchors": anchors,
             "state": main_state, "index": None, "index_build_work": 0, "collector": None}
    rebuild_index(world)
    return world


def rebuild_index(world: Dict) -> None:
    """(Re)build the REAL SolveOperatorIndex over the current catalogue; charge build work."""
    state = world["state"]
    collector = {"work": 0}

    def backend_for(instance: Instance) -> Callable:
        def backend(ks, operator_id, ctx):
            passed, work, _ = execute_instance(instance, ctx["query"], world["atoms"], state)
            collector["work"] += work
            return {"passed": passed, "exec_work": work}
        return backend

    world["catalogue"] = _catalogue(state, world["anchors"])
    ops = []
    for it in world["catalogue"]:
        inputs = () if it.anchor is None else (it.anchor,)
        it.spec = OperatorSpec(it.op_id, "1", backend_for(it), inputs)
        ops.append(it.spec)
    world["index"] = SolveOperatorIndex(tuple(ops))
    world["index_build_work"] = sum(world["index"].build_work.values())
    world["collector"] = collector


def applicable(world: Dict, q: Query) -> Tuple[List[Instance], Dict[str, int]]:
    """Real structural-applicability surface: SolveOperatorIndex.select over the
    active slice atoms, then declared param constraints (W<=n, k<=n)."""
    sel = world["index"].select(list(q.slice_ids))
    by_id = {it.op_id: it for it in world["catalogue"]}
    insts = []
    for op in sel.operators:
        it = by_id.get(op.operator_id)
        if it is None:
            continue
        if it.family in ("window", "sample") and it.param > q.n:
            continue
        insts.append(it)
    return sorted(insts, key=lambda i: i.op_id), dict(sel.work)


def execute_instance(inst: Instance, q: Query, atoms: Dict[str, Atom],
                     state: Dict[str, float]) -> Tuple[bool, int, object]:
    """Execute one instance: (pass?, counted exec work, produced answer)."""
    m = 1.1 if q.task_flag else 1.0
    if inst.family == "scan":
        work = int(inst.base_cost * m * state["scan_version_mult"]) + int(
            inst.unit_cost * state["scan_version_mult"] * q.n)
        return True, work, _answer(q, q.true_mass(atoms))
    if inst.family == "probe":
        work = int(inst.base_cost * m) + int(inst.unit_cost * (
            2 * (math.log2(max(q.n, 2)) + 3) + min(q.n, 12)))
        return True, work, _answer(q, q.true_mass(atoms))
    if inst.family == "window":
        work = int(inst.base_cost * m) + int(inst.unit_cost * inst.param)
        ok = (q.disp + 0.12 * (q.u - 0.5)) <= _theta1_eff(inst.param, inst.realized)
        return ok, work, _answer(q, _approx_mass(q, atoms, inst.param))
    if inst.family == "sample":
        work = int(inst.base_cost * m) + int(inst.unit_cost * inst.param)
        ok = ((q.alias + 0.12 * (q.u - 0.5) <= inst.realized["theta3s"])
              and (inst.realized["theta4"] <= q.disp <= inst.realized["theta7"]))
        return ok, work, _answer(q, _approx_mass(q, atoms, inst.param))
    raise ValueError(inst.family)


def _approx_mass(q: Query, atoms: Dict[str, Atom], k: int) -> Fraction:
    """Approximate aggregate over the first k slice atoms scaled to n (declared bias)."""
    ids = list(q.slice_ids)[: min(k, q.n)]
    if not ids:
        return Fraction(0)
    part = Fraction(0)
    for aid in ids:
        a = atoms[aid]
        if not a.revoked:
            part += a.weight
    return part * Fraction(q.n, len(ids))


def _answer(q: Query, mass: Fraction):
    if q.task_flag:
        return ("AGG", mass)
    return ("THRESH", mass, mass >= q.theta_q)


def check(q: Query, atoms: Dict[str, Atom], produced) -> Tuple[bool, int]:
    """Exact O(slice) certificate: recompute once, compare exactly. Work charged."""
    truth = q.exact_answer(atoms)
    work = VERIFY_WORK_PER_ATOM * q.n + COMMIT_GATE_WORK
    try:
        if q.task_flag:
            ok = (isinstance(produced, tuple) and len(produced) == 2
                  and produced[0] == "AGG" and Fraction(produced[1]) == truth[1])
        else:
            ok = (isinstance(produced, tuple) and len(produced) == 3
                  and produced[0] == "THRESH" and Fraction(produced[1]) == truth[1]
                  and bool(produced[2]) == bool(truth[2]))
    except (TypeError, ValueError):
        ok = False
    return ok, work


def parse_proposal(text: str, legal_ids: List[str]) -> List[str]:
    """Parse the proposer's strict single-line reply -> ranked operator ids.

    Unknown ids are dropped (never repaired); an empty result raises ValueError.
    """
    stripped = text.strip()
    if not stripped:
        raise ValueError("empty model output")
    line = stripped.splitlines()[-1].strip()
    parts = [p.strip() for p in line.split("|")]
    if not parts or parts[0] != "PROP":
        raise ValueError("bad PROP format: %r" % line)
    ids = [p for p in parts[1:] if p in legal_ids]
    if not ids:
        raise ValueError("no legal operator id in proposal: %r" % line)
    seen = set()
    out = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def render_prompt(q: Query, world: Dict, example: Optional[Tuple[Query, object]] = None,
                  propose: bool = False) -> str:
    """Frozen R1/R2 controller interface: public query + declared catalogue only.

    Information surface (structurally tested): slice atoms (ids, pools, weights,
    revoked flags), declared cost laws, DECLARED design centres, the public
    task spec. Never realized thetas, never labels, never split membership.
    """
    cat = world["catalogue"]
    state = world["state"]
    lines = [
        "You are the CONTROLLER of an exact aggregation service.",
        "Obligation: over the listed atoms, mass = sum of weights of atoms with revoked=false.",
        "Task AGG: report mass exactly (at most 2 decimals).",
        "Task THRESH: report mass and whether mass >= theta.",
        "Operators (declared cost laws; APPROX ones may FAIL a hidden exact check):",
    ]
    for inst in sorted(cat, key=lambda i: i.op_id):
        kind = "EXACT" if inst.family in EXACT_FAMILIES else "APPROX"
        lines.append("  %s family=%s %s declared_cost=%.1f" % (
            inst.op_id, inst.family, kind, inst.declared_cost_estimate(q, state)))
    lines.append("Declared approximate-success centres (public design values): "
                 "theta1c(peak eff)=0.35 theta3s=0.30 band=[0.42,0.65]")
    lines.append("Query %s task=%s" % (
        q.qid, "AGG" if q.task_flag else "THRESH theta=%s" % q.theta_q))
    lines.append("Atoms (%d):" % q.n)
    for aid in q.slice_ids:
        a = world["atoms"][aid]
        lines.append("  %s pool=%s weight=%s revoked=%s" % (aid, a.pool, a.weight, a.revoked))
    if example is not None:
        eq, ea = example
        if eq.task_flag:
            tail = "%s" % ea[1]
        else:
            tail = "%s|%s" % (ea[1], "HIGH" if ea[2] else "LOW")
        lines.append("Worked example from the declared spec (%s, task=%s): ANS|%s" % (
            eq.qid, "AGG" if eq.task_flag else "THRESH", tail))
    if propose:
        lines.append(
            "PROPOSE mode: reply ONE line 'PROP|<op1>|<op2>|<op3>' ranking at most 3 "
            "operator ids, best-first by your judgement. The exact selector tests them "
            "in your order and commits the first that passes the exact check; if none "
            "passes, the safe scan runs.")
    else:
        lines.append(
            "CONTROL mode: choose exactly one operator to execute and compute its "
            "delivered answer yourself. Reply ONE line 'CTRL|<operator_id>|<mass>' (AGG) "
            "or 'CTRL|<operator_id>|<mass>|HIGH' / 'CTRL|<operator_id>|<mass>|LOW' "
            "(THRESH). Mass has at most 2 decimals. If your chosen operator fails the "
            "exact check, the safe scan runs and the failure is charged to you.")
    return "\n".join(lines)


def parse_controller_line(q: Query, text: str) -> Tuple[str, object]:
    """Parse the controller's strict single-line reply -> (operator_id, answer).

    Raises ValueError on any deviation — the caller records the parse failure;
    nothing is repaired or guessed (no fabricated model output, ever).
    """
    stripped = text.strip()
    if not stripped:
        raise ValueError("empty model output")
    line = stripped.splitlines()[-1].strip()
    parts = [p.strip() for p in line.split("|")]
    if not parts or parts[0] != "CTRL" or len(parts) < 3:
        raise ValueError("bad CTRL format: %r" % line)
    op_id = parts[1]
    if not op_id:
        raise ValueError("empty operator id: %r" % line)
    if q.task_flag:
        if len(parts) != 3:
            raise ValueError("bad AGG ctrl arity: %r" % line)
        return op_id, ("AGG", Fraction(parts[2]))
    if len(parts) != 4 or parts[3].upper() not in ("HIGH", "LOW"):
        raise ValueError("bad THRESH ctrl: %r" % line)
    return op_id, ("THRESH", Fraction(parts[2]), parts[3].upper() == "HIGH")
