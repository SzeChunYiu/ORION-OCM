"""Representation arms over one KnowledgeSpace (M8 §1).  No arm is privileged by name.

R0 flat          one region = every atom (the M1–M7 default)
R1 hand tree     regions from declared labels (field → subject), single parent; tuned on dev only
R2 communities   deterministic label propagation on the undirected incidence graph; overlaps where
                 an atom's neighbourhood is split between two communities (multiple membership)
R3 nested        R2 regions each summarised by a macro (abstraction.summarize with a certificate);
                 the parent level sees exported claims only
R4 fibred        base = scope contexts; fibres = per-context sub-spaces; transports = declared
                 correspondences between contexts (TransportMap, warrant ⊗)
R5 sheaf         CANNOT_CHECK disposition: no task in the suites gives overlap/gluing semantics
R6 learned       proposals (split / merge / overlap / promote-to-macro / drop-macro) scored on a
                 *frozen future task stream* by the objective vector; adopted only if the predicted
                 effect is realised on held-out tasks (never rewarding complexity)
R7 continuous    CANNOT_CHECK disposition: no embedding/neural component off-GPU in this study

Parents: label propagation (Raghavan–Albert–Kumara 2007), Louvain/Leiden (Blondel 2008; Traag 2019),
multilevel coarsening (Karypis–Kumar), lumpability (Kemeny–Snell) via `abstraction`; fibrations /
indexed categories (Grothendieck) for R4 — the residual, if any, is the evidence-governed coupling.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable, Mapping, Sequence

from ocm.kso import abstraction as AB
from ocm.kso.space import KnowledgeSpace
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile

from .interface import MacroInterface, Region, TransportMap, containment_consistent, macro_for


def _adjacency(ks: KnowledgeSpace) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {a: set() for a in ks.ids}
    for e in ks.hyperedges:
        inc = list(e.incident)
        for a in inc:
            for b in inc:
                if a != b:
                    adj[a].add(b)
    return adj


# ------------------------------------------------------------------ R0 / R1
@dataclass
class FlatArm:
    name: str = "R0_flat"
    ks: KnowledgeSpace = None

    def regions(self) -> list[Region]:
        return [Region("all", frozenset(self.ks.ids), (), "all")]

    def regions_of(self, atom_id: str) -> list[str]:
        return ["all"]

    def macro(self, region_id: str) -> MacroInterface:
        return macro_for(self.ks, self.regions()[0])

    def transports(self) -> list[TransportMap]:
        return []

    def describe(self) -> dict[str, Any]:
        return {"arm": self.name, "regions": 1, "overlaps": 0, "transports": 0}


@dataclass
class HandTreeArm:
    ks: KnowledgeSpace
    labels: Mapping[str, str]                  # atom → field label (declared, possibly misleading)
    name: str = "R1_hand_tree"

    def regions(self) -> list[Region]:
        groups: dict[str, set[str]] = defaultdict(set)
        for a in self.ks.ids:
            groups[self.labels.get(a, "unlabelled")].add(a)
        root = Region("root", frozenset(self.ks.ids), (), "root")
        return [root] + [Region(lab, frozenset(ats), ("root",), lab) for lab, ats in sorted(groups.items())]

    def regions_of(self, atom_id: str) -> list[str]:
        return ["root", self.labels.get(atom_id, "unlabelled")]

    def macro(self, region_id: str) -> MacroInterface:
        return macro_for(self.ks, next(r for r in self.regions() if r.region_id == region_id))

    def transports(self) -> list[TransportMap]:
        return []

    def describe(self) -> dict[str, Any]:
        rs = self.regions()
        ok, why = containment_consistent(rs)
        return {"arm": self.name, "regions": len(rs) - 1, "overlaps": 0, "transports": 0, "containment_consistent": ok}


# ------------------------------------------------------------------ R2 communities
def label_propagation(ks: KnowledgeSpace, *, rounds: int = 20) -> dict[str, str]:
    """Deterministic (sorted ties) label propagation on the undirected incidence graph."""
    adj = _adjacency(ks)
    label = {a: a for a in ks.ids}
    for _ in range(rounds):
        changed = False
        for a in sorted(ks.ids):
            counts: dict[str, int] = defaultdict(int)
            for b in adj[a]:
                counts[label[b]] += 1
            if not counts:
                continue
            best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            if best != label[a] and counts[best] > counts.get(label[a], 0):
                label[a] = best
                changed = True
        if not changed:
            break
    return label


@dataclass
class CommunityArm:
    ks: KnowledgeSpace
    name: str = "R2_communities"
    overlap_fraction: float = 0.34             # an atom joins a second community if ≥ this share of its neighbours are there

    def _communities(self) -> tuple[dict[str, str], dict[str, set[str]]]:
        lab = label_propagation(self.ks)
        adj = _adjacency(self.ks)
        members: dict[str, set[str]] = defaultdict(set)
        for a, l in lab.items():
            members[l].add(a)
        # multiple membership (M8 §6): shared atoms, never duplicated
        for a in self.ks.ids:
            counts: dict[str, int] = defaultdict(int)
            for b in adj[a]:
                counts[lab[b]] += 1
            tot = sum(counts.values())
            for l, c in counts.items():
                if l != lab[a] and tot and c / tot >= self.overlap_fraction:
                    members[l].add(a)
        return lab, members

    def regions(self) -> list[Region]:
        _, members = self._communities()
        names = {l: f"c{i}" for i, l in enumerate(sorted(members))}
        return [Region(names[l], frozenset(ats), (), names[l]) for l, ats in sorted(members.items())]

    def regions_of(self, atom_id: str) -> list[str]:
        return [r.region_id for r in self.regions() if atom_id in r.atoms]

    def macro(self, region_id: str) -> MacroInterface:
        return macro_for(self.ks, next(r for r in self.regions() if r.region_id == region_id))

    def transports(self) -> list[TransportMap]:
        return []

    def describe(self) -> dict[str, Any]:
        rs = self.regions()
        overl = sum(1 for a in self.ks.ids if sum(1 for r in rs if a in r.atoms) > 1)
        return {"arm": self.name, "regions": len(rs), "overlaps": overl, "transports": 0}


# ------------------------------------------------------------------ R3 nested summaries
@dataclass
class NestedArm:
    ks: KnowledgeSpace
    name: str = "R3_nested"
    base: CommunityArm = None
    summaries: dict[str, str] = field(default_factory=dict)      # region → summary atom id
    ks_with_summaries: KnowledgeSpace = None

    def __post_init__(self) -> None:
        self.base = CommunityArm(self.ks)
        ks = self.ks
        for r in self.base.regions():
            sid = f"macro:{r.region_id}"
            try:
                ks, _ = AB.summarize(ks, sorted(r.atoms), sid)
                self.summaries[r.region_id] = sid
            except Exception:  # noqa: BLE001 — a region that cannot be summarised stays unsummarised (reported)
                continue
        self.ks_with_summaries = ks

    def regions(self) -> list[Region]:
        return self.base.regions()

    def regions_of(self, atom_id: str) -> list[str]:
        return self.base.regions_of(atom_id)

    def macro(self, region_id: str) -> MacroInterface:
        return macro_for(self.ks_with_summaries, next(r for r in self.regions() if r.region_id == region_id))

    def transports(self) -> list[TransportMap]:
        return []

    def describe(self) -> dict[str, Any]:
        d = self.base.describe()
        return {**d, "arm": self.name, "summaries": len(self.summaries)}


# ------------------------------------------------------------------ R4 fibred
@dataclass
class FibredArm:
    ks: KnowledgeSpace
    correspondences: Sequence[TransportMap] = ()
    name: str = "R4_fibred"

    def regions(self) -> list[Region]:
        fibres: dict[str, set[str]] = defaultdict(set)
        for a in self.ks.atoms:
            ctx = "universal" if a.scope.contexts is None else "+".join(sorted(a.scope.contexts))
            fibres[ctx].add(a.atom_id)
        return [Region(f"fibre:{c}", frozenset(ats), (), c) for c, ats in sorted(fibres.items())]

    def regions_of(self, atom_id: str) -> list[str]:
        a = self.ks.atom(atom_id)
        return [f"fibre:{'universal' if a.scope.contexts is None else '+'.join(sorted(a.scope.contexts))}"]

    def macro(self, region_id: str) -> MacroInterface:
        return macro_for(self.ks, next(r for r in self.regions() if r.region_id == region_id))

    def transports(self) -> list[TransportMap]:
        return list(self.correspondences)

    def describe(self) -> dict[str, Any]:
        return {"arm": self.name, "regions": len(self.regions()), "overlaps": 0, "transports": len(self.correspondences)}


# ------------------------------------------------------------------ R6 learned partitions
@dataclass(frozen=True)
class Proposal:
    op: str                                     # split | merge | overlap | promote_macro | drop_macro
    regions: tuple[str, ...]
    predicted_effect: dict[str, float]          # objective components the proposal claims to improve
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class LearnedArm:
    """Starts from R2 and adopts proposals whose predicted objective effect is *realised* on a frozen
    held-out task stream; a proposal that only increases topology size is refused."""
    ks: KnowledgeSpace
    name: str = "R6_learned"
    current: list[Region] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    learner_cost: int = 0

    def __post_init__(self) -> None:
        self.current = CommunityArm(self.ks).regions()

    def regions(self) -> list[Region]:
        return list(self.current)

    def regions_of(self, atom_id: str) -> list[str]:
        return [r.region_id for r in self.current if atom_id in r.atoms]

    def macro(self, region_id: str) -> MacroInterface:
        return macro_for(self.ks, next(r for r in self.current if r.region_id == region_id))

    def transports(self) -> list[TransportMap]:
        return []

    def propose(self, evaluate) -> list[Proposal]:
        """Candidate operations with predicted effects from a *dev* evaluation (evaluate(regions) → vector)."""
        base = evaluate(self.current)
        props = []
        for r in self.current:
            if len(r.atoms) >= 4:
                atoms = sorted(r.atoms)
                half = len(atoms) // 2
                cand = [x for x in self.current if x.region_id != r.region_id] + [Region(r.region_id + "a", frozenset(atoms[:half]), (), r.label), Region(r.region_id + "b", frozenset(atoms[half:]), (), r.label)]
                v = evaluate(cand)
                self.learner_cost += 1
                props.append(Proposal("split", (r.region_id,), {k: v[k] - base[k] for k in v}, {"candidate": cand}))
        for i, r in enumerate(self.current):
            for s in self.current[i + 1:]:
                cand = [x for x in self.current if x.region_id not in (r.region_id, s.region_id)] + [Region(r.region_id + "+" + s.region_id, r.atoms | s.atoms, (), r.label)]
                v = evaluate(cand)
                self.learner_cost += 1
                props.append(Proposal("merge", (r.region_id, s.region_id), {k: v[k] - base[k] for k in v}, {"candidate": cand}))
        return props

    def adopt(self, proposal: Proposal, evaluate_heldout, *, base_heldout: dict[str, float]) -> bool:
        """Adopt iff the held-out objective improves on the components the proposal predicted, with no
        component worse by more than its predicted loss, and the region count did not grow for free."""
        cand = proposal.detail["candidate"]
        v = evaluate_heldout(cand)
        self.learner_cost += 1
        improved = any(proposal.predicted_effect.get(k, 0) > 0 and v[k] > base_heldout[k] for k in v)
        regressed = any(v[k] < base_heldout[k] - 1e-9 and proposal.predicted_effect.get(k, 0) >= 0 for k in v)
        grew = len(cand) > len(self.current) and not improved
        ok = improved and not regressed and not grew
        self.history.append({"op": proposal.op, "regions": proposal.regions, "predicted": proposal.predicted_effect, "heldout": v, "adopted": ok})
        if ok:
            self.current = list(cand)
        return ok

    def describe(self) -> dict[str, Any]:
        overl = sum(1 for a in self.ks.ids if sum(1 for r in self.current if a in r.atoms) > 1)
        return {"arm": self.name, "regions": len(self.current), "overlaps": overl, "transports": 0, "adopted": sum(1 for h in self.history if h["adopted"]), "proposals": len(self.history), "learner_cost": self.learner_cost}


CANNOT_CHECK_ARMS = {"R5_sheaf": "no task in the frozen suites gives overlap/gluing semantics beyond R2 multiple membership", "R7_continuous": "no embedding/neural component is available off-GPU in this study"}


def mutant_reward_complexity(arm: LearnedArm, proposal: Proposal) -> bool:
    """Planted (M8 §15 'learned topology grows without task benefit'): adopt every split."""
    if proposal.op == "split":
        arm.current = list(proposal.detail["candidate"])
        return True
    return False
