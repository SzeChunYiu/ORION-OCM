"""Read retained proposals and P1 from the frozen #164 capsule. No native export."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIVAL = HERE.parent
REPO = REVIVAL.parent.parent
FROZEN = REPO / "research" / "ordinary-cut-opportunity-result-v1"
CONSUMER = REPO / "research" / "ordinary-cut-source-evidence-v1" / "consumer-v3"
RAW = FROZEN / "RAW.zip"
RAW_SHA256 = "f920d0a1bca8d45a7f4d7067a54748d2cabfb246c03476fdc612f4ff8474d2ff"
RESULT_MEMBER = "prospective-run-01/opportunity-01/RESULT.json"
P1_MEMBER = "prospective-run-01/opportunity-01/P1-CONTRACTS.json"
RESULT_SHA256 = "94626dd0a0ac7ad4ce0f727b1542b3dc0bf20f8fd545a0893b7ee47cbc5aecd1"
P1_SHA256 = "f5a167da1771a47c8e3edb16fb2bbe85f0056d3252c65ab892e6f6012ba9f587"

CLASS_PARAMETERS = [
    {"id": "V0", "type": "class"},
    {"id": "V1", "type": "class"},
    {"id": "V2", "type": "class"},
]
SSRIN_STYLE = ["(", "V0", "C_", "V1", "->", "(", "V0", "i^i", "V2", ")", "C_", "(", "V1", "i^i", "V2", ")", ")"]
MEMBERSHIP = ["V0", "e.", "V1"]
EQUALITY = ["V0", "=", "V1"]
PREDECESSOR_SUBSET = ["V0", "C_", "V1"]
PREDECESSOR_AND = ["(", "V0", "C_", "V1", "/\\", "V1", "C_", "V2", ")"]


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(path):
    raw = Path(path).read_bytes()
    return {"bytes": len(raw), "sha256": sha256(raw)}


def read_raw_member(name):
    raw = RAW.read_bytes()
    if sha256(raw) != RAW_SHA256:
        raise ValueError("frozen RAW identity")
    with zipfile.ZipFile(RAW) as archive:
        data = archive.read(name)
    return data


def load_result():
    data = read_raw_member(RESULT_MEMBER)
    if sha256(data) != RESULT_SHA256:
        raise ValueError("frozen RESULT identity")
    return json.loads(data)


def load_p1():
    data = read_raw_member(P1_MEMBER)
    if sha256(data) != P1_SHA256:
        raise ValueError("frozen P1 identity")
    return json.loads(data)


def proposals_in_order(result=None):
    """Every CUT_PROPOSAL body in original root/cut order. Does not re-enumerate."""
    if result is None:
        result = load_result()
    rows = []
    for root in result["roots"]:
        for cut in root.get("cuts") or []:
            if cut.get("status") != "CUT_PROPOSAL":
                continue
            body = cut["body"]
            rows.append({
                "ordinal": root["ordinal"],
                "label": root.get("label"),
                "canonical_id": cut.get("canonical_id"),
                "query": body["query"],
                "premises": body["premises"],
                "parameters": body["parameters"],
                "original_screen": cut.get("screen"),
            })
    return rows


def root_status_counts(result=None):
    if result is None:
        result = load_result()
    counts = {}
    for root in result["roots"]:
        status = root.get("status")
        counts[status] = counts.get(status, 0) + 1
    return counts
