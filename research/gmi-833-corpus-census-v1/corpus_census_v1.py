#!/usr/bin/env python3
"""Frozen-source GMI corpus census for #833/#842.

This module inventories the corpus at the SHA pinned in FREEZE_V1.md.  It is a
structural/provenance audit, not a theorem prover.  Unknown scientific material
is retained as an explicit gap rather than silently omitted.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
FREEZE = HERE / "FREEZE_V1.md"

FILE_ROLES = {
    "SCIENTIFIC_TEXT", "MACHINE_METADATA", "EXECUTABLE_WITNESS",
    "TEST_OR_HOSTILE", "RECEIPT_OR_RESULT", "WORKFLOW_OR_OPS",
    "DATA_OR_FIXTURE", "ANCILLARY", "UNKNOWN",
}
OBJECT_CLASSES = {
    "AXIOM", "DEFINITION", "THEOREM", "LEMMA", "PROPOSITION", "COROLLARY",
    "LAW", "CLAIM", "ALGORITHM", "EXPERIMENT", "RECEIPT_CERTIFICATE",
    "PROTOCOL", "FALSIFIER_COUNTEREXAMPLE", "OTHER_SCIENTIFIC_OBJECT", "UNKNOWN",
}
QUANTIFIERS = {
    "UNIVERSAL", "FINITE_EXACT", "HELD_OUT", "SAMPLED_STATISTICAL",
    "EXISTENTIAL_WITNESS", "CONDITIONAL", "UNKNOWN",
}
PROOF_MODES = {
    "ANALYTIC_DEDUCTIVE", "MECHANIZED_PROOF", "COMPUTER_ASSISTED_EXHAUSTIVE",
    "FINITE_EXECUTABLE_CERTIFICATE", "STATISTICAL_EXPERIMENT", "EMPIRICAL_EXPERIMENT",
    "PROTOCOL_ONLY", "MIXED", "UNKNOWN",
}
DISPOSITIONS = {"RED", "AMBER", "GREEN"}

MARKER = re.compile(
    r"\b(axiom|definition|theorem|lemma|proposition|corollary|law|claim|algorithm|"
    r"experiment|receipt|certificate|protocol|falsifier|counterexample|proof)\b",
    re.IGNORECASE,
)
EXPLICIT_ID = re.compile(r"\b([A-Z][A-Z0-9]*(?:[-_.][A-Z0-9]+){1,5})\b")
DEP_LINE = re.compile(r"\b(?:claim|theorem)[-_ ]dependencies?\s*[:=]\s*(.+)$", re.IGNORECASE)
UNIVERSAL = re.compile(r"\b(for\s+all|forall|every|all\s+(?:machines?|tasks?|systems?|cases?)|universal)\b", re.I)
FINITE = re.compile(r"\b(finite|bounded|exhaustive|enumerat|registered\s+scope|exact\s+scope|n\s*[<≤])\b", re.I)
HELD = re.compile(r"\b(held[- ]?out|protected\s+(?:set|split|case))\b", re.I)
SAMPLED = re.compile(r"\b(sample|confidence|statistical|p[- ]?value|coverage|random(?:ized)?)\b", re.I)
EXISTENTIAL = re.compile(r"\b(exists|existential|witness|counterexample)\b", re.I)
CONDITIONAL = re.compile(r"\b(if|assuming|assumption|conditional|under\s+(?:the|a|this)|provided\s+that)\b", re.I)


class CensusError(RuntimeError):
    pass


def sh(*args: str, cwd: Path = REPO_ROOT) -> bytes:
    proc = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode:
        raise CensusError(f"command failed {args!r}: {proc.stderr.decode('utf-8', 'replace')}")
    return proc.stdout


def frozen_sha() -> str:
    text = FREEZE.read_text(encoding="utf-8")
    m = re.search(r"Frozen source authority:\*\* `([0-9a-f]{40})`", text)
    if not m:
        raise CensusError("FREEZE_V1.md does not contain an exact frozen SHA")
    return m.group(1)


def is_primary_candidate(path: str) -> bool:
    parts = [p.lower() for p in Path(path).parts]
    return path.startswith("research/") and any(
        p.startswith("gmi-") or p.startswith("gmi_") or p == "machine-intelligence-morphogenesis-v1"
        for p in parts
    )


def tracked_research_paths(ref: str) -> list[str]:
    raw = sh("git", "ls-tree", "-r", "-z", "--name-only", ref, "--", "research")
    paths = [p.decode("utf-8") for p in raw.split(b"\0") if p]
    return sorted(paths)


def blob_bytes(ref: str, path: str) -> bytes:
    return sh("git", "show", f"{ref}:{path}")


def blob_sha(ref: str, path: str) -> str:
    return sh("git", "rev-parse", f"{ref}:{path}").decode().strip()


def file_role(path: str, data: bytes) -> tuple[str, str | None]:
    name = Path(path).name.lower()
    suffix = Path(path).suffix.lower()
    if name.startswith("test_") or "/tests/" in f"/{path.lower()}/" or "hostile" in name:
        return "TEST_OR_HOSTILE", None
    if any(x in name for x in ("receipt", "result", "certificate")) and suffix in {".json", ".md", ".txt"}:
        return "RECEIPT_OR_RESULT", None
    if suffix in {".yml", ".yaml"} or "workflow" in name or "reconcile" in name:
        return "WORKFLOW_OR_OPS", None
    if suffix == ".md":
        return "SCIENTIFIC_TEXT", None
    if suffix == ".py":
        return "EXECUTABLE_WITNESS", None
    if suffix == ".json":
        if any(x in name for x in ("manifest", "schema", "registry", "freeze", "prediction")):
            return "MACHINE_METADATA", None
        return "DATA_OR_FIXTURE", None
    if suffix in {".csv", ".tsv", ".jsonl", ".ndjson", ".toml", ".ini"}:
        return "DATA_OR_FIXTURE", None
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return "ANCILLARY", "binary_or_non_utf8"
    return "ANCILLARY", "unregistered_text_role"


def object_class_for(text: str) -> str:
    lower = text.lower()
    for token, cls in (
        ("axiom", "AXIOM"), ("definition", "DEFINITION"), ("theorem", "THEOREM"),
        ("lemma", "LEMMA"), ("proposition", "PROPOSITION"), ("corollary", "COROLLARY"),
        ("law", "LAW"), ("claim", "CLAIM"), ("algorithm", "ALGORITHM"),
        ("experiment", "EXPERIMENT"), ("receipt", "RECEIPT_CERTIFICATE"),
        ("certificate", "RECEIPT_CERTIFICATE"), ("protocol", "PROTOCOL"),
        ("falsifier", "FALSIFIER_COUNTEREXAMPLE"), ("counterexample", "FALSIFIER_COUNTEREXAMPLE"),
        ("proof", "OTHER_SCIENTIFIC_OBJECT"),
    ):
        if re.search(rf"\b{re.escape(token)}\b", lower):
            return cls
    return "UNKNOWN"


def quantifier_for(text: str) -> str:
    if HELD.search(text): return "HELD_OUT"
    if SAMPLED.search(text): return "SAMPLED_STATISTICAL"
    if FINITE.search(text): return "FINITE_EXACT"
    if UNIVERSAL.search(text): return "UNIVERSAL"
    if EXISTENTIAL.search(text): return "EXISTENTIAL_WITNESS"
    if CONDITIONAL.search(text): return "CONDITIONAL"
    return "UNKNOWN"


def proof_mode_for(text: str, path: str) -> str:
    t = text.lower(); p = path.lower()
    if "lean" in t or "coq" in t or "isabelle" in t or "proof assistant" in t:
        return "MECHANIZED_PROOF"
    if "exhaustive" in t or "enumerat" in t:
        return "COMPUTER_ASSISTED_EXHAUSTIVE"
    if "analytic proof" in t or "deductive proof" in t or "prove" in t or "theorem" in t:
        return "ANALYTIC_DEDUCTIVE"
    if "confidence" in t or "statistical" in t or "sample" in t:
        return "STATISTICAL_EXPERIMENT"
    if "experiment" in t or "benchmark" in t or "real-scale" in t:
        return "EMPIRICAL_EXPERIMENT"
    if "protocol" in t or "freeze" in p:
        return "PROTOCOL_ONLY"
    if "certificate" in t or "receipt" in t or p.endswith(".py"):
        return "FINITE_EXECUTABLE_CERTIFICATE"
    return "UNKNOWN"


def normalized_statement(text: str) -> str:
    return " ".join(text.strip().split())


def provisional_id(path: str, line: int, text: str) -> str:
    raw = f"{path}:{line}:{normalized_statement(text)}".encode()
    return "AUTO-" + hashlib.sha256(raw).hexdigest()[:20].upper()


def explicit_id_for(text: str) -> str | None:
    hits = EXPLICIT_ID.findall(text)
    return hits[0] if hits else None


def claim_dependencies_for(text: str) -> list[str]:
    m = DEP_LINE.search(text)
    if not m:
        return []
    return sorted(set(EXPLICIT_ID.findall(m.group(1))))


def canonical_json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def make_gap(*, gap_id: str, claim_id: str, premise: str, inference: str,
             assumption: str, counterexample: str, severity: str, evidence: str,
             parent: str = "T833-B1-AA", materiality: str = "MATERIAL") -> dict[str, object]:
    return {
        "id": gap_id, "claim_id": claim_id, "premise": premise, "inference": inference,
        "unresolved_assumption": assumption, "possible_counterexample": counterexample,
        "severity": severity, "owner_role": "HOSTILE_VERIFICATION",
        "parent_result": parent, "evidence_needed": evidence,
        "status": "OPEN", "materiality": materiality, "descendants": [],
    }


def scientific_objects(path: str, text: str, sha: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not MARKER.search(line):
            continue
        statement = normalized_statement(line)
        cls = object_class_for(statement)
        explicit = explicit_id_for(statement)
        oid = explicit or provisional_id(path, lineno, statement)
        quant = quantifier_for(statement)
        mode = proof_mode_for(statement, path)
        out.append({
            "object_id": oid,
            "id_kind": "EXPLICIT" if explicit else "PROVISIONAL_ID",
            "object_class": cls,
            "source_path": path,
            "source_locator": f"L{lineno}",
            "source_blob": sha,
            "statement": statement,
            "quantifier_class": quant,
            "proof_evidence_mode": mode,
            "evidence_level": "UNKNOWN",
            "maturity_level": "UNKNOWN",
            "claim_dependencies": claim_dependencies_for(statement),
            "strongest_parents": [],
            "assumptions": [],
            "falsifiers": [],
            "forbidden_extrapolations": [],
            "audit_disposition": "AMBER" if (quant == "UNKNOWN" or mode == "UNKNOWN" or not explicit) else "GREEN",
        })
    return out


def detect_cycles(nodes: Iterable[str], edges: Mapping[str, Sequence[str]]) -> list[list[str]]:
    nodes = sorted(set(nodes))
    visiting: set[str] = set(); done: set[str] = set(); stack: list[str] = []; cycles: list[list[str]] = []
    def dfs(node: str) -> None:
        if node in done: return
        if node in visiting:
            i = stack.index(node); cycles.append(stack[i:] + [node]); return
        visiting.add(node); stack.append(node)
        for dep in sorted(edges.get(node, ())):
            if dep in set(nodes): dfs(dep)
        stack.pop(); visiting.remove(node); done.add(node)
    for n in nodes: dfs(n)
    return cycles


def validate_complete_file_census(expected: Sequence[str], rows: Sequence[Mapping[str, object]]) -> None:
    actual = sorted(str(r["path"]) for r in rows)
    if sorted(expected) != actual:
        missing = sorted(set(expected) - set(actual)); extra = sorted(set(actual) - set(expected))
        raise CensusError(f"file census mismatch missing={missing} extra={extra}")


def audit(ref: str) -> dict[str, object]:
    all_research = tracked_research_paths(ref)
    included = [p for p in all_research if is_primary_candidate(p)]
    files: list[dict[str, object]] = []
    objects: list[dict[str, object]] = []
    gaps: list[dict[str, object]] = []

    for path in included:
        data = blob_bytes(ref, path); sha = blob_sha(ref, path)
        role, exclusion = file_role(path, data)
        row = {"path": path, "blob": sha, "role": role, "parse_exclusion": exclusion}
        files.append(row)
        if role in {"SCIENTIFIC_TEXT", "MACHINE_METADATA", "EXECUTABLE_WITNESS", "RECEIPT_OR_RESULT", "DATA_OR_FIXTURE"}:
            try: text = data.decode("utf-8")
            except UnicodeDecodeError:
                gaps.append(make_gap(gap_id=f"GAP-NONUTF8-{sha[:12]}", claim_id=path,
                    premise="scientific candidate file is parseable text", inference="object extraction",
                    assumption="UTF-8 scientific source", counterexample="non-UTF8 bytes", severity="HIGH",
                    evidence="typed decoder or explicit binary scientific schema")); continue
            objects.extend(scientific_objects(path, text, sha))

    validate_complete_file_census(included, files)

    # Duplicate object identities are never silently merged.
    by_id: dict[str, list[dict[str, object]]] = {}
    for obj in objects: by_id.setdefault(str(obj["object_id"]), []).append(obj)
    for oid, group in sorted(by_id.items()):
        if len(group) > 1:
            for obj in group: obj["audit_disposition"] = "RED"
            gaps.append(make_gap(gap_id=f"GAP-DUPID-{hashlib.sha256(oid.encode()).hexdigest()[:12]}", claim_id=oid,
                premise="scientific object IDs are unique", inference="dependency resolution",
                assumption="one semantic object per registered ID", counterexample=f"{len(group)} declarations share ID",
                severity="CRITICAL", evidence="explicit alias/equivalence adjudication or unique IDs"))

    ids = set(by_id)
    edges: dict[str, list[str]] = {}
    for obj in objects:
        oid = str(obj["object_id"]); deps = list(obj["claim_dependencies"]); edges[oid] = deps
        for dep in deps:
            if dep not in ids:
                obj["audit_disposition"] = "RED"
                gaps.append(make_gap(gap_id=f"GAP-DANGLING-{hashlib.sha256((oid+dep).encode()).hexdigest()[:12]}", claim_id=oid,
                    premise=f"internal claim dependency {dep} resolves", inference="claim dependency graph",
                    assumption="dependency exists exactly once", counterexample="missing dependency target",
                    severity="CRITICAL", evidence="registered dependency target or typed external-parent edge"))

        # Universal wording cannot be licensed by bounded-only evidence metadata.
        if obj["quantifier_class"] == "UNIVERSAL" and obj["proof_evidence_mode"] in {
            "COMPUTER_ASSISTED_EXHAUSTIVE", "FINITE_EXECUTABLE_CERTIFICATE"
        }:
            obj["audit_disposition"] = "RED"
            gaps.append(make_gap(gap_id=f"GAP-FIN2UNIV-{hashlib.sha256(oid.encode()).hexdigest()[:12]}", claim_id=oid,
                premise="bounded computation supports only its declared bounded universe",
                inference="universal theorem language", assumption="analytic/mechanized universal bridge exists",
                counterexample="outside-enumeration case", severity="CRITICAL",
                evidence="analytic/mechanized proof or narrowed finite quantifier"))

    cycles = detect_cycles(ids, edges)
    for i, cycle in enumerate(cycles, 1):
        gaps.append(make_gap(gap_id=f"GAP-CYCLE-{i:04d}", claim_id=cycle[0],
            premise="claim dependencies are acyclic", inference="theorem dependency ordering",
            assumption="no circular justification", counterexample=" -> ".join(cycle), severity="CRITICAL",
            evidence="break cycle with independently grounded premise/evidence"))
        for oid in cycle:
            for obj in by_id.get(oid, []): obj["audit_disposition"] = "RED"

    # Explicit unknown scientific objects are retained as gaps.
    for obj in objects:
        if obj["object_class"] == "UNKNOWN":
            obj["audit_disposition"] = "AMBER"
            gaps.append(make_gap(gap_id=f"GAP-UNKNOWN-{hashlib.sha256((str(obj['object_id'])).encode()).hexdigest()[:12]}",
                claim_id=str(obj["object_id"]), premise="candidate scientific marker has a typed object class",
                inference="corpus inventory", assumption="grammar covers declaration", counterexample=str(obj["statement"]),
                severity="MEDIUM", evidence="manual classification or grammar extension", materiality="REVIEW"))

    # Candidate semantic duplicates: same normalized statement at distinct locations.
    by_stmt: dict[str, list[dict[str, object]]] = {}
    for obj in objects: by_stmt.setdefault(str(obj["statement"]).lower(), []).append(obj)
    duplicate_candidates = []
    for statement, group in sorted(by_stmt.items()):
        if len({(g["source_path"], g["source_locator"]) for g in group}) > 1:
            duplicate_candidates.append({"statement_hash": hashlib.sha256(statement.encode()).hexdigest(),
                                         "object_ids": sorted(str(g["object_id"]) for g in group)})
            for g in group:
                if g["audit_disposition"] == "GREEN": g["audit_disposition"] = "AMBER"

    disposition_counts = {d: sum(1 for o in objects if o["audit_disposition"] == d) for d in sorted(DISPOSITIONS)}
    gap_counts = {s: sum(1 for g in gaps if g["severity"] == s and g["status"] == "OPEN") for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}

    return {
        "schema": "GMI_833_CORPUS_CENSUS_V1",
        "frozen_source_sha": ref,
        "claim_ceiling": "GMI_CORPUS_CENSUS_AND_DEPENDENCY_AUDIT_AT_FROZEN_MAIN_SCOPE",
        "discovery_rule": "research path component starts gmi-/gmi_ or equals machine-intelligence-morphogenesis-v1",
        "file_census": files,
        "scientific_objects": sorted(objects, key=lambda o: (str(o["source_path"]), str(o["source_locator"]), str(o["object_id"]))),
        "claim_dependency_edges": {k: sorted(v) for k, v in sorted(edges.items()) if v},
        "dependency_cycles": cycles,
        "candidate_semantic_duplicates": duplicate_candidates,
        "gaps": sorted(gaps, key=lambda g: str(g["id"])),
        "summary": {
            "tracked_research_files": len(all_research), "included_files": len(included),
            "scientific_objects": len(objects), "provisional_ids": sum(o["id_kind"] == "PROVISIONAL_ID" for o in objects),
            "dispositions": disposition_counts, "open_gaps_by_severity": gap_counts,
            "dependency_cycles": len(cycles), "duplicate_candidate_groups": len(duplicate_candidates),
        },
        "forbidden_promotions": [
            "ALL_GMI_THEOREMS_TRUE", "ONTOLOGICAL_COMPLETENESS", "ALL_PARENTS_EXHAUSTED",
            "ALL_OVERCLAIMS_REPAIRED", "KNOWN_FAMILY_DERIVATION_COMPLETE",
            "REAL_SCALE_VALIDATION_COMPLETE", "COMPLETE_GMI",
        ],
    }


def write_outputs(result: Mapping[str, object], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "CORPUS_INDEX_V1.json").write_bytes(canonical_json_bytes({
        "schema": result["schema"], "frozen_source_sha": result["frozen_source_sha"],
        "file_census": result["file_census"], "scientific_objects": result["scientific_objects"],
    }))
    (out_dir / "DEPENDENCY_GRAPH_V1.json").write_bytes(canonical_json_bytes({
        "schema": "GMI_833_DEPENDENCY_GRAPH_V1", "frozen_source_sha": result["frozen_source_sha"],
        "edges": result["claim_dependency_edges"], "cycles": result["dependency_cycles"],
    }))
    (out_dir / "GMI_GAP_GRAPH_V1.json").write_bytes(canonical_json_bytes({
        "schema": "GMI_GAP_GRAPH_V1", "frozen_source_sha": result["frozen_source_sha"], "gaps": result["gaps"],
    }))
    (out_dir / "AUDIT_V1.json").write_bytes(canonical_json_bytes({
        "schema": "GMI_833_CORPUS_AUDIT_V1", "frozen_source_sha": result["frozen_source_sha"],
        "claim_ceiling": result["claim_ceiling"], "summary": result["summary"],
        "candidate_semantic_duplicates": result["candidate_semantic_duplicates"],
        "forbidden_promotions": result["forbidden_promotions"],
    }))


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--ref", default=None); ap.add_argument("--out-dir", type=Path)
    args = ap.parse_args(); ref = args.ref or frozen_sha(); result = audit(ref)
    if args.out_dir: write_outputs(result, args.out_dir)
    print(canonical_json_bytes({"schema": result["schema"], "summary": result["summary"],
                                "frozen_source_sha": ref, "claim_ceiling": result["claim_ceiling"]}).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
