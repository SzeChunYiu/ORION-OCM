"""Read frozen native-export and opportunity bytes. Does not re-export or overwrite RAW."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
NATIVE = REPO / "research" / "ordinary-training-native-export-v1"
OPPORTUNITY = REPO / "research" / "ordinary-cut-opportunity-result-v1"
CONSUMER = REPO / "research" / "ordinary-cut-source-evidence-v1" / "consumer-v3"
TRANSPORT = NATIVE / "trace_transport.py"

NATIVE_RAW = NATIVE / "RAW-RECORDS.zip"
NATIVE_RAW_SHA256 = "8844340fef4a98bf3c60ae7232ca82339d5eb796e18348dc59601fde42a48a4d"
CUSTODIAN_MEMBER = "native-export-01/CUSTODIAN-UNUSABLE-TRACES.json"
CUSTODIAN_SHA256 = "23ad0fe909a53c30d86e61373e826cd7e0d420581cf660a7773f3890219a14a8"
PACKET_MEMBER = "native-export-01/TEACHING-PACKET-CANDIDATE.json"
PACKET_SHA256 = "c57888abaad115493beb9c5829273837442e93d78d18d8ff2af5541f4d818c55"
P1_MEMBER = "native-export-01/P1-INVENTORY.json"
P1_SHA256 = "82b1ab1a35bc6d5d3ff72ab57867c49f6954ef3372c06ee1fd94fa5a0f09b992"

OPP_RAW = OPPORTUNITY / "RAW.zip"
OPP_RAW_SHA256 = "f920d0a1bca8d45a7f4d7067a54748d2cabfb246c03476fdc612f4ff8474d2ff"
OPP_RESULT_MEMBER = "prospective-run-01/opportunity-01/RESULT.json"
OPP_RESULT_SHA256 = "94626dd0a0ac7ad4ce0f727b1542b3dc0bf20f8fd545a0893b7ee47cbc5aecd1"

REASONS = (
    "OUTSIDE_NO_DV_INTERFACE",
    "OUTSIDE_USED_CONTRACT_NO_DV_INTERFACE",
    "OUTSIDE_MANDATORY_HYPOTHESIS_INTERFACE",
)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def read_zip_member(path, expected, name, member_sha=None):
    raw = path.read_bytes()
    if sha256(raw) != expected:
        raise ValueError("frozen archive identity: " + path.name)
    with zipfile.ZipFile(path) as archive:
        data = archive.read(name)
    if member_sha is not None and sha256(data) != member_sha:
        raise ValueError("frozen member identity: " + name)
    return data


def load_custodian():
    return json.loads(read_zip_member(NATIVE_RAW, NATIVE_RAW_SHA256, CUSTODIAN_MEMBER, CUSTODIAN_SHA256))


def load_packet():
    return json.loads(read_zip_member(NATIVE_RAW, NATIVE_RAW_SHA256, PACKET_MEMBER, PACKET_SHA256))


def load_p1():
    return json.loads(read_zip_member(NATIVE_RAW, NATIVE_RAW_SHA256, P1_MEMBER, P1_SHA256))


def load_opportunity_result():
    return json.loads(read_zip_member(OPP_RAW, OPP_RAW_SHA256, OPP_RESULT_MEMBER, OPP_RESULT_SHA256))


def required_active_pairs(node):
    pairs = 0
    for item in node.get("distinct_variable_obligations") or []:
        pairs += len(item.get("required_active_pairs") or [])
    return pairs


def extra_hypotheses(trace):
    source = trace["source"]
    mandatory = {h["label"] for h in source["floating"] + source["essential"]}
    extra = []
    for node in trace["nodes"]:
        if node.get("kind") in ("floating_hypothesis", "essential_hypothesis"):
            if node.get("label") not in mandatory:
                extra.append(node["label"])
    return extra


def graph_ok(trace):
    nodes = trace["nodes"]
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 256:
        return False
    root = trace.get("root")
    if type(root) is not int or not 0 <= root < len(nodes):
        return False
    if nodes[root]["output"] != trace["source"]["statement"]:
        return False
    for i, node in enumerate(nodes):
        if node.get("id") != i:
            return False
        for key in ("output", "inputs", "kind"):
            if key not in node:
                return False
        for j in node["inputs"]:
            if type(j) is not int or not 0 <= j < i:
                return False
    return True


def independent_reason(trace, p1_by_label):
    source = trace["source"]
    if source["dv"] or source["active_dv"]:
        return "OUTSIDE_NO_DV_INTERFACE"
    used = {node["label"] for node in trace["nodes"] if "label" in node}
    for label in used:
        row = p1_by_label.get(label)
        if row is not None and row.get("dv"):
            return "OUTSIDE_USED_CONTRACT_NO_DV_INTERFACE"
    if extra_hypotheses(trace):
        return "OUTSIDE_MANDATORY_HYPOTHESIS_INTERFACE"
    return None


def ordinary_ready_blockers(trace, p1_by_label):
    """Declared TRACE_READY / constructor prerequisites. Not a new interface."""
    blockers = []
    source = trace["source"]
    if trace.get("terminal") != "NATIVE_VERIFIED":
        blockers.append("not_native_verified")
    if not graph_ok(trace):
        blockers.append("incomplete_or_malformed_graph")
    if source["dv"] or source["active_dv"]:
        blockers.append("source_or_active_dv")
    floats = [h["statement"][0] for h in source["floating"]]
    if len(floats) != 3:
        blockers.append("not_three_mandatory_floats")
    elif len(set(floats)) != 1 or floats[0] not in ("class", "wff"):
        blockers.append("nonhomogeneous_or_nonpacket_floats")
    if extra_hypotheses(trace):
        blockers.append("extra_active_hypothesis")
    used = {node["label"] for node in trace["nodes"] if "label" in node}
    if any(p1_by_label.get(label, {}).get("dv") for label in used):
        blockers.append("used_assertion_dv")
    return blockers
