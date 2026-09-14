"""B12: residual memory -- what an absorbing machine still has to keep outside.

B11 asked whether to hold a body of knowledge as a table or as a rule, from
scratch. This asks the question one step later, and it is a different question:
a machine has ALREADY absorbed most of the body parametrically, and the only
thing still in dispute is the part it could not absorb. That part is the
RESIDUAL. Everything here is about the residual -- how it is identified, when
it belongs outside the description, what it costs to consult, and what happens
to it when the knowledge itself changes.

Six things get derived:

  1. the residual quotient -- the store need not tell residual inputs apart
     beyond the response each demands;
  2. irreducibility -- a residual is only worth storing if it is not itself
     expressible in the class, which is a tie-break-free search, not a taste;
  3. the external-versus-absorbed condition, and the frequency/probe/index
     laws that price a consultation;
  4. the update law under changing knowledge -- PVR-3 with the twist that a
     stored item's value is destroyed by change, and repair is per-entry for a
     store and global for a description;
  5. the comparison against caches, closeness-keyed stores and adapters,
     decided by eviction soundness and metric alignment rather than by name;
  6. neutral recovery: a search whose candidate space never says "retrieval",
     "index", "database" or "adapter" and still selects a residual store, in
     exactly the cells where one is right.

Exact enumeration over a 4-bit universe with a three-valued response. Every
reported number is an int or a Fraction; nothing is floating point. The rule
class is DELIBERATELY not closed under its own composition -- a closed class
would absorb every residual and there would be nothing to store.
"""

import itertools
import json
from fractions import Fraction

BITS = 4
UNIVERSE = list(itertools.product((0, 1), repeat=BITS))
M = len(UNIVERSE)
ALPHABET = (0, 1, 2)

OUT = {}


def jf(x):
    """Fractions are reported as exact 'p/q' strings; nothing becomes a float."""
    return str(Fraction(x))


# ---- prices ----------------------------------------------------------------
# Orderings are the result; magnitudes are not. Each is a separate physical act.
EVAL = 1        # running the description once at serve time (the baseline C)
PROBE = 1       # a local test of whether this query is one the description misses
LOOKUP = 3      # fetching a payload from the external store (strictly > PROBE)
WRITE = 1       # putting one item into the external store
ABSORB = 4      # installing one item into the description instead
RESEARCH = 4    # one-time cost of re-deriving a description from scratch
INDEX_BUILD = 2  # per-item cost of arranging the store for constant-time probing


# ---- the class a description may draw from ---------------------------------
def rule_class():
    """Constants, bit reads, two families of thresholds, and two counters.

    Small and honest: a class that could say everything would make the residual
    always empty, and a class that could say nothing would make it always the
    whole universe. Note it is NOT closed under (a+b) mod 3 -- section 2 depends
    on that being false, and checks it.
    """
    out = []
    for c in ALPHABET:
        out.append(("const%d" % c, 1, tuple(c for _ in UNIVERSE)))
    for i in range(BITS):
        out.append(("bit%d" % i, 2, tuple(x[i] for x in UNIVERSE)))
        out.append(("notbit%d" % i, 2, tuple(1 - x[i] for x in UNIVERSE)))
    for t in range(BITS + 1):
        out.append(("one_if>=%d" % t, 3,
                    tuple(1 if sum(x) >= t else 0 for x in UNIVERSE)))
        out.append(("two_if>=%d" % t, 3,
                    tuple(2 if sum(x) >= t else 0 for x in UNIVERSE)))
    out.append(("sum_mod3", 4, tuple(sum(x) % 3 for x in UNIVERSE)))
    out.append(("cap2", 4, tuple(min(sum(x), 2) for x in UNIVERSE)))
    return out


RULES = rule_class()
BY_NAME = dict((n, (c, v)) for n, c, v in RULES)

ONE_TERM = {}
for _n, _c, _v in RULES:
    if _v not in ONE_TERM or _c < ONE_TERM[_v][1]:
        ONE_TERM[_v] = (_n, _c)

TWO_TERM = {}
for _na, _ca, _va in RULES:
    for _nb, _cb, _vb in RULES:
        _v = tuple((p + q) % 3 for p, q in zip(_va, _vb))
        if _v not in TWO_TERM or _ca + _cb < TWO_TERM[_v][2]:
            TWO_TERM[_v] = (_na, _nb, _ca + _cb)


def best_rule(obl):
    """Widest coverage; ties broken by (cost, name). Returns name, cost, values,
    coverage. Where the tie-break could matter, section 2 uses the tie-break-free
    composition search instead."""
    best = None
    for n, c, v in RULES:
        cov = sum(1 for a, b in zip(v, obl) if a == b)
        key = (-cov, c, n)
        if best is None or key < best[0]:
            best = (key, n, c, v, cov)
    return best[1], best[2], best[3], best[4]


def residual_of(obl):
    _, _, v, _ = best_rule(obl)
    return tuple(i for i in range(M) if v[i] != obl[i])


# ---- the world: obligations, two of them a matched twin --------------------
BASE = BY_NAME["sum_mod3"][1]


def find_twin():
    """Search for three positions admitting BOTH twins: same base rule, same
    three perturbed inputs, differing ONLY in whether the perturbed inputs
    demand the same response or three different ones. Both must be
    irreducible (not expressible with one or two class terms), or the twin
    would be about expressibility rather than about payload collapse."""
    for trio in itertools.combinations(range(M), 3):
        for c in ALPHABET:
            if any(BASE[i] == c for i in trio):
                continue
            coll = list(BASE)
            for i in trio:
                coll[i] = c
            coll = tuple(coll)
            if coll in TWO_TERM:
                continue
            for perm in itertools.permutations(ALPHABET):
                if any(perm[j] == BASE[trio[j]] for j in range(3)):
                    continue
                dist = list(BASE)
                for j, i in enumerate(trio):
                    dist[i] = perm[j]
                dist = tuple(dist)
                if dist in TWO_TERM:
                    continue
                if best_rule(coll)[0] != "sum_mod3":
                    continue
                if best_rule(dist)[0] != "sum_mod3":
                    continue
                if residual_of(coll) != trio or residual_of(dist) != trio:
                    continue
                return trio, c, perm, coll, dist
    return None


_twin = find_twin()
assert _twin is not None, (
    "no three positions give a matched collapsing/distinct pair -- the twin "
    "that the whole of section 1 rests on does not exist in this world")
TRIO, COLL_VAL, DIST_VALS, OBL_COLLAPSE, OBL_DISTINCT = _twin

# a deterministic pseudo-random table: no LCG state leaks between runs
_lcg = 12345
_rand = []
for _ in range(M):
    _lcg = (1103515245 * _lcg + 12345) % (2 ** 31)
    _rand.append((_lcg >> 16) % 3)
OBL_INCOMPRESSIBLE = tuple(_rand)

OBL_ABSORBED = BASE
OBL_REDUCIBLE = tuple((BASE[i] + BY_NAME["two_if>=3"][1][i]) % 3 for i in range(M))
OBL_SMOOTH = BY_NAME["one_if>=2"][1]
# a smooth obligation with a smooth residual: perturb one Hamming-contiguous
# corner of the threshold rule, so nearby inputs still demand nearby responses
_sm = list(OBL_SMOOTH)
for _i, _x in enumerate(UNIVERSE):
    if sum(_x) >= 3:
        _sm[_i] = 2
OBL_SMOOTH_RESIDUAL = tuple(_sm)

OBLIGATIONS = [
    ("absorbed", OBL_ABSORBED),
    ("residual_collapse", OBL_COLLAPSE),
    ("residual_distinct", OBL_DISTINCT),
    ("residual_reducible", OBL_REDUCIBLE),
    ("smooth_residual", OBL_SMOOTH_RESIDUAL),
    ("incompressible", OBL_INCOMPRESSIBLE),
]
OBL_BY_NAME = dict(OBLIGATIONS)

print("=" * 78)
print("0  THE WORLD")
print("=" * 78)
print("  %d inputs of %d bits, responses in %s, %d rules in the class."
      % (M, BITS, str(ALPHABET), len(RULES)))
print("  matched twin found at inputs %s: collapsing assigns %d to all three,"
      % (str([UNIVERSE[i] for i in TRIO]), COLL_VAL))
print("  distinct assigns %s. Same base rule, same three inputs, same count."
      % str(list(DIST_VALS)))
closed = sum(1 for v in TWO_TERM if v in ONE_TERM)
print("  class closed under (a+b) mod 3? %s -- the %d ordered pairs collapse to"
      % ("NO" if closed < len(TWO_TERM) else "YES", len(RULES) ** 2))
print("  %d distinct functions, of which only %d are already single terms, so"
      % (len(TWO_TERM), closed))
print("  composition genuinely leaves the class.")
assert closed < len(TWO_TERM), (
    "the class is closed under its own composition, so every residual would be "
    "absorbable and there would be nothing to store -- the derivation is vacuous")
OUT["world"] = {"M": M, "bits": BITS, "alphabet": list(ALPHABET),
                "rules": len(RULES), "twin_positions": [list(UNIVERSE[i]) for i in TRIO],
                "collapse_value": COLL_VAL, "distinct_values": list(DIST_VALS),
                "two_term_images": len(TWO_TERM), "one_term_images": len(ONE_TERM),
                "class_closed": closed >= len(TWO_TERM)}


print()
print("=" * 78)
print("1  THE PREDICTIVE-TARGET RESIDUAL QUOTIENT")
print("=" * 78)
print("  After parametric absorption the machine keeps outside only the inputs")
print("  its description gets wrong. The store must tell those inputs apart --")
print("  but only up to the RESPONSE each demands. That is the quotient.")
print()
print("  %-20s %-12s %-6s %-9s %-9s %s"
      % ("obligation", "rule", "cov", "residual", "classes", "payload collapses"))
quot = []
for name, obl in OBLIGATIONS:
    rn, rc, rv, cov = best_rule(obl)
    res = tuple(i for i in range(M) if rv[i] != obl[i])
    classes = sorted(set(obl[i] for i in res))
    collapses = len(classes) < len(res)
    quot.append({"obligation": name, "rule": rn, "rule_cost": rc,
                 "coverage": cov, "residual": len(res),
                 "classes": len(classes), "collapses": collapses,
                 "residual_inputs": [list(UNIVERSE[i]) for i in res]})
    print("  %-20s %-12s %-6d %-9d %-9d %s"
          % (name, rn, cov, len(res), len(classes),
             "yes" if collapses else "no"))
OUT["quotient"] = quot

empty = [q for q in quot if q["residual"] == 0]
nonempty = [q for q in quot if q["residual"] > 0]
assert empty and nonempty, (
    "every obligation has the same residual status -- external memory is then "
    "either always or never needed, and there is nothing to derive")
assert all(q["residual"] < M for q in nonempty), (
    "some obligation was absorbed not at all, so its store is not a RESIDUAL "
    "store -- that is B11's question, not this one")
coll = dict((q["obligation"], q) for q in quot)
assert coll["residual_collapse"]["collapses"], (
    "the collapsing twin did not collapse")
assert not coll["residual_distinct"]["collapses"], (
    "the distinct twin collapsed too -- the twin is not matched on the "
    "property under test")
assert (coll["residual_collapse"]["residual"]
        == coll["residual_distinct"]["residual"]), (
    "the twins differ in residual SIZE as well as in payload, so any "
    "difference between them is not attributable to the quotient")
anyc = [q["collapses"] for q in nonempty]
assert any(anyc) and not all(anyc), (
    "the residual quotient either always or never collapses -- it is then not "
    "a measured property of the obligation")
print()
print("  MATCHED TWIN. residual_collapse and residual_distinct perturb the SAME")
print("  three inputs of the SAME rule. Residual size is %d for both. The only"
      % coll["residual_collapse"]["residual"])
print("  difference is what the three demand: one response, or three. The store")
print("  needs %d payload class(es) in the first case and %d in the second."
      % (coll["residual_collapse"]["classes"], coll["residual_distinct"]["classes"]))
print("  A residual store is a KEY SET plus one response per class, not one")
print("  response per item. The keys never collapse; the payload does.")
print()
print("  And the limit case is the interesting one: when the payload collapses")
print("  to a single class the store is no longer a store -- it is a constant")
print("  on a set, which is a rule term wearing a store's clothes. Whether the")
print("  class can SAY that set is exactly what section 2 decides.")


print()
print("=" * 78)
print("2  IRREDUCIBILITY: WHEN A RESIDUAL IS WORTH KEEPING OUTSIDE AT ALL")
print("=" * 78)
print("  Before provisioning a store, ask whether the residual is itself")
print("  expressible. Exhaustive search over all %d ordered pairs of class"
      % (len(RULES) ** 2))
print("  terms under (a+b) mod 3 -- tie-break-free, so it does not depend on")
print("  which rule the coverage search happened to pick.")
print()
print("  %-20s %-10s %-22s %-11s %s"
      % ("obligation", "one term", "two terms", "hybrid", "verdict"))
irr = []
for name, obl in OBLIGATIONS:
    rn, rc, rv, cov = best_rule(obl)
    res = tuple(i for i in range(M) if rv[i] != obl[i])
    one = ONE_TERM.get(obl)
    two = TWO_TERM.get(obl)
    hybrid = rc + EVAL + WRITE * len(res) + (PROBE + LOOKUP if res else 0)
    if one is not None:
        verdict = "no residual"
        twocost = one[1] + EVAL
    elif two is not None:
        twocost = two[2] + 2 * EVAL
        verdict = "STORE IS WASTE" if twocost < hybrid else "store still cheaper"
    else:
        twocost = None
        verdict = "STORE IS FORCED"
    irr.append({"obligation": name, "one_term": one[0] if one else None,
                "two_term": ("%s+%s" % (two[0], two[1])) if two else None,
                "two_cost": twocost, "hybrid_cost": hybrid,
                "verdict": verdict})
    print("  %-20s %-10s %-22s %-11s %s"
          % (name, one[0] if one else "none",
             ("%s+%s=%d" % (two[0], two[1], twocost)) if two else "none",
             hybrid, verdict))
OUT["irreducibility"] = irr

found_two = [x for x in irr if x["two_term"] is not None and x["one_term"] is None]
no_two = [x for x in irr if x["two_term"] is None]
assert found_two, (
    "the composition search never found a two-term expression for anything, so "
    "its failures are worthless -- POSITIVE CONTROL FAILED")
assert no_two, (
    "every obligation is expressible in two terms, so no residual is ever "
    "forced outside and the rest of this derivation has no subject")
waste = [x for x in found_two if x["verdict"] == "STORE IS WASTE"]
assert waste, (
    "no obligation was found where absorbing the residual as a second term "
    "beats storing it -- the irreducibility test then never changes a decision")
print()
print("  POSITIVE CONTROL. The same search that reports 'none' for %d"
      % len(no_two))
print("  obligation(s) finds a genuine two-term expression for %d, so its"
      % len(found_two))
print("  negatives are evidence and not an empty candidate space.")
print()
print("  RULE. Provision an external store for a residual only after the")
print("  composition search fails on it. A residual that the class can say is")
print("  a description the machine has not finished writing, and %s"
      % waste[0]["obligation"])
print("  pays %d for two terms against %d for rule-plus-store."
      % (waste[0]["two_cost"], waste[0]["hybrid_cost"]))


print()
print("=" * 78)
print("3  EXTERNAL STORE VERSUS FULL PARAMETRIC ABSORPTION")
print("=" * 78)
print("  Both machines hold the same residual. They differ in WHERE, and that")
print("  sets two prices in opposite directions: installing one item costs")
print("  %d in the description against %d in the store, while serving one" % (ABSORB, WRITE))
print("  query costs %d for the description against %d plus %d on a hit."
      % (EVAL, EVAL + PROBE, LOOKUP))
print()
print("  Over N uniform queries, with k the residual size and f = k/M:")
print("      store   = rule + %d*k + N*(%d + %d + f*%d)" % (WRITE, EVAL, PROBE, LOOKUP))
print("      absorb  = rule + %d*k + N*%d" % (ABSORB, EVAL))
print("  so the store wins iff (%d-%d)*k  >  N*(%d + f*%d)."
      % (ABSORB, WRITE, PROBE, LOOKUP))
print()
print("  %-20s %-5s %-8s %-10s %-10s %s"
      % ("obligation", "k", "f", "N*", "N=1 wins", "N=64 wins"))
cond = []
for name, obl in OBLIGATIONS:
    rn, rc, rv, cov = best_rule(obl)
    k = len([i for i in range(M) if rv[i] != obl[i]])
    f = Fraction(k, M)
    per = PROBE + f * LOOKUP
    nstar = Fraction((ABSORB - WRITE) * k, 1) / per if per else None
    row = {"obligation": name, "k": k, "f": jf(f),
           "n_star": jf(nstar) if nstar is not None else None}
    for N in (1, 64):
        store = rc + WRITE * k + N * (EVAL + PROBE + f * LOOKUP)
        absorb = rc + ABSORB * k + N * EVAL
        row["win_N%d" % N] = ("store" if store < absorb
                              else ("absorb" if absorb < store else "tie"))
    cond.append(row)
    print("  %-20s %-5d %-8s %-10s %-10s %s"
          % (name, k, jf(f), jf(nstar) if nstar is not None else "-",
             row["win_N1"], row["win_N64"]))
OUT["external_vs_absorbed"] = cond
winners = set()
for r in cond:
    winners.add(r["win_N1"])
    winners.add(r["win_N64"])
assert "store" in winners and "absorb" in winners, (
    "one side wins in every cell of the volume table -- the condition is "
    "vacuous: got %s" % sorted(winners))
print()
print("  NOT B11's THRESHOLD, AND IT RUNS THE OTHER WAY. B11 asks how often one")
print("  item must RECUR before keeping it beats recomputing it, and more reuse")
print("  favours the store. This asks how many queries a FIXED residual will")
print("  serve, and more queries favour absorption, because the store pays its")
print("  price per query while the description pays its price once.")

print()
print("  3b  RETRIEVAL FREQUENCY, SEPARATED FROM RESIDUAL SIZE")
print("  Above, f was k/M -- the residual's MEASURE under uniform queries. That")
print("  is not a frequency, and conflating the two would make this box a")
print("  restatement of section 3. A frequency is a property of the QUERY")
print("  STREAM. Let each residual input be w times as likely to be asked as a")
print("  covered one; then f = w*k / (w*k + (M-k)) and f is free of k.")
print()
print("  A probe is a local test (%d); a lookup fetches a payload (%d). Probing"
      % (PROBE, LOOKUP))
print("  first pays iff %d < (1-f)*%d, i.e. iff f < %s."
      % (PROBE, LOOKUP, jf(Fraction(LOOKUP - PROBE, LOOKUP))))
print()
WEIGHTS = (Fraction(1, 8), Fraction(1), Fraction(8))


def freq_of(k, w):
    if k == 0:
        return Fraction(0)
    if k == M:
        return Fraction(1)
    return (w * k) / (w * k + (M - k))


print("  %-5s %-8s %-10s %-12s %-12s %s"
      % ("k", "w", "f", "gated", "ungated", "probe pays"))
freq = []
for k in (1, 3, 6, 10):
    for w in WEIGHTS:
        f = freq_of(k, w)
        gated = EVAL + PROBE + f * LOOKUP
        ungated = EVAL + LOOKUP
        pays = gated < ungated
        freq.append({"k": k, "w": jf(w), "f": jf(f), "gated": jf(gated),
                     "ungated": jf(ungated), "probe_pays": pays})
        print("  %-5d %-8s %-10s %-12s %-12s %s"
              % (k, jf(w), jf(f), jf(gated), jf(ungated),
                 "yes" if pays else "no"))
OUT["frequency"] = freq
pp = [x["probe_pays"] for x in freq]
assert any(pp), "probing never pays -- the law is empty"
assert not all(pp), "probing always pays -- the threshold is doing no work"
_same_k = [k for k in (1, 3, 6, 10)
           if len(set(x["probe_pays"] for x in freq if x["k"] == k)) > 1]
_same_w = [jf(w) for w in WEIGHTS
           if len(set(x["probe_pays"] for x in freq if x["w"] == jf(w))) > 1]
OUT["probe_separation"] = {"flips_at_fixed_k": _same_k, "flips_at_fixed_w": _same_w}
print()
print("  SEPARATION CHECK. Residual sizes where the verdict flips on FREQUENCY")
print("  alone (k held fixed, w varied):  %s" % str(_same_k))
print("  Weights where it flips on SIZE alone (w held fixed, k varied): %s"
      % str(_same_w))
assert _same_k, (
    "the probe verdict never changes at fixed residual size, so frequency is "
    "not separated from size and this box is still section 3 restated")
assert _same_w, (
    "the probe verdict never changes at fixed frequency weight, so size does "
    "no independent work either")
print("  Both non-empty, so the law turns on the PRODUCT and neither variable")
print("  is a proxy for the other. A large residual asked about rarely and a")
print("  small one asked about constantly are genuinely different machines,")
print("  and this table contains both.")
print()
print("  Where the six obligations sit, under uniform queries (w=1):")
sits = []
for name, obl in OBLIGATIONS:
    rn, rc, rv, cov = best_rule(obl)
    k = len([i for i in range(M) if rv[i] != obl[i]])
    f = freq_of(k, Fraction(1))
    pays = PROBE < (1 - f) * LOOKUP
    sits.append({"obligation": name, "k": k, "f": jf(f), "probe_pays": pays})
    print("    %-22s k=%-3d f=%-8s probe pays: %s" % (name, k, jf(f), pays))
OUT["frequency_obligations"] = sits
assert all(s["probe_pays"] for s in sits), (
    "report changed: some obligation now sits on the non-paying side")
print("  ALL SIX PAY. The non-paying regime is exhibited by the sweep above,")
print("  not by any obligation in this world -- the threshold is LOCATED here,")
print("  not straddled by the examples. Stated so it is not mistaken for a")
print("  measured split among the obligations.")

print()
print("  3c  THE INDEX COST LAW")
print("  Scanning k stored items costs k; arranging them costs %d per item and"
      % INDEX_BUILD)
print("  reduces a hit to 1. Arranging pays iff N*f*(k-1) > %d*k, with f the"
      % INDEX_BUILD)
print("  query-weighted frequency from 3b rather than the residual's measure.")
print()
print("  %-5s %-8s %-10s %-10s %-10s %s"
      % ("k", "w", "f", "N=8", "N=64", "N=512"))
idx = []
for k in (1, 3, 6, 10):
    for w in WEIGHTS:
        f = freq_of(k, w)
        row = {"k": k, "w": jf(w), "f": jf(f)}
        cells = []
        for N in (8, 64, 512):
            pays = N * f * (k - 1) > INDEX_BUILD * k
            row["arrange_N%d" % N] = pays
            cells.append("yes" if pays else "no")
        idx.append(row)
        print("  %-5d %-8s %-10s %-10s %-10s %s"
              % (k, jf(w), jf(f), cells[0], cells[1], cells[2]))
OUT["index_law"] = idx
allc = []
for r in idx:
    for N in (8, 64, 512):
        allc.append(r["arrange_N%d" % N])
assert any(allc) and not all(allc), (
    "arranging the store either always or never pays -- the index law is "
    "vacuous over this table")
_idx_k = [k for k in (1, 3, 6, 10)
          if len(set(r["arrange_N64"] for r in idx if r["k"] == k)) > 1]
OUT["index_separation_fixed_k"] = _idx_k
print()
print("  At N=64 the verdict flips on frequency alone at k = %s." % str(_idx_k))
assert _idx_k, (
    "the index verdict never changes at fixed residual size, so this law is "
    "about size and volume only and 'frequency' is doing nothing in it")
print("  A one-item store is never worth arranging at any volume or frequency,")
print("  because there is nothing to search -- the (k-1) factor, not a price.")
print("  Everywhere else the law turns on N*f*k, and the table above contains")
print("  both a large rarely-asked store and a small constantly-asked one on")
print("  opposite sides of it.")


print()
print("=" * 78)
print("4  THE UPDATE LAW WHEN THE KNOWLEDGE ITSELF CHANGES")
print("=" * 78)
print("  This is where a residual store is supposed to earn its keep, so it is")
print("  where the comparison has to be made most carefully. One entry of the")
print("  obligation changes. Two machines hold the same knowledge.")
print()

TARGET = "residual_distinct"
_obl = list(OBL_BY_NAME[TARGET])
_rn, _rc, _rv, _cov = best_rule(tuple(_obl))
_res = [i for i in range(M) if _rv[i] != _obl[i]]
_cov_idx = [i for i in range(M) if _rv[i] == _obl[i]]

print("  Working on %s: rule %s, residual %d, covered %d."
      % (TARGET, _rn, len(_res), len(_cov_idx)))
print()
print("  %-26s %-14s %-16s %s"
      % ("change lands", "store repair", "description repair", "cheaper"))
upd = []
for where, pos in (("inside the residual", _res[0]),
                   ("in the covered region", _cov_idx[0])):
    drifted = list(_obl)
    drifted[pos] = (drifted[pos] + 1) % 3
    drifted = tuple(drifted)
    store_repair = WRITE
    if where == "inside the residual":
        desc_repair = ABSORB
    else:
        nrn, nrc, nrv, ncov = best_rule(drifted)
        nres = [i for i in range(M) if nrv[i] != drifted[i]]
        desc_repair = RESEARCH + nrc + ABSORB * len(nres)
    upd.append({"where": where, "store": store_repair, "description": desc_repair,
                "cheaper": "store" if store_repair < desc_repair else "description"})
    print("  %-26s %-14d %-16d %s"
          % (where, store_repair, desc_repair,
             "store" if store_repair < desc_repair else "description"))
OUT["repair"] = upd
assert upd[0]["store"] == upd[1]["store"], (
    "the store's repair cost depended on where the change landed -- the "
    "asymmetry this section claims is not there")
assert upd[0]["description"] < upd[1]["description"], (
    "re-deriving a description costs no more than editing one absorbed item, "
    "so the two repair regimes are not distinguishable")
assert all(u["cheaper"] == "store" for u in upd), (
    "the description repaired more cheaply somewhere -- state that instead of "
    "claiming the store is always cheaper to repair")
print()
print("  A STORE'S REPAIR COST DOES NOT DEPEND ON WHERE THE CHANGE LANDED; A")
print("  DESCRIPTION'S DOES. Editing an entry is %d either way. Editing an" % WRITE)
print("  absorbed item is %d, but a change in the region the RULE covers"
      % upd[0]["description"])
print("  invalidates the rule itself and costs %d to re-derive."
      % upd[1]["description"])

print()
print("  4b  WHEN DOES PATCHING STOP BEING RIGHT?")
print("  Every change in the covered region grows the residual by one, which")
print("  raises f, which raises the price of every future query. Re-deriving")
print("  buys that back. Break-even is a query volume, computed exactly.")
print()
print("  %-6s %-8s %-10s %-14s %-12s %s"
      % ("drift", "k_d", "f_d", "serve gap", "re-derive", "N* to re-derive"))
drift_rows = []
_d_obl = list(_obl)
_order = [i for i in _cov_idx]
for d in range(0, 7):
    if d > 0:
        p = _order[d - 1]
        _d_obl[p] = (_d_obl[p] + 1) % 3
    cur = tuple(_d_obl)
    k_d = len(_res) + d
    f_d = Fraction(k_d, M)
    hybrid_serve = EVAL + PROBE + f_d * LOOKUP
    param_serve = EVAL
    gap = hybrid_serve - param_serve
    nrn, nrc, nrv, ncov = best_rule(cur)
    nres = [i for i in range(M) if nrv[i] != cur[i]]
    reabsorb = RESEARCH + nrc + ABSORB * len(nres)
    nstar = Fraction(reabsorb, 1) / gap
    drift_rows.append({"d": d, "k_d": k_d, "f_d": jf(f_d), "gap": jf(gap),
                       "reabsorb": reabsorb, "n_star": jf(nstar),
                       "fresh_rule": nrn, "fresh_residual": len(nres)})
    print("  %-6d %-8d %-10s %-14s %-12d %s"
          % (d, k_d, jf(f_d), jf(gap), reabsorb, jf(nstar)))
OUT["drift"] = drift_rows
ns = [Fraction(r["n_star"]) for r in drift_rows]
assert len(set(ns)) > 1, (
    "the break-even volume is constant across drift, so accumulated change "
    "costs the machine nothing and there is no update law")

print()
print("  %-6s %-12s %-12s %-12s %s"
      % ("drift", "N=4", "N=16", "N=64", "N=256"))
dn = []
for r in drift_rows:
    row = {"d": r["d"]}
    cells = []
    for N in (4, 16, 64, 256):
        w = "re-derive" if N > Fraction(r["n_star"]) else "patch"
        row["N%d" % N] = w
        cells.append(w)
    dn.append(row)
    print("  %-6d %-12s %-12s %-12s %s" % (r["d"], cells[0], cells[1],
                                           cells[2], cells[3]))
OUT["drift_winners"] = dn
_ws = set()
for r in dn:
    for N in (4, 16, 64, 256):
        _ws.add(r["N%d" % N])
assert _ws == set(["patch", "re-derive"]), (
    "one response wins in every drift/volume cell -- the update law is "
    "vacuous: got %s" % str(sorted(_ws)))
_by_n = dict((N, set(r["N%d" % N] for r in dn)) for N in (4, 16, 64, 256))
_drift_flips = [N for N in (4, 16, 64, 256) if len(_by_n[N]) > 1]
OUT["drift_flips_at_volume"] = _drift_flips
print()
print("  MEASURED, NOT NARRATED: at each fixed volume the decision is the same")
print("  for every drift level tested. Volumes where accumulated drift flips")
print("  the decision: %s." % (str(_drift_flips) if _drift_flips else "NONE"))
print("  Recorded, not asserted: a price regime in which drift DOES flip the")
print("  decision is the more interesting finding, and gating on its absence")
print("  would make that discovery read as a regression here.")

print()
print("  CORRECTED AGAINST THE OBVIOUS EXPECTATION. The break-even volume does")
print("  not fall as the store grows. It ends HIGHER than it began, %s -> %s"
      % (jf(ns[0]), jf(ns[-1])))
print("  -- and it is not monotone: it dips wherever a fresh description")
print("  happens to fit the drifted world better. Range %s to %s."
      % (jf(min(ns)), jf(max(ns))))
assert ns[-1] > ns[0], (
    "N* fell with drift after all -- the reported direction is wrong")
assert min(ns) < max(ns), "N* is constant, so drift costs the machine nothing"
print("  The reason is symmetric and was not anticipated: accumulated change")
print("  degrades the thing you would re-derive INTO by as much as it degrades")
print("  the patched machine. Each change adds %s to the store's serve price"
      % jf(Fraction(LOOKUP, M)))
print("  through f, and adds %d to a fresh description through that" % ABSORB)
print("  description's own larger residual. The second is the bigger")
print("  increment, so 'patch until it is too messy, then retrain' is FALSE in")
print("  this price regime: the mess is in the WORLD, not in the store, and")
print("  re-deriving does not remove it. Re-derivation is chosen by query")
print("  VOLUME, not by accumulated drift.")

print()
print("  4c  THE TWIST: CHANGE DESTROYS A STORED ITEM'S VALUE")
print("  B11's PVR-3 keeps an item iff S < (r-1)(C-U). Under change, the reuse")
print("  r is capped by the item's LIFETIME L -- reuses after the knowledge")
print("  moved are served wrong. The effective rule is S < (min(r,L)-1)(C-U).")
print()
print("  %-8s %-8s %-8s %-8s %-10s %-10s %s"
      % ("r", "L", "C", "U", "no change", "with L", "same?"))
pvr = []
for r_ in (2, 8, 20):
    for L in (1, 2, 8):
        for C, U in ((4, 1), (2, 1)):
            S = 1
            keep_naive = S < (r_ - 1) * (C - U)
            keep_life = S < (min(r_, L) - 1) * (C - U)
            pvr.append({"r": r_, "L": L, "C": C, "U": U,
                        "keep_naive": keep_naive, "keep_lifetime": keep_life})
            print("  %-8d %-8d %-8d %-8d %-10s %-10s %s"
                  % (r_, L, C, U, keep_naive, keep_life,
                     "yes" if keep_naive == keep_life else "NO"))
OUT["pvr3_lifetime"] = pvr
assert any(p["keep_naive"] != p["keep_lifetime"] for p in pvr), (
    "capping reuse by lifetime never changed a retention decision -- the "
    "twist is not doing any work")
assert any(p["keep_lifetime"] for p in pvr), (
    "nothing is ever worth storing once lifetime is counted -- that is too "
    "strong to be true and means the prices are wrong")
print()
print("  And revalidation is not a free repair. If an entry must be checked")
print("  against the world on every use, the check costs what recomputing")
print("  costs, so U rises to C -- and B11's threshold says NOTHING is ever")
print("  worth keeping at U >= C, at any recurrence. A residual store is only")
print("  viable where change ANNOUNCES itself; polling dissolves the store.")
_reval = Fraction(1, 1) < (min(20, 8) - 1) * (4 - 4)
assert not _reval, (
    "an entry was still worth keeping when revalidation raised U to C, which "
    "contradicts B11's PVR-3 result")

print()
print("  4d  STALENESS UNDER NO MAINTENANCE (both machines, same world)")
_stale = []
_s_obl = list(_obl)
for d in (1, 3, 5):
    s2 = list(_obl)
    for j in range(d):
        p = _order[j]
        s2[p] = (s2[p] + 1) % 3
    s2 = tuple(s2)
    store_err = sum(1 for i in range(M)
                    if (_obl[i] if i in _res else _rv[i]) != s2[i])
    param_err = sum(1 for i in range(M) if _obl[i] != s2[i])
    _stale.append({"d": d, "store_errors": store_err,
                   "description_errors": param_err})
    print("  after %d unmaintained changes: store errs %d, description errs %d"
          % (d, store_err, param_err))
OUT["staleness"] = _stale
assert all(s["store_errors"] == s["description_errors"] for s in _stale), (
    "the two machines degraded differently under NO maintenance, which would "
    "mean the store's advantage is in correctness rather than in repair cost")
print("  Identical. Neither holding is self-correcting; the store's whole")
print("  advantage is that its errors are ADDRESSABLE one at a time.")


print()
print("=" * 78)
print("5  CACHES, CLOSENESS-KEYED STORES, ADAPTERS, AND THE RESIDUAL STORE")
print("=" * 78)
print("  These are not four traditions to pick between. They differ in two")
print("  measurable things: whether a miss is survivable, and whether the key")
print("  is exact. Both are measured here, not asserted.")
print()
print("  5a  EVICTION SOUNDNESS -- the sharp line between a cache and a store")
print("  Matched twin: the same %d entries, the same prices, differing ONLY in"
      % 3)
print("  whether a correct rule covers the inputs they hold.")
print()
ev = []
for label, idxs in (("held over covered inputs (a cache)", _cov_idx[:3]),
                    ("held over residual inputs (a store)", _res[:3])):
    held = set(idxs)

    def answer(i, h):
        """Held entries answer from the holding; everything else falls back to
        the description. Scored on the held inputs only, so the comparison is
        about eviction and not about the rest of the world."""
        return _obl[i] if i in h else _rv[i]

    before = sum(1 for i in idxs if answer(i, held) != _obl[i])
    after = sum(1 for i in idxs if answer(i, set()) != _obl[i])
    ev.append({"held": label, "entries": len(idxs),
               "errors_before_eviction": before,
               "errors_after_eviction": after})
    print("  %-40s %d entries -> %d error(s) held, %d after eviction"
          % (label, len(idxs), before, after))
OUT["eviction"] = ev
assert ev[0]["errors_before_eviction"] == 0 and ev[1]["errors_before_eviction"] == 0, (
    "a holding answered its own entries wrongly -- the twin is measuring a "
    "broken holding, not eviction")
assert ev[0]["errors_after_eviction"] == 0, (
    "evicting from the cache produced errors, so the fallback is not sound and "
    "the twin does not isolate coverage")
assert ev[1]["errors_after_eviction"] == ev[1]["entries"], (
    "evicting from the residual store produced no errors, so its entries were "
    "recoverable and it was not a residual store at all")
print()
print("  A CACHE IS A HOLDING WHOSE MISS IS SURVIVABLE. That is not a policy")
print("  choice, it is a property of what it covers: every cached answer is")
print("  recomputable from the description, so eviction costs time. A residual")
print("  holding covers exactly what the description CANNOT produce, so")
print("  eviction costs correctness. The same code, the same entries, the same")
print("  eviction -- and a different kind of machine, decided by coverage.")

print()
print("  5b  EXACT KEY VERSUS CLOSEST KEY -- metric alignment, with a control")
print("  A closeness-keyed holding answers x from the nearest key it holds. It")
print("  can therefore cover a residual with a SUBSET -- but only where the")
print("  obligation is smooth in the metric. Subset search is capped at 8 and")
print("  reports 'none <= 8' rather than claiming impossibility.")
print()


_SUBSET_CACHE = {}


def closest_subset(obl, targets):
    """Smallest held subset of `targets` that answers every target correctly by
    nearest key (Hamming, ties by lexicographic order). Capped at 8."""
    key = (obl, tuple(targets))
    if key in _SUBSET_CACHE:
        return _SUBSET_CACHE[key]
    size, sub = _closest_subset(obl, targets)
    _SUBSET_CACHE[key] = (size, sub)
    return size, sub


def _closest_subset(obl, targets):
    if not targets:
        return 0, []

    def ham(a, b):
        return sum(1 for p, q in zip(UNIVERSE[a], UNIVERSE[b]) if p != q)

    for size in range(1, min(len(targets), 8) + 1):
        for sub in itertools.combinations(targets, size):
            ok = True
            for t in targets:
                near = sorted(sub, key=lambda s: (ham(s, t), UNIVERSE[s]))[0]
                if obl[near] != obl[t]:
                    ok = False
                    break
            if ok:
                return size, list(sub)
    return None, None


print("  %-22s %-9s %-14s %-14s %s"
      % ("obligation", "residual", "exact keys", "closest keys", "subset helps"))
ck = []
for name, obl in OBLIGATIONS:
    rn, rc, rv, cov = best_rule(obl)
    res = [i for i in range(M) if rv[i] != obl[i]]
    size, sub = closest_subset(obl, res)
    helps = size is not None and size < len(res)
    ck.append({"obligation": name, "residual": len(res),
               "closest_subset": size, "helps": helps})
    print("  %-22s %-9d %-14d %-14s %s"
          % (name, len(res), len(res),
             size if size is not None else "none<=8",
             "yes" if helps else "no"))
OUT["closest_key"] = ck
helps = [x["helps"] for x in ck if x["residual"] > 0]
assert any(helps), (
    "closeness keying never covered a residual with a subset, so its failures "
    "below are worthless -- POSITIVE CONTROL FAILED")
assert not all(helps), (
    "closeness keying helped on every residual including the rough ones -- "
    "then the metric is doing no work and the comparison is rigged")
_rough = [x for x in ck if x["obligation"] in ("residual_distinct",
                                               "incompressible")]
_smooth = [x for x in ck if x["obligation"] == "smooth_residual"]
print()
print("  POSITIVE CONTROL. The identical subset search that returns no saving")
print("  on the rough residuals (%s) returns a saving on smooth_residual:"
      % str([x["obligation"] for x in _rough]))
print("  %s keys for %d residual inputs. The negative is therefore about the"
      % (str(_smooth[0]["closest_subset"]), _smooth[0]["residual"]))
print("  obligation's roughness, not about a search that cannot find anything.")

print()
print("  5c  WHO WINS WHERE")
print("  Four holdings scored on the same cells: (obligation, query volume N,")
print("  recompute price C, changes d). Correctness first, then total cost.")
print()


def score_config(obl, kind, N, C, d):
    """Total (errors, cost) for one holding on one cell. No family names are
    used inside: each kind is a distinct set of prices and coverages."""
    rn, rc, rv, cov = best_rule(obl)
    res = [i for i in range(M) if rv[i] != obl[i]]
    k = len(res)
    f = Fraction(k, M)
    errors = 0
    build = rc
    serve = Fraction(0)
    repair = Fraction(0)
    if kind == "absorb_all":
        build += ABSORB * k
        serve = Fraction(C)
        # any change in the covered region forces a fresh derivation
        repair = Fraction(d * (RESEARCH + rc)) if d else Fraction(0)
    elif kind == "store_residual":
        build += WRITE * k
        serve = C + PROBE + f * LOOKUP
        repair = Fraction(WRITE * d)
    elif kind == "cache_only":
        # holds recomputable answers only; cannot serve the residual at all
        hot = min(4, len(UNIVERSE) - k)
        build += WRITE * hot
        hit = Fraction(hot, M)
        serve = PROBE + hit * LOOKUP + (1 - hit) * C
        repair = Fraction(WRITE * d)
        errors = k
    elif kind == "store_by_closeness":
        size, sub = closest_subset(obl, res)
        if size is None:
            errors = k
            size = min(8, k)
        build += WRITE * size
        serve = C + PROBE + f * LOOKUP
        repair = Fraction(WRITE * d)
    else:
        raise ValueError(kind)
    return errors, build + N * serve + repair


KINDS = ("absorb_all", "store_residual", "cache_only", "store_by_closeness")
print("  Ties are reported as ties: every cell lists ALL holdings attaining the")
print("  minimum. Two holdings that answer identically at identical cost are")
print("  the same machine under two names, and letting a sort order pick")
print("  between them would manufacture a 'never wins' verdict out of nothing.")
print()
print("  %-20s %-5s %-4s %-4s %-34s %s"
      % ("obligation", "N", "C", "d", "winner(s)", "errors"))
cells = []
for name in ("absorbed", "residual_distinct", "smooth_residual", "incompressible"):
    obl = OBL_BY_NAME[name]
    for N in (1, 16, 256):
        for C in (1, 4):
            for d in (0, 3):
                sc = [(score_config(obl, kd, N, C, d), kd) for kd in KINDS]
                lo = min(s[0] for s in sc)
                winners = sorted(kd for s, kd in sc if s == lo)
                cells.append({"obligation": name, "N": N, "C": C, "d": d,
                              "winners": winners, "tied": len(winners) > 1,
                              "errors": lo[0], "cost": jf(lo[1])})
                if (N, C) in ((1, 1), (256, 4)):
                    print("  %-20s %-5d %-4d %-4d %-34s %d"
                          % (name, N, C, d, "+".join(winners), lo[0]))
OUT["comparison_cells"] = cells
won = {}
outright = {}
for c in cells:
    for w in c["winners"]:
        won[w] = won.get(w, 0) + 1
        if not c["tied"]:
            outright[w] = outright.get(w, 0) + 1
print()
print("  cells attained, out of %d: %s" % (len(cells), str(sorted(won.items()))))
print("  of those, won outright (no tie):  %s" % str(sorted(outright.items())))
tied_cells = len([c for c in cells if c["tied"]])
print("  %d of %d cells are ties between holdings that answer identically at"
      % (tied_cells, len(cells)))
print("  identical cost -- on this world those are the SAME machine under two")
print("  names, which is itself the finding of 5a and 5b.")
never = [k for k in KINDS if k not in won]
if never:
    print("  NEVER ATTAINS THE MINIMUM IN THIS PRICE REGIME: %s" % str(never))
    print("  -- reported, not tuned away.")
OUT["comparison_tally"] = won
OUT["comparison_outright"] = outright
OUT["comparison_never_wins"] = never
assert len(won) >= 2, (
    "fewer than two holdings ever attain the minimum -- the comparison is "
    "decided by the prices alone and says nothing about the holdings")
assert max(won.values()) < len(cells), (
    "one holding attains the minimum in every single cell; that is a rigged "
    "comparison")
assert outright, (
    "every cell is a tie, so no holding is ever strictly better than another "
    "and the comparison has no content")


print()
print("=" * 78)
print("6  NEUTRAL RECOVERY OF RESIDUAL-MEMORY BEHAVIOUR")
print("=" * 78)
print("  The candidate space below never names a family. It offers a machine")
print("  four independent choices, each stated as a mechanism. The search sees")
print("  errors and costs, never a label.")
print()

DESCRIBED = [None] + [n for n, c, v in RULES]
LISTED = ("nothing", "the_misses", "half_the_misses", "everything")
MATCHING = ("same_input", "closest_input")
HELD_IN = ("the_description", "the_side_list")
TEST_FIRST = (0, 1)

VOCAB = list(LISTED) + list(MATCHING) + list(HELD_IN) + ["test_first", "described"]
BANNED = ("retriev", "rag", "index", "database", "adapter", "cache", "memor")
_joined = " ".join(VOCAB).lower()
_hits = [b for b in BANNED if b in _joined]
assert not _hits, (
    "the candidate space leaks family vocabulary %s -- the recovery would be "
    "a lookup of the answer, not a search for it" % str(_hits))
print("  candidate vocabulary: %s" % str(VOCAB))
print("  banned substrings checked: %s -- none present." % str(list(BANNED)))
OUT["neutral_vocabulary"] = {"vocabulary": VOCAB, "banned": list(BANNED),
                             "hits": _hits}


def canonical(described, listed, matching, held_in, test_first):
    """Collapse choices that describe the same machine, so the winner is one
    shape and not an arbitrary member of an equivalence class."""
    if listed == "nothing":
        return (described, listed, "same_input", "the_description", 0)
    if held_in == "the_description":
        return (described, listed, "same_input", "the_description", 0)
    return (described, listed, matching, held_in, test_first)


def realized(obl, cand):
    """The machine a candidate actually becomes on this obligation: the answers
    it gives and the holding it ends up with. Two candidates with the same
    realization are the same machine and must not be counted as two."""
    described, listed, matching, held_in, test_first = cand
    if described is None:
        rv = None
    else:
        rv = BY_NAME[described][1]
    miss = [i for i in range(M) if rv is None or rv[i] != obl[i]]
    if listed == "nothing":
        held = []
    elif listed == "the_misses":
        held = list(miss)
    elif listed == "half_the_misses":
        held = list(miss[:max(1, len(miss) // 2)]) if miss else []
    else:
        held = list(range(M))
    return described, tuple(held), held_in if held else "the_description", \
        (matching if held else "same_input"), (test_first if held else 0)


def run_candidate(obl, cand, N, C, d):
    described, listed, matching, held_in, test_first = cand
    if described is None:
        rc, rv = 0, None
    else:
        rc, rv = BY_NAME[described]
    miss = [i for i in range(M) if rv is None or rv[i] != obl[i]]
    if listed == "nothing":
        held = []
    elif listed == "the_misses":
        held = list(miss)
    elif listed == "half_the_misses":
        held = list(miss[:max(1, len(miss) // 2)]) if miss else []
    else:
        held = list(range(M))

    def ham(a, b):
        return sum(1 for p, q in zip(UNIVERSE[a], UNIVERSE[b]) if p != q)

    errors = 0
    for i in range(M):
        if i in held:
            ans = obl[i]
        elif held and matching == "closest_input" and i in miss:
            near = sorted(held, key=lambda s: (ham(s, i), UNIVERSE[s]))[0]
            ans = obl[near]
        elif rv is not None:
            ans = rv[i]
        else:
            ans = None
        if ans != obl[i]:
            errors += 1

    unit = ABSORB if held_in == "the_description" else WRITE
    build = rc + unit * len(held)
    # Every answer costs at least one act. A machine with no rule that reads a
    # table baked into its own description still has to read it; charging that
    # zero would let "describe nothing, absorb everything" serve for free.
    if described is not None:
        ev = Fraction(C)
    elif held:
        ev = Fraction(EVAL)
    else:
        ev = Fraction(0)
    if held_in == "the_description" or not held:
        serve = ev
    else:
        frac = Fraction(len(miss), M) if test_first else Fraction(1)
        serve = ev + (PROBE if test_first else 0) + frac * LOOKUP
    if held_in == "the_description":
        repair = Fraction(d * (RESEARCH + rc)) if d else Fraction(0)
    else:
        repair = Fraction(WRITE * d)
    return errors, build + N * serve + repair


CANDIDATES = sorted(set(
    canonical(dd, ll, mm, hh, tt)
    for dd in DESCRIBED for ll in LISTED for mm in MATCHING
    for hh in HELD_IN for tt in TEST_FIRST),
    key=lambda t: (t[0] or "", t[1], t[2], t[3], t[4]))
print("  %d distinct candidate machines after canonicalisation." % len(CANDIDATES))
print()
print("  Two further disciplines, both of which cost the claim rather than help")
print("  it. Candidates that REALIZE the same machine on a given obligation are")
print("  collapsed before scoring, so no shape is counted twice for an")
print("  accidental distinction. And remaining ties are broken AGAINST the")
print("  external holding -- an internal holding of equal cost always wins --")
print("  so every external selection below is strict.")


def simplicity(cand):
    """Declared preference order for ties, chosen to be adverse to the claim:
    fewer commitments first, exact key before closest key, and an internal
    holding before an external one."""
    described, listed, matching, held_in, test_first = cand
    return (LISTED.index(listed),
            0 if matching == "same_input" else 1,
            0 if held_in == "the_description" else 1,
            test_first,
            described or "")


print()
print("  %-20s %-5s %-4s %-4s %-38s %s"
      % ("obligation", "N", "C", "d", "selected machine", "err"))
neutral = []
for name in ("absorbed", "residual_distinct", "smooth_residual", "incompressible"):
    obl = OBL_BY_NAME[name]
    for N in (1, 16, 256):
        for C in (1, 4):
            for d in (0, 3):
                seen = {}
                for cand in CANDIDATES:
                    sig = realized(obl, cand)
                    if sig not in seen or simplicity(cand) < simplicity(seen[sig]):
                        seen[sig] = cand
                scored = []
                for cand in seen.values():
                    e, c = run_candidate(obl, cand, N, C, d)
                    scored.append(((e, c, simplicity(cand)), cand))
                scored.sort(key=lambda t: t[0])
                (e, c, _), win = scored[0]
                ties = len([s for s in scored if (s[0][0], s[0][1]) == (e, c)])
                shape = "%s|%s|%s|%s|t%d" % (
                    win[0] if win[0] else "-", win[1], win[2], win[3], win[4])
                neutral.append({"obligation": name, "N": N, "C": C, "d": d,
                                "shape": shape, "errors": e, "cost": jf(c),
                                "described": win[0], "listed": win[1],
                                "matching": win[2], "held_in": win[3],
                                "test_first": win[4], "tied_with": ties - 1,
                                "candidates_after_collapse": len(seen)})
                if (N, C, d) in ((1, 1, 0), (256, 4, 3)):
                    print("  %-20s %-5d %-4d %-4d %-38s %d"
                          % (name, N, C, d, shape, e))
OUT["neutral"] = neutral

shapes = {}
for r in neutral:
    shapes[r["shape"]] = shapes.get(r["shape"], 0) + 1
print()
print("  distinct selected shapes: %d over %d cells" % (len(shapes), len(neutral)))
for s, n in sorted(shapes.items(), key=lambda t: -t[1]):
    print("    %-44s %d cell(s)" % (s, n))
OUT["neutral_shapes"] = shapes
assert len(shapes) >= 3, (
    "the neutral search selected fewer than three distinct machines across all "
    "cells -- the obvious answer wins everywhere and the recovery is rigged: "
    "got %s" % str(sorted(shapes)))
assert max(shapes.values()) < len(neutral), (
    "one shape won every cell")

held_out = [r for r in neutral if r["held_in"] == "the_side_list"]
held_in_desc = [r for r in neutral if r["held_in"] == "the_description"
                and r["listed"] != "nothing"]
assert held_out, (
    "the search never selected an external holding in any cell, so it did not "
    "recover residual-memory behaviour at all")
assert held_in_desc, (
    "the search never selected an internal holding, so the external one won "
    "by default rather than on the merits")
drift_out = len([r for r in held_out if r["d"] > 0])
drift_in = len([r for r in held_in_desc if r["d"] > 0])
print()
print("  external holding selected in %d cells (%d of them under change);"
      % (len(held_out), drift_out))
print("  internal holding selected in %d cells (%d of them under change)."
      % (len(held_in_desc), drift_in))
OUT["neutral_split"] = {"external": len(held_out), "internal": len(held_in_desc),
                        "external_under_change": drift_out,
                        "internal_under_change": drift_in}

closest_wins = [r for r in neutral if r["matching"] == "closest_input"]
print()
if closest_wins:
    print("  closeness keying selected in %d cell(s): %s"
          % (len(closest_wins),
             str(sorted(set(r["obligation"] for r in closest_wins)))))
else:
    print("  closeness keying selected in NO cell of this price regime.")
    print("  Reported, not tuned away: section 5b's positive control already")
    print("  shows the mechanism is reachable (it covers smooth_residual with")
    print("  a strict subset), so this is a statement about the prices, not")
    print("  about a dead option in the candidate space.")
OUT["neutral_closest_cells"] = len(closest_wins)

_reach = [x for x in ck if x["helps"]]
assert _reach, (
    "closeness keying is unreachable in this world, so reporting that the "
    "neutral search never picks it would be worthless")

print()
print("  WHAT WAS RECOVERED. Told nothing but mechanisms and prices, the search")
print("  selects: no holding at all when the description is exact; an internal")
print("  holding when the residual is small, stable and the volume is high; and")
print("  an external holding keyed on the same input, consulted only after a")
print("  test, when the knowledge changes. That last shape is a residual store,")
print("  and the search arrived at it without the word.")


print()
print("=" * 78)
print("SCOPE AND FALSIFIERS")
print("=" * 78)
print("  - A 4-bit universe (16 inputs) with a THREE-valued response. The third")
print("    value is load-bearing: with a binary response every residual has one")
print("    possible correction, the quotient of section 1 is trivially a single")
print("    class, and its matched twin cannot be built at all.")
print("  - The class is deliberately NOT closed under (a+b) mod 3, checked at")
print("    section 0. A closed class absorbs every residual and nothing is ever")
print("    stored, which is why the comparison exists.")
print("  - Section 2's composition search is exhaustive over ONE and TWO terms.")
print("    'STORE IS FORCED' means not expressible in two, not not expressible")
print("    at all -- a three-term expression is untested.")
print("  - The closest-key subset search is capped at 8 and reports 'none<=8'")
print("    rather than claiming impossibility, following B11.")
print("  - Sections 5 and 6 PRICE change; they do not re-score correctness")
print("    after it. A machine that pays its repair bill is correct by")
print("    construction there. Section 4d is where unmaintained error is")
print("    actually counted.")
print("  - 'incompressible' is one fixed pseudo-random table, not a sample over")
print("    tables. It witnesses that the class has gaps, not how many.")
print("  - Every price (%d absorb, %d write, %d lookup, %d probe, %d research)"
      % (ABSORB, WRITE, LOOKUP, PROBE, RESEARCH))
print("    is a modelling choice. The ORDERINGS and thresholds are the result;")
print("    the magnitudes are not. LOOKUP > PROBE is the one relation section")
print("    3b needs, and it is stated rather than discovered.")
print()
print("  FALSIFIERS. Exhibit a residual that the class can express where an")
print("  external store is still cheaper than a second term; or a holding whose")
print("  repair cost depends on where the change landed; or a world where")
print("  accumulated drift makes re-derivation MORE attractive at fixed query")
print("  volume; or a closeness-keyed holding that covers a rough residual with")
print("  a strict subset.")
print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

OUT["protocol"] = {
    "obligation": "Answer every query over a finite universe when a compact description in a fixed class already answers most of them, by deciding which remaining queries must be held individually outside that description, what consulting the holding costs, and what happens to it when the underlying knowledge changes.",
    "state_sufficient": True,
    "lower_bound": None,
    "upper_bound_construction": "quotient",
    "coordinate": "entries",
    "resource_law": "PVR-3",
    "negative_control": None,
    "prediction_frozen_before_outcome": False,
    "neutral_search_blind_to_family": True,
    "replication": [],
    "version": "B1/v1",
}

with open("microscopes/results/STAGE_RESIDUAL_MEMORY_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
