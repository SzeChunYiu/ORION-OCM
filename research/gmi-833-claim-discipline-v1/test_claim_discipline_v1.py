"""Package invariants for gmi-833-claim-discipline-v1 (stdlib-only, host-free)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["scope_quantifiers", "assumptions", "falsifiers", "strongest_parents", "forbidden_extrapolations"]
STATUSES = {"CARRIED_SCORES_V1", "CARRIED_SCORES_V2", "EXTRACTED", "DERIVED", "REGISTERED_GAP"}


def _reg():
    return json.load(open(os.path.join(HERE, "REGISTRATIONS_V1.json")))


def test_universe_complete():
    reg = _reg()
    assert reg["counts"]["objects"] == 233
    ids = [o["result_id"] for o in reg["objects"]]
    assert len(set(ids)) == 233
    tr = {}
    for o in reg["objects"]:
        tr[o["tranche"]] = tr.get(o["tranche"], 0) + 1
    assert tr == {"U-V1": 29, "U-LEGACY": 173, "U-ARRIVALS": 24, "U-NEW": 7}


def test_every_field_present_and_valid():
    reg = _reg()
    for o in reg["objects"]:
        for f in FIELDS:
            fd = o["fields"].get(f)
            assert fd is not None, (o["result_id"], f)
            assert fd["status"] in STATUSES
            if fd["status"] == "REGISTERED_GAP":
                assert fd.get("reason", "").strip(), (o["result_id"], f)
            else:
                assert fd.get("content"), (o["result_id"], f)


def test_gap_count_enumerated():
    reg = _reg()
    gaps = [(o["object_id"], f) for o in reg["objects"] for f in FIELDS if o["fields"][f]["status"] == "REGISTERED_GAP"]
    assert reg["counts"]["registered_gap"] == 8
    assert len(gaps) == 8
    assert reg["counts"]["fields_registered"] == 233 * 5 - 8


def test_no_boilerplate_derived():
    seen = {}
    for o in _reg()["objects"]:
        for f in FIELDS:
            fd = o["fields"][f]
            if fd["status"] == "DERIVED":
                for item in fd.get("content", []):
                    assert item not in seen, ("duplicate DERIVED string", o["object_id"], seen.get(item))
                    seen[item] = o["object_id"]


def test_g7_object_not_bridged():
    reg = _reg()
    by_id = {o["object_id"]: o for o in reg["objects"]}
    assert "MORPHOLOGY_PHASE_RV_THEOREM_V1" in by_id  # G7 stays M0: registration does not bridge substance gaps


def test_rescore_packages_unmodified_by_bridge():
    # the bridge lives in this package only; rescore v2 must still show the 7 G6 rows at M0
    v2 = json.load(open(os.path.join(os.path.dirname(HERE), "gmi-833-maturity-rescore-v2-v1", "THEOREM_SCORES_V2.json")))
    g6 = ["AS-1", "EC-2", "DE-3", "DP2-6", "NC-3", "SG-1", "TI-2"]
    join = json.load(open(os.path.join(HERE, "evidence", "join_v2_census.json")))
    for rid, oid in join.items():
        if oid in g6:
            row = next(e for e in v2 if e["result_id"] == rid)
            assert (row["maturity_M"], row["evidence_EV"]) == ("M0", "EV0"), (rid, row["maturity_M"])
