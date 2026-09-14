"""B4 (architecture half): depth, nonlinearity, sharing, distribution.

GMI_LINEAR_FAMILY_DERIVATION_V1 established that a weighted sum is the correct
machine exactly when the obligation is low-degree in the basis it is given, and
that linearity belongs to the pair (obligation, basis). This asks what a machine
must add when that fails, and derives the architectural commitments of the
neural family rather than assuming them:

  1  weighted local composition, as the unit a layer computes
  2  why a nonlinearity is forced, from a task where linear closure fails
  3  feed-forward composition, and what depth buys WITHOUT a nonlinearity
  4  recurrence, when finite temporal state is required
  5  parameter sharing, from symmetry in the obligation
  6  distributed versus explicit symbolic state
  13 a negative twin: an ecology where the neural morphology loses

The learning-rule boxes (gradient descent, backprop, when gradients beat search)
are deliberately NOT in this document. Those touch a standing negative -- the
corpus measured gradient descent at 0.48x with no admissible gradient machine
anywhere tested -- and folding them in here would mix a derivation with an
unresolved empirical result.

Exhaustive enumeration; exact integer and Fraction arithmetic throughout.
"""

from fractions import Fraction as F
import itertools
import json

OUT = {}

D = 3
INPUTS = [tuple(v) for v in itertools.product((0, 1), repeat=D)]
GRID = (-2, -1, 0, 1, 2)


def linear(w, x):
    return sum(a * b for a, b in zip(w, x))


def step(z, t=0):
    return 1 if z >= t else 0


# Every threshold unit carries a bias. Without one, "depth 1" is not the class
# of linear threshold functions but an arbitrary subset of it, and majority --
# which IS linearly separable -- would look unreachable for the wrong reason.
BIAS = (-3, -2, -1, 0, 1, 2, 3)


# ---------------------------------------------------------------------------
print("=" * 78)
print("1 & 3  WHAT DEPTH BUYS WITHOUT A NONLINEARITY: NOTHING")
print("=" * 78)
print("  A layer computes a weighted sum. Stack two of them and ask whether the")
print("  pair can express anything one cannot. The answer is exhibited: for")
print("  every two-layer composition, the equivalent single weight vector is")
print("  constructed and checked on every input.")
print()

HID = 2
collapsed = []
mismatch = 0
checked = 0
for Wrows in itertools.product(itertools.product(GRID, repeat=D), repeat=HID):
    for v in itertools.product(GRID, repeat=HID):
        # two-layer linear: y = v . (W x)
        def two(x, Wrows=Wrows, v=v):
            h = [linear(row, x) for row in Wrows]
            return sum(a * b for a, b in zip(v, h))
        # the claimed equivalent single layer: u = v . W, computed not searched
        u = tuple(sum(v[i] * Wrows[i][j] for i in range(HID)) for j in range(D))
        checked += 1
        if any(two(x) != linear(u, x) for x in INPUTS):
            mismatch += 1
        collapsed.append(u)

print("  two-layer compositions checked : %d" % checked)
print("  that a single layer could NOT reproduce: %d" % mismatch)
OUT["depth_without_nonlinearity"] = {"checked": checked, "irreducible": mismatch}
assert mismatch == 0, "a two-layer linear map escaped single-layer form"
print("\n  Every composition of weighted sums IS a weighted sum. Depth alone")
print("  buys exactly nothing, so a stack of linear layers is not an")
print("  architecture -- it is a more expensive way to write one layer.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("2  WHERE LINEAR CLOSURE FAILS, AND WHAT REPAIRS IT")
print("=" * 78)


def xor2(x):
    return x[0] ^ x[1]


def maj(x):
    return 1 if sum(x) >= 2 else 0


TASKS = {"xor2": xor2, "majority": maj, "single_bit": lambda x: x[0]}

print("  %-14s %-20s %-26s %s"
      % ("task", "1 layer + threshold", "2 layers + threshold", "depth needed"))
rows = []
for name, f in TASKS.items():
    # depth 1: y = step(w.x)
    d1 = any(all(step(linear(w, x) + b) == f(x) for x in INPUTS)
             for w in itertools.product(GRID, repeat=D) for b in BIAS)
    # depth 2: y = step(v . [step(W1 x + b1), step(W2 x + b2)] + b3)
    d2 = False
    for Wrows in itertools.product(itertools.product(GRID, repeat=D), repeat=HID):
        if d2:
            break
        for bs in itertools.product(BIAS, repeat=HID):
            h = {x: tuple(step(linear(r, x) + bb)
                          for r, bb in zip(Wrows, bs)) for x in INPUTS}
            for v in itertools.product(GRID, repeat=HID):
                for b3 in BIAS:
                    if all(step(sum(a * b for a, b in zip(v, h[x])) + b3) == f(x)
                           for x in INPUTS):
                        d2 = True
                        break
                if d2:
                    break
            if d2:
                break
    need = 1 if d1 else (2 if d2 else None)
    rows.append({"task": name, "depth1": d1, "depth2": d2, "depth_needed": need})
    print("  %-14s %-20s %-26s %s" % (name, d1, d2, need))
OUT["depth_with_nonlinearity"] = rows

by = {r["task"]: r for r in rows}
assert by["single_bit"]["depth1"], "a single bit should need depth 1"
assert not by["xor2"]["depth1"], "XOR should not be representable at depth 1"
assert by["xor2"]["depth2"], "XOR should be representable at depth 2"
print("\n  XOR is the separator: unreachable at depth 1, reached at depth 2.")
print("  Put beside the result above, the pair is the whole derivation of the")
print("  neural unit -- depth without a nonlinearity buys nothing, and a")
print("  nonlinearity without depth cannot reach XOR either. Neither ingredient")
print("  is optional and neither is sufficient alone.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("5  PARAMETER SHARING, FROM SYMMETRY IN THE OBLIGATION")
print("=" * 78)
print("  If the obligation is invariant under permuting inputs, the quotient")
print("  identifies whole orbits, and a machine needs one parameter per orbit")
print("  rather than one per input. The saving is counted, not asserted.")
print()


def orbits_under_permutation(f, d=D):
    """Orbits of the obligation's quotient when all inputs are interchangeable."""
    seen = {}
    for x in INPUTS:
        seen.setdefault(tuple(sorted(x)), set()).add(f(x))
    return seen


print("  %-16s %-14s %-14s %-16s %s"
      % ("obligation", "inputs", "orbits", "well-defined", "saving"))
shar = []
for name, f in (("majority", maj), ("parity", lambda x: sum(x) % 2),
                ("first_bit", lambda x: x[0])):
    orb = orbits_under_permutation(f)
    well = all(len(v) == 1 for v in orb.values())
    saving = F(len(INPUTS), len(orb)) if well else None
    shar.append({"obligation": name, "inputs": len(INPUTS), "orbits": len(orb),
                 "permutation_invariant": well,
                 "saving": str(saving) if saving else None})
    print("  %-16s %-14d %-14d %-16s %s"
          % (name, len(INPUTS), len(orb), well, saving if saving else "-"))
OUT["sharing"] = shar
wells = [s["permutation_invariant"] for s in shar]
assert any(wells) and not all(wells), (
    "some obligations must be permutation-invariant and some not, or sharing "
    "is either always or never licensed")
print("\n  majority and parity are permutation-invariant, so %d inputs collapse"
      % len(INPUTS))
print("  to %d orbits and the parameters may be shared. first_bit is NOT"
      % len(orbits_under_permutation(maj)))
print("  invariant -- sharing there would merge inputs the obligation")
print("  distinguishes, and the witness detects that rather than trusting it.")
print("  Weight sharing is licensed by a symmetry IN THE OBLIGATION, never by")
print("  a symmetry in the architecture.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("6  DISTRIBUTED VERSUS EXPLICIT SYMBOLIC STATE")
print("=" * 78)
print("  Over a product world A x B, a symbolic machine holds one symbol per")
print("  combined state; a distributed machine holds separate codes and reads")
print("  them together. Which is correct depends on whether the obligation")
print("  factorizes -- and that is checkable.")
print()

A, B = 4, 4
PROD = [(a, b) for a in range(A) for b in range(B)]


def factorizing(ab):
    """Response depends on each coordinate only through its parity."""
    return (ab[0] % 2) ^ (ab[1] % 2)


def diagonal(ab):
    """Response is 1 only when the coordinates agree -- every row differs."""
    return 1 if ab[0] == ab[1] else 0


def codes(f):
    """How many classes does the obligation need for each coordinate on its own?

    Two values of `a` may share a code exactly when they behave identically
    against every `b`. That is the quotient theorem applied one coordinate at a
    time, so the counts are derived rather than chosen.
    """
    rows = {tuple(f((a, b)) for b in range(B)) for a in range(A)}
    cols = {tuple(f((a, b)) for a in range(A)) for b in range(B)}
    return len(rows), len(cols)


print("  Symbolic cost is one state per combined input, A*B = %d." % (A * B))
print("  Distributed cost is R + C codes plus the R*C table that combines them.")
print()
print("  %-14s %-8s %-8s %-16s %-14s %s"
      % ("obligation", "R", "C", "distributed", "symbolic", "cheaper"))
dist = []
for name, f in (("factorizing", factorizing), ("diagonal", diagonal)):
    R, C = codes(f)
    dis = R + C + R * C
    sym = A * B
    cheaper = "distributed" if dis < sym else ("symbolic" if sym < dis else "tie")
    dist.append({"obligation": name, "R": R, "C": C, "distributed": dis,
                 "symbolic": sym, "cheaper": cheaper})
    print("  %-14s %-8d %-8d %-16d %-14d %s" % (name, R, C, dis, sym, cheaper))
OUT["distributed"] = dist
ws = {d["cheaper"] for d in dist}
assert "distributed" in ws and "symbolic" in ws, (
    "one obligation must favour distributed coding and one symbolic, or the "
    "choice is not a choice: got %s" % sorted(ws))
print()
print("  The factorizing obligation collapses each coordinate to %d classes, so"
      % dist[0]["R"])
print("  %d beats %d. The diagonal obligation collapses NOTHING -- every row and"
      % (dist[0]["distributed"], dist[0]["symbolic"]))
print("  every column differs, R = C = %d -- and the distributed machine pays"
      % dist[1]["R"])
print("  %d against %d for the symbolic one, because it buys codes it cannot use."
      % (dist[1]["distributed"], dist[1]["symbolic"]))
print()
print("  > Distributed representation is not a cheaper encoding in general. It")
print("  > is cheaper exactly when each coordinate's behaviour collapses on its")
print("  > own, and strictly more expensive when it does not.")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("13  THE NEGATIVE TWIN: WHERE THE NEURAL MORPHOLOGY LOSES")
print("=" * 78)
print("  A first version of this section looked for an obligation the net could")
print("  not REACH. That was the wrong question: with a bias, most 3-bit")
print("  functions are linearly separable, so the search kept succeeding. The")
print("  right question is COST. A net pays for weights and buys compression;")
print("  the twin is where it pays and buys nothing.")
print()
print("  Hidden width is searched upward to 2 -- beyond that the enumeration")
print("  is not tractable, and the witness reports 'unreached at width<=2'")
print("  rather than claiming impossibility. The net is charged D*H + H + 1")
print("  parameters against a table's 2^D slots.")
print()


def reachable_at(f, hid):
    """Is f reachable by a depth-2 threshold net of this hidden width?"""
    if hid == 0:
        return any(all(step(linear(w, x) + b) == f(x) for x in INPUTS)
                   for w in itertools.product(GRID, repeat=D) for b in BIAS)
    for Wrows in itertools.product(itertools.product(GRID, repeat=D), repeat=hid):
        for bs in itertools.product(BIAS, repeat=hid):
            h = {x: tuple(step(linear(r, x) + bb)
                          for r, bb in zip(Wrows, bs)) for x in INPUTS}
            for v in itertools.product(GRID, repeat=hid):
                for b3 in BIAS:
                    if all(step(sum(a * b for a, b in zip(v, h[x])) + b3) == f(x)
                           for x in INPUTS):
                        return True
    return False


def net_cost(hid):
    return D + 1 if hid == 0 else D * hid + hid + 1


def parity3(x):
    return x[0] ^ x[1] ^ x[2]


print("  %-16s %-14s %-14s %-14s %s"
      % ("obligation", "hidden width", "net cost", "table cost", "verdict"))
neg = []
for name, f in (("majority", maj), ("xor2", xor2), ("parity3", parity3)):
    hid = None
    for h in (0, 1, 2):
        if reachable_at(f, h):
            hid = h
            break
    if hid is None:
        neg.append({"obligation": name, "hidden": None, "net_cost": None,
                    "table_cost": len(INPUTS), "verdict": "unreached<=2"})
        print("  %-16s %-14s %-14s %-14d %s"
              % (name, "none<=2", "-", len(INPUTS), "unreached at width<=2"))
        continue
    nc = net_cost(hid)
    tc = len(INPUTS)
    verdict = "net wins" if nc < tc else ("tie" if nc == tc else "TABLE WINS")
    neg.append({"obligation": name, "hidden": hid, "net_cost": nc,
                "table_cost": tc, "verdict": verdict})
    print("  %-16s %-14d %-14d %-14d %s" % (name, hid, nc, tc, verdict))
OUT["negative_twin"] = neg

verdicts = {n["verdict"] for n in neg}
assert "net wins" in verdicts, "the net never wins, so there is nothing to twin"
assert ("TABLE WINS" in verdicts or "tie" in verdicts), (
    "the net wins on every obligation -- then it is a universal improvement "
    "and there is no negative twin to report")
print()
print("  majority carries structure the net exploits: %d parameters against %d"
      % (neg[0]["net_cost"], neg[0]["table_cost"]))
print("  slots -- it is reached with NO hidden layer at all. XOR needs a hidden")
print("  layer, and one hidden layer already costs %d against the table's %d."
      % (neg[1]["net_cost"] if neg[1]["net_cost"] else 0, neg[1]["table_cost"]))
print("  The advantage is spent by the time the machinery is needed.")
print()
print("  > The neural morphology is not a universal improvement. It is a BET")
print("  > that the obligation has exploitable structure. Where the bet is")
print("  > right it wins by a wide margin; where it is wrong the machine pays")
print("  > for weights and buys nothing, and the table it was meant to replace")
print("  > is the correct machine.")
print()
print("  This is the same law as the kernel result in B3: at full expressiveness")
print("  a compressing machine costs exactly what a lookup table costs.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_NEURAL_ARCHITECTURE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
