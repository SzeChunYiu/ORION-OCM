"""Whole-batch publication and durable replay; no native proof execution."""
from dataclasses import replace
import json
import subprocess
import sys

import pytest

from ocm.kso.admission import CertificateKind
from ocm.kso.resources import ResourceVector
from ocm.kso.space import Atom, Hyperedge, TypedRejection
from ocm.kso.surprise import SurpriseModel
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime, RuntimeRefusal
from ocm.store.event import EventStatus, EventType
from ocm.store.ledger import StaleLedgerHead


def batch(prefix=""):
    a, p, c = (prefix + x for x in ("anchor", "proof", "claim"))
    w = WP.of({"checked-run", "checker-environment"})
    return ((Atom(a, "claim", w, quarantined=True), (), CertificateKind.EXACT_CHECKER),
            (Atom(p, "claim", w), (Hyperedge(prefix+"ap", (a,), (p,), "COMPOSITION", warrant=w,
              meta=(("route", "checked"),)),), "EXACT_CHECKER"),
            (Atom(c, "claim", w), (Hyperedge(prefix+"pc", (p,), (c,), "COMPOSITION", warrant=w),), "EXACT_CHECKER"))


def unchanged(rt):
    return (rt.state.snapshot(), dict(rt.state.certificates), rt._solve_epochs,
            rt.ledger.path.read_bytes(), tuple(e.event_hash for e in rt.events))


def test_whole_batch_one_event_and_fresh_process_replay(tmp_path):
    rt = OCMRuntime(tmp_path)
    receipts = rt.admit_batch(batch())
    assert tuple(r.atom_id for r in receipts) == ("anchor", "proof", "claim")
    assert len(rt.ledger.entries()) == len(rt.events) == 1
    event = rt.events[0]
    assert event.event_type is EventType.OBJECT_BATCH_ADMITTED
    assert event.payload["schema"] == "ocm.object-admission-batch.v1"
    assert event.output_object_ids == ("anchor", "proof", "ap", "claim", "pc")
    total = ResourceVector()
    for receipt in receipts: total = total + receipt.resources
    assert event.resources == rt.state.meter == total
    assert rt._solve_epochs == (1, 0, 0)
    assert dict(rt.state.ks.edge_view["ap"].meta) == {"route": "checked"}
    code = "from ocm.runtime.ocm_runtime import OCMRuntime; import json,sys; r=OCMRuntime(sys.argv[1]); print(json.dumps(r.state.snapshot()))"
    proc = subprocess.run([sys.executable, "-B", "-c", code, str(tmp_path)], text=True,
                          capture_output=True, timeout=20, check=True)
    assert json.loads(proc.stdout) == json.loads(json.dumps(rt.state.snapshot()))
    assert OCMRuntime(tmp_path).state.certificates == rt.state.certificates


@pytest.mark.parametrize("kind", ("duplicate_atom", "duplicate_edge", "scope", "warrant", "empty"))
def test_invalid_last_item_has_no_prefix_or_event(tmp_path, kind):
    rt = OCMRuntime(tmp_path)
    items = list(batch())
    atom, edges, cert = items[-1]
    if kind == "duplicate_atom": atom = replace(atom, atom_id="proof")
    elif kind == "duplicate_edge": edges = (replace(edges[0], edge_id="ap"),)
    elif kind == "scope":
        from ocm.kso.types import Scope
        atom = replace(atom, scope=Scope(frozenset()))
    elif kind == "warrant": atom = replace(atom, warrant=WP.of({"different"}))
    items[-1] = (atom, edges, cert)
    before = unchanged(rt)
    with pytest.raises((TypedRejection, RuntimeRefusal, ValueError)):
        rt.admit_batch([] if kind == "empty" else items)
    assert unchanged(rt) == before
    assert OCMRuntime(tmp_path).state.ks.ids == ()


def test_stale_ledger_refuses_without_partial_memory(tmp_path):
    stale = OCMRuntime(tmp_path)
    writer = OCMRuntime(tmp_path)
    writer.admit_object(Atom("other", "claim", quarantined=True), (), "INSTRUCTION")
    before = unchanged(stale)
    with pytest.raises(StaleLedgerHead): stale.admit_batch(batch())
    assert unchanged(stale) == before
    assert OCMRuntime(tmp_path).state.ks.ids == ("other",)


@pytest.mark.parametrize("after_write", (False, True))
def test_append_interruption_replays_all_or_none(tmp_path, monkeypatch, after_write):
    rt = OCMRuntime(tmp_path)
    original = rt.ledger.append
    def fail(*args, **kw):
        if after_write: original(*args, **kw)
        raise OSError("simulated append interruption")
    monkeypatch.setattr(rt.ledger, "append", fail)
    with pytest.raises(OSError): rt.admit_batch(batch())
    assert rt.state.ks.ids == () and rt.state.certificates == {} and rt.events == []
    restored = OCMRuntime(tmp_path)
    assert restored.state.ks.ids == (("anchor", "proof", "claim") if after_write else ())
    assert len(restored.events) == int(after_write)


@pytest.mark.parametrize("defect", ("schema", "empty", "last", "extra", "resource", "outputs", "evidence", "status"))
def test_malformed_batch_reducer_does_not_publish_prefix(tmp_path, defect):
    donor = OCMRuntime(tmp_path / "donor")
    donor.admit_batch(batch())
    ev = donor.events[0]
    payload = json.loads(json.dumps(ev.payload))
    changes = {"payload": payload, "event_hash": "", "event_id": ""}
    if defect == "schema": payload["schema"] = "unknown"
    elif defect == "empty": payload["items"] = []
    elif defect == "last": payload["items"][-1]["atom"]["warrant"] = WP.of({"wrong"}).as_dict()
    elif defect == "extra": payload["items"][-1]["unexpected"] = True
    elif defect == "resource": changes["resource_delta"] = ResourceVector().as_dict()
    elif defect == "outputs": changes["output_object_ids"] = ("anchor",)
    elif defect == "evidence": changes["evidence_ids"] = ()
    else: changes["status"] = EventStatus.FAIL
    bad = replace(ev, **changes)
    rt = OCMRuntime(tmp_path / "victim")
    before = unchanged(rt)
    with pytest.raises((RuntimeRefusal, TypedRejection, ValueError)): rt._apply(bad)
    assert unchanged(rt) == before
    rt.ledger.append("OCM_EVENT", bad.as_dict(), expected_head=None)
    with pytest.raises((RuntimeRefusal, TypedRejection, ValueError)): OCMRuntime(rt.root)


@pytest.mark.parametrize("where", ("backend", "checker"))
def test_batch_mutation_inside_solve_cannot_commit_answer(tmp_path, where):
    rt = OCMRuntime(tmp_path, config=SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED))
    rt.admit_object(Atom("q", "goal", quarantined=True), (), "INSTRUCTION")
    rt.admit_object(Atom("fact", "claim"), (Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),), "INSTRUCTION")
    def backend(*args):
        if where == "backend": rt.admit_batch(batch())
        return {"answer": 42}
    def checker(out):
        if where == "checker": rt.admit_batch(batch())
        return SV.Status.PASS
    op = SV.OperatorSpec("answer", "1", backend, ("fact",), checker=checker)
    out = rt.solve(SV.Task("q", (SV.QueryPart("use fact", "claim", ("q",)),), targets=("fact",)), (op,))
    assert out.decision is SV.Decision.CANNOT_CHECK and not SV.committed(out)
    assert out.answer is None and out.candidate is None
    assert set(("anchor", "proof", "claim")) <= set(OCMRuntime(tmp_path).state.ks.ids)


def test_post_append_reducer_failure_blocks_writes_until_verified_replay(tmp_path, monkeypatch):
    rt = OCMRuntime(tmp_path)
    original = rt._stage_admission_batch
    calls = []
    def interrupted(payload):
        calls.append(1)
        if len(calls) == 2: raise MemoryError("after durable append, before state publication")
        return original(payload)
    monkeypatch.setattr(rt, "_stage_admission_batch", interrupted)
    with pytest.raises(MemoryError): rt.admit_batch(batch())
    monkeypatch.setattr(rt, "_stage_admission_batch", original)
    assert rt.state.ks.ids == () and len(rt.ledger.entries()) == 1
    for write in (lambda: rt.admit_batch(batch("later:")),
                  lambda: rt.admit_evidence("unrelated", "instruction", "host")):
        with pytest.raises(RuntimeRefusal, match="REPLAY_REQUIRED"): write()
    assert len(rt.ledger.entries()) == 1
    def fail_replay(payload): raise MemoryError("replay still interrupted")
    monkeypatch.setattr(rt, "_stage_admission_batch", fail_replay)
    with pytest.raises(MemoryError): rt.replay()
    monkeypatch.setattr(rt, "_stage_admission_batch", original)
    with pytest.raises(RuntimeRefusal, match="REPLAY_REQUIRED"): rt.admit_batch(batch("later:"))
    rt.replay()
    assert rt.state.ks.ids == ("anchor", "proof", "claim")
    rt.admit_batch(batch("later:"))
    assert OCMRuntime(tmp_path).state.snapshot() == rt.state.snapshot()
