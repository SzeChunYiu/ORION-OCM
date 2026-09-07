"""Real retained evidence baseline and data-only falsifying controls; no solver use."""
import copy
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_data import canonical, load_json, read_archive, record
from audit_evidence import audit, validate_final, verify_sources
from audit_receipts import audit_rows
HERE = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def retained():
    members = load_json((HERE / "records/final-commissioning.members.json").read_bytes())
    data = read_archive(HERE / "records/final-commissioning.tar.gz", members)
    freeze = load_json((HERE / "SOURCE_FREEZE.json").read_bytes())
    return data, freeze


def rows(data, freeze):
    return audit_rows(data, load_json(data["result.json"]), load_json(data["matrix.json"]),
                      load_json(data["cases/composition/prepare/runtime.json"]), freeze["original_root"])


def test_real_current_archive_and_sources_pass_portably():
    result = audit(HERE)
    assert result["terminal"] == "RETAINED_EVIDENCE_AND_SOURCE_BINDINGS_PASS"
    assert (result["controls"], result["kernel_passes"], result["native_processes"]) == (47, 14, 47)


def test_real_nested_rows_pass(retained):
    data, freeze = retained
    assert rows(data, freeze)["controls"] == 47


@pytest.mark.parametrize("change", ["missing", "extra", "changed", "seal"])
def test_final_complete_seal_is_required(retained, change):
    raw, freeze = retained; data = dict(raw)
    if change == "missing": del data["cases/composition/prepare/request.json"]
    if change == "extra": data["extra"] = b"x"
    if change == "changed": data["cases/composition/prepare/request.json"] += b" "
    if change == "seal":
        seal = load_json(data["seal.json"]); seal["evidence_complete"] = False
        data["seal.json"] = canonical(seal)
    with pytest.raises(ValueError): validate_final(data, freeze)


@pytest.mark.parametrize("field,value", [("denominator", 46), ("passed", True), ("failure", "failed")])
def test_false_or_incomplete_result_cannot_pass(retained, field, value):
    data, freeze = retained; result = load_json(data["result.json"]); result[field] = value
    with pytest.raises(ValueError): audit_rows(data, result, load_json(data["matrix.json"]),
        load_json(data["cases/composition/prepare/runtime.json"]), freeze["original_root"])


def test_duplicate_or_missing_control_is_not_another_success(retained):
    data, freeze = retained; result = load_json(data["result.json"])
    result["controls"][1] = copy.deepcopy(result["controls"][0])
    with pytest.raises(ValueError, match="row identities"):
        audit_rows(data, result, load_json(data["matrix.json"]),
                   load_json(data["cases/composition/prepare/runtime.json"]), freeze["original_root"])


@pytest.mark.parametrize("change", ["native_cleanup", "wrong_native", "native_raw", "wrong_issuer", "wrong_input", "wrong_cause", "wrong_mount"])
def test_rebound_row_still_requires_actual_custody_and_cause(retained, change):
    original, freeze = retained; data = dict(original); result = load_json(data["result.json"])
    name = "cases/composition/check-0/check.json"; receipt = load_json(data[name])
    if change == "native_cleanup": receipt["process"]["cleanup"]["group_absent"] = False
    if change == "wrong_native": receipt["process"]["executable"]["sha256"] = "0" * 64
    if change == "native_raw": receipt["process"]["stdout_base64"] = "e30="
    if change == "wrong_issuer": receipt["prepared_receipt_sha256"] = "0" * 64
    if change == "wrong_input": receipt["inputs"]["candidate_packet"]["sha256"] = "0" * 64
    if change == "wrong_cause": receipt["stage"] = receipt["native"]["stage"] = "unrelated_refusal"
    if change == "wrong_mount": receipt["process"]["mounts"].append({"source": "/host", "destination": "/source", "mode": "read-only"})
    data[name] = canonical(receipt)
    data[name.replace("check.json", "receipt.json")] = canonical({k: v for k, v in receipt.items()
        if k not in {"prepared_receipt_sha256", "environment_id"}})
    result["controls"][1]["receipt"].update(record(data[name]))
    cause = {"native_cleanup": "native process incomplete", "wrong_native": "native executable differs",
             "native_raw": "stdout: byte binding differs", "wrong_issuer": "issuer differs",
             "wrong_input": "issued input identities differ", "wrong_cause": "control cause differs",
             "wrong_mount": "native role mounts differ"}[change]
    with pytest.raises(ValueError, match=cause):
        audit_rows(data, result, load_json(data["matrix.json"]),
                   load_json(data["cases/composition/prepare/runtime.json"]), freeze["original_root"])


def test_host_raw_stream_custody_is_checked(retained):
    original, freeze = retained; data = dict(original)
    data["cases/composition/prepare-process/stdout.bin"] = b"FORGED\n"
    with pytest.raises(ValueError): rows(data, freeze)


def test_bound_source_mutation_and_symlink_refuse(tmp_path):
    raw = b"registered source"; expected = {"research/proof-environment-v1/Check.lean": record(raw)}
    file = tmp_path / next(iter(expected)); file.parent.mkdir(parents=True); file.write_bytes(raw)
    verify_sources(tmp_path, expected)
    file.write_bytes(b"changed source")
    with pytest.raises(ValueError): verify_sources(tmp_path, expected)
    file.unlink(); target = tmp_path / "outside"; target.write_bytes(raw); file.symlink_to(target)
    with pytest.raises(ValueError): verify_sources(tmp_path, expected)


def test_recorded_host_cleanup_must_be_complete(retained):
    original, freeze = retained; data = dict(original)
    name = "cases/composition/prepare-process/process.json"
    process = load_json(data[name]); process["cleanup"]["group_absent"] = False
    data[name] = canonical(process)
    with pytest.raises(ValueError, match="host cleanup incomplete"): rows(data, freeze)


def test_current_source_binding_cannot_omit_registered_helper(retained, monkeypatch):
    import audit_evidence as E
    _, frozen = retained; freeze = copy.deepcopy(frozen)
    del freeze["source_files"]["research/mechanical-proof-v1/isolation.py"]
    original = E.file_bytes
    monkeypatch.setattr(E, "file_bytes", lambda p: canonical(freeze) if Path(p).name == "SOURCE_FREEZE.json" else original(p))
    with pytest.raises(ValueError, match="registered source membership differs"): E.audit(HERE)


def test_portable_audit_never_opens_original_host_paths(monkeypatch):
    import builtins
    import io
    original, io_original = builtins.open, io.open
    allowed = HERE.parent.parent.resolve()
    def checked(opener):
        def call(path, *args, **kwargs):
            if isinstance(path, (str, bytes, Path)):
                assert Path(path).resolve().is_relative_to(allowed), "external historical host path opened"
            return opener(path, *args, **kwargs)
        return call
    monkeypatch.setattr(builtins, "open", checked(original))
    monkeypatch.setattr(io, "open", checked(io_original))
    assert audit(HERE)["controls"] == 47
