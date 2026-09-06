#!/usr/bin/env python3
"""Verify immutable historical V5 custody; never regenerate or promote its receipt."""
from __future__ import annotations

import json
import sys
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/provenance/M12_PAIRED_RECEIPT_V5.json"


def main(argv: list[str]) -> int:
    if argv != ["--verify"]:
        print(json.dumps({"status": "REFUSED_HISTORICAL_V5_GENERATION",
                          "reason": "Verification only; frozen receipts cannot be regenerated"}))
        return 2
    try:
        from engineering_predecessor import verify
        predecessor = verify(ROOT)
    except (ImportError, OSError, KeyError, TypeError, ValueError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "ARCHIVED_V5_CUSTODY_REFUSED", "reason": str(exc),
                          "current_scientific_promotion": "NOT_ESTABLISHED"}))
        return 1
    print(json.dumps({"status": "ARCHIVED_V5_CUSTODY_VERIFIED",
                      "receipt": "docs/provenance/M12_PAIRED_RECEIPT_V5.json",
                      "current_scientific_promotion": "NOT_ESTABLISHED",
                      "protected_reevaluation": "NOT_RUN", "legacy_recipe_execution": "NOT_EXECUTED",
                      "predecessor": predecessor}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
