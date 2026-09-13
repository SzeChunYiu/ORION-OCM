#!/usr/bin/env python3
"""Verify this frozen packet and reproduce V2 adjudication in a new directory."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    packet = Path(__file__).resolve().parent
    manifest = json.loads((packet / "MANIFEST.json").read_text())
    for row in manifest["files"]:
        source = packet / row["path"]
        if source.stat().st_size != row["bytes"] or sha(source) != row["sha256"]:
            raise SystemExit("INPUT_INTEGRITY_FAILED: " + row["path"])
    inputs = packet / "microscopes/results"
    records = {p.name: json.loads(p.read_text()) for p in inputs.glob("*.json")}
    for name, record in records.items():
        encoded = json.dumps(
            {k: v for k, v in record.items() if k != "receipt_sha256"},
            sort_keys=True, default=str).encode()
        if hashlib.sha256(encoded).hexdigest() != record["receipt_sha256"]:
            raise SystemExit("RECEIPT_INTEGRITY_FAILED: " + name)
    sources = {r["receipt_sha256"] for r in records.values()
               if r["schema"] == "StageB6DevelopmentSourceV1"}
    for name, record in records.items():
        source_id = record.get("seeding", {}).get("source_receipt_sha256")
        if source_id is not None and source_id not in sources:
            raise SystemExit("SOURCE_REFERENCE_MISSING: " + name)
    if args.output_dir.exists():
        raise SystemExit("REFUSED: output directory must be new")
    args.output_dir.mkdir(parents=True)
    for name, record in records.items():
        if record["schema"] == "StageB6DevelopmentArmV1":
            shutil.copyfile(inputs / name, args.output_dir / name)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(
        "frozen_b6_scorer", packet / "gmi_microscope/b6_adjudicate.py")
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    scorer.RES = str(args.output_dir)
    with contextlib.redirect_stdout(io.StringIO()):
        result = scorer.adjudicate("billy", (0, 1, 2))
    name = "STAGE_B6_DEV_ADJUDICATION_V2_billy.json"
    expected, actual = packet / "outputs" / name, args.output_dir / name
    expected_data = json.loads(expected.read_text())
    actual_data = json.loads(actual.read_text())
    # Only these provenance locators contain the invocation's absolute output path.
    field = "identity_unknown_receipt_files"
    for value in actual_data["duplicate_experiments"][field]:
        if Path(value).parent.resolve() != args.output_dir.resolve():
            raise SystemExit("UNEXPECTED_PROVENANCE_LOCATOR")
    for data in (expected_data, actual_data):
        data["duplicate_experiments"][field] = [
            Path(value).name for value in data["duplicate_experiments"][field]]
    if actual_data != expected_data:
        raise SystemExit("REPLAY_MISMATCH")
    print(json.dumps({"replay": "EXACT_JSON_EXCEPT_OUTPUT_DIRECTORY_LOCATORS",
                      "output_sha256": sha(actual),
                      "terminal": result["terminal"],
                      "input_arm_files": len(manifest["present_arm_files"]),
                      "missing_arm_files": len(manifest["missing_arm_files"])}))


if __name__ == "__main__":
    main()
