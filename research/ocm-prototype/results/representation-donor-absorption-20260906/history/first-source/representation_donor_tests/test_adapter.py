"""Real existing SV consumer controls; no model, training or timing comparison."""
from pathlib import Path
import importlib.util
import sys
import copy
import pytest

PROTOTYPE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE))


def module(name):
    path = PROTOTYPE / (name + ".py")
    assert path.is_file(), f"Missing donor-absorption implementation: {name}"
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def run(variant="base", *, revoked=(), available_states=None, arm="ocm", **kw):
    D = module("representation_donor")
    policy = D.prepare(D.fixture(variant), available_states=available_states)
    return D, policy, D.evaluate(policy, arm=arm, revoked=revoked, **kw)


def test_actual_sv_full_vectors_and_complete_consumer_match_informed_parent():
    D, p, actual = run()
    reference = D.evaluate(p, arm="full")
    parent = D.evaluate(p, arm="informed_parent")
    G = module("representation_donor_grade")
    assert G.compare(reference, actual)["functional_parity"]
    assert G.compare(reference, parent)["functional_parity"]
    assert actual["consumer"]["answer"]["result"] == 42
    assert actual["consumer"]["committed"] is True
    assert actual["eligibility"]["warranted"] == "CERTIFIED"
    assert actual["eligibility"]["exploratory"] == "DYNAMIC_LUMPABILITY_ONLY"
    assert actual["calls"] and all(c["selected"] == "compact" for c in actual["calls"])
    assert {c["mode"] for c in actual["calls"]} == {"WARRANTED", "EXPLORATORY"}
    assert any(c["seed_kind"] == "global_uniform" for c in actual["calls"])
    assert all(c["fine_dimension"] == 14 and c["solve_dimension"] == 6 for c in actual["calls"])
    assert actual["resources"]["donor_calls"]["router.choose"] == len(actual["calls"])
    assert actual["resources"]["donor_calls"]["f2.fixed_point"] == len(actual["calls"])
    assert parent["calls"] == actual["calls"]


def test_incoming_edge_preserves_lumpability_but_requires_full_reconstruction_fallback():
    D, p, actual = run("incoming")
    assert actual["eligibility"]["warranted"] == "CERTIFIED"
    assert actual["eligibility"]["reconstruction"] == "REFINE_REQUIRED_NONZERO_INCIDENT_KERNEL"
    assert all(c["selected"] == "full" for c in actual["calls"])
    assert module("representation_donor_grade").compare(D.evaluate(p, arm="full"), actual)["functional_parity"]


def test_mixed_warrants_fail_the_whole_registered_family():
    D, p, actual = run("mixed_warrant")
    assert actual["eligibility"]["warranted"] == "REFINE_REQUIRED_WARRANT_NONMEASURABLE"
    assert all(c["selected"] == "full" for c in actual["calls"])
    assert module("representation_donor_grade").compare(D.evaluate(p, arm="full"), actual)["functional_parity"]


def test_missing_state_cannot_be_relabelled_as_negative_or_certificate():
    _, _, actual = run(available_states=(frozenset(),))
    assert actual["eligibility"]["warranted"] == "CANNOT_CHECK_MISSING_REGISTERED_STATE"
    assert all(c["selected"] == "full" for c in actual["calls"])


@pytest.mark.parametrize("revoked", [(), (1,), ("backup",), (1,"backup"), (2,), (3,), ("irrelevant",), ()])
def test_alternative_support_unknown_withdrawal_and_reinstatement_snapshots(revoked):
    D, p, actual = run("alternative", revoked=revoked)
    G = module("representation_donor_grade")
    assert G.compare(D.evaluate(p, arm="full", revoked=revoked), actual)["functional_parity"]
    assert actual["eligibility"]["warranted"] == "CERTIFIED"
    assert all(c["selected"] == "compact" for c in actual["calls"])


def test_changed_query_config_state_and_unregistered_revocation_cannot_reuse_binding():
    from dataclasses import replace
    from fractions import Fraction
    D = module("representation_donor")
    p = D.prepare(D.fixture())
    variants = [dict(task=replace(p.fixture["task"], task_id="changed-query")),
                dict(config=replace(p.fixture["config"], alpha=Fraction(1,2))),
                dict(ks=D.fixture("incoming")["ks"]), dict(revoked=("unregistered",))]
    for change in variants:
        actual = D.evaluate(p, arm="ocm", **change)
        reference = D.evaluate(p, arm="full", **change)
        assert actual["calls"] and all(c["selected"] == "full" for c in actual["calls"])
        assert all(c["binding"] == "REFINE_REQUIRED_CHANGED_BINDING" for c in actual["calls"])
        assert module("representation_donor_grade").compare(reference, actual)["functional_parity"]


def test_external_grader_rejects_actual_selected_vector_and_consumer_tampering():
    D, p, actual = run()
    reference = D.evaluate(p, arm="full")
    G = module("representation_donor_grade")
    assert G.compare(reference, actual)["functional_parity"]
    wrong = copy.deepcopy(actual)
    key = next(iter(wrong["vectors"][0]["values"]))
    wrong["vectors"][0]["values"][key] = "99/1"
    assert not G.compare(reference, wrong)["functional_parity"]
    wrong = copy.deepcopy(actual)
    wrong["consumer"]["answer"]["result"] = 99
    assert not G.compare(reference, wrong)["functional_parity"]


def test_exact_donor_source_is_loaded_and_a_changed_source_is_refused(tmp_path):
    I = module("representation_donor_imports")
    assert set(I.load()) == {"router", "f2", "revision"}
    import shutil
    shutil.copytree(I.DONORS, tmp_path / "donors")
    source = tmp_path / "donors" / "v2" / "f2.py"
    source.write_bytes(source.read_bytes() + b"\n# altered\n")
    with pytest.raises(ValueError, match="DONOR_SOURCE_DRIFT"):
        I.load(tmp_path / "donors")


def test_existing_revision_checker_refuses_split_fibre_and_malformed_maps():
    I = module("representation_donor_imports")
    revision = I.load()["revision"]
    blocks = ((0,1),(2,))
    assert revision.revision_commutes((0,1,2), blocks, (0,1))
    assert not revision.revision_commutes((0,2,2), blocks, (0,1))
    with pytest.raises(revision.CannotCheck):
        revision.revision_commutes({0:0,1:1,2:2}, blocks, (0,1))
