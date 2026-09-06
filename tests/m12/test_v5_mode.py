"""M12 V5 mode: protected pre-registered study on fresh streams (issue #38 M12 gates)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ocm.evaluation import m12_paired_eval as PE
from ocm.lifetime import streams as SR


def test_v5_config_is_the_preregistered_rule():
    assert PE.V5["seed"] == "OCM-M12-V5" and PE.V5["primary"] == "A_conversations"
    assert PE.V5["secondary"] == ("A_post_deployment", "A_honest_unknown", "D_causal")          # three inferential secondaries
    assert PE.V5["categorical"] == ("E_transfer", "F_integrity", "G_self_repair")                 # never tested
    assert set(PE.V5["secondary"]).isdisjoint(PE.V5["categorical"])
    assert PE.V5["seed"] != PE.V4["seed"]                                                        # fresh, never-exposed streams


def test_v5_streams_are_fresh_and_leak_free():
    v4 = {SR.build_stream(k, seed=PE.V4["seed"], world_true_half=True)["sha256"] for k in range(PE.N_LIFETIMES)}
    v5 = [SR.build_stream(k, seed=PE.V5["seed"], world_true_half=True) for k in range(PE.N_LIFETIMES)]
    assert not (v4 & {s["sha256"] for s in v5})
    assert all(SR.leak_check(s)["ok"] for s in v5)
    man = SR.stream_manifest(PE.N_LIFETIMES, seed=PE.V5["seed"], world_true_half=True, name="M12_V5_STREAM_MANIFEST_V1")
    frozen = Path(PE.V5["manifest"])
    if frozen.exists():                                                                          # the frozen manifest is exactly the regenerated one
        assert json.loads(frozen.read_text())["sha256"] == man["sha256"]


def test_v5_refuses_without_frozen_manifest_and_preregistration(tmp_path, monkeypatch):
    monkeypatch.setitem(PE.V5, "manifest", tmp_path / "absent_manifest.json")
    monkeypatch.setitem(PE.V5, "prereg", tmp_path / "absent_prereg.md")
    with pytest.raises(SystemExit):
        PE.main(["--v5", "--out", str(tmp_path / "out.json")])
    assert not (tmp_path / "out.json").exists()                                                  # no outcome is written


def test_one_sided_sign_test_and_collapsed_flag():
    st = PE.sign_test_one_sided([0.4] * 8, 0.05)
    assert st["positive"] == 8 and st["verdict"] == "OCM_RESIDUAL" and st["collapsed_one_coin"] is True
    st2 = PE.sign_test_one_sided([0.4, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01, -0.1], 0.05)
    assert st2["positive"] == 7 and st2["verdict"] == "OCM_RESIDUAL" and st2["collapsed_one_coin"] is False
    assert PE.sign_test_one_sided([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, -0.1, -0.1], 0.05)["verdict"] == "INCONCLUSIVE"
    assert PE.sign_test_one_sided([0.0] * 8, 0.05)["verdict"] == "TIES_ONLY"
