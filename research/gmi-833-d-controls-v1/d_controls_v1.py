#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha1
import importlib.util
import json
from pathlib import Path
import sys

CLAIM_CEILING = "GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "ALL_GMI_DERIVATIONS_ROBUST",
    "ARCHITECTURE_PRIOR_FREE_UNIVERSALLY",
    "REPRESENTATION_INDEPENDENT_UNIVERSALLY",
    "SEARCH_INDEPENDENT_UNIVERSALLY",
    "RESOURCE_PRICE_INDEPENDENT_UNIVERSALLY",
    "KNOWN_FAMILY_RECOVERY_COMPLETE",
    "COMPLETE_GMI",
)
PARENT_RESULT_PATH = "research/gmi-833-no-smuggling-audit-v1/RESULT_V1.json"
PARENT_RESULT_BLOB = "0d8b8c1dcd05512e2ec54db6bae872953daed87f"
PARENT_CLAIM_CEILING = "GMI_NO_SMUGGLING_AUDIT_TOOLING_VALIDATED_AT_REGISTERED_FINITE_FIXTURE_SCOPE"
CLEAN = "CLEAN_AT_REGISTERED_AUDIT_SCOPE"
ROBUST = "ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE"

REQUIRED_NUISANCE_KEYS = (
    "candidate_capacity",
    "max_depth",
    "non_target_primitives",
    "task",
    "ecology",
    "evaluator",
    "search_budget",
    "tie_rule",
    "stopping_rule",
    "resource_coordinates",
)


def F(value):
    return value if isinstance(value, Fraction) else Fraction(str(value))


def repo_root(start: Path | None = None):
    p = (start or Path(__file__).resolve()).parent
    while p.parent != p:
        if (p / "research").is_dir():
            return p
        p = p.parent
    return Path(__file__).resolve().parents[2]


def git_blob_sha(data: bytes):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parent_result(root: Path | None = None):
    root = root or repo_root()
    path = root / PARENT_RESULT_PATH
    if not path.is_file():
        return {"all_ok": False, "path": PARENT_RESULT_PATH, "actual_blob": None, "blob_ok": False, "claim_ceiling_ok": False, "verdict_ok": False}
    data = path.read_bytes()
    actual_blob = git_blob_sha(data)
    try:
        parsed = json.loads(data)
    except Exception:
        parsed = {}
    return {
        "all_ok": actual_blob == PARENT_RESULT_BLOB and parsed.get("claim_ceiling") == PARENT_CLAIM_CEILING and parsed.get("verdict") == "GREEN",
        "path": PARENT_RESULT_PATH,
        "actual_blob": actual_blob,
        "blob_ok": actual_blob == PARENT_RESULT_BLOB,
        "claim_ceiling_ok": parsed.get("claim_ceiling") == PARENT_CLAIM_CEILING,
        "verdict_ok": parsed.get("verdict") == "GREEN",
    }


def load_parent_auditor(root: Path | None = None):
    root = root or repo_root()
    parent_dir = root / "research/gmi-833-no-smuggling-audit-v1"
    path = parent_dir / "no_smuggling_audit_v1.py"
    if not path.is_file():
        raise FileNotFoundError(path)
    sys.path.insert(0, str(parent_dir))
    try:
        name = "gmi_833_no_smuggling_parent_for_d_controls"
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load parent no-smuggling auditor")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        try:
            sys.path.remove(str(parent_dir))
        except ValueError:
            pass


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def matched_twin_gate(control):
    if not isinstance(control, dict):
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_MATCHED_TWIN", "contrast_support": False, "mismatches": ("MISSING_CONTROL",)}
    positive = control.get("positive")
    negative = control.get("negative")
    if not isinstance(positive, dict) or not isinstance(negative, dict):
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_MATCHED_TWIN", "contrast_support": False, "mismatches": ("MISSING_ARM",)}
    if positive.get("target_mechanism_enabled") is not True or negative.get("target_mechanism_enabled") is not False:
        return {"terminal": "TARGET_MECHANISM_NOT_REMOVED", "contrast_support": False, "mismatches": ()}
    if negative.get("compensating_target_macro") is True:
        return {"terminal": "COMPENSATING_TARGET_MACRO", "contrast_support": False, "mismatches": ()}
    pcap = positive.get("nuisance_capacity")
    ncap = negative.get("nuisance_capacity")
    if not isinstance(pcap, dict) or not isinstance(ncap, dict):
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_MATCHED_TWIN", "contrast_support": False, "mismatches": ("MISSING_NUISANCE_CAPACITY",)}
    missing = tuple(sorted(k for k in REQUIRED_NUISANCE_KEYS if k not in pcap or k not in ncap))
    if missing:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_MATCHED_TWIN", "contrast_support": False, "mismatches": missing}
    mismatches = tuple(sorted(k for k in REQUIRED_NUISANCE_KEYS if pcap[k] != ncap[k]))
    if positive.get("audit_identifiers") != negative.get("audit_identifiers"):
        mismatches = tuple(sorted(set(mismatches) | {"audit_identifiers"}))
    if mismatches:
        return {"terminal": "UNMATCHED_MECHANISM_TWIN", "contrast_support": False, "mismatches": mismatches}
    return {
        "terminal": "MATCHED_MECHANISM_TWIN",
        "contrast_support": bool(control.get("positive_outcome")) and not bool(control.get("negative_outcome")),
        "mismatches": (),
    }


def _canonical_projection(encoding):
    if not isinstance(encoding, dict) or not isinstance(encoding.get("candidates"), dict):
        raise ValueError("encoding requires candidate map")
    projection = {}
    raw_ids = set()
    for raw_id, row in encoding["candidates"].items():
        if raw_id in raw_ids:
            raise ValueError("duplicate raw encoding id")
        raw_ids.add(raw_id)
        row = _require_mapping(row, "encoding candidate")
        canonical_id = row.get("canonical_id")
        if not canonical_id or canonical_id in projection:
            raise ValueError("canonical encoding ids must be unique and nonempty")
        resources = _require_mapping(row.get("resources"), "encoding resources")
        normalized_resources = tuple(sorted((str(k), F(v)) for k, v in resources.items()))
        if any(v < 0 for _, v in normalized_resources):
            raise ValueError("encoding resources must be nonnegative")
        behavior = tuple(row.get("behavior", ()))
        projection[canonical_id] = (behavior, normalized_resources, bool(row.get("property")))
    return projection, frozenset(raw_ids)


def encoding_gate(control):
    if not isinstance(control, dict) or len(control.get("encodings", ())) < 2:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_ENCODING", "encoding_count": 0, "alternate_syntax": False}
    projections = []
    raw_sets = []
    try:
        for encoding in control["encodings"]:
            projection, raw = _canonical_projection(encoding)
            projections.append(projection)
            raw_sets.append(raw)
    except (ValueError, TypeError) as exc:
        return {"terminal": "ENCODING_NOT_SEMANTICALLY_EQUIVALENT", "encoding_count": len(control["encodings"]), "alternate_syntax": False, "reason": str(exc)}
    alternate = any(raw_sets[i].isdisjoint(raw_sets[j]) for i in range(len(raw_sets)) for j in range(i + 1, len(raw_sets)))
    if not alternate:
        return {"terminal": "ENCODING_NOT_SEMANTICALLY_EQUIVALENT", "encoding_count": len(projections), "alternate_syntax": False, "reason": "RAW_SYNTAX_NOT_ALTERNATE"}
    equal = all(p == projections[0] for p in projections[1:])
    return {
        "terminal": "ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE" if equal else "ENCODING_NOT_SEMANTICALLY_EQUIVALENT",
        "encoding_count": len(projections),
        "alternate_syntax": alternate,
        "canonical_candidate_count": len(projections[0]),
    }


def _candidate_map(candidates):
    rows = tuple(candidates)
    by_id = {row["id"]: row for row in rows}
    if not rows or len(by_id) != len(rows):
        raise ValueError("candidate ids must be unique and nonempty")
    return rows, by_id


def _run_search(candidates, algorithm, budget):
    candidates, by_id = _candidate_map(candidates)
    kind = algorithm.get("kind")
    if kind == "exhaustive":
        order = tuple(algorithm.get("order") or tuple(sorted(by_id)))
        if set(order) != set(by_id):
            raise ValueError("exhaustive order must cover every candidate exactly once")
        evaluated = order[:budget]
        if not evaluated:
            return {"selected": (), "evaluations": 0, "certificate": "INCOMPLETE"}
        values = {cid: F(by_id[cid]["task_loss"]) for cid in evaluated}
        best = min(values.values())
        selected = tuple(sorted(cid for cid, value in values.items() if value == best))
        certificate = "EXHAUSTIVE" if len(evaluated) == len(by_id) else "INCOMPLETE"
        return {"selected": selected, "evaluations": len(evaluated), "certificate": certificate}
    if kind == "branch_and_bound":
        for row in candidates:
            if F(row["lower_bound"]) > F(row["task_loss"]):
                raise ValueError("lower bound exceeds objective")
        ordered = tuple(sorted(candidates, key=lambda row: (F(row["lower_bound"]), row["id"])))
        best = None
        selected = []
        evaluations = 0
        complete = True
        for row in ordered:
            lower = F(row["lower_bound"])
            if best is not None and lower > best:
                continue
            if evaluations >= budget:
                complete = False
                break
            evaluations += 1
            value = F(row["task_loss"])
            if best is None or value < best:
                best = value
                selected = [row["id"]]
            elif value == best:
                selected.append(row["id"])
        return {"selected": tuple(sorted(selected)), "evaluations": evaluations, "certificate": "ADMISSIBLE_BOUND_COMPLETE" if complete else "INCOMPLETE"}
    if kind == "early_stop":
        order = tuple(algorithm.get("order", ()))
        if not order or any(cid not in by_id for cid in order):
            raise ValueError("early-stop order invalid")
        limit = min(int(algorithm.get("limit", 1)), budget, len(order))
        evaluated = order[:limit]
        values = {cid: F(by_id[cid]["task_loss"]) for cid in evaluated}
        best = min(values.values())
        return {"selected": tuple(sorted(cid for cid, value in values.items() if value == best)), "evaluations": len(evaluated), "certificate": "INCOMPLETE"}
    raise ValueError(f"unknown search algorithm kind: {kind}")


def search_gate(control):
    if not isinstance(control, dict):
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SEARCH", "runs": (), "conclusions": ()}
    algorithms = tuple(control.get("algorithms", ()))
    candidates = tuple(control.get("candidates", ()))
    if len(algorithms) < 2 or not candidates:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SEARCH", "runs": (), "conclusions": ()}
    kinds = tuple(algorithm.get("kind") for algorithm in algorithms)
    if len(set(kinds)) < 2:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SEARCH", "runs": (), "conclusions": (), "reason": "SEARCH_PROCEDURES_NOT_DISTINCT"}
    budget = int(control.get("budget", 0))
    if budget < 1:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SEARCH", "runs": (), "conclusions": (), "reason": "BAD_BUDGET"}
    _, by_id = _candidate_map(candidates)
    runs = []
    try:
        for algorithm in algorithms:
            if not algorithm.get("name"):
                raise ValueError("search algorithm needs name")
            runs.append((algorithm["name"], _run_search(candidates, algorithm, budget)))
    except (ValueError, TypeError, KeyError) as exc:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SEARCH", "runs": tuple(runs), "conclusions": (), "reason": str(exc)}
    property_key = control.get("claim_property")
    conclusions = []
    for name, run in runs:
        values = tuple(sorted({bool(by_id[cid].get(property_key)) for cid in run["selected"]}))
        conclusions.append((name, values))
    certified = all(run["certificate"] in {"EXHAUSTIVE", "ADMISSIBLE_BOUND_COMPLETE"} for _, run in runs)
    agrees = len({values for _, values in conclusions}) == 1 and conclusions[0][1] == (True,)
    return {
        "terminal": "SEARCH_ROBUST" if certified and agrees else "SEARCH_SENSITIVE",
        "runs": tuple(runs),
        "conclusions": tuple(conclusions),
        "all_searches_certified": certified,
    }


def pareto_set(candidates):
    candidates, _ = _candidate_map(candidates)
    if not candidates:
        return ()
    coordinate_sets = {tuple(sorted(row["resources"])) for row in candidates}
    if len(coordinate_sets) != 1:
        raise ValueError("resource coordinate schemas differ")
    coords = tuple(sorted(candidates[0]["resources"]))
    for row in candidates:
        if any(F(row["resources"][key]) < 0 for key in coords):
            raise ValueError("negative resource")
    result = []
    for candidate in candidates:
        rc = candidate["resources"]
        dominated = False
        for other in candidates:
            if other["id"] == candidate["id"]:
                continue
            ro = other["resources"]
            weak = all(F(ro[key]) <= F(rc[key]) for key in coords)
            strict = any(F(ro[key]) < F(rc[key]) for key in coords)
            if weak and strict:
                dominated = True
                break
        if not dominated:
            result.append(candidate["id"])
    return tuple(sorted(result))


def scalarization_gate(control):
    if not isinstance(control, dict):
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SCALARIZATION", "pareto_set": (), "winners": ()}
    candidates = tuple(control.get("candidates", ()))
    scalarizations = tuple(control.get("scalarizations", ()))
    if not candidates or len(scalarizations) < 2:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SCALARIZATION", "pareto_set": (), "winners": ()}
    try:
        candidates, by_id = _candidate_map(candidates)
        pset = pareto_set(candidates)
        coords = tuple(sorted(candidates[0]["resources"]))
        winners = []
        for spec in scalarizations:
            weights = spec.get("weights")
            if not spec.get("name") or not isinstance(weights, dict) or tuple(sorted(weights)) != coords:
                raise ValueError("scalarization coordinate mismatch")
            if any(F(weights[key]) <= 0 for key in coords):
                raise ValueError("scalarization weights must be strictly positive")
            scores = {
                row["id"]: sum(F(row["resources"][key]) * F(weights[key]) for key in coords)
                for row in candidates
            }
            best = min(scores.values())
            winners.append((spec["name"], tuple(sorted(cid for cid, score in scores.items() if score == best))))
    except (ValueError, TypeError, KeyError) as exc:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SCALARIZATION", "pareto_set": (), "winners": (), "reason": str(exc)}
    identity_sensitive = len({cid for _, ids in winners for cid in ids}) > 1
    claim_type = control.get("claim_type")
    if claim_type == "PROPERTY_UNIVERSAL":
        key = control.get("claim_property")
        robust = all(bool(by_id[cid].get(key)) for cid in pset) and all(bool(by_id[cid].get(key)) for _, ids in winners for cid in ids)
    elif claim_type == "CANDIDATE_UNIVERSAL":
        all_winners = {cid for _, ids in winners for cid in ids}
        robust = len(pset) == 1 and len(all_winners) == 1 and set(pset) == all_winners
    elif claim_type == "PRICE_CONDITIONAL":
        robust = True
    else:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_SCALARIZATION", "pareto_set": pset, "winners": tuple(winners), "reason": "UNKNOWN_CLAIM_TYPE"}
    return {
        "terminal": "SCALARIZATION_ROBUST" if robust else "SCALARIZATION_SENSITIVE",
        "pareto_set": pset,
        "winners": tuple(winners),
        "candidate_identity_sensitive": identity_sensitive,
    }


def no_smuggling_arm_gate(control, root: Path | None = None):
    parent = audit_parent_result(root)
    if not parent["all_ok"]:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_NO_SMUGGLING_PARENT", "parent": parent, "arms": {}}
    try:
        auditor = load_parent_auditor(root)
    except Exception as exc:
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_NO_SMUGGLING_PARENT", "parent": parent, "arms": {}, "reason": str(exc)}
    twin = control.get("matched_twin", {}) if isinstance(control, dict) else {}
    arms = {}
    for label in ("positive", "negative"):
        arm = twin.get(label, {})
        identifiers = arm.get("audit_identifiers")
        if identifiers is None:
            arms[label] = "CANNOT_AUDIT_SEARCH_VISIBLE_IDENTIFIERS"
            continue
        record = auditor.clean_record()
        record["search_visible_identifiers"] = list(identifiers)
        arms[label] = auditor.audit_record(record)["terminal"]
    terminal = "NO_SMUGGLING_ARMS_CLEAN" if arms and all(value == CLEAN for value in arms.values()) else "NO_SMUGGLING_ARM_NOT_CLEAN"
    return {"terminal": terminal, "parent": parent, "arms": arms}


MISSING_CONTROL_TERMINALS = {
    "matched_twin": "CANNOT_ESTABLISH_D_ROBUSTNESS_MATCHED_TWIN",
    "encodings": "CANNOT_ESTABLISH_D_ROBUSTNESS_ENCODING",
    "search": "CANNOT_ESTABLISH_D_ROBUSTNESS_SEARCH",
    "scalarization": "CANNOT_ESTABLISH_D_ROBUSTNESS_SCALARIZATION",
}


def evaluate_record(record, root: Path | None = None, no_smuggling_override=None):
    if not isinstance(record, dict):
        return {"terminal": "CANNOT_ESTABLISH_D_ROBUSTNESS_RECORD", "controls": {}}
    for key, terminal in MISSING_CONTROL_TERMINALS.items():
        if key not in record:
            return {"terminal": terminal, "controls": {}}
    twin = matched_twin_gate(record["matched_twin"])
    encoding = encoding_gate(record["encodings"])
    search = search_gate(record["search"])
    scalar = scalarization_gate(record["scalarization"])
    no_smuggling = no_smuggling_override if no_smuggling_override is not None else no_smuggling_arm_gate(record, root)
    controls = {"matched_twin": twin, "encodings": encoding, "search": search, "scalarization": scalar, "no_smuggling": no_smuggling}
    passed = (
        twin["terminal"] == "MATCHED_MECHANISM_TWIN"
        and twin["contrast_support"]
        and encoding["terminal"] == "ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE"
        and search["terminal"] == "SEARCH_ROBUST"
        and scalar["terminal"] == "SCALARIZATION_ROBUST"
        and no_smuggling.get("terminal") == "NO_SMUGGLING_ARMS_CLEAN"
    )
    return {"terminal": ROBUST if passed else "D_ROBUSTNESS_NOT_ESTABLISHED", "controls": controls}


def semantic_candidates():
    return (
        {"id": "k_balanced", "behavior": ("target_ok",), "property": True, "task_loss": Fraction(0), "lower_bound": Fraction(0), "resources": {"compute": Fraction(2), "memory": Fraction(2)}},
        {"id": "k_compute", "behavior": ("target_ok",), "property": True, "task_loss": Fraction(1), "lower_bound": Fraction(1), "resources": {"compute": Fraction(1), "memory": Fraction(4)}},
        {"id": "k_memory", "behavior": ("target_ok",), "property": True, "task_loss": Fraction(1), "lower_bound": Fraction(1), "resources": {"compute": Fraction(4), "memory": Fraction(1)}},
        {"id": "baseline", "behavior": ("target_fail",), "property": False, "task_loss": Fraction(3), "lower_bound": Fraction(2), "resources": {"compute": Fraction(5), "memory": Fraction(5)}},
    )


def _encoding(name, rows):
    candidates = {}
    for index, row in enumerate(rows):
        candidates[f"{name}_{index}"] = {
            "canonical_id": row["id"],
            "behavior": row["behavior"],
            "resources": deepcopy(row["resources"]),
            "property": row["property"],
        }
    return {"name": name, "candidates": candidates}


def positive_record():
    rows = semantic_candidates()
    nuisance = {
        "candidate_capacity": 4,
        "max_depth": 3,
        "non_target_primitives": ("add", "compare", "index_read", "index_write"),
        "task": "registered_target_task_v1",
        "ecology": "registered_ecology_v1",
        "evaluator": "protected_behavior_verifier_v1",
        "search_budget": 4,
        "tie_rule": "CANONICAL_ID",
        "stopping_rule": "CERTIFIED_COMPLETE",
        "resource_coordinates": ("compute", "memory"),
    }
    return {
        "matched_twin": {
            "target_mechanism": "registered_K",
            "positive": {"target_mechanism_enabled": True, "compensating_target_macro": False, "nuisance_capacity": deepcopy(nuisance), "audit_identifiers": ("add", "index_read")},
            "negative": {"target_mechanism_enabled": False, "compensating_target_macro": False, "nuisance_capacity": deepcopy(nuisance), "audit_identifiers": ("add", "index_read")},
            "positive_outcome": True,
            "negative_outcome": False,
        },
        "encodings": {
            "encodings": (_encoding("alpha", rows), _encoding("zeta", tuple(reversed(rows)))),
        },
        "search": {
            "candidates": deepcopy(rows),
            "budget": 4,
            "claim_property": "property",
            "algorithms": (
                {"name": "exact_enumeration", "kind": "exhaustive", "order": tuple(row["id"] for row in rows)},
                {"name": "admissible_branch_and_bound", "kind": "branch_and_bound"},
            ),
        },
        "scalarization": {
            "candidates": deepcopy(rows),
            "claim_type": "PROPERTY_UNIVERSAL",
            "claim_property": "property",
            "scalarizations": (
                {"name": "compute_high", "weights": {"compute": Fraction(4), "memory": Fraction(1)}},
                {"name": "memory_high", "weights": {"compute": Fraction(1), "memory": Fraction(4)}},
                {"name": "balanced", "weights": {"compute": Fraction(1), "memory": Fraction(1)}},
            ),
        },
    }


def hostile_unmatched_twin():
    record = positive_record()
    record["matched_twin"]["negative"]["nuisance_capacity"]["max_depth"] = 1
    return record


def hostile_target_not_removed():
    record = positive_record()
    record["matched_twin"]["negative"]["target_mechanism_enabled"] = True
    return record


def hostile_compensating_macro():
    record = positive_record()
    record["matched_twin"]["negative"]["compensating_target_macro"] = True
    return record


def hostile_encoding_missing_candidate():
    record = positive_record()
    second = record["encodings"]["encodings"][1]
    first_key = next(iter(second["candidates"]))
    del second["candidates"][first_key]
    return record


def hostile_encoding_resource_change():
    record = positive_record()
    second = record["encodings"]["encodings"][1]
    first_key = next(iter(second["candidates"]))
    second["candidates"][first_key]["resources"]["compute"] += 1
    return record


def hostile_search_early_stop():
    record = positive_record()
    record["search"]["algorithms"] = (
        {"name": "exact_enumeration", "kind": "exhaustive", "order": tuple(row["id"] for row in record["search"]["candidates"])},
        {"name": "early_heuristic", "kind": "early_stop", "order": ("baseline", "k_balanced", "k_compute", "k_memory"), "limit": 1},
    )
    return record


def hostile_scalar_candidate_universal():
    record = positive_record()
    record["scalarization"]["claim_type"] = "CANDIDATE_UNIVERSAL"
    record["scalarization"].pop("claim_property", None)
    return record


def missing_control_record(control):
    record = positive_record()
    del record[control]
    return record


def canonicalize(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return [canonicalize(item) for item in value]
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonicalize(item) for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))}
    return value


def canonical_json(value):
    return json.dumps(canonicalize(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def build_receipt(root: Path | None = None, no_smuggling_override=None):
    parent = audit_parent_result(root)
    clean_override = no_smuggling_override
    positive = evaluate_record(positive_record(), root, clean_override)
    if clean_override is None:
        arm_audit = positive["controls"].get("no_smuggling", {}) if positive.get("controls") else {}
    else:
        arm_audit = clean_override
    unmatched = matched_twin_gate(hostile_unmatched_twin()["matched_twin"])
    not_removed = matched_twin_gate(hostile_target_not_removed()["matched_twin"])
    compensating = matched_twin_gate(hostile_compensating_macro()["matched_twin"])
    enc_missing = encoding_gate(hostile_encoding_missing_candidate()["encodings"])
    enc_resource = encoding_gate(hostile_encoding_resource_change()["encodings"])
    search_positive = search_gate(positive_record()["search"])
    search_hostile = search_gate(hostile_search_early_stop()["search"])
    scalar_positive = scalarization_gate(positive_record()["scalarization"])
    scalar_hostile = scalarization_gate(hostile_scalar_candidate_universal()["scalarization"])
    missing = {control: evaluate_record(missing_control_record(control), root, clean_override)["terminal"] for control in MISSING_CONTROL_TERMINALS}
    combined = evaluate_record(hostile_unmatched_twin(), root, clean_override)
    checks = {
        "parent_no_smuggling_result_pinned": parent["all_ok"],
        "positive_record_robust": positive["terminal"] == ROBUST,
        "matched_twin_capacity_hostile_flags": unmatched["terminal"] == "UNMATCHED_MECHANISM_TWIN",
        "target_removal_hostile_flags": not_removed["terminal"] == "TARGET_MECHANISM_NOT_REMOVED",
        "compensating_macro_hostile_flags": compensating["terminal"] == "COMPENSATING_TARGET_MACRO",
        "encoding_missing_candidate_flags": enc_missing["terminal"] == "ENCODING_NOT_SEMANTICALLY_EQUIVALENT",
        "encoding_resource_change_flags": enc_resource["terminal"] == "ENCODING_NOT_SEMANTICALLY_EQUIVALENT",
        "alternate_search_positive_robust": search_positive["terminal"] == "SEARCH_ROBUST",
        "early_stop_search_hostile_flags": search_hostile["terminal"] == "SEARCH_SENSITIVE",
        "pareto_property_robust_despite_identity_change": scalar_positive["terminal"] == "SCALARIZATION_ROBUST" and scalar_positive["candidate_identity_sensitive"],
        "universal_candidate_winner_hostile_flags": scalar_hostile["terminal"] == "SCALARIZATION_SENSITIVE",
        "missing_controls_fail_closed": all(value.startswith("CANNOT_ESTABLISH_D_ROBUSTNESS_") for value in missing.values()),
        "failed_control_blocks_global_robustness": combined["terminal"] == "D_ROBUSTNESS_NOT_ESTABLISHED",
        "no_smuggling_arms_clean": arm_audit.get("terminal") == "NO_SMUGGLING_ARMS_CLEAN",
    }
    return {
        "schema": "GMI833DerivationRobustnessControlsResultV1",
        "issue": 859,
        "parent_issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent,
        "positive": {
            "terminal": positive["terminal"],
            "matched_twin": positive.get("controls", {}).get("matched_twin", {}),
            "encoding": positive.get("controls", {}).get("encodings", {}),
            "search": search_positive,
            "scalarization": scalar_positive,
            "no_smuggling": arm_audit,
        },
        "hostiles": {
            "unmatched_twin": unmatched,
            "target_not_removed": not_removed,
            "compensating_macro": compensating,
            "encoding_missing_candidate": enc_missing,
            "encoding_resource_change": enc_resource,
            "search_early_stop": search_hostile,
            "scalar_candidate_universal": scalar_hostile,
            "missing_controls": missing,
            "combined_failed_control_terminal": combined["terminal"],
        },
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
