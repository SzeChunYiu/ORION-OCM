"""Host callbacks must not certify candidates across runtime state transitions."""
import pytest

from ocm.kso.space import Atom, Hyperedge
from ocm.kso.surprise import SurpriseModel
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.event import EventStatus, EventType


def runtime(path):
    rt = OCMRuntime(path, config=SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED))
    rt.admit_object(Atom("q", "goal", quarantined=True), (), "INSTRUCTION")
    rt.admit_object(Atom("fact", "claim", WP.of({"support"})),
                    (Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),), "INSTRUCTION")
    task = SV.Task("pure", (SV.QueryPart("use fact", "claim", ("q",)),), targets=("fact",))
    return rt, task


@pytest.mark.parametrize("callback", ("backend", "checker"))
def test_revocation_inside_actual_runtime_callback_cannot_commit(tmp_path, callback):
    rt, task = runtime(tmp_path)
    def backend(*args):
        if callback == "backend":
            rt.revoke(("support",))
        return {"answer": 42}
    def checker(out):
        if callback == "checker":
            rt.revoke(("support",))
        return SV.Status.PASS
    op = SV.OperatorSpec("answer", "1", backend, ("fact",), checker=checker)
    result = rt.solve(task, (op,))
    assert result.decision is SV.Decision.CANNOT_CHECK
    assert not SV.committed(result) and result.answer is None and result.candidate is None
    assert "support" in rt.state.revoked
    assert not any(s.stage in (SV.Stage.CHECK, SV.Stage.DECISION, SV.Stage.COMMITMENT)
                   and s.status is SV.Status.PASS for s in result.trace.stages)
    assert not any(e.event_type is EventType.CHECKER_RESULT and e.status is EventStatus.PASS
                   for e in rt.events)
    assert "support" in OCMRuntime(tmp_path, config=rt.config).state.revoked


@pytest.mark.parametrize("callback", ("backend", "checker"))
@pytest.mark.parametrize("mutation", ("field", "evidence", "registry_rebind", "audit_write", "revoke_then_raise"))
def test_all_runtime_epochs_and_exception_paths_abort(tmp_path, callback, mutation):
    from dataclasses import replace
    from ocm.operators.registry import BackendKind, OperatorSpec
    rt, task = runtime(tmp_path)
    registered = OperatorSpec("host", "1", BackendKind.PROGRAMMATIC, lambda *a: {}, ("fact",))
    rt.register_operator(registered)
    calls = []
    def mutate():
        if mutation == "field":
            rt.admit_object(Atom("new", "claim"), (Hyperedge("fn", ("fact",), ("new",), "SUPPORT"),), "INSTRUCTION")
        elif mutation == "evidence":
            rt.admit_evidence("new evidence", "instruction", "host")
        elif mutation == "audit_write":
            before = rt._solve_epochs
            rt.persist()
            assert rt._solve_epochs == before  # Callback-local event position must catch this.
        elif mutation == "registry_rebind":
            before = len(rt.events)
            rt.register_operator(replace(registered, backend=lambda *a: {"new": True}))
            assert len(rt.events) == before  # Same manifest: registry epoch must catch this.
        else:
            rt.revoke(("support",))
            raise RuntimeError("callback failed after withdrawal")
    def backend(*args):
        calls.append("backend")
        if callback == "backend":
            mutate()
        return {"answer": 42}
    def checker(out):
        calls.append("checker")
        if callback == "checker":
            mutate()
        return SV.Status.PASS
    op = SV.OperatorSpec("answer", "1", backend, ("fact",), checker=checker)
    out = rt.solve(task, (op,))
    assert out.decision is SV.Decision.CANNOT_CHECK and not SV.committed(out)
    assert out.candidate is None and out.answer is None
    assert calls == (["backend"] if callback == "backend" else ["backend", "checker"])
    assert any(s.reason == callback.upper()+"_RUNTIME_STATE_CHANGED" for s in out.trace.stages)


def test_later_checker_mutation_invalidates_earlier_pass_and_stops_callbacks(tmp_path):
    rt, task = runtime(tmp_path)
    called = []
    def checker(name):
        def run(out):
            called.append(name)
            if name == "second":
                rt.revoke(("support",))
            return SV.Status.PASS
        return run
    ops = tuple(SV.OperatorSpec(name, "1", lambda *a: {"answer": 42}, ("fact",), checker=checker(name))
                for name in ("first", "second", "third"))
    out = rt.solve(task, ops)
    check = next(s for s in out.trace.stages if s.stage is SV.Stage.CHECK)
    assert check.payload["verdicts"] == {"first": "CANNOT_CHECK", "second": "CANNOT_CHECK"}
    assert called == ["first", "second"]
    assert out.decision is SV.Decision.CANNOT_CHECK and not SV.committed(out)


def test_pure_callbacks_keep_query_audits_and_index_locality(tmp_path, monkeypatch):
    from ocm.runtime.operator_index import SolveOperatorIndex
    from ocm.runtime.ocm_runtime import RuntimeState
    from ocm.kso.extraction_index import ExtractionIndex
    rt, task = runtime(tmp_path)
    calls = []
    def backend(*args):
        calls.append("backend")
        assert rt.trace()[-1]["event_type"] == EventType.QUERY_OPENED.value
        return {"answer": 42}
    def checker(out):
        calls.append("checker")
        return SV.Status.PASS
    ops = (SV.OperatorSpec("answer", "1", backend, ("fact",), checker=checker),
           *(SV.OperatorSpec(str(i), "1", lambda *a: {}, (f"absent:{i}",)) for i in range(1000)))
    index = SolveOperatorIndex(ops)
    def forbidden(*args):
        raise AssertionError("full catalogue traversal or state digest inside callback guard")
    monkeypatch.setattr(SolveOperatorIndex, "__iter__", forbidden)
    original_checkpoint = rt._solve_callback_checkpoint
    def checkpoint():
        with monkeypatch.context() as patch:
            for prop in ("kso_state_hash", "registry_revision", "evidence_epoch"):
                patch.setattr(RuntimeState, prop, property(forbidden))
            return original_checkpoint()
    monkeypatch.setattr(rt, "_solve_callback_checkpoint", checkpoint)
    extraction = ExtractionIndex(rt.state.ks)
    for _ in range(2):
        before = len(rt.events)
        out = rt.solve(task, index, extraction_index=extraction)
        assert out.decision is SV.Decision.ANSWER and SV.committed(out)
        assert out.answer == {"answer": 42}
        composition = next(s for s in out.trace.stages if s.stage is SV.Stage.COMPOSITION)
        assert composition.payload["operator_selection"]["operators_considered"] == 1
        guard = out.trace.stages[0].payload["runtime_callback_guard"]
        assert guard["callbacks"] == 2 and guard["checkpoint_reads"] == 4
        assert guard["full_state_hashes"] == guard["full_catalogue_traversals"] == 0
        assert [e.event_type for e in rt.events[before:]] == [EventType.QUERY_OPENED, EventType.NAVIGATION,
            EventType.EXTRACTION, EventType.CANDIDATE_COMPOSED, EventType.CHECKER_RESULT]
    assert calls == ["backend", "checker", "backend", "checker"]
