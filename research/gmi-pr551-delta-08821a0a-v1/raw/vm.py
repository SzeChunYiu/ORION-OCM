"""R1 — exact evaluator for morphology IR genotypes on the charged Machine, with the complete lifecycle resource meter
(GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1 R1; burden vector of GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1 section 10).

The VM executes a typed genotype (gmi_microscope.morph) event by event under a registered ecology protocol: a QUERY pass
(phase exec) evaluates the dataflow graph from INPUT to OUTPUT; a FEEDBACK pass (phase upd) re-evaluates the graph with the
TARGET bound and a local reverse-mode tape, then executes the update nodes (U class), whose side effects replace the state of
the state node they read; verification nodes (V class) are evaluated in phase ver when they gate an update; a REVOKE pass
(phase rev) removes an example from every memory, resets dense parameters to their declared initial values and replays the
evidence buffer. Every arithmetic, store and stochastic operation is charged through Machine.op, so the resource ledger of
the Machine IS the meter: nothing a genotype can do is free, and a genotype carries no data payload (parameters are small
integers), so precomputed knowledge cannot be smuggled in (B0.3 hidden-cost defence by construction; init state is audited).

The VM presents the row interface of the D'/E' microscopes (init / query / feedback / revoke, ladder) so an IR genotype can
be run by smooth.run and compared cell for cell with the hand-written rows (R4 known-parent adapters live in zoo.py).
"""
from __future__ import annotations

import itertools

from .core import Machine, clamp, fx


def prog_bad(p):
    return p is None or isinstance(p, (str, Val))
from . import morph

FX_ONE = fx(1.0)


def _mul(a, b):
    return clamp((a * b + 8) >> 4)


class Val:
    """a fixed-point scalar with an optional local autodiff record (parents: list of (Val, local derivative in fx units))."""
    __slots__ = ("v", "parents", "grad")

    def __init__(self, v, parents=None):
        self.v = int(v); self.parents = parents or []; self.grad = 0


class ProgramGrammar:
    """declared program grammars for PROGRAM/SEARCH/PMUTATE/PROGEXEC. grammar 0: linear coefficient vectors over the 7-value
    coefficient set (S2a's grammar, 2401 programs); grammar 1: XOR-linear masks (32 programs)."""
    COEFFS = [fx(v) for v in (-0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75)]

    def __init__(self, gid, width=4):
        self.gid = gid; self.width = width
        if gid == 0: self.progs = list(itertools.product(self.COEFFS, repeat=width))
        elif gid == 1: self.progs = [(mask, b) for b in (0, 1) for mask in range(2 ** width)]
        else: raise morph.MorphError(f"unknown grammar {gid}")

    def initial(self): return self.progs[0]

    def size(self): return len(self.progs)

    def execute(self, M, prog, xb):
        if self.gid == 0:
            s = 0
            for c, b in zip(prog, xb): s = M.op("ADD", s, M.op("MUL", c, b))
            return s
        mask, bit = prog; acc = bit
        for i, b in enumerate(xb):
            if (mask >> i) & 1: acc = M.op("XOR", acc, 1 if b else 0)
        return FX_ONE if acc else 0

    def n_ops(self): return 2 * self.width + 1


class VM:
    def __init__(self, genotype, M: Machine, seed=0):
        morph.typecheck(genotype)
        self.g = genotype; self.M = M; self.order = morph.toposort(genotype)
        self.nodes = genotype["nodes"]; self.inputs = {}
        for a, b, pt in genotype["edges"]: self.inputs.setdefault(b, {})[pt] = a
        self.state = {}; self.initial_dense = {}; self.grammars = {}; self.rng_seed = seed
        self.abstained = False; self.n_prog_ops = 0
        self.kinds_by_class = morph.mechanism_vector(genotype)
        self.output = [i for i, (k, _) in self.nodes.items() if k == "OUTPUT"]
        if len(self.output) != 1: raise morph.MorphError("exactly one OUTPUT node required")
        self.output = self.output[0]
        self.update_nodes = [i for i in self.order if morph.CLASS_OF[self.nodes[i][0]] == "U"]
        self.clabel = morph.canonical_labels(genotype)  # remint-invariant per-node indices (H5)
        # evaluation order: forward (non-update) nodes first, then update nodes; ties broken by canonical label so the
        # charged trace is a function of the canonical genotype only (remint-invariant response, H5)
        depth = {}
        for i in self.order: depth[i] = 1 + max([depth[a] for a in self.inputs.get(i, {}).values()] or [0])
        fwd = sorted([i for i in self.order if morph.CLASS_OF[self.nodes[i][0]] != "U"], key=lambda i: (depth[i], self.clabel[i]))
        upd = sorted([i for i in self.order if morph.CLASS_OF[self.nodes[i][0]] == "U"], key=lambda i: (depth[i], self.clabel[i]))
        self.order = fwd + upd
        self.evidence_nodes = [i for i in self.order if self.nodes[i][0] == "EVIDENCE"]

    # ------------------------------------------------------------------------------------------------ allocation
    def init(self):
        M = self.M
        # dense initialization: one contiguous declared sequence over the DENSE nodes ordered by (-width, canonical label);
        # the offset of a node depends only on the widths of the wider DENSE nodes, so it is invariant under remint and
        # under implementation-equivalent rewrites that add non-DENSE nodes (B0.1), and reproduces the S4 row's init
        init = [0.5, -0.25, 0.75, -0.5, 0.25, 0.5, -0.75, 0.25, 0.5, -0.5, 0.25, 0.75, -0.25, 0.5, 0.25, -0.5, 0.125, -0.125, 0.375, -0.375, 0.625, -0.625, 0.875, -0.875]
        dense = sorted([i for i in self.order if self.nodes[i][0] == "DENSE"], key=lambda i: (-self.nodes[i][1]["width"], self.clabel[i]))
        offset = {}; acc = 0
        for i in dense: offset[i] = acc; acc += self.nodes[i][1]["width"]
        for i in self.order:
            k, p = self.nodes[i]
            if k == "DENSE":
                names = []
                for j in range(p["width"]):
                    n = f"{i}_w{j}"; M.declare(n, "fx", fx(init[(offset[i] + j) % len(init)])); names.append(n)
                self.state[i] = names; self.initial_dense[i] = [M.read(n) for n in names]
            elif k in ("TABLE", "KVSTORE", "EVIDENCE"):
                M.declare_store(f"{i}_s"); self.state[i] = f"{i}_s"
            elif k == "PROGRAM":
                gr = ProgramGrammar(p["grammar"]); self.grammars[i] = gr; self.state[i] = gr.initial(); self.n_prog_ops += gr.n_ops()
            elif k == "SHADOW":
                M.declare_store(f"{i}_s"); self.state[i] = f"{i}_s"
            elif k == "MATERIALIZE":
                M.declare_store(f"{i}_s"); self.state[i] = f"{i}_s"
            elif k == "VERSIONED":
                M.declare_store(f"{i}_hist"); self.state[i] = f"{i}_hist"; M.declare(f"{i}_ver", "fin", 0)
            elif k == "CONST":
                M.declare(f"{i}_c", "fx", p["value"])
            elif k == "PROGEXEC" or k == "SEARCH" or k == "VERIFY" or k == "PMUTATE":
                pass
            if morph.CLASS_OF[k] in "RTUV": self.n_prog_ops += 2
        M.declare_program(self.n_prog_ops)
        self.audit_initial_state = {"stores_nonempty_at_init": sum(1 for i in self.state.values() if isinstance(i, str) and i in M.stores and M.stores[i]), "dense_cells": sum(len(v) for v in self.state.values() if isinstance(v, list))}

    # ------------------------------------------------------------------------------------------------ evaluation
    def _in(self, i, pt, vals):
        src = self.inputs.get(i, {}).get(pt)
        return None if src is None else vals.get(src)

    def _bits(self, x):
        return [(x >> b) & 1 for b in range(4)]

    def _key(self, xvec, keybits):
        return tuple(1 if getattr(v, "v", 0) > 0 else 0 for v in (xvec or [])[:keybits])

    def _dot(self, w_names, xvec, tape):
        """dot product of a parameter block with a vector; one extra parameter cell beyond the vector length acts as a bias."""
        if not isinstance(w_names, list) or not all(isinstance(t, str) for t in w_names): return Val(0)
        xvec = [v for v in (xvec or []) if isinstance(v, Val)]
        M = self.M; s = Val(0)
        for n, xv in zip(w_names, xvec):
            w = Val(M.read(n)); prod = M.op("MUL", w.v, xv.v)
            pv = Val(prod, [(w, xv.v), (xv, w.v)] if tape else None)
            s = Val(M.op("ADD", s.v, pv.v), [(s, FX_ONE), (pv, FX_ONE)] if tape else None)
            if tape: pv.parents.append(("param", n))
        if len(w_names) == len(xvec) + 1:
            b = Val(M.read(w_names[-1])); s = Val(M.op("ADD", s.v, b.v), [(s, FX_ONE), (b, FX_ONE), ("param", w_names[-1])] if tape else None)
        return s

    def evaluate(self, x, y=None, tape=False):
        """one pass over the graph; returns (values dict, served output Val or None)."""
        M = self.M; vals = {}; xb = [Val(FX_ONE if b else 0) for b in self._bits(x)]
        for i in self.order:
            k, p = self.nodes[i]; cls = morph.CLASS_OF[k]
            if cls == "U" and y is None: continue
            if k == "INPUT": vals[i] = xb[: p["width"]]
            elif k == "TARGET": vals[i] = None if y is None else Val(y)
            elif k == "CONST": vals[i] = Val(M.read(f"{i}_c")) if f"{i}_c" in M.cells else Val(0)
            elif k in ("DENSE",): vals[i] = self.state.get(i, [])
            elif k in ("TABLE", "KVSTORE", "EVIDENCE", "SHADOW", "MATERIALIZE", "VERSIONED"): vals[i] = self.state[i] if k != "VERSIONED" else self._in(i, 0, vals)
            elif k == "PROGRAM": vals[i] = self.state[i]
            elif k == "EDGE": vals[i] = self._in(i, 0, vals)
            elif k == "LINEAR":
                vals[i] = self._dot(self._in(i, 0, vals), self._in(i, 1, vals), tape)
            elif k == "AFFINE":
                w = self._in(i, 0, vals); xv = self._in(i, 1, vals); W = p["width"]; out = []
                if not isinstance(w, list) or not all(isinstance(t, str) for t in w) or not isinstance(xv, list) or not all(isinstance(v, Val) for v in xv): vals[i] = [Val(0)] * W
                else:
                    per = len(xv) + 1
                    for j in range(W):
                        block = w[j * per: (j + 1) * per]
                        if len(block) < per: out.append(Val(0)); continue
                        s = self._dot(block[:-1], xv, tape); b = Val(M.read(block[-1]))
                        s2 = Val(M.op("ADD", s.v, b.v), [(s, FX_ONE), (b, FX_ONE), ("param", block[-1])] if tape else None); out.append(s2)
                    vals[i] = out
            elif k == "NONLIN":
                xv = self._in(i, 0, vals) or []; fn = p["fn"]; out = []
                for v in xv:
                    if fn == 0: r = M.op("THRESH", v.v); out.append(Val(r, [(v, FX_ONE if v.v > 0 else 0)] if tape else None))
                    elif fn == 1: out.append(Val(M.op("NEG", v.v), [(v, -FX_ONE)] if tape else None))
                    else: out.append(v)
                vals[i] = out
            elif k == "NONLIN1":
                v = self._in(i, 0, vals) or Val(0); fn = p["fn"]
                if fn == 0: r = M.op("THRESH", v.v); vals[i] = Val(r, [(v, FX_ONE if v.v > 0 else 0)] if tape else None)
                elif fn == 1: vals[i] = Val(M.op("NEG", v.v), [(v, -FX_ONE)] if tape else None)
                else: vals[i] = v
            elif k == "GATE":
                a = self._in(i, 0, vals) or []; b = self._in(i, 1, vals) or []
                vals[i] = [Val(M.op("MUL", u.v, w.v), [(u, w.v), (w, u.v)] if tape else None) for u, w in zip(a, b)]
            elif k == "SUM":
                a = self._in(i, 0, vals) or Val(0); b = self._in(i, 1, vals) or Val(0)
                vals[i] = Val(M.op("ADD", a.v, b.v), [(a, FX_ONE), (b, FX_ONE)] if tape else None)
            elif k == "LOOKUP":
                st = self._in(i, 0, vals); xv = self._in(i, 1, vals); kb = self._keybits(i, 0)
                r = M.op("S_LOOKUP", st, self._key(xv, kb)) if (isinstance(st, str) and st in M.stores and isinstance(xv, list)) else None; vals[i] = Val(0 if r is None else r)
            elif k == "NEAREST":
                st = self._in(i, 0, vals); xv = self._in(i, 1, vals); vals[i] = self._nearest(st, xv, p["k"]) if (isinstance(st, str) and st in M.stores and isinstance(xv, list)) else Val(0)
            elif k == "SCORESELECT":
                st = self._in(i, 0, vals); xv = self._in(i, 1, vals); vals[i] = self._scoreselect(st, xv) if (isinstance(st, str) and st in M.stores and isinstance(xv, list)) else Val(0)
            elif k == "SELECT":
                a = self._in(i, 0, vals); b = self._in(i, 1, vals); f = self._in(i, 2, vals); vals[i] = (a if M.op("EQ", 1 if f else 0, 1) else b) or Val(0)
            elif k == "PROGEXEC":
                prog = self._in(i, 0, vals); xv = self._in(i, 1, vals); src = self.inputs.get(i, {}).get(0)
                try: vals[i] = Val(self._grammar_of(src).execute(M, prog, [v.v for v in xv])) if (prog is not None and not isinstance(prog, str) and xv and all(isinstance(v, Val) for v in xv)) else Val(0)
                except morph.MorphError: vals[i] = Val(0)
            elif k == "VERIFY":
                prog = self._in(i, 0, vals); ev = self._in(i, 1, vals)
                vals[i] = self._verify_prog(self.inputs.get(i, {}).get(0), prog, ev) if (prog is not None and not isinstance(prog, str) and isinstance(ev, str)) else 1
            elif k == "VERIFYTAB":
                st = self._in(i, 0, vals); ev = self._in(i, 1, vals); vals[i] = self._verify_tab(st, ev, self._keybits(i, 0)) if (isinstance(st, str) and st in M.stores and isinstance(ev, str) and ev in M.stores) else 1
            elif k == "ABSTAIN":
                v = self._in(i, 0, vals); f = self._in(i, 1, vals); vals[i] = v if M.op("EQ", 1 if f else 0, 1) else None
            elif k == "ROLLBACK":
                new = self._in(i, 0, vals); old = self._in(i, 1, vals); f = self._in(i, 2, vals); vals[i] = new if M.op("EQ", 1 if f else 0, 1) else old
            elif k == "OUTPUT": vals[i] = self._in(i, 0, vals)
            elif k == "PLACE" or k == "MORPH_RULE" or k == "NOUPDATE": vals[i] = 1
            elif cls == "U": vals[i] = self._update(i, k, p, vals, y)
            else: vals[i] = None
        return vals, vals.get(self.output)

    def _keybits(self, i, port):
        src = self.inputs.get(i, {}).get(port)
        if src is None: return 4
        k, p = self.nodes[src]
        if k == "TABLE": return p["keybits"]
        if k == "MATERIALIZE": return p["keybits"]
        if k in ("SHADOW", "ROLLBACK", "VERSIONED"):
            return self._keybits(src, 0)
        return 4

    def _grammar_of(self, node, depth=0):
        if node is None or depth > 8 or node not in self.nodes: raise morph.MorphError("no grammar upstream")
        k = self.nodes[node][0]
        if k == "PROGRAM": return self.grammars[node]
        if k in ("SEARCH", "PMUTATE", "ROLLBACK"): return self._grammar_of(self.inputs.get(node, {}).get(0), depth + 1)
        raise morph.MorphError("no grammar upstream")

    def _nearest(self, st, xv, k):
        M = self.M; xb = [1 if getattr(v, "v", 0) > 0 else 0 for v in xv]; ds = []
        for key, val in M.stores[st]:
            d = 0
            for a, b in zip(key, xb): d = M.op("ADD", d, M.op("XOR", a, b))
            ds.append((d, val))
        if not ds: return Val(0)
        ds.sort(key=lambda t: t[0]); top = ds[:k]; acc = 0
        for _, v in top: acc = M.op("ADD", acc, v)
        n = len(top)
        if n & (n - 1) == 0:
            for _ in range(n.bit_length() - 1): acc = M.op("SHR", acc)
        else: acc = M.op("MUL", acc, fx(1.0 / n))
        return Val(acc)

    def _scoreselect(self, st, xv):
        M = self.M; xb = [1 if getattr(v, "v", 0) > 0 else 0 for v in xv]; ds = []; vs = []
        for key, val in M.stores[st]:
            d = 0
            for a, b in zip(key, xb): d = M.op("ADD", d, M.op("XOR", a, b))
            ds.append(M.op("SUB", fx(0.25), fx(d / 16))); vs.append(val)
        if not ds: return Val(0)
        w = M.op("NORMALIZE", ds); acc = 0
        for wi, v in zip(w, vs): acc = M.op("ADD", acc, M.op("SCORE", wi, v))
        return Val(acc)

    def _verify_prog(self, prog_node, prog, ev):
        M = self.M
        if not isinstance(ev, str) or ev not in M.stores: return 1
        try: gr = self._grammar_of(prog_node)
        except morph.MorphError: return 1
        ok = 1
        for xk, y in M.stores[ev]:
            pred = gr.execute(M, prog, [FX_ONE if b else 0 for b in xk]); ok = M.op("AND", ok, M.op("EQ", pred, y))
        return ok

    def _verify_tab(self, st, ev, kb):
        M = self.M; ok = 1
        for xk, y in M.stores[ev]:
            r = M.op("S_LOOKUP", st, tuple(xk[:kb])); ok = M.op("AND", ok, M.op("EQ", 0 if r is None else r, y))
        return ok

    # ------------------------------------------------------------------------------------------------ updates
    def _update(self, i, k, p, vals, y):
        M = self.M
        if k == "GRAD":
            names = self._in(i, 0, vals); pred = self._in(i, 1, vals); tgt = self._in(i, 2, vals)
            if not isinstance(names, list) or not all(isinstance(t, str) for t in names) or not isinstance(pred, Val) or not isinstance(tgt, Val): return None
            err = M.op("SUB", pred.v, tgt.v); M.op("ADJ", err)
            grads = self._backprop(pred, err); lr = p["lr"]; native = "ADJ" in M.basis.native
            mul = _mul if native else (lambda a, b: M.op("MUL", a, b))
            for n in names:
                g = grads.get(n, 0)
                if g: M.write(n, clamp(M.read(n) - mul(lr, g)))
            return None
        src = self.inputs.get(i, {}).get(0)
        if src is None: return None
        if k == "INSERT":
            st = self._in(i, 0, vals); xv = self._in(i, 1, vals); tgt = self._in(i, 2, vals)
            if isinstance(st, str) and st in M.stores and isinstance(xv, list) and isinstance(tgt, Val):
                key = tuple(1 if getattr(v, "v", 0) > 0 else 0 for v in xv); M.stores[st] = [(kk, vv) for kk, vv in M.stores[st] if kk != key]
                M.op("S_INSERT", st, key, tgt.v)
            return None
        if k == "CLOSEDFORM":
            st = self._in(i, 0, vals); xv = self._in(i, 1, vals); tgt = self._in(i, 2, vals); kb = self._keybits(i, 0)
            if isinstance(st, str) and st in M.stores and isinstance(xv, list) and isinstance(tgt, Val):
                key = self._key(xv, kb); M.stores[st] = [(kk, vv) for kk, vv in M.stores[st] if kk != key]; M.op("S_INSERT", st, key, tgt.v)
            return None
        if k == "SEARCH":
            if prog_bad(self._in(i, 0, vals)) or not isinstance(self._in(i, 1, vals), str): return None
            prog = self._in(i, 0, vals); ev = self._in(i, 1, vals)
            try: gr = self._grammar_of(src)
            except morph.MorphError: return None
            best = prog; best_err = None; tried = 0
            for cand in gr.progs[: p["budget"]]:
                tried += 1; e = 0
                for xk, yy in M.stores[ev]:
                    pred = gr.execute(M, cand, [FX_ONE if b else 0 for b in xk]); d = M.op("SUB", pred, yy); e = M.op("ADD", e, d if d >= 0 else M.op("NEG", d))
                if best_err is None or e < best_err: best_err, best = e, cand
            self.state[src] = best; return None
        if k == "PMUTATE":
            if prog_bad(self._in(i, 0, vals)) or not isinstance(self._in(i, 1, vals), str): return None
            prog = self._in(i, 0, vals); ev = self._in(i, 1, vals)
            try: gr = self._grammar_of(src)
            except morph.MorphError: return None
            def err_of(c):
                e = 0
                for xk, yy in M.stores[ev]:
                    pred = gr.execute(M, c, [FX_ONE if b else 0 for b in xk]); d = M.op("SUB", pred, yy); e = M.op("ADD", e, d if d >= 0 else M.op("NEG", d))
                return e
            cur = list(prog) if gr.gid == 0 else prog; cur_err = err_of(tuple(cur) if gr.gid == 0 else cur)
            for _ in range(p["pop"]):
                if gr.gid == 0:
                    cand = list(cur); slot = (M.op("SAMPLE", 0.5) << 1) | M.op("SAMPLE", 0.5)
                    cand[slot] = gr.COEFFS[(gr.COEFFS.index(cand[slot]) + 1 + M.op("SAMPLE", 0.5) * 3) % len(gr.COEFFS)]; cand = tuple(cand)
                else:
                    idx = (gr.progs.index(cur) + 1 + M.op("SAMPLE", 0.5) * 7) % len(gr.progs); cand = gr.progs[idx]
                e = err_of(cand)
                if e <= cur_err: cur, cur_err = (list(cand) if gr.gid == 0 else cand), e
            self.state[src] = tuple(cur) if gr.gid == 0 else cur; return None
        return None

    def _backprop(self, out, err):
        """reverse accumulation over the local tape from the served output; returns {param_name: gradient (fx units)}."""
        order = []; seen = set()
        def visit(v):
            if id(v) in seen or not isinstance(v, Val): return
            seen.add(id(v))
            for par in v.parents:
                if par[0] != "param": visit(par[0])
            order.append(v)
        visit(out); grads = {}
        for v in order: v.grad = 0
        out.grad = err
        for v in reversed(order):
            for par in v.parents:
                if par[0] == "param": grads[par[1]] = clamp(grads.get(par[1], 0) + v.grad)
                else: par[0].grad = clamp(par[0].grad + _mul(v.grad, par[1]))
        return grads

    # ------------------------------------------------------------------------------------------------ row interface
    def query(self, x):
        _, out = self.evaluate(x); self.abstained = not isinstance(out, Val)
        return 0 if self.abstained else out.v

    def feedback(self, x, y):
        M = self.M
        for e in self.evidence_nodes:
            st = self.state[e]; cap = self.nodes[e][1]["cap"]; key = tuple(self._bits(x))
            M.stores[st] = [(kk, vv) for kk, vv in M.stores[st] if kk != key]
            if len(M.stores[st]) >= cap: M.stores[st] = M.stores[st][1:]
            M.op("S_INSERT", st, key, y)
        M.start_tape(); self.evaluate(x, y, tape=True); M.tape = None
        self._materialize_all()

    def _materialize_all(self):
        M = self.M
        for i in self.order:
            k, p = self.nodes[i]
            if k == "MATERIALIZE":
                src = self.inputs.get(i, {}).get(0)
                if src is None: continue
                if src not in self.nodes or self.nodes[src][0] != "PROGRAM" or src not in self.grammars or i not in self.state: continue
                gr = self.grammars[src]; prog = self.state.get(src)
                if prog is None: continue
                st = self.state[i]; M.stores[st] = []
                for key in itertools.product((0, 1), repeat=p["keybits"]):
                    M.op("S_INSERT", st, key, gr.execute(M, prog, [FX_ONE if b else 0 for b in key] + [0] * (4 - p["keybits"])))

    def revoke(self, x):
        M = self.M; key = tuple(self._bits(x))
        for i, st in self.state.items():
            if isinstance(st, str) and st in M.stores and self.nodes[i][0] in ("TABLE", "KVSTORE", "EVIDENCE"):
                before = len(M.stores[st]); M.stores[st] = [(kk, vv) for kk, vv in M.stores[st] if kk[: len(key)] != key[: len(kk)]]
                if len(M.stores[st]) != before: M.op("S_DELETE", st, key)
        for i, names in self.initial_dense.items():
            for n, v in zip(self.state[i], names): M.write(n, v)
        for i in self.order:
            if self.nodes[i][0] == "PROGRAM": self.state[i] = self.grammars[i].initial()
        replay = []
        for e in self.evidence_nodes: replay = list(M.stores[self.state[e]])
        for kk, vv in replay:
            xx = sum(b << j for j, b in enumerate(kk)); M.start_tape(); self.evaluate(xx, vv, tape=True); M.tape = None
        self._materialize_all()


class VMRow:
    """adapter presenting a genotype as a D'/E' row (init/query/feedback/revoke) for smooth.run."""
    ladder = (1,)

    def __init__(self, genotype, size=1, seed=0):
        self.g = genotype; self.row = "IR"; self.seed = seed

    def init(self, M):
        self.vm = VM(self.g, M, self.seed); self.vm.init()

    def query(self, M, x): return self.vm.query(x)

    def feedback(self, M, x, y): self.vm.feedback(x, y)

    def revoke(self, M, x): self.vm.revoke(x)


def lifecycle_vector(M: Machine, n_events, n_queries, search_cost=0, failed_draws=0, imported_capital_bits=0, external_calls=0, human_effort=0, wrong_served=0, abstentions=0, lam=0):
    """the biosphere burden vector from the Machine ledger plus the search-side terms the ledger cannot see."""
    c = M.L.c; desc_state = sum(M.basis.desc_bits(M.cell_types[n]) for n in M.cells) + sum(M.basis.desc_store_header + len(st) * M.basis.desc_store_entry for st in M.stores.values())
    return {"B_train": c["upd"], "B_data": n_events, "B_search": search_cost, "B_failed_candidates": failed_draws, "B_serve": c["exec"], "B_lat": (c["exec"] / n_queries if n_queries else 0),
            "B_mem": desc_state, "B_desc": c["desc"], "B_comm": 0, "B_update": c["rev"], "B_verify": c["ver"], "B_human": human_effort, "B_energy": None, "B_external_calls": external_calls,
            "B_capital": imported_capital_bits, "B_compile": 0, "B_risk": lam * wrong_served + (lam / 16) * abstentions, "native_ops": M.L.native_ops, "emulated_ops": M.L.emulated_ops}
