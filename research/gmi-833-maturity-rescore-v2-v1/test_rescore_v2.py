"""Package-scoped tests for the v2 maturity rescore (FREEZE_V2 §7/§10).

Run from the package dir: python -I -B -m pytest test_rescore_v2.py -q
Deterministic; no network; no writes outside the package dir.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCORER = os.path.join(HERE, "rescore_v2.py")
JUDG = os.path.join(HERE, "judgments_v2.py")


def _run(args=None, cwd=None):
    return subprocess.run(
        [sys.executable, "-I", "-B", SCORER] + (args or []),
        cwd=cwd or HERE,
        capture_output=True,
        text=True,
    )


def test_scorer_green_and_counts():
    r = _run()
    assert r.returncode == 0, r.stderr
    res = json.load(open(os.path.join(HERE, "RESULT_V2.json")))
    c = res["counts"]
    assert c["legacy_objects_scored"] == c["legacy_target"] == 173
    assert c["arrival_packages_scored"] == c["arrival_target"] == 24
    rows = json.load(open(os.path.join(HERE, "THEOREM_SCORES_V2.json")))
    assert len(rows) == 173 + 24
    assert sum(1 for x in rows if x["tranche"] == "LEGACY_173") == 173
    assert sum(1 for x in rows if x["tranche"] == "ARRIVALS_24") == 24


def test_determinism_opt_byte_identical():
    _run()
    a = open(os.path.join(HERE, "THEOREM_SCORES_V2.json"), "rb").read()
    b = open(os.path.join(HERE, "RESULT_V2.json"), "rb").read()
    subprocess.run([sys.executable, "-I", "-O", "-B", SCORER], cwd=HERE, capture_output=True, check=True)
    assert open(os.path.join(HERE, "THEOREM_SCORES_V2.json"), "rb").read() == a
    assert open(os.path.join(HERE, "RESULT_V2.json"), "rb").read() == b


def test_fail_closed_unknown_object():
    src = open(JUDG).read()
    tampered = src.replace("('gmi-adaptive-row-confidence-v1', 'V0.2')", "('gmi-adaptive-row-confidence-v1', 'ZZZ-NOPE')", 1)
    assert tampered != src
    backup = JUDG + ".bak"
    shutil.copyfile(JUDG, backup)
    try:
        open(JUDG, "w").write(tampered)
        r = _run()
        assert r.returncode == 2, (r.returncode, r.stderr)
        assert "FAIL_CLOSED" in r.stderr
    finally:
        shutil.move(backup, JUDG)


def test_fail_closed_missing_required_field():
    src = open(JUDG).read()
    tampered = src.replace("'falsifiers':", "'falsifiers_x':", 1)
    assert tampered != src
    backup = JUDG + ".bak"
    shutil.copyfile(JUDG, backup)
    try:
        open(JUDG, "w").write(tampered)
        r = _run()
        assert r.returncode == 2, (r.returncode, r.stderr)
    finally:
        shutil.move(backup, JUDG)


def test_no_forbidden_promotion_emitted():
    res = json.load(open(os.path.join(HERE, "RESULT_V2.json")))
    rows = json.load(open(os.path.join(HERE, "THEOREM_SCORES_V2.json")))
    for promo in res["forbidden_promotions"]:
        # legal ONLY as a forbidden-list entry (result list or a record's own
        # forbidden_extrapolations); never as a claim, justification or score
        assert promo not in json.dumps(res["counts"]) + json.dumps(res["distribution_maturity"])
        for r in rows:
            assert promo not in r.get("justification", ""), (promo, r["result_id"])
            assert promo not in str(r.get("maturity_M")) + str(r.get("evidence_EV"))
            if promo in json.dumps(r):
                assert promo in json.dumps(r.get("forbidden_extrapolations", [])) or promo in json.dumps(r.get("prior_standing", "")), (promo, r["result_id"])


def test_down_generating_all_verified_and_spot_rate():
    res = json.load(open(os.path.join(HERE, "RESULT_V2.json")))
    assert res["down_generating_count"] == len(res["down_generating_ids"])
    assert res["spot_check"]["rate"] >= res["spot_check"]["frozen_minimum"]
    rows = json.load(open(os.path.join(HERE, "THEOREM_SCORES_V2.json")))
    for r in rows:
        if r["delta_kind"] == "DOWN_GENERATING":
            assert r.get("individually_verified") is True, r["result_id"]
            assert r.get("verification_note"), r["result_id"]
        # ceiling map enforced structurally
        if r["maturity_M"].startswith("M") and r["evidence_EV"].startswith("EV"):
            ceil = {"EV0": 1, "EV1": 2, "EV2": 3, "EV3": 4, "EV4": 5, "EV5": 6}[r["evidence_EV"]]
            assert int(r["maturity_M"][1]) <= ceil, r["result_id"]
