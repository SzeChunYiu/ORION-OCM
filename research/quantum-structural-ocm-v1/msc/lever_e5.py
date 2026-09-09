"""E5 lever (post-freeze engineering-chain pass): cone confirmation.

Stage attribution (from the E4 component decomposition, measured on the frozen stream):
the E4 objects residual above the Q1 parent is NOT counting work. Per task,

    Q2_QUOTIENT_E4 objects 839.34
      = 540.94 counting (block warrant checks + firings + lookups)
      +   8.66 path-block member fetch
      + 289.75 charged full-closure fallback (= 488 atoms x 19 positives / 32 tasks)

and the counting stage alone already beats the parent (540.94 vs 767.88). The failing
stage is witness extraction: path_blocks never yields a member set that confirms, so
every positive falls back. Root cause: the fully-inside induced-subfield restriction
drops any derivation edge that carries a side-head outside the extracted region, while
production gated_closure fires edges and admits heads individually -- and the
single-path backward walk discards the rest of the counted cone.

Lever: confirm on the COUNTED CONE (all blocks with count > 0 at early stop) under the
production-faithful tail projection: an edge is kept when every tail lies in the region,
with heads restricted to the region. Soundness of the projection: a firing inside the
projected subfield (tails reached in-region, warrant live) is a firing in the full field
admitting a subset of the same heads, so any SUPPORTED witness is a field witness; the
projection never invents derivations. Cone sufficiency (why the fallback becomes
unreachable): at early stop the firing trace realizes a quotient derivation whose blocks
are all counted, and every trace qedge's live head blocks were credited -- for singleton
blocks the trace is a concrete edge-path inside the cone under the tail projection.
Residual ambiguity exists only at non-singleton (merged) blocks; the charged fallback is
kept for that case and its counter is recorded.

Python 3.8-compatible syntax.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Tuple

import quotient as _q
from arms import (NOT_SUPPORTED, SUPPORTED, Q2Quotient, finish_record,
                  new_task_record)
from lever_e4 import Q2E4, Q5E4
from ocm.kso.navigation import gated_closure
from ocm.kso.space import Hyperedge, KnowledgeSpace


def cone_confirm(ks, s: str, t: str, revoked,
                 member_tuples) -> Tuple[bool, Dict[str, int], set]:
    """Exact check on the tail-projected induced subfield of the counted cone.

    Charge mirrors confirm_on_induced: one member fetch per region atom, one edge per
    kept projected edge.
    """
    mset = set()
    for mem in member_tuples:
        mset |= set(mem)
    mset |= {s, t}
    sub_atoms = tuple(a for a in ks.atoms if a.atom_id in mset)
    sub_edges = []
    for e in ks.hyperedges:
        if not (set(e.tails) <= mset):
            continue
        heads = tuple(h for h in e.heads if h in mset)
        if not heads:
            continue
        sub_edges.append(Hyperedge(e.edge_id, e.tails, heads, e.relation_type,
                                   warrant=e.warrant))
    sub = KnowledgeSpace(sub_atoms, tuple(sub_edges))
    reached = gated_closure(sub, [s], revoked)
    ok = t in reached
    witness = _q._witness_in_induced(sub, s, t, reached, revoked) if ok else set()
    metrics = {"verifier_calls": 1, "induced_atoms": len(sub_atoms),
               "induced_edges": len(sub_edges), "objects_touched": len(mset)}
    return ok, metrics, witness


class Q2E5(Q2E4):
    """Q2 with E4 scheduling + E5 cone confirmation; costs fully charged."""

    def __init__(self):
        Q2E4.__init__(self)
        self.name = "Q2_QUOTIENT_E4E5"
        self.cone_confirms = 0
        self.cone_confirm_fallbacks = 0

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
        # E5: witness region = the counted cone, confirmed under the tail projection.
        members = [view.blocks[b] for b in counted_blocks] \
            or [view.blocks[view.partition[t]]]
        ok, met, witness = cone_confirm(self.ks, s, t, revoked, members)
        rec["verifier_calls"] += 1
        rec["objects_touched"] += met["objects_touched"]
        rec["edges_touched"] += met["induced_edges"]
        self.confirmations_used += 1
        if ok:
            decision = SUPPORTED
            self.cone_confirms += 1
        else:
            self.confirmation_fallbacks += 1
            self.cone_confirm_fallbacks += 1
            reached = gated_closure(self.ks, [s], revoked)
            rec["verifier_calls"] += 1
            rec["objects_touched"] += len(self.ks.atoms)
            decision = SUPPORTED if t in reached else NOT_SUPPORTED
            witness = {s, t} if decision == SUPPORTED else set()
        finish_record(rec, decision, truth, cand_obj - {s}, witness)
        rec["mechanism"] = dict(mech, quotient_confirmation=True,
                                confirmation_fallback=(not ok),
                                cone_members=met["objects_touched"],
                                projected_induced_edges=met["induced_edges"])
        rec["extra"]["k_active_blocks"] = len(counted_blocks)
        rec["extra"]["k_active_objects"] = len(cand_obj)
        self.lifetime["tasks"] += 1
        return rec


class Q5E5(Q5E4):
    """Q5 with E4 scheduling + E5 cone probing region; costs fully charged."""

    def __init__(self):
        Q5E4.__init__(self)
        self.name = "Q5_COMPOSED_E4E5"
        self.cone_confirms = 0
        self.cone_confirm_fallbacks = 0

    def _confirm_by_probing(self, members: set, s: str, t: str,
                            revoked: FrozenSet) -> Tuple[bool, dict, set]:
        """Same acquisition discipline as Q5Composed._confirm_by_probing, with the E5
        tail projection: an edge whose tails are all in-region is usable, heads are
        admitted individually in-region (production semantics); edges carrying outside
        side-heads are no longer dropped."""
        reached = {s}
        revealed = set()
        pending = {}
        revealed_tail_index = {}
        parent_edge = {s: None}
        c = {"probes": 0, "expansions": 0, "warrant_observations": 0}
        summary = self.pf.channel_summary() if self.probe_policy == "rarity" else None
        rarity = {}

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

        def drain(new_atoms):
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
            new_atoms = []
            for e in postings:
                if not (set(e.tails) <= members):  # E5: tails-in-region projection
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
            rec["extra"]["k_active_objects"] = sum(len(view.blocks[b])
                                                   for b in counted_blocks)
            return rec
        # E5: probe region = the counted cone.
        members = set()
        for b in counted_blocks:
            members |= set(view.blocks[b])
        members |= {s, t}
        rec["extra"]["cone_members"] = len(members)
        self.cone_restrictions_applied += 1
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
        self.confirmations_used += 1
        self.lifetime["verifier_calls"] += 1
        if ok:
            decision = SUPPORTED
            self.cone_confirms += 1
        else:
            self.confirmation_fallbacks += 1
            self.cone_confirm_fallbacks += 1
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
