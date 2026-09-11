"""Reference morphologies M0..M5 as programs over the primitive universe, each with (i) its parent's
own resource accounting c_M (documented per row), (ii) its native Dev protocol (which feedback
channel it consumes), (iii) a revocation (drift) semantics, and (iv) declared structural
coordinates that the runner cross-checks against measured ones.

Ecology domain shared by all rows: inputs x in Fin(4) = {0,1,2,3}; targets y in {0,1}. Every
row is asked the same registered queries after every feedback event so Q/D tables are comparable.
Sizes on the ladder scale the row's own parameter (states / rules / library / particles / hidden /
entries). No row names an architecture; the runner classifies post hoc from observables.
"""
from __future__ import annotations

from .core import FX_ONE, Machine, fx

X_DOMAIN = (0, 1, 2, 3)
BITS = lambda x: ((x >> 1) & 1, x & 1)


class Reference:
    row = "M?"
    declared = {}
    fb_channel = None  # feedback type consumed
    ladder = (2, 4, 8)

    def __init__(self, size: int):
        self.size = size

    def init(self, M: Machine): ...
    def query(self, M: Machine, x: int) -> int: ...
    def feedback(self, M: Machine, x: int, y: int): ...
    def revoke(self, M: Machine, x: int): ...
    def parent_cost(self) -> dict: ...
    def flat_table_entries(self) -> int: ...


# ---------------------------------------------------------------- M0 inert transducer
class M0Transducer(Reference):
    row = "M0"
    declared = {"execution_shape": "BOUNDED_LOOP", "store_discipline": "NONE"}
    fb_channel = None
    ladder = (2, 4, 8)

    def init(self, M):
        self.k = self.size
        M.declare("q", "fin", 0)
        # transition table q' = (q + x) mod k, output = parity of q  — fixed, no update
        M.declare_program(3)

    def query(self, M, x):
        q = M.read("q")
        nq = M.op("INC", q) if x & 1 else q
        nq = M.op("SEL", M.op("EQ", nq, self.k), 0, nq)
        M.write("q", nq)
        return M.op("AND", nq, 1)

    def feedback(self, M, x, y):
        return  # inert

    def revoke(self, M, x):
        return

    def parent_cost(self):
        k = self.k
        return {"desc": k * 4 * (k.bit_length() + 1), "exec": 1, "upd": None, "ver": 4, "rev": None,
                "note": "finite transducer: table bits; one table step per query; update/revocation uncharged by parent"}

    def flat_table_entries(self):
        return self.k * 4


# ---------------------------------------------------------------- M1 production system
class M1Production(Reference):
    row = "M1"
    declared = {"execution_shape": "STORE_MATCH_CYCLE", "store_discipline": "RULE_SET"}
    fb_channel = "exact_counterexample"
    ladder = (2, 4, 8)

    def init(self, M):
        M.declare_store("rules")
        M.declare("default", "bool", 0)
        M.declare_program(4)
        # seed rules (size-1 pre-existing rules on padded keys so the store has the ladder size)
        for i in range(self.size - 1):
            M.op("S_INSERT", "rules", 16 + i, 0)

    def query(self, M, x):
        hit = M.op("S_MATCH", "rules", lambda k, x=x: k == x)
        return hit[1] if hit else M.read("default")

    def feedback(self, M, x, y):
        if self.query(M, x) != y:
            M.op("S_DELETE", "rules", x)
            M.op("S_INSERT", "rules", x, y)  # chunk: one rule per counterexample

    def revoke(self, M, x):
        M.op("S_DELETE", "rules", x)

    def parent_cost(self):
        n = self.size
        return {"desc": n * 3, "exec": 1 + (n + 1).bit_length(), "upd": 2, "ver": 4, "rev": 1,
                "note": "production system: rule bits; Rete-indexed match 1+log2(n); chunking = one insert (+delete); revocation = one delete (independent rules)"}

    def flat_table_entries(self):
        return (2 ** self.size) * 4


# ---------------------------------------------------------------- M2 program + library
GRAMMAR = [  # candidate programs over Fin ops: each is a list of (op, args-as-slots)
    ("CONST0", lambda M, x: 0), ("CONST1", lambda M, x: 1),
    ("BIT0", lambda M, x: M.op("AND", x, 1)), ("BIT1", lambda M, x: M.op("AND", M.op("SEL", M.op("GT", x, 1), 1, 0), 1)),
    ("NBIT0", lambda M, x: M.op("NOT", M.op("AND", x, 1))), ("NBIT1", lambda M, x: M.op("NOT", M.op("SEL", M.op("GT", x, 1), 1, 0))),
    ("XOR01", lambda M, x: M.op("XOR", M.op("AND", x, 1), M.op("SEL", M.op("GT", x, 1), 1, 0))),
    ("NXOR01", lambda M, x: M.op("NOT", M.op("XOR", M.op("AND", x, 1), M.op("SEL", M.op("GT", x, 1), 1, 0)))),
    ("AND01", lambda M, x: M.op("AND", M.op("AND", x, 1), M.op("SEL", M.op("GT", x, 1), 1, 0))),
    ("OR01", lambda M, x: M.op("OR", M.op("AND", x, 1), M.op("SEL", M.op("GT", x, 1), 1, 0))),
    ("NAND01", lambda M, x: M.op("NOT", M.op("AND", M.op("AND", x, 1), M.op("SEL", M.op("GT", x, 1), 1, 0)))),
    ("NOR01", lambda M, x: M.op("NOT", M.op("OR", M.op("AND", x, 1), M.op("SEL", M.op("GT", x, 1), 1, 0)))),
    ("EQ0", lambda M, x: M.op("EQ", x, 0)), ("EQ1", lambda M, x: M.op("EQ", x, 1)), ("EQ2", lambda M, x: M.op("EQ", x, 2)), ("EQ3", lambda M, x: M.op("EQ", x, 3)),
]
GRAMMAR_INDEX = {name: f for name, f in GRAMMAR}


class M2Program(Reference):
    row = "M2"
    declared = {"execution_shape": "ENUMERATE_TEST_CYCLE", "store_discipline": "TERM_LIBRARY"}
    fb_channel = "exact_counterexample"
    ladder = (2, 4, 8)

    def init(self, M):
        M.declare_store("library")   # (task_key, program_name)
        M.declare_store("examples")  # (x, y) observed
        M.declare("current", "fin", 0)  # index into GRAMMAR of the current program
        M.declare_program(6)
        for i in range(self.size - 1):  # pre-existing library entries for other task keys
            M.op("S_INSERT", "library", 16 + i, i % len(GRAMMAR))
        self.examples = []

    def _run(self, M, idx, x):
        return GRAMMAR[idx][1](M, x)

    def query(self, M, x):
        return self._run(M, M.read("current"), x)

    def feedback(self, M, x, y):
        if self.query(M, x) == y:
            return
        M.op("S_INSERT", "examples", x, y)
        self.examples = [(k, v) for k, v in M.stores["examples"]]
        # enumerate-test: first grammar program consistent with all stored examples
        for idx in range(len(GRAMMAR)):
            ok = True
            for ex, ey in self.examples:
                if self._run(M, idx, ex) != ey:
                    ok = False
                    break
            if ok:
                M.write("current", idx)
                M.op("S_INSERT", "library", 0, idx)
                return
        # no consistent program: keep current (bounded grammar)

    def revoke(self, M, x):
        M.op("S_DELETE", "examples", x)
        self.examples = [(k, v) for k, v in M.stores["examples"]]
        M.op("S_DELETE", "library", 0)
        # re-synthesize from remaining examples
        for idx in range(len(GRAMMAR)):
            if all(self._run(M, idx, ex) == ey for ex, ey in self.examples):
                M.write("current", idx)
                M.op("S_INSERT", "library", 0, idx)
                return

    def parent_cost(self):
        n = self.size
        return {"desc": n * 6, "exec": 3, "upd": 16 * 3, "ver": 4, "rev": 16 * 3,
                "note": "program search + library: AST bits per entry; ~3 ops per program execution; update = enumerate up to 16 grammar programs x execution; revocation = re-synthesis (Levin/OOPS accounting: candidates x execution)"}

    def flat_table_entries(self):
        return len(GRAMMAR) * (2 ** 4) * 4


# ---------------------------------------------------------------- M3 particle (trace-distribution) learner
class M3Particles(Reference):
    row = "M3"
    declared = {"execution_shape": "SAMPLE_SCORE_CYCLE", "store_discipline": "TRACE_DISTRIBUTION"}
    fb_channel = "likelihood_score"
    ladder = (2, 4, 8)

    def init(self, M):
        self.K = self.size
        # particles: hypotheses h in 0..15 (mapping x->y as 4-bit table), weights fx
        for i in range(self.K):
            M.declare(f"h{i}", "fin", (i * 5) % 16)
            M.declare(f"w{i}", "fx", fx(1.0 / self.K))
        M.declare_store("evidence")
        M.declare_program(8)

    def _pred(self, M, h, x):
        return M.op("AND", M.op("SEL", M.op("EQ", x, 3), h >> 3, M.op("SEL", M.op("EQ", x, 2), h >> 2, M.op("SEL", M.op("EQ", x, 1), h >> 1, h))), 1)

    def query(self, M, x):
        s1 = 0
        for i in range(self.K):
            p = self._pred(M, M.read(f"h{i}"), x)
            s1 = M.op("ADD", s1, M.op("SCORE", M.read(f"w{i}"), fx(1.0) if p else 0))
        return M.op("GT", s1, fx(0.5))

    def feedback(self, M, x, y):
        M.op("S_INSERT", "evidence", x, y)
        self._condition(M)

    def _loglike_ok(self, M, h):
        """count of evidence items consistent with hypothesis h (charged compares)."""
        n = 0
        for ex, ey in M.stores["evidence"]:
            n += M.op("EQ", self._pred(M, h, ex), ey)
        return n

    def _condition(self, M):
        # posterior weights from the uniform prior over ALL stored evidence (charged scores), normalized, kept
        ws = []
        for i in range(self.K):
            w = fx(1.0)
            for ex, ey in M.stores["evidence"]:
                like = fx(0.9) if self._pred(M, M.read(f"h{i}"), ex) == ey else fx(0.1)
                w = M.op("SCORE", w, like)
            ws.append(w)
        ws = M.op("NORMALIZE", ws)
        for i in range(self.K):
            M.write(f"w{i}", ws[i])
        # rejuvenation: each particle proposes a one-bit mutation of its hypothesis with prob 1/2 and
        # accepts it iff it is consistent with at least as much evidence (charged compares + samples)
        for i in range(self.K):
            if M.op("SAMPLE", 0.5):
                bit = (M.op("SAMPLE", 0.5) << 1) | M.op("SAMPLE", 0.5)
                h = M.read(f"h{i}")
                h2 = h ^ (1 << bit)
                if self._loglike_ok(M, h2) >= self._loglike_ok(M, h):
                    M.write(f"h{i}", h2)

    def revoke(self, M, x):
        M.op("S_DELETE", "evidence", x)
        self._condition(M)

    def parent_cost(self):
        K = self.K
        return {"desc": K * 12, "exec": 2 * K, "upd": 3 * K, "ver": 4, "rev": 3 * K,
                "note": "particle/trace distribution: K hypotheses x (4+8) bits; query = K scores + adds; conditioning = K likelihood scores + normalize + K samples; revocation = re-condition"}

    def flat_table_entries(self):
        return (16 ** self.K) * 4


# ---------------------------------------------------------------- M4 parametric gradient learner
class M4Net(Reference):
    row = "M4"
    declared = {"execution_shape": "ACYCLIC_FIXED_DEPTH", "store_discipline": "PARAMETER_ARRAY"}
    fb_channel = "scalar_loss"
    ladder = (1, 2, 4)
    LR = fx(0.5)

    def init(self, M):
        self.h = self.size
        init = [0.5, -0.25, 0.75, -0.5, 0.25, 0.5, -0.75, 0.25, 0.5, -0.5, 0.25, 0.75, -0.25, 0.5, 0.25, -0.5]
        k = 0
        for j in range(self.h):
            for i in range(2):
                M.declare(f"w{j}{i}", "fx", fx(init[k % len(init)])); k += 1
            M.declare(f"b{j}", "fx", fx(init[k % len(init)])); k += 1
            M.declare(f"v{j}", "fx", fx(init[k % len(init)])); k += 1
        M.declare("c", "fx", fx(0.0))
        M.declare_store("examples")
        M.declare_program(6 * self.h + 2)
        self.names = [n for n in M.cells if n != "c"] + ["c"]

    def _forward(self, M, x, record=False):
        xb = [fx(1.0) if b else 0 for b in BITS(x)]
        if record:
            M.start_tape()
        acts = []
        for j in range(self.h):
            s = M.read(f"b{j}")
            for i in range(2):
                s = M.op("ADD", s, M.op("MUL", M.read(f"w{j}{i}"), xb[i]))
            acts.append(M.op("THRESH", s))
        out = M.read("c")
        for j in range(self.h):
            out = M.op("ADD", out, M.op("MUL", M.read(f"v{j}"), acts[j]))
        return out, acts, xb

    def query(self, M, x):
        out, _, _ = self._forward(M, x)
        return M.op("GT", out, fx(0.5))

    def _grad_step(self, M, x, y):
        out, acts, xb = self._forward(M, x, record=True)
        err = M.op("SUB", out, fx(1.0) if y else 0)  # d loss/d out (squared loss, factor 2 folded into LR)
        # adjoint pass: charged natively (ADJ) or explicitly; VALUES computed identically in fixed point
        from .core import clamp as _cl
        if "ADJ" in M.basis.native:
            M.op("ADJ", err)
            mul = lambda a, b: _cl((a * b + (1 << 3)) >> 4)  # uncharged value computation (charged by ADJ); same saturation as native MUL
            add = lambda a, b: _cl(a + b)
        else:
            M.op("ADJ", err)
            mul = lambda a, b: M.op("MUL", a, b)
            add = lambda a, b: M.op("ADD", a, b)
        upd = {}
        upd["c"] = _cl(M.read("c") - mul(self.LR, err))
        for j in range(self.h):
            g_v = mul(err, acts[j])
            upd[f"v{j}"] = _cl(M.read(f"v{j}") - mul(self.LR, g_v))
            g_act = mul(err, M.read(f"v{j}")) if acts[j] > 0 else 0
            upd[f"b{j}"] = _cl(M.read(f"b{j}") - mul(self.LR, g_act))
            for i in range(2):
                upd[f"w{j}{i}"] = _cl(M.read(f"w{j}{i}") - mul(self.LR, mul(g_act, xb[i])))
        for name, val in upd.items():
            M.write(name, val)

    def feedback(self, M, x, y):
        M.op("S_INSERT", "examples", x, y)
        self._grad_step(M, x, y)

    def revoke(self, M, x):
        # parent semantics: no dependency cone — retrain from the initial parameters on remaining examples
        M.op("S_DELETE", "examples", x)
        self.init_params = getattr(self, "init_params", None)
        for name in self.names:
            M.write(name, self._initial[name])
        for ex, ey in list(M.stores["examples"]):
            self._grad_step(M, ex, ey)

    def snapshot_initial(self, M):
        self._initial = {n: M.read(n) for n in self.names}

    def parent_cost(self):
        h = self.h
        macs = 2 * h + h
        params = 4 * h + 1
        return {"desc": params * 8, "exec": macs, "upd": 3 * macs, "ver": 4 * macs, "rev": 8 * 3 * macs,
                "note": "parametric gradient learner: 8-bit params; forward = MACs; backprop charged 3x forward (cheap-gradient parent); revocation = retrain on remaining examples (no dependency cone)"}

    def flat_table_entries(self):
        return (256 ** (4 * self.h + 1)) * 4


# ---------------------------------------------------------------- M5 exemplar memory
class M5Memory(Reference):
    row = "M5"
    declared = {"execution_shape": "STORE_MATCH_CYCLE", "store_discipline": "INDEXED_EXEMPLARS"}
    fb_channel = "exact_counterexample"
    ladder = (2, 4, 8)

    def init(self, M):
        M.declare_store("mem")
        M.declare("default", "bool", 0)
        M.declare_program(3)
        for i in range(self.size - 1):
            M.op("S_INSERT", "mem", 16 + i, 0)

    def query(self, M, x):
        v = M.op("S_LOOKUP", "mem", x)
        return M.read("default") if v is None else v

    def feedback(self, M, x, y):
        M.op("S_DELETE", "mem", x)
        M.op("S_INSERT", "mem", x, y)

    def revoke(self, M, x):
        M.op("S_DELETE", "mem", x)

    def parent_cost(self):
        n = self.size
        return {"desc": n * 3, "exec": 1, "upd": 2, "ver": 4, "rev": 1,
                "note": "indexed exemplar memory: entry bits; hash lookup O(1); insert; delete"}

    def flat_table_entries(self):
        return (2 ** self.size) * 4


ROWS = {"M0": M0Transducer, "M1": M1Production, "M2": M2Program, "M3": M3Particles, "M4": M4Net, "M5": M5Memory}
