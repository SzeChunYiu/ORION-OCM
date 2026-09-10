#!/usr/bin/env python3
"""M2-P2 world compiler: authored package -> per-world ecology (m2p1 schema).

Implements EXACTLY the compilation rule frozen in M2P2_FREEZE_V1.json:

  enumerate all builders of length 0..8 in the registered order (the spec's public
  order add1<sub1<dbl<sqr mapped positionally onto the registered grammar), compute
  each builder's polynomial via the REGISTERED normal_form, take first-in-enumeration
  as the canonical builder, take as members exactly those polynomials whose canonical
  builder (a) decomposes end-to-end into the world's chunks (m2p1 DP) and (b) has
  length >= the world's min_builder_length; split members into initial/tuning/future
  streams by per-length quotas in the world's part_fractions, hashed ordering exactly
  as m2p1_ecology.py.

Intent-stripping is structural: the loader whitelists the four frozen interface keys
(world_id, chunks, min_builder_length, part_fractions) and never opens `surface` or
`intent`. Those fields are copied verbatim into a separate audit section of the
receipt by m2p2_check.py, never by this compiler, and never into the ecology.

The emitted ecology is schema-compatible with m2p1 (streams train/validation/protected
= initial/tuning/future; hidden_motifs = mapped chunks) so the m2p1 runner, dose
ladder and summarize import run on it UNMODIFIED.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, sys, time
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2P2_COMPILED_WORLD_V1"

# frozen interface bridge (M2P2_FREEZE_V1.json neutral_author_spec.interface_bridge)
OP_MAP = {"add1": "inc", "sub1": "dec", "dbl": "double", "sqr": "square"}

INTERFACE_KEYS = ("world_id", "chunks", "min_builder_length", "part_fractions")

VIABILITY = {"members_min": 90, "initial_min": 15, "tuning_min": 6, "future_min": 20}
STREAM_NAME = {"initial": "train", "tuning": "validation", "future": "protected"}


class AuthorPackageDefect(Exception):
    pass


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def load_worlds_interface_only(path: Path) -> list[dict]:
    """Whitelist loader: reads ONLY the frozen interface keys; surface/intent are
    structurally invisible to compilation (frozen intent-stripping rule)."""
    worlds = []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        missing = [k for k in INTERFACE_KEYS if k not in obj]
        if missing:
            raise AuthorPackageDefect(f"line {lineno}: missing interface keys {missing}")
        worlds.append({k: obj[k] for k in INTERFACE_KEYS})   # whitelist copy
    return worlds


def validate_world(w: dict, idx: int) -> dict:
    problems = []
    wid = w["world_id"]
    if not isinstance(wid, str) or not wid:
        problems.append("world_id must be a nonempty string")
    chunks = w["chunks"]
    if not isinstance(chunks, list) or not (4 <= len(chunks) <= 8):
        problems.append("chunk count outside 4..8")
    else:
        for c in chunks:
            if not isinstance(c, list) or not (2 <= len(c) <= 3):
                problems.append(f"chunk {c} length outside 2..3")
            elif any(op not in OP_MAP for op in c):
                problems.append(f"chunk {c} uses an unknown operation")
        seqs = [tuple(c) for c in chunks]
        if len(set(seqs)) != len(seqs):
            problems.append("duplicate chunks")
    mbl = w["min_builder_length"]
    if not (isinstance(mbl, int) and 4 <= mbl <= 8):
        problems.append("min_builder_length outside 4..8")
    pf = w["part_fractions"]
    if not isinstance(pf, dict) or set(pf) != {"initial", "tuning", "future"}:
        problems.append("part_fractions keys must be initial/tuning/future")
    else:
        bands = {"initial": (0.35, 0.60), "tuning": (0.10, 0.30), "future": (0.25, 0.75)}
        for k, (lo, hi) in bands.items():
            v = pf[k]
            if not isinstance(v, (int, float)) or not (lo <= v <= hi):
                problems.append(f"part_fraction {k}={v} outside [{lo},{hi}]")
        if abs(sum(pf.values()) - 1.0) > 1e-9:
            problems.append("part_fractions do not sum to 1")
    if problems:
        raise AuthorPackageDefect(f"world[{idx}] {wid!r}: " + "; ".join(problems))
    return w


def decomposable(program, motifs) -> bool:
    n = len(program)
    reach = [False] * (n + 1)
    reach[0] = True
    for i in range(n):
        if not reach[i]:
            continue
        for m in motifs:
            j = i + len(m)
            if j <= n and tuple(program[i:j]) == m:
                reach[j] = True
    return reach[n]


def compile_world(M, world: dict, seed: int) -> dict:
    motifs = tuple(sorted(tuple(OP_MAP[op] for op in c) for c in world["chunks"]))
    mbl = world["min_builder_length"]
    pf = world["part_fractions"]

    canonical, first_index = {}, {}
    slot = 0
    for L in range(9):
        for prog in product(M.PRIMITIVES, repeat=L):
            slot += 1
            nf = M.normal_form(prog)
            if nf not in canonical:
                canonical[nf], first_index[nf] = prog, slot

    members = [nf for nf, prog in canonical.items()
               if len(prog) >= mbl and decomposable(prog, motifs)]
    by_len = defaultdict(list)
    for nf in members:
        by_len[len(canonical[nf])].append(nf)
    for L in by_len:
        by_len[L].sort(key=lambda nf: hashlib.sha256(str(nf).encode()).hexdigest())

    # per-length quotas in the world's fractions, hashed ordering, exactly m2p1
    quota = {STREAM_NAME[k]: v for k, v in pf.items()}
    streams = {"train": [], "validation": [], "protected": []}
    for L, nfs in sorted(by_len.items()):
        i = 0
        for name, frac in quota.items():
            k = int(round(len(nfs) * frac))
            streams[name].extend(nfs[i:i + k])
            i += k
        streams["train"].extend(nfs[i:])          # remainder to initial, as m2p1

    def row(nf):
        return {"coefficients": [str(c) for c in nf],
                "canonical_program": list(canonical[nf]),
                "canonical_length": len(canonical[nf]),
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
    parity = max((abs(dists[x].get(L, 0.0) - dists[y].get(L, 0.0)) for L in alll
                  for x in dists for y in dists if x != y), default=1.0)

    g3_bad = [r["normal_form_digest"] for v in out_streams.values() for r in v
              if not decomposable(tuple(r["canonical_program"]), motifs)]

    sizes = {k: len(v) for k, v in out_streams.items()}
    viable = (len(members) >= VIABILITY["members_min"]
              and sizes["train"] >= VIABILITY["initial_min"]
              and sizes["validation"] >= VIABILITY["tuning_min"]
              and sizes["protected"] >= VIABILITY["future_min"])

    return {
        "schema": SCHEMA, "lane": LANE,
        "status": "WORLD_COMPILATION_NOT_A_SCORED_RUN",
        "owner_issue": 165, "hardening_parent": 323,
        "world_id": world["world_id"],
        "op_map": OP_MAP,
        "author_part_fractions": pf,
        "author_min_builder_length": mbl,
        "shape": {"chunk_count": len(motifs),
                  "chunk_lengths": sorted(len(m) for m in motifs),
                  "min_builder_length": mbl,
                  "part_fractions": {k: round(v, 4) for k, v in sorted(pf.items())}},
        "frozen_seed": seed,
        "hidden_motifs": [list(m) for m in motifs],
        "hidden_motifs_sha256": hashlib.sha256(
            json.dumps([list(m) for m in motifs]).encode()).hexdigest(),
        "grammar": {"primitives": list(M.PRIMITIVES), "max_length": 8},
        "ecology": {"members": len(members),
                    "canonical_length_distribution": {
                        str(k): v for k, v in sorted(
                            Counter(len(canonical[nf]) for nf in members).items())}},
        "streams": out_streams,
        "stream_sizes": sizes,
        "entry_gates": {
            "G1_length_parity_max_deviation": round(parity, 4),
            "G1_verdict": "PASS" if parity <= 0.12 else "FAIL",
            "G2_shared_normal_forms": len(shared),
            "G2_verdict": "PASS" if not shared else "FAIL",
            "G3_non_decomposable": len(g3_bad),
            "G3_verdict": "PASS" if not g3_bad else "FAIL",
            "G4_surface_predictor_null": "DEFERRED_TO_GSURF"},
        "viability": {"counts": {"members": len(members), **sizes},
                      "floors": VIABILITY,
                      "viable": viable,
                      "verdict": "VIABLE" if viable else "CANNOT_CHECK_WORLD"},
        "length_distributions_by_stream": {
            k: {str(x): round(y, 4) for x, y in v.items()} for k, v in dists.items()},
        "intent_stripped": ("compilation read ONLY the frozen interface keys "
                            + str(INTERFACE_KEYS) + "; surface/intent fields were "
                            "never opened by this compiler"),
        "host": {"hostname": platform.node(), "python": platform.python_version()},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--worlds", required=True, help="authored worlds.jsonl")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260911)
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M
    outdir = Path(a.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    worlds = [validate_world(w, i) for i, w in
              enumerate(load_worlds_interface_only(Path(a.worlds)))]
    if len({w["world_id"] for w in worlds}) != len(worlds):
        raise AuthorPackageDefect("world_id values are not unique")
    chunk_sets = {tuple(sorted(tuple(c) for c in w["chunks"])) for w in worlds}
    shapes = {(len(w["chunks"]), tuple(sorted(len(c) for c in w["chunks"])),
               w["min_builder_length"],
               tuple(sorted(round(v, 4) for v in w["part_fractions"].values())))
              for w in worlds}

    index = []
    for i, w in enumerate(worlds):
        eco = compile_world(M, w, a.seed + i)
        eco["bound_sources"] = {
            "methods.py": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py"),
            "git_head": os.popen(f"/usr/bin/git -C {repo} rev-parse HEAD").read().strip(),
            "worlds_jsonl": sha256_file(Path(a.worlds))}
        p = outdir / f"M2P2_WORLD_{w['world_id']}.json"
        p.write_text(json.dumps(eco, indent=1, sort_keys=True))
        g = eco["entry_gates"]
        index.append({"world_id": w["world_id"], "file": str(p),
                      "members": eco["ecology"]["members"],
                      "sizes": eco["stream_sizes"],
                      "gates": {k: v for k, v in g.items() if k.endswith("verdict")},
                      "viability": eco["viability"]["verdict"]})
        print(json.dumps(index[-1]))

    summary = {"schema": "OCM_M2P2_COMPILE_SUMMARY_V1", "lane": LANE,
               "owner_issue": 165, "hardening_parent": 323,
               "worlds_n": len(worlds), "unique_chunk_sets": len(chunk_sets),
               "distinct_shapes": len(shapes),
               "floors": {"worlds_min": 6, "distinct_shapes_min": 2,
                          "worlds_floor_met": len(worlds) >= 6,
                          "shapes_floor_met": len(shapes) >= 2},
               "viable_worlds": sum(1 for r in index if r["viability"] == "VIABLE"),
               "worlds": index,
               "timing_seconds": round(time.perf_counter() - t0, 2)}
    (outdir / "M2P2_COMPILE_SUMMARY.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in summary.items() if k != "worlds"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
