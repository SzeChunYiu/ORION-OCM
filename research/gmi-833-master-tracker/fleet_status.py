#!/usr/bin/env python3
"""Fleet status aggregator for #833: JSON state where each tranche reports."""
from __future__ import annotations
import json, sys
from pathlib import Path

DEFAULT = {
  "A": "lane-835-foundations (PR #835)", "B": "tranche-b-audit", "C": "lane-835-foundations",
  "D": "lane-835-foundations", "E": "tranche-ef-grammar", "F": "tranche-ef-grammar",
  "G": "tranche-g-ecology", "H": "tranche-h-knownforms", "I": "tranche-ij-learnlaw",
  "J": "tranche-ij-learnlaw", "K": "tranche-kl-capdev", "L": "tranche-kl-capdev",
  "M": "tranche-m-cognition", "AA": "lanes+addenda", "AB": "tranche-ab-ac-lit",
  "AC": "tranche-ab-ac-lit", "AD": "master-tracker", "Z": "master-tracker+z-gates",
}

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    ledger = json.loads((root / "BOX_LEDGER_V1.json").read_text())
    total = 0; n_checked = 0
    rows = []
    for sec in ledger["sections"]:
        name = sec["section"].rstrip(".")
        cb = [b for b in sec["boxes"] if b.get("checked")]
        total += len(sec["boxes"]); n_checked += len(cb)
        rows.append({"section": name, "boxes": len(sec["boxes"]), "checked": len(cb),
                     "owner": DEFAULT.get(name, "unassigned")})
    return {"total_boxes": total, "checked": n_checked, "unchecked": total - n_checked,
            "pct": round(100.0 * n_checked / total, 2), "sections": rows}

if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
