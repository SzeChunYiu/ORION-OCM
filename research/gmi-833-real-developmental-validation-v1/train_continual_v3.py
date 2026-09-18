"""Section L V3 outcome producer (FREEZE_V3_REVIVAL.md).

Created AFTER revival freeze commit 8ada2a533e24d96f569ee2d0ea64406c496ae464.
Runs on the execution host (laptop-billy, torch CPU). Writes only
REAL_RUNS/cl3_<id>.json; all verdicts are computed by the Route A scorer.

Usage: python3 -B train_continual_v3.py <out REAL_RUNS dir>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import torch
import torch.nn as nn

NFEAT = 16
K_SEQ = 4
SEQ_STEPS = 120          # h_high = K_SEQ * SEQ_STEPS = 480 (V3 lever)
N_PROP = 24
BLOCKS = 4
T_TRAIN, T_EVAL = 512, 128
THETA_DEN = 8            # criterion: at most T_EVAL/8 = 16 errors
WIDTH = 6
LR = 0.01
CHUNK = 32
SRC_ROOT = os.environ.get("OCM833_SRC_ROOT", "/home/billy/ocm-scratch/real-l/sources")

POS_SEQ = ((1, 3), (2, 4), (1, 4), (2, 3))
NEG_SEQ = ((12, 13), (13, 14), (14, 15), (12, 15))
UOFF = (1, 2)
# (pos id, neg id, source, registered per-source proposal budget B_prop = c)
SOURCES_V3 = [
    ("T01", "T11", SRC_ROOT + "/g2701.txt", 180),
    ("T02", "T12", SRC_ROOT + "/g11.txt", 90),
    ("T03", "T13", "/usr/share/dict/cracklib-small", 120),
    ("T04", "T14", "/usr/lib/python3.8/argparse.py", 90),
    ("T05", "T15", "/usr/lib/python3.8/difflib.py", 180),
    ("T06", "T16", "/usr/lib/python3.8/tokenize.py", 120),
    ("T07", "T17", "/usr/share/dict/swedish", 120),
]
SEQUENCES = []
for _p, _n, _s, _b in SOURCES_V3:
    SEQUENCES.append((_p, "POS", _s, POS_SEQ, UOFF, _b))
    SEQUENCES.append((_n, "NEG", _s, NEG_SEQ, UOFF, _b))



def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def bits_from_file(path, nbits):
    raw = open(path, "rb").read()
    need = (nbits + 7) // 8
    if len(raw) < need:
        raise RuntimeError("source too short: " + path)
    out = []
    for byte in raw[:need]:
        for s in (7, 6, 5, 4, 3, 2, 1, 0):
            out.append((byte >> s) & 1)
    return out[:nbits]


def xor_at(bits, z, offs):
    if offs[0] == 0:
        return 1                      # registered degenerate constant task
    v = 0
    for o in offs:
        v ^= bits[z - o]
    return v


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.body = nn.Sequential(nn.Linear(NFEAT, WIDTH), nn.ReLU())
        self.head = nn.Linear(WIDTH, 1)

    def forward(self, x):
        return torch.sigmoid(self.head(self.body(x))).squeeze(-1)


def make_xy(bits, zs, fn):
    X = torch.tensor([[float(bits[z - d]) for d in range(1, NFEAT + 1)] for z in zs])
    Y = torch.tensor([float(fn(z)) for z in zs])
    return X, Y


def fit(net, X, Y, steps, seed):
    torch.manual_seed(seed)
    opt = torch.optim.Adam(net.parameters(), lr=LR)
    lossf = nn.BCELoss()
    n, done = X.shape[0], 0
    while done < steps:
        for s in range(0, n, CHUNK):
            if done >= steps:
                break
            opt.zero_grad()
            lossf(net(X[s:s + CHUNK]), Y[s:s + CHUNK]).backward()
            opt.step()
            done += 1
    return net


def correct(net, X, Y):
    with torch.no_grad():
        p = (net(X) >= 0.5).float()
    return int((p == Y).sum().item())


def run(spec, outdir):
    sid, fam, src, seq, uoffs, b_prop = spec
    B_PROP = b_prop
    B1, B2 = max(1, b_prop // 3), b_prop
    sha = sha256_file(src)
    need = (K_SEQ + 1) * (T_TRAIN + T_EVAL) + NFEAT + 64
    bits = bits_from_file(src, need)
    t0 = time.time()
    lo = NFEAT + 8
    n_sid = int(sid[1:])
    torch.manual_seed(1000 + n_sid)
    net = Net()
    stored = []
    for j, offs in enumerate(seq):
        base = lo + j * (T_TRAIN + T_EVAL)
        zs = list(range(base, base + T_TRAIN))
        X, Y = make_xy(bits, zs, lambda z, o=offs: xor_at(bits, z, o))
        net.head = nn.Linear(WIDTH, 1)
        fit(net, X, Y, SEQ_STEPS, 2000 + 17 * j + n_sid)
        stored.append(dict((k, v.clone()) for k, v in net.state_dict().items()))
    seq_body = dict((k, v.clone()) for k, v in net.state_dict().items()
                    if k.startswith("body"))
    ub = lo + K_SEQ * (T_TRAIN + T_EVAL)
    uz_tr = list(range(ub, ub + T_TRAIN))
    uz_ev = list(range(ub + T_TRAIN, ub + T_TRAIN + T_EVAL))
    ufn = (lambda z: xor_at(bits, z, uoffs))
    Xtr, Ytr = make_xy(bits, uz_tr, ufn)
    Xev, Yev = make_xy(bits, uz_ev, ufn)
    crit_correct = T_EVAL - (T_EVAL // THETA_DEN)
    stored_scores = []
    for st in stored:
        p = Net()
        p.load_state_dict(st)
        stored_scores.append(correct(p, Xev, Yev))
    stored_hits = sum(1 for s in stored_scores if s >= crit_correct)

    def law(use_history, budget):
        scores = []
        for i in range(N_PROP):
            seed = 5000 + 31 * i + n_sid
            torch.manual_seed(seed)
            c = Net()
            if use_history:
                sd = c.state_dict()
                sd.update(seq_body)
                c.load_state_dict(sd)
                c.head = nn.Linear(WIDTH, 1)
            fit(c, Xtr, Ytr, budget, seed)
            scores.append(correct(c, Xev, Yev))
        hits = [1 if s >= crit_correct else 0 for s in scores]
        per = N_PROP // BLOCKS
        fh, cens = [], 0
        for b in range(BLOCKS):
            blk = hits[b * per:(b + 1) * per]
            if 1 in blk:
                fh.append(blk.index(1) + 1)
            else:
                cens += 1
        return scores, hits, fh, cens

    s0b2, h0, f0, c0 = law(False, B2)
    sHb2, hH, fH, cH = law(True, B2)
    s0b1, _, _, _ = law(False, B1)
    sHb1, _, _, _ = law(True, B1)
    torch.manual_seed(7777 + n_sid)
    n0 = Net()
    cnow0 = correct(n0, Xev, Yev)
    nH = Net()
    sd = nH.state_dict()
    sd.update(seq_body)
    nH.load_state_dict(sd)
    nH.head = nn.Linear(WIDTH, 1)
    cnowH = correct(nH, Xev, Yev)
    rec = {
        "sequence_id": sid, "family": fam, "source": src, "source_sha256": sha,
        "sequence_tasks": [list(o) for o in seq], "U_rule": "XOR",
        "U_offsets": list(uoffs), "criterion_correct": crit_correct,
        "T_eval": T_EVAL, "N_prop": N_PROP, "c": B_PROP,
        "B1": B1, "B2": B2, "h_low": 0, "h_high": K_SEQ * SEQ_STEPS,
        "successes_Q0": int(sum(h0)), "successes_QH": int(sum(hH)),
        "scores_Q0_B2": s0b2, "scores_QH_B2": sHb2,
        "scores_Q0_B1": s0b1, "scores_QH_B1": sHb1,
        "first_hit_sum_QH": int(sum(fH)), "first_hit_blocks_QH": len(fH),
        "first_hit_censored_QH": cH,
        "first_hit_sum_Q0": int(sum(f0)), "first_hit_blocks_Q0": len(f0),
        "first_hit_censored_Q0": c0,
        "stored_solution_reaches_U": bool(stored_hits > 0),
        "stored_solution_scores": stored_scores,
        "law_changed": True,
        "C_now_Q0": cnow0, "C_now_QH": cnowH,
        "C_pot_Q0_B1": max(s0b1), "C_pot_QH_B1": max(sHb1),
        "C_pot_Q0_B2": max(s0b2), "C_pot_QH_B2": max(sHb2),
        "torch_version": torch.__version__,
        "train_seconds": int(time.time() - t0),
    }
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "cl3_%s.json" % sid)
    with open(p, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write("\n")
    print(sid, fam, "p0=%d/24 pH=%d/24" % (sum(h0), sum(hH)),
          "storedhit=%d" % stored_hits, "Cnow", cnow0, cnowH,
          "Cpot_B2", max(s0b2), max(sHb2), "secs", rec["train_seconds"], flush=True)


def main():
    torch.set_num_threads(4)
    for spec in SEQUENCES:
        run(spec, sys.argv[1])


if __name__ == "__main__":
    main()
