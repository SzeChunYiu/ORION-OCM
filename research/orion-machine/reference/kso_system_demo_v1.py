"""One-command controlled KSO system demonstration through M6a + multi-domain integration.

The demo intentionally reports each milestone separately rather than collapsing them into a fake
single score. Default mode executes M3 procedure learning, M4 governed Jump, M5 controlled chat,
M6a Lean proof-channel integration, and one controlled KnowledgeSpace containing both learned
procedures and Lean-verified mathematics. `--with-m2` additionally runs a small M2 solve smoke pass
on the upstream ME-X1 exact domain.

This is a runnable integration demo, not an open-domain AGI/frontier-math/scalability claim.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str):
    if name in sys.modules:
        return sys.modules[name]
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run_system(*, with_m2: bool = False) -> dict[str, object]:
    m3 = _load("kso_m3_learning_v1")
    m4 = _load("kso_m4_jump_v1")
    m5 = _load("kso_m5_chat_v1")
    demo = _load("kso_demo_v1")
    m6 = _load("kso_m6_formal_math_v1")
    multi = _load("kso_multidomain_v1")

    r3 = m3.run_m3()
    r4 = m4.run_m4()
    r5 = m5.run_m5()
    r6 = m6.run_m6a()
    rm = multi.run_multidomain()
    transcript = demo.run_script()

    stages: dict[str, object] = {
        "M3": {
            "terminal": r3["terminal"],
            "learned_channels": sum(1 for row in r3["channels"].values() if row["warranted"]),
            "feedback_warranted": r3["channels"]["FEEDBACK"]["warranted"],
        },
        "M4": {
            "terminal": r4["terminal"],
            "trigger": r4["trigger"]["kind"],
            "minimum_jump": r4["proposals"]["minimum_sufficient"],
        },
        "M5": {
            "terminal": r5["terminal"],
            "translator_invariant": all(r5["translator_invariance"].values()),
            "prelesson": r5["chat"]["prelesson_gap"],
            "postlesson_answer": r5["chat"]["answer_after_lesson"],
            "postrevocation": r5["chat"]["answer_after_revocation"],
        },
        "M6A": {
            "terminal": r6["terminal"],
            "kernel_verified": r6["source"]["kernel_verified"],
            "registered_rejections": r6["source"]["registered_rejections"],
            "frontier_math_discovery": r6["authority"]["frontier_math_discovery"],
        },
        "MULTIDOMAIN": {
            "terminal": rm["terminal"],
            "learned_procedures": rm["space"]["learned_procedures"],
            "verified_math_proofs": rm["space"]["verified_math_proofs"],
            "cross_domain_noninterference": all(rm["noninterference"].values()),
        },
    }

    if with_m2:
        m2 = _load("kso_m2_solve_v1")
        r2 = m2.run(per_family=1)
        stages = {
            "M2_SMOKE": {
                "terminal": r2["terminal"],
                "instances": r2["G1_exact"]["n"],
                "store_exact": r2["G1_exact"]["exact"],
                "navigation_found": r2["G1_exact"]["FOUND_BY_NAVIGATION"],
                "authority": "smoke rerun only; full registered comparator result remains #298 PARENT_SUFFICIENT",
            },
            **stages,
        }

    expected = (
        r3["terminal"] == "M3_EXACT_GAP_LEARNING_GREEN"
        and r4["terminal"] == "M4_FINITE_GOVERNED_JUMP_GREEN"
        and r5["terminal"] == "M5_CONTROLLED_CODEC_CHAT_GREEN"
        and r6["terminal"] == "M6A_FORMAL_MATH_VERIFIER_CHANNEL_INTEGRATED_PARENT_SUFFICIENT"
        and rm["terminal"] == "CONTROLLED_MULTIDOMAIN_KSO_GREEN"
        and r6["authority"]["M6_full"] is False
    )
    if not expected:
        raise AssertionError("one or more controlled KSO stages failed")

    return {
        "terminal": "KSO_CONTROLLED_SYSTEM_DEMO_GREEN_THROUGH_M6A",
        "stages": stages,
        "chat_transcript": transcript,
        "boundary": {
            "controlled_multidomain_kso": True,
            "scalability_established": False,
            "automatic_domain_router": False,
            "open_domain_language": False,
            "full_frontier_math": False,
            "novelty": False,
        },
    }


def print_human(result: dict[str, object]) -> None:
    print("KSO controlled system demo")
    print("=" * 28)
    stages = result["stages"]
    assert isinstance(stages, dict)
    for name, row in stages.items():
        assert isinstance(row, dict)
        print(f"{name}: {row['terminal']}")
    print("\nConversation/lifecycle:")
    transcript = result["chat_transcript"]
    assert isinstance(transcript, list)
    for row in transcript:
        print(f"> {row['user']}")
        print(row["kso"])
    print("\nBoundary:")
    print("  controlled multi-domain KSO: YES")
    print("  scalability / learned router: NOT YET")
    print("  open-domain language:         NOT YET")
    print("  frontier math discovery:      NOT YET")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--with-m2", action="store_true")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        r = run_system(with_m2=a.with_m2)
    except Exception as exc:
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    if a.json:
        print(json.dumps(r, indent=2, sort_keys=True))
    else:
        print_human(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
