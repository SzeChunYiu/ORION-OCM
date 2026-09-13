"""Check complete frozen evidence custody and retained outcomes; no ecology runs."""
import hashlib
import importlib.util
import json
from pathlib import Path

BINDINGS = {
    "gmi-witness-recovery-v1": "28266dbadd899acc76364d3efa5d578a080f165cd8dffc14a5ffd70bae29668d",
    "gmi-witness-mechanism-v1": "01e813c8de45ac90c847142ab31921e8593039b1acf7130d7a014f968f5d31e9",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(root):
    counts = {}
    for name, digest in BINDINGS.items():
        unit = root / name
        raw = (unit / "MANIFEST.json").read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, name + " manifest changed")
        entries = json.loads(raw)["files"]
        names = [row["path"] for row in entries]
        require(len(names) == len(set(names)), "duplicate payload path")
        for row in entries:
            path = unit / row["path"]
            require(path.resolve().is_relative_to(unit.resolve()), "external payload")
            payload = path.read_bytes()
            require(len(payload) == row["bytes"], row["path"] + " length changed")
            require(hashlib.sha256(payload).hexdigest() == row["sha256"], row["path"] + " changed")
        counts[name] = len(entries)
    return counts


if __name__ == "__main__":
    research = Path(__file__).resolve().parent.parent
    counts = validate(research)
    checker = research / "gmi-witness-mechanism-v1/check_mechanism_record.py"
    spec = importlib.util.spec_from_file_location("retained_mechanism_record", checker)
    module = importlib.util.module_from_spec(spec)
    exec(compile(checker.read_bytes(), str(checker), "exec"), module.__dict__)
    module.main()
    print(json.dumps({"verified_payload_files": counts, "ecology_calls_executed": 0}, sort_keys=True))
