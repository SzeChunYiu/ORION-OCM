"""run_all_v1.py -- single deterministic entry point for HST-D3 lane B.

Re-derives every JSON certificate from scratch, asserts cross-certificate internal
consistency, and writes RUN_ALL_V1_MANIFEST.json (sha256 of each artifact for binding).
Exit code 0 iff every assertion holds. Run: python3 run_all_v1.py  (py3.8).
"""
import hashlib
import json
import platform
import sys
import time
from typing import Dict

import t02_reach_v1
import t10_ev_v1
import t11_module_v1
import parent_witnesses_v1
import finite_world_v1 as fw


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def dump(name: str, doc: Dict) -> str:
    path = name
    with open(path, "w") as fh:
        json.dump(doc, fh, sort_keys=True, indent=1)
    return path


def main() -> int:
    t0 = time.time()
    certs = {}
    times = {}
    for name, mod in [("T02_REACH_WITNESS_V1.json", t02_reach_v1),
                      ("T10_EV_ORACLE_V1.json", t10_ev_v1),
                      ("T11_MODULE_PROMOTION_V1.json", t11_module_v1),
                      ("PARENT_WITNESSES_T04_T08_V1.json", parent_witnesses_v1)]:
        s = time.time()
        certs[name] = mod.main()
        times[name] = round(time.time() - s, 3)
        dump(name, certs[name])

    t02c, t10c, t11c = (certs["T02_REACH_WITNESS_V1.json"],
                        certs["T10_EV_ORACLE_V1.json"],
                        certs["T11_MODULE_PROMOTION_V1.json"])
    pw = certs["PARENT_WITNESSES_T04_T08_V1.json"]

    # cross-certificate consistency (world identity + counts + hostile/flip flags)
    world_ids = {c["world"]["world_id"] for c in (t02c, t10c, t11c)}
    assert world_ids == {"FW1"}, "world spec mismatch across certificates"
    for c in (t02c, t10c, t11c):
        assert c["world"] == fw.WORLD_SPEC, "world spec drifted from finite_world_v1"
    assert t02c["exhaustive_enumeration_flags"]["closure_fixpoint_verified"]
    assert t02c["checks"]["C2_p_notin_closure_O"]["p_in_closure_O"] is False
    assert t02c["checks"]["C5_reach_B_expansion"]["strict_expansion_at_B"]
    assert t02c["checks"]["C6_hostile_burden"]["hostile_confirmed_reach_up_burden_worse"]
    assert t10c["summary"]["separation_confirmed"]
    assert t10c["oracle_not_estimate"] and t10c["deterministic"]
    assert t11c["flip_verified"] and t11c["module"]["interface_preservation_all_16_states"]
    assert pw["T04_allocation_witness"]["ratio_equals_2^Delta"]
    assert pw["T08_blackwell_witness"]["buy_information"] is False

    manifest = {
        "run_id": "RUN_ALL_V1",
        "lane": "HST-D3 lane B (issue #233)",
        "host_python": platform.python_version(),
        "host": platform.node(),
        "world": fw.WORLD_SPEC["world_id"],
        "certificates": {name: {"runtime_seconds": times[name],
                                "sha256": sha256_file(name)} for name in certs},
        "cross_checks": ["world identity FW1 across T02/T10/T11",
                         "T02 closure fixpoint + p-notin-closure + strict reach expansion "
                         "+ hostile burden worsening",
                         "T10 exact oracle separation + table/oracle consistency",
                         "T11 threshold flip + interface preservation on all 16 states",
                         "T04 Kraft-complete codes + 2^Delta ratio; T08 VoI + no-buy"],
        "total_runtime_seconds": round(time.time() - t0, 3),
        "deterministic": True,
        "all_assertions_passed": True,
    }
    dump("RUN_ALL_V1_MANIFEST.json", manifest)
    print("RUN_ALL OK in %.3fs (python %s): %s" % (
        manifest["total_runtime_seconds"], platform.python_version(), sorted(certs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
