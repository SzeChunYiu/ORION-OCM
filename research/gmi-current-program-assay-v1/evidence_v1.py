"""Full retained-payload verification; native qualification is an explicit separate option."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import stat
from call_capture_v1 import V2, summarize, validate_charges
from legacy_terminal_v1 import terminal

HERE = Path(__file__).resolve().parent


def encoded(payload):
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()


def verify_manifest(root=HERE):
    anchor = (root / "MANIFEST_V1.json").read_bytes()
    manifest = json.loads(anchor)
    observed = {}
    def walk(directory):
        for entry in os.scandir(directory):
            path = Path(entry.path)
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):
                raise ValueError("symlink in unit")
            if stat.S_ISDIR(mode):
                walk(path)
            elif stat.S_ISREG(mode):
                relative = path.relative_to(root).as_posix()
                if relative != "MANIFEST_V1.json":
                    data = path.read_bytes()
                    observed[relative] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            else:
                raise ValueError("nonregular unit member")
    walk(root)
    if observed != manifest["files"]:
        raise ValueError("complete manifest membership/content mismatch")
    return anchor


def validate_payload(payload):
    if payload["schema"] != "CurrentProgramAssayQualificationV1":
        raise ValueError("unknown payload")
    if payload["status"] != "QUALIFIED_EXPOSED_APPARATUS":
        raise ValueError("unqualified record")
    rows = payload["v2_calls"]
    if summarize(rows, V2) != payload["family"]:
        raise ValueError("family summary mismatch")
    for row in rows + [payload["failed_call"]]:
        validate_charges(row)
        previous = 0
        for call in row["calls"]:
            a, b = call["charge_start"], call["charge_end"]
            if not 0 <= previous <= a <= b <= len(row["charge_events"]):
                raise ValueError("invalid exposed-call charge interval")
            previous = b
            if call["status"] not in ("RETURNED", "ERROR"):
                raise ValueError("incomplete exposed-call record")
        if row["calls"] and previous != len(row["charge_events"]):
            raise ValueError("unattributed final charge")
    failed = payload["failed_call"]
    if failed["status"] != "ERROR" or failed["final_ledger"]["upd"] <= 0:
        raise ValueError("failed native update witness absent")
    if summarize([failed] + rows[1:], V2) != payload["failed_family_refusal"]:
        raise ValueError("incomplete-call refusal mismatch")
    program = payload["program_state_control"]
    histories = [program["acquisition_history"], program["same_input_zero_label_control"]["history"]]
    for history in histories:
        events = []
        for step in history:
            events.extend(step["native_charge_events"])
            validate_charges({"charge_events": events, "final_ledger": step["native_ledger"]})
    if histories[0][-1]["native_ledger"] != program["acquisition_ledger"]:
        raise ValueError("acquisition ledger mismatch")
    baseline = program["checkpoint_sha256"]
    arms = program["arms"]
    for label in ("acquired", "sham", "restored"):
        if arms[label]["cloned_start_sha256"] != baseline or arms[label]["post_assignment_sha256"] != baseline:
            raise ValueError("pre-query restoration mismatch")
        if arms[label]["served"] != arms["acquired"]["served"]:
            raise ValueError("complete restored result mismatch")
    for arm in arms.values():
        if arm["cloned_start_sha256"] != baseline:
            raise ValueError("unequal initial joint checkpoint")
    old = [payload["historical_incomplete_control"], payload["historical_complete_control"]]
    for control in old:
        if terminal(control["original_full_result"]["tasks"], ("fixture",)) != control["successor_terminal"]:
            raise ValueError("terminal-control mismatch")
    return payload


def replay(native=False, root=HERE):
    anchor = verify_manifest(root)
    expected = gzip.decompress((root / "raw/QUALIFICATION_RECEIPT_V1.json.gz").read_bytes())
    payload = validate_payload(json.loads(expected))
    if native:
        from qualification_v1 import run
        observed = encoded(run())
        if observed != expected:
            raise ValueError("complete native payload differs from retained receipt")
    if verify_manifest(root) != anchor:
        raise ValueError("unit changed during replay")
    if encoded(payload) != expected:
        raise ValueError("noncanonical retained receipt")
    return payload
