"""FNA-6 blackboard arms: P1A (append-only panels) and P1B (versioned hypotheses).

Faithful control structure per Hayes-Roth 1985 (doi:10.1016/0004-3702(85)90063-9): a
partitioned blackboard (field panel / closure panel / result panel), knowledge sources
triggered by blackboard events, and an agenda scheduler that rates and fires KS activation
records. The BB1 line adds the control blackboard: a world-version control fact, hypothesis
version tags, and validate-on-read with full recompute — the pre-registered lever L1 for
the append-only line's absent dependency records.

P1A has no retraction primitive: hypotheses are append-only history, so a path revoked from
the field remains on the closure panel and a later serve reads it (stale, counted, never
hidden). Admissions are monotone: the field post triggers KS_CLOSURE for every obligation
that already reached the new edge's tail, so closure grows correctly through admissions.
Liveness gating inside an expansion uses the world state at fire time (a KS can read the
field and the revoked-evidence control facts); what P1A cannot do is un-post.
"""
from __future__ import annotations

from typing import Dict, List, Set, Tuple

from ocm.kso.space import KnowledgeSpace

from contract import ArmResult


class BlackboardArm:
    def __init__(self, code: str, versioned: bool) -> None:
        self.code = code
        self.versioned = versioned
        self.res = ArmResult(code)
        self.c = self.res.counters
        self.ks: KnowledgeSpace = None
        self.revoked: Set[int] = set()
        self.world_version = 0
        self.field: Dict[str, dict] = {}             # edge_id -> {tails, heads, dead}
        self.tail_index: Dict[str, List[str]] = {}   # BB1-style hypothesis index postings
        self.closure: Dict[Tuple[int, str], dict] = {}  # (ob, atom) -> {v, dead}
        self.agenda: List[tuple] = []                # KSAR (priority, -seq, kind, ob, atom)
        self._seq = 0

    # -- scheduler ---------------------------------------------------------
    def _enqueue(self, phase: str, ksar: tuple) -> None:
        self._seq += 1
        self.agenda.append((ksar[0], -self._seq) + ksar[1:])
        self.c.op(phase, kind="agenda_insert")

    def _drain(self, phase: str) -> None:
        while self.agenda:
            self.c.op(phase, kind="agenda_pop")
            ksar = max(self.agenda)
            self.agenda.remove(ksar)
            _, _, kind, ob, atom = ksar
            self._fire_ks_closure(phase, ob, atom)

    def _edge_ok(self, phase: str, eid: str) -> bool:
        rec = self.field[eid]
        self.c.op(phase, kind="field_hyp_read")
        if rec.get("dead"):
            return False
        self.c.op(phase, kind="edge_warrant_check")
        return self.ks.edge_view[eid].warrant.is_live(frozenset(self.revoked))

    def _atom_ok(self, phase: str, atom: str) -> bool:
        self.c.op(phase, kind="atom_warrant_check")
        return self.ks.atom_view[atom].is_live(frozenset(self.revoked))

    def _fire_ks_closure(self, phase: str, ob: int, node: str) -> None:
        """KS_CLOSURE: post successor hypotheses for one frontier node (gated at fire time)."""
        self.c.op(phase, kind="ks_fire")
        for eid in self.tail_index.get(node, ()):
            if not self._edge_ok(phase, eid):
                continue
            rec = self.field[eid]
            if not all(self._live(self.closure.get((ob, t))) for t in rec["tails"]):
                continue
            for h in rec["heads"]:
                if self._atom_ok(phase, h) and not self._live(self.closure.get((ob, h))):
                    self.closure[(ob, h)] = {"v": self.world_version, "dead": False}
                    self.c.op(phase, kind="closure_hyp_post")
                    self._enqueue(phase, (1, "expand", ob, h))

    def _live(self, rec: dict) -> bool:
        return rec is not None and not rec.get("dead", False)

    # -- lifecycle ---------------------------------------------------------
    def open(self, field: KnowledgeSpace, seeds: List[str]) -> None:
        self.ks = field
        for e in field.hyperedges:
            self.field[e.edge_id] = {"tails": tuple(e.tails), "heads": tuple(e.heads), "dead": False}
            self.c.op("build", kind="field_hyp_post")
            for t in e.tails:
                self.tail_index.setdefault(t, []).append(e.edge_id)
                self.c.op("build", kind="tail_posting")
        self.c.op("build", n=len(field.atoms), kind="panel_index_entry")

    def apply_admission(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self.revoked = set(revoked_after)
        if self.versioned:
            self.world_version += 1
            self.c.op("merge", kind="world_version_bump")
        for e in event["_edges"]:
            self.field[e.edge_id] = {"tails": tuple(e.tails), "heads": tuple(e.heads), "dead": False}
            self.c.op("merge", kind="field_hyp_post")
            for t in e.tails:
                self.tail_index.setdefault(t, []).append(e.edge_id)
                self.c.op("merge", kind="tail_posting")
                for ob in (0, 1):
                    if self._live(self.closure.get((ob, t))):
                        self._enqueue("merge", (1, "expand", ob, t))
        if not self.versioned:
            self._drain("merge")  # monotone growth serves admissions
        touched = set()
        for e in event["_edges"]:
            touched |= set(e.tails) | set(e.heads)
        self.c.touch("admission:%d" % event["after"], touched)

    def apply_revocation(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self.revoked = set(revoked_after)
        if self.versioned:
            self.world_version += 1
            self.c.op("sweep", kind="world_version_bump")
        else:
            self.c.op("sweep", kind="no_retraction_primitive")
        self.c.touch("revocation:%d" % event["after"], set())

    def apply_drift(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self.revoked = set(revoked_after)
        if self.versioned:
            self.world_version += 1
            self.c.op("drift", kind="world_version_bump")
            # lever L1's minimal dependency record: the retracted field fact is tombstoned
            self.field[event["edge_id"]]["dead"] = True
            self.c.op("drift", kind="field_hyp_invalidate")
        else:
            self.c.op("drift", kind="no_retraction_primitive")
        e = event.get("_edge_before")
        touched = set([event["atom_id"]]) | (set(e.tails) | set(e.heads) if e is not None else set())
        self.c.touch("drift:%d" % event["after"], touched)

    # -- serving -----------------------------------------------------------
    def serve(self, ob: int, seed: str, target: str, ks_now: KnowledgeSpace, revoked_now: Set[int]) -> Tuple[bool, Set[str]]:
        self.ks = ks_now
        self.revoked = set(revoked_now)
        if not self._live(self.closure.get((ob, seed))):
            self.closure[(ob, seed)] = {"v": self.world_version, "dead": False}
            self.c.op("serve", kind="closure_hyp_post")
            self._enqueue("serve", (2, "expand", ob, seed))
        if self.versioned:
            stale = any(self._live(r) and r["v"] != self.world_version
                        for (o, _), r in self.closure.items() if o == ob)
            if stale:
                for (o, _), r in self.closure.items():
                    if o == ob and self._live(r):
                        r["dead"] = True  # tombstone: append-only history keeps the bytes
                        self.c.op("serve", kind="hyp_invalidate")
                self.closure[(ob, seed)] = {"v": self.world_version, "dead": False}
                self.c.op("serve", kind="closure_hyp_post")
                self._enqueue("serve", (2, "expand", ob, seed))
        self._drain("serve")
        self.c.resident_sync(ob, {a for (o, a), r in self.closure.items()
                                  if o == ob and self._live(r)})
        self.c.op("serve", kind="ks_fire")  # KS_ANSWER reads the closure panel
        got = self._live(self.closure.get((ob, target)))
        self.c.op("serve", kind="closure_hyp_read")
        consulted = {a for (o, a), r in self.closure.items() if o == ob and self._live(r)}
        return bool(got), consulted

    def resident(self, ob: int) -> Set[str]:
        return {a for (o, a), r in self.closure.items() if o == ob and self._live(r)}

    def persistent_state(self) -> dict:
        return {"field": {k: {"tails": list(v["tails"]), "heads": list(v["heads"]),
                              "dead": bool(v.get("dead"))}
                          for k, v in sorted(self.field.items())},
                "closure": sorted("%d|%s|%d|%d" % (o, a, r["v"], int(bool(r.get("dead"))))
                                  for (o, a), r in self.closure.items())}

    def close(self) -> None:
        return None
