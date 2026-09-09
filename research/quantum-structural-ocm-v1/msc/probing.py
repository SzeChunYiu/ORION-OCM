"""Probe acquisition (FQ-2) for MSC V1: adjacency hidden behind charged probes.

One probe reveals one atom's full outgoing posting list (E3 batched probes). Warrant
liveness is a separate charged observation. The non-oracle probe order is
rarest-channel-first (rank reached-unprobed atoms by the global rarity of the relation
channel through which they were admitted; the global per-channel edge counts are a charged
cheap first summary). The shuffle-null policy picks uniformly at random from the same
frontier under a frozen seed -- the control required by the retraction note in the
protocol: adaptive value is only ever the Q4-minus-null margin.

The probe decision procedure mirrors production gated_closure semantics (conjunctive tails,
live warrants, live heads) but only over REVEALED structure; exhausting the frontier is an
exact NOT_SUPPORTED because the revealed subgraph then equals the full forward closure.

Python 3.8-compatible syntax.
"""
from __future__ import annotations

import random
from collections import Counter, deque
from typing import Dict, FrozenSet, List, Optional, Tuple

from ocm.kso.space import KnowledgeSpace

SUPPORTED = "SUPPORTED"
NOT_SUPPORTED = "NOT_SUPPORTED"


class ProbeField(object):
    """The environment side of the probe API: adjacency is private until probed."""

    def __init__(self, ks: KnowledgeSpace):
        self._out = {v: ks.outgoing_edges(v) for v in ks.ids}
        self._atom_view = ks.atom_view
        self.counters = {"probes": 0, "edges_revealed": 0, "warrant_observations": 0,
                         "atoms_revealed": 0, "channel_summary_calls": 0}
        self._channel_counts = None

    def probe(self, atom_id: str):
        """Reveal one atom's outgoing posting list (one probe = one atom, batched edges)."""
        self.counters["probes"] += 1
        self.counters["atoms_revealed"] += 1
        postings = self._out.get(atom_id, ())
        self.counters["edges_revealed"] += len(postings)
        return postings

    def edge_live(self, edge, revoked: FrozenSet) -> bool:
        self.counters["warrant_observations"] += 1
        return edge.warrant.is_live(revoked)

    def atom_live(self, atom_id: str, revoked: FrozenSet) -> bool:
        self.counters["warrant_observations"] += 1
        return self._atom_view[atom_id].is_live(revoked)

    def channel_summary(self) -> Dict[str, int]:
        """The cheap first summary: per-relation-type global edge counts (charged once/call)."""
        self.counters["channel_summary_calls"] += 1
        if self._channel_counts is None:
            c: Counter = Counter()
            for postings in self._out.values():
                for e in postings:
                    c[e.relation_type] += 1
            self._channel_counts = dict(c)
        return dict(self._channel_counts)


def probe_decide(pf: ProbeField, s: str, t: str, revoked: FrozenSet,
                 policy: str = "rarity", rng: Optional[random.Random] = None,
                 budget: Optional[int] = None) -> dict:
    """Decide D1(s,t) using only probes.

    policy: 'naive' (FIFO frontier), 'rarity' (rarest admission channel first),
            'shuffle' (uniform random frontier choice under rng).
    budget: stop probing after this many probes (decision forced on revealed structure;
            used only by the shuffle-null control at Q4's consumed budget).
    Early stop on SUPPORTED admission is sound by monotonicity of admissions. A negative
    requires frontier exhaustion: the revealed subgraph then equals the full closure.
    """
    c = {"probes": 0, "atoms_admitted": 0, "warrant_observations": 0,
         "early_stopped": False, "budget_exhausted": False, "expansions": 0,
         "pending_rechecks": 0}
    admitted_via: Dict[str, Optional[str]] = {}
    parent_edge: Dict[str, str] = {}
    reached: Dict[str, None] = {}
    revealed: Dict[str, None] = {}
    pending: Dict[str, set] = {}
    revealed_tail_index: Dict[str, List] = {}
    revealed_edges: Dict[str, None] = {}
    rarity: Dict[str, int] = {}
    summary = pf.channel_summary() if policy == "rarity" else None

    def fire(edge) -> List[str]:
        """Fire one fully-tailed, warrant-live edge; admit live heads. Returns new atoms."""
        c["expansions"] += 1
        new_atoms: List[str] = []
        for h in edge.heads:
            if h in reached:
                continue
            if not pf.atom_live(h, revoked):
                continue
            reached[h] = None
            admitted_via[h] = edge.relation_type
            parent_edge[h] = edge.edge_id
            rarity[h] = summary.get(edge.relation_type, 0) if summary else 0
            c["atoms_admitted"] += 1
            new_atoms.append(h)
        return new_atoms

    def process_new_atoms(new_atoms: List[str]) -> None:
        """Decrement pending counters of revealed edges tailed at newly reached atoms."""
        queue = deque(new_atoms)
        while queue:
            u = queue.popleft()
            for e2 in revealed_tail_index.get(u, ()):
                p = pending.get(e2.edge_id)
                if p is None:
                    continue
                p.discard(u)
                c["pending_rechecks"] += 1
                if not p:
                    del pending[e2.edge_id]
                    if pf.edge_live(e2, revoked):
                        queue.extend(fire(e2))

    if not pf.atom_live(s, revoked):
        return {"decision": NOT_SUPPORTED, "counters": c, "reached": set(),
                "admitted_via": admitted_via, "parent_edge": parent_edge}
    reached[s] = None
    admitted_via[s] = None

    def frontier():
        return [v for v in reached if v not in revealed]

    while True:
        if t in reached:
            c["early_stopped"] = True
            return {"decision": SUPPORTED, "counters": c, "reached": set(reached),
                    "admitted_via": admitted_via, "parent_edge": parent_edge}
        fr = frontier()
        if not fr:
            return {"decision": NOT_SUPPORTED, "counters": c, "reached": set(reached),
                    "admitted_via": admitted_via, "parent_edge": parent_edge}
        if budget is not None and pf.counters["probes"] >= budget:
            c["budget_exhausted"] = True
            return {"decision": NOT_SUPPORTED, "counters": c, "reached": set(reached),
                    "admitted_via": admitted_via, "parent_edge": parent_edge}
        if policy == "naive":
            v = fr[0]
        elif policy == "rarity":
            v = min(fr, key=lambda x: (rarity.get(x, 0), x))
        elif policy == "shuffle":
            if rng is None:
                raise ValueError("shuffle policy requires a seeded rng")
            v = rng.choice(fr)
        else:
            raise ValueError("unknown policy %r" % policy)
        postings = pf.probe(v)
        revealed[v] = None
        c["probes"] += 1
        new_atoms: List[str] = []
        for e in postings:
            if e.edge_id in revealed_edges:
                continue
            revealed_edges[e.edge_id] = None
            for u in e.tails:
                revealed_tail_index.setdefault(u, []).append(e)
            unreached_tails = {u for u in e.tails if u not in reached}
            if unreached_tails:
                pending.setdefault(e.edge_id, set()).update(unreached_tails)
            elif pf.edge_live(e, revoked):
                new_atoms.extend(fire(e))
        if new_atoms:
            process_new_atoms(new_atoms)
