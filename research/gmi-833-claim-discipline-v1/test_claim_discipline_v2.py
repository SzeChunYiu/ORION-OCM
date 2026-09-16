"""Package invariants for gmi-833-claim-discipline-v1 successor tranche v2 (stdlib-only)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["scope_quantifiers", "assumptions", "falsifiers", "strongest_parents", "forbidden_extrapolations"]
PINNED = {
    "CD-1": "strongest_parents",
    "CD-2": "strongest_parents",
    "FORMAL_DERIVATION_INTEGRATION_V1": "strongest_parents",
    "GRAND_GMI_EMPIRICAL_PROGRAMME_COMPLETE": "strongest_parents",
    "READY_FORMAL": "strongest_parents",
    "TF-055": "strongest_parents",
    "V0.2": "assumptions",
    "NON-FINAL": "falsifiers",
}


def _v1():
    return json.load(open(os.path.join(HERE, "REGISTRATIONS_V1.json")))


def _v2():
    return json.load(open(os.path.join(HERE, "REGISTRATIONS_V2.json")))


def test_v1_byte_intact_gap_count_still_8():
    v1 = _v1()
    assert v1["counts"]["registered_gap"] == 8
    assert v1["counts"]["objects"] == 234
    gaps = [(o["object_id"], f) for o in v1["objects"] for f in FIELDS if o["fields"][f]["status"] == "REGISTERED_GAP"]
    assert len(gaps) == 8


def test_v2_universe_identical_to_v1():
    v1, v2 = _v1(), _v2()
    ids1 = [o["result_id"] for o in v1["objects"]]
    ids2 = [o["result_id"] for o in v2["objects"]]
    assert ids1 == ids2 and len(ids2) == 234


def test_v2_exactly_eight_slots_changed_all_pins():
    v1, v2 = _v1(), _v2()
    diffs = []
    for o1, o2 in zip(v1["objects"], v2["objects"]):
        for f in FIELDS:
            if o1["fields"][f] != o2["fields"][f]:
                diffs.append((o2["object_id"], f))
    assert sorted(diffs) == sorted((k, v) for k, v in PINNED.items())
    for oid, f in PINNED.items():
        o = next(x for x in v2["objects"] if x["object_id"] == oid)
        fd = o["fields"][f]
        assert fd["status"] in ("EXTRACTED", "DERIVED"), (oid, fd["status"])
        assert fd["content"] and fd["basis"].strip() and fd["v2_outcome"].strip()


def test_v2_zero_registered_gap():
    v2 = _v2()
    gaps = [(o["object_id"], f) for o in v2["objects"] for f in FIELDS if o["fields"][f]["status"] == "REGISTERED_GAP"]
    assert gaps == []
    assert v2["counts"]["registered_gap"] == 0
    assert v2["counts"]["fields_registered"] == 234 * 5


def test_v2_outcomes_terminal_and_typed():
    v2 = _v2()
    outs = {e["object"]: e for e in v2["v2_outcomes"]}
    assert set(outs) == set(PINNED)
    for oid, e in outs.items():
        assert e["slot"] == PINNED[oid]
        assert e["outcome"] in ("PINNED_AT_SCOPE", "RESOLVED_BY_SUPPORT_LOCATION", "RESOLVED_BY_DERIVATION", "NOT_APPLICABLE_CLAIM_CLASS", "PARENT_UNVERIFIED")
        assert e["verification"].strip()
    pinned = [e for e in outs.values() if e["outcome"] == "PINNED_AT_SCOPE"]
    assert len(pinned) == 6, "the six parent-literature gaps must be pinned at scope"
    # no invented citation: every external parent claim carries a verification record
    assert len(v2["v2_verifications"]) >= 5


def test_v2_no_boilerplate_derived_across_merged_register():
    seen = {}
    for o in _v2()["objects"]:
        for f in FIELDS:
            fd = o["fields"][f]
            if fd["status"] == "DERIVED":
                for item in fd.get("content", []):
                    assert item not in seen, ("duplicate DERIVED string", o["object_id"], seen.get(item))
                    seen[item] = o["object_id"]


def test_v2_citations_resolve_under_research():
    import re
    research = os.path.dirname(HERE)
    basenames = {}

    def pkg_basenames(pkg):
        if pkg not in basenames:
            s = set()
            for dirpath, _, files in os.walk(os.path.join(research, pkg)):
                for fn in files:
                    s.add(fn)
            basenames[pkg] = s
        return basenames[pkg]

    n = 0
    for o in _v2()["objects"]:
        pinned_field = PINNED.get(o["object_id"])
        for f in FIELDS:
            fd = o["fields"][f]
            if fd["status"] == "EXTRACTED":
                for it in fd.get("content", []):
                    m = re.match(r"([A-Za-z0-9_./-]+\.[A-Za-z0-9]+):L?\d+", it)
                    if m:
                        p = m.group(1)
                        if f == pinned_field:
                            # v2 pins must resolve research/-rooted (cross-package pins)
                            assert os.path.exists(os.path.join(research, p)), (o["object_id"], p)
                        else:
                            # v1-carried rows: research/-rooted OR own-package basename anywhere in the tree (v1 semantics)
                            assert os.path.exists(os.path.join(research, p)) or os.path.basename(p) in pkg_basenames(
                                o["package"]
                            ), (o["object_id"], p)
                        n += 1
    assert n >= 8  # the v2 EXTRACTED pins alone contribute 20+; v1-extracted rows also re-resolve
