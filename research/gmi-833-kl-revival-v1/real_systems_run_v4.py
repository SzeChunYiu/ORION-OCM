"""Train and externally evaluate the 32 registered SIGMA_REAL4 systems (torch, CPU).

Runs on laptop-billy only, strictly AFTER commit 2a (the frozen set-valued
prediction stream).  The parent's protocol is reused byte-for-byte: same source,
word length, windows, optimizer, epochs, batch, threads, seed rule and the
99/100 band; only the widths differ (6 and 48).  Nothing here can see a
prediction: the bridge lives in ``heldout_universes_real4_v1`` and is compared
to these measurements only by the scorer.

Writes ``REAL_RUNS_V4/REAL_MEASURED_V4.json``.
"""

from fractions import Fraction
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL_PKG = os.path.join(os.path.dirname(HERE), "gmi-833-capability-predictor-evaluation-v1")
for p in (HERE, EVAL_PKG):
    if p not in sys.path:
        sys.path.insert(0, p)

import heldout_universes_v1 as hu  # noqa: E402
import heldout_universes_real4_v1 as r4  # noqa: E402

OUT_DIR = os.path.join(HERE, "REAL_RUNS_V4")


def load_bits():
    path = hu.REAL_SOURCE["path"]
    with open(path, "rb") as handle:
        data = handle.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != hu.REAL_SOURCE["sha256"]:
        raise ValueError("pinned source sha256 mismatch: %s" % digest)
    if len(data) != hu.REAL_SOURCE["bytes"]:
        raise ValueError("pinned source size mismatch: %d" % len(data))
    return [b & 1 for b in data], digest


def windows(bits, lo, hi):
    length = hu.REAL_WORD_LEN
    out = []
    for i in range(lo, hi):
        chunk = bits[i * length:(i + 1) * length]
        if len(chunk) < length:
            break
        out.append(tuple(chunk))
    return out


def targets(word, task_index):
    if task_index == 0:
        return word[-1]
    if task_index == 1:
        return sum(word) % 2
    return 1 if sum(word) % 3 == 0 else 0


def build_model(torch, nn, mech, size, w):
    class MLP(nn.Module):
        def __init__(self):
            super(MLP, self).__init__()
            self.body = nn.Sequential(nn.Linear(hu.REAL_WORD_LEN, size), nn.Tanh())
            self.head = nn.Linear(size + w, 1)

        def forward(self, x):
            z = self.body(x)
            if w:
                z = torch.cat([z, x[:, -1:]], dim=1)
            return self.head(z).squeeze(1)

    class GRUNet(nn.Module):
        def __init__(self):
            super(GRUNet, self).__init__()
            self.rnn = nn.GRU(1, size, batch_first=True)
            self.head = nn.Linear(size + w, 1)

        def forward(self, x):
            seq = x.unsqueeze(2)
            _out, hidden = self.rnn(seq)
            z = hidden[-1]
            if w:
                z = torch.cat([z, x[:, -1:]], dim=1)
            return self.head(z).squeeze(1)

    return MLP() if mech == "MLP" else GRUNet()


def exact_accuracy(torch, model, xs, ys):
    with torch.no_grad():
        logits = model(xs)
        pred = (logits > 0).long()
    correct = int((pred == ys.long()).sum().item())
    return Fraction(correct, int(ys.shape[0]))


def main():
    import torch
    import torch.nn as nn
    torch.set_num_threads(hu.REAL_TRAINING["threads"])
    bits, digest = load_bits()
    train_words = windows(bits, *hu.REAL_TRAIN_WINDOWS)
    eval_words = windows(bits, *hu.REAL_EVAL_WINDOWS)
    if not train_words or not eval_words:
        raise ValueError("empty protected battery")
    xs_tr = torch.tensor([[float(b) for b in w] for w in train_words])
    xs_ev = torch.tensor([[float(b) for b in w] for w in eval_words])

    trained = {}
    untrained = {}
    accs = {}
    mech_index = {"MLP": 0, "GRU": 1}
    epochs = hu.REAL_TRAINING["epochs"]
    batch = hu.REAL_TRAINING["batch"]
    lr = float(Fraction(hu.REAL_TRAINING["lr"]))
    for mech in r4.REAL4_MECHS:
        for size in r4.REAL4_SIZES:
            for w in (0, 1):
                for task_index in range(3):
                    seed = 8317 + 101 * mech_index[mech] + 17 * size + 3 * w + task_index
                    ys_tr = torch.tensor([float(targets(x, task_index)) for x in train_words])
                    ys_ev = torch.tensor([float(targets(x, task_index)) for x in eval_words])
                    torch.manual_seed(seed)
                    model = build_model(torch, nn, mech, size, w)
                    key = "%s|%d|%d|%d" % (mech, size, w, task_index)
                    untrained[key] = str(exact_accuracy(torch, model, xs_ev, ys_ev))
                    opt = torch.optim.Adam(model.parameters(), lr=lr)
                    loss_fn = nn.BCEWithLogitsLoss()
                    count = xs_tr.shape[0]
                    for epoch in range(epochs):
                        perm = torch.randperm(count)
                        for start in range(0, count, batch):
                            sel = perm[start:start + batch]
                            opt.zero_grad()
                            out = model(xs_tr[sel])
                            loss = loss_fn(out, ys_tr[sel])
                            loss.backward()
                            opt.step()
                    acc = exact_accuracy(torch, model, xs_ev, ys_ev)
                    trained[key] = str(acc)
                    accs[key] = {"trained": str(acc), "untrained": untrained[key]}
                    sys.stderr.write("%s trained=%s untrained=%s\n"
                                     % (key, acc, untrained[key]))
                    sys.stderr.flush()

    measured = {}
    for machine in r4.REAL4_MACHINES:
        mech, size, w, h = machine
        bitset = 0
        for task_index in range(3):
            key = "%s|%d|%d|%d" % (mech, size, w, task_index)
            acc = Fraction(trained[key] if (h >> task_index) & 1 else untrained[key])
            if acc >= r4.REAL4_BAND:
                bitset |= 1 << task_index
        measured["|".join(str(x) for x in machine)] = bitset

    payload = {
        "schema": "GMI_833_KL_REVIVAL_REAL_MEASURED_V4",
        "population": "SIGMA_REAL4",
        "freeze_commit": r4.FREEZE_COMMIT,
        "torch_version": torch.__version__,
        "device": "cpu",
        "threads": hu.REAL_TRAINING["threads"],
        "source": dict(hu.REAL_SOURCE),
        "source_sha256_verified": digest,
        "train_items": len(train_words),
        "protected_eval_items": len(eval_words),
        "training": dict(hu.REAL_TRAINING),
        "sizes": list(r4.REAL4_SIZES),
        "per_head_exact_accuracy": dict(sorted(accs.items())),
        "measured_solved_bits": dict(sorted(measured.items())),
        "solved_rule": "exact accuracy >= 99/100 on the protected split (V3 band)",
        "band": str(r4.REAL4_BAND),
    }
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    body = json.dumps(payload, indent=2, sort_keys=True)
    with open(os.path.join(OUT_DIR, "REAL_MEASURED_V4.json"), "w") as handle:
        handle.write(body)
        handle.write("\n")
    sys.stderr.write("receipt sha256 %s\n"
                     % hashlib.sha256((body + "\n").encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
