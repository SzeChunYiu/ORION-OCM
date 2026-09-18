#!/usr/bin/env python3
"""Exact reachable semantic-quotient fractions for a frozen finite law registry."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha1, sha256
from itertools import permutations
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
SOURCE_MAIN = "5aaebc5a7bab7825f30c007d9fd5cd4e34f5118e"
FREEZE_COMMIT = "d9ee6f49130749a2eede101cd26e6cfa839dd51e"
SOURCE_ISSUE = 1000
SOURCE_PR = 1001
CLAIM_CEILING = (
    "GMI_833_FINITE_REACHABLE_QUOTIENT_FRACTIONS_MEASURED_FOR_"
    "COMPLETE_DECLARED_LAW_REGISTRY_AT_REGISTERED_SCOPE"
)
REGISTERED_INTERFACE_WORDS = ((), (0,), (1,))
REGISTERED_STEP_CAP = 6
SEMANTIC_OPS = ("READ", "INC", "DECJZ", "EMIT", "HALT")
EXPECTED_LAW_IDS = (
    "REWRITE_11",
    "CODE_GROWTH_R1",
    "REGISTER_GROWTH_N1",
    "JOINT_GROWTH_22",
)
FORBIDDEN_PROMOTIONS = (
    "COMPLETE_REGISTRY_OF_ALL_DEVELOPMENTAL_OR_SEARCH_LAWS",
    "UNIVERSAL_REACHABILITY",
    "UNBIASED_LAW_ONTOLOGY",
    "ARBITRARY_BUDGETS",
    "UNBOUNDED_PROGRAM_EQUIVALENCE",
    "STOCHASTIC_OR_ADAPTIVE_DYNAMICS",
    "OPTIMIZER_CONVERGENCE",
    "ARCHITECTURE_PRIOR_FREE_RECOVERY",
    "CLUSTERING_OR_KNOWN_FAMILY_RECOVERY",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    (
        "finite_candidate_space",
        "research/gmi-833-finite-candidate-space-v1/RESULT_V1.json",
        "4086d6bea440d626e48d92eb35d39267a010589e",
        "claim_ceiling",
        "GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_REGISTERED_SCOPE",
    ),
    (
        "finite_morphology_metrics",
        "research/gmi-833-finite-morphology-metrics-v1/RESULT_V1.json",
        "b5bafc0ac9460de87723a27fe1a307ae7d06751b",
        "claim_ceiling",
        "GMI_833_FINITE_COLLAPSE_AND_SEMANTIC_RESOURCE_DEVELOPMENTAL_METRICS_AT_REGISTERED_SCOPE",
    ),
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


F = _load_module(
    "gmi833_f_reachability_parent",
    HERE.parent / "gmi-833-finite-candidate-space-v1" / "finite_candidate_space_v1.py",
)


@dataclass(frozen=True)
class DevelopmentLaw:
    law_id: str
    operators: tuple[str, ...]
    max_code_cells: int
    max_register_cells: int


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def repo_root(start: Path | None = None) -> Path:
    current = (start or HERE).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / ".git").is_file():
            return candidate
    raise RuntimeError("repository root not found")


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def audit_parents(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    rows: list[dict[str, object]] = []
    for name, relative, expected_blob, field, expected_value in PARENT_PINS:
        path = root / relative
        if not path.is_file():
            rows.append({
                "name": name,
                "path": relative,
                "expected_blob": expected_blob,
                "actual_blob": None,
                "blob_ok": False,
                "field": field,
                "expected_value": expected_value,
                "actual_value": None,
                "value_ok": False,
            })
            continue
        data = path.read_bytes()
        try:
            payload = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = {}
        actual_blob = git_blob_sha(data)
        actual_value = payload.get(field)
        rows.append({
            "name": name,
            "path": relative,
            "expected_blob": expected_blob,
            "actual_blob": actual_blob,
            "blob_ok": actual_blob == expected_blob,
            "field": field,
            "expected_value": expected_value,
            "actual_value": actual_value,
            "value_ok": actual_value == expected_value,
        })
    return {"all_ok": all(row["blob_ok"] and row["value_ok"] for row in rows), "rows": rows}


def load_registry(path: Path | None = None) -> tuple[DevelopmentLaw, ...]:
    payload = json.loads((path or HERE / "LAW_REGISTRY_V1.json").read_text(encoding="utf-8"))
    if payload.get("schema") != "GMI_833_FINITE_REACHABILITY_LAW_REGISTRY_V1":
        raise ValueError("law registry schema mismatch")
    rows = payload.get("laws")
    if type(rows) is not list or not rows:
        raise ValueError("law registry must be a nonempty list")
    laws: list[DevelopmentLaw] = []
    for row in rows:
        if type(row) is not dict:
            raise ValueError("each law must be an object")
        law_id = row.get("id")
        operators = row.get("operators")
        nmax = row.get("max_code_cells")
        rmax = row.get("max_register_cells")
        if type(law_id) is not str or not law_id:
            raise ValueError("law id must be a nonempty string")
        if type(operators) is not list or not operators or any(type(x) is not str for x in operators):
            raise ValueError("operators must be a nonempty string list")
        if len(set(operators)) != len(operators):
            raise ValueError("operators must be duplicate-free")
        if not set(operators) <= {"REWRITE", "GROW_CODE", "GROW_REGISTER"}:
            raise ValueError("unknown successor operator")
        if type(nmax) is not int or type(rmax) is not int or not (1 <= nmax <= 2 and 1 <= rmax <= 2):
            raise ValueError("law carrier ceiling is outside the registered universe")
        laws.append(DevelopmentLaw(law_id, tuple(operators), nmax, rmax))
    ids = tuple(law.law_id for law in laws)
    if len(set(ids)) != len(ids):
        raise ValueError("law ids must be duplicate-free")
    if path is None and ids != EXPECTED_LAW_IDS:
        raise ValueError("frozen law registry membership or order drift")
    return tuple(laws)


def start_program():
    return F.CandidateProgram(1, (F.Instruction("HALT"),))


def _inside_law(program, law: DevelopmentLaw) -> bool:
    return len(program.instructions) <= law.max_code_cells and program.register_count <= law.max_register_cells


def presentation_successors(program, law: DevelopmentLaw) -> tuple[object, ...]:
    F.validate_program(program)
    if not isinstance(law, DevelopmentLaw):
        raise ValueError("law must be a DevelopmentLaw")
    if not _inside_law(program, law):
        raise ValueError("source presentation lies outside the law ceiling")
    successors: set[object] = set()
    if "REWRITE" in law.operators:
        options = F.instruction_options(len(program.instructions), program.register_count)
        for index in range(len(program.instructions)):
            for instruction in options:
                if instruction == program.instructions[index]:
                    continue
                table = list(program.instructions)
                table[index] = instruction
                successors.add(F.CandidateProgram(program.register_count, tuple(table)))
    if "GROW_CODE" in law.operators and len(program.instructions) < law.max_code_cells:
        successors.add(F.CandidateProgram(program.register_count, program.instructions + (F.Instruction("HALT"),)))
    if "GROW_REGISTER" in law.operators and program.register_count < law.max_register_cells:
        successors.add(F.CandidateProgram(program.register_count + 1, program.instructions))
    for successor in successors:
        F.validate_program(successor)
        if not _inside_law(successor, law):
            raise AssertionError("successor escaped its registered law ceiling")
    return tuple(sorted(successors, key=lambda item: item.canonical_code()))


def bfs_reachable(law: DevelopmentLaw) -> tuple[object, ...]:
    start = start_program()
    if not _inside_law(start, law):
        raise ValueError("registered start lies outside law ceiling")
    seen = {start}
    queue = deque((start,))
    while queue:
        current = queue.popleft()
        for successor in presentation_successors(current, law):
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
    return tuple(sorted(seen, key=lambda item: item.canonical_code()))


def analytic_reachable(law: DevelopmentLaw) -> tuple[object, ...]:
    """Direct theorem characterization, intentionally not using successor traversal."""
    if "REWRITE" not in law.operators:
        raise ValueError("registered completeness theorem requires REWRITE")
    if law.max_code_cells > 1 and "GROW_CODE" not in law.operators:
        raise ValueError("code ceiling above one requires GROW_CODE")
    if law.max_register_cells > 1 and "GROW_REGISTER" not in law.operators:
        raise ValueError("register ceiling above one requires GROW_REGISTER")
    candidates = F.enumerate_candidates(F.StructuralBudget(law.max_code_cells, law.max_register_cells))
    return tuple(candidates)


def registered_interface():
    return F.ObservationInterface(REGISTERED_INTERFACE_WORDS, REGISTERED_STEP_CAP)


def _fraction_text(numerator: int, denominator: int) -> str:
    value = Fraction(numerator, denominator)
    return f"{value.numerator}/{value.denominator}"


def _load_oracle():
    return _load_module("gmi833_f_reachability_oracle", HERE / "independent_reachability_oracle_v1.py")


def reachability_census() -> dict[str, object]:
    laws = load_registry()
    interface = registered_interface()
    universe = F.enumerate_candidates(F.StructuralBudget(2, 2))
    universe_codes = {program.canonical_code() for program in universe}
    universe_keys = {F.semantic_key(program, interface) for program in universe}
    if len(universe) != 576 or len(universe_keys) != 21:
        raise ValueError("pinned #966/#984 universe or quotient drift")
    oracle = _load_oracle()
    oracle_rows = {row["law_id"]: row for row in oracle.oracle_census() ["laws"]}
    law_rows: list[dict[str, object]] = []
    bfs_edge_checks = 0
    for law in laws:
        reached = bfs_reachable(law)
        analytic = analytic_reachable(law)
        reached_codes = {program.canonical_code() for program in reached}
        analytic_codes = {program.canonical_code() for program in analytic}
        if not reached_codes <= universe_codes:
            raise ValueError("BFS escaped the frozen candidate universe")
        if reached_codes != analytic_codes:
            raise ValueError(f"BFS and analytic characterization disagree for {law.law_id}")
        quotient_keys = {F.semantic_key(program, interface) for program in reached}
        oracle_row = oracle_rows.get(law.law_id)
        if oracle_row is None:
            raise ValueError("independent oracle omitted a registered law")
        if (
            oracle_row["reachable_presentation_count"] != len(reached)
            or oracle_row["reachable_quotient_class_count"] != len(quotient_keys)
            or oracle_row["reachable_semantic_keys_sha256"]
            != sha256(canonical_json(sorted(_jsonable_key(key) for key in quotient_keys)).encode("utf-8")).hexdigest()
        ):
            raise ValueError(f"primary/oracle disagreement for {law.law_id}")
        bfs_edge_checks += sum(len(presentation_successors(program, law)) for program in reached)
        law_rows.append({
            "law_id": law.law_id,
            "operators": list(law.operators),
            "carrier_ceiling": [law.max_code_cells, law.max_register_cells],
            "reachable_presentation_count": len(reached),
            "presentation_denominator": len(universe),
            "reachable_presentation_fraction": _fraction_text(len(reached), len(universe)),
            "reachable_quotient_class_count": len(quotient_keys),
            "quotient_denominator": len(universe_keys),
            "reachable_quotient_fraction": _fraction_text(len(quotient_keys), len(universe_keys)),
            "bfs_equals_analytic_characterization": True,
            "independent_oracle_exact_match": True,
        })
    return {
        "presentation_denominator": len(universe),
        "quotient_denominator": len(universe_keys),
        "registered_law_count": len(laws),
        "bfs_successor_edge_checks": bfs_edge_checks,
        "laws": law_rows,
    }


def _jsonable_key(key: tuple[tuple[str, tuple[int, ...]], ...]) -> list[list[object]]:
    return [[status, list(output)] for status, output in key]


def remint_census() -> dict[str, object]:
    laws = load_registry()
    universe = F.enumerate_candidates(F.StructuralBudget(2, 2))
    baseline = {law.law_id: {program.canonical_code() for program in bfs_reachable(law)} for law in laws}
    token_bank = ("u0", "u1", "u2", "u3", "u4")
    checks = 0
    for tokens in permutations(token_bank):
        remint = dict(zip(SEMANTIC_OPS, tokens))
        for program in universe:
            decoded = F.decode_reminted(F.remint_program(program, remint), remint)
            if decoded != program:
                raise ValueError("certified operation-token remint changed a typed presentation")
            code = decoded.canonical_code()
            for law in laws:
                if (code in baseline[law.law_id]) != (program.canonical_code() in baseline[law.law_id]):
                    raise ValueError("reachability membership changed under certified surface remint")
            checks += len(laws)
    original = F.CandidateProgram(1, (F.Instruction("INC", 0, 0),))
    honest = dict(zip(SEMANTIC_OPS, token_bank))
    dishonest = dict(honest)
    dishonest["INC"], dishonest["READ"] = dishonest["READ"], dishonest["INC"]
    changed = F.decode_reminted(F.remint_program(original, honest), dishonest)
    hostile_detected = F.semantic_key(original, registered_interface()) != F.semantic_key(changed, registered_interface())
    if not hostile_detected:
        raise ValueError("semantics-changing pseudo-remint escaped detection")
    return {
        "certified_surface_remint_count": 120,
        "presentation_law_membership_checks": checks,
        "semantics_changing_hostile_detected": hostile_detected,
    }


def hostile_census() -> dict[str, object]:
    registry = json.loads((HERE / "LAW_REGISTRY_V1.json").read_text(encoding="utf-8"))
    detected: dict[str, bool] = {}
    variants: dict[str, object] = {}
    duplicate = json.loads(json.dumps(registry)); duplicate["laws"].append(duplicate["laws"][0])
    variants["duplicate_law"] = duplicate
    unknown = json.loads(json.dumps(registry)); unknown["laws"][0]["operators"] = ["TELEPORT"]
    variants["unknown_operator"] = unknown
    missing_rewrite = DevelopmentLaw("HOSTILE", ("GROW_CODE",), 2, 1)
    missing_growth = DevelopmentLaw("HOSTILE", ("REWRITE",), 2, 1)
    for name, payload in variants.items():
        with tempfile.TemporaryDirectory() as td:
            temporary = Path(td) / f"{name}.json"
            temporary.write_text(canonical_json(payload), encoding="utf-8")
            try:
                load_registry(temporary)
            except ValueError:
                detected[name] = True
            else:
                detected[name] = False
    for name, law in (("missing_rewrite", missing_rewrite), ("missing_growth", missing_growth)):
        try:
            analytic_reachable(law)
        except ValueError:
            detected[name] = True
        else:
            detected[name] = False
    out_of_scope = F.CandidateProgram(2, (F.Instruction("HALT"),))
    try:
        presentation_successors(out_of_scope, load_registry()[0])
    except ValueError:
        detected["out_of_scope_source"] = True
    else:
        detected["out_of_scope_source"] = False
    census = reachability_census()
    detected["presentation_vs_quotient_distinguished"] = any(
        row["reachable_presentation_fraction"] != row["reachable_quotient_fraction"]
        for row in census["laws"]
    )
    if not all(detected.values()):
        raise ValueError("one or more hostile controls escaped")
    return detected


def validate_scientific_ledger() -> dict[str, object]:
    payload = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text(encoding="utf-8"))
    claims = payload.get("claims")
    gaps = payload.get("open_gaps")
    if type(claims) is not list or {row.get("id") for row in claims} != {"REACH-1", "ORACLE-1", "REMINT-1"}:
        raise ValueError("scientific claim ledger drift")
    required = {"statement", "scope", "assumptions", "dependencies", "falsifiers", "strongest_parent", "counterexample_methods", "limits"}
    if any(not required <= set(row) for row in claims):
        raise ValueError("scientific ledger claim fields incomplete")
    if type(gaps) is not list or len(gaps) < 5 or any(row.get("status") != "OPEN" for row in gaps):
        raise ValueError("larger-scope gaps must remain explicitly open")
    return {"claim_ledgers": len(claims), "open_gaps": len(gaps), "closure_level": "REGISTERED_FINITE_SCOPE_ONLY"}


def validate_package_contracts() -> dict[str, object]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_FINITE_REACHABILITY_V1.json").read_text(encoding="utf-8"))
    manifest_ok = (
        manifest.get("issue") == SOURCE_ISSUE
        and manifest.get("source_pr") == SOURCE_PR
        and manifest.get("freeze_commit") == FREEZE_COMMIT
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and manifest.get("law_ids") == list(EXPECTED_LAW_IDS)
        and manifest.get("target_rows") == 1
    )
    replacements = reconciliation.get("replacements")
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("source_issue") == SOURCE_ISSUE
        and reconciliation.get("source_pr") == SOURCE_PR
        and type(replacements) is list
        and len(replacements) == 1
        and replacements[0].get("old") == "- [ ] Measure reachable fraction under each developmental/search law."
    )
    if not manifest_ok or not reconciliation_ok:
        raise ValueError("manifest or reconciliation contract drift")
    return {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 1, "source_pr": SOURCE_PR}


def build_receipt(parent_audit: Mapping[str, object] | None = None) -> dict[str, object]:
    parent_audit = dict(parent_audit or audit_parents())
    try:
        census = reachability_census()
        remints = remint_census()
        hostiles = hostile_census()
        ledger = validate_scientific_ledger()
        package = validate_package_contracts()
        checks = {
            "parents_exactly_pinned": bool(parent_audit.get("all_ok")),
            "frozen_registry_has_exactly_four_laws": census["registered_law_count"] == 4,
            "pinned_universe_has_576_presentations": census["presentation_denominator"] == 576,
            "pinned_quotient_has_21_classes": census["quotient_denominator"] == 21,
            "bfs_matches_analytic_for_every_law": all(row["bfs_equals_analytic_characterization"] for row in census["laws"]),
            "independent_oracle_matches_every_law": all(row["independent_oracle_exact_match"] for row in census["laws"]),
            "all_surface_remints_preserve_membership": remints["presentation_law_membership_checks"] == 276_480,
            "semantics_changing_remint_is_detected": remints["semantics_changing_hostile_detected"] is True,
            "all_registered_hostiles_detected": all(hostiles.values()),
            "scientific_ledger_complete": ledger["claim_ledgers"] == 3,
            "larger_scope_gaps_remain_open": ledger["open_gaps"] >= 5,
            "package_contract_exact": package["manifest_ok"] and package["reconciliation_ok"],
        }
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        return {
            "schema": "GMI833FiniteReachabilityFractionsResultV1",
            "issue": SOURCE_ISSUE,
            "parent_issue": 833,
            "source_pr": SOURCE_PR,
            "claim_ceiling": CLAIM_CEILING,
            "verdict": "RED",
            "error": str(exc),
            "parent_audit": parent_audit,
            "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        }
    return {
        "schema": "GMI833FiniteReachabilityFractionsResultV1",
        "issue": SOURCE_ISSUE,
        "parent_issue": 833,
        "source_pr": SOURCE_PR,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "checks": checks,
        "census": census,
        "remints": remints,
        "hostiles": hostiles,
        "ledger": ledger,
        "package": package,
        "parent_audit": parent_audit,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


def main(argv: Sequence[str] | None = None) -> int:
    del argv
    receipt = build_receipt()
    print(canonical_json(receipt), end="")
    return 0 if receipt.get("verdict") == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
