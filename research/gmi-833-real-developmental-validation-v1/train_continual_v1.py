"""Section L outcome producer: real continual-learning systems.

Created AFTER freeze commit 808054d94dcdc188b7ef3e72cd55c18265ef22af.
Runs on the execution host (laptop-billy, torch CPU). For each of the eight
registered sequences (FREEZE_V1.md section 3.1) it trains one real body on a
sequence of four real tasks, then runs the two registered proposal laws on the
held-out discovery task, and writes REAL_RUNS/cl_<id>.json with exact integer
counts only. All verdicts are computed by the Route A scorer, never here.

Usage: python3 -B train_continual_v1.py <out REAL_RUNS dir>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import torch
import torch.nn as nn

NFEAT = 16          # delay features b[z-1] .. b[z-16]
K_SEQ = 4           # tasks in the sequence
SEQ_STEPS = 1200    # optimizer steps per sequence task (4 * 1200 = h_high)
B_PROP = 300        # optimizer steps in one proposal (= c)
N_PROP = 24         # registered proposals per law
BLOCKS = 4          # first-hit blocks of 6
T_TRAIN = 512
T_EVAL = 128
THETA_NUM, THETA_DEN = 1, 4
LR = 0.01
CHUNK = 32
SRC_ROOT = os.environ.get("OCM833_SRC_ROOT", "/home/billy/ocm-scratch/real-l/sources")

# (id, family, source, sequence delays, U rule, U offsets)
SEQUENCES = [
    ("S1", "POS", SRC_ROOT + "/g1342.txt", (1, 2, 3, 4), "AND", (1, 2)),
    ("S2", "POS", "/usr/share/sounds/alsa/Noise.wav", (1, 2, 3, 4), "OR", (1, 2)),
    ("S3", "POS", "/usr/lib/python3.8/json/__init__.py", (1, 2, 3, 4), "AND", (1, 3)),
    ("S4", "POS", "/usr/share/dict/american-english", (1, 2, 3, 4), "MAJ", (1, 2, 3)),
    ("S5", "POS", SRC_ROOT + "/g84.txt", (1, 2, 3, 4), "OR", (1, 3)),
    ("S6", "NEG", "/usr/bin/python3.8", (12, 13, 14, 15), "AND", (1, 2)),
    ("S7", "NEG", "/usr/share/sounds/alsa/Rear_Left.wav", (12, 13, 14, 15), "OR", (1, 2)),
    ("S8", "NEG", "/usr/share/dict/swedish", (0, 0, 0, 0), "AND", (1, 2)),
]


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
        for s in range(7, -1, -1):
            out.append((byte >> s) & 1)
    return out[:nbits]


def rule_val(bits, z, rule, offs):
    v = [bits[z - o] for o in offs]
    if rule == "AND":
        return 1 if all(v) else 0
    if rule == "OR":
        return 1 if any(v) else 0
    if rule == "MAJ":
        return 1 if sum(v) * 2 > len(v) else 0
    raise RuntimeError("unregistered rule " + rule)


class Net(nn.Module):
    """body (carried across the sequence) + head (re-initialised per task)"""

    def __init__(self):
        super(Net, self).__init__()
        self.body = nn.Sequential(nn.Linear(NFEAT, 16), nn.ReLU())
        self.head = nn.Linear(16, 1)

    def forward(self, x):
        return torch.sigmoid(self.head(self.body(x))).squeeze(-1)


def make_xy(bits, zs, target_fn):
    X = torch.tensor([[float(bits[z - d]) for d in range(1, NFEAT + 1)] for z in zs])
    Y = torch.tensor([float(target_fn(z)) for z in zs])
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


def errors(net, X, Y):
    with torch.no_grad():
        p = (net(X) >= 0.5).float()
    return int((p != Y).sum().item())


def run_sequence(spec, outdir):
    sid, fam, src, delays, urule, uoffs = spec
    sha = sha256_file(src)
    need = (K_SEQ + 1) * (T_TRAIN + T_EVAL) + NFEAT + 64
    bits = bits_from_file(src, need)
    t0 = time.time()
    lo = NFEAT + 8
    # --- the sequence of K_SEQ real tasks, body carried across --------------
    torch.manual_seed(1000 + int(sid[1:]))
    net = Net()
    stored = []
    for j, d in enumerate(delays):
        base = lo + j * (T_TRAIN + T_EVAL)
        zs = list(range(base, base + T_TRAIN))
        if d == 0:                      # registered degenerate constant task
            fn = (lambda z: 1)
        else:
            fn = (lambda z, dd=d: bits[z - dd])
        X, Y = make_xy(bits, zs, fn)
        net.head = nn.Linear(16, 1)     # head re-initialised per task
        fit(net, X, Y, SEQ_STEPS, 2000 + 17 * j + int(sid[1:]))
        stored.append({k: v.clone() for k, v in net.state_dict().items()})
    seq_body = {k: v.clone() for k, v in net.state_dict().items() if k.startswith("body")}
    # --- the held-out discovery task U -------------------------------------
    ubase = lo + K_SEQ * (T_TRAIN + T_EVAL)
    uz_tr = list(range(ubase, ubase + T_TRAIN))
    uz_ev = list(range(ubase + T_TRAIN, ubase + T_TRAIN + T_EVAL))
    ufn = (lambda z: rule_val(bits, z, urule, uoffs))
    Xtr, Ytr = make_xy(bits, uz_tr, ufn)
    Xev, Yev = make_xy(bits, uz_ev, ufn)
    crit = (THETA_NUM * T_EVAL) // THETA_DEN
    # --- CAPITAL-1 disjointness gate: stored solutions, no further training --
    stored_hits = 0
    stored_errs = []
    for st in stored:
        probe = Net()
        probe.load_state_dict(st)
        e = errors(probe, Xev, Yev)
        stored_errs.append(e)
        if e <= crit:
            stored_hits += 1
    # --- the two registered proposal laws ----------------------------------
    def proposals(use_history):
        hits, first_hit, errs = [], [], []
        for i in range(N_PROP):
            seed = 5000 + 31 * i + int(sid[1:])
            torch.manual_seed(seed)
            cand = Net()
            if use_history:
                sd = cand.state_dict()
                sd.update(seq_body)
                cand.load_state_dict(sd)
                cand.head = nn.Linear(16, 1)
            fit(cand, Xtr, Ytr, B_PROP, seed)
            e = errors(cand, Xev, Yev)
            errs.append(e)
            hits.append(1 if e <= crit else 0)
        per = N_PROP // BLOCKS
        censored = 0
        for b in range(BLOCKS):
            blk = hits[b * per:(b + 1) * per]
            if 1 in blk:
                first_hit.append(blk.index(1) + 1)
            else:
                censored += 1
        return hits, first_hit, censored, errs

    h0, f0, c0, e0 = proposals(False)
    hH, fH, cH, eH = proposals(True)
    # C_now: capability of a drawn init before any proposal training
    torch.manual_seed(7777 + int(sid[1:]))
    n0 = Net()
    cnow0 = 1 if errors(n0, Xev, Yev) <= crit else 0
    nH = Net()
    sd = nH.state_dict()
    sd.update(seq_body)
    nH.load_state_dict(sd)
    nH.head = nn.Linear(16, 1)
    cnowH = 1 if errors(nH, Xev, Yev) <= crit else 0
    rec = {
        "sequence_id": sid, "family": fam, "source": src, "source_sha256": sha,
        "sequence_delays": list(delays), "U_rule": urule, "U_offsets": list(uoffs),
        "criterion_errors": crit, "T_eval": T_EVAL,
        "successes_Q0": int(sum(h0)), "successes_QH": int(sum(hH)),
        "errors_Q0": e0, "errors_QH": eH,
        "first_hit_sum_QH": int(sum(fH)), "first_hit_blocks_QH": len(fH),
        "first_hit_censored_QH": cH,
        "first_hit_sum_Q0": int(sum(f0)), "first_hit_blocks_Q0": len(f0),
        "first_hit_censored_Q0": c0,
        "stored_solution_reaches_U": bool(stored_hits > 0),
        "stored_solution_errors": stored_errs,
        "law_changed": True,
        "C_now_Q0": cnow0, "C_now_QH": cnowH,
        "C_pot_Q0": 1 if sum(h0) > 0 else 0,
        "C_pot_QH": 1 if sum(hH) > 0 else 0,
        "torch_version": torch.__version__,
        "train_seconds": int(time.time() - t0),
    }
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "cl_%s.json" % sid)
    with open(p, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write("\n")
    print(sid, fam, "p0=%d/24 pH=%d/24" % (sum(h0), sum(hH)),
          "storedhit=%d" % stored_hits, "secs", rec["train_seconds"])
    return p


def main():
    torch.set_num_threads(4)
    outdir = sys.argv[1]
    for spec in SEQUENCES:
        run_sequence(spec, outdir)


if __name__ == "__main__":
    main()
