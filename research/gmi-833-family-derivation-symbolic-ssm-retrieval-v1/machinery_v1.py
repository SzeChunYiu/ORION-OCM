"""Machinery v1 — neutral substrate for the derivation tranches (GMI #833).

Frozen basis and machine models per BASIS_GRID_V1.json / PRIOR_DISCLOSURE_V1.md.
This module is BLIND: it reads and carries no family, benchmark, or fingerprint
information. Expressions and machines are JSON-serializable lists.

Expression ADT:  ["atom", name] | ["const", v] | ["un", uname, e] | ["add", a, b]
Machine models:
  M_STREAM: {"model":"M_STREAM","cells":k,"update":[e]*k,"readout":e,"rho":r}
            state s in D^k all-zero initially; per stream position:
            s_i' = e_i(s, x); y = e_readout(s, x).  Guard at every node.
  M_ITER:   {"model":"M_ITER","input_cells":n,"update":[e]*n_work,
            "output_cell":j,"steps":T}
            cells = n input cells (loaded from the task layout, indices 0..n-1)
            plus n_work work cells (indices n..n+n_work-1, zero-initialized);
            T synchronous steps; output = cell output_cell at the final step.

cost(machine) = rho * (chosen cells) + total operator nodes.
"""
from __future__ import annotations

GUARD = 3
DOMAIN = tuple(range(-GUARD, GUARD + 1))
CONSTS = (-1, 0, 1)
UNARIES = {"NEG": lambda v: -v}
for _c in DOMAIN:
    UNARIES["GE%+d" % _c] = (lambda c: (lambda v: 1 if v >= c else 0))(_c)


def unary_names():
    return sorted(UNARIES)


def expr_ops(e):
    """Operator-node count (unary + add); atoms/consts are free."""
    if e[0] in ("atom", "const"):
        return 0
    if e[0] == "un":
        return 1 + expr_ops(e[2])
    if e[0] == "add":
        return 1 + expr_ops(e[1]) + expr_ops(e[2])
    raise ValueError(e)


def expr_atoms(e, acc=None):
    if acc is None:
        acc = set()
    if e[0] == "atom":
        acc.add(e[1])
    elif e[0] == "un":
        expr_atoms(e[2], acc)
    elif e[0] == "add":
        expr_atoms(e[1], acc)
        expr_atoms(e[2], acc)
    return acc


def expr_gate_sites(e):
    """Number of order-test (GE*) nodes."""
    if e[0] in ("atom", "const"):
        return 0
    if e[0] == "un":
        return (1 if e[1].startswith("GE") else 0) + expr_gate_sites(e[2])
    return expr_gate_sites(e[1]) + expr_gate_sites(e[2])


def expr_eval(e, env):
    """Exact evaluation with guard check; returns None on guard violation."""
    t = e[0]
    if t == "atom":
        return env[e[1]]
    if t == "const":
        return e[1]
    if t == "un":
        v = expr_eval(e[2], env)
        if v is None:
            return None
        return UNARIES[e[1]](v)
    a = expr_eval(e[1], env)
    if a is None:
        return None
    b = expr_eval(e[2], env)
    if b is None:
        return None
    s = a + b
    if s < -GUARD or s > GUARD:
        return None
    return s


def machine_cost(m):
    if m["model"] == "M_STREAM":
        return m["rho"] * m["cells"] + sum(expr_ops(e) for e in m["update"]) \
            + expr_ops(m["readout"])
    if m["model"] == "M_ITER":
        return m["rho"] * len(m["update"]) \
            + sum(expr_ops(e) for e in m["update"])
    raise ValueError(m)


def machine_gate_sites(m):
    exprs = list(m["update"]) + ([m["readout"]] if m["model"] == "M_STREAM" else [])
    return sum(expr_gate_sites(e) for e in exprs)


# ---------------------------------------------------------------------------
# pure-python simulators (exact; used for verification and adjudication)
# ---------------------------------------------------------------------------

def sim_stream(m, stream):
    """Run M_STREAM on a token stream from the all-zero state.
    Returns (outputs, trajectories, legal): outputs[i] = y at position i
    (None on guard violation), trajectories[i] = tuple of cell values."""
    k = m["cells"]
    s = [0] * k
    outs = []
    trajs = [tuple(s)]
    legal = True
    for x in stream:
        env = {"s%d" % i: s[i] for i in range(k)}
        env["x"] = x
        ns = []
        for i in range(k):
            v = expr_eval(m["update"][i], env)
            if v is None:
                legal = False
                v = 0
            ns.append(v)
        y = expr_eval(m["readout"], env)
        if y is None:
            legal = False
            y = 0
        s = ns
        outs.append(y)
        trajs.append(tuple(s))
    return outs, trajs, legal


def sim_iter(m, init_cells):
    """Run M_ITER from the given input-cell values (work cells zero).
    Returns (final_cells, trajectories, legal)."""
    n = m["input_cells"]
    cells = list(init_cells) + [0] * len(m["update"])
    trajs = [tuple(cells)]
    legal = True
    for _ in range(m["steps"]):
        env = {"s%d" % i: cells[i] for i in range(len(cells))}
        nc = list(cells)
        for wi, e in enumerate(m["update"]):
            v = expr_eval(e, env)
            if v is None:
                legal = False
                v = 0
            nc[n + wi] = v
        cells = nc
        trajs.append(tuple(cells))
    return cells, trajs, legal


# ---------------------------------------------------------------------------
# numpy batch simulators (search-side; numpy is a search-only dependency)
# ---------------------------------------------------------------------------

def _compile_expr(e, atom_index, consts_ok=True):
    """Compile an expression to a stack program over vectorized arrays.
    Returns list of ops: ('const', v) | ('atom', idx) | ('un', name) | ('add',).
    Guard violations set a global violation flag (caller accumulates)."""
    prog = []
    def go(x):
        t = x[0]
        if t == "atom":
            prog.append(("atom", atom_index[x[1]]))
        elif t == "const":
            prog.append(("const", x[1]))
        elif t == "un":
            go(x[2])
            prog.append(("un", x[1]))
        else:
            go(x[1])
            go(x[2])
            prog.append(("add",))
    go(e)
    return prog


def run_prog(prog, arrays, np):
    """Execute a compiled program; arrays = list of input vectors (numpy int64).
    Returns (values, illegal_mask)."""
    stack = []
    illegal = arrays[0] != arrays[0]  # all-False bool mask
    for op in prog:
        if op[0] == "atom":
            stack.append(arrays[op[1]].copy())
        elif op[0] == "const":
            stack.append(np.full(arrays[0].shape, op[1], dtype=np.int64))
        elif op[0] == "un":
            a = stack.pop()
            name = op[1]
            if name == "NEG":
                stack.append(-a)
            else:
                c = int(name[2:])
                stack.append((a >= c).astype(np.int64))
        else:
            b = stack.pop()
            a = stack.pop()
            s = a + b
            bad = (s < -GUARD) | (s > GUARD)
            illegal = illegal | bad
            stack.append(np.where(bad, 0, s))
    return stack[0], illegal


def batch_sim_stream(m, streams, np):
    """streams: (N, L) int array. Returns (outs (N,L), legal_mask (N,),
    traj (k, N, L+1))."""
    N, L = streams.shape
    k = m["cells"]
    ai = {}
    for i in range(k):
        ai["s%d" % i] = i
    ai["x"] = k
    uprog = [_compile_expr(e, ai) for e in m["update"]]
    yprog = _compile_expr(m["readout"], ai)
    s = np.zeros((k, N), dtype=np.int64)
    legal = np.ones(N, dtype=bool)
    outs = np.zeros((N, L), dtype=np.int64)
    traj = np.zeros((k, N, L + 1), dtype=np.int64)
    traj[:, :, 0] = s
    for t in range(L):
        arrays = [s[i] for i in range(k)] + [streams[:, t]]
        ns = []
        for i in range(k):
            v, ill = run_prog(uprog[i], arrays, np)
            legal &= ~ill
            ns.append(v)
        yv, ill = run_prog(yprog, arrays, np)
        legal &= ~ill
        s = np.vstack(ns)
        traj[:, :, t + 1] = s
        outs[:, t] = yv
    return outs, legal, traj


def batch_sim_iter(m, inits, np):
    """inits: (N, input_cells). Returns (final (N, cells), legal (N,),
    traj (steps+1, N, cells))."""
    N = inits.shape[0]
    n = m["input_cells"]
    cells = [inits[:, i].copy() for i in range(n)] \
        + [np.zeros(N, dtype=np.int64) for _ in m["update"]]
    ai = {"s%d" % i: i for i in range(len(cells))}
    progs = [_compile_expr(e, ai) for e in m["update"]]
    legal = np.ones(N, dtype=bool)
    traj = np.zeros((m["steps"] + 1, N, len(cells)), dtype=np.int64)
    traj[0] = np.vstack(cells).T
    for t in range(m["steps"]):
        for wi, prog in enumerate(progs):
            v, ill = run_prog(prog, cells, np)
            legal &= ~ill
            cells[n + wi] = v
        traj[t + 1] = np.vstack(cells).T
    return np.vstack(cells).T, legal, traj


# frozen integer hash (grammar-growth NULL-1 recipe)
def frozen_hash(s):
    return ((s + 1) * 2654435761) % (2 ** 32)
