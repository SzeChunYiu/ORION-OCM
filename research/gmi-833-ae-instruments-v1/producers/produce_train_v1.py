#!/usr/bin/env python3
"""Training producer for gmi-833-ae-instruments-v1 (FREEZE_V1.md, Instruments I and II).

Runs on the registered host (torch 2.4.1+cpu, one thread). Created AFTER the
freeze commit dd9b34cef55ef13d144eb5a9258fbd515c55cd06 and the register
commit 527f326ec342a3d3041880c63edc84a2cc46984f. Produces only REAL_RUNS
artifacts (plus laptop-local weight files for the energy producer).

Usage: python3 -I -B produce_train_v1.py <pkg_dir> <cache_dir> <Cid> [--ladder]

Family names never enter any scoring here; every run is recorded as raw
integer counts and per-position prediction bits and is scored later by the
stdlib routes.
"""
import base64
import hashlib
import json
import os
import sys
import time
import zlib
from fractions import Fraction

import torch
import torch.nn as nn

torch.set_num_threads(1)

FREEZE_COMMIT = "dd9b34cef55ef13d144eb5a9258fbd515c55cd06"
REGISTER_COMMIT = "527f326ec342a3d3041880c63edc84a2cc46984f"
AMENDMENT_COMMIT = "212b989bd3e1b632bf256d61eab5139527089ae5"
CHUNK = 64
LR = 0.01
EPOCHS = 3
W_MLP = 16
H_GRU = 16
PROBE = 2048
WARMUP = 4096
CKPT_STEPS = sorted(set(list(range(0, 301, 10)) + list(range(350, 1001, 50)) + list(range(1250, 5501, 250))))


def hex_to_bits(h, n):
    raw = bytes.fromhex(h)
    out = []
    for byte in raw:
        for i in range(7, -1, -1):
            out.append((byte >> i) & 1)
            if len(out) == n:
                return out
    return out


def bits_to_hex(bits):
    n = len(bits)
    out = bytearray()
    for i in range(0, n, 8):
        v = 0
        for j in range(8):
            v = (v << 1) | (bits[i + j] if i + j < n else 0)
        out.append(v)
    return out.hex()


def fr(x):
    return "%d/%d" % (x.numerator, x.denominator)


def make_xy(bits, modes):
    T = len(bits)
    X = torch.zeros(T, 2)
    Y = torch.zeros(T)
    prev = 0
    for t in range(T):
        X[t, 0] = bits[t]
        X[t, 1] = modes[t]
        Y[t] = bits[t] if modes[t] == 0 else prev
        prev = bits[t]
    return X, Y


class MLP(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(2, width), nn.ReLU(), nn.Linear(width, 1))

    def forward(self, x):
        return self.net(x).squeeze(-1)


class GRUModel(nn.Module):
    def __init__(self, hidden):
        super().__init__()
        self.gru = nn.GRU(2, hidden, batch_first=True)
        self.out = nn.Linear(hidden, 1)


def param_count(m):
    return sum(p.numel() for p in m.parameters())


def pack_codes(codes):
    """codes: list of ints (< 2**16) -> base64(zlib(uint16 LE))."""
    raw = bytearray()
    for c in codes:
        raw.append(c & 0xFF)
        raw.append((c >> 8) & 0xFF)
    return base64.b64encode(zlib.compress(bytes(raw), 9)).decode("ascii")


def codes_from_h(h):
    b = (h > 0).to(torch.int64)
    weights = torch.tensor([1 << i for i in range(h.shape[1])], dtype=torch.int64)
    return (b * weights).sum(dim=1).tolist()


def pr_rank(h):
    hc = h - h.mean(dim=0, keepdim=True)
    cov = hc.t() @ hc / max(1, h.shape[0] - 1)
    ev = torch.linalg.eigvalsh(cov).clamp(min=0)
    s1 = float(ev.sum())
    s2 = float((ev * ev).sum())
    return (s1 * s1 / s2) if s2 > 0 else 0.0


# ----------------------------------------------------------------- training

def train_mlp(seed, X, Y, ntr, epochs):
    torch.manual_seed(seed)
    m = MLP(W_MLP)
    opt = torch.optim.Adam(m.parameters(), lr=LR)
    lossf = nn.BCEWithLogitsLoss()
    losses = []
    for _ in range(epochs):
        for i in range(0, ntr, CHUNK):
            xb, yb = X[i:i + CHUNK], Y[i:i + CHUNK]
            loss = lossf(m(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
            losses.append(float(loss))
    return m, losses


def gru_probe(m, X, Y, ntr, modes_probe_flipped=None):
    """Run from zero state over the last WARMUP train positions + PROBE eval positions.
    Returns hidden states at probe positions and their mode-flipped counterfactuals."""
    start = ntr - WARMUP
    with torch.no_grad():
        seq = X[start:ntr + PROBE].unsqueeze(0)
        out, _ = m.gru(seq)
        hs = out[0]  # (WARMUP+PROBE, H)
        h_probe = hs[WARMUP:]
        h_prev = torch.cat([hs[WARMUP - 1:WARMUP], hs[WARMUP:-1]], dim=0)  # h_{t-1} for probe t
        xf = X[ntr:ntr + PROBE].clone()
        xf[:, 1] = 1 - xf[:, 1]
        out_cf, _ = m.gru(xf.unsqueeze(1), h_prev.unsqueeze(0).contiguous())
        h_cf = out_cf[:, 0, :]
        logits = m.out(h_probe).squeeze(-1)
        pred = (logits > 0).to(torch.int64)
    return h_probe, h_cf, pred


def train_gru(seed, X, Y, ntr, H, epochs, fp16=False, ckpt=False, modes=None):
    torch.manual_seed(seed)
    m = GRUModel(H)
    opt = torch.optim.Adam(m.parameters(), lr=LR)
    lossf = nn.BCEWithLogitsLoss()
    losses = []
    ckpts = []
    step = 0
    ck_set = set(CKPT_STEPS)

    def record(step):
        h_probe, h_cf, pred = gru_probe(m, X, Y, ntr)
        yp = Y[ntr:ntr + PROBE].to(torch.int64)
        mp = torch.tensor(modes[ntr:ntr + PROBE], dtype=torch.int64)
        wrong = (pred != yp).to(torch.int64)
        ckpts.append({
            "step": step,
            "train_loss_running_last10": (sum(losses[-10:]) / len(losses[-10:])) if losses else None,
            "cap_wrong_delayed": int((wrong * mp).sum()), "cap_N_delayed": int(mp.sum()),
            "wrong_immediate": int((wrong * (1 - mp)).sum()), "N_immediate": int((1 - mp).sum()),
            "codes_b64": pack_codes(codes_from_h(h_probe)),
            "codes_cf_b64": pack_codes(codes_from_h(h_cf)),
            "pr_rank": pr_rank(h_probe),
        })

    if ckpt:
        record(0)
    for _ in range(epochs):
        h = None
        for i in range(0, ntr, CHUNK):
            xb = X[i:i + CHUNK].unsqueeze(0)
            yb = Y[i:i + CHUNK]
            out, h = m.gru(xb, h)
            loss = lossf(m.out(out[0]).squeeze(-1), yb)
            opt.zero_grad(); loss.backward(); opt.step()
            losses.append(float(loss))
            h = h.detach()
            if fp16:
                h = h.half().float()
            step += 1
            if ckpt and step in ck_set:
                record(step)
    if ckpt and step not in ck_set:
        record(step)
    return m, losses, ckpts, step


def eval_gru(m, X, Y, ntr, fp16=False):
    with torch.no_grad():
        h = None
        preds = []
        for i in range(0, X.shape[0], CHUNK):
            out, h = m.gru(X[i:i + CHUNK].unsqueeze(0), h)
            if fp16:
                h = h.half().float()
            preds.append((m.out(out[0]).squeeze(-1) > 0).to(torch.int64))
        pred = torch.cat(preds)
    return pred[ntr:]


def eval_mlp(m, X, ntr):
    with torch.no_grad():
        return (m(X[ntr:]) > 0).to(torch.int64)


def score(pred, Y, modes, ntr):
    yp = Y[ntr:].to(torch.int64)
    mp = torch.tensor(modes[ntr:], dtype=torch.int64)
    wrong = (pred != yp).to(torch.int64)
    return {"N_imm": int((1 - mp).sum()), "wrong_imm": int((wrong * (1 - mp)).sum()),
            "N_delay": int(mp.sum()), "wrong_delay": int((wrong * mp).sum()),
            "pred_hex": bits_to_hex(pred.tolist())}


def run_pair(tag, bits, modes, ntr, seeds, H=H_GRU, epochs=EPOCHS, fp16=False, ckpt_seed=None, save_weights=None):
    X, Y = make_xy(bits, modes)
    rec = {"tag": tag, "T": len(bits), "n_train": ntr, "n_eval": len(bits) - ntr, "H": H, "epochs": epochs,
           "fp16_state": fp16, "state_bytes": (2 * H if fp16 else 4 * H), "W": W_MLP, "seeds": seeds,
           "mlp": {}, "gru": {}, "ckpt": None, "torch": torch.__version__, "threads": torch.get_num_threads()}
    for s in seeds:
        t0 = time.perf_counter()
        mm, ml = train_mlp(s, X, Y, ntr, epochs)
        tm = time.perf_counter() - t0
        sc = score(eval_mlp(mm, X, ntr), Y, modes, ntr)
        sc.update({"seed": s, "wall_seconds": tm, "params": param_count(mm), "final_train_loss": ml[-1]})
        rec["mlp"][str(s)] = sc
        if save_weights and s == seeds[0]:
            torch.save(mm.state_dict(), save_weights + "_mlp.pt")
        t0 = time.perf_counter()
        do_ckpt = (ckpt_seed is not None and s == ckpt_seed)
        gm, gl, ck, steps = train_gru(s, X, Y, ntr, H, epochs, fp16=fp16, ckpt=do_ckpt, modes=modes)
        tg = time.perf_counter() - t0
        sc = score(eval_gru(gm, X, Y, ntr, fp16=fp16), Y, modes, ntr)
        sc.update({"seed": s, "wall_seconds": tg, "params": param_count(gm), "final_train_loss": gl[-1],
                   "optimizer_steps": steps})
        rec["gru"][str(s)] = sc
        if do_ckpt:
            rec["ckpt"] = {"seed": s, "steps": CKPT_STEPS, "probe": PROBE, "warmup": WARMUP, "records": ck}
        if save_weights and s == seeds[0]:
            torch.save(gm.state_dict(), save_weights + "_gru%d.pt" % H)
    return rec


# ------------------------------------------------------------- tabular learners

def tabular_run(kind, bits, modes, ntr):
    """Online majority table; kind = 'persistent' (x_{t-1}, x_t, m_t) or 'stateless' (x_t, m_t)."""
    tab = {}
    ck = []
    xprev = [0] + bits[:-1]

    def ctx(t):
        if kind == "persistent":
            return (xprev[t] << 2) | (bits[t] << 1) | modes[t]
        return (bits[t] << 1) | modes[t]

    def target(t):
        return bits[t] if modes[t] == 0 else xprev[t]

    def record(step):
        codes, wrong_d, nd, wrong_i, ni = [], 0, 0, 0, 0
        for t in range(ntr, ntr + PROBE):
            c = ctx(t)
            codes.append(c)
            n = tab.get(c)
            pred = 0 if n is None else (1 if n[1] > n[0] else 0)
            w = int(pred != target(t))
            if modes[t]:
                nd += 1; wrong_d += w
            else:
                ni += 1; wrong_i += w
        ck.append({"step": step, "train_loss_running_last10": None, "cap_wrong_delayed": wrong_d,
                   "cap_N_delayed": nd, "wrong_immediate": wrong_i, "N_immediate": ni,
                   "codes_b64": pack_codes(codes), "codes_cf_b64": None, "pr_rank": None})

    record(0)
    step = 0
    ck_set = set(CKPT_STEPS)
    for i in range(0, ntr, CHUNK):
        for t in range(i, min(i + CHUNK, ntr)):
            tab.setdefault(ctx(t), [0, 0])[target(t)] += 1
        step += 1
        if step in ck_set:
            record(step)
    if step not in ck_set:
        record(step)
    return {"kind": kind, "context_bits": 3 if kind == "persistent" else 2, "steps": CKPT_STEPS,
            "probe": PROBE, "records": ck, "optimizer_steps": step}


# --------------------------------------------------------------------- main

def main():
    pkg, cache_dir, cid = sys.argv[1], sys.argv[2], sys.argv[3]
    ladder = "--ladder" in sys.argv
    out_dir = os.path.join(pkg, "REAL_RUNS", cid)
    with open(os.path.join(out_dir, "corpus.json")) as f:
        corpus = json.load(f)
    with open(os.path.join(cache_dir, cid + "_streams.json")) as f:
        cache = json.load(f)
    T, ntr, seed = cache["T"], cache["n_train"], cache["seed"]
    modes = hex_to_bits(cache["modes"], T)
    streams = {k: hex_to_bits(v, T) for k, v in cache["bits"].items()}
    seeds = [seed, seed + 7]
    base_m = corpus["variants"]["base"]
    eta_train = Fraction(corpus["realized_eta_train"])

    def in_band_v2(m):
        # FREEZE_V2_AMENDMENT.md: the parent's A4 band on the whole-stream floor
        e0_all = eta_train * Fraction(m["E0"])
        return Fraction(1, 8) < e0_all < Fraction(3, 8)

    in_band = in_band_v2(base_m)
    G = Fraction(base_m["G"])
    plan = {"base": True,
            "bitshuf": in_band and G >= Fraction(1, 64),
            "complement": in_band,
            "reversal": in_band and in_band_v2(corpus["variants"]["reversal"])}
    results = {"schema": "GMI_833_AE_INSTRUMENTS_TRAIN_RECORD_V1", "id": cid, "freeze_commit": FREEZE_COMMIT,
               "register_commit": REGISTER_COMMIT, "amendment_commit": AMENDMENT_COMMIT,
               "in_band_v1_rule": base_m["in_band"], "in_band": in_band, "band_rule": "V2: 1/8 < eta_train*E0 < 3/8", "plan": {k: bool(v) for k, v in plan.items()},
               "runs": {}}
    wpath = os.path.join(cache_dir, cid + "_seed1")
    for variant, do in plan.items():
        if not do:
            results["runs"][variant] = {"skipped": True, "reason": "OUT_OF_BAND" if not in_band else "NOT_APPLICABLE"}
            continue
        bits = streams[variant]
        results["runs"][variant] = run_pair(variant, bits, modes, ntr, seeds,
                                            ckpt_seed=(seed if variant == "base" else None),
                                            save_weights=(wpath if variant == "base" else None))
        print(cid, variant, "done", flush=True)
    # neural control: modes := 0 everywhere, checkpointed, first seed only
    if in_band:
        zero_modes = [0] * T
        results["runs"]["control_immediate_only"] = run_pair("control_immediate_only", streams["base"], zero_modes,
                                                             ntr, [seed], ckpt_seed=seed)
        results["runs"]["tabular_persistent"] = tabular_run("persistent", streams["base"], modes, ntr)
        results["runs"]["tabular_stateless"] = tabular_run("stateless", streams["base"], modes, ntr)
        print(cid, "controls done", flush=True)
    if ladder and in_band:
        b = streams["base"]
        lad = {}
        for H in (8, 32, 64):
            lad["H%d" % H] = run_pair("H%d" % H, b, modes, ntr, seeds, H=H, save_weights=wpath)
            print(cid, "ladder H", H, "done", flush=True)
        lad["H16_fp16"] = run_pair("H16_fp16", b, modes, ntr, seeds, H=16, fp16=True)
        Ts = 40000
        lad["T_small"] = run_pair("T_small", b[:Ts], modes[:Ts], 3 * Ts // 4, seeds)
        lad["one_pass"] = run_pair("one_pass", b, modes, ntr, seeds, epochs=1)
        for H in (256, 1024):
            torch.manual_seed(4242)
            torch.save(GRUModel(H).state_dict(), wpath + "_gru%d_random4242.pt" % H)
        results["ladder"] = lad
        print(cid, "ladder done", flush=True)
    with open(os.path.join(out_dir, "train.json"), "w") as f:
        json.dump(results, f, indent=1, sort_keys=True)
    print(cid, "written", flush=True)


if __name__ == "__main__":
    main()
