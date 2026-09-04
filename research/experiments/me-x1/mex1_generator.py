#!/usr/bin/env python3
"""ME-X1 exact known-answer generator (frozen with design V1, S2-S3).

Every instance = registered epistemic state at v0 + typed event sequence
(0-3 events) + one TransitionRequest. The per-family planter plants the
family's structure for the scheduled variant (POSITIVE / NEGATIVE /
AMBIGUITY, frozen cycle VARIANT_CYCLE), then the family invariant is checked
against the exact oracle (deterministic rejection sampling under the instance
seed). Expected decisions are computed by mex1_oracle and written to
protected custody by the runner, never handed to arms.

Also holds the hand-authored known-answer fixtures (G0a): the 14 public
development cases of ME_X1_X2_DEVELOPMENT_KNOWN_ANSWER_FIXTURES_V1.json bound
to concrete registered worlds, and the H-EXT-3 finite separation pair (P, Q).
"""
from __future__ import annotations

import hashlib
import random
from typing import Any, Callable

from mex1_model import (
    ABSTAIN_AUTHORITY, AUTH_UNDER_REVIEW, AUTHORITY_BELIEF, AUTHORITY_EXTERNAL, AUTHORITY_OPERATIONAL, BLOCK_TRANSPORT,
    CAL_VALID, CHECKER_INVALID, CHECKER_UNKNOWN, CHECKER_VALID, COMP_CANNOT_CHECK, COMP_COMPARABLE, COMP_NONCOMPARABLE,
    DEFER_CANNOT_CHECK, EQUIV_CANNOT_CHECK, EQUIV_EQUIVALENT, EQUIV_NOT_EQUIVALENT, FAMILIES, FIDELITY_FAITHFUL,
    FIDELITY_UNFAITHFUL, IDENTITY_UNRECOVERABLE, PRESERVE, REFORMULATE_PROBLEM, RELATION_CANNOT_CHECK, RELATION_RANK,
    REPLACE_OR_CHALLENGE_EVALUATOR, REQUEST_NEW_EVIDENCE, REVALIDATE, SELECTIVELY_REOPEN, SOURCE_VALID, UPDATE,
    VARIANT_CYCLE, AuthorityPolicy, Calibration, Claim, Evaluator, Event, Evidence, Family, Instance, Overlap, Relation,
    Result, TransitionRequest, World,
)
from mex1_oracle import Expected, all_accepted_supported_at_v0, expected_for, oracle

CONTEXTS = ("ctx0", "ctx1", "ctx2")
FAILURE_CLASSES = ("FC_A", "FC_B", "FC_C")
SCOPE_ELEMENTS = ("S1", "S2", "S3")
STRONG_RELATIONS = ("ISOMORPHIC", "BEHAVIORALLY_EQUIVALENT", "PREDICTIVELY_EQUIVALENT", "DECISION_DOMINATES")
DEP_KINDS = ("SHARED_DATA", "SHARED_SOURCE", "SHARED_MODEL", "SHARED_INSTRUMENT", "COMMON_CAUSE")
MAX_UNKNOWN_ATOMS = 8
MAX_EVENTS = 3
MAX_ATTEMPTS = 400


def instance_seed(split_seed: str, family: str, index: int) -> int:
    return int(hashlib.sha256(f"{split_seed}|{family}|{index}".encode()).hexdigest()[:12], 16)


def variant_for(index: int) -> str:
    return VARIANT_CYCLE[index % len(VARIANT_CYCLE)]


# ---- base world -------------------------------------------------------------

class _Builder:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.w = World()
        self.n_ev = 0
        self.n_fam = 0
        self.n_res = 0

    def new_evidence(self, claim: Claim, *, source: str | None = None, context: str | None = None, calibration: str | None = None, evaluator: str | None = None, supports: bool = True) -> Evidence:
        rng, w = self.rng, self.w
        self.n_ev += 1
        eid = f"e{self.n_ev:02d}"
        src = source or rng.choice(sorted(s for s in w.sources if s != "src_unused"))
        ctx = context or claim.context_id
        if calibration is None and rng.random() < 0.4:
            calibration = rng.choice(sorted(c for c in w.calibrations if "unused" not in c))
        if evaluator is None:
            eligible = sorted(e for e, ev in w.evaluators.items() if claim.failure_class in ev.coverage)
            evaluator = rng.choice(eligible) if eligible and rng.random() < 0.7 else ""
        e = Evidence(eid, claim.claim_id, src, ctx, tuple(claim.scope), evaluator or "", calibration or "", data_id=f"data:{src}", instrument_id=(w.calibrations[calibration].instrument_id if calibration else ""), supports=supports)
        w.evidence[eid] = e
        return e

    def new_family(self, claim: Claim, evidence_ids: tuple[str, ...], prereqs: tuple[str, ...] = (), *, min_independent: int = 0, required_relation: str = "") -> Family:
        self.n_fam += 1
        fid = f"{claim.claim_id}.F{self.n_fam}"
        fam = Family(fid, claim.claim_id, tuple(evidence_ids), tuple(prereqs), min_independent, required_relation)
        self.w.families[fid] = fam
        return fam

    def evaluator_covering(self, fc: str) -> str:
        w = self.w
        eligible = sorted(e for e, ev in w.evaluators.items() if fc in ev.coverage and ev.status == "VALID")
        return self.rng.choice(eligible) if eligible else "ev0"

    def new_result(self, claim: Claim, basis: tuple[str, ...] | None = None, *, bound: str | None = None, context: str | None = None, evaluator: str | None = None, **kw) -> Result:
        w = self.w
        self.n_res += 1
        rid = f"r{self.n_res}"
        if basis is None:
            fams = [f for f in w.families_of(claim.claim_id) if w.positive_evidence_of_family(f)]
            basis = tuple(e.evidence_id for e in w.positive_evidence_of_family(fams[0])) if fams else ()
        r = Result(rid, bound or claim.claim_id, tuple(basis), context or claim.context_id, self.evaluator_covering(claim.failure_class) if evaluator is None else evaluator, **kw)
        w.results[rid] = r
        return r


def build_base_world(rng: random.Random) -> _Builder:
    b = _Builder(rng)
    w = b.w
    for i in range(rng.randint(4, 6)):
        w.sources[f"src{i}"] = SOURCE_VALID
    w.sources["src_unused"] = SOURCE_VALID
    for inst in ("inst0", "inst1"):
        for j in range(rng.randint(1, 2)):
            cid = f"cal:{inst}:{j}"
            w.calibrations[cid] = Calibration(cid, inst, CAL_VALID)
    w.calibrations["cal:inst_unused:0"] = Calibration("cal:inst_unused:0", "inst_unused", CAL_VALID)
    w.evaluators["ev0"] = Evaluator("ev0", FAILURE_CLASSES)
    w.evaluators["ev1"] = Evaluator("ev1", tuple(sorted(rng.sample(FAILURE_CLASSES, 2))))
    w.evaluators["ev2"] = Evaluator("ev2", tuple(sorted(rng.sample(FAILURE_CLASSES, rng.randint(1, 2)))))
    for a in CONTEXTS:
        for c in CONTEXTS:
            if a != c and rng.random() < 0.7:
                w.relations[w.relation_key(a, c)] = Relation(a, c, rng.choice(STRONG_RELATIONS))
    w.authority = AuthorityPolicy(AUTHORITY_OPERATIONAL, "VALID")
    n_claims = rng.randint(3, 6)
    layers: list[list[str]] = [[], [], []]
    for i in range(n_claims):
        cid = f"c{i}"
        layer = 0 if i < 2 else rng.choice((0, 1, 1, 2))
        scope = tuple(sorted(rng.sample(SCOPE_ELEMENTS, rng.randint(1, 2))))
        w.claims[cid] = Claim(cid, rng.choice(CONTEXTS[:2]), rng.choice(FAILURE_CLASSES), scope, f"K_{cid}", True, intended_spec_id=f"SPEC_{cid}")
        layers[layer].append(cid)
    for layer_idx, layer in enumerate(layers):
        lower = [c for lo in layers[:layer_idx] for c in lo]
        for cid in layer:
            claim = w.claims[cid]
            for _ in range(rng.choice((1, 1, 2, 2))):
                ev_ids: list[str] = []
                req = ""
                prereq_only = bool(lower) and rng.random() < 0.2
                for _k in range(0 if prereq_only else rng.randint(1, 3)):
                    ev_ids.append(b.new_evidence(claim).evidence_id)
                prereqs = tuple(sorted(rng.sample(lower, min(len(lower), rng.choice((1, 2)) if prereq_only else rng.choice((0, 0, 1)))))) if lower else ()
                if not ev_ids and not prereqs:
                    ev_ids.append(b.new_evidence(claim).evidence_id)
                k = 2 if (len(ev_ids) >= 2 and rng.random() < 0.3) else 0
                b.new_family(claim, tuple(ev_ids), prereqs, min_independent=k, required_relation=req)
    w.validate()
    return b


# ---- helpers ----------------------------------------------------------------

def _targets(w: World) -> list[str]:
    return [c for c in w.accepted_ids() if any(w.positive_evidence_of_family(f) for f in w.families_of(c))]


def _first_evidence_family(w: World, c: str) -> Family:
    return next(f for f in w.families_of(c) if w.positive_evidence_of_family(f))


def _decoy_event(b: _Builder, avoid_claims: set[str]) -> Event | None:
    """An event that touches registered entities but defeats nothing sufficient
    for the claims in avoid_claims (checked later by the oracle invariant)."""
    rng, w = b.rng, b.w
    picks = ["UNUSED_SOURCE", "UNUSED_CALIBRATION", "EVALUATOR_WIDENED", "RELATION_UPGRADED", "TARGET_CHANGED_OTHER", "IRRELEVANT_DEPENDENCE", "AUTHORITY_RAISED"]
    v = rng.choice(picks)
    if v == "UNUSED_SOURCE":
        return Event("SOURCE_RETRACTED", {"source_id": "src_unused"}, note="decoy")
    if v == "UNUSED_CALIBRATION":
        return Event("CALIBRATION_INVALIDATED", {"calibration_id": "cal:inst_unused:0"}, note="decoy")
    if v == "EVALUATOR_WIDENED":
        return Event("EVALUATOR_COVERAGE_CHANGED", {"evaluator_id": "ev1", "coverage": list(FAILURE_CLASSES), "uncertain": []}, note="decoy")
    if v == "RELATION_UPGRADED":
        keys = sorted(k for k, r in w.relations.items() if r.relation_type != "ISOMORPHIC")
        if keys:
            r = w.relations[rng.choice(keys)]
            return Event("RELATION_RETYPED", {"source_context": r.source_context, "target_context": r.target_context, "relation_type": "ISOMORPHIC"}, note="decoy")
    if v == "TARGET_CHANGED_OTHER":
        others = [c for c in w.accepted_ids() if c not in avoid_claims]
        if others:
            return Event("TARGET_CHANGED", {"claim_id": rng.choice(others)}, note="decoy")
    if v == "IRRELEVANT_DEPENDENCE":
        fams = [f for f in w.families.values() if f.min_independent == 0 and len(w.positive_evidence_of_family(f)) >= 2]
        if fams:
            f = rng.choice(sorted(fams, key=lambda x: x.family_id)); pos = [e.evidence_id for e in w.positive_evidence_of_family(f)]
            return Event("DEPENDENCE_DISCOVERED", {"left_id": pos[0], "right_id": pos[1], "kind": rng.choice(DEP_KINDS)}, note="decoy")
    if v == "AUTHORITY_RAISED":
        return Event("AUTHORITY_POLICY_CHANGED", {"ceiling_level": AUTHORITY_EXTERNAL, "status": "VALID"}, note="decoy")
    return None


def _accept(target: str, result: str, **kw) -> TransitionRequest:
    return TransitionRequest("ACCEPT_RESULT", target, result, kw.get("criterion", ""), kw.get("level", AUTHORITY_BELIEF))


def _defeat(target: str, idx: int = 0) -> TransitionRequest:
    return TransitionRequest("PROPAGATE_DEFEAT", target, "", "", AUTHORITY_BELIEF, idx)


def _assign_source_exclusive(b: _Builder, evidence_ids: list[str], s: str, avoid_claims: set[str]) -> None:
    """Give the listed evidence source s and move every other use of s (in avoid_claims) elsewhere."""
    w, rng = b.w, b.rng
    for e in evidence_ids:
        w.evidence[e].source_id = s
    for e in w.evidence.values():
        if e.evidence_id not in evidence_ids and e.source_id == s and e.claim_id in avoid_claims:
            e.source_id = rng.choice(sorted(x for x in w.sources if x not in (s, "src_unused")))


# ---- planters: each returns (events, request, features) or None --------------
# invariants receive (Expected, features, final World) and return bool

def plant_A(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    if len(ts) < 2:
        return None
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    if variant == "POSITIVE":
        sub = rng.choice(("BINDING", "BINDING", "CRITERION"))
        feats["sub"] = sub
        if sub == "BINDING":
            S = rng.choice([c for c in ts if c != T])
            fam = _first_evidence_family(w, S)
            r = b.new_result(Tc, tuple(e.evidence_id for e in w.positive_evidence_of_family(fam)), bound=S, context=Tc.context_id)
            req = _accept(T, r.result_id)
        else:
            r = b.new_result(Tc)
            if rng.random() < 0.5:
                events.append(Event("CRITERION_EQUIVALENCE_ASSESSED", {"left": Tc.criterion_id, "right": "K_decision", "status": EQUIV_NOT_EQUIVALENT}))
            req = _accept(T, r.result_id, criterion="K_decision")
    elif variant == "NEGATIVE":
        r = b.new_result(Tc)
        if rng.random() < 0.5:
            events.append(Event("CRITERION_EQUIVALENCE_ASSESSED", {"left": Tc.criterion_id, "right": "K_decision", "status": EQUIV_EQUIVALENT}))
            req = _accept(T, r.result_id, criterion="K_decision"); feats["sub"] = "EQUIVALENT_CRITERION"
        else:
            req = _accept(T, r.result_id); feats["sub"] = "SAME_OUTPUT_CORRECT_BINDING"
        d = _decoy_event(b, {T})
        if d:
            events.append(d)
    else:
        sub = rng.choice(("BINDING_UNRECOVERABLE", "EVIDENCE_IDENTITY_LOST", "CRITERION_CANNOT_CHECK"))
        feats["sub"] = sub
        if sub == "BINDING_UNRECOVERABLE":
            r = b.new_result(Tc, binding_status=IDENTITY_UNRECOVERABLE); req = _accept(T, r.result_id)
        elif sub == "EVIDENCE_IDENTITY_LOST":
            r = b.new_result(Tc); events.append(Event("EVIDENCE_IDENTITY_LOST", {"evidence_id": r.basis_evidence_ids[0]})); req = _accept(T, r.result_id)
        else:
            r = b.new_result(Tc); events.append(Event("CRITERION_EQUIVALENCE_ASSESSED", {"left": Tc.criterion_id, "right": "K_decision", "status": EQUIV_CANNOT_CHECK})); req = _accept(T, r.result_id, criterion="K_decision")
    return events, req, feats


def inv_A(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        return (exp.action == REVALIDATE and exp.decisive_atom.startswith("identity:")) if f["sub"] == "BINDING" else (exp.action == REFORMULATE_PROBLEM and exp.decisive_atom.startswith("criterion:"))
    if variant == "NEGATIVE":
        return exp.action == UPDATE
    return exp.action == DEFER_CANNOT_CHECK and bool({REVALIDATE, REFORMULATE_PROBLEM} & set(exp.action_set))


def plant_B(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    r = b.new_result(Tc)
    e0 = w.evidence[r.basis_evidence_ids[0]]
    cals = sorted(c for c in w.calibrations if "unused" not in c)
    if not e0.calibration_id:
        e0.calibration_id = rng.choice(cals); e0.instrument_id = w.calibrations[e0.calibration_id].instrument_id
    req = _accept(T, r.result_id)
    if variant == "POSITIVE":
        sub = rng.choice(("CALIBRATION", "CALIBRATION", "COMPARABILITY")); feats["sub"] = sub
        if sub == "CALIBRATION":
            events.append(Event("CALIBRATION_INVALIDATED", {"calibration_id": e0.calibration_id}))
        else:
            events.append(Event("COMPARABILITY_ASSESSED", {"result_id": r.result_id, "status": COMP_NONCOMPARABLE}))
    elif variant == "NEGATIVE":
        sub = rng.choice(("SIBLING_CALIBRATION_DECOY", "TARGET_CHANGED")); feats["sub"] = sub
        if sub == "SIBLING_CALIBRATION_DECOY":
            inst = w.calibrations[e0.calibration_id].instrument_id
            sib = [c for c in cals if c != e0.calibration_id and w.calibrations[c].instrument_id == inst]
            if not sib:
                sib_id = f"cal:{inst}:9"; w.calibrations[sib_id] = Calibration(sib_id, inst, CAL_VALID); sib = [sib_id]
            for e in w.evidence.values():
                if e.evidence_id in r.basis_evidence_ids and e.calibration_id == sib[0]:
                    e.calibration_id = e0.calibration_id
            events.append(Event("CALIBRATION_INVALIDATED", {"calibration_id": sib[0]}, note="sibling calibration, not used by the basis"))
        else:
            events.append(Event("TARGET_CHANGED", {"claim_id": T}, note="ontic change registered; measurement model intact"))
            events.append(Event("COMPARABILITY_ASSESSED", {"result_id": r.result_id, "status": COMP_COMPARABLE}))
    else:
        sub = rng.choice(("CALIBRATION_UNDER_REVIEW", "COMPARABILITY_CANNOT_CHECK")); feats["sub"] = sub
        if sub == "CALIBRATION_UNDER_REVIEW":
            events.append(Event("CALIBRATION_UNDER_REVIEW", {"calibration_id": e0.calibration_id}))
        else:
            events.append(Event("COMPARABILITY_ASSESSED", {"result_id": r.result_id, "status": COMP_CANNOT_CHECK}))
    return events, req, feats


def inv_B(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        return exp.action == REVALIDATE and (exp.decisive_atom.startswith("cal:") or exp.decisive_atom.startswith("comparability:"))
    if variant == "NEGATIVE":
        return exp.action == UPDATE
    return exp.action == DEFER_CANNOT_CHECK and REVALIDATE in exp.action_set


def _single_family_with_two(b: _Builder, T: str) -> Family | None:
    """Make T carry exactly one family with >= 2 positive evidence and k = 2."""
    w = b.w
    fams = w.families_of(T)
    keep = next((f for f in fams if len(w.positive_evidence_of_family(f)) >= 2), None)
    if keep is None:
        keep = next((f for f in fams if w.positive_evidence_of_family(f)), None)
        if keep is None:
            return None
        keep.evidence_ids = tuple(keep.evidence_ids) + (b.new_evidence(w.claims[T]).evidence_id,)
    for f in fams:
        if f.family_id != keep.family_id:
            del w.families[f.family_id]
    keep.min_independent = 2
    return keep


def plant_C(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    if variant == "POSITIVE":
        sub = rng.choice(("REOPEN", "REOPEN", "NEW_SUPPORT_REQUIREMENT")); feats["sub"] = sub
        if sub == "REOPEN":
            fam = _single_family_with_two(b, T)
            if fam is None:
                return None
            pos = [e.evidence_id for e in w.positive_evidence_of_family(fam)]
            events.append(Event("DEPENDENCE_DISCOVERED", {"left_id": pos[0], "right_id": pos[1], "kind": rng.choice(DEP_KINDS)}))
            if len(pos) == 3:
                events.append(Event("DEPENDENCE_DISCOVERED", {"left_id": pos[1], "right_id": pos[2], "kind": rng.choice(DEP_KINDS)}))
            decoys = [g for g in w.families.values() if g.claim_id != T and len(w.positive_evidence_of_family(g)) >= 2 and w.claims[g.claim_id].accepted_v0]
            feats["decoy"] = ""
            if decoys and rng.random() < 0.6:
                g = rng.choice(sorted(decoys, key=lambda x: x.family_id)); gp = [e.evidence_id for e in w.positive_evidence_of_family(g)]
                g.min_independent = 2 if len(gp) >= 3 else 0
                events.append(Event("DEPENDENCE_DISCOVERED", {"left_id": gp[0], "right_id": gp[1], "kind": rng.choice(DEP_KINDS)}, note="decoy"))
                feats["decoy"] = g.claim_id
            req = _defeat(T)
        else:
            fam = _first_evidence_family(w, T)
            pos = [e.evidence_id for e in w.positive_evidence_of_family(fam)]
            if len(pos) < 2:
                pos.append(b.new_evidence(Tc).evidence_id)
            r = b.new_result(Tc, tuple(pos[:2]), min_independent=2)
            events.append(Event("DEPENDENCE_DISCOVERED", {"left_id": pos[0], "right_id": pos[1], "kind": rng.choice(DEP_KINDS)}))
            req = _accept(T, r.result_id)
    elif variant == "NEGATIVE":
        sub = rng.choice(("INDEPENDENT_SECOND_FAMILY", "K_STILL_SATISFIED")); feats["sub"] = sub
        fam = _single_family_with_two(b, T)
        if fam is None:
            return None
        pos = [e.evidence_id for e in w.positive_evidence_of_family(fam)]
        if sub == "INDEPENDENT_SECOND_FAMILY":
            e_new = b.new_evidence(Tc, source=rng.choice(sorted(s for s in w.sources if s != "src_unused" and s != w.evidence[pos[0]].source_id)))
            b.new_family(Tc, (e_new.evidence_id,))
            events.append(Event("DEPENDENCE_DISCOVERED", {"left_id": pos[0], "right_id": pos[1], "kind": rng.choice(DEP_KINDS)}))
            if len(pos) == 3:
                events.append(Event("DEPENDENCE_DISCOVERED", {"left_id": pos[1], "right_id": pos[2], "kind": rng.choice(DEP_KINDS)}))
        else:
            if len(pos) < 3:
                fam.evidence_ids = tuple(fam.evidence_ids) + (b.new_evidence(Tc).evidence_id,)
                pos = [e.evidence_id for e in w.positive_evidence_of_family(fam)]
            events.append(Event("DEPENDENCE_DISCOVERED", {"left_id": pos[0], "right_id": pos[1], "kind": rng.choice(DEP_KINDS)}))
        req = _defeat(T)
    else:
        fam = _single_family_with_two(b, T)
        if fam is None:
            return None
        pos = [e.evidence_id for e in w.positive_evidence_of_family(fam)]
        events.append(Event("DEPENDENCE_SUSPECTED", {"left_id": pos[0], "right_id": pos[1], "kind": rng.choice(DEP_KINDS)}))
        if len(pos) == 3:
            events.append(Event("DEPENDENCE_SUSPECTED", {"left_id": pos[1], "right_id": pos[2], "kind": rng.choice(DEP_KINDS)}))
        feats["sub"] = "SUSPECTED"
        req = _defeat(T)
    return events, req, feats


def inv_C(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        if f["sub"] == "REOPEN":
            return exp.action == SELECTIVELY_REOPEN and f["target"] in exp.reopened and (not f.get("decoy") or f["decoy"] not in exp.reopened)
        return exp.action == REQUEST_NEW_EVIDENCE and exp.decisive_atom.startswith("support:")
    if variant == "NEGATIVE":
        return exp.action == PRESERVE
    return exp.action == DEFER_CANNOT_CHECK


def plant_D(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    donor_ctx = rng.choice([c for c in CONTEXTS if c != Tc.context_id])
    key = w.relation_key(donor_ctx, Tc.context_id)
    req_rel = rng.choice(("PREDICTIVELY_EQUIVALENT", "DECISION_DOMINATES", "BEHAVIORALLY_EQUIVALENT"))
    e_d = b.new_evidence(Tc, context=donor_ctx)
    r = b.new_result(Tc, (e_d.evidence_id,), context=donor_ctx, required_relation=req_rel)
    req = _accept(T, r.result_id)
    feats["donor_context"] = donor_ctx; feats["required"] = req_rel
    if variant == "POSITIVE":
        sub = rng.choice(("RETYPED_BELOW", "RETYPED_BELOW", "ABSENT")); feats["sub"] = sub
        if sub == "ABSENT":
            w.relations.pop(key, None)
        else:
            w.relations[key] = Relation(donor_ctx, Tc.context_id, "ISOMORPHIC")
            weaker = [x for x, k in RELATION_RANK.items() if k < RELATION_RANK[req_rel]]
            events.append(Event("RELATION_RETYPED", {"source_context": donor_ctx, "target_context": Tc.context_id, "relation_type": rng.choice(weaker)}))
        others = [k for k in sorted(w.relations) if k != key]
        if others and rng.random() < 0.6:
            o = w.relations[rng.choice(others)]
            events.append(Event("RELATION_RETYPED", {"source_context": o.source_context, "target_context": o.target_context, "relation_type": "ISOMORPHIC"}, note="decoy"))
    elif variant == "NEGATIVE":
        feats["sub"] = "TYPED_VALID_TRANSPORT"
        adequate = [x for x, k in RELATION_RANK.items() if k >= RELATION_RANK[req_rel]]
        w.relations[key] = Relation(donor_ctx, Tc.context_id, rng.choice(adequate))
        others = [k for k in sorted(w.relations) if k != key]
        if others and rng.random() < 0.6:
            o = w.relations[rng.choice(others)]
            events.append(Event("RELATION_RETYPED", {"source_context": o.source_context, "target_context": o.target_context, "relation_type": "APPROXIMATELY_EQUIVALENT"}, note="decoy: another relation weakened"))
        else:
            d = _decoy_event(b, {T})
            if d:
                events.append(d)
    else:
        feats["sub"] = "RELATION_CANNOT_CHECK"
        w.relations[key] = Relation(donor_ctx, Tc.context_id, "ISOMORPHIC")
        events.append(Event("RELATION_RETYPED", {"source_context": donor_ctx, "target_context": Tc.context_id, "relation_type": RELATION_CANNOT_CHECK}))
    return events, req, feats


def inv_D(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        return exp.action == BLOCK_TRANSPORT
    if variant == "NEGATIVE":
        return exp.action == UPDATE
    return exp.action == DEFER_CANNOT_CHECK and BLOCK_TRANSPORT in exp.action_set


def plant_E(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    s = rng.choice(sorted(x for x in w.sources if x != "src_unused"))
    if variant == "POSITIVE":
        sub = rng.choice(("OWN_ROUTES", "PREREQUISITE")); feats["sub"] = sub
        if sub == "OWN_ROUTES":
            firsts = [f.evidence_ids[0] for f in w.families_of(T) if f.evidence_ids]
            for f in w.families_of(T):
                if not f.evidence_ids:
                    del w.families[f.family_id]
            _assign_source_exclusive(b, firsts, s, set(w.accepted_ids()) - {T})
        else:
            P = Tc
            deps = [c for c in ts if c != T and T not in {p for f in w.families_of(c) for p in f.prerequisite_ids}]
            # T becomes the prerequisite of a fresh downstream claim Q via all of Q's routes
            Q = Claim("q_down", Tc.context_id, Tc.failure_class, Tc.scope, f"K_q_down", True, intended_spec_id="SPEC_q_down")
            w.claims["q_down"] = Q
            e_q = b.new_evidence(Q)
            b.new_family(Q, (e_q.evidence_id,), (T,))
            firsts = [f.evidence_ids[0] for f in w.families_of(T) if f.evidence_ids]
            for f in w.families_of(T):
                if not f.evidence_ids:
                    del w.families[f.family_id]
            _assign_source_exclusive(b, firsts, s, set(w.accepted_ids()) - {T})
            feats["downstream"] = "q_down"
        events.append(Event("SOURCE_RETRACTED", {"source_id": s}))
        req = _defeat(T)
    elif variant == "NEGATIVE":
        feats["sub"] = "INDEPENDENT_ROUTE_REMAINS"
        fams = [f for f in w.families_of(T) if f.evidence_ids]
        if len(fams) < 2:
            e_new = b.new_evidence(Tc); b.new_family(Tc, (e_new.evidence_id,)); fams = [f for f in w.families_of(T) if f.evidence_ids]
        hit = fams[0]
        _assign_source_exclusive(b, [hit.evidence_ids[0]], s, set(w.accepted_ids()))
        events.append(Event("SOURCE_RETRACTED", {"source_id": s}))
        req = _defeat(T)
    else:
        feats["sub"] = "RETRACTION_DISPUTED"
        firsts = [f.evidence_ids[0] for f in w.families_of(T) if f.evidence_ids]
        for f in w.families_of(T):
            if not f.evidence_ids:
                del w.families[f.family_id]
        _assign_source_exclusive(b, firsts, s, set(w.accepted_ids()) - {T})
        events.append(Event("SOURCE_RETRACTION_DISPUTED", {"source_id": s}))
        req = _defeat(T)
    feats["source"] = s
    return events, req, feats


def inv_E(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        ok = exp.action == SELECTIVELY_REOPEN and f["target"] in exp.reopened
        if f["sub"] == "PREREQUISITE":
            ok &= f["downstream"] in exp.reopened
        return ok
    if variant == "NEGATIVE":
        return exp.action == PRESERVE
    return exp.action == DEFER_CANNOT_CHECK


def plant_F(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    r = b.new_result(Tc)
    req = _accept(T, r.result_id)
    if variant == "POSITIVE":
        sub = rng.choice(("BLIND_WITH_ALTERNATIVE", "BLIND_WITH_ALTERNATIVE", "CONTRACT_INVALIDATED")); feats["sub"] = sub
        if sub == "CONTRACT_INVALIDATED":
            events.append(Event("EVALUATOR_INVALIDATED", {"evaluator_id": r.evaluator_id}))
        else:
            # the result's evaluator loses coverage of the claim's failure class; ev0 still covers it
            r.evaluator_id = "ev_narrow"
            w.evaluators["ev_narrow"] = Evaluator("ev_narrow", tuple(FAILURE_CLASSES))
            events.append(Event("EVALUATOR_COVERAGE_CHANGED", {"evaluator_id": "ev_narrow", "coverage": [x for x in FAILURE_CLASSES if x != Tc.failure_class], "uncertain": []}, note="constructed without the failure class"))
    elif variant == "NEGATIVE":
        feats["sub"] = "COVERED_WITH_DECOY"
        other = rng.choice([e for e in ("ev1", "ev2") if e != r.evaluator_id] or ["ev2"])
        events.append(Event("EVALUATOR_COVERAGE_CHANGED", {"evaluator_id": other, "coverage": [x for x in FAILURE_CLASSES if x != Tc.failure_class][:1], "uncertain": []}, note="decoy: an evaluator not used by the result narrowed"))
    else:
        sub = rng.choice(("BLIND_NO_ALTERNATIVE", "COVERAGE_UNCERTAIN", "CONTRACT_UNDER_REVIEW")); feats["sub"] = sub
        if sub == "BLIND_NO_ALTERNATIVE":
            new_fc = "FC_RARE"
            events.append(Event("CLAIM_FAILURE_CLASS_CHANGED", {"claim_id": T, "failure_class": new_fc}, note="safety conclusion re-scoped to a failure class no evaluator was built for"))
        elif sub == "COVERAGE_UNCERTAIN":
            ev = w.evaluators[r.evaluator_id]
            events.append(Event("EVALUATOR_COVERAGE_CHANGED", {"evaluator_id": r.evaluator_id, "coverage": [x for x in ev.coverage if x != Tc.failure_class], "uncertain": [Tc.failure_class]}))
        else:
            events.append(Event("EVALUATOR_UNDER_REVIEW", {"evaluator_id": r.evaluator_id}))
    return events, req, feats


def inv_F(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        return exp.action == REPLACE_OR_CHALLENGE_EVALUATOR
    if variant == "NEGATIVE":
        return exp.action == UPDATE
    return exp.action == DEFER_CANNOT_CHECK and REPLACE_OR_CHALLENGE_EVALUATOR in exp.action_set


def plant_G(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    r = b.new_result(Tc)
    if variant == "POSITIVE":
        sub = rng.choice(("CEILING_LOWERED", "EXTERNAL_REQUIRED")); feats["sub"] = sub
        if sub == "CEILING_LOWERED":
            events.append(Event("AUTHORITY_POLICY_CHANGED", {"ceiling_level": AUTHORITY_BELIEF, "status": "VALID"}))
            req = _accept(T, r.result_id, level=AUTHORITY_OPERATIONAL)
        else:
            req = _accept(T, r.result_id, level=AUTHORITY_EXTERNAL)
    elif variant == "NEGATIVE":
        sub = rng.choice(("WITHIN_CEILING", "CEILING_RAISED")); feats["sub"] = sub
        if sub == "CEILING_RAISED":
            events.append(Event("AUTHORITY_POLICY_CHANGED", {"ceiling_level": AUTHORITY_EXTERNAL, "status": "VALID"}))
            req = _accept(T, r.result_id, level=AUTHORITY_EXTERNAL)
        else:
            req = _accept(T, r.result_id, level=AUTHORITY_OPERATIONAL)
            d = _decoy_event(b, {T})
            if d and d.kind != "AUTHORITY_POLICY_CHANGED":
                events.append(d)
    else:
        feats["sub"] = "POLICY_UNDER_REVIEW"
        events.append(Event("AUTHORITY_POLICY_CHANGED", {"status": AUTH_UNDER_REVIEW}))
        req = _accept(T, r.result_id, level=AUTHORITY_OPERATIONAL)
    return events, req, feats


def inv_G(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        return exp.action == ABSTAIN_AUTHORITY
    if variant == "NEGATIVE":
        return exp.action == UPDATE
    return exp.action == DEFER_CANNOT_CHECK and ABSTAIN_AUTHORITY in exp.action_set


def plant_H(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    if variant == "POSITIVE":
        sub = rng.choice(("UNFAITHFUL", "UNFAITHFUL", "CHECKER_INVALID")); feats["sub"] = sub
        if sub == "UNFAITHFUL":
            r = b.new_result(Tc, proved_spec_id=f"{Tc.intended_spec_id}_weakened", checker_status=CHECKER_VALID)
            events.append(Event("SPEC_FIDELITY_ASSESSED", {"proved_spec_id": r.proved_spec_id, "intended_spec_id": Tc.intended_spec_id, "status": FIDELITY_UNFAITHFUL}, note="a condition was dropped during autoformalization"))
        else:
            r = b.new_result(Tc, proved_spec_id=Tc.intended_spec_id, checker_status=CHECKER_INVALID)
    elif variant == "NEGATIVE":
        sub = rng.choice(("IDENTICAL_SPEC", "FAITHFUL_REFINEMENT")); feats["sub"] = sub
        if sub == "IDENTICAL_SPEC":
            r = b.new_result(Tc, proved_spec_id=Tc.intended_spec_id, checker_status=CHECKER_VALID)
        else:
            r = b.new_result(Tc, proved_spec_id=f"{Tc.intended_spec_id}_refined", checker_status=CHECKER_VALID)
            events.append(Event("SPEC_FIDELITY_ASSESSED", {"proved_spec_id": r.proved_spec_id, "intended_spec_id": Tc.intended_spec_id, "status": FIDELITY_FAITHFUL}))
        d = _decoy_event(b, {T})
        if d:
            events.append(d)
    else:
        sub = rng.choice(("FIDELITY_UNCHECKED", "CHECKER_UNKNOWN")); feats["sub"] = sub
        if sub == "FIDELITY_UNCHECKED":
            r = b.new_result(Tc, proved_spec_id=f"{Tc.intended_spec_id}_variant", checker_status=CHECKER_VALID)
        else:
            r = b.new_result(Tc, proved_spec_id=Tc.intended_spec_id, checker_status=CHECKER_UNKNOWN)
    req = _accept(T, r.result_id)
    return events, req, feats


def inv_H(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        return (exp.action == REVALIDATE and exp.decisive_atom.startswith("spec:")) if f["sub"] == "UNFAITHFUL" else (exp.action == REQUEST_NEW_EVIDENCE and exp.decisive_atom.startswith("checker:"))
    if variant == "NEGATIVE":
        return exp.action == UPDATE
    return exp.action == DEFER_CANNOT_CHECK


def plant_I(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    acc = list(w.accepted_ids())
    if len(acc) < 2:
        return None
    pieces = sorted(rng.sample(acc, min(len(acc), rng.choice((2, 3)))))
    G = Claim("g0", w.claims[pieces[0]].context_id, w.claims[pieces[0]].failure_class, ("S1",), "K_g0", False, intended_spec_id="SPEC_g0")
    w.claims["g0"] = G
    b.new_family(G, (), tuple(pieces))
    ovs = []
    for i in range(len(pieces)):
        for j in range(i + 1, len(pieces)):
            oid = f"o:{pieces[i]}:{pieces[j]}"
            w.overlaps[oid] = Overlap(oid, pieces[i], pieces[j], True, f"w:{oid}"); ovs.append(oid)
    feats: dict[str, Any] = {"target": "g0", "pieces": pieces}
    events: list[Event] = []
    req = TransitionRequest("CLOSE_GLOBAL", "g0", "", "", AUTHORITY_BELIEF)
    if variant == "POSITIVE":
        feats["sub"] = "OBSTRUCTION"
        o = rng.choice(ovs)
        if rng.random() < 0.5:
            events.append(Event("OVERLAP_ASSESSED", {"overlap_id": o, "compatible": False, "witness_id": f"w:{o}"}, note="explicit obstruction"))
        else:
            w.overlaps[o].compatible = False
        if rng.random() < 0.5:
            G.global_witness_id = "gw0"
    elif variant == "NEGATIVE":
        feats["sub"] = "WITNESSED"
        if rng.random() < 0.5:
            events.append(Event("GLOBAL_WITNESS_REGISTERED", {"claim_id": "g0", "witness_id": "gw0"}))
        else:
            G.global_witness_id = "gw0"
        d = _decoy_event(b, set(pieces) | {"g0"})
        if d:
            events.append(d)
    else:
        sub = rng.choice(("WITNESS_ABSENT", "WITNESS_ABSENT", "OVERLAP_UNRESOLVED")); feats["sub"] = sub
        if sub == "OVERLAP_UNRESOLVED":
            o = rng.choice(ovs); w.overlaps[o].compatible = None; w.overlaps[o].witness_id = ""
            G.global_witness_id = "gw0"
    return events, req, feats


def inv_I(exp: Expected, f: dict, w: World, variant: str) -> bool:
    if variant == "POSITIVE":
        return exp.action == REFORMULATE_PROBLEM and exp.decisive_atom.startswith("overlap:")
    if variant == "NEGATIVE":
        return exp.action == UPDATE
    return exp.action == DEFER_CANNOT_CHECK


def plant_J(b: _Builder, variant: str):
    rng, w = b.rng, b.w
    ts = _targets(w)
    T = rng.choice(ts); Tc = w.claims[T]
    feats: dict[str, Any] = {"target": T}
    events: list[Event] = []
    if variant == "POSITIVE":
        sub = rng.choice(("PLAIN", "TRANSPORTED", "OPERATIONAL", "FORMAL")); feats["sub"] = sub
        if sub == "TRANSPORTED":
            donor = rng.choice([c for c in CONTEXTS if c != Tc.context_id])
            w.relations[w.relation_key(donor, Tc.context_id)] = Relation(donor, Tc.context_id, "ISOMORPHIC")
            e_d = b.new_evidence(Tc, context=donor)
            r = b.new_result(Tc, (e_d.evidence_id,), context=donor, required_relation="PREDICTIVELY_EQUIVALENT")
            req = _accept(T, r.result_id)
        elif sub == "OPERATIONAL":
            r = b.new_result(Tc); req = _accept(T, r.result_id, level=AUTHORITY_OPERATIONAL)
        elif sub == "FORMAL":
            r = b.new_result(Tc, proved_spec_id=Tc.intended_spec_id, checker_status=CHECKER_VALID); req = _accept(T, r.result_id)
        else:
            r = b.new_result(Tc); req = _accept(T, r.result_id)
        for _ in range(rng.choice((1, 2))):
            d = _decoy_event(b, {T})
            if d:
                events.append(d)
    elif variant == "NEGATIVE":
        sub = rng.choice(("PARTIAL_FAMILY_FAILURE", "K_SATISFIED_DEPENDENCE", "UNRELATED_RETRACTION")); feats["sub"] = sub
        if sub == "PARTIAL_FAMILY_FAILURE":
            fams = [f for f in w.families_of(T) if f.evidence_ids]
            if len(fams) < 2:
                e_new = b.new_evidence(Tc); b.new_family(Tc, (e_new.evidence_id,)); fams = [f for f in w.families_of(T) if f.evidence_ids]
            s = rng.choice(sorted(x for x in w.sources if x != "src_unused"))
            _assign_source_exclusive(b, [fams[0].evidence_ids[0]], s, set(w.accepted_ids()))
            events.append(Event("SOURCE_RETRACTED", {"source_id": s}))
        elif sub == "K_SATISFIED_DEPENDENCE":
            fam = _first_evidence_family(w, T)
            while len(w.positive_evidence_of_family(fam)) < 3:
                fam.evidence_ids = tuple(fam.evidence_ids) + (b.new_evidence(Tc).evidence_id,)
            fam.min_independent = 2
            pos = [e.evidence_id for e in w.positive_evidence_of_family(fam)]
            events.append(Event("DEPENDENCE_DISCOVERED", {"left_id": pos[0], "right_id": pos[1], "kind": rng.choice(DEP_KINDS)}))
        else:
            events.append(Event("SOURCE_RETRACTED", {"source_id": "src_unused"}))
        req = _defeat(T)
    else:
        sub = rng.choice(("UNUSED_SOURCE_DISPUTED", "UNUSED_CALIBRATION_REVIEW", "K0_DEPENDENCE_SUSPECTED")); feats["sub"] = sub
        if sub == "UNUSED_SOURCE_DISPUTED":
            events.append(Event("SOURCE_RETRACTION_DISPUTED", {"source_id": "src_unused"}))
        elif sub == "UNUSED_CALIBRATION_REVIEW":
            events.append(Event("CALIBRATION_UNDER_REVIEW", {"calibration_id": "cal:inst_unused:0"}))
        else:
            fams = [f for f in w.families.values() if f.min_independent == 0 and len(w.positive_evidence_of_family(f)) >= 2]
            if not fams:
                fam = _first_evidence_family(w, T); fam.evidence_ids = tuple(fam.evidence_ids) + (b.new_evidence(Tc).evidence_id,); fams = [fam]
            f0 = rng.choice(sorted(fams, key=lambda x: x.family_id)); pos = [e.evidence_id for e in w.positive_evidence_of_family(f0)]
            events.append(Event("DEPENDENCE_SUSPECTED", {"left_id": pos[0], "right_id": pos[1], "kind": rng.choice(DEP_KINDS)}))
        if rng.random() < 0.5:
            r = b.new_result(Tc); req = _accept(T, r.result_id)
        else:
            req = _defeat(T)
    return events, req, feats


def inv_J(exp: Expected, f: dict, w: World, variant: str) -> bool:
    return exp.action in (UPDATE, PRESERVE) and (exp.action == PRESERVE if variant == "NEGATIVE" else True)


PLANTERS: dict[str, tuple[Callable[[_Builder, str], Any], Callable[[Expected, dict, World, str], bool]]] = {
    "X1-A_CLAIM_PROBLEM_IDENTITY": (plant_A, inv_A),
    "X1-B_MEASUREMENT_CALIBRATION": (plant_B, inv_B),
    "X1-C_HIDDEN_DEPENDENCE": (plant_C, inv_C),
    "X1-D_INVALID_TRANSPORT": (plant_D, inv_D),
    "X1-E_DEFEATED_PREREQUISITE": (plant_E, inv_E),
    "X1-F_EVALUATOR_BLINDNESS": (plant_F, inv_F),
    "X1-G_AUTHORITY_MISMATCH": (plant_G, inv_G),
    "X1-H_PROOF_WRONG_SPECIFICATION": (plant_H, inv_H),
    "X1-I_LOCAL_COMPAT_GLOBAL_OBSTRUCTION": (plant_I, inv_I),
    "X1-J_FULLY_WARRANTED": (plant_J, inv_J),
}
assert set(PLANTERS) == set(FAMILIES)


def generate_instance(split: str, split_seed: str, family: str, index: int) -> tuple[Instance, Expected]:
    seed = instance_seed(split_seed, family, index)
    rng = random.Random(seed)
    variant = variant_for(index)
    planter, invariant = PLANTERS[family]
    for attempt in range(MAX_ATTEMPTS):
        b = build_base_world(rng)
        try:
            planted = planter(b, variant)
        except (IndexError, StopIteration):
            continue
        if planted is None:
            continue
        events, req, feats = planted
        if len(events) > MAX_EVENTS:
            continue
        w0 = b.w
        try:
            w0.validate()
            if not all_accepted_supported_at_v0(w0):
                continue
            w_final, exp = expected_for(w0, events, req)
        except ValueError:
            continue
        if not exp.exhaustive_agrees:
            raise RuntimeError(f"oracle self-disagreement on {family}#{index}")
        if len(exp.unknown_atoms) > MAX_UNKNOWN_ATOMS:
            continue
        if not invariant(exp, feats, w_final, variant):
            continue
        feats = dict(feats); feats["attempts"] = attempt + 1; feats["request_kind"] = req.kind
        inst = Instance(f"{split}-{family}-{index:03d}", family, variant, split, seed, w0, events, req, feats)
        return inst, exp
    raise RuntimeError(f"could not plant {family}/{variant} within {MAX_ATTEMPTS} attempts (seed {seed})")


def generate_split(split: str, split_seed: str, per_family: dict[str, int]) -> list[tuple[Instance, Expected]]:
    out = []
    for family in FAMILIES:
        for i in range(per_family.get(family, 0)):
            out.append(generate_instance(split, split_seed, family, i))
    return out


# ---- hand-authored known-answer fixtures (G0a) ---------------------------------

def _mini_world() -> World:
    w = World()
    for s in ("sA", "sB", "sC", "sD"):
        w.sources[s] = SOURCE_VALID
    w.calibrations["cal1"] = Calibration("cal1", "inst"); w.calibrations["cal2"] = Calibration("cal2", "inst")
    w.evaluators["evX"] = Evaluator("evX", ("FC_A", "FC_B"))
    w.relations["ctx1->ctx0"] = Relation("ctx1", "ctx0", "BEHAVIORALLY_EQUIVALENT")
    w.authority = AuthorityPolicy(AUTHORITY_OPERATIONAL, "VALID")
    return w


def _claim(w: World, cid: str, fc: str = "FC_A", scope=("S1",), ctx: str = "ctx0", accepted: bool = True, spec: str = "") -> Claim:
    c = Claim(cid, ctx, fc, tuple(scope), f"K_{cid}", accepted, intended_spec_id=spec or f"SPEC_{cid}"); w.claims[cid] = c; return c


def _ev(w: World, eid: str, cid: str, src: str, *, ctx: str = "ctx0", cal: str = "", ev: str = "", supports: bool = True) -> str:
    w.evidence[eid] = Evidence(eid, cid, src, ctx, ("S1",), ev, cal, supports=supports); return eid


def _fam(w: World, fid: str, cid: str, evs, prereqs=(), k: int = 0, req: str = "") -> str:
    w.families[fid] = Family(fid, cid, tuple(evs), tuple(prereqs), k, req); return fid


def _res(w: World, rid: str, bound: str, basis, *, ctx: str = "ctx0", ev: str = "evX", **kw) -> str:
    w.results[rid] = Result(rid, bound, tuple(basis), ctx, ev, **kw); return rid


def known_answer_fixtures() -> list[dict[str, Any]]:
    """The 14 public development cases of
    ME_X1_X2_DEVELOPMENT_KNOWN_ANSWER_FIXTURES_V1.json bound to concrete
    registered worlds; expected actions are the fixture file's labels."""
    fx: list[dict[str, Any]] = []

    # X1-DEV-001 claim binding error: solver output for model B attached to claim A
    w = _mini_world(); _claim(w, "cA"); _claim(w, "cB")
    _fam(w, "cA.F1", "cA", [_ev(w, "e1", "cA", "sA", ev="evX")]); _fam(w, "cB.F1", "cB", [_ev(w, "e2", "cB", "sB", ev="evX")])
    _res(w, "r1", "cB", ["e2"])
    fx.append({"case_id": "X1-DEV-001", "family": "X1-A_CLAIM_PROBLEM_IDENTITY", "world": w, "events": [], "request": TransitionRequest("ACCEPT_RESULT", "cA", "r1"), "expected": REVALIDATE, "forbidden": [UPDATE]})

    # X1-DEV-002 correct binding, evaluator covers
    w = _mini_world(); _claim(w, "cA"); _fam(w, "cA.F1", "cA", [_ev(w, "e1", "cA", "sA", ev="evX")]); _res(w, "r1", "cA", ["e1"])
    fx.append({"case_id": "X1-DEV-002", "family": "X1-A_CLAIM_PROBLEM_IDENTITY", "world": w, "events": [], "request": TransitionRequest("ACCEPT_RESULT", "cA", "r1"), "expected": UPDATE, "negative_control": True})

    # X1-DEV-003 calibration curve invalidated
    w = _mini_world(); _claim(w, "cA"); _fam(w, "cA.F1", "cA", [_ev(w, "e1", "cA", "sA", cal="cal1", ev="evX")]); _res(w, "r1", "cA", ["e1"])
    fx.append({"case_id": "X1-DEV-003", "family": "X1-B_MEASUREMENT_CALIBRATION", "world": w, "events": [Event("CALIBRATION_INVALIDATED", {"calibration_id": "cal1"})], "request": TransitionRequest("ACCEPT_RESULT", "cA", "r1"), "expected": REVALIDATE, "forbidden": [UPDATE]})

    # X1-DEV-004 three supports share a dataset; claim required two independent routes; c2 depends on c1 via all routes, c3 independent
    w = _mini_world(); _claim(w, "c1"); _claim(w, "c2"); _claim(w, "c3")
    _fam(w, "c1.F1", "c1", [_ev(w, "e1", "c1", "sA"), _ev(w, "e2", "c1", "sB"), _ev(w, "e3", "c1", "sC")], k=2)
    _fam(w, "c2.F1", "c2", [], prereqs=["c1"]); _fam(w, "c3.F1", "c3", [_ev(w, "e4", "c3", "sD")])
    evs = [Event("DEPENDENCE_DISCOVERED", {"left_id": "e1", "right_id": "e2", "kind": "SHARED_DATA"}), Event("DEPENDENCE_DISCOVERED", {"left_id": "e2", "right_id": "e3", "kind": "SHARED_DATA"})]
    fx.append({"case_id": "X1-DEV-004", "family": "X1-C_HIDDEN_DEPENDENCE", "world": w, "events": evs, "request": TransitionRequest("PROPAGATE_DEFEAT", "c1", challenged_event_index=0), "expected": SELECTIVELY_REOPEN, "expected_reopened": ["c1", "c2"], "preserved": ["c3"]})

    # X1-DEV-005 independent routes remain (decoy dependence on a family without requirement)
    w = _mini_world(); _claim(w, "c1"); _claim(w, "c3")
    _fam(w, "c1.F1", "c1", [_ev(w, "e1", "c1", "sA"), _ev(w, "e2", "c1", "sB"), _ev(w, "e3", "c1", "sC")], k=2)
    _fam(w, "c3.F1", "c3", [_ev(w, "e4", "c3", "sD"), _ev(w, "e5", "c3", "sA")], k=0)
    evs = [Event("DEPENDENCE_DISCOVERED", {"left_id": "e4", "right_id": "e5", "kind": "SHARED_SOURCE"})]
    fx.append({"case_id": "X1-DEV-005", "family": "X1-C_HIDDEN_DEPENDENCE", "world": w, "events": evs, "request": TransitionRequest("PROPAGATE_DEFEAT", "c1", challenged_event_index=0), "expected": PRESERVE, "negative_control": True})

    # X1-DEV-006 invalid transport: effect modifier differs outside scope -> relation below required
    w = _mini_world(); _claim(w, "cT"); _fam(w, "cT.F1", "cT", [_ev(w, "e1", "cT", "sA", ev="evX")]); _ev(w, "e2", "cT", "sB", ctx="ctx1", ev="evX")
    _res(w, "r1", "cT", ["e2"], ctx="ctx1", required_relation="PREDICTIVELY_EQUIVALENT")
    evs = [Event("RELATION_RETYPED", {"source_context": "ctx1", "target_context": "ctx0", "relation_type": "APPROXIMATELY_EQUIVALENT"})]
    fx.append({"case_id": "X1-DEV-006", "family": "X1-D_INVALID_TRANSPORT", "world": w, "events": evs, "request": TransitionRequest("ACCEPT_RESULT", "cT", "r1"), "expected": BLOCK_TRANSPORT, "forbidden": [UPDATE]})

    # X1-DEV-007 one route retracted, a second independent sufficient route remains
    w = _mini_world(); _claim(w, "q"); _fam(w, "q.F1", "q", [_ev(w, "e1", "q", "sA")]); _fam(w, "q.F2", "q", [_ev(w, "e2", "q", "sB")])
    fx.append({"case_id": "X1-DEV-007", "family": "X1-E_DEFEATED_PREREQUISITE", "world": w, "events": [Event("SOURCE_RETRACTED", {"source_id": "sA"})], "request": TransitionRequest("PROPAGATE_DEFEAT", "q", challenged_event_index=0), "expected": PRESERVE, "negative_control": True})

    # X1-DEV-008 every sufficient route for Q depends on a calibration theorem P whose support is now false
    w = _mini_world(); _claim(w, "p_cal"); _claim(w, "q"); _claim(w, "z")
    _fam(w, "p_cal.F1", "p_cal", [_ev(w, "e1", "p_cal", "sA")])
    _fam(w, "q.F1", "q", [_ev(w, "e2", "q", "sB")], prereqs=["p_cal"]); _fam(w, "q.F2", "q", [_ev(w, "e3", "q", "sC")], prereqs=["p_cal"])
    _fam(w, "z.F1", "z", [_ev(w, "e4", "z", "sD")])
    fx.append({"case_id": "X1-DEV-008", "family": "X1-E_DEFEATED_PREREQUISITE", "world": w, "events": [Event("SOURCE_RETRACTED", {"source_id": "sA"})], "request": TransitionRequest("PROPAGATE_DEFEAT", "q", challenged_event_index=0), "expected": SELECTIVELY_REOPEN, "expected_reopened": ["p_cal", "q"], "preserved": ["z"]})

    # X1-DEV-009 benchmark constructed without the rare failure mode; no registered evaluator covers it
    w = _mini_world(); _claim(w, "cS", fc="FC_A"); _fam(w, "cS.F1", "cS", [_ev(w, "e1", "cS", "sA", ev="evX")]); _res(w, "r1", "cS", ["e1"])
    evs = [Event("CLAIM_FAILURE_CLASS_CHANGED", {"claim_id": "cS", "failure_class": "FC_RARE"})]
    fx.append({"case_id": "X1-DEV-009", "family": "X1-F_EVALUATOR_BLINDNESS", "world": w, "events": evs, "request": TransitionRequest("ACCEPT_RESULT", "cS", "r1"), "expected": DEFER_CANNOT_CHECK})

    # X1-DEV-010 belief update warranted, no authority for a clinical operating protocol
    w = _mini_world(); _claim(w, "cC"); _fam(w, "cC.F1", "cC", [_ev(w, "e1", "cC", "sA", ev="evX")]); _res(w, "r1", "cC", ["e1"])
    w.authority = AuthorityPolicy(AUTHORITY_BELIEF, "VALID")
    fx.append({"case_id": "X1-DEV-010", "family": "X1-G_AUTHORITY_MISMATCH", "world": w, "events": [], "request": TransitionRequest("ACCEPT_RESULT", "cC", "r1", "", AUTHORITY_OPERATIONAL), "expected": ABSTAIN_AUTHORITY, "belief_update_warranted": True})

    # X1-DEV-011 Lean verifies a weakened statement
    w = _mini_world(); _claim(w, "thm", spec="SPEC_thm"); _fam(w, "thm.F1", "thm", [_ev(w, "e1", "thm", "sA", ev="evX")])
    _res(w, "r1", "thm", ["e1"], proved_spec_id="SPEC_thm_dropped_condition", checker_status=CHECKER_VALID)
    evs = [Event("SPEC_FIDELITY_ASSESSED", {"proved_spec_id": "SPEC_thm_dropped_condition", "intended_spec_id": "SPEC_thm", "status": FIDELITY_UNFAITHFUL})]
    fx.append({"case_id": "X1-DEV-011", "family": "X1-H_PROOF_WRONG_SPECIFICATION", "world": w, "events": evs, "request": TransitionRequest("ACCEPT_RESULT", "thm", "r1"), "expected": REVALIDATE})

    # X1-DEV-012 three local models pairwise compatible; global witness absent
    w = _mini_world(); _claim(w, "m1"); _claim(w, "m2"); _claim(w, "m3"); _claim(w, "g", accepted=False)
    _fam(w, "m1.F1", "m1", [_ev(w, "e1", "m1", "sA")]); _fam(w, "m2.F1", "m2", [_ev(w, "e2", "m2", "sB")]); _fam(w, "m3.F1", "m3", [_ev(w, "e3", "m3", "sC")])
    _fam(w, "g.F1", "g", [], prereqs=["m1", "m2", "m3"])
    for a, bb in (("m1", "m2"), ("m1", "m3"), ("m2", "m3")):
        w.overlaps[f"o:{a}:{bb}"] = Overlap(f"o:{a}:{bb}", a, bb, True, f"w:{a}:{bb}")
    fx.append({"case_id": "X1-DEV-012", "family": "X1-I_LOCAL_COMPAT_GLOBAL_OBSTRUCTION", "world": w, "events": [], "request": TransitionRequest("CLOSE_GLOBAL", "g"), "expected": DEFER_CANNOT_CHECK, "local_pairwise_compatibility": True})

    # X1-DEV-013 fully warranted update (identity, provenance, dependence, calibration, evaluator, transport, authority)
    w = _mini_world(); _claim(w, "cW"); _fam(w, "cW.F1", "cW", [_ev(w, "e1", "cW", "sA", cal="cal1", ev="evX"), _ev(w, "e2", "cW", "sB", cal="cal2", ev="evX")], k=2)
    _ev(w, "e3", "cW", "sC", ctx="ctx1", ev="evX")
    _res(w, "r1", "cW", ["e1", "e2", "e3"], ctx="ctx1", min_independent=2, required_relation="DECISION_DOMINATES", comparability_status=COMP_COMPARABLE)
    fx.append({"case_id": "X1-DEV-013", "family": "X1-J_FULLY_WARRANTED", "world": w, "events": [Event("SOURCE_RETRACTED", {"source_id": "sD"}, note="unused source")], "request": TransitionRequest("ACCEPT_RESULT", "cW", "r1", "", AUTHORITY_OPERATIONAL), "expected": UPDATE, "negative_control": True})

    # X1-DEV-014 result quoted correctly but the exact source artifact cannot be recovered
    w = _mini_world(); _claim(w, "cQ"); _fam(w, "cQ.F1", "cQ", [_ev(w, "e1", "cQ", "sA", ev="evX")]); _res(w, "r1", "cQ", ["e1"])
    fx.append({"case_id": "X1-DEV-014", "family": "X1-A_CLAIM_PROBLEM_IDENTITY", "world": w, "events": [Event("EVIDENCE_IDENTITY_LOST", {"evidence_id": "e1"})], "request": TransitionRequest("ACCEPT_RESULT", "cQ", "r1"), "expected": DEFER_CANNOT_CHECK})

    for f in fx:
        f["world"].validate()
    return fx


def separation_pair() -> tuple[dict[str, Any], dict[str, Any]]:
    """H-EXT-3 finite separation example (family C/E composition, ME-X4 P/Q
    recast as a PROPAGATE_DEFEAT transition).

    P: c has F1={e1,e2 | k=2} and F2={e3 transported via ctx1->ctx0, requires PREDICTIVELY_EQUIVALENT}.
    Q: c has F1={e1,e2,e3(transported) | k=2 over e1,e2} and F2={e4 native}.
    Events (identical): dependence discovered (e1,e2) AND relation ctx1->ctx0 downgraded.
    Per-module family-anonymous verdicts are identical in P and Q (DEP: defeats some,
    TRANS: defeats some, others none) but the oracle differs:
    P -> SELECTIVELY_REOPEN {c}; Q -> PRESERVE."""
    events = [Event("DEPENDENCE_DISCOVERED", {"left_id": "e1", "right_id": "e2", "kind": "SHARED_DATA"}), Event("RELATION_RETYPED", {"source_context": "ctx1", "target_context": "ctx0", "relation_type": "APPROXIMATELY_EQUIVALENT"})]
    p = _mini_world(); _claim(p, "c")
    _fam(p, "c.F1", "c", [_ev(p, "e1", "c", "sA"), _ev(p, "e2", "c", "sB")], k=2)
    _fam(p, "c.F2", "c", [_ev(p, "e3", "c", "sC", ctx="ctx1")], req="PREDICTIVELY_EQUIVALENT")
    q = _mini_world(); _claim(q, "c")
    _fam(q, "c.F1", "c", [_ev(q, "e1", "c", "sA"), _ev(q, "e2", "c", "sB"), _ev(q, "e3", "c", "sC", ctx="ctx1")], k=2, req="PREDICTIVELY_EQUIVALENT")
    _fam(q, "c.F2", "c", [_ev(q, "e4", "c", "sD")])
    p.validate(); q.validate()
    req = TransitionRequest("PROPAGATE_DEFEAT", "c", challenged_event_index=0)
    return ({"name": "SEP-P", "world": p, "events": events, "request": req, "expected": SELECTIVELY_REOPEN, "expected_reopened": ["c"]},
            {"name": "SEP-Q", "world": q, "events": events, "request": req, "expected": PRESERVE, "expected_reopened": []})
