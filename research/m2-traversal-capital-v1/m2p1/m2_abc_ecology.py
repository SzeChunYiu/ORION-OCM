#!/usr/bin/env python3
"""A -> B -> C lifetime for the developmental-capital (C3 / K2) test.

A from a seed; B = the complement of A's length-2 motifs (disjoint); C = 4 of A's motifs + 4 of
B's -- a RECOMBINATION regime: every C motif has been met before, in different company. Every
normal form that is a member of A or of B is removed from C's stream, so each C target mixes the
two earlier regimes and none was seen before. Development happens on A only; the protected
stream is A[:n] + B[:n] + C[:n] (C drawn from all of C's streams, since C is never developed on).
"""
import argparse, json, random, subprocess, sys
from itertools import product
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--gen", required=True, help="path to m2p1_ecology_e4.py")
ap.add_argument("--n", type=int, default=45)
ap.add_argument("--split", default="0.2,0.1,0.7")
ap.add_argument("--seed-a", type=int, default=601)
a = ap.parse_args()
py = sys.executable
COMMON = ["--min-canonical-len", "6", "--max-canonical-len", "6", "--max-tokens", "3",
          "--split", a.split, "--min-targets", "900", "--trials", "1"]


def gen(extra, out):
    subprocess.run([py, a.gen, "--repo", a.repo, "--out", out, *extra, *COMMON], check=True, capture_output=True)
    return json.loads(Path(out).read_text())


tag = f"{a.seed_a}_{Path(a.out).stem}"
A = gen(["--seed", str(a.seed_a), "--motifs", "8", "--motif-min-len", "2", "--motif-max-len", "2"], f"/tmp/abcA_{tag}.json")
mA = sorted(tuple(m) for m in A["hidden_motifs"])
prims = ("inc", "dec", "double", "square")
compB = [list(m) for m in product(prims, repeat=2) if m not in set(mA)]
Path(f"/tmp/abcB_motifs_{tag}.json").write_text(json.dumps({"fragments": compB}))
B = gen(["--motif-file", f"/tmp/abcB_motifs_{tag}.json"], f"/tmp/abcB_{tag}.json")
mB = sorted(tuple(m) for m in B["hidden_motifs"])
assert not (set(mA) & set(mB)), "A and B must be disjoint"
rng = random.Random(a.seed_a + 99)
fromA, fromB = sorted(rng.sample(mA, 4)), sorted(rng.sample(mB, 4))
mC = fromA + fromB
Path(f"/tmp/abcC_motifs_{tag}.json").write_text(json.dumps({"fragments": [list(m) for m in mC]}))
C = gen(["--motif-file", f"/tmp/abcC_motifs_{tag}.json"], f"/tmp/abcC_{tag}.json")
seen = {r["normal_form_digest"] for E in (A, B) for st in E["streams"].values() for r in st}
poolC = [r for st in ("protected", "train", "validation") for r in C["streams"][st] if r["normal_form_digest"] not in seen]
n = a.n
protA, protB = A["streams"]["protected"], B["streams"]["protected"]
if len(protA) < n or len(protB) < n or len(poolC) < n:
    raise SystemExit(f"too small A={len(protA)} B={len(protB)} C_new={len(poolC)}")
for r in protA[:n]: r["segment"] = "A"
for r in protB[:n]: r["segment"] = "B"
for r in poolC[:n]: r["segment"] = "C"
E = dict(A)
E["ecology_variant"] = {"label": "SHIFT_ABC_RECOMBINATION", "n_per_segment": n, "seed_A": a.seed_a, "split": a.split,
                        "C_from_A": [list(m) for m in fromA], "C_from_B": [list(m) for m in fromB],
                        "C_members_total": sum(len(v) for v in C["streams"].values()), "C_members_new": len(poolC)}
E["hidden_motifs_B"] = [list(m) for m in mB]
E["hidden_motifs_C"] = [list(m) for m in mC]
E["streams"] = {"train": A["streams"]["train"], "validation": A["streams"]["validation"],
                "protected": protA[:n] + protB[:n] + poolC[:n]}
E["stream_sizes"] = {k: len(v) for k, v in E["streams"].items()}
Path(a.out).write_text(json.dumps(E, indent=1, sort_keys=True))
print(json.dumps({"A": ["".join(m) for m in mA], "B": ["".join(m) for m in mB], "C": ["".join(m) for m in mC],
                  "sizes": E["stream_sizes"], "C_new": len(poolC)}, indent=1))
