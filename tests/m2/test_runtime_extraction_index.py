"""Opt-in extraction reaches the real solve while retaining the default oracle."""
from dataclasses import replace

import pytest

from ocm.kso import extraction as EX
from ocm.kso.extraction_index import ExtractionIndex
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.surprise import SurpriseModel
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.event import EventType


def _task():
    return SV.Task("t", (SV.QueryPart("use fact", "claim", ("q",)),), targets=("rule",))


def _ops(calls=None):
    def backend(value, name):
        def run(*args):
            if calls is not None:
                calls.append(name)
            return {"value": value}
        return run
    return (SV.OperatorSpec("z_first", "1", backend(42, "first"), ("fact", "rule"),
                            warrant=WP.of({"e:first"}), checker=lambda out: SV.Status.PASS),
            SV.OperatorSpec("a_second", "1", backend(99, "second"), ("fact", "rule"),
                            checker=lambda out: SV.Status.PASS))


def _runtime(path, exact_bound=0):
    cfg = SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED, exact_extraction_max_atoms=exact_bound)
    rt = OCMRuntime(path, config=cfg)
    rt.admit_object(Atom("q", "goal", quarantined=True), (), "INSTRUCTION")
    rt.admit_object(Atom("fact", "claim"), (Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),), "INSTRUCTION")
    rt.admit_object(Atom("rule", "procedure"), (Hyperedge("fr", ("fact",), ("rule",), "DEPENDENCE"),), "INSTRUCTION")
    return rt


def _semantic(outcome):
    data = outcome.as_dict()
    for stage in data["trace"]["stages"]:
        stage["payload"].pop("indexed_extraction", None)
    return data


def _extraction(outcome):
    return next(stage for stage in outcome.trace.stages if stage.stage is SV.Stage.EXTRACTION)


@pytest.mark.parametrize("bound", (0, 12))
@pytest.mark.parametrize("revoked", ((), ("e:first",), ("e:fact",)))
def test_default_and_indexed_solve_preserve_all_semantic_trace_fields(bound, revoked):
    ks = KnowledgeSpace((Atom("q", "query_seed"), Atom("fact", "claim", WP.of({"e:fact"})),
                         Atom("rule", "procedure")),
                        (Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),
                         Hyperedge("fr", ("fact",), ("rule",), "DEPENDENCE")))
    cfg = SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED, exact_extraction_max_atoms=bound)
    ops = _ops()
    reference = SV.solve(ks, _task(), ops, revoked=revoked, config=cfg)
    indexed = SV.solve(ks, _task(), ops, revoked=revoked, config=cfg, extraction_index=ExtractionIndex(ks))
    assert _semantic(indexed) == _semantic(reference)
    assert SV.committed(indexed) == SV.committed(reference)
    assert "indexed_extraction" not in _extraction(reference).payload
    report = _extraction(indexed).payload["indexed_extraction"]
    assert report["global_preparation"]["prize_entries_materialized"] == len(ks.ids)
    assert report["global_preparation"]["optimizer_seed_entries_examined"] == len(ks.ids)
    for mode in ("warranted_reaction", "exploratory_reaction"):
        assert report["query_work"][mode]["dense_seed_entries_examined"] == len(ks.ids)
    if not revoked:
        assert report["global_preparation"]["exact_optimizer_universe_entries_examined"] == len(ks.ids)
        assert bool(report["global_preparation"]["exact_optimizer_candidate_subsets"]) is (bound == 12)
        assert ("greedy_optimizer" in report["query_work"]) is (bound == 0)


def test_actual_runtime_selected_path_forbids_incumbent_reaction_and_greedy(tmp_path, monkeypatch):
    rt = _runtime(tmp_path)
    index = ExtractionIndex(rt.state.ks)
    exact_calls, calls = [], []
    original_exact = EX.pcst_exact_bounded
    def exact(*args, **kwargs):
        exact_calls.append(kwargs["max_atoms"])
        return original_exact(*args, **kwargs)
    def forbidden(*args, **kwargs):
        raise AssertionError("incumbent extraction used by selected indexed path")
    monkeypatch.setattr(EX, "reacting_subgraph_from_surprise", forbidden)
    monkeypatch.setattr(EX, "pcst_greedy", forbidden)
    monkeypatch.setattr(EX, "pcst_exact_bounded", exact)
    result = rt.solve(_task(), _ops(calls), extraction_index=index)
    assert result.answer == {"value": 42} and SV.committed(result)
    assert calls == ["first", "second"] and exact_calls == [0]
    event = next(e for e in reversed(rt.events) if e.event_type is EventType.EXTRACTION)
    report = event.payload["payload"]["indexed_extraction"]
    assert set(report["query_work"]) == {"warranted_reaction", "exploratory_reaction", "greedy_optimizer"}


def test_reused_index_reports_caller_build_without_recurring_query_charge(tmp_path):
    rt = _runtime(tmp_path)
    index = ExtractionIndex(rt.state.ks)
    outcomes = [rt.solve(_task(), _ops(), extraction_index=index) for _ in range(2)]
    assert outcomes[0].trace.resources == outcomes[1].trace.resources
    for result in outcomes:
        report = _extraction(result).payload["indexed_extraction"]
        preparation = report["index_preparation"]
        assert preparation == {"accounting": "CALLER_OWNED", "charged_in_query": False,
                               "build_work": dict(index.build_work)}
        assert all(not work["cold_build_work"] for work in report["query_work"].values())
        assert report["complete_runtime_scaling"] == "NOT_ESTABLISHED"


def test_actual_runtime_revocation_and_reinstatement_reuse_same_snapshot(tmp_path):
    rt = _runtime(tmp_path)
    index = ExtractionIndex(rt.state.ks)
    assert rt.solve(_task(), _ops(), extraction_index=index).answer == {"value": 42}
    rt.revoke(("e:first",))
    assert rt.solve(_task(), _ops(), extraction_index=index).answer == {"value": 99}
    rt.reinstate(("e:first",))
    assert rt.solve(_task(), _ops(), extraction_index=index).answer == {"value": 42}


def test_stale_snapshot_refuses_before_navigation_backend_or_commit(tmp_path, monkeypatch):
    rt = _runtime(tmp_path)
    index = ExtractionIndex(rt.state.ks)
    rt.admit_object(Atom("extra", "claim"), (Hyperedge("qe", ("q",), ("extra",), "SUPPORT"),), "INSTRUCTION")
    calls = []
    def forbidden(*args, **kwargs):
        raise AssertionError("stale index must be refused before navigation")
    monkeypatch.setattr(SV, "navigate_stage", forbidden)
    result = rt.solve(_task(), _ops(calls), extraction_index=index)
    assert result.decision is SV.Decision.CANNOT_CHECK and not SV.committed(result)
    assert not calls and result.answer is None
    assert _extraction(result).reason == "EXTRACTION_INDEX_SNAPSHOT_MISMATCH"
    assert not any(s.stage in (SV.Stage.COMPOSITION, SV.Stage.CHECK) for s in result.trace.stages)


def test_restart_requires_rebinding_index_to_replayed_space(tmp_path):
    rt = _runtime(tmp_path)
    old_index = ExtractionIndex(rt.state.ks)
    assert SV.committed(rt.solve(_task(), _ops(), extraction_index=old_index))
    rt.persist()
    restarted = OCMRuntime(tmp_path, config=rt.config)
    refused = restarted.solve(_task(), _ops(), extraction_index=old_index)
    assert refused.decision is SV.Decision.CANNOT_CHECK and not SV.committed(refused)
    fresh_index = ExtractionIndex(restarted.state.ks)
    result = restarted.solve(_task(), _ops(), extraction_index=fresh_index)
    assert result.answer == {"value": 42} and SV.committed(result)


def test_direct_extraction_stage_stale_snapshot_is_cannot_check():
    ks = KnowledgeSpace((Atom("q", "query_seed"),), ())
    index = ExtractionIndex(ks)
    stage, output = SV.extract_stage(replace(ks), (), {}, SV.SolveConfig(), (), extraction_index=index)
    assert stage.status is SV.Status.CANNOT_CHECK and output == {}
