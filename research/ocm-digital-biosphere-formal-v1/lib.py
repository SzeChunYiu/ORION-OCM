"""EB-F0 shared hashing, events, freeze gate. Python 3.8, stdlib only."""
from __future__ import annotations

import hashlib
import json
import os
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
FREEZE_NAME = "FREEZE_V1.json"
EVENTS = os.path.join(ROOT, "EVENTS.jsonl")

HASHED = (
    "lib.py",
    "parents.py",
    "kernels.py",
    "micro_earth.py",
    "theorems.py",
    "hostiles.py",
    "graph_agreement.py",
    "freeze_ebf0.py",
    "run_ebf0.py",
    "DEFINITIONS.md",
    "PARENT_LEDGER.md",
    "WORLD_STATE_AND_DYNAMICS_V1.json",
    "COGNITIVE_UNIT_CONTRACT_V1.json",
    "INHERITANCE_SOCIAL_CHANNELS_V1.json",
    "COARSE_GRAINING_INDIVIDUALITY_V1.json",
    "ASSAY_TRANSFER_CONTRACT_V1.json",
    "THEOREM_REGISTRY_V1.json",
    "HOSTILE_REGISTRY_V1.json",
    "EXACT_WORLD_REGISTRY_V1.json",
    "DUPLICATION_GUARD_V1.json",
)


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: str, obj) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, sort_keys=True, indent=1)
        fh.write("\n")
    return sha256_file(path)


def load_json(path: str):
    with open(path) as fh:
        return json.load(fh)


def code_files_sha256(root: str = ROOT) -> dict:
    out = {}
    for rel in HASHED:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            out[rel] = sha256_file(p)
    return out


def code_digest(root: str = ROOT) -> str:
    h = hashlib.sha256()
    for rel, sha in sorted(code_files_sha256(root).items()):
        h.update(rel.encode("utf-8") + b"\0" + sha.encode("utf-8") + b"\n")
    return h.hexdigest()


def event(kind: str, **kv) -> None:
    kv = dict(kv)
    kv.pop("ts", None)
    kv.pop("kind", None)
    line = dict(ts=now(), kind=kind, **kv)
    with open(EVENTS, "a") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")


def scored_certificates_exist(root: str = ROOT) -> list:
    hits = []
    d = os.path.join(root, "results")
    if not os.path.isdir(d):
        return hits
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json") and fn not in ("SMOKE.json",):
            hits.append(fn)
    return hits


def require_freeze(root: str = ROOT) -> dict:
    path = os.path.join(root, FREEZE_NAME)
    if not os.path.exists(path):
        raise SystemExit("REFUSED: EB-F0 freeze missing")
    freeze = load_json(path)
    digest = code_digest(root)
    if digest != freeze.get("code_digest"):
        raise SystemExit("REFUSED: code drift vs EB-F0 freeze")
    return freeze
