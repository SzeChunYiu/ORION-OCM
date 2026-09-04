"""Recursive KSO V0 — overlapping local KnowledgeSpaces with authority-safe macro interfaces.

This is a finite executable calibration of the field -> subject -> domain idea. It is intentionally
not a literal tree: one scope may have several parents. Every scope owns a local frozen KSO shape;
a child can publish an exported macro into a parent only through an explicit evidence-bearing
bridge. The macro's warrant is the conjunction of the bridge and the exported child warrants, so
revoking child evidence automatically kills every dependent macro without touching unrelated
fibres.

No category-theory novelty is claimed. The implementation is a concrete witness for the contract
in RECURSIVE_KSO_ARCHITECTURE_V1.md. Exit: 0 pass, 1 defect, 2 CANNOT_CHECK.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m0 = _load("kso_m0_freeze_checks_v1", HERE / "kso_m0_freeze_checks_v1.py")
kso = m0.kso
ONE = m0.ONE


class CannotCheck(RuntimeError):
    pass


@dataclass(frozen=True)
class MacroCell:
    macro_id: str
    child_scope: str
    parent_scope: str
    export_atom_ids: tuple[str, ...]
    bridge_evidence_id: int
    parent_atom_id: str


@dataclass
class Scope:
    scope_id: str
    kind: str
    parents: set[str] = field(default_factory=set)
    children: set[str] = field(default_factory=set)
    space: object = field(init=False)

    def __post_init__(self) -> None:
        root = f"scope:{self.scope_id}:root"
        self.space = kso.KnowledgeSpace((kso.Atom(root, "scope_root", ONE),), ())
        self.space.validate()

    @property
    def root_id(self) -> str:
        return f"scope:{self.scope_id}:root"


@dataclass
class RecursiveKSO:
    scopes: dict[str, Scope] = field(default_factory=dict)
    macros: dict[str, MacroCell] = field(default_factory=dict)
    revoked: set[int] = field(default_factory=set)

    def add_scope(self, scope_id: str, kind: str, parents: Sequence[str] = ()) -> Scope:
        if not scope_id.strip() or not kind.strip():
            raise ValueError("scope id and kind are required")
        if scope_id in self.scopes:
            raise ValueError(f"duplicate scope {scope_id}")
        missing = [p for p in parents if p not in self.scopes]
        if missing:
            raise KeyError(f"unknown parent scopes: {missing}")
        s = Scope(scope_id, kind)
        self.scopes[scope_id] = s
        linked: list[str] = []
        try:
            for p in parents:
                self.link_parent(scope_id, p)
                linked.append(p)
        except Exception:
            for p in linked:
                self.scopes[p].children.discard(scope_id)
            self.scopes.pop(scope_id, None)
            raise
        return s

    def link_parent(self, child: str, parent: str) -> None:
        if child == parent:
            raise ValueError("a scope cannot contain itself")
        if child not in self.scopes or parent not in self.scopes:
            raise KeyError("both scopes must exist")
        # Adding child -> parent forms a cycle exactly when the proposed parent is already below child.
        if parent in self.descendants(child):
            raise ValueError("containment cycle")
        self.scopes[child].parents.add(parent)
        self.scopes[parent].children.add(child)

    def descendants(self, scope_id: str) -> frozenset[str]:
        if scope_id not in self.scopes:
            raise KeyError(scope_id)
        reached: set[str] = set()
        frontier = list(self.scopes[scope_id].children)
        while frontier:
            x = frontier.pop()
            if x in reached:
                continue
            reached.add(x)
            frontier.extend(self.scopes[x].children)
        return frozenset(reached)

    def ancestors(self, scope_id: str) -> frozenset[str]:
        if scope_id not in self.scopes:
            raise KeyError(scope_id)
        reached: set[str] = set()
        frontier = list(self.scopes[scope_id].parents)
        while frontier:
            x = frontier.pop()
            if x in reached:
                continue
            reached.add(x)
            frontier.extend(self.scopes[x].parents)
        return frozenset(reached)

    def add_local_atom(
        self,
        scope_id: str,
        atom_id: str,
        atom_type: str,
        evidence_id: int,
        *,
        certificate=None,
    ) -> None:
        scope = self.scopes[scope_id]
        atom = kso.Atom(atom_id, atom_type, (frozenset({evidence_id}),))
        edge = kso.Hyperedge(
            "scope-edge:" + hashlib.sha256(f"{scope_id}|{atom_id}".encode()).hexdigest()[:16],
            (scope.root_id,),
            (atom_id,),
            "SUPPORT",
            profile=ONE,
        )
        scope.space, rec = m0.admit(
            scope.space,
            atom,
            (edge,),
            certificate or m0.CertificateKind.INSTRUCTION,
            revoked=self.revoked,
        )
        if not (rec.warranted and rec.reachable_by_navigation):
            raise CannotCheck(f"local atom admission failed: {scope_id}:{atom_id}")

    def attach_space(self, scope_id: str, space) -> None:
        """Attach an already-validated local KSO (e.g. LanguageKSO.space) to a registered scope."""
        if scope_id not in self.scopes:
            raise KeyError(scope_id)
        space.validate()
        self.scopes[scope_id].space = space

    def publish_macro(
        self,
        child_scope: str,
        parent_scope: str,
        export_atom_ids: Sequence[str],
        bridge_evidence_id: int,
    ) -> MacroCell:
        if child_scope not in self.scopes or parent_scope not in self.scopes:
            raise KeyError("unknown child/parent scope")
        if parent_scope not in self.scopes[child_scope].parents:
            raise ValueError("macro publication requires a registered containment/interface link")
        exports = tuple(dict.fromkeys(export_atom_ids))
        if not exports:
            raise ValueError("macro needs at least one exported child atom")
        child = self.scopes[child_scope]
        amap = child.space.atom_map()
        if any(x not in amap for x in exports):
            raise KeyError("macro references unknown child atom")

        profile = (frozenset({bridge_evidence_id}),)
        for atom_id in exports:
            profile = kso.profile_and(profile, amap[atom_id].profile)
        if not kso.profile_live(profile, self.revoked):
            raise CannotCheck("cannot publish a macro whose supporting warrant is not live")

        digest = hashlib.sha256(f"{child_scope}|{parent_scope}|{'|'.join(exports)}".encode()).hexdigest()[:16]
        macro_id = f"macro:{child_scope}->{parent_scope}:{digest}"
        parent_atom = f"scope:{parent_scope}:{macro_id}"
        if macro_id in self.macros:
            raise ValueError("duplicate macro")
        parent = self.scopes[parent_scope]
        atom = kso.Atom(parent_atom, "kso_macro", profile)
        edge = kso.Hyperedge(
            f"macro-edge:{digest}",
            (parent.root_id,),
            (parent_atom,),
            "SUPPORT",
            profile=ONE,
        )
        parent.space, rec = m0.admit(
            parent.space,
            atom,
            (edge,),
            m0.CertificateKind.INSTRUCTION,
            revoked=self.revoked,
        )
        if not (rec.warranted and rec.reachable_by_navigation):
            raise CannotCheck("macro admission failed")
        macro = MacroCell(macro_id, child_scope, parent_scope, exports, bridge_evidence_id, parent_atom)
        self.macros[macro_id] = macro
        return macro

    def macro_live(self, macro_id: str) -> bool:
        m = self.macros[macro_id]
        atom = self.scopes[m.parent_scope].space.atom_map()[m.parent_atom_id]
        return kso.profile_live(atom.profile, self.revoked)

    def descend(self, macro_id: str) -> Scope:
        return self.scopes[self.macros[macro_id].child_scope]

    def revoke(self, evidence_id: int) -> None:
        self.revoked.add(evidence_id)

    def reinstate(self, evidence_id: int) -> None:
        self.revoked.discard(evidence_id)

    def local_atom_live(self, scope_id: str, atom_id: str) -> bool:
        atom = self.scopes[scope_id].space.atom_map()[atom_id]
        return kso.profile_live(atom.profile, self.revoked)


def run_recursive_kso_v0() -> dict[str, object]:
    r = RecursiveKSO()
    r.add_scope("science", "DOMAIN")
    r.add_scope("mathematics", "SUBJECT", ("science",))
    r.add_scope("machine-learning", "SUBJECT", ("science",))
    r.add_scope("statistics", "FIELD", ("mathematics",))
    # One field can live in several subjects: this is the deliberate non-tree case.
    r.add_scope("causal-inference", "FIELD", ("statistics", "machine-learning"))
    r.add_scope("linguistics", "SUBJECT", ("science",))

    assert r.scopes["causal-inference"].parents == {"statistics", "machine-learning"}
    assert {"statistics", "mathematics", "machine-learning", "science"} <= r.ancestors("causal-inference")

    r.add_local_atom("causal-inference", "claim:do-semantics", "claim", 101)
    r.add_local_atom("causal-inference", "skill:adjustment", "procedure", 102)
    r.add_local_atom("linguistics", "claim:construction", "claim", 201)

    m_stats = r.publish_macro("causal-inference", "statistics", ("claim:do-semantics", "skill:adjustment"), 301)
    m_ml = r.publish_macro("causal-inference", "machine-learning", ("claim:do-semantics",), 302)
    assert r.macro_live(m_stats.macro_id) and r.macro_live(m_ml.macro_id)
    assert r.descend(m_stats.macro_id).scope_id == "causal-inference"

    # Child revocation must kill every macro that depends on that export, but not an unrelated fibre.
    assert r.local_atom_live("linguistics", "claim:construction")
    r.revoke(101)
    assert not r.macro_live(m_stats.macro_id)
    assert not r.macro_live(m_ml.macro_id)
    assert r.local_atom_live("linguistics", "claim:construction")
    assert r.local_atom_live("causal-inference", "skill:adjustment")
    r.reinstate(101)
    assert r.macro_live(m_stats.macro_id) and r.macro_live(m_ml.macro_id)

    # Bridge revocation is local to one macro/interface.
    r.revoke(301)
    assert not r.macro_live(m_stats.macro_id)
    assert r.macro_live(m_ml.macro_id)
    r.reinstate(301)

    cycle_rejected = False
    try:
        r.link_parent("science", "causal-inference")
    except ValueError as exc:
        assert str(exc) == "containment cycle"
        cycle_rejected = True
    assert cycle_rejected

    dead_publish_blocked = False
    r.revoke(102)
    try:
        r.publish_macro("causal-inference", "statistics", ("skill:adjustment",), 303)
    except CannotCheck:
        dead_publish_blocked = True
    assert dead_publish_blocked
    r.reinstate(102)

    return {
        "terminal": "RECURSIVE_KSO_V0_CONTROLLED_GREEN",
        "scopes": len(r.scopes),
        "macros": len(r.macros),
        "non_tree": {
            "causal_inference_parent_count": len(r.scopes["causal-inference"].parents),
            "multiple_parent_membership": True,
        },
        "revocation": {
            "child_evidence_kills_both_dependent_macros": True,
            "unrelated_fibre_unchanged": True,
            "bridge_revocation_local": True,
            "reinstatement_restores": True,
        },
        "governance": {
            "dead_export_cannot_publish_macro": dead_publish_blocked,
            "containment_cycle_rejected": cycle_rejected,
            "macro_can_grant_new_authority": False,
        },
        "authority": {
            "scale_established": False,
            "learned_topology": False,
            "category_theory_novelty": False,
            "novelty": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    try:
        result = run_recursive_kso_v0()
    except CannotCheck as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
