#!/usr/bin/env python3
"""RAPL energy producer for gmi-833-ae-instruments-v1 (FREEZE_V1.md, Instrument III).

Runs on the registered host with `sudo -n` read access to the powercap
counters. Created AFTER the freeze commit dd9b34cef55ef13d144eb5a9258fbd515c55cd06
and the register commit 527f326ec342a3d3041880c63edc84a2cc46984f. Produces
only REAL_RUNS/energy/rapl_rounds.json. Every number recorded is an integer
read from the hardware or a step count; nothing is derived here.

Usage: python3 -I -B produce_energy_v1.py <pkg_dir> <cache_dir> <Cid>
"""
import hashlib
import json
import os
import subprocess
import sys
import time

import torch
import torch.nn as nn

torch.set_num_threads(1)

FREEZE_COMMIT = "dd9b34cef55ef13d144eb5a9258fbd515c55cd06"
REGISTER_COMMIT = "527f326ec342a3d3041880c63edc84a2cc46984f"
AMENDMENT_COMMIT = "212b989bd3e1b632bf256d61eab5139527089ae5"
DOMAINS = {
    "pkg_msr": "/sys/class/powercap/intel-rapl:0/energy_uj",
    "pkg_mmio": "/sys/class/powercap/intel-rapl-mmio:0/energy_uj",
    "core": "/sys/class/powercap/intel-rapl:0:0/energy_uj",
}
RANGE_PATH = "/sys/class/powercap/intel-rapl:0/max_energy_range_uj"
ROUNDS = 12
CHUNK = 64
IDLE_S = 2.0
BLOCKS = [("IDLE_A", 0), ("MLP_BATCH", 2000), ("MLP_SEQ", 8), ("GRU8", 4), ("GRU16", 4),
          ("GRU64", 2), ("GRU256", 1), ("GRU1024", 1), ("IDLE_B", 0)]


def read_counters():
    out = subprocess.run(["sudo", "-n", "cat"] + list(DOMAINS.values()), capture_output=True,
                         text=True, check=True).stdout.split()
    return dict(zip(DOMAINS.keys(), [int(v) for v in out]))


def coretemp_path():
    for h in sorted(os.listdir("/sys/class/hwmon")):
        p = os.path.join("/sys/class/hwmon", h)
        try:
            with open(os.path.join(p, "name")) as f:
                if f.read().strip() == "coretemp":
                    return os.path.join(p, "temp1_input")
        except OSError:
            pass
    return None


def read_temp(path):
    if path is None:
        return None
    with open(path) as f:
        return int(f.read().strip())


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


def hex_to_bits(h, n):
    raw = bytes.fromhex(h)
    out = []
    for byte in raw:
        for i in range(7, -1, -1):
            out.append((byte >> i) & 1)
            if len(out) == n:
                return out
    return out


def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    pkg, cache_dir, cid = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(os.path.join(cache_dir, cid + "_streams.json")) as f:
        cache = json.load(f)
    T, ntr = cache["T"], cache["n_train"]
    bits = hex_to_bits(cache["bits"]["base"], T)
    modes = hex_to_bits(cache["modes"], T)
    N = T - ntr
    X = torch.zeros(N, 2)
    for i, t in enumerate(range(ntr, T)):
        X[i, 0] = bits[t]
        X[i, 1] = modes[t]
    wp = os.path.join(cache_dir, cid + "_seed1")
    mlp = MLP(16)
    mlp.load_state_dict(torch.load(wp + "_mlp.pt"))
    weights = {"mlp": sha256_file(wp + "_mlp.pt")}
    grus = {}
    for H in (8, 16, 64):
        g = GRUModel(H)
        g.load_state_dict(torch.load(wp + "_gru%d.pt" % H))
        grus[H] = g
        weights["gru%d" % H] = sha256_file(wp + "_gru%d.pt" % H)
    for H in (256, 1024):
        g = GRUModel(H)
        g.load_state_dict(torch.load(wp + "_gru%d_random4242.pt" % H))
        grus[H] = g
        weights["gru%d" % H] = sha256_file(wp + "_gru%d_random4242.pt" % H)
    for m in [mlp] + list(grus.values()):
        m.eval()

    def mlp_batch(passes):
        with torch.no_grad():
            for _ in range(passes):
                mlp(X)

    def mlp_seq(passes):
        with torch.no_grad():
            for _ in range(passes):
                for i in range(0, N, CHUNK):
                    mlp(X[i:i + CHUNK])

    def gru_seq(H, passes):
        g = grus[H]
        with torch.no_grad():
            for _ in range(passes):
                h = None
                for i in range(0, N, CHUNK):
                    out, h = g.gru(X[i:i + CHUNK].unsqueeze(0), h)
                    g.out(out[0])

    def run_block(name, passes):
        if name.startswith("IDLE"):
            time.sleep(IDLE_S)
        elif name == "MLP_BATCH":
            mlp_batch(passes)
        elif name == "MLP_SEQ":
            mlp_seq(passes)
        else:
            gru_seq(int(name[3:]), passes)

    tpath = coretemp_path()
    with open(RANGE_PATH) as f:
        max_range = int(f.read().strip())
    # resolution probe: 50 rapid consecutive reads
    res = [read_counters() for _ in range(50)]
    rec = {"schema": "GMI_833_AE_INSTRUMENTS_ENERGY_RECORD_V1", "id": cid, "freeze_commit": FREEZE_COMMIT,
           "register_commit": REGISTER_COMMIT, "amendment_commit": AMENDMENT_COMMIT, "domains": DOMAINS, "max_energy_range_uj": max_range,
           "rounds": ROUNDS, "N_steps_per_pass": N, "chunk": CHUNK, "idle_seconds": IDLE_S,
           "blocks_registered": BLOCKS, "weights_sha256": weights, "torch": torch.__version__,
           "threads": torch.get_num_threads(), "coretemp_path": tpath,
           "resolution_probe": res, "blocks": []}
    # warm-up pass so the first block is not paying for lazy initialisation
    gru_seq(8, 1); mlp_seq(1); mlp_batch(10)
    for r in range(ROUNDS):
        order = BLOCKS[r % len(BLOCKS):] + BLOCKS[:r % len(BLOCKS)]
        for name, passes in order:
            temp0 = read_temp(tpath)
            e0 = read_counters()
            t0 = time.perf_counter_ns()
            run_block(name, passes)
            t1 = time.perf_counter_ns()
            e1 = read_counters()
            temp1 = read_temp(tpath)
            rec["blocks"].append({"round": r, "block": name, "passes": passes,
                                  "steps": (0 if passes == 0 else passes * N),
                                  "e_before": e0, "e_after": e1, "t_ns_before": t0, "t_ns_after": t1,
                                  "temp_before_mC": temp0, "temp_after_mC": temp1})
        print("round", r, "done", flush=True)
    out_dir = os.path.join(pkg, "REAL_RUNS", "energy")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "rapl_rounds.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print("written", flush=True)


if __name__ == "__main__":
    main()
