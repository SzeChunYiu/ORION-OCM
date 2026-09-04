"""Type registry, authority lattice and scope algebra.

* ``TypeRegistry`` — extensible atom-type and relation-type vocabulary.  The relation vocabulary is
  bound to the atlas ``ContextMapKind`` (``orion_v2.epistemic_atlas``) plus the four KSO relation
  kinds; a new type can be registered without touching warrant/navigation code (M1 A1 test).
* ``Authority`` — a product lattice of named integer ranks; composition takes the meet, so authority
  can never amplify (contract §3: ``A_comp ⪯ A_b ∧ ⋀ A_i``).  Parent: lattice-based information
  flow (Denning 1976).
* ``Scope`` — a set of context tags intersected under composition plus a validity epoch interval
  (contract §3: ``S_comp = S_b ∩ ⋂ S_i``; WLL-4 proves union-scope is unsound).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

ATLAS_CONTEXT_MAP_KINDS: tuple[str, ...] = (
    "RESTRICTION",
    "EMBEDDING",
    "SCALE_CHANGE",
    "BOUNDARY_CHANGE",
    "REPRESENTATION_TRANSPORT",
    "DECISION_TRANSPORT",
)
KSO_RELATION_KINDS: tuple[str, ...] = ("DEPENDENCE", "SUPPORT", "COMPOSITION", "CONSTRAINT")
EDGE_VOCABULARY: tuple[str, ...] = ATLAS_CONTEXT_MAP_KINDS + KSO_RELATION_KINDS
DEPENDENCY_TYPES: frozenset[str] = frozenset(KSO_RELATION_KINDS)

CORE_ATOM_TYPES: tuple[str, ...] = (
    "claim",
    "procedure",
    "constraint",
    "representation",
    "observation",
    "goal",
    "counterexample",
    "proof",
    "model",
    "query_seed",
    "summary",
)


class TypeError_(ValueError):
    """Typed rejection for an unregistered type (named to avoid shadowing the builtin)."""


def atlas_vocabulary_from_source() -> tuple[str, ...] | None:
    try:
        from orion_v2.epistemic_atlas import ContextMapKind  # type: ignore
    except Exception:
        return None
    return tuple(member.value for member in ContextMapKind)


@dataclass(frozen=True, slots=True)
class RelationSpec:
    name: str
    dependency: bool = True      # participates in the impact/reopening cone
    executable: bool = False     # may carry φ_h and fire (Petri conjunctive enabling)
    conjunctive: bool = True     # tails are joint prerequisites (default for hyperedges)


@dataclass(slots=True)
class TypeRegistry:
    atom_types: set[str] = field(default_factory=lambda: set(CORE_ATOM_TYPES))
    relation_types: dict[str, RelationSpec] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.relation_types:
            for r in ATLAS_CONTEXT_MAP_KINDS:
                self.relation_types[r] = RelationSpec(r, dependency=False)
            self.relation_types["DEPENDENCE"] = RelationSpec("DEPENDENCE")
            self.relation_types["SUPPORT"] = RelationSpec("SUPPORT")
            self.relation_types["COMPOSITION"] = RelationSpec("COMPOSITION", executable=True)
            self.relation_types["CONSTRAINT"] = RelationSpec("CONSTRAINT")

    def register_atom_type(self, name: str) -> None:
        if not name.strip():
            raise TypeError_("atom type must be non-blank")
        self.atom_types.add(name)

    def register_relation_type(self, spec: RelationSpec) -> None:
        if not spec.name.strip():
            raise TypeError_("relation type must be non-blank")
        self.relation_types[spec.name] = spec

    def require_atom_type(self, name: str) -> None:
        if name not in self.atom_types:
            raise TypeError_(f"UNREGISTERED_ATOM_TYPE: {name}")

    def require_relation_type(self, name: str) -> RelationSpec:
        spec = self.relation_types.get(name)
        if spec is None:
            raise TypeError_(f"UNREGISTERED_RELATION_TYPE: {name}")
        return spec

    @property
    def dependency_types(self) -> frozenset[str]:
        return frozenset(n for n, s in self.relation_types.items() if s.dependency)

    def bound_to_atlas(self) -> bool | None:
        source = atlas_vocabulary_from_source()
        if source is None:
            return None
        return tuple(source) == ATLAS_CONTEXT_MAP_KINDS and all(r in self.relation_types for r in source)


DEFAULT_REGISTRY = TypeRegistry()


@dataclass(frozen=True, slots=True)
class Authority:
    """Product lattice of named ranks; ``meet`` is coordinate-wise minimum; missing = 0."""

    ranks: tuple[tuple[str, int], ...] = ()

    @staticmethod
    def of(**ranks: int) -> "Authority":
        for k, v in ranks.items():
            if v < 0:
                raise ValueError(f"authority rank must be non-negative: {k}={v}")
        return Authority(tuple(sorted(ranks.items())))

    @staticmethod
    def top(coordinates: Iterable[str], rank: int = 1) -> "Authority":
        return Authority(tuple(sorted((c, rank) for c in coordinates)))

    def as_dict(self) -> dict[str, int]:
        return dict(self.ranks)

    def rank(self, coordinate: str) -> int:
        return self.as_dict().get(coordinate, 0)

    def meet(self, other: "Authority") -> "Authority":
        keys = set(self.as_dict()) | set(other.as_dict())
        return Authority(tuple(sorted((k, min(self.rank(k), other.rank(k))) for k in keys)))

    def __le__(self, other: "Authority") -> bool:
        keys = set(self.as_dict()) | set(other.as_dict())
        return all(self.rank(k) <= other.rank(k) for k in keys)

    def __lt__(self, other: "Authority") -> bool:
        return self <= other and self != other


COMMIT_COORDINATE = "commit"


def meet_authority(items: Iterable[Authority]) -> Authority:
    items = list(items)
    if not items:
        raise ValueError("meet over no authorities is undefined")
    out = items[0]
    for a in items[1:]:
        out = out.meet(a)
    return out


def internal_authority(items: Iterable[Authority]) -> Authority:
    """Authority of an internally composed object (MEG-04 / T1): the meet of the components with
    the operator's own factor, whose ``commit`` coordinate is undeclared (= 0).  Hence no chain of
    internal operations ever reaches commit authority; only an external ActionReceipt confers it."""
    m = meet_authority(items)
    return Authority(tuple(sorted({**m.as_dict(), COMMIT_COORDINATE: 0}.items())))


UNBOUNDED_EPOCH = (0, float("inf"))


@dataclass(frozen=True, slots=True)
class Scope:
    """Context tags (``None`` = universal) and a half-open validity epoch interval."""

    contexts: frozenset[str] | None = None
    epoch: tuple[float, float] = UNBOUNDED_EPOCH

    @staticmethod
    def universal() -> "Scope":
        return Scope()

    @staticmethod
    def of(*contexts: str, epoch: tuple[float, float] = UNBOUNDED_EPOCH) -> "Scope":
        return Scope(frozenset(contexts), epoch)

    @property
    def is_empty(self) -> bool:
        return (self.contexts is not None and not self.contexts) or self.epoch[0] >= self.epoch[1]

    def intersect(self, other: "Scope") -> "Scope":
        if self.contexts is None:
            ctx = other.contexts
        elif other.contexts is None:
            ctx = self.contexts
        else:
            ctx = self.contexts & other.contexts
        return Scope(ctx, (max(self.epoch[0], other.epoch[0]), min(self.epoch[1], other.epoch[1])))

    def covers(self, context: str, at: float | None = None) -> bool:
        if self.contexts is not None and context not in self.contexts:
            return False
        return at is None or (self.epoch[0] <= at < self.epoch[1])

    def __le__(self, other: "Scope") -> bool:  # self ⊆ other
        inter = self.intersect(other)
        return inter == self or (self.is_empty)

    def as_dict(self) -> dict:
        return {"contexts": None if self.contexts is None else sorted(self.contexts), "epoch": list(self.epoch)}


def intersect_scopes(items: Iterable[Scope]) -> Scope:
    out = Scope.universal()
    for s in items:
        out = out.intersect(s)
    return out


# planted mutants


def mutant_authority_max(items: Iterable[Authority]) -> Authority:
    """Wrong: composition amplifies authority to the strongest component."""
    items = list(items)
    keys = set().union(*(set(a.as_dict()) for a in items))
    return Authority(tuple(sorted((k, max(a.rank(k) for a in items)) for k in keys)))


def mutant_scope_union(items: Iterable[Scope]) -> Scope:
    """Wrong: composite scope is the union of component scopes (WLL-4 countermodel)."""
    ctx: set[str] = set()
    lo, hi = float("inf"), 0.0
    universal = False
    for s in items:
        if s.contexts is None:
            universal = True
        else:
            ctx |= s.contexts
        lo, hi = min(lo, s.epoch[0]), max(hi, s.epoch[1])
    return Scope(None if universal else frozenset(ctx), (lo, hi))
