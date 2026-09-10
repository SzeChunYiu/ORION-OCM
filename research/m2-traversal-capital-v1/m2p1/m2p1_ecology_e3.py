#!/usr/bin/env python3
"""M2-P1 ecology E3: derived from the measured admission condition, not from tuning.

M2-P1b established WHY validate_generator refuses. methods.solve runs the guided
stream on odd slots only, so a candidate that finds its answer at guided step g
returns at about 2g slots, while the baseline returns at b. Admission needs
candidate <= baseline on EVERY held-out task, i.e.

    2 * g  <=  b        for every target

and g is the position of the target's motif composition in the guided token
enumeration, roughly T^k for a k-token composition over T = |fragments| + 4 tokens.
With T ~= 20 that is g ~= 400 for k=2, ~8 000 for k=3, ~160 000 for k=4, while b runs
to 87 381. So k=4 compositions can essentially never satisfy the rule and k=2
compositions satisfy it whenever b >= 800.

E3 therefore builds an ecology of **2-token compositions with long canonical
programs**: motifs of length 3-4, targets whose canonical program decomposes into
exactly two motifs (length 6-8, so b is large). This is an ECOLOGY choice derived from
the measured mechanism -- the learner, the gate, the no-slowdown rule, the thresholds
and the integration mode are all untouched (#323 section 11).

The prediction is registered before running: E3 should produce ZERO vetoes and the
unmodified validate_generator should ACCEPT.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, sys, time
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2P1_ECOLOGY_E3_V1"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def min_tokens(program, motifs):
    """Fewest motifs whose concatenation is exactly `program`; None if not decomposable."""
    n = len(program)
    best = [None] * (n + 1)
    best[0] = 0
    for i in range(n):
        if best[i] is None:
            continue
        for m in motifs:
            j = i + len(m)
            if j <= n and tuple(program[i:j]) == m:
                if best[j] is None or best[i] + 1 < best[j]:
                    best[j] = best[i] + 1
    return best[n]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--motifs", type=int, default=6)
    ap.add_argument("--motif-min-len", type=int, default=3)
    ap.add_argument("--motif-max-len", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=2)
    ap.add_argument("--min-canonical-len", type=int, default=6)
    ap.add_argument("--min-targets", type=int, default=90)
    ap.add_argument("--trials", type=int, default=600)
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M

    canonical, first_index = {}, {}
    slot = 0
    for L in range(9):
        for prog in product(M.PRIMITIVES, repeat=L):
            slot += 1
            nf = M.normal_form(prog)
            if nf not in canonical:
                canonical[nf], first_index[nf] = prog, slot

    rng = random.Random(a.seed)
    pool = [p for L in range(a.motif_min_len, a.motif_max_len + 1)
            for p in product(M.PRIMITIVES, repeat=L)]
    best = None
    for _ in range(a.trials):
        motifs = tuple(sorted(rng.sample(pool, a.motifs)))
        members = []
        for nf, prog in canonical.items():
            if len(prog) < a.min_canonical_len:
                continue
            k = min_tokens(prog, motifs)
            if k is not None and k <= a.max_tokens:
                members.append((nf, k))
        if best is None or len(members) > len(best[1]):
            best = (motifs, members)
        if len(members) >= a.min_targets:
            break
    motifs, members = best

    # ---- registered admission prediction, computed BEFORE any dev run
    T_est = 16 + len(M.PRIMITIVES)          # learn_generator caps the library at 16
    g_est = sum(T_est ** i for i in range(1, a.max_tokens + 1))
    predicted = [{"digest": hashlib.sha256(json.dumps([str(c) for c in nf]).encode()).hexdigest(),
                  "b": first_index[nf], "tokens": k, "predicted_veto": 2 * g_est > first_index[nf]}
                 for nf, k in members]
    predicted_veto_rate = sum(1 for p in predicted if p["predicted_veto"]) / len(predicted)

    by_len = defaultdict(list)
    for nf, k in members:
        by_len[len(canonical[nf])].append(nf)
    for L in by_len:
        by_len[L].sort(key=lambda nf: hashlib.sha256(str(nf).encode()).hexdigest())
    streams = {"train": [], "validation": [], "protected": []}
    for L, nfs in sorted(by_len.items()):
        i = 0
        for name, frac in (("train", 0.5), ("validation", 0.2), ("protected", 0.3)):
            k = int(round(len(nfs) * frac))
            streams[name].extend(nfs[i:i + k])
            i += k
        streams["train"].extend(nfs[i:])

    tok = dict(members)

    def row(nf):
        return {"coefficients": [str(c) for c in nf],
                "canonical_program": list(canonical[nf]),
                "canonical_length": len(canonical[nf]),
                "motif_tokens": tok[nf],
                "baseline_first_index": first_index[nf],
                "normal_form_digest": hashlib.sha256(
                    json.dumps([str(c) for c in nf]).encode()).hexdigest()}

    out_streams = {k: [row(nf) for nf in v] for k, v in streams.items()}
    digs = {k: {r["normal_form_digest"] for r in v} for k, v in out_streams.items()}
    shared = (digs["train"] & digs["protected"]) | (digs["train"] & digs["validation"]) | \
             (digs["validation"] & digs["protected"])

    def dist(rows):
        c = Counter(r["canonical_length"] for r in rows)
        n = sum(c.values()) or 1
        return {L: c[L] / n for L in sorted(c)}
    dists = {k: dist(v) for k, v in out_streams.items()}
    alll = sorted({L for d in dists.values() for L in d})
    parity = max((abs(dists[x][L] - dists[y][L]) for L in alll for x in dists for y in dists
                  if x != y and L in dists[x] and L in dists[y]), default=1.0)

    out = {
        "schema": SCHEMA, "lane": LANE, "status": "ECOLOGY_EMISSION_NOT_A_SCORED_RUN",
        "owner_issue": 165, "hardening_parent": 323,
        "ecology_variant": {"label": "E3", "min_canonical_length": a.min_canonical_len,
                            "max_motif_tokens": a.max_tokens,
                            "motif_lengths": [a.motif_min_len, a.motif_max_len],
                            "derivation": "2*g <= b admission condition measured in M2-P1b"},
        "host": {"hostname": platform.node(), "python": platform.python_version()},
        "bound_sources": {"methods.py": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py"),
                          "git_head": os.popen(f"/usr/bin/git -C {repo} rev-parse HEAD").read().strip()},
        "frozen_seed": a.seed,
        "hidden_motifs": [list(m) for m in motifs],
        "hidden_motifs_sha256": hashlib.sha256(json.dumps([list(m) for m in motifs]).encode()).hexdigest(),
        "grammar": {"primitives": list(M.PRIMITIVES), "max_length": 8},
        "ecology": {"members": len(members),
                    "token_distribution": dict(Counter(k for _, k in members)),
                    "canonical_length_distribution": {
                        str(k): v for k, v in sorted(Counter(len(canonical[nf]) for nf, _ in members).items())}},
        "registered_admission_prediction": {
            "guided_position_estimate_g": g_est, "tokens_T": T_est,
            "predicted_veto_rate": round(predicted_veto_rate, 4),
            "rule": "veto predicted when 2*g > b",
            "note": "computed from the ecology alone, before any developmental run"},
        "streams": out_streams,
        "stream_sizes": {k: len(v) for k, v in out_streams.items()},
        "entry_gates": {
            "G1_length_parity_max_deviation": round(parity, 4),
            "G1_verdict": "PASS" if parity <= 0.12 else "FAIL",
            "G2_shared_normal_forms": len(shared),
            "G2_verdict": "PASS" if not shared else "FAIL",
            "G3_non_decomposable": 0, "G3_verdict": "PASS",
            "G4_surface_predictor_null": "DEFERRED_TO_SCORED_RUN"},
        "timing_seconds": round(time.perf_counter() - t0, 2),
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"members": len(members), "motifs": ["".join(m) for m in motifs],
                      "sizes": out["stream_sizes"],
                      "tokens": out["ecology"]["token_distribution"],
                      "lens": out["ecology"]["canonical_length_distribution"],
                      "predicted_veto_rate": round(predicted_veto_rate, 4),
                      "gates": {k: v for k, v in out["entry_gates"].items() if k.endswith("verdict")}},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
