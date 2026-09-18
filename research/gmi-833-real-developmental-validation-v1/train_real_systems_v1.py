"""Section I outcome producer for gmi-833-real-developmental-validation-v1.

Created AFTER freeze commit 808054d94dcdc188b7ef3e72cd55c18265ef22af.
Runs on the execution host (laptop-billy, torch CPU). Trains the nine
registered real systems on each sha256-bound real ecology and writes
REAL_RUNS/ecology_<id>.json with MEASURED integer resource counts and the
exact integer held-out error count. Never writes RESULT_V1.json.

Family names never enter scoring: the emitted `measured` map is keyed by
opaque ids c1..c9, and `opaque_to_signature` is consumed by the scorer only
after the argmin is fixed.

Usage: python3 -I -B train_real_systems_v1.py <out REAL_RUNS dir>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import real_dev_validation_v1 as RV  # noqa: E402

LR = 0.01
EPOCHS = 3
CHUNK = 16
POP_MUT_SCALE = 0.25


class Counters(object):
    def __init__(self):
        self.evals = 0
        self.carry = 0
        self.store = 0
        self.build = 0
        self.branch = 0
        self.meta = 0
        self.mut = 0

    def vec(self, loss):
        return [self.evals, self.carry, self.store, self.build,
                self.branch, self.meta, self.mut, loss]


class Unit(nn.Module):
    """one real trainable single-feature logistic unit"""

    def __init__(self):
        super(Unit, self).__init__()
        self.lin = nn.Linear(1, 1)

    def forward(self, x):
        return torch.sigmoid(self.lin(x)).squeeze(-1)


class Body(nn.Module):
    """one real trainable MLP over the 9 delay features"""

    def __init__(self, width=8):
        super(Body, self).__init__()
        self.h = nn.Linear(9, width)
        self.o = nn.Linear(width, 1)

    def forward(self, x):
        return torch.sigmoid(self.o(torch.relu(self.h(x)))).squeeze(-1)


def feats(env, zs):
    return torch.tensor([[float(env["H"][i][z]) for i in range(RV.M)] for z in zs])


def labels(env, zs):
    return torch.tensor([float(env["target"][z]) for z in zs])


def errcount(pred_bits, env, zs):
    return int(sum(1 for p, z in zip(pred_bits, zs) if p != env["target"][z]))


def train_units(env, seed, cnt):
    """SIG-W / BASE-0 shared substrate: M real single-feature units."""
    torch.manual_seed(seed)
    zs = list(env["train"])
    X, Y = feats(env, zs), labels(env, zs)
    units = [Unit() for _ in range(RV.M)]
    opt = torch.optim.Adam([p for u in units for p in u.parameters()], lr=LR)
    lossf = nn.BCELoss()
    for _ep in range(EPOCHS):
        for s in range(0, len(zs), CHUNK):
            xb, yb = X[s:s + CHUNK], Y[s:s + CHUNK]
            opt.zero_grad()
            tot = 0.0
            for i, u in enumerate(units):
                tot = tot + lossf(u(xb[:, i:i + 1]), yb)
                cnt.evals += xb.shape[0]
            tot.backward()
            opt.step()
            cnt.carry += RV.M * xb.shape[0]
    return units


def unit_bits(units, env, zs):
    X = feats(env, zs)
    with torch.no_grad():
        return [[int(u(X[:, i:i + 1])[j].item() >= 0.5) for j in range(len(zs))]
                for i, u in enumerate(units)]


def run_ecology(spec, outdir):
    sid = spec[0]
    eco = RV.derive(*spec)
    used = eco["source_used"]
    bits = RV.bits_from_file(used, RV.K * (RV.T + RV.NQ) + 16 * RV.K + 64)
    env = RV.build_episode(bits, 0, spec[3], spec[4])
    episodes = [RV.build_episode(bits, ep * (RV.T + RV.NQ), spec[3], spec[4])
                for ep in range(RV.K)]
    q = list(env["Qset"])
    inv = eco["invariants"]
    seeds = (RV.M * 101 + 7, RV.M * 101 + 1007)
    per_seed = {}
    t0 = time.time()
    for seed in seeds:
        m = {}
        # --- SIG-W and BASE-0 (real gradient-trained units) ---------------
        cw, cb = Counters(), Counters()
        units = train_units(env, seed, cw)
        cb.evals, cb.carry = cw.evals // RV.M, cw.carry // RV.M
        tb = unit_bits(units, env, list(env["train"]))
        acc = [sum(1 for j, z in enumerate(env["train"])
                   if tb[i][j] == env["target"][z]) for i in range(RV.M)]
        wts = torch.softmax(torch.tensor([float(a) for a in acc]), 0).tolist()
        qb = unit_bits(units, env, q)
        cw.evals += RV.M * len(q)
        cb.evals += len(q)
        wpred = [1 if sum(wts[i] for i in range(RV.M) if qb[i][j] == 1) > 0.5 else 0
                 for j in range(len(q))]
        best_i = max(range(RV.M), key=lambda i: (acc[i], -i))
        bpred = [qb[best_i][j] for j in range(len(q))]
        m["SIG-W"] = cw.vec(errcount(wpred, env, q))
        m["BASE-0"] = cb.vec(errcount(bpred, env, q))
        # --- NULL-0 (registered incumbent, untrained) ---------------------
        cn = Counters()
        cn.evals = len(q)
        inc = RV.STARTS[0]
        m["NULL-0"] = cn.vec(errcount([env["H"][inc][z] for z in q], env, q))
        # --- SIG-X (real exemplar learner fitted to the real stream) ------
        cx = Counters()
        retr, mu = RV.retrieval(env, spec[5])
        tr = env["train"]
        cx.store = mu * len(tr)
        cx.evals = len(tr) + len(q)
        xpred = [env["target"][tr[retr[z]]] for z in q]
        m["SIG-X"] = cx.vec(errcount(xpred, env, q))
        # --- SIG-R / SIG-L (real exhaustive rule induction) ---------------
        rs = RV.production_space(spec[6])
        Dmin, sub, _cov, _nc = RV.consistent_cover(env, rs)
        for rid, ln in (("SIG-R", Dmin), ("SIG-L", inv["Dmin_L"])):
            if ln is None:
                m[rid] = None
                continue
            c = Counters()
            c.evals = len(rs) * len(tr) + len(q)
            c.build = ln
            rp = []
            for z in q:
                p = None
                for j in (sub or ()):
                    if RV.fires(env, rs[j], z):
                        p = rs[j][1]
                        break
                rp.append(0 if p is None else p)
            m[rid] = c.vec(errcount(rp, env, q))
        # --- SIG-P (real population search, mutation+selection, no grads) --
        cp = Counters()
        b = inv["Bmin"] if inv["Bmin"] >= 2 else 2
        torch.manual_seed(seed + 1)
        pop = [Body() for _ in range(b)]
        Xtr, Ytr = feats(env, list(tr)), labels(env, list(tr))
        for _step in range(inv["Tsteps"] * EPOCHS * 4):
            scores = []
            with torch.no_grad():
                for mem in pop:
                    pr = (mem(Xtr) >= 0.5).float()
                    scores.append(float((pr == Ytr).float().sum().item()))
                    cp.evals += Xtr.shape[0]
            order = sorted(range(b), key=lambda i: -scores[i])
            elite = pop[order[0]]
            newpop = [elite]
            for _ in range(b - 1):
                child = Body()
                child.load_state_dict(elite.state_dict())
                with torch.no_grad():
                    for prm in child.parameters():
                        prm.add_(torch.randn_like(prm) * POP_MUT_SCALE)
                newpop.append(child)
            pop = newpop
            cp.branch += (b - 1) * inv["Tsteps"]
        Xq = feats(env, q)
        with torch.no_grad():
            pp = [int(v >= 0.5) for v in pop[0](Xq).tolist()]
        cp.evals += Xq.shape[0]
        m["SIG-P"] = cp.vec(errcount(pp, env, q))
        # --- SIG-T (real meta-learner: body carried across K episodes) -----
        ct = Counters()
        torch.manual_seed(seed + 2)
        body = Body()
        opt = torch.optim.Adam(body.parameters(), lr=LR)
        lossf = nn.BCELoss()
        for ep, e in enumerate(episodes):
            ezs = list(e["train"])
            Xe, Ye = feats(e, ezs), labels(e, ezs)
            for _k in range(EPOCHS):
                for s in range(0, len(ezs), CHUNK):
                    opt.zero_grad()
                    out = body(Xe[s:s + CHUNK])
                    lossf(out, Ye[s:s + CHUNK]).backward()
                    opt.step()
                    ct.evals += Xe[s:s + CHUNK].shape[0]
                    ct.carry += Xe[s:s + CHUNK].shape[0]
            ct.meta += inv["Mprime"]
        with torch.no_grad():
            tp = [int(v >= 0.5) for v in body(Xq).tolist()]
        ct.evals += Xq.shape[0]
        m["SIG-T"] = ct.vec(errcount(tp, env, q))
        # --- SIG-S (real self-modifying learner) ---------------------------
        cs = Counters()
        torch.manual_seed(seed + 3)
        sbody = Body()
        opt = torch.optim.Adam(sbody.parameters(), lr=LR)
        allowed = list(range(RV.M))
        for ep, e in enumerate(episodes):
            ezs = list(e["train"])
            Xe, Ye = feats(e, ezs), labels(e, ezs)
            mask = torch.zeros(RV.M)
            for i in allowed:
                mask[i] = 1.0
            for _k in range(EPOCHS):
                for s in range(0, len(ezs), CHUNK):
                    opt.zero_grad()
                    out = sbody(Xe[s:s + CHUNK] * mask)
                    lossf(out, Ye[s:s + CHUNK]).backward()
                    opt.step()
                    cs.evals += Xe[s:s + CHUNK].shape[0]
                    cs.carry += Xe[s:s + CHUNK].shape[0]
            # registered successor-set change between episodes
            if ep + 1 < len(episodes) and len(allowed) > 2:
                allowed = allowed[:-1]
                cs.mut += 1
        maskq = torch.zeros(RV.M)
        for i in allowed:
            maskq[i] = 1.0
        with torch.no_grad():
            sp = [int(v >= 0.5) for v in sbody(Xq * maskq).tolist()]
        cs.evals += Xq.shape[0]
        m["SIG-S"] = cs.vec(errcount(sp, env, q))
        per_seed[seed] = m
    # median-of-two on the loss coordinate = the smaller (registered rule:
    # median of an even sample is the lower order statistic, frozen)
    sigs = ["SIG-W", "BASE-0", "NULL-0", "SIG-X", "SIG-R", "SIG-L", "SIG-P",
            "SIG-T", "SIG-S"]
    measured, spread, opaque_map = {}, {}, {}
    idx = 0
    for s in sigs:
        a, b_ = per_seed[seeds[0]][s], per_seed[seeds[1]][s]
        if a is None or b_ is None:
            continue
        idx += 1
        oid = "c%d" % idx
        lo = a if a[7] <= b_[7] else b_
        measured[oid] = [int(x) for x in lo]
        spread[oid] = abs(a[7] - b_[7])
        opaque_map[oid] = s
    out = {"system_id": sid, "source_used": used,
           "fallback_used": eco["fallback_used"],
           "source_sha256": eco["source_sha256"],
           "seeds": list(seeds), "measured": measured,
           "seed_spread": spread, "opaque_to_signature": opaque_map,
           "torch_version": torch.__version__,
           "train_seconds": int(time.time() - t0)}
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "ecology_%s.json" % sid)
    with open(p, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(sid, "sha", eco["source_sha256"][:12], "systems", len(measured),
          "secs", out["train_seconds"])
    return p


def main():
    outdir = sys.argv[1]
    torch.set_num_threads(4)
    for spec in RV.SOURCES:
        run_ecology(spec, outdir)


if __name__ == "__main__":
    main()
