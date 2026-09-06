"""Explicit, exclusive engineering output; historical evidence is never overwritten."""
import argparse
import json
from pathlib import Path


def new_output_path(argv, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--out", required=True, type=Path, help="New engineering output file; must not already exist")
    path = parser.parse_args(argv).out
    if path.exists() or path.is_symlink():
        parser.error("output already exists; choose a new engineering evidence path")
    return path


def write_result(path: Path, result):
    data = json.dumps(result, indent=1, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(data)
