"""FNA-6 Soar-style production working memory arm (P2) and the no-goal-binding mutant.

Faithful core of the Soar decision cycle for this function (Soar manual §4,
https://soar.eecs.umich.edu/soar_manual/04_ProceduralKnowledgeLearning/):

* working memory = WMEs ``(id ^attr value)``; input-link WMEs (field edges with their
  tail/head structure, edge-live and atom-live facts) are o-supported and maintained by
  perception when the stream changes — not rescanned per decision;
* an elaboration production derives goal-scoped ``(^node h)`` WMEs, i-supported by their
  firing instantiation: condition = a node WME for the goal, an input edge whose every tail
  is a live node of that goal, the edge-live fact and the head atom-live fact (conjunctive
  enabling, exactly the KSO edge gate);
* WM maintenance retracts an i-supported WME when no instantiation supports it any more
  (support-retraction cascade); a node with an alternative live derivation survives.
  Operator preference resolution is not exercised: the closure is elaboration-level. That
  simplification is declared in the source ledger, not hidden.

The mutant (``goal_scoped=False``) drops goal scoping: node WMEs are global, so the two
obligations' derivations contaminate each other. It is labelled MUTANT and never reported
as a result; it exists so the interference detector provably has teeth.
"""
from __future__ import annotations

from typing import Dict, List, Set, Tuple

from ocm.kso.space import KnowledgeSpace

from contract import ArmResult


class SoarArm:
    def __init__(self, code: str, goal_scoped: bool = True) -> None:
        self.code = code
        self.goal_scoped = goal_scoped
        self.res = ArmResult(code)
        self.c = self.res.counters
        self.ks: KnowledgeSpace = None
        self.revoked: Set[int] = set()
        self.nodes: Dict[Tuple, dict] = {}       # key -> {"alive": bool}
        self.goals: Set[int] = set()
        self._seed_atoms: Dict[int, Set[str]] = {}
        self.edge_live: Dict[str, bool] = {}
        self.atom_live: Dict[str, bool] = {}
        self.edge_tails: Dict[str, tuple] = {}
        self.edge_heads: Dict[str, tuple] = {}
        self.tail_index: Dict[str, List[str]] = {}   # tail atom -> edge ids
        self.head_index: Dict[str, List[str]] = {}   # head atom -> edge ids

    # -- perception / input-link -------------------------------------------
    def _perceive(self, phase: str, ks: KnowledgeSpace, revoked: Set[int]) -> None:
        """Perception diff on a stream change. Charges one input check per edge/atom."""
        rv = frozenset(revoked)
        emap = ks.edge_view
        for eid in list(self.edge_live):         # edges that left the space (drift)
            if eid not in emap:
                self.edge_live.pop(eid)
                self.c.op(phase, kind="wme_remove")
        for e in ks.hyperedges:
            self.c.op(phase, kind="input_edge_check")
            live = e.warrant.is_live(rv)
            if e.edge_id not in self.edge_live:
                self.edge_live[e.edge_id] = live
                self.edge_tails[e.edge_id] = tuple(e.tails)
                self.edge_heads[e.edge_id] = tuple(e.heads)
                for t in e.tails:
                    self.tail_index.setdefault(t, []).append(e.edge_id)
                for h in e.heads:
                    self.head_index.setdefault(h, []).append(e.edge_id)
                self.c.op(phase, kind="wme_add")
            else:
                self.edge_live[e.edge_id] = live
        amap = ks.atom_view
        for x in ks.ids:
            self.c.op(phase, kind="input_atom_check")
            self.atom_live[x] = amap[x].is_live(rv)
        self.revoked = set(revoked)

    # -- WME helpers --------------------------------------------------------
    def _key(self, ob: int, atom: str) -> Tuple:
        return (ob, atom) if self.goal_scoped else ("*", atom)

    def _has_node(self, ob: int, atom: str) -> bool:
        r = self.nodes.get(self._key(ob, atom))
        return r is not None and r["alive"]

    def _edge_fires(self, ob: int, eid: str) -> bool:
        if not self.edge_live.get(eid, False):
            return False
        return all(self._has_node(ob, t) for t in self.edge_tails[eid])

    def _add_node(self, phase: str, ob: int, atom: str) -> None:
        k = self._key(ob, atom)
        if self._has_node(ob, atom):
            return
        if not self.atom_live.get(atom, False):
            return   # the production's atom-live condition: dead atoms never enter WM
        self.nodes[k] = {"alive": True}
        self.c.op(phase, kind="wme_add")
        for eid in self.tail_index.get(atom, ()):  # new token activates candidate tests
            self.c.op(phase, kind="match_test")
            if self._edge_fires(ob, eid):
                for h in self.edge_heads[eid]:
                    if self.atom_live.get(h, False):
                        self._add_node(phase, ob, h)

    def _retract_unsupported(self, phase: str) -> None:
        """Support-retraction cascade to fixpoint. Seeds are o-supported; every node
        WME additionally requires its own atom's live input-link fact (the enabling
        condition of the production that asserts it) — withdrawing that fact retracts
        the node and everything it supported."""
        goals = sorted(self.goals) if not self.goal_scoped else None
        changed = True
        while changed:
            changed = False
            for k in list(self.nodes):
                if not self.nodes[k]["alive"]:
                    continue
                atom = k[1]
                gs = [k[0]] if self.goal_scoped else goals
                alive = self.atom_live.get(atom, False)
                supported = alive and any(atom in self._seed_atoms.get(g, set())
                                          for g in gs)
                if alive and not supported:
                    for eid in self.head_index.get(atom, ()):
                        self.c.op(phase, kind="support_check")
                        if not self.edge_live.get(eid, False) or atom not in self.edge_heads[eid]:
                            continue
                        if any(all(self._has_node(g, t) for t in self.edge_tails[eid]) for g in gs):
                            supported = True
                            break
                if not supported:
                    self.nodes[k]["alive"] = False
                    self.c.op(phase, kind="wme_remove")
                    changed = True

    # -- lifecycle ---------------------------------------------------------
    def open(self, field: KnowledgeSpace, seeds: List[str]) -> None:
        self.ks = field
        self._seed_atoms = {0: set(), 1: set()}
        self._perceive("build", field, set())

    def apply_admission(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self._perceive("merge", ks_after, set(revoked_after))
        obs = sorted(self.goals) if self.goal_scoped else [0]
        for e in event["_edges"]:
            for ob in obs:
                for t in e.tails:
                    if self._has_node(ob, t) and self._edge_fires(ob, e.edge_id):
                        for h in e.heads:
                            if self.atom_live.get(h, False):
                                self._add_node("merge", ob, h)
        touched = set()
        for e in event["_edges"]:
            touched |= set(e.tails) | set(e.heads)
        self.c.touch("admission:%d" % event["after"], touched)

    def apply_revocation(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self._perceive("sweep", ks_after, set(revoked_after))
        self._retract_unsupported("sweep")
        self.c.touch("revocation:%d" % event["after"], set())

    def apply_drift(self, event: dict, ks_after: KnowledgeSpace, revoked_after: Set[int]) -> None:
        self.ks = ks_after
        self._perceive("drift", ks_after, set(revoked_after))
        self._retract_unsupported("drift")
        e = event.get("_edge_before")
        touched = set([event["atom_id"]]) | (set(e.tails) | set(e.heads) if e is not None else set())
        self.c.touch("drift:%d" % event["after"], touched)

    # -- serving -----------------------------------------------------------
    def serve(self, ob: int, seed: str, target: str, ks_now: KnowledgeSpace, revoked_now: Set[int]) -> Tuple[bool, Set[str]]:
        self.ks = ks_now
        if seed not in self._seed_atoms.get(ob, set()):
            self._seed_atoms.setdefault(ob, set()).add(seed)
            self.c.op("serve", kind="wme_add")   # o-supported goal augmentation
        self.goals.add(ob)
        if not self.goal_scoped:
            for g in sorted(self.goals):
                for s in self._seed_atoms.get(g, set()):
                    self._add_node("serve", g, s)
        else:
            self._add_node("serve", ob, seed)
        got = self._has_node(ob, target)
        self.c.resident_sync(ob, self.resident(ob))
        consulted = {k[1] for k, r in self.nodes.items()
                     if r["alive"] and (not self.goal_scoped or k[0] == ob)}
        return bool(got), consulted

    def resident(self, ob: int) -> Set[str]:
        if self.goal_scoped:
            return {k[1] for k, r in self.nodes.items() if k[0] == ob and r["alive"]}
        return {k[1] for k, r in self.nodes.items() if r["alive"]}

    def persistent_state(self) -> dict:
        return {"nodes": sorted("%s|%s" % k for k, r in self.nodes.items() if r["alive"]),
                "seeds": {str(o): sorted(s) for o, s in self._seed_atoms.items()}}

    def close(self) -> None:
        return None
