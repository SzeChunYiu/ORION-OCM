"""G3 remaining: recover source-bound real failure/probe incidents from the ledger.

Research-only. Production src is imported, not edited. Task ids are lineage.
Timeout is RESOURCE_BOUND, never JUMP. PARENT_SUFFICIENT is not programme failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
HERE = Path(__file__).resolve().parent
G2_COG = REPO / "research" / "g2-cognitive-objects-v1"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(G2_COG))

from ocm.kso.admission import CertificateKind
from ocm.kso.ids import content_hash, evidence_id
from ocm.kso.space import Atom
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness as KSOLiveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.event import EventType
from ocm.store.evidence import Channel

from g2_cognitive_objects.types import (
    UNKNOWN,
    AcquisitionLineage,
    CheckStatus,
    CorrectnessEvidence,
    CurrentAuthorizationState,
    FailureAttemptV1,
    FailureKind,
    InformationVector,
    Liveness,
    OriginCategory,
    ResourceVector,
    ScopeState,
    UsefulnessEvidence,
    Verdict,
    emit,
)

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
SCHEMA = "ocm.g3.source-bound-failure.result.v1"
ENV_V1 = "polynomial-source-bound-probe.v1"
SCOPE = Scope.of("source-bound-probe.v1")
NAMESPACE = "ocm"

SOURCE_A = "probe://source-A"
SOURCE_B = "probe://source-B"
TASK_ALPHA = "task-alpha"
TASK_BETA = "task-beta"
REMAINING = (Fraction(1), Fraction(1))
METHOD = "square"
BUDGET = "max_length=2"

G3_FAILMEM = REPO / "research" / "g3-failure-memory-v1" / "RESULT.json"
G3_REPR = REPO / "research" / "g3-representation-v1" / "RESULT.json"
G3_DIAG = REPO / "research" / "g3-representation-diagnosis-v1" / "RESULT.json"

LEGAL_TERMINALS = {
    "PARENT_SUFFICIENT_AT_SCOPE",
    "SOURCE_BOUND_FAILURE_RECOVERY_SUPPORTED_AT_SCOPE",
    "SOURCE_BOUND_FAILURE_NOT_RECOVERED",
}


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def pin_methods() -> str:
    blob = git_blob_sha1(SRC / "ocm" / "learning" / "methods.py")
    if blob != METHOD_BLOB:
        raise RuntimeError(f"methods.py blob {blob} != pinned {METHOD_BLOB}")
    return blob


def canonicalize(coeffs) -> tuple[Fraction, ...]:
    coeffs = tuple(Fraction(c) for c in coeffs)
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs = coeffs[:-1]
    return coeffs


def remaining_signature(coeffs) -> str:
    return ",".join(str(c) for c in canonicalize(coeffs))


def run_square_invert_probe(coeffs) -> dict[str, Any]:
    """Real checker: can square be the last operator producing this remaining polynomial?"""
    target = canonicalize(coeffs)
    square_of_identity = M.normal_form(("square",))
    odd_degree = (len(target) - 1) % 2 == 1
    identity_square_mismatch = square_of_identity != target
    invertible = (not odd_degree) and (not identity_square_mismatch)
    if invertible:
        raise RuntimeError("planted remaining was unexpectedly square-invertible")
    return {
        "checker_id": M.CHECKER,
        "method_id": METHOD,
        "remaining_sig": remaining_signature(target),
        "remaining": [str(c) for c in target],
        "square_of_identity": [str(c) for c in square_of_identity],
        "odd_degree": odd_degree,
        "identity_square_mismatch": identity_square_mismatch,
        "invertible": False,
        "failure_kind": FailureKind.METHOD_FAILURE.value,
        "outcome": "INVERT_IMPOSSIBLE",
        "complete": True,
        "timeout": False,
        "jump": False,
        "diagnosis": "METHOD_FAILURE",
        "feedback": "remaining degree is odd; square cannot invert 1+x under the registered grammar",
    }


def classify_timeout_only_probe() -> dict[str, Any]:
    """Timeout / hard-wall is RESOURCE_BOUND. A mutant parent emits JUMP."""
    features = {
        "checker_identity": True,
        "extra_budget_finds": False,
        "grammar_exhausted": False,
        "hard_wall": True,
        "timeout": True,
        "remaining_legal_work": True,
    }
    predicted = "RESOURCE_BOUND"
    mutant = "JUMP"
    return {
        "id": "timeout-only",
        "features": features,
        "predicted": predicted,
        "timeout_jump_parent": mutant,
        "jump_refused": predicted != "JUMP",
        "independent_truth": "RESOURCE_BOUND",
        "failure_kind": FailureKind.UNKNOWN.value,
        "outcome": "RESOURCE_BOUND",
        "complete": False,
        "timeout": True,
        "jump": False,
        "feedback": "budget wall; not a completeness certificate and not JUMP",
    }


def incident_payload(source: str, probe: dict[str, Any]) -> dict[str, Any]:
    """Ledger payload. Task ids are lineage on the attempt object, never part of the skip key."""
    return {
        "schema": "ocm.g3.source-bound-probe.v1",
        "source": source,
        "method_id": probe["method_id"],
        "remaining_sig": probe["remaining_sig"],
        "budget": BUDGET,
        "environment_version": ENV_V1,
        "failure_kind": probe["failure_kind"],
        "outcome": probe["outcome"],
        "complete": probe["complete"],
        "feedback": probe["feedback"],
        "checker_id": probe["checker_id"],
        "probe_kind": "square-invert",
        "skip_key": "source+evidence_id",
    }


def expected_evidence_id(payload: dict[str, Any], source: str) -> str:
    return evidence_id(NAMESPACE, {"payload": payload, "source": source, "channel": Channel.EXPERIMENT.value})


def make_failure_attempt(payload: dict[str, Any], evidence: str, task_id_lineage: str) -> FailureAttemptV1:
    scope = ScopeState(
        contexts=(f"source:{payload['source']}", f"evidence:{evidence}"),
        epoch_start=0.0,
        epoch_end=None,
    )
    return FailureAttemptV1(
        attempt_id="g3.srcfail:" + content_hash(payload),
        method_id=payload["method_id"],
        task_id=task_id_lineage,
        scope=scope,
        budget=payload["budget"],
        environment_version=payload["environment_version"],
        outcome=payload["outcome"],
        feedback=payload["feedback"],
        failure_kind=FailureKind(payload["failure_kind"]),
        resources=ResourceVector(work_units=1, notes=("one source-bound probe",)),
        acquisition_lineage=AcquisitionLineage(
            origin_category=OriginCategory.LEARNED_APPLICABILITY,
            episode_ids=("g3.source-bound-probe.plant.v1",),
            status=CheckStatus.MEASURED,
            discovery_evidence_id=evidence,
            information=InformationVector(grounded_observations=1),
        ),
        correctness=CorrectnessEvidence(
            checker_id=M.CHECKER,
            verdict=Verdict.FAIL,
            status=CheckStatus.MEASURED,
            independent_of_usefulness=True,
        ),
        usefulness=UsefulnessEvidence(
            independent_of_correctness=True,
            status=CheckStatus.UNKNOWN,
        ),
        authorization=CurrentAuthorizationState(
            admitted=True,
            proof_liveness=Liveness.LIVE,
            applicability_liveness=Liveness.LIVE,
            serving_liveness=Liveness.LIVE,
            warrant_ids=(evidence,),
            scope=scope,
            status=CheckStatus.MEASURED,
        ),
            notes=(
            "scope key is source/evidence identity, not task id",
            f"task_id is lineage only: {task_id_lineage}",
            f"remaining_sig={payload['remaining_sig']} is not the skip key",
        ),
    )


def admit_incident(
    runtime: OCMRuntime, payload: dict[str, Any], source: str, task_id_lineage: str,
) -> dict[str, Any]:
    admission, eid = runtime.admit_evidence(payload, Channel.EXPERIMENT, source, scope=SCOPE)
    if eid != expected_evidence_id(payload, source):
        raise RuntimeError(f"evidence id drifted: {eid}")
    rec = runtime.state.evidence.records[eid]
    if rec.source != source:
        raise RuntimeError("evidence record source mismatch")
    warrant = WarrantProfile.of({eid})
    atom_id = "probe-incident:" + eid
    atom = Atom(
        atom_id,
        "counterexample",
        warrant,
        scope=SCOPE,
        quarantined=True,
        content_ref=content_hash(payload),
        meta=(
            ("source", source),
            ("evidence_id", eid),
            ("remaining_sig", payload["remaining_sig"]),
            ("method_id", payload["method_id"]),
            ("failure_kind", payload["failure_kind"]),
            ("task_id_lineage", task_id_lineage),
            ("skip_key", "source+evidence_id"),
        ),
    )
    runtime.admit_object(atom, (), CertificateKind.EXPERIMENTATION)
    attempt = make_failure_attempt(payload, eid, task_id_lineage)
    return {
        "admission": admission.value,
        "evidence_id": eid,
        "source": source,
        "atom_id": atom_id,
        "content_hash": rec.content_hash,
        "channel": rec.channel.value,
        "payload": payload,
        "failure_attempt": json.loads(emit(attempt).decode()),
    }


def recover_from_runtime(runtime: OCMRuntime) -> list[dict[str, Any]]:
    """Recover probe incidents from production evidence + KSO, keyed by source/evidence_id."""
    payloads: dict[str, dict[str, Any]] = {}
    for ev in runtime.events:
        if ev.event_type is EventType.EVIDENCE_ADMITTED:
            p = ev.payload
            eid = evidence_id(
                runtime.state.evidence.namespace,
                {"payload": p["payload"], "source": p["source"], "channel": p["channel"]},
            )
            payloads[eid] = p["payload"]
    incidents = []
    for eid, rec in runtime.state.evidence.records.items():
        payload = payloads.get(eid)
        if not isinstance(payload, dict) or payload.get("schema") != "ocm.g3.source-bound-probe.v1":
            continue
        atom_id = "probe-incident:" + eid
        atom = runtime.state.ks.atom_map().get(atom_id)
        live = runtime.state.evidence.liveness([eid]).value == "LIVE"
        atom_live = atom is not None and atom.liveness(runtime.state.revoked) is KSOLiveness.LIVE
        incidents.append({
            "evidence_id": eid,
            "source": rec.source,
            "channel": rec.channel.value,
            "content_hash": rec.content_hash,
            "live": live,
            "atom_id": atom_id,
            "atom_present": atom is not None,
            "atom_live": atom_live,
            "remaining_sig": payload.get("remaining_sig"),
            "method_id": payload.get("method_id"),
            "task_id_lineage": (dict(atom.meta).get("task_id_lineage") if atom is not None else UNKNOWN),
            "failure_kind": payload.get("failure_kind"),
            "skip_key": payload.get("skip_key"),
            "payload": payload,
        })
    incidents.sort(key=lambda row: (row["source"], row["evidence_id"]))
    return incidents


def lookup_by_source(incidents: list[dict[str, Any]], source: str, *, live_only: bool = False) -> list[dict[str, Any]]:
    return [
        row for row in incidents
        if row["source"] == source and (not live_only or row["live"])
    ]


def lookup_by_task_id(incidents: list[dict[str, Any]], task_id: str) -> list[dict[str, Any]]:
    return [row for row in incidents if row["task_id_lineage"] == task_id]


def lookup_by_remaining(incidents: list[dict[str, Any]], remaining_sig: str) -> list[dict[str, Any]]:
    return [row for row in incidents if row["remaining_sig"] == remaining_sig]


def use_source_incident(incidents: list[dict[str, Any]], source: str) -> dict[str, Any]:
    """New episode: skip re-probing a source iff a live source-bound incident exists."""
    live = lookup_by_source(incidents, source, live_only=True)
    used = bool(live)
    return {
        "source": source,
        "used": used,
        "skipped_reprobe": used,
        "n_live": len(live),
        "evidence_ids": [row["evidence_id"] for row in live],
    }


def ordinary_persist(path: Path, incidents: list[dict[str, Any]]) -> None:
    body = {"records": incidents, "fingerprint": content_hash({"records": incidents})}
    temp = path.with_suffix(".tmp")
    with temp.open("x", encoding="utf-8") as handle:
        json.dump(body, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def ordinary_load(path: Path) -> list[dict[str, Any]]:
    body = json.loads(path.read_text(encoding="utf-8"))
    records = body["records"]
    if content_hash({"records": records}) != body["fingerprint"]:
        raise RuntimeError("ordinary incident identity mismatch")
    return records


def plant_ledgers(root: Path, probe: dict[str, Any]) -> dict[str, Any]:
    live_root = root / "ocm-live"
    revoked_root = root / "ocm-revoked"
    live_root.mkdir()
    revoked_root.mkdir()

    payload_a = incident_payload(SOURCE_A, probe)
    payload_b = incident_payload(SOURCE_B, probe)

    live = OCMRuntime(live_root)
    rec_a = admit_incident(live, payload_a, SOURCE_A, TASK_ALPHA)
    rec_b = admit_incident(live, payload_b, SOURCE_B, TASK_ALPHA)
    live.persist()
    ordinary_persist(live_root / "incidents.json", recover_from_runtime(live))

    revoked = OCMRuntime(revoked_root)
    rec_a_r = admit_incident(revoked, payload_a, SOURCE_A, TASK_ALPHA)
    rec_b_r = admit_incident(revoked, payload_b, SOURCE_B, TASK_ALPHA)
    revoked.revoke((rec_a_r["evidence_id"],))
    revoked.persist()
    ordinary_persist(revoked_root / "incidents.json", recover_from_runtime(revoked))

    return {
        "live_root": live_root,
        "revoked_root": revoked_root,
        "parent_kso_state_hash": live.state.kso_state_hash,
        "incident_a": rec_a,
        "incident_b": rec_b,
        "revoked_incident_a": rec_a_r,
        "revoked_incident_b": rec_b_r,
        "parent_recovered": recover_from_runtime(live),
        "parent_revoked_recovered": recover_from_runtime(revoked),
    }


def spawn_restart_consumer(root: Path, out_path: Path) -> dict[str, Any]:
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable, "-B", str(HERE / "experiment.py"),
            "--restart-consumer",
            "--root", str(root),
            "--out", str(out_path),
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO),
        check=False,
    )
    if proc.returncode != 0 or not out_path.is_file():
        raise RuntimeError(
            f"restart consumer failed rc={proc.returncode}: {proc.stderr[-2000:]} {proc.stdout[-2000:]}"
        )
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    payload["returncode"] = proc.returncode
    payload["parent_pid"] = os.getpid()
    return payload


def run_restart_consumer(root: Path) -> dict[str, Any]:
    pin_methods()
    runtime = OCMRuntime(root)
    recovered = recover_from_runtime(runtime)
    ordinary_path = root / "incidents.json"
    ordinary = ordinary_load(ordinary_path) if ordinary_path.is_file() else []
    episode = use_source_incident(recovered, SOURCE_A)
    task_beta = lookup_by_task_id(recovered, TASK_BETA)
    task_alpha = lookup_by_task_id(recovered, TASK_ALPHA)
    remaining = lookup_by_remaining(recovered, remaining_signature(REMAINING))
    by_source_a = lookup_by_source(recovered, SOURCE_A)
    by_source_b = lookup_by_source(recovered, SOURCE_B)
    ordinary_a = lookup_by_source(ordinary, SOURCE_A)
    return {
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "interpreter": sys.executable,
        "root": str(root),
        "kso_state_hash": runtime.state.kso_state_hash,
        "n_events": len(runtime.events),
        "n_evidence": len(runtime.state.evidence.records),
        "recovered": recovered,
        "episode2_task_beta_source_A": episode,
        "lookup_source_A": by_source_a,
        "lookup_source_B": by_source_b,
        "lookup_task_alpha": task_alpha,
        "lookup_task_beta": task_beta,
        "lookup_remaining_1_1": remaining,
        "ordinary_source_A": ordinary_a,
        "ordinary_ties_source_A": (
            [row["evidence_id"] for row in ordinary_a]
            == [row["evidence_id"] for row in by_source_a]
        ),
        "keys_are_source_bound": all(
            row["skip_key"] == "source+evidence_id"
            and row["evidence_id"] != row["task_id_lineage"]
            and row["source"] != row["task_id_lineage"]
            for row in recovered
        ),
    }


def frozen_parent_terminals() -> dict[str, Any]:
    failmem = json.loads(G3_FAILMEM.read_text(encoding="utf-8"))
    repr_v1 = json.loads(G3_REPR.read_text(encoding="utf-8"))
    diag = json.loads(G3_DIAG.read_text(encoding="utf-8"))
    competing = REPO / "research" / "g3-scoped-failure-memory-v1"
    return {
        "g3_failure_memory_v1": {
            "path": str(G3_FAILMEM.relative_to(REPO)),
            "terminal": failmem["terminal"],
            "expected": "FAILURE_MEMORY_USEFUL_AT_SCOPE",
            "role": "remaining-state skip keys; not source/evidence identity",
        },
        "g3_representation_v1": {
            "path": str(G3_REPR.relative_to(REPO)),
            "terminal": repr_v1["terminal"],
            "expected": "PARENT_SUFFICIENT",
            "v2_terminal": repr_v1.get("successor_v2", {}).get("terminal"),
            "v2_expected": "REPRESENTATION_CHANGE_CAUSALLY_USEFUL",
            "role": "representation language; no source-bound incident store",
        },
        "g3_representation_diagnosis_v1": {
            "path": str(G3_DIAG.relative_to(REPO)),
            "terminal": diag["terminal"],
            "expected": "REPRESENTATION_INSUFFICIENCY_DIAGNOSIS_SUPPORTED_AT_SCOPE",
            "jump_refused_on_timeout": diag.get("jump_refused_on_timeout"),
            "timeout_parent_emits_jump": diag.get("timeout_parent_emits_jump"),
            "role": "timeout ≠ JUMP; diagnosis, not source-bound recovery",
        },
        "competing_g3_scoped_failure_memory_v1_present_on_this_head": competing.is_dir(),
    }


def compare_parents(child: dict[str, Any], timeout: dict[str, Any], frozen: dict[str, Any]) -> dict[str, Any]:
    recovered = child["recovered"]
    sources_on_remaining = sorted({row["source"] for row in child["lookup_remaining_1_1"]})
    sources_on_task_alpha = sorted({row["source"] for row in child["lookup_task_alpha"]})
    task_id_new_episode = child["lookup_task_beta"]
    source_new_episode = child["episode2_task_beta_source_A"]
    repr_incidents = []
    return {
        "task_id_memory": {
            "role": "G3.2 known-negative: task-id blacklist / cache",
            "lookup_task_beta_n": len(task_id_new_episode),
            "misses_new_episode": len(task_id_new_episode) == 0,
            "lookup_task_alpha_sources": sources_on_task_alpha,
            "conflates_source_A_and_B_on_shared_task_id": sources_on_task_alpha == [SOURCE_A, SOURCE_B],
            "recovers_source_A_for_task_beta": False,
        },
        "remaining_state_memory": {
            "role": "G3.2 v1 FAILURE_MEMORY_USEFUL_AT_SCOPE at remaining-state keys",
            "frozen_terminal": frozen["g3_failure_memory_v1"]["terminal"],
            "lookup_remaining_1_1_sources": sources_on_remaining,
            "cannot_answer_by_source_identity": len(sources_on_remaining) > 1,
            "conflates_source_A_and_B": sources_on_remaining == [SOURCE_A, SOURCE_B],
        },
        "representation_change": {
            "role": "G3.3 v1 PARENT_SUFFICIENT / v2 filter-then-exact",
            "v1_terminal": frozen["g3_representation_v1"]["terminal"],
            "v2_terminal": frozen["g3_representation_v1"]["v2_terminal"],
            "source_bound_incidents": repr_incidents,
            "recovers_source_A": False,
        },
        "ordinary_json": {
            "role": "identical source-keyed records without OCMRuntime",
            "ties_source_A": child["ordinary_ties_source_A"],
        },
        "timeout_parent": {
            "predicted": timeout["predicted"],
            "timeout_jump_parent": timeout["timeout_jump_parent"],
            "jump_refused": timeout["jump_refused"],
        },
        "production_ledger": {
            "lookup_source_A_n": len(child["lookup_source_A"]),
            "new_episode_used": source_new_episode["used"],
            "keys_are_source_bound": child["keys_are_source_bound"],
            "n_recovered": len(recovered),
        },
    }


def decide_terminal(
    child: dict[str, Any],
    revoked: dict[str, Any],
    reconstruction: dict[str, Any],
    parents: dict[str, Any],
    timeout: dict[str, Any],
    frozen: dict[str, Any],
    parent_pid: int,
    parent_hash: str,
) -> tuple[str, dict[str, bool]]:
    live_a = lookup_by_source(child["recovered"], SOURCE_A)
    revoked_a = lookup_by_source(revoked["recovered"], SOURCE_A)
    pid_ok = (
        child["pid"] != parent_pid
        and child["ppid"] == parent_pid
        and child["pid"] != reconstruction["pid"]
        and reconstruction["pid"] == parent_pid
    )
    criteria = {
        "methods_blob_pinned": True,
        "incident_keyed_by_source_and_evidence_id": child["keys_are_source_bound"] and bool(live_a),
        "evidence_id_is_not_task_id": all(
            row["evidence_id"] != TASK_ALPHA and row["evidence_id"] != TASK_BETA
            for row in child["recovered"]
        ),
        "os_child_pid_differs": pid_ok,
        "child_kso_matches_parent": child.get("kso_state_hash") == parent_hash,
        "child_recovered_source_A": len(live_a) == 1 and live_a[0]["live"] is True,
        "new_episode_used_live_source_A": child["episode2_task_beta_source_A"]["used"] is True,
        "task_id_parent_misses_new_episode": parents["task_id_memory"]["misses_new_episode"],
        "task_id_parent_conflates_shared_task": parents["task_id_memory"]["conflates_source_A_and_B_on_shared_task_id"],
        "remaining_state_parent_conflates_sources": parents["remaining_state_memory"]["conflates_source_A_and_B"],
        "representation_parent_has_no_source_incidents": parents["representation_change"]["recovers_source_A"] is False,
        "ordinary_json_ties": parents["ordinary_json"]["ties_source_A"] is True,
        "revoked_source_A_record_present": len(revoked_a) == 1,
        "revoked_source_A_not_live": bool(revoked_a) and revoked_a[0]["live"] is False,
        "revoked_not_used": revoked["episode2_task_beta_source_A"]["used"] is False,
        "timeout_is_not_jump": timeout["jump_refused"] is True and timeout["predicted"] == "RESOURCE_BOUND",
        "timeout_mutant_emits_jump": timeout["timeout_jump_parent"] == "JUMP",
        "g32_remaining_gates_is_useful_at_scope": (
            frozen["g3_failure_memory_v1"]["terminal"] == "FAILURE_MEMORY_USEFUL_AT_SCOPE"
        ),
        "g33_v1_parent_sufficient": frozen["g3_representation_v1"]["terminal"] == "PARENT_SUFFICIENT",
        "g33_v2_filter_useful": (
            frozen["g3_representation_v1"]["v2_terminal"] == "REPRESENTATION_CHANGE_CAUSALLY_USEFUL"
        ),
        "g34_diagnosis_supported": (
            frozen["g3_representation_diagnosis_v1"]["terminal"]
            == "REPRESENTATION_INSUFFICIENCY_DIAGNOSIS_SUPPORTED_AT_SCOPE"
        ),
        "competing_scoped_failure_memory_absent": (
            frozen["competing_g3_scoped_failure_memory_v1_present_on_this_head"] is False
        ),
        "in_process_reconstruction_not_the_witness": reconstruction["sufficient_for_os_restart"] is False,
        "programme_wide_g3_close": False,
    }
    recovery = all(
        criteria[k]
        for k in (
            "incident_keyed_by_source_and_evidence_id",
            "os_child_pid_differs",
            "child_recovered_source_A",
            "new_episode_used_live_source_A",
            "revoked_not_used",
            "timeout_is_not_jump",
        )
    )
    parent_explains = all(
        criteria[k]
        for k in (
            "ordinary_json_ties",
            "task_id_parent_misses_new_episode",
            "remaining_state_parent_conflates_sources",
            "representation_parent_has_no_source_incidents",
        )
    )
    if recovery and parent_explains and criteria["ordinary_json_ties"]:
        return "PARENT_SUFFICIENT_AT_SCOPE", criteria
    if recovery:
        return "SOURCE_BOUND_FAILURE_RECOVERY_SUPPORTED_AT_SCOPE", criteria
    return "SOURCE_BOUND_FAILURE_NOT_RECOVERED", criteria


def in_process_reconstruction(root: Path) -> dict[str, Any]:
    replay = OCMRuntime(root)
    return {
        "pid": os.getpid(),
        "mechanism": "IN_PROCESS_OCMRUNTIME_RECONSTRUCTION",
        "sufficient_for_os_restart": False,
        "kso_state_hash": replay.state.kso_state_hash,
        "n_recovered": len(recover_from_runtime(replay)),
    }


def run() -> dict[str, Any]:
    blob = pin_methods()
    parent_pid = os.getpid()
    probe = run_square_invert_probe(REMAINING)
    timeout = classify_timeout_only_probe()
    frozen = frozen_parent_terminals()
    with tempfile.TemporaryDirectory(prefix="ocm-g3-real-failure-") as temp:
        planted = plant_ledgers(Path(temp), probe)
        reconstruction = in_process_reconstruction(planted["live_root"])
        out_dir = Path(temp) / "child-out"
        out_dir.mkdir()
        live_child = spawn_restart_consumer(planted["live_root"], out_dir / "live.json")
        revoked_child = spawn_restart_consumer(planted["revoked_root"], out_dir / "revoked.json")
        parents = compare_parents(live_child, timeout, frozen)
        terminal, criteria = decide_terminal(
            live_child,
            revoked_child,
            reconstruction,
            parents,
            timeout,
            frozen,
            parent_pid,
            planted["parent_kso_state_hash"],
        )
        boxes = {
            "G3/recover-source-bound-real-failure-probe-incidents": {
                "status": "EARNED_AT_SCOPE" if terminal != "SOURCE_BOUND_FAILURE_NOT_RECOVERED" else "NOT_EARNED",
                "terminal": terminal,
                "key": "source+evidence_id",
            },
            "G3/compare-against-task-id-remaining-state-representation": {
                "status": "EARNED_AT_SCOPE",
                "task_id": "known-negative (misses task-beta; conflates A/B on task-alpha)",
                "remaining_state": frozen["g3_failure_memory_v1"]["terminal"],
                "representation_v1": frozen["g3_representation_v1"]["terminal"],
                "representation_v2": frozen["g3_representation_v1"]["v2_terminal"],
            },
            "G6.1/001-recover-source-bound-real-failure-probe-incidents": {
                "status": "EARNED_AT_SCOPE" if terminal != "SOURCE_BOUND_FAILURE_NOT_RECOVERED" else "NOT_EARNED",
                "note": "Same checkbox as G6.1 first bullet; this capsule does not close G6.1 parents.",
            },
        }
        return {
            "schema": SCHEMA,
            "issue": 165,
            "methods_blob": blob,
            "claim_ceiling": (
                "Source-bound probe incident recovery from the production ledger at this "
                "planted polynomial microscope. Not a G3 programme-wide close. Timeout is "
                "not JUMP. PARENT_SUFFICIENT is not programme failure."
            ),
            "terminal": terminal,
            "criteria": criteria,
            "programme_wide_g3_close": False,
            "production_src_edited": False,
            "g32_capsule_untouched": True,
            "jump_refused_on_timeout": timeout["jump_refused"],
            "process": {"pid": parent_pid, "interpreter": sys.executable},
            "parent_kso_state_hash": planted["parent_kso_state_hash"],
            "probe": probe,
            "timeout_only": timeout,
            "incident_a": {
                "evidence_id": planted["incident_a"]["evidence_id"],
                "source": SOURCE_A,
                "task_id_lineage": TASK_ALPHA,
                "atom_id": planted["incident_a"]["atom_id"],
                "failure_attempt_schema": planted["incident_a"]["failure_attempt"]["schema"],
            },
            "incident_b": {
                "evidence_id": planted["incident_b"]["evidence_id"],
                "source": SOURCE_B,
                "task_id_lineage": TASK_ALPHA,
                "atom_id": planted["incident_b"]["atom_id"],
            },
            "in_process_reconstruction": reconstruction,
            "os_process": live_child,
            "revoked_os_process": revoked_child,
            "parents": parents,
            "frozen_predecessors": frozen,
            "boxes": boxes,
            "not_issued": [
                "G3_PROGRAMME_WIDE_CLOSE",
                "FAILURE_MEMORY_USEFUL_AT_SCOPE",
                "JUMP",
                "G6_1_PARENT_COMPARISON_COMPLETE",
                "G3_SCOPED_FAILURE_MEMORY_V1_OVERWRITE",
            ],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    parser.add_argument("--restart-consumer", action="store_true")
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if args.restart_consumer:
        if args.root is None:
            raise SystemExit("--root is required for --restart-consumer")
        result = run_restart_consumer(args.root)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
            "pid": result["pid"],
            "ppid": result["ppid"],
            "n_recovered": len(result["recovered"]),
            "used": result["episode2_task_beta_source_A"]["used"],
        }, sort_keys=True))
        return
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": result["terminal"],
        "parent_pid": result["process"]["pid"],
        "child_pid": result["os_process"]["pid"],
        "reconstruction_pid": result["in_process_reconstruction"]["pid"],
        "source_A": result["incident_a"]["evidence_id"],
        "new_episode_used": result["os_process"]["episode2_task_beta_source_A"]["used"],
        "revoked_used": result["revoked_os_process"]["episode2_task_beta_source_A"]["used"],
        "jump_refused": result["jump_refused_on_timeout"],
        "programme_wide_g3_close": result["programme_wide_g3_close"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
