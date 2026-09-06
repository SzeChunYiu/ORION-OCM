"""Isolated exact-source digest compatibility control; no OCM runtime or study."""
import hashlib
import importlib
import json
import sys
import types
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(space):
    body = {"atoms": [a.as_dict() for a in space.atoms],
            "hyperedges": [e.as_dict() for e in space.hyperedges]}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return raw, sha(raw.encode("utf-8"))

def load(arm):
    name = "_pr90_" + arm
    package = types.ModuleType(name)
    package.__path__ = [str(ROOT / arm)]
    sys.modules[name] = package
    return importlib.import_module(name + ".space")

def make(M):
    atom_payload = {"nested": {"labels": ["initial"]}}
    edge_payload = {"nested": {"labels": ["initial"]}}
    a = M.Atom("a", "claim", meta=(("review", atom_payload),))
    b = M.Atom("b", "claim")
    e = M.Hyperedge("e", ("a",), ("b",), "SUPPORT", meta=(("review", edge_payload),))
    return M.KnowledgeSpace((a, b), (e,)), atom_payload, edge_payload

def observe(M, case):
    space, atom_payload, edge_payload = make(M)
    before_raw, before_fresh = canonical(space)
    before_reported = space.digest()
    if before_reported != before_fresh:
        raise RuntimeError("clean canonical no-alarm failed")
    if case == "atom_nested_metadata":
        atom_payload["nested"]["labels"].append("changed")
    elif case == "edge_nested_metadata":
        edge_payload["nested"]["labels"].append("changed")
    elif case == "atom_as_dict_nested_alias":
        space.atoms[0].as_dict()["meta"]["review"]["nested"]["labels"].append("changed")
    elif case == "edge_as_dict_nested_alias":
        space.hyperedges[0].as_dict()["meta"]["review"]["nested"]["labels"].append("changed")
    elif case == "new_constructor_after_nested_mutation":
        atom_payload["nested"]["labels"].append("changed")
        space = M.KnowledgeSpace(space.atoms, space.hyperedges, space.registry)
    elif case == "new_generation_with_atoms":
        space = space.with_atoms(M.Atom("c", "claim"))
    elif case == "new_generation_with_edges":
        space = space.with_edges(M.Hyperedge("f", ("b",), ("a",), "SUPPORT"))
    elif case != "unchanged_repeat":
        raise ValueError(case)
    after_raw, after_fresh = canonical(space)
    after_reported = space.digest()
    return {"case": case, "before_fresh": before_fresh, "before_reported": before_reported,
            "after_fresh": after_fresh, "after_reported": after_reported,
            "canonical_changed": before_raw != after_raw,
            "matches_fresh_canonical": after_reported == after_fresh,
            "before_canonical": before_raw, "after_canonical": after_raw}

def main():
    bindings = json.loads((ROOT / "source-bindings.json").read_text())
    for path, item in bindings["files"].items():
        if sha((ROOT/path).read_bytes()) != item["sha256"]:
            raise RuntimeError("source drift " + path)
    cases = ("unchanged_repeat", "atom_nested_metadata", "edge_nested_metadata",
             "atom_as_dict_nested_alias", "edge_as_dict_nested_alias",
             "new_constructor_after_nested_mutation", "new_generation_with_atoms",
             "new_generation_with_edges")
    results = {arm: [observe(load(arm), case) for case in cases]
               for arm in ("baseline", "candidate")}
    if not all(row["matches_fresh_canonical"] for row in results["baseline"]):
        raise RuntimeError("baseline no-alarm failed")
    for arm, rows in results.items():
        if any(row["canonical_changed"] != (row["case"] != "unchanged_repeat") for row in rows):
            raise RuntimeError("mutation/generation was not applied " + arm)
    failures = [r["case"] for r in results["candidate"] if not r["matches_fresh_canonical"]]
    observed = {"schema": "pr90.digest.compatibility.control.v1",
                "terminal": "COMPATIBILITY_REGRESSION_PROVED" if failures else "NO_REGRESSION_OBSERVED",
                "started_scope": "isolated source modules; no runtime, solver, model, or performance test",
                "utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
                "executable": sys.executable, "source_bindings": bindings,
                "control_sha256": sha(Path(__file__).read_bytes()),
                "results": results, "candidate_failure_cases": failures}
    (ROOT / "observed.json").write_text(json.dumps(observed, indent=2) + "\n")
    for path, item in bindings["files"].items():
        if sha((ROOT/path).read_bytes()) != item["sha256"]:
            raise RuntimeError("post-control source drift " + path)
    print(json.dumps({"terminal": observed["terminal"], "baseline": "8/8 canonical matches",
                      "candidate_matches": 8-len(failures), "candidate_mismatches": failures,
                      "observed_sha256": sha((ROOT/"observed.json").read_bytes())}, indent=2))

if __name__ == "__main__":
    main()
