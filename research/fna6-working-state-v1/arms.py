"""FNA-6 arms P0 (incumbent active-KSO state) and P4 (no working state, full rescan).

P0 mirrors the production working state: the persistent structural adjacency index over an
immutable ``KnowledgeSpace`` (rebuilt and charged on every structural change — snapshot
bound, exactly as ``kso/extraction_index.py`` documents), per-query liveness derivation
(the revoked set is applied at query time; every atom/edge warrant check is charged), and a
per-obligation active-subspace view (the reached set of the obligation's last serve).
Equality with production ``gated_closure`` is asserted by the test suite and by a pre-run
assertion in the runner; disagreement aborts the scored run.

P4 is the no-working-state control: every serve rescans the raw edge tuple; there is no
persistent state, no build, no merge, no sweep.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from ocm.kso.space import KnowledgeSpace

from contract import ArmResult, Counters


class IncumbentArm:
    """P0_INCUMBENT_ACTIVE_KSO — production active-KSO working state, instrumented."""

    code = "P0_INCUMBENT_ACTIVE_KSO"

    def __init__(self) -> None:
        self.res = ArmResult(self.code)
        self.c = self.res.counters
        self.ks: KnowledgeSpace = None
        self.revoked: Set[int] = set()
        self.adj: Dict[str, List[str]] = {}        # atom -> outgoing edge objects
        self.edges_by_id: Dict[str, object] = {}
        self.last_reached: Dict[int, Set[str]] = {0: set(), 1: set()}

    # -- lifecycle ---------------------------------------------------------
    def _prepare_adjacency(self, phase: str) -> None:
        self.adj = {}
        self.edges_by_id = {}
        for e in self.ks.hyperedges:
            self.c.op(phase, kind="index_edge_entry")
            self.edges_by_id[e.edge_id] = e
            for t in e.tails:
                self.adj.setdefault(t, []).append(e)
        self.c.op(phase, n=len(self.ks.atoms), kind="index_atom_entry")

    def open(self, field: KnowledgeSpace, seeds: List[str]) -> None:
        self.ks = field
        self._prepare_adjacency("build")

    def apply_admission(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self.revoked = set(revoked_after)
        self._prepare_adjacency("merge")
        touched = set()
        for e in event["_edges"]:
            touched |= set(e.tails) | set(e.heads)
        self.c.touch("admission:%d" % event["after"], touched)

    def apply_revocation(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.revoked = set(revoked_after)
        self.c.op("sweep", kind="revoked_set_update")  # liveness re-derived lazily per serve
        self.c.touch("revocation:%d" % event["after"], set())

    def apply_drift(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self.revoked = set(revoked_after)
        self._prepare_adjacency("drift")
        e = event.get("_edge_before")
        touched = set([event["atom_id"]]) | (set(e.tails) | set(e.heads) if e is not None else set())
        self.c.touch("drift:%d" % event["after"], touched)

    # -- serving -----------------------------------------------------------
    def _closure(self, seed: str) -> Set[str]:
        """Instrumented mirror of production gated_closure on the incumbent's index."""
        amap = self.ks.atom_view
        live: Dict[str, bool] = {}
        for x in self.ks.ids:
            self.c.op("serve", kind="atom_warrant_check")
            live[x] = amap[x].is_live(frozenset(self.revoked))
        pending = {eid: len(e.tails) for eid, e in self.edges_by_id.items()}
        self.c.op("serve", n=len(pending), kind="edge_pending_init")
        reached = {seed} if live.get(seed) else set()
        work = list(reached)
        while work:
            v = work.pop()
            self.c.op("serve", kind="expansion")
            for e in self.adj.get(v, ()):
                self.c.op("serve", kind="edge_examined")
                pending[e.edge_id] -= 1
                if pending[e.edge_id] == 0:
                    self.c.op("serve", kind="edge_warrant_check")
                    if e.warrant.is_live(frozenset(self.revoked)):
                        for h in e.heads:
                            if h not in reached and live[h]:
                                reached.add(h)
                                work.append(h)
        return reached

    def serve(self, ob: int, seed: str, target: str, ks_now: KnowledgeSpace, revoked_now: Set[int]) -> Tuple[bool, Set[str]]:
        self.revoked = set(revoked_now)
        if ks_now is not self.ks:
            self.ks = ks_now  # defensive: stream state and arm state must agree
        reached = self._closure(seed)
        self.last_reached[ob] = reached
        self.c.resident_sync(ob, reached)
        return target in reached, set(reached)

    def resident(self, ob: int) -> Set[str]:
        return set(self.last_reached[ob])

    def persistent_state(self) -> dict:
        return {"adjacency": {k: [e.edge_id for e in v] for k, v in sorted(self.adj.items())},
                "revoked": sorted(self.revoked)}

    def close(self) -> None:
        return None


class RescanArm:
    """P4_FULL_RESCAN — no working state; every serve rescans the raw edge tuple."""

    code = "P4_FULL_RESCAN"

    def __init__(self) -> None:
        self.res = ArmResult(self.code)
        self.c = self.res.counters
        self.last_reached: Dict[int, Set[str]] = {0: set(), 1: set()}

    def open(self, field: KnowledgeSpace, seeds: List[str]) -> None:
        return None  # stateless: zero build

    def apply_admission(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        touched = set()
        for e in event["_edges"]:
            touched |= set(e.tails) | set(e.heads)
        self.c.touch("admission:%d" % event["after"], touched)

    def apply_revocation(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.c.touch("revocation:%d" % event["after"], set())

    def apply_drift(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        e = event.get("_edge_before")
        touched = set([event["atom_id"]]) | (set(e.tails) | set(e.heads) if e is not None else set())
        self.c.touch("drift:%d" % event["after"], touched)

    def _closure(self, ks: KnowledgeSpace, seed: str, revoked: Set[int]) -> Set[str]:
        amap = ks.atom_view
        rv = frozenset(revoked)
        live = {}
        for x in ks.ids:
            self.c.op("serve", kind="atom_warrant_check")
            live[x] = amap[x].is_live(rv)
        edges = list(ks.hyperedges)
        pending = {e.edge_id: len(e.tails) for e in edges}
        self.c.op("serve", n=len(pending), kind="edge_pending_init")
        reached = {seed} if live.get(seed) else set()
        work = list(reached)
        while work:
            v = work.pop()
            self.c.op("serve", kind="expansion")
            out_edges = [e for e in edges if v in e.tails]  # raw scan: E examined per pop
            self.c.op("serve", n=len(edges), kind="edge_examined")
            for e in out_edges:
                pending[e.edge_id] -= 1
                if pending[e.edge_id] == 0:
                    self.c.op("serve", kind="edge_warrant_check")
                    if e.warrant.is_live(rv):
                        for h in e.heads:
                            if h not in reached and live[h]:
                                reached.add(h)
                                work.append(h)
        return reached

    def serve(self, ob: int, seed: str, target: str, ks_now: KnowledgeSpace, revoked_now: Set[int]) -> Tuple[bool, Set[str]]:
        reached = self._closure(ks_now, seed, set(revoked_now))
        self.last_reached[ob] = reached
        self.c.resident_sync(ob, set())   # stateless: nothing persists between serves
        return target in reached, set(reached)

    def resident(self, ob: int) -> Set[str]:
        return set()  # nothing persists between serves

    def persistent_state(self) -> dict:
        return {}

    def close(self) -> None:
        return None
