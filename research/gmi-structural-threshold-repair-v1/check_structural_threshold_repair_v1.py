#!/usr/bin/env python3
"""Standalone full receipt; native opcode incompatibility is explicitly unavailable."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from structural_threshold_analytic_v1 import run

if __name__ == "__main__":
    try:
        print(json.dumps(run(), indent=2, sort_keys=True))
    except ValueError as error:
        if str(error).startswith("UNVERIFIABLE:"):
            print(str(error), file=sys.stderr)
            raise SystemExit(2)
        raise
