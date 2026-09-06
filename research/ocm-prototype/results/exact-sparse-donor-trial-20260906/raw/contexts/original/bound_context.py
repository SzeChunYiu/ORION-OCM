"""Fixed trusted-host binding for a future authorized consumer run; never run on import."""
from pathlib import Path
import json
import shutil
import sys
from restore_context import restore, sha


def load(context_root, worker_root):
    """Return (evaluate kwargs, metering context), using only a new private state copy."""
    context_root, worker_root = Path(context_root).resolve(), Path(worker_root).resolve()
    binding = json.loads((context_root / "HOST_BINDING_MANIFEST.json").read_text())
    if sha(context_root / "CONTEXT_MANIFEST.json") != binding["context_manifest_sha256"]:
        raise ValueError("CANNOT_CHECK_CONTEXT_MANIFEST_DRIFT")
    for name, record in binding["required_additional_files"].items():
        if sha(context_root / "source" / name) != record["sha256"]:
            raise ValueError("CANNOT_CHECK_HOST_BINDING_INPUT_DRIFT:" + name)
    worker_root.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(context_root / "CONTEXT_MANIFEST.json", worker_root / "CONTEXT_MANIFEST.json")
    shutil.copytree(context_root / "input", worker_root / "input")
    (worker_root / "prefix-state").mkdir()
    shutil.copyfile(context_root / "prefix-state/ledger.jsonl", worker_root / "prefix-state/ledger.jsonl")
    source_root = context_root / "source"
    ctx = restore(worker_root, source_root)
    sys.path.insert(0, str(source_root / "research/ocm-prototype"))
    import clia_reuse_vessel as V
    from ocm.kso.types import Authority
    runtime = ctx["runtime"]
    before = (runtime.state.kso_state_hash, runtime.state.registry_revision, runtime.state.evidence_epoch)
    original_manifests = dict(runtime.state.operator_manifests)
    bindings = json.loads((worker_root / "input/ocm-state/study-bindings.json").read_text())
    receipts = [V.bind(runtime, b["descriptor_id"]) for b in bindings["programs"].values()]
    if before != (runtime.state.kso_state_hash, runtime.state.registry_revision, runtime.state.evidence_epoch):
        raise ValueError("CANNOT_CHECK_HOST_BIND_CHANGED_AUTHORITY")
    if runtime.state.operator_manifests != original_manifests or len(runtime.state.operators.operators) != 2:
        raise ValueError("CANNOT_CHECK_WRONG_HOST_BINDING")
    checks = []
    counters = {"catalogue_visits": [], "application_calls": 0, "pointwise_checks": 0, "synthesis_dispatches": 0}
    operators = V.catalogue(runtime, ctx["task"].task_id, ctx["request"], checks, counters)
    expected = ["syntax:udpipe1", "procedure:cvc5"] + sorted(m["operator_id"] for m in original_manifests.values())
    if [op.operator_id for op in operators] != expected:
        raise ValueError("CANNOT_CHECK_WRONG_FULL_CATALOGUE")
    kwargs = {"ks": runtime.state.ks, "task": ctx["task"], "operators": operators,
              "revoked": runtime.state.revoked, "config": ctx["config"], "commit_authority": Authority()}
    metering = {"runtime": runtime, "checks": checks, "counters": counters,
                "binding_receipts": receipts, "catalogue": expected, "authority_identity": before}
    return kwargs, metering
