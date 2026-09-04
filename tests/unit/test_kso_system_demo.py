from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_system_demo_v1.py"


def load():
    name = "kso_system_demo_v1"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_controlled_system_demo_runs_through_m6a_and_multidomain():
    demo = load()
    r = demo.run_system(with_m2=False)
    assert r["terminal"] == "KSO_CONTROLLED_SYSTEM_DEMO_GREEN_THROUGH_M6A"
    assert r["stages"]["M3"]["terminal"] == "M3_EXACT_GAP_LEARNING_GREEN"
    assert r["stages"]["M4"]["minimum_jump"] == "kso-j3-add-conjunction-feature"
    assert r["stages"]["M5"]["translator_invariant"] is True
    assert r["stages"]["M6A"]["kernel_verified"] == 20
    assert r["stages"]["M6A"]["registered_rejections"] == 20
    assert r["stages"]["MULTIDOMAIN"]["terminal"] == "CONTROLLED_MULTIDOMAIN_KSO_GREEN"
    assert r["stages"]["MULTIDOMAIN"]["learned_procedures"] == 1
    assert r["stages"]["MULTIDOMAIN"]["verified_math_proofs"] == 20
    assert r["stages"]["MULTIDOMAIN"]["cross_domain_noninterference"] is True
    assert [row["receipt"]["status"] for row in r["chat_transcript"]] == [
        "GAP_UNKNOWN_PROCEDURE",
        "LEARNED",
        "PASS",
        "REVOKED",
        "GAP_REVOKED_PROCEDURE",
        "REINSTATED",
        "PASS",
    ]
    assert r["boundary"] == {
        "controlled_multidomain_kso": True,
        "scalability_established": False,
        "automatic_domain_router": False,
        "open_domain_language": False,
        "full_frontier_math": False,
        "novelty": False,
    }


def test_demo_main_returns_zero():
    demo = load()
    assert demo.main(["--json"]) == 0
