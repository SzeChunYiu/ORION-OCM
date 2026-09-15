"""#602 V2 domain-basis closure executable."""
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
LEDGER = HERE / "V2_CLOSURE_LEDGER_V1.json"
RECEIPT = HERE / "RECEIPT_V1.json"
TERMINAL = "DOMAIN_BASIS_RECURSIVELY_HARDENED_AT_REGISTERED_SCOPE"
BOXES = [
    "All major candidate domains have explicit reduction disposition.",
    "No surviving candidate lacks carrier/operator/burden evidence.",
    "No known obvious paradigm sits outside the registry untested.",
]

def run():
    ledger = json.loads(LEDGER.read_text())
    checks = {
        "all_candidates_have_reduction_disposition": all(
            "disposition" in c and c["disposition"] for c in ledger["candidates"]
        ),
        "no_candidate_lacks_carrier_operator_burden": all(
            c.get("has_carrier") and c.get("has_operator") and c.get("has_burden_evidence")
            for c in ledger["candidates"]
        ),
        "no_obvious_paradigm_untested": all(
            p.get("tested") for p in ledger["paradigms_outside_registry_screen"]
        ),
    }
    out = {
        "schema": "GMIV2ClosureReceiptV1",
        "terminal": TERMINAL,
        "checks": checks,
        "n_domains": len(ledger["domains"]),
        "n_candidates": len(ledger["candidates"]),
        "n_paradigms_screened": len(ledger["paradigms_outside_registry_screen"]),
        "boxes": {b: True for b in BOXES} if all(checks.values()) else {b: False for b in BOXES},
        "all_v2_boxes_green": all(checks.values()) and len(ledger["domains"]) == 8,
        "forbidden_claims": ["ONTOLOGICAL_UNIVERSALITY"],
    }
    RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
