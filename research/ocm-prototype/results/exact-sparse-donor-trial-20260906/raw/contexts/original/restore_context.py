"""Read-only current-core restoration of the bound pre-query G1 context."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def restore(root=HERE, source_root=None):
    """Return runtime, task, config and request; do not bind or invoke operators."""
    root = Path(root)
    source_root = Path(source_root or root / "source")
    manifest = json.loads((root / "CONTEXT_MANIFEST.json").read_text())
    for name, expected in manifest["original_inputs"].items():
        if sha(root / "input" / name) != expected:
            raise ValueError("CANNOT_CHECK_INPUT_DRIFT:" + name)
    for name, record in manifest["source_files"].items():
        if sha(source_root / name) != record["sha256"]:
            raise ValueError("CANNOT_CHECK_CURRENT_SOURCE_DRIFT:" + name)
    prefix = root / "prefix-state/ledger.jsonl"
    if sha(prefix) != manifest["prefix_ledger_sha256"]:
        raise ValueError("CANNOT_CHECK_PREFIX_DRIFT")
    sys.path[:0] = [str(source_root / "src")]
    from ocm.runtime.ocm_runtime import OCMRuntime
    from ocm.runtime import solve as SV
    from ocm.kso.ids import content_hash
    from ocm.store.event import OCMEvent
    from ocm.store.ledger import LedgerStore
    # Refuse an already imported incompatible core from a different checkout.
    for name, module in tuple(sys.modules.items()):
        if not name.startswith(("ocm.", "orion_v2.")) or not getattr(module, "__file__", None):
            continue
        relative = "src/" + name.replace(".", "/")
        relative += "/__init__.py" if hasattr(module, "__path__") else ".py"
        expected = manifest["source_files"].get(relative)
        if expected and sha(module.__file__) != expected["sha256"]:
            raise ValueError("CANNOT_CHECK_IMPORTED_CORE_DRIFT:" + name)
    current_g1 = (source_root / "research/ocm-prototype/g1_vessel.py").read_text()
    if "CONFIG = SV.SolveConfig(exact_extraction_max_atoms=0)" not in current_g1:
        raise ValueError("CANNOT_CHECK_CHANGED_CONFIG_CONSTRUCTOR")
    config = SV.SolveConfig(exact_extraction_max_atoms=0)
    runtime = OCMRuntime(root / "prefix-state", config=config)
    rows = [json.loads(line) for line in (root / "input/5-restore-ocm.rows.jsonl").read_text().splitlines()]
    row = next(r for r in rows if r["id"] == manifest["original_request_id"])
    request = row["request"]
    target = next(OCMEvent.from_dict(e.payload) for e in LedgerStore(root / "input/ocm-state").entries()
                  if e.kind == "OCM_EVENT" and e.payload["sequence"] == manifest["query_open_sequence"])
    target.expectation.check(log_head=runtime.events[-1].event_hash,
                            kso_state_hash=runtime.state.kso_state_hash,
                            registry_revision=runtime.state.registry_revision,
                            evidence_epoch=runtime.state.evidence_epoch)
    if len(runtime.events) != manifest["prefix_event_count"]:
        raise ValueError("CANNOT_CHECK_WRONG_EVENT_PREFIX")
    if runtime.state.kso_state_hash != manifest["target_state_hash"]:
        raise ValueError("CANNOT_CHECK_WRONG_STATE")
    qid = "clia:application:" + content_hash(request)
    refs = (qid, "g1:model", "g1:clia", *(x for x in runtime.state.ks.ids if x.startswith("clia:executable:")))
    task = SV.Task(qid, (SV.QueryPart(json.dumps(request, sort_keys=True, separators=(",", ":")), "query_seed", refs),), context="g1-pilot")
    if task.task_id != target.payload["task_id"] or refs != target.input_object_ids or list(task.targets) != target.payload["targets"]:
        raise ValueError("CANNOT_CHECK_WRONG_TASK_BINDING")
    if sorted(runtime.state.revoked) != row["authority"]["revoked"]:
        raise ValueError("CANNOT_CHECK_WRONG_REVOCATION")
    grounded, seed = SV.atomise(runtime.state.ks, task)
    stages = row["result"]["trace"]["stages"]
    if grounded.payload != next(s["payload"] for s in stages if s["stage"] == "GROUNDING"):
        raise ValueError("CANNOT_CHECK_WRONG_GROUNDING")
    if len(runtime.state.ks.ids) != next(s["payload"]["atoms"] for s in stages if s["stage"] == "REPRESENTATION"):
        raise ValueError("CANNOT_CHECK_WRONG_FIELD_SIZE")
    if sha(prefix) != manifest["prefix_ledger_sha256"]:
        raise ValueError("CANNOT_CHECK_RESTORE_WROTE_LEDGER")
    return {"runtime": runtime, "task": task, "config": config, "request": request,
            "seed": seed, "manifest": manifest}
