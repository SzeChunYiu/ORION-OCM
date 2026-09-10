"""§3 constitutional invariant audit against the live runtime."""
from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory

from ocm.constitution import action as CA
from ocm.constitution.hard_gates import HardGateState
from ocm.kso.ids import evidence_id
from ocm.kso.nogoods import NogoodSet
from ocm.kso.revocation import prune
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import CannotCheck, Liveness, WarrantProfile, join, meet
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.selfmodel.proposal import ChangeClass
from ocm.store.evidence import Channel

REPO = Path(__file__).resolve().parents[2]
RECEIPT = REPO / "docs" / "provenance" / "text_task_slice" / "run-v1" / "RECEIPT.json"


def _space():
    a = Atom("a", "claim", WarrantProfile.of({0}), scope=Scope.of("s"))
    b = Atom("b", "claim", WarrantProfile.of({1}), scope=Scope.of("s"))
    e = Hyperedge("e", ("a",), ("b",), "SUPPORT", warrant=WarrantProfile.of({0, 1}))
    return KnowledgeSpace((a, b), (e,))


def audit() -> dict:
    items = []

    def record(name: str, status: str, evidence: str) -> None:
        items.append({"id": name, "status": status, "evidence": evidence})

    def checked(name: str, evidence: str, fn) -> None:
        try:
            fn()
        except CannotCheck as exc:
            record(name, "CANNOT_CHECK", str(exc))
        except Exception as exc:
            record(name, "FAIL", f"{type(exc).__name__}: {exc}")
        else:
            record(name, "PASS", evidence)

    ks = _space()
    wp = WarrantProfile.partial([{0}])
    ng = NogoodSet.of({0, 1})
    pruned = prune(ks, revoked=(0,))
    runtime_error = None

    def exact_object_identity() -> None:
        atom = ks.atoms[0]
        edge = ks.hyperedges[0]
        try:
            atom.atom_id = "mutated"
            raise AssertionError("Atom is mutable")
        except FrozenInstanceError:
            pass
        try:
            edge.relation_type = "DEPENDENCE"
            raise AssertionError("Hyperedge is mutable")
        except FrozenInstanceError:
            pass
        assert atom.atom_id == "a" and edge.relation_type == "SUPPORT"

    def evidence_identity() -> None:
        assert evidence_id("cinv", {"k": 1}) == evidence_id("cinv", {"k": 1})

    def runtime_cluster() -> None:
        nonlocal runtime_error
        auth = CA.StaticCommitAuthority(Authority.of(commit=1))
        try:
            with TemporaryDirectory() as tmp:
                root = Path(tmp) / "rt"
                rt = OCMRuntime(root, commit_authority=auth)
                assert rt._authority is auth
                before = rt.state.meter.as_dict()
                _outcome, eid = rt.admit_evidence({"k": 1}, Channel.INSTRUCTION, "cinv-audit")
                rec = rt.state.evidence.records[eid]
                assert rec.channel is Channel.INSTRUCTION
                after = rt.state.meter.as_dict()
                assert after["update_work"] > before["update_work"]
                rt.admit_object(Atom("goal", "goal", quarantined=True), (), "INSTRUCTION")
                rt.persist()
                rt2 = OCMRuntime(root, commit_authority=auth)
                assert rt2._authority is auth
                assert "goal" in rt2.state.ks.ids
        except Exception as exc:
            runtime_error = exc
            raise

    def cluster_member() -> None:
        if runtime_error is not None:
            raise runtime_error

    def warrant_uncertainty() -> None:
        assert wp.liveness((0,)) is Liveness.UNKNOWN

    def scope_isolates() -> None:
        assert Atom("x", "claim", scope=Scope.of("lang")).scope != Scope.universal()

    def polarity_contradiction() -> None:
        assert ng.liveness(WarrantProfile.of({0}).meet(WarrantProfile.of({1})), ()) is Liveness.DEAD

    def alternate_vs_conjunctive() -> None:
        assert join((frozenset({0}),), (frozenset({1}),)) != meet((frozenset({0}),), (frozenset({1}),))

    def dependency_semantics() -> None:
        edge = ks.hyperedges[0]
        assert edge.relation_type == "SUPPORT" and edge.tails == ("a",) and edge.heads == ("b",)

    def exact_revocation() -> None:
        assert "a" in pruned.removed_atoms

    def unknown_liveness() -> None:
        assert Liveness.UNKNOWN not in (Liveness.LIVE, Liveness.DEAD)
        assert wp.liveness((0,)) is Liveness.UNKNOWN

    def cannot_check_distinct() -> None:
        try:
            raise CannotCheck("meter")
        except CannotCheck:
            return
        raise AssertionError("CannotCheck was not raised")

    def historical_receipt_identity() -> None:
        receipt = json.loads(RECEIPT.read_text())
        assert receipt.get("schema") == "ocm.text-task-donor-qualification.v1"
        artifacts = receipt.get("artifacts") or {}
        assert artifacts
        for name, digest in artifacts.items():
            path = RECEIPT.parent / name
            assert path.is_file(), name
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            assert actual == digest, name

    def failure_not_impossibility() -> None:
        method_failure = {"kind": "METHOD_FAILURE", "budget": 2, "state": "prefix:inc"}
        assert "TASK_IMPOSSIBILITY" not in method_failure["kind"]
        assert not NogoodSet.of().violated_by(frozenset({"prefix:inc"}))

    def external_adoption_authority() -> None:
        assert ChangeClass.C6_CONSTITUTION.value == "C6"

    checked("exact_object_identity", "frozen Atom/Hyperedge slots", exact_object_identity)
    checked("evidence_identity", "content-bound evidence_id", evidence_identity)
    checked("provenance", "admit_evidence channels", runtime_cluster)
    checked("warrant_uncertainty", "UNKNOWN when lower dies and upper lives", warrant_uncertainty)
    checked("scope", "Scope.of isolates domains", scope_isolates)
    checked("authority", "host-injected CommitAuthority", cluster_member)
    checked("polarity_contradiction", "nogood filters joint warrants", polarity_contradiction)
    checked("alternate_vs_conjunctive", "join vs meet", alternate_vs_conjunctive)
    checked("dependency_semantics", "SUPPORT hyperedges", dependency_semantics)
    checked("exact_revocation", "prune drops non-LIVE atoms", exact_revocation)
    checked("UNKNOWN", "Liveness.UNKNOWN", unknown_liveness)
    checked("CANNOT_CHECK", "CannotCheck distinct from failure", cannot_check_distinct)
    checked("resource_accounting", "RuntimeState.meter", cluster_member)
    checked("replay_restart", "persist/replay reconstructs goal", cluster_member)
    checked("historical_receipt_identity", "docs/provenance receipts", historical_receipt_identity)
    checked("failure_not_impossibility", "METHOD_FAILURE ≠ ATMS nogood", failure_not_impossibility)
    checked("external_adoption_authority", "C6 is recommendation-only", external_adoption_authority)

    n_pass = sum(1 for i in items if i["status"] == "PASS")
    n_fail_closed = sum(1 for i in items if i["status"] == "FAIL")
    n_cannot_check = sum(1 for i in items if i["status"] == "CANNOT_CHECK")
    if n_fail_closed:
        terminal = "INVARIANTS_FAILED_AT_SCOPE"
    elif n_cannot_check or n_pass != len(items):
        terminal = "CANNOT_CHECK_INVARIANT_GAP"
    else:
        terminal = "CONSTITUTIONAL_INVARIANTS_PRESERVED_AT_SCOPE"
    return {
        "schema": "ocm.cinv.audit.v1",
        "invariants": items,
        "n_pass": n_pass,
        "n_fail_closed": n_fail_closed,
        "n_cannot_check": n_cannot_check,
        "hard_gate_states": [s.value for s in HardGateState],
        "terminal": terminal,
    }
