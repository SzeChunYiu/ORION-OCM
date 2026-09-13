"""RV-377-118 Lane D: the DG-12 completion instrument (degeneracy_audit.audit_module) and its manifest units."""
import json
from pathlib import Path

from gmi_microscope import degeneracy_audit as da

HERE = Path(__file__).resolve().parent


def test_classify_is_unchanged_from_rv_377_112():
    assert da._classify([1] * 24)["status"] == "DEGENERATE__OBLIGATION_IS_A_CONSTANT"
    assert da._classify([1] * 21 + [0] * 3)["status"] == "NEAR_DEGENERATE__CONSTANT_AGREES_ON_>=85%"
    assert da._classify([1] * 19 + [0] * 2 + [1] * 3)["status"] == "NEAR_DEGENERATE__CONSTANT_AGREES_ON_>=85%"
    assert da._classify([0] * 13 + [1] * 11)["status"] == "NON_DEGENERATE"
    # SKEWED_BINARY is reachable only below n = 7 (a 1-of-n minority with the constant under 85 %); RV-377-112 kept it
    assert da._classify([0] * 5 + [1])["status"] == "SKEWED_BINARY"
    assert da._classify([0] * 9 + [1])["status"] == "NEAR_DEGENERATE__CONSTANT_AGREES_ON_>=85%"


def test_not_applicable_module_writes_a_receipt_with_no_scored_rows(tmp_path):
    s = da.audit_module("b2_common", host="test", out_dir=str(tmp_path))
    assert s["verdict"] == "NOT_APPLICABLE__NO_OBLIGATION_OF_THIS_SHAPE"
    r = json.load(open(tmp_path / "STAGE_DG12_COMPLETION_b2_common_test.json"))
    assert r["n_scored"] == 0 and r["not_applicable"] and r["module"] == "b2_common"
    assert r["revival_record"] == "RV-377-118" and r["gap"] == "DG-12"


def test_grid_obligation_is_non_degenerate_and_deterministic_across_hosts(tmp_path):
    a = da.audit_module("b2_depth", host="h1", out_dir=str(tmp_path))
    b = da.audit_module("b2_depth", host="h2", out_dir=str(tmp_path))
    assert a["verdict"] == "ALL_REGISTERED_OBLIGATIONS_NON_DEGENERATE"
    assert a["content_sha256"] == b["content_sha256"]        # host and timing are outside the content hash
    r = json.load(open(tmp_path / "STAGE_DG12_COMPLETION_b2_depth_h1.json"))
    row = r["obligations"]["b2_depth.obligation|GRID"]
    assert row["n_queries"] == 256 and row["n_distinct_answers"] == 4 and row["registered_evaluation_set"]
    assert row["rule40_constant_control"]["best_constant_capability"] == 0.25
    assert "b2_depth.py" in r["inputs_sha256"] and len(r["inputs_sha256"]["b2_depth.py"]) == 64


def test_unknown_module_is_refused():
    try:
        da.audit_module("e1_scdi", host="test")
    except KeyError:
        return
    raise AssertionError("e1_scdi is covered by RV-377-112 and must not be accepted as a DG-12 completion module")


def test_manifest_lane_d_units_are_frozen_and_host_keyed():
    m = json.load(open(HERE / "GMI_WORK_MANIFEST_V1.json"))
    ud = {u["unit_id"]: u for u in m["units"] if u["lane"] == "RV118-D"}
    assert set(ud) == {f"U-D-{n}" for n in da.DG12_MODULES}
    for uid, u in ud.items():
        name = uid[len("U-D-"):]
        assert u["frozen"] is True and u["revival_id"] == "RV-377-118"
        assert u["receipt"] == f"microscopes/results/STAGE_DG12_COMPLETION_{name}_{{HOST}}.json"
        assert "{HOST}" in u["cmd"][-1] and f"audit_module('{name}'" in u["cmd"][-1]
