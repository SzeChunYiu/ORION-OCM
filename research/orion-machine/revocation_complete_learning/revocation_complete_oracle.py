#!/usr/bin/env python3
"""Exact finite oracle for the hand-proved RCL V0 theorem pack."""

from __future__ import annotations

import argparse
import json

from rcl_model import *  # re-exported for exact unit tests
from rcl_checks_core import *  # re-exported for exact unit tests
from rcl_checks_finish import *  # re-exported for exact unit tests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("--self-test is required")
    result = run_self_test()
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if result["terminal"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
