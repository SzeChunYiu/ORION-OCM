"""MSC V1 arms: Q0 full scan, Q1 indexed, Q2 quotient, Q3 subspace, Q4 probe,
Q4 shuffle-null control, Q5 composed (+ ablations).

Every arm replays the identical frozen stream and answers the identical D1(s,t) tasks with
the identical information surface (the field + stream events). What differs is consumption:
each arm pays for exactly the structure it uses, at build, maintenance, query and reopen
time. The instrumented closure mirrors production gated_closure (validated by the test
suite and by a pre-run equality assertion); production code stays the decision ground truth.

Python 3.8-compatible syntax.
"""
from __future__ import annotations

import random
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

from ocm.kso.extraction_index import ExtractionIndex
from ocm.kso.navigation import gated_closure, ungated_closure
from ocm.kso.space import KnowledgeSpace

from probing import NOT_SUPPORTED, ProbeField, SUPPORTED, probe_decide
from quotient import Quotient, confirm_on_induced
from world import measure_bytes

CUSTODY = "custody"


def instrumented_closure(ks: KnowledgeSpace, start: Sequence[str], revoked: FrozenSet,
                         use_index: bool = True,
                         parents: Optional[Dict[str, str]] = None) -> dict:
    """gated_closure with consumption counters (and an optional derivation parent map).

    use_index=True charges the production adjacency index (Q1); use_index=False scans the
    raw edge tuple per worklist pop (Q0, the no-index baseline). Decisions are identical by
    construction; only consumption differs.
    """
    c = {"atom_warrant_checks": 0, "edge_warrant_checks": 0, "expansions": 0,
         "edges_examined": 0, "objects_touched": 0}
    amap = ks.atom_view
    live = {}
    for x in ks.ids:
        c["atom_warrant_checks"] += 1
        live[x] = amap[x].is_live(revoked)
    pending = {e.edge_id: len(e.tails) for e in ks.hyperedges}
    reached = {x for x in start if live[x]}
    work = list(reached)
    if parents is not None:
        for x in reached:
            parents.setdefault(x, None)
    fired_edges = []
    while work:
        v = work.pop()
        c["expansions"] += 1
        if use_index:
            out_edges = ks.outgoing_edges(v)
            c["edges_examined"] += len(out_edges)
        else:
            out_edges = [e for e in ks.hyperedges if v in e.tails]
            c["edges_examined"] += len(ks.hyperedges)
        for e in out_edges:
            pending[e.edge_id] -= 1
            if pending[e.edge_id] == 0:
                c["edge_warrant_checks"] += 1
                if e.warrant.is_live(revoked):
                    fired_edges.append(e.edge_id)
                    for h in e.heads:
                        if h not in reached and live[h]:
                            reached.add(h)
                            work.append(h)
                            if parents is not None:
                                parents[h] = e.edge_id
    c["objects_touched"] = len(reached) + c["atom_warrant_checks"] // max(1, 1)
    c["fired_edges"] = len(fired_edges)
    return {"reached": reached, "counters": c}


def witness_from_parents(parents: Dict[str, str], edge_index, s: str, t: str) -> set:
    """Atoms on one concrete derivation path s->t (BFS parent chain)."""
    if t not in parents and t != s:
        return set()
    chain = {s, t}
    cur = t
    guard = 0
    while cur != s and guard < 10 ** 6:
        guard += 1
        eid = parents.get(cur)
        if eid is None:
            break
        e = edge_index[eid]
        for x in e.tails:
            chain.add(x)
        cur = next(iter(e.tails)) if e.tails else s
    return chain


def new_task_record() -> Dict[str, object]:
    return {"decision": None, "objects_touched": 0, "edges_touched": 0,
            "candidates": 0, "false_candidates": 0, "probes": 0, "expansions": 0,
            "verifier_calls": 0, "mechanism": {}, "extra": {}}


def finish_record(rec, decision, truth, candidates: set, witness: set) -> None:
    rec["decision"] = decision
    rec["correct"] = (decision == SUPPORTED) == truth
    rec["candidates"] = len(candidates)
    if not truth:
        rec["false_candidates"] = len(candidates)
    else:
        rec["false_candidates"] = len([x for x in candidates if x not in witness])


# ---------------------------------------------------------------------------
# Q0 — full/global exact scan (no index, no quotient)
# ---------------------------------------------------------------------------

class Q0FullScan(object):
    name = "Q0_FULL_SCAN"

    def __init__(self):
        self.ks = None
        self.lifetime = {"tasks": 0, "atom_warrant_checks": 0, "edge_warrant_checks": 0,
                         "edges_examined": 0, "expansions": 0, "verifier_calls": 0,
                         "build_work": 0, "maintenance_work": 0, "reopen_work": 0,
                         "persistent_bytes": 0}

    def on_field(self, ks: KnowledgeSpace) -> None:
        self.ks = ks  # no auxiliary structure; the field itself is read raw each task

    def on_admission(self, ks: KnowledgeSpace, new_edges) -> None:
        self.ks = ks  # nothing to maintain

    def on_revocation(self, evidence) -> None:
        pass  # liveness is re-read from the field at every task

    def decide(self, s: str, t: str, revoked: FrozenSet, truth: bool) -> Dict[str, object]:
        parents = {}
        res = instrumented_closure(self.ks, [s], revoked, use_index=False, parents=parents)
        c = res["counters"]
        decision = SUPPORTED if t in res["reached"] else NOT_SUPPORTED
        rec = new_task_record()
        rec["objects_touched"] = c["objects_touched"]
        rec["edges_touched"] = c["edges_examined"]
        rec["expansions"] = c["expansions"]
        rec["verifier_calls"] = 1
        rec["mechanism"] = {"scan_edges_per_expansion": c["edges_examined"]}
        witness = witness_from_parents(parents, self.ks.edge_view, s, t) if decision == SUPPORTED else set()
        finish_record(rec, decision, truth, res["reached"] - {s}, witness)
        for k in ("atom_warrant_checks", "edge_warrant_checks", "edges_examined", "expansions"):
            self.lifetime[k] += c[k]
        self.lifetime["verifier_calls"] += 1
        self.lifetime["tasks"] += 1
        return rec

    def serve_d2(self, ks: KnowledgeSpace, members: Sequence[str],
                 build: bool = False) -> Dict[str, object]:
        amap = ks.atom_view
        cands = [m for m in members if amap[m].authority.rank(CUSTODY) >= 2]
        return {"decision": cands[0] if len(cands) == 1 else "NO_UNIQUE_MEMBER",
                "status": "NATIVE_IDENTITY", "members_fetched": len(members),
                "serialized_state_bytes": measure_bytes(
                    {"members": sorted(members)})}


# ---------------------------------------------------------------------------
# Q1 — production exact typed/indexed retrieval (strongest-parent arm)
# ---------------------------------------------------------------------------

class Q1Indexed(object):
    name = "Q1_INDEXED"

    def __init__(self):
        self.ks = None
        self.index = None
        self.rebuilds = 0
        self.lifetime = {"tasks": 0, "atom_warrant_checks": 0, "edge_warrant_checks": 0,
                         "edges_examined": 0, "expansions": 0, "verifier_calls": 0,
                         "build_work": 0, "maintenance_work": 0, "reopen_work": 0,
                         "persistent_bytes": 0}

    def _build(self, ks: KnowledgeSpace) -> None:
        self.index = ExtractionIndex(ks)
        self.rebuilds += 1
        bw = dict(self.index.build_work)
        self.lifetime["build_work"] += int(bw.get("outgoing_postings_built", 0)) + \
            int(bw.get("atom_entries_built", 0)) + int(bw.get("edge_entries_scanned", 0))
        adj = {v: [e.edge_id for e in ks.outgoing_edges(v)] for v in ks.ids}
        self.lifetime["persistent_bytes"] = measure_bytes(adj)

    def on_field(self, ks: KnowledgeSpace) -> None:
        self.ks = ks
        self._build(ks)

    def on_admission(self, ks: KnowledgeSpace, new_edges) -> None:
        self.ks = ks
        self._build(ks)  # snapshot-bound: structural update forces a charged rebuild

    def on_revocation(self, evidence) -> None:
        pass  # structure unchanged: index stays valid; liveness re-evaluated per query

    def decide(self, s: str, t: str, revoked: FrozenSet, truth: bool) -> Dict[str, object]:
        parents = {}
        res = instrumented_closure(self.ks, [s], revoked, use_index=True, parents=parents)
        c = res["counters"]
        decision = SUPPORTED if t in res["reached"] else NOT_SUPPORTED
        rec = new_task_record()
        rec["objects_touched"] = c["objects_touched"]
        rec["edges_touched"] = c["edges_examined"]
        rec["expansions"] = c["expansions"]
        rec["verifier_calls"] = 1
        witness = witness_from_parents(parents, self.ks.edge_view, s, t) if decision == SUPPORTED else set()
        finish_record(rec, decision, truth, res["reached"] - {s}, witness)
        for k in ("atom_warrant_checks", "edge_warrant_checks", "edges_examined", "expansions"):
            self.lifetime[k] += c[k]
        self.lifetime["verifier_calls"] += 1
        self.lifetime["tasks"] += 1
        return rec

    def serve_d2(self, ks: KnowledgeSpace, members: Sequence[str],
                 build: bool = False) -> Dict[str, object]:
        amap = ks.atom_view
        cands = [m for m in members if amap[m].authority.rank(CUSTODY) >= 2]
        return {"decision": cands[0] if len(cands) == 1 else "NO_UNIQUE_MEMBER",
                "status": "NATIVE_IDENTITY", "members_fetched": len(members),
                "serialized_state_bytes": measure_bytes(
                    {"adjacency_bytes": self.lifetime["persistent_bytes"],
                     "members": sorted(members)})}


# ---------------------------------------------------------------------------
# Q2 — exact decision-sufficient quotient (FQ-1)
# ---------------------------------------------------------------------------

class Q2Quotient(object):
    name = "Q2_QUOTIENT"

    def __init__(self, incremental: bool = False):
        self.ks = None
        self.q: Optional[Quotient] = None
        self.incremental = incremental  # E1 lever (off in the base policy: rebuild)
        if incremental:
            self.name = "Q2_QUOTIENT_E1"
        self.rebuilds = 0
        self.lifetime = {"tasks": 0, "atom_warrant_checks": 0, "edge_warrant_checks": 0,
                         "edges_examined": 0, "expansions": 0, "verifier_calls": 0,
                         "build_work": 0, "maintenance_work": 0, "reopen_work": 0,
                         "quotient_build_atom_sig_evals": 0,
                         "quotient_build_incidence_evals": 0,
                         "quotient_build_passes": 0,
                         "quotient_blocks": 0, "quotient_qedges": 0,
                         "persistent_bytes": 0}
        self.refutations_used = 0
        self.confirmations_used = 0
        self.confirmation_fallbacks = 0

    def _charge_build(self, q: Quotient) -> None:
        bw = q.build_work
        self.lifetime["build_work"] += (int(bw.get("atom_signature_evaluations", 0))
                                        + int(bw.get("incidence_evaluations", 0)))
        self.lifetime["quotient_build_atom_sig_evals"] += int(bw.get("atom_signature_evaluations", 0))
        self.lifetime["quotient_build_incidence_evals"] += int(bw.get("incidence_evaluations", 0))
        self.lifetime["quotient_build_passes"] += int(bw.get("refinement_passes", 0))
        self.lifetime["quotient_blocks"] = len(q.blocks)
        self.lifetime["quotient_qedges"] = len(q.qedges)
        self.lifetime["persistent_bytes"] = measure_bytes(q.serialize())

    def on_field(self, ks: KnowledgeSpace) -> None:
        self.ks = ks
        self.q = Quotient(ks)
        self.rebuilds += 1
        self._charge_build(self.q)

    def on_admission(self, ks: KnowledgeSpace, new_edges) -> None:
        self.ks = ks
        if self.incremental:
            self.q.incremental_maintain(ks, new_edges)
            mw = self.q.maintenance_work
            self.lifetime["maintenance_work"] += int(mw.get("atom_signature_evaluations", 0)) \
                + int(mw.get("incidence_evaluations", 0)) + int(mw.get("atoms_resigned", 0)) \
                + int(mw.get("qedges_regrouped", 0))
            # maintenance accumulates in the quotient's own dicts; reset per update
            self.q.maintenance_work = {}
            self.lifetime["quotient_blocks"] = len(self.q.blocks)
            self.lifetime["quotient_qedges"] = len(self.q.qedges)
            self.lifetime["persistent_bytes"] = measure_bytes(self.q.serialize())
        else:
            self.q.rebuild(ks)
            self.rebuilds += 1
            self._charge_build(self.q)

    def on_revocation(self, evidence) -> None:
        pass  # structure unchanged; block liveness re-evaluated per query under R

    def decide(self, s: str, t: str, revoked: FrozenSet, truth: bool) -> Dict[str, object]:
        rec = new_task_record()
        view = self.q.split_singletons([s, t])
        res = view.counting_closure(s, revoked, t, early_stop=True)
        m = res["m"]
        mech = {"quotient_expansions": m["quotient_expansions"],
                "quotient_firings": m["quotient_firings"],
                "block_warrant_checks": m["block_warrant_checks"],
                "split_blocks": view.split_work.get("split_blocks", 0),
                "qedges_remapped": view.split_work.get("qedges_remapped", 0)}
        rec["expansions"] = m["quotient_expansions"]
        rec["edges_touched"] = m["qedge_warrant_checks"]
        rec["objects_touched"] = m["block_warrant_checks"] + m["quotient_firings"] \
            + view.split_work.get("member_lookups", 0)
        counted_blocks = [b for b, cnt in res["counts"].items() if cnt > 0]
        cand_obj = set()
        for b in counted_blocks:
            cand_obj |= set(view.blocks[b])
        if res["refuted"]:
            finish_record(rec, NOT_SUPPORTED, truth, cand_obj, set())
            rec["mechanism"] = dict(mech, quotient_refutation=True)
            self.refutations_used += 1
            self.lifetime["tasks"] += 1
            rec["extra"]["k_active_blocks"] = len(counted_blocks)
            rec["extra"]["k_active_objects"] = len(cand_obj)
            return rec
        # quotient admission: confirm on the induced subfield of one derivation path
        blocks = view.path_blocks(res, s, t)
        members = [view.blocks[b] for b in blocks] or [view.blocks[view.partition[t]]]
        ok, met, witness = confirm_on_induced(self.ks, s, t, revoked, members)
        rec["verifier_calls"] += 1
        rec["objects_touched"] += met["objects_touched"]
        rec["edges_touched"] += met["induced_edges"]
        self.confirmations_used += 1
        if ok:
            decision = SUPPORTED
        else:
            self.confirmation_fallbacks += 1
            reached = gated_closure(self.ks, [s], revoked)
            rec["verifier_calls"] += 1
            rec["objects_touched"] += len(self.ks.atoms)
            decision = SUPPORTED if t in reached else NOT_SUPPORTED
            witness = {s, t} if decision == SUPPORTED else set()
        finish_record(rec, decision, truth, cand_obj - {s}, witness)
        rec["mechanism"] = dict(mech, quotient_confirmation=True,
                                confirmation_fallback=(not ok))
        rec["extra"]["k_active_blocks"] = len(counted_blocks)
        rec["extra"]["k_active_objects"] = len(cand_obj)
        self.lifetime["tasks"] += 1
        return rec

    def serve_d2(self, ks: KnowledgeSpace, members: Sequence[str],
                 build: bool = False) -> Dict[str, object]:
        """FQ-5 hostile service: quotient state first, insufficiency, then charged reopen."""
        out = {}
        if build:
            q = Quotient(ks)
            self._charge_build(q)
        else:
            q = self.q
        block = None
        for b, mem in q.blocks.items():
            if set(members) <= set(mem) and len(mem) == len(members):
                block = b
                break
        summary = q.authority_summary(block)
        state_bytes = measure_bytes(q.serialize())
        if summary["custody_members"] == 1:
            # knowing THAT exactly one member carries custody does not determine WHICH:
            # the identity<->authority pairing is the missing coordinate.
            member, status = q.reopen_member_selection(block)
            return {"decision": member,
                    "status": "REPRESENTATION_INSUFFICIENT__MISSING_COORDINATE_FOUND"
                              if status == "REOPENED" else status,
                    "summary": summary, "serialized_state_bytes": state_bytes,
                    "members_fetched": len(members), "insufficient_then_reopened": True}
        member, status = q.reopen_member_selection(block)
        return {"decision": member, "status": status, "summary": summary,
                "serialized_state_bytes": state_bytes,
                "members_fetched": len(members), "insufficient_then_reopened": False}


# ---------------------------------------------------------------------------
# Q3 — local active-subspace traversal (FQ-3)
# ---------------------------------------------------------------------------

class Q3Subspace(object):
    name = "Q3_SUBSPACE"

    def __init__(self):
        self.ks = None
        self.lifetime = {"tasks": 0, "atom_warrant_checks": 0, "edge_warrant_checks": 0,
                         "edges_examined": 0, "expansions": 0, "verifier_calls": 0,
                         "build_work": 0, "maintenance_work": 0, "reopen_work": 0,
                         "persistent_bytes": 0}
        self.cone_restrictions_applied = 0

    def on_field(self, ks: KnowledgeSpace) -> None:
        self.ks = ks

    def on_admission(self, ks: KnowledgeSpace, new_edges) -> None:
        self.ks = ks  # region is per-task; nothing persistent to maintain

    def on_revocation(self, evidence) -> None:
        pass

    def _backward_plain(self, ks: KnowledgeSpace, t: str) -> Tuple[set, int]:
        """Backward plain reachability via production incident adjacency (charged)."""
        seen = {t}
        work = [t]
        examined = 0
        while work:
            v = work.pop()
            for e in ks.incident_edges(v):
                examined += 1
                for u in e.tails:
                    if u not in seen:
                        seen.add(u)
                        work.append(u)
        return seen, examined

    def decide(self, s: str, t: str, revoked: FrozenSet, truth: bool) -> Dict[str, object]:
        rec = new_task_record()
        fwd = ungated_closure(self.ks, [s])
        bwd, examined = self._backward_plain(self.ks, t)
        region = fwd & bwd
        region |= {s, t}
        rec["edges_touched"] = examined
        rec["extra"]["region_size"] = len(region)
        rec["extra"]["field_size"] = len(self.ks.atoms)
        self.cone_restrictions_applied += 1
        sub_atoms = tuple(a for a in self.ks.atoms if a.atom_id in region)
        sub_edges = tuple(e for e in self.ks.hyperedges if e.incident <= region)
        sub = KnowledgeSpace(sub_atoms, sub_edges)
        rec["edges_touched"] += len(self.ks.hyperedges)  # induced-field construction scan
        parents = {}
        res = instrumented_closure(sub, [s], revoked, use_index=True, parents=parents)
        c = res["counters"]
        decision = SUPPORTED if t in res["reached"] else NOT_SUPPORTED
        rec["objects_touched"] = len(region) + c["objects_touched"]
        rec["edges_touched"] += c["edges_examined"]
        rec["expansions"] = c["expansions"]
        rec["verifier_calls"] = 1
        witness = witness_from_parents(parents, sub.edge_view, s, t) if decision == SUPPORTED else set()
        finish_record(rec, decision, truth, res["reached"] - {s}, witness)
        for k in ("atom_warrant_checks", "edge_warrant_checks"):
            self.lifetime[k] += c[k]
        self.lifetime["edges_examined"] += rec["edges_touched"]
        self.lifetime["expansions"] += c["expansions"]
        self.lifetime["verifier_calls"] += 1
        self.lifetime["tasks"] += 1
        return rec

    def serve_d2(self, ks: KnowledgeSpace, members: Sequence[str],
                 build: bool = False) -> Dict[str, object]:
        amap = ks.atom_view
        cands = [m for m in members if amap[m].authority.rank(CUSTODY) >= 2]
        return {"decision": cands[0] if len(cands) == 1 else "NO_UNIQUE_MEMBER",
                "status": "NATIVE_IDENTITY", "members_fetched": len(members),
                "serialized_state_bytes": measure_bytes({"members": sorted(members)})}


# ---------------------------------------------------------------------------
# Q4 — adaptive probe acquisition (FQ-2) and its mandatory shuffle-equal-n null
# ---------------------------------------------------------------------------

class Q4Probe(object):
    name = "Q4_PROBE"

    def __init__(self, policy: str = "rarity", salt: str = "ocm-q216-msc-v1-20260909/probe-default"):
        from world import stable_seed
        self.ks = None
        self.pf: Optional[ProbeField] = None
        self.policy = policy
        self.rng = random.Random(stable_seed(salt)) if policy == "shuffle" else None
        self.salt = salt
        self.lifetime = {"tasks": 0, "atom_warrant_checks": 0, "edge_warrant_checks": 0,
                         "edges_examined": 0, "expansions": 0, "verifier_calls": 0,
                         "build_work": 0, "maintenance_work": 0, "reopen_work": 0,
                         "persistent_bytes": 0, "probes": 0, "edges_revealed": 0,
                         "warrant_observations": 0, "early_stops": 0}
        self.budget: Optional[int] = None  # set per task by the null control

    def on_field(self, ks: KnowledgeSpace) -> None:
        self.ks = ks
        self._rebuild_pf()

    def _rebuild_pf(self) -> None:
        self.pf = ProbeField(self.ks)
        postings = sum(len(self.ks.outgoing_edges(v)) for v in self.ks.ids)
        self.lifetime["build_work"] += len(self.ks.ids) + postings

    def on_admission(self, ks: KnowledgeSpace, new_edges) -> None:
        self.ks = ks
        self._rebuild_pf()  # adjacency refresh is charged

    def on_revocation(self, evidence) -> None:
        pass  # warrants observed live per query

    def decide(self, s: str, t: str, revoked: FrozenSet, truth: bool) -> Dict[str, object]:
        before = dict(self.pf.counters)
        budget_arg = None
        if self.budget is not None:
            # null control: per-task budget on top of this arm's consumed probe count
            budget_arg = before.get("probes", 0) + self.budget
        res = probe_decide(self.pf, s, t, revoked, policy=self.policy,
                           rng=self.rng, budget=budget_arg)
        c = res["counters"]
        rec = new_task_record()
        rec["decision"] = res["decision"]
        rec["correct"] = (res["decision"] == SUPPORTED) == truth
        rec["probes"] = c["probes"]
        rec["expansions"] = c["expansions"]
        rec["verifier_calls"] = 0
        after = self.pf.counters
        rec["objects_touched"] = c["probes"] + c["atoms_admitted"]
        rec["edges_touched"] = after.get("edges_revealed", 0) - before.get("edges_revealed", 0)
        rec["mechanism"] = {"early_stopped": c["early_stopped"],
                            "budget_exhausted": c["budget_exhausted"],
                            "warrant_observations": after.get("warrant_observations", 0) - before.get("warrant_observations", 0)}
        # witness via the probe admission parent chain
        witness = set()
        if res["decision"] == SUPPORTED:
            pe = res["parent_edge"]
            emap = self.ks.edge_view
            cur = t
            guard = 0
            while cur != s and guard < 10 ** 6:
                guard += 1
                witness.add(cur)
                eid = pe.get(cur)
                if eid is None:
                    break
                e = emap[eid]
                for x in e.tails:
                    witness.add(x)
                cur = e.tails[0] if e.tails else s
            witness.add(s)
        finish_record(rec, res["decision"], truth, res["reached"] - {s}, witness)
        self.lifetime["probes"] += c["probes"]
        self.lifetime["edges_revealed"] += after.get("edges_revealed", 0) - before.get("edges_revealed", 0)
        self.lifetime["warrant_observations"] += after.get("warrant_observations", 0) - before.get("warrant_observations", 0)
        self.lifetime["expansions"] += c["expansions"]
        self.lifetime["tasks"] += 1
        if c["early_stopped"]:
            self.lifetime["early_stops"] += 1
        rec["extra"]["k_active_objects"] = len(res["reached"])
        return rec

    def serve_d2(self, ks: KnowledgeSpace, members: Sequence[str],
                 build: bool = False) -> Dict[str, object]:
        # probing arms must PROBE members to observe authority (identity is in the record)
        amap = ks.atom_view
        probes = 0
        cands = []
        for m in members:
            probes += 1  # one probe per member to fetch its record
            if amap[m].authority.rank(CUSTODY) >= 2:
                cands.append(m)
        self.lifetime["probes"] += probes
        return {"decision": cands[0] if len(cands) == 1 else "NO_UNIQUE_MEMBER",
                "status": "NATIVE_IDENTITY_VIA_PROBES", "members_fetched": len(members),
                "probes": probes,
                "serialized_state_bytes": measure_bytes(
                    {"channel_summary": self.pf.channel_summary() if self.pf else {}})}


# ---------------------------------------------------------------------------
# Q5 — composed: quotient refutation + path-cone confirmation via minimal probes
# ---------------------------------------------------------------------------

class Q5Composed(object):
    name = "Q5_COMPOSED"

    def __init__(self, use_quotient: bool = True, use_cone: bool = True,
                 use_probe: bool = True, incremental: bool = False,
                 probe_policy: str = "rarity"):
        self.ks = None
        self.q: Optional[Quotient] = None
        self.pf: Optional[ProbeField] = None
        self.use_quotient = use_quotient
        self.use_cone = use_cone
        self.use_probe = use_probe
        self.incremental = incremental
        self.probe_policy = probe_policy
        self.name = "Q5_COMPOSED"
        if not use_quotient:
            self.name = "Q5_NO_QUOTIENT"
        elif not use_cone:
            self.name = "Q5_NO_CONE"
        elif not use_probe:
            self.name = "Q5_NO_PROBE"
        if incremental:
            self.name += "_E1"
        if probe_policy == "naive":
            self.name += "_NAIVEORDER"
        self.lifetime = {"tasks": 0, "atom_warrant_checks": 0, "edge_warrant_checks": 0,
                         "edges_examined": 0, "expansions": 0, "verifier_calls": 0,
                         "build_work": 0, "maintenance_work": 0, "reopen_work": 0,
                         "quotient_build_atom_sig_evals": 0,
                         "quotient_build_incidence_evals": 0,
                         "quotient_build_passes": 0,
                         "quotient_blocks": 0, "quotient_qedges": 0,
                         "persistent_bytes": 0, "probes": 0, "edges_revealed": 0,
                         "warrant_observations": 0, "early_stops": 0}
        self.refutations_used = 0
        self.confirmations_used = 0
        self.confirmation_fallbacks = 0
        self.cone_restrictions_applied = 0
        self.probe_early_stops = 0

    # -- maintenance -------------------------------------------------------
    def _charge_quotient_build(self) -> None:
        bw = self.q.build_work
        self.lifetime["build_work"] += (int(bw.get("atom_signature_evaluations", 0))
                                        + int(bw.get("incidence_evaluations", 0)))
        self.lifetime["quotient_build_atom_sig_evals"] += int(bw.get("atom_signature_evaluations", 0))
        self.lifetime["quotient_build_incidence_evals"] += int(bw.get("incidence_evaluations", 0))
        self.lifetime["quotient_build_passes"] += int(bw.get("refinement_passes", 0))
        self.lifetime["quotient_blocks"] = len(self.q.blocks)
        self.lifetime["quotient_qedges"] = len(self.q.qedges)
        self.lifetime["persistent_bytes"] = measure_bytes(self.q.serialize())

    def on_field(self, ks: KnowledgeSpace) -> None:
        self.ks = ks
        if self.use_quotient:
            self.q = Quotient(ks)
            self._charge_quotient_build()
        if self.use_probe:
            self.pf = ProbeField(ks)
            self.lifetime["build_work"] += len(ks.ids) + \
                sum(len(ks.outgoing_edges(v)) for v in ks.ids)

    def on_admission(self, ks: KnowledgeSpace, new_edges) -> None:
        self.ks = ks
        if self.use_quotient:
            if self.incremental:
                self.q.incremental_maintain(ks, new_edges)
                mw = self.q.maintenance_work
                self.lifetime["maintenance_work"] += int(mw.get("atom_signature_evaluations", 0)) \
                    + int(mw.get("incidence_evaluations", 0)) + int(mw.get("atoms_resigned", 0)) \
                    + int(mw.get("qedges_regrouped", 0))
                self.q.maintenance_work = {}
                self.lifetime["quotient_blocks"] = len(self.q.blocks)
                self.lifetime["quotient_qedges"] = len(self.q.qedges)
                self.lifetime["persistent_bytes"] = measure_bytes(self.q.serialize())
            else:
                self.q.rebuild(ks)
                self._charge_quotient_build()
        if self.use_probe:
            self.pf = ProbeField(ks)
            self.lifetime["build_work"] += len(ks.ids) + \
                sum(len(ks.outgoing_edges(v)) for v in ks.ids)

    def on_revocation(self, evidence) -> None:
        pass

    # -- decision ------------------------------------------------------------
    def _confirm_by_probing(self, members: set, s: str, t: str,
                            revoked: FrozenSet) -> Tuple[bool, dict]:
        """Acquire the path-block induced subfield via probes only, then evaluate exactly.

        Probes members in policy order (rarity via the charged channel summary; naive is
        insertion order); only edges fully inside the member region can fire (matching the
        induced-subfield restriction of confirm_on_induced). Stops probing once t is
        admitted (monotonicity).
        """
        reached = {s}
        revealed: set = set()
        pending: Dict[str, set] = {}
        revealed_tail_index: Dict[str, List] = {}
        parent_edge: Dict[str, str] = {s: None}
        c = {"probes": 0, "expansions": 0, "warrant_observations": 0}
        summary = self.pf.channel_summary() if self.probe_policy == "rarity" else None
        rarity: Dict[str, int] = {}

        def try_fire(edge):
            c["expansions"] += 1
            if not self.pf.edge_live(edge, revoked):
                return []
            new = []
            for h in edge.heads:
                if h in reached or h not in members:
                    continue
                if not self.pf.atom_live(h, revoked):
                    continue
                reached.add(h)
                parent_edge[h] = edge.edge_id
                rarity[h] = summary.get(edge.relation_type, 0) if summary else 0
                new.append(h)
            return new

        def drain(new_atoms: List[str]) -> None:
            dq = list(new_atoms)
            while dq:
                u = dq.pop()
                for e2 in revealed_tail_index.get(u, ()):
                    p = pending.get(e2.edge_id)
                    if p is None:
                        continue
                    p.discard(u)
                    if not p:
                        del pending[e2.edge_id]
                        dq.extend(try_fire(e2))

        member_list = sorted(members)
        while member_list:
            if t in reached:
                break
            if self.probe_policy == "rarity" and rarity:
                member_list.sort(key=lambda x: (rarity.get(x, 0), x))
            v = member_list.pop(0)
            if v in revealed:
                continue
            postings = self.pf.probe(v)
            revealed.add(v)
            c["probes"] += 1
            new_atoms: List[str] = []
            for e in postings:
                if not (set(e.tails) <= members and set(e.heads) <= members):
                    continue
                for u in e.tails:
                    revealed_tail_index.setdefault(u, []).append(e)
                un = {u for u in e.tails if u not in reached}
                if un:
                    pending.setdefault(e.edge_id, set()).update(un)
                else:
                    new_atoms.extend(try_fire(e))
            if new_atoms:
                drain(new_atoms)
        c["early_stopped"] = (t in reached and bool(member_list))
        witness = set()
        if t in reached:
            witness = {s, t}
            cur = t
            emap = self.ks.edge_view
            guard = 0
            while cur != s and guard < 10 ** 6:
                guard += 1
                eid = parent_edge.get(cur)
                if eid is None:
                    break
                e = emap[eid]
                for x in e.tails:
                    witness.add(x)
                cur = e.tails[0] if e.tails else s
        return t in reached, c, witness

    def decide(self, s: str, t: str, revoked: FrozenSet, truth: bool) -> Dict[str, object]:
        rec = new_task_record()
        if not self.use_quotient:
            # ablation: full probe BFS without quotient guidance (Q4 machinery)
            before = dict(self.pf.counters)
            res = probe_decide(self.pf, s, t, revoked, policy=self.probe_policy)
            c = res["counters"]
            rec["decision"] = res["decision"]
            rec["correct"] = (res["decision"] == SUPPORTED) == truth
            rec["probes"] = c["probes"]
            rec["expansions"] = c["expansions"]
            rec["objects_touched"] = c["probes"] + c["atoms_admitted"]
            after = self.pf.counters
            rec["edges_touched"] = after["edges_revealed"] - before["edges_revealed"]
            self.lifetime["probes"] += c["probes"]
            self.lifetime["edges_revealed"] += after["edges_revealed"] - before["edges_revealed"]
            self.lifetime["expansions"] += c["expansions"]
            self.lifetime["tasks"] += 1
            finish_record(rec, res["decision"], truth, res["reached"] - {s}, set(res["reached"]))
            rec["extra"]["k_active_objects"] = len(res["reached"])
            return rec
        view = self.q.split_singletons([s, t])
        res = view.counting_closure(s, revoked, t, early_stop=True)
        m = res["m"]
        rec["expansions"] = m["quotient_expansions"]
        rec["edges_touched"] = m["qedge_warrant_checks"]
        rec["objects_touched"] = m["block_warrant_checks"] + m["quotient_firings"] \
            + view.split_work.get("member_lookups", 0)
        counted_blocks = [b for b, cnt in res["counts"].items() if cnt > 0]
        if res["refuted"]:
            rec["decision"] = NOT_SUPPORTED
            rec["correct"] = (truth is False)
            rec["candidates"] = len(counted_blocks)
            rec["false_candidates"] = len(counted_blocks)
            rec["mechanism"] = {"quotient_refutation": True,
                                "quotient_expansions": m["quotient_expansions"]}
            self.refutations_used += 1
            self.lifetime["tasks"] += 1
            rec["extra"]["k_active_blocks"] = len(counted_blocks)
            rec["extra"]["k_active_objects"] = sum(len(view.blocks[b]) for b in counted_blocks)
            return rec
        blocks = view.path_blocks(res, s, t)
        members: set = set()
        for b in blocks:
            members |= set(view.blocks[b])
        members |= {s, t}
        if not self.use_cone:
            members = set(self.ks.ids)  # ablation: confirm over the whole field
        rec["extra"]["cone_members"] = len(members)
        self.cone_restrictions_applied += 1
        ok = False
        witness: set = set()
        if self.use_probe:
            ok, pc, witness = self._confirm_by_probing(members, s, t, revoked)
            rec["probes"] = pc["probes"]
            rec["expansions"] += pc["expansions"]
            rec["objects_touched"] += pc["probes"]
            rec["verifier_calls"] += 1
            self.lifetime["probes"] += pc["probes"]
            self.lifetime["expansions"] += pc["expansions"]
            if pc.get("early_stopped"):
                self.probe_early_stops += 1
                self.lifetime["early_stops"] = self.lifetime.get("early_stops", 0) + 1
        else:
            ok, met, witness = confirm_on_induced(
                self.ks, s, t, revoked,
                [tuple(sorted(members))] if self.use_cone
                else [tuple(sorted(set(self.ks.ids)))])
            rec["verifier_calls"] += 1
            rec["objects_touched"] += met["objects_touched"]
            rec["edges_touched"] += met["induced_edges"]
        self.confirmations_used += 1
        self.lifetime["verifier_calls"] += 1
        if ok:
            decision = SUPPORTED
        else:
            self.confirmation_fallbacks += 1
            reached = gated_closure(self.ks, [s], revoked)
            rec["verifier_calls"] += 1
            self.lifetime["verifier_calls"] += 1
            rec["objects_touched"] += len(self.ks.atoms)
            decision = SUPPORTED if t in reached else NOT_SUPPORTED
            witness = {s, t} if decision == SUPPORTED else set()
        cand_obj = set()
        for b in counted_blocks:
            cand_obj |= set(view.blocks[b])
        finish_record(rec, decision, truth, cand_obj - {s}, witness)
        rec["mechanism"] = {"quotient_confirmation": True,
                            "confirmation_fallback": (not ok),
                            "cone_members": len(members)}
        rec["extra"]["k_active_blocks"] = len(counted_blocks)
        rec["extra"]["k_active_objects"] = len(members)
        self.lifetime["tasks"] += 1
        return rec

    def serve_d2(self, ks: KnowledgeSpace, members: Sequence[str],
                 build: bool = False) -> Dict[str, object]:
        if build:
            q = Quotient(ks)
        else:
            q = self.q
        block = None
        for b, mem in q.blocks.items():
            if set(members) <= set(mem) and len(mem) == len(members):
                block = b
                break
        summary = q.authority_summary(block)
        state_bytes = measure_bytes(q.serialize())
        if summary["custody_members"] == 1:
            member, status = q.reopen_member_selection(block)
            return {"decision": member,
                    "status": "REPRESENTATION_INSUFFICIENT__MISSING_COORDINATE_FOUND"
                              if status == "REOPENED" else status,
                    "summary": summary, "serialized_state_bytes": state_bytes,
                    "members_fetched": len(members),
                    "insufficient_then_reopened": True}
        member, status = q.reopen_member_selection(block)
        return {"decision": member, "status": status, "summary": summary,
                "serialized_state_bytes": state_bytes,
                "members_fetched": len(members),
                "insufficient_then_reopened": False}



