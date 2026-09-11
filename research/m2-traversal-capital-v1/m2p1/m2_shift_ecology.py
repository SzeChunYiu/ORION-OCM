#!/usr/bin/env python3
"""Compose a shifted ecology A -> B -> A' from two generated ecologies with DISJOINT motif
sets, so the integrated arm's liveness is exercised inside the runner (not a side script).
Development happens on A only; the protected stream is A[:n] + B[:n] + A[n:2n]."""
import argparse, json, subprocess, sys
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--gen", required=True, help="path to m2p1_ecology_e4.py")
ap.add_argument("--n", type=int, default=40)
ap.add_argument("--seed-a", type=int, default=601)
ap.add_argument("--split", default="0.4,0.15,0.45", help="A and B stream split; a leaner train share leaves more protected members for longer segments")
a = ap.parse_args()
py = sys.executable
def gen(seed, out):
    subprocess.run([py, a.gen, "--repo", a.repo, "--out", out, "--seed", str(seed), "--motifs", "8",
                    "--motif-min-len", "2", "--motif-max-len", "2", "--min-canonical-len", "6",
                    "--max-canonical-len", "6", "--max-tokens", "3", "--split", a.split,
                    "--min-targets", "900", "--trials", "1"], check=True, capture_output=True)
    return json.loads(Path(out).read_text())
A = gen(a.seed_a, "/tmp/shiftA_%d.json" % a.seed_a)
mA = {tuple(m) for m in A["hidden_motifs"]}
# Only 16 length-2 strings exist, so two 8-motif samples are disjoint only if they are
# exact complements. Build B as the COMPLEMENT of A explicitly -- deterministic, disjoint.
from itertools import product as _prod
prims = ("inc", "dec", "double", "square")
comp = [list(m) for m in _prod(prims, repeat=2) if m not in mA]
Path("/tmp/shiftB_motifs.json").write_text(json.dumps({"fragments": comp}))
subprocess.run([py, a.gen, "--repo", a.repo, "--out", "/tmp/shiftB.json", "--motif-file", "/tmp/shiftB_motifs.json",
                "--min-canonical-len", "6", "--max-canonical-len", "6", "--max-tokens", "3",
                "--split", a.split, "--min-targets", "900", "--trials", "1"], check=True, capture_output=True)
B = json.loads(Path("/tmp/shiftB.json").read_text())
mB = {tuple(m) for m in B["hidden_motifs"]}
assert not (mA & mB), "complement construction failed"
s = "complement"
n = a.n
prot = A["streams"]["protected"]; protB = B["streams"]["protected"]
if len(prot) < 2 * n or len(protB) < n:
    raise SystemExit(f"too small A={len(prot)} B={len(protB)}")
for i, r in enumerate(prot[:n]): r["segment"] = "A"
for r in protB[:n]: r["segment"] = "B"
for r in prot[n:2 * n]: r["segment"] = "A_prime"
E = dict(A)
E["ecology_variant"] = {"label": "SHIFT_ABA", "n_per_segment": n, "seed_A": a.seed_a, "seed_B": s, "split": a.split}
E["hidden_motifs_B"] = B["hidden_motifs"]
E["streams"] = {"train": A["streams"]["train"], "validation": A["streams"]["validation"],
                "protected": prot[:n] + protB[:n] + prot[n:2 * n]}
E["stream_sizes"] = {k: len(v) for k, v in E["streams"].items()}
Path(a.out).write_text(json.dumps(E, indent=1, sort_keys=True))
print(json.dumps({"A_motifs": ["".join(m) for m in sorted(mA)], "B_motifs": ["".join(m) for m in sorted(mB)],
                  "sizes": E["stream_sizes"], "seed_B": s}, indent=1))
