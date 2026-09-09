"""FNA-6 ACT-R-style module-buffer arms: P3 (strict capacity, plain declarative memory)
and P3R (pre-registered revival lever L2: retrieval-time revalidation).

Faithful core of ACT-R for this function (ACT-R manual, module buffers with strict
capacity; declarative memory as persistent chunks; retrieval requests return one chunk
selected by activation; newly derived knowledge is added to DM by declarative learning):

* three buffers — goal, retrieval, imaginal — each holding at most ONE chunk. Every
  buffer assignment is a charged swap; that capacity signature, not cosplay, is what the
  arm measures;
* DM chunks encode field edges (learned by perception at build) and traversal knowledge
  (node chunks per obligation, learned while serving). Chunks carry the goal context as a
  slot — the standard ACT-R way to keep concurrent goals apart;
* a serve is a traversal driven purely by retrieval requests: pick an unexpanded node
  chunk, retrieve its outgoing edge chunks one per request, learn node chunks for unseen
  heads, mark expanded.

Plain P3 has NO update pathway: ACT-R declarative memory has no revocation semantics and
no deletion, so admissions/revocations/drift change nothing in DM (charged zero ops) and
stale chunks are retrieved afterwards — the honest parent failure mode, counted.

P3R (lever L2) applies stream events by encoding new edge chunks and maintaining a
world-version stamp: on a version change all of an obligation's node-chunk expansions are
invalidated, and the serve runs an exact revalidation pass — a pending-counter closure
over DM-known edges that are live under the CURRENT field (dead edges/atoms excluded) —
which gates both expansion (stale chunks are tombstoned, never deleted) and the final
answer. The revalidation pass, its DM scans and its warrant reads are all charged.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from ocm.kso.space import KnowledgeSpace

from contract import ArmResult


class ActrArm:
    def __init__(self, code: str, revalidate: bool = False) -> None:
        self.code = code
        self.revalidate = revalidate
        self.res = ArmResult(code)
        self.c = self.res.counters
        self.ks: KnowledgeSpace = None
        self.revoked: Set[int] = set()
        self.dm: Dict[str, dict] = {}          # chunk name -> chunk
        self.world_version = 0
        self.learned_version: Dict[int, int] = {0: 0, 1: 0}  # ob -> version last expanded at
        self.goal = None
        self.retrieval = None
        self.imaginal = None
        self._seq = 0
        self._access: Dict[str, int] = {}
        self.build_live_atoms: Set[str] = set()  # warrants as perceived at build
        self._valid_cache_key = None
        self._valid_cache: Set[str] = set()

    # -- buffers ------------------------------------------------------------
    def _set(self, buf: str, chunk) -> None:
        setattr(self, buf, chunk)
        self.c.op("serve", kind="buffer_swap")

    # -- declarative memory -------------------------------------------------
    def _learn(self, phase: str, name: str, chunk: dict) -> None:
        self._seq += 1
        chunk = dict(chunk)
        self.dm[name] = chunk
        self._access[name] = self._seq
        self.c.op(phase, kind="dm_chunk_add")   # declarative learning

    def _request(self, phase: str, pattern: dict, exclude: Set[str] = None) -> Optional[str]:
        """One retrieval request. Deterministic selection: most recently accessed chunk
        matching the pattern (a fixed, declared stand-in for base-level activation), not in
        ``exclude``. Multivalued slots (tuples) match by membership. Returns the chunk name
        or None (retrieval failure)."""
        self.c.op(phase, kind="retrieval_request")
        exclude = exclude or set()

        def matches(chunk: dict) -> bool:
            for k, v in pattern.items():
                cv = chunk.get(k)
                if isinstance(cv, tuple):
                    if v not in cv:
                        return False
                elif cv != v:
                    return False
            return True

        best, best_seq = None, -1
        for name, chunk in self.dm.items():
            if name in exclude or chunk.get("dead"):
                continue
            if matches(chunk):
                seq = self._access.get(name, 0)
                if seq > best_seq or (seq == best_seq and (best is None or name < best)):
                    best, best_seq = name, seq
        if best is None:
            return None
        self._seq += 1
        self._access[best] = self._seq
        self._set("retrieval", self.dm[best])
        if self.revalidate:
            self.c.op(phase, kind="retrieval_validation")
        return best

    def _edge_valid(self, eid: str) -> bool:
        self.c.op("serve", kind="edge_warrant_check")
        e = self.ks.edge_view.get(eid)
        return e is not None and e.warrant.is_live(frozenset(self.revoked))

    def _atom_valid(self, atom: str) -> bool:
        self.c.op("serve", kind="atom_warrant_check")
        a = self.ks.atom_view.get(atom)
        return a is not None and a.is_live(frozenset(self.revoked))

    def _head_ok(self, atom: str) -> bool:
        """Can a newly derived head be accepted as a live node chunk? Plain P3 uses the
        build-frozen perception (no update pathway: DM never revisits warrants); P3R
        validates against the current field (retrieval-time revalidation, lever L2)."""
        if self.revalidate:
            return self._atom_valid(atom)
        return atom in self.build_live_atoms

    # -- lifecycle ---------------------------------------------------------
    def open(self, field: KnowledgeSpace, seeds: List[str]) -> None:
        self.ks = field
        self.revoked = set()
        rv0 = frozenset()
        amap = field.atom_view
        for x in field.ids:
            self.c.op("build", kind="atom_warrant_check")
            if amap[x].is_live(rv0):
                self.build_live_atoms.add(x)
        for e in field.hyperedges:
            self.c.op("build", kind="edge_warrant_check")
            if not e.warrant.is_live(rv0):
                continue   # perception encodes usable structure, not dead warrants
            self._learn("build", "edge-%s" % e.edge_id,
                        {"kind": "edge", "tail": tuple(e.tails),
                         "heads": tuple(e.heads), "eid": e.edge_id})
        self.c.op("build", n=len(field.atoms), kind="dm_slot_count")

    def apply_admission(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self.revoked = set(revoked_after)
        if self.revalidate:
            self.world_version += 1
            self.c.op("merge", kind="world_version_bump")
            for e in event["_edges"]:
                self._learn("merge", "edge-%s" % e.edge_id,
                            {"kind": "edge", "tail": tuple(e.tails),
                             "heads": tuple(e.heads), "eid": e.edge_id})
        # plain P3: no encoding pathway from environment events — zero ops, stays stale
        touched = set()
        for e in event["_edges"]:
            touched |= set(e.tails) | set(e.heads)
        self.c.touch("admission:%d" % event["after"], touched)

    def apply_revocation(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self.revoked = set(revoked_after)
        if self.revalidate:
            self.world_version += 1
            self.c.op("sweep", kind="world_version_bump")
        else:
            self.c.op("sweep", kind="no_update_pathway")
        self.c.touch("revocation:%d" % event["after"], set())

    def apply_drift(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self.revoked = set(revoked_after)
        if self.revalidate:
            self.world_version += 1
            self.c.op("drift", kind="world_version_bump")
        else:
            self.c.op("drift", kind="no_update_pathway")
        e = event.get("_edge_before")
        touched = set([event["atom_id"]]) | (set(e.tails) | set(e.heads) if e is not None else set())
        self.c.touch("drift:%d" % event["after"], touched)

    # -- serving -----------------------------------------------------------
    def _valid_set(self, ob: int, seed: str) -> Set[str]:
        """P3R validity (lever L2): the exact set of atoms lying on some live path from
        the seed, over DM-known edges, under the CURRENT field and revoked set. Iterative
        pending-counter BFS — no recursion, so no in-progress memo ambiguity on cyclic
        graphs; conjunctive tails must all be valid, heads must be live, exactly the
        production closure restricted to what DM can retrieve. Cached per
        (obligation, seed, world_version) — the version stamp is what makes the cache
        sound, since DM edge chunks only change on version bumps. DM scans, edge visits
        and warrant reads are charged; cache hits are free (nothing is re-read)."""
        key = (ob, seed, self.world_version)
        if key == self._valid_cache_key:
            return self._valid_cache
        edges = {}
        for chunk in self.dm.values():
            if chunk.get("kind") != "edge":
                continue
            self.c.op("serve", kind="validation_edge_check")
            if self._edge_valid(chunk["eid"]):
                edges[chunk["eid"]] = chunk
        pending = {eid: len(ch["tail"]) for eid, ch in edges.items()}
        tail_index: Dict[str, List[str]] = {}
        for eid, ch in edges.items():
            for t in ch["tail"]:
                tail_index.setdefault(t, []).append(eid)
        ok: Set[str] = set()
        work: List[str] = []
        if self._atom_valid(seed):  # a dead seed has an empty closure
            ok.add(seed)
            work.append(seed)
        while work:
            v = work.pop()
            for eid in tail_index.get(v, ()):
                self.c.op("serve", kind="validation_edge_check")
                pending[eid] -= 1
                if pending[eid] == 0:
                    for h in edges[eid]["heads"]:
                        if h not in ok and self._atom_valid(h):
                            ok.add(h)
                            work.append(h)
        self._valid_cache_key = key
        self._valid_cache = ok
        return ok

    def serve(self, ob: int, seed: str, target: str, ks_now: KnowledgeSpace, revoked_now: Set[int]) -> Tuple[bool, Set[str]]:
        self.ks = ks_now
        self.revoked = set(revoked_now)
        self._set("goal", {"kind": "goal", "ob": ob, "seed": seed, "target": target})
        consulted: Set[str] = set()
        if self.revalidate:
            if self.learned_version[ob] != self.world_version:
                # invalidate expansions and tombstones: everything must be re-derived and
                # re-validated under the new version (a later admission can revive a path)
                for name, chunk in self.dm.items():
                    if chunk.get("kind") == "node" and chunk.get("ob") == ob:
                        if chunk.get("expanded") or chunk.get("dead"):
                            chunk["expanded"] = False
                            chunk["dead"] = False
                            self.c.op("serve", kind="dm_chunk_modify")
                self.learned_version[ob] = self.world_version
            valid = self._valid_set(ob, seed)
        if self.dm.get("node-%d-%s" % (ob, seed)) is None:
            self._learn("serve", "node-%d-%s" % (ob, seed),
                        {"kind": "node", "ob": ob, "atom": seed, "expanded": False})
            consulted.add(seed)
        # traversal: expand unexpanded node chunks of this obligation
        while True:
            name = self._request("serve", {"kind": "node", "ob": ob, "expanded": False})
            if name is None:
                break
            node = self.dm[name]
            atom = node["atom"]
            consulted.add(atom)
            self._set("imaginal", node)
            if self.revalidate and atom not in valid:
                node["dead"] = True           # tombstone: DM chunks are never deleted
                self.c.op("serve", kind="dm_chunk_modify")
                continue
            used: Set[str] = set()
            while True:
                ename = self._request("serve", {"kind": "edge", "tail": atom}, exclude=used)
                if ename is None:
                    break
                used.add(ename)
                echunk = self.dm[ename]
                if self.revalidate and not self._edge_valid(echunk["eid"]):
                    continue
                # conjunctive firing: an edge fires only when every tail is a live node of ob
                def _reached(t: str) -> bool:
                    ch = self.dm.get("node-%d-%s" % (ob, t))
                    return ch is not None and not ch.get("dead")
                if all(_reached(t) for t in self.ks.edge_view[echunk["eid"]].tails):
                    for h in echunk["heads"]:
                        consulted.add(h)
                        if self.dm.get("node-%d-%s" % (ob, h)) is None and self._head_ok(h):
                            self._learn("serve", "node-%d-%s" % (ob, h),
                                        {"kind": "node", "ob": ob, "atom": h, "expanded": False})
            node["expanded"] = True
            self.c.op("serve", kind="dm_chunk_modify")
        got = self._request("serve", {"kind": "node", "ob": ob, "atom": target}) is not None
        if got and self.revalidate:
            got = target in self._valid_set(ob, seed)   # cache hit: no re-read, no charge
        self.c.resident_sync(ob, self.resident(ob))
        return bool(got), consulted

    def resident(self, ob: int) -> Set[str]:
        return {c["atom"] for c in self.dm.values()
                if c.get("kind") == "node" and c.get("ob") == ob and not c.get("dead")}

    def persistent_state(self) -> dict:
        return {"chunks": {k: {kk: (list(vv) if isinstance(vv, tuple) else vv)
                               for kk, vv in sorted(v.items())}
                           for k, v in sorted(self.dm.items())}}

    def close(self) -> None:
        return None
