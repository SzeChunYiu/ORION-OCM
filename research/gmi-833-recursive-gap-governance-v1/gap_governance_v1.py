#!/usr/bin/env python3
"""Recursive scientific-gap governance for #833 AA/AD.

This module validates research records and closure promotion. It does not prove
that a corpus has been exhaustively reviewed; it enforces the metadata/logic
needed before such a claim can be made.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Mapping, Sequence

CLOSURE = ("OPEN", "LOCALLY_CLOSED", "HOSTILE_CLOSED", "REPLICATED_CLOSED", "REAL_SCALE_CLOSED")
RANK = {name: i for i, name in enumerate(CLOSURE)}
SEVERITY = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
LOGIC_DIRECTIONS = ("SUFFICIENT", "NECESSARY", "IFF", "NONE")
RECORD_KINDS = ("THEOREM", "PROOF", "EXPERIMENT_RESULT")
EVIDENCE_SCOPES = ("UNIVERSAL", "FINITE_EXHAUSTIVE", "HELD_OUT", "SAMPLED", "PROTOCOL")
RESEARCH_LOOP = (
    "formalize", "parent_search", "derive", "counterexample_search",
    "repair_or_downgrade", "architecture_prior_audit", "independent_implementation",
    "frozen_prediction", "replication", "real_scale_test", "new_gap_extraction",
)

class GapGovernanceError(ValueError):
    pass


def _nonempty(record: Mapping[str, object], key: str) -> str:
    val = record.get(key)
    if not isinstance(val, str) or not val.strip():
        raise GapGovernanceError(f"{key} must be a nonempty string")
    return val


def validate_claim_logic(record: Mapping[str, object]) -> None:
    """Fail closed on common logic-category conflations via explicit metadata."""
    quantifiers = record.get("quantifiers")
    if not isinstance(quantifiers, list) or not quantifiers or any(not isinstance(x, str) or not x.strip() for x in quantifiers):
        raise GapGovernanceError("explicit ordered quantifiers are required")
    direction = record.get("logical_direction")
    if direction not in LOGIC_DIRECTIONS:
        raise GapGovernanceError("logical_direction must distinguish necessity/sufficiency/iff")
    scope = record.get("evidence_scope")
    if scope not in EVIDENCE_SCOPES:
        raise GapGovernanceError("evidence_scope must distinguish universal/finite/held-out/sampled/protocol")
    for pair in (("representable", "reachable"), ("optimal", "selected")):
        if pair[0] not in record or pair[1] not in record:
            raise GapGovernanceError(f"must record {pair[0]} and {pair[1]} separately")
        if not isinstance(record[pair[0]], bool) or not isinstance(record[pair[1]], bool):
            raise GapGovernanceError(f"{pair[0]}/{pair[1]} must be booleans")
    causal = record.get("causal_claim")
    design = record.get("causal_design")
    if not isinstance(causal, bool):
        raise GapGovernanceError("causal_claim must be boolean")
    if causal and design not in {"INTERVENTION", "RANDOMIZED", "IDENTIFIED_QUASI_EXPERIMENT", "DEDUCTIVE"}:
        raise GapGovernanceError("causal claim lacks a registered causal identification route")
    if scope == "FINITE_EXHAUSTIVE" and record.get("unrestricted_universal_wording") is True:
        raise GapGovernanceError("finite exhaustive evidence cannot be silently promoted to unrestricted universal wording")
    if record.get("converse_claimed") is True and direction not in {"IFF", "NECESSARY"}:
        raise GapGovernanceError("converse claimed without a converse/necessity theorem")


def validate_result_record(record: Mapping[str, object]) -> None:
    if record.get("record_kind") not in RECORD_KINDS:
        raise GapGovernanceError("record_kind must be THEOREM/PROOF/EXPERIMENT_RESULT")
    if not isinstance(record.get("flagship"), bool):
        raise GapGovernanceError("flagship must be boolean")
    for key in ("claim_id", "statement", "domain", "proof_mode", "evidence_level", "maturity_level"):
        _nonempty(record, key)
    for key in ("assumptions", "dependencies", "falsifiers", "strongest_parents", "forbidden_extrapolations", "open_gaps", "counterexample_methods"):
        val = record.get(key)
        if not isinstance(val, list):
            raise GapGovernanceError(f"{key} must be a list")
    if any(not isinstance(x, str) or not x.strip() for key in ("assumptions","dependencies","falsifiers","strongest_parents","forbidden_extrapolations","open_gaps","counterexample_methods") for x in record[key]):
        raise GapGovernanceError("result ledgers may contain only nonempty strings")
    prior = record.get("prior_disclosure")
    if not isinstance(prior, Mapping):
        raise GapGovernanceError("prior_disclosure must be a mapping")
    closure = record.get("closure_state")
    if closure not in CLOSURE:
        raise GapGovernanceError("bare or unknown scientific closure state")
    if closure == "HOSTILE_CLOSED" and len(set(record["counterexample_methods"])) < 2:
        raise GapGovernanceError("HOSTILE_CLOSED requires two distinct counterexample methods")
    if record["flagship"] and len(set(record["counterexample_methods"])) < 2:
        raise GapGovernanceError("flagship results require two distinct counterexample methods")
    validate_claim_logic(record)


def validate_experiment_ledger(record: Mapping[str, object]) -> None:
    for key in ("experiment_id", "search_space", "cost_model", "evaluation", "sampling_bias", "leakage_audit"):
        _nonempty(record, key)
    if record.get("outcomes_seen_before_freeze") is not False:
        raise GapGovernanceError("experiment must explicitly say outcomes were not seen before freeze")
    if not isinstance(record.get("negative_controls"), list):
        raise GapGovernanceError("negative_controls must be a list")


def validate_gap(gap: Mapping[str, object]) -> None:
    for key in ("id","claim_id","premise","inference","unresolved_assumption","possible_counterexample","owner_role","parent_result","evidence_needed","materiality"):
        _nonempty(gap, key)
    if gap.get("severity") not in SEVERITY:
        raise GapGovernanceError("invalid severity")
    if gap.get("status") not in CLOSURE:
        raise GapGovernanceError("invalid/bare gap closure state")
    for key in ("descendants", "introduced_assumptions", "counterexample_methods"):
        if not isinstance(gap.get(key), list):
            raise GapGovernanceError(f"{key} must be a list")
    if gap["status"] != "OPEN" and "closure_evidence" not in gap:
        raise GapGovernanceError("closed gap must retain closure_evidence")
    if gap["status"] == "HOSTILE_CLOSED" and len(set(gap["counterexample_methods"])) < 2:
        raise GapGovernanceError("HOSTILE_CLOSED gap requires two counterexample methods")


def graph_audit(graph: Mapping[str, object]) -> dict[str, object]:
    nodes = graph.get("nodes")
    roots = graph.get("roots")
    if not isinstance(nodes, Mapping) or not nodes:
        raise GapGovernanceError("gap graph needs nodes")
    if not isinstance(roots, list) or not roots:
        raise GapGovernanceError("gap graph needs roots")
    for node_id, gap in nodes.items():
        if not isinstance(node_id, str) or not isinstance(gap, Mapping):
            raise GapGovernanceError("malformed node")
        validate_gap(gap)
        if gap["id"] != node_id:
            raise GapGovernanceError("node key/id mismatch")
    missing = sorted({child for gap in nodes.values() for child in gap["descendants"] if child not in nodes})
    missing_roots = sorted(r for r in roots if r not in nodes)
    incoming = {k: 0 for k in nodes}
    for gap in nodes.values():
        for child in gap["descendants"]:
            if child in incoming:
                incoming[child] += 1
    orphans = sorted(k for k,v in incoming.items() if v == 0 and k not in roots)

    cycles: list[list[str]] = []
    color = {k: 0 for k in nodes}
    stack: list[str] = []
    def dfs(v: str) -> None:
        color[v] = 1; stack.append(v)
        for w in nodes[v]["descendants"]:
            if w not in nodes: continue
            if color[w] == 0: dfs(w)
            elif color[w] == 1:
                i = stack.index(w)
                cyc = stack[i:] + [w]
                if cyc not in cycles: cycles.append(cyc)
        stack.pop(); color[v] = 2
    for v in nodes:
        if color[v] == 0: dfs(v)

    return {"missing_nodes": missing, "missing_roots": missing_roots, "orphans": orphans, "cycles": cycles,
            "valid": not (missing or missing_roots or orphans or cycles)}


def unresolved_critical_descendants(graph: Mapping[str, object], root: str) -> tuple[str, ...]:
    nodes = graph["nodes"]
    seen: set[str] = set()
    todo = list(nodes[root]["descendants"])
    blockers: list[str] = []
    while todo:
        gid = todo.pop()
        if gid in seen or gid not in nodes: continue
        seen.add(gid)
        gap = nodes[gid]
        if gap["severity"] == "CRITICAL" and gap["status"] == "OPEN": blockers.append(gid)
        todo.extend(gap["descendants"])
    return tuple(sorted(blockers))


def can_promote_result(result: Mapping[str, object], graph: Mapping[str, object], target: str) -> tuple[bool, str]:
    validate_result_record(result)
    audit = graph_audit(graph)
    if not audit["valid"]:
        return False, "INVALID_GAP_GRAPH"
    if target not in CLOSURE:
        return False, "UNKNOWN_TARGET"
    if target == "OPEN": return True, "OK"
    blockers: set[str] = set()
    for gid in result["open_gaps"]:
        if gid in graph["nodes"]:
            if graph["nodes"][gid]["severity"] == "CRITICAL" and graph["nodes"][gid]["status"] == "OPEN": blockers.add(gid)
            blockers.update(unresolved_critical_descendants(graph, gid))
    if blockers: return False, "CRITICAL_DESCENDANT_OPEN:" + ",".join(sorted(blockers))
    if target == "HOSTILE_CLOSED" and len(set(result["counterexample_methods"])) < 2:
        return False, "TWO_COUNTEREXAMPLE_METHODS_REQUIRED"
    return True, "OK"


def validate_research_iteration(record: Mapping[str, object]) -> None:
    if tuple(record.get("stages", ())) != RESEARCH_LOOP:
        raise GapGovernanceError("research loop stages differ from registered AD loop")
    for key in ("iteration_id", "claim_id", "gap_extraction_notes"):
        _nonempty(record, key)
    for key in ("new_gap_ids", "new_assumptions"):
        if not isinstance(record.get(key), list):
            raise GapGovernanceError(f"{key} must be an explicit list")
    if not isinstance(record.get("failure_occurred"), bool):
        raise GapGovernanceError("failure_occurred must be boolean")
    if record["failure_occurred"]:
        if record.get("failure_evidence_retained") is not True:
            raise GapGovernanceError("failed results must preserve failure evidence")
        _nonempty(record, "theory_update")
    if not isinstance(record.get("parent_subsumed"), bool):
        raise GapGovernanceError("parent_subsumed must be boolean")
    if record["parent_subsumed"]:
        if record.get("parent_math_absorbed") is not True or record.get("novelty_claim_moved_upward") is not True:
            raise GapGovernanceError("parent-subsumed results must absorb parent mathematics and move novelty upward")
    theories = record.get("competing_theories")
    if not isinstance(theories, list):
        raise GapGovernanceError("competing_theories must be a list")
    if len(theories) > 1:
        if not isinstance(record.get("discrimination_identifiable"), bool):
            raise GapGovernanceError("theory ties must state whether discrimination is identifiable")
        if record["discrimination_identifiable"]:
            _nonempty(record, "discriminating_experiment")
        else:
            _nonempty(record, "observational_indistinguishability_scope")
    if record.get("stopped") is True:
        _nonempty(record, "declared_evidence_ceiling")
        _nonempty(record, "stop_reason")


def _base_logic() -> dict[str, object]:
    return {
        "quantifiers": ["forall registered finite nodes", "exists recorded witness where required"],
        "logical_direction": "SUFFICIENT",
        "evidence_scope": "FINITE_EXHAUSTIVE",
        "representable": True, "reachable": False, "optimal": False, "selected": False,
        "causal_claim": False, "causal_design": "NONE", "unrestricted_universal_wording": False,
        "converse_claimed": False,
    }


def build_receipt() -> dict[str, object]:
    result = {
        "record_kind":"THEOREM", "flagship":False,
        "claim_id":"AA-GOV-1", "statement":"critical descendants block scientific closure promotion",
        "domain":"registered finite gap graph", "proof_mode":"deductive + finite hostile",
        "evidence_level":"EV2", "maturity_level":"M2", "assumptions":["registered graph is complete for this fixture"],
        "dependencies":[], "falsifiers":["promotion succeeds with open critical child"],
        "strongest_parents":["proof obligation/dependency graphs", "assurance cases"],
        "prior_disclosure":{"scope":"governance fixture"}, "forbidden_extrapolations":["ALL_GAPS_EXHAUSTED"],
        "open_gaps":["G0"], "counterexample_methods":["exact graph hostile", "metadata mutation hostile"],
        "closure_state":"LOCALLY_CLOSED", **_base_logic(),
    }
    graph = {"roots":["G0"], "nodes":{
        "G0":{"id":"G0","claim_id":"AA-GOV-1","premise":"root claim","inference":"P -> Q","unresolved_assumption":"child review","possible_counterexample":"critical child","severity":"HIGH","owner_role":"logic","parent_result":"AA-GOV-1","evidence_needed":"descendant discharge","materiality":"may alter evidence level","status":"OPEN","descendants":["G1"],"introduced_assumptions":[],"counterexample_methods":[]},
        "G1":{"id":"G1","claim_id":"AA-GOV-1","premise":"load-bearing premise","inference":"R -> P","unresolved_assumption":"R not yet discharged","possible_counterexample":"not-R","severity":"CRITICAL","owner_role":"hostile","parent_result":"G0","evidence_needed":"counterexample/proof","materiality":"can reverse claim","status":"OPEN","descendants":[],"introduced_assumptions":[],"counterexample_methods":[]},
    }}
    audit = graph_audit(graph)
    allowed, reason = can_promote_result(result, graph, "HOSTILE_CLOSED")
    cycle_graph = {"roots":["A"], "nodes":{
        "A":{"id":"A","claim_id":"x","premise":"p","inference":"p->q","unresolved_assumption":"a","possible_counterexample":"c","severity":"LOW","owner_role":"x","parent_result":"x","evidence_needed":"e","materiality":"m","status":"OPEN","descendants":["B"],"introduced_assumptions":[],"counterexample_methods":[]},
        "B":{"id":"B","claim_id":"x","premise":"p","inference":"p->q","unresolved_assumption":"a","possible_counterexample":"c","severity":"LOW","owner_role":"x","parent_result":"x","evidence_needed":"e","materiality":"m","status":"OPEN","descendants":["A"],"introduced_assumptions":[],"counterexample_methods":[]},
    }}
    return {"schema":"GMI_833_RECURSIVE_GAP_GOVERNANCE_RECEIPT_V1",
            "terminal":"GMI_833_RECURSIVE_GAP_GOVERNANCE_V1_AT_DECLARED_SCOPE",
            "closure_states":list(CLOSURE), "registered_research_loop":list(RESEARCH_LOOP),
            "principal_graph_audit":audit, "critical_promotion_allowed":allowed,
            "critical_promotion_reason":reason, "cycle_hostile":graph_audit(cycle_graph),
            "forbidden_promotions":["ALL_GAPS_EXHAUSTED","INDEPENDENT_HOSTILE_REVIEW_COMPLETE","CORPUS_AUDIT_COMPLETE","REPLICATED_CLOSED","REAL_SCALE_CLOSED","COMPLETE_GMI"]}

if __name__ == "__main__":
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
