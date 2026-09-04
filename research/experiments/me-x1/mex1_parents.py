#!/usr/bin/env python3
"""ME-X1 parent baselines (frozen with design V1, S4).

Each parent is implemented against its native semantics and carries its own
known-answer tests (`fidelity_selftests()`), which must pass before the parent
is used inside any arm (ME_X1_PARENT_FIDELITY_RECEIPT_V1.md).

Vendored from ME-X4 (`research/experiments/me-x4/mex4_parents.py`, frozen
sha256 484213b4...; byte-identical class bodies):
  JTMS            Doyle 1979 / Forbus & de Kleer 1993 ch. 7 (support engine of B4/B5)
  AssuranceCase   GSN change-impact analysis (B3)
  ProvenanceOnly  orion_v2.provenance revocation descendants (B2)

New parents for the cross-transition conditions (each a faithful local parent):
  ContractBinding        design-by-contract / assume-guarantee binding of a result to a
                         registered problem identity and decision criterion
  RefinementFidelity     formal refinement: proved statement vs intended specification,
                         separated from proof-checker validity
  IndependenceWitness    orion_v2.evidence.assess_evidence_dependence (dependence-aware synthesis)
  TransportLicense       typed transport licence over orion_v2.structural.RelationType rank
  MetrologyComparability orion_v2.comparability.ComparabilityCertificate (measurement comparability)
  EvaluatorCoverage      evaluator/verifier coverage contract with registered alternatives
  AtlasGluing            orion_v2.epistemic_atlas.assess_atlas_gluing (local-to-global)
  AuthorityLattice       governance ceiling comparison on an ordered authority lattice
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from orion_v2.comparability import Anchor, ComparabilityCertificate, ComparabilityStatus
from orion_v2.epistemic_atlas import GluingStatus, LocalEpistemicChart, OverlapAssessment, assess_atlas_gluing
from orion_v2.evidence import DependenceEdge, DependenceKind, EvidenceUnit, assess_evidence_dependence
from orion_v2.provenance import InheritanceRelation, ProvenanceEdge, ProvenanceNode, ReticulateProvenance
from orion_v2.structural import RelationType

IN = "IN"
OUT = "OUT"
ENABLED_ASSUMPTION = "ENABLED_ASSUMPTION"

RELATION_RANK: dict[str, int] = {"ISOMORPHIC": 5, "BEHAVIORALLY_EQUIVALENT": 4, "PREDICTIVELY_EQUIVALENT": 3, "DECISION_DOMINATES": 2, "APPROXIMATELY_EQUIVALENT": 1, "INCOMPARABLE": 0, "DISTINGUISHED_BY": 0}


# =============================================================================
# JTMS (vendored from ME-X4)
# =============================================================================

@dataclass
class Justification:
    just_id: int
    informant: str
    consequence: str
    inlist: tuple[str, ...]
    outlist: tuple[str, ...]


@dataclass
class JNode:
    node_id: str
    is_assumption: bool = False
    is_contradiction: bool = False
    label: str = OUT
    support: object = None
    justs: list[Justification] = field(default_factory=list)
    consequences: list[Justification] = field(default_factory=list)


class JTMS:
    """Justification-based TMS with well-founded support."""

    def __init__(self) -> None:
        self.nodes: dict[str, JNode] = {}
        self.justs: list[Justification] = []
        self.ops = 0
        self._enable_order: dict[str, int] = {}
        self._tick = 0
        self.nogoods: list[frozenset[str]] = []

    def create_node(self, node_id: str, *, assumption: bool = False, contradiction: bool = False) -> JNode:
        if node_id in self.nodes:
            raise ValueError(f"duplicate node {node_id}")
        n = JNode(node_id, assumption, contradiction)
        self.nodes[node_id] = n
        return n

    def justify_node(self, informant: str, consequence: str, inlist: Iterable[str], outlist: Iterable[str] = ()) -> Justification:
        j = Justification(len(self.justs), informant, consequence, tuple(inlist), tuple(outlist))
        self.justs.append(j)
        self.nodes[consequence].justs.append(j)
        for n in (*j.inlist, *j.outlist):
            self.nodes[n].consequences.append(j)
        self._check_justification(j)
        return j

    def is_in(self, node_id: str) -> bool:
        return self.nodes[node_id].label == IN

    def assumptions_of(self, node_id: str) -> frozenset[str]:
        found: set[str] = set(); seen: set[str] = set(); stack = [node_id]
        while stack:
            nid = stack.pop()
            if nid in seen:
                continue
            seen.add(nid)
            n = self.nodes[nid]
            if n.label != IN:
                continue
            if n.support == ENABLED_ASSUMPTION:
                found.add(nid)
            elif isinstance(n.support, Justification):
                stack.extend(n.support.inlist)
        return frozenset(found)

    def _satisfied(self, j: Justification) -> bool:
        self.ops += 1
        return all(self.nodes[n].label == IN for n in j.inlist) and all(self.nodes[n].label == OUT for n in j.outlist)

    def _check_justification(self, j: Justification) -> bool:
        c = self.nodes[j.consequence]
        if c.label == OUT and self._satisfied(j):
            self._make_node_in(j.consequence, j)
            return True
        return False

    def _make_node_in(self, node_id: str, reason) -> None:
        n = self.nodes[node_id]
        n.label = IN; n.support = reason; self.ops += 1
        self._propagate_inness(node_id)

    def _propagate_inness(self, node_id: str) -> None:
        queue = [node_id]
        while queue:
            nid = queue.pop(0)
            for j in list(self.nodes[nid].consequences):
                c = self.nodes[j.consequence]
                if c.label == OUT and self._satisfied(j):
                    c.label = IN; c.support = j; self.ops += 1
                    queue.append(j.consequence)
                    if c.is_contradiction:
                        self._on_contradiction(j.consequence)
        self._retract_unsupported()

    def _make_node_out(self, node_id: str) -> None:
        n = self.nodes[node_id]
        n.label = OUT; n.support = None; self.ops += 1

    def _propagate_outness(self, node_id: str) -> list[str]:
        out_queue = [node_id]; i = 0
        while i < len(out_queue):
            nid = out_queue[i]; i += 1
            for j in self.nodes[nid].consequences:
                c = self.nodes[j.consequence]
                if c.support is j:
                    self._make_node_out(j.consequence)
                    out_queue.append(j.consequence)
        return out_queue

    def _find_alternative_support(self, out_queue: list[str]) -> None:
        changed = True
        while changed:
            changed = False
            for nid in list(out_queue):
                n = self.nodes[nid]
                if n.label == IN:
                    continue
                for j in n.justs:
                    if self._satisfied(j):
                        self._make_node_in(nid, j); changed = True
                        break
            for j in self.justs:
                if self.nodes[j.consequence].label == OUT and j.outlist and self._satisfied(j):
                    self._make_node_in(j.consequence, j); changed = True

    def _retract_unsupported(self) -> None:
        changed = True
        while changed:
            changed = False
            for n in list(self.nodes.values()):
                if n.label == IN and isinstance(n.support, Justification) and not self._satisfied(n.support):
                    alt = next((j for j in n.justs if self._satisfied(j)), None)
                    if alt is not None:
                        n.support = alt; self.ops += 1
                        continue
                    self._make_node_out(n.node_id)
                    q = self._propagate_outness(n.node_id)
                    self._find_alternative_support(q)
                    changed = True

    def enable_assumption(self, node_id: str) -> None:
        n = self.nodes[node_id]
        if not n.is_assumption:
            raise ValueError(f"{node_id} is not an assumption")
        if n.label == IN:
            return
        self._tick += 1; self._enable_order[node_id] = self._tick
        n.label = IN; n.support = ENABLED_ASSUMPTION; self.ops += 1
        self._propagate_inness(node_id)

    def retract_assumption(self, node_id: str) -> None:
        n = self.nodes[node_id]
        if n.support != ENABLED_ASSUMPTION:
            return
        self._make_node_out(node_id)
        q = self._propagate_outness(node_id)
        self._find_alternative_support(q)

    def _on_contradiction(self, node_id: str) -> None:
        nogood = self.assumptions_of(node_id)
        if not nogood:
            return
        self.nogoods.append(nogood)
        culprit = max(nogood, key=lambda a: self._enable_order.get(a, -1))
        self.retract_assumption(culprit)


# =============================================================================
# Assurance-case change impact (GSN-style; vendored from ME-X4)
# =============================================================================

class AssuranceCase:
    def __init__(self) -> None:
        self.kind: dict[str, str] = {}
        self.parents: dict[str, set[str]] = {}
        self.ops = 0

    def add(self, element_id: str, kind: str) -> None:
        self.kind[element_id] = kind; self.parents.setdefault(element_id, set())

    def supported_by(self, parent: str, child: str) -> None:
        self.parents.setdefault(child, set()).add(parent)

    def in_context_of(self, element: str, context: str) -> None:
        self.parents.setdefault(context, set()).add(element)

    def change_impact(self, changed: Iterable[str]) -> tuple[frozenset[str], frozenset[str]]:
        challenged = frozenset(changed)
        suspect: set[str] = set(); stack = list(challenged)
        while stack:
            e = stack.pop(); self.ops += 1
            for p in self.parents.get(e, ()):
                if p not in suspect:
                    suspect.add(p); stack.append(p)
        return challenged, frozenset(suspect)


# =============================================================================
# Provenance-only invalidation (orion_v2.provenance; vendored from ME-X4)
# =============================================================================

class ProvenanceOnly:
    def __init__(self, nodes: Iterable[tuple[str, str]], edges: Iterable[tuple[str, str, str, str]]) -> None:
        self.graph = ReticulateProvenance(
            nodes=tuple(ProvenanceNode(n, k, "v0") for n, k in nodes),
            edges=tuple(ProvenanceEdge(p, c, InheritanceRelation(r), comp) for p, c, r, comp in edges),
        )
        self.ops = 0

    def affected(self, revoked_roots: Iterable[str]) -> frozenset[str]:
        out: set[str] = set()
        for r in revoked_roots:
            self.ops += 1
            out.update(self.graph.affected_by_revocation(r))
        return frozenset(out)


# =============================================================================
# New parents (cross-transition conditions, each locally faithful)
# =============================================================================

VALID, INVALID, UNKNOWN = "VALID", "INVALID", "UNKNOWN"


class ContractBinding:
    """Design-by-contract binding: a result satisfies the contract of a
    registered problem identity only if it is bound to that identity and the
    decision criterion it was produced under is the registered one (or a
    registered equivalent)."""

    def __init__(self) -> None:
        self.ops = 0

    def identity(self, bound_claim_id: str, target_claim_id: str, *, recoverable: bool = True) -> str:
        self.ops += 1
        if not recoverable:
            return UNKNOWN
        return VALID if bound_claim_id == target_claim_id else INVALID

    def criterion(self, registered: str, required: str, equivalence: dict[str, str]) -> str:
        self.ops += 1
        if registered == required:
            return VALID
        e = equivalence.get(f"{registered}->{required}", "")
        return VALID if e == "EQUIVALENT" else UNKNOWN if e == "CANNOT_CHECK" else INVALID


class RefinementFidelity:
    """Formal refinement check: the proved statement must refine (be faithful
    to) the intended specification; proof-checker validity is a separate
    verdict and never substitutes for fidelity."""

    def __init__(self) -> None:
        self.ops = 0

    def fidelity(self, proved: str, intended: str, table: dict[str, str]) -> str:
        self.ops += 1
        if proved == intended:
            return VALID
        f = table.get(f"{proved}->{intended}", "")
        return VALID if f == "FAITHFUL" else INVALID if f == "UNFAITHFUL" else UNKNOWN

    def checker(self, status: str) -> str:
        self.ops += 1
        return INVALID if status == "INVALID" else UNKNOWN if status == "UNKNOWN" else VALID


class IndependenceWitness:
    """Dependence-aware evidence synthesis through orion_v2.evidence."""

    def __init__(self) -> None:
        self.ops = 0

    def status(self, claim_id: str, units: Iterable[tuple[str, str]], confirmed: Iterable[tuple[str, str, str]], suspected: Iterable[tuple[str, str, str]], k: int) -> str | None:
        if k <= 0:
            return None
        us = tuple(EvidenceUnit(e, claim_id, s, "registered", supports=True) for e, s in units)
        if not us:
            return None
        ids = {u.evidence_id for u in us}
        def edges(pairs):
            return tuple(DependenceEdge(a, b, DependenceKind(kd), ("registered",)) for a, b, kd in pairs if a in ids and b in ids)
        self.ops += 1
        c = assess_evidence_dependence(us, edges(confirmed)).conservative_independent_support_count
        cs = assess_evidence_dependence(us, edges(list(confirmed) + list(suspected))).conservative_independent_support_count
        return INVALID if c < k else UNKNOWN if cs < k else VALID


class TransportLicense:
    """Typed transport licence: reuse of a donor result in a target context is
    licensed iff the registered relation is at least as strong as the
    relation the consumer requires (orion_v2.structural.RelationType)."""

    def __init__(self) -> None:
        self.ops = 0

    def license(self, relation_type: str | None, required: str) -> str:
        self.ops += 1
        if relation_type is None:
            return INVALID
        rt = RelationType(relation_type)
        if rt is RelationType.CANNOT_CHECK:
            return UNKNOWN
        req = RelationType(required or "APPROXIMATELY_EQUIVALENT")
        return VALID if RELATION_RANK[rt.value] >= RELATION_RANK[req.value] else INVALID


class MetrologyComparability:
    """Measurement comparability across epochs via orion_v2.comparability."""

    def __init__(self) -> None:
        self.ops = 0

    def status(self, registered_status: str) -> str:
        """Map a registered comparability record to a certificate and read its status."""
        self.ops += 1
        if registered_status == "NONCOMPARABLE":
            cert = ComparabilityCertificate("cert", "e0", "e1", "ctx", ("m",), (Anchor("a", "o", "n", ("inv",)),), ("inv",), violated_invariant_ids=("inv",))
        elif registered_status == "CANNOT_CHECK":
            cert = ComparabilityCertificate("cert", "e0", "e1", "ctx", (), (), ("inv",))
        else:
            cert = ComparabilityCertificate("cert", "e0", "e1", "ctx", ("m",), (Anchor("a", "o", "n", ("inv",)),), ("inv",))
        st = cert.status
        return INVALID if st is ComparabilityStatus.NONCOMPARABLE else UNKNOWN if st is ComparabilityStatus.CANNOT_CHECK else VALID


class EvaluatorCoverage:
    """Evaluator/verifier coverage contract: an evaluator certifies a claim
    about failure class f only if f is in its registered coverage and its
    validity contract holds; a blind evaluator is replaceable only when a
    registered valid alternative covers f, otherwise f is uncheckable."""

    def __init__(self) -> None:
        self.ops = 0

    def status(self, evaluator: tuple[str, tuple[str, ...], tuple[str, ...], str], failure_class: str, others: Iterable[tuple[str, tuple[str, ...], str]]) -> str:
        self.ops += 1
        eid, cov, unc, st = evaluator
        if st == "INVALID":
            return INVALID
        if st == "UNDER_REVIEW":
            return UNKNOWN
        if failure_class in cov:
            return VALID
        if failure_class in unc:
            return UNKNOWN
        alt = any(oid != eid and ost == "VALID" and failure_class in ocov for oid, ocov, ost in others)
        return INVALID if alt else UNKNOWN


class AtlasGluing:
    """Local-to-global through orion_v2.epistemic_atlas.assess_atlas_gluing."""

    def __init__(self) -> None:
        self.ops = 0

    def status(self, pieces: Iterable[str], overlaps: Iterable[tuple[str, str, str, bool | None]], witness_id: str) -> GluingStatus:
        self.ops += 1
        charts = tuple(LocalEpistemicChart(p, "ctx", (f"state:{p}",)) for p in pieces)
        ovs = tuple(OverlapAssessment(oid, a, b, comp, (f"w:{oid}",) if comp is not None else ()) for oid, a, b, comp in overlaps)
        return assess_atlas_gluing(charts, ovs, global_section_witness_id=witness_id).status


class AuthorityLattice:
    """Governance ceiling on an ordered lattice NONE < BELIEF < OPERATIONAL < EXTERNAL."""

    def __init__(self) -> None:
        self.ops = 0

    def status(self, ceiling: int, required: int, policy_status: str = "VALID") -> str:
        self.ops += 1
        if policy_status == "UNDER_REVIEW":
            return UNKNOWN
        return VALID if ceiling >= required else INVALID


# =============================================================================
# Native known-answer tests (parent fidelity)
# =============================================================================

def fidelity_selftests() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []

    def rec(parent: str, name: str, passed: bool, detail: str = "") -> None:
        results.append({"parent": parent, "test": name, "passed": bool(passed), "detail": detail})

    # --- JTMS (identical to ME-X4 fidelity tests) -------------------------
    j = JTMS()
    for n in ("A", "B", "C"):
        j.create_node(n, assumption=True)
    for n in ("x", "y", "z"):
        j.create_node(n)
    j.justify_node("jx", "x", ["A"]); j.justify_node("jy", "y", ["B"]); j.justify_node("jz1", "z", ["x", "y"]); j.justify_node("jz2", "z", ["C"])
    j.enable_assumption("A"); j.enable_assumption("B")
    rec("JTMS", "propagation_chain", j.is_in("x") and j.is_in("y") and j.is_in("z"))
    rec("JTMS", "well_founded_assumptions_of", j.assumptions_of("z") == frozenset({"A", "B"}))
    j.retract_assumption("A")
    rec("JTMS", "retraction_propagates_out", (not j.is_in("x")) and (not j.is_in("z")) and j.is_in("y"))
    j.enable_assumption("C")
    rec("JTMS", "alternative_justification_restores", j.is_in("z") and j.assumptions_of("z") == frozenset({"C"}))
    j.enable_assumption("A"); j.retract_assumption("C")
    rec("JTMS", "alternative_support_found_after_retraction", j.is_in("z") and j.assumptions_of("z") == frozenset({"A", "B"}))
    j2 = JTMS(); j2.create_node("q", assumption=True); j2.create_node("p"); j2.justify_node("default", "p", [], ["q"])
    rec("JTMS", "outlist_default_in_when_q_out", j2.is_in("p"))
    j2.enable_assumption("q")
    rec("JTMS", "outlist_default_out_when_q_in", not j2.is_in("p"))
    j3 = JTMS(); j3.create_node("u"); j3.create_node("v"); j3.justify_node("uv", "u", ["v"]); j3.justify_node("vu", "v", ["u"])
    rec("JTMS", "circular_support_not_in", (not j3.is_in("u")) and (not j3.is_in("v")))
    j4 = JTMS(); j4.create_node("A", assumption=True); j4.create_node("B", assumption=True); j4.create_node("bot", contradiction=True)
    j4.justify_node("clash", "bot", ["A", "B"]); j4.enable_assumption("A"); j4.enable_assumption("B")
    rec("JTMS", "ddb_records_nogood_and_retracts_culprit", j4.nogoods == [frozenset({"A", "B"})] and (not j4.is_in("bot")) and j4.is_in("A") and (not j4.is_in("B")))

    # --- Assurance case ---------------------------------------------------
    ac = AssuranceCase()
    for e, k in (("G1", "goal"), ("G2", "goal"), ("S1", "strategy"), ("S2", "strategy"), ("Sn1", "solution"), ("Sn2", "solution"), ("Ctx", "context")):
        ac.add(e, k)
    ac.supported_by("G1", "S1"); ac.supported_by("S1", "Sn1"); ac.supported_by("G2", "S2"); ac.supported_by("S2", "Sn2"); ac.in_context_of("S2", "Ctx")
    _, sus = ac.change_impact(["Sn1"])
    rec("ASSURANCE", "solution_change_marks_own_argument_suspect", sus == frozenset({"S1", "G1"}))
    _, sus = ac.change_impact(["Ctx"])
    rec("ASSURANCE", "context_change_marks_contextualised_argument_suspect", sus == frozenset({"S2", "G2"}))

    # --- Provenance-only --------------------------------------------------
    po = ProvenanceOnly([("src", "source"), ("cal", "calibration"), ("e1", "evidence"), ("e2", "evidence"), ("c", "commitment")], [("src", "e1", "DERIVES", "source"), ("cal", "e2", "CALIBRATES_FROM", "calibration"), ("e1", "c", "DERIVES", "support"), ("e2", "c", "DERIVES", "support")])
    rec("PROVENANCE", "revocation_descendants", po.affected(["src"]) == frozenset({"src", "e1", "c"}) and po.affected(["cal"]) == frozenset({"cal", "e2", "c"}))
    rec("PROVENANCE", "unrelated_root_unaffected", "e2" not in po.affected(["src"]))

    # --- Contract binding -------------------------------------------------
    cb = ContractBinding()
    rec("CONTRACT_BINDING", "matching_identity_satisfies", cb.identity("cA", "cA") == VALID)
    rec("CONTRACT_BINDING", "mismatched_identity_violates_even_with_valid_output", cb.identity("cB", "cA") == INVALID)
    rec("CONTRACT_BINDING", "unrecoverable_binding_cannot_check", cb.identity("cB", "cA", recoverable=False) == UNKNOWN)
    rec("CONTRACT_BINDING", "same_criterion_satisfies", cb.criterion("K1", "K1", {}) == VALID)
    rec("CONTRACT_BINDING", "registered_equivalent_criterion_satisfies", cb.criterion("K1", "K2", {"K1->K2": "EQUIVALENT"}) == VALID)
    rec("CONTRACT_BINDING", "non_equivalent_or_unregistered_criterion_violates", cb.criterion("K1", "K2", {"K1->K2": "NOT_EQUIVALENT"}) == INVALID and cb.criterion("K1", "K2", {}) == INVALID)
    rec("CONTRACT_BINDING", "uncheckable_equivalence_cannot_check", cb.criterion("K1", "K2", {"K1->K2": "CANNOT_CHECK"}) == UNKNOWN)

    # --- Refinement fidelity ---------------------------------------------
    rf = RefinementFidelity()
    rec("REFINEMENT_FIDELITY", "identical_statement_faithful", rf.fidelity("S", "S", {}) == VALID)
    rec("REFINEMENT_FIDELITY", "registered_unfaithful_refinement_violates", rf.fidelity("S_weak", "S", {"S_weak->S": "UNFAITHFUL"}) == INVALID)
    rec("REFINEMENT_FIDELITY", "registered_faithful_refinement_satisfies", rf.fidelity("S2", "S", {"S2->S": "FAITHFUL"}) == VALID)
    rec("REFINEMENT_FIDELITY", "unassessed_refinement_cannot_check", rf.fidelity("S2", "S", {}) == UNKNOWN)
    rec("REFINEMENT_FIDELITY", "checker_verdict_separate_from_fidelity", rf.checker("INVALID") == INVALID and rf.checker("VALID") == VALID and rf.fidelity("S", "S", {}) == VALID)

    # --- Independence witness (orion_v2.evidence) --------------------------
    iw = IndependenceWitness()
    units = [("e1", "s1"), ("e2", "s2"), ("e3", "s3")]
    rec("INDEPENDENCE", "no_edges_three_components", iw.status("c", units, [], [], 2) == VALID)
    rec("INDEPENDENCE", "confirmed_edge_defeats_k3", iw.status("c", units, [("e1", "e2", "SHARED_DATA")], [], 3) == INVALID)
    rec("INDEPENDENCE", "one_edge_leaves_k2_satisfied", iw.status("c", units, [("e1", "e2", "SHARED_DATA")], [], 2) == VALID)
    rec("INDEPENDENCE", "suspected_edge_censors", iw.status("c", units[:2], [], [("e1", "e2", "SHARED_SOURCE")], 2) == UNKNOWN)
    rec("INDEPENDENCE", "no_requirement_no_atom", iw.status("c", units, [("e1", "e2", "SHARED_DATA")], [], 0) is None)

    # --- Transport licence ----------------------------------------------
    tl = TransportLicense()
    rec("TRANSPORT_LICENSE", "isomorphic_licenses_any_requirement", tl.license("ISOMORPHIC", "PREDICTIVELY_EQUIVALENT") == VALID)
    rec("TRANSPORT_LICENSE", "weaker_relation_does_not_license", tl.license("APPROXIMATELY_EQUIVALENT", "PREDICTIVELY_EQUIVALENT") == INVALID)
    rec("TRANSPORT_LICENSE", "equal_strength_licenses", tl.license("DECISION_DOMINATES", "DECISION_DOMINATES") == VALID)
    rec("TRANSPORT_LICENSE", "absent_relation_blocks", tl.license(None, "APPROXIMATELY_EQUIVALENT") == INVALID)
    rec("TRANSPORT_LICENSE", "cannot_check_censors", tl.license("CANNOT_CHECK", "APPROXIMATELY_EQUIVALENT") == UNKNOWN)

    # --- Metrology comparability (orion_v2.comparability) -----------------
    mc = MetrologyComparability()
    rec("COMPARABILITY", "violated_invariant_noncomparable", mc.status("NONCOMPARABLE") == INVALID)
    rec("COMPARABILITY", "missing_mapping_and_anchors_cannot_check", mc.status("CANNOT_CHECK") == UNKNOWN)
    rec("COMPARABILITY", "anchored_invariants_comparable", mc.status("COMPARABLE") == VALID)

    # --- Evaluator coverage ----------------------------------------------
    ec = EvaluatorCoverage()
    rec("EVALUATOR_COVERAGE", "covered_class_passes", ec.status(("evA", ("FC_A",), (), "VALID"), "FC_A", []) == VALID)
    rec("EVALUATOR_COVERAGE", "blind_with_registered_alternative_replaceable", ec.status(("evA", ("FC_B",), (), "VALID"), "FC_A", [("evB", ("FC_A",), "VALID")]) == INVALID)
    rec("EVALUATOR_COVERAGE", "blind_without_alternative_uncheckable", ec.status(("evA", ("FC_B",), (), "VALID"), "FC_A", [("evB", ("FC_B",), "VALID")]) == UNKNOWN)
    rec("EVALUATOR_COVERAGE", "invalidated_contract_replaceable", ec.status(("evA", ("FC_A",), (), "INVALID"), "FC_A", []) == INVALID)
    rec("EVALUATOR_COVERAGE", "uncertain_coverage_censors", ec.status(("evA", ("FC_B",), ("FC_A",), "VALID"), "FC_A", [("evB", ("FC_A",), "VALID")]) == UNKNOWN)

    # --- Atlas gluing (orion_v2.epistemic_atlas) ---------------------------
    ag = AtlasGluing()
    rec("ATLAS", "pairwise_compatibility_is_matching_family_only", ag.status(["p1", "p2"], [("o12", "p1", "p2", True)], "") is GluingStatus.MATCHING_FAMILY_ONLY)
    rec("ATLAS", "separate_witness_glues", ag.status(["p1", "p2"], [("o12", "p1", "p2", True)], "w") is GluingStatus.GLOBAL_SECTION_WITNESSED)
    rec("ATLAS", "incompatible_overlap_obstructs", ag.status(["p1", "p2"], [("o12", "p1", "p2", False)], "w") is GluingStatus.GLOBAL_SECTION_OBSTRUCTED)
    rec("ATLAS", "unresolved_overlap_cannot_check", ag.status(["p1", "p2"], [("o12", "p1", "p2", None)], "w") is GluingStatus.CANNOT_CHECK)

    # --- Authority lattice -----------------------------------------------
    al = AuthorityLattice()
    rec("AUTHORITY", "within_ceiling_allowed", al.status(2, 2) == VALID and al.status(3, 1) == VALID)
    rec("AUTHORITY", "exceeding_ceiling_blocked", al.status(1, 2) == INVALID and al.status(2, 3) == INVALID)
    rec("AUTHORITY", "policy_under_review_cannot_check", al.status(3, 1, "UNDER_REVIEW") == UNKNOWN)
    rec("AUTHORITY", "monotone_in_ceiling", all(al.status(c, r) == (VALID if c >= r else INVALID) for c in range(4) for r in range(4)))
    return results
