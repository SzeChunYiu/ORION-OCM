"""Standalone archived-source authority; independent of the portable grand helpers."""
from pathlib import Path
import hashlib
import json
HERE = Path(__file__).resolve().parent
SOURCE_REGISTER_SHA = "5478aef25c0f56ab226e4b1c9ef79834da99e084a63ae6da9ced66ecef82b81a"


def verify_sources(base=HERE):
    raw = (base / "SOURCE_PARENTS_V1.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_REGISTER_SHA:
        raise ValueError("source-register changed")
    register = json.loads(raw)
    for name, item in register["files"].items():
        data = (base / name).read_bytes()
        if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("archived source changed: " + name)
    return len(register["files"])
