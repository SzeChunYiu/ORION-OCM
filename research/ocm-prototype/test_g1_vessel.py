"""Scientific custody/admission controls; fake model rows are unit fixtures only."""
import copy
from importlib.metadata import PackageNotFoundError
from pathlib import Path
import sys
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import g1_vessel as G
import g1_field as F
import udpipe_donor as U
from syntax_contract import validate
from clia_tasks import load_task

WORDS = [{"id": 1, "form": "Birds", "head": 2, "deprel": "nsubj", "upos": "NOUN"},
         {"id": 2, "form": "fly", "head": 0, "deprel": "root", "upos": "VERB"}]
TOKENS = ["Birds", "fly"]


@pytest.fixture
def vessel(tmp_path):
    model = tmp_path / "INVALID_MODEL_BYTES.udpipe"
    model.write_bytes(b"UNIT_FIXTURE_NOT_A_TRAINED_DONOR")
    runtime = G.OCMRuntime(tmp_path / "state", config=G.CONFIG)
    fixture = F.setup(runtime, model, {"role": "UNIT_FIXTURE"})
    return runtime, fixture, model


def test_structural_validator_accepts_and_rejects():
    assert validate(WORDS, TOKENS) is None
    assert validate(WORDS[:1], TOKENS) == "WORD_COUNT_MISMATCH"
    for field, value in [("id", True), ("form", "Gold"), ("head", 3),
                         ("upos", "INVENTED"), ("deprel", "nsubj\n")]:
        words = copy.deepcopy(WORDS); words[0][field] = value
        assert validate(words, TOKENS) is not None
    words = copy.deepcopy(WORDS); words[1].update(head=1, deprel="dep")
    assert validate(words, TOKENS).startswith("INVALID_TREE")
    assert validate(None, TOKENS) == "WORD_COUNT_MISMATCH"


def test_setup_idempotence_and_identity_refusal(vessel, tmp_path):
    runtime, fixture, model = vessel
    assert F.setup(runtime, model, {"role": "UNIT_FIXTURE"}) == fixture
    with pytest.raises(ValueError, match="mismatch"):
        F.setup(runtime, model, {"role": "different training"})
    other = tmp_path / "other.udpipe"; other.write_bytes(b"another model")
    with pytest.raises(ValueError, match="mismatch"):
        F.setup(runtime, other, {"role": "UNIT_FIXTURE"})


def test_unavailable_or_changed_model_is_cannot_check(vessel, monkeypatch):
    runtime, fixture, model = vessel
    assert U.predict(TOKENS, model, "0" * 64)["status"] == "CANNOT_CHECK"
    assert U.predict(TOKENS, model.parent / "missing", "0" * 64)["status"] == "CANNOT_CHECK"
    def unavailable(_):
        raise PackageNotFoundError("ufal.udpipe")
    monkeypatch.setattr(U, "version", unavailable)
    assert U.predict(TOKENS, model, fixture["model_sha256"])["status"] == "CANNOT_CHECK"


def test_syntax_observation_is_not_truth_and_whole_model_withdrawal(vessel, monkeypatch):
    runtime, fixture, model = vessel
    monkeypatch.setattr(G, "predict", lambda *args: {
        "status": "PREDICTED", "words": WORDS, "model_sha256": fixture["model_sha256"]})
    syntax = G.query(runtime, {"kind": "syntax", "tokens": TOKENS})
    assert syntax["status"] == "ADMITTED" and syntax["claim"] == "MODEL_SUPPORTED_SYNTAX_OBSERVATION"
    sid = syntax["admitted_id"]
    assert runtime.state.ks.atom_map()[sid].atom_type == "observation"
    assert runtime.state.certificates[sid] == "OBSERVATION"
    # No gold correctness is available at admission. A different structurally
    # valid model tree would also pass structure; external accuracy is separate.
    math = G.query(runtime, {"kind": "clia", "task": load_task("jmbl_fg_max3")})
    assert math["status"] == "ADMITTED" and math["claim"] == "SPECIFICATION_VERIFIED_PROGRAM"
    G.worker(runtime.root, {"action": "revoke", "evidence": [fixture["model_evidence"]]})
    restored = G.OCMRuntime(runtime.root, config=G.CONFIG)
    assert not restored.state.ks.atom_map()[sid].is_live(restored.state.revoked)
    assert restored.state.ks.atom_map()[math["admitted_id"]].is_live(restored.state.revoked)
    refused = G.query(restored, {"kind": "syntax", "tokens": TOKENS})
    assert refused["admitted_id"] is None and refused["answer"] is None
    with pytest.raises(ValueError, match="complete evidence identifiers"):
        G.worker(runtime.root, {"action": "revoke", "evidence": fixture["model_evidence"]})


def test_final_admission_refusal_cannot_count_as_answer(vessel, monkeypatch):
    runtime, fixture, model = vessel
    original = G.check
    calls = 0
    def fail_second(runtime, request, output, name):
        nonlocal calls
        if name == G.CATALOGUE[1]:
            calls += 1
            if calls == 2:
                return {"status": "CANNOT_CHECK", "reason": "TEST_CHECKER_UNAVAILABLE"}
        return original(runtime, request, output, name)
    monkeypatch.setattr(G, "check", fail_second)
    result = G.query(runtime, {"kind": "clia", "task": load_task("jmbl_fg_max3")})
    assert result["solve_status"] == "ANSWER" and result["status"] == "CANNOT_CHECK"
    assert result["admitted_id"] is None and result["answer"] is None


def test_missing_checker_and_gold_inputs_refused(vessel):
    runtime, fixture, model = vessel
    request = {"kind": "clia", "task": load_task("jmbl_fg_max3")}
    result = G.query(runtime, request, "missing_checker")
    assert result["status"] == "CANNOT_CHECK" and result["admitted_id"] is None
    result = G.query(runtime, {"kind": "syntax", "tokens": TOKENS, "gold": WORDS})
    assert result["status"] == "INPUT_REFUSED"
