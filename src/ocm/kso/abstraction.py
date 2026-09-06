"""Representation, quotienting and abstraction (contract §9, §11; M1 F).

A representation move is admissible only when **both** hold (contract §9.2):

    navigation lumpability  ∧  warrant/authority measurability.

* ``is_lumpable`` / ``lump`` / ``pushforward`` — Kemeny–Snell lumpability (KS-T07, parent theorem).
* ``warrant_measurable`` — every atom in a block has the same three-valued liveness under every
  registered revocation (the S4 requirement lifted to a partition of atoms).
* ``summarize`` — a summary/macro atom over constituents.  Its warrant is the correspondence
  warrant ⊗ ⊗(exported constituents), so LIVE(summary) ⇒ live support exists below it (F2: no
  authority from abstraction).  Aggregation, majority, similarity or compression never mint warrant.
* ``answer_with_summary`` — a summary answers a query family only when a registered sufficiency
  certificate covers that family; otherwise ``REFINE_REQUIRED`` (F3).
Parents: Kemeny & Snell 1976 (lumpability); ATMS label conjunction; MDL (compression objective is
necessary, never sufficient — contract §11).  KS-T12 (lifecycle-safe consolidation) stays open.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from fractions import Fraction
from typing import Hashable, Iterable, Sequence

from .space import Atom, Hyperedge, KnowledgeSpace, TypedRejection
from .types import Authority, Scope, intersect_scopes, internal_authority, meet_authority
from .warrant import WarrantProfile, meet_all_profiles

Partition = tuple[tuple[int, ...], ...]


def is_lumpable(p: Sequence[Sequence[Fraction]], blocks: Partition) -> bool:
    if any(not block for block in blocks):
        raise ValueError("blocks must partition all states into non-empty blocks")
    universe = sorted(i for block in blocks for i in block)
    if universe != list(range(len(p))) or len(universe) != len(set(universe)):
        raise ValueError("blocks must partition all states")
    for block in blocks:
        for target in blocks:
            vals = {sum((p[i][j] for j in target), Fraction(0, 1)) for i in block}
            if len(vals) > 1:
                return False
    return True


def lump(p: Sequence[Sequence[Fraction]], blocks: Partition) -> list[list[Fraction]]:
    if not is_lumpable(p, blocks):
        raise ValueError("not lumpable")
    return [[sum((p[block[0]][j] for j in target), Fraction(0, 1)) for target in blocks] for block in blocks]


def pushforward(x: Sequence[Fraction], blocks: Partition) -> list[Fraction]:
    return [sum((x[i] for i in block), Fraction(0, 1)) for block in blocks]


def row_vector_step(x: Sequence[Fraction], p: Sequence[Sequence[Fraction]]) -> list[Fraction]:
    return [sum((x[i] * p[i][j] for i in range(len(x))), Fraction(0, 1)) for j in range(len(x))]


def mutant_bad_quotient(p: Sequence[Sequence[Fraction]], blocks: Partition) -> list[list[Fraction]]:
    """Planted: averages rows inside a block whether or not the partition is lumpable."""
    out = []
    for block in blocks:
        row = []
        for target in blocks:
            vals = [sum((p[i][j] for j in target), Fraction(0, 1)) for i in block]
            row.append(sum(vals, Fraction(0, 1)) / len(vals))
        out.append(row)
    return out


# --------------------------------------------------------------------------------------------
# warrant measurability and admissibility of a representation move
# --------------------------------------------------------------------------------------------


def warrant_measurable(ks: KnowledgeSpace, blocks: Iterable[Iterable[str]], registered_revocations: Iterable[frozenset]) -> bool:
    """Every registered revocation R yields identical three-valued liveness within each block."""
    amap = ks.atom_map()
    gammas = list(registered_revocations) or [frozenset()]
    for block in blocks:
        members = list(block)
        for R in gammas:
            sigs = {amap[x].liveness(R) for x in members}
            if len(sigs) > 1:
                return False
    return True


class QuotientVerdict(str, Enum):
    ADMISSIBLE = "ADMISSIBLE"
    NOT_LUMPABLE = "NOT_LUMPABLE"
    NOT_WARRANT_MEASURABLE = "NOT_WARRANT_MEASURABLE"
    NEITHER = "NEITHER"


def quotient_admissible(ks: KnowledgeSpace, p: Sequence[Sequence[Fraction]], blocks: Iterable[Iterable[str]], registered_revocations: Iterable[frozenset]) -> QuotientVerdict:
    # Both predicates must inspect the same partition. The public contract accepts
    # one-shot outer AND inner iterables; consuming either before the warrant
    # check would make that check vacuously true.
    stable_blocks = tuple(tuple(block) for block in blocks)
    index_by_id = {atom_id: i for i, atom_id in enumerate(ks.ids)}
    try:
        idx_blocks: Partition = tuple(tuple(index_by_id[x] for x in block) for block in stable_blocks)
    except KeyError as error:
        # Preserve the ValueError category of the previous tuple.index lookup.
        raise ValueError(f"unknown atom in quotient partition: {error.args[0]!r}") from None
    lumpable = is_lumpable(p, idx_blocks)
    measurable = warrant_measurable(ks, stable_blocks, registered_revocations)
    if lumpable and measurable:
        return QuotientVerdict.ADMISSIBLE
    if lumpable:
        return QuotientVerdict.NOT_WARRANT_MEASURABLE
    if measurable:
        return QuotientVerdict.NOT_LUMPABLE
    return QuotientVerdict.NEITHER


# --------------------------------------------------------------------------------------------
# summary / macro atoms — no authority from abstraction (F2) and REFINE_REQUIRED (F3)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SufficiencyCertificate:
    summary_id: str
    query_family: str
    proof_ref: str


@dataclass(frozen=True)
class SummaryReceipt:
    summary_id: str
    constituents: tuple[str, ...]
    exported: tuple[str, ...]
    warrant: WarrantProfile
    authority: Authority
    scope: Scope


def summarize(
    ks: KnowledgeSpace,
    constituents: Sequence[str],
    summary_id: str,
    *,
    exported: Sequence[str] | None = None,
    correspondence_warrant: WarrantProfile | None = None,
    edge_id: str | None = None,
) -> tuple[KnowledgeSpace, SummaryReceipt]:
    """Λ(summary) = Λ_corr ⊗ ⊗_{x ∈ exported} Λ(x); authority meet; scope intersection.

    ``exported`` defaults to every constituent (the strongest reading: the summary is only as
    warranted as all of its parts).  Aggregation never creates warrant: with every exported part
    DEAD the summary is DEAD; with any exported part UNKNOWN it is at most UNKNOWN (KS-T21)."""
    if summary_id in ks.ids:
        raise TypedRejection("DUPLICATE_ATOM", summary_id)
    if not constituents:
        raise TypedRejection("EMPTY_SUMMARY")
    amap = ks.atom_map()
    for x in constituents:
        if x not in amap:
            raise TypedRejection("UNKNOWN_ATOM", x)
    exp = tuple(exported) if exported is not None else tuple(constituents)
    if not exp or not set(exp) <= set(constituents):
        raise TypedRejection("EXPORTED_NOT_SUBSET_OF_CONSTITUENTS", summary_id)
    corr = correspondence_warrant or WarrantProfile.one()
    warrant = meet_all_profiles([corr, *(amap[x].warrant for x in exp)])
    authority = internal_authority([amap[x].authority for x in constituents])  # MEG-04
    scope = intersect_scopes([amap[x].scope for x in constituents])
    atom = Atom(summary_id, "summary", warrant, authority, scope, meta=(("constituents", tuple(constituents)), ("exported", exp)))
    edge = Hyperedge(edge_id or f"summarize:{summary_id}", tuple(constituents), (summary_id,), "REPRESENTATION_TRANSPORT", warrant=corr, authority=authority, scope=scope)
    return ks.with_atoms(atom).with_edges(edge), SummaryReceipt(summary_id, tuple(constituents), exp, warrant, authority, scope)


def mutant_summary_majority(ks: KnowledgeSpace, constituents: Sequence[str], summary_id: str) -> KnowledgeSpace:
    """Planted: summary is LIVE when a majority of constituents are live (⊕ over a majority) —
    authority minted by aggregation (F2 violation)."""
    amap = ks.atom_map()
    w = WarrantProfile.zero()
    for x in constituents:
        w = w.join(amap[x].warrant)
    atom = Atom(summary_id, "summary", w)
    return ks.with_atoms(atom).with_edges(Hyperedge(f"summarize:{summary_id}", tuple(constituents), (summary_id,), "REPRESENTATION_TRANSPORT"))


class SummaryAnswer(str, Enum):
    ANSWERED_FROM_SUMMARY = "ANSWERED_FROM_SUMMARY"
    REFINE_REQUIRED = "REFINE_REQUIRED"
    SUMMARY_NOT_LIVE = "SUMMARY_NOT_LIVE"


def answer_with_summary(
    ks: KnowledgeSpace,
    summary_id: str,
    query_family: str,
    certificates: Iterable[SufficiencyCertificate],
    *,
    revoked: Iterable[Hashable] = (),
) -> SummaryAnswer:
    """F3: a summary answers a query family only under a registered sufficiency certificate."""
    atom = ks.atom(summary_id)
    if not atom.is_live(revoked):
        return SummaryAnswer.SUMMARY_NOT_LIVE
    for c in certificates:
        if c.summary_id == summary_id and c.query_family == query_family and c.proof_ref:
            return SummaryAnswer.ANSWERED_FROM_SUMMARY
    return SummaryAnswer.REFINE_REQUIRED


def descend(ks: KnowledgeSpace, summary_id: str) -> tuple[str, ...]:
    """Refinement access: the constituents a summary reconstructs to (provenance map χ)."""
    atom = ks.atom(summary_id)
    meta = dict(atom.meta)
    if "constituents" not in meta:
        raise TypedRejection("NOT_A_SUMMARY", summary_id)
    return tuple(meta["constituents"])


def mdl_delta(size_subgraph: int, size_macro: int, size_map: int, size_exceptions: int) -> int:
    """ΔL = L(G) − [L(m) + L(χ) + L(exceptions)]; positive compression is necessary, never sufficient."""
    return size_subgraph - (size_macro + size_map + size_exceptions)


def strip_summary_support(ks: KnowledgeSpace, summary_id: str, revoked: Iterable[Hashable]) -> frozenset:
    """Helper for the F2 hostile: the evidence that must be revoked to kill every exported part."""
    atom = ks.atom(summary_id)
    exp = dict(atom.meta)["exported"]
    amap = ks.atom_map()
    ev: set = set(revoked)
    for x in exp:
        ev |= amap[x].warrant.evidence
    return frozenset(ev)
