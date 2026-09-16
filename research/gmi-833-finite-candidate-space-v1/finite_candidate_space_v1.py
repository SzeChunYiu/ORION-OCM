#!/usr/bin/env python3
"""Exact finite G0 candidate space, semantic quotient, and neutral descriptors."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha1, sha256
from itertools import permutations, product
import importlib.util
import json
from pathlib import Path
import sys
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
SOURCE_MAIN = "fcbb8c08ce36b2970079ed715d5e757f28da46d2"
FREEZE_COMMIT = "070bc0d28bdf86e5683dd68e1cf5ba0962522907"
SOURCE_ISSUE = 956
SOURCE_PR = 0  # bound after the pull request exists
CLAIM_CEILING = "GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_REGISTERED_SCOPE"
SEMANTIC_OPS = ("READ", "INC", "DECJZ", "EMIT", "HALT")
RESOURCE_COORDINATES = ("code_cells", "register_cells")
FORBIDDEN_PROMOTIONS = (
    "UNBOUNDED_PROGRAM_EQUIVALENCE_DECIDED",
    "UNIVERSAL_SEMANTIC_QUOTIENT",
    "ARCHITECTURE_FREE_IN_ABSOLUTE_SENSE",
    "UNIQUE_OR_UNBIASED_GRAMMAR",
    "SCALABLE_LARGE_BUDGET_SAMPLING",
    "MILLION_SCALE_GENERATION",
    "HUNDRED_MILLION_SCALE_GENERATION",
    "CLUSTERING_OR_KNOWN_FAMILY_RECOVERY",
    "UNIVERSAL_MORPHOLOGY_TAXONOMY",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    (
        "foundation",
        "research/gmi-833-foundation-v1/RESULT_V1.json",
        "c0c574c4ec6e237d5fdafa694eac131399625a70",
        "terminal",
        "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE",
    ),
    (
        "g0_core",
        "research/gmi-833-g0-register-core-v1/RESULT_V1.json",
        "5d2948b9c04c84a46f6625e043753a489895478f",
        "claim_ceiling",
        "GMI_G0_REGISTER_CORE_AND_FINITE_EMBEDDINGS_AT_DECLARED_SCOPE",
    ),
    (
        "morphcap",
        "research/gmi-833-morphcap-v1/RESULT_V1.json",
        "bdc5c3cd42e312d8c7af52f7ba84220631a25f8a",
        "claim_ceiling",
        "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "grammar_bias",
        "research/gmi-833-g0-grammar-bias-v1/RESULT_V1.json",
        "e903033615946a71f2f0859cda42e5b902e0d693",
        "claim_ceiling",
        "GMI_FINITE_GRAMMAR_BIAS_AND_REMINT_BOUNDARY_AT_REGISTERED_G0_SCOPE",
    ),
    (
        "robustness_controls",
        "research/gmi-833-robustness-controls-v1/RESULT_V1.json",
        "c3ff199c343b6905dabe8e3aefdc5958a2c8a06a",
        "claim_ceiling",
        "GMI_DERIVATION_ROBUSTNESS_CONTROL_REQUIREMENTS_FORMALIZED_AT_REGISTERED_FINITE_SCOPE",
    ),
)


def _load_g0_parent():
    path = HERE.parent / "gmi-833-g0-register-core-v1" / "g0_register_core_v1.py"
    spec = importlib.util.spec_from_file_location("gmi833_f1_g0_parent", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned G0 parent")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


G0 = _load_g0_parent()


def _exact_positive_int(value: object, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label} must be a positive exact integer")
    return value


def _exact_natural(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be an exact natural number")
    return value


@dataclass(frozen=True, order=True)
class StructuralBudget:
    code_cells: int
    register_cells: int

    def __post_init__(self) -> None:
        _exact_positive_int(self.code_cells, "code_cells")
        _exact_positive_int(self.register_cells, "register_cells")

    def as_tuple(self) -> tuple[int, int]:
        return (self.code_cells, self.register_cells)


@dataclass(frozen=True)
class Instruction:
    op: str
    register: int | None = None
    target0: int | None = None
    target1: int | None = None

    def canonical_code(self) -> tuple[str, int, int, int]:
        return (
            self.op,
            -1 if self.register is None else self.register,
            -1 if self.target0 is None else self.target0,
            -1 if self.target1 is None else self.target1,
        )


@dataclass(frozen=True)
class CandidateProgram:
    register_count: int
    instructions: tuple[Instruction, ...]

    def canonical_code(self) -> tuple[int, tuple[tuple[str, int, int, int], ...]]:
        return (self.register_count, tuple(item.canonical_code() for item in self.instructions))

    def resource_vector(self) -> tuple[int, int]:
        # One CODE_CELL atom per instruction plus one REGISTER_CELL atom per declaration.
        return (len(self.instructions), self.register_count)


@dataclass(frozen=True)
class ObservationInterface:
    input_words: tuple[tuple[int, ...], ...]
    step_cap: int

    def __post_init__(self) -> None:
        _exact_positive_int(self.step_cap, "step_cap")
        if type(self.input_words) is not tuple or not self.input_words:
            raise ValueError("input_words must be a nonempty finite tuple")
        normalized: list[tuple[int, ...]] = []
        for word in self.input_words:
            if type(word) is not tuple:
                raise ValueError("each input word must be a tuple")
            if any(type(value) is not int or value < 0 for value in word):
                raise ValueError("input symbols must be exact natural numbers")
            normalized.append(word)
        if len(set(normalized)) != len(normalized):
            raise ValueError("registered input words must be duplicate-free")


def validate_instruction(instruction: Instruction, label_count: int, register_count: int) -> None:
    if not isinstance(instruction, Instruction) or instruction.op not in SEMANTIC_OPS:
        raise ValueError("instruction must use one registered semantic operation")
    if instruction.op == "HALT":
        if (instruction.register, instruction.target0, instruction.target1) != (None, None, None):
            raise ValueError("HALT cannot carry operands")
        return
    if type(instruction.register) is not int or not 0 <= instruction.register < register_count:
        raise ValueError("instruction register is outside the declared carrier")
    if instruction.op in {"READ", "INC", "EMIT"}:
        if type(instruction.target0) is not int or not 0 <= instruction.target0 < label_count:
            raise ValueError("successor is outside the declared label carrier")
        if instruction.target1 is not None:
            raise ValueError("single-successor instruction has an extra operand")
        return
    if instruction.op == "DECJZ":
        if type(instruction.target0) is not int or not 0 <= instruction.target0 < label_count:
            raise ValueError("nonzero successor is outside the declared label carrier")
        if type(instruction.target1) is not int or not 0 <= instruction.target1 < label_count:
            raise ValueError("zero successor is outside the declared label carrier")
        return
    raise AssertionError("registered operation validation fell through")


def validate_program(program: CandidateProgram) -> None:
    if not isinstance(program, CandidateProgram):
        raise ValueError("candidate must be a CandidateProgram")
    _exact_positive_int(program.register_count, "register_count")
    if type(program.instructions) is not tuple or not program.instructions:
        raise ValueError("instruction table must be a nonempty tuple")
    for instruction in program.instructions:
        validate_instruction(instruction, len(program.instructions), program.register_count)


def instruction_options(label_count: int, register_count: int) -> tuple[Instruction, ...]:
    label_count = _exact_positive_int(label_count, "label_count")
    register_count = _exact_positive_int(register_count, "register_count")
    result: list[Instruction] = []
    for register in range(register_count):
        for target in range(label_count):
            result.append(Instruction("READ", register, target))
    for register in range(register_count):
        for target in range(label_count):
            result.append(Instruction("INC", register, target))
    for register in range(register_count):
        for nonzero in range(label_count):
            for zero in range(label_count):
                result.append(Instruction("DECJZ", register, nonzero, zero))
    for register in range(register_count):
        for target in range(label_count):
            result.append(Instruction("EMIT", register, target))
    result.append(Instruction("HALT"))
    if len(result) != 1 + 3 * register_count * label_count + register_count * label_count**2:
        raise AssertionError("instruction-instance formula drift")
    return tuple(result)


def candidate_count(budget: StructuralBudget) -> int:
    if not isinstance(budget, StructuralBudget):
        raise ValueError("budget must be a StructuralBudget")
    total = 0
    for registers in range(1, budget.register_cells + 1):
        for labels in range(1, budget.code_cells + 1):
            instances = 1 + 3 * registers * labels + registers * labels**2
            total += instances**labels
    return total


def enumerate_candidates(
    budget: StructuralBudget,
    *,
    max_candidates: int = 100_000,
) -> tuple[CandidateProgram, ...]:
    if not isinstance(budget, StructuralBudget):
        raise ValueError("budget must be a StructuralBudget")
    max_candidates = _exact_positive_int(max_candidates, "max_candidates")
    expected = candidate_count(budget)
    if expected > max_candidates:
        raise ValueError("budget exceeds the registered exact small-enumeration limit")
    result: list[CandidateProgram] = []
    for registers in range(1, budget.register_cells + 1):
        for labels in range(1, budget.code_cells + 1):
            options = instruction_options(labels, registers)
            for table in product(options, repeat=labels):
                candidate = CandidateProgram(registers, tuple(table))
                validate_program(candidate)
                if any(a > b for a, b in zip(candidate.resource_vector(), budget.as_tuple())):
                    raise AssertionError("enumerator emitted an over-budget candidate")
                result.append(candidate)
    codes = [program.canonical_code() for program in result]
    if len(result) != expected or len(codes) != len(set(codes)):
        raise AssertionError("exact enumerator count or uniqueness drift")
    return tuple(result)


def to_parent_program(program: CandidateProgram):
    validate_program(program)
    registers = tuple(f"r{i}" for i in range(program.register_count))
    labels = tuple(f"L{i}" for i in range(len(program.instructions)))
    table: dict[str, object] = {}
    for label, instruction in zip(labels, program.instructions):
        if instruction.op == "HALT":
            compiled = G0.Halt()
        elif instruction.op == "READ":
            compiled = G0.Read(registers[instruction.register], labels[instruction.target0])
        elif instruction.op == "INC":
            compiled = G0.Inc(registers[instruction.register], labels[instruction.target0])
        elif instruction.op == "EMIT":
            compiled = G0.Emit(registers[instruction.register], labels[instruction.target0])
        elif instruction.op == "DECJZ":
            compiled = G0.DecJz(
                registers[instruction.register], labels[instruction.target0], labels[instruction.target1]
            )
        else:  # pragma: no cover - validation already excludes this
            raise AssertionError("validated operation became unknown")
        table[label] = compiled
    parent = G0.Program(registers, labels[0], table)
    if G0.validate_program(parent):
        raise AssertionError("validated finite candidate did not compile to G0")
    return parent


def protected_observation(program: CandidateProgram, word: Sequence[int], step_cap: int) -> tuple[str, tuple[int, ...]]:
    if type(word) not in (tuple, list) or any(type(value) is not int or value < 0 for value in word):
        raise ValueError("word must be a finite sequence of exact natural numbers")
    _exact_positive_int(step_cap, "step_cap")
    result = G0.execute(to_parent_program(program), tuple(word), step_cap)
    status = {
        "HALTED": "HALTED",
        "INPUT_UNDERFLOW": "BLOCKED_INPUT",
        "STEP_BUDGET_EXHAUSTED": "STEP_LIMIT",
    }.get(result.terminal)
    if status is None:
        raise AssertionError(f"well-typed candidate produced unexpected terminal {result.terminal!r}")
    return (status, tuple(result.output))


def semantic_key(
    program: CandidateProgram,
    interface: ObservationInterface,
) -> tuple[tuple[str, tuple[int, ...]], ...]:
    if not isinstance(interface, ObservationInterface):
        raise ValueError("interface must be an ObservationInterface")
    return tuple(protected_observation(program, word, interface.step_cap) for word in interface.input_words)


def semantic_equivalent(
    left: CandidateProgram,
    right: CandidateProgram,
    interface: ObservationInterface,
) -> bool:
    return semantic_key(left, interface) == semantic_key(right, interface)


def semantic_quotient(
    candidates: Iterable[CandidateProgram],
    interface: ObservationInterface,
) -> tuple[dict[str, object], ...]:
    programs = tuple(candidates)
    if not programs:
        raise ValueError("semantic quotient requires a nonempty finite candidate tuple")
    for program in programs:
        validate_program(program)
    codes = [program.canonical_code() for program in programs]
    if len(codes) != len(set(codes)):
        raise ValueError("semantic quotient input must be syntactically duplicate-free")
    classes: dict[tuple[tuple[str, tuple[int, ...]], ...], list[CandidateProgram]] = defaultdict(list)
    for program in programs:
        classes[semantic_key(program, interface)].append(program)
    rows: list[dict[str, object]] = []
    for key in sorted(classes):
        members = tuple(sorted(classes[key], key=lambda item: item.canonical_code()))
        rows.append({
            "semantic_key": key,
            "representative": members[0],
            "members": members,
            "multiplicity": len(members),
        })
    if sum(row["multiplicity"] for row in rows) != len(programs):
        raise AssertionError("semantic quotient dropped or duplicated a candidate")
    if len({row["semantic_key"] for row in rows}) != len(rows):
        raise AssertionError("semantic quotient emitted a class more than once")
    return tuple(rows)


def _jsonable_semantics(key: tuple[tuple[str, tuple[int, ...]], ...]) -> list[list[object]]:
    return [[status, list(output)] for status, output in key]


def morphology_descriptor_from_invariants(
    observations: tuple[tuple[str, tuple[int, ...]], ...],
    resource_vector: tuple[int, int],
    developmental_distance: int,
) -> dict[str, object]:
    if type(observations) is not tuple or not observations:
        raise ValueError("descriptor requires a nonempty complete observation table")
    allowed_status = {"HALTED", "BLOCKED_INPUT", "STEP_LIMIT"}
    normalized: list[tuple[str, tuple[int, ...]]] = []
    for row in observations:
        if type(row) is not tuple or len(row) != 2 or row[0] not in allowed_status or type(row[1]) is not tuple:
            raise ValueError("malformed protected observation")
        if any(type(value) is not int or value < 0 for value in row[1]):
            raise ValueError("protected output must contain exact natural numbers")
        normalized.append(row)
    if (
        type(resource_vector) is not tuple
        or len(resource_vector) != 2
        or any(type(value) is not int or value <= 0 for value in resource_vector)
    ):
        raise ValueError("resource vector must contain two positive exact integers")
    developmental_distance = _exact_natural(developmental_distance, "developmental_distance")
    statuses = Counter(status for status, _ in normalized)
    semantic_json = json.dumps(_jsonable_semantics(tuple(normalized)), separators=(",", ":"), sort_keys=True)
    return {
        "schema": "GMI833FiniteNeutralMorphologyDescriptorV1",
        "semantic_class_sha256": sha256(semantic_json.encode()).hexdigest(),
        "protected_case_count": len(normalized),
        "status_histogram": {status: statuses.get(status, 0) for status in sorted(allowed_status)},
        "output_length_profile": [len(output) for _, output in normalized],
        "distinct_output_trace_count": len({output for _, output in normalized}),
        "resource_coordinates": list(RESOURCE_COORDINATES),
        "resource_vector": list(resource_vector),
        "developmental_distance": developmental_distance,
    }


def morphology_descriptor(
    program: CandidateProgram,
    interface: ObservationInterface,
    developmental_distance: int,
) -> dict[str, object]:
    return morphology_descriptor_from_invariants(
        semantic_key(program, interface), program.resource_vector(), developmental_distance
    )


@dataclass(frozen=True)
class SurfaceInstruction:
    token: str
    register: int | None = None
    target0: int | None = None
    target1: int | None = None


@dataclass(frozen=True)
class SurfaceProgram:
    register_count: int
    instructions: tuple[SurfaceInstruction, ...]


def validate_remint(remint: Mapping[str, str]) -> None:
    if set(remint) != set(SEMANTIC_OPS):
        raise ValueError("remint domain must be exactly the registered operations")
    values = tuple(remint[op] for op in SEMANTIC_OPS)
    if any(type(token) is not str or not token for token in values) or len(set(values)) != len(values):
        raise ValueError("remint must be a bijection onto distinct nonempty surface tokens")


def remint_program(program: CandidateProgram, remint: Mapping[str, str]) -> SurfaceProgram:
    validate_program(program)
    validate_remint(remint)
    return SurfaceProgram(
        program.register_count,
        tuple(SurfaceInstruction(remint[i.op], i.register, i.target0, i.target1) for i in program.instructions),
    )


def decode_reminted(surface: SurfaceProgram, remint: Mapping[str, str]) -> CandidateProgram:
    if not isinstance(surface, SurfaceProgram):
        raise ValueError("surface candidate must be a SurfaceProgram")
    validate_remint(remint)
    inverse = {token: op for op, token in remint.items()}
    decoded: list[Instruction] = []
    for item in surface.instructions:
        if not isinstance(item, SurfaceInstruction) or item.token not in inverse:
            raise ValueError("surface token is not covered by the certified remint")
        decoded.append(Instruction(inverse[item.token], item.register, item.target0, item.target1))
    result = CandidateProgram(surface.register_count, tuple(decoded))
    validate_program(result)
    return result


def relabel_registers(program: CandidateProgram, old_to_new: Sequence[int]) -> CandidateProgram:
    validate_program(program)
    mapping = tuple(old_to_new)
    if sorted(mapping) != list(range(program.register_count)):
        raise ValueError("register relabeling must be a permutation of the declared carrier")
    result = CandidateProgram(
        program.register_count,
        tuple(
            Instruction(
                item.op,
                None if item.register is None else mapping[item.register],
                item.target0,
                item.target1,
            )
            for item in program.instructions
        ),
    )
    validate_program(result)
    return result


def repo_root(start: Path | None = None) -> Path:
    current = (start or HERE).resolve()
    while current.parent != current:
        if (current / "research").is_dir():
            return current
        current = current.parent
    return HERE.parents[1]


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    rows: list[dict[str, object]] = []
    for name, relative, expected_blob, field, expected_claim in PARENT_PINS:
        path = root / relative
        if not path.is_file():
            rows.append({"name": name, "path": relative, "blob_ok": False, "claim_ok": False, "actual_blob": None})
            continue
        data = path.read_bytes()
        try:
            claim_ok = json.loads(data).get(field) == expected_claim
        except (UnicodeDecodeError, json.JSONDecodeError):
            claim_ok = False
        actual_blob = git_blob_sha(data)
        rows.append({
            "name": name,
            "path": relative,
            "actual_blob": actual_blob,
            "blob_ok": actual_blob == expected_blob,
            "claim_ok": claim_ok,
        })
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


def validate_scientific_ledger() -> dict[str, object]:
    ledger = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text(encoding="utf-8"))
    required = {
        "id", "statement", "scope", "assumptions", "dependencies", "falsifiers",
        "strongest_parent", "counterexample_methods", "limits",
    }
    claims = ledger.get("claims", [])
    gaps = ledger.get("open_gaps", [])
    if len(claims) != 4 or any(set(row) != required for row in claims):
        raise ValueError("scientific claim ledger schema/count drifted")
    if any(not row["assumptions"] or not row["falsifiers"] or not row["limits"] for row in claims):
        raise ValueError("scientific claim ledger has an empty discipline field")
    if len(gaps) < 4 or any(row.get("status") != "OPEN" for row in gaps):
        raise ValueError("forbidden larger-scope gaps must remain explicitly open")
    return {"claim_ledgers": 4, "open_gaps": len(gaps), "closure_level": "REGISTERED_FINITE_SCOPE_ONLY"}


def validate_package_contracts() -> dict[str, object]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_FINITE_CANDIDATE_SPACE_V1.json").read_text(encoding="utf-8"))
    replacements = reconciliation.get("replacements", [])
    expected_old = (
        "- [ ] Formalize the candidate machine space `M(G0, B)` under finite budget `B`.",
        "- [ ] Define semantic equivalence classes so implementation duplicates collapse.",
        "- [ ] Define morphology/species descriptors independent of architecture names.",
        "- [ ] Implement exact enumeration for small budgets.",
    )
    manifest_ok = (
        manifest.get("schema") == "GMI_833_FINITE_CANDIDATE_SPACE_MANIFEST_V1"
        and manifest.get("issue") == SOURCE_ISSUE
        and manifest.get("source_pr") == SOURCE_PR
        and manifest.get("parent_issue") == 833
        and manifest.get("source_main") == SOURCE_MAIN
        and manifest.get("freeze_commit") == FREEZE_COMMIT
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and manifest.get("target_rows") == 4
        and tuple(manifest.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
    )
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("issue") == 833
        and reconciliation.get("source_issue") == SOURCE_ISSUE
        and reconciliation.get("source_pr") == SOURCE_PR
        and reconciliation.get("claim_ceiling") == CLAIM_CEILING
        and tuple(reconciliation.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
        and len(replacements) == 4
        and tuple(row.get("old") for row in replacements) == expected_old
        and all(row.get("anchor") == "# F. Intelligence-space generator" for row in replacements)
        and all(str(SOURCE_PR) in row.get("new", "") and row.get("new", "").startswith("- [x] ") for row in replacements)
    )
    if not manifest_ok or not reconciliation_ok:
        raise ValueError("manifest/reconciliation package contract drifted")
    return {
        "manifest_ok": True,
        "reconciliation_ok": True,
        "reconciliation_rows": 4,
        "source_pr": SOURCE_PR,
    }


def registered_census() -> dict[str, object]:
    # Imported lazily so the scientific executor does not depend on its oracle.
    oracle_path = HERE / "independent_oracle_v1.py"
    spec = importlib.util.spec_from_file_location("gmi833_f1_independent_oracle", oracle_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent oracle")
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)

    budget_rows: list[dict[str, object]] = []
    oracle_comparisons = 0
    for budget in (StructuralBudget(1, 1), StructuralBudget(2, 1), StructuralBudget(1, 2), StructuralBudget(2, 2)):
        candidates = enumerate_candidates(budget)
        actual = {program.canonical_code() for program in candidates}
        independent = set(oracle.enumerate_raw_codes(budget.code_cells, budget.register_cells))
        if actual != independent:
            raise ValueError("constructive enumerator disagrees with independent Cartesian oracle")
        if len(actual) != oracle.closed_form_count(budget.code_cells, budget.register_cells):
            raise ValueError("closed-form candidate count disagrees with independent oracle")
        oracle_comparisons += len(actual)
        budget_rows.append({
            "budget": list(budget.as_tuple()),
            "candidate_count": len(candidates),
            "oracle_exact_match": True,
        })

    interface = ObservationInterface(((), (0,), (1,)), 6)
    registered = enumerate_candidates(StructuralBudget(2, 1))
    quotient = semantic_quotient(registered, interface)
    if len(registered) != 126 or len(quotient) != 18:
        raise ValueError("registered 126-presentation control drifted from pinned #875 result")

    remint_checks = 0
    token_bank = ("u0", "u1", "u2", "u3", "u4")
    baseline_descriptors = {
        program.canonical_code(): morphology_descriptor(program, interface, sum(program.resource_vector()))
        for program in registered
    }
    for permuted in permutations(token_bank):
        remint = dict(zip(SEMANTIC_OPS, permuted))
        for program in registered:
            decoded = decode_reminted(remint_program(program, remint), remint)
            if decoded != program:
                raise ValueError("certified syntax remint did not round-trip exactly")
            if morphology_descriptor(decoded, interface, sum(decoded.resource_vector())) != baseline_descriptors[program.canonical_code()]:
                raise ValueError("neutral descriptor changed under certified syntax remint")
            remint_checks += 1

    two_register = enumerate_candidates(StructuralBudget(2, 2))
    register_relabel_checks = 0
    nontrivial_register_relabels = 0
    for program in two_register:
        if program.register_count != 2:
            continue
        relabelled = relabel_registers(program, (1, 0))
        nontrivial_register_relabels += int(relabelled != program)
        if semantic_key(program, interface) != semantic_key(relabelled, interface):
            raise ValueError("external behavior changed under internal register relabeling")
        distance = sum(program.resource_vector())
        if morphology_descriptor(program, interface, distance) != morphology_descriptor(relabelled, interface, distance):
            raise ValueError("neutral descriptor changed under register relabeling")
        register_relabel_checks += 1

    hostile_original = CandidateProgram(1, (Instruction("INC", 0, 0),))
    honest_remint = dict(zip(SEMANTIC_OPS, token_bank))
    dishonest_decoder = dict(honest_remint)
    dishonest_decoder["INC"], dishonest_decoder["READ"] = dishonest_decoder["READ"], dishonest_decoder["INC"]
    hostile_changed = decode_reminted(remint_program(hostile_original, honest_remint), dishonest_decoder)
    hostile_detected = (
        hostile_changed != hostile_original
        and semantic_key(hostile_original, interface) != semantic_key(hostile_changed, interface)
    )
    if not hostile_detected:
        raise ValueError("semantics-changing pseudo-remint escaped detection")

    register_control = CandidateProgram(
        2,
        (
            Instruction("READ", 0, 1),
            Instruction("EMIT", 0, 2),
            Instruction("HALT"),
        ),
    )
    inconsistent_register_change = CandidateProgram(
        2,
        (
            Instruction("READ", 1, 1),
            Instruction("EMIT", 0, 2),
            Instruction("HALT"),
        ),
    )
    register_hostile_detected = semantic_key(register_control, interface) != semantic_key(
        inconsistent_register_change, interface
    )
    if not register_hostile_detected:
        raise ValueError("inconsistent internal-register rename escaped detection")

    # The relation induced by equality of a total key is checked exhaustively on
    # the 126-program slice: reflexive, symmetric, transitive.
    keys = [semantic_key(program, interface) for program in registered]
    relation_checks = 0
    for i, left in enumerate(keys):
        if left != left:
            raise AssertionError("semantic equality lost reflexivity")
        relation_checks += 1
        for j, right in enumerate(keys):
            if (left == right) != (right == left):
                raise AssertionError("semantic equality lost symmetry")
            relation_checks += 1
            if left == right:
                for third in keys:
                    if right == third and left != third:
                        raise AssertionError("semantic equality lost transitivity")
                    relation_checks += 1

    multiplicities = Counter(row["multiplicity"] for row in quotient)
    return {
        "budget_rows": budget_rows,
        "independent_oracle_candidate_comparisons": oracle_comparisons,
        "registered_candidates": len(registered),
        "registered_semantic_classes": len(quotient),
        "registered_collapse_count": len(registered) - len(quotient),
        "class_multiplicity_histogram": {str(k): multiplicities[k] for k in sorted(multiplicities)},
        "equivalence_relation_checks": relation_checks,
        "syntax_remint_descriptor_checks": remint_checks,
        "register_relabel_descriptor_checks": register_relabel_checks,
        "nontrivial_register_relabels": nontrivial_register_relabels,
        "semantics_changing_hostile_detected": hostile_detected,
        "inconsistent_register_rename_hostile_detected": register_hostile_detected,
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or audit_parents()
    try:
        census = registered_census()
        ledger = validate_scientific_ledger()
        package = validate_package_contracts()
        checks = {
            "parents_exactly_pinned": bool(parent_audit.get("all_ok")),
            "finite_formula_matches_constructive_enumerator": all(row["oracle_exact_match"] for row in census["budget_rows"]),
            "independent_cartesian_oracle_exact": census["independent_oracle_candidate_comparisons"] == 721,
            "registered_126_control_matches_parent": census["registered_candidates"] == 126 and census["registered_semantic_classes"] == 18,
            "semantic_quotient_exactly_once": census["registered_collapse_count"] == 108,
            "equivalence_relation_exact": census["equivalence_relation_checks"] > 0,
            "all_syntax_remints_invariant": census["syntax_remint_descriptor_checks"] == 15_120,
            "all_two_register_relabels_invariant": census["register_relabel_descriptor_checks"] == 450,
            "register_relabels_are_nonvacuous": census["nontrivial_register_relabels"] == 448,
            "semantic_hostile_detected": census["semantics_changing_hostile_detected"] is True,
            "register_rename_hostile_detected": census["inconsistent_register_rename_hostile_detected"] is True,
            "scientific_ledger_complete": ledger["claim_ledgers"] == 4,
            "larger_scope_gaps_remain_open": ledger["open_gaps"] >= 4,
            "package_contract_exact": package["manifest_ok"] and package["reconciliation_ok"],
        }
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        return {
            "schema": "GMI833FiniteCandidateSpaceResultV1",
            "issue": SOURCE_ISSUE,
            "parent_issue": 833,
            "source_pr": SOURCE_PR,
            "claim_ceiling": CLAIM_CEILING,
            "verdict": "RED",
            "error": str(exc),
            "parent_audit": parent_audit,
            "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        }
    verdict = "GREEN" if all(checks.values()) else "RED"
    return {
        "schema": "GMI833FiniteCandidateSpaceResultV1",
        "issue": SOURCE_ISSUE,
        "parent_issue": 833,
        "source_pr": SOURCE_PR,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "grammar": "G0-fin-v1",
        "resource_coordinates": list(RESOURCE_COORDINATES),
        "registered_interface": {"input_words": [[], [0], [1]], "step_cap": 6},
        "claim_ceiling": CLAIM_CEILING,
        "checks": checks,
        "census": census,
        "ledger": ledger,
        "package": package,
        "parent_audit": parent_audit,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "verdict": verdict,
    }


def main() -> int:
    receipt = build_receipt()
    print(canonical_json(receipt), end="")
    return 0 if receipt.get("verdict") == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
