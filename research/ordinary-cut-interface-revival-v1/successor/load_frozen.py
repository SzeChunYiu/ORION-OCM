"""Read the frozen #164 capsule and the bound teaching packet. No native export."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIVAL = HERE.parent
REPO = REVIVAL.parent.parent
FROZEN = REPO / "research" / "ordinary-cut-opportunity-result-v1"
EXPORT = REPO / "research" / "ordinary-training-native-export-v1"
RAW = FROZEN / "RAW.zip"
RAW_SHA256 = "f920d0a1bca8d45a7f4d7067a54748d2cabfb246c03476fdc612f4ff8474d2ff"
RESULT_MEMBER = "prospective-run-01/opportunity-01/RESULT.json"
P1_MEMBER = "prospective-run-01/opportunity-01/P1-CONTRACTS.json"
RESULT_SHA256 = "94626dd0a0ac7ad4ce0f727b1542b3dc0bf20f8fd545a0893b7ee47cbc5aecd1"
P1_SHA256 = "f5a167da1771a47c8e3edb16fb2bbe85f0056d3252c65ab892e6f6012ba9f587"
EXPORT_RAW = EXPORT / "RAW-RECORDS.zip"
EXPORT_RAW_SHA256 = "8844340fef4a98bf3c60ae7232ca82339d5eb796e18348dc59601fde42a48a4d"
PACKET_MEMBER = "native-export-01/TEACHING-PACKET-CANDIDATE.json"
PACKET_SHA256 = "c57888abaad115493beb9c5829273837442e93d78d18d8ff2af5541f4d818c55"


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(path):
    raw = Path(path).read_bytes()
    return {"bytes": len(raw), "sha256": sha256(raw)}


def read_zip_member(archive, expected_sha, member, member_sha=None):
    raw = Path(archive).read_bytes()
    if sha256(raw) != expected_sha:
        raise ValueError("frozen archive identity")
    with zipfile.ZipFile(archive) as z:
        data = z.read(member)
    if member_sha is not None and sha256(data) != member_sha:
        raise ValueError("frozen member identity")
    return data


def load_result():
    return json.loads(read_zip_member(RAW, RAW_SHA256, RESULT_MEMBER, RESULT_SHA256))


def load_p1():
    return json.loads(read_zip_member(RAW, RAW_SHA256, P1_MEMBER, P1_SHA256))


def load_packet():
    return json.loads(read_zip_member(EXPORT_RAW, EXPORT_RAW_SHA256, PACKET_MEMBER, PACKET_SHA256))


def p1_index(rows):
    return {row["label"]: row for row in rows}


def unknown_interface_roots(result=None):
    if result is None:
        result = load_result()
    rows = [row for row in result["roots"] if row.get("status") == "UNKNOWN_INTERFACE"]
    if len(rows) != 54:
        raise ValueError("frozen UNKNOWN_INTERFACE population")
    return rows


def root_status_counts(result=None):
    if result is None:
        result = load_result()
    counts = {}
    for root in result["roots"]:
        status = root.get("status")
        counts[status] = counts.get(status, 0) + 1
    return counts
