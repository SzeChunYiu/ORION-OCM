"""ADJUDICATION: does symbiosis occur?  Phase two; frozen at 080a86ae."""

import json
import os

PRED = os.path.join("microscopes", "results", "STAGE_SYMBIOSIS_PREDICTION_V1.json")
R10 = os.path.join("microscopes", "results", "STAGE_R10_INVASION_V1.json")

pred = json.load(open(PRED))
r10 = json.load(open(R10))
CELLS = r10["cells"]
SOLO = r10["solo_baseline_by_pool"]
MATRIX = r10["invasion_matrix_by_pool"]

print("=" * 80)
print("ADJUDICATION -- symbiosis (section G box 10)")
print("=" * 80)

# ---------------------------------------------------------------------------
# 0  KEY PARSING SELF-CHECK.
# The cell key is "pool<P>|<a>|<b>".  Which of a,b is the resident decides the
# sign of everything below, so it is verified against the invasion matrix
# rather than assumed: matrix[resident][invader] must equal the cell's outcome.
# ---------------------------------------------------------------------------
def parse(key):
    p, a, b = key.split("|")
    return p[len("pool"):], a, b


agree_ra = agree_ar = 0
for key, cell in CELLS.items():
    pool, a, b = parse(key)
    if MATRIX[pool].get(a, {}).get(b) == cell["outcome"]:
        agree_ra += 1
    if MATRIX[pool].get(b, {}).get(a) == cell["outcome"]:
        agree_ar += 1
print()
print("  cells: %d" % len(CELLS))
print("  key read as pool|resident|invader : %d cells agree with the matrix" % agree_ra)
print("  key read as pool|invader|resident : %d cells agree with the matrix" % agree_ar)
assert agree_ra != agree_ar, (
    "both readings of the cell key agree equally with the matrix, so the "
    "resident/invader order cannot be determined and every comparison below "
    "would have an undetermined sign")
RESIDENT_FIRST = agree_ra > agree_ar
print("  -> resident is the %s field of the key" % ("SECOND" if RESIDENT_FIRST else "THIRD"))
assert max(agree_ra, agree_ar) == len(CELLS), (
    "the winning key reading still disagrees with the matrix on %d cells"
    % (len(CELLS) - max(agree_ra, agree_ar)))


# ---------------------------------------------------------------------------
# 1  SYMBIOSIS AND MUTUAL HARM
# ---------------------------------------------------------------------------
symbiotic, harmful, one_sided, ties = [], [], 0, 0
for key, cell in CELLS.items():
    pool, a, b = parse(key)
    resident, invader = (a, b) if RESIDENT_FIRST else (b, a)
    if resident == invader:
        continue                      # a carrier against a copy of itself
    sr = SOLO[pool].get(resident, {}).get("capability")
    si = SOLO[pool].get(invader, {}).get("capability")
    if sr is None or si is None:
        continue
    cr, ci = cell["capability_resident"], cell["capability_invader"]
    if cr > sr and ci > si:
        symbiotic.append((pool, resident, invader, sr, cr, si, ci))
    elif cr < sr and ci < si:
        harmful.append((pool, resident, invader, sr, cr, si, ci))
    elif cr == sr and ci == si:
        ties += 1
    else:
        one_sided += 1

compared = len(symbiotic) + len(harmful) + one_sided + ties
print()
print("-" * 80)
print("1  JOINT OUTCOMES relative to each carrier's solo capability")
print("-" * 80)
print("  distinct-carrier pairs compared : %d" % compared)
print("  SYMBIOTIC   (both above solo)   : %d" % len(symbiotic))
print("  MUTUAL HARM (both below solo)   : %d" % len(harmful))
print("  one-sided                       : %d" % one_sided)
print("  both unchanged                  : %d" % ties)

p1 = len(symbiotic) == 0
p2 = len(harmful) > 0
print()
print("  P1 (symbiosis never occurs) : %s" % ("HOLDS" if p1 else "FALSIFIED"))
print("  P2 (mutual harm occurs)     : %s" % ("HOLDS" if p2 else "FALSIFIED"))

# The control that decides whether P1's zero means anything at all.
assert compared > 0, "no pair was compared; the measurement did nothing"
assert p2, (
    "mutual harm is ALSO zero, so the comparison is not detecting joint effects "
    "at all and P1's zero is uninformative -- this is the control the frozen "
    "prediction named in advance, and it has fired")

if symbiotic:
    print()
    print("  symbiotic examples:")
    for row in symbiotic[:4]:
        print("    pool %-8s %s(res) %.4f->%.4f  %s(inv) %.4f->%.4f"
              % (row[0], row[1], row[3], row[4], row[2], row[5], row[6]))

verdict = "BOTH_HOLD" if (p1 and p2) else ("P1_FALSIFIED" if not p1 else "P2_FALSIFIED")
print()
print("  VERDICT: %s" % verdict)
print()
if p1:
    print("  > Symbiosis does not occur in this ecology.  Two carriers sharing ONE")
    print("  > charged pool never both end above their solo capability, while %d" % len(harmful))
    print("  > pairs both end below it.  Sharing a fixed budget is not a")
    print("  > cooperative interaction here -- box 10's criterion is satisfiable")
    print("  > in principle and has NO positive instance in this corpus.")
else:
    print("  > Symbiosis DOES occur: %d pairs both exceed their solo capability." % len(symbiotic))
    print("  > The frozen prediction was wrong, and box 10 gains a positive")
    print("  > instance rather than a negative one.")

OUT = {
    "registration_scored": pred["registration"],
    "P1": pred["P1"],
    "P2": pred["P2"],
    "resident_field": "second" if RESIDENT_FIRST else "third",
    "key_check_cells_agreeing": max(agree_ra, agree_ar),
    "pairs_compared": compared,
    "symbiotic_pairs": len(symbiotic),
    "mutually_harmful_pairs": len(harmful),
    "one_sided_pairs": one_sided,
    "unchanged_pairs": ties,
    "P1_holds": p1,
    "P2_holds": p2,
    "verdict": verdict,
    "symbiosis_examples": [list(r) for r in symbiotic[:5]],
    "criterion": pred["criterion_symbiotic"],
}

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_SYMBIOSIS_VERDICT_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_SYMBIOSIS_VERDICT_V1.json")
print("=" * 80)
