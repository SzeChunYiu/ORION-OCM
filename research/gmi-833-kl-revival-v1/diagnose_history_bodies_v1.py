"""Post-outcome diagnosis of the row-L scores (FREEZE_V1.md 4.6: a miss is
attributed to ONE stage and the bit statistics are reported).

For every admitted posterior source and both families the sequence phase of
``train_continual_v4.run`` is reproduced op-for-op (same seeds, same order), and
the history-conditioned BODY is inspected BEFORE any proposal is trained:
live ReLU units on the U training inputs, all-zero activation rows, distinct
activation-sign patterns.  Fresh (baseline) bodies are inspected the same way.
Label and input-bit statistics of the U task and of the four sequence tasks are
reported per source.  Nothing here changes any receipt; this file only reads
the sources and writes ``L4_DIAGNOSIS_V1.json``.

Runs on laptop-billy:  python3 -B diagnose_history_bodies_v1.py POSTERIOR_SOURCES_V1.json
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

import torch
import torch.nn as nn

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import train_continual_v4 as T  # noqa: E402


def body_stats(net, X):
    with torch.no_grad():
        pre = net.body[0](X)                     # Linear pre-activations
        act = torch.relu(pre)
    live_frac = (act > 0).float().mean(dim=0)    # per unit
    live_units = int((live_frac > 0).sum().item())
    dead_units = T.WIDTH - live_units
    zero_rows = int((act.sum(dim=1) == 0).sum().item())
    patterns = len(set(tuple(int(v) for v in row) for row in (act > 0).int().tolist()))
    return {"live_units": live_units, "dead_units": dead_units,
            "unit_live_fraction": [str(Fraction(int(round(f * X.shape[0])), X.shape[0])) for f in live_frac.tolist()],
            "all_zero_activation_rows": zero_rows, "rows": int(X.shape[0]),
            "distinct_sign_patterns": patterns,
            "body_weight_abs_mean": str(Fraction(net.body[0].weight.abs().mean().item()).limit_denominator(10 ** 6))}


def label_stats(bits, zs, fn):
    ys = [fn(z) for z in zs]
    ones = sum(ys)
    return {"n": len(ys), "ones": ones, "mean": str(Fraction(ones, len(ys)))}


def sequence_body(bits, n_sid, seq):
    """Op-for-op copy of the sequence phase of train_continual_v4.run."""
    lo = T.NFEAT + 8
    torch.manual_seed(1000 + n_sid)
    net = T.Net()
    for j, offs in enumerate(seq):
        base = lo + j * (T.T_TRAIN + T.T_EVAL)
        zs = list(range(base, base + T.T_TRAIN))
        X, Y = T.make_xy(bits, zs, lambda z, o=offs: T.xor_at(bits, z, o))
        net.head = nn.Linear(T.WIDTH, 1)
        T.fit(net, X, Y, T.SEQ_STEPS, 2000 + 17 * j + n_sid)
    return net


def main():
    torch.set_num_threads(4)
    with open(sys.argv[1]) as f:
        record = json.load(f)
    need = (T.K_SEQ + 1) * (T.T_TRAIN + T.T_EVAL) + T.NFEAT + 64
    out = {"schema": "GMI_833_KL_REVIVAL_L4_DIAGNOSIS_V1", "torch_version": torch.__version__,
           "sources": []}
    lo = T.NFEAT + 8
    for n, src in enumerate(record["admitted"]):
        path = src["local_path"]
        if T.sha256_file(path) != src["sha256"]:
            raise RuntimeError("source drifted: %s" % src["source_id"])
        bits = T.bits_from_file(path, need)
        Xtr, Ytr, Xev, Yev = T.u_split(bits)
        ub = lo + T.K_SEQ * (T.T_TRAIN + T.T_EVAL)
        entry = {"source_id": src["source_id"], "bytes": src["bytes"],
                 "U_train": label_stats(bits, list(range(ub, ub + T.T_TRAIN)), lambda z: T.xor_at(bits, z, T.UOFF)),
                 "U_eval": label_stats(bits, list(range(ub + T.T_TRAIN, ub + T.T_TRAIN + T.T_EVAL)),
                                       lambda z: T.xor_at(bits, z, T.UOFF)),
                 "input_bit_means_U_train": [str(Fraction(int(round(m * T.T_TRAIN)), T.T_TRAIN))
                                             for m in Xtr.mean(dim=0).tolist()],
                 "fraction_ascii_msb_zero": str(Fraction(sum(1 for b in bits[::8] if b == 0), len(bits[::8]))),
                 "families": {}}
        crit = T.T_EVAL - (T.T_EVAL // T.THETA_DEN)
        entry["U_eval_majority_class_correct"] = max(entry["U_eval"]["ones"], T.T_EVAL - entry["U_eval"]["ones"])
        entry["U_eval_majority_meets_criterion"] = entry["U_eval_majority_class_correct"] >= crit
        for fam, seq, sid in (("POS", T.POS_SEQ, "T%02d" % (21 + n)), ("NEG", T.NEG_SEQ, "T%02d" % (31 + n))):
            n_sid = int(sid[1:])
            tasks = []
            for j, offs in enumerate(seq):
                base = lo + j * (T.T_TRAIN + T.T_EVAL)
                tasks.append({"offsets": list(offs),
                              "train": label_stats(bits, list(range(base, base + T.T_TRAIN)),
                                                   lambda z, o=offs: T.xor_at(bits, z, o))})
            net = sequence_body(bits, n_sid, seq)
            hist = body_stats(net, Xtr)
            # Fresh baseline bodies: the first three proposal seeds of law(False, .).
            fresh = []
            for i in range(3):
                seed = 5000 + 31 * i + n_sid
                torch.manual_seed(seed)
                c = T.Net()
                fresh.append(body_stats(c, Xtr)["live_units"])
            entry["families"][fam] = {"sequence_id": sid, "sequence_tasks": tasks,
                                      "history_body_on_U_train": hist,
                                      "fresh_body_live_units_first_3_seeds": fresh}
        out["sources"].append(entry)
        print(src["source_id"], "POS live", entry["families"]["POS"]["history_body_on_U_train"]["live_units"],
              "zero_rows", entry["families"]["POS"]["history_body_on_U_train"]["all_zero_activation_rows"],
              "| NEG live", entry["families"]["NEG"]["history_body_on_U_train"]["live_units"],
              "zero_rows", entry["families"]["NEG"]["history_body_on_U_train"]["all_zero_activation_rows"],
              "| U mean", entry["U_train"]["mean"], flush=True)
    with open(os.path.join(HERE, "L4_DIAGNOSIS_V1.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
