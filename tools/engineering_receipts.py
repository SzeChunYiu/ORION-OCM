"""Select immutable source-addressed engineering runs; never inherit scientific authority."""
from __future__ import annotations
import json
from pathlib import Path
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET
import engineering_predecessor as P
import runtime_revision_receipts_v4 as V4

DIRECTORY = P.DIRECTORY
CURRENT = DIRECTORY + "/CURRENT_ENGINEERING.json"
SCHEMA = "ocm.current-engineering.v1"
SCOPE = {"status": "ENGINEERING_REGRESSION_ONLY", "protected_reevaluation": "NOT_RUN",
         "scientific_promotion": "NOT_ESTABLISHED", "independent_replication": "NOT_RUN",
         "legacy_recipe_execution": "NOT_EXECUTED"}


def source_id(inventory):
    return V4.digest(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode())


def verify_source_archive(root, inventory):
    path = DIRECTORY + "/sources/" + source_id(inventory) + ".zip"
    with zipfile.ZipFile(V4.path_in(root, path)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(inventory):
            raise V4.ReceiptError("archived engineering source inventory changed")
        for name in names:
            if V4.digest(archive.read(name)) != inventory[name]:
                raise V4.ReceiptError("archived engineering source changed: " + name)
    return {"path": path, "sha256": V4.sha(root, path)}


def archive_current(root, inventory):
    """Preserve only the existing source inventory, shared by runs of that source."""
    path = V4.path_in(root, DIRECTORY + "/sources/" + source_id(inventory) + ".zip")
    if not path.exists():
        data = {p: V4.raw(root, p) for p in inventory}
        if any(V4.digest(v) != inventory[p] for p, v in data.items()):
            raise V4.ReceiptError("source changed before archiving")
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, value in sorted(data.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, value)
    return verify_source_archive(root, inventory)


def gates(root, run):
    """Adapt the pinned V4 gate recipes only by using new immutable artifact paths."""
    config = V4.CurrentReceipts(root).config
    result = {}
    for label, spec in config["validation_requirements"].items():
        artifact = run + "/" + Path(spec["artifact_path"]).name
        argv = [a if not a.startswith("--junitxml=") else "--junitxml=" + artifact for a in spec["argv"]]
        result[label] = {"argv": argv, "artifact_path": artifact, "minimum_tests": spec["minimum_tests"],
                         "log_path": run + "/" + label + ".log"}
    return result


def build_record(root, run, inventory, executions, predecessor):
    artifacts = {e[k]: V4.sha(root, e[k]) for e in executions for k in ("artifact_path", "log_path")}
    return {"schema": SCHEMA, **SCOPE, "source_id": source_id(inventory), "run": run,
            "current_source_inventory": inventory, "predecessor_anchor": predecessor,
            "source_archive": verify_source_archive(root, inventory),
            "executions": executions, "validation_artifacts": artifacts,
            "scope": "Recorded engineering execution attestation, not independent evaluation or cryptographic proof of execution."}


def _junit(root, spec):
    try:
        report = ET.fromstring(V4.raw(root, spec["artifact_path"]))
        suites, cases = list(report.iter("testsuite")), list(report.iter("testcase"))
        counts = {k: sum(int(s.attrib[k]) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
    except (ET.ParseError, KeyError, TypeError, ValueError) as exc:
        raise V4.ReceiptError("invalid engineering JUnit") from exc
    if (not suites or counts["tests"] != len(cases) or len(cases) < spec["minimum_tests"]
            or any(counts[k] for k in ("failures", "errors", "skipped"))
            or any(any(c.find(tag) is not None for tag in ("failure", "error", "skipped")) for c in cases)):
        raise V4.ReceiptError("required engineering JUnit gate did not pass")
    return counts


def verify_record(root, path, expected_sha=None):
    root = Path(root)
    V4.relative_path(path)
    if expected_sha is not None and V4.sha(root, path) != expected_sha:
        raise V4.ReceiptError("selected engineering receipt changed")
    receipt = V4.read_json(root, path)
    if receipt.get("schema") != SCHEMA or any(receipt.get(k) != v for k, v in SCOPE.items()):
        raise V4.ReceiptError("engineering receipt has invalid authority")
    inventory = V4.source_inventory(root)
    sid = source_id(inventory)
    run = receipt.get("run", "")
    pattern = re.escape(DIRECTORY) + r"/runs/" + sid + r"/[0-9a-f]{16}"
    if (receipt.get("current_source_inventory") != inventory or receipt.get("source_id") != sid
            or not re.fullmatch(pattern, run) or path != run + "/RECEIPT.json"):
        raise V4.ReceiptError("current engineering source/run binding DRIFT")
    if receipt.get("source_archive") != verify_source_archive(root, inventory):
        raise V4.ReceiptError("engineering source archive binding changed")
    if receipt.get("predecessor_anchor") != P.verify(root):
        raise V4.ReceiptError("engineering predecessor binding changed")
    requirements = gates(root, run)
    executions = receipt.get("executions")
    if not isinstance(executions, list) or len(executions) != len(requirements):
        raise V4.ReceiptError("missing engineering gate")
    found = set(); artifacts = set(); summaries = {}
    for execution in executions:
        label = execution.get("label")
        if label not in requirements or label in found:
            raise V4.ReceiptError("undeclared or duplicate engineering gate")
        found.add(label); spec = requirements[label]
        if (type(execution.get("exit_code")) is not int or execution["exit_code"] != 0
                or any(execution.get(k) != spec[k] for k in ("argv", "artifact_path", "log_path"))):
            raise V4.ReceiptError("engineering gate command or exit status changed")
        artifacts.update((spec["artifact_path"], spec["log_path"]))
        summaries[label] = _junit(root, spec)
    if set(receipt.get("validation_artifacts", {})) != artifacts:
        raise V4.ReceiptError("engineering artifact inventory changed")
    for artifact, expected in receipt["validation_artifacts"].items():
        if V4.sha(root, artifact) != expected:
            raise V4.ReceiptError("engineering artifact changed: " + artifact)
    return {"receipt_path": path, "receipt_sha256": V4.sha(root, path), "source_id": sid,
            "junit": summaries, "current_scientific_promotion": "NOT_ESTABLISHED", **SCOPE}


def verify(root, milestone=1):
    if type(milestone) is not int or milestone not in range(1, 13):
        raise V4.ReceiptError("unknown milestone")
    pointer = V4.read_json(root, CURRENT)
    if set(pointer) != {"schema", "receipt_path", "receipt_sha256"} or pointer["schema"] != SCHEMA:
        raise V4.ReceiptError("invalid current engineering selector")
    result = verify_record(root, pointer["receipt_path"], pointer["receipt_sha256"])
    return {"milestone": milestone, **result}


def select(root, path):
    """Only the current pointer is replaceable; run artifacts are exclusively created."""
    result = verify_record(root, path)
    pointer = {"schema": SCHEMA, "receipt_path": path, "receipt_sha256": result["receipt_sha256"]}
    target = V4.path_in(Path(root), CURRENT)
    temporary = target.with_name(target.name + "." + uuid.uuid4().hex + ".tmp")
    with temporary.open("xb") as output: output.write(P.encoded(pointer))
    temporary.replace(target)
    return result


def revision_main(root, argv, milestone):
    if argv != ["--verify"]:
        print("Current engineering receipts require an actual recorded replay; use tools/record_engineering_revision.py.")
        return 2
    try:
        result = verify(root, milestone)
        print(f"M{milestone} current engineering verified: {result['source_id']}; historical custody only")
        return 0
    except (V4.ReceiptError, OSError, KeyError, TypeError, ValueError, zipfile.BadZipFile) as exc:
        print("CURRENT ENGINEERING REFUSED:", exc)
        return 1
