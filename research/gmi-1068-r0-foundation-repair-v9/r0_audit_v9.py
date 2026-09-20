"""Independent successor audit of the original eight R0 governance atoms."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

_spec = importlib.util.spec_from_file_location("r0_constants_v9", Path(__file__).with_name("constants_v9.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
_spec = importlib.util.spec_from_file_location("r0_schema_v9", Path(__file__).with_name("r0_schema_v9.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


class Invalid(ValueError):
    """Input was read and contradicts the registered requirement."""


class CannotCheck(RuntimeError):
    """Required input or git evidence could not be read."""


def need(condition, reason):
    if not condition:
        raise Invalid(reason)


def indexed(rows, expected, label):
    need(type(rows) is list and all(type(r) is dict for r in rows), label + "_ROWS")
    ids = [r["id"] for r in rows]
    need(len(ids) == len(set(ids)) and set(ids) == set(expected), label + "_IDS")
    return {r["id"]: r for r in rows}


def _validate(b):
    need(type(b) is dict and set(b) == set(C.FILES), "BUNDLE_FILES")
    S.validate_structure(b, need)
    for name, schema in C.SCHEMAS.items():
        need(type(b[name]) is dict and b[name]["schema"] == schema, "SCHEMA:" + name)
        if name != "THEOREM_STATUS_V1.json":
            need(type(b[name]["source_issue"]) is int and b[name]["source_issue"] == 1068, "SOURCE_ISSUE")
    freeze = b["FREEZE_V1.md"]
    need(type(freeze) is str and "working hypothesis" in freeze and
         "R0 does NOT establish this fixed point" in freeze, "HYPOTHESIS_FREEZE")
    need(all("- " + text in freeze for text in C.FORBIDDEN), "FORBIDDEN_PROMOTIONS")
    need(C.SOURCE_MAIN in freeze and "Issue: #1068" in freeze and
         "Parent programme: #833" in freeze, "FREEZE_PROVENANCE")
    checklist = b["ATOMIC_CHECKLIST_V1.json"]
    need(checklist["source_main"] == C.SOURCE_MAIN and checklist["freeze_commit"] == C.FREEZE, "CHECKLIST_SOURCE")
    expected = {f"GMI2-{r}-{i:03d}": (r, title, kind)
                for r, rows in C.ATOMS.items() for i, (title, kind) in enumerate(rows, 1)}
    atoms = indexed(checklist["rows"], expected, "ATOM")
    need(type(checklist["row_count"]) is int and checklist["row_count"] == len(atoms) == 205, "ATOM_COUNT")
    for key, row in atoms.items():
        r, title, kind = expected[key]
        need(row["round"] == r and row["title"] == title, "ATOM_ROUND_TITLE")
        need(row["authoritative_owner"] == "#1068/" + r, "ATOM_OWNER")
        need(row["evidence_kind"] in C.EVIDENCE and row["evidence_kind"] == kind, "ATOM_EVIDENCE")
        need(row["status"] == "NOT_STARTED" and row["closes_by_prose"] is False, "ATOM_INITIAL_STATUS")
    dag = b["THEORY_DAG_V1.json"]
    nodes, deps = dag["nodes"], dag["dependencies"]
    need(type(nodes) is list and len(nodes) == len(set(nodes)) == 17 and
         set(nodes) == set(C.DAG) == set(deps), "DAG_NODES")
    for node in nodes:
        parents = deps[node]
        need(type(parents) is list and len(parents) == len(set(parents)), "DAG_DUPLICATE_EDGE")
        need(set(parents) <= set(nodes), "DAG_UNKNOWN_PARENT")
    seen, active = set(), set()
    def visit(node):
        need(node not in active, "DAG_CYCLE")
        if node in seen:
            return
        active.add(node)
        for parent in deps[node]:
            visit(parent)
        active.remove(node)
        seen.add(node)
    for node in nodes:
        visit(node)
        need(set(deps[node]) == set(C.DAG[node]), "DAG_CANONICAL_EDGES")
    parents = indexed(b["PARENT_REGISTRY_V1.json"]["entries"], C.PARENTS, "PARENT")
    for key, row in parents.items():
        title, source, role, lane = C.PARENTS[key]
        need(type(row["source_id"]) is str and bool(row["source_id"].strip()), "PARENT_SOURCE")
        need(row["role"] in C.OWNERSHIP, "PARENT_ROLE")
        need(all(r in C.DAG for r in row["lane"].split("/")), "PARENT_LANE")
        need((row["title"], row["source_id"], row["role"], row["lane"]) ==
             (title, source, role, lane), "PARENT_REGISTERED_FIELDS")
    registry = b["THEOREM_STATUS_V1.json"]
    allowed = registry["allowed_status"]
    need(type(allowed) is list and len(allowed) == len(set(allowed)) == len(C.STATUSES)
         and set(allowed) == set(C.STATUSES), "THEOREM_VOCABULARY")
    theorems = indexed(registry["entries"], C.THEOREMS, "THEOREM")
    for key, row in theorems.items():
        need(row["status"] in C.STATUSES, "THEOREM_STATUS")
        need((row["title"], row["status"], row["owner_round"]) == C.THEOREMS[key], "THEOREM_UNSUPPORTED_CHANGE")
    gate = b["MERGE_GATE_V1.json"]
    for key, target in (("requirements", C.GATE_RULES), ("valid_nonpositive_terminals", C.NONPOSITIVE)):
        values = gate[key]
        need(type(values) is list and len(values) == len(set(values)) == len(target)
             and set(values) == set(target), "MERGE_GATE:" + key)
    counts = dict(atomic_rows=len(atoms), rounds=len(nodes), parent_entries=len(parents),
                  theorem_entries=len(theorems), dag_nodes=len(nodes), expected_hostiles=6)
    result = b["RESULT_V1.json"]
    for key, value in counts.items():
        need(type(result[key]) is int and result[key] == value, "HISTORICAL_RESULT:" + key)
    need(result["freeze_commit"] == C.FREEZE and result["status"] == "GREEN_REGISTRY_CONSTITUTION_ONLY"
         and result["claim_ceiling"] == "GRAND_GMI_V2_R0_PROGRAMME_REGISTRY_AND_EXECUTION_CONSTITUTION_ONLY",
         "HISTORICAL_RESULT_AUTHORITY")
    need(type(b["check_r0.py"]) is str and bool(b["check_r0.py"].strip()), "MISSING_HISTORICAL_CHECKER")
    return counts


def validate(bundle):
    """Semantic validation only: mutations are not rejected by file digests."""
    try:
        return _validate(bundle)
    except (KeyError, TypeError, AttributeError) as exc:
        raise Invalid("MALFORMED_STRUCTURE:" + str(exc)) from exc


def read_bundle(root):
    raw = {}
    try:
        for name in C.FILES:
            raw[name] = (Path(root) / C.BASE / name).read_bytes()
    except OSError as exc:
        raise CannotCheck("UNREADABLE_INPUT:" + str(exc)) from exc
    try:
        bundle = {n: json.loads(v) if n.endswith(".json") else v.decode() for n, v in raw.items()}
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Invalid("MALFORMED_INPUT:" + str(exc)) from exc
    return bundle, raw


def _git(root, *args):
    try:
        result = subprocess.run(["/usr/bin/git", "-C", str(root), *args], capture_output=True, text=True)
    except OSError as exc:
        raise CannotCheck("GIT_UNAVAILABLE") from exc
    if result.returncode not in (0, 1):
        raise CannotCheck("GIT_EVIDENCE_UNAVAILABLE:" + result.stderr.strip())
    return result.stdout.strip()


def evaluate(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    bundle, raw = read_bundle(root)
    counts = validate(bundle)
    head = _git(root, "rev-parse", "HEAD")
    need(_git(root, "merge-base", C.BASELINE, head) == C.BASELINE, "BASELINE_NOT_ANCESTOR")
    need(_git(root, "merge-base", C.SOURCE_MAIN, C.FREEZE) == C.SOURCE_MAIN, "SOURCE_NOT_ANCESTOR")
    need(_git(root, "merge-base", C.FREEZE, head) == C.FREEZE, "FREEZE_NOT_ANCESTOR")
    need(_git(root, "ls-tree", "-r", "--name-only", C.FREEZE, C.BASE).splitlines() ==
         [C.BASE + "FREEZE_V1.md"], "FREEZE_NOT_ONLY")
    for name, (introduced, digest) in C.CUSTODY.items():
        need(hashlib.sha256(raw[name]).hexdigest() == digest, "FROZEN_CONTENT_DRIFT:" + name)
        need(_git(root, "merge-base", introduced, head) == introduced, "INTRO_NOT_ANCESTOR:" + name)
        need(_git(root, "merge-base", C.FREEZE, introduced) == C.FREEZE, "INTRO_BEFORE_FREEZE:" + name)
        need(name == "FREEZE_V1.md" or introduced != C.FREEZE, "OUTCOME_IN_FREEZE")
        need(_git(root, "diff-tree", "--no-commit-id", "--name-status", "-r", introduced, "--", C.BASE + name)
             == "A\t" + C.BASE + name, "INTRO_NOT_ADDITION:" + name)
    summaries = ("Freeze-only constitution, source ancestry and unchanged historical delivery",
                 "Candidate fixed point explicitly remains a hypothesis",
                 "All 205 original atomic identities, owners and initial states validated",
                 "Nine original theorem entries and authority statuses preserved",
                 "Thirteen original source anchors and ownership roles preserved",
                 "Exact original seventeen-round dependency DAG is acyclic and complete",
                 "Eight frozen merge rules and four nonpositive outcomes preserved",
                 "Independent semantic checks and historical content/custody checks pass")
    return {"schema": "GMI_1068_R0_AUDIT_V9", "scope": "GOVERNANCE_ONLY", "counts": counts,
            "atoms": {f"GMI2-R0-{i:03d}": {"status": "VERIFIED_GOVERNANCE", "evidence": text}
                      for i, text in enumerate(summaries, 1)},
            "custody": {"source_main": C.SOURCE_MAIN, "freeze": C.FREEZE, "baseline": C.BASELINE,
                        "files": {n: {"introduced": v[0], "sha256": v[1]} for n, v in C.CUSTODY.items()}},
            "overall_closure": "OPEN", "scientific_truth_certified": False}


def main():
    try:
        if len(sys.argv) > 2:
            raise CannotCheck("usage: r0_audit_v9.py [repository]")
        print(json.dumps(evaluate(sys.argv[1] if len(sys.argv) == 2 else None), sort_keys=True))
        return 0
    except (Invalid, CannotCheck) as exc:
        print(json.dumps({"status": "CANNOT_CHECK" if isinstance(exc, CannotCheck) else "INVALID",
                          "reason": str(exc)}))
        return 2 if isinstance(exc, CannotCheck) else 1


if __name__ == "__main__":
    raise SystemExit(main())
