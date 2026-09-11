"""RV-377-030: the reinforcement / temporal-credit ecology E_credit and its rows (the RL family's D1/D3 rows).

Ecology (declared): 4-bit inputs; hidden Boolean rule g(x) = (x0 AND x1) OR (x2 AND x3); seen inputs TRAIN_MIXED
(balanced: 5 ones / 3 zeros), unseen the other eight (2 ones / 6 zeros, so the default-0 policy scores 0.75 < theta).
An EPISODE is four consecutive seen inputs (sliding window over TRAIN, episode e uses TRAIN[(e+i) % 8]); the row emits an
action a_t in {0,1} per input; the only feedback is the scalar episode return R = number of correct actions (0..4),
delivered once at the end of the episode (credit ambiguity: which of the four actions earned the reward is not told).
Capability = fraction of UNSEEN inputs on which the greedy action equals g(x); theta = 0.85 (7 of 8).
Cost model, phases and the frontier over (H, r) are the same as smooth.py; 'revoke' withdraws one stored episode.

Rows (each a program over the same charged universe):
  R1  consistency search (RL as inference): store episodes; enumerate a small Boolean grammar; keep the first program whose
      predicted per-episode returns match every stored return; act = program(x).
  R2  Monte-Carlo Q-table (tabular RL, memory form): credit R/4 to each (x_t, a_t); act = argmax_a Q[x][a], deterministic
      alternation when tied (exploration); unseen inputs fall back to action 0.
  R3  REINFORCE policy net (dense form): a one-hidden-layer ReLU net gives a score s(x); action = 1 if s + noise > 0 with
      SAMPLE-based exploration; update w <- w + lr * (R - 2) * (a - p) * x over the episode (eligibility), fixed point.
  R4  kNN credited-action memory: act = majority credited action of the Hamming-nearest stored (x, a, R/4) entries.
"""
from __future__ import annotations

import itertools
import json
import os

from . import bases
from .core import COORDS, FX_ONE, Machine, clamp, fx, sha256_of
from .smooth import THETA, analytic_rstar, cost, per_event  # noqa: F401  (same cost model)
H_GRID = [1, 2, 4, 8, 16, 32, 64, 128]; R_GRID = [0, 1, 2, 4, 8, 16, 32]

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
ALL_X = list(range(16))
TRAIN = [0, 3, 5, 6, 7, 11, 13, 14]
UNSEEN = [x for x in ALL_X if x not in TRAIN]
EP_LEN = 4
bits = lambda x: [(x >> i) & 1 for i in range(4)]


def g_rule(x):
    b = bits(x); return int((b[0] and b[1]) or (b[2] and b[3]))


# Boolean grammar: constants, literals, single 2-monomials, disjunctions of two 2-monomials (contains g)
PAIRS = list(itertools.combinations(range(4), 2))
GRAMMAR_B = [("const", 0), ("const", 1)] + [("lit", i) for i in range(4)] + [("mono", p) for p in PAIRS] + [("or2", (p, q)) for p, q in itertools.combinations(PAIRS, 2)]


def prog_eval(M, prog, x):
    kind, arg = prog; b = bits(x)
    if kind == "const": M.op("CONST", arg); return arg
    if kind == "lit": M.op("AND", b[arg], 1); return b[arg]
    if kind == "mono": return M.op("AND", b[arg[0]], b[arg[1]])
    (i, j), (k, l) = arg
    return M.op("OR", M.op("AND", b[i], b[j]), M.op("AND", b[k], b[l]))


def episodes(n_episodes):
    return [[TRAIN[(e + i) % len(TRAIN)] for i in range(EP_LEN)] for e in range(n_episodes)]


class R1Search:
    row = "R1"; ladder = (2, 4)

    def __init__(self, n): self.n = n

    def init(self, M):
        M.declare_store("episodes"); M.declare("current", "fin", 0); M.declare_program(8); self.idx = 0
        for i in range(self.n - 1): M.op("S_INSERT", "episodes", 100 + i, 0)

    def act(self, M, x):
        return prog_eval(M, GRAMMAR_B[self.idx], x)

    def _synth(self, M):
        eps = [(k, v) for k, v in M.stores["episodes"] if k < 100]
        for k, prog in enumerate(GRAMMAR_B):
            ok = True
            for key, (xs, acts, R) in eps:
                pred = 0
                for x, a in zip(xs, acts): pred = M.op("ADD", pred, M.op("EQ", prog_eval(M, prog, x), a))
                if not M.op("EQ", pred, R): ok = False; break
            if ok: self.idx = k; M.write("current", k % 4); return

    def feedback(self, M, key, xs, acts, R):
        pred = 0
        for x, a in zip(xs, acts): pred = M.op("ADD", pred, M.op("EQ", self.act(M, x), a))
        M.op("S_INSERT", "episodes", key, (xs, acts, R))
        if not M.op("EQ", pred, R): self._synth(M)

    def revoke(self, M, key):
        M.op("S_DELETE", "episodes", key); self._synth(M)


class R2QTable:
    row = "R2"; ladder = (2, 4)

    def __init__(self, n): self.n = n

    def init(self, M):
        M.declare_store("q"); M.declare_store("episodes"); M.declare("tick", "fin", 0); M.declare_program(6)
        for i in range(self.n - 1): M.op("S_INSERT", "q", 100 + i, 0)

    def _q(self, M, x, a):
        v = M.op("S_LOOKUP", "q", 2 * x + a); return (0, 0) if v is None else v  # (sum of credited returns, count)

    def act(self, M, x):
        q0, q1 = self._q(M, x, 0), self._q(M, x, 1)
        v0 = M.op("SCORE", q0[0], fx(1.0)) if q0[1] else 0; v1 = M.op("SCORE", q1[0], fx(1.0)) if q1[1] else 0
        if M.op("GT", v1, v0): return 1
        if M.op("GT", v0, v1): return 0
        t = M.read("tick"); M.write("tick", (t + 1) % 2); return t  # deterministic alternation when tied

    def feedback(self, M, key, xs, acts, R):
        M.op("S_INSERT", "episodes", key, (xs, acts, R))
        share = M.op("SHR", M.op("SHR", fx(R)))  # R/4 in fx
        for x, a in zip(xs, acts):
            s, c = self._q(M, x, a)
            M.op("S_DELETE", "q", 2 * x + a); M.op("S_INSERT", "q", 2 * x + a, (M.op("ADD", s, share), M.op("INC", c)))

    def revoke(self, M, key):
        for k, v in list(M.stores["episodes"]):
            if k == key:
                xs, acts, R = v; share = M.op("SHR", M.op("SHR", fx(R)))
                for x, a in zip(xs, acts):
                    s, c = self._q(M, x, a)
                    M.op("S_DELETE", "q", 2 * x + a); M.op("S_INSERT", "q", 2 * x + a, (M.op("SUB", s, share), c - 1))
        M.op("S_DELETE", "episodes", key)


class R3Policy:
    row = "R3"; ladder = (2, 4); LR = fx(0.5)

    def __init__(self, h): self.h = h

    def init(self, M):
        init = [0.5, -0.25, 0.75, -0.5, 0.25, 0.5, -0.75, 0.25, 0.5, -0.5, 0.25, 0.75, -0.25, 0.5, 0.25, -0.5, 0.125, -0.125, 0.375, -0.375, 0.625, -0.625, 0.875, -0.875]
        k = 0
        for j in range(self.h):
            for i in range(4): M.declare(f"w{j}{i}", "fx", fx(init[k % len(init)])); k += 1
            M.declare(f"b{j}", "fx", fx(init[k % len(init)])); k += 1
            M.declare(f"v{j}", "fx", fx(init[k % len(init)])); k += 1
        M.declare("c", "fx", 0); M.declare_store("episodes"); M.declare_program(10 * self.h + 3)
        self.names = list(M.cells); self._initial = {n: M.read(n) for n in self.names}

    def _score(self, M, x):
        xb = [fx(1.0) if b else 0 for b in bits(x)]; acts = []
        for j in range(self.h):
            s = M.read(f"b{j}")
            for i in range(4): s = M.op("ADD", s, M.op("MUL", M.read(f"w{j}{i}"), xb[i]))
            acts.append(M.op("THRESH", s))
        out = M.read("c")
        for j in range(self.h): out = M.op("ADD", out, M.op("MUL", M.read(f"v{j}"), acts[j]))
        return out, acts, xb

    def act(self, M, x):
        out, _, _ = self._score(M, x); return 1 if M.op("GT", out, 0) else 0

    def explore(self, M, x):
        out, _, _ = self._score(M, x)
        flip = M.op("SAMPLE", 0.25)  # exploration: 25% of actions are inverted
        a = 1 if M.op("GT", out, 0) else 0
        return (1 - a) if flip else a

    def _update(self, M, xs, acts, R):
        adv = clamp(fx(R) - fx(2.0))  # baseline 2 of 4
        if adv == 0: M.op("AND", 0, 0); return
        for x, a in zip(xs, acts):
            out, hid, xb = self._score(M, x)
            p = fx(1.0) if out > 0 else 0
            grad_out = M.op("MUL", adv, clamp(fx(a) - p))  # (R - b) * (a - greedy)
            if grad_out == 0: continue
            M.write("c", M.op("ADD", M.read("c"), M.op("MUL", self.LR, grad_out)))
            for j in range(self.h):
                M.write(f"v{j}", M.op("ADD", M.read(f"v{j}"), M.op("MUL", self.LR, M.op("MUL", grad_out, hid[j]))))
                if hid[j] > 0:
                    gh = M.op("MUL", grad_out, M.read(f"v{j}"))
                    M.write(f"b{j}", M.op("ADD", M.read(f"b{j}"), M.op("MUL", self.LR, gh)))
                    for i in range(4): M.write(f"w{j}{i}", M.op("ADD", M.read(f"w{j}{i}"), M.op("MUL", self.LR, M.op("MUL", gh, xb[i]))))

    def feedback(self, M, key, xs, acts, R):
        M.op("S_INSERT", "episodes", key, (xs, acts, R)); self._update(M, xs, acts, R)

    def revoke(self, M, key):
        M.op("S_DELETE", "episodes", key)
        for n in self.names: M.write(n, self._initial[n])
        for k, (xs, acts, R) in list(M.stores["episodes"]): self._update(M, xs, acts, R)


class R4KNN:
    row = "R4"; ladder = (2, 4)

    def __init__(self, n): self.n = n

    def init(self, M):
        M.declare_store("mem"); M.declare_store("episodes"); M.declare_program(14)
        for i in range(self.n - 1): M.op("S_INSERT", "mem", 100 + i, 0)

    def act(self, M, x):
        best_d, vote = 5, 0
        for k, v in M.op("S_SCAN", "mem"):
            if k >= 100: M.op("GT", k, 99); continue
            xk, a, share = v; d = 0
            for i in range(4): d = M.op("ADD", d, M.op("XOR", (xk >> i) & 1, (x >> i) & 1))
            if M.op("GT", best_d, d): best_d, vote = d, 0
            if M.op("EQ", d, best_d): vote = M.op("ADD", vote, M.op("SCORE", share if a else clamp(-share), fx(1.0)))
        return 1 if M.op("GT", vote, 0) else 0

    def feedback(self, M, key, xs, acts, R):
        M.op("S_INSERT", "episodes", key, (xs, acts, R)); share = M.op("SHR", M.op("SHR", fx(R)))
        for i, (x, a) in enumerate(zip(xs, acts)): M.op("S_INSERT", "mem", 1000 * key + i, (x, a, clamp(share - fx(0.5))))  # centred credit

    def revoke(self, M, key):
        M.op("S_DELETE", "episodes", key)
        for i in range(EP_LEN): M.op("S_DELETE", "mem", 1000 * key + i)


ROWS_RL = {"R1": R1Search, "R2": R2QTable, "R3": R3Policy, "R4": R4KNN}
DENSE_RL = {"R3"}


def run(row, basis, size, seed=0, n_episodes=8, rows=None):
    ref = (rows or ROWS_RL)[row](size)
    M = Machine(basis, seed=seed); M.phase("exec"); ref.init(M)
    eps = episodes(n_episodes); revoke_at = n_episodes // 2 + 1
    D = []; max_writes = 0
    for e, xs in enumerate(eps, start=1):
        M.phase("exec")
        acts = [ref.explore(M, x) if hasattr(ref, "explore") else ref.act(M, x) for x in xs]
        D.append({xx: ref.act(M, xx) for xx in ALL_X})
        R = sum(int(a == g_rule(x)) for x, a in zip(xs, acts))
        M.phase("upd"); ref.feedback(M, e, xs, acts, R); max_writes = max(max_writes, len(M.L.writes_in_event)); M.end_event()
        M.phase("ver")
        for xx in ALL_X: M.op("EQ", ref.act(M, xx), g_rule(xx))
        if e == revoke_at:
            M.phase("rev"); ref.revoke(M, 2); M.end_event()
    M.phase("exec"); final = {xx: ref.act(M, xx) for xx in ALL_X}; D.append(final)
    cap = sum(int(final[xx] == g_rule(xx)) for xx in UNSEEN) / len(UNSEEN)
    return {"row": row, "basis": basis.name, "size": size, "D": D, "R": dict(M.L.c), "capability": round(cap, 4), "max_writes": max_writes, "n_events": n_episodes}


def main(tag="V11_CREDIT_E8", n_episodes=8, seed=0):
    rows = ROWS_RL; cols = list(bases.ALL); cells = {}
    for row, cls in rows.items():
        for col in cols:
            for size in cls.ladder:
                cells[(row, col, size)] = run(row, bases.ALL[col], size, seed, n_episodes, rows)
    c2 = {f"{row}@{size}": all(cells[(row, col, size)]["D"] == cells[(row, cols[0], size)]["D"] for col in cols) for row, cls in rows.items() for size in cls.ladder}
    caps = {f"{row}|{col}|{size}": cells[(row, col, size)]["capability"] for (row, col, size) in cells}
    frontier = {}; ph = {}
    for col in cols:
        for Hh in H_GRID:
            for r in R_GRID:
                adm = []
                for row, cls in rows.items():
                    c = cells[(row, col, cls.ladder[-1])]
                    if c["capability"] >= THETA: adm.append((row, cost(per_event(c["R"], n_episodes), Hh, r)))
                if not adm: frontier[f"{col}|H={Hh}|r={r}"] = []; continue
                cmin = min(v for _, v in adm); frontier[f"{col}|H={Hh}|r={r}"] = sorted(row for row, v in adm if v <= cmin + 1e-9)
        ph[col] = {"winners_by_r_H16": {str(r): frontier[f"{col}|H=16|r={r}"] for r in R_GRID}}
    receipt = {"schema": "StageDECreditV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 377, "revival_record": "RV-377-030", "run_tag": tag,
               "ecology": {"kind": "credit", "rule": "(x0 AND x1) OR (x2 AND x3)", "inputs": 16, "train": TRAIN, "episodes": n_episodes, "episode_length": EP_LEN, "reward": "episode return = number of correct actions (0..4), delivered at episode end", "revoke_at": n_episodes // 2 + 1, "theta": THETA, "rows": list(rows), "capability_criterion": "unseen"},
               "grammar_size": len(GRAMMAR_B), "C2": c2, "capability_by_cell": caps, "R_by_cell": {f"{row}|{col}|{size}": cells[(row, col, size)]["R"] for (row, col, size) in cells},
               "writes_by_cell": {f"{row}|{col}|{size}": cells[(row, col, size)]["max_writes"] for (row, col, size) in cells}, "frontier_H_r": frontier, "PH_REV": ph,
               "claim_ceiling": "P2 exact at a 16-input, 8-bit scope; one rule; frozen cost model; the R1 grammar contains the rule by construction (declared)"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DE_CREDIT_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("C2 all:", all(c2.values()))
    for row, cls in rows.items(): print(row, {c.split('_')[0]: caps[f"{row}|{c}|{cls.ladder[-1]}"] for c in cols})
    for col, p in ph.items(): print(col.split('_')[0], p["winners_by_r_H16"])
    return receipt


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(tag=f"V11_CREDIT_E{n}", n_episodes=n)
