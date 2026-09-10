#!/usr/bin/env python3
"""M2-P1 ecology E4: adds the measured LEARNABILITY condition that E3 violated.

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

E3 tested only the admission condition and FAILED: admit=False, 10/29 better, 14.7%
WORSE overall. Diagnosis, measured not assumed:

    ecology  motifs        motif-pairs sharing a substring   true motifs recovered
    E1       6 x len 2-3   0                                 6/6
    E3       16 x len 3-4  15                                1/16

learn_generator ranks candidate fragments by (support count DESC, length DESC). If two
motifs share a substring, that substring's count strictly EXCEEDS either motif's, so it
outranks them and the fixed top-16 fills with generic length-2 fragments. The true
motifs are then never in the library, k rises, and 2g <= b fails everywhere.

So the ecology must satisfy BOTH conditions:

    LEARNABILITY  motifs pairwise substring-disjoint (no shared substring of length>=2,
                  and no motif a substring of another) -- then counts TIE and the
                  (length DESC) tiebreak puts the motif above its own substrings
    ADMISSION     2-token compositions with long canonical programs, so 2g <= b

Note the two conditions fight each other: a motif of length L contributes L-1 distinct
length-2 substrings and only 16 length-2 strings exist, so m*(L-1) <= 16. That is why
E3's 16 motifs of length 3-4 could not possibly be disjoint -- the failure was
predictable from the grammar's own combinatorics and is recorded as such.

Registered predictions, computed before the run: ALL motifs recovered by the learner,
and predicted_veto_rate = 0.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, sys, time
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2P1_ECOLOGY_E4_V1"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def proper_substrings(m):
    """All substrings of length >= 2 that are shorter than m itself."""
    return {m[i:j] for i in range(len(m)) for j in range(i + 2, len(m) + 1) if j - i < len(m)}


def substring_disjoint(motifs):
    """No two motifs share a substring of length >= 2, and none contains another.

    This is exactly the condition under which learn_generator's (count DESC, length
    DESC) ranking places a motif ABOVE its own substrings: shared substrings would
    otherwise accumulate strictly higher support and displace the motifs entirely.
    """
    seen = set()
    for m in motifs:
        subs = proper_substrings(m)
        if subs & seen:
            return False
        seen |= subs
    for x in motifs:
        for y in motifs:
            if x is not y and len(x) < len(y):
                if any(y[i:i + len(x)] == x for i in range(len(y) - len(x) + 1)):
                    return False
    return True


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
    ap.add_argument("--max-canonical-len", type=int, default=8,
                    help="E6: cap target length so a constant max-length guess is a WEAK baseline")
    ap.add_argument("--split", default="0.5,0.2,0.3",
                    help="train,validation,protected fractions. A protected-heavy split "
                         "gives the agent a LONGER FUTURE HORIZON on LESS developmental "
                         "data -- harder for the history arm, not easier.")
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
    rejected_non_disjoint = 0
    for _ in range(a.trials):
        motifs = tuple(sorted(rng.sample(pool, a.motifs)))
        if not substring_disjoint(motifs):          # LEARNABILITY condition (E4)
            rejected_non_disjoint += 1
            continue
        members = []
        for nf, prog in canonical.items():
            if not (a.min_canonical_len <= len(prog) <= a.max_canonical_len):
                continue
            k = min_tokens(prog, motifs)
            if k is not None and k <= a.max_tokens:
                members.append((nf, k))
        if best is None or len(members) > len(best[1]):
            best = (motifs, members)
        if len(members) >= a.min_targets:
            break
    if best is None:
        raise SystemExit(f"NO_SUBSTRING_DISJOINT_MOTIF_SET_FOUND after {a.trials} trials "
                         f"(m*(L-1) <= 16 is necessary; try fewer or shorter motifs)")
    motifs, members = best

    # ---- registered admission prediction, computed BEFORE any dev run
    T_est = 16 + len(M.PRIMITIVES)          # learn_generator caps the library at 16
    g_est = sum(T_est ** i for i in range(1, a.max_tokens + 1))
    predicted = [{"digest": hashlib.sha256(json.dumps([str(c) for c in nf]).encode()).hexdigest(),
                  "b": first_index[nf], "tokens": k, "predicted_veto": 2 * g_est > first_index[nf]}
                 for nf, k in members]
    predicted_veto_rate = sum(1 for p in predicted if p["predicted_veto"]) / len(predicted)

    split_fracs = [float(x) for x in a.split.split(",")]
    by_len = defaultdict(list)
    for nf, k in members:
        by_len[len(canonical[nf])].append(nf)
    for L in by_len:
        by_len[L].sort(key=lambda nf: hashlib.sha256(str(nf).encode()).hexdigest())
    streams = {"train": [], "validation": [], "protected": []}
    for L, nfs in sorted(by_len.items()):
        i = 0
        for name, frac in zip(("train", "validation", "protected"), split_fracs):
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
        "ecology_variant": {"label": "E3", "split": a.split, "min_canonical_length": a.min_canonical_len,
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
        "learnability_condition": {
            "motifs_pairwise_substring_disjoint": True,
            "rejected_non_disjoint_samples": rejected_non_disjoint,
            "necessary_bound": "m*(L-1) <= 16 distinct length-2 substrings exist",
            "predicted_true_motifs_recovered": a.motifs,
            "rule": ("learn_generator ranks by (count DESC, length DESC); disjointness "
                     "makes a motif's count TIE its substrings' so the length tiebreak "
                     "puts the motif first")},
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
