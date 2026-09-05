"""M12 V3: stream generation is deterministic, leak-free and inside the bounded world; one paired lifetime runs end to end."""
from __future__ import annotations

import json
from pathlib import Path

from ocm.evaluation import m12_paired_eval as PE
from ocm.lifetime import streams as SR

ROOT = Path(__file__).resolve().parents[2]


def test_streams_are_deterministic_leak_free_and_distinct():
    a, b = SR.build_stream(3), SR.build_stream(3)
    assert a["sha256"] == b["sha256"] and SR.leak_check(a)["ok"]
    hashes = {SR.build_stream(k)["sha256"] for k in range(8)}
    assert len(hashes) == 8
    man = json.loads((ROOT / "research/ocm-m12/M12_V3_STREAM_MANIFEST_V1.json").read_text())
    assert SR.stream_manifest(8)["sha256"] == man["sha256"]                      # the frozen manifest is what the code generates
    s = SR.build_stream(0)
    nonce = set(s["maps"]["nonce"].values())
    assert nonce.isdisjoint(SR._manifest_words()) and all(v in SR.REGULAR for v in (s["maps"]["verb"][r] for r in SR.REGULAR))
    assert any("finded" in u or "seed" in u or "holded" in u for u, _ in s["negative_transfer"])  # mis-inflection probes survive substitution


def test_one_paired_lifetime_runs_with_chain_identity(tmp_path):
    st = SR.build_stream(1)
    o = PE.run_lifetime("ocm", st, tmp_path)
    p = PE.run_lifetime("whole_system_parent", st, tmp_path)
    assert o["chain_continuous"] and len(o["phases"]) == 8 and len(p["phases"]) == 8
    so, sp = PE.lifetime_scores(o), PE.lifetime_scores(p)
    assert so["G_self_repair"] == 1.0 and sp["G_self_repair"] == 0.0 and so["F_integrity"] == 1.0
    assert PE.sign_test([1, 1, 1, 1, 1, 1, 1, 1])["verdict"] == "OCM_RESIDUAL" and PE.sign_test([1, 1, 1, 1, 1, 1, 1, -1])["verdict"] == "INCONCLUSIVE" and PE.sign_test([0] * 8)["verdict"] == "TIES_ONLY"
