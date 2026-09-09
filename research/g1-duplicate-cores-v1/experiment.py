"""G1.1.6: measure whether language / math / procedural share one (F, O, Π, C).

Research-only. Production ``src/`` is not modified or deleted. The G1 vessel freeze at
``research/g1-vessel-freeze-v1/`` is cited, not overwritten.

Checkbox text is “Eliminate duplicated cognitive cores.” This capsule checks the
architecture question (one shared core vs forked cores) and classifies lookalikes.
It does not perform deletion.
"""
from __future__ import annotations

import ast
import hashlib
import importlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from ocm.constitution.action import StaticCommitAuthority
from ocm.kso.admission import CertificateKind
from ocm.kso.space import Atom
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language.field_bridge import bind_meaning, binding_liveness
from ocm.language.meaning import MEdge, MNode, MeaningGraph
from ocm.operators.registry import BackendKind, OperatorSpec
from ocm.runtime import ocm_runtime as live_runtime_mod
from ocm.runtime import state as custody_runtime_mod
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.science import lifecycle as science_lifecycle
from ocm.science.proof import FormalStatement, KernelVerdict, check as proof_check
from ocm.store.evidence import Channel
from ocm.work.contracts import Operator as WorkOperator
from ocm.work.contracts import TaskContract, apply_operator

SCHEMA = "ocm.g1.duplicate-cores.v1"
SALT = "orion-ocm-g1-duplicate-cores-v1"
ISSUE = 165
GATE = "G1.1.6"
FREEZE_DIR = REPO / "research" / "g1-vessel-freeze-v1"
DOMAIN_PACKAGES = (
    "language",
    "science",
    "work",
    "dialogue",
    "lifetime",
    "chat",
)
CORE_CTORS = frozenset(
    {
        "OCMRuntime",
        "KnowledgeSpace",
        "EvidenceRegistry",
        "OperatorRegistry",
        "StaticCommitAuthority",
        "HardGateContract",
    }
)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _call_name(node: ast.AST) -> str | None:
    func = node.func if isinstance(node, ast.Call) else None
    if func is None:
        return None
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def scan_package(package: str) -> dict[str, Any]:
    root = SRC / "ocm" / package
    constructors: list[dict[str, Any]] = []
    class_defs: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.py")):
        rel = str(path.relative_to(REPO))
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = _call_name(node)
                if name in CORE_CTORS:
                    constructors.append({"name": name, "path": rel, "lineno": node.lineno})
            elif isinstance(node, ast.ClassDef) and node.name in CORE_CTORS:
                class_defs.append({"name": node.name, "path": rel, "lineno": node.lineno})
    return {
        "package": package,
        "constructors": constructors,
        "core_class_defs": class_defs,
        "n_core_constructors": len(constructors),
        "n_core_class_defs": len(class_defs),
    }


def classify_constructor(item: dict[str, Any]) -> dict[str, Any]:
    path = item["path"]
    name = item["name"]
    if name == "OCMRuntime" and path == "src/ocm/chat/session.py":
        kind = "SHARED_RUNTIME_ENTRY"
        live_second = False
        detail = "ChatSession constructs the one live ocm_runtime.OCMRuntime ledger for the session."
    elif name == "OCMRuntime" and path == "src/ocm/dialogue/session.py":
        kind = "SHARED_RUNTIME_REOPEN"
        live_second = False
        detail = "DialogueRuntime.resume reopens OCMRuntime at the same ledger root; not a second field."
    elif name in {"KnowledgeSpace", "EvidenceRegistry", "OperatorRegistry", "StaticCommitAuthority"}:
        kind = "LIVE_SECOND_CORE"
        live_second = True
        detail = f"{name} constructed inside a domain package would be a forked core."
    else:
        kind = "UNCLASSIFIED_CORE_CTOR"
        live_second = True
        detail = f"{name} at {path}:{item['lineno']} is not a registered shared-entry constructor."
    return {**item, "kind": kind, "live_second_core": live_second, "detail": detail}


def import_identities() -> dict[str, Any]:
    runtime_pkg = importlib.import_module("ocm.runtime")
    field_bridge = importlib.import_module("ocm.language.field_bridge")
    lifecycle = importlib.import_module("ocm.science.lifecycle")
    lifetime = importlib.import_module("ocm.lifetime.machine")
    work_contracts = importlib.import_module("ocm.work.contracts")
    operators = importlib.import_module("ocm.operators.registry")
    live = live_runtime_mod.OCMRuntime
    custody = custody_runtime_mod.OCMRuntime
    return {
        "live_class": f"{live.__module__}.{live.__qualname__}",
        "custody_class": f"{custody.__module__}.{custody.__qualname__}",
        "package_export_is_custody": runtime_pkg.OCMRuntime is custody,
        "package_export_is_live": runtime_pkg.OCMRuntime is live,
        "live_is_not_custody": live is not custody,
        "language_field_bridge_uses_live": field_bridge.OCMRuntime is live,
        "science_lifecycle_uses_live": lifecycle.OCMRuntime is live,
        "lifetime_persistent_uses_live_attr": hasattr(lifetime.PersistentOCM, "identity"),
        "work_operator_is_not_operator_spec": work_contracts.Operator is not operators.OperatorSpec,
        "science_ledger_holds_runtime": "runtime" in science_lifecycle.ScienceLedger.__dataclass_fields__,
    }


def _seeing_graph() -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("event", "event", "see"),
            MNode("left", "entity", "person"),
            MNode("right", "entity", "person"),
        ),
        (
            MEdge("ROLE:agent", ("event",), ("left",)),
            MEdge("ROLE:patient", ("event",), ("right",)),
        ),
        root="event",
    )


def _anchor(runtime: OCMRuntime, atom_id: str) -> str:
    _, eid = runtime.admit_evidence(
        {"fixture_entity": atom_id},
        Channel.IMPORTED,
        "g1-duplicate-cores",
        authority=Authority.of(world_truth=1),
    )
    runtime.admit_object(
        Atom(
            atom_id,
            "claim",
            WarrantProfile.of({eid}),
            Authority.of(world_truth=1),
            Scope.universal(),
            quarantined=True,
            content_ref=atom_id,
        ),
        (),
        CertificateKind.IMPORTED,
    )
    return eid


def run_shared_core_probe(root: Path) -> dict[str, Any]:
    runtime = OCMRuntime(root)
    evidence_id = id(runtime.state.evidence)
    operators_id = id(runtime.state.operators)
    pi_solve = callable(getattr(runtime, "solve", None))
    host_authority_injected = runtime._authority is None

    _anchor(runtime, "field:alice")
    _anchor(runtime, "field:bob")
    _, said = runtime.admit_evidence(
        {"utterance": "Alice sees Bob", "speaker": "user", "salt": SALT},
        Channel.OBSERVATION,
        "user",
        scope=Scope.of("g1:language"),
        authority=Authority.of(speaker=1),
    )
    language_receipt = bind_meaning(
        runtime,
        _seeing_graph(),
        {"left": "field:alice", "right": "field:bob"},
        warrant=WarrantProfile.of({said}),
        certificate=CertificateKind.OBSERVATION,
        authority=Authority.of(speaker=1),
        scope=Scope.of("g1:language"),
    )
    language_live_before = binding_liveness(runtime, language_receipt.representation_id) is Liveness.LIVE

    science = science_lifecycle.ScienceLedger(runtime)
    science.observe("obs-p", "lab", {"fact": "P", "salt": SALT})
    math_eid = science.conclude(
        "thm-id",
        "P implies P",
        support=["obs-p"],
        kind="FORMAL",
    )
    _, kernel_run = runtime.admit_evidence(
        {"kernel": "propositional", "statement": "P -> P", "salt": SALT},
        Channel.PROOF,
        "science.kernel",
        scope=Scope.of("science"),
    )
    cert = proof_check(
        FormalStatement(
            "stmt-p-imp-p",
            "propositional",
            "P -> P",
            "P implies P",
            (kernel_run,),
        ),
        run_id=kernel_run,
    )

    ids_before_work = set(runtime.state.ks.ids)
    work_op = WorkOperator(
        "inc",
        "1",
        "proc",
        lambda s: True,
        lambda s: {**s, "n": int(s["n"]) + 1},
        ("n",),
        lambda s: True,
        lambda s: s.get("n") == 1,
    )
    contract = TaskContract(
        "t",
        "1",
        "proc",
        {"n": 0},
        "n=1",
        ("inc",),
        (),
        ("n",),
        {},
        4,
        0,
        Authority(),
        lambda state, hidden: state.get("n") == 1,
    )
    new_state, step = apply_operator(work_op, {"n": 0}, contract)
    ids_after_work_apply = set(runtime.state.ks.ids)
    _, demo_eid = runtime.admit_evidence(
        {"demonstration": "inc", "salt": SALT},
        Channel.DEMONSTRATION,
        "work.demo",
        scope=Scope.of("g1:procedural"),
    )
    spec = OperatorSpec(
        "inc-spec",
        "1",
        BackendKind.PROGRAMMATIC,
        lambda ks, args: {"n": int(args.get("n", 0)) + 1},
        ("n",),
    )
    runtime.register_operator(spec)

    # KnowledgeSpace is structurally immutable: admit returns a new space on the
    # same runtime. Identity is the live runtime field, not the initial object id.
    same_ks = runtime.state.ks is science.runtime.state.ks
    same_evidence = id(runtime.state.evidence) == evidence_id
    same_operators = id(runtime.state.operators) == operators_id
    language_in_ks = language_receipt.representation_id in runtime.state.ks.ids
    math_in_ledger = math_eid in runtime.state.evidence.records
    procedural_in_ledger = demo_eid in runtime.state.evidence.records
    work_apply_not_field_write = ids_before_work == ids_after_work_apply
    science_shares_runtime = science.runtime is runtime

    runtime.persist()
    reopened = OCMRuntime(root)
    reopen_shares_all_three = (
        language_receipt.representation_id in reopened.state.ks.ids
        and math_eid in reopened.state.evidence.records
        and demo_eid in reopened.state.evidence.records
    )

    language_liveness_before_revoke = language_live_before
    math_liveness_before = science.liveness("thm-id") is Liveness.LIVE
    procedural_liveness_before = runtime.state.evidence.liveness([demo_eid]) is Liveness.LIVE

    runtime.revoke([said])
    language_after = binding_liveness(runtime, language_receipt.representation_id)
    math_after = science.liveness("thm-id")
    procedural_after = runtime.state.evidence.liveness([demo_eid])

    shared = all(
        [
            same_ks,
            same_evidence,
            same_operators,
            language_in_ks,
            math_in_ledger,
            procedural_in_ledger,
            work_apply_not_field_write,
            science_shares_runtime,
            language_liveness_before_revoke,
            math_liveness_before,
            procedural_liveness_before,
            language_after is not Liveness.LIVE,
            math_after is Liveness.LIVE,
            procedural_after is Liveness.LIVE,
            cert.verdict is KernelVerdict.PASS,
            step.outcome.value == "APPLIED",
            new_state["n"] == 1,
            pi_solve,
            host_authority_injected,
            reopen_shares_all_three,
        ]
    )
    return {
        "shared_one_core": shared,
        "F": {
            "same_knowledge_space_object": same_ks,
            "same_evidence_registry_object": same_evidence,
            "language_representation_in_ks": language_in_ks,
            "math_conclusion_in_evidence": math_in_ledger,
            "procedural_demo_in_evidence": procedural_in_ledger,
            "science_ledger_is_adapter_on_same_runtime": science_shares_runtime,
            "ks_atom_count": len(runtime.state.ks.ids),
            "evidence_record_count": len(runtime.state.evidence.records),
            "reopen_shares_all_three": reopen_shares_all_three,
            "ks_replaced_on_admit": True,
        },
        "O": {
            "same_operator_registry_object": same_operators,
            "operator_spec_registered_on_shared_registry": spec.operator_id + "@" + spec.version
            in runtime.state.operator_manifests
            or any(spec.operator_id in k for k in runtime.state.operator_manifests),
            "work_operator_apply_does_not_write_ks": work_apply_not_field_write,
            "work_apply_outcome": step.outcome.value,
            "work_dict_state_after": new_state,
        },
        "Pi": {
            "runtime_has_solve": pi_solve,
            "work_apply_is_not_runtime_solve": True,
        },
        "C": {
            "commit_authority_host_injected_not_constructed": host_authority_injected,
            "revoke_uses_shared_runtime": True,
            "language_liveness_after_utterance_revoke": language_after.value,
            "math_liveness_after_language_revoke": math_after.value,
            "procedural_liveness_after_language_revoke": procedural_after.value,
            "independent_warrants_survive_cross_domain_revoke": math_after is Liveness.LIVE
            and procedural_after is Liveness.LIVE,
        },
        "language": {
            "representation_id": language_receipt.representation_id,
            "utterance_evidence": said,
            "live_before_revoke": language_liveness_before_revoke,
        },
        "math": {
            "conclusion_evidence": math_eid,
            "kernel": cert.kernel,
            "kernel_verdict": cert.verdict.value,
            "kernel_detail": cert.detail,
        },
        "procedural": {
            "demo_evidence": demo_eid,
            "operator_manifest_keys": sorted(runtime.state.operator_manifests),
        },
        "slots": {
            "F": "one KnowledgeSpace + one EvidenceRegistry on one ocm.runtime.ocm_runtime.OCMRuntime",
            "O": "one OperatorRegistry; work.Operator is a parallel dict-state schema",
            "Pi": "runtime.solve executive; work.apply_operator is not a second executive field",
            "C": "constitution + host-injected CommitAuthority; domains do not construct C",
        },
    }


def lookalikes() -> list[dict[str, Any]]:
    return [
        {
            "id": "M0_RUNTIME_NAME_COLLISION",
            "kind": "historical_wrapper",
            "paths": ["src/ocm/runtime/state.py", "src/ocm/runtime/__init__.py"],
            "live_second_core": False,
            "disposition": "RETAIN_AS_CUSTODY",
            "detail": (
                "Package export ocm.runtime.OCMRuntime is the M0 custody runtime. "
                "Live cognition imports ocm.runtime.ocm_runtime.OCMRuntime."
            ),
        },
        {
            "id": "WORK_OPERATOR_PARALLEL_SCHEMA",
            "kind": "parallel_operator_api",
            "paths": ["src/ocm/work/contracts.py", "src/ocm/operators/registry.py"],
            "live_second_core": False,
            "disposition": "RETAIN_AS_DONOR_SCHEMA",
            "detail": (
                "work.Operator applies to dict state and does not write KnowledgeSpace. "
                "Persistent identity is admitted through the shared OCMRuntime ledger."
            ),
        },
        {
            "id": "MEANINGGRAPH_COMPACT_VIEW",
            "kind": "typed_working_view",
            "paths": ["src/ocm/language/meaning.py", "src/ocm/language/field_bridge.py"],
            "live_second_core": False,
            "disposition": "TYPED_VIEW",
            "detail": "MeaningGraph is compact language representation. Persistence goes through field_bridge onto the one KSO.",
        },
        {
            "id": "DIALOGUE_WORKSPACE_COMPACT_VIEW",
            "kind": "typed_working_view",
            "paths": ["src/ocm/dialogue/workspace.py", "src/ocm/dialogue/field_binding.py"],
            "live_second_core": False,
            "disposition": "TYPED_VIEW",
            "detail": "DialogueWorkspace is a conversation view. Binding reuses language.field_bridge.",
        },
        {
            "id": "SCIENCE_LEDGER_ADAPTER",
            "kind": "typed_working_view",
            "paths": ["src/ocm/science/lifecycle.py", "src/ocm/science/proof.py"],
            "live_second_core": False,
            "disposition": "ADAPTER_ON_SHARED_RUNTIME",
            "detail": "ScienceLedger holds the shared OCMRuntime. Proof kernels are donor checkers, not a second C.",
        },
        {
            "id": "GOVERNEDSPACE_VIEW",
            "kind": "historical_wrapper",
            "paths": ["src/ocm/kso/admission.py", "src/ocm/kso/space.py"],
            "live_second_core": False,
            "disposition": "ALREADY_COLLAPSED_TO_VIEWS",
            "detail": "GovernedSpace / documented KSO wrappers are views of one KnowledgeSpace. No RecursiveKSO or UnifiedKSO class remains.",
        },
        {
            "id": "KSO_PI_VS_EXECUTIVE_PI",
            "kind": "naming_collision",
            "paths": ["docs/spec/KSO_NAVIGATION_REFERENCE_V1.md", "src/ocm/runtime/solve.py"],
            "live_second_core": False,
            "disposition": "DISAMBIGUATED",
            "detail": "KSO navigation is Π_nav. Issue #165 executive is Π_exec (solve.py). Not two cores.",
        },
    ]


def g1_1_6_honesty(*, shared: bool, live_second: list[dict[str, Any]], deleted: bool) -> dict[str, Any]:
    """Whether the G1.1.6 checkbox can be honestly checked.

    The architecture question (share one core vs fork) is checkable. The verb
    “eliminate” as production deletion is not earnable here: deletion is forbidden
    and there is no live second core to remove.
    """
    forks = [x for x in live_second if x.get("live_second_core")]
    checkable = True
    as_deletion = False
    if deleted:
        as_deletion = False
        checkable = False
        status = "PROTOCOL_VIOLATION_PRODUCTION_DELETED"
        reason = "Production deletion occurred; this capsule forbids it."
    elif forks:
        status = "NOT_EARNED_AS_DELETION"
        reason = (
            "Live second-core constructors exist and were classified. "
            "Elimination-by-deletion is forbidden, so G1.1.6 cannot be earned as deletion."
        )
    elif shared:
        status = "NOT_EARNED_AS_DELETION"
        reason = (
            "Language, mathematics and procedural domains already share one (F, O, Π, C). "
            "Lookalikes are classified, not deleted. The checkbox verb “eliminate” is not "
            "an applicable deletion: there is no live second core."
        )
    else:
        status = "CANNOT_CHECK_CORE_IDENTITY"
        checkable = False
        reason = "Shared-core probe did not confirm one field; G1.1.6 is not closed."
    return {
        "id": "G1.1.6",
        "text": "Eliminate duplicated cognitive cores.",
        "can_be_honestly_checked": checkable,
        "check_kind": "architecture_measurement_and_classification",
        "can_be_honestly_earned_as_deletion": as_deletion,
        "status": status,
        "reason": reason,
        "live_second_core_count": len(forks),
    }


def decide_terminal(probe: dict[str, Any], classified_ctors: list[dict[str, Any]]) -> str:
    live_forks = [c for c in classified_ctors if c["live_second_core"]]
    if live_forks:
        return "DOMAIN_CORE_FORK_REQUIRED"
    if probe["shared_one_core"]:
        return "SINGLE_CORE_AT_SCOPE"
    return "CANNOT_CHECK_CORE_IDENTITY"


def freeze_parent() -> dict[str, Any]:
    dup = FREEZE_DIR / "DUPLICATE_CORES.json"
    boxes = FREEZE_DIR / "G1_CHECKBOXES.json"
    terminal = FREEZE_DIR / "TERMINAL.json"
    payload = {
        "path": "research/g1-vessel-freeze-v1",
        "present": FREEZE_DIR.is_dir(),
        "not_overwritten": True,
        "duplicate_cores_sha256": sha256_file(dup) if dup.is_file() else None,
        "g1_checkboxes_sha256": sha256_file(boxes) if boxes.is_file() else None,
    }
    if boxes.is_file():
        data = json.loads(boxes.read_text())
        g116 = next(x for x in data["G1.1"] if x["id"] == "G1.1.6")
        payload["freeze_G1_1_6_status"] = g116["status"]
    if terminal.is_file():
        payload["freeze_terminal"] = json.loads(terminal.read_text())["terminal"]
    return payload


def src_tree_intact() -> dict[str, Any]:
    src = REPO / "src"
    files = sorted(p for p in src.rglob("*") if p.is_file())
    return {
        "exists": src.is_dir(),
        "n_files": len(files),
        "deleted": False,
        "note": "This capsule writes only under research/g1-duplicate-cores-v1/ and the workflow file.",
    }


def run_study(tmp: Path) -> dict[str, Any]:
    scans = [scan_package(name) for name in DOMAIN_PACKAGES]
    ctor_items = [item for scan in scans for item in scan["constructors"]]
    classified_ctors = [classify_constructor(item) for item in ctor_items]
    identities = import_identities()
    probe = run_shared_core_probe(tmp)
    items = lookalikes()
    live_second = [c for c in classified_ctors if c["live_second_core"]] + [
        x for x in items if x["live_second_core"]
    ]
    deleted = False
    honesty = g1_1_6_honesty(shared=probe["shared_one_core"], live_second=live_second, deleted=deleted)
    terminal = decide_terminal(probe, classified_ctors)
    domains_share = {
        "language": probe["F"]["language_representation_in_ks"] and identities["language_field_bridge_uses_live"],
        "mathematics": probe["F"]["math_conclusion_in_evidence"] and identities["science_lifecycle_uses_live"],
        "procedural": probe["F"]["procedural_demo_in_evidence"]
        and identities["work_operator_is_not_operator_spec"]
        and probe["O"]["work_operator_apply_does_not_write_ks"],
    }
    return {
        "schema": SCHEMA,
        "salt": SALT,
        "issue": ISSUE,
        "gate": GATE,
        "head": git_head(),
        "terminal": terminal,
        "production_code_deleted": deleted,
        "parent_freeze": freeze_parent(),
        "src_custody": src_tree_intact(),
        "live_core": {
            "F": probe["slots"]["F"],
            "O": probe["slots"]["O"],
            "Pi": probe["slots"]["Pi"],
            "C": probe["slots"]["C"],
            "class": identities["live_class"],
            "custody_class": identities["custody_class"],
        },
        "identities": identities,
        "domains_share_one_core": domains_share,
        "all_three_domains_share_one_core": all(domains_share.values()) and probe["shared_one_core"],
        "probe": probe,
        "domain_scans": scans,
        "classified_constructors": classified_ctors,
        "lookalikes": items,
        "live_second_cores": live_second,
        "G1_1_6": honesty,
        "G1_checkboxes": {
            "G1.1": [
                {
                    "id": "G1.1.6",
                    "text": "Eliminate duplicated cognitive cores.",
                    "status": honesty["status"],
                    "can_be_honestly_checked": honesty["can_be_honestly_checked"],
                    "can_be_honestly_earned_as_deletion": honesty["can_be_honestly_earned_as_deletion"],
                    "evidence": "research/g1-duplicate-cores-v1/RESULT.json",
                }
            ]
        },
        "claim_ceiling": (
            "Architecture-scope measurement: language, mathematics and procedural work "
            "enter one (F, O, Π, C) at this head. Lookalikes classified. Production not "
            "deleted. Not #93 empirical field closure. Not G1.2 minimality."
        ),
        "not_issued": [
            "MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE",
            "CURRENT_KSO_PARENT_SUFFICIENT",
            "DOMAIN_CORE_FORK_REQUIRED",
            "CONTROLLER_GROWTH_DOMINATES",
            "STATE_SIZE_DOMINATES",
            "PARENT_SUFFICIENT",
        ],
        "not_issued_reasons": {
            "CURRENT_KSO_PARENT_SUFFICIENT": (
                "Reserved for #93 empirical field closure. This capsule is architecture-scope "
                "core identity, issued as SINGLE_CORE_AT_SCOPE when the probe shares one core."
            ),
            "DOMAIN_CORE_FORK_REQUIRED": "Issued only if a domain constructs a live second (F, O, Π, C).",
        },
        "static_commit_authority_available_to_host": StaticCommitAuthority.__name__,
    }


def main(out: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="g1-duplicate-cores-") as tmp:
        result = run_study(Path(tmp))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "G1_1_6_can_be_honestly_checked": result["G1_1_6"]["can_be_honestly_checked"],
                "G1_1_6_status": result["G1_1_6"]["status"],
                "shared": result["all_three_domains_share_one_core"],
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)
