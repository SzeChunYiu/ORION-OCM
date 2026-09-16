"""Outcome producer for gmi-833-real-transition-receipts-v1 (FREEZE_V1.md).

Runs on the execution host (torch, CPU). Created AFTER the freeze commit
cd6196aa5fd0edcdbcfb535ff2aecf7cd0870754; produces REAL_RUNS/ artifacts only.
Deterministic given registered seeds. No family names enter scoring or
classification: candidates are opaque IDs `c1`/`c2` after construction.

Usage: python -I -B train_real_transitions_v1.py <repo_root> <out_dir>
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

ETA = 0.5  # registered delayed-mode frequency in expectation
TRAIN_FRAC = 0.8
CHUNK = 64
LR = 0.01
EPOCHS = 3
DTYPE_BYTES = 4

SYSTEMS = [
    # id, primary source, fallback source, T, W, H, p, seed
    ("R01-gutenberg-1342",
     "https://www.gutenberg.org/files/1342/1342-0.txt:/tmp/w6-gutenberg-1342.txt",
     "/usr/bin/git", 400000, 32, 32, 8.0, 101),
    ("R02-alsa-frontcenter",
     "/usr/share/sounds/alsa/Front_Center.wav",
     "/usr/bin/python3.8", 300000, 24, 24, 4.0, 202),
    ("R03-python38-binary",
     "/usr/bin/python3.8",
     "/usr/bin/git", 500000, 16, 48, 16.0, 303),
    ("R04-dpkg-log",
     "/var/log/dpkg.log",
     "/usr/share/sounds/alsa/Noise.wav", 200000, 24, 16, 2.0, 404),
    ("R05-stdlib-json",
     "/usr/lib/python3.8/json/__init__.py+/usr/lib/python3.8/json/decoder.py+"
     "/usr/lib/python3.8/json/encoder.py+/usr/lib/python3.8/json/scanner.py",
     "/var/log/dpkg.log", 250000, 32, 24, 8.0, 505),
    ("R06-spare-git",
     "/usr/bin/git",
     "", 400000, 16, 32, 32.0, 606),
]
SPARE_ID = "R06-spare-git"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def load_source(spec: str) -> tuple[Path, bool]:
    """Resolve a primary source spec (url:/path or path or a+b concatenation)."""
    parts = spec.split("+")
    if len(parts) == 1 and parts[0].startswith("http"):
        url, _, dest = parts[0].rpartition(":")
        d = Path(dest)
        if not d.exists():
            subprocess.run(["curl", "-fsSL", "--max-time", "120", "-o", str(d), url],
                           check=True, timeout=180)
        return d, True
    if len(parts) == 1:
        return Path(parts[0]), False
    # concatenation of real files, in listed order
    tmp = Path("/tmp/w6-concat-%s.bin" % hashlib.sha256(spec.encode()).hexdigest()[:12])
    if not tmp.exists():
        with open(tmp, "wb") as out:
            for p in parts:
                out.write(Path(p).read_bytes())
    return tmp, False


def bits_from_file(path: Path, T: int) -> np.ndarray:
    raw = path.read_bytes()
    n_bytes = (T + 7) // 8
    arr = np.frombuffer(raw[:n_bytes], dtype=np.uint8)
    bits = np.unpackbits(arr, bitorder="big")[:T].astype(np.float32)
    if bits.shape[0] < T:
        raise RuntimeError("source too short: %s" % path)
    return bits


class StatelessMLP(nn.Module):
    def __init__(self, width: int):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(2, width), nn.ReLU(), nn.Linear(width, 1))

    def forward(self, x):  # x: (N,2)
        return self.net(x).squeeze(-1)


class PersistentGRU(nn.Module):
    def __init__(self, hidden: int):
        super().__init__()
        self.gru = nn.GRU(2, hidden, batch_first=True)
        self.out = nn.Linear(hidden, 1)

    def forward(self, x):  # x: (N,2) flat stream -> sequential with carried h
        h = None
        outs = []
        for i in range(0, x.shape[0], CHUNK):
            c = x[i:i + CHUNK].unsqueeze(0)
            o, h = self.gru(c, h)
            h = h.detach()
            outs.append(self.out(o).squeeze(0).squeeze(-1))
        return torch.cat(outs)


def targets(bits: np.ndarray, modes: np.ndarray) -> np.ndarray:
    prev = np.concatenate([[0.0], bits[:-1]])
    y = np.where(modes == 1.0, prev, bits)  # mode 1 = DELAYED
    return y.astype(np.float32)


def eval_model(model, bits, modes, y, kind, batch=8192):
    model.eval()
    n = bits.shape[0]
    errs = np.zeros(n, dtype=np.float32)
    with torch.no_grad():
        if kind == "mlp":
            feats = torch.from_numpy(np.stack([bits, modes], axis=1))
            for i in range(0, n, batch):
                pred = model(feats[i:i + batch])
                errs[i:i + batch] = (pred > 0).numpy() != (y[i:i + batch] > 0.5)
        else:
            feats = torch.from_numpy(np.stack([bits, modes], axis=1))
            pred = model(feats)
            errs = (pred > 0).numpy() != (y > 0.5)
    dmask = modes == 1.0
    imask = ~dmask
    return {
        "err_all": float(errs.mean()),
        "err_delay": float(errs[dmask].mean()),
        "err_imm": float(errs[imask].mean()),
        "N_delay": int(dmask.sum()),
        "N_imm": int(imask.sum()),
    }


def train_candidate(kind, width, feats, y, seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = StatelessMLP(width) if kind == "mlp" else PersistentGRU(width)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    lossf = nn.BCEWithLogitsLoss()
    n = feats.shape[0]
    model.train()
    for _ in range(EPOCHS):
        if kind == "mlp":
            perm = torch.randperm(n)
            for i in range(0, n, 4096):
                idx = perm[i:i + 4096]
                opt.zero_grad()
                loss = lossf(model(feats[idx]), y[idx])
                loss.backward()
                opt.step()
        else:
            # full-stream truncated BPTT with carried (detached) state
            h = None
            for i in range(0, n, CHUNK):
                c = feats[i:i + CHUNK].unsqueeze(0)
                o, h2 = model.gru(c, h)
                h = h2.detach()
                pred = model.out(o).squeeze(0).squeeze(-1)
                loss = lossf(pred, y[i:i + CHUNK])
                opt.zero_grad()
                loss.backward()
                opt.step()
    return model


def main() -> None:
    repo = Path(sys.argv[1]).resolve()
    out_root = Path(sys.argv[2]).resolve()
    smoke = len(sys.argv) > 3 and sys.argv[3] == "smoke"
    global EPOCHS
    if smoke:
        EPOCHS = 1
    out_root.mkdir(parents=True, exist_ok=True)
    rng_global_note = "numpy PCG64 per-system mode seeds; torch seeds {s, s+1000}"

    available = []
    used_fallback = {}
    for row in SYSTEMS:
        sid, primary, fallback, T, W, H, p, seed = row
        try:
            src, downloaded = load_source(primary)
            if not src.exists():
                raise FileNotFoundError(src)
            available.append((sid, src, T, W, H, p, seed))
            used_fallback[sid] = False
        except Exception as e:  # registered fallback path
            print("primary failed for %s: %r -> fallback" % (sid, e))
            if not fallback:
                continue
            src, _ = load_source(fallback)
            if not src.exists():
                print("fallback also missing for %s; skipping" % sid)
                continue
            available.append((sid, src, T, W, H, p, seed))
            used_fallback[sid] = True

    # keep all distinct-source systems in registered order; the amendment's
    # pre-registered eligibility filter (licensed band) selects the receipt
    # set afterwards -- no post-hoc system choice happens here
    non_spare = [a for a in available if a[0] != SPARE_ID]
    spare = [a for a in available if a[0] == SPARE_ID]
    seen = set()
    ordered = []
    for a in non_spare + spare:
        key = a[1].resolve()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(a)
    available = ordered
    if len(available) < 5:
        raise RuntimeError("fewer than five systems available")

    for sid, src, T, W, H, p, seed in available:
        t0 = time.time()
        if smoke:
            T = min(T, 8000)
        bits = bits_from_file(src, T)
        modes = np.random.Generator(np.random.PCG64(seed)).integers(0, 2, size=T).astype(np.float32)
        y = targets(bits, modes)
        n_train = int(TRAIN_FRAC * T)
        feats_tr = torch.from_numpy(np.stack([bits[:n_train], modes[:n_train]], axis=1))
        y_tr = torch.from_numpy(y[:n_train])
        feats_ev = torch.from_numpy(np.stack([bits[n_train:], modes[n_train:]], axis=1))

        B_gru = DTYPE_BYTES * H
        lambda_star = p * ETA / (2 * B_gru)

        runs = {
            "system_id": sid,
            "source_path": str(src),
            "source_sha256": sha256_file(src),
            "source_bytes": src.stat().st_size,
            "fallback_used": used_fallback[sid],
            "T": T, "W": W, "H": H, "p": p, "seed": seed, "eta_registered": ETA,
            "B_gru": B_gru, "lambda_star": lambda_star,
            "lambda_low": lambda_star / 2, "lambda_high": 3 * lambda_star / 2,
            "realized_eta": float((modes == 1.0).mean()),
            "torch": torch.__version__, "numpy": np.__version__,
            "candidates": {},
            "protocol_note": rng_global_note,
        }

        for kind, cid, width in (("mlp", "c1", W), ("gru", "c2", H)):
            per_seed = []
            for s in (seed, seed + 1000):
                t1 = time.time()
                model = train_candidate(kind, width, feats_tr, y_tr, s)
                m = eval_model(model, bits[n_train:], modes[n_train:], y[n_train:], kind)
                m["train_seconds"] = round(time.time() - t1, 3)
                m["seed"] = s
                per_seed.append(m)
            errs_sorted = sorted(x["err_all"] for x in per_seed)
            med = errs_sorted[len(errs_sorted) // 2] if len(errs_sorted) % 2 else 0.5 * (errs_sorted[len(errs_sorted) // 2 - 1] + errs_sorted[len(errs_sorted) // 2])
            runs["candidates"][cid] = {
                "kind_recorded_post_outcome": kind,  # provenance only; never used by selection/classification
                "carried_state_bytes": 0 if kind == "mlp" else B_gru,
                "seeds_runs": per_seed,
                "err_all_median": med,
                "param_count": None,
            }

        # param counts measured from fresh constructions
        m1 = StatelessMLP(W)
        m2 = PersistentGRU(H)
        runs["candidates"]["c1"]["param_count"] = sum(q.numel() for q in m1.parameters())
        runs["candidates"]["c2"]["param_count"] = sum(q.numel() for q in m2.parameters())

        # analytic floor witness CONST-0 (never eligible as winner)
        dmask_ev = modes[n_train:] == 1.0
        runs["floor_witness_const0"] = {
            "err_imm": 0.5, "err_delay": 0.5, "err_all": 0.5,
            "N_imm": int((~dmask_ev).sum()), "N_delay": int(dmask_ev.sum()),
        }
        runs["wall_seconds"] = round(time.time() - t0, 3)

        d = out_root / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / "runs.json").write_text(json.dumps(runs, sort_keys=True, indent=1))
        print("done", sid, "lambda_star", lambda_star, "wall", runs["wall_seconds"])

    print("TRAINING-COMPLETE")


if __name__ == "__main__":
    main()
