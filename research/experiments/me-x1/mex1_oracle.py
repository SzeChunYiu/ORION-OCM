#!/usr/bin/env python3
"""ME-X1 exact oracle (frozen with design V1, S2.3-S2.5).

For a registered World and a TransitionRequest the oracle computes the
three-valued status of every atomic transition condition and the exact
transition decision:

  decision = (action, reopened-commitment set)

Semantics (frozen):
  * request-level atoms are ordered by a frozen precedence list; each atom
    names the action taken when it is the first INVALID atom;
  * a PROPAGATE_DEFEAT request is decided by the support graph (Kleene
    three-valued, ME-X4 semantics): SELECTIVELY_REOPEN(R) with R = the
    commitments unsupported under every resolution of censored atoms,
    PRESERVE when every commitment is supported under every resolution, and
    DEFER_CANNOT_CHECK when some commitment depends on the resolution;
  * every other request is decided by the precedence walk: the action is the
    one that holds under EVERY resolution of the censored atoms; when the
    resolutions disagree the exact action is DEFER_CANNOT_CHECK.

Two independent computations are always run and must agree (G0b):
  (1) the precedence walk / Kleene support evaluation;
  (2) exhaustive enumeration of all 2^u resolutions of the u censored atoms.

This module is protected custody: arms never import it.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Optional

from mex1_model import (
    ABSTAIN_AUTHORITY, AUTH_UNDER_REVIEW, BLOCK_TRANSPORT, CAL_INVALID, CAL_UNDER_REVIEW, CHECKER_INVALID,
    CHECKER_UNKNOWN, COMP_CANNOT_CHECK, COMP_NONCOMPARABLE, DEFER_CANNOT_CHECK, DEP_CONFIRMED, DEP_SUSPECTED,
    EQUIV_CANNOT_CHECK, EQUIV_EQUIVALENT, EVAL_INVALID, EVAL_UNDER_REVIEW, EVAL_VALID, FIDELITY_FAITHFUL,
    FIDELITY_UNFAITHFUL, IDENTITY_UNRECOVERABLE, PRESERVE, REFORMULATE_PROBLEM, RELATION_CANNOT_CHECK,
    RELATION_RANK, REPLACE_OR_CHALLENGE_EVALUATOR, REQUEST_NEW_EVIDENCE, REVALIDATE, SELECTIVELY_REOPEN,
    SOURCE_DISPUTED, SOURCE_RETRACTED, STATUS_INVALID, STATUS_UNKNOWN, STATUS_VALID, UPDATE, Family,
    TransitionRequest, World,
)

Tri = Optional[bool]

# frozen module precedence (request-level walk)
MODULE_RANK: dict[str, int] = {"IDENT": 0, "PROV": 1, "DEP": 2, "TRANS": 3, "EVAL": 4, "ATLAS": 5, "AUTH": 6}


def _tri(status: str) -> Tri:
    return {STATUS_VALID: True, STATUS_INVALID: False, STATUS_UNKNOWN: None}[status]


def _status(v: Tri) -> str:
    return STATUS_VALID if v is True else STATUS_INVALID if v is False else STATUS_UNKNOWN


def _and(values) -> Tri:
    seen_unknown = False
    for v in values:
        if v is False:
            return False
        if v is None:
            seen_unknown = True
    return None if seen_unknown else True


def _or(values) -> Tri:
    seen_unknown = False
    for v in values:
        if v is True:
            return True
        if v is None:
            seen_unknown = True
    return None if seen_unknown else False


# ---- base atom semantics (S2.3) ---------------------------------------------

def source_status(w: World, evidence_id: str) -> str:
    src = w.sources[w.evidence[evidence_id].source_id]
    return STATUS_INVALID if src == SOURCE_RETRACTED else STATUS_UNKNOWN if src == SOURCE_DISPUTED else STATUS_VALID


def identity_status(w: World, evidence_id: str) -> str:
    return STATUS_UNKNOWN if w.evidence[evidence_id].identity_status == IDENTITY_UNRECOVERABLE else STATUS_VALID


def calibration_status(w: World, evidence_id: str) -> str | None:
    e = w.evidence[evidence_id]
    if not e.calibration_id:
        return None
    st = w.calibrations[e.calibration_id].status
    return STATUS_INVALID if st == CAL_INVALID else STATUS_UNKNOWN if st == CAL_UNDER_REVIEW else STATUS_VALID


def evaluator_coverage(w: World, evidence_id: str) -> str | None:
    e = w.evidence[evidence_id]
    if not e.evaluator_id:
        return None
    return evaluator_atom_status(w, e.evaluator_id, w.claims[e.claim_id].failure_class)


def evaluator_atom_status(w: World, evaluator_id: str, failure_class: str) -> str:
    ev = w.evaluators[evaluator_id]
    if ev.status == EVAL_INVALID:
        return STATUS_INVALID
    if ev.status == EVAL_UNDER_REVIEW:
        return STATUS_UNKNOWN
    if failure_class in ev.coverage:
        return STATUS_VALID
    if failure_class in ev.uncertain:
        return STATUS_UNKNOWN
    # blind: a registered valid alternative that covers the class makes replacement actionable;
    # without one the failure class cannot be checked by any registered evaluator (censored)
    alt = any(o.evaluator_id != evaluator_id and o.status == EVAL_VALID and failure_class in o.coverage for o in w.evaluators.values())
    return STATUS_INVALID if alt else STATUS_UNKNOWN


def transport_rank_status(w: World, source_context: str, target_context: str, required: str) -> str | None:
    if source_context == target_context:
        return None
    rel = w.relations.get(w.relation_key(source_context, target_context))
    if rel is None:
        return STATUS_INVALID
    if rel.relation_type == RELATION_CANNOT_CHECK:
        return STATUS_UNKNOWN
    return STATUS_VALID if RELATION_RANK[rel.relation_type] >= RELATION_RANK[required or "APPROXIMATELY_EQUIVALENT"] else STATUS_INVALID


def _components(nodes: set[str], pairs) -> int:
    adj = {n: set() for n in nodes}
    for a, b in pairs:
        if a in adj and b in adj:
            adj[a].add(b); adj[b].add(a)
    seen: set[str] = set(); count = 0
    for n in sorted(nodes):
        if n in seen:
            continue
        count += 1; stack = [n]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x); stack.extend(adj[x] - seen)
    return count


def independence_status(w: World, nodes: set[str], k: int) -> str | None:
    if k <= 0:
        return None
    confirmed = [(d.left_id, d.right_id) for d in w.dependence if d.status == DEP_CONFIRMED]
    all_edges = confirmed + [(d.left_id, d.right_id) for d in w.dependence if d.status == DEP_SUSPECTED]
    if _components(nodes, confirmed) < k:
        return STATUS_INVALID
    if _components(nodes, all_edges) < k:
        return STATUS_UNKNOWN
    return STATUS_VALID


def nocontra_status(w: World, claim_id: str) -> str:
    vals = []
    for e in w.negative_evidence_against(claim_id):
        parts = [source_status(w, e.evidence_id)]
        c = calibration_status(w, e.evidence_id)
        if c is not None:
            parts.append(c)
        vals.append(_and(_tri(p) for p in parts))
    if any(v is True for v in vals):
        return STATUS_INVALID
    if any(v is None for v in vals):
        return STATUS_UNKNOWN
    return STATUS_VALID


# ---- support graph (ME-X4 semantics over ME-X1 base atoms) ----------------------

@dataclass
class SupportTable:
    atoms: dict[str, str]
    family_atoms: dict[str, tuple[str, ...]]
    claim_atoms: dict[str, tuple[str, ...]]


def support_table(w: World) -> SupportTable:
    atoms: dict[str, str] = {}
    family_atoms: dict[str, tuple[str, ...]] = {}
    claim_atoms: dict[str, tuple[str, ...]] = {}
    for fam in sorted(w.families.values(), key=lambda f: f.family_id):
        ids: list[str] = []
        for e in fam.evidence_ids:
            if not w.evidence[e].supports:
                continue
            a = f"src:{e}"; atoms[a] = source_status(w, e); ids.append(a)
            a = f"ident:{e}"; atoms[a] = identity_status(w, e); ids.append(a)
            s = calibration_status(w, e)
            if s is not None:
                a = f"cal:{e}"; atoms[a] = s; ids.append(a)
            s = evaluator_coverage(w, e)
            if s is not None:
                a = f"evc:{e}"; atoms[a] = s; ids.append(a)
            s = transport_rank_status(w, w.evidence[e].context_id, w.claims[fam.claim_id].context_id, fam.required_relation)
            if s is not None:
                a = f"tr:{fam.family_id}:{e}"; atoms[a] = s; ids.append(a)
        s = independence_status(w, {e.evidence_id for e in w.positive_evidence_of_family(fam)}, fam.min_independent)
        if s is not None:
            a = f"ind:{fam.family_id}"; atoms[a] = s; ids.append(a)
        family_atoms[fam.family_id] = tuple(ids)
    for c in w.claims:
        a = f"nocontra:{c}"; atoms[a] = nocontra_status(w, c); claim_atoms[c] = (a,)
    return SupportTable(atoms, family_atoms, claim_atoms)


def evaluate_support(w: World, atom_values: dict[str, Tri], table: SupportTable) -> dict[str, Tri]:
    support: dict[str, Tri] = {}
    for c in w.prerequisite_topological_order():
        fams = w.families_of(c)
        fam_vals = []
        for fam in fams:
            parts = [atom_values[a] for a in table.family_atoms[fam.family_id]]
            parts += [support[p] for p in fam.prerequisite_ids]
            fam_vals.append(_and(parts))
        s = _or(fam_vals) if fams else False
        support[c] = _and([s] + [atom_values[a] for a in table.claim_atoms[c]])
    return support


# ---- request-level atoms (S2.4, frozen precedence) -------------------------------

@dataclass(frozen=True)
class ReqAtom:
    atom_id: str
    module: str
    status: str
    action: str          # action when this atom is the first INVALID one
    derived_from: tuple[str, ...] = ()   # base atoms this atom is a function of (derived atoms only)


def global_pieces(w: World, claim_id: str) -> tuple[str, ...]:
    return tuple(sorted({p for f in w.families_of(claim_id) for p in f.prerequisite_ids}))


def request_atoms(w: World, req: TransitionRequest, support: dict[str, Tri], table: SupportTable) -> list[ReqAtom]:
    """Ordered request-level atoms. Base atoms shared with the support graph
    keep their support-graph ids so that a resolution is consistent."""
    T = w.claims[req.target_claim_id]
    out: list[ReqAtom] = []
    if req.kind == "ACCEPT_RESULT":
        R = w.results[req.result_id]
        # IDENT
        ident = STATUS_UNKNOWN if R.binding_status == IDENTITY_UNRECOVERABLE else (STATUS_VALID if R.bound_claim_id == T.claim_id else STATUS_INVALID)
        out.append(ReqAtom(f"identity:{R.result_id}", "IDENT", ident, REVALIDATE))
        dc = req.decision_criterion_id or T.criterion_id
        if dc == T.criterion_id:
            crit = STATUS_VALID
        else:
            eq = w.criterion_equivalence.get(w.pair_key(T.criterion_id, dc), "")
            crit = STATUS_VALID if eq == EQUIV_EQUIVALENT else STATUS_UNKNOWN if eq == EQUIV_CANNOT_CHECK else STATUS_INVALID
        out.append(ReqAtom(f"criterion:{T.claim_id}", "IDENT", crit, REFORMULATE_PROBLEM))
        if R.proved_spec_id:
            if R.proved_spec_id == T.intended_spec_id:
                fid = STATUS_VALID
            else:
                f = w.spec_fidelity.get(w.pair_key(R.proved_spec_id, T.intended_spec_id), "")
                fid = STATUS_VALID if f == FIDELITY_FAITHFUL else STATUS_INVALID if f == FIDELITY_UNFAITHFUL else STATUS_UNKNOWN
            out.append(ReqAtom(f"spec:{R.result_id}", "IDENT", fid, REVALIDATE))
            chk = STATUS_INVALID if R.checker_status == CHECKER_INVALID else STATUS_UNKNOWN if R.checker_status == CHECKER_UNKNOWN else STATUS_VALID
            out.append(ReqAtom(f"checker:{R.result_id}", "IDENT", chk, REQUEST_NEW_EVIDENCE))
        # PROV (basis evidence; ids shared with the support graph when the evidence sits in a family)
        for e in R.basis_evidence_ids:
            out.append(ReqAtom(f"src:{e}", "PROV", source_status(w, e), REQUEST_NEW_EVIDENCE))
            out.append(ReqAtom(f"ident:{e}", "PROV", identity_status(w, e), REVALIDATE))
            c = calibration_status(w, e)
            if c is not None:
                out.append(ReqAtom(f"cal:{e}", "PROV", c, REVALIDATE))
        if R.comparability_status:
            comp = STATUS_INVALID if R.comparability_status == COMP_NONCOMPARABLE else STATUS_UNKNOWN if R.comparability_status == COMP_CANNOT_CHECK else STATUS_VALID
            out.append(ReqAtom(f"comparability:{R.result_id}", "PROV", comp, REVALIDATE))
        # DEP
        s = independence_status(w, set(R.basis_evidence_ids), R.min_independent)
        if s is not None:
            out.append(ReqAtom(f"support:{R.result_id}", "DEP", s, REQUEST_NEW_EVIDENCE))
        # TRANS
        s = transport_rank_status(w, R.context_id, T.context_id, R.required_relation)
        if s is not None:
            out.append(ReqAtom(f"transport:{R.result_id}", "TRANS", s, BLOCK_TRANSPORT))
        # EVAL
        if R.evaluator_id:
            out.append(ReqAtom(f"evaluator:{R.result_id}", "EVAL", evaluator_atom_status(w, R.evaluator_id, T.failure_class), REPLACE_OR_CHALLENGE_EVALUATOR))
    elif req.kind == "CLOSE_GLOBAL":
        pieces = global_pieces(w, T.claim_id)
        for c in pieces:
            deps = tuple(sorted(_support_base_atoms(w, c, table)))
            out.append(ReqAtom(f"piece:{c}", "ATLAS", _status(support[c]), REQUEST_NEW_EVIDENCE, deps))
        for o in sorted(w.overlaps.values(), key=lambda x: x.overlap_id):
            if o.left_claim_id in pieces and o.right_claim_id in pieces:
                st = STATUS_VALID if o.compatible is True else STATUS_INVALID if o.compatible is False else STATUS_UNKNOWN
                out.append(ReqAtom(f"overlap:{o.overlap_id}", "ATLAS", st, REFORMULATE_PROBLEM))
        out.append(ReqAtom(f"witness:{T.claim_id}", "ATLAS", STATUS_VALID if T.global_witness_id else STATUS_UNKNOWN, REFORMULATE_PROBLEM))
    else:
        raise ValueError(req.kind)
    # AUTH (last: authority is checked after every epistemic condition)
    auth = STATUS_UNKNOWN if w.authority.status == AUTH_UNDER_REVIEW else (STATUS_VALID if w.authority.ceiling_level >= req.required_authority_level else STATUS_INVALID)
    out.append(ReqAtom("authority", "AUTH", auth, ABSTAIN_AUTHORITY))
    assert [MODULE_RANK[a.module] for a in out] == sorted(MODULE_RANK[a.module] for a in out)
    return out


def _support_base_atoms(w: World, claim_id: str, table: SupportTable) -> set[str]:
    """Base atoms the support of claim_id depends on (transitively over prerequisites)."""
    out: set[str] = set(); stack = [claim_id]; seen: set[str] = set()
    while stack:
        c = stack.pop()
        if c in seen:
            continue
        seen.add(c)
        out.update(table.claim_atoms[c])
        for fam in w.families_of(c):
            out.update(table.family_atoms[fam.family_id]); stack.extend(fam.prerequisite_ids)
    return out


# ---- decision --------------------------------------------------------------------

@dataclass(frozen=True)
class Expected:
    action: str
    reopened: tuple[str, ...]
    decisive_module: str
    decisive_atom: str
    action_set: tuple[str, ...]
    unknown_atoms: tuple[str, ...]
    exhaustive_agrees: bool

    def as_dict(self) -> dict:
        return {"action": self.action, "reopened": list(self.reopened), "decisive_module": self.decisive_module, "decisive_atom": self.decisive_atom, "action_set": list(self.action_set), "unknown_atoms": list(self.unknown_atoms), "exhaustive_agrees": self.exhaustive_agrees}

    def decision(self) -> tuple[str, tuple[str, ...]]:
        return (self.action, self.reopened)


def walk(atoms: list[ReqAtom]) -> tuple[str, str, str, tuple[str, ...]]:
    """Precedence walk with the singleton rule. Returns (action, decisive_module, decisive_atom, action_set)."""
    first_invalid = next((i for i, a in enumerate(atoms) if a.status == STATUS_INVALID), None)
    pre_unknown = [a for a in (atoms[:first_invalid] if first_invalid is not None else atoms) if a.status == STATUS_UNKNOWN]
    terminal = atoms[first_invalid].action if first_invalid is not None else UPDATE
    action_set = tuple(sorted({a.action for a in pre_unknown} | {terminal}))
    if len(action_set) == 1:
        if first_invalid is None:
            return UPDATE, "", "", action_set
        a = atoms[first_invalid]
        return a.action, a.module, a.atom_id, action_set
    return DEFER_CANNOT_CHECK, "CENSORED", "", action_set


def _two_valued_walk(atoms: list[ReqAtom], values: dict[str, bool], support2: dict[str, bool]) -> str:
    for a in atoms:
        if a.derived_from:
            v = support2[a.atom_id.split(":", 1)[1]]
        else:
            v = values[a.atom_id]
        if not v:
            return a.action
    return UPDATE


def oracle(w: World, req: TransitionRequest, *, max_unknown: int = 12) -> Expected:
    table = support_table(w)
    tri = {a: _tri(s) for a, s in table.atoms.items()}
    support = evaluate_support(w, tri, table)
    accepted = w.accepted_ids()
    if req.kind == "PROPAGATE_DEFEAT":
        reopened = tuple(c for c in accepted if support[c] is False)
        unresolved = tuple(c for c in accepted if support[c] is None)
        if unresolved:
            action, module, atom = DEFER_CANNOT_CHECK, "CENSORED", ""
        elif reopened:
            action, module, atom = SELECTIVELY_REOPEN, "SUPPORT", ""
        else:
            action, module, atom = PRESERVE, "", ""
        action_set = (action,) if not unresolved else (PRESERVE, SELECTIVELY_REOPEN)
        base_unknown = tuple(sorted(a for a, v in tri.items() if v is None))
        req_atoms: list[ReqAtom] = []
    else:
        req_atoms = request_atoms(w, req, support, table)
        action, module, atom, action_set = walk(req_atoms)
        reopened = ()
        base_unknown = tuple(sorted({a for a, v in tri.items() if v is None} | {a.atom_id for a in req_atoms if a.status == STATUS_UNKNOWN and not a.derived_from}))
    # ---- exhaustive cross-check over all resolutions of the censored base atoms ----
    if len(base_unknown) > max_unknown:
        raise ValueError(f"too many censored atoms for exhaustive oracle: {len(base_unknown)}")
    req_values = {a.atom_id: _tri(a.status) for a in req_atoms if not a.derived_from}
    decisions: set[tuple[str, tuple[str, ...]]] = set()
    for bits in itertools.product((True, False), repeat=len(base_unknown)):
        res = dict(zip(base_unknown, bits))
        vals = {a: (res[a] if v is None else v) for a, v in tri.items()}
        sup2 = evaluate_support(w, vals, table)
        if req.kind == "PROPAGATE_DEFEAT":
            r = tuple(c for c in accepted if not sup2[c])
            decisions.add((SELECTIVELY_REOPEN if r else PRESERVE, r))
        else:
            rv = {a: (res[a] if v is None else v) for a, v in req_values.items()}
            decisions.add((_two_valued_walk(req_atoms, rv, sup2), ()))
    if len(decisions) == 1:
        exhaustive = next(iter(decisions))
    else:
        exhaustive = (DEFER_CANNOT_CHECK, ())
    agrees = exhaustive == (action, reopened)
    return Expected(action, reopened, module, atom, tuple(action_set), base_unknown, agrees)


def all_accepted_supported_at_v0(w: World) -> bool:
    table = support_table(w)
    tri = {a: _tri(s) for a, s in table.atoms.items()}
    sup = evaluate_support(w, tri, table)
    return all(sup[c] is True for c in w.accepted_ids()) and not any(v is None for v in tri.values())


def final_world(world_v0: World, events) -> World:
    from mex1_model import apply_event
    w = world_v0
    for ev in events:
        w = apply_event(w, ev)
    return w


def expected_for(world_v0: World, events, req: TransitionRequest) -> tuple[World, Expected]:
    w = final_world(world_v0, events)
    return w, oracle(w, req)


__all__ = ["Expected", "ReqAtom", "SupportTable", "Family", "oracle", "expected_for", "final_world", "all_accepted_supported_at_v0", "support_table", "evaluate_support", "request_atoms", "walk", "MODULE_RANK"]
