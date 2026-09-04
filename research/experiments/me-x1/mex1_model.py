#!/usr/bin/env python3
"""ME-X1 registered-information model (frozen with design V1).

Everything here is *registered information*: the epistemic state every arm
receives (a versioned support graph plus the request-level records of the
candidate transition), and the typed event vocabulary that updates it. No
answer key lives here. The oracle (mex1_oracle.py) interprets this model under
the frozen S2 semantics; arms interpret it under their own semantics.

Design: research/experiments/me-x1/ME_X1_TRANSITION_COUPLING_EXACT_STUDY_DESIGN_V1.{md,json}
"""
from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field
from typing import Any

# ---- registered transition action set (protocol S2) -------------------------
ACTIONS: tuple[str, ...] = (
    "UPDATE",
    "PRESERVE",
    "SELECTIVELY_REOPEN",
    "REVALIDATE",
    "REQUEST_NEW_EVIDENCE",
    "BLOCK_TRANSPORT",
    "REFORMULATE_PROBLEM",
    "REPLACE_OR_CHALLENGE_EVALUATOR",
    "DEFER_CANNOT_CHECK",
    "ABSTAIN_AUTHORITY",
)
UPDATE, PRESERVE, SELECTIVELY_REOPEN, REVALIDATE, REQUEST_NEW_EVIDENCE = ACTIONS[:5]
BLOCK_TRANSPORT, REFORMULATE_PROBLEM, REPLACE_OR_CHALLENGE_EVALUATOR, DEFER_CANNOT_CHECK, ABSTAIN_AUTHORITY = ACTIONS[5:]

# ---- case families (protocol S3) ----------------------------------------------
FAMILIES: tuple[str, ...] = (
    "X1-A_CLAIM_PROBLEM_IDENTITY",
    "X1-B_MEASUREMENT_CALIBRATION",
    "X1-C_HIDDEN_DEPENDENCE",
    "X1-D_INVALID_TRANSPORT",
    "X1-E_DEFEATED_PREREQUISITE",
    "X1-F_EVALUATOR_BLINDNESS",
    "X1-G_AUTHORITY_MISMATCH",
    "X1-H_PROOF_WRONG_SPECIFICATION",
    "X1-I_LOCAL_COMPAT_GLOBAL_OBSTRUCTION",
    "X1-J_FULLY_WARRANTED",
)
VARIANTS: tuple[str, ...] = ("POSITIVE", "NEGATIVE", "AMBIGUITY")
# per 10 consecutive indices: 5 positive, 3 negative, 2 ambiguity (frozen schedule)
VARIANT_CYCLE: tuple[str, ...] = ("POSITIVE", "NEGATIVE", "AMBIGUITY", "POSITIVE", "NEGATIVE", "POSITIVE", "POSITIVE", "NEGATIVE", "POSITIVE", "AMBIGUITY")

REQUEST_KINDS: tuple[str, ...] = ("ACCEPT_RESULT", "PROPAGATE_DEFEAT", "CLOSE_GLOBAL")

# Frozen strength order over orion_v2.structural.RelationType names used for
# typed transport (identical to ME-X4). CANNOT_CHECK is the censored status.
RELATION_RANK: dict[str, int] = {
    "ISOMORPHIC": 5,
    "BEHAVIORALLY_EQUIVALENT": 4,
    "PREDICTIVELY_EQUIVALENT": 3,
    "DECISION_DOMINATES": 2,
    "APPROXIMATELY_EQUIVALENT": 1,
    "INCOMPARABLE": 0,
    "DISTINGUISHED_BY": 0,
}
RELATION_CANNOT_CHECK = "CANNOT_CHECK"

STATUS_VALID = "VALID"
STATUS_INVALID = "INVALID"
STATUS_UNKNOWN = "UNKNOWN"

SOURCE_VALID, SOURCE_RETRACTED, SOURCE_DISPUTED = "VALID", "RETRACTED", "DISPUTED"
CAL_VALID, CAL_INVALID, CAL_UNDER_REVIEW = "VALID", "INVALID", "UNDER_REVIEW"
EVAL_VALID, EVAL_INVALID, EVAL_UNDER_REVIEW = "VALID", "INVALID", "UNDER_REVIEW"
DEP_CONFIRMED, DEP_SUSPECTED = "CONFIRMED", "SUSPECTED"
IDENTITY_RECOVERABLE, IDENTITY_UNRECOVERABLE = "RECOVERABLE", "UNRECOVERABLE"
CHECKER_VALID, CHECKER_INVALID, CHECKER_UNKNOWN = "VALID", "INVALID", "UNKNOWN"
FIDELITY_FAITHFUL, FIDELITY_UNFAITHFUL, FIDELITY_UNCHECKED = "FAITHFUL", "UNFAITHFUL", "UNCHECKED"
EQUIV_EQUIVALENT, EQUIV_NOT_EQUIVALENT, EQUIV_CANNOT_CHECK = "EQUIVALENT", "NOT_EQUIVALENT", "CANNOT_CHECK"
COMP_COMPARABLE, COMP_NONCOMPARABLE, COMP_CANNOT_CHECK = "COMPARABLE", "NONCOMPARABLE", "CANNOT_CHECK"
AUTH_VALID, AUTH_UNDER_REVIEW = "VALID", "UNDER_REVIEW"

# authority levels (ordered lattice)
AUTHORITY_NONE, AUTHORITY_BELIEF, AUTHORITY_OPERATIONAL, AUTHORITY_EXTERNAL = 0, 1, 2, 3
AUTHORITY_LEVEL_NAMES = {0: "NONE", 1: "BELIEF", 2: "OPERATIONAL", 3: "EXTERNAL"}

EVENT_KINDS: tuple[str, ...] = (
    # ME-X4 vocabulary
    "SOURCE_RETRACTED", "SOURCE_RETRACTION_DISPUTED", "SOURCE_CORRECTED",
    "CALIBRATION_INVALIDATED", "CALIBRATION_UNDER_REVIEW", "CALIBRATION_REVALIDATED",
    "DEPENDENCE_DISCOVERED", "DEPENDENCE_SUSPECTED", "RELATION_RETYPED",
    "EVALUATOR_COVERAGE_CHANGED", "CLAIM_FAILURE_CLASS_CHANGED", "FAMILY_ADDED", "EVIDENCE_ADDED",
    # ME-X1 additions (request-level registered records)
    "EVALUATOR_INVALIDATED", "EVALUATOR_UNDER_REVIEW", "EVALUATOR_REGISTERED",
    "AUTHORITY_POLICY_CHANGED", "TARGET_CHANGED",
    "OVERLAP_ASSESSED", "GLOBAL_WITNESS_REGISTERED",
    "SPEC_FIDELITY_ASSESSED", "CRITERION_EQUIVALENCE_ASSESSED",
    "RESULT_REGISTERED", "RESULT_REBOUND", "COMPARABILITY_ASSESSED", "EVIDENCE_IDENTITY_LOST",
)


@dataclass
class Claim:
    claim_id: str
    context_id: str
    failure_class: str
    scope: tuple[str, ...]
    criterion_id: str
    accepted_v0: bool = True
    intended_spec_id: str = ""
    global_witness_id: str = ""      # for global (glued) claims: registered global-section witness
    target_epoch: int = 0            # incremented by TARGET_CHANGED (ontic change, registered)


@dataclass
class Evidence:
    evidence_id: str
    claim_id: str
    source_id: str
    context_id: str
    scope_coverage: tuple[str, ...]
    evaluator_id: str = ""
    calibration_id: str = ""
    data_id: str = ""
    model_id: str = ""
    instrument_id: str = ""
    supports: bool = True
    identity_status: str = IDENTITY_RECOVERABLE


@dataclass
class Family:
    family_id: str
    claim_id: str
    evidence_ids: tuple[str, ...]
    prerequisite_ids: tuple[str, ...] = ()
    min_independent: int = 0
    required_relation: str = ""


@dataclass
class Calibration:
    calibration_id: str
    instrument_id: str
    status: str = CAL_VALID


@dataclass
class Evaluator:
    evaluator_id: str
    coverage: tuple[str, ...]
    uncertain: tuple[str, ...] = ()
    status: str = EVAL_VALID


@dataclass
class Relation:
    source_context: str
    target_context: str
    relation_type: str


@dataclass
class DependenceDeclaration:
    left_id: str
    right_id: str
    kind: str
    status: str = DEP_CONFIRMED


@dataclass
class Overlap:
    overlap_id: str
    left_claim_id: str
    right_claim_id: str
    compatible: bool | None = True
    witness_id: str = ""


@dataclass
class AuthorityPolicy:
    ceiling_level: int = AUTHORITY_OPERATIONAL
    status: str = AUTH_VALID


@dataclass
class Result:
    """A locally produced result offered as the basis of a transition."""

    result_id: str
    bound_claim_id: str
    basis_evidence_ids: tuple[str, ...]
    context_id: str
    evaluator_id: str = ""
    proved_spec_id: str = ""          # formal results only
    checker_status: str = ""          # formal results only: VALID/INVALID/UNKNOWN
    binding_status: str = IDENTITY_RECOVERABLE
    comparability_status: str = ""    # '' when no epoch change is registered
    min_independent: int = 0          # independence requirement on the basis (new support family)
    required_relation: str = ""       # required transport strength when context differs from target


@dataclass
class TransitionRequest:
    kind: str
    target_claim_id: str
    result_id: str = ""
    decision_criterion_id: str = ""
    required_authority_level: int = AUTHORITY_BELIEF
    challenged_event_index: int = -1


@dataclass
class Event:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    note: str = ""


@dataclass
class World:
    """Registered epistemic state at one version."""

    claims: dict[str, Claim] = field(default_factory=dict)
    evidence: dict[str, Evidence] = field(default_factory=dict)
    families: dict[str, Family] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    calibrations: dict[str, Calibration] = field(default_factory=dict)
    evaluators: dict[str, Evaluator] = field(default_factory=dict)
    relations: dict[str, Relation] = field(default_factory=dict)
    dependence: list[DependenceDeclaration] = field(default_factory=list)
    overlaps: dict[str, Overlap] = field(default_factory=dict)
    criterion_equivalence: dict[str, str] = field(default_factory=dict)   # "K1->K2" -> status
    spec_fidelity: dict[str, str] = field(default_factory=dict)           # "proved->intended" -> status
    results: dict[str, Result] = field(default_factory=dict)
    authority: AuthorityPolicy = field(default_factory=AuthorityPolicy)

    # ---- accessors ------------------------------------------------------
    def accepted_ids(self) -> tuple[str, ...]:
        return tuple(sorted(c for c, claim in self.claims.items() if claim.accepted_v0))

    def families_of(self, claim_id: str) -> tuple[Family, ...]:
        return tuple(f for f in sorted(self.families.values(), key=lambda x: x.family_id) if f.claim_id == claim_id)

    def positive_evidence_of_family(self, family: Family) -> tuple[Evidence, ...]:
        return tuple(self.evidence[e] for e in family.evidence_ids if self.evidence[e].supports)

    def negative_evidence_against(self, claim_id: str) -> tuple[Evidence, ...]:
        return tuple(e for e in sorted(self.evidence.values(), key=lambda x: x.evidence_id) if e.claim_id == claim_id and not e.supports)

    def dependents_of(self, claim_id: str) -> tuple[str, ...]:
        return tuple(sorted({f.claim_id for f in self.families.values() if claim_id in f.prerequisite_ids}))

    @staticmethod
    def relation_key(source_context: str, target_context: str) -> str:
        return f"{source_context}->{target_context}"

    @staticmethod
    def pair_key(a: str, b: str) -> str:
        return f"{a}->{b}"

    def copy(self) -> "World":
        return copy.deepcopy(self)

    def validate(self) -> None:
        for fam in self.families.values():
            if fam.claim_id not in self.claims:
                raise ValueError(f"family {fam.family_id} references unknown claim")
            for e in fam.evidence_ids:
                if e not in self.evidence:
                    raise ValueError(f"family {fam.family_id} references unknown evidence {e}")
            for p in fam.prerequisite_ids:
                if p not in self.claims:
                    raise ValueError(f"family {fam.family_id} references unknown prerequisite {p}")
        for ev in self.evidence.values():
            if ev.source_id not in self.sources:
                raise ValueError(f"evidence {ev.evidence_id} references unknown source")
            if ev.calibration_id and ev.calibration_id not in self.calibrations:
                raise ValueError(f"evidence {ev.evidence_id} references unknown calibration")
            if ev.evaluator_id and ev.evaluator_id not in self.evaluators:
                raise ValueError(f"evidence {ev.evidence_id} references unknown evaluator")
        for r in self.results.values():
            if r.bound_claim_id not in self.claims:
                raise ValueError(f"result {r.result_id} bound to unknown claim")
            for e in r.basis_evidence_ids:
                if e not in self.evidence:
                    raise ValueError(f"result {r.result_id} references unknown evidence {e}")
            if r.evaluator_id and r.evaluator_id not in self.evaluators:
                raise ValueError(f"result {r.result_id} references unknown evaluator")
        for o in self.overlaps.values():
            if o.left_claim_id not in self.claims or o.right_claim_id not in self.claims:
                raise ValueError(f"overlap {o.overlap_id} references unknown claim")
        if self.authority.ceiling_level not in AUTHORITY_LEVEL_NAMES:
            raise ValueError("unknown authority level")
        order = self.prerequisite_topological_order()
        if len(order) != len(self.claims):
            raise ValueError("prerequisite graph contains a cycle")

    def prerequisite_topological_order(self) -> tuple[str, ...]:
        prereqs = {c: set() for c in self.claims}
        for fam in self.families.values():
            prereqs[fam.claim_id].update(fam.prerequisite_ids)
        order: list[str] = []
        done: set[str] = set()
        while True:
            ready = sorted(c for c in self.claims if c not in done and prereqs[c] <= done)
            if not ready:
                break
            order.extend(ready)
            done.update(ready)
        return tuple(order)


def _evidence_from_dict(d: dict[str, Any]) -> Evidence:
    d = dict(d)
    d["scope_coverage"] = tuple(d["scope_coverage"])
    return Evidence(**d)


def _result_from_dict(d: dict[str, Any]) -> Result:
    d = dict(d)
    d["basis_evidence_ids"] = tuple(d["basis_evidence_ids"])
    return Result(**d)


def apply_event(world: World, event: Event) -> World:
    """Registered update of the epistemic state. Pure registry semantics: it
    records what the event *says*; it never decides the transition."""
    w = world.copy()
    p = event.payload
    k = event.kind
    if k == "SOURCE_RETRACTED":
        w.sources[p["source_id"]] = SOURCE_RETRACTED
    elif k == "SOURCE_RETRACTION_DISPUTED":
        w.sources[p["source_id"]] = SOURCE_DISPUTED
    elif k == "SOURCE_CORRECTED":
        w.sources[p["source_id"]] = SOURCE_VALID
    elif k == "CALIBRATION_INVALIDATED":
        w.calibrations[p["calibration_id"]].status = CAL_INVALID
    elif k == "CALIBRATION_UNDER_REVIEW":
        w.calibrations[p["calibration_id"]].status = CAL_UNDER_REVIEW
    elif k == "CALIBRATION_REVALIDATED":
        w.calibrations[p["calibration_id"]].status = CAL_VALID
    elif k in ("DEPENDENCE_DISCOVERED", "DEPENDENCE_SUSPECTED"):
        status = DEP_CONFIRMED if k == "DEPENDENCE_DISCOVERED" else DEP_SUSPECTED
        w.dependence = [d for d in w.dependence if {d.left_id, d.right_id} != {p["left_id"], p["right_id"]}]
        w.dependence.append(DependenceDeclaration(p["left_id"], p["right_id"], p["kind"], status))
    elif k == "RELATION_RETYPED":
        key = w.relation_key(p["source_context"], p["target_context"])
        w.relations[key] = Relation(p["source_context"], p["target_context"], p["relation_type"])
    elif k == "EVALUATOR_COVERAGE_CHANGED":
        old = w.evaluators[p["evaluator_id"]]
        w.evaluators[p["evaluator_id"]] = Evaluator(p["evaluator_id"], tuple(p["coverage"]), tuple(p.get("uncertain", ())), old.status)
    elif k == "CLAIM_FAILURE_CLASS_CHANGED":
        w.claims[p["claim_id"]].failure_class = p["failure_class"]
    elif k == "FAMILY_ADDED":
        fam = Family(**p["family"])
        fam.evidence_ids = tuple(fam.evidence_ids)
        fam.prerequisite_ids = tuple(fam.prerequisite_ids)
        for ev in p.get("evidence", ()):
            e = _evidence_from_dict(ev)
            w.evidence[e.evidence_id] = e
        w.families[fam.family_id] = fam
    elif k == "EVIDENCE_ADDED":
        e = _evidence_from_dict(p["evidence"])
        w.evidence[e.evidence_id] = e
    elif k == "EVALUATOR_INVALIDATED":
        w.evaluators[p["evaluator_id"]].status = EVAL_INVALID
    elif k == "EVALUATOR_UNDER_REVIEW":
        w.evaluators[p["evaluator_id"]].status = EVAL_UNDER_REVIEW
    elif k == "EVALUATOR_REGISTERED":
        w.evaluators[p["evaluator_id"]] = Evaluator(p["evaluator_id"], tuple(p["coverage"]), tuple(p.get("uncertain", ())), EVAL_VALID)
    elif k == "AUTHORITY_POLICY_CHANGED":
        w.authority = AuthorityPolicy(int(p.get("ceiling_level", w.authority.ceiling_level)), p.get("status", w.authority.status))
    elif k == "TARGET_CHANGED":
        w.claims[p["claim_id"]].target_epoch += 1
    elif k == "OVERLAP_ASSESSED":
        o = w.overlaps[p["overlap_id"]]
        o.compatible = p["compatible"]
        o.witness_id = p.get("witness_id", o.witness_id)
    elif k == "GLOBAL_WITNESS_REGISTERED":
        w.claims[p["claim_id"]].global_witness_id = p["witness_id"]
    elif k == "SPEC_FIDELITY_ASSESSED":
        w.spec_fidelity[w.pair_key(p["proved_spec_id"], p["intended_spec_id"])] = p["status"]
    elif k == "CRITERION_EQUIVALENCE_ASSESSED":
        w.criterion_equivalence[w.pair_key(p["left"], p["right"])] = p["status"]
        w.criterion_equivalence[w.pair_key(p["right"], p["left"])] = p["status"]
    elif k == "RESULT_REGISTERED":
        r = _result_from_dict(p["result"])
        w.results[r.result_id] = r
    elif k == "RESULT_REBOUND":
        w.results[p["result_id"]].bound_claim_id = p["bound_claim_id"]
    elif k == "COMPARABILITY_ASSESSED":
        w.results[p["result_id"]].comparability_status = p["status"]
    elif k == "EVIDENCE_IDENTITY_LOST":
        w.evidence[p["evidence_id"]].identity_status = IDENTITY_UNRECOVERABLE
    else:
        raise ValueError(f"unknown event kind {k}")
    w.validate()
    return w


@dataclass
class Instance:
    instance_id: str
    family: str
    variant: str
    split: str
    seed: int
    world_v0: World
    events: list[Event]
    request: TransitionRequest
    features: dict[str, Any] = field(default_factory=dict)


# ---- JSON (de)serialisation -------------------------------------------------

def world_to_json(w: World) -> dict[str, Any]:
    return {
        "claims": {k: asdict(v) for k, v in sorted(w.claims.items())},
        "evidence": {k: asdict(v) for k, v in sorted(w.evidence.items())},
        "families": {k: asdict(v) for k, v in sorted(w.families.items())},
        "sources": dict(sorted(w.sources.items())),
        "calibrations": {k: asdict(v) for k, v in sorted(w.calibrations.items())},
        "evaluators": {k: asdict(v) for k, v in sorted(w.evaluators.items())},
        "relations": {k: asdict(v) for k, v in sorted(w.relations.items())},
        "dependence": [asdict(d) for d in w.dependence],
        "overlaps": {k: asdict(v) for k, v in sorted(w.overlaps.items())},
        "criterion_equivalence": dict(sorted(w.criterion_equivalence.items())),
        "spec_fidelity": dict(sorted(w.spec_fidelity.items())),
        "results": {k: asdict(v) for k, v in sorted(w.results.items())},
        "authority": asdict(w.authority),
    }


def world_from_json(d: dict[str, Any]) -> World:
    w = World()
    for k, v in d["claims"].items():
        v = dict(v); v["scope"] = tuple(v["scope"]); w.claims[k] = Claim(**v)
    for k, v in d["evidence"].items():
        w.evidence[k] = _evidence_from_dict(v)
    for k, v in d["families"].items():
        v = dict(v); v["evidence_ids"] = tuple(v["evidence_ids"]); v["prerequisite_ids"] = tuple(v["prerequisite_ids"]); w.families[k] = Family(**v)
    w.sources = dict(d["sources"])
    for k, v in d["calibrations"].items():
        w.calibrations[k] = Calibration(**v)
    for k, v in d["evaluators"].items():
        v = dict(v); v["coverage"] = tuple(v["coverage"]); v["uncertain"] = tuple(v.get("uncertain", ())); w.evaluators[k] = Evaluator(**v)
    for k, v in d["relations"].items():
        w.relations[k] = Relation(**v)
    w.dependence = [DependenceDeclaration(**x) for x in d["dependence"]]
    for k, v in d.get("overlaps", {}).items():
        w.overlaps[k] = Overlap(**v)
    w.criterion_equivalence = dict(d.get("criterion_equivalence", {}))
    w.spec_fidelity = dict(d.get("spec_fidelity", {}))
    for k, v in d.get("results", {}).items():
        w.results[k] = _result_from_dict(v)
    w.authority = AuthorityPolicy(**d.get("authority", {}))
    w.validate()
    return w


def instance_to_json(inst: Instance) -> dict[str, Any]:
    return {
        "instance_id": inst.instance_id,
        "family": inst.family,
        "variant": inst.variant,
        "split": inst.split,
        "seed": inst.seed,
        "world_v0": world_to_json(inst.world_v0),
        "events": [asdict(e) for e in inst.events],
        "request": asdict(inst.request),
        "features": inst.features,
    }


def instance_from_json(d: dict[str, Any]) -> Instance:
    return Instance(d["instance_id"], d["family"], d["variant"], d["split"], d["seed"], world_from_json(d["world_v0"]), [Event(**e) for e in d["events"]], TransitionRequest(**d["request"]), dict(d.get("features", {})))


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
