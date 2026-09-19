#!/usr/bin/env python3
"""Corpus producer for gmi-833-ae-instruments-v1 (FREEZE_V1.md, Instruments I and IV).

Runs on the registered host. stdlib only. Created AFTER the freeze commit
dd9b34cef55ef13d144eb5a9258fbd515c55cd06 and the register commit
527f326ec342a3d3041880c63edc84a2cc46984f. Produces only REAL_RUNS artifacts
plus a laptop-local stream cache consumed by the torch producer.

Usage: python3 -I -B produce_corpus_v1.py <pkg_dir> <cache_dir> [C1 C2 ...]

Every source digest is verified against PROSPECTIVE_REGISTER_V1.json before
any byte of it is used; a mismatch is a hard refusal.
"""
import gzip
import hashlib
import io
import json
import os
import random
import sys
import urllib.request
import zipfile
from fractions import Fraction

FREEZE_COMMIT = "dd9b34cef55ef13d144eb5a9258fbd515c55cd06"
REGISTER_COMMIT = "527f326ec342a3d3041880c63edc84a2cc46984f"
AMENDMENT_COMMIT = "212b989bd3e1b632bf256d61eab5139527089ae5"
SKLEARN_DATA = os.path.expanduser("~/.local/lib/python3.8/site-packages/sklearn/datasets/data")
LADDER_M = [16, 64, 256, 1024, 4096]
CLASS_LADDER_M = [64, 256, 1024, 4096, 16384, 65536]
TIE_ORDER = ["local1", "local2", "local4", "shared_comp", "full"]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def fr(x):
    return "%d/%d" % (x.numerator, x.denominator)


def fetch(url, dest):
    if not os.path.exists(dest):
        req = urllib.request.Request(url, headers={"User-Agent": "gmi-833-ae-instruments-v1"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            f.write(r.read())
    with open(dest, "rb") as f:
        return f.read()


def read_file(path):
    with open(path, "rb") as f:
        return f.read()


def require(cond, msg):
    if not cond:
        raise SystemExit("REFUSED: " + msg)


# ----------------------------------------------------------------- extractors

def extract(entry, cache_dir):
    name = entry["name"]
    src = entry["source"]
    ex = entry["extractor"]
    if ex == "raw":
        if src.startswith("http"):
            raw = fetch(src, os.path.join(cache_dir, name + ".src"))
        else:
            raw = read_file(src)
        require(sha256_bytes(raw) == entry["sha256"], "digest mismatch for " + name)
        return raw, {"source_sha256": sha256_bytes(raw)}
    if ex == "raw_concat":
        parts = src.split("+")
        blobs = [read_file(p) for p in parts]
        digs = [sha256_bytes(b) for b in blobs]
        require(digs == entry["member_sha256"], "member digest mismatch for " + name)
        return b"".join(blobs), {"member_sha256": digs}
    if ex == "digits_pixels":
        raw = read_file(os.path.join(SKLEARN_DATA, "digits.csv.gz"))
        require(sha256_bytes(raw) == entry["sha256"], "digest mismatch for " + name)
        text = gzip.decompress(raw).decode("ascii")
        lines = text.split("\n")[1:]
        out = bytearray()
        rows = 0
        for ln in lines:
            if not ln.strip():
                continue
            vals = ln.split(",")[:64]
            require(len(vals) == 64, "digits row shape")
            for v in vals:
                iv = int(v)
                require(0 <= iv <= 16, "digits pixel range")
                out.append(iv)
            rows += 1
        return bytes(out), {"source_sha256": sha256_bytes(raw), "rows": rows}
    if ex == "jpeg_grey_raster":
        raw = read_file(src)
        require(sha256_bytes(raw) == entry["sha256"], "digest mismatch for " + name)
        from PIL import Image  # decoder only
        im = Image.open(io.BytesIO(raw)).convert("L")
        w, h = im.size
        return im.tobytes(), {"source_sha256": sha256_bytes(raw), "width": w, "height": h}
    if ex == "robot_steps":
        raw = fetch(src, os.path.join(cache_dir, name + ".zip"))
        require(sha256_bytes(raw) == entry["sha256"], "digest mismatch for " + name + " zip")
        member = zipfile.ZipFile(io.BytesIO(raw)).read(entry["member"])
        require(sha256_bytes(member) == entry["member_sha256"], "member digest mismatch for " + name)
        cmd = {"Move-Forward": 0, "Slight-Right-Turn": 1, "Sharp-Right-Turn": 2, "Slight-Left-Turn": 3}
        out = bytearray()
        steps = 0
        for ln in member.decode("ascii").replace("\r", "").split("\n"):
            if not ln.strip():
                continue
            f = ln.split(",")
            require(len(f) == 25, "robot row shape")
            for v in f[:24]:
                # floor(51 * v) on the decimal string, exactly
                q = Fraction(v)
                b = int(51 * q)  # floor for non-negative
                out.append(min(255, b))
            out.append(cmd[f[24].strip()])
            steps += 1
        return bytes(out), {"source_sha256": sha256_bytes(raw), "member_sha256": sha256_bytes(member), "steps": steps}
    if ex == "cancer_rows":
        raw = read_file(os.path.join(SKLEARN_DATA, "breast_cancer.csv"))
        require(sha256_bytes(raw) == entry["sha256"], "digest mismatch for " + name)
        lines = [ln for ln in raw.decode("ascii").split("\n")[1:] if ln.strip()]
        rows = []
        for ln in lines:
            f = ln.split(",")
            require(len(f) == 31, "cancer row shape")
            rows.append(([Fraction(v) for v in f[:30]], int(f[30])))
        mins = [min(r[0][j] for r in rows) for j in range(30)]
        maxs = [max(r[0][j] for r in rows) for j in range(30)]
        out = bytearray()
        for feats, lab in rows:
            for j in range(30):
                span = maxs[j] - mins[j]
                b = int(255 * (feats[j] - mins[j]) / span) if span else 0
                out.append(b)
            out.append(lab)
        return bytes(out), {"source_sha256": sha256_bytes(raw), "cases": len(rows)}
    if ex == "wav_payload_44":
        raw = read_file(src)
        require(sha256_bytes(raw) == entry["sha256"], "digest mismatch for " + name)
        return raw[44:], {"source_sha256": sha256_bytes(raw)}
    raise SystemExit("unknown extractor " + ex)


def bits_msb(data, T):
    out = []
    for byte in data:
        for i in range(7, -1, -1):
            out.append((byte >> i) & 1)
            if len(out) == T:
                return out
    raise SystemExit("REFUSED: stream too short (%d bits < %d)" % (len(out), T))


def bits_to_hex(bits):
    n = len(bits)
    out = bytearray()
    for i in range(0, n, 8):
        v = 0
        for j in range(8):
            v = (v << 1) | (bits[i + j] if i + j < n else 0)
        out.append(v)
    return out.hex()


# ----------------------------------------------------------- structure measures

def bigram(bits):
    c = [[0, 0], [0, 0]]
    for t in range(1, len(bits)):
        c[bits[t - 1]][bits[t]] += 1
    return c


def floors_from_bigram(c):
    N = sum(c[a][b] for a in range(2) for b in range(2))
    e0 = Fraction(N - sum(max(c[0][b], c[1][b]) for b in range(2)), N)
    e00 = Fraction(N - max(sum(c[0]), sum(c[1])), N)
    e0_rev = Fraction(N - sum(max(c[a][0], c[a][1]) for a in range(2)), N)
    e00_rev = Fraction(N - max(c[0][0] + c[1][0], c[0][1] + c[1][1]), N)
    return N, e0, e00, e0_rev, e00_rev


def context_floors(bits, ks=(1, 2, 4, 8)):
    """E_k over train positions t >= 8 (common position set for every k)."""
    out = {}
    N = len(bits) - 8
    for k in ks:
        counts = {}
        for t in range(8, len(bits)):
            ctx = 0
            for j in range(t - k, t):
                ctx = (ctx << 1) | bits[j]
            key = (ctx, bits[t])
            counts[key] = counts.get(key, 0) + 1
        per = {}
        for (ctx, v), n in counts.items():
            per.setdefault(ctx, [0, 0])[v] += n
        out[k] = Fraction(N - sum(max(v) for v in per.values()), N)
    return N, out


def measures(train_bits):
    p1 = Fraction(sum(train_bits), len(train_bits))
    c = bigram(train_bits)
    N, e0, e00, e0r, e00r = floors_from_bigram(c)
    Nk, ek = context_floors(train_bits)
    return {
        "n_train": len(train_bits), "p1": fr(p1), "bigram": c, "N_bigram": N,
        "E0": fr(e0), "E00": fr(e00), "G": fr(e00 - e0),
        "E0_rev_predicted": fr(e0r), "E00_rev_predicted": fr(e00r),
        "N_context": Nk, "E_k": {str(k): fr(v) for k, v in ek.items()},
        "DELTA_k": {str(k): fr(ek[k] - ek[8]) for k in (1, 2, 4)},
        "in_band": bool(Fraction(1, 8) < e0 < Fraction(3, 8)),
    }


# ------------------------------------------------------------ Instrument IV

def windows(bits):
    ws, ys = [], []
    for t in range(7, len(bits) - 1):
        w = 0
        for j in range(t - 7, t + 1):
            w = (w << 1) | bits[j]
        ws.append(w)
        ys.append(bits[t + 1])
    return ws, ys


def gf2_affine_dim(points):
    pts = sorted(set(points))
    if not pts:
        return 0
    base = pts[0]
    basis = []  # reduced basis by leading bit (insertion method)
    for p in pts[1:]:
        v = p ^ base
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)


def rev8(w):
    return int("{:08b}".format(w)[::-1], 2)


def tv(counts_a, N_a, counts_b, N_b):
    keys = set(counts_a) | set(counts_b)
    s = Fraction(0)
    for k in keys:
        s += abs(Fraction(counts_a.get(k, 0), N_a) - Fraction(counts_b.get(k, 0), N_b))
    return s / 2


def orbit_estimator(ws):
    N = len(ws)
    n = {}
    for w in ws:
        n[w] = n.get(w, 0) + 1
    half = N // 2
    n1, n2 = {}, {}
    for w in ws[:half]:
        n1[w] = n1.get(w, 0) + 1
    for w in ws[half:]:
        n2[w] = n2.get(w, 0) + 1
    tv_split = tv(n1, half, n2, N - half)
    g = {"rev": rev8, "comp": lambda w: w ^ 0xFF, "revcomp": lambda w: rev8(w) ^ 0xFF}
    out = {"N_windows": N, "TV_split": fr(tv_split), "TV": {}, "INVARIANT": {}}
    for name, fn in g.items():
        ng = {}
        for w, c in n.items():
            ng[fn(w)] = ng.get(fn(w), 0) + c
        t = tv(n, N, ng, N)
        out["TV"][name] = fr(t)
        out["INVARIANT"][name] = bool(t <= tv_split)
    return out


def cell_of(cls, w):
    if cls == "local1":
        return w & 1
    if cls == "local2":
        return w & 3
    if cls == "local4":
        return w & 15
    if cls == "shared_comp":
        return min(w, w ^ 0xFF)
    return w


def class_errors(ws_tr, ys_tr, ws_ev, ys_ev, m):
    m = min(m, len(ws_tr))
    n1 = sum(ys_tr[:m])
    prefix_major = 1 if n1 > m - n1 else 0
    out = {}
    for cls in TIE_ORDER:
        tab = {}
        for w, y in zip(ws_tr[:m], ys_tr[:m]):
            tab.setdefault(cell_of(cls, w), [0, 0])[y] += 1
        wrong = 0
        for w, y in zip(ws_ev, ys_ev):
            c = tab.get(cell_of(cls, w))
            pred = prefix_major if c is None else (1 if c[1] > c[0] else 0)
            wrong += (pred != y)
        out[cls] = {"wrong": wrong, "N": len(ws_ev), "error": fr(Fraction(wrong, len(ws_ev)))}
    return out, m


def instrument_iv(train_bits, eval_bits):
    ws_tr, ys_tr = windows(train_bits)
    ws_ev, ys_ev = windows(eval_bits)
    dims = {}
    for m in LADDER_M + ["ALL"]:
        mm = len(ws_tr) if m == "ALL" else m
        pts = ws_tr[:mm]
        dims[str(m)] = {"DIM_AFF": gf2_affine_dim(pts), "SUPPORT": fr(Fraction(len(set(pts)), 256)), "m": mm}
    final = dims["ALL"]["DIM_AFF"]
    m_sat = next(k for k in [str(x) for x in LADDER_M] + ["ALL"] if dims[k]["DIM_AFF"] == final)
    ladder = {}
    for m in CLASS_LADDER_M + ["ALL"]:
        mm = len(ws_tr) if m == "ALL" else m
        errs, used = class_errors(ws_tr, ys_tr, ws_ev, ys_ev, mm)
        best = min(TIE_ORDER, key=lambda c: (Fraction(errs[c]["error"]), TIE_ORDER.index(c)))
        ladder[str(m)] = {"m_used": used, "errors": errs, "selected": best}
    return {"N_train_windows": len(ws_tr), "N_eval_windows": len(ws_ev),
            "DIM_AFF_ladder": dims, "DIM_AFF_final": final, "m_sat": m_sat,
            "orbit": orbit_estimator(ws_tr), "class_ladder": ladder}


# ------------------------------------------------------------------- main

def build_dataset(entry, cache_dir, out_dir):
    c = int(entry["id"][1:])
    seed = 1000 + 100 * c
    data, meta = extract(entry, cache_dir)
    T = entry["T"]
    bits = bits_msb(data, T)
    ntr = 3 * T // 4
    train, ev = bits[:ntr], bits[ntr:]
    rng = random.Random(seed)
    modes = [rng.getrandbits(1) for _ in range(T)]
    rec = {"schema": "GMI_833_AE_INSTRUMENTS_CORPUS_RECORD_V1", "id": entry["id"], "name": entry["name"],
           "domain": entry["domain"], "freeze_commit": FREEZE_COMMIT, "register_commit": REGISTER_COMMIT,
           "amendment_commit": AMENDMENT_COMMIT, "seed": seed, "T": T, "n_train": ntr, "n_eval": T - ntr, "extract_meta": meta,
           "stream_sha256": sha256_bytes(bytes(data[:(T + 7) // 8])),
           "stream_bytes_available": len(data),
           "train_bits_sha256": sha256_bytes(bytes(train)), "eval_bits_sha256": sha256_bytes(bytes(ev)),
           "train_bits_hex": bits_to_hex(train),
           "eval_bits_hex": bits_to_hex(ev), "eval_mode_hex": bits_to_hex(modes[ntr:]),
           "realized_eta_eval": fr(Fraction(sum(modes[ntr:]), T - ntr)),
           "realized_eta_train": fr(Fraction(sum(modes[:ntr]), ntr)),
           "variants": {}}
    # base
    rec["variants"]["base"] = measures(train)
    # bit shuffle
    r3 = random.Random(seed + 3)
    tr_s = list(train); r3.shuffle(tr_s)
    ev_s = list(ev); r3.shuffle(ev_s)
    rec["variants"]["bitshuf"] = measures(tr_s)
    rec["variants"]["bitshuf"]["eval_bits_hex"] = bits_to_hex(ev_s)
    rec["variants"]["bitshuf"]["train_bits_sha256"] = sha256_bytes(bytes(tr_s))
    # byte shuffle (bytes of the bit stream; T multiple of 8)
    r5 = random.Random(seed + 5)
    tr_bytes = [train[i:i + 8] for i in range(0, ntr, 8)]
    ev_bytes = [ev[i:i + 8] for i in range(0, T - ntr, 8)]
    r5.shuffle(tr_bytes); r5.shuffle(ev_bytes)
    tr_b = [b for chunk in tr_bytes for b in chunk]
    rec["variants"]["byteshuf"] = measures(tr_b)
    # complement
    rec["variants"]["complement"] = measures([1 - b for b in train])
    # reversal
    rec["variants"]["reversal"] = measures(train[::-1])
    # probe for Instrument II: first 2048 eval positions
    P = 2048
    xprev = [train[-1]] + ev[:P - 1]
    rec["probe"] = {"n": P, "x_prev_hex": bits_to_hex(xprev), "x_hex": bits_to_hex(ev[:P]),
                    "mode_hex": bits_to_hex(modes[ntr:ntr + P]),
                    "n_delayed": sum(modes[ntr:ntr + P]), "warmup_positions": 4096}
    # Instrument IV
    rec["instrument_iv"] = instrument_iv(train, ev)
    if entry["id"] == "C1":
        tr2 = train + [1 - b for b in train]
        ev2 = ev + [1 - b for b in ev]
        rec["instrument_iv_symcomp"] = instrument_iv(tr2, ev2)
    d = os.path.join(out_dir, entry["id"])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "corpus.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    # laptop-local cache for the torch producer (not committed)
    cache = {"id": entry["id"], "seed": seed, "T": T, "n_train": ntr,
             "bits": {"base": bits_to_hex(bits), "bitshuf": bits_to_hex(tr_s + ev_s),
                      "complement": bits_to_hex([1 - b for b in bits]),
                      "reversal": bits_to_hex(train[::-1] + ev[::-1])},
             "modes": bits_to_hex(modes)}
    with open(os.path.join(cache_dir, entry["id"] + "_streams.json"), "w") as f:
        json.dump(cache, f)
    print(entry["id"], entry["name"], "E0", rec["variants"]["base"]["E0"], "E00", rec["variants"]["base"]["E00"],
          "in_band", rec["variants"]["base"]["in_band"], "DIM_AFF", rec["instrument_iv"]["DIM_AFF_final"])


def main():
    pkg, cache_dir = sys.argv[1], sys.argv[2]
    only = sys.argv[3:]
    os.makedirs(cache_dir, exist_ok=True)
    with open(os.path.join(pkg, "PROSPECTIVE_REGISTER_V1.json")) as f:
        reg = json.load(f)
    out_dir = os.path.join(pkg, "REAL_RUNS")
    for entry in reg["corpus"]:
        if only and entry["id"] not in only:
            continue
        build_dataset(entry, cache_dir, out_dir)


if __name__ == "__main__":
    main()
