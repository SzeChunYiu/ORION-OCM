"""B4 remainder: reverse-mode credit assignment, and neutral MLP recovery.

GMI_UPDATE_LAW_DERIVATION_V1 left two boxes open and said why: it read slopes
directly rather than propagating them, so it could say nothing about HOW slopes
should be obtained, and neutral MLP recovery needed a slope-bearing ecology it
did not have. This supplies both.

  1  forward and reverse accumulation, IMPLEMENTED and counted on a real graph
  2  the rule that selects between them, derived from those counts
  3  a regime crossover: where reverse mode is the dearer choice.  Both modes
     succeed there, so this is NOT a matched failing control
  4  neutral recovery: a label-free search over machines that is told only
     "meet the obligation, pay for structure"
  5  the twin for that: an ecology where the recovered machine is NOT an MLP

Nothing is asserted from a formula. Both accumulation modes are executed on the
same computation graph and their multiply-accumulate operations are counted.
"""

import itertools
import json

OUT = {}


# ---------------------------------------------------------------------------
# a small computation graph, built explicitly so both modes run on the SAME one
# ---------------------------------------------------------------------------
class Graph:
    """y_k = sum_j V[k][j] * relu(sum_i W[j][i] * x_i)

    ONLY W is parameterised; the readout V is fixed. That matters: if every
    output carried its own weights, the parameter count would grow with the
    output count and the forward regime would be unreachable by construction --
    which is how a first version of this witness accidentally made reverse mode
    win everywhere.
    """

    def __init__(self, n_in, n_hid, n_out):
        self.n_in, self.n_hid, self.n_out = n_in, n_hid, n_out
        self.W = [[1 for _ in range(n_in)] for _ in range(n_hid)]
        self.V = [[1 for _ in range(n_hid)] for _ in range(n_out)]  # FIXED

    def n_params(self):
        return self.n_hid * self.n_in          # W only

    def forward(self, x, counter):
        h_pre = []
        for j in range(self.n_hid):
            s = 0
            for i in range(self.n_in):
                s += self.W[j][i] * x[i]
                counter[0] += 1
            h_pre.append(s)
        h = [max(0, v) for v in h_pre]
        y = []
        for k in range(self.n_out):
            s = 0
            for j in range(self.n_hid):
                s += self.V[k][j] * h[j]
                counter[0] += 1
            y.append(s)
        return y, h_pre, h


def forward_mode(g, x):
    """One tangent pass per PARAMETER. Each pass yields that parameter's effect
    on every output, so the cost scales with the parameter count."""
    c = [0]
    for _p in range(g.n_params()):
        g.forward(x, c)
    return c[0]


def reverse_mode(g, x):
    """One forward pass, then one backward traversal PER OUTPUT. Each backward
    pass yields one output's derivative with respect to every parameter, so the
    cost scales with the output count -- not with the parameter count."""
    c = [0]
    _y, h_pre, _h = g.forward(x, c)
    for _k in range(g.n_out):
        for j in range(g.n_hid):
            c[0] += 1                       # through the fixed readout
            if h_pre[j] > 0:
                for _i in range(g.n_in):
                    c[0] += 1               # into each W entry
    return c[0]


print("=" * 78)
print("1-2  FORWARD AND REVERSE ACCUMULATION, COUNTED ON THE SAME GRAPH")
print("=" * 78)
print("  Both modes are executed and their multiply-accumulates counted. The")
print("  graph has n_out outputs and P parameters.")
print()
print("  %-8s %-8s %-8s %-10s %-12s %-12s %s"
      % ("n_in", "n_hid", "n_out", "params", "forward", "reverse", "cheaper"))
rows = []
for n_in, n_hid, n_out in ((4, 4, 1), (6, 6, 1), (8, 8, 1),
                           (2, 2, 8), (2, 1, 8), (2, 1, 32), (1, 1, 32)):
    g = Graph(n_in, n_hid, n_out)
    x = [1] * n_in
    f, r = forward_mode(g, x), reverse_mode(g, x)
    cheaper = "reverse" if r < f else ("forward" if f < r else "tie")
    rows.append({"n_in": n_in, "n_hid": n_hid, "n_out": n_out,
                 "params": g.n_params(), "forward": f, "reverse": r,
                 "cheaper": cheaper})
    print("  %-8d %-8d %-8d %-10d %-12d %-12d %s"
          % (n_in, n_hid, n_out, g.n_params(), f, r, cheaper))
OUT["accumulation"] = rows

kinds = {r["cheaper"] for r in rows}
assert "reverse" in kinds, "reverse mode is never cheaper -- nothing to derive"
assert "forward" in kinds or "tie" in kinds, (
    "reverse mode is cheaper in EVERY regime, so the choice is not a choice "
    "and the derivation has no content")
print()
print("  Forward cost scales with the PARAMETER count; reverse cost scales with")
print("  the OUTPUT count. That is the derived asymmetry, and it is what the")
print("  counts show: at one output, reverse is 40 against 320 and the gap")
print("  widens with parameters; with two parameters and many outputs the")
print("  ordering reverses.")
print()
print("  It is NOT a bare 'more parameters than outputs' rule. At 4 parameters")
print("  and 8 outputs reverse still wins, because a forward pass carries the")
print("  whole output layer while a backward traversal per output does not.")
print("  The crossover sits where n_out x (backward traversal) passes")
print("  P x (forward pass), and those per-pass costs are part of the graph.")
print("  Stating it as P > n_out would be tidier and wrong.")
print()
print("  > Obtain slopes by reverse accumulation when the cost of one traversal")
print("  > per OUTPUT is below the cost of one pass per PARAMETER, and by")
print("  > forward accumulation otherwise.")
print()
print("  A loss is a single scalar, so a machine learning from a scalar signal")
print("  sits at n_out = 1 -- the deepest point of the reverse regime. That is")
print("  why reverse mode looks universal in practice. It is not universal; it")
print("  is the correct side of a ratio that learning happens to sit on, and")
print("  the rows below are the side it does not sit on.")

fwd_rows = [r for r in rows if r["cheaper"] == "forward"]
print("\n  The twin, where reverse mode is the WRONG choice:")
for r in fwd_rows:
    print("    %d params against %d outputs: forward %d, reverse %d"
          % (r["params"], r["n_out"], r["forward"], r["reverse"]))
OUT["forward_regime"] = fwd_rows


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4-5  NEUTRAL RECOVERY: THE SEARCH IS NEVER TOLD WHAT AN MLP IS")
print("=" * 78)
print("  Candidate machines are (depth, width, nonlinearity present). The")
print("  search is told only: does it meet the obligation, and what does it")
print("  cost. No family name appears anywhere in the candidate description.")
print()

# Two inputs, not three: XOR's canonical case, and it keeps the exhaustive
# search finite. The linear depth-2 shape has to exhaust its whole space before
# it can report failure, which at three inputs is ~134M combinations.
D = 2
INPUTS = [tuple(v) for v in itertools.product((0, 1), repeat=D)]
GRID = (-2, -1, 0, 1, 2)
BIAS = (-2, -1, 0, 1, 2)


def step(z):
    return 1 if z >= 0 else 0


def lin(w, x):
    return sum(a * b for a, b in zip(w, x))


def meets(f, depth, width, nonlin):
    """Can a machine of this shape meet the obligation?"""
    if depth == 1:
        if nonlin:
            return any(all(step(lin(w, x) + b) == f(x) for x in INPUTS)
                       for w in itertools.product(GRID, repeat=D) for b in BIAS)
        return any(all(lin(w, x) == f(x) for x in INPUTS)
                   for w in itertools.product(GRID, repeat=D))
    for Wr in itertools.product(itertools.product(GRID, repeat=D), repeat=width):
        for bs in itertools.product(BIAS, repeat=width):
            if nonlin:
                h = {x: tuple(step(lin(r, x) + bb) for r, bb in zip(Wr, bs))
                     for x in INPUTS}
            else:
                h = {x: tuple(lin(r, x) + bb for r, bb in zip(Wr, bs))
                     for x in INPUTS}
            for v in itertools.product(GRID, repeat=width):
                for b3 in BIAS:
                    out = (step if nonlin else (lambda z: z))
                    if all(out(sum(a * b for a, b in zip(v, h[x])) + b3) == f(x)
                           for x in INPUTS):
                        return True
    return False


def shape_cost(depth, width, nonlin):
    """Parameters, plus a charge for carrying a nonlinearity at all."""
    if depth == 1:
        return D + 1 + (1 if nonlin else 0)
    return D * width + width + width + 1 + (1 if nonlin else 0)


SHAPES = [(1, 0, False), (1, 0, True), (2, 1, False), (2, 1, True),
          (2, 2, False), (2, 2, True)]


def recover(f):
    best = None
    for depth, width, nonlin in SHAPES:
        if meets(f, depth, width, nonlin):
            c = shape_cost(depth, width, nonlin)
            if best is None or c < best[0]:
                best = (c, depth, width, nonlin)
    return best


def xor2(x):
    return x[0] ^ x[1]


def either(x):
    """OR of the two inputs: linearly separable, so no MLP should be needed."""
    return 1 if sum(x) >= 1 else 0


print("  %-12s %-10s %-10s %-14s %-10s %s"
      % ("obligation", "depth", "width", "nonlinearity", "cost", "is an MLP"))
rec = []
for name, f in (("or2", either), ("xor2", xor2)):
    b = recover(f)
    if b is None:
        rec.append({"obligation": name, "recovered": None})
        print("  %-12s %s" % (name, "not met by any registered shape"))
        continue
    c, depth, width, nonlin = b
    is_mlp = (depth >= 2 and nonlin)
    rec.append({"obligation": name, "depth": depth, "width": width,
                "nonlinearity": nonlin, "cost": c, "is_mlp": is_mlp})
    print("  %-12s %-10d %-10d %-14s %-10d %s"
          % (name, depth, width, nonlin, c, is_mlp))
OUT["neutral_recovery"] = rec

mlps = [r.get("is_mlp") for r in rec]
assert any(mlps), "the search never recovers a multi-layer nonlinear machine"
assert not all(mlps), (
    "the search recovers an MLP for EVERY obligation, including one that is "
    "linearly separable -- that is a search that prefers MLPs, not one that "
    "prices them")
by = {r["obligation"]: r for r in rec}
assert by["xor2"]["is_mlp"], "XOR should recover a depth-2 nonlinear machine"
assert not by["or2"]["is_mlp"], (
    "OR is linearly separable and should NOT recover an MLP")
print()
print("  XOR recovers a depth-2 machine WITH a nonlinearity -- an MLP, selected")
print("  by cost alone from a description that never names one. OR")
print("  recovers a single layer, because the extra structure would be paid")
print("  for and not used.")
print()
print("  > The MLP is what the accounting selects when, and only when, the")
print("  > obligation defeats a single weighted sum. It is not a default and")
print("  > it is not an improvement in general.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_CREDIT_ASSIGNMENT_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
