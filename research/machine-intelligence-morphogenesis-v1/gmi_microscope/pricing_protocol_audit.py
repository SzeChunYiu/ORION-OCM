"""N's two protocol rules, audited: scalarization and Pareto frontiers.

Sixteen of section N's boxes are coverage questions, answered in
GMI_COST_COORDINATE_V1.md.  The other two are RULES, and a rule is checkable in
a way a count is not:

  R1  no scalarization without a prospectively frozen price vector
  R2  report Pareto frontiers when prices are not fixed

WHAT THIS DOES AND DOES NOT ASSERT
    A receipt carrying a key like `score` is not necessarily scalarizing COSTS --
    it may be scoring capability, which is a different thing and not what R1
    restricts.  So this audit reports CANDIDATES and hand-checks them, rather
    than declaring violations it cannot substantiate.  Calling a capability
    score a pricing violation would be exactly the kind of over-claim the
    corpus's own audits exist to prevent.
"""

import json
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "microscopes", "results")

COST = re.compile(r"^(charge\w*|cost\w*|desc|exec\w*|upd\w*|ver_e|rev_e|cells|"
                  r"states|bits|opcodes?|nodes|probes?|wall\w*|seconds)$")
# `w_scalars` is NOT scalarization: it is a COUNT of scalar weights in a
# log-domain machine -- a size measure.  It surfaced as the only two R1
# candidates, was read, and is excluded by name with the reason recorded, rather
# than left to be rediscovered as a violation by the next reader.
SCALAR = re.compile(r"^(total_cost|total_charge|scalars?|weighted\w*|"
                    r"combined_cost|aggregate_cost)$")
NOT_SCALARIZATION = {"w_scalars"}
PRICE = re.compile(r"^(price\w*|prices|coefficients|cost_model|tariff)$")
FRONT = re.compile(r"^(pareto\w*|frontier|frontiers|nondominated|non_dominated)$")


def segs(keys):
    out = set()
    for k in keys:
        for s in re.split(r"[^a-z0-9]+", k):
            if s:
                out.add(s)
    return out


def allkeys(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            out.add(str(k).lower())
            allkeys(v, out)
    elif isinstance(o, list):
        for v in o[:60]:
            allkeys(v, out)
    return out


rows = {}
for f in sorted(glob.glob(os.path.join(RESULTS, "STAGE_*.json"))):
    try:
        ks = allkeys(json.load(open(f)), set())
    except Exception:
        continue
    sg = segs(ks)
    # drop segments that belong to an excluded whole key
    excluded = {seg for k in ks if k in NOT_SCALARIZATION
                for seg in re.split(r"[^a-z0-9]+", k) if seg}
    sg_scalar = sg - excluded if any(k in NOT_SCALARIZATION for k in ks) else sg
    rows[os.path.basename(f)] = {
        "n_cost": len({s for s in sg if COST.match(s)}),
        "scalar": sorted(s for s in sg_scalar if SCALAR.match(s)),
        "price": sorted(s for s in sg if PRICE.match(s)),
        "front": sorted(s for s in sg if FRONT.match(s)),
    }

n = len(rows)
multi = {f: r for f, r in rows.items() if r["n_cost"] >= 2}
print("=" * 96)
print("N's PROTOCOL RULES: scalarization and Pareto frontiers")
print("=" * 96)
print("  receipts                              : %d" % n)
print("  receipts metering >= 2 cost coordinates: %d" % len(multi))
assert multi, "no receipt meters two coordinates; neither rule can bind"

# ---- R1 ------------------------------------------------------------------
cand = {f: r for f, r in multi.items() if r["scalar"] and not r["price"]}
withprice = {f: r for f, r in multi.items() if r["scalar"] and r["price"]}
print()
print("-" * 96)
print("R1  SCALARIZATION WITHOUT A PRICE VECTOR")
print("-" * 96)
print("  multi-coordinate receipts that scalarize            : %d"
      % len([f for f, r in multi.items() if r["scalar"]]))
print("    ... and DO carry a price-vector key               : %d" % len(withprice))
print("    ... and do NOT  (candidate violations)            : %d" % len(cand))
for f, r in sorted(cand.items())[:8]:
    print("      %-52s scalar=%s" % (f[:52], r["scalar"]))
if not cand:
    print("      none")

# ---- R2 ------------------------------------------------------------------
nofix = {f: r for f, r in multi.items() if not r["price"]}
withfront = {f: r for f, r in nofix.items() if r["front"]}
print()
print("-" * 96)
print("R2  FRONTIERS WHERE PRICES ARE NOT FIXED")
print("-" * 96)
print("  multi-coordinate receipts with NO price vector      : %d" % len(nofix))
print("    ... that report a frontier                        : %d (%.0f%%)"
      % (len(withfront), 100.0 * len(withfront) / max(1, len(nofix))))
print("    ... that do not                                   : %d"
      % (len(nofix) - len(withfront)))

assert len(nofix) > 0, "every multi-coordinate receipt fixes prices; R2 cannot bind"
assert len(withfront) > 0, (
    "no unpriced multi-coordinate receipt reports a frontier, which would mean "
    "R2 is universally unmet -- check the frontier pattern before believing it")
assert len(withfront) < len(nofix), (
    "every unpriced receipt reports a frontier, which would make R2 trivially "
    "satisfied; that is not credible and suggests the pattern is too permissive")

OUT = {
    "hand_checked_false_positives": {
        "w_scalars": (
            "a COUNT of scalar weights in a log-domain machine, not a cost "
            "scalarization; it was the only R1 candidate and was read before "
            "being excluded")},
    "receipts": n,
    "multi_coordinate_receipts": len(multi),
    "R1_scalarizing": len([f for f, r in multi.items() if r["scalar"]]),
    "R1_scalarizing_with_price_vector": len(withprice),
    "R1_candidate_violations": sorted(cand),
    "R2_unpriced_multi_coordinate": len(nofix),
    "R2_reporting_a_frontier": len(withfront),
    "R2_not_reporting_a_frontier": len(nofix) - len(withfront),
    "caveat": (
        "candidates are NOT violations: a `score` key may be scoring capability "
        "rather than scalarizing costs, which R1 does not restrict; and a "
        "receipt may fix prices in its document rather than its receipt"),
}
os.makedirs(RESULTS, exist_ok=True)
with open(os.path.join(RESULTS, "STAGE_PRICING_PROTOCOL_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("=" * 96)
print("  R1 candidates are NOT violations.  A `score` key may be scoring")
print("  CAPABILITY rather than scalarizing costs, and R1 restricts only the")
print("  latter.  Each candidate needs reading before it is called a breach.")
print("  R2 is measurably partial: %d of %d unpriced multi-coordinate receipts"
      % (len(withfront), len(nofix)))
print("  report a frontier.")
print()
print("  receipt: microscopes/results/STAGE_PRICING_PROTOCOL_V1.json")
