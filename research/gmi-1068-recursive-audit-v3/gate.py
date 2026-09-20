#!/usr/bin/env python3
"""Validate custody and scope accounting under a reviewer-trusted checker.

Hashes and locators do not establish theorem truth. A successful run explicitly
reports OPEN overall closure. This version cannot certify complete GMI.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

NODES = tuple(f"R{i}" for i in range(18))
DAG = {
    "R0": [], "R1": ["R0"], "R2": ["R0", "R1"],
    "R3": ["R1", "R2"], "R4": ["R3"],
    "R5": ["R1", "R3", "R4"],
    "R6": ["R1", "R2", "R3", "R4", "R5"], "R7": ["R6"],
    "R8": ["R6", "R7"], "R9": ["R1", "R2", "R3", "R6"],
    "R10": ["R2", "R3", "R4", "R9"],
    "R11": ["R3", "R4", "R9", "R10"],
    "R12": ["R3", "R4", "R5", "R9", "R10", "R11"],
    "R13": ["R6", "R7", "R8", "R9", "R10", "R11", "R12"],
    "R14": ["R1", "R2", "R3", "R4", "R5", "R6", "R9", "R10"],
    "R15": [f"R{i}" for i in range(1, 15)],
    "R16": ["R13", "R14", "R15"],
    "R17": [f"R{i}" for i in range(17)],
}
COUNTS = (8, 10, 9, 10, 10, 10, 15, 13, 14, 9, 10, 13, 17, 11, 14, 18, 14, 17)
STATUSES = {"EARNED", "OPEN", "STALE", "UNKNOWN", "CANNOT_CHECK", "NOT_STARTED"}
ATOM_STATUSES = {"CLOSED", "OPEN", "UNKNOWN", "CANNOT_CHECK", "NOT_STARTED"}
HEX = re.compile(r"[0-9a-f]{64}\Z")
CLAIM = "REGISTERED_SCOPE_INTEGRITY_ONLY_NOT_SCIENTIFIC_COMPLETENESS"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def evidence_digest(row):
    # Include status, obligations and parent bindings, not only file names.
    return digest({k: row[k] for k in ("status", "scope", "artifacts", "obligations", "parent_bindings", "local_repairs")})


def resolve(root, rel):
    need(isinstance(rel, str) and bool(rel), "INVALID_PATH")
    p = PurePosixPath(rel)
    need(not p.is_absolute() and ".." not in p.parts and str(p) == rel, "UNSAFE_PATH:" + rel)
    target = (root / rel).resolve()
    need(target.is_relative_to(root.resolve()) and target.is_file(), "MISSING_OR_EXTERNAL_FILE:" + rel)
    return target


def verify_artifact(root, artifact):
    need(isinstance(artifact, dict) and set(artifact) == {"path", "sha256"}, "ARTIFACT_SCHEMA")
    need(isinstance(artifact["sha256"], str) and bool(HEX.fullmatch(artifact["sha256"])), "BAD_SHA256")
    target = resolve(root, artifact["path"])
    need(hashlib.sha256(target.read_bytes()).hexdigest() == artifact["sha256"], "ARTIFACT_DRIFT:" + artifact["path"])
    return target


def verify_locator(root, witness, artifacts):
    need(isinstance(witness, dict) and set(witness) == {"path", "sha256", "kind", "locator"}, "WITNESS_SCHEMA")
    path = witness["path"]
    need(path in artifacts and artifacts[path] == witness["sha256"], "UNBOUND_WITNESS")
    target = verify_artifact(root, {"path": path, "sha256": witness["sha256"]})
    content = target.read_text()
    kind, locator = witness["kind"], witness["locator"]
    need(isinstance(locator, str) and bool(locator), "EMPTY_LOCATOR")
    if kind == "python_symbol":
        tree = ast.parse(content)
        found = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == locator for n in ast.walk(tree))
    elif kind == "lean_declaration":
        found = re.search(r"(?m)^\s*(?:theorem|lemma|def)\s+" + re.escape(locator) + r"\b", content) is not None
    elif kind == "markdown_heading":
        found = any(line.lstrip("#").strip() == locator and line.startswith("#") for line in content.splitlines())
    elif kind == "json_pointer":
        need(locator.startswith("/") and re.search(r"~(?![01])", locator) is None, "INVALID_JSON_POINTER")
        value = json.loads(content)
        try:
            for token in locator[1:].split("/"):
                token = token.replace("~1", "/").replace("~0", "~")
                if isinstance(value, list):
                    need(re.fullmatch(r"0|[1-9][0-9]*", token) is not None, "INVALID_ARRAY_POINTER")
                    value = value[int(token)]
                else:
                    value = value[token]
            found = True
        except (ValueError, KeyError, IndexError, TypeError):
            found = False
    else:
        raise ValueError("UNSUPPORTED_WITNESS_KIND:" + str(kind))
    need(found, "MISSING_WITNESS_LOCATOR:" + path + "::" + locator)


def infer_rounds(paths):
    out = set()
    for path in paths:
        if re.search(r"(?:^|/)gmi-1068-grand-unified-v2-r0(?:/|$)", path) or "gmi-1068-r0-programme-registry-" in path:
            out.add("R0")
        match = re.search(r"(?:^|/)gmi-1068-r(\d+)(?:-|/)", path)
        if match:
            name = "R" + str(int(match.group(1)))
            need(name in NODES, "UNKNOWN_CHANGED_ROUND:" + name)
            out.add(name)
    return out


def descendants(parent):
    out = set()
    for node in NODES:
        if parent in DAG[node] or any(p in out for p in DAG[node]):
            out.add(node)
    return out


def validate(snapshot, root):
    need(set(snapshot) == {"schema", "source_issue", "observed_main", "audited_base", "claim_ceiling", "overall_closure", "scientific_truth_certified", "trust_boundary", "dependencies", "rounds"}, "SNAPSHOT_FIELDS")
    need(snapshot["source_issue"] == 1068, "WRONG_CONTROL_PLANE")
    need(all(isinstance(snapshot[k], str) and re.fullmatch(r"[0-9a-f]{40}", snapshot[k]) for k in ("observed_main", "audited_base")), "SOURCE_REF_FORMAT")
    need(snapshot["schema"] == "GMI_1068_SCOPE_SNAPSHOT_V3", "SCHEMA")
    need(snapshot["claim_ceiling"] == CLAIM and snapshot["overall_closure"] == "OPEN", "GLOBAL_PROMOTION_FORBIDDEN")
    need(snapshot["scientific_truth_certified"] is False, "SCIENTIFIC_TRUTH_PROMOTION")
    need(snapshot["dependencies"] == DAG, "CANONICAL_DAG_DRIFT")
    need(set(snapshot["rounds"]) == set(NODES), "ROUND_COVERAGE")
    need(snapshot["trust_boundary"] == "reviewer_trusted_checker_and_adjudication", "TRUST_BOUNDARY_DRIFT")
    rows = snapshot["rounds"]
    hashes = {}
    open_count = 0
    for index, name in enumerate(NODES):
        row = rows[name]
        need(set(row) == {"status", "scope", "historical_reconciliation_status", "artifacts", "obligations", "local_repairs", "parent_bindings", "evidence_digest"}, "ROUND_FIELDS:" + name)
        need(row["status"] in STATUSES, "ROUND_STATUS:" + name)
        need(isinstance(row["scope"], str) and bool(row["scope"].strip()), "EMPTY_SCOPE:" + name)
        need(isinstance(row["historical_reconciliation_status"], str) and bool(row["historical_reconciliation_status"]), "MISSING_HISTORY:" + name)
        need(isinstance(row["artifacts"], list), "ARTIFACT_LIST:" + name)
        artifacts = {}
        for artifact in row["artifacts"]:
            verify_artifact(root, artifact)
            need(artifact["path"] not in artifacts, "DUPLICATE_ARTIFACT:" + name)
            artifacts[artifact["path"]] = artifact["sha256"]
        need(isinstance(row["local_repairs"], list), "LOCAL_REPAIR_SCHEMA:" + name)
        repair_ids = set()
        for repair in row["local_repairs"]:
            need(set(repair) == {"id", "scope", "status", "evidence"}, "REPAIR_SCHEMA")
            need(repair["id"] not in repair_ids, "DUPLICATE_REPAIR")
            repair_ids.add(repair["id"])
            need(repair["status"] in {"LOCAL_VERIFIED", "PENDING_REVIEW"}, "REPAIR_STATUS")
            need(isinstance(repair["scope"], str) and bool(repair["scope"].strip()), "REPAIR_SCOPE")
            need(isinstance(repair["evidence"], list) and bool(repair["evidence"]), "REPAIR_EVIDENCE")
            for witness in repair["evidence"]:
                verify_locator(root, witness, artifacts)
        obligations = row["obligations"]
        expected = [f"GMI2-{name}-{i:03d}" for i in range(1, COUNTS[index] + 1)]
        need([o["id"] for o in obligations] == expected, "ATOMIC_COVERAGE:" + name)
        for atom in obligations:
            need(set(atom) == {"id", "title", "historical_status", "status", "disposition", "evidence"}, "ATOM_FIELDS")
            need(atom["historical_status"] == "NOT_STARTED", "HISTORICAL_ATOM_DRIFT")
            need(atom["status"] in ATOM_STATUSES, "ATOMIC_STATUS:" + atom["id"])
            need(isinstance(atom["disposition"], str) and bool(atom["disposition"].strip()), "MISSING_DISPOSITION:" + atom["id"])
            need(isinstance(atom["evidence"], list), "ATOMIC_EVIDENCE_SCHEMA")
            for witness in atom["evidence"]:
                verify_locator(root, witness, artifacts)
            if atom["status"] == "CLOSED":
                need(bool(atom["evidence"]), "CLOSED_WITHOUT_WITNESS:" + atom["id"])
            else:
                open_count += 1
        bindings = row["parent_bindings"]
        need(set(bindings) == set(DAG[name]), "PARENT_BINDING_KEYS:" + name)
        for parent in DAG[name]:
            need(bindings[parent] == hashes[parent], "PARENT_EVIDENCE_DRIFT:" + name + ":" + parent)
        if row["status"] == "EARNED":
            need(bool(artifacts), "EARNED_WITHOUT_ARTIFACTS:" + name)
            need(all(o["status"] == "CLOSED" for o in obligations), "EARNED_WITH_UNRESOLVED_ATOM:" + name)
            need(all(rows[p]["status"] == "EARNED" for p in DAG[name]), "EARNED_WITH_UNEARNED_PARENT:" + name)
        hashes[name] = evidence_digest(row)
        need(row["evidence_digest"] == hashes[name], "ROUND_DIGEST_DRIFT:" + name)
    for name in NODES:
        if rows[name]["status"] == "STALE":
            need(not any(rows[d]["status"] == "EARNED" for d in descendants(name)), "STALE_HAS_EARNED_DESCENDANT:" + name)
    return {"status": "GREEN_AT_INTEGRITY_SCOPE", "overall_closure": "OPEN", "scientific_truth_certified": False,
            "rounds": len(NODES), "registered_atoms": sum(COUNTS), "unresolved_atoms": open_count,
            "earned_rounds": [n for n in NODES if rows[n]["status"] == "EARNED"],
            "stale_rounds": [n for n in NODES if rows[n]["status"] == "STALE"],
            "stale_closure": [n for n in NODES if rows[n]["status"] == "STALE" or any(rows[p]["status"] == "STALE" and n in descendants(p) for p in NODES)]}


def read_json(path):
    # Supplied missing or unreadable baselines must raise; never disable the gate.
    return json.loads(Path(path).read_text())


def validate_baseline(current, baseline, paths):
    need(baseline["schema"] == "GMI_1068_SCOPE_SNAPSHOT_V3", "BASELINE_SCHEMA")
    need(baseline["dependencies"] == DAG and set(baseline["rounds"]) == set(NODES), "BASELINE_COVERAGE")
    touched = infer_rounds(paths)
    for name in NODES:
        old, new = baseline["rounds"][name], current["rounds"][name]
        need(old["evidence_digest"] == evidence_digest(old), "BASELINE_DIGEST_DRIFT:" + name)
        if old["status"] != "EARNED" and new["status"] == "EARNED":
            need(name in touched, "STATUS_ONLY_PROMOTION:" + name)
        if old["evidence_digest"] != new["evidence_digest"]:
            for child in descendants(name):
                if current["rounds"][child]["status"] == "EARNED":
                    need(child in touched, "CHANGED_PARENT_WITHOUT_DESCENDANT_REVIEW:" + child)
    return sorted(touched, key=lambda n: int(n[1:]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default=str(Path(__file__).with_name("SCOPE_SNAPSHOT_V3.json")))
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    custody = parser.add_mutually_exclusive_group(required=True)
    custody.add_argument("--baseline")
    custody.add_argument("--initial-introduction", action="store_true", help="CI must independently verify no prior gate exists on the target base")
    parser.add_argument("--changed-files")
    args = parser.parse_args()
    need(args.initial_introduction or bool(args.baseline), "EMPTY_BASELINE_FORBIDDEN")
    need(bool(args.baseline) == bool(args.changed_files), "BASELINE_AND_CHANGED_FILES_REQUIRED_TOGETHER")
    current = read_json(args.snapshot)
    result = validate(current, Path(args.repo))
    result["baseline_applied"] = False
    result["initial_introduction"] = args.initial_introduction
    if args.baseline:
        baseline = read_json(args.baseline)
        paths = Path(args.changed_files).read_text().splitlines()
        result["touched_rounds"] = validate_baseline(current, baseline, paths)
        result["baseline_applied"] = True
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, SyntaxError) as exc:
        print("SCOPE_GATE_RED:" + str(exc), file=sys.stderr)
        sys.exit(1)
