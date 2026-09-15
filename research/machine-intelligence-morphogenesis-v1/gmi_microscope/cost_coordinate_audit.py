"""N: which cost coordinates does the corpus actually meter?

Section N lists sixteen cost coordinates every claim should meter, plus two
protocol rules.  The obvious way to check is to grep the receipts for words like
"cost" and "charge".  That is the method the B1 audit showed to be unsound, and
a first pass here reproduced the problem exactly: a substring scan reported
"exec" in 70% of 461 receipts, which counts the word "executed" in a prose note
as evidence of metered execution cost.

So this audit works at KEY level.  A coordinate counts as metered when a receipt
carries a KEY naming it -- `charge_resident`, `upd_e`, `search_compute` -- not
when the word appears somewhere in the text.  A key is a commitment by the
witness; a word in a note is not.

Validated against receipts whose answer is known before the counts are believed.
"""

import json
import glob
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "microscopes", "results")

# Section N's sixteen metering coordinates, with key patterns.  Patterns match
# whole key SEGMENTS (split on _ and camelCase boundaries), never free text.
COORDS = [
    ("build/acquisition",   [r"^build$", r"^acquisition$", r"^desc$", r"^c$", r"^held$", r"^hold$"]),
    ("training/development", [r"^train\w*$", r"^develop\w*$", r"^dev$", r"^fit$"]),
    ("serving/execution",   [r"^exec\w*$", r"^serve$", r"^serving$", r"^traversal$", r"^replay\w*$"]),
    ("memory/storage",      [r"^mem\w*$", r"^storage$", r"^store\w*$", r"^cells$", r"^states$", r"^entries$"]),
    ("retrieval/index",     [r"^retriev\w*$", r"^index\w*$", r"^lookup$", r"^nearest$", r"^probe\w*$"]),
    ("verification",        [r"^verif\w*$", r"^ver_e$", r"^check\w*$"]),
    ("update",              [r"^upd\w*$", r"^update\w*$"]),
    # NOT ^rev\w*$ -- that matched `revival` (311 keys, from REVIVAL_LEDGER) and
    # `revoke` (92, capability revocation), neither of which is revision cost.
    # It reported 81% of receipts metering unlearning, the highest of any
    # coordinate, which is what made it obviously wrong.
    ("revision/unlearning", [r"^revision$", r"^revisions$", r"^revise$",
                             r"^revised$", r"^rev_e$", r"^unlearn\w*$",
                             r"^forget\w*$"]),
    # NOT ^comm\w*$ -- that matched `committed`, `commit` and `commuting`.
    ("communication",       [r"^communication$", r"^traffic$", r"^messages?$",
                             r"^rounds$", r"^bandwidth$"]),
    ("precision",           [r"^precision$", r"^bits$", r"^frac\w*$"]),
    ("search/discovery",    [r"^search\w*$", r"^discovery$", r"^n_eval$", r"^evals?$"]),
    ("failed-candidate",    [r"^failed\w*$", r"^rejected$", r"^misses$", r"^losers?$"]),
    ("maintenance",         [r"^maintenance$", r"^maintain\w*$", r"^upkeep$"]),
    ("human/AI design input", [r"^design_input$", r"^human\w*$", r"^hand_registered$"]),
    ("physical counters",   [r"^wall\w*$", r"^cpu\w*$", r"^io_\w*$", r"^opcodes?$", r"^seconds$", r"^nanos\w*$"]),
    ("energy",              [r"^energy$", r"^joules?$", r"^watt\w*$"]),
]


def all_keys(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(str(k).lower())
            all_keys(v, out)
    elif isinstance(obj, list):
        for v in obj[:50]:
            all_keys(v, out)
    return out


# Receipts produced BY audits that scan the corpus.  An audit must not count
# its own output as corpus data: adding the pricing-protocol receipt changed the
# cost-coordinate audit's own inputs and broke its reproduction, which is a
# structural coupling rather than a one-off.  Excluding them makes each audit a
# function of the DERIVATION receipts only, so adding another audit later cannot
# silently move these numbers.
SELF_REFERENTIAL = {
    "STAGE_PROTOCOL_CONFORMANCE_V1.json",
    "STAGE_PARENT_COVERAGE_V1.json",
    "STAGE_COST_COORDINATE_V1.json",
    "STAGE_PRICING_PROTOCOL_V1.json",
}

receipts = {}
for f in sorted(glob.glob(os.path.join(RESULTS, "STAGE_*.json"))):
    base = os.path.basename(f)
    if base in SELF_REFERENTIAL:
        continue
    try:
        receipts[base] = all_keys(json.load(open(f)), set())
    except Exception:
        continue

print("=" * 96)
print("N: COST-COORDINATE METERING, measured at KEY level")
print("=" * 96)
print("  receipts scanned: %d" % len(receipts))


def meters(keys, pats):
    for k in keys:
        for seg in re.split(r"[^a-z0-9]+", k):
            if not seg:
                continue
            for p in pats:
                if re.match(p, seg):
                    return True
    return False


# --- validate the detector before believing it --------------------------
GROUND = [
    ("STAGE_R10_INVASION_V1.json", "search/discovery", True),   # n_eval / search keys
    ("STAGE_R10_INVASION_V1.json", "energy", False),            # nothing measures joules
    ("STAGE_FINITE_STATE_V1.json", "memory/storage", True),     # states
    ("STAGE_FINITE_STATE_V1.json", "energy", False),
    # these two patterns were over-broad and were corrected; the cases that
    # exposed them are kept so a regression is caught rather than re-derived
    ("STAGE_FINITE_STATE_V1.json", "revision/unlearning", False),
    ("STAGE_MESSAGE_PASSING_V1.json", "communication", True),
]
print()
print("-" * 96)
print("VALIDATING THE DETECTOR")
print("-" * 96)
val_ok = True
for fn, coord, truth in GROUND:
    if fn not in receipts:
        print("  SKIP  %-34s %-22s (receipt absent)" % (fn, coord))
        continue
    pats = dict(COORDS)[coord]
    got = meters(receipts[fn], pats)
    ok = got is truth
    val_ok = val_ok and ok
    print("  %-5s %-34s %-22s truth=%s got=%s" % ("ok" if ok else "MISS", fn, coord, truth, got))
assert val_ok, (
    "the key-level detector disagrees with a known answer; its counts cannot be "
    "believed until it agrees")

# --- coverage ------------------------------------------------------------
print()
print("-" * 96)
print("HOW MANY RECEIPTS METER EACH COORDINATE")
print("-" * 96)
counts = {}
for name, pats in COORDS:
    n = sum(1 for ks in receipts.values() if meters(ks, pats))
    counts[name] = n
    frac = 100.0 * n / max(1, len(receipts))
    flag = "  <-- rarely metered" if frac < 5 else ""
    print("  %-24s %4d of %d  (%5.1f%%)%s" % (name, n, len(receipts), frac, flag))

rare = [k for k, v in counts.items() if 100.0 * v / max(1, len(receipts)) < 5]
common = [k for k, v in counts.items() if 100.0 * v / max(1, len(receipts)) >= 50]
assert rare, (
    "every coordinate is metered in at least 5% of receipts, which would mean "
    "section N is essentially satisfied -- not credible, suspect the patterns")
assert common, "no coordinate is metered in half the receipts -- suspect the patterns"

OUT = {
    "self_referential_excluded": sorted(SELF_REFERENTIAL),
    "receipts_scanned": len(receipts),
    "method": (
        "a coordinate counts as metered when a receipt carries a KEY naming it, "
        "matched on whole key segments; a word in prose does not count"),
    "counts": counts,
    "rarely_metered": sorted(rare),
    "commonly_metered": sorted(common),
    "detector_validated_on": [[f, c, t] for f, c, t in GROUND],
    "scope": (
        "this measures whether a coordinate is METERED ANYWHERE in a receipt, "
        "not whether every claim in that receipt is charged for it, and not "
        "whether the number is correct"),
}
os.makedirs(RESULTS, exist_ok=True)
with open(os.path.join(RESULTS, "STAGE_COST_COORDINATE_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  commonly metered (>=50%%): %s" % ", ".join(sorted(common)))
print("  rarely metered   (<5%%)  : %s" % ", ".join(sorted(rare)))
print()
print("  receipt: microscopes/results/STAGE_COST_COORDINATE_V1.json")
