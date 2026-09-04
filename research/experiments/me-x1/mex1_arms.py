#!/usr/bin/env python3
"""ME-X1 arms (frozen with design V1, S4 and the H-EXT-3 ladder).

Every arm receives the SAME registered information (World at v0, World at the
request time, the event history, the TransitionRequest, the accepted list).
Arms differ in (i) which parent modules interpret the typed information and
how (typed / lineage-only / untyped / absent), (ii) what crosses the module
boundary into the decision engine (verdict-level vs witness-level; the B5
ladder), and (iii) the engine (direct / calibrated abstention / provenance +
verifier / assurance change-impact / JTMS federation with the registered
precedence glue / orion_v2 transition control).

The registered transition-action semantics (precedence walk with the
singleton rule; SELECTIVELY_REOPEN over the support graph) are registered
information, shared by every arm that uses them. No arm imports mex1_oracle.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from mex1_model import (
    ABSTAIN_AUTHORITY, ACTIONS, AUTHORITY_LEVEL_NAMES, BLOCK_TRANSPORT, CAL_INVALID, CAL_UNDER_REVIEW, CHECKER_INVALID,
    DEFER_CANNOT_CHECK, DEP_CONFIRMED, DEP_SUSPECTED, EVAL_INVALID, IDENTITY_UNRECOVERABLE, PRESERVE, REFORMULATE_PROBLEM,
    REPLACE_OR_CHALLENGE_EVALUATOR, REQUEST_NEW_EVIDENCE, REVALIDATE, SELECTIVELY_REOPEN, SOURCE_DISPUTED,
    SOURCE_RETRACTED, STATUS_INVALID, STATUS_UNKNOWN, STATUS_VALID, UPDATE, Event, TransitionRequest, World,
)
from mex1_parents import (
    JTMS, AssuranceCase, AtlasGluing, AuthorityLattice, ContractBinding, EvaluatorCoverage, IndependenceWitness,
    MetrologyComparability, ProvenanceOnly, RefinementFidelity, TransportLicense,
)
from orion_v2.contracts import Obligation, ObligationStatus, ProblemContract, Terminal
from orion_v2.epistemic_atlas import GluingStatus
from orion_v2.provenance import InheritanceRelation, ProvenanceEdge, ProvenanceNode, ReticulateProvenance
from orion_v2.reopening import Commitment, SupportFamily, selective_reopen

PRESERVED, REOPENED, UNRESOLVED = "PRESERVED", "REOPENED", "UNRESOLVED"
MODULES = ("IDENT", "PROV", "DEP", "TRANS", "EVAL", "ATLAS", "AUTH")
MODULE_DEFAULT_ACTION = {"IDENT": REVALIDATE, "PROV": REVALIDATE, "DEP": REQUEST_NEW_EVIDENCE, "TRANS": BLOCK_TRANSPORT, "EVAL": REPLACE_OR_CHALLENGE_EVALUATOR, "ATLAS": REFORMULATE_PROBLEM, "AUTH": ABSTAIN_AUTHORITY}
ATOM_KINDS = ("identity", "criterion", "spec", "checker", "src", "ident", "cal", "comparability", "support", "ind", "transport", "tr", "evc", "evaluator", "piece", "overlap", "witness", "authority", "nocontra")


@dataclass
class ArmView:
    world_v0: World
    world: World
    events: list[Event]
    request: TransitionRequest
    accepted: tuple[str, ...]


@dataclass
class Decision:
    action: str
    reopened: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {"action": self.action, "reopened": list(self.reopened)}


def _kind(atom: str) -> str:
    return atom.split(":", 1)[0]


# ---- registered structure (slots: atoms with owning module, no status) --------

def support_slots(w: World) -> dict[str, list[tuple[str, str]]]:
    slots: dict[str, list[tuple[str, str]]] = {}
    for fam in sorted(w.families.values(), key=lambda f: f.family_id):
        s: list[tuple[str, str]] = []
        claim = w.claims[fam.claim_id]
        for e in fam.evidence_ids:
            ev = w.evidence[e]
            if not ev.supports:
                continue
            s.append((f"src:{e}", "PROV")); s.append((f"ident:{e}", "PROV"))
            if ev.calibration_id:
                s.append((f"cal:{e}", "PROV"))
            if ev.evaluator_id:
                s.append((f"evc:{e}", "EVAL"))
            if ev.context_id != claim.context_id:
                s.append((f"tr:{fam.family_id}:{e}", "TRANS"))
        if fam.min_independent > 0:
            s.append((f"ind:{fam.family_id}", "DEP"))
        slots[fam.family_id] = s
    return slots


def contra_slot(c: str) -> str:
    return f"nocontra:{c}"


@dataclass
class ReqSlot:
    atom: str
    module: str
    action: str
    piece: str = ""     # derived from the support disposition of this claim


def request_slots(w: World, req: TransitionRequest) -> list[ReqSlot]:
    T = w.claims[req.target_claim_id]
    out: list[ReqSlot] = []
    if req.kind == "ACCEPT_RESULT":
        R = w.results[req.result_id]
        out.append(ReqSlot(f"identity:{R.result_id}", "IDENT", REVALIDATE))
        out.append(ReqSlot(f"criterion:{T.claim_id}", "IDENT", REFORMULATE_PROBLEM))
        if R.proved_spec_id:
            out.append(ReqSlot(f"spec:{R.result_id}", "IDENT", REVALIDATE))
            out.append(ReqSlot(f"checker:{R.result_id}", "IDENT", REQUEST_NEW_EVIDENCE))
        for e in R.basis_evidence_ids:
            out.append(ReqSlot(f"src:{e}", "PROV", REQUEST_NEW_EVIDENCE))
            out.append(ReqSlot(f"ident:{e}", "PROV", REVALIDATE))
            if w.evidence[e].calibration_id:
                out.append(ReqSlot(f"cal:{e}", "PROV", REVALIDATE))
        if R.comparability_status:
            out.append(ReqSlot(f"comparability:{R.result_id}", "PROV", REVALIDATE))
        if R.min_independent > 0:
            out.append(ReqSlot(f"support:{R.result_id}", "DEP", REQUEST_NEW_EVIDENCE))
        if R.context_id != T.context_id:
            out.append(ReqSlot(f"transport:{R.result_id}", "TRANS", BLOCK_TRANSPORT))
        if R.evaluator_id:
            out.append(ReqSlot(f"evaluator:{R.result_id}", "EVAL", REPLACE_OR_CHALLENGE_EVALUATOR))
    elif req.kind == "CLOSE_GLOBAL":
        pieces = tuple(sorted({p for f in w.families_of(T.claim_id) for p in f.prerequisite_ids}))
        for c in pieces:
            out.append(ReqSlot(f"piece:{c}", "ATLAS", REQUEST_NEW_EVIDENCE, piece=c))
        for o in sorted(w.overlaps.values(), key=lambda x: x.overlap_id):
            if o.left_claim_id in pieces and o.right_claim_id in pieces:
                out.append(ReqSlot(f"overlap:{o.overlap_id}", "ATLAS", REFORMULATE_PROBLEM))
        out.append(ReqSlot(f"witness:{T.claim_id}", "ATLAS", REFORMULATE_PROBLEM))
    out.append(ReqSlot("authority", "AUTH", ABSTAIN_AUTHORITY))
    return out


# ---- module status functions --------------------------------------------------
# Each returns {atom_id: status} for the atoms its module owns (support-graph and
# request-level). Missing atoms default to VALID ("no registered defeat").

def _provenance_graph(w: World) -> ReticulateProvenance:
    nodes = [ProvenanceNode(s, "source", "v0") for s in sorted(w.sources)]
    nodes += [ProvenanceNode(c, "calibration", "v0") for c in sorted(w.calibrations)]
    nodes += [ProvenanceNode(e, "evidence", "v0") for e in sorted(w.evidence)]
    edges = []
    for e in w.evidence.values():
        edges.append(ProvenanceEdge(e.source_id, e.evidence_id, InheritanceRelation.DERIVES, "source"))
        if e.calibration_id:
            edges.append(ProvenanceEdge(e.calibration_id, e.evidence_id, InheritanceRelation.CALIBRATES_FROM, "calibration"))
    return ReticulateProvenance(tuple(nodes), tuple(edges))


def prov_typed(v: ArmView, ops: dict, *, measurement: bool = True) -> dict[str, str]:
    """Evidence validity through orion_v2.provenance revocation descendants,
    component-typed (source vs calibration), identity recoverability, and
    comparability through orion_v2.comparability."""
    w = v.world
    g = _provenance_graph(w)
    out: dict[str, str] = {}
    retracted = [s for s, st in w.sources.items() if st == SOURCE_RETRACTED]; disputed = [s for s, st in w.sources.items() if st == SOURCE_DISPUTED]
    bad_cal = [c for c, cal in w.calibrations.items() if cal.status == CAL_INVALID]; rev_cal = [c for c, cal in w.calibrations.items() if cal.status == CAL_UNDER_REVIEW]
    src_inv = set(g.descendants(tuple(retracted), component="source")) if retracted else set()
    src_unk = set(g.descendants(tuple(disputed), component="source")) if disputed else set()
    cal_inv = set(g.descendants(tuple(bad_cal), component="calibration")) if bad_cal else set()
    cal_unk = set(g.descendants(tuple(rev_cal), component="calibration")) if rev_cal else set()
    ops["n"] = ops.get("n", 0) + len(retracted) + len(disputed) + len(bad_cal) + len(rev_cal)
    for e, ev in w.evidence.items():
        out[f"src:{e}"] = STATUS_INVALID if e in src_inv else STATUS_UNKNOWN if e in src_unk else STATUS_VALID
        out[f"ident:{e}"] = STATUS_UNKNOWN if ev.identity_status == IDENTITY_UNRECOVERABLE else STATUS_VALID
        if ev.calibration_id and measurement:
            out[f"cal:{e}"] = STATUS_INVALID if e in cal_inv else STATUS_UNKNOWN if e in cal_unk else STATUS_VALID
    if measurement:
        mc = MetrologyComparability()
        for r in w.results.values():
            if r.comparability_status:
                out[f"comparability:{r.result_id}"] = mc.status(r.comparability_status)
        ops["n"] = ops.get("n", 0) + mc.ops
    for c in w.claims:
        vals = []
        for e in w.negative_evidence_against(c):
            s = out[f"src:{e.evidence_id}"]; k = out.get(f"cal:{e.evidence_id}", STATUS_VALID)
            vals.append(STATUS_INVALID if STATUS_INVALID in (s, k) else STATUS_UNKNOWN if STATUS_UNKNOWN in (s, k) else STATUS_VALID)
        out[contra_slot(c)] = STATUS_INVALID if any(x == STATUS_VALID for x in vals) else STATUS_UNKNOWN if any(x == STATUS_UNKNOWN for x in vals) else STATUS_VALID
    return out


def ident_typed(v: ArmView, ops: dict, *, mode: str) -> dict[str, str]:
    """mode: typed (ContractBinding + RefinementFidelity), lineage (artifact
    lineage only: basis evidence must belong to the target; checker verdict),
    checker_only (ablation: no identity/criterion/spec)."""
    w, req = v.world, v.request
    if req.kind != "ACCEPT_RESULT":
        return {}
    R = w.results[req.result_id]; T = w.claims[req.target_claim_id]
    cb, rf = ContractBinding(), RefinementFidelity()
    out: dict[str, str] = {}
    if mode == "typed":
        out[f"identity:{R.result_id}"] = cb.identity(R.bound_claim_id, T.claim_id, recoverable=R.binding_status != IDENTITY_UNRECOVERABLE)
        out[f"criterion:{T.claim_id}"] = cb.criterion(T.criterion_id, req.decision_criterion_id or T.criterion_id, w.criterion_equivalence)
        if R.proved_spec_id:
            out[f"spec:{R.result_id}"] = rf.fidelity(R.proved_spec_id, T.intended_spec_id, w.spec_fidelity)
    elif mode == "lineage":
        ok = all(w.evidence[e].claim_id == T.claim_id for e in R.basis_evidence_ids) and R.bound_claim_id == T.claim_id
        out[f"identity:{R.result_id}"] = STATUS_VALID if ok else STATUS_INVALID
        ops["n"] = ops.get("n", 0) + 1
    if R.proved_spec_id:
        out[f"checker:{R.result_id}"] = rf.checker(R.checker_status)
    ops["n"] = ops.get("n", 0) + cb.ops + rf.ops
    return out


def dep_typed(v: ArmView, ops: dict) -> dict[str, str]:
    w, req = v.world, v.request
    iw = IndependenceWitness()
    confirmed = [(d.left_id, d.right_id, d.kind) for d in w.dependence if d.status == DEP_CONFIRMED]
    suspected = [(d.left_id, d.right_id, d.kind) for d in w.dependence if d.status == DEP_SUSPECTED]
    out: dict[str, str] = {}
    for fam in w.families.values():
        s = iw.status(fam.claim_id, [(e.evidence_id, e.source_id) for e in w.positive_evidence_of_family(fam)], confirmed, suspected, fam.min_independent)
        if s is not None:
            out[f"ind:{fam.family_id}"] = s
    if req.kind == "ACCEPT_RESULT":
        R = w.results[req.result_id]
        s = iw.status(req.target_claim_id, [(e, w.evidence[e].source_id) for e in R.basis_evidence_ids], confirmed, suspected, R.min_independent)
        if s is not None:
            out[f"support:{R.result_id}"] = s
    ops["n"] = ops.get("n", 0) + iw.ops
    return out


def trans_typed(v: ArmView, ops: dict, *, untyped: bool = False) -> dict[str, str]:
    w, w0, req = v.world, v.world_v0, v.request
    tl = TransportLicense()
    out: dict[str, str] = {}

    def status(src_ctx: str, dst_ctx: str, required: str) -> str:
        key = w.relation_key(src_ctx, dst_ctx)
        rel = w.relations.get(key)
        if untyped:
            before = w0.relations.get(key); ops["n"] = ops.get("n", 0) + 1
            return STATUS_INVALID if (rel is None or before is None or before.relation_type != rel.relation_type) else STATUS_VALID
        return tl.license(rel.relation_type if rel else None, required)
    for fam in w.families.values():
        claim = w.claims[fam.claim_id]
        for e in w.positive_evidence_of_family(fam):
            if e.context_id != claim.context_id:
                out[f"tr:{fam.family_id}:{e.evidence_id}"] = status(e.context_id, claim.context_id, fam.required_relation)
    if req.kind == "ACCEPT_RESULT":
        R = w.results[req.result_id]; T = w.claims[req.target_claim_id]
        if R.context_id != T.context_id:
            out[f"transport:{R.result_id}"] = status(R.context_id, T.context_id, R.required_relation)
    ops["n"] = ops.get("n", 0) + tl.ops
    return out


def eval_typed(v: ArmView, ops: dict, *, mode: str = "typed") -> dict[str, str]:
    """mode: typed (coverage contract with alternatives), status_only (only the
    validity contract; blindness ignored), untyped (coverage changed -> defeated)."""
    w, w0, req = v.world, v.world_v0, v.request
    ec = EvaluatorCoverage()
    others = [(o.evaluator_id, o.coverage, o.status) for o in w.evaluators.values()]

    def status(evaluator_id: str, fc: str) -> str:
        ev = w.evaluators[evaluator_id]
        if mode == "typed":
            return ec.status((ev.evaluator_id, ev.coverage, ev.uncertain, ev.status), fc, others)
        ops["n"] = ops.get("n", 0) + 1
        if mode == "status_only":
            return STATUS_INVALID if ev.status == EVAL_INVALID else STATUS_VALID
        b = w0.evaluators.get(evaluator_id)
        changed = b is None or set(b.coverage) != set(ev.coverage) or set(b.uncertain) != set(ev.uncertain) or b.status != ev.status
        return STATUS_INVALID if changed else STATUS_VALID
    out: dict[str, str] = {}
    for e in w.evidence.values():
        if e.evaluator_id and e.supports:
            out[f"evc:{e.evidence_id}"] = status(e.evaluator_id, w.claims[e.claim_id].failure_class)
    if req.kind == "ACCEPT_RESULT":
        R = w.results[req.result_id]
        if R.evaluator_id:
            out[f"evaluator:{R.result_id}"] = status(R.evaluator_id, w.claims[req.target_claim_id].failure_class)
    ops["n"] = ops.get("n", 0) + ec.ops
    return out


def atlas_typed(v: ArmView, ops: dict, *, matching_only: bool = False) -> dict[str, str]:
    w, req = v.world, v.request
    if req.kind != "CLOSE_GLOBAL":
        return {}
    T = w.claims[req.target_claim_id]
    pieces = tuple(sorted({p for f in w.families_of(T.claim_id) for p in f.prerequisite_ids}))
    ovs = [o for o in sorted(w.overlaps.values(), key=lambda x: x.overlap_id) if o.left_claim_id in pieces and o.right_claim_id in pieces]
    ag = AtlasGluing()
    st = ag.status(pieces, [(o.overlap_id, o.left_claim_id, o.right_claim_id, o.compatible) for o in ovs], "" if matching_only else T.global_witness_id)
    out: dict[str, str] = {}
    for o in ovs:
        out[f"overlap:{o.overlap_id}"] = STATUS_INVALID if o.compatible is False else STATUS_UNKNOWN if o.compatible is None else STATUS_VALID
    if matching_only:
        out[f"witness:{T.claim_id}"] = STATUS_VALID   # pairwise compatibility taken as global
    else:
        out[f"witness:{T.claim_id}"] = STATUS_VALID if st is GluingStatus.GLOBAL_SECTION_WITNESSED else STATUS_UNKNOWN if st in (GluingStatus.MATCHING_FAMILY_ONLY, GluingStatus.CANNOT_CHECK) else STATUS_VALID
    ops["n"] = ops.get("n", 0) + ag.ops
    return out


def auth_typed(v: ArmView, ops: dict) -> dict[str, str]:
    al = AuthorityLattice()
    s = al.status(v.world.authority.ceiling_level, v.request.required_authority_level, v.world.authority.status)
    ops["n"] = ops.get("n", 0) + al.ops
    return {"authority": s}


# ---- structure and engines -------------------------------------------------------

@dataclass
class Structure:
    families: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]]   # fid -> (claim, atoms, prereqs)
    claim_atoms: dict[str, tuple[str, ...]]
    claims: tuple[str, ...]
    request: list[ReqSlot] = field(default_factory=list)

    def key(self) -> tuple:
        return (tuple(sorted((f, c, a, p) for f, (c, a, p) in self.families.items())), tuple(sorted(self.claim_atoms.items())), self.claims)


def build_structure(v: ArmView, spec: "ArmSpec") -> Structure:
    w = v.world
    active = {m for m, mode in spec.modules.items() if mode != "none"}
    dropped = set(spec.dropped_kinds)
    if spec.modules["IDENT"] in ("lineage", "checker_only"):
        dropped |= {"criterion", "spec"}
    if spec.modules["IDENT"] == "checker_only":
        dropped |= {"identity"}
    if spec.modules["PROV"] == "no_measurement":
        dropped |= {"cal", "comparability"}
    slots = support_slots(w)
    keep = lambda a, m: m in active and _kind(a) not in dropped  # noqa: E731
    fams: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {}
    if spec.merge_families:
        for c in w.claims:
            atoms: list[str] = []; prereqs: list[str] = []
            for fam in w.families_of(c):
                atoms += [a for a, m in slots[fam.family_id] if keep(a, m)]; prereqs += list(fam.prerequisite_ids)
            fams[f"{c}.MERGED"] = (c, tuple(atoms), tuple(sorted(set(prereqs))))
    else:
        for fam in w.families.values():
            fams[fam.family_id] = (fam.claim_id, tuple(a for a, m in slots[fam.family_id] if keep(a, m)), tuple(fam.prerequisite_ids))
    req = [s for s in request_slots(w, v.request) if keep(s.atom, s.module)]
    return Structure(fams, {c: (contra_slot(c),) for c in w.claims}, tuple(sorted(w.claims)), req)


def topo(struct: Structure) -> list[str]:
    prereqs = {c: set() for c in struct.claims}
    for cid, _a, p in struct.families.values():
        prereqs[cid].update(p)
    order: list[str] = []; done: set[str] = set()
    while len(order) < len(struct.claims):
        ready = sorted(c for c in struct.claims if c not in done and prereqs[c] <= done)
        if not ready:
            raise ValueError("cycle")
        order += ready; done.update(ready)
    return order


def compress_support_to_verdicts(struct: Structure, slots: dict[str, list[tuple[str, str]]], status: dict[str, str], module: str) -> tuple[Structure, dict[str, str]]:
    """ME-X4 rule: replace module-owned support atoms by one family-anonymous
    per-claim verdict atom attached to every family of the claim."""
    owned = {a for fid in slots for a, m in slots[fid] if m == module}
    new_fams = {}
    per_claim: dict[str, list[str]] = {}
    for fid, (c, _atoms, _p) in struct.families.items():
        per_claim.setdefault(c, []).append(fid)
    new_status = dict(status)   # request-level atoms may share ids with support atoms; only the structure changes
    for c in struct.claims:
        fam_ids = per_claim.get(c, [])
        defeated = []; censored = []
        for fid in fam_ids:
            atoms = [a for a in struct.families[fid][1] if a in owned]
            defeated.append(any(status.get(a, STATUS_VALID) == STATUS_INVALID for a in atoms))
            censored.append(any(status.get(a, STATUS_VALID) == STATUS_UNKNOWN for a in atoms))
        va = f"verdict:{module}:{c}"
        if fam_ids and all(defeated):
            new_status[va] = STATUS_INVALID
        elif fam_ids and all(d or u for d, u in zip(defeated, censored)) and any(censored):
            new_status[va] = STATUS_UNKNOWN
        else:
            new_status[va] = STATUS_VALID
        for fid in fam_ids:
            cc, atoms, prereqs = struct.families[fid]
            new_fams[fid] = (cc, tuple(a for a in atoms if a not in owned) + (va,), prereqs)
    return Structure(new_fams, struct.claim_atoms, struct.claims, struct.request), new_status


def compress_request_to_verdict(struct: Structure, status: dict[str, str], module: str) -> tuple[Structure, dict[str, str]]:
    """Request-level verdict compression: the module's request atoms (piece
    dispositions included, family-anonymous) collapse to one verdict atom at
    the module's position carrying the module default action."""
    owned = [s for s in struct.request if s.module == module]
    if not owned:
        return struct, status
    sts = [status.get(s.atom, STATUS_VALID) for s in owned]
    verdict = STATUS_INVALID if STATUS_INVALID in sts else STATUS_UNKNOWN if STATUS_UNKNOWN in sts else STATUS_VALID
    va = f"verdict:{module}:req"
    new_req: list[ReqSlot] = []
    inserted = False
    for s in struct.request:
        if s.module != module:
            new_req.append(s)
        elif not inserted:
            new_req.append(ReqSlot(va, module, MODULE_DEFAULT_ACTION[module])); inserted = True
    new_status = {a: st for a, st in status.items() if a not in {s.atom for s in owned}}
    new_status[va] = verdict
    return Structure(struct.families, struct.claim_atoms, struct.claims, new_req), new_status


# ---- registered decision semantics (shared glue) ------------------------------

def walk(atoms: list[tuple[str, str, str]], *, three_valued: bool) -> Decision:
    """atoms: ordered (atom_id, status, action). Precedence walk with the singleton rule."""
    if not three_valued:
        atoms = [(a, STATUS_VALID if s == STATUS_UNKNOWN else s, act) for a, s, act in atoms]
    first_invalid = next((i for i, (_a, s, _x) in enumerate(atoms) if s == STATUS_INVALID), None)
    pre = atoms[:first_invalid] if first_invalid is not None else atoms
    action_set = {act for _a, s, act in pre if s == STATUS_UNKNOWN} | {atoms[first_invalid][2] if first_invalid is not None else UPDATE}
    if len(action_set) == 1:
        return Decision(next(iter(action_set)))
    return Decision(DEFER_CANNOT_CHECK)


def decide_defeat(disp: dict[str, str], accepted: tuple[str, ...], *, three_valued: bool) -> Decision:
    if three_valued and any(disp[c] == UNRESOLVED for c in accepted):
        return Decision(DEFER_CANNOT_CHECK)
    r = tuple(c for c in accepted if disp[c] == REOPENED)
    return Decision(SELECTIVELY_REOPEN, r) if r else Decision(PRESERVE)


def piece_status(disp: str) -> str:
    return STATUS_VALID if disp == PRESERVED else STATUS_INVALID if disp == REOPENED else STATUS_UNKNOWN


# ---- support engines -----------------------------------------------------------------

def engine_selective_reopen(struct: Structure, status: dict[str, str], accepted: tuple[str, ...], cost: dict, *, three_valued: bool) -> dict[str, str]:
    """orion_v2.reopening.selective_reopen run optimistic/pessimistic (ME-X4 M engine)."""
    by_claim: dict[str, list[SupportFamily]] = {c: [] for c in struct.claims}
    for fid, (c, atoms, prereqs) in struct.families.items():
        by_claim[c].append(SupportFamily(fid, frozenset(atoms) | frozenset(struct.claim_atoms[c]), frozenset(prereqs)))
    commitments = tuple(Commitment(c, tuple(by_claim[c])) for c in struct.claims if by_claim[c])
    invalid = tuple(sorted(a for a, s in status.items() if s == STATUS_INVALID))
    unknown = tuple(sorted(a for a, s in status.items() if s == STATUS_UNKNOWN)) if three_valued else ()
    opt = selective_reopen(commitments, invalid)
    pes = selective_reopen(commitments, invalid + unknown) if unknown else opt
    n_atoms = sum(len(f.evidence_ids) for c in commitments for f in c.support_families)
    cost["ops"] = cost.get("ops", 0) + (2 if unknown else 1) * (len(commitments) + n_atoms)
    pes_pres = set(pes.preserved_commitment_ids); opt_reop = set(opt.reopened_commitment_ids)
    return {c: PRESERVED if c in pes_pres else REOPENED if c in opt_reop else UNRESOLVED for c in struct.claims}


class JTMSEngine:
    def __init__(self) -> None:
        self.tms: JTMS | None = None
        self.key = None
        self.enabled: set[str] = set()

    def _build(self, struct: Structure) -> None:
        t = JTMS()
        atoms = sorted({a for _c, at, _p in struct.families.values() for a in at} | {a for ats in struct.claim_atoms.values() for a in ats})
        for a in atoms:
            t.create_node(a, assumption=True)
        for c in struct.claims:
            t.create_node(c)
        for fid, (c, at, prereqs) in struct.families.items():
            t.create_node(fid)
            t.justify_node("family", fid, list(at) + list(prereqs))
            t.justify_node("support", c, [fid] + list(struct.claim_atoms[c]))
        self.tms = t; self.key = struct.key(); self.enabled = set()

    def _set(self, want: set[str]) -> None:
        assert self.tms is not None
        for a in sorted(self.enabled - want):
            self.tms.retract_assumption(a)
        for a in sorted(want - self.enabled):
            self.tms.enable_assumption(a)
        self.enabled = set(want)

    def run(self, struct: Structure, status: dict[str, str], cost: dict, *, three_valued: bool) -> dict[str, str]:
        if self.tms is None or self.key != struct.key():
            self._build(struct)
        assert self.tms is not None
        before = self.tms.ops
        atoms = set(self.tms.nodes) - set(struct.claims) - set(struct.families)
        valid = {a for a in atoms if status.get(a, STATUS_VALID) == STATUS_VALID}
        unknown = {a for a in atoms if status.get(a, STATUS_VALID) == STATUS_UNKNOWN}
        self._set(valid | unknown); opt = {c: self.tms.is_in(c) for c in struct.claims}
        if three_valued and unknown:
            self._set(valid); pes = {c: self.tms.is_in(c) for c in struct.claims}
        else:
            pes = opt
        cost["ops"] = cost.get("ops", 0) + (self.tms.ops - before)
        return {c: PRESERVED if pes[c] else REOPENED if not opt[c] else UNRESOLVED for c in struct.claims}


# ---- baseline engines B0-B3 ----------------------------------------------------------

def engine_direct(v: ArmView, cost: dict) -> Decision:
    """B0: the local task system. Local checks pass -> proceed."""
    req, w = v.request, v.world
    cost["ops"] = cost.get("ops", 0) + 1
    if req.kind == "PROPAGATE_DEFEAT":
        return Decision(PRESERVE)
    if req.kind == "ACCEPT_RESULT" and w.results[req.result_id].checker_status == CHECKER_INVALID:
        return Decision(REQUEST_NEW_EVIDENCE)
    return Decision(UPDATE)


def _lineage_flags(v: ArmView) -> int:
    """Untyped count of non-nominal or changed registered statuses in the lineage of the request."""
    w, w0, req = v.world, v.world_v0, v.request
    T = w.claims[req.target_claim_id]
    flags = 0
    ev_ids: set[str] = set()
    for fam in w.families_of(T.claim_id):
        ev_ids.update(fam.evidence_ids)
        for p in fam.prerequisite_ids:
            ev_ids.update(e for f in w.families_of(p) for e in f.evidence_ids)
    if req.kind == "ACCEPT_RESULT":
        R = w.results[req.result_id]; ev_ids.update(R.basis_evidence_ids)
        if R.binding_status == IDENTITY_UNRECOVERABLE or R.comparability_status not in ("", "COMPARABLE") or R.checker_status in ("INVALID", "UNKNOWN"):
            flags += 1
        if R.proved_spec_id and R.proved_spec_id != T.intended_spec_id:
            flags += 1
        if req.decision_criterion_id and req.decision_criterion_id != T.criterion_id:
            flags += 1
        if R.evaluator_id:
            ev = w.evaluators[R.evaluator_id]; b = w0.evaluators.get(R.evaluator_id)
            flags += int(ev.status != "VALID" or b is None or set(b.coverage) != set(ev.coverage) or set(b.uncertain) != set(ev.uncertain))
        if R.context_id != T.context_id:
            key = w.relation_key(R.context_id, T.context_id); rel = w.relations.get(key); b = w0.relations.get(key)
            flags += int(rel is None or b is None or rel.relation_type != b.relation_type)
        flags += int(R.min_independent > 0 and any({d.left_id, d.right_id} <= set(R.basis_evidence_ids) for d in w.dependence))
    if req.kind == "CLOSE_GLOBAL":
        flags += sum(1 for o in w.overlaps.values() if o.compatible is not True)
        flags += int(not T.global_witness_id)
    for e in ev_ids:
        ev = w.evidence[e]
        flags += int(w.sources[ev.source_id] != "VALID") + int(ev.identity_status == IDENTITY_UNRECOVERABLE)
        if ev.calibration_id:
            flags += int(w.calibrations[ev.calibration_id].status != "VALID")
        if ev.evaluator_id:
            x = w.evaluators[ev.evaluator_id]; b = w0.evaluators.get(ev.evaluator_id)
            flags += int(x.status != "VALID" or b is None or set(b.coverage) != set(x.coverage))
        flags += int(any(e in (d.left_id, d.right_id) for d in w.dependence))
    flags += int(T.target_epoch != w0.claims[T.claim_id].target_epoch if T.claim_id in w0.claims else 0)
    flags += int(w.authority.status != "VALID" or w.authority.ceiling_level != w0.authority.ceiling_level)
    return flags


def engine_abstain(v: ArmView, cost: dict) -> Decision:
    """B1: calibrated abstention = B0 plus DEFER whenever any registered status in
    the request's lineage is non-nominal or changed (untyped uncertainty gate)."""
    n = _lineage_flags(v)
    cost["ops"] = cost.get("ops", 0) + n + 1
    if n > 0:
        return Decision(DEFER_CANNOT_CHECK)
    return engine_direct(v, cost)


def engine_provenance_verifier(v: ArmView, cost: dict) -> Decision:
    """B2: typed execution/provenance graph with revocation descendants
    (orion_v2.provenance) plus the local verifier verdict. Two-valued."""
    w, w0, req = v.world, v.world_v0, v.request
    nodes: list[tuple[str, str]] = [(s, "source") for s in w.sources] + [(c, "calibration") for c in w.calibrations]
    nodes += [(f"evaluator:{e}", "evaluator") for e in w.evaluators] + [(f"relation:{k}", "relation") for k in w.relations]
    nodes += [(f"epoch:{c}", "epoch") for c in w.claims] + [(f"authority", "policy")]
    nodes += [(e, "evidence") for e in w.evidence] + [(f, "family") for f in w.families] + [(c, "commitment") for c in w.claims] + [(f"result:{r}", "result") for r in w.results]
    edges: list[tuple[str, str, str, str]] = []
    for e in w.evidence.values():
        edges.append((e.source_id, e.evidence_id, "DERIVES", "source"))
        if e.calibration_id:
            edges.append((e.calibration_id, e.evidence_id, "CALIBRATES_FROM", "calibration"))
        if e.evaluator_id:
            edges.append((f"evaluator:{e.evaluator_id}", e.evidence_id, "EVALUATED_BY", "evaluator"))
    for fam in w.families.values():
        claim = w.claims[fam.claim_id]
        for e in w.positive_evidence_of_family(fam):
            edges.append((e.evidence_id, fam.family_id, "DERIVES", "support"))
            if e.context_id != claim.context_id:
                key = w.relation_key(e.context_id, claim.context_id)
                if key in w.relations:
                    edges.append((f"relation:{key}", fam.family_id, "TRANSLATES", "transport"))
        edges.append((fam.family_id, fam.claim_id, "DERIVES", "support"))
        for p in fam.prerequisite_ids:
            edges.append((p, fam.family_id, "DERIVES", "prerequisite"))
    for r in w.results.values():
        rid = f"result:{r.result_id}"
        for e in r.basis_evidence_ids:
            edges.append((e, rid, "DERIVES", "basis"))
        if r.evaluator_id:
            edges.append((f"evaluator:{r.evaluator_id}", rid, "EVALUATED_BY", "evaluator"))
        edges.append((f"epoch:{r.bound_claim_id}", rid, "REFINES", "epoch"))
        tgt = w.claims[r.bound_claim_id]
        if r.context_id != tgt.context_id:
            key = w.relation_key(r.context_id, tgt.context_id)
            if key in w.relations:
                edges.append((f"relation:{key}", rid, "TRANSLATES", "transport"))
    po = ProvenanceOnly(nodes, edges)
    roots = [s for s, st in w.sources.items() if st == SOURCE_RETRACTED] + [c for c, cal in w.calibrations.items() if cal.status == CAL_INVALID]
    roots += [f"evaluator:{e}" for e, ev in w.evaluators.items() if ev.status == EVAL_INVALID]
    for k, r in w.relations.items():
        b = w0.relations.get(k)
        if b is None or b.relation_type != r.relation_type:
            roots.append(f"relation:{k}")
    for c, cl in w.claims.items():
        if c in w0.claims and w0.claims[c].target_epoch != cl.target_epoch:
            roots.append(f"epoch:{c}")
    affected = po.affected(roots)
    cost["ops"] = cost.get("ops", 0) + po.ops + len(affected)
    T = req.target_claim_id
    if req.kind == "PROPAGATE_DEFEAT":
        r = tuple(c for c in v.accepted if c in affected)
        return Decision(SELECTIVELY_REOPEN, r) if r else Decision(PRESERVE)
    if req.kind == "ACCEPT_RESULT":
        R = w.results[req.result_id]
        if R.checker_status == CHECKER_INVALID:
            return Decision(REQUEST_NEW_EVIDENCE)
        lineage_ok = R.bound_claim_id == T and all(w.evidence[e].claim_id == T for e in R.basis_evidence_ids)
        if not lineage_ok or f"result:{R.result_id}" in affected:
            return Decision(REVALIDATE)
        return Decision(UPDATE)
    pieces = {p for f in w.families_of(T) for p in f.prerequisite_ids}
    return Decision(REVALIDATE) if pieces & affected else Decision(UPDATE)


def engine_assurance(struct: Structure, status: dict[str, str], v: ArmView, cost: dict) -> Decision:
    """B3: GSN change-impact over the registered argument. AND semantics:
    every non-VALID element challenges its argument; a challenged goal is
    re-argued (REVALIDATE) or reopened. Two-valued (challenged = not VALID)."""
    ac = AssuranceCase()
    for c in struct.claims:
        ac.add(c, "goal")
    for fid, (c, at, prereqs) in struct.families.items():
        ac.add(fid, "strategy"); ac.supported_by(c, fid)
        for a in at:
            if a not in ac.kind:
                ac.add(a, "solution" if _kind(a) in ("src", "ident", "cal") else "context")
            (ac.supported_by if ac.kind[a] == "solution" else ac.in_context_of)(fid, a)
        for p in prereqs:
            ac.supported_by(fid, p)
    for c, ats in struct.claim_atoms.items():
        for a in ats:
            if a not in ac.kind:
                ac.add(a, "context")
            ac.in_context_of(c, a)
    ac.add("REQ", "goal"); ac.add("REQ.S", "strategy"); ac.supported_by("REQ", "REQ.S"); ac.supported_by("REQ.S", v.request.target_claim_id)
    for s in struct.request:
        if s.piece:
            ac.supported_by("REQ.S", s.piece); continue
        if s.atom not in ac.kind:
            ac.add(s.atom, "solution" if _kind(s.atom) in ("src", "ident", "cal") else "context")
        (ac.supported_by if ac.kind[s.atom] == "solution" else ac.in_context_of)("REQ.S", s.atom)
    changed = [a for a in ac.kind if ac.kind[a] in ("solution", "context") and status.get(a, STATUS_VALID) != STATUS_VALID]
    _ch, suspect = ac.change_impact(changed)
    cost["ops"] = cost.get("ops", 0) + ac.ops
    if v.request.kind == "PROPAGATE_DEFEAT":
        r = tuple(c for c in v.accepted if c in suspect)
        return Decision(SELECTIVELY_REOPEN, r) if r else Decision(PRESERVE)
    return Decision(REVALIDATE) if "REQ" in suspect else Decision(UPDATE)


# ---- M: orion_v2 transition control ---------------------------------------------------

def engine_transition_control(struct: Structure, status: dict[str, str], v: ArmView, cost: dict, *, three_valued: bool) -> Decision:
    """M: registered problem contract (orion_v2.contracts.ProblemContract),
    one typed Obligation per cross-transition condition, selective reopening
    through orion_v2.reopening, and the registered precedence walk."""
    req = v.request; w = v.world; T = w.claims[req.target_claim_id]
    contract = ProblemContract(problem_id=T.claim_id, target=f"claim:{T.claim_id}", decision_class=req.kind, scope=tuple(T.scope), authority_requirements=((AUTHORITY_LEVEL_NAMES[req.required_authority_level],) if req.required_authority_level > 1 else ()))
    cost["ops"] = cost.get("ops", 0) + 1 + int(contract.requires_authority())
    disp = engine_selective_reopen(struct, status, v.accepted, cost, three_valued=three_valued)
    if req.kind == "PROPAGATE_DEFEAT":
        return decide_defeat(disp, v.accepted, three_valued=three_valued)
    obligations: list[tuple[Obligation, str]] = []
    for s in struct.request:
        st = piece_status(disp[s.piece]) if s.piece else status.get(s.atom, STATUS_VALID)
        if not three_valued and st == STATUS_UNKNOWN:
            st = STATUS_VALID
        ostatus = ObligationStatus.SATISFIED if st == STATUS_VALID else ObligationStatus.CENSORED if st == STATUS_UNKNOWN else (ObligationStatus.AUTHORITY_BLOCKED if s.module == "AUTH" else ObligationStatus.DEFEATED)
        obligations.append((Obligation(s.atom, f"{s.module} condition {s.atom}", ostatus, support_ids=(s.atom,)), s.action))
    cost["ops"] = cost.get("ops", 0) + len(obligations)
    atoms = [(o.obligation_id, STATUS_VALID if o.status is ObligationStatus.SATISFIED else STATUS_UNKNOWN if o.status is ObligationStatus.CENSORED else STATUS_INVALID, act) for o, act in obligations]
    d = walk(atoms, three_valued=three_valued)
    _terminal = {DEFER_CANNOT_CHECK: Terminal.CANNOT_CHECK, ABSTAIN_AUTHORITY: Terminal.AUTHORITY_REQUIRED, UPDATE: Terminal.JUSTIFIED_SOLUTION}.get(d.action, Terminal.JUSTIFIED_PARTIAL_RESULT)
    return d


# ---- arm definitions ---------------------------------------------------------------------

@dataclass
class ArmSpec:
    name: str
    family: str
    modules: dict[str, str]
    engine: str
    witness_level: tuple[str, ...] = MODULES
    merge_families: bool = False
    three_valued: bool = True
    dropped_kinds: tuple[str, ...] = ()
    note: str = ""


TYPED = {m: "typed" for m in MODULES}


def _status_for(spec: ArmSpec, v: ArmView, ops: dict) -> dict[str, str]:
    st: dict[str, str] = {}
    m = spec.modules
    if m["IDENT"] != "none":
        st.update(ident_typed(v, ops, mode=m["IDENT"]))
    st.update(prov_typed(v, ops, measurement=(m["PROV"] != "no_measurement")))
    if m["DEP"] == "typed":
        st.update(dep_typed(v, ops))
    if m["TRANS"] != "none":
        st.update(trans_typed(v, ops, untyped=(m["TRANS"] == "untyped")))
    if m["EVAL"] != "none":
        st.update(eval_typed(v, ops, mode=m["EVAL"]))
    if m["ATLAS"] != "none":
        st.update(atlas_typed(v, ops, matching_only=(m["ATLAS"] == "matching")))
    if m["AUTH"] == "typed":
        st.update(auth_typed(v, ops))
    return st


def arm_specs(minimal_dropped_kinds: tuple[str, ...] = ()) -> list[ArmSpec]:
    specs = [
        ArmSpec("B0_DIRECT", "B0", dict(TYPED), "direct", note="local task system: local checks pass -> proceed"),
        ArmSpec("B1_CALIBRATED_ABSTENTION", "B1", dict(TYPED), "abstain", note="B0 + untyped uncertainty gate on the request lineage: any flag -> DEFER"),
        ArmSpec("B2_PROVENANCE_PLUS_VERIFIER", "B2", dict(TYPED), "provenance_verifier", three_valued=False, note="orion_v2.provenance revocation descendants over the execution graph + local verifier; artifact lineage identity; two-valued"),
        ArmSpec("B3_PARENT_NATIVE_ASSURANCE", "B3", dict(TYPED), "assurance", three_valued=False, note="GSN change-impact over typed context elements; AND semantics; re-argue (REVALIDATE) or reopen suspect goals; two-valued"),
        ArmSpec("B4_PARENT_MODULES_WITH_SHARED_STATE", "B4", {**TYPED, "IDENT": "lineage", "ATLAS": "matching", "AUTH": "none"}, "federation", note="typed provenance/dependence/transport/evaluator modules + JTMS shared state + registered precedence glue; identity by artifact lineage; pairwise compatibility taken as global; no authority module"),
    ]
    ladder = {1: (), 2: ("PROV",), 3: ("PROV", "DEP"), 4: ("PROV", "DEP", "TRANS", "EVAL"), 5: MODULES}
    for r, wl in ladder.items():
        name = "B5_STRONGEST_FAITHFUL_PARENT_FEDERATION" if r == 5 else f"B5_R{r}_{'VERDICT_ONLY' if r == 1 else '+'.join(wl)}"
        specs.append(ArmSpec(name, "B5_LADDER", dict(TYPED), "federation", witness_level=tuple(wl), note=f"federation rung {r}: all parents typed; witness-level export {wl or 'none'}; JTMS propagation with censored-atom envelope; registered precedence glue"))
    specs += [
        ArmSpec("M_ME_TRANSITION_CONTROL", "M", dict(TYPED), "transition_control", note="orion_v2 ProblemContract + typed Obligations + provenance/dependence/RelationType/comparability/atlas reference modules + selective_reopen envelope + registered precedence walk"),
        ArmSpec("M_MINUS_PROBLEM_IDENTITY", "M_ABLATION", {**TYPED, "IDENT": "checker_only"}, "transition_control", note="identity/criterion/spec conditions removed (checker verdict kept)"),
        ArmSpec("M_MINUS_DEPENDENCE", "M_ABLATION", {**TYPED, "DEP": "none"}, "transition_control", note="independence witnesses removed"),
        ArmSpec("M_MINUS_EVALUATOR_CONTRACT", "M_ABLATION", {**TYPED, "EVAL": "status_only"}, "transition_control", note="evaluator coverage contract removed (only the validity status remains)"),
        ArmSpec("M_MINUS_TRANSPORT", "M_ABLATION", {**TYPED, "TRANS": "none"}, "transition_control", note="typed transport removed (donor results reused freely)"),
        ArmSpec("M_MINUS_SUPPORT_REOPENING", "M_ABLATION", dict(TYPED), "transition_control", merge_families=True, note="support families merged into one AND family per claim (no selective reopening)"),
        ArmSpec("M_MINUS_AUTHORITY", "M_ABLATION", {**TYPED, "AUTH": "none"}, "transition_control", note="authority ceiling removed"),
        ArmSpec("M_MINUS_UNRESOLVED_TERMINAL", "M_ABLATION", dict(TYPED), "transition_control", three_valued=False, note="censored conditions treated as satisfied (no DEFER_CANNOT_CHECK)"),
        ArmSpec("M_MINUS_MEASUREMENT_COMPARABILITY", "M_ABLATION", {**TYPED, "PROV": "no_measurement"}, "transition_control", note="beyond protocol S6: calibration and comparability conditions removed"),
        ArmSpec("M_MINIMAL_RECEIPT", "M_ABLATION", dict(TYPED), "transition_control", dropped_kinds=tuple(minimal_dropped_kinds), note="atom kinds dropped by the development-frozen minimal-receipt rule"),
        ArmSpec("C_ALWAYS_UPDATE", "CONTROL", dict(TYPED), "always_update"),
        ArmSpec("C_ALWAYS_DEFER", "CONTROL", dict(TYPED), "always_defer"),
        ArmSpec("C_RANDOM_ACTION", "CONTROL", dict(TYPED), "random"),
    ]
    return specs


class ArmRunner:
    def __init__(self, spec: ArmSpec, instance_seed: int) -> None:
        self.spec = spec
        self.rng = random.Random(instance_seed ^ 0x5EED)
        self.jtms = JTMSEngine()

    def run(self, v: ArmView) -> tuple[Decision, dict]:
        spec = self.spec
        cost: dict = {"ops": 0, "module_ops": 0}
        t0 = time.perf_counter_ns()
        eng = spec.engine
        if eng == "always_update":
            d = Decision(PRESERVE if v.request.kind == "PROPAGATE_DEFEAT" else UPDATE)
        elif eng == "always_defer":
            d = Decision(DEFER_CANNOT_CHECK)
        elif eng == "random":
            a = self.rng.choice(ACTIONS)
            d = Decision(a, tuple(sorted(c for c in v.accepted if self.rng.random() < 0.5)) if a == SELECTIVELY_REOPEN else ())
        elif eng == "direct":
            d = engine_direct(v, cost)
        elif eng == "abstain":
            d = engine_abstain(v, cost)
        elif eng == "provenance_verifier":
            d = engine_provenance_verifier(v, cost)
        else:
            mops: dict = {}
            status = _status_for(spec, v, mops)
            cost["module_ops"] = mops.get("n", 0)
            struct = build_structure(v, spec)
            if eng == "assurance":
                d = engine_assurance(struct, status, v, cost)
            elif eng == "transition_control":
                d = engine_transition_control(struct, status, v, cost, three_valued=spec.three_valued)
            elif eng == "federation":
                slots = support_slots(v.world)
                for m in MODULES:
                    if m not in spec.witness_level:
                        struct, status = compress_support_to_verdicts(struct, slots, status, m)
                disp = self.jtms.run(struct, status, cost, three_valued=spec.three_valued)
                if v.request.kind == "PROPAGATE_DEFEAT":
                    d = decide_defeat(disp, v.accepted, three_valued=spec.three_valued)
                else:
                    for s in struct.request:
                        if s.piece:
                            status[s.atom] = piece_status(disp[s.piece])
                    for m in MODULES:
                        if m not in spec.witness_level:
                            struct, status = compress_request_to_verdict(struct, status, m)
                    d = walk([(s.atom, status.get(s.atom, STATUS_VALID), s.action) for s in struct.request], three_valued=spec.three_valued)
            else:
                raise ValueError(eng)
        cost["wall_ns"] = time.perf_counter_ns() - t0
        return d, cost
