#!/usr/bin/env python3
"""Verify full unit custody and compare the entire fresh static payload."""
from pathlib import Path
import json
import os
import stat
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
from contract_v1 import require, same, sha, strict_json

HERE = Path(__file__).resolve().parent


def verify_manifest(base=HERE):
    found = set()
    def visit(path):
        with os.scandir(path) as entries:
            for entry in entries:
                mode = entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode): visit(Path(entry.path))
                else:
                    require(stat.S_ISREG(mode), "nonregular unit entry")
                    found.add(Path(entry.path).relative_to(base).as_posix())
    visit(base)
    manifest = strict_json((base / "MANIFEST.json").read_bytes())
    same(sorted(found), sorted(set(manifest["files"]) | {"MANIFEST.json"}), "unit membership drift")
    for name, row in manifest["files"].items():
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts, "unsafe manifest path")
        data = (base / path).read_bytes()
        require(len(data) == row["bytes"] and sha(data) == row["sha256"], "unit hash drift: " + name)
    return manifest


def replay(base=HERE):
    manifest_before = (base / "MANIFEST.json").read_bytes()
    verify_manifest(base)
    receipt_before = (base / "CONSUMER_CENSUS_RECEIPT_V1.json").read_bytes()
    require((base / "MANIFEST.json").read_bytes() == manifest_before, "manifest changed before worker")
    with tempfile.TemporaryDirectory(prefix="b6-census-bytecode-") as cache:
        cmd = [sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache]
        if sys.flags.optimize: cmd.append("-O")
        cmd.append(str(base / "check_census_v1.py"))
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    require(done.returncode == 0 and not done.stderr, "fresh static worker failed: " + done.stderr)
    fresh = strict_json(done.stdout)
    require((base / "MANIFEST.json").read_bytes() == manifest_before, "manifest changed during worker")
    verify_manifest(base)
    same(fresh, strict_json(receipt_before), "complete census receipt differs")
    return {"status": "FULL_STATIC_PAYLOAD_REPLAY_PASS", "new_ecology_search_timing_calls": 0,
            "receipt_sha256": sha(receipt_before),
            "independent_graph_comparisons": fresh["independent_oracle_row_comparisons"]}


if __name__ == "__main__":
    print(json.dumps(replay(), sort_keys=True))
