"""Independent authority for continuation of the already-open V2 material episode."""
from hashlib import sha256
from pathlib import Path
import json
import time
import acquisition_contract as c
import materialize_objects as objects

PINS = {
 "ACQUISITION.json": "ae12fc94b684efe07dbb0dc41bb2f5d451fbeafed86220947df2d2ffd2b3e636",
 "STARTED.json": "735f3bca0600a55cd5ddc6c7678f79ea5399ef7b1fd0ce6ba007958e73b4f3af",
 "SOURCE-FREEZE.json": "c348cf7b8a6cfd4bccff20e2b6d2bb5de94cdeda4e0c7e52c89f8802a2d46a03",
 "REGISTRATION-REFERENCE.json": "0553c116f915109a2b865924c34dcba8fe3af14032c5228a1a9423e50aa4fb63",
 "LOCK-INPUT.json": "a9734d7e6ab3b170dc2953cd2557c7cb23b3eb03eb9faedac47c1833935bc900",
 "ROWS-DECLARED.json": "5754f61837015642111d1e71fb9a036365000c9c9ffc06e1734d9a3c8de6e9e5",
 "ROWS-AFTER-ACQUISITION.json": "cfc94750fe94be844020cbd4335d96eec8376eb12656042e5a9fe9cc3ba9016f",
 "lake-manifest.json": c.LOCK}
DEADLINE = 390867.56895429
TREE = "8bb1c43c8f26f1c127591dddeffdead2b5094eb7"
GIT = "c3edb15c9715b79fcfb1fa978256cdfc14a9ad72a4a8d5680a9fc5ebc6a57e0e"


def read(path, expected=None):
    record = c.record(path); raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != record["sha256"] or (expected and record["sha256"] != expected):
        raise ValueError("INPUT_IDENTITY: " + str(path))
    return json.loads(raw), record


def recheck(records):
    for value in records:
        if c.record(value["path"]) != value:
            raise ValueError("INPUT_DRIFT: " + value["path"])


def clock(start, now=None, boot=None):
    now = time.monotonic() if now is None else now
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip() if boot is None else boot
    left = c.remaining_episode(start, now, boot)
    if left <= 0:
        raise TimeoutError("WHOLE_EPISODE_DEADLINE")
    return left


def process_ok(receipt):
    dispatch = receipt.get("dispatch", {})
    if (receipt.get("terminal") != "COMPLETED" or type(receipt.get("returncode")) is not int
        or receipt["returncode"] != 0 or receipt.get("evidence_complete") is not True
        or dispatch.get("state") != "STARTED" or dispatch.get("attempted") is not True
        or type(dispatch.get("pid")) is not int or dispatch["pid"] <= 0
        or not all(receipt.get("cleanup", {}).get(k) is True
                   for k in ("reaped", "members_empty", "controllers_removed"))):
        raise ValueError("PROCESS_CUSTODY")


def acquired(episode, frozen):
    for name, pair in frozen["sources"].items():
        item = pair["frozen"]
        if Path(item["path"]) != episode / "sources" / (name + ".py"):
            raise ValueError("HISTORICAL_SOURCE_PATH")
        recheck([item])
    module = c.load_source(episode / "sources/acquisition_git.py", "materialize_acquisition_custody")
    value, binding = read(episode / "materials/RESULT.json")
    if module.revalidate(value, episode / "materials") != dict(terminal="MATERIAL_BYTES_REVALIDATED", packages=9):
        raise ValueError("ACQUIRED_CUSTODY")
    return value, binding


def authorize(registrar, episode, bare):
    episode = Path(episode).absolute(); bare = Path(bare).absolute()
    if episode.resolve(strict=True) != episode or bare.resolve(strict=True) != bare:
        raise ValueError("INPUT_PATH")
    values = {}; inputs = []
    for name, digest in PINS.items():
        value, record = read(episode / name, digest); values[name] = value; inputs.append(record)
    start = values["STARTED.json"]
    if start["whole_deadline_monotonic"] != DEADLINE or start["registration_seal_sha256"] != c.SEAL:
        raise ValueError("ORIGINAL_EPISODE")
    clock(start)
    seal, assignments, policy = c.registration(registrar)
    reference = dict(seal=seal, assignments=assignments, policy=policy)
    if c.canonical(reference) != c.canonical(values["REGISTRATION-REFERENCE.json"]):
        raise ValueError("REGISTRATION_REFERENCE")
    inputs.append(seal)
    registration_seal, _ = read(seal["path"])
    for name, item in registration_seal["files"].items():
        inputs.append(dict(path=str(Path(registrar) / name), **item))
    historical = values["SOURCE-FREEZE.json"]
    process_ok(values["ACQUISITION.json"]["resource"])
    if values["ACQUISITION.json"]["terminal"] != "MATERIAL_READY":
        raise ValueError("ACQUISITION_NOT_READY")
    result, result_binding = acquired(episode, historical); inputs.append(result_binding)
    if c.canonical(result) != c.canonical(values["ACQUISITION.json"]["worker"]):
        raise ValueError("ACQUISITION_RESULT")
    for pair in historical["sources"].values(): inputs.append(pair["frozen"])
    for value in values["ACQUISITION.json"]["resource"]["raw"].values(): inputs.append(value)
    if c.record("/usr/bin/git")["sha256"] != GIT or c.record(historical["interpreter"]["path"])["sha256"] != c.PYTHON:
        raise ValueError("TOOL_IDENTITY")
    git, _ = read(Path(registrar) / "GIT.json")
    if git["commit"] != c.COMMIT or git["tree"] != TREE or str(bare) != git["argv"][git["argv"].index("-C") + 1]:
        raise ValueError("REGISTERED_CORPUS")
    materials = [dict(name="corpus", bare_path=str(bare), commit=c.COMMIT, tree=TREE,
                      files=objects.file_map(bare, start["whole_deadline_monotonic"]))]
    materials.extend({k: row[k] for k in ("name", "bare_path", "commit", "tree", "files")}
                     for row in result["packages"])
    if len(materials) != 10 or len({r["name"] for r in materials}) != 10:
        raise ValueError("MATERIAL_DENOMINATOR")
    recheck(inputs); clock(start)
    return dict(start=start, assignments=assignments, policy=policy, inputs=inputs, materials=materials,
                episode=str(episode), registration=str(Path(registrar)), acquisition_phase_sha256=PINS["ACQUISITION.json"])
