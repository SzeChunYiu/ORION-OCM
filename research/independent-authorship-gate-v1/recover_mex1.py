#!/usr/bin/env python3
"""Independent min-sufficient-cause recovery for ME-X1 worlds.

The procedure never reads ``Instance.family``. It uses only the registered world,
events and request, plus the exact cheap oracle already frozen with ME-X1. The
planted family is compared afterwards as an audit field, not as truth.

Minimum sufficient cause:
  ACCEPT_RESULT / CLOSE_GLOBAL
    decisive atom = first INVALID request atom under the frozen precedence walk
    min-sufficient repair = smallest set of currently INVALID request atoms whose
    repair to VALID yields UPDATE (exact subset search, capped like the oracle)
  PROPAGATE_DEFEAT
    recovered object = reopened commitments
    min-sufficient repair = smallest set of INVALID support-table atoms whose
    repair empties the reopened set
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MEX1 = ROOT / "research" / "experiments" / "me-x1"

# Audit-only map from recovered atom kind → planter family name. This is not a
# truth label. It exists so recovered-vs-planted disagreement can be counted.
ATOM_KIND_AUDIT_CLASS = {
    "identity": "X1-A_CLAIM_PROBLEM_IDENTITY",
    "criterion": "X1-A_CLAIM_PROBLEM_IDENTITY",
    "cal": "X1-B_MEASUREMENT_CALIBRATION",
    "comparability": "X1-B_MEASUREMENT_CALIBRATION",
    "support": "X1-C_HIDDEN_DEPENDENCE",
    "ind": "X1-C_HIDDEN_DEPENDENCE",
    "transport": "X1-D_INVALID_TRANSPORT",
    "tr": "X1-D_INVALID_TRANSPORT",
    "src": "X1-E_DEFEATED_PREREQUISITE",
    "evaluator": "X1-F_EVALUATOR_BLINDNESS",
    "evc": "X1-F_EVALUATOR_BLINDNESS",
    "authority": "X1-G_AUTHORITY_MISMATCH",
    "spec": "X1-H_PROOF_WRONG_SPECIFICATION",
    "checker": "X1-H_PROOF_WRONG_SPECIFICATION",
    "overlap": "X1-I_LOCAL_COMPAT_GLOBAL_OBSTRUCTION",
    "witness": "X1-I_LOCAL_COMPAT_GLOBAL_OBSTRUCTION",
    "piece": "X1-I_LOCAL_COMPAT_GLOBAL_OBSTRUCTION",
}

NO_INVALID_ATOM = "NO_INVALID_ATOM"
CENSORED = "CENSORED"
MAX_REPAIR_ATOMS = 12


def load_mex1():
    for p in (str(MEX1), str(ROOT / "src")):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("mex1_generator", MEX1 / "mex1_generator.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load mex1_generator")
    gen = importlib.util.module_from_spec(spec)
    sys.modules["mex1_generator"] = gen
    spec.loader.exec_module(gen)
    import mex1_model  # type: ignore
    import mex1_oracle  # type: ignore
    return gen, mex1_model, mex1_oracle


def _kind(atom_id: str) -> str:
    return atom_id.split(":", 1)[0] if atom_id else ""


def audit_class_for_atom(atom_id: str) -> str:
    if not atom_id:
        return NO_INVALID_ATOM
    if atom_id == "CENSORED" or atom_id.startswith("CENSORED"):
        return CENSORED
    return ATOM_KIND_AUDIT_CLASS.get(_kind(atom_id), f"UNMAPPED:{_kind(atom_id)}")


def _smallest_repair(candidates: list[str], restores, *, cap: int = MAX_REPAIR_ATOMS) -> dict[str, Any]:
    if len(candidates) > cap:
        return {"status": "CANNOT_CHECK", "reason": f"too many invalid atoms for exact repair search: {len(candidates)}", "set": []}
    if restores(()):
        return {"status": "RECOVERED", "reason": None, "set": []}
    for k in range(1, len(candidates) + 1):
        for combo in itertools.combinations(candidates, k):
            if restores(combo):
                return {"status": "RECOVERED", "reason": None, "set": list(combo)}
    return {"status": "CANNOT_CHECK", "reason": "no repair of invalid atoms restores the warranted transition", "set": []}


def _unknown_atoms(model, atoms) -> list[str]:
    return [a.atom_id for a in atoms if a.status == model.STATUS_UNKNOWN]


def recover_world(model, oracle, world_v0, events, request) -> dict[str, Any]:
    """Recover min-sufficient cause from world+request only. No family argument.

    A DEFER caused by UNKNOWN/censored atoms is a recovered cause (CENSORED),
    not CANNOT_CHECK. Repair-to-UPDATE may still be CANNOT_CHECK when unknowns
    remain; that is recorded on the truth object and does not erase the cause.
    """
    w, exp = oracle.expected_for(world_v0, events, request)
    if not exp.exhaustive_agrees:
        return {"status": "CANNOT_CHECK", "reason": "oracle self-disagreement", "truth": None}
    table = oracle.support_table(w)
    tri = {a: oracle._tri(s) for a, s in table.atoms.items()}
    support = oracle.evaluate_support(w, tri, table)

    if request.kind == "PROPAGATE_DEFEAT":
        invalid = sorted(a for a, s in table.atoms.items() if s == model.STATUS_INVALID)
        accepted = w.accepted_ids()

        def restores(flip):
            flipped = set(flip)
            vals = {a: (True if a in flipped else v) for a, v in tri.items()}
            sup = oracle.evaluate_support(w, vals, table)
            return not any(sup[c] is False for c in accepted)

        repair = _smallest_repair(invalid, restores)
        truth = {
            "action": exp.action,
            "reopened": list(exp.reopened),
            "decisive_module": exp.decisive_module,
            "decisive_atom": exp.decisive_atom,
            "invalid_atoms": invalid,
            "unknown_atoms": list(exp.unknown_atoms),
            "min_sufficient_repair": repair["set"] if repair["status"] == "RECOVERED" else [],
            "repair_to_warranted_status": repair["status"],
            "repair_to_warranted_reason": repair.get("reason"),
            "request_kind": request.kind,
        }
        return {"status": "RECOVERED", "reason": None, "truth": truth}

    req_atoms = oracle.request_atoms(w, request, support, table)
    invalid = [a.atom_id for a in req_atoms if a.status == model.STATUS_INVALID]
    unknown = _unknown_atoms(model, req_atoms)
    by_id = {a.atom_id: a for a in req_atoms}

    def restores(flip):
        flipped = set(flip)
        patched = []
        for a in req_atoms:
            status = model.STATUS_VALID if a.atom_id in flipped else a.status
            patched.append(oracle.ReqAtom(a.atom_id, a.module, status, a.action, a.derived_from))
        action, _, _, _ = oracle.walk(patched)
        return action == model.UPDATE

    repair = _smallest_repair(invalid, restores)
    truth = {
        "action": exp.action,
        "reopened": list(exp.reopened),
        "decisive_module": exp.decisive_module,
        "decisive_atom": exp.decisive_atom,
        "invalid_atoms": invalid,
        "unknown_atoms": unknown,
        "min_sufficient_repair": repair["set"] if repair["status"] == "RECOVERED" else [],
        "repair_to_warranted_status": repair["status"],
        "repair_to_warranted_reason": repair.get("reason"),
        "request_kind": request.kind,
        "decisive_atom_module": by_id[exp.decisive_atom].module if exp.decisive_atom in by_id else exp.decisive_module,
    }
    return {"status": "RECOVERED", "reason": None, "truth": truth}


def compare_to_planted(planted_family: str, variant: str, recovered: dict[str, Any]) -> dict[str, Any]:
    """Audit-only comparison. Does not become a truth label."""
    if recovered.get("status") != "RECOVERED":
        return {
            "comparable": False,
            "agreement": "CANNOT_CHECK",
            "reason": recovered.get("reason"),
            "planted_family": planted_family,
            "variant": variant,
        }
    truth = recovered["truth"]
    decisive = truth.get("decisive_atom") or ""
    recovered_class = audit_class_for_atom(decisive) if decisive else NO_INVALID_ATOM
    if not decisive and truth.get("action") == "DEFER_CANNOT_CHECK":
        recovered_class = CENSORED
    if not decisive and truth.get("action") in {"SELECTIVELY_REOPEN", "PRESERVE", "UPDATE"}:
        recovered_class = "SUPPORT_REOPEN" if truth.get("action") == "SELECTIVELY_REOPEN" else NO_INVALID_ATOM
    repair_classes = sorted({audit_class_for_atom(a) for a in truth.get("min_sufficient_repair", [])})
    planted_matches_decisive = recovered_class == planted_family
    planted_covers_repair = planted_family in repair_classes if repair_classes else (
        planted_family == "X1-J_FULLY_WARRANTED" and recovered_class == NO_INVALID_ATOM
    )
    if not truth.get("min_sufficient_repair") and planted_family == "X1-J_FULLY_WARRANTED" and recovered_class == NO_INVALID_ATOM:
        planted_matches_decisive = True
        planted_covers_repair = True
    extra_repair = set(repair_classes) - {planted_family, NO_INVALID_ATOM}
    reason = "MATCH"
    if extra_repair:
        reason = "PLANTED_FAMILY_INCOMPLETE_VS_REPAIR_SET"
    elif planted_matches_decisive and variant == "POSITIVE":
        reason = "GENERATOR_FILTERED_BY_ORACLE_INVARIANT"
    elif not planted_matches_decisive and recovered_class == NO_INVALID_ATOM:
        reason = "PLANTED_FAMILY_BUT_NO_INVALID_ATOM"
    elif not planted_matches_decisive and recovered_class == "SUPPORT_REOPEN":
        reason = "PLANTED_FAMILY_VS_SUPPORT_REOPEN_SET"
    elif not planted_matches_decisive and recovered_class == CENSORED:
        reason = "PLANTED_FAMILY_VS_CENSORED"
    elif not planted_matches_decisive:
        reason = "PLANTED_FAMILY_NEQ_RECOVERED_DECISIVE"
    return {
        "comparable": True,
        "agreement": "AGREE" if planted_matches_decisive and planted_covers_repair and reason in {"MATCH", "GENERATOR_FILTERED_BY_ORACLE_INVARIANT"} else "DISAGREE",
        "reason": reason,
        "planted_family": planted_family,
        "variant": variant,
        "recovered_decisive_class": recovered_class,
        "recovered_repair_classes": repair_classes,
        "planted_matches_decisive_class": planted_matches_decisive,
        "planted_covers_repair": planted_covers_repair,
        "artifact_explained_if_used_as_truth": reason == "GENERATOR_FILTERED_BY_ORACLE_INVARIANT",
    }


def bindings() -> dict[str, str]:
    out = {}
    for rel in (
        "research/experiments/me-x1/mex1_generator.py",
        "research/experiments/me-x1/mex1_oracle.py",
        "research/experiments/me-x1/mex1_model.py",
        "research/independent-authorship-gate-v1/recover_mex1.py",
        "research/independent-authorship-gate-v1/policy.py",
    ):
        out[rel] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    return out
