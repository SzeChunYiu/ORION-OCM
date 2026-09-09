"""DecisionSufficientQuotient (FQ-1) for MSC V1.

Classical partition refinement (parents: bisimulation minimization / partition refinement,
database materialized-view maintenance for the lifetime view) over the production
KnowledgeSpace, restricted to the coordinates the D1 protected decision can read:

    color(x) = (atom_type, warrant signature, quarantined)

Authority ranks, meta and content_ref are DISCARDED (declared in the protocol): they cannot
affect gated-closure membership. Discarded distinctions stay reopenable: members live in the
persistent field, and the quotient carries concrete-edge back-references.

Quotient edges carry counting-block (Petri-style) semantics: a quotient edge with tail
multiset {B: m} is enabled when m distinct members of B are counted reached. Sound direction
(used for exact negative refutation): the concrete gated closure maps into the counting
closure (count(B) >= |reached members of B| by induction, since concrete tails are distinct
atoms within an edge, block members share one warrant signature hence one liveness, and counts
are capped at block size), so count([t]) == 0 implies t is NOT reachable. Quotient admission
is an over-approximation: positives are confirmed on the induced subfield of one quotient
derivation path (a reopen), with a charged full-closure fallback.

Python 3.8-compatible syntax.
"""
from __future__ import annotations

import json
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

from ocm.kso.navigation import gated_closure
from ocm.kso.space import Hyperedge, KnowledgeSpace

CUSTODY = "custody"


def warrant_sig(w) -> str:
    """Canonical string for a WarrantProfile: the quotient's warrant coordinate.

    Equal signatures imply equal liveness under every revocation set (the signature records
    the full lower/upper antichain content), which is what block-level warrant gating needs.
    """
    def prof(p):
        return sorted(tuple(sorted(repr(x) for x in w2)) for w2 in p)
    return json.dumps([prof(w.lower), prof(w.upper)], sort_keys=True)


class QEdge(object):
    """One quotient edge: a class of concrete edges with identical quotient signature."""

    __slots__ = ("qid", "relation", "warrant_sig", "warrant", "tails", "heads", "concrete")

    def __init__(self, qid, relation, warrant_sig, warrant, tails, heads, concrete):
        self.qid = qid                  # int
        self.relation = relation        # str
        self.warrant_sig = warrant_sig  # str
        self.warrant = warrant          # WarrantProfile shared by every instance
        self.tails = tails              # tuple of (block_id, multiplicity)
        self.heads = heads              # tuple of (block_id, multiplicity)
        self.concrete = concrete        # tuple of concrete edge ids (back-reference)

    def key(self):
        return (self.relation, self.warrant_sig, self.tails, self.heads)

    def as_dict(self):
        return {"qid": self.qid, "relation": self.relation, "warrant": self.warrant_sig,
                "tails": list(self.tails), "heads": list(self.heads),
                "instances": len(self.concrete)}


class Quotient(object):
    """The persistent decision-sufficient quotient of one field snapshot."""

    def __init__(self, ks: KnowledgeSpace):
        self.ks = ks
        self.partition: Dict[str, int] = {}
        self.blocks: Dict[int, Tuple[str, ...]] = {}
        self.colors: Dict[int, tuple] = {}
        self.block_warrants: Dict[int, object] = {}
        self.qedges: List[QEdge] = []
        self.build_work: Dict[str, int] = {}
        self.maintenance_work: Dict[str, int] = {}
        self.reopen_work: Dict[str, int] = {}
        self._next_block = 0
        self._next_qedge = 0
        self._build(ks)

    # -- construction ------------------------------------------------------
    def _initial_color(self, a) -> tuple:
        return (a.atom_type, warrant_sig(a.warrant), bool(a.quarantined))

    def _signature(self, x: str, part: Dict[str, int], color_x: tuple,
                   ks: KnowledgeSpace, work: Dict[str, int]) -> tuple:
        """Refinement signature: own current block + own color + outgoing edge signatures.

        Including the own current block makes refinement monotonely finer (classical
        bisimulation-style iteration), so the loop terminates and never merges split atoms.
        """
        out = []
        for e in ks.outgoing_edges(x):
            co = tuple(sorted(part[t] for t in e.tails if t != x))
            hd = tuple(sorted(part[h] for h in e.heads))
            out.append((e.relation_type, warrant_sig(e.warrant), co, hd))
            work["incidence_evaluations"] += 1
        work["atom_signature_evaluations"] += 1
        return (color_x, part[x], tuple(sorted(out)))

    def _build(self, ks: KnowledgeSpace) -> None:
        work = {"refinement_passes": 0, "atom_signature_evaluations": 0,
                "incidence_evaluations": 0, "blocks_final": 0, "qedge_classes": 0}
        initial: Dict[str, tuple] = {a.atom_id: self._initial_color(a) for a in ks.atoms}
        # initial partition by color
        groups: Dict[tuple, List[str]] = {}
        for x, c in initial.items():
            groups.setdefault(c, []).append(x)
        part: Dict[str, int] = {}
        for c in sorted(groups, key=repr):
            bid = self._new_block()
            for x in groups[c]:
                part[x] = bid
        # refine to fixpoint (signatures include own block => monotone refinement)
        while True:
            work["refinement_passes"] += 1
            by_sig: Dict[tuple, List[str]] = {}
            for x in ks.ids:
                by_sig.setdefault(self._signature(x, part, initial[x], ks, work), []).append(x)
            if len(by_sig) == len(set(part.values())):
                break
            part = {}
            for c in sorted(by_sig, key=repr):
                bid = self._new_block()
                for x in by_sig[c]:
                    part[x] = bid
        self.partition = part
        blocks: Dict[int, List[str]] = {}
        for x, bid in part.items():
            blocks.setdefault(bid, []).append(x)
        self.blocks = {b: tuple(sorted(m)) for b, m in blocks.items()}
        amap = ks.atom_view
        for b, members in self.blocks.items():
            a0 = amap[members[0]]
            self.colors[b] = self._initial_color(a0)
            self.block_warrants[b] = a0.warrant
        # quotient edges: group concrete edges by quotient signature
        self.qedges = list(self._qedges_from(ks, part))
        work["blocks_final"] = len(self.blocks)
        work["qedge_classes"] = len(self.qedges)
        self.build_work = work

    def _qedges_from(self, ks: KnowledgeSpace, part: Dict[str, int]) -> List[QEdge]:
        by_key: Dict[tuple, List[Hyperedge]] = {}
        for e in ks.hyperedges:
            tails: Dict[int, int] = {}
            for t in e.tails:
                tails[part[t]] = tails.get(part[t], 0) + 1
            heads: Dict[int, int] = {}
            for h in e.heads:
                heads[part[h]] = heads.get(part[h], 0) + 1
            key = (e.relation_type, warrant_sig(e.warrant),
                   tuple(sorted(tails.items())), tuple(sorted(heads.items())))
            by_key.setdefault(key, []).append(e)
        out = []
        for key in sorted(by_key, key=repr):
            edges = by_key[key]
            out.append(QEdge(self._next_qedge, key[0], key[1], edges[0].warrant, key[2], key[3],
                             tuple(sorted(e.edge_id for e in edges))))
            self._next_qedge += 1
        return out

    def _new_block(self) -> int:
        b = self._next_block
        self._next_block += 1
        return b

    def _remap_qedges(self, ks: KnowledgeSpace, part: Dict[str, int],
                      changed_blocks: set) -> List[QEdge]:
        """Recompute quotient edges touching changed blocks from their concrete back-references.

        Required for exactness: a qedge multiset must always reflect the partition that
        produced it, else firing conditions stop corresponding to any concrete edge.
        """
        out: List[QEdge] = []
        emap = ks.edge_view
        for q in self.qedges:
            blocks_in = {b for b, _ in q.tails} | {b for b, _ in q.heads}
            if not (blocks_in & changed_blocks):
                out.append(q)
                continue
            tails: Dict[int, int] = {}
            heads: Dict[int, int] = {}
            concrete = []
            for eid in q.concrete:
                e = emap[eid]
                concrete.append(eid)
                for t in e.tails:
                    tails[part[t]] = tails.get(part[t], 0) + 1
                for h in e.heads:
                    heads[part[h]] = heads.get(part[h], 0) + 1
            out.append(QEdge(q.qid, q.relation, q.warrant_sig, q.warrant,
                             tuple(sorted(tails.items())), tuple(sorted(heads.items())),
                             tuple(concrete)))
        return out

    # -- per-query singleton protection (ephemeral overlay, charged) --------
    def split_singletons(self, atoms: Sequence[str]) -> "QuotientView":
        """Overlay view with the given atoms as singleton blocks.

        Splitting is a refinement: soundness holds for ANY partition, so no re-refinement
        pass is required -- only quotient edges touching the affected blocks (old and new)
        are remapped from their concrete back-references.
        """
        w = {"split_blocks": 0, "qedges_remapped": 0, "member_lookups": 0}
        part = dict(self.partition)
        blocks: Dict[int, List[str]] = {b: list(m) for b, m in self.blocks.items()}
        changed: set = set()
        for x in atoms:
            old = part[x]
            if len(blocks[old]) == 1:
                continue
            bid = self._next_block
            self._next_block += 1
            blocks[old].remove(x)
            blocks[bid] = [x]
            part[x] = bid
            self.colors[bid] = self.colors[old]
            self.block_warrants[bid] = self.block_warrants[old]
            changed |= {old, bid}
            w["split_blocks"] += 1
            w["member_lookups"] += len(blocks[old]) + 1
        if changed:
            qedges = self._remap_qedges(self.ks, part, changed)
            w["qedges_remapped"] = sum(1 for a, b in zip(self.qedges, qedges) if a is not b)
        else:
            qedges = list(self.qedges)
        blocks_t = {b: tuple(sorted(m)) for b, m in blocks.items() if m}
        return QuotientView(part, blocks_t, qedges, self, w)

    # -- incremental maintenance (E1 lever) ---------------------------------
    def incremental_maintain(self, new_ks: KnowledgeSpace, new_edges: Sequence[Hyperedge]) -> None:
        """E1: re-refine only blocks incident to changed edges; charge the incremental work.

        Sound for any resulting partition (and every qedge is remapped to match it); aims to
        avoid the full rebuild's whole-field refinement passes.
        """
        w = self.maintenance_work
        w["incremental_passes"] = w.get("incremental_passes", 0) + 1
        w["atom_signature_evaluations"] = w.get("atom_signature_evaluations", 0)
        w["incidence_evaluations"] = w.get("incidence_evaluations", 0)
        w["atoms_resigned"] = w.get("atoms_resigned", 0)
        w["qedges_regrouped"] = w.get("qedges_regrouped", 0)
        self.ks = new_ks
        amap = new_ks.atom_view
        affected: Dict[str, None] = {}
        for e in new_edges:
            for x in (*e.tails, *e.heads):
                affected[x] = None
        part = dict(self.partition)
        blocks: Dict[int, List[str]] = {b: list(m) for b, m in self.blocks.items()}
        changed: set = set()
        for x in affected:
            color_x = self._initial_color(amap[x])
            sig = self._signature(x, part, color_x, new_ks, w)
            old = part[x]
            bid = self._block_for_signature(sig, x, color_x, part, blocks, new_ks)
            if bid != old:
                blocks[old].remove(x)
                blocks[bid].append(x)
                part[x] = bid
                changed |= {old, bid}
                w["atoms_resigned"] += 1
        # remap every qedge touching a changed block; then absorb the new edges
        if changed:
            self.qedges = self._remap_qedges(new_ks, part, changed)
        key_index = {q.key(): q for q in self.qedges}
        for e in new_edges:
            tails: Dict[int, int] = {}
            for t in e.tails:
                tails[part[t]] = tails.get(part[t], 0) + 1
            heads: Dict[int, int] = {}
            for h in e.heads:
                heads[part[h]] = heads.get(part[h], 0) + 1
            key = (e.relation_type, warrant_sig(e.warrant),
                   tuple(sorted(tails.items())), tuple(sorted(heads.items())))
            q = key_index.get(key)
            if q is None:
                q = QEdge(self._next_qedge, key[0], key[1], e.warrant, key[2], key[3], (e.edge_id,))
                self._next_qedge += 1
                self.qedges.append(q)
                key_index[key] = q
            else:
                q.concrete = tuple(sorted(set(q.concrete) | {e.edge_id}))
            w["qedges_regrouped"] += 1
        self.blocks = {b: tuple(sorted(m)) for b, m in blocks.items() if m}
        self.partition = part

    def _block_for_signature(self, sig, x, color_x, part, blocks, ks) -> int:
        """Find or create the block whose members share x's signature (local re-refinement).

        Matching compares (color, outgoing signatures) -- the own-block component exists only
        to keep the build loop monotone and must not block an atom from matching its own
        current block. The representative's neighborhood is evaluated under the same current
        partition, so the comparison is well-defined.
        """
        amap = ks.atom_view
        work = {"atom_signature_evaluations": 0, "incidence_evaluations": 0}
        match = (sig[0], sig[2])
        found = None
        for b, members in blocks.items():
            if not members or members[0] == x:
                continue
            m0 = members[0]
            sig0 = self._signature(m0, part, self._initial_color(amap[m0]), ks, work)
            if (sig0[0], sig0[2]) == match:
                found = b
                break
        self.maintenance_work["atom_signature_evaluations"] = \
            self.maintenance_work.get("atom_signature_evaluations", 0) + work["atom_signature_evaluations"]
        self.maintenance_work["incidence_evaluations"] = \
            self.maintenance_work.get("incidence_evaluations", 0) + work["incidence_evaluations"]
        if found is not None:
            return found
        bid = self._new_block()
        self.colors[bid] = color_x
        self.block_warrants[bid] = amap[x].warrant
        blocks[bid] = []
        return bid

    def rebuild(self, ks: KnowledgeSpace) -> None:
        """Full rebuild (the pre-lever maintenance policy)."""
        saved_counters = (dict(self.maintenance_work), dict(self.reopen_work))
        self.__init__(ks)
        self.maintenance_work, self.reopen_work = saved_counters

    # -- hostile: D2 member selection ----------------------------------------
    def _authority_summary(self, block_id: int, charge: bool) -> Dict[str, object]:
        """Block-level authority summary: counts only, never the identity pairing."""
        amap = self.ks.atom_view
        custody_members = 0
        hetero = False
        seen = None
        for m in self.blocks[block_id]:
            sig = json.dumps(amap[m].authority.as_dict(), sort_keys=True)
            if seen is None:
                seen = sig
            elif sig != seen:
                hetero = True
            if amap[m].authority.rank(CUSTODY) >= 2:
                custody_members += 1
        if charge:
            self.reopen_work["summary_evaluations"] = \
                self.reopen_work.get("summary_evaluations", 0) + len(self.blocks[block_id])
        return {"custody_members": custody_members, "authority_heterogeneous": hetero}

    def authority_summary(self, block_id: int) -> Dict[str, object]:
        return self._authority_summary(block_id, charge=True)

    def reopen_member_selection(self, block_id: int) -> Tuple[Optional[str], str]:
        """Reopen the discarded identity<->authority coordinate and select the member.

        Returns (member_id, status). REOPENED charges |block| member fetches.
        """
        amap = self.ks.atom_view
        members = self.blocks[block_id]
        self.reopen_work["reopened_members_fetched"] = \
            self.reopen_work.get("reopened_members_fetched", 0) + len(members)
        cands = [m for m in members if amap[m].authority.rank(CUSTODY) >= 2]
        if len(cands) == 1:
            return cands[0], "REOPENED"
        return None, "REOPENED_NO_UNIQUE_MEMBER"

    def twin_block_of(self, member: str) -> int:
        """The block containing a member (used to aim the hostile D2 task)."""
        return self.partition[member]

    def serialize(self, state_only: bool = True) -> Dict[str, object]:
        """The persistent quotient state: blocks, colors, quotient edges, authority summaries.

        Byte-level identity of two serialized quotients is the FQ-5 isomorphism witness.
        Serialization itself performs no charged arm work.
        """
        return {
            "blocks": {str(b): list(m) for b, m in sorted(self.blocks.items())},
            "colors": {str(b): list(self.colors[b]) for b in sorted(self.blocks)},
            "qedges": [q.as_dict() for q in self.qedges],
            "authority_summaries": {str(b): self._authority_summary(b, charge=False)
                                    for b in sorted(self.blocks)},
        }


class QuotientView(object):
    """Ephemeral per-query refinement of a Quotient (singleton splits applied)."""

    def __init__(self, partition, blocks, qedges, parent, split_work):
        self.partition = partition
        self.blocks = blocks
        self.qedges = qedges
        self.parent = parent
        self.split_work = split_work

    def counting_closure(self, seed: str, revoked: FrozenSet, target: str,
                         early_stop: bool = False) -> dict:
        """Counting-block closure. Returns counts, firing trace and per-call metrics.

        Mirrors production gated_closure gating: seeds must be live; edges need a live edge
        warrant and live incident atoms (block liveness is well-defined because block members
        share one warrant signature). Soundness: count(B) >= |concrete reached members of B|
        by induction, hence count([t]) == 0 implies t not reachable (exact negative).
        """
        m = {"quotient_expansions": 0, "quotient_firings": 0,
             "block_warrant_checks": 0, "qedge_warrant_checks": 0, "early_stopped": False}
        live_block: Dict[int, bool] = {}
        for b in self.blocks:
            m["block_warrant_checks"] += 1
            live_block[b] = self.parent.block_warrants[b].is_live(revoked)
        counts: Dict[int, int] = {b: 0 for b in self.blocks}
        sb = self.partition[seed]
        tb = self.partition[target]
        if not live_block.get(sb, False):
            return {"counts": counts, "m": m, "refuted": True, "fired": [],
                    "parent_edge": {}}
        counts[sb] = 1
        parent_edge: Dict[int, tuple] = {}
        fired_log: List[int] = []
        changed = True
        done = False
        while changed and not done:
            changed = False
            for q in self.qedges:
                m["quotient_expansions"] += 1
                m["qedge_warrant_checks"] += 1
                if not q.warrant.is_live(revoked):
                    continue
                if any((not live_block.get(b, False)) for b, _ in q.tails) or \
                   any((not live_block.get(b, False)) for b, _ in q.heads):
                    continue
                if any(counts.get(b, 0) < k for b, k in q.tails):
                    continue
                fired_log.append(q.qid)
                m["quotient_firings"] += 1
                for b, k in q.heads:
                    size = len(self.blocks[b])
                    newc = min(size, counts[b] + k)
                    if newc > counts[b]:
                        counts[b] = newc
                        changed = True
                        if b not in parent_edge:
                            parent_edge[b] = (q.qid,)
                if early_stop and counts.get(tb, 0) >= 1:
                    m["early_stopped"] = True
                    done = True
                    break
        refuted = counts.get(tb, 0) == 0
        return {"counts": counts, "m": m, "refuted": refuted, "fired": fired_log,
                "parent_edge": parent_edge}

    def path_blocks(self, res: dict, seed: str, target: str) -> List[int]:
        """Blocks of one quotient derivation path seed->target (from the firing trace)."""
        sb, tb = self.partition[seed], self.partition[target]
        if res["counts"].get(tb, 0) == 0:
            return []
        path = [tb]
        cur = tb
        guard = 0
        while cur != sb and guard < 10 ** 6:
            guard += 1
            nxt = None
            for q in self.qedges:
                if q.qid in res["fired"] and any(b == cur for b, _ in q.heads):
                    cand = [b for b, _ in q.tails if res["counts"].get(b, 0) > 0]
                    if cand:
                        nxt = cand[0]
                        break
            if nxt is None or nxt in path:
                break
            path.append(nxt)
            cur = nxt
        path.append(sb)
        return list(dict.fromkeys(path))


def _witness_in_induced(sub: KnowledgeSpace, s: str, t: str, reached: set,
                        revoked) -> set:
    """One concrete derivation path s->t inside the induced subfield (measurement only).

    Backward walk over admitted atoms: every atom in reached\\{s} was admitted by some
    warrant-live edge whose tails were all reached, so the first such edge is a valid
    derivation parent. Harness instrumentation: never charged to an arm.
    """
    witness = {t, s}
    stack = [t]
    guard = 0
    while stack and guard < 10 ** 6:
        guard += 1
        v = stack.pop()
        if v == s:
            continue
        for e in sub.hyperedges:
            if v not in e.heads:
                continue
            if not e.warrant.is_live(revoked):
                continue
            if not all(x in reached for x in e.tails):
                continue
            for u in e.tails:
                if u not in witness:
                    witness.add(u)
                    stack.append(u)
            break
    return witness


def confirm_on_induced(ks: KnowledgeSpace, s: str, t: str, revoked,
                       blocks_members: Sequence[Tuple[str, ...]]) -> Tuple[bool, dict, set]:
    """Positive confirmation: production gated closure restricted to the path-block members.

    Returns (confirmed, charged_metrics, witness_path). The witness path is harness
    instrumentation (uncharged) used for the false_candidates measurement.
    """
    members = set()
    for m in blocks_members:
        members |= set(m)
    members |= {s, t}
    sub_atoms = tuple(a for a in ks.atoms if a.atom_id in members)
    sub_edges = tuple(e for e in ks.hyperedges if e.incident <= members)
    sub = KnowledgeSpace(sub_atoms, sub_edges)
    reached = gated_closure(sub, [s], revoked)
    ok = t in reached
    witness = _witness_in_induced(sub, s, t, reached, revoked) if ok else set()
    metrics = {"verifier_calls": 1, "induced_atoms": len(sub.atoms),
               "induced_edges": len(sub.hyperedges),
               "objects_touched": len(members)}
    return ok, metrics, witness
