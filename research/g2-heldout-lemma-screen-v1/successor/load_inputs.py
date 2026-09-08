"""Frozen cuts, P1, screened negatives, and held-out H1. No native export."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAPSULE = HERE.parent
REPO = CAPSULE.parent.parent
RAW = REPO / "research" / "ordinary-cut-opportunity-result-v1" / "RAW.zip"
RAW_SHA256 = "f920d0a1bca8d45a7f4d7067a54748d2cabfb246c03476fdc612f4ff8474d2ff"
RESULT_MEMBER = "prospective-run-01/opportunity-01/RESULT.json"
P1_MEMBER = "prospective-run-01/opportunity-01/P1-CONTRACTS.json"
RESULT_SHA256 = "94626dd0a0ac7ad4ce0f727b1542b3dc0bf20f8fd545a0893b7ee47cbc5aecd1"
P1_SHA256 = "f5a167da1771a47c8e3edb16fb2bbe85f0056d3252c65ab892e6f6012ba9f587"
CONSUMER = REPO / "research" / "ordinary-cut-source-evidence-v1" / "consumer-v3"
NEGATIVES = CAPSULE / "inputs" / "SCREENED-NEGATIVES.json"
HELDOUT = CAPSULE / "inputs" / "HELDOUT-H1.json"
PINS = CAPSULE / "inputs" / "PINS.json"


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(path):
    raw = Path(path).read_bytes()
    return {"bytes": len(raw), "sha256": sha256(raw)}


def read_raw_member(name, expected):
    raw = RAW.read_bytes()
    if sha256(raw) != RAW_SHA256:
        raise ValueError("frozen RAW identity")
    with zipfile.ZipFile(RAW) as archive:
        data = archive.read(name)
    if sha256(data) != expected:
        raise ValueError("frozen member identity: " + name)
    return json.loads(data)


def load_opportunity():
    return read_raw_member(RESULT_MEMBER, RESULT_SHA256)


def load_p1():
    return read_raw_member(P1_MEMBER, P1_SHA256)


def load_negatives():
    return json.loads(NEGATIVES.read_text())


def load_heldout():
    return json.loads(HELDOUT.read_text())


def unique_negatives(payload=None):
    payload = payload or load_negatives()
    rows = []
    seen = set()
    for row in payload["rows"]:
        cid = row["canonical_id"]
        if cid in seen:
            continue
        seen.add(cid)
        rows.append(row)
    return rows


def cut_bodies(opportunity=None, canonical_ids=None):
    opportunity = opportunity or load_opportunity()
    wanted = set(canonical_ids)
    found = {}
    for root in opportunity["roots"]:
        for cut in root.get("cuts") or []:
            cid = cut.get("canonical_id")
            if cid in wanted and cid not in found:
                found[cid] = {
                    "body": cut["body"],
                    "source_label": root.get("label"),
                    "source_ordinal": root["ordinal"],
                }
    missing = wanted - set(found)
    if missing:
        raise ValueError("missing cut bodies")
    return found
