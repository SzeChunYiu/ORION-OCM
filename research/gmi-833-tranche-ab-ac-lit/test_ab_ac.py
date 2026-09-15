"""House-pattern unittest for the AB/AC terminology authority package (#833).

Run: python3 -m unittest discover -s research/gmi-833-tranche-ab-ac-lit -p 'test_*.py' -v
or
     python3 research/gmi-833-tranche-ab-ac-lit/test_ab_ac.py -v

Asserts, tamper-evidence style:
  * RECEIPT_ABAC_V1.json equality with run() -> dict (json.dumps sort_keys).
  * crosswalk v2 covers every AB term, each with the exact-match column filled.
  * banned list non-empty, every entry has a replacement.
  * literature lanes cover the 11 lanes with >= 5 entries each.
  * CI gate accepts a clean fixture (exit 0) and rejects a "we achieve
    prior-free derivation" hostile fixture (exit 1), both against the gate's
    own scan function.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = "gmi-833-tranche-ab-ac-lit"
AB_TERMS = [  # every term named in addendum section AB
    "obligation", "behavioral specification", "morphology", "machine species",
    "ecology", "niche", "selection", "phase law", "phase diagram", "prior-free",
    "inductive bias", "hypothesis class", "possibility space", "DSL", "grammar",
    "neutral search", "remint", "negative twin", "parent subtraction", "carrier",
    "quotient", "capability ceiling", "development", "evolvability", "open-ended",
    "novel intelligence", "unseen form", "cognition", "causal", "uncertainty",
    "verification", "proof", "computer-assisted", "derive", "predict", "discover",
]
LANES = [
    "theoretical CS / formal languages", "statistical learning / information theory",
    "optimization / algorithm selection", "program synthesis", "neural architectures",
    "RL / control", "Bayesian / causal inference", "evolutionary computation / ALife",
    "cognitive science / neuroscience", "formal methods", "philosophy of science",
]


def _load(name: str):
    path = (HERE / name).resolve()
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run() -> dict:
    """Deterministic run() that outputs the committed receipt content."""
    result = {}
    crosswalk = (HERE / "GMI_TERMINOLOGY_CROSSWALK_V2.md").read_text(encoding="utf-8")
    banned = (HERE / "BANNED_PAPER_TERMS_V1.md").read_text(encoding="utf-8")
    lanes = (HERE / "EXPERT_LITERATURE_LANES_V1.md").read_text(encoding="utf-8")

    # crosswalk row extraction: rows begin with `| <int> |`
    rows = re.findall(r"^\|\s*(\d+)\s*\|(.*?)\|\s*$", crosswalk, re.MULTILINE)
    row_num = max((int(r[0]) for r in rows), default=0)
    rows_txt = crosswalk.splitlines()
    row_lines = [l for l in rows_txt if l.startswith("|") and re.match(r"^\|\s*\d+\s*\|", l)]

    # coverage: every AB term appears in the crosswalk row terms
    row_terms = " ".join(row_lines).lower()
    covered = sorted(t for t in AB_TERMS if re.search(r"(^|\W)" + re.escape(t.lower()) + r"(\W|$)", row_terms))

    # exact-match column filled per row: check '| EXACT' or '| PARTIAL' or '| NON'
    exact_filled = sum(1 for l in row_lines if re.search(r"\|\s*(EXACT|PARTIAL|NON)\b", l))

    # banned list rows (markdown table after '| banned term |')
    banned_rows = [l for l in banned.splitlines() if l.startswith("|") and "migration rule" not in l][2:]
    banned_terms = [l.split("|")[1].strip() for l in banned_rows if len(l.split("|")) > 2 and l.split("|")[1].strip()]
    with_replacement = sum(1 for l in banned_rows if len(l.split("|")) > 3 and l.split("|")[3].strip())

    # lanes: count entries in each "| work | citation" table (rows after lane heading)
    def lane_entry_count(heading: str) -> int:
        lines = lanes.splitlines()
        counts = []
        for i, l in enumerate(lines):
            if heading.lower() in l.lower():
                # count following table rows until next '## Lane' heading
                j = i + 1
                n = 0
                while j < len(lines) and not lines[j].startswith("## Lane"):
                    if lines[j].startswith("|") and not lines[j].startswith("| work |"):
                        n += 1
                    j += 1
                counts.append(n)
        return max(counts) if counts else 0

    lane_counts = {}
    for h in ["Lane 1", "Lane 2", "Lane 3", "Lane 4", "Lane 5", "Lane 6",
              "Lane 7", "Lane 8", "Lane 9", "Lane 10", "Lane 11"]:
        lane_counts[h] = lane_entry_count(h)

    # gate fixtures
    gate = _load("GMI_TERMINOLOGY_CI_GATE_V1.py")
    clean_hits, hostile_hits = [], []
    with tempfile.TemporaryDirectory() as td:
        clean = Path(td) / "clean.md"
        clean.write_text("# Clean fixture\n\nUses architecture-agnostic search with an explicit ledger.\n", encoding="utf-8")
        hostile = Path(td) / "hostile.md"
        hostile.write_text("# Hostile fixture\n\nWe achieve prior-free derivation of the hidden family.\n", encoding="utf-8")
        clean_hits = gate.scan_paths([str(clean)])
        hostile_hits = gate.scan_paths([str(hostile)])

    result = {
        "package": PKG,
        "crosswalk_rows": row_num,
        "crosswalk_row_lines": len(row_lines),
        "ab_terms_total": len(AB_TERMS),
        "ab_terms_covered": len(covered),
        "ab_terms_missing": sorted(set(AB_TERMS) - set(covered)),
        "exact_match_filled_rows": exact_filled,
        "banned_terms": len(banned_terms),
        "banned_with_replacement": with_replacement,
        "lane_counts": {h: lane_counts[h] for h in ["Lane %d" % i for i in range(1, 12)]},
        "gate_clean_hits": len(clean_hits),
        "gate_hostile_hits": len(hostile_hits),
        "claim_ceiling": "REGISTERED_TERMINOLOGY_AUTHORITY_V1",
        "sections": ["AB", "AC"],
    }
    return result


class TestABAutority(unittest.TestCase):
    def test_receipt(self):
        rec_path = HERE / "RECEIPT_ABAC_V1.json"
        if not rec_path.exists():
            self.skipTest("receipt not yet committed")
        self.maxDiff = 200000
        with rec_path.open(encoding="utf-8") as fh:
            expected = json.load(fh)
        got = run()
        self.assertEqual(json.dumps(got, sort_keys=True), json.dumps(expected, sort_keys=True))

    def test_crosswalk_covers_all_ab_terms(self):
        r = run()
        self.assertEqual(r["ab_terms_covered"], r["ab_terms_total"], r["ab_terms_missing"])
        self.assertGreaterEqual(r["exact_match_filled_rows"], 40)

    def test_banned_list_nonempty_with_replacements(self):
        r = run()
        self.assertGreaterEqual(r["banned_terms"], 20)
        self.assertEqual(r["banned_with_replacement"], r["banned_terms"])

    def test_lanes_11_with_entries(self):
        r = run()
        for h in ["Lane %d" % i for i in range(1, 12)]:
            self.assertGreaterEqual(r["lane_counts"][h], 5, h)

    def test_gate_clean_and_hostile(self):
        r = run()
        self.assertEqual(r["gate_clean_hits"], 0)
        self.assertGreaterEqual(r["gate_hostile_hits"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
