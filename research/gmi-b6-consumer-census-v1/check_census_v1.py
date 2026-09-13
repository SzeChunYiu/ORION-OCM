#!/usr/bin/env python3
"""Emit the complete portable static receipt; never execute a saved genotype."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from census_v1 import run

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))
