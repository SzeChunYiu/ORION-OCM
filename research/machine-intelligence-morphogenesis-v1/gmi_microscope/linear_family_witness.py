"""B3: linear, GLM, basis and kernel systems, derived from compressibility.

The quotient theorem says a machine holds one state per distinction it must
make. GMI_EXEMPLAR_VERSUS_PARAMETRIC_V1 showed a rule's cost does not grow with
the universe while a table's does. This asks what happens when the rule is
specifically a WEIGHTED SUM -- which is what a coefficient representation is --
and derives, rather than assumes:

  1  when a coefficient vector is a sufficient statistic for the obligation
  2  the exact number of observations needed to identify it, by exhaustion
  3  the real-valued (regression) specialization
  4  the link-function (GLM) specialization, and what the link costs
  5  the fixed-basis / kernel specialization
  6  the coefficient-versus-exemplar crossover
  7  a quantitative response prediction, frozen and then measured

Exact arithmetic over Fractions throughout. Identification is decided by
enumerating every candidate weight vector, not by a rank formula, so the
formula is confirmed rather than restated.
"""

from fractions import Fraction as F
import itertools
import json

OUT = {}

D = 3                                    # feature dimension
WEIGHTS = list(range(-2, 3))             # candidate integer coefficients
INPUTS = [tuple(v) for v in itertools.product((0, 1), repeat=D)]


def linear(w, x):
    return sum(wi * xi for wi, xi in zip(w, x))


def consistent(w, obs, f):
    return all(f(w, x) == y for x, y in obs)


def candidates(obs, f=linear):
    """Every weight vector consistent with these observations. Exhaustive."""
    return [w for w in itertools.product(WEIGHTS, repeat=D) if consistent(w, obs, f)]


print("=" * 78)
print("1-2  THE COEFFICIENT VECTOR, AND HOW MANY OBSERVATIONS IDENTIFY IT")
print("=" * 78)
TRUE_W = (2, -1, 1)
print("  true coefficients %s over %d binary features" % (str(TRUE_W), D))
print("  a table would need %d entries; the coefficient vector needs %d numbers."
      % (len(INPUTS), D))
print()
print("  %-8s %-40s %-14s %s" % ("n obs", "observations", "consistent w", "identified"))
ident = []
# observations chosen as the standard basis plus one more, in order
ORDER = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 1, 1)]
for n in range(0, len(ORDER) + 1):
    obs = [(x, linear(TRUE_W, x)) for x in ORDER[:n]]
    cs = candidates(obs)
    ident.append({"n": n, "consistent": len(cs), "identified": len(cs) == 1})
    print("  %-8d %-40s %-14d %s"
          % (n, " ".join("".join(map(str, x)) for x in ORDER[:n]) or "(none)",
             len(cs), len(cs) == 1))
OUT["identification"] = ident

first_id = next(r["n"] for r in ident if r["identified"])
print("\n  identified at n = %d, which is exactly the dimension d = %d." % (first_id, D))
assert first_id == D, "identification did not happen at n = d"
assert ident[D - 1]["consistent"] > 1, (
    "with d-1 observations the weights must still be ambiguous, or there is no "
    "lower bound to speak of")
print("  With d-1 observations %d weight vectors remain consistent, so no"
      % ident[D - 1]["consistent"])
print("  machine can answer correctly on every continuation -- that is the")
print("  sample lower bound, exhibited rather than argued from rank.")

# independence matters, not just count: d dependent observations do not identify
DEP = [(1, 0, 0), (1, 0, 0), (0, 1, 0)]
dep_obs = [(x, linear(TRUE_W, x)) for x in DEP]
dep_cs = candidates(dep_obs)
print("\n  three observations that are NOT independent (%s): %d still consistent"
      % (" ".join("".join(map(str, x)) for x in DEP), len(dep_cs)))
OUT["dependent_observations"] = {"n": len(DEP), "consistent": len(dep_cs)}
assert len(dep_cs) > 1, "dependent observations should not identify"
print("  So the bound is d INDEPENDENT observations, and counting alone is not")
print("  sufficient -- which is the content of the dimensionality bound.")


print()
print("=" * 78)
print("3-4  REGRESSION AND THE COST OF A LINK")
print("=" * 78)


def thresholded(w, x, t=1):
    return 1 if linear(w, x) >= t else 0


print("  Same obligation, two response channels: the exact value, or a binary")
print("  threshold of it. The threshold is a GLM link -- it discards magnitude.")
print()
print("  %-24s %-10s %-14s %s" % ("channel", "n obs", "consistent w", "identified"))
link_rows = []
ALL_ORDER = ORDER + [x for x in INPUTS if x not in ORDER]
ident_at = {}
for name, f in (("real value (regression)", linear),
                ("threshold (GLM link)", lambda w, x: thresholded(w, x))):
    for n in range(1, len(ALL_ORDER) + 1):
        obs = [(x, f(TRUE_W, x)) for x in ALL_ORDER[:n]]
        cs = [w for w in itertools.product(WEIGHTS, repeat=D)
              if all(f(w, x) == y for x, y in obs)]
        link_rows.append({"channel": name, "n": n, "consistent": len(cs),
                          "identified": len(cs) == 1})
        if len(cs) == 1 and name not in ident_at:
            ident_at[name] = n
        if n <= 5 or len(cs) == 1:
            print("  %-24s %-10d %-14d %s" % (name, n, len(cs), len(cs) == 1))
        if len(cs) == 1:
            break
OUT["link_cost"] = link_rows
OUT["identified_at"] = ident_at

r_n = ident_at["real value (regression)"]
t_n = ident_at["threshold (GLM link)"]
print("\n  regression identifies after %d observations; the GLM link needs %d."
      % (r_n, t_n))
assert r_n == D, "regression should identify at n = d"
assert t_n > r_n, (
    "the link must DELAY identification, or it costs nothing and there is no "
    "GLM specialization to speak of")
print("  The link does not destroy identifiability here -- it DELAYS it, from")
print("  d = %d to %d, the whole input set. A link buys a bounded response range"
      % (r_n, t_n))
print("  and pays in samples: every thresholded observation carries strictly")
print("  less than the value it replaced, so more of them are needed to reach")
print("  the same conclusion.")
print()
print("  Scope: this alphabet is finite and the weight grid is coarse, which is")
print("  why the threshold eventually becomes unique. Over an unbounded weight")
print("  space a threshold channel would fix the weights only up to positive")
print("  scaling -- a direction, not a vector. The delay is the robust claim;")
print("  eventual uniqueness is an artefact of the finite grid and is not")
print("  asserted beyond it.")

print()
print("=" * 78)
print("5  FIXED BASIS: WHERE THE COMPRESSIBILITY ACTUALLY LIVES")
print("=" * 78)
print("  XOR of the first two features is not a weighted sum of them. Add one")
print("  product feature and it is. Nothing about the obligation changed.")
print()


def xor_obl(x):
    return x[0] ^ x[1]


def basis_raw(x):
    return x


def basis_product(x):
    return x + (x[0] * x[1],)


bas = []
for name, phi, dim in (("raw features", basis_raw, D),
                       ("raw + product", basis_product, D + 1)):
    found = None
    for w in itertools.product(WEIGHTS, repeat=dim):
        if all(linear(w, phi(x)) == xor_obl(x) for x in INPUTS):
            found = w
            break
    bas.append({"basis": name, "dim": dim, "representable": found is not None,
                "weights": list(found) if found else None})
    print("  %-16s dim %-4d representable: %-6s %s"
          % (name, dim, found is not None, "w=%s" % (found,) if found else ""))
OUT["basis"] = bas
assert bas[0]["representable"] is False, "XOR should not be linear in raw features"
assert bas[1]["representable"] is True, "XOR should be linear in the product basis"
print("\n  Linearity is a property of the PAIR (obligation, basis), never of the")
print("  obligation alone. A kernel machine is a coefficient machine whose basis")
print("  was chosen so the obligation became compressible in it -- the choosing")
print("  is where the work went, and it is charged there rather than to the")
print("  weighted sum.")


print()
print("=" * 78)
print("6  WHAT THE BASIS COSTS -- and why a rich enough kernel IS a table")
print("=" * 78)
print("  A first version compared d coefficients against 2^d table slots and")
print("  found coefficients cheaper at every d. That is not a crossover, it is")
print("  the observation that d < 2^d. The real trade is the BASIS: a machine")
print("  can only use a weighted sum on features it actually has, and richer")
print("  features cost more coefficients.")
print()
print("  Monomial bases up to degree k over d features.")
print()
DD = 3
UNIV = [tuple(v) for v in itertools.product((0, 1), repeat=DD)]


def monomials(d, k):
    out = []
    for deg in range(0, k + 1):
        for combo in itertools.combinations(range(d), deg):
            out.append(combo)
    return out


def phi(x, mons):
    return tuple(
        1 if not c else (1 if all(x[i] for i in c) else 0) for c in mons)


def solve_exact(rows, rhs):
    """Exact Gaussian elimination over Fractions. Returns a solution or None.

    Solving rather than searching a weight grid: a grid that is too coarse
    reports 'not representable' when the truth is 'not representable WITH THESE
    COEFFICIENTS', which is a different claim. Exact solving removes that
    artefact -- 3-way parity needs a coefficient of 4 and a +/-2 grid missed it.
    """
    m = [list(map(F, r)) + [F(v)] for r, v in zip(rows, rhs)]
    n_col = len(rows[0])
    piv_row = 0
    pivots = []
    for c in range(n_col):
        p = next((r for r in range(piv_row, len(m)) if m[r][c] != 0), None)
        if p is None:
            continue
        m[piv_row], m[p] = m[p], m[piv_row]
        pv = m[piv_row][c]
        m[piv_row] = [v / pv for v in m[piv_row]]
        for r in range(len(m)):
            if r != piv_row and m[r][c] != 0:
                f = m[r][c]
                m[r] = [a - f * b for a, b in zip(m[r], m[piv_row])]
        pivots.append(c)
        piv_row += 1
        if piv_row == len(m):
            break
    for r in range(piv_row, len(m)):
        if all(v == 0 for v in m[r][:-1]) and m[r][-1] != 0:
            return None                  # inconsistent
    sol = [F(0)] * n_col
    for i, c in enumerate(pivots):
        sol[c] = m[i][-1]
    return sol


def min_degree_for(obl, d=DD):
    """Smallest monomial degree in which this obligation is a weighted sum."""
    for k in range(0, d + 1):
        mons = monomials(d, k)
        rows = [phi(x, mons) for x in UNIV]
        rhs = [obl(x) for x in UNIV]
        if solve_exact(rows, rhs) is not None:
            return k, len(mons)
    return None, None


# structured obligations of KNOWN true degree, so the ladder is meaningful
OBLS = {
    "constant (deg 0)": (lambda x: 1, 0),
    "single bit (deg 1)": (lambda x: x[0], 1),
    "AND of two (deg 2)": (lambda x: x[0] & x[1], 2),
    "XOR of two (deg 2)": (lambda x: x[0] ^ x[1], 2),
    "3-way parity (deg 3)": (lambda x: x[0] ^ x[1] ^ x[2], 3),
}

print("  %-24s %-14s %-16s %s"
      % ("obligation", "true degree", "min basis degree", "basis size"))
basis_rows = []
for name, (fn, true_deg) in OBLS.items():
    k, size = min_degree_for(fn)
    basis_rows.append({"obligation": name, "true_degree": true_deg,
                       "min_basis_degree": k, "basis_size": size})
    print("  %-24s %-14d %-16s %s" % (name, true_deg, k, size))

full_size = len(monomials(DD, DD))
print("\n  the full monomial basis has %d features; the universe has %d inputs."
      % (full_size, len(UNIV)))
basis_rows.append({"obligation": "__full_basis__", "true_degree": DD,
                   "min_basis_degree": DD, "basis_size": full_size})
assert full_size == len(UNIV), "the full basis should cost exactly a table"
degs = [r["min_basis_degree"] for r in basis_rows if r["obligation"] != "__full_basis__"]
assert len(set(degs)) > 1, "every obligation needs the same basis degree"
assert min(degs) < max(degs), "there is no ladder of basis degrees"
OUT["basis_cost"] = basis_rows

# the degree ladder must be strict: each obligation needs exactly its degree
for r in basis_rows:
    if r["obligation"] == "__full_basis__":
        continue
    assert r["min_basis_degree"] == r["true_degree"], (
        "%s needs basis degree %s but its true degree is %s"
        % (r["obligation"], r["min_basis_degree"], r["true_degree"]))
print("\n  The full monomial basis has exactly 2^d = %d features, so a machine"
      % len(UNIV))
print("  that can express EVERY obligation by a weighted sum carries exactly as")
print("  many coefficients as a lookup table carries slots.")
print()
print("  > A kernel machine is not a way to avoid paying for a table. It is a")
print("  > way to pay for only the part of the table the obligation needs, and")
print("  > at full expressiveness the two costs coincide exactly.")
print()
print("  So the coefficient-versus-exemplar crossover is really a statement")
print("  about the basis: coefficients win when a LOW-degree basis suffices,")
print("  and the advantage disappears continuously as the required degree rises.")

print()
print("=" * 78)
print("7  A QUANTITATIVE PREDICTION, FROZEN THEN MEASURED")
print("=" * 78)
print("  Prediction, computed BEFORE the measurement below: a coefficient")
print("  machine over d features identifies after exactly d independent")
print("  observations, for every d -- not d-1, and not more than d.")
print()
print("  %-8s %-18s %-18s %s" % ("d", "predicted n", "measured n", "match"))
pred = []
for d in (1, 2, 3, 4):
    ws = list(range(-1, 2))
    inputs = [tuple(v) for v in itertools.product((0, 1), repeat=d)]
    true_w = tuple((1 if i % 2 == 0 else -1) for i in range(d))
    basis = [tuple(1 if j == i else 0 for j in range(d)) for i in range(d)]
    measured = None
    for n in range(0, d + 1):
        obs = [(x, sum(a * b for a, b in zip(true_w, x))) for x in basis[:n]]
        cs = [w for w in itertools.product(ws, repeat=d)
              if all(sum(a * b for a, b in zip(w, x)) == y for x, y in obs)]
        if len(cs) == 1:
            measured = n
            break
    pred.append({"d": d, "predicted": d, "measured": measured,
                 "match": measured == d})
    print("  %-8d %-18d %-18s %s" % (d, d, measured, measured == d))
OUT["quantitative_prediction"] = pred
assert all(p["match"] for p in pred), "the sample-count prediction failed"
print("\n  The prediction holds at every dimension tested. It is a derived")
print("  consequence rather than a fit: nothing was tuned to make it land.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_LINEAR_FAMILY_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
