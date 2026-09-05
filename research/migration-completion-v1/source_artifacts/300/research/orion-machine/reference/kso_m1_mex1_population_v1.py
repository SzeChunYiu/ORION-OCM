"""KSO M1 — populate KnowledgeSpace.v1 from ME-X1 worlds and run the M0 invariants on the machine.

Source of truth: ``research/experiments/me-x1/`` — ``mex1_generator.generate_split`` (worlds),
``mex1_oracle.support_table`` / ``evaluate_support`` (the registered support algebra),
``mex1_model.apply_event`` (registered events).  Nothing under ``research/experiments/**`` is
modified or re-run; the generator is imported read-only.

Population (every world is one warranted typed hypergraph):

  evidence universe E   = the oracle's base atoms (``src:e``, ``ident:e``, ``cal:e``, ``evc:e``,
                          ``tr:fam:e``, ``ind:fam``, ``nocontra:c``); base atom i carries the
                          assumption label {{i}} — it is its own ATMS environment.
  ev:<e>                = ⊗ of its own base atoms          (COMPOSITION hyperedge, joint tails)
  fam:<f>               = ⊗ (ev of positive evidence, tr, ind, prerequisite claims)   (COMPOSITION)
  claim:<c>             = (⊕ over its families) ⊗ nocontra:c   (SUPPORT edges per family,
                          CONSTRAINT edge from nocontra:c)
  res:<r>, req:<kind>   = result over its basis evidence (COMPOSITION), request → target (DEPENDENCE)

The registered statuses give the registered revocation set R0 = {i : status(i) = INVALID} and the
censored set U = {i : status(i) = UNKNOWN}.

Checkers on the machine (each with a planted failure, a no-alarm control, and CANNOT_CHECK distinct):

  P1  dense by construction: every atom is incident to ≥ 1 typed edge; 0 quarantined.
  P2  label ≡ oracle: for every claim and family, ℓ_R(label) equals the oracle's
      ``evaluate_support`` under R0 and under every two-valued resolution of U (≤ 12 unknowns,
      the oracle's own cap) — the ATMS label *is* the support algebra, shown per world.
  P3  retraction propagation, both directions, on real worlds: for a sample of base atoms b with
      dependents, revoke {b}: dependents whose label dies stop reacting exactly (activation 0);
      atoms not reachable from any dead atom are exactly unchanged; reachable live atoms never
      gain; the renormalising parent raises an unreachable atom on ≥ 1 world (must differ);
      reinstating restores the pre-vector exactly.  The registered events are replayed as the
      real revocation: labels on the v0 graph under R(v1) agree with the oracle's v1 support.
  P4  hub normalisation, both directions: the background question scores 0 everywhere (the
      hub included); a question seeding the hub makes the hub score > 0 and outrank every other
      atom; a question seeding one evidence atom is reported (hub raw rank vs surprise rank).
  P5  the genome (S1–S7 as KSO predicates) holds on every populated space and its digest is
      unchanged by population.

Exit codes: 0 all hold; 1 a check fails; 2 could not check.  NO NOVELTY OR BREAKTHROUGH CLAIM.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MEX1 = ROOT / "research" / "experiments" / "me-x1"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


kso = _load("kso_math_v1", HERE / "kso_math_v1.py")
m0 = _load("kso_m0_freeze_checks_v1", HERE / "kso_m0_freeze_checks_v1.py")
CannotCheck = kso.CannotCheck
Atom, Hyperedge, KnowledgeSpace = kso.Atom, kso.Hyperedge, kso.KnowledgeSpace
ONE, ZERO = m0.ONE, m0.ZERO
Cert = m0.CertificateKind


def _mex1():
    for p in (str(MEX1), str(ROOT / "src")):
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        import mex1_generator  # type: ignore
        import mex1_model  # type: ignore
        import mex1_oracle  # type: ignore
    except Exception as exc:  # pragma: no cover - environment
        raise CannotCheck(f"ME-X1 modules unimportable: {exc}") from exc
    return mex1_generator, mex1_model, mex1_oracle


# ----------------------------------------------------------------------------------------------
# population
# ----------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Population:
    space: KnowledgeSpace
    governed: object
    base_index: dict[str, int]          # oracle base atom id -> evidence index
    base_status: dict[str, str]         # oracle base atom id -> VALID/INVALID/UNKNOWN
    claim_atom: dict[str, str]          # claim id -> KSO atom id
    family_atom: dict[str, str]
    registered_revoked: frozenset[int]
    unknown: tuple[int, ...]


def _and_all(profiles: Iterable[tuple]) -> tuple:
    out: tuple = ONE
    for p in profiles:
        out = kso.profile_and(out, p)
    return out


def populate(world, request=None, request_id: str = "req") -> Population:
    """Build the governed knowledge space of one world; with ``request`` (a ``TransitionRequest``)
    one goal atom ``req:<request_id>`` is added with DEPENDENCE hyperedges to its target claim and,
    when set, to its result — the M2 seed convention."""
    _, model, oracle = _mex1()
    table = oracle.support_table(world)
    base_ids = sorted(table.atoms)
    base_index = {b: i for i, b in enumerate(base_ids)}
    atoms: list[Atom] = []
    edges: list[Hyperedge] = []
    certs: dict[str, str] = {}
    profiles: dict[str, tuple] = {}

    def add(atom_id: str, atom_type: str, profile: tuple, cert: Cert) -> None:
        atoms.append(Atom(atom_id, atom_type, profile))
        profiles[atom_id] = profile
        certs[atom_id] = cert.value

    for b in base_ids:
        kind = b.split(":", 1)[0]
        add(b, "constraint" if kind in ("nocontra", "ind", "tr") else "observation", (frozenset({base_index[b]}),), Cert.EXPERIMENTATION)
    # evidence atoms: the base atoms that are functions of the evidence item alone
    ev_base: dict[str, list[str]] = {}
    for b in base_ids:
        kind, _, rest = b.partition(":")
        if kind in ("src", "ident", "cal", "evc"):
            ev_base.setdefault(rest, []).append(b)
    for e in sorted(world.evidence):
        parts = ev_base.get(e, [])
        if not parts:
            continue  # negative evidence enters the graph only through nocontra:<claim>
        aid = f"ev:{e}"
        add(aid, "observation", _and_all(profiles[b] for b in parts), Cert.EXPERIMENTATION)
        edges.append(Hyperedge(f"compose:{aid}", tuple(parts), (aid,), "COMPOSITION", profile=ONE))
    # families and claims in prerequisite order
    for c in world.prerequisite_topological_order():
        fam_profiles: list[tuple] = []
        for fam in world.families_of(c):
            tails: list[str] = []
            for b in table.family_atoms[fam.family_id]:
                kind, _, rest = b.partition(":")
                if kind in ("src", "ident", "cal", "evc"):
                    ev_atom = f"ev:{rest}"
                    if ev_atom not in tails:
                        tails.append(ev_atom)
                else:
                    tails.append(b)
            for p in fam.prerequisite_ids:
                tails.append(f"claim:{p}")
            fid = f"fam:{fam.family_id}"
            prof = _and_all(profiles[t] for t in tails) if tails else ONE
            add(fid, "procedure", prof, Cert.INSTRUCTION)
            if tails:
                edges.append(Hyperedge(f"compose:{fid}", tuple(dict.fromkeys(tails)), (fid,), "COMPOSITION", profile=ONE))
            fam_profiles.append(prof)
        cid = f"claim:{c}"
        alt: tuple = ZERO
        for p in fam_profiles:
            alt = kso.profile_or(alt, p)
        nocontra = f"nocontra:{c}"
        prof = kso.profile_and(alt, profiles[nocontra])
        add(cid, "claim", prof, Cert.INSTRUCTION)
        for fam in world.families_of(c):
            edges.append(Hyperedge(f"support:{fam.family_id}", (f"fam:{fam.family_id}",), (cid,), "SUPPORT", profile=ONE))
        edges.append(Hyperedge(f"constraint:{c}", (nocontra,), (cid,), "CONSTRAINT", profile=ONE))
    # results
    for r in sorted(world.results):
        res = world.results[r]
        basis = [f"ev:{e}" for e in res.basis_evidence_ids if f"ev:{e}" in profiles]
        rid = f"res:{r}"
        cert = Cert.EXACT_CHECKER if res.proved_spec_id else Cert.EXPERIMENTATION
        add(rid, "proof" if res.proved_spec_id else "observation", _and_all(profiles[b] for b in basis) if basis else ONE, cert)
        if basis:
            edges.append(Hyperedge(f"compose:{rid}", tuple(basis), (rid,), "COMPOSITION", profile=ONE))
        edges.append(Hyperedge(f"bind:{r}", (rid,), (f"claim:{res.bound_claim_id}",), "DEPENDENCE", profile=ONE))
    if request is not None:
        rid = f"req:{request_id}"
        add(rid, "goal", ONE, Cert.INSTRUCTION)
        edges.append(Hyperedge(f"goal:{request_id}:claim", (rid,), (f"claim:{request.target_claim_id}",), "DEPENDENCE", profile=ONE))
        if getattr(request, "result_id", "") and f"res:{request.result_id}" in profiles:
            edges.append(Hyperedge(f"goal:{request_id}:result", (rid,), (f"res:{request.result_id}",), "DEPENDENCE", profile=ONE))
    ks = KnowledgeSpace(tuple(atoms), tuple(edges))
    ks.validate()
    m0.check_edge_vocabulary(ks)
    status = dict(table.atoms)
    revoked = frozenset(base_index[b] for b, s in status.items() if s == model.STATUS_INVALID)
    unknown = tuple(sorted(base_index[b] for b, s in status.items() if s == model.STATUS_UNKNOWN))
    n_comp = sum(1 for e in edges if e.relation_type == "COMPOSITION")
    governed = m0.GovernedSpace(ks, {k: Cert(v) for k, v in certs.items()}, evidence_atoms=len(base_ids), meter=m0.Meter(admit=len(atoms), compose=n_comp), revoked=revoked)
    return Population(ks, governed, base_index, status, {c: f"claim:{c}" for c in world.claims}, {f: f"fam:{f}" for f in world.families}, revoked, unknown)


# ----------------------------------------------------------------------------------------------
# exact activation on the populated DAG
# ----------------------------------------------------------------------------------------------


def _topological(ks: KnowledgeSpace, p: list[list[Fraction]]) -> list[int] | None:
    n = len(p)
    indeg = [0] * n
    for i in range(n):
        for j in range(n):
            if p[i][j] != 0:
                indeg[j] += 1
    order = [i for i in range(n) if indeg[i] == 0]
    seen = 0
    out: list[int] = []
    while order:
        i = order.pop()
        out.append(i)
        seen += 1
        for j in range(n):
            if p[i][j] != 0:
                indeg[j] -= 1
                if indeg[j] == 0:
                    order.append(j)
    return out if seen == n else None


def activation(ks: KnowledgeSpace, seed: Sequence[Fraction], alpha: Fraction, *, revoked: Iterable[int] = (), matrix=None) -> dict[str, Fraction]:
    """Exact restart fixed point a* = α s + (1−α) Pᵀ a*; on an acyclic P the Neumann series is finite."""
    rv = frozenset(revoked)
    amap = ks.atom_map()
    # the restart seed is warrant-gated like every other contribution: a dead atom receives no
    # restart mass and its share dissipates; the surviving entries are NOT renormalised
    gated_seed = [s if kso.profile_live(amap[x].profile, rv) else Fraction(0, 1) for x, s in zip(ks.ids, seed, strict=True)]
    p = (matrix or kso.navigation_matrix)(ks, revoked=rv)
    order = _topological(ks, p)
    if order is None:
        pt = [list(col) for col in zip(*p, strict=True)]
        n = len(p)
        a_mat = [[Fraction(int(i == j), 1) - (1 - alpha) * pt[i][j] for j in range(n)] for i in range(n)]
        a = kso._solve_fraction(a_mat, [alpha * x for x in gated_seed])
        return dict(zip(ks.ids, a, strict=True))
    n = len(p)
    a = [alpha * s for s in gated_seed]
    for i in order:
        if a[i] == 0:
            continue
        row = p[i]
        for j in range(n):
            if row[j] != 0:
                a[j] += (1 - alpha) * a[i] * row[j]
    return dict(zip(ks.ids, a, strict=True))


def uniform(ks: KnowledgeSpace) -> list[Fraction]:
    n = len(ks.ids)
    return [Fraction(1, n)] * n


def point(ks: KnowledgeSpace, atom_id: str) -> list[Fraction]:
    return [Fraction(1, 1) if x == atom_id else Fraction(0, 1) for x in ks.ids]


# ----------------------------------------------------------------------------------------------
# checkers
# ----------------------------------------------------------------------------------------------


def check_P1_dense(pop: Population) -> dict[str, object]:
    ks = pop.space
    incident = {x: 0 for x in ks.ids}
    for e in ks.hyperedges:
        for x in (*e.tails, *e.heads):
            incident[x] += 1
    isolated = sorted(x for x, k in incident.items() if k == 0)
    assert not isolated, isolated
    assert all(not a.quarantined for a in ks.atoms)
    # planted: an isolated live atom must be rejected by the acquisition transaction
    try:
        m0.admit(ks, Atom("planted:isolated", "claim", ONE), (), Cert.INSTRUCTION)
        planted = "MISSED"
    except m0.TypedRejection as exc:
        planted = exc.code
    assert planted == "ISOLATED_ATOM_REJECTED"
    return {"atoms": len(ks.atoms), "hyperedges": len(ks.hyperedges), "isolated": 0, "quarantined": 0, "planted_isolated_rejected": 1}


def check_P2_label_equals_oracle(pop: Population, world) -> dict[str, object]:
    _, model, oracle = _mex1()
    table = oracle.support_table(world)
    amap = pop.space.atom_map()
    inv = {i: b for b, i in pop.base_index.items()}
    unknown = list(pop.unknown)
    if len(unknown) > 12:
        raise CannotCheck(f"{len(unknown)} censored base atoms exceed the exhaustive cap")
    cells = 0
    mismatches: list[str] = []
    for bits in itertools.product((True, False), repeat=len(unknown)):
        resolved_false = {u for u, bit in zip(unknown, bits, strict=True) if not bit}
        r = pop.registered_revoked | frozenset(resolved_false)
        vals = {b: (pop.base_index[b] not in r) for b in table.atoms}
        sup = oracle.evaluate_support(world, vals, table)
        for c in world.claims:
            live = kso.profile_live(amap[f"claim:{c}"].profile, r)
            cells += 1
            if live != bool(sup[c]):
                mismatches.append(f"{c}@{sorted(inv[i] for i in r)}")
        for fam in world.families.values():
            parts = [vals[a] for a in table.family_atoms[fam.family_id]] + [bool(sup[p]) for p in fam.prerequisite_ids]
            live = kso.profile_live(amap[f"fam:{fam.family_id}"].profile, r)
            cells += 1
            if live != all(parts):
                mismatches.append(f"{fam.family_id}@{sorted(inv[i] for i in r)}")
    assert not mismatches, mismatches[:5]
    negatives = 0
    for bits in itertools.product((True, False), repeat=len(unknown)):
        resolved_false = {u for u, bit in zip(unknown, bits, strict=True) if not bit}
        r = pop.registered_revoked | frozenset(resolved_false)
        vals = {b: (pop.base_index[b] not in r) for b in table.atoms}
        sup = oracle.evaluate_support(world, vals, table)
        negatives += sum(1 for c in world.claims if not sup[c])
    # planted: a merged (⊕) family label disagrees with the oracle on a world where a family has ≥ 2 tails
    planted = "NO_FAMILY_WITH_TWO_TAILS"
    for e in pop.space.hyperedges:
        if e.relation_type == "COMPOSITION" and e.edge_id.startswith("compose:fam:") and len(e.tails) >= 2:
            merged: tuple = ZERO
            for t in e.tails:
                merged = kso.profile_or(merged, amap[t].profile)
            # revoke exactly one tail's first environment: the product dies, the merge survives
            first_env = next(iter(amap[e.tails[0]].profile), None)
            if first_env:
                r = pop.registered_revoked | first_env
                planted = "CAUGHT" if kso.profile_live(merged, r) and not kso.profile_live(amap[e.heads[0]].profile, r) else "MISSED"
                if planted == "CAUGHT":
                    break
    return {"cells": cells, "mismatches": 0, "oracle_negative_cells": negatives, "power": "POWERED" if negatives else "NO_POWER__ALL_CELLS_POSITIVE",
            "resolutions": 2 ** len(unknown), "planted_merged_family_label_caught": planted}


def check_P2_constraint_power(world, claim_id: str) -> dict[str, object]:
    """The CONSTRAINT (nocontra) tail of a claim label is load-bearing only on a world with an
    undefeated negative evidence item; the generator plants none (0 INVALID nocontra atoms on the
    dev split), so a derived world with one negative evidence against ``claim_id`` from a valid
    source is populated and the tail-drop mutant (claim label without ⊗ nocontra) must be caught."""
    gen, model, oracle = _mex1()
    w = world.copy()
    claim = w.claims[claim_id]
    valid_sources = [sid for sid, st in sorted(w.sources.items()) if st == model.SOURCE_VALID]
    if not valid_sources:
        raise CannotCheck("no valid source to attach a negative evidence to")
    eid = f"neg:{claim_id}"
    w.evidence[eid] = model.Evidence(eid, claim_id, valid_sources[0], claim.context_id, tuple(claim.scope), supports=False)
    w.validate()
    table = oracle.support_table(w)
    assert table.atoms[f"nocontra:{claim_id}"] == model.STATUS_INVALID, "planted negative evidence did not invalidate nocontra"
    pop = populate(w)
    amap = pop.space.atom_map()
    r = pop.registered_revoked
    tri = {a: oracle._tri(st) for a, st in table.atoms.items()}
    sup = oracle.evaluate_support(w, {a: (v if v is not None else True) for a, v in tri.items()}, table)
    live = kso.profile_live(amap[f"claim:{claim_id}"].profile, r)
    assert live == bool(sup[claim_id]) and live is False, ("label vs oracle on the negative-evidence world", live, sup[claim_id])
    # tail-drop mutant: the claim label without its constraint tail = ⊕ of its family labels
    dropped: tuple = ZERO
    for fam in w.families_of(claim_id):
        dropped = kso.profile_or(dropped, amap[f"fam:{fam.family_id}"].profile)
    mutant_live = kso.profile_live(dropped, r)
    return {"claim": claim_id, "nocontra_status": table.atoms[f"nocontra:{claim_id}"], "claim_label_dead": not live, "oracle_support": bool(sup[claim_id]),
            "tail_drop_mutant_caught": "CAUGHT" if mutant_live and not live else ("NO_POWER__CLAIM_DEAD_WITHOUT_CONSTRAINT" if not mutant_live else "MISSED")}


def dead_set(pop: Population, revoked: frozenset[int]) -> frozenset[str]:
    amap = pop.space.atom_map()
    return frozenset(x for x in pop.space.ids if not kso.profile_live(amap[x].profile, revoked))


def _matrix_closure(ks: KnowledgeSpace, start: Iterable[str]) -> frozenset[str]:
    p = kso.navigation_matrix(ks)  # ungated (R = ∅)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    reached = {idx[x] for x in start}
    frontier = list(reached)
    while frontier:
        i = frontier.pop()
        for j in range(len(ids)):
            if p[i][j] != 0 and j not in reached:
                reached.add(j)
                frontier.append(j)
    return frozenset(ids[i] for i in reached)


def check_P3_retraction(pop: Population, world, *, alpha: Fraction = Fraction(1, 3), sample: int = 8) -> dict[str, object]:
    ks = pop.space
    inv = {i: b for b, i in pop.base_index.items()}
    seed = uniform(ks)
    r0 = pop.registered_revoked
    pre = activation(ks, seed, alpha, revoked=r0)
    candidates = [i for i in sorted(inv) if i not in r0 and kso.profile_live(ks.atom_map()[inv[i]].profile, r0)]
    # deterministic sample: spread across the sorted candidates
    step = max(1, len(candidates) // sample)
    chosen = candidates[::step][:sample]
    n_dead_zero = n_unreach_same = n_reach_nogain = n_restore = 0
    parent_raised = 0
    checked = 0
    for i in chosen:
        r = r0 | {i}
        dead = dead_set(pop, r) - dead_set(pop, r0)
        if not dead:
            continue
        checked += 1
        post = activation(ks, seed, alpha, revoked=r)
        # frame: the unreachable set is computed by the structural closure over hyperedges (m0) and,
        # independently, by the transitive closure of the nonzero entries of the UNGATED matrix; both
        # must agree, and neither uses the gated mechanic under test
        reach = m0.ungated_closure(ks, dead)
        reach_matrix = _matrix_closure(ks, dead)
        assert reach == reach_matrix, (inv[i], sorted(reach ^ reach_matrix)[:5])
        for x in dead:
            assert post[x] == 0, (inv[i], x)
        n_dead_zero += 1
        for x in ks.ids:
            if x not in reach:
                assert post[x] == pre[x], (inv[i], x)
            else:
                assert post[x] <= pre[x], (inv[i], x)
        n_unreach_same += 1
        n_reach_nogain += 1
        bad = activation(ks, seed, alpha, revoked=r, matrix=kso.navigation_matrix_bad_renormalize)
        if any(bad[x] > pre[x] for x in ks.ids if x not in reach):
            parent_raised += 1
        back = activation(ks, seed, alpha, revoked=r0)
        assert back == pre
        n_restore += 1
    if checked == 0:
        raise CannotCheck("no base atom with dependents to revoke")
    # the registered events as the real revocation
    gen, model, oracle = _mex1()
    return {
        "revocations_checked": checked,
        "dead_atoms_zero": n_dead_zero,
        "unreachable_atoms_unchanged": n_unreach_same,
        "reachable_atoms_never_gain": n_reach_nogain,
        "reinstatement_restores": n_restore,
        "renormalising_parent_raised_unreachable_atom": parent_raised,
        "unreachable_frame": "structural closure over hyperedges (kso_m0_freeze_checks_v1.ungated_closure) == transitive closure of nonzero entries of the ungated navigation matrix; asserted equal per revocation; neither uses the gated matrix under test",
    }


def check_P3_events(pop: Population, inst) -> dict[str, object]:
    """Replay the registered events: the v0 labels under R(v1) must agree with the oracle at v1
    for every claim whose base atoms all exist at v0 (added atoms are an acquisition, M3)."""
    gen, model, oracle = _mex1()
    w1 = oracle.final_world(inst.world_v0, inst.events)
    t1 = oracle.support_table(w1)
    shared = [b for b in t1.atoms if b in pop.base_index]
    added = [b for b in t1.atoms if b not in pop.base_index]
    r1 = frozenset(pop.base_index[b] for b in shared if t1.atoms[b] == model.STATUS_INVALID)
    unknown1 = [pop.base_index[b] for b in shared if t1.atoms[b] == model.STATUS_UNKNOWN]
    amap = pop.space.atom_map()
    agree = disagree = 0
    if added or len(unknown1) > 12 or set(w1.claims) != set(inst.world_v0.claims) or set(w1.families) != set(inst.world_v0.families):
        return {"events": len(inst.events), "status": "ACQUISITION_NEEDED" if added else "STRUCTURE_CHANGED", "added_base_atoms": len(added)}
    for bits in itertools.product((True, False), repeat=len(unknown1)):
        r = r1 | frozenset(u for u, bit in zip(unknown1, bits, strict=True) if not bit)
        vals = {b: (pop.base_index[b] not in r) for b in t1.atoms}
        sup = oracle.evaluate_support(w1, vals, t1)
        for c in w1.claims:
            if kso.profile_live(amap[f"claim:{c}"].profile, r) == bool(sup[c]):
                agree += 1
            else:
                disagree += 1
    assert disagree == 0, f"{inst.instance_id}: {disagree} claim cells disagree with the oracle at v1 under the replayed events"
    return {"events": len(inst.events), "status": "REPLAYED", "claim_cells_agree": agree, "claim_cells_disagree": disagree, "newly_revoked": len(r1 - pop.registered_revoked)}


def check_P4_hub(pop: Population, *, alpha: Fraction = Fraction(1, 3)) -> dict[str, object]:
    """KS-T06b on the real world, ranked over the atoms the question did not seed.

    (i)  the evidence question — uniform over every live ``ev:`` atom — touches the hub (which
         collects from many of them) and every specific family/claim; discriminating iff the hub is
         first by raw activation AND not first by surprise AND the planted popularity ranker (raw
         order) differs from the surprise order.  Reported per world; the receipt asserts ≥ 1
         world exhibits it and reports the count.
    (ii) hub-only question: hub first by surprise — NOT_DISCRIMINATING (any seeded atom is first);
         kept as a record only.
    (iii) background question: 0 everywhere — an identity (no-alarm), labelled as such.
    """
    ks = pop.space
    degree = {x: 0 for x in ks.ids}
    for e in ks.hyperedges:
        for x in (*e.tails, *e.heads):
            degree[x] += 1
    r0 = pop.registered_revoked
    amap = ks.atom_map()
    hub = max(ks.ids, key=lambda x: (degree[x], x))
    background = activation(ks, uniform(ks), alpha, revoked=r0)
    zero = m0.reaction_surprise_vector(background, background)
    assert all(v == 0.0 for v in zero.values()), f"background question is surprising at {[x for x, v in zero.items() if v != 0.0][:3]} — the surprise normalisation is not an identity on its own baseline"
    ev_atoms = [x for x in ks.ids if x.startswith("ev:") and kso.profile_live(amap[x].profile, r0)]
    if not ev_atoms:
        raise CannotCheck("no live evidence atom to seed the evidence question")
    seed = [Fraction(1, len(ev_atoms)) if x in ev_atoms else Fraction(0, 1) for x in ks.ids]
    q = activation(ks, seed, alpha, revoked=r0)
    s_q = m0.reaction_surprise_vector(q, background)
    raw_rank = m0.rank_by(q, exclude=ev_atoms)
    sur_rank = m0.rank_by(s_q, exclude=ev_atoms)
    hub_raw_first = raw_rank[0] == hub
    hub_sur_first = sur_rank[0] == hub
    planted_ranker_differs = raw_rank != sur_rank
    direction_i = hub_raw_first and not hub_sur_first and planted_ranker_differs
    hub_q = activation(ks, point(ks, hub), alpha, revoked=r0)
    s_hub = m0.reaction_surprise_vector(hub_q, background)
    return {"hub": hub, "hub_degree": degree[hub], "hub_is_seed": hub in ev_atoms,
            "direction_i": {"seed": f"uniform over {len(ev_atoms)} live ev atoms", "hub_raw_rank": raw_rank.index(hub) + 1 if hub in raw_rank else None, "hub_surprise_rank": sur_rank.index(hub) + 1 if hub in sur_rank else None,
                            "raw_winner": raw_rank[0], "surprise_winner": sur_rank[0], "planted_popularity_ranker_differs": planted_ranker_differs, "holds": direction_i},
            "direction_ii_hub_only": {"hub_first_by_surprise": m0.rank_by(s_hub)[0] == hub, "status": "NOT_DISCRIMINATING__ANY_SEEDED_ATOM_IS_FIRST"},
            "direction_iii_background": {"zero_everywhere": True, "status": "IDENTITY__NO_ALARM_ONLY"}}


def check_P5_genome(pop: Population, digest_before: str) -> dict[str, object]:
    g = pop.governed
    held = {"S1": m0.ks_S1_admission(g), "S2": m0.ks_S2_composition(g), "S6": m0.ks_S6_signature_round_trip(g) if g.evidence_atoms <= 3 else None}
    # S3 on the machine: sampled — registered R0, every singleton, and R0 ∪ singleton
    ks = pop.space
    amap = ks.atom_map()
    ok = True
    n = len(ks.ids)
    samples = [pop.registered_revoked] + [frozenset({i}) for i in range(min(g.evidence_atoms, 40))] + [pop.registered_revoked | {i} for i in range(min(g.evidence_atoms, 40))]
    for r in samples:
        p = kso.navigation_matrix(ks, revoked=r)
        for i, x in enumerate(ks.ids):
            moving = any(p[i][j] != 0 for j in range(n)) or any(p[j][i] != 0 for j in range(n))
            if moving and not kso.profile_live(amap[x].profile, r):
                ok = False
    held["S3_sampled"] = ok
    held["S3_samples"] = len(samples)
    # S4: singleton Γ over base atoms is measurable for the identity partition; merging two base atoms of one family is not
    gamma = [frozenset({i}) for i in range(min(g.evidence_atoms, 8))]
    identity = tuple((i,) for i in range(g.evidence_atoms))
    held["S4_identity_measurable"] = m0.ks_S4_representation_measurability(g, identity, gamma)
    merged = ((0, 1),) + tuple((i,) for i in range(2, g.evidence_atoms))
    held["S4_merged_pair_not_measurable"] = not m0.ks_S4_representation_measurability(g, merged, gamma)
    # S5: re-certifying every admitted atom under another warranting policy leaves signatures unchanged
    swapped = m0.GovernedSpace(g.ks, {k: Cert.DEMONSTRATION for k in g.certificates}, g.evidence_atoms, g.meter, g.revoked)
    held["S5_policy_swap_invariant"] = _signatures_equal(g, swapped, samples)
    # S6 on the machine: every populated label is in canonical antichain form (Min is idempotent)
    held["S6_labels_canonical"] = all(kso._canon_profile(a.profile) == a.profile for a in ks.atoms)
    # S7: the population metered every admission and composition
    held["S7_metered"] = g.meter.admit == len(ks.atoms) and g.meter.compose == sum(1 for e in ks.hyperedges if e.relation_type == "COMPOSITION")
    held["genome_digest_unchanged"] = m0.genome_digest() == digest_before
    bad = {k: v for k, v in held.items() if v is False}
    assert not bad, bad
    return held


def _signatures_equal(g, swapped, samples) -> bool:
    a, b = g.ks.atom_map(), swapped.ks.atom_map()
    return all(kso.profile_live(a[x].profile, r) == kso.profile_live(b[x].profile, r) for x in g.ks.ids for r in samples)


# ----------------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------------


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(split: str = "dev", split_seed: str = "ME-X1-DEV-20260902", per_family: int = 2) -> dict[str, object]:
    gen, model, oracle = _mex1()
    if split != "dev" or per_family > 5:
        raise CannotCheck("M1 population runs on the public development split only (≤ 5 per family)")
    digest_before = m0.genome_digest()
    t0 = time.time()
    pairs = gen.generate_split(split, split_seed, {f: per_family for f in model.FAMILIES})
    worlds = []
    totals = {"atoms": 0, "hyperedges": 0, "p2_cells": 0, "p3_revocations": 0, "p3_parent_raised_worlds": 0, "events_replayed": 0, "events_acquisition_needed": 0,
              "v1_revoked_base_atoms": 0, "v1_unknown_base_atoms": 0, "v1_p2_cells": 0, "v1_worlds_with_revocation_or_censoring": 0,
              "v0_oracle_negative_cells": 0, "v1_oracle_negative_cells": 0, "constraint_power_worlds_caught": 0, "p4_direction_i_worlds": 0, "p4_hub_is_target_claim": 0}
    for inst, exp in pairs:
        pop = populate(inst.world_v0)
        rec = {"instance_id": inst.instance_id, "family": inst.family, "variant": inst.variant, "oracle_action": exp.action, "base_atoms": len(pop.base_index), "registered_revoked": len(pop.registered_revoked), "unknown": len(pop.unknown)}
        rec["P1_dense"] = check_P1_dense(pop)
        rec["P2_label_equals_oracle"] = check_P2_label_equals_oracle(pop, inst.world_v0)
        rec["P3_retraction"] = check_P3_retraction(pop, inst.world_v0)
        rec["P3_events"] = check_P3_events(pop, inst)
        rec["P4_hub"] = check_P4_hub(pop)
        rec["P5_genome"] = check_P5_genome(pop, digest_before)
        rec["P2_constraint_power"] = check_P2_constraint_power(inst.world_v0, inst.request.target_claim_id)
        # the post-event world v1 carries the registered INVALID / UNKNOWN statuses: populate it too,
        # so that P2 is exercised on real revoked and censored base atoms, not only on an all-VALID v0
        w1 = oracle.final_world(inst.world_v0, inst.events)
        pop1 = populate(w1)
        rec["v1"] = {"base_atoms": len(pop1.base_index), "registered_revoked": len(pop1.registered_revoked), "unknown": len(pop1.unknown),
                     "P1_dense": check_P1_dense(pop1), "P2_label_equals_oracle": check_P2_label_equals_oracle(pop1, w1), "P5_genome": check_P5_genome(pop1, digest_before)}
        totals["v1_revoked_base_atoms"] += rec["v1"]["registered_revoked"]
        totals["v1_unknown_base_atoms"] += rec["v1"]["unknown"]
        totals["v1_p2_cells"] += rec["v1"]["P2_label_equals_oracle"]["cells"]
        totals["v1_worlds_with_revocation_or_censoring"] += 1 if (rec["v1"]["registered_revoked"] or rec["v1"]["unknown"]) else 0
        totals["v0_oracle_negative_cells"] += rec["P2_label_equals_oracle"]["oracle_negative_cells"]
        totals["v1_oracle_negative_cells"] += rec["v1"]["P2_label_equals_oracle"]["oracle_negative_cells"]
        totals["constraint_power_worlds_caught"] += 1 if rec["P2_constraint_power"]["tail_drop_mutant_caught"] == "CAUGHT" else 0
        totals["p4_direction_i_worlds"] += 1 if rec["P4_hub"]["direction_i"]["holds"] else 0
        totals["p4_hub_is_target_claim"] += 1 if rec["P4_hub"]["hub"] == f"claim:{inst.request.target_claim_id}" else 0
        worlds.append(rec)
        totals["atoms"] += rec["P1_dense"]["atoms"]
        totals["hyperedges"] += rec["P1_dense"]["hyperedges"]
        totals["p2_cells"] += rec["P2_label_equals_oracle"]["cells"]
        totals["p3_revocations"] += rec["P3_retraction"]["revocations_checked"]
        totals["p3_parent_raised_worlds"] += 1 if rec["P3_retraction"]["renormalising_parent_raised_unreachable_atom"] else 0
        totals["events_replayed"] += 1 if rec["P3_events"]["status"] == "REPLAYED" else 0
        totals["events_acquisition_needed"] += 1 if rec["P3_events"]["status"] != "REPLAYED" else 0
    assert totals["p3_parent_raised_worlds"] >= 1, "the renormalising parent never differed — the must-differ control did not fire"
    assert totals["v1_worlds_with_revocation_or_censoring"] >= 1, "no v1 world carries a revoked or censored base atom — P2 would be vacuous"
    assert totals["v1_oracle_negative_cells"] >= 1, "P2 has no oracle-negative cell anywhere — NO_POWER"
    assert totals["constraint_power_worlds_caught"] >= 1, "the CONSTRAINT tail-drop mutant was never caught — NO_POWER"
    assert totals["p4_direction_i_worlds"] >= 1, "KS-T06b direction (i) never exhibited on a real world — NO_POWER"
    seconds = round(time.time() - t0, 1)
    return {
        "schema": "orion.kso.m1-population-receipt.v1",
        "provenance": {"command": f"python research/orion-machine/reference/kso_m1_mex1_population_v1.py --per-family {per_family} --out research/orion-machine/results/KSO_M1_POPULATION_RECEIPT_V1.json",
                       "python": sys.version.split()[0], "split_seed": split_seed, "declared_nondeterminism": "none: generator seeded by split_seed; all arithmetic exact rational; float only in reaction surprise (deterministic IEEE)",
                       "wall_seconds_not_part_of_the_reproducible_body": seconds},
        "contract": "KnowledgeSpace.v1-M1",
        "source": {"generator": "research/experiments/me-x1/mex1_generator.py", "oracle": "research/experiments/me-x1/mex1_oracle.py", "split": split, "split_seed": split_seed, "per_family": per_family, "families": list(model.FAMILIES)},
        "bindings": {p.name: sha256_file(p) for p in (MEX1 / "mex1_generator.py", MEX1 / "mex1_oracle.py", MEX1 / "mex1_model.py", HERE / "kso_math_v1.py", HERE / "kso_m0_freeze_checks_v1.py", HERE / "kso_m1_mex1_population_v1.py")},
        "worlds": worlds,
        "totals": {**totals, "worlds": len(worlds)},
        "genome_digest": digest_before,
        "power": {"P2_v0": "NO_POWER__ALL_CELLS_POSITIVE (reported, not evidence)" if totals["v0_oracle_negative_cells"] == 0 else "POWERED",
                  "P2_v1": f"POWERED: {totals['v1_oracle_negative_cells']} oracle-negative cells over {totals['v1_worlds_with_revocation_or_censoring']} worlds",
                  "P2_constraint_edge": f"POWERED by derived negative-evidence worlds: tail-drop mutant caught on {totals['constraint_power_worlds_caught']}/{len(worlds)} (generator plants 0 negatives)",
                  "P4_direction_i": f"{totals['p4_direction_i_worlds']}/{len(worlds)} worlds exhibit hub-raw-first ∧ specific-surprise-first with the planted popularity ranker differing; hub is the target claim on {totals['p4_hub_is_target_claim']}/{len(worlds)}",
                  "P4_direction_ii": "NOT_DISCRIMINATING (record only)", "P4_direction_iii": "IDENTITY (no-alarm only)"},
        "terminals": {"M1_KSO_INSTANCE": "GREEN_DEV_SPLIT", "M1_PROTECTED": "NOT_RUN", "M2_SOLVE_LOOP": "NOT_RUN", "GENERAL_NOVELTY": "NOT_ESTABLISHED"},
        "authority": "development split; population and invariant checks only; no solve-loop, comparator or novelty authority",
    }


def _default(o):
    if isinstance(o, Fraction):
        return str(o)
    if isinstance(o, (frozenset, set)):
        return sorted(o)
    raise TypeError(type(o).__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=2)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        result = run(per_family=args.per_family)
        # byte reproducibility: a second run in the same process must produce the same body
        body = lambda r: json.dumps({k: v for k, v in r.items() if k != "provenance"}, sort_keys=True, default=_default)  # noqa: E731
        second = run(per_family=args.per_family)
        result["provenance"]["byte_reproducible_in_process"] = body(result) == body(second)
        result["provenance"]["body_sha256"] = hashlib.sha256(body(result).encode()).hexdigest()
        assert result["provenance"]["byte_reproducible_in_process"], "receipt body differed between two in-process runs"
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True, default=_default)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text if not args.out else json.dumps({**result["totals"], "body_sha256": result["provenance"]["body_sha256"], "byte_reproducible_in_process": result["provenance"]["byte_reproducible_in_process"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
