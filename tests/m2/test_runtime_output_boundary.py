"""Delayed candidate methods must remain inside the runtime state boundary."""
from collections.abc import Mapping
import pytest
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.surprise import SurpriseModel
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime


def setup(path):
    rt = OCMRuntime(path, config=SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED))
    rt.admit_object(Atom("q", "goal", quarantined=True), (), "INSTRUCTION")
    rt.admit_object(Atom("fact", "claim", WP.of({"support"})),
                    (Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),), "INSTRUCTION")
    return rt, SV.Task("delayed", (SV.QueryPart("fact", "claim", ("q",)),), targets=("fact",))


def run(rt, task, backend, checker=lambda out: SV.Status.PASS):
    return rt.solve(task, (SV.OperatorSpec("answer", "1", backend, ("fact",), checker=checker),))


def test_dict_subclass_contains_cannot_revoke_between_guards(tmp_path):
    rt, task = setup(tmp_path)
    class Delayed(dict):
        def __contains__(self, key):
            rt.revoke(("support",))
            return super().__contains__(key)
    out = run(rt, task, lambda *a: Delayed(answer=42))
    assert out.decision is SV.Decision.CANNOT_CHECK
    assert not SV.committed(out) and out.answer is None
    assert "support" in OCMRuntime(tmp_path).state.revoked


@pytest.mark.parametrize("method", ["items", "getitem", "nested"])
@pytest.mark.parametrize("raise_after", [False, True])
def test_delayed_mapping_consumption_cannot_commit(tmp_path, method, raise_after):
    rt, task = setup(tmp_path)
    def mutate():
        rt.revoke(("support",))
        if raise_after:
            raise ValueError("after revocation")
    class Delayed(Mapping):
        def __iter__(self):
            return iter(("answer",))
        def __len__(self):
            return 1
        def __contains__(self, key):
            return key == "answer"
        def __getitem__(self, key):
            if method in ("getitem", "nested"):
                mutate()
            return 42
        def items(self):
            if method == "items":
                mutate()
            return super().items()
    value = {"nested": [Delayed()]} if method == "nested" else Delayed()
    out = run(rt, task, lambda *a: value)
    assert out.decision is SV.Decision.CANNOT_CHECK
    assert not SV.committed(out) and out.answer is None
    assert "support" in rt.state.revoked


def test_solve_wide_checkpoint_invalidates_late_transition(tmp_path, monkeypatch):
    rt, task = setup(tmp_path)
    original = SV.decide
    def late(*args):
        result = original(*args)
        rt.revoke(("support",))
        return result
    monkeypatch.setattr(SV, "decide", late)
    out = run(rt, task, lambda *a: {"answer": 42})
    assert out.decision is SV.Decision.CANNOT_CHECK
    assert not SV.committed(out) and out.answer is None and out.candidate is None
    assert not any(s.stage is SV.Stage.CHECK and s.status is SV.Status.PASS for s in out.trace.stages)


def test_checker_cannot_change_candidate_then_approve_it(tmp_path):
    rt, task = setup(tmp_path)
    def checker(value):
        value["answer"][0] = 999
        return SV.Status.PASS
    out = run(rt, task, lambda *a: {"answer": [42]}, checker)
    assert out.decision is SV.Decision.CANNOT_CHECK and not SV.committed(out)


def test_plain_nested_payload_and_mapping_materialization_keep_semantics(tmp_path):
    rt, task = setup(tmp_path)
    expected = {"answer": [42, True, None], "program": ("add", 1), "metrics": {"wall": 0.25}}
    class Plain(Mapping):
        def __iter__(self):
            return iter(expected)
        def __len__(self):
            return len(expected)
        def __getitem__(self, key):
            return expected[key]
    seen = []
    def checker(value):
        assert type(value) is dict and type(value["answer"]) is list
        assert type(value["program"]) is tuple and type(value["answer"][0]) is int
        seen.append(value)
        return SV.Status.PASS
    out = run(rt, task, lambda *a: Plain(), checker)
    assert SV.committed(out) and out.answer == expected
    seen[0]["answer"][0] = 999
    assert out.answer == expected  # checker-owned references are detached
    assert out.answer["answer"][0] == expected["answer"][0] == 42
    guard = out.trace.stages[0].payload["runtime_callback_guard"]
    assert guard["checkpoint_reads"] == 4 and guard["solve_checkpoint_reads"] == 2


@pytest.mark.parametrize("value", [object(), {1: "not a string key"}])
def test_opaque_candidate_data_fails_closed(tmp_path, value):
    rt, task = setup(tmp_path)
    out = run(rt, task, lambda *a: {"answer": value})
    assert out.decision is SV.Decision.CANNOT_CHECK and not SV.committed(out)


def test_cyclic_candidate_data_fails_closed(tmp_path):
    rt, task = setup(tmp_path)
    value = []
    value.append(value)
    out = run(rt, task, lambda *a: {"answer": value})
    assert out.decision is SV.Decision.CANNOT_CHECK and not SV.committed(out)


def test_checker_bool_int_coercion_is_a_changed_candidate(tmp_path):
    rt, task = setup(tmp_path)
    def checker(value):
        value["answer"] = True
        return SV.Status.PASS
    out = run(rt, task, lambda *a: {"answer": 1}, checker)
    assert out.decision is SV.Decision.CANNOT_CHECK and not SV.committed(out)


def test_opaque_exception_diagnostic_cannot_execute_after_guard(tmp_path):
    rt, task = setup(tmp_path)
    class DelayedError(ValueError):
        def __str__(self):
            rt.revoke(("support",))
            raise ValueError("diagnostic code must not run")
    def backend(*args):
        raise DelayedError()
    out = run(rt, task, backend)
    assert not SV.committed(out) and out.answer is None
    assert "support" not in rt.state.revoked
