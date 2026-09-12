"""DK — the PRECISION-GATED KINGDOM microscope: is there an ecology in which, at wide precision, the
probabilistic carrier occupies frontier cells that NO carrier admissible at 8 bits occupies at any reuse
horizon? (issue #422, record RV-377-066; GMI-DA1, GMI-DA4, GMI-DA5 and section 9 of
GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md; gap G5 closed, its consequence not yet executed.)

WHY THIS QUESTION. Eleven domain candidates have been executed against matched strongest parents and all
eleven reduced. GMI-DA1 explains why: each was a bounded composition over the primitive alphabet AT A FIXED
ARITHMETIC PRECISION. GMI-DA5 proves that carrier admissibility is a function of the arithmetic INSTRUMENT,
not only of the carrier and the ecology. Two carriers are known to be shut out at 8 bits and to work wide:
the probabilistic carrier (D3, RV-377-029/031) and the energy/coupling carrier (RV-377-045). The kingdom
question has never been asked on the precision axis. If the probabilistic carrier is the SOLE frontier
occupant of a cell that no 8-bit-admissible carrier occupies, D3 is a structural domain that exists only
above a precision threshold, and the eleven reductions were an artefact of the registered 8-bit universe.

THE TWO CONFOUNDS, SEPARATED (deliverable 2). A capability difference between two instruments is a PRECISION
GATE only if
  (i)  the CHARGED OPERATION SEQUENCES are identical -- every row here is written with fixed-trip-count
       loops and no data-dependent early exit, so the charged op vector R = (desc, exec, upd, ver, rev) is
       identical across instruments by construction; the receipt asserts this per row per cell, and a
       frozen clause falsifies the run if it ever fails; and
  (ii) the DESCRIPTIONS are charged on the same basis -- desc is charged as
       n_declared_scalars * DESC_BITS_PER_SCALAR with DESC_BITS_PER_SCALAR = 8 (the registered word), the
       SAME for every instrument. The receipt also reports `desc_bits_scaled` (n_scalars * instrument bits)
       as a declared sensitivity, because charging a 64-bit weight vector at 8 bits is generous to the wide
       instrument and the honest thing is to report the frontier under both.

THE INSTRUMENT FAMILY. fx(b): two's-complement fixed point, b total bits, F = b//2 fractional bits, values
clamped to +-(2^(b-1)-1)/2^F. fx8 is EXACTLY the registered universe (b = 8, F = 4, clamp +-7.9375, MUL
rounding (a*b + 8) >> 4) -- `test_dk_fx8_is_the_registered_universe` asserts bit-identity against core.op.
The ladder is 8, 12, 16, 24, 32 and `wide` (unbounded integers at a declared scale 2^64). Only resolution
and range change; the op SEQUENCE never does.

THE ECOLOGIES. Both are ecologies in which a CALIBRATED PROBABILITY is the only correct answer; both score
with the BRIER proper scoring rule in exact rational arithmetic (`fractions.Fraction`). For an outcome
y ~ Bernoulli(q*) and a served forecast q, the expected Brier loss is (q - q*)^2 + q*(1 - q*), so the
excess over the irreducible term is exactly (q - q*)^2 and the rule is strictly proper: only q = q* is
optimal, and a point-estimate carrier is provably sub-optimal by exactly the squared distance of its point
estimate from the Bayes probability. Capability is the standard Brier SKILL score against the declared
base-rate forecaster (the constant mean of q* over the evaluated inputs), i.e. the fraction of the variance
of the Bayes probabilities that the row explains:

    cap = max(0, 1 - sum_x (q_row(x) - q*(x))^2 / sum_x (qbar - q*(x))^2),     theta = 0.85

  E_noisy   NOISY-LABEL. A latent deterministic rule (bit3) with a declared label-flip schedule at rate
            5/24. The Bayes-optimal answer at every input is a probability, never a label; the served
            obligation q*(x) is the exact posterior predictive under the declared hypothesis class and
            prior. Evaluated on ALL 16 inputs.
  E_ambig   AMBIGUOUS-EVIDENCE. The seen inputs are exactly those where bit0 = bit1, so the hypotheses
            keyed on bit0 and on bit1 are BOTH consistent with every event and disagree on every unseen
            input. The correct served answer on an unseen input is the POSTERIOR MIXTURE, which no single
            hypothesis produces. Evaluated on the 8 UNSEEN inputs.

Both draw hypotheses from one declared class of 32: 8 predicates x 4 value pairs, with a declared integer
prior. q*(x) = sum_h P(h|E) h(x) computed exactly over the FINAL evidence (after the revocation).

ROWS (protocol rule 19: the strongest 8-bit opponent, adversarially constructed, not a convenient one).
  BAYES    the probabilistic/Bayesian carrier (D3): a normalized posterior over the whole declared class,
           conditioned event by event, served as the posterior mixture.
  MAP      the same evidence-weighing machinery served as a POINT ESTIMATE IN HYPOTHESIS SPACE: the single
           maximum-a-posteriori hypothesis's probability. Strictly cheaper to serve than BAYES.
  PROG     program search (D4/D5) over the 16 deterministic classifiers (8 predicates and their negations),
           scored by matches and served as a 0/1 label -- the classical point-estimate carrier.
  COEF     the coefficient/gradient row (D1): q(x) = c0 + sum_i c_i bit_i(x) fitted by squared-error
           gradient steps.
  EXEM     the exemplar store (D2): per-input (sum, count), served as the stored frequency, global mean
           elsewhere.
  GEN      the generalizing store (D2): Hamming-nearest-neighbour average of the stored frequencies -- the
           S5h carrier of RV-377-025, which is the row that actually threatens both ecologies.
  QCOUNT   THE ADVERSARIAL 8-BIT POSTERIOR APPROXIMATOR the task requires: it approximates the posterior by
           QUANTIZED COUNTS. It never multiplies likelihoods (so it cannot underflow); it accumulates, in
           declared units of 1/EVENT_SCALE (so it cannot saturate), one unit per event each hypothesis
           explains, keeps the top M = 4 by count (so its weights are ~1/4 and are representable at 4
           fractional bits), normalizes them and serves the count-weighted mixture.
  UNIFMIX  negative twin: the same mixture machinery with the evidence discarded (uniform weights).
  BASE     negative twin: the running base rate served everywhere (capability 0 by construction).

COST MODEL (frozen, as registered): C = desc + H*exec_q + r*(upd_e + ver_e) + (r/4)*rev_e, theta = 0.85.
Two declared price vectors: `reduced` (one charge per scalar operation, the registered price) and `native`
(a declared probabilistic-accelerator price: one op per posterior-conditioning step and one per mixture
readout). Per gap DG-2 the H and r grids are EXTENDED past twice the analytic crossover of every pair under
every price vector, and the receipt additionally reports the exact asymptotic occupants as H -> infinity and
as r -> infinity, so that a 'no cell exists' clause is not a grid-truncation artefact.

THE DECISION (frontier rule: protocol rule 17 -- every frontier here is over the LARGEST declared size of
each row, and a row occupies a cell iff it is admissible AND its lifecycle cost is within 1e-9 of the
minimum over the admissible rows AT THE SAME INSTRUMENT). Let A8 be the set of rows admissible under fx8. A
cell (ecology, price, H, r) is PRECISION-GATED at instrument p iff BAYES is on the frontier at p and no
member of A8 is on that frontier. The kingdom is established iff some precision-gated cell exists and BAYES
is not itself in A8; the threshold is the smallest b in the ladder at which one exists.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")

THETA = F(85, 100)
X_ALL = list(range(16))
EVENT_SCALE = 16         # declared: every count-like accumulator advances by 1/16, the finest step the registered
                         # 8-bit universe represents, so that after 24 events NO row's accumulator or normalizing
                         # sum saturates an 8-bit cell (24/16 = 1.5; the largest normalizing sum here is 6.0 < 7.9375).
                         # Pre-freeze calibration disclosed in RV-377-066: at EVENT_SCALE = 8 the top-M normalizing
                         # sum of the count row reached 12 and CLAMPED at 7.9375, which handicapped the 8-bit
                         # opponent by an accounting choice rather than by precision. Protocol rule 19.
M_TOP = 4                # declared: QCOUNT keeps the top 4 hypotheses so its weights are representable at 4 fractional bits
DESC_BITS_PER_SCALAR = 8  # declared: descriptions are charged on the SAME basis for every instrument (deliverable 2)
DIV_CHARGE = 32          # declared: one division is charged as a fixed 16 MUL + 16 GT macro, the SAME for every instrument
WIDE_FRAC = 64           # declared scale of the unbounded instrument
BITS = {"fx8": 8, "fx12": 12, "fx16": 16, "fx24": 24, "fx32": 32, "wide": None}
BITS.update({f"fx{b}": b for b in range(8, 17)})   # the fine ladder used only by the threshold REFINEMENT
FINE = tuple(f"fx{b}" for b in range(8, 17))
LADDER = ("fx8", "fx12", "fx16", "fx24", "fx32", "wide")

PREDS = (
    ("bit0", lambda x: (x >> 0) & 1),
    ("bit1", lambda x: (x >> 1) & 1),
    ("bit2", lambda x: (x >> 2) & 1),
    ("bit3", lambda x: (x >> 3) & 1),
    ("bit0_and_bit1", lambda x: ((x >> 0) & 1) & ((x >> 1) & 1)),
    ("bit0_or_bit1", lambda x: ((x >> 0) & 1) | ((x >> 1) & 1)),
    ("bit2_xor_bit3", lambda x: ((x >> 2) & 1) ^ ((x >> 3) & 1)),
    ("const1", lambda x: 1),
)
PRED_PRIOR = (4, 2, 2, 2, 1, 1, 1, 1)   # declared integer prior over predicates (a description-length prior)
VALS_AMBIG = ((F(7, 8), F(1, 8)), (F(3, 4), F(1, 4)), (F(5, 8), F(3, 8)), (F(1, 2), F(1, 2)))
ETAS_NOISY = (F(1, 10), F(1, 5), F(3, 10), F(2, 5))
SEEN = [x for x in X_ALL if ((x >> 0) & 1) == ((x >> 1) & 1)]        # {0,3,4,7,8,11,12,15}
UNSEEN = [x for x in X_ALL if x not in SEEN]                          # {1,2,5,6,9,10,13,14}
N_EVENTS = 24
REVOKE_AT = 13            # the revocation is executed after event 13 ...
REVOKE_INDEX = 1          # ... and removes event index 1 of the declared sequence
FLIPS_AMBIG = (5, 18)
FLIPS_NOISY = (3, 8, 14, 19, 22)
# variant B: a SECOND declared flip schedule, the G2-style replication (a different event sequence, same rates)
FLIPS_AMBIG_B = (9, 22)
FLIPS_NOISY_B = (1, 7, 12, 17, 21)
# variant C: a THIRD declared flip schedule, written into the code BEFORE the freeze and NOT executed before it,
# so that RV-377-066 carries at least one genuinely blind clause (clause 12)
FLIPS_AMBIG_C = (2, 13)
FLIPS_NOISY_C = (0, 6, 11, 16, 23)


# --------------------------------------------------------------------------------------- the instrument
class Arith:
    """One DECLARED precision instrument. Every method charges exactly one primitive activation (a division
    charges the fixed DIV_CHARGE macro), so the charged operation sequence of a row is IDENTICAL under every
    instrument and any capability difference is attributable to precision alone (GMI-DA5)."""

    def __init__(self, M, precision):
        b = BITS[precision]
        self.M = M; self.precision = precision; self.bits = b
        self.Fb = WIDE_FRAC if b is None else b // 2
        self.S = 1 << self.Fb
        self.hi = None if b is None else (1 << (b - 1)) - 1
        self.lo = None if b is None else -(1 << (b - 1))
        self.n_ops = 0

    def clamp(self, v):
        if self.hi is None: return v
        return self.hi if v > self.hi else self.lo if v < self.lo else v

    def add(self, a, b): self.M.op("ADD", 0, 0); self.n_ops += 1; return self.clamp(a + b)

    def sub(self, a, b): self.M.op("SUB", 0, 0); self.n_ops += 1; return self.clamp(a - b)

    def mul(self, a, b):
        self.M.op("MUL", 0, 0); self.n_ops += 1
        return self.clamp((a * b + (1 << (self.Fb - 1))) >> self.Fb)

    def gt(self, a, b): self.M.op("GT", 0, 0); self.n_ops += 1; return int(a > b)

    def eq(self, a, b): self.M.op("EQ", 0, 0); self.n_ops += 1; return int(a == b)

    def div(self, a, b):
        """charged restoring division: a DECLARED fixed macro of 16 MUL + 16 GT, identical for every instrument
        (an instrument note in the RV-377-031 sense: the wide instrument's true division cost is under-charged,
        deliberately, so that the charged op sequences stay identical)."""
        for _ in range(DIV_CHARGE // 2): self.M.op("MUL", 0, 0); self.M.op("GT", 0, 0)
        self.n_ops += DIV_CHARGE
        if b == 0: return 0
        num = a * self.S; neg = (num < 0) != (b < 0)
        n, d = abs(num), abs(b); q = (n + d // 2) // d
        return self.clamp(-q if neg else q)

    def const(self, fr):
        """an exact rational stored in the carrier's description, rounded to the instrument's grid (uncharged:
        it is part of desc, not of exec)."""
        n, d = fr.numerator, fr.denominator
        v = (abs(n) * self.S * 2 + d) // (2 * d)
        return self.clamp(v if n >= 0 else -v)

    def frac(self, v): return F(v, self.S)

    def one(self): return self.S


# --------------------------------------------------------------------------------------- the ecologies
def _hyp_table(kind):
    """the declared hypothesis class: 8 predicates x 4 value pairs, with the declared integer prior."""
    hyps = []
    vals = VALS_AMBIG if kind == "ambig" else tuple((1 - e, e) for e in ETAS_NOISY)
    for pi, (pname, pf) in enumerate(PREDS):
        for vi, (hi, lo) in enumerate(vals):
            hyps.append({"pred": pname, "vi": vi, "prior": PRED_PRIOR[pi],
                         "p": {x: (hi if pf(x) else lo) for x in X_ALL}})
    return hyps


def ecology(kind, variant="A"):
    hyps = _hyp_table(kind)
    truth = (lambda x: (x >> 0) & 1) if kind == "ambig" else (lambda x: (x >> 3) & 1)
    flips = set({("ambig", "A"): FLIPS_AMBIG, ("ambig", "B"): FLIPS_AMBIG_B,
                 ("ambig", "C"): FLIPS_AMBIG_C, ("noisy", "A"): FLIPS_NOISY,
                 ("noisy", "B"): FLIPS_NOISY_B, ("noisy", "C"): FLIPS_NOISY_C}[(kind, variant)])
    events = []
    for i in range(N_EVENTS):
        x = SEEN[i % len(SEEN)]; y = truth(x)
        events.append((x, (1 - y) if i in flips else y))
    ev_final = [e for i, e in enumerate(events) if i != REVOKE_INDEX]
    post = []
    for h in hyps:
        w = F(h["prior"])
        for x, y in ev_final:
            w *= h["p"][x] if y else (1 - h["p"][x])
        post.append(w)
    Z = sum(post); post = [w / Z for w in post]
    ev_x = X_ALL if kind == "noisy" else UNSEEN
    qstar = {x: sum(post[j] * hyps[j]["p"][x] for j in range(len(hyps))) for x in ev_x}
    qbar = sum(qstar.values()) / len(ev_x)
    var = sum((qstar[x] - qbar) ** 2 for x in ev_x)
    return {"kind": kind, "variant": variant, "hyps": hyps, "events": events, "events_final": ev_final, "eval": ev_x,
            "post": post, "qstar": qstar, "qbar": qbar, "var": var, "n_hyps": len(hyps)}


def capability(eco, served):
    """Brier SKILL score against the declared base-rate forecaster, exact rational; theta = 0.85."""
    num = sum((served[x] - eco["qstar"][x]) ** 2 for x in eco["eval"])
    return max(F(0), 1 - num / eco["var"]), num


# --------------------------------------------------------------------------------------- rows
class Row:
    """Every row declares (i) w_scalars, the stored NUMERIC scalars, which are what an instrument's word width
    would scale, and (ii) struct_bits, the instrument-independent structural description (hypothesis codes,
    predicate definitions, program length). desc is charged flat (w_scalars * 8 + struct_bits) for every
    instrument -- the same basis, deliverable 2 -- and `desc_bits_scaled` is the declared sensitivity."""
    row = "?"

    def __init__(self, eco, A):
        self.e = eco; self.A = A; self.w_scalars = 0; self.struct_bits = 0
        self.nat = {"exec": 0, "upd": 0, "ver": 0, "rev": 0}
        self.M = None

    def _n(self, M, k=1): self.nat[M.L.phase] += k

    def init(self, M): pass

    def observe(self, M, x, y): pass

    def revoke(self, M, idx, x, y): pass

    def query(self, M, x): raise NotImplementedError

    def desc_bits(self): return self.w_scalars * DESC_BITS_PER_SCALAR + self.struct_bits

    def desc_bits_scaled(self):
        wb = (WIDE_FRAC + 8) if self.A.bits is None else self.A.bits
        return self.w_scalars * wb + self.struct_bits


CLASS_STRUCT_BITS = 32 * 5 + 8 * 16   # 32 hypothesis codes (3-bit predicate + 2-bit value pair) + 8 predicate truth tables


class _Mixture(Row):
    """shared carrier state for every row that holds a weight over the declared hypothesis class."""

    def init(self, M):
        A = self.A; e = self.e; K = e["n_hyps"]
        self.P = [[A.const(h["p"][x]) for x in X_ALL] for h in e["hyps"]]
        tot = sum(h["prior"] for h in e["hyps"])
        self.pri = [A.const(F(h["prior"], tot)) for h in e["hyps"]]
        self.w = list(self.pri); self.hist = []
        self.w_scalars = K; self.struct_bits = CLASS_STRUCT_BITS

    def _condition(self, M, x, y):
        A = self.A; K = self.e["n_hyps"]
        for j in range(K):
            like = self.P[j][x] if y else A.sub(A.one(), self.P[j][x])
            self.w[j] = A.mul(self.w[j], like)
        s = 0
        for j in range(K): s = A.add(s, self.w[j])
        for j in range(K): self.w[j] = A.div(self.w[j], s)
        self._n(M, K)

    def _neutral(self, M):
        A = self.A; K = self.e["n_hyps"]
        for j in range(K): self.w[j] = A.mul(self.w[j], A.one())
        s = 0
        for j in range(K): s = A.add(s, self.w[j])
        for j in range(K): self.w[j] = A.div(self.w[j], s)
        self._n(M, K)

    def observe(self, M, x, y):
        self.hist.append((x, y)); self._condition(M, x, y)

    def revoke(self, M, idx, x, y):
        """exact re-derivation from the retained evidence; the revoked slot is replayed as a NEUTRAL event
        (a charged multiply by one), so a revocation's charged op count is data-independent."""
        self.w = list(self.pri)
        for i, (hx, hy) in enumerate(self.hist):
            if i == idx: self._neutral(M)
            else: self._condition(M, hx, hy)
        self.hist = [ev for i, ev in enumerate(self.hist) if i != idx]


class Bayes(_Mixture):
    """D3, the probabilistic carrier: the posterior mixture over the whole declared class."""
    row = "BAYES"

    def query(self, M, x):
        A = self.A; acc = 0
        for j in range(self.e["n_hyps"]): acc = A.add(acc, A.mul(self.w[j], self.P[j][x]))
        self._n(M, self.e["n_hyps"])
        return acc


class MapHyp(_Mixture):
    """the SAME evidence-weighing machinery served as a POINT ESTIMATE IN HYPOTHESIS SPACE (rule 19: this is
    the strongest opponent, because it pays the same update price and a constant readout price)."""
    row = "MAP"

    def init(self, M):
        super().init(M); self.best = 0; self.w_scalars = self.e["n_hyps"]; self.struct_bits = CLASS_STRUCT_BITS + 5

    def _pick(self, M):
        A = self.A; b = 0
        for j in range(1, self.e["n_hyps"]):
            if A.gt(self.w[j], self.w[b]): b = j
        self.best = b; self._n(M, self.e["n_hyps"])

    def observe(self, M, x, y): super().observe(M, x, y); self._pick(M)

    def revoke(self, M, idx, x, y): super().revoke(M, idx, x, y); self._pick(M)

    def query(self, M, x):
        self.A.eq(0, 0); self._n(M)
        return self.P[self.best][x]


class UnifMix(_Mixture):
    """negative twin: the mixture machinery with the evidence discarded."""
    row = "UNIFMIX"

    def init(self, M):
        super().init(M); self.u = self.A.const(F(1, self.e["n_hyps"]))
        self.w_scalars = 1; self.struct_bits = CLASS_STRUCT_BITS

    def observe(self, M, x, y): self.A.add(0, 0); self._n(M)

    def revoke(self, M, idx, x, y): self.A.add(0, 0); self._n(M)

    def query(self, M, x):
        A = self.A; acc = 0
        for j in range(self.e["n_hyps"]): acc = A.add(acc, A.mul(self.u, self.P[j][x]))
        self._n(M, self.e["n_hyps"])
        return acc


class QCount(_Mixture):
    """THE ADVERSARIAL 8-BIT POSTERIOR APPROXIMATOR (protocol rule 19). It never multiplies likelihoods, so
    nothing underflows; it counts in declared units of 1/EVENT_SCALE, so nothing saturates; it keeps only the
    top M = 4 hypotheses, so its normalized weights are about 1/4 and ARE representable at 4 fractional bits.
    This is the strongest posterior approximation this lane can build inside the registered 8-bit universe."""
    row = "QCOUNT"

    def init(self, M):
        super().init(M)
        A = self.A; K = self.e["n_hyps"]
        self.c = [0] * K; self.unit = A.const(F(1, EVENT_SCALE))
        self.expl = [[1 if self.e["hyps"][j]["p"][x] >= F(1, 2) else 0 for x in X_ALL] for j in range(K)]
        self.top = list(range(M_TOP)); self.tw = [A.const(F(1, M_TOP))] * M_TOP
        self.w_scalars = K + M_TOP; self.struct_bits = CLASS_STRUCT_BITS + M_TOP * 5

    def _rank(self, M):
        A = self.A; K = self.e["n_hyps"]; used = []
        for _ in range(M_TOP):
            b = -1
            for j in range(K):
                g = A.gt(self.c[j], self.c[b] if b >= 0 else -1)
                if j not in used and (b < 0 or g): b = j
            used.append(b)
        self.top = used
        s = 0
        for j in used: s = A.add(s, self.c[j])
        self.tw = [A.div(self.c[j], s) for j in used]
        self._n(M, self.e["n_hyps"])

    def observe(self, M, x, y):
        A = self.A; self.hist.append((x, y))
        for j in range(self.e["n_hyps"]):
            self.c[j] = A.add(self.c[j], self.unit if self.expl[j][x] == y else 0)
        self._n(M, self.e["n_hyps"]); self._rank(M)

    def revoke(self, M, idx, x, y):
        A = self.A
        for j in range(self.e["n_hyps"]):
            self.c[j] = A.sub(self.c[j], self.unit if self.expl[j][x] == y else 0)
        self.hist = [ev for i, ev in enumerate(self.hist) if i != idx]
        self._n(M, self.e["n_hyps"]); self._rank(M)

    def query(self, M, x):
        A = self.A; acc = 0
        for m in range(M_TOP): acc = A.add(acc, A.mul(self.tw[m], self.P[self.top[m]][x]))
        self._n(M, M_TOP)
        return acc


class BayesPruned(_Mixture):
    """THE STRONGEST 8-BIT BAYESIAN OPPONENT (protocol rule 19), and the second thing the task asks for: a row
    that approximates the posterior inside the registered 8-bit universe. It applies the two standard
    anti-underflow devices of practical Bayesian computation:
      (i)  MAX-renormalization after every conditioning step (the largest weight is pinned at 1.0, so the
           informative weights never fall below the instrument's smallest positive value merely because the
           class is large), instead of sum-normalization which drives all 32 weights to about 1/32; and
      (ii) PRUNING to the top M = 4 at readout, so the mixture weights it must represent are about 1/4.
    If this row is admissible at 8 bits then a probabilistic carrier is admissible at 8 bits and the
    precision-gated-kingdom claim is dead on arrival, which is exactly the point of building it."""
    row = "BAYESM"

    def init(self, M):
        super().init(M)
        self.top = list(range(M_TOP)); self.tw = [self.A.const(F(1, M_TOP))] * M_TOP
        self.w_scalars = self.e["n_hyps"] + M_TOP; self.struct_bits = CLASS_STRUCT_BITS + M_TOP * 5

    def _renorm_max(self, M):
        A = self.A; K = self.e["n_hyps"]; b = 0
        for j in range(1, K):
            if A.gt(self.w[j], self.w[b]): b = j
        mx = self.w[b]
        for j in range(K): self.w[j] = A.div(self.w[j], mx) if mx else self.w[j]
        self._n(M, K)

    def _condition(self, M, x, y):
        A = self.A; K = self.e["n_hyps"]
        for j in range(K):
            like = self.P[j][x] if y else A.sub(A.one(), self.P[j][x])
            self.w[j] = A.mul(self.w[j], like)
        self._renorm_max(M)

    def _neutral(self, M):
        A = self.A
        for j in range(self.e["n_hyps"]): self.w[j] = A.mul(self.w[j], A.one())
        self._renorm_max(M)


    def _rank(self, M):
        A = self.A; K = self.e["n_hyps"]; used = []
        for _ in range(M_TOP):
            b = -1
            for j in range(K):
                g = A.gt(self.w[j], self.w[b] if b >= 0 else -1)
                if j not in used and (b < 0 or g): b = j
            used.append(b)
        self.top = used
        s = 0
        for j in used: s = A.add(s, self.w[j])
        self.tw = [A.div(self.w[j], s) for j in used]
        self._n(M, self.e["n_hyps"])

    def observe(self, M, x, y): super().observe(M, x, y); self._rank(M)

    def revoke(self, M, idx, x, y): super().revoke(M, idx, x, y); self._rank(M)

    def query(self, M, x):
        A = self.A; acc = 0
        for m in range(M_TOP): acc = A.add(acc, A.mul(self.tw[m], self.P[self.top[m]][x]))
        self._n(M, M_TOP)
        return acc


class Prog(Row):
    """program search (D4/D5) over the 16 deterministic classifiers (8 predicates and their negations),
    scored by matches and served as a 0/1 LABEL: the classical point-estimate carrier."""
    row = "PROG"

    def init(self, M):
        A = self.A
        self.progs = [(pf, neg) for _, pf in PREDS for neg in (0, 1)]
        self.score = [0] * len(self.progs); self.unit = A.const(F(1, EVENT_SCALE))
        self.out = [[(pf(x) ^ neg) for x in X_ALL] for pf, neg in self.progs]
        self.best = 0
        self.w_scalars = len(self.progs); self.struct_bits = len(self.progs) * 4 + 8 * 16 + 4

    def _pick(self, M):
        A = self.A; b = 0
        for k in range(1, len(self.progs)):
            if A.gt(self.score[k], self.score[b]): b = k
        self.best = b

    def observe(self, M, x, y):
        A = self.A
        for k in range(len(self.progs)):
            self.score[k] = A.add(self.score[k], self.unit if self.out[k][x] == y else 0)
        self._pick(M); self._n(M, len(self.progs))

    def revoke(self, M, idx, x, y):
        A = self.A
        for k in range(len(self.progs)):
            self.score[k] = A.sub(self.score[k], self.unit if self.out[k][x] == y else 0)
        self._pick(M); self._n(M, len(self.progs))

    def query(self, M, x):
        self.A.eq(0, 0); self._n(M)
        return self.A.one() if self.out[self.best][x] else 0


class Coef(Row):
    """D1 coefficient/gradient row: q(x) = c0 + sum_i c_i bit_i(x), squared-error gradient step at LR = 1/4."""
    row = "COEF"

    def init(self, M):
        A = self.A
        self.c = [A.const(F(1, 2)), 0, 0, 0, 0]; self.lr = A.const(F(1, 4))
        self.w_scalars = 6; self.struct_bits = 10

    def _fwd(self, M, x):
        A = self.A; s = self.c[0]
        for i in range(4): s = A.add(s, A.mul(self.c[i + 1], A.one() if (x >> i) & 1 else 0))
        return s

    def _step(self, M, x, y, sign):
        A = self.A; out = self._fwd(M, x); err = A.sub(out, A.one() if y else 0)
        g = A.mul(self.lr, err)
        g = A.sub(0, g) if sign < 0 else A.add(g, 0)
        self.c[0] = A.sub(self.c[0], g)
        for i in range(4): self.c[i + 1] = A.sub(self.c[i + 1], A.mul(g, A.one() if (x >> i) & 1 else 0))

    def observe(self, M, x, y): self._step(M, x, y, +1); self._n(M)

    def revoke(self, M, idx, x, y): self._step(M, x, y, -1); self._n(M)

    def query(self, M, x):
        A = self.A; v = self._fwd(M, x); self._n(M)
        lo = A.gt(0, v); hi = A.gt(v, A.one())
        return 0 if lo else (A.one() if hi else v)


class Exemplar(Row):
    """D2 exemplar store: per-input (sum, count) in units of 1/EVENT_SCALE; the stored frequency where the
    input was seen, the running base rate elsewhere."""
    row = "EXEM"

    def init(self, M):
        A = self.A
        self.s = [0] * 16; self.n = [0] * 16; self.gs = 0; self.gn = 0
        self.unit = A.const(F(1, EVENT_SCALE))
        self.w_scalars = 34; self.struct_bits = 16 * 4

    def _upd(self, M, x, y, sign):
        A = self.A; d = self.unit if y else 0
        for k in X_ALL: A.eq(k, x)
        if sign > 0:
            self.s[x] = A.add(self.s[x], d); self.n[x] = A.add(self.n[x], self.unit)
            self.gs = A.add(self.gs, d); self.gn = A.add(self.gn, self.unit)
        else:
            self.s[x] = A.sub(self.s[x], d); self.n[x] = A.sub(self.n[x], self.unit)
            self.gs = A.sub(self.gs, d); self.gn = A.sub(self.gn, self.unit)

    def observe(self, M, x, y): self._upd(M, x, y, +1); self._n(M)

    def revoke(self, M, idx, x, y): self._upd(M, x, y, -1); self._n(M)

    def query(self, M, x):
        A = self.A; self._n(M)
        for k in X_ALL: A.eq(k, x)
        loc = A.div(self.s[x], self.n[x]); glob = A.div(self.gs, self.gn)
        return loc if A.gt(self.n[x], 0) else glob


class Generalizing(Row):
    """D2 generalizing store (the S5h carrier of RV-377-025): the Hamming-nearest-neighbour average of the
    stored frequencies. This is the row that actually threatens both ecologies."""
    row = "GEN"

    def init(self, M):
        A = self.A
        self.s = [0] * 16; self.n = [0] * 16; self.unit = A.const(F(1, EVENT_SCALE))
        self.pen = A.const(F(5))
        self.w_scalars = 32; self.struct_bits = 16 * 4 + 14

    def _upd(self, M, x, y, sign):
        A = self.A; d = self.unit if y else 0
        for k in X_ALL: A.eq(k, x)
        if sign > 0: self.s[x] = A.add(self.s[x], d); self.n[x] = A.add(self.n[x], self.unit)
        else: self.s[x] = A.sub(self.s[x], d); self.n[x] = A.sub(self.n[x], self.unit)

    def observe(self, M, x, y): self._upd(M, x, y, +1); self._n(M)

    def revoke(self, M, idx, x, y): self._upd(M, x, y, -1); self._n(M)

    def query(self, M, x):
        A = self.A; self._n(M, 16)          # declared native price: the whole store is scanned (memory bound)
        d = []
        for k in X_ALL:
            acc = 0
            for i in range(4): acc = A.add(acc, A.one() if ((k >> i) & 1) != ((x >> i) & 1) else 0)
            live = A.gt(self.n[k], 0)
            d.append(acc if live else A.add(acc, self.pen))
        best = d[0]
        for k in range(1, 16):
            if A.gt(best, d[k]): best = d[k]
        num = 0; den = 0
        for k in X_ALL:
            hit = A.eq(d[k], best)
            num = A.add(num, self.s[k] if hit else 0); den = A.add(den, self.n[k] if hit else 0)
        return A.div(num, den)


class BaseRate(Row):
    """negative twin: the running base rate served everywhere (capability 0 by construction: it IS the
    reference forecaster of the Brier skill score)."""
    row = "BASE"

    def init(self, M):
        A = self.A; self.gs = 0; self.gn = 0; self.unit = A.const(F(1, EVENT_SCALE))
        self.w_scalars = 2; self.struct_bits = 4

    def observe(self, M, x, y):
        A = self.A; self.gs = A.add(self.gs, self.unit if y else 0); self.gn = A.add(self.gn, self.unit); self._n(M)

    def revoke(self, M, idx, x, y):
        A = self.A; self.gs = A.sub(self.gs, self.unit if y else 0); self.gn = A.sub(self.gn, self.unit); self._n(M)

    def query(self, M, x): self._n(M); return self.A.div(self.gs, self.gn)


ROWS = {c.row: c for c in (Bayes, BayesPruned, MapHyp, QCount, Prog, Coef, Exemplar, Generalizing, UnifMix, BaseRate)}

# THE PROBABILISTIC CARRIER (D3), declared: a carrier whose sufficient state is a NORMALIZED WEIGHT
# DISTRIBUTION over an explicit hypothesis class, served as a posterior mixture. Three realizations of it are
# registered -- the exact posterior (BAYES), the max-renormalized pruned posterior (BAYESM) and the
# quantized-count posterior (QCOUNT) -- and the last two were built as ADVERSARIAL 8-BIT OPPONENTS under
# protocol rule 19. The domain decision is taken over D3_ROWS; the exact-posterior row's own decision is
# reported separately, because which of the two answers a reader wants is a real question and both are here.
D3_ROWS = ("BAYES", "BAYESM", "QCOUNT")
CARRIER = "BAYES"


# --------------------------------------------------------------------------------------- execution
def run(row, basis, eco, precision, seed=0):
    M = Machine(basis, seed=seed); A = Arith(M, precision); ref = ROWS[row](eco, A)
    M.phase("exec"); ref.init(M)
    ev = eco["events"]; nev = len(eco["eval"])
    for t, (x, y) in enumerate(ev, 1):
        M.phase("exec")
        for xx in eco["eval"]: ref.query(M, xx)
        M.phase("upd"); ref.observe(M, x, y); M.end_event()
        M.phase("ver")
        for xx in eco["eval"]: M.op("EQ", ref.query(M, xx), 0)
        if t == REVOKE_AT:
            M.phase("rev"); ref.revoke(M, REVOKE_INDEX, *ev[REVOKE_INDEX]); M.end_event()
    M.phase("exec")
    served = {xx: ref.query(M, xx) for xx in eco["eval"]}
    sfr = {xx: A.frac(v) for xx, v in served.items()}
    cap, excess = capability(eco, sfr)
    R = dict(M.L.c); nat = dict(ref.nat)
    return {"row": row, "precision": precision, "capability": float(round(cap, 6)),
            "capability_exact": f"{cap.numerator}/{cap.denominator}", "admissible": bool(cap >= THETA),
            "brier_excess_exact": f"{excess.numerator}/{excess.denominator}",
            "R": R, "native_R": nat, "charged_ops_total": A.n_ops,
            "exec_q": F(R["exec"], nev * (N_EVENTS + 1)), "upd_e": F(R["upd"], N_EVENTS),
            "ver_e": F(R["ver"], N_EVENTS), "rev_e": F(R["rev"]),
            "nat_exec_q": F(nat["exec"], nev * (N_EVENTS + 1)), "nat_upd_e": F(nat["upd"], N_EVENTS),
            "nat_ver_e": F(nat["ver"], N_EVENTS), "nat_rev_e": F(nat["rev"]),
            "desc_bits": ref.desc_bits(), "desc_bits_scaled": ref.desc_bits_scaled(),
            "w_scalars": ref.w_scalars, "struct_bits": ref.struct_bits,
            "served": {str(xx): f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]},
            "answer_signature": sha256_of([f"{sfr[xx].numerator}/{sfr[xx].denominator}" for xx in eco["eval"]])}


def fx8_identity_check():
    """the fx8 instrument must be BIT-IDENTICAL to the registered 8-bit universe (core.Machine.op), or the
    'registered 8-bit universe' column of this microscope is not the registered universe at all."""
    M = Machine(bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]); A = Arith(M, "fx8")
    n = 0
    for a in range(-128, 128):
        for b in range(-128, 128):
            assert A.mul(a, b) == M.op("MUL", a, b) and A.add(a, b) == M.op("ADD", a, b) \
                and A.sub(a, b) == M.op("SUB", a, b) and A.gt(a, b) == M.op("GT", a, b), (a, b)
            n += 4
    return {"pairs_checked": 256 * 256, "assertions": n, "bit_identical_to_registered_universe": True}


def per_event(c, price, scaled=False):
    """the frozen cost model's per-event vector under a declared price vector."""
    desc = F(c["desc_bits_scaled"] if scaled else c["desc_bits"])
    if price == "reduced":
        return {"desc": desc, "exec_q": c["exec_q"], "upd_e": c["upd_e"], "ver_e": c["ver_e"], "rev_e": c["rev_e"]}
    return {"desc": desc, "exec_q": c["nat_exec_q"], "upd_e": c["nat_upd_e"], "ver_e": c["nat_ver_e"], "rev_e": c["nat_rev_e"]}


def cost(pe, Hh, r):
    return pe["desc"] + Hh * pe["exec_q"] + r * (pe["upd_e"] + pe["ver_e"]) + F(r, 4) * pe["rev_e"]


def crossovers(pes):
    """analytic pairwise crossovers of the affine cost function, in H (at r = 0) and in r (at H = 0)."""
    out = {}; names = sorted(pes)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pa, pb = pes[a], pes[b]
            de = pb["exec_q"] - pa["exec_q"]
            if de != 0:
                h = (pa["desc"] - pb["desc"]) / de
                if h > 0: out[f"H|{a}|{b}"] = h
            dr = (pb["upd_e"] + pb["ver_e"] + pb["rev_e"] / 4) - (pa["upd_e"] + pa["ver_e"] + pa["rev_e"] / 4)
            if dr != 0:
                rr = (pa["desc"] - pb["desc"]) / dr
                if rr > 0: out[f"r|{a}|{b}"] = rr
    return out


def grid_from(cross, axis, base):
    """DG-2: the grid must extend past TWICE the analytic crossover of every pair under this price vector."""
    g = set(base)
    for k, v in cross.items():
        if not k.startswith(axis + "|"): continue
        f = int(v) + 1
        g.add(max(1, int(v))); g.add(f); g.add(2 * f)
    return sorted(g)


def frontier_for(pes, hg, rg):
    fr = {}
    for Hh in hg:
        for r in rg:
            if not pes: fr[f"H={Hh}|r={r}"] = []; continue
            cs = {n: cost(p, Hh, r) for n, p in pes.items()}; m = min(cs.values())
            fr[f"H={Hh}|r={r}"] = sorted(n for n, v in cs.items() if v == m)
    return fr


def asymptotics(pes):
    if not pes: return {}
    def argmins(f):
        vals = {n: f(p) for n, p in pes.items()}; m = min(vals.values())
        return sorted(n for n, v in vals.items() if v == m)
    return {"at_H1_r0_min_cost": argmins(lambda p: p["desc"] + p["exec_q"]),
            "H_to_infinity_min_exec_q": argmins(lambda p: p["exec_q"]),
            "r_to_infinity_min_upd_ver_rev": argmins(lambda p: p["upd_e"] + p["ver_e"] + p["rev_e"] / 4)}


def main(tag="DK_V2_PRECISION_GATED", seed=0, ladder=LADDER, out=None, verbose=True):
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"; b = bases.ALL[col]
    ecos = {k: ecology(k) for k in ("noisy", "ambig")}
    cells = {}
    for ek, eco in ecos.items():
        for rname in ROWS:
            for p in ladder: cells[(ek, rname, p)] = run(rname, b, eco, p, seed)

    opeq = {}
    for ek in ecos:
        for rname in ROWS:
            ref = cells[(ek, rname, ladder[0])]
            same = all(cells[(ek, rname, p)]["R"] == ref["R"] and
                       cells[(ek, rname, p)]["charged_ops_total"] == ref["charged_ops_total"] and
                       cells[(ek, rname, p)]["native_R"] == ref["native_R"] for p in ladder)
            opeq[f"{ek}|{rname}"] = {"identical_across_instruments": bool(same),
                                     "charged_ops_total": ref["charged_ops_total"], "R": ref["R"],
                                     "native_R": ref["native_R"],
                                     "by_instrument": {p: cells[(ek, rname, p)]["charged_ops_total"] for p in ladder}}
    all_op_equal = all(v["identical_across_instruments"] for v in opeq.values())

    adm = {f"{ek}|{p}": sorted(r for r in ROWS if cells[(ek, r, p)]["admissible"]) for ek in ecos for p in ladder}
    A8 = {ek: set(adm[f"{ek}|fx8"]) for ek in ecos}

    frontier = {}; crossall = {}; grids = {}; asym = {}; gated = {}
    for ek in ecos:
        for scaled in (False, True):
            for price in ("reduced", "native"):
                for p in ladder:
                    key = f"{ek}|{p}|{price}|{'scaled' if scaled else 'flat'}"
                    pes = {r: per_event(cells[(ek, r, p)], price, scaled) for r in adm[f"{ek}|{p}"]}
                    cr = crossovers(pes); crossall[key] = {k: float(v) for k, v in cr.items()}
                    hg = grid_from(cr, "H", (1, 2, 16, 128, 1024, 8192))
                    rg = grid_from(cr, "r", (0, 1, 4, 16, 64, 256))
                    grids[key] = {"H": hg, "r": rg}
                    fr = frontier_for(pes, hg, rg); frontier[key] = fr
                    asym[key] = asymptotics(pes)
                    g3 = [c for c, occ in fr.items() if (set(occ) & set(D3_ROWS)) and not (set(occ) & A8[ek])]
                    gb = [c for c, occ in fr.items() if CARRIER in occ and not (set(occ) & A8[ek])]
                    gated[key] = {"n_cells": len(fr), "n_gated_d3": len(g3), "n_gated_carrier": len(gb),
                                  "gated_cells_d3": g3[:64], "gated_cells_carrier": gb[:64],
                                  "carrier_sole_occupant_cells": sum(1 for occ in fr.values() if occ == [CARRIER]),
                                  "occupants_over_grid": sorted({r for occ in fr.values() for r in occ})}
    d3_8bit_admissible = {ek: sorted(set(D3_ROWS) & A8[ek]) for ek in ecos}
    carrier_8bit_admissible = {ek: CARRIER in A8[ek] for ek in ecos}

    # DECISION. A cell is PRECISION-GATED for a carrier set S at instrument p iff some member of S occupies it
    # and NO member of A8 (the rows admissible in the registered 8-bit universe) occupies it. The kingdom is
    # established for S iff such a cell exists in an ecology where NO member of S is itself admissible at 8
    # bits -- otherwise the carrier is not gated by precision at all, only priced by it.
    def decide(S):
        keys = [k for k, v in gated.items()
                if v["n_gated_" + S] > 0 and not (set(D3_ROWS if S == "d3" else [CARRIER]) & A8[k.split("|")[0]])]
        if not keys: return None, keys
        return LADDER[min(LADDER.index(k.split("|")[1]) for k in keys)], keys

    # THE THRESHOLD IS THE SCIENTIFIC CONTENT: bisect the instrument on the fine ladder 8..16 bits, per ecology
    # and per D3 realization, so the declared ladder's answer is not confused with the true crossing.
    refine = {}
    for ek, eco in ecos.items():
        refine[ek] = {}
        for rname in D3_ROWS:
            caps = {}
            for pr in FINE:
                caps[pr] = run(rname, b, eco, pr, seed)["capability"]
            first = next((BITS[pr] for pr in FINE if F(round(caps[pr] * 10 ** 6), 10 ** 6) >= THETA), None)
            refine[ek][rname] = {"capability_by_bits": {str(BITS[pr]): caps[pr] for pr in FINE},
                                 "fractional_bits_by_total": {str(BITS[pr]): BITS[pr] // 2 for pr in FINE},
                                 "smallest_admissible_total_bits": first}
        firsts = [refine[ek][r]["smallest_admissible_total_bits"] for r in D3_ROWS
                  if refine[ek][r]["smallest_admissible_total_bits"] is not None]
        refine[ek]["smallest_admissible_total_bits_any_d3_row"] = min(firsts) if firsts else None

    # G2-style replication on a SECOND declared event sequence, and a second machine seed. Every row here is
    # deterministic (no SAMPLE activations), so seed-invariance is a prediction, not a hope.
    rep = {}
    for ek, var in [(e, v) for e in ecos for v in ("B", "C")]:
        e2 = ecology(ek, var)
        caps = {f"{r}|{p}": run(r, b, e2, p, seed)["capability"] for r in ROWS for p in ladder}
        a2 = {p: sorted(r for r in ROWS if F(round(caps[f"{r}|{p}"] * 10 ** 6), 10 ** 6) >= THETA) for p in ladder}
        rep[f"{ek}|{var}"] = {"events": [list(x) for x in e2["events"]],
                   "qstar_float": {str(x): float(v) for x, v in e2["qstar"].items()},
                   "variance_float": float(e2["var"]), "capability": caps, "admissible_sets": a2,
                   "d3_admissible_at_8_bits": sorted(set(D3_ROWS) & set(a2["fx8"])),
                   "any_row_admissible_at_8_bits": a2["fx8"]}
    seedchk = {f"{ek}|{r}": (cells[(ek, r, "wide")]["capability"] == run(r, b, ecos[ek], "wide", 1)["capability"]
                             and cells[(ek, r, "fx8")]["capability"] == run(r, b, ecos[ek], "fx8", 1)["capability"])
               for ek in ecos for r in ROWS}

    thr_d3, keys_d3 = decide("d3")
    thr_bayes, keys_bayes = decide("carrier")
    threshold = thr_d3
    terminal = (f"PRECISION_GATED_KINGDOM_ESTABLISHED_AT_SCOPE__THRESHOLD_{BITS[threshold]}_BITS"
                if threshold else "NO_PRECISION_GATED_KINGDOM__AN_8_BIT_PARENT_OCCUPIES_EVERY_CELL")
    receipt = {
        "schema": "StageDKPrecisionGatedV2", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
        "revival_record": "RV-377-066", "run_tag": tag, "seed": seed,
        "question": "is there an ecology in which, at wide precision, the probabilistic carrier occupies frontier cells that NO carrier admissible at 8 bits occupies at any reuse horizon?",
        "theta": "17/20", "cost_model": "C = desc + H*exec_q + r*(upd_e + ver_e) + (r/4)*rev_e",
        "frontier_rule": "protocol rule 17: the frontier is over the largest declared size of each row; a row OCCUPIES a cell iff it is admissible AND its exact-rational lifecycle cost equals the minimum over the rows admissible AT THE SAME INSTRUMENT",
        "decision_rule": "a cell is PRECISION-GATED for a carrier set S at instrument p iff some member of S occupies it at p and NO member of A8 (the rows admissible in the registered 8-bit universe) occupies it. The kingdom is established for S iff such a cell exists in an ecology where no member of S is itself admissible at 8 bits. The terminal is taken over S = D3 (the probabilistic carrier, all three registered realizations); the exact-posterior row's own decision is reported alongside it. Per gap G3 the H = 0 description corner is ABSTAINED: every frontier grid here starts at H = 1.",
        "scoring_rule": "Brier (strictly proper), exact rational; capability = the Brier skill score against the declared base-rate forecaster = 1 - sum_x (q_row(x) - q*(x))^2 / sum_x (qbar - q*(x))^2, clipped at 0",
        "instruments": {p: ("unbounded integers at declared scale 2^%d" % WIDE_FRAC) if BITS[p] is None
                        else "two's complement, %d total bits, %d fractional bits, raw clamp +-%d" % (BITS[p], BITS[p] // 2, (1 << (BITS[p] - 1)) - 1)
                        for p in ladder},
        "instrument_ladder": list(ladder),
        "charged_op_identity": {"all_rows_all_cells_identical": bool(all_op_equal), "per_row": opeq},
        "description_basis": {"flat": f"w_scalars * {DESC_BITS_PER_SCALAR} bits + struct_bits, identical for every instrument (deliverable 2)",
                              "scaled": "w_scalars * the instrument's own word width + struct_bits (a declared sensitivity: charging a wide carrier's weights at 8 bits is generous to it)"},
        "declared_prices": {"reduced": "one charge per scalar primitive activation (the registered price); one division is a fixed 16 MUL + 16 GT macro, the same for every instrument",
                            "native": "one op per STATE ELEMENT the row's own law touches: a mixture row pays one per hypothesis conditioned, ranked or read out (so the exact posterior pays 32 per readout and the pruned/count rows pay 4), the program row pays one per program scored, the stores pay one per slot touched (the generalizing store scans all 16 per readout: memory bound), the coefficient row pays one per forward/backward pass"},
        "ecologies": {ek: {"eval_inputs": eco["eval"], "seen_inputs": SEEN, "n_events": N_EVENTS,
                           "revoke_after_event": REVOKE_AT, "revoked_event_index": REVOKE_INDEX,
                           "events": [list(e) for e in eco["events"]], "n_hypotheses": eco["n_hyps"],
                           "predicate_prior": list(PRED_PRIOR), "predicates": [p[0] for p in PREDS],
                           "qstar": {str(x): f"{v.numerator}/{v.denominator}" for x, v in eco["qstar"].items()},
                           "qstar_float": {str(x): float(v) for x, v in eco["qstar"].items()},
                           "base_rate": f"{eco['qbar'].numerator}/{eco['qbar'].denominator}",
                           "variance_of_qstar": f"{eco['var'].numerator}/{eco['var'].denominator}",
                           "variance_float": float(eco["var"])} for ek, eco in ecos.items()},
        "rows": list(ROWS),
        "capability": {f"{ek}|{r}|{p}": cells[(ek, r, p)]["capability"] for ek in ecos for r in ROWS for p in ladder},
        "admissible_sets": adm,
        "eight_bit_admissible_carriers": {ek: sorted(A8[ek]) for ek in ecos},
        "carrier_admissible_at_8_bits": carrier_8bit_admissible,
        "cells": {f"{ek}|{r}|{p}": {k: (str(v) if isinstance(v, F) else v) for k, v in cells[(ek, r, p)].items() if k != "row"}
                  for ek in ecos for r in ROWS for p in ladder},
        "analytic_crossovers": crossall, "frontier_grids": grids, "frontier": frontier,
        "frontier_asymptotics": asym, "precision_gated_cells": gated,
        "d3_rows": list(D3_ROWS), "carrier_row": CARRIER,
        "d3_admissible_at_8_bits": d3_8bit_admissible,
        "decision": {
            "d3_domain": {"threshold_instrument": thr_d3, "threshold_bits": BITS[thr_d3] if thr_d3 else None,
                          "gated_keys": sorted(keys_d3)},
            "exact_posterior_row_only": {"threshold_instrument": thr_bayes,
                                         "threshold_bits": BITS[thr_bayes] if thr_bayes else None,
                                         "gated_keys": sorted(keys_bayes)}},
        "threshold_refinement": refine,
        "replication_second_event_sequence": rep,
        "seed_invariance_wide_and_fx8": {"all_rows_seed_invariant": bool(all(seedchk.values())), "by_row": seedchk},
        "fx8_identity_check": fx8_identity_check(),
        "threshold_instrument": threshold, "threshold_bits": BITS[threshold] if threshold else None,
        "terminal": terminal,
        "claim_ceiling": "exact charged replay at scope. One declared event sequence, one declared hypothesis class (32 members) and one declared prior per ecology; one machine seed; no second class and no second sequence (the obvious G2-style replication). Charged ops are counted per scalar ACTIVATION, not per bit, so a wide-precision operation is charged exactly as an 8-bit one and a division is charged by a fixed macro: this is the declared basis on which the two instruments are made comparable (deliverable 2), and it is generous to the wide instrument -- the `scaled` description column is the declared sensitivity. Native prices are declared, not measured. The frontier is decided on an H,r grid extended past twice every analytic pairwise crossover, together with the exact asymptotic occupants as H -> infinity and as r -> infinity; it is not a proof over the whole non-negative quadrant. Nothing here is a claim about any real probabilistic system.",
    }
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    path = out or os.path.join(RES, "STAGE_DK_V2_PRECISION_GATED.json")
    json.dump(receipt, open(path, "w"), indent=1, sort_keys=True, default=str)
    if verbose:
        for ek in ecos:
            print(f"\n== {ek}  var(q*) = {float(ecos[ek]['var']):.6f}  base = {float(ecos[ek]['qbar']):.4f}")
            for r in ROWS:
                print(f"  {r:8s}", {p: cells[(ek, r, p)]["capability"] for p in ladder})
            for p in ladder: print(f"   adm[{p}] =", adm[f"{ek}|{p}"])
        print("\nD3 admissible at 8 bits:", d3_8bit_admissible)
        print("d3 threshold:", thr_d3, "| exact-posterior-row threshold:", thr_bayes)
        print("\ncharged op sequences identical across instruments:", all_op_equal)
        print("terminal:", terminal)
        print("sha:", receipt["receipt_sha256"][:16])
    return receipt


if __name__ == "__main__":
    main(tag=sys.argv[1] if len(sys.argv) > 1 else "DK_V2_PRECISION_GATED")
