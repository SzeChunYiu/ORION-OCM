"""Replay saved-witness controls using the bound archive; no search or Git required."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_recovery


def archived_sources(_repo, binding):
    expected = {row["path"]: row["sha256"] for row in binding["source_files"]}
    with tarfile.open(Path(__file__).with_name("HISTORICAL_SOURCE_V1.tar.gz"), "r:gz") as tar:
        members = tar.getmembers()
        if len(members) != len(expected) or {m.name for m in members} != set(expected):
            raise ValueError("source archive member coverage mismatch")
        result = {}
        for member in members:
            if not member.isfile():
                raise ValueError("source archive must contain regular files only")
            raw = tar.extractfile(member).read()
            if hashlib.sha256(raw).hexdigest() != expected[member.name]:
                raise ValueError("source archive content binding mismatch")
            result[member.name] = raw
    return result


def prepare_archived(packet, output):
    original = prepare_recovery.source_bytes
    prepare_recovery.source_bytes = archived_sources
    try:
        return prepare_recovery.prepare(None, packet, output)
    finally:
        prepare_recovery.source_bytes = original


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=Path(__file__).resolve().parent.parent/
        "machine-intelligence-morphogenesis-v1/evidence/b6-corrected-20260913")
    parser.add_argument("--witness", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if not args.prepare_only and args.witness is None:
        parser.error("--witness is required except with --prepare-only")
    args.output.mkdir(parents=True, exist_ok=False)
    print(json.dumps(prepare_archived(args.packet, args.output/"prepared"), indent=2, sort_keys=True))
    if not args.prepare_only:
        subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).with_name("verify_witness.py")),
                        "--prepared", str(args.output/"prepared"), "--witness", str(args.witness),
                        "--output", str(args.output/"VERIFICATION.json")], check=True)
