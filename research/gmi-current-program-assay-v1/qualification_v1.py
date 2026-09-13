"""Run only the fixed exposed controls in PROTOCOL_V1, retaining full native records."""
from call_capture_v1 import V2, capture, summarize
from legacy_terminal_v1 import original_control
from native_source_v1 import load
from program_controls_v1 import run as program_run


def check_split(native, row):
    spec = native.ecology.REGISTRY["E_smooth3"]
    fed = {call["args"][0] for call in row["calls"] if call["method"] == "feedback"}
    scored = set(native.smooth.UNSEEN[4:] if row["intervention"] == V2[-1] else native.smooth.UNSEEN)
    if fed & scored or spec["criterion"] != "unseen":
        raise ValueError("feedback/scoring overlap in declared V2 unseen assay")
    return {"actual_feedback_inputs": sorted(fed), "scored_inputs": sorted(scored)}


def run():
    native = load()
    genotype = native.zoo.program_search(grammar=1, budget=32)
    spec = native.ecology.REGISTRY["E_smooth3"]
    rows = [capture(native, spec, genotype, j) for j in V2]
    family = summarize(rows, V2)
    if family["status"] != "COMPLETE_EXPOSED_ASSAY":
        raise ValueError("native no-alarm V2 control incomplete")
    for row in rows:
        row["scoring_split"] = check_split(native, row)
    failed = capture(native, spec, genotype, "standard", fail_at=4)
    if failed["status"] != "ERROR" or len(failed["charge_events"]) != 4:
        raise ValueError("failed-call accounting control not exercised")
    if not any(c["method"] == "feedback" and c["status"] == "ERROR" for c in failed["calls"]):
        raise ValueError("fault must interrupt charged native feedback, not only allocation")
    incomplete = [failed] + rows[1:]
    refused = summarize(incomplete, V2)
    if refused["status"] != "UNRESOLVED_INCOMPLETE":
        raise ValueError("failed call promoted")
    legacy_bad = original_control(native, False)
    legacy_good = original_control(native, True)
    if legacy_bad["original_full_result"]["terminal"] != "NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE":
        raise ValueError("historical countercontrol no longer matches source")
    if legacy_bad["successor_terminal"] != "UNRESOLVED_INCOMPLETE":
        raise ValueError("successor promoted missing evidence")
    return {"schema": "CurrentProgramAssayQualificationV1", "status": "QUALIFIED_EXPOSED_APPARATUS",
            "program_state_control": program_run(native), "v2_calls": rows, "family": family,
            "failed_call": failed, "failed_family_refusal": refused,
            "historical_incomplete_control": legacy_bad, "historical_complete_control": legacy_good,
            "native_call_scope": "six registered exposed ecology calls plus one interrupted call; no campaign",
            "scientific_verdict": "NO_NEW_METHOD_OR_TRANSFER_OR_LIFETIME_CLAIM"}
