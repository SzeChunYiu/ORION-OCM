"""Exact catalogue pruning must affect the real solve without changing policy."""
from dataclasses import replace
from itertools import combinations

import pytest

from ocm.kso import extraction as EX
from ocm.kso import navigation as N
from ocm.kso import space as S
from ocm.kso.surprise import SurpriseModel
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime import solve as SV
from ocm.runtime.operator_index import SolveOperatorIndex
from ocm.runtime.ocm_runtime import OCMRuntime


def op(name, inputs, value=1, warrant=None):
    return SV.OperatorSpec(name, "1", lambda *a: {"value": value}, tuple(inputs),
                           warrant=warrant or WP.one(), checker=lambda out: SV.Status.PASS)


def space():
    return S.KnowledgeSpace(
        (S.Atom("q", "query_seed"), S.Atom("fact", "claim"), S.Atom("rule", "procedure")),
        (S.Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),
         S.Hyperedge("fr", ("fact",), ("rule",), "DEPENDENCE")))


def test_exact_selection_preserves_duplicates_zero_inputs_and_caller_order():
    ops = (op("z", ()), op("b", ("q", "fact")), op("a", ("rule",)),
           op("b", ("q", "fact"), 2), op("dup", ("q", "q")))
    index = SolveOperatorIndex(iter(ops))
    ids = ("q", "fact", "rule", "absent")
    for n in range(len(ids) + 1):
        for pool in combinations(ids, n):
            result = index.select(pool)
            assert result.operators == tuple(o for o in ops if set(o.input_atoms) <= set(pool))
    assert tuple(index) == ops and index[1:3] == ops[1:3]


def test_rare_anchor_avoids_visiting_common_input_postings():
    ops = tuple(op(str(i), ("common", f"key:{i}")) for i in range(10000))
    index = SolveOperatorIndex(ops)
    result = index.select(("common", "key:42"))
    assert result.operators == (ops[42],)
    assert result.work["index_probes"] == 2
    assert result.work["postings_examined"] == 1
    assert result.work["operators_considered"] == 1
    assert index.build_work["input_memberships"] == 20000
    assert index.build_work["catalogue_operators"] == 10000


def test_globally_applicable_catalogue_reports_global_work():
    index = SolveOperatorIndex(op(str(i), ()) for i in range(30))
    result = index.select(())
    assert len(result.operators) == 30
    assert result.work["operators_considered"] == 30


def test_index_rejects_mutable_input_contract():
    bad = replace(op("x", ("q",)), input_atoms=["q"])
    with pytest.raises(ValueError, match="IMMUTABLE_INPUT_CONTRACT_REQUIRED"):
        SolveOperatorIndex((bad,))


def test_compose_reads_index_without_iterating_full_catalogue(monkeypatch):
    ks = space()
    first, second = op("z_first", ("fact", "rule"), 42), op("a_second", ("fact",), 99)
    ops = (first, *(op(f"no:{i}", (f"missing:{i}",)) for i in range(1000)), second)
    index = SolveOperatorIndex(ops)
    def forbidden(*args):
        raise AssertionError("full catalogue or atom copy")
    monkeypatch.setattr(SolveOperatorIndex, "__iter__", forbidden)
    monkeypatch.setattr(S.KnowledgeSpace, "atom_map", forbidden)
    g = EX.ReactingSubgraph(frozenset(ks.ids), frozenset(e.edge_id for e in ks.hyperedges),
                            N.NavigationMode.WARRANTED, frozenset(("q",)))
    stage, candidates = SV.compose_stage(ks, index, g, ())
    assert [row[0] for row in candidates] == [first, second]
    assert stage.payload["operator_selection"]["operators_considered"] == 2
    assert stage.payload["operator_selection"]["catalogue_operators"] == 1002


def test_real_solve_keeps_first_passing_answer_and_checks_live_warrant():
    ks = space()
    task = SV.Task("t", (SV.QueryPart("use fact", "claim", ("q",)),), targets=("rule",))
    cfg = SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED)
    ops = (op("z_first", ("fact", "rule"), 42, WP.of({"e:first"})),
           op("a_second", ("fact", "rule"), 99))
    for revoked, expected in [((), 42), (("e:first",), 99)]:
        ref = SV.solve(ks, task, ops, revoked=revoked, config=cfg)
        got = SV.solve(ks, task, SolveOperatorIndex(ops), revoked=revoked, config=cfg)
        assert got.decision == ref.decision == SV.Decision.ANSWER
        assert got.answer == ref.answer == {"value": expected}
        assert SV.committed(got) == SV.committed(ref)


def test_runtime_consumes_index_and_rebinds_after_restart(tmp_path):
    cfg = SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED)
    runtime = OCMRuntime(tmp_path, config=cfg)
    runtime.admit_object(S.Atom("q", "goal", quarantined=True), (), "INSTRUCTION")
    runtime.admit_object(S.Atom("fact", "claim"), (S.Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),), "INSTRUCTION")
    runtime.admit_object(S.Atom("rule", "procedure"), (S.Hyperedge("fr", ("fact",), ("rule",), "DEPENDENCE"),), "INSTRUCTION")
    task = SV.Task("t", (SV.QueryPart("use fact", "claim", ("q",)),), targets=("rule",))
    index = SolveOperatorIndex((op("chosen", ("fact", "rule"), 42), op("missing", ("absent",))))
    for attempt in range(2):
        rt = runtime if attempt == 0 else OCMRuntime(tmp_path, config=cfg)
        result = rt.solve(task, index)
        assert result.decision is SV.Decision.ANSWER and result.answer == {"value": 42}
        stage = next(s for s in result.trace.stages if s.stage is SV.Stage.COMPOSITION)
        assert stage.payload["operator_selection"]["operators_considered"] == 1
