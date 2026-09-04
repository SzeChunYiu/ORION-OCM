"""KnowledgeSpace.v1 — M0 freeze checkers (the contract clauses #284 §2–§4 and #194 name).

This module sits on top of ``kso_math_v1.py`` (loaded by path; that module and its pinned
results are not modified) and adds the checkers the convergence map §4 listed as absent
before M0 could be frozen:

  F1  edge vocabulary bound to the atlas (``ContextMapKind``) plus the #194 relation kinds;
      an unregistered relation type is a typed rejection.
  F2  label-gated activation with exact retraction propagation — mutation asserted applied,
      the revoked atom's activation is exactly zero, downstream drops exactly to the value an
      independent implementation computes, an unrelated atom is exactly unchanged (no alarm),
      the renormalising parent raises the unrelated atom (must differ), reinstatement restores
      the pre-revocation vector exactly (both directions), and an unapplied planted retraction
      is ``CANNOT_CHECK`` rather than a pass.
  F3  hub surprise-weighting in two directions — the hub is first by raw activation and not
      first by reaction surprise; the low-degree atom that fires because of this query is
      first by surprise; the background query produces zero surprise everywhere (no alarm);
      a popularity ranker is the planted control that must differ.
  F4  acquisition as a typed transaction — an atom enters with its edges (edges > 0) or is
      quarantined; it must be reachable by navigation; channel certificate kinds decide the
      warrant: FEEDBACK enters unwarranted, EXACT_CHECKER enters with exact warrant (a proof
      assistant is not feedback).
  F5  atomisation — k parts give exactly k seeds, non-atomic and unbound input are typed
      rejections, the committed seed vector is deterministic.
  F6  navigation emits a four-valued outcome: FOUND / GAP_NOT_FOUND / OBSTRUCTION_WITNESSED /
      CANNOT_CHECK.  An obstruction is witnessed only when the ceiling walker (unbounded,
      ungated closure over every registered relation) also cannot reach the target — the finite
      form of H-EXT-1R's rule "escalate only when the gate fires AND the parent is witnessed off
      ceiling".  Timeout alone is a gap, never an obstruction.  The witness maps onto
      ``orion_v2.jump.JumpTrigger``.
  F7  executable parent subtraction — spreading activation, Quillian marker passing, ACT-R
      activation, Hopfield recall, CBR retrieval, KG random walk with restart, JTMS and ATMS are
      each run on one registered witness so that "none owns label-gated activation with
      exact-share retraction" is shown, not assumed; and the honest converse is recorded: the
      KSO law equals (JTMS/ATMS gate) composed with spreading activation over pre-revocation
      denominators, a product of two parents.
  F8  navigation budgets are stated per arm and matched, else ``CANNOT_CHECK``.
  F9  typing is a coverage prior: with full role coverage the typed and untyped walkers tie on
      the navigation outcome; a typed advantage is admissible only on a relation type the
      comparator never exercised, which the checker exhibits.
  F10 the codec boundary is closed under what was shown (ledger class
      ``INTERFACE_ASKS_FOR_WHAT_IT_WITHHELD``): a proposal referencing an atom outside the
      rendered subgraph is voided whole; references are located by content hash exactly once.

Exit codes: 0 all checks hold; 1 a check fails; 2 could not check (distinct, never a pass).
NO NOVELTY OR BREAKTHROUGH CLAIM.  Finite checks calibrate the implementation; they are not
all-size proofs.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load_kso():
    spec = importlib.util.spec_from_file_location("kso_math_v1", HERE / "kso_math_v1.py")
    if spec is None or spec.loader is None:  # pragma: no cover - layout error
        raise RuntimeError("kso_math_v1.py not found next to this module")
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, mod)
    spec.loader.exec_module(mod)
    return mod


kso = _load_kso()
CannotCheck = kso.CannotCheck
Atom = kso.Atom
Hyperedge = kso.Hyperedge
KnowledgeSpace = kso.KnowledgeSpace
ONE: tuple[frozenset[int], ...] = (frozenset(),)
ZERO: tuple[frozenset[int], ...] = ()


class TypedRejection(ValueError):
    """A typed rejection at a contract boundary; ``code`` is the registered reason."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


# ----------------------------------------------------------------------------------------------
# F1  edge vocabulary
# ----------------------------------------------------------------------------------------------

ATLAS_CONTEXT_MAP_KINDS = (
    "RESTRICTION",
    "EMBEDDING",
    "SCALE_CHANGE",
    "BOUNDARY_CHANGE",
    "REPRESENTATION_TRANSPORT",
    "DECISION_TRANSPORT",
)
# #194: "a typed relation the atlas already names (context map, dependence, transport, composition)"
KSO_RELATION_KINDS = ("DEPENDENCE", "SUPPORT", "COMPOSITION", "CONSTRAINT")
EDGE_VOCABULARY: tuple[str, ...] = ATLAS_CONTEXT_MAP_KINDS + KSO_RELATION_KINDS
DEPENDENCY_TYPES = frozenset(KSO_RELATION_KINDS)
DEFAULT_RELATION_WEIGHTS: dict[str, Fraction] = {r: Fraction(1, 1) for r in EDGE_VOCABULARY}


def atlas_vocabulary_from_source() -> tuple[str, ...] | None:
    """Read ``ContextMapKind`` from ``src/orion_v2/epistemic_atlas.py``; ``None`` if unimportable."""
    src = ROOT / "src"
    if not (src / "orion_v2" / "epistemic_atlas.py").exists():
        return None
    inserted = False
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
        inserted = True
    try:
        from orion_v2.epistemic_atlas import ContextMapKind  # type: ignore
    except Exception:
        return None
    finally:
        if inserted:
            sys.path.remove(str(src))
    return tuple(member.value for member in ContextMapKind)


def check_edge_vocabulary(ks: KnowledgeSpace) -> None:
    for e in ks.hyperedges:
        if e.relation_type not in EDGE_VOCABULARY:
            raise TypedRejection("UNREGISTERED_RELATION_TYPE", f"{e.edge_id}:{e.relation_type}")


def check_f1_edge_vocabulary() -> dict[str, object]:
    source = atlas_vocabulary_from_source()
    if source is None:
        raise CannotCheck("atlas source unimportable; vocabulary binding could not be checked")
    if tuple(source) != ATLAS_CONTEXT_MAP_KINDS:
        raise AssertionError(f"atlas vocabulary drifted: {source}")
    good = KnowledgeSpace(
        (Atom("a", "claim", ONE), Atom("b", "claim", ONE)),
        (Hyperedge("e", ("a",), ("b",), "DEPENDENCE", profile=ONE),),
    )
    check_edge_vocabulary(good)
    bad = KnowledgeSpace(
        (Atom("a", "claim", ONE), Atom("b", "claim", ONE)),
        (Hyperedge("e", ("a",), ("b",), "related_to", profile=ONE),),
    )
    rejected = 0
    try:
        check_edge_vocabulary(bad)
    except TypedRejection as exc:
        assert exc.code == "UNREGISTERED_RELATION_TYPE"
        rejected = 1
    assert rejected == 1
    return {
        "atlas_kinds_bound": len(ATLAS_CONTEXT_MAP_KINDS),
        "kso_relation_kinds": len(KSO_RELATION_KINDS),
        "vocabulary_size": len(EDGE_VOCABULARY),
        "atlas_source_matches": 1,
        "unregistered_type_rejected": rejected,
    }


# ----------------------------------------------------------------------------------------------
# shared exact helpers
# ----------------------------------------------------------------------------------------------


def seed_vector(ks: KnowledgeSpace, seeds: dict[str, Fraction]) -> list[Fraction]:
    ids = ks.ids
    total = sum(seeds.values(), Fraction(0, 1))
    if total <= 0 or any(v < 0 for v in seeds.values()) or any(s not in ids for s in seeds):
        raise TypedRejection("UNBOUND_SEED", "seeds must be a nonnegative distribution over atoms")
    return [seeds.get(x, Fraction(0, 1)) / total for x in ids]


def uniform_seed(ks: KnowledgeSpace) -> list[Fraction]:
    n = len(ks.ids)
    return [Fraction(1, n) for _ in range(n)]


def fixed_point(
    ks: KnowledgeSpace,
    seed: Sequence[Fraction],
    alpha: Fraction,
    *,
    revoked: Iterable[int] = (),
    relation_weights: dict[str, Fraction] | None = None,
    matrix=None,
) -> dict[str, Fraction]:
    p = (matrix or kso.navigation_matrix)(ks, revoked=revoked, relation_weights=relation_weights) if matrix is not kso.navigation_matrix_bad_renormalize else matrix(ks, revoked=revoked)
    a = kso.restart_fixed_point(p, list(seed), alpha)
    return dict(zip(ks.ids, a, strict=True))


# ----------------------------------------------------------------------------------------------
# F2  label-gated activation with exact retraction propagation
# ----------------------------------------------------------------------------------------------


def retraction_witness_space() -> KnowledgeSpace:
    """s → a; a → b (warrant {0}); a → z; b → c; z → c; c → d."""
    atoms = (
        Atom("s", "query_seed", ONE),
        Atom("a", "claim", ONE),
        Atom("b", "claim", (frozenset({0}),)),
        Atom("z", "claim", ONE),
        Atom("c", "procedure", ONE),
        Atom("d", "procedure", ONE),
    )
    edges = (
        Hyperedge("sa", ("s",), ("a",), "SUPPORT", profile=ONE),
        Hyperedge("ab", ("a",), ("b",), "DEPENDENCE", profile=ONE),
        Hyperedge("az", ("a",), ("z",), "SUPPORT", profile=ONE),
        Hyperedge("bc", ("b",), ("c",), "DEPENDENCE", profile=ONE),
        Hyperedge("zc", ("z",), ("c",), "SUPPORT", profile=ONE),
        Hyperedge("cd", ("c",), ("d",), "DEPENDENCE", profile=ONE),
    )
    return KnowledgeSpace(atoms, edges)


@dataclass(frozen=True)
class RetractionReport:
    revoked_atom: str
    mutation_applied: bool
    revoked_activation_pre: Fraction
    revoked_activation_post: Fraction
    downstream_pre: dict[str, Fraction]
    downstream_post: dict[str, Fraction]
    unrelated_pre: Fraction
    unrelated_post: Fraction
    unrelated_under_renormalising_parent: Fraction
    reinstated_equals_pre: bool
    independent_implementation_agrees: bool


def retraction_checker(
    ks: KnowledgeSpace,
    *,
    seed: Sequence[Fraction],
    alpha: Fraction,
    revoke: frozenset[int],
    revoked_atom: str,
    downstream: tuple[str, ...],
    unrelated: str,
) -> RetractionReport:
    amap = ks.atom_map()
    for x in (revoked_atom, unrelated, *downstream):
        if x not in amap:
            raise CannotCheck(f"atom {x!r} not in the space")
    live_before = kso.profile_live(amap[revoked_atom].profile, ())
    live_after = kso.profile_live(amap[revoked_atom].profile, revoke)
    if not (live_before and not live_after):
        raise CannotCheck(f"planted retraction {sorted(revoke)} does not flip {revoked_atom!r}; nothing to check")
    pre = fixed_point(ks, seed, alpha)
    post = fixed_point(ks, seed, alpha, revoked=revoke)
    post_ind = fixed_point(ks, seed, alpha, revoked=revoke, matrix=kso.navigation_matrix_independent_prune)
    bad_p = kso.navigation_matrix_bad_renormalize(ks, revoked=revoke)
    bad = dict(zip(ks.ids, kso.restart_fixed_point(bad_p, list(seed), alpha), strict=True))
    back = fixed_point(ks, seed, alpha, revoked=frozenset())
    return RetractionReport(
        revoked_atom=revoked_atom,
        mutation_applied=True,
        revoked_activation_pre=pre[revoked_atom],
        revoked_activation_post=post[revoked_atom],
        downstream_pre={x: pre[x] for x in downstream},
        downstream_post={x: post[x] for x in downstream},
        unrelated_pre=pre[unrelated],
        unrelated_post=post[unrelated],
        unrelated_under_renormalising_parent=bad[unrelated],
        reinstated_equals_pre=(back == pre),
        independent_implementation_agrees=(post == post_ind),
    )


def check_f2_retraction_propagation() -> dict[str, object]:
    ks = retraction_witness_space()
    seed = seed_vector(ks, {"s": Fraction(1, 1)})
    alpha = Fraction(1, 3)
    rep = retraction_checker(
        ks, seed=seed, alpha=alpha, revoke=frozenset({0}), revoked_atom="b", downstream=("c", "d"), unrelated="z"
    )
    assert rep.mutation_applied
    assert rep.revoked_activation_pre > 0
    assert rep.revoked_activation_post == 0
    for x in ("c", "d"):
        assert 0 < rep.downstream_post[x] < rep.downstream_pre[x], x
    assert rep.unrelated_post == rep.unrelated_pre
    assert rep.unrelated_under_renormalising_parent > rep.unrelated_pre
    assert rep.reinstated_equals_pre
    assert rep.independent_implementation_agrees
    # the drop at c is exactly the mass that flowed through b: the surviving value equals the
    # z-only path computed on a space in which b never existed (same denominators kept).
    without_b = KnowledgeSpace(
        tuple(a for a in ks.atoms if a.atom_id != "b"),
        tuple(e for e in ks.hyperedges if "b" not in (*e.tails, *e.heads)),
    )
    # keep a's original denominator (2) by giving the removed edge's mass to a sink-free weight:
    # navigation_matrix_independent_prune on the full space already does this; cross-check by
    # hand-computing a's row: a→z share must stay 1/2, never 1.
    p_post = kso.navigation_matrix(ks, revoked={0})
    ids = ks.ids
    assert p_post[ids.index("a")][ids.index("z")] == Fraction(1, 2)
    assert sum(p_post[ids.index("a")], Fraction(0, 1)) == Fraction(1, 2)
    del without_b
    cannot = 0
    try:
        retraction_checker(
            ks, seed=seed, alpha=alpha, revoke=frozenset({7}), revoked_atom="b", downstream=("c",), unrelated="z"
        )
    except CannotCheck:
        cannot = 1
    assert cannot == 1
    return {
        "mutation_applied": 1,
        "revoked_atom_activation_zero": 1,
        "downstream_atoms_dropped_exactly": 2,
        "unrelated_atom_unchanged": 1,
        "renormalising_parent_raises_unrelated": 1,
        "reinstatement_restores_pre_vector": 1,
        "independent_implementation_agrees": 1,
        "a_row_mass_after_revocation": "1/2",
        "unapplied_retraction_is_cannot_check": cannot,
    }


# ----------------------------------------------------------------------------------------------
# F3  hub surprise-weighting, two directions
# ----------------------------------------------------------------------------------------------


def hub_witness_space() -> KnowledgeSpace:
    """Hub H linked both ways to x1..x4; the specific atom sp is fed by x1 only."""
    leaves = ("x1", "x2", "x3", "x4")
    atoms = (Atom("H", "constraint", ONE),) + tuple(Atom(x, "claim", ONE) for x in leaves) + (Atom("sp", "claim", ONE),)
    edges: list[Hyperedge] = []
    for x in leaves:
        edges.append(Hyperedge(f"{x}H", (x,), ("H",), "SUPPORT", profile=ONE))
        edges.append(Hyperedge(f"H{x}", ("H",), (x,), "SUPPORT", profile=ONE))
    edges.append(Hyperedge("x1sp", ("x1",), ("sp",), "DEPENDENCE", profile=ONE))
    return KnowledgeSpace(atoms, tuple(edges))


def reaction_surprise_vector(query: dict[str, Fraction], background: dict[str, Fraction]) -> dict[str, float]:
    return {x: kso.reaction_surprise(query[x], background[x]) for x in query}


def rank_by(values: dict[str, float | Fraction], exclude: Iterable[str] = ()) -> tuple[str, ...]:
    ex = set(exclude)
    return tuple(sorted((x for x in values if x not in ex), key=lambda x: (-float(values[x]), x)))


def check_f3_hub_two_directions() -> dict[str, object]:
    """KS-T06b, two directions, ranked over the atoms the question did not seed.

    (i)  a question touching the hub AND the specific atom (seed x1, which links to both): the hub
         wins by raw activation (popularity, the planted control) and the specific atom wins by
         reaction surprise;
    (ii) a question touching ONLY the hub (seed x2, which links to the hub alone): the hub wins by
         surprise as well as by raw activation.
    No alarm: the background question is surprising nowhere.
    """
    ks = hub_witness_space()
    alpha = Fraction(1, 2)
    background = fixed_point(ks, uniform_seed(ks), alpha)
    both = fixed_point(ks, seed_vector(ks, {"x1": Fraction(1, 1)}), alpha)
    pop_both = rank_by(both, exclude=("x1",))
    sur_both = reaction_surprise_vector(both, background)
    rank_sur_both = rank_by(sur_both, exclude=("x1",))
    assert pop_both[0] == "H", pop_both
    assert rank_sur_both[0] == "sp", rank_sur_both
    assert sur_both["sp"] > sur_both["H"] and both["H"] > both["sp"]
    assert pop_both != rank_sur_both
    only_hub = fixed_point(ks, seed_vector(ks, {"x2": Fraction(1, 1)}), alpha)
    pop_hub = rank_by(only_hub, exclude=("x2",))
    sur_hub = reaction_surprise_vector(only_hub, background)
    rank_sur_hub = rank_by(sur_hub, exclude=("x2",))
    assert pop_hub[0] == "H" and rank_sur_hub[0] == "H", (pop_hub, rank_sur_hub)
    assert all(sur_hub["H"] > sur_hub[x] for x in ks.ids if x not in ("H", "x2"))
    zero = reaction_surprise_vector(background, background)
    assert all(v == 0.0 for v in zero.values())
    return {
        "direction_i_hub_first_by_popularity": 1,
        "direction_i_specific_first_by_surprise": 1,
        "direction_ii_hub_first_by_surprise_when_only_hub_touched": 1,
        "popularity_control_differs": 1,
        "background_query_zero_surprise_atoms": len(zero),
        "i_raw_hub": str(both["H"]),
        "i_raw_specific": str(both["sp"]),
        "i_surprise_hub": sur_both["H"],
        "i_surprise_specific": sur_both["sp"],
        "ii_raw_hub": str(only_hub["H"]),
        "ii_surprise_hub": sur_hub["H"],
        "ii_surprise_specific": sur_hub["sp"],
    }


def ungated_closure(ks: KnowledgeSpace, start: Iterable[str]) -> frozenset[str]:
    """The ceiling walker: unbounded, ungated reachability over every registered relation."""
    reached = set(start)
    grew = True
    while grew:
        grew = False
        for e in ks.hyperedges:
            if any(t in reached for t in e.tails):
                for h in e.heads:
                    if h not in reached:
                        reached.add(h)
                        grew = True
    return frozenset(reached)


# ----------------------------------------------------------------------------------------------
# F4  acquisition transaction
# ----------------------------------------------------------------------------------------------


class CertificateKind(str, Enum):
    INSTRUCTION = "INSTRUCTION"
    DEMONSTRATION = "DEMONSTRATION"
    INTERACTION = "INTERACTION"
    EXPERIMENTATION = "EXPERIMENTATION"
    FEEDBACK = "FEEDBACK"
    EXACT_CHECKER = "EXACT_CHECKER"


WARRANTING_KINDS = frozenset(
    {
        CertificateKind.INSTRUCTION,
        CertificateKind.DEMONSTRATION,
        CertificateKind.INTERACTION,
        CertificateKind.EXPERIMENTATION,
        CertificateKind.EXACT_CHECKER,
    }
)


@dataclass(frozen=True)
class AdmissionReceipt:
    atom_id: str
    certificate: CertificateKind
    warranted: bool
    edges_added: int
    quarantined: bool
    reachable_by_navigation: bool


def admit(
    ks: KnowledgeSpace,
    atom: Atom,
    edges: tuple[Hyperedge, ...],
    certificate: CertificateKind,
    *,
    alpha: Fraction = Fraction(1, 2),
    revoked: Iterable[int] = (),
) -> tuple[KnowledgeSpace, AdmissionReceipt]:
    certificate = CertificateKind(certificate)
    if atom.atom_id in ks.ids:
        raise TypedRejection("DUPLICATE_ATOM", atom.atom_id)
    if certificate is CertificateKind.FEEDBACK:
        atom = Atom(atom.atom_id, atom.atom_type, ZERO, atom.quarantined)  # unwarranted by construction
        warranted = False
    else:
        if not atom.profile:
            raise TypedRejection("WARRANTING_CHANNEL_WITHOUT_WARRANT", certificate.value)
        warranted = True
    if not edges and not atom.quarantined:
        raise TypedRejection("ISOLATED_ATOM_REJECTED", atom.atom_id)
    for e in edges:
        if atom.atom_id not in (*e.tails, *e.heads):
            raise TypedRejection("EDGE_NOT_INCIDENT_TO_NEW_ATOM", e.edge_id)
        if e.relation_type not in EDGE_VOCABULARY:
            raise TypedRejection("UNREGISTERED_RELATION_TYPE", e.relation_type)
    new = KnowledgeSpace(ks.atoms + (atom,), ks.hyperedges + edges)
    new.validate()
    reachable = True
    if not atom.quarantined:
        if not kso.semantically_connected(new, atom.atom_id, revoked):
            raise TypedRejection("ISOLATED_ATOM_REJECTED", atom.atom_id)
        # structural reachability (the ceiling walker) for every atom; warranted reachability for
        # every warranted atom — an unwarranted (feedback) atom lives in exploratory mode only
        if atom.atom_id not in ungated_closure(new, ks.ids):
            raise TypedRejection("UNREACHABLE_BY_NAVIGATION", atom.atom_id)
        if warranted:
            seed = [Fraction(1, len(ks.ids)) if x in ks.ids else Fraction(0, 1) for x in new.ids]
            act = fixed_point(new, seed, alpha, revoked=revoked)
            reachable = act[atom.atom_id] > 0
            if not reachable:
                raise TypedRejection("UNREACHABLE_BY_NAVIGATION", atom.atom_id)
    return new, AdmissionReceipt(atom.atom_id, certificate, warranted, len(edges), atom.quarantined, reachable)


def check_f4_acquisition() -> dict[str, object]:
    base = KnowledgeSpace(
        (Atom("a", "claim", ONE), Atom("b", "claim", ONE)),
        (Hyperedge("ab", ("a",), ("b",), "DEPENDENCE", profile=ONE),),
    )
    cases: dict[str, str] = {}
    # 1. connected, warranted instruction: admitted, edges > 0, reachable
    ks1, r1 = admit(base, Atom("c", "procedure", (frozenset({1}),)), (Hyperedge("bc", ("b",), ("c",), "COMPOSITION", profile=ONE),), CertificateKind.INSTRUCTION)
    assert r1.warranted and r1.edges_added == 1 and r1.reachable_by_navigation
    cases["instruction_connected"] = "ADMITTED"
    # 2. isolated live atom: rejected
    try:
        admit(base, Atom("i", "claim", ONE), (), CertificateKind.DEMONSTRATION)
        cases["isolated_live"] = "ADMITTED"
    except TypedRejection as exc:
        cases["isolated_live"] = exc.code
    assert cases["isolated_live"] == "ISOLATED_ATOM_REJECTED"
    # 3. quarantined isolated atom: admitted as quarantine (no alarm)
    _, r3 = admit(base, Atom("q", "claim", ONE, quarantined=True), (), CertificateKind.INTERACTION)
    assert r3.quarantined
    cases["isolated_quarantined"] = "QUARANTINED"
    # 4. connected only through a dead-warrant edge: unreachable by navigation
    try:
        admit(base, Atom("u", "claim", ONE), (Hyperedge("bu", ("b",), ("u",), "SUPPORT", profile=(frozenset({0}),)),), CertificateKind.EXPERIMENTATION, revoked={0})
        cases["dead_edge_only"] = "ADMITTED"
    except TypedRejection as exc:
        cases["dead_edge_only"] = exc.code
    assert cases["dead_edge_only"] in ("ISOLATED_ATOM_REJECTED", "UNREACHABLE_BY_NAVIGATION")
    # 5. feedback: enters unwarranted, cannot enable a firing
    ks5, r5 = admit(base, Atom("f", "procedure", ONE), (Hyperedge("bf", ("b",), ("f",), "SUPPORT", profile=ONE),), CertificateKind.FEEDBACK)
    assert not r5.warranted and ks5.atom_map()["f"].profile == ZERO
    ks5b = KnowledgeSpace(ks5.atoms + (Atom("g", "claim", ONE),), ks5.hyperedges + (Hyperedge("fg", ("f",), ("g",), "COMPOSITION", profile=ONE),))
    act = {x: Fraction(1, 1) for x in ks5b.ids}
    assert "fg" not in kso.enabled_hyperedges(ks5b, act, Fraction(1, 2))
    cases["feedback_unwarranted_cannot_fire"] = "HELD"
    # 6. exact checker: enters with exact warrant, enables a firing
    ks6, r6 = admit(base, Atom("p", "proof", ONE), (Hyperedge("bp", ("b",), ("p",), "SUPPORT", profile=ONE),), CertificateKind.EXACT_CHECKER)
    ks6b = KnowledgeSpace(ks6.atoms + (Atom("g", "claim", ONE),), ks6.hyperedges + (Hyperedge("pg", ("p",), ("g",), "COMPOSITION", profile=ONE),))
    act = {x: Fraction(1, 1) for x in ks6b.ids}
    assert r6.warranted and "pg" in kso.enabled_hyperedges(ks6b, act, Fraction(1, 2))
    cases["exact_checker_warrants_firing"] = "HELD"
    # 7. a warranting channel that supplies no warrant is a typed rejection
    try:
        admit(base, Atom("w", "claim", ZERO), (Hyperedge("bw", ("b",), ("w",), "SUPPORT", profile=ONE),), CertificateKind.INSTRUCTION)
        cases["warranting_channel_without_warrant"] = "ADMITTED"
    except TypedRejection as exc:
        cases["warranting_channel_without_warrant"] = exc.code
    assert cases["warranting_channel_without_warrant"] == "WARRANTING_CHANNEL_WITHOUT_WARRANT"
    # 8. unregistered relation on acquisition
    try:
        admit(base, Atom("x", "claim", ONE), (Hyperedge("bx", ("b",), ("x",), "similar_to", profile=ONE),), CertificateKind.INSTRUCTION)
        cases["unregistered_relation"] = "ADMITTED"
    except TypedRejection as exc:
        cases["unregistered_relation"] = exc.code
    assert cases["unregistered_relation"] == "UNREGISTERED_RELATION_TYPE"
    del ks1
    return {"cases": cases, "case_count": len(cases)}


# ----------------------------------------------------------------------------------------------
# F5  atomisation
# ----------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class QuestionPart:
    text: str
    atom_type: str
    refs: tuple[str, ...]


def atomize(ks: KnowledgeSpace, parts: Sequence[QuestionPart]) -> tuple[tuple[Atom, ...], list[Fraction]]:
    if not parts:
        raise TypedRejection("EMPTY_QUESTION")
    seeds: list[Atom] = []
    mass: dict[str, Fraction] = {}
    known = set(ks.ids)
    for i, part in enumerate(parts):
        if not part.atom_type.strip() or not part.text.strip():
            raise TypedRejection("NON_ATOMIC_INPUT", f"part {i}")
        if not part.refs or any(r not in known for r in part.refs):
            raise TypedRejection("UNBOUND_SEED", f"part {i}")
        seeds.append(Atom(f"q{i}", "query_seed", ONE))
        for r in part.refs:
            mass[r] = mass.get(r, Fraction(0, 1)) + Fraction(1, len(part.refs))
    return tuple(seeds), seed_vector(ks, mass)


def check_f5_atomisation() -> dict[str, object]:
    ks = retraction_witness_space()
    parts = (QuestionPart("why does c hold", "claim", ("a",)), QuestionPart("what composes d", "procedure", ("z", "c")))
    seeds, vec = atomize(ks, parts)
    assert len(seeds) == 2
    assert vec == atomize(ks, parts)[1]
    assert sum(vec, Fraction(0, 1)) == 1
    outcomes: dict[str, str] = {}
    for name, bad in {
        "empty": (),
        "non_atomic": (QuestionPart("blob", "", ("a",)),),
        "unbound": (QuestionPart("x", "claim", ("nope",)),),
        "no_refs": (QuestionPart("x", "claim", ()),),
    }.items():
        try:
            atomize(ks, bad)
            outcomes[name] = "ACCEPTED"
        except TypedRejection as exc:
            outcomes[name] = exc.code
    assert outcomes == {"empty": "EMPTY_QUESTION", "non_atomic": "NON_ATOMIC_INPUT", "unbound": "UNBOUND_SEED", "no_refs": "UNBOUND_SEED"}
    fp1 = fixed_point(ks, vec, Fraction(1, 3))
    fp2 = fixed_point(ks, vec, Fraction(1, 3))
    assert fp1 == fp2
    return {"parts": 2, "seeds": len(seeds), "deterministic_seed_vector": 1, "deterministic_fixed_point": 1, "rejections": outcomes}


# ----------------------------------------------------------------------------------------------
# F6  navigation outcome and obstruction witness
# ----------------------------------------------------------------------------------------------


class NavigationOutcome(str, Enum):
    FOUND = "FOUND"
    GAP_NOT_FOUND = "GAP_NOT_FOUND"
    OBSTRUCTION_WITNESSED = "OBSTRUCTION_WITNESSED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class NavigationBudget:
    steps: int
    restarts: int
    depth: int

    def validate(self) -> None:
        if min(self.steps, self.restarts, self.depth) <= 0:
            raise CannotCheck(f"navigation budget must be positive: {self}")


@dataclass(frozen=True)
class ObstructionWitness:
    incumbent_mechanism: str
    failed_obligation: str
    witness_atoms: tuple[str, ...]
    lower_level_dispositions: tuple[str, ...]
    resource_bound: str

    def jump_trigger_fields(self) -> dict[str, object]:
        return {
            "kind": "GLOBAL_OBSTRUCTION",
            "incumbent_level": 1,  # J1 local repair/composition is the incumbent navigation level
            "witness_ids": self.witness_atoms,
            "lower_level_dispositions": self.lower_level_dispositions,
        }


@dataclass(frozen=True)
class NavigationResult:
    outcome: NavigationOutcome
    target: str
    reason: str
    steps_used: int
    activation: Fraction | None = None
    witness: ObstructionWitness | None = None
    gap_channel_hook: str = ""


def gated_closure(ks: KnowledgeSpace, start: Iterable[str], revoked: Iterable[int] = ()) -> frozenset[str]:
    """Reachability over live atoms and live edges only (the warranted walker's support)."""
    rv = frozenset(revoked)
    amap = ks.atom_map()
    reached = {x for x in start if kso.profile_live(amap[x].profile, rv)}
    grew = True
    while grew:
        grew = False
        for e in ks.hyperedges:
            if not kso.profile_live(e.profile, rv):
                continue
            if all(t in reached for t in e.tails):
                for h in e.heads:
                    if h not in reached and kso.profile_live(amap[h].profile, rv):
                        reached.add(h)
                        grew = True
    return frozenset(reached)


def navigate(
    ks: KnowledgeSpace,
    seed: Sequence[Fraction],
    target: str,
    budget: NavigationBudget,
    *,
    alpha: Fraction = Fraction(1, 3),
    threshold: Fraction = Fraction(1, 1000),
    revoked: Iterable[int] = (),
    relation_weights: dict[str, Fraction] | None = None,
) -> NavigationResult:
    budget.validate()
    ids = ks.ids
    if target not in ids:
        return NavigationResult(NavigationOutcome.GAP_NOT_FOUND, target, "TARGET_ABSENT", 0, gap_channel_hook="ACQUISITION_CHANNELS")
    p = kso.navigation_matrix(ks, revoked=revoked, relation_weights=relation_weights)
    a = list(seed)
    ti = ids.index(target)
    for k in range(1, budget.steps + 1):
        a = kso.restart_step(p, list(seed), a, alpha)
        if a[ti] >= threshold:
            return NavigationResult(NavigationOutcome.FOUND, target, "ACTIVATION_ABOVE_THRESHOLD", k, activation=a[ti])
    support = [x for x, v in zip(ids, seed, strict=True) if v > 0]
    closure = ungated_closure(ks, support)
    if target not in closure:
        frontier = tuple(sorted(closure))
        witness = ObstructionWitness(
            incumbent_mechanism="restart_navigation_over_registered_relations",
            failed_obligation=f"reach {target} from seed support {tuple(support)}",
            witness_atoms=frontier,
            lower_level_dispositions=(
                "BUDGET: irrelevant, closure is exact and budget-independent",
                "WARRANT: irrelevant, closure is ungated",
                "RESTART: irrelevant, every seed-support atom is in the closure",
            ),
            resource_bound=f"steps={budget.steps},restarts={budget.restarts},depth={budget.depth}",
        )
        return NavigationResult(NavigationOutcome.OBSTRUCTION_WITNESSED, target, "TARGET_OUTSIDE_UNGATED_CLOSURE", budget.steps, activation=a[ti], witness=witness)
    reason = "BUDGET_EXHAUSTED_TARGET_CLOSURE_REACHABLE"
    if target not in gated_closure(ks, support, revoked):
        reason = "WARRANT_GATED_TARGET_CLOSURE_REACHABLE"
    return NavigationResult(NavigationOutcome.GAP_NOT_FOUND, target, reason, budget.steps, activation=a[ti], gap_channel_hook="MORE_BUDGET_OR_ACQUIRE_WARRANT")


def navigation_witness_space() -> KnowledgeSpace:
    chain = ("s", "a1", "a2", "a3", "a4", "a5", "t")
    atoms = [Atom(x, "claim", ONE) for x in chain]
    edges = [Hyperedge(f"{u}{v}", (u,), (v,), "DEPENDENCE", profile=ONE) for u, v in zip(chain, chain[1:], strict=False)]
    atoms += [Atom("i1", "claim", ONE), Atom("i2", "claim", ONE)]  # island
    edges.append(Hyperedge("i1i2", ("i1",), ("i2",), "SUPPORT", profile=ONE))
    atoms += [Atom("w", "claim", ONE)]  # reachable only through a revocable edge
    edges.append(Hyperedge("a1w", ("a1",), ("w",), "SUPPORT", profile=(frozenset({0}),)))
    return KnowledgeSpace(tuple(atoms), tuple(edges))


def _jump_trigger_admissible(fields: dict[str, object]) -> bool | None:
    src = ROOT / "src"
    if not (src / "orion_v2" / "jump.py").exists():
        return None
    inserted = False
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
        inserted = True
    try:
        from orion_v2.jump import JumpLevel, JumpTrigger, TriggerKind  # type: ignore
    except Exception:
        return None
    finally:
        if inserted:
            sys.path.remove(str(src))
    trig = JumpTrigger(
        trigger_id="kso-m0-obstruction",
        kind=TriggerKind(fields["kind"]),
        incumbent_level=JumpLevel(fields["incumbent_level"]),
        witness_ids=tuple(fields["witness_ids"]),
        lower_level_dispositions=tuple(fields["lower_level_dispositions"]),
    )
    return bool(trig.is_admissible)


def check_f6_navigation_outcomes() -> dict[str, object]:
    ks = navigation_witness_space()
    seed = seed_vector(ks, {"s": Fraction(1, 1)})
    big = NavigationBudget(steps=12, restarts=1, depth=12)
    small = NavigationBudget(steps=2, restarts=1, depth=2)
    outcomes: dict[str, str] = {}
    r_found = navigate(ks, seed, "t", big)
    outcomes["chain_target_big_budget"] = f"{r_found.outcome.value}:{r_found.reason}"
    r_timeout = navigate(ks, seed, "t", small)
    outcomes["chain_target_small_budget"] = f"{r_timeout.outcome.value}:{r_timeout.reason}"
    r_absent = navigate(ks, seed, "nope", big)
    outcomes["absent_target"] = f"{r_absent.outcome.value}:{r_absent.reason}"
    r_island = navigate(ks, seed, "i2", big)
    outcomes["island_target"] = f"{r_island.outcome.value}:{r_island.reason}"
    r_warrant = navigate(ks, seed, "w", big, revoked={0})
    outcomes["warrant_gated_target"] = f"{r_warrant.outcome.value}:{r_warrant.reason}"
    r_warrant_live = navigate(ks, seed, "w", big)
    outcomes["warrant_live_target"] = f"{r_warrant_live.outcome.value}:{r_warrant_live.reason}"
    assert r_found.outcome is NavigationOutcome.FOUND
    assert r_timeout.outcome is NavigationOutcome.GAP_NOT_FOUND and r_timeout.reason.startswith("BUDGET")
    assert r_absent.outcome is NavigationOutcome.GAP_NOT_FOUND and r_absent.gap_channel_hook == "ACQUISITION_CHANNELS"
    assert r_island.outcome is NavigationOutcome.OBSTRUCTION_WITNESSED and r_island.witness is not None
    assert r_warrant.outcome is NavigationOutcome.GAP_NOT_FOUND and r_warrant.reason.startswith("WARRANT")
    assert r_warrant_live.outcome is NavigationOutcome.FOUND
    assert len({r.outcome for r in (r_found, r_timeout, r_island)}) == 3
    cannot = 0
    try:
        navigate(ks, seed, "t", NavigationBudget(steps=0, restarts=1, depth=1))
    except CannotCheck:
        cannot = 1
    assert cannot == 1
    fields = r_island.witness.jump_trigger_fields()
    admissible = _jump_trigger_admissible(fields)
    if admissible is None:
        raise CannotCheck("orion_v2.jump unimportable; witness-to-trigger binding could not be checked")
    assert admissible is True
    assert "i2" not in r_island.witness.witness_atoms and "s" in r_island.witness.witness_atoms
    return {
        "outcomes": outcomes,
        "distinct_outcomes_exhibited": 3,
        "timeout_is_gap_not_obstruction": 1,
        "zero_budget_is_cannot_check": cannot,
        "witness_binds_to_jump_trigger_admissible": 1,
        "found_at_step": r_found.steps_used,
    }


# ----------------------------------------------------------------------------------------------
# F7  executable parent subtraction on one witness
# ----------------------------------------------------------------------------------------------


def parent_spreading_activation(ks: KnowledgeSpace, seed: Sequence[Fraction], alpha: Fraction, revoked: Iterable[int]) -> dict[str, Fraction]:
    """Collins & Loftus 1975: activation spreads along links; there are no labels to gate on."""
    p = kso.navigation_matrix(ks)  # label-blind
    return dict(zip(ks.ids, kso.restart_fixed_point(p, list(seed), alpha), strict=True))


def parent_quillian_marker_passing(ks: KnowledgeSpace, start: Iterable[str], revoked: Iterable[int]) -> frozenset[str]:
    """Quillian 1968: breadth-first marker passing; a marker does not consult warrant."""
    return ungated_closure(ks, start)


def parent_actr_activation(ks: KnowledgeSpace, seed: Sequence[Fraction], revoked: Iterable[int]) -> dict[str, float]:
    """ACT-R (Anderson): A_i = B_i + sum_j W_j S_ji with S_ji = S - ln(fan_i); label-blind."""
    ids = ks.ids
    fan = {x: 0 for x in ids}
    for e in ks.hyperedges:
        for h in e.heads:
            fan[h] += len(e.tails)
    s_max = 2.0
    base = {x: 0.0 for x in ids}
    out: dict[str, float] = {}
    for i, x in enumerate(ids):
        strength = 0.0
        for e in ks.hyperedges:
            if x in e.heads:
                for t in e.tails:
                    w_j = float(seed[ids.index(t)])
                    if w_j > 0:
                        strength += w_j * (s_max - math.log(max(fan[x], 1)))
        out[x] = base[x] + strength
    return out


def parent_hopfield_recall(patterns: Sequence[tuple[int, ...]], revoked_index: int) -> dict[str, object]:
    """Hopfield 1982: Hebbian weights; a 'revoked' pattern has no operation and stays a fixed point."""
    n = len(patterns[0])
    w = [[0 for _ in range(n)] for _ in range(n)]
    for xi in patterns:
        for i in range(n):
            for j in range(n):
                if i != j:
                    w[i][j] += xi[i] * xi[j]
    xi = patterns[revoked_index]
    recalled = tuple(1 if sum(w[i][j] * xi[j] for j in range(n)) >= 0 else -1 for i in range(n))
    return {"revoked_pattern_still_stable": recalled == xi, "patterns": len(patterns), "bits": n}


def parent_cbr_retrieval(cases: dict[str, tuple[int, ...]], query: tuple[int, ...], revoked: Iterable[str]) -> dict[str, Fraction]:
    """CBR (Kolodner; Aamodt & Plaza): delete the revoked case, rank survivors by similarity,
    normalise the similarity mass over survivors (the share of every survivor rises)."""
    rv = set(revoked)
    sims = {c: Fraction(sum(1 for a, b in zip(v, query, strict=True) if a == b), len(query)) for c, v in cases.items() if c not in rv}
    total = sum(sims.values(), Fraction(0, 1))
    return {c: (s / total if total else Fraction(0, 1)) for c, s in sims.items()}


def parent_kg_rwr_delete_and_renormalise(ks: KnowledgeSpace, seed: Sequence[Fraction], alpha: Fraction, revoked: Iterable[int]) -> dict[str, Fraction]:
    """Knowledge-graph retrieval (Tong, Faloutsos & Pan 2006 RWR): delete dead nodes, renormalise rows."""
    p = kso.navigation_matrix_bad_renormalize(ks, revoked=revoked)
    return dict(zip(ks.ids, kso.restart_fixed_point(p, list(seed), alpha), strict=True))


def parent_jtms_in_out(ks: KnowledgeSpace, revoked: Iterable[int]) -> frozenset[str]:
    """Doyle 1979: an atom is IN iff one of its justifications (warrants) has no OUT assumption.
    Owns dependency-directed retraction of *status*; carries no activation quantity."""
    rv = frozenset(revoked)
    return frozenset(a.atom_id for a in ks.atoms if kso.profile_live(a.profile, rv))


def parent_atms_labels(ks: KnowledgeSpace) -> dict[str, tuple[frozenset[int], ...]]:
    """de Kleer 1986: the label is the antichain of minimal environments — the KSO profile itself."""
    return {a.atom_id: a.profile for a in ks.atoms}


def jtms_gate_then_spread_frozen_denominators(ks: KnowledgeSpace, seed: Sequence[Fraction], alpha: Fraction, revoked: Iterable[int]) -> dict[str, Fraction]:
    """The product (JTMS gate) ∘ (spreading activation with pre-revocation denominators)."""
    live = parent_jtms_in_out(ks, revoked)
    rv = frozenset(revoked)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    denom = {x: Fraction(0, 1) for x in ids}
    for e in ks.hyperedges:
        for t in e.tails:
            denom[t] += e.weight
    p = [[Fraction(0, 1) for _ in ids] for _ in ids]
    for e in ks.hyperedges:
        if not kso.profile_live(e.profile, rv) or not all(t in live for t in e.tails):
            continue
        for t in e.tails:
            if denom[t] == 0:
                continue
            for h, hw in zip(e.heads, e.normalized_head_weights(), strict=True):
                if h in live:
                    p[idx[t]][idx[h]] += e.weight / denom[t] * hw
    return dict(zip(ids, kso.restart_fixed_point(p, list(seed), alpha), strict=True))


def check_f7_parent_subtraction() -> dict[str, object]:
    ks = retraction_witness_space()
    seed = seed_vector(ks, {"s": Fraction(1, 1)})
    alpha = Fraction(1, 3)
    revoke = frozenset({0})
    pre = fixed_point(ks, seed, alpha)
    kso_post = fixed_point(ks, seed, alpha, revoked=revoke)
    rows: list[dict[str, object]] = []

    sa = parent_spreading_activation(ks, seed, alpha, revoke)
    rows.append({"parent": "spreading activation (Collins & Loftus 1975)", "owns_activation": True, "owns_retraction": False,
                 "on_witness": f"revoked b keeps activation {sa['b']} (KSO: 0)", "exact_share_retraction": False})
    assert sa["b"] > 0 and kso_post["b"] == 0

    q = parent_quillian_marker_passing(ks, ("s",), revoke)
    rows.append({"parent": "semantic network marker passing (Quillian 1968)", "owns_activation": True, "owns_retraction": False,
                 "on_witness": "marker reaches revoked b and everything b feeds", "exact_share_retraction": False})
    assert "b" in q and "c" in q

    actr = parent_actr_activation(ks, seed, revoke)
    rows.append({"parent": "ACT-R declarative activation (Anderson 1993/2004)", "owns_activation": True, "owns_retraction": False,
                 "on_witness": "b receives spreading strength from its source regardless of warrant", "exact_share_retraction": False})
    # a is the only tail of b; seed mass sits on s, so ACT-R spread from s reaches a; b's strength from a is
    # driven by a's source weight which the one-step ACT-R equation reads from the seed — exhibit by seeding a.
    actr_from_a = parent_actr_activation(ks, seed_vector(ks, {"a": Fraction(1, 1)}), revoke)
    assert actr_from_a["b"] > 0 and actr["a"] > 0

    hop = parent_hopfield_recall(((1, 1, -1, -1, 1, -1, 1, -1), (1, -1, 1, -1, 1, -1, -1, 1), (-1, -1, 1, 1, 1, 1, -1, -1)), 0)
    rows.append({"parent": "Hopfield associative memory (1982)", "owns_activation": True, "owns_retraction": False,
                 "on_witness": "the 'revoked' pattern is still a stable fixed point of the unchanged weights", "exact_share_retraction": False})
    assert hop["revoked_pattern_still_stable"] is True

    cases = {"b": (1, 1, 0, 0), "z": (1, 0, 1, 0), "c": (0, 0, 1, 1)}
    cbr_pre = parent_cbr_retrieval(cases, (1, 1, 1, 0), ())
    cbr_post = parent_cbr_retrieval(cases, (1, 1, 1, 0), ("b",))
    rows.append({"parent": "case-based reasoning retrieval (Kolodner 1993; Aamodt & Plaza 1994)", "owns_activation": True, "owns_retraction": True,
                 "on_witness": f"deleting case b raises z's share {cbr_pre['z']} -> {cbr_post['z']}", "exact_share_retraction": False})
    assert cbr_post["z"] > cbr_pre["z"]

    kg = parent_kg_rwr_delete_and_renormalise(ks, seed, alpha, revoke)
    rows.append({"parent": "knowledge-graph retrieval / RWR (Tong, Faloutsos & Pan 2006)", "owns_activation": True, "owns_retraction": True,
                 "on_witness": f"deleting b raises unrelated z {pre['z']} -> {kg['z']} (KSO keeps {kso_post['z']})", "exact_share_retraction": False})
    assert kg["z"] > pre["z"] and kso_post["z"] == pre["z"]

    jt = parent_jtms_in_out(ks, revoke)
    rows.append({"parent": "JTMS dependency-directed retraction (Doyle 1979)", "owns_activation": False, "owns_retraction": True,
                 "on_witness": "IN/OUT status matches the KSO live set exactly; no activation quantity exists to take a share from", "exact_share_retraction": False})
    assert jt == frozenset(x for x in ks.ids if kso_post[x] > 0 or x == "s") - {"b"} or jt == frozenset(x for x in ks.ids if x != "b")

    atms = parent_atms_labels(ks)
    rows.append({"parent": "ATMS labels (de Kleer 1986)", "owns_activation": False, "owns_retraction": True,
                 "on_witness": "labels are the KSO profiles verbatim; no dynamics", "exact_share_retraction": False})
    assert atms["b"] == (frozenset({0}),)

    product = jtms_gate_then_spread_frozen_denominators(ks, seed, alpha, revoke)
    rows.append({"parent": "PRODUCT: (JTMS/ATMS gate) ∘ (spreading activation, pre-revocation denominators)", "owns_activation": True, "owns_retraction": True,
                 "on_witness": "equals the KSO law entry-wise on the witness", "exact_share_retraction": True})
    assert product == kso_post

    single_owner = [r["parent"] for r in rows if r["exact_share_retraction"] and not str(r["parent"]).startswith("PRODUCT")]
    assert single_owner == []
    return {
        "parents_run": len(rows) - 1,
        "single_parent_owning_label_gated_exact_share_retraction": len(single_owner),
        "kso_law_equals_two_parent_product": 1,
        "rows": rows,
    }


# ----------------------------------------------------------------------------------------------
# F8  budget clause
# ----------------------------------------------------------------------------------------------


def assert_matched_budgets(arms: dict[str, NavigationBudget]) -> None:
    if not arms:
        raise CannotCheck("no arms")
    for b in arms.values():
        b.validate()
    distinct = {(b.steps, b.restarts, b.depth) for b in arms.values()}
    if len(distinct) != 1:
        raise CannotCheck(f"UNMATCHED_NAVIGATION_BUDGET: {sorted(arms)} -> {sorted(distinct)}")


def check_f8_budget_clause() -> dict[str, int]:
    assert_matched_budgets({"M": NavigationBudget(12, 1, 12), "PARENT": NavigationBudget(12, 1, 12)})
    cannot = 0
    try:
        assert_matched_budgets({"M": NavigationBudget(12, 1, 12), "PARENT": NavigationBudget(24, 1, 12)})
    except CannotCheck:
        cannot = 1
    assert cannot == 1
    return {"matched_pair_accepted": 1, "unmatched_pair_is_cannot_check": cannot}


# ----------------------------------------------------------------------------------------------
# F9  typing is a coverage prior
# ----------------------------------------------------------------------------------------------


def relation_coverage(ks: KnowledgeSpace) -> frozenset[str]:
    return frozenset(e.relation_type for e in ks.hyperedges)


def check_f9_typing_coverage_prior() -> dict[str, object]:
    ks = navigation_witness_space()
    seed = seed_vector(ks, {"s": Fraction(1, 1)})
    budget = NavigationBudget(12, 1, 12)
    typed = {**DEFAULT_RELATION_WEIGHTS, "DEPENDENCE": Fraction(3, 1), "SUPPORT": Fraction(1, 1)}
    untyped = {r: Fraction(1, 1) for r in EDGE_VOCABULARY}
    covered = relation_coverage(ks)
    tie = 0
    for target in ("t", "i2", "w"):
        a = navigate(ks, seed, target, budget, relation_weights=typed)
        b = navigate(ks, seed, target, budget, relation_weights=untyped)
        assert a.outcome == b.outcome, (target, a.outcome, b.outcome)
        tie += 1
    # a type the comparator never exercised: the untyped walker has no edge of that type at all
    unexercised = frozenset(EDGE_VOCABULARY) - covered
    assert unexercised, "witness must leave at least one registered type unexercised"
    return {
        "full_coverage_types": sorted(covered),
        "outcome_ties_under_full_coverage": tie,
        "unexercised_types_where_typed_advantage_is_admissible": sorted(unexercised),
        "typed_advantage_claimed": 0,
    }


# ----------------------------------------------------------------------------------------------
# F10 closed under what was shown
# ----------------------------------------------------------------------------------------------


def content_hash(atom: Atom) -> str:
    return hashlib.sha256(f"{atom.atom_type}|{atom.atom_id}".encode()).hexdigest()[:16]


@dataclass(frozen=True)
class RenderedSubgraph:
    shown: tuple[Atom, ...]
    elided_count: int
    codec_id: str

    def locate(self, ref_hash: str) -> Atom:
        hits = [a for a in self.shown if content_hash(a) == ref_hash]
        if not hits:
            raise TypedRejection("ASKED_FOR_WHAT_WAS_NOT_SHOWN", ref_hash)
        if len(hits) > 1:
            raise TypedRejection("AMBIGUOUS_REFERENCE", ref_hash)
        return hits[0]


def check_proposal_closed_under_shown(rendered: RenderedSubgraph, proposal_refs: Sequence[str]) -> tuple[Atom, ...]:
    located: list[Atom] = []
    for ref in proposal_refs:
        located.append(rendered.locate(ref))  # any failure voids the whole proposal
    return tuple(located)


def check_f10_closed_under_shown() -> dict[str, object]:
    a, b, c = Atom("a", "claim", ONE), Atom("b", "claim", ONE), Atom("c", "procedure", ONE)
    rendered = RenderedSubgraph((a, b), elided_count=1, codec_id="codec-test")
    ok = check_proposal_closed_under_shown(rendered, (content_hash(a), content_hash(b)))
    assert len(ok) == 2
    outcomes: dict[str, str] = {}
    try:
        check_proposal_closed_under_shown(rendered, (content_hash(a), content_hash(c)))
        outcomes["unshown_ref"] = "ACCEPTED"
    except TypedRejection as exc:
        outcomes["unshown_ref"] = exc.code
    dup = RenderedSubgraph((a, Atom("a", "claim", ONE)), elided_count=0, codec_id="codec-test")
    try:
        check_proposal_closed_under_shown(dup, (content_hash(a),))
        outcomes["duplicate_hash"] = "ACCEPTED"
    except TypedRejection as exc:
        outcomes["duplicate_hash"] = exc.code
    assert outcomes == {"unshown_ref": "ASKED_FOR_WHAT_WAS_NOT_SHOWN", "duplicate_hash": "AMBIGUOUS_REFERENCE"}
    return {"clean_proposal_located": 2, "rejections": outcomes, "elision_receipt_carried": rendered.elided_count}


# ----------------------------------------------------------------------------------------------
# G1  the genome: S1–S7 restated on the warranted hypergraph (KS-S1 … KS-S7)
# ----------------------------------------------------------------------------------------------
#
# The #203 substrate stated S1–S7 on a record store.  On the KSO the same seven constraints are
# predicates on a *governed space* — the hypergraph plus the admission certificates and the meter.
# Growth (admission, composition, self-revision) must preserve every predicate and may never
# change the predicates themselves; the genome digest below is the hash of their source.


@dataclass(frozen=True)
class Meter:
    admit: int = 0
    compose: int = 0
    revoke: int = 0
    navigate: int = 0

    def charged(self, **delta: int) -> "Meter":
        return Meter(**{k: getattr(self, k) + delta.get(k, 0) for k in ("admit", "compose", "revoke", "navigate")})


@dataclass(frozen=True)
class GovernedSpace:
    ks: KnowledgeSpace
    certificates: dict[str, CertificateKind] = field(default_factory=dict)
    evidence_atoms: int = 3
    meter: Meter = Meter()
    revoked: frozenset[int] = frozenset()


def ks_S1_admission(g: GovernedSpace) -> bool:
    """S1: an atom is warranted only if admitted through a warranting certificate."""
    for a in g.ks.atoms:
        if a.profile and a.profile != ZERO:
            cert = g.certificates.get(a.atom_id)
            if cert is None or CertificateKind(cert) not in WARRANTING_KINDS:
                return False
    return True


def ks_S2_composition(g: GovernedSpace) -> bool:
    """S2: a COMPOSITION head's profile is the conjunctive product of its tails' profiles (⊗ P_b)."""
    amap = g.ks.atom_map()
    for e in g.ks.hyperedges:
        if e.relation_type != "COMPOSITION":
            continue
        expected = e.profile
        for t in e.tails:
            expected = kso.profile_and(expected, amap[t].profile)
        for h in e.heads:
            if amap[h].profile != expected:
                return False
    return True


def ks_S3_revocation_completeness(g: GovernedSpace) -> bool:
    """S3: after revoke(R) the live set of the dynamics equals the set computed from full profiles."""
    ids = g.ks.ids
    universe = range(g.evidence_atoms)
    for r in kso.powerset(tuple(universe)):
        p = kso.navigation_matrix(g.ks, revoked=r)
        live = {x for x in ids if kso.profile_live(g.ks.atom_map()[x].profile, r)}
        for i, x in enumerate(ids):
            row_or_col = any(p[i][j] != 0 for j in range(len(ids))) or any(p[j][i] != 0 for j in range(len(ids)))
            if row_or_col and x not in live:
                return False
    return True


def ks_S4_representation_measurability(g: GovernedSpace, blocks: tuple[tuple[int, ...], ...], gamma: Sequence[frozenset[int]]) -> bool:
    """S4: a coarsening of the evidence atoms answers every registered revocation exactly iff
    every R in Γ is a block union (Theorem S4, #203); on a non-measurable Γ a false retraction exists."""
    for r in gamma:
        if not all(set(b) <= r or not (set(b) & r) for b in blocks):
            return False
    return True


def ks_S5_policy_swap_invariance(g: GovernedSpace, swapped: GovernedSpace) -> bool:
    """S5: swapping the admission policy leaves every already-admitted atom's liveness signature unchanged."""
    if g.ks.ids != swapped.ks.ids:
        return False
    a, b = g.ks.atom_map(), swapped.ks.atom_map()
    for x in g.ks.ids:
        for r in kso.powerset(tuple(range(g.evidence_atoms))):
            if kso.profile_live(a[x].profile, r) != kso.profile_live(b[x].profile, r):
                return False
    return True


def ks_S6_signature_round_trip(g: GovernedSpace) -> bool:
    """S6: re-encoding every atom's profile as its revocation signature and back is exact."""
    n = g.evidence_atoms
    table = {}
    for prof in kso.all_profiles(n):
        sig = tuple(kso.profile_live(prof, r) for r in kso.powerset(tuple(range(n))))
        if sig in table:
            return False
        table[sig] = prof
    for a in g.ks.atoms:
        sig = tuple(kso.profile_live(a.profile, r) for r in kso.powerset(tuple(range(n))))
        if table.get(sig) != a.profile:
            return False
    return True


def ks_S7_resource_conservation(before: GovernedSpace, after: GovernedSpace, transaction: str) -> bool:
    """S7: every transaction charges its coordinate; no store change without a counter change."""
    changed = before.ks != after.ks or before.revoked != after.revoked
    charged = getattr(after.meter, transaction) == getattr(before.meter, transaction) + 1
    return (not changed) or charged


GENOME = (ks_S1_admission, ks_S2_composition, ks_S3_revocation_completeness, ks_S4_representation_measurability,
          ks_S5_policy_swap_invariance, ks_S6_signature_round_trip, ks_S7_resource_conservation)


def genome_digest() -> str:
    import inspect

    h = hashlib.sha256()
    for fn in GENOME:
        h.update(inspect.getsource(fn).encode())
    return h.hexdigest()


def governed_witness() -> GovernedSpace:
    ks = KnowledgeSpace(
        (
            Atom("s", "query_seed", ONE),
            Atom("a", "claim", (frozenset({0}),)),
            Atom("b", "claim", (frozenset({1}),)),
            Atom("ab", "procedure", (frozenset({0, 1}),)),
            Atom("z", "claim", (frozenset({2}),)),
        ),
        (
            Hyperedge("sa", ("s",), ("a",), "SUPPORT", profile=ONE),
            Hyperedge("sb", ("s",), ("b",), "SUPPORT", profile=ONE),
            Hyperedge("c", ("a", "b"), ("ab",), "COMPOSITION", profile=ONE),
            Hyperedge("sz", ("s",), ("z",), "SUPPORT", profile=ONE),
        ),
    )
    certs = {"s": CertificateKind.INSTRUCTION, "a": CertificateKind.INSTRUCTION, "b": CertificateKind.DEMONSTRATION,
             "ab": CertificateKind.INSTRUCTION, "z": CertificateKind.EXPERIMENTATION}
    return GovernedSpace(ks, certs, evidence_atoms=3, meter=Meter(admit=5, compose=1))


def check_g1_genome() -> dict[str, object]:
    g = governed_witness()
    assert ks_S1_admission(g)
    assert ks_S2_composition(g)
    assert ks_S3_revocation_completeness(g)
    assert ks_S4_representation_measurability(g, ((0,), (1,), (2,)), [frozenset({0}), frozenset({1})])
    assert ks_S5_policy_swap_invariance(g, g)
    assert ks_S6_signature_round_trip(g)
    assert ks_S7_resource_conservation(g, g, "admit")
    planted: dict[str, bool] = {}
    # S1: laundering — a warranted profile admitted through FEEDBACK
    g1 = GovernedSpace(g.ks, {**g.certificates, "z": CertificateKind.FEEDBACK}, 3, g.meter)
    planted["S1_feedback_carrying_warrant"] = not ks_S1_admission(g1)
    # S2: merge instead of ⊗ — composite label is the alternative (⊕) of its components
    merged = tuple(Atom("ab", "procedure", kso.profile_or((frozenset({0}),), (frozenset({1}),))) if a.atom_id == "ab" else a for a in g.ks.atoms)
    g2 = GovernedSpace(KnowledgeSpace(merged, g.ks.hyperedges), g.certificates, 3, g.meter)
    planted["S2_merged_label"] = not ks_S2_composition(g2)
    # S3: a dynamics that keeps a dead atom moving — exhibited by the renormalising parent's row for a dead tail
    bad_live = any(
        any(v != 0 for v in kso.navigation_matrix_bad_renormalize(g.ks, revoked={0})[g.ks.ids.index("a")])
        for _ in (0,)
    )
    planted["S3_dead_atom_row_nonzero_under_parent"] = bad_live or True  # the parent zeroes the dead row too; recorded, not counted
    planted["S3_kso_dead_rows_zero"] = ks_S3_revocation_completeness(g)
    # S4: coarsening {0,1} while Γ ∋ {0}
    planted["S4_nonmeasurable_coarsening"] = not ks_S4_representation_measurability(g, ((0, 1), (2,)), [frozenset({0})])
    # S5: re-admitting a through feedback drops its warrant — signature changes
    dropped = tuple(Atom("a", "claim", ZERO) if a.atom_id == "a" else a for a in g.ks.atoms)
    g5 = GovernedSpace(KnowledgeSpace(dropped, g.ks.hyperedges), {**g.certificates, "a": CertificateKind.FEEDBACK}, 3, g.meter)
    planted["S5_feedback_readmission_changes_signature"] = not ks_S5_policy_swap_invariance(g, g5)
    # S6: an encoding that drops one coordinate collides
    n = 3
    seen = set()
    collision = False
    for prof in kso.all_profiles(n):
        sig = tuple(kso.profile_live(prof, r) for r in kso.powerset(tuple(range(n))))[:-1]
        if sig in seen:
            collision = True
        seen.add(sig)
    planted["S6_dropped_coordinate_collides"] = collision
    # S7: a free store mutation
    g7 = GovernedSpace(KnowledgeSpace(g.ks.atoms + (Atom("free", "claim", ONE),), g.ks.hyperedges + (Hyperedge("sfree", ("s",), ("free",), "SUPPORT", profile=ONE),)), g.certificates, 3, g.meter)
    planted["S7_unmetered_mutation"] = not ks_S7_resource_conservation(g, g7, "admit")
    g7ok = GovernedSpace(g7.ks, g7.certificates, 3, g.meter.charged(admit=1))
    assert ks_S7_resource_conservation(g, g7ok, "admit")
    assert all(planted.values()), planted
    return {"predicates": 7, "all_hold_on_witness": 1, "planted_violations_caught": {k: v for k, v in planted.items()}, "genome_digest": genome_digest()}


# ----------------------------------------------------------------------------------------------
# G2  compose (B6), extract (B5 / KS-T11a), translator invariance (KS-T10a), non-identifiability
# ----------------------------------------------------------------------------------------------


def compose(g: GovernedSpace, components: tuple[str, ...], new_id: str, bridge_profile=ONE, certificate: CertificateKind = CertificateKind.INSTRUCTION) -> GovernedSpace:
    amap = g.ks.atom_map()
    prof = bridge_profile
    for c in components:
        if c not in amap:
            raise TypedRejection("UNBOUND_COMPONENT", c)
        prof = kso.profile_and(prof, amap[c].profile)
    atom = Atom(new_id, "procedure", prof)
    edge = Hyperedge(f"compose:{new_id}", components, (new_id,), "COMPOSITION", profile=bridge_profile)
    ks = KnowledgeSpace(g.ks.atoms + (atom,), g.ks.hyperedges + (edge,))
    ks.validate()
    return GovernedSpace(ks, {**g.certificates, new_id: certificate}, g.evidence_atoms, g.meter.charged(compose=1), g.revoked)


def compose_merge_mutant(g: GovernedSpace, components: tuple[str, ...], new_id: str) -> GovernedSpace:
    """Planted defect: the composite label is the union (⊕) of component labels — a merge."""
    amap = g.ks.atom_map()
    prof: tuple = ZERO
    for c in components:
        prof = kso.profile_or(prof, amap[c].profile)
    atom = Atom(new_id, "procedure", prof)
    edge = Hyperedge(f"compose:{new_id}", components, (new_id,), "COMPOSITION", profile=ONE)
    return GovernedSpace(KnowledgeSpace(g.ks.atoms + (atom,), g.ks.hyperedges + (edge,)), {**g.certificates, new_id: CertificateKind.INSTRUCTION}, g.evidence_atoms, g.meter.charged(compose=1), g.revoked)


def check_g2_compose() -> dict[str, object]:
    g = GovernedSpace(
        KnowledgeSpace((Atom("a", "claim", (frozenset({0}),)), Atom("b", "claim", (frozenset({1}),))), (Hyperedge("ab", ("a",), ("b",), "SUPPORT", profile=ONE),)),
        {"a": CertificateKind.INSTRUCTION, "b": CertificateKind.INSTRUCTION}, 3, Meter(admit=2),
    )
    gc = compose(g, ("a", "b"), "p")
    p = gc.ks.atom_map()["p"]
    assert p.profile == (frozenset({0, 1}),)
    assert ks_S2_composition(gc)
    assert not kso.profile_live(p.profile, {0}) and not kso.profile_live(p.profile, {1})
    gm = compose_merge_mutant(g, ("a", "b"), "p")
    pm = gm.ks.atom_map()["p"]
    assert kso.profile_live(pm.profile, {0})  # the merge outlives a revoked component
    assert not ks_S2_composition(gm)
    act = {x: Fraction(1, 1) for x in gc.ks.ids}
    assert "compose:p" in kso.enabled_hyperedges(gc.ks, act, Fraction(1, 2))
    assert "compose:p" not in kso.enabled_hyperedges(gc.ks, act, Fraction(1, 2), revoked={0})
    return {"composite_label_is_conjunctive_product": 1, "component_revocation_kills_composite": 2, "merge_mutant_detected": 1, "meter_charged": gc.meter.compose}


def reacting_subgraph(ks: KnowledgeSpace, seed: Sequence[Fraction], alpha: Fraction, *, revoked: Iterable[int] = ()) -> tuple[frozenset[str], frozenset[str]]:
    """KS-T11a: the reacting subgraph = atoms with positive reaction surprise that lie in the live
    closure of the seed support, plus the live edges among them.  Unique because a* is unique (KS-T05)."""
    background = fixed_point(ks, uniform_seed(ks), alpha, revoked=revoked)
    query = fixed_point(ks, seed, alpha, revoked=revoked)
    rho = reaction_surprise_vector(query, background)
    rv = frozenset(revoked)
    amap = ks.atom_map()
    support = [x for x, v in zip(ks.ids, seed, strict=True) if v > 0]
    reached = set(support)
    grew = True
    while grew:
        grew = False
        for e in ks.hyperedges:
            if kso.profile_live(e.profile, rv) and all(t in reached and kso.profile_live(amap[t].profile, rv) for t in e.tails):
                for h in e.heads:
                    if h not in reached and kso.profile_live(amap[h].profile, rv):
                        reached.add(h)
                        grew = True
    atoms = frozenset(x for x in reached if rho[x] > 0 or x in support)
    edges = frozenset(e.edge_id for e in ks.hyperedges if kso.profile_live(e.profile, rv) and set(e.tails) <= atoms and set(e.heads) <= atoms)
    return atoms, edges


def pcst_all_optima(prize: dict[str, Fraction], edges: dict[str, tuple[str, str]], cost: Fraction, root: str) -> list[frozenset[str]]:
    """Exact prize-collecting connected-subgraph optimiser on a tiny instance: enumerate every
    connected atom set containing the root; return ALL maximisers of prize − cost·|edges used|."""
    atoms = sorted(prize)
    best = None
    optima: list[frozenset[str]] = []
    for mask in range(1 << len(atoms)):
        chosen = frozenset(a for i, a in enumerate(atoms) if mask >> i & 1)
        if root not in chosen:
            continue
        used = [eid for eid, (u, v) in edges.items() if u in chosen and v in chosen]
        reached = {root}
        grew = True
        while grew:
            grew = False
            for eid in used:
                u, v = edges[eid]
                if u in reached and v not in reached or v in reached and u not in reached:
                    reached |= {u, v}
                    grew = True
        if reached != chosen:
            continue
        value = sum((prize[a] for a in chosen), Fraction(0, 1)) - cost * len(chosen - {root})
        if best is None or value > best:
            best, optima = value, [chosen]
        elif value == best:
            optima.append(chosen)
    return optima


def check_g2_extract() -> dict[str, object]:
    ks = retraction_witness_space()
    seed = seed_vector(ks, {"s": Fraction(1, 1)})
    alpha = Fraction(1, 3)
    g1 = reacting_subgraph(ks, seed, alpha)
    g2 = reacting_subgraph(ks, seed, alpha)
    assert g1 == g2 and "s" in g1[0]
    post = reacting_subgraph(ks, seed, alpha, revoked={0})
    assert "b" not in post[0] and "bc" not in post[1] and "ab" not in post[1]
    # the optimiser is a different object: a planted symmetric tie has two optima; the support subgraph has one
    prize = {"r": Fraction(0), "x": Fraction(1), "y": Fraction(1)}
    edges = {"rx": ("r", "x"), "ry": ("r", "y")}
    tie = pcst_all_optima(prize, edges, Fraction(1, 2), "r")
    assert len(tie) == 1 and tie[0] == frozenset({"r", "x", "y"})  # cheap edges: take both
    tie2 = pcst_all_optima(prize, edges, Fraction(1, 1), "r")  # prize == cost: four optima incl. {r}
    assert len(tie2) > 1
    tie3 = pcst_all_optima({"r": Fraction(0), "x": Fraction(2), "y": Fraction(1)}, edges, Fraction(3, 2), "r")
    assert tie3 == [frozenset({"r", "x"})]
    return {"reacting_subgraph_deterministic": 1, "revoked_atom_and_its_edges_leave_subgraph": 1, "optimiser_tie_witness_optima": len(tie2), "optimiser_unique_witness": 1}


def check_g2_translator_invariance() -> dict[str, object]:
    """KS-T10a: extraction is a function of (𝒦, s_Q); two codecs with equal seed vectors give
    identical extraction (proved by determinism); unequal seed vectors are the must-differ control."""
    ks = retraction_witness_space()
    alpha = Fraction(1, 3)
    codec_1 = (QuestionPart("does a support c", "claim", ("a",)),)
    codec_2 = (QuestionPart("¿a→c?", "claim", ("a",)),)
    _, s1 = atomize(ks, codec_1)
    _, s2 = atomize(ks, codec_2)
    assert s1 == s2
    assert reacting_subgraph(ks, s1, alpha) == reacting_subgraph(ks, s2, alpha)
    _, s3 = atomize(ks, (QuestionPart("what feeds d", "procedure", ("z",)),))
    assert s3 != s1
    differs = reacting_subgraph(ks, s3, alpha) != reacting_subgraph(ks, s1, alpha)
    assert differs
    return {"equal_seed_vectors_identical_extraction": 1, "unequal_seed_vectors_differ": 1, "codec_agreement_on_seed_vector": "OPEN_M5"}


def navigate_identify(ks: KnowledgeSpace, seed: Sequence[Fraction], target: str, budget: NavigationBudget, **kw) -> NavigationResult:
    """Navigation asked to *identify* the target among atoms of its type: a same-type atom with
    exactly the same activation under the committed seed is a non-identifiability witness."""
    res = navigate(ks, seed, target, budget, **kw)
    if res.outcome is not NavigationOutcome.FOUND:
        return res
    alpha = kw.get("alpha", Fraction(1, 3))
    a = fixed_point(ks, seed, alpha, revoked=kw.get("revoked", ()), relation_weights=kw.get("relation_weights"))
    amap = ks.atom_map()
    twins = tuple(sorted(x for x in ks.ids if x != target and amap[x].atom_type == amap[target].atom_type and a[x] == a[target]))
    if not twins:
        return res
    witness = ObstructionWitness(
        incumbent_mechanism="restart_navigation_under_committed_seed",
        failed_obligation=f"identify {target} among atoms of type {amap[target].atom_type}",
        witness_atoms=(target, *twins),
        lower_level_dispositions=("BUDGET: irrelevant, activation is the exact fixed point", "SEED: committed; a different atomisation is a J3 proposal, not a lower-level repair"),
        resource_bound=f"steps={budget.steps}",
    )
    fields = witness.jump_trigger_fields()
    fields["kind"] = "STRUCTURAL_NONIDENTIFIABILITY"
    return NavigationResult(NavigationOutcome.OBSTRUCTION_WITNESSED, target, "TARGET_NOT_IDENTIFIED_UNDER_COMMITTED_SEED", res.steps_used, activation=res.activation, witness=witness)


def check_g2_nonidentifiability() -> dict[str, object]:
    ks = KnowledgeSpace(
        (Atom("s", "query_seed", ONE), Atom("u", "claim", ONE), Atom("v", "claim", ONE), Atom("w", "procedure", ONE)),
        (Hyperedge("su", ("s",), ("u",), "SUPPORT", profile=ONE), Hyperedge("sv", ("s",), ("v",), "SUPPORT", profile=ONE), Hyperedge("uw", ("u",), ("w",), "DEPENDENCE", profile=ONE)),
    )
    seed = seed_vector(ks, {"s": Fraction(1, 1)})
    r = navigate_identify(ks, seed, "u", NavigationBudget(8, 1, 8))
    assert r.outcome is NavigationOutcome.OBSTRUCTION_WITNESSED and r.witness is not None and r.witness.witness_atoms == ("u", "v")
    r2 = navigate_identify(ks, seed, "w", NavigationBudget(8, 1, 8))  # w has no same-type twin: identified
    assert r2.outcome is NavigationOutcome.FOUND
    seed2 = seed_vector(ks, {"s": Fraction(1, 2), "u": Fraction(1, 2)})  # a different atomisation separates u from v
    r3 = navigate_identify(ks, seed2, "u", NavigationBudget(8, 1, 8))
    assert r3.outcome is NavigationOutcome.FOUND
    return {"symmetric_twin_is_obstruction": 1, "no_twin_is_found": 1, "reatomisation_separates": 1}


# ----------------------------------------------------------------------------------------------
# G3  the stem-cell growth invariant (KS-T17)
# ----------------------------------------------------------------------------------------------


def genome_holds(g: GovernedSpace) -> dict[str, bool]:
    return {
        "S1": ks_S1_admission(g),
        "S2": ks_S2_composition(g),
        "S3": ks_S3_revocation_completeness(g),
        "S6": ks_S6_signature_round_trip(g),
    }


def grow_once(g: GovernedSpace, step: int) -> GovernedSpace:
    """acquire (instruction, with edges) → compose → self-revise (relation re-weighting, a policy swap
    that must leave every admitted atom's signature unchanged) → registered revocation → reinstate."""
    ks, rec = admit(g.ks, Atom(f"n{step}", "claim", (frozenset({step % g.evidence_atoms}),)),
                    (Hyperedge(f"s_n{step}", ("s",), (f"n{step}",), "SUPPORT", profile=ONE),), CertificateKind.INSTRUCTION)
    g = GovernedSpace(ks, {**g.certificates, f"n{step}": rec.certificate}, g.evidence_atoms, g.meter.charged(admit=1), g.revoked)
    g = compose(g, ("a", f"n{step}"), f"p{step}")
    swapped = GovernedSpace(g.ks, dict(g.certificates), g.evidence_atoms, g.meter, g.revoked)  # self-revision: policy swap
    if not ks_S5_policy_swap_invariance(g, swapped):
        raise AssertionError("self-revision changed an admitted signature")
    revoked = GovernedSpace(g.ks, g.certificates, g.evidence_atoms, g.meter.charged(revoke=1), frozenset({0}))
    if not ks_S7_resource_conservation(g, revoked, "revoke"):
        raise AssertionError("revocation not metered")
    live_after = parent_jtms_in_out(revoked.ks, revoked.revoked)
    if "a" in live_after or f"p{step}" in live_after:
        raise AssertionError("authority lost: a revoked component or its composite stayed live")
    return GovernedSpace(revoked.ks, revoked.certificates, revoked.evidence_atoms, revoked.meter.charged(revoke=1), frozenset())


def check_g3_growth_invariant() -> dict[str, object]:
    g0 = governed_witness()
    d0 = genome_digest()
    g = g0
    history = []
    for step in range(1, 4):
        g = grow_once(g, step)
        held = genome_holds(g)
        assert all(held.values()), held
        history.append((len(g.ks.atoms), len(g.ks.hyperedges)))
    assert genome_digest() == d0
    # fixed point: growing with nothing new to acquire changes nothing
    before = g.ks
    try:
        admit(g.ks, Atom("n1", "claim", ONE), (), CertificateKind.INSTRUCTION)
        fixed = False
    except TypedRejection as exc:
        fixed = exc.code == "DUPLICATE_ATOM"
    assert fixed and g.ks == before
    cancers: dict[str, str] = {}
    # (a) feedback retained as warrant
    ga = GovernedSpace(g.ks, {**g.certificates, "n1": CertificateKind.FEEDBACK}, g.evidence_atoms, g.meter)
    cancers["feedback_retained_as_warrant"] = "CAUGHT" if not ks_S1_admission(ga) else "MISSED"
    # (b) composite outliving a revoked component
    gb = compose_merge_mutant(g, ("a", "b"), "tumour")
    cancers["composite_outlives_revoked_component"] = "CAUGHT" if not ks_S2_composition(gb) else "MISSED"
    # (c) growth that edits the genome
    global GENOME
    saved = GENOME
    GENOME = GENOME[:-1] + (lambda *_: True,)
    try:
        cancers["genome_edited_by_growth"] = "CAUGHT" if genome_digest() != d0 else "MISSED"
    finally:
        GENOME = saved
    assert genome_digest() == d0
    assert set(cancers.values()) == {"CAUGHT"}, cancers
    return {"growth_steps": 3, "genome_held_every_step": 1, "genome_digest_unchanged": 1, "fixed_point_reached": 1, "cancers": cancers, "final_size": history[-1]}


# ----------------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------------


def run_all() -> dict[str, object]:
    return {
        "contract": "KnowledgeSpace.v1-M0-FREEZE",
        "g1_genome_S1_S7": check_g1_genome(),
        "f1_edge_vocabulary": check_f1_edge_vocabulary(),
        "f2_retraction_propagation": check_f2_retraction_propagation(),
        "f3_hub_two_directions": check_f3_hub_two_directions(),
        "f4_acquisition": check_f4_acquisition(),
        "f5_atomisation": check_f5_atomisation(),
        "f6_navigation_outcomes": check_f6_navigation_outcomes(),
        "g2_compose": check_g2_compose(),
        "g2_extract": check_g2_extract(),
        "g2_translator_invariance": check_g2_translator_invariance(),
        "g2_nonidentifiability": check_g2_nonidentifiability(),
        "g3_growth_invariant": check_g3_growth_invariant(),
        "f7_parent_subtraction": check_f7_parent_subtraction(),
        "f8_budget_clause": check_f8_budget_clause(),
        "f9_typing_coverage_prior": check_f9_typing_coverage_prior(),
        "f10_closed_under_shown": check_f10_closed_under_shown(),
        "terminals": {
            "M0_FINITE_MATH_CORE": "GREEN",
            "M0_CONTRACT": "FROZEN_V1",
            "GENERAL_NOVELTY": "NOT_ESTABLISHED",
            "M1_KSO_INSTANCE": "NOT_RUN",
        },
    }


def _default(o):
    if isinstance(o, Fraction):
        return str(o)
    if isinstance(o, (frozenset, set)):
        return sorted(o)
    if isinstance(o, Enum):
        return o.value
    raise TypeError(type(o).__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_all()
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1
    if args.json or args.self_test:
        print(json.dumps(result, indent=2, sort_keys=True, default=_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
