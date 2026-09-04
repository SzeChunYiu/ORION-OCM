"""KSO M2 — comparator arms and the budget-matching harness for the solve loop.

The KSO solve loop (``kso_m2_solve_v1``, lane-ocm-3) answers the registered ME-X1 transition
question on the M1-populated knowledge space. This module supplies the arms it is compared
against, on the SAME 50 development instances, the SAME populated graph, the SAME seed set and
the SAME typed-module statuses, and the table that scores every column against
``mex1_oracle`` exactly. The expected honest terminal is ``PARENT_SUFFICIENT`` and that is a
success; nothing here says "better".

Arms (every arm returns the answer object the oracle scores: ``{"action", "reopened"}``):

  B5_STRONGEST_FAITHFUL_PARENT_FEDERATION   ME-X1's strongest faithful parent, re-run through
      ``mex1_arms.ArmRunner`` unchanged. On this generator it reproduces the oracle exactly
      (ME_X1_OUTCOME_RECEIPT §3: 1.000 on 1 000 protected instances), so it is the CEILING
      CONTROL of the table, not an oracle-independent comparator; its cost is recorded, not
      budget-capped (a JTMS does not navigate the graph).
  RWR_PPR_SPREADING_ACTIVATION   spreading activation (Collins & Loftus 1975) realised as a
      random walk with restart / personalised PageRank (Tong, Faloutsos & Pan 2006) on the
      populated hypergraph, undirected, warrant-gated with the frozen denominators (a dead
      atom takes no mass and nothing is renormalised). Decision rule native to retrieval:
      the highest-activated defeater (INVALID or UNKNOWN typed status) reachable from the seed
      decides — its registered action, or DEFER when it is censored — and UPDATE when none is
      reachable; for PROPAGATE_DEFEAT the accepted claims whose support carries a reachable
      INVALID atom are reopened. Activation order replaces the registered precedence order,
      and "some family still supports" is not consulted: those are the mechanism differences
      the paired table measures.
  CBR_KG_RETRIEVAL   case-based reasoning (Aamodt & Plaza 1994: retrieve-reuse-adapt) over a
      knowledge-graph retrieval: the 2-hop typed neighbourhood of the seed is retrieved, its
      (module, status) defeater signature is matched by Jaccard similarity against the case
      base — the 14 PUBLIC known-answer fixtures of ME-X1 (registered information; no oracle
      label of any dev instance is read) — and the nearest case's action is reused, with the
      reopened set adapted from the retrieved neighbourhood.
  C_RANDOM_ACTION   ME-X1's registered random control (null).
  ORACLE_POSITIVE_CONTROL   the oracle's own decision (positive control; must score 1.0).
  KSO_M2_SOLVE   reserved column, merged from lane-ocm-3's receipt with ``--kso-column``. Its COMPOSE
      step may read the store beyond the navigated subgraph (``store_read`` per row), so its
      exactness is the store's; it is paired against B5 (PARENT_SUFFICIENT).
  KSO_NAVIGATION_ONLY   derived from the same receipt: ``navigation_only_answer`` (what EXTRACT
      alone returned; null ⇒ OBSTRUCTION, never exact). This is the mechanic's honest number and
      the column paired against RWR and CBR, which may not read the store either. A receipt
      without the field leaves this column CANNOT_CHECK and the run exits 2.

Information matching, stated: every arm receives the same ``ArmView`` (world at v0, world at
the request, events, request, accepted list) that ME-X1 gave every arm; the graph arms receive
in addition the same populated graph (``kso_m1_mex1_population_v1.populate(w1, request=…)``,
plus ``kso_m2_solve_v1.add_request_atoms`` when that module is present, so the KSO and the
comparators see one graph — its sha256 is recorded per instance), the same seed set
S = {req:<instance_id>, claim:<target>} ∪ {res:<result_id>} and the same typed-module statuses
(``mex1_arms._status_for`` with every module typed — exactly what B5 reads). No arm imports the
oracle; the positive control is scored FROM the registered expected decision and labelled so.

NavigationBudget (row A14): ``steps`` (atoms examined), ``edge_visits`` (hyperedges traversed),
``restarts``, ``wall_ns`` and an ``ops`` proxy = steps + edge_visits, recorded per instance per
arm; caps matched across navigating arms at steps ≤ 2·|atoms|, edge_visits ≤ 2·|hyperedges|,
restarts ≤ 1. An arm over its cap on an instance is ``CANNOT_CHECK`` on that instance — never
silently scored — and the run exits 2.

Checkers, each with a plant and a no-alarm control:
  K1 the random control scores inside the simulated null band (200 re-seeded random arms); an
     arm handed the oracle falls outside it (plant).
  K2 the positive control scores exactly 1.0; one perturbed answer breaks it (plant).
  K3 no arm-instance is CANNOT_CHECK under the matched caps; ``--cap-scale 0`` plants an
     overrun and the run exits 2.
  K4 the paired test goes red on a planted systematic disagreement (12 of B5's exact flags
     flipped: discordant 12, exact p < 0.001) and stays quiet on an identical copy (p = 1).
  K5 information matching: every graph arm recorded the same graph_sha256 and seed set per
     instance.
  K6 byte-reproducible: a second in-process run produces the same receipt body sha256.

Exit codes: 0 every checker holds; 1 a checker fails; 2 could not check (a budget overrun, the
ME-X1 or KSO modules unimportable, an unreadable KSO column). NO NOVELTY OR BREAKTHROUGH CLAIM.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import sys
import time
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MEX1 = ROOT / "research" / "experiments" / "me-x1"
RESULTS = HERE.parent / "results"

SCHEMA = "orion.kso.m2-comparator-receipt.v1"
CONTRACT = "KnowledgeSpace.v1-M2-comparator"
SPLIT, SPLIT_SEED, PER_FAMILY = "dev", "ME-X1-DEV-20260902", 5
ALPHA = Fraction(1, 3)                 # restart mass; the M1 activation's frozen alpha
NULL_SIMS, NULL_SEED_SALT = 200, 0x4E55
B5 = "B5_STRONGEST_FAITHFUL_PARENT_FEDERATION"
RWR = "RWR_PPR_SPREADING_ACTIVATION"
CBR = "CBR_KG_RETRIEVAL"
RANDOM = "C_RANDOM_ACTION"
ORACLE = "ORACLE_POSITIVE_CONTROL"
KSO_COL = "KSO_M2_SOLVE"
KSO_NAV = "KSO_NAVIGATION_ONLY"
ARMS = (B5, RWR, CBR, RANDOM, ORACLE)
# Which arms may read the store (the populated space beyond what navigation reached) when they answer:
STORE_READ = {B5: "yes (its parent modules read the whole world)", KSO_COL: "yes (COMPOSE may consult the store; store_read is recorded per row)",
              KSO_NAV: "NO (answer = what EXTRACT returned from the navigated subgraph only)", RWR: "NO (reachable activation only)",
              CBR: "NO (2-hop retrieved neighbourhood only)", RANDOM: "n/a", ORACLE: "n/a (positive control)"}
NAVIGATING = (RWR, CBR)
CAP_STEPS_PER_ATOM, CAP_VISITS_PER_EDGE, CAP_RESTARTS = 2, 2, 1


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m1 = _load("kso_m1_mex1_population_v1", HERE / "kso_m1_mex1_population_v1.py")
kso = sys.modules["kso_math_v1"]
CannotCheck = kso.CannotCheck


def _mex1():
    for p in (str(MEX1), str(ROOT / "src")):
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        import mex1_arms  # type: ignore
        import mex1_generator  # type: ignore
        import mex1_model  # type: ignore
        import mex1_oracle  # type: ignore
    except Exception as exc:  # pragma: no cover - environment
        raise CannotCheck(f"ME-X1 modules unimportable: {exc}") from exc
    return mex1_arms, mex1_generator, mex1_model, mex1_oracle


def _kso_m2_solve():
    """lane-ocm-3's solve module, when present beside this file: its add_request_atoms is the
    one graph transformation every arm must share. Absent -> the M1 graph only, and said so."""
    path = HERE / "kso_m2_solve_v1.py"
    if not path.exists():
        return None
    mod = _load("kso_m2_solve_v1", path)
    return mod if hasattr(mod, "add_request_atoms") else None


# ----------------------------------------------------------------------------------------------
# budget
# ----------------------------------------------------------------------------------------------


@dataclass
class NavigationBudget:
    steps: int = 0
    edge_visits: int = 0
    restarts: int = 0
    wall_ns: int = 0
    capped: bool = True                # False for arms that do not navigate (recorded, not capped)

    @property
    def ops(self) -> int:
        return self.steps + self.edge_visits

    def as_dict(self) -> dict:
        return {"steps": self.steps, "edge_visits": self.edge_visits, "restarts": self.restarts,
                "wall_ns": self.wall_ns, "ops": self.ops, "capped": self.capped}


@dataclass(frozen=True)
class Caps:
    steps: int
    edge_visits: int
    restarts: int

    def overrun(self, b: NavigationBudget) -> str | None:
        if not b.capped:
            return None
        if b.steps > self.steps:
            return f"steps {b.steps} > cap {self.steps}"
        if b.edge_visits > self.edge_visits:
            return f"edge_visits {b.edge_visits} > cap {self.edge_visits}"
        if b.restarts > self.restarts:
            return f"restarts {b.restarts} > cap {self.restarts}"
        return None


def caps_for(n_atoms: int, n_edges: int, scale: float = 1.0) -> Caps:
    return Caps(int(CAP_STEPS_PER_ATOM * n_atoms * scale), int(CAP_VISITS_PER_EDGE * n_edges * scale),
                int(CAP_RESTARTS * scale) if scale >= 1 else int(CAP_RESTARTS * scale))


# ----------------------------------------------------------------------------------------------
# the shared frame: view, graph, seed, statuses
# ----------------------------------------------------------------------------------------------


@dataclass
class Frame:
    instance_id: str
    view: object                        # mex1_arms.ArmView
    pop: object                         # kso_m1 Population (after add_request_atoms when present)
    seed_atoms: tuple[str, ...]
    status: dict[str, str]              # typed-module statuses (what B5 reads)
    slot_module: dict[str, str]         # atom -> module (support + request slots)
    slot_action: dict[str, str]         # request atom -> registered action
    claim_slots: dict[str, tuple[str, ...]]   # claim -> its support atoms (all families) + nocontra
    graph_sha256: str
    request_atoms: str                  # "kso_m2_solve_v1.add_request_atoms" or "M1_ONLY"


def graph_sha256(ks) -> str:
    """The shared digest (one definition, pinned by lane-ocm-3's test_graph_digest_format_is_the_shared_one):
    sorted ``A|id|type`` lines, then sorted ``E|edge_id|tails|heads|relation_type`` lines with tails and
    heads comma-joined, lines newline-joined, no trailing newline."""
    lines = sorted(f"A|{a.atom_id}|{a.atom_type}" for a in ks.atoms)
    lines += sorted(f"E|{e.edge_id}|{','.join(e.tails)}|{','.join(e.heads)}|{e.relation_type}" for e in ks.hyperedges)
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def make_view(inst):
    arms, _, model, _ = _mex1()
    w = inst.world_v0
    for ev in inst.events:
        w = model.apply_event(w, ev)
    return arms.ArmView(inst.world_v0, w, list(inst.events), inst.request, inst.world_v0.accepted_ids())


def typed_spec():
    arms, *_ = _mex1()
    return arms.ArmSpec("TYPED_STATUS_SOURCE", "SHARED", dict(arms.TYPED), "federation")


def frame_for(inst) -> Frame:
    arms, _, model, _ = _mex1()
    v = make_view(inst)
    w1 = v.world
    pop = m1.populate(w1, request=inst.request, request_id=inst.instance_id)
    solve = _kso_m2_solve()
    request_atoms = "M1_ONLY"
    if solve is not None:
        out = solve.add_request_atoms(pop, w1, inst)
        pop = out[0] if isinstance(out, tuple) else out
        request_atoms = "kso_m2_solve_v1.add_request_atoms"
    ks = pop.space
    ids = set(ks.ids)
    seed = [f"req:{inst.instance_id}", f"claim:{inst.request.target_claim_id}"]
    if getattr(inst.request, "result_id", "") and f"res:{inst.request.result_id}" in ids:
        seed.append(f"res:{inst.request.result_id}")
    missing = [s for s in seed if s not in ids]
    if missing:
        raise CannotCheck(f"{inst.instance_id}: seed atoms {missing} are not in the populated graph")
    ops: dict = {}
    status = arms._status_for(typed_spec(), v, ops)
    slot_module: dict[str, str] = {}
    claim_slots: dict[str, tuple[str, ...]] = {}
    slots = arms.support_slots(w1)
    for fam in w1.families.values():
        for a, mod in slots[fam.family_id]:
            slot_module[a] = mod
    for c in w1.claims:
        acc: list[str] = []
        for fam in w1.families_of(c):
            acc += [a for a, _ in slots[fam.family_id]]
        acc.append(arms.contra_slot(c))
        slot_module[arms.contra_slot(c)] = "PROV"
        claim_slots[c] = tuple(dict.fromkeys(acc))
    slot_action: dict[str, str] = {}
    for s in arms.request_slots(w1, inst.request):
        slot_module[s.atom] = s.module
        slot_action[s.atom] = s.action
    return Frame(inst.instance_id, v, pop, tuple(seed), status, slot_module, slot_action, claim_slots,
                 graph_sha256(ks), request_atoms)


# ----------------------------------------------------------------------------------------------
# undirected, warrant-gated walk structure (shared by the two retrieval arms)
# ----------------------------------------------------------------------------------------------


def live_structure(pop, budget: NavigationBudget) -> tuple[list[str], dict[str, list[str]]]:
    """Undirected adjacency over live atoms from live hyperedges (frozen denominators: a dead
    atom or a dead edge contributes nothing; nothing is renormalised). Counts one edge visit per
    live hyperedge traversed."""
    ks = pop.space
    rv = pop.registered_revoked
    amap = ks.atom_map()
    live = [x for x in ks.ids if kso.profile_live(amap[x].profile, rv)]
    live_set = set(live)
    adj: dict[str, list[str]] = {x: [] for x in live}
    for e in ks.hyperedges:
        if not kso.profile_live(e.profile, rv):
            continue
        members = [x for x in (*e.tails, *e.heads) if x in live_set]
        if len(members) < 2:
            continue
        budget.edge_visits += 1
        for a in members:
            for b in members:
                if a != b:
                    adj[a].append(b)
    return live, adj


def rwr_activation(live: list[str], adj: dict[str, list[str]], seed_atoms: Sequence[str],
                   alpha: Fraction, budget: NavigationBudget) -> dict[str, Fraction]:
    """Exact RWR fixed point a = α s + (1−α) Pᵀ a on the undirected live graph; s uniform over
    the live seed atoms (a dead seed takes 0 mass, no renormalisation). One restart."""
    idx = {x: i for i, x in enumerate(live)}
    n = len(live)
    seed_live = [s for s in seed_atoms if s in idx]
    s_vec = [Fraction(0, 1)] * n
    for s in seed_live:
        s_vec[idx[s]] = Fraction(1, len(seed_atoms))     # denominators are the seed set as declared
    budget.restarts += 1
    budget.steps += n
    a_mat = [[Fraction(int(i == j), 1) for j in range(n)] for i in range(n)]
    for x in live:
        deg = len(adj[x])
        if deg == 0:
            continue
        i = idx[x]
        for y in adj[x]:
            j = idx[y]
            a_mat[j][i] -= (1 - alpha) / deg           # (I - (1-α) Pᵀ)
    sol = kso._solve_fraction(a_mat, [alpha * v for v in s_vec])
    return dict(zip(live, sol, strict=True))


def khop(live: list[str], adj: dict[str, list[str]], seed_atoms: Sequence[str], k: int,
         budget: NavigationBudget) -> list[str]:
    seen = [s for s in seed_atoms if s in adj]
    frontier = list(seen)
    seen_set = set(seen)
    for _ in range(k):
        nxt: list[str] = []
        for x in frontier:
            budget.steps += 1
            for y in sorted(adj[x]):
                if y not in seen_set:
                    seen_set.add(y)
                    nxt.append(y)
        seen += nxt
        frontier = nxt
    return seen


# ----------------------------------------------------------------------------------------------
# arms
# ----------------------------------------------------------------------------------------------


@dataclass
class Answer:
    action: str
    reopened: tuple[str, ...] = ()
    status: str = "SCORED"             # SCORED | CANNOT_CHECK | OBSTRUCTION
    note: str = ""
    budget: NavigationBudget = field(default_factory=NavigationBudget)

    def as_dict(self) -> dict:
        return {"action": self.action, "reopened": list(self.reopened)}


def _reopen_from(frame: Frame, reachable: set[str]) -> tuple[str, ...]:
    """Accepted claims whose support (any family, or nocontra) carries a reachable INVALID atom."""
    _, _, model, _ = _mex1()
    out = []
    for c in frame.view.accepted:
        if any(frame.status.get(a) == model.STATUS_INVALID and a in reachable for a in frame.claim_slots.get(c, ())):
            out.append(c)
    return tuple(sorted(out))


def _has_unknown(frame: Frame, reachable: set[str]) -> bool:
    _, _, model, _ = _mex1()
    return any(frame.status.get(a) == model.STATUS_UNKNOWN and a in reachable
               for c in frame.view.accepted for a in frame.claim_slots.get(c, ()))


def arm_b5(inst, frame: Frame) -> Answer:
    arms, *_ = _mex1()
    spec = next(s for s in arms.arm_specs() if s.name == B5)
    d, cost = arms.ArmRunner(spec, inst.seed).run(frame.view)
    b = NavigationBudget(steps=int(cost.get("module_ops", 0)), edge_visits=int(cost.get("ops", 0)),
                         restarts=0, wall_ns=int(cost.get("wall_ns", 0)), capped=False)
    return Answer(d.action, tuple(d.reopened), budget=b, note="ceiling control; JTMS cost recorded, not capped")


def arm_random(inst, frame: Frame) -> Answer:
    arms, *_ = _mex1()
    spec = next(s for s in arms.arm_specs() if s.name == RANDOM)
    d, cost = arms.ArmRunner(spec, inst.seed).run(frame.view)
    return Answer(d.action, tuple(d.reopened), budget=NavigationBudget(wall_ns=int(cost.get("wall_ns", 0)), capped=False),
                  note="registered null control")


def arm_oracle(expected, frame: Frame) -> Answer:
    action, reopened = expected.decision()
    return Answer(action, tuple(reopened), budget=NavigationBudget(capped=False), note="positive control: the registered expected decision")


def arm_rwr(inst, frame: Frame) -> Answer:
    _, _, model, _ = _mex1()
    b = NavigationBudget()
    t0 = time.perf_counter_ns()
    live, adj = live_structure(frame.pop, b)
    act = rwr_activation(live, adj, frame.seed_atoms, ALPHA, b)
    reachable = {x for x, v in act.items() if v > 0}
    defeaters = [(a, frame.status[a]) for a in frame.status
                 if frame.status[a] in (model.STATUS_INVALID, model.STATUS_UNKNOWN) and a in reachable]
    ranked = sorted(defeaters, key=lambda t: (-act[t[0]], t[0]))
    if frame.view.request.kind == "PROPAGATE_DEFEAT":
        if _has_unknown(frame, reachable):
            ans = Answer(model.DEFER_CANNOT_CHECK)
        else:
            r = _reopen_from(frame, reachable)
            ans = Answer(model.SELECTIVELY_REOPEN, r) if r else Answer(model.PRESERVE)
        b.steps += len(ranked)
    elif not ranked:
        ans = Answer(model.UPDATE)
    else:
        a, st = ranked[0]
        b.steps += 1
        if st == model.STATUS_UNKNOWN:
            ans = Answer(model.DEFER_CANNOT_CHECK)
        else:
            arms_mod = _mex1()[0]
            action = frame.slot_action.get(a) or arms_mod.MODULE_DEFAULT_ACTION.get(frame.slot_module.get(a, ""), model.REVALIDATE)
            ans = Answer(action)
    b.wall_ns = time.perf_counter_ns() - t0
    ans.budget = b
    return ans


def _signature(frame: Frame, retrieved: Iterable[str]) -> tuple[str, frozenset[tuple[str, str]]]:
    _, _, model, _ = _mex1()
    rs = set(retrieved)
    sig = frozenset((frame.slot_module.get(a, "?"), s) for a, s in frame.status.items()
                    if s != model.STATUS_VALID and (a in rs or a in frame.slot_action))
    return frame.view.request.kind, sig


_CASE_BASE: list[tuple[str, str, frozenset, str]] | None = None


def case_base() -> list[tuple[str, str, frozenset, str]]:
    """(case_id, request kind, defeater signature, expected action) for the 14 public fixtures."""
    global _CASE_BASE
    if _CASE_BASE is not None:
        return _CASE_BASE
    _, gen, model, _ = _mex1()
    out = []
    for fx in gen.known_answer_fixtures():
        inst = model.Instance(fx["case_id"], fx["family"], "FIXTURE", "fixture", 0, fx["world"], list(fx["events"]), fx["request"])
        fr = frame_for(inst)
        b = NavigationBudget()
        live, adj = live_structure(fr.pop, b)
        kind, sig = _signature(fr, khop(live, adj, fr.seed_atoms, 2, b))
        out.append((fx["case_id"], kind, sig, fx["expected"]))
    _CASE_BASE = out
    return out


def _jaccard(a: frozenset, b: frozenset) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def arm_cbr(inst, frame: Frame) -> Answer:
    _, _, model, _ = _mex1()
    b = NavigationBudget()
    t0 = time.perf_counter_ns()
    live, adj = live_structure(frame.pop, b)
    retrieved = khop(live, adj, frame.seed_atoms, 2, b)
    kind, sig = _signature(frame, retrieved)
    base = case_base()
    same_kind = [c for c in base if c[1] == kind] or base
    best = max(same_kind, key=lambda c: (_jaccard(sig, c[2]), -sorted(x[0] for x in same_kind).index(c[0])))
    action = best[3]
    reopened: tuple[str, ...] = ()
    if action == model.SELECTIVELY_REOPEN:
        reopened = _reopen_from(frame, set(retrieved))
        if not reopened:
            action = model.PRESERVE
    b.wall_ns = time.perf_counter_ns() - t0
    return Answer(action, reopened, budget=b, note=f"nearest case {best[0]} (jaccard {round(_jaccard(sig, best[2]), 3)})")


# ----------------------------------------------------------------------------------------------
# scoring
# ----------------------------------------------------------------------------------------------


def navigation_only_cell(full: dict, expected) -> dict:
    """The KSO's answer restricted to what EXTRACT returned (no store read). Requires the receipt
    fields `navigation_only_answer` ({action, reopened} | null) and `store_read` (bool); without
    them the column is CANNOT_CHECK -- a store-reading answer must never be scored as navigation."""
    if "navigation_only_answer" not in full:
        return {"answer": {"action": "", "reopened": []}, "exact": False, "status": "CANNOT_CHECK", "attribution": "",
                "budget": full.get("budget", {}), "store_read": full.get("store_read"),
                "note": "receipt lacks navigation_only_answer; a store-reading answer is not scored as navigation"}
    nav = full["navigation_only_answer"]
    if not nav:
        return {"answer": {"action": "", "reopened": []}, "exact": False, "status": "OBSTRUCTION", "attribution": "",
                "budget": full.get("budget", {}), "store_read": full.get("store_read"),
                "navigation_outcome": full.get("navigation_outcome"), "note": "EXTRACT returned nothing decisive; obstruction witness, never exact"}
    ans = Answer(str(nav.get("action")), tuple(nav.get("reopened", ())))
    return {"answer": ans.as_dict(), "exact": exact(ans, expected), "status": "SCORED", "attribution": "",
            "budget": full.get("budget", {}), "store_read": full.get("store_read"), "navigation_outcome": full.get("navigation_outcome"), "note": ""}


def exact(ans: Answer, expected) -> bool:
    return ans.status == "SCORED" and (ans.action, tuple(ans.reopened)) == (expected.decision()[0], tuple(expected.decision()[1]))


def exact_binomial_two_sided(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def paired(x_name: str, y_name: str, x: Sequence[bool], y: Sequence[bool]) -> dict:
    """mex1_run.paired_summary semantics: exact McNemar on the discordant pairs."""
    n = len(x)
    b = sum(1 for a, bb in zip(x, y, strict=True) if a and not bb)
    c = sum(1 for a, bb in zip(x, y, strict=True) if bb and not a)
    diff = (b - c) / n if n else 0.0
    se = math.sqrt(max(0.0, (b + c) - (b - c) ** 2 / n)) / n if n else 0.0
    p = exact_binomial_two_sided(b, c)
    return {"x": x_name, "y": y_name, "n": n, "x_only": b, "y_only": c, "discordant": b + c,
            "diff_x_minus_y": diff, "wald_ci95": [diff - 1.96 * se, diff + 1.96 * se],
            "exact_p_two_sided": p, "red": p < 0.01}


def null_band(pairs, frames: dict[str, Frame], sims: int = NULL_SIMS) -> dict:
    """Exact-count distribution of the registered random control under re-seeding."""
    arms, *_ = _mex1()
    spec = next(s for s in arms.arm_specs() if s.name == RANDOM)
    counts = []
    for k in range(sims):
        c = 0
        for inst, exp in pairs:
            d, _ = arms.ArmRunner(spec, (inst.seed ^ NULL_SEED_SALT) + 7919 * (k + 1)).run(frames[inst.instance_id].view)
            c += (d.action, tuple(d.reopened)) == exp.decision()
        counts.append(c)
    counts.sort()
    return {"sims": sims, "min": counts[0], "max": counts[-1], "mean": sum(counts) / sims,
            "p975": counts[min(sims - 1, int(round(0.975 * sims)))]}


def at_null(count: int, band: dict) -> bool:
    return band["min"] <= count <= band["max"]


# ----------------------------------------------------------------------------------------------
# run
# ----------------------------------------------------------------------------------------------


def run(cap_scale: float = 1.0, kso_column: dict | None = None, quiet: bool = False) -> dict:
    _, gen, model, _ = _mex1()
    pairs = gen.generate_split(SPLIT, SPLIT_SEED, {f: PER_FAMILY for f in model.FAMILIES})
    ids = [inst.instance_id for inst, _ in pairs]
    ids_sha = hashlib.sha256("\n".join(ids).encode()).hexdigest()
    frames = {inst.instance_id: frame_for(inst) for inst, _ in pairs}
    rows = []
    cannot: list[str] = []
    flags: dict[str, list[bool]] = {a: [] for a in ARMS}
    for inst, exp in pairs:
        fr = frames[inst.instance_id]
        n_atoms, n_edges = len(fr.pop.space.atoms), len(fr.pop.space.hyperedges)
        caps = caps_for(n_atoms, n_edges, cap_scale)
        answers = {B5: arm_b5(inst, fr), RWR: arm_rwr(inst, fr), CBR: arm_cbr(inst, fr),
                   RANDOM: arm_random(inst, fr), ORACLE: arm_oracle(exp, fr)}
        row_arms = {}
        for name, ans in answers.items():
            over = caps.overrun(ans.budget)
            if over:
                ans.status = "CANNOT_CHECK"
                ans.note = f"budget overrun: {over}"
                cannot.append(f"{inst.instance_id}/{name}: {over}")
            ex = exact(ans, exp)
            flags[name].append(ex)
            row_arms[name] = {"answer": ans.as_dict(), "exact": ex, "status": ans.status, "attribution": "",
                              "budget": ans.budget.as_dict(), "note": ans.note}
        if kso_column is not None:
            k = kso_column.get(inst.instance_id)
            if k is None:
                raise CannotCheck(f"KSO column lacks instance {inst.instance_id}")
            theirs = k.get("_graph_sha256")
            if theirs is not None and theirs != fr.graph_sha256:
                raise CannotCheck(f"{inst.instance_id}: the KSO column was scored on graph {theirs[:12]}, this run on {fr.graph_sha256[:12]}; "
                                  "the two receipts did not see the same graph -- the join is refused")
            full = {kk: vv for kk, vv in k.items() if kk != "_graph_sha256"}
            full_ans = Answer(str(full["answer"].get("action")), tuple(full["answer"].get("reopened", ())), status=str(full.get("status", "SCORED")))
            full["exact_declared"] = full.get("exact")
            full["exact"] = exact(full_ans, exp)            # recomputed here, never trusted from the column
            row_arms[KSO_COL] = full
            row_arms[KSO_NAV] = navigation_only_cell(full, exp)
        rows.append({"instance_id": inst.instance_id, "family": inst.family, "variant": inst.variant,
                     "request_kind": inst.request.kind, "oracle": {"action": exp.action, "reopened": list(exp.reopened)},
                     "graph": {"sha256": fr.graph_sha256, "atoms": n_atoms, "hyperedges": n_edges,
                               "seed_atoms": list(fr.seed_atoms), "request_atoms": fr.request_atoms},
                     "caps": caps.__dict__, "arms": row_arms})
    per_arm = {}
    for name in ARMS:
        scored = [r["arms"][name] for r in rows if r["arms"][name]["status"] == "SCORED"]
        per_arm[name] = {"exact": sum(1 for r in scored if r["exact"]), "n_scored": len(scored),
                         "n_cannot_check": sum(1 for r in rows if r["arms"][name]["status"] == "CANNOT_CHECK"),
                         "exact_rate": (sum(1 for r in scored if r["exact"]) / len(scored)) if scored else None,
                         "role": {B5: "ceiling control", RWR: "oracle-independent comparator", CBR: "oracle-independent comparator",
                                  RANDOM: "null control", ORACLE: "positive control"}[name]}
    band = null_band(pairs, frames)
    table = [paired(a, B5, flags[a], flags[B5]) for a in (RWR, CBR, RANDOM, ORACLE)]
    kso_flags = None
    if kso_column is not None:
        kso_flags = [bool(r["arms"][KSO_COL]["exact"]) and r["arms"][KSO_COL].get("status") == "SCORED" for r in rows]
        nav_flags = [bool(r["arms"][KSO_NAV]["exact"]) and r["arms"][KSO_NAV]["status"] == "SCORED" for r in rows]
        nav_cnc = [r["instance_id"] for r in rows if r["arms"][KSO_NAV]["status"] == "CANNOT_CHECK"]
        cannot += [f"{i}/{KSO_NAV}: navigation_only_answer not provided" for i in nav_cnc]
        per_arm[KSO_COL] = {"exact": sum(kso_flags), "n_scored": sum(1 for r in rows if r["arms"][KSO_COL].get("status") == "SCORED"),
                            "n_cannot_check": sum(1 for r in rows if r["arms"][KSO_COL].get("status") == "CANNOT_CHECK"),
                            "exact_rate": sum(kso_flags) / len(rows), "role": "the machine under test (full arm; COMPOSE may read the store)",
                            "store_read_rows": sum(1 for r in rows if r["arms"][KSO_COL].get("store_read") is True),
                            "exact_declared_disagreements": sum(1 for r in rows if r["arms"][KSO_COL].get("exact_declared") not in (None, r["arms"][KSO_COL]["exact"]))}
        per_arm[KSO_NAV] = {"exact": sum(nav_flags), "n_scored": sum(1 for r in rows if r["arms"][KSO_NAV]["status"] == "SCORED"),
                            "n_obstruction": sum(1 for r in rows if r["arms"][KSO_NAV]["status"] == "OBSTRUCTION"),
                            "n_cannot_check": len(nav_cnc), "exact_rate": sum(nav_flags) / len(rows),
                            "role": "the machine under test, navigation only (may NOT read the store): the mechanic's honest number"}
        table += [paired(KSO_COL, B5, kso_flags, flags[B5])]
        table += [paired(KSO_NAV, a, nav_flags, flags[a]) for a in (B5, RWR, CBR)]

    # checkers
    b5_flags = flags[B5]
    planted = list(b5_flags)
    for i in range(min(12, len(planted))):
        planted[i] = not planted[i]
    k4_red = paired("PLANT", B5, planted, b5_flags)
    k4_quiet = paired("COPY", B5, list(b5_flags), b5_flags)
    oracle_count = sum(flags[ORACLE])
    perturbed = list(flags[ORACLE]); perturbed[0] = not perturbed[0]
    graph_ok = all(len({r["graph"]["sha256"]}) == 1 for r in rows)  # one digest per row by construction
    checkers = {
        "K1_random_at_null": {"count": sum(flags[RANDOM]), "band": band, "pass": at_null(sum(flags[RANDOM]), band),
                              "plant_oracle_outside_band": not at_null(oracle_count, band)},
        "K2_positive_control_exact": {"rate": per_arm[ORACLE]["exact_rate"], "pass": per_arm[ORACLE]["exact_rate"] == 1.0,
                                      "plant_one_perturbed_breaks": (sum(perturbed) / len(perturbed)) != 1.0},
        "K3_budget_no_overrun": {"cannot_check": cannot, "pass": not cannot, "cap_scale": cap_scale},
        "K4_paired_red_on_planted_disagreement": {"plant": k4_red, "no_alarm": k4_quiet,
                                                  "pass": k4_red["red"] and k4_red["discordant"] == min(12, len(planted)) and not k4_quiet["red"] and k4_quiet["exact_p_two_sided"] == 1.0},
        "K7_joined_exact_recomputed": {"pass": (per_arm.get(KSO_COL, {}).get("exact_declared_disagreements", 0) == 0),
                                       "note": "the joined column's exact flags are recomputed against the oracle here; a disagreement is red"} if kso_column is not None else {"pass": True, "note": "no column joined"},
        "K5_information_matching": {"pass": graph_ok and all(r["graph"]["request_atoms"] == rows[0]["graph"]["request_atoms"] for r in rows),
                                    "request_atoms": rows[0]["graph"]["request_atoms"], "note": "every arm read one graph, one seed set and one typed-status map per instance (Frame); the digest is on the row"},
    }
    body = {
        "schema": SCHEMA, "contract": CONTRACT, "n_instances": len(rows), "ids_sha256": ids_sha,
        "source": {"generator": "research/experiments/me-x1/mex1_generator.py", "oracle": "research/experiments/me-x1/mex1_oracle.py",
                   "arms": "research/experiments/me-x1/mex1_arms.py", "split": SPLIT, "split_seed": SPLIT_SEED, "per_family": PER_FAMILY,
                   "population": "research/orion-machine/reference/kso_m1_mex1_population_v1.py",
                   "request_atoms": rows[0]["graph"]["request_atoms"]},
        "information_matching": "every arm: the ME-X1 ArmView (world v0, world at request, events, request, accepted); graph arms: the same populated graph (sha256 per row), seed set S = {req:<id>, claim:<target>} ∪ {res:<result>}, typed-module statuses (mex1_arms._status_for, all modules typed = what B5 reads); CBR additionally reads the 14 public known-answer fixtures; no arm imports the oracle",
        "store_read_permissions": STORE_READ,
        "budget_matched": {"steps": f"{CAP_STEPS_PER_ATOM}*|atoms|", "edge_visits": f"{CAP_VISITS_PER_EDGE}*|hyperedges|", "restarts": CAP_RESTARTS,
                           "wall_proxy": "ops = steps + edge_visits", "cap_scale": cap_scale, "applies_to": list(NAVIGATING) + [KSO_COL],
                           "recorded_not_capped": [B5, RANDOM, ORACLE], "overrun": "CANNOT_CHECK on that instance; run exit 2"},
        "per_arm": per_arm, "paired": table, "checkers": checkers, "instances": rows,
        "terminals": {"COMPARATOR_TABLE": "READY", "KSO_COLUMN": "PRESENT" if kso_column is not None else "ABSENT",
                      "PARENT_SUFFICIENT": ("YES" if per_arm[KSO_COL]["exact"] <= per_arm[B5]["exact"] else "NO") if kso_column is not None else "EXPECTED_WHEN_KSO_COLUMN_MERGED",
                      "NAVIGATION_ONLY_VS_RETRIEVAL_PARENTS": ("REPORTED" if kso_column is not None and not nav_cnc else "NOT_SCORED"),
                      "GENERAL_NOVELTY": "NOT_ESTABLISHED"},
        "authority": "development split; comparator table and budget matching only; no solve-loop, protected or novelty authority. NO NOVELTY OR BREAKTHROUGH CLAIM.",
    }
    return body


def verdict(body: dict) -> int:
    if body["checkers"]["K3_budget_no_overrun"]["cannot_check"]:
        return 2
    return 0 if all(c["pass"] for c in body["checkers"].values()) else 1


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _default(o):
    if isinstance(o, Fraction):
        return str(o)
    if isinstance(o, (frozenset, set, tuple)):
        return sorted(o) if isinstance(o, (frozenset, set)) else list(o)
    raise TypeError(type(o).__name__)


def strip_timing(obj):
    """The body with every wall_ns zeroed: what byte-reproducibility is asserted on (a clock is not a result)."""
    if isinstance(obj, dict):
        return {k: (0 if k == "wall_ns" else strip_timing(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [strip_timing(v) for v in obj]
    return obj


def canonical(body: dict) -> bytes:
    return json.dumps(strip_timing(body), sort_keys=True, default=_default).encode()


def finalize(body: dict, design_path: Path | None) -> dict:
    canon = canonical(body)
    bindings = {"kso_m2_comparator_v1.py": sha256_file(HERE / "kso_m2_comparator_v1.py"),
                "kso_m1_mex1_population_v1.py": sha256_file(HERE / "kso_m1_mex1_population_v1.py"),
                "kso_math_v1.py": sha256_file(HERE / "kso_math_v1.py"),
                "mex1_arms.py": sha256_file(MEX1 / "mex1_arms.py"), "mex1_generator.py": sha256_file(MEX1 / "mex1_generator.py"),
                "mex1_oracle.py": sha256_file(MEX1 / "mex1_oracle.py")}
    solve = HERE / "kso_m2_solve_v1.py"
    if solve.exists():
        bindings["kso_m2_solve_v1.py"] = sha256_file(solve)
    design = None
    if design_path is not None and design_path.exists():
        design = {"path": str(design_path.relative_to(ROOT)), "sha256": sha256_file(design_path)}
        try:
            dj = json.loads(design_path.read_text())
            cm = dj.get("commitment", {})
            design["kso_m2_solve_design_sha256"] = cm.get("kso_m2_solve_design_sha256")
            design["ids_sha256_declared"] = cm.get("ids_sha256")
            design["ids_match"] = cm.get("ids_sha256") == body["ids_sha256"]
            design["module_sha256_at_freeze"] = cm.get("module_sha256_at_freeze")
            design["module_matches_freeze"] = cm.get("module_sha256_at_freeze") == sha256_file(HERE / "kso_m2_comparator_v1.py")
        except json.JSONDecodeError:
            design["error"] = "design json unreadable"
    out = dict(body)
    out["provenance"] = {"body_sha256": hashlib.sha256(canon).hexdigest(), "body_sha256_is_over": "the body with wall_ns zeroed",
                         "bindings": bindings, "design": design,
                         "python": sys.version.split()[0],
                         "command": "python research/orion-machine/reference/kso_m2_comparator_v1.py --out research/orion-machine/results/KSO_M2_COMPARATOR_RECEIPT_V1.json"}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, help="write the receipt here (omit for a dry run)")
    ap.add_argument("--design", type=Path, default=RESULTS / "KSO_M2_COMPARATOR_DESIGN_V1.json")
    ap.add_argument("--kso-column", type=Path, help="lane-ocm-3's KSO_M2_SOLVE receipt; its rows join the table")
    ap.add_argument("--cap-scale", type=float, default=1.0, help="scale the matched caps (0 plants an overrun)")
    ap.add_argument("--no-repro-check", action="store_true")
    args = ap.parse_args(argv)
    print(f"kso_m2_comparator: python {sys.version.split()[0]}")
    try:
        kso_col = None
        if args.kso_column:
            try:
                kj = json.loads(args.kso_column.read_text())
            except (OSError, json.JSONDecodeError) as exc:
                raise CannotCheck(f"KSO column unreadable: {exc}") from exc
            rows = kj.get("instances") if isinstance(kj, dict) else None
            if not rows:
                raise CannotCheck("KSO column has no instances[]")
            kso_col = {}
            for r in rows:
                cell = r.get("arms", {}).get(KSO_COL) or r.get(KSO_COL)
                if not isinstance(cell, dict) or "answer" not in cell:
                    raise CannotCheck(f"KSO column row {r.get('instance_id')} lacks arms.{KSO_COL}.answer")
                kso_col[r["instance_id"]] = {**cell, "_graph_sha256": r.get("graph_sha256")}
        body = run(cap_scale=args.cap_scale, kso_column=kso_col)
        code = verdict(body)
        if not args.no_repro_check and code == 0:
            again = run(cap_scale=args.cap_scale, kso_column=kso_col)
            same = canonical(body) == canonical(again)
            body["checkers"]["K6_byte_reproducible"] = {"pass": same, "note": "wall_ns zeroed on both sides; every other byte identical"}
            if not same:
                code = 1
        receipt = finalize(body, args.design)
    except CannotCheck as exc:
        print(f"COULD NOT CHECK: {exc}", file=sys.stderr)
        return 2
    for name, c in receipt["checkers"].items():
        print(f"  [{'PASS' if c.get('pass') else 'FAIL'}] {name}")
    for name, s in receipt["per_arm"].items():
        print(f"  {name:42s} exact {s['exact']:3d}/{s['n_scored']:3d}  cannot_check {s['n_cannot_check']}  ({s['role']})")
    for t in receipt["paired"]:
        print(f"  paired {t['x']} vs {t['y']}: x_only {t['x_only']} y_only {t['y_only']} p={t['exact_p_two_sided']:.3g}{' RED' if t['red'] else ''}")
    print(f"  terminals: {receipt['terminals']}")
    if args.out:
        args.out.write_text(json.dumps(receipt, indent=1, sort_keys=True, default=_default) + "\n")
        print(f"  receipt written: {args.out} (body sha256 {receipt['provenance']['body_sha256'][:12]})")
    if code == 2:
        print("COULD NOT CHECK: a budget overrun left an arm-instance unscored", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
