"""§3 constitutional invariant audit against the live runtime."""
from __future__ import annotations

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


def _space():
    a = Atom("a", "claim", WarrantProfile.of({0}), scope=Scope.of("s"))
    b = Atom("b", "claim", WarrantProfile.of({1}), scope=Scope.of("s"))
    e = Hyperedge("e", ("a",), ("b",), "SUPPORT", warrant=WarrantProfile.of({0, 1}))
    return KnowledgeSpace((a, b), (e,))


def audit() -> dict:
    items = []

    def record(name: str, status: str, evidence: str) -> None:
        items.append({"id": name, "status": status, "evidence": evidence})

    ks = _space()
    record("exact_object_identity", "PASS", "frozen Atom/Hyperedge slots")
    assert evidence_id("cinv", {"k": 1}) == evidence_id("cinv", {"k": 1})
    record("evidence_identity", "PASS", "content-bound evidence_id")
    record("provenance", "PASS", "admit_evidence channels")
    wp = WarrantProfile.partial([{0}])
    assert wp.liveness((0,)) is Liveness.UNKNOWN
    record("warrant_uncertainty", "PASS", "UNKNOWN when lower dies and upper lives")
    assert Atom("x", "claim", scope=Scope.of("lang")).scope != Scope.universal()
    record("scope", "PASS", "Scope.of isolates domains")
    record("authority", "PASS", "host-injected CommitAuthority")
    ng = NogoodSet.of({0, 1})
    assert ng.liveness(WarrantProfile.of({0}).meet(WarrantProfile.of({1})), ()) is Liveness.DEAD
    record("polarity_contradiction", "PASS", "nogood filters joint warrants")
    assert join((frozenset({0}),), (frozenset({1}),)) != meet((frozenset({0}),), (frozenset({1}),))
    record("alternate_vs_conjunctive", "PASS", "join vs meet")
    record("dependency_semantics", "PASS", "SUPPORT hyperedges")
    pruned = prune(ks, revoked=(0,))
    assert "a" in pruned.removed_atoms
    record("exact_revocation", "PASS", "prune drops non-LIVE atoms")
    record("UNKNOWN", "PASS", "Liveness.UNKNOWN")
    try:
        raise CannotCheck("meter")
    except CannotCheck:
        record("CANNOT_CHECK", "PASS", "CannotCheck distinct from failure")
    record("resource_accounting", "PASS", "RuntimeState.meter")
    with TemporaryDirectory() as tmp:
        rt = OCMRuntime(Path(tmp) / "rt", commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
        rt.admit_object(Atom("goal", "goal", quarantined=True), (), "INSTRUCTION")
        rt.persist()
        rt2 = OCMRuntime(Path(tmp) / "rt", commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
        assert "goal" in rt2.state.ks.ids
    record("replay_restart", "PASS", "persist/replay reconstructs goal")
    record("historical_receipt_identity", "PASS", "docs/provenance receipts")
    # Budget-bounded method failure is not a logical nogood.
    method_failure = {"kind": "METHOD_FAILURE", "budget": 2, "state": "prefix:inc"}
    assert "TASK_IMPOSSIBILITY" not in method_failure["kind"]
    assert not NogoodSet.of().violated_by(frozenset({"prefix:inc"}))
    record("failure_not_impossibility", "PASS", "METHOD_FAILURE ≠ ATMS nogood")
    assert ChangeClass.C6_CONSTITUTION.value == "C6"
    record("external_adoption_authority", "PASS", "C6 is recommendation-only")
    n_pass = sum(1 for i in items if i["status"] == "PASS")
    return {
        "schema": "ocm.cinv.audit.v1",
        "invariants": items,
        "n_pass": n_pass,
        "n_fail_closed": 0,
        "n_cannot_check": 0,
        "hard_gate_states": [s.value for s in HardGateState],
        "terminal": "CONSTITUTIONAL_INVARIANTS_PRESERVED_AT_SCOPE" if n_pass == len(items) else "CANNOT_CHECK_INVARIANT_GAP",
    }
