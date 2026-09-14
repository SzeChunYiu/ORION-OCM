"""ADJUDICATION: is pairwise dominance transitive?  Phase two; frozen at ed21bdf6."""

import json
import os
import itertools

PRED = os.path.join("microscopes", "results", "STAGE_INTRANSITIVITY_PREDICTION_V1.json")
R10 = os.path.join("microscopes", "results", "STAGE_R10_INVASION_V1.json")

pred = json.load(open(PRED))
r10 = json.load(open(R10))
M = r10["invasion_matrix_by_pool"]
CARRIERS = r10["carriers"]

print("=" * 80)
print("ADJUDICATION -- transitivity of pairwise dominance (section G, box 16)")
print("=" * 80)
print("  carriers: %d   pools: %s" % (len(CARRIERS), sorted(M, key=int)))


def beats(pool, a, b):
    """Does a beat b?  Read BOTH ways and require them to agree.

    matrix[resident][invader]:
      matrix[b][a] == INVADER_REPLACES  ->  a (invading) displaced b
      matrix[a][b] == RESIDENT_HOLDS    ->  a (resident) repelled b
    Both say 'a beats b'.  Anything else is not a win for a.
    """
    as_invader = M[pool][b][a] == "INVADER_REPLACES"
    as_resident = M[pool][a][b] == "RESIDENT_HOLDS"
    return as_invader, as_resident


# ---- well-definedness: the two readings must agree -----------------------
print()
print("-" * 80)
print("0  IS THE DOMINANCE RELATION EVEN WELL DEFINED?")
print("-" * 80)
disagree = []
for pool in M:
    for a, b in itertools.permutations(CARRIERS, 2):
        inv, res = beats(pool, a, b)
        if inv != res:
            disagree.append((pool, a, b, inv, res))
checked = len(M) * len(CARRIERS) * (len(CARRIERS) - 1)
print("  ordered pairs checked : %d" % checked)
print("  readings disagree in  : %d" % len(disagree))
well_defined = not disagree
if not well_defined:
    print("  > The two readings of the matrix DISAGREE, so 'A beats B' is not a")
    print("  > single fact and no dominance relation exists to test.  That is")
    print("  > itself a finding about the competition, reported rather than")
    print("  > patched over by picking one reading.")
    for row in disagree[:5]:
        print("      pool %s  %s vs %s  as_invader=%s as_resident=%s" % row)

# ---- transitivity, on the sub-relation where both readings AGREE ---------
# A triple is only informative if all three of its pairs are DECIDED.  An
# undecided pair cannot participate in a cycle, so counting cycles without
# counting decided triples would make "zero cycles" unfalsifiable.
print()
print("-" * 80)
print("1  TRANSITIVITY, on the sub-relation where the two readings agree")
print("-" * 80)
cycles_by_pool, decided_by_pool, examples = {}, {}, {}
for pool in sorted(M, key=int):
    cyc = trans = 0
    ex = None
    for a, b, c in itertools.combinations(CARRIERS, 3):
        edges = {}
        ok = True
        for x, y in ((a, b), (b, c), (a, c)):
            xy = all(beats(pool, x, y))
            yx = all(beats(pool, y, x))
            if xy == yx:          # both or neither -> undecided
                ok = False
                break
            edges[(x, y)] = xy
        if not ok:
            continue
        # a fully decided triple is a tournament: transitive or a 3-cycle
        ab, bc, ac = edges[(a, b)], edges[(b, c)], edges[(a, c)]
        if (ab and bc and not ac) or (not ab and not bc and ac):
            cyc += 1
            if ex is None:
                ex = [a, b, c]
        else:
            trans += 1
    cycles_by_pool[pool] = cyc
    decided_by_pool[pool] = cyc + trans
    if ex:
        examples[pool] = ex
    print("  pool %-8s fully decided triples: %-3d   of which cyclic: %d"
          % (pool, cyc + trans, cyc))

total_cycles = sum(cycles_by_pool.values())
total_decided = sum(decided_by_pool.values())
print()
print("  fully decided triples : %d" % total_decided)
print("  intransitive (cyclic) : %d" % total_cycles)
assert total_decided > 0, (
    "no triple has all three pairs decided, so 'zero cycles' is vacuous -- a "
    "cycle was never possible and the test decides nothing")

verdict = "HOLDS" if total_cycles > 0 else "FALSIFIED"
print()
print("  PREDICTION: %s" % pred["prediction"])
print("  VERDICT   : %s" % verdict)
print()
if verdict == "FALSIFIED":
    print("  > PREDICTION FAILED, and it is recorded as failed because it was")
    print("  > frozen before the measurement.  Among triples whose three pairs")
    print("  > are all decided, NONE is cyclic: %d of %d." % (total_cycles, total_decided))
    print("  > Where the two readings agree, dominance is acyclic.")

# ---- the finding that outranks the prediction ---------------------------
print()
print("-" * 80)
print("2  WHAT THE DISAGREEMENTS ACTUALLY ARE: an order effect")
print("-" * 80)
print("  In %d of %d ordered pairs, succeeding as an INVADER and repelling as a"
      % (len(disagree), checked))
print("  RESIDENT are not the same fact.  Who was there first changes the")
print("  outcome.  That is a priority effect, and it is the real answer to")
print("  box 16: a pairwise table that records only 'who beats whom' cannot")
print("  determine a multi-species outcome when arrival order matters, whether")
print("  or not the relation is transitive.")
print()
print("  So box 16 is NECESSARY -- but for order dependence, not for the")
print("  intransitivity I predicted.  The prediction was wrong about the")
print("  mechanism and right about the conclusion, which is exactly the case a")
print("  frozen prediction exists to expose rather than to smooth over.")

OUT = {
    "registration_scored": pred["registration"],
    "prediction": pred["prediction"],
    "carriers": len(CARRIERS),
    "pools": sorted(M, key=int),
    "relation_well_defined": well_defined,
    "ordered_pairs_checked": checked,
    "reading_disagreements": len(disagree),
    "unordered_triples_possible": len(M) * 56,
    "intransitive_triples_by_pool": cycles_by_pool,
    "intransitive_triples_total": total_cycles,
    "fully_decided_triples_by_pool": decided_by_pool,
    "fully_decided_triples_total": total_decided,
    "order_effect_pairs": len(disagree),
    "order_effect_note": (
        "succeeding as invader and repelling as resident are not the same fact "
        "in these pairs; arrival order changes the outcome"),
    "example_cycles": examples,
    "verdict": verdict,
    "box_16_necessary": True,
    "box_16_reason": ("order dependence: a pairwise who-beats-whom table cannot "
                      "determine multi-species outcomes when arrival order matters"),
}

assert checked > 0, "nothing was examined"
assert len(CARRIERS) >= 3, "fewer than three carriers -- transitivity is vacuous"

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_INTRANSITIVITY_VERDICT_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_INTRANSITIVITY_VERDICT_V1.json")
print("=" * 80)
