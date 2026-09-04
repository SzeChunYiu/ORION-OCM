"""Acquisition as a typed transaction, composition, and the governed space with its genome.

* ``CertificateKind`` — the acquisition channels.  The inherited six (INSTRUCTION, DEMONSTRATION,
  INTERACTION, EXPERIMENTATION, FEEDBACK, EXACT_CHECKER) plus OBSERVATION and IMPORTED so the M2
  eight-channel evidence registry maps one-to-one.  FEEDBACK ⇒ certified-zero warrant (KS-T18).
* ``admit`` — the transaction of contract §27: fresh id; edges > 0 or quarantine; registered
  relation types; reachable by navigation; certificate decides the label; scope non-empty.
* ``compose`` — Λ = P_b ⊗ ⊗Λ(x_i), A = A_b ∧ ⋀A_i, S = S_b ∩ ⋂S_i (KS-T20; contract §3).
* ``GovernedSpace`` + ``KS-S1…S7`` — the genome predicates and the stem-cell growth loop (KS-T17).
Parents: proof-carrying code (Necula 1997), ATMS premises vs assumptions, PCC/PCC-style admission.
"""
from __future__ import annotations

import hashlib
import inspect
from dataclasses import dataclass, field, replace
from enum import Enum
from fractions import Fraction
from typing import Hashable, Iterable, Sequence

from .navigation import fixed_point, ungated_closure
from .resources import Meter, ResourceVector
from .space import Atom, Hyperedge, KnowledgeSpace, TypedRejection
from .types import Authority, Scope, intersect_scopes, meet_authority
from .warrant import Liveness, WarrantProfile, meet_all_profiles


class CertificateKind(str, Enum):
    INSTRUCTION = "INSTRUCTION"
    DEMONSTRATION = "DEMONSTRATION"
    OBSERVATION = "OBSERVATION"
    INTERACTION = "INTERACTION"
    EXPERIMENTATION = "EXPERIMENTATION"
    FEEDBACK = "FEEDBACK"
    EXACT_CHECKER = "EXACT_CHECKER"
    IMPORTED = "IMPORTED"


WARRANTING_KINDS = frozenset(k for k in CertificateKind if k is not CertificateKind.FEEDBACK)
EXACT_ADMISSION_MAX_ATOMS = 200  # above this the admission reachability check uses the sparse solver (KS-T32)
INHERITED_KINDS = frozenset(
    {
        CertificateKind.INSTRUCTION,
        CertificateKind.DEMONSTRATION,
        CertificateKind.INTERACTION,
        CertificateKind.EXPERIMENTATION,
        CertificateKind.FEEDBACK,
        CertificateKind.EXACT_CHECKER,
    }
)


@dataclass(frozen=True, slots=True)
class AdmissionReceipt:
    atom_id: str
    certificate: CertificateKind
    warranted: bool
    edges_added: int
    quarantined: bool
    reachable_by_navigation: bool
    resources: ResourceVector = field(default_factory=ResourceVector)


def semantically_connected(ks: KnowledgeSpace, atom_id: str, revoked: Iterable[Hashable] = ()) -> bool:
    """KS-T08: a live, non-quarantined atom must touch a live typed relation with a live peer."""
    amap = ks.atom_map()
    atom = amap[atom_id]
    if atom.quarantined:
        return True
    rv = frozenset(revoked)
    if not atom.is_live(rv):
        return True
    for e in ks.hyperedges:
        if atom_id not in e.incident or not e.warrant.is_live(rv):
            continue
        peers = e.incident - {atom_id}
        if any(amap[p].is_live(rv) for p in peers):
            return True
    return False


def admit(
    ks: KnowledgeSpace,
    atom: Atom,
    edges: tuple[Hyperedge, ...],
    certificate: CertificateKind | str,
    *,
    alpha: Fraction = Fraction(1, 2),
    revoked: Iterable[Hashable] = (),
) -> tuple[KnowledgeSpace, AdmissionReceipt]:
    certificate = CertificateKind(certificate)
    if atom.atom_id in ks.ids:
        raise TypedRejection("DUPLICATE_ATOM", atom.atom_id)
    if atom.scope.is_empty:
        raise TypedRejection("SCOPE_EMPTY", atom.atom_id)
    if certificate is CertificateKind.FEEDBACK:
        atom = replace(atom, warrant=WarrantProfile.zero())  # unwarranted by construction (KS-T18)
        warranted = False
    else:
        if atom.warrant.is_zero:
            raise TypedRejection("WARRANTING_CHANNEL_WITHOUT_WARRANT", certificate.value)
        warranted = True
    if not edges and not atom.quarantined:
        raise TypedRejection("ISOLATED_ATOM_REJECTED", atom.atom_id)
    for e in edges:
        if atom.atom_id not in e.incident:
            raise TypedRejection("EDGE_NOT_INCIDENT_TO_NEW_ATOM", e.edge_id)
        if e.relation_type not in ks.registry.relation_types:
            raise TypedRejection("UNREGISTERED_RELATION_TYPE", e.relation_type)
    if atom.atom_type not in ks.registry.atom_types:
        raise TypedRejection("UNREGISTERED_ATOM_TYPE", atom.atom_type)
    # KS-S2 at admission: a COMPOSITION edge whose head is the new atom must carry the composite
    # warrant (bridge ⊗ tails) — otherwise the new atom would mint warrant the composition denies.
    amap = ks.atom_map()
    for e in edges:
        if e.relation_type == "COMPOSITION" and atom.atom_id in e.heads and warranted:
            expected = meet_all_profiles([e.warrant, *(amap[t].warrant for t in e.tails if t in amap)])
            if expected != atom.warrant:
                raise TypedRejection("COMPOSITION_WARRANT_MISMATCH", f"{e.edge_id}: head must carry bridge ⊗ tails")
    new = ks.with_atoms(atom).with_edges(*edges)
    reachable = True
    if not atom.quarantined:
        if not semantically_connected(new, atom.atom_id, revoked):
            raise TypedRejection("ISOLATED_ATOM_REJECTED", atom.atom_id)
        if atom.atom_id not in ungated_closure(new, ks.ids):
            raise TypedRejection("UNREACHABLE_BY_NAVIGATION", atom.atom_id)
        if warranted:
            seed = [Fraction(1, len(ks.ids)) if x in ks.ids else Fraction(0, 1) for x in new.ids]
            if len(new.ids) <= EXACT_ADMISSION_MAX_ATOMS:
                act = fixed_point(new, seed, alpha, revoked=revoked)
                reachable = act[atom.atom_id] > 0
            else:  # scale path: sparse float iteration (KS-T32); positivity is what is asked, not the value
                from .navigation_sparse import sparse_activation

                act_f, _, _ = sparse_activation(new, seed, float(alpha), revoked=revoked, tol=1e-12)
                reachable = act_f[atom.atom_id] > 0.0
            if not reachable:
                raise TypedRejection("UNREACHABLE_BY_NAVIGATION", atom.atom_id)
    res = ResourceVector(object_count=1, relation_count=len(edges), update_work=1 + len(edges), navigation_work=len(new.ids) ** 2)
    return new, AdmissionReceipt(atom.atom_id, certificate, warranted, len(edges), atom.quarantined, reachable, res)


# --------------------------------------------------------------------------------------------
# composition (KS-T20; contract §3 composition law)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CompositionReceipt:
    head_id: str
    edge_id: str
    warrant: WarrantProfile
    authority: Authority
    scope: Scope
    resources: ResourceVector


def compose(
    ks: KnowledgeSpace,
    tails: Sequence[str],
    head_id: str,
    *,
    head_type: str = "procedure",
    bridge_warrant: WarrantProfile | None = None,
    bridge_authority: Authority | None = None,
    bridge_scope: Scope | None = None,
    edge_id: str | None = None,
    executable_ref: str | None = None,
) -> tuple[KnowledgeSpace, CompositionReceipt]:
    if head_id in ks.ids:
        raise TypedRejection("DUPLICATE_ATOM", head_id)
    if not tails:
        raise TypedRejection("EMPTY_COMPOSITION")
    amap = ks.atom_map()
    for t in tails:
        if t not in amap:
            raise TypedRejection("UNKNOWN_ATOM", t)
    bridge_warrant = bridge_warrant or WarrantProfile.one()
    warrant = meet_all_profiles([bridge_warrant, *(amap[t].warrant for t in tails)])
    authorities = [amap[t].authority for t in tails] + ([bridge_authority] if bridge_authority is not None else [])
    authority = meet_authority(authorities)
    scope = intersect_scopes([amap[t].scope for t in tails] + ([bridge_scope] if bridge_scope is not None else []))
    if scope.is_empty:
        raise TypedRejection("SCOPE_EMPTY", head_id)
    eid = edge_id or f"compose:{head_id}"
    head = Atom(head_id, head_type, warrant, authority, scope)
    edge = Hyperedge(eid, tuple(tails), (head_id,), "COMPOSITION", warrant=bridge_warrant, authority=authority, scope=scope, executable_ref=executable_ref)
    new = ks.with_atoms(head).with_edges(edge)
    res = ResourceVector(object_count=1, relation_count=1, composition_work=len(tails), warrant_size=len(warrant.lower) + len(warrant.upper))
    return new, CompositionReceipt(head_id, eid, warrant, authority, scope, res)


def mutant_compose_merge(ks: KnowledgeSpace, tails: Sequence[str], head_id: str) -> KnowledgeSpace:
    """Planted: composite warrant as ⊕ (alternative) instead of ⊗ (KS-T20 mutant)."""
    amap = ks.atom_map()
    w = WarrantProfile.zero()
    for t in tails:
        w = w.join(amap[t].warrant)
    head = Atom(head_id, "procedure", w)
    return ks.with_atoms(head).with_edges(Hyperedge(f"compose:{head_id}", tuple(tails), (head_id,), "COMPOSITION"))


def mutant_compose_drop_bridge(ks: KnowledgeSpace, tails: Sequence[str], head_id: str, bridge_warrant: WarrantProfile) -> KnowledgeSpace:
    """Planted: ignores the bridge/operator warrant."""
    amap = ks.atom_map()
    w = meet_all_profiles(amap[t].warrant for t in tails)
    head = Atom(head_id, "procedure", w)
    return ks.with_atoms(head).with_edges(Hyperedge(f"compose:{head_id}", tuple(tails), (head_id,), "COMPOSITION", warrant=bridge_warrant))


# --------------------------------------------------------------------------------------------
# the governed space and its genome KS-S1…S7 (contract §32)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernedSpace:
    ks: KnowledgeSpace
    certificates: dict[str, CertificateKind] = field(default_factory=dict)
    revoked: frozenset = frozenset()
    meter: Meter = field(default_factory=Meter)
    registered_revocations: tuple[frozenset, ...] = ()   # Γ: the revocation events the space commits to

    @property
    def evidence(self) -> frozenset:
        return self.ks.evidence_universe()


def ks_S1_admission(g: GovernedSpace) -> bool:
    """S1: an atom carries a non-zero warrant only if it entered through a warranting certificate."""
    for a in g.ks.atoms:
        if not a.warrant.is_zero:
            cert = g.certificates.get(a.atom_id)
            if cert is None or CertificateKind(cert) not in WARRANTING_KINDS:
                return False
    return True


def ks_S2_composition(g: GovernedSpace) -> bool:
    """S2: every COMPOSITION head's warrant is bridge ⊗ tails, authority the meet, scope the intersection."""
    amap = g.ks.atom_map()
    for e in g.ks.hyperedges:
        if e.relation_type != "COMPOSITION":
            continue
        expected = meet_all_profiles([e.warrant, *(amap[t].warrant for t in e.tails)])
        for h in e.heads:
            if amap[h].warrant != expected:
                return False
            if not (amap[h].authority <= meet_authority([amap[t].authority for t in e.tails])):
                return False
            if not (amap[h].scope <= intersect_scopes([amap[t].scope for t in e.tails])):
                return False
    return True


def ks_S3_revocation_completeness(g: GovernedSpace, sample: int = 64) -> bool:
    """S3: the live set of the navigation gate equals the live set computed from the warrants
    themselves, for every revocation subset of the (bounded) evidence universe."""
    from itertools import combinations

    from .navigation import navigation_matrix

    ev = sorted(g.evidence, key=repr)
    subsets: list[frozenset] = []
    for r in range(len(ev) + 1):
        for c in combinations(ev, r):
            subsets.append(frozenset(c))
            if len(subsets) >= sample:
                break
        if len(subsets) >= sample:
            break
    ids = g.ks.ids
    for R in subsets:
        m = navigation_matrix(g.ks, revoked=R)
        for i, x in enumerate(ids):
            row_live = any(v > 0 for v in m.rows[i]) or any(m.rows[j][i] > 0 for j in range(len(ids)))
            if row_live and not g.ks.atom_map()[x].is_live(R):
                return False
    return True


def ks_S4_measurability(g: GovernedSpace) -> bool:
    """S4: every registered revocation Γ is a subset of the evidence universe (measurable)."""
    ev = g.evidence
    return all(R <= ev for R in g.registered_revocations)


def ks_S5_liveness_signature_preserved(g: GovernedSpace, previous: GovernedSpace | None) -> bool:
    """S5: growth never changes an already-admitted atom's liveness signature over Γ."""
    if previous is None:
        return True
    prev = previous.ks.atom_map()
    curr = g.ks.atom_map()
    gammas = g.registered_revocations or (frozenset(),)
    for x, a in prev.items():
        if x not in curr:
            return False
        for R in gammas:
            if a.liveness(R) is not curr[x].liveness(R):
                return False
    return True


def ks_S6_canonical_form(g: GovernedSpace) -> bool:
    """S6: every warrant is a canonical antichain interval (lower ≤ upper), no duplicates."""
    from .warrant import is_antichain, leq

    for a in g.ks.atoms:
        if not (is_antichain(a.warrant.lower) and is_antichain(a.warrant.upper) and leq(a.warrant.lower, a.warrant.upper)):
            return False
    for e in g.ks.hyperedges:
        if not (is_antichain(e.warrant.lower) and is_antichain(e.warrant.upper)):
            return False
    return True


def ks_S7_resource_conservation(g: GovernedSpace, expected_events: int) -> bool:
    """S7: every mutation was metered — the meter's event count equals the mutations performed."""
    return g.meter.events == expected_events and g.meter.total.object_count >= 0


GENOME = (ks_S1_admission, ks_S2_composition, ks_S3_revocation_completeness, ks_S4_measurability, ks_S5_liveness_signature_preserved, ks_S6_canonical_form, ks_S7_resource_conservation)


def genome_digest() -> str:
    """The hash of the predicates' source — a changed digest is a cancer, not a revision."""
    src = "\n".join(inspect.getsource(f) for f in GENOME)
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


def check_genome(g: GovernedSpace, previous: GovernedSpace | None, expected_events: int) -> dict[str, bool]:
    return {
        "KS-S1": ks_S1_admission(g),
        "KS-S2": ks_S2_composition(g),
        "KS-S3": ks_S3_revocation_completeness(g),
        "KS-S4": ks_S4_measurability(g),
        "KS-S5": ks_S5_liveness_signature_preserved(g, previous),
        "KS-S6": ks_S6_canonical_form(g),
        "KS-S7": ks_S7_resource_conservation(g, expected_events),
    }


def governed_admit(g: GovernedSpace, atom: Atom, edges: tuple[Hyperedge, ...], certificate: CertificateKind) -> tuple[GovernedSpace, AdmissionReceipt]:
    new_ks, receipt = admit(g.ks, atom, edges, certificate, revoked=g.revoked)
    certs = dict(g.certificates)
    certs[atom.atom_id] = certificate
    meter = Meter(g.meter.total, g.meter.events).charge(receipt.resources)
    return replace(g, ks=new_ks, certificates=certs, meter=meter), receipt


def governed_compose(g: GovernedSpace, tails: Sequence[str], head_id: str, **kw) -> tuple[GovernedSpace, CompositionReceipt]:
    new_ks, receipt = compose(g.ks, tails, head_id, **kw)
    certs = dict(g.certificates)
    certs[head_id] = CertificateKind.EXACT_CHECKER if all(CertificateKind(certs.get(t, CertificateKind.FEEDBACK)) in WARRANTING_KINDS for t in tails) else CertificateKind.FEEDBACK
    meter = Meter(g.meter.total, g.meter.events).charge(receipt.resources)
    return replace(g, ks=new_ks, certificates=certs, meter=meter), receipt


def governed_revoke(g: GovernedSpace, evidence: Iterable[Hashable]) -> GovernedSpace:
    rv = g.revoked | frozenset(evidence)
    meter = Meter(g.meter.total, g.meter.events).charge(ResourceVector(update_work=1))
    return replace(g, revoked=rv, meter=meter)


def governed_reinstate(g: GovernedSpace, evidence: Iterable[Hashable]) -> GovernedSpace:
    rv = g.revoked - frozenset(evidence)
    meter = Meter(g.meter.total, g.meter.events).charge(ResourceVector(update_work=1))
    return replace(g, revoked=rv, meter=meter)


def mutant_feedback_retains_warrant(g: GovernedSpace, atom: Atom, edges: tuple[Hyperedge, ...]) -> GovernedSpace:
    """Cancer 1: a FEEDBACK-admitted atom keeps its supplied warrant (KS-S1 / KS-T18 violation)."""
    new_ks = g.ks.with_atoms(atom).with_edges(*edges)
    certs = dict(g.certificates)
    certs[atom.atom_id] = CertificateKind.FEEDBACK
    return replace(g, ks=new_ks, certificates=certs)


def mutant_unmetered_mutation(g: GovernedSpace, atom: Atom, edges: tuple[Hyperedge, ...]) -> GovernedSpace:
    """Cancer 3: a mutation that skips the meter (KS-S7 violation)."""
    new_ks = g.ks.with_atoms(atom).with_edges(*edges)
    certs = dict(g.certificates)
    certs[atom.atom_id] = CertificateKind.INSTRUCTION
    return replace(g, ks=new_ks, certificates=certs)


def liveness_signature(atom: Atom, gammas: Iterable[frozenset]) -> tuple[Liveness, ...]:
    return tuple(atom.liveness(R) for R in gammas)
