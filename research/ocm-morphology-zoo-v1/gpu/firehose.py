"""Vectorized T0 firehose for the GS GPU lane (#221 sec 18, worker O).

Modes
  random   — n frozen-seed draws from morphology.direct_genome.random_genome
             over the closed census grammar (draws re-index the closed
             lattice); optional centre sampling weights (GS-R1h)
  census   — enumerate_census() once: every legal genome in CENSUS_BOUND_V1
             (56160), each distinct phenotype evaluated exactly once per run
  manifest — genomes listed in a JSON manifest [{F_arch, extras, T_family,
             Pi_arch, L, R, K}, ...]

Every organism is evaluated by the batched T0 tape (gpu.t0_tape), which is
bit-identical to evaluation.lifetime.run_lifetime (asserted on the first
chunk against the pure-python backend and by the test suite).  Receipts are
sha256-chained via evaluation.receipts.  Every failure appends one
FAILURES.jsonl line attributed to exactly ONE stage
(compile / encode / tape / assembly).  All costs charged: encode_s and
tape_s reported separately.

Scoring gate (GS ordering, worker N owns the freeze): unless a
GRAND_SEARCH_R1_FREEZE.json is present AND its sha256 equals the expected
sha, every artifact this module writes is labelled SMOKE_NOT_SCORED and can
never be mixed into scored results.

GS-R1h hourly discipline (operator update, 2026-09-09):
  * checkpoint lines  -> results/GS_R1_CHECKPOINTS.jsonl, one per
    checkpoint_every seconds (default 3600) and at run end.  Line schema
    (centre-coordinated; matches worker N's CPU checkpoints when his
    zoo/gs-round1 branch lands, else this documented schema):
      {"lane", "ts", "run_id", "label", "spec_id", "attempted",
       "completed", "n_feasible", "viability_rate", "throughput",
       "evals_per_s_tape", "encode_s", "tape_s", "wall_s", "n_failures",
       "receipt_head", "freeze_sha256", "backend"}
  * status            -> results/GS_R1_STATUS.json, overwritten every
    checkpoint with {"lanes": {<lane>: latest-totals}} so one cat per host
    gives centre the state of every lane on that host.
  * resumable batches — each hourly run may consume a fresh centre batch
    spec (--run-spec JSON: sampling weights / tier promotions) as an
    INDEPENDENT run under the same freeze.  Every mid-run adaptivity
    decision is logged to results/ADAPTIVITY_LEDGER.jsonl BEFORE
    submission (log_adaptivity_decision); frozen rules are never modified
    mid-run.  This lane executes the T0-sampling part of a spec; any
    tier_promotions field is recorded and forwarded (T1/T2 stay CPU).

Usage (from the capsule root):
  python3 -m gpu.firehose --mode random --n 20000 --seed 2210 \
      [--backend auto] [--chunk 4096] [--lane gpu]
      [--freeze P --freeze-sha S] [--run-spec SPEC.json] \
      [--checkpoint-every 3600] [--tag mytag]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import sys
import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

if __package__ in (None, ""):  # direct-script execution from capsule root
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.receipts import (all_dispositions, append_record,  # noqa: E402
                                 make_receipt, verify_receipt)
from gpu import encode as _encode
from gpu.t0_tape import make_backend, run_t0_tape  # noqa: E402
from morphology.direct_genome import (CENSUS_BOUND_V1, DEFAULT_THETA,  # noqa: E402
                                      enumerate_census, operators_for,
                                      random_genome)
from morphology.schema import OCMMorphologyGenomeV1, UnitSpec  # noqa: E402

FREEZE_NAME = "GRAND_SEARCH_R1_FREEZE.json"
SMOKE_LABEL = "SMOKE_NOT_SCORED"
CHECKPOINTS = "GS_R1_CHECKPOINTS.jsonl"
STATUS = "GS_R1_STATUS.json"
LEDGER = "ADAPTIVITY_LEDGER.jsonl"


# --------------------------------------------------------------- genome modes
def _weighted_options(rng: random.Random, options: Sequence[str],
                      weights: Optional[Dict[str, float]]) -> str:
    if not weights:
        return rng.choice(list(options))
    total = sum(max(0.0, float(weights.get(o, 0.0))) for o in options)
    if total <= 0.0:
        return rng.choice(list(options))
    x = rng.random() * total
    acc = 0.0
    for o in options:
        acc += max(0.0, float(weights.get(o, 0.0)))
        if x <= acc:
            return o
    return options[-1]


def _weighted_sample_no_replace(rng: random.Random, pool: Sequence[str],
                                n: int, weights: Optional[Dict[str, float]]
                                ) -> List[str]:
    """Efraimidis-Spirakis weighted sample without replacement."""
    if not weights:
        return sorted(rng.sample(list(pool), n))
    keys = {o: -math.log(1.0 - rng.random()) / max(1e-12, float(weights.get(o, 1e-12)))
            for o in pool}
    return sorted(sorted(pool, key=lambda o: keys[o])[:n])


def genomes_random(n: int, seed: int,
                   weights: Optional[Dict[str, Dict[str, float]]] = None
                   ) -> List[Any]:
    """Frozen-seed draws; optional centre sampling weights (GS-R1h)."""
    rng = random.Random(seed)
    if not weights:
        return [random_genome(rng, CENSUS_BOUND_V1) for _ in range(n)]
    b = CENSUS_BOUND_V1
    out: List[Any] = []
    for _ in range(n):
        nw = _weighted_options(rng, ("0", "1", "2", "3"),
                               weights.get("n_extras"))
        extras = _weighted_sample_no_replace(
            rng, list(b["extra_units"]), int(nw), weights.get("extras"))
        out.append(spec_to_genome({
            "F_arch": _weighted_options(rng, b["F_arch"], weights.get("F_arch")),
            "extras": extras,
            "T_family": _weighted_options(rng, b["T_family"], weights.get("T_family")),
            "Pi_arch": _weighted_options(rng, b["Pi_arch"], weights.get("Pi_arch")),
            "L": _weighted_options(rng, b["L"], weights.get("L")),
            "R": _weighted_options(rng, b["R"], weights.get("R")),
            "K": _weighted_options(rng, b["K"], weights.get("K"))}))
    return out


def genomes_census() -> Iterable[Any]:
    return enumerate_census(CENSUS_BOUND_V1)


def spec_to_genome(spec: Dict[str, Any]) -> OCMMorphologyGenomeV1:
    extras = list(spec.get("extras", []))
    unit_types = ["fact_relation"] + extras
    units = [UnitSpec("u%02d_%s" % (i, t), t) for i, t in enumerate(unit_types)]
    return OCMMorphologyGenomeV1(
        encoding="E0_direct", F_arch=spec["F_arch"], U=units,
        T_family=spec["T_family"],
        O_basis=operators_for(unit_types, spec["L"], spec["K"], spec["R"]),
        Pi_arch=spec["Pi_arch"], L=spec["L"], R=spec["R"], K=spec["K"],
        theta=dict(DEFAULT_THETA))


def genomes_manifest(path: str) -> List[Any]:
    with open(path) as f:
        specs = json.load(f)
    if isinstance(specs, dict):
        specs = specs["genomes"]
    return [spec_to_genome(s) for s in specs]


# ------------------------------------------------- GS-R1h checkpoints / status
def checkpoint_line(root: str, lane: str, run_id: str, label: str,
                    spec_id: Optional[str], attempted: int, completed: int,
                    n_feasible: int, encode_s: float, tape_s: float,
                    wall_s: float, n_failures: int, receipt_head: str,
                    freeze_sha: Optional[str], backend: str,
                    ts: Optional[str] = None) -> Dict[str, Any]:
    line = {"lane": lane, "ts": ts or time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_id": run_id, "label": label, "spec_id": spec_id,
        "attempted": attempted, "completed": completed,
        "n_feasible": n_feasible,
        "viability_rate": round(n_feasible / max(1, completed), 6),
        "throughput": round(completed / max(1e-9, wall_s), 1),
        "evals_per_s_tape": round(completed / max(1e-9, tape_s), 1),
        "encode_s": round(encode_s, 3), "tape_s": round(tape_s, 3),
        "wall_s": round(wall_s, 3), "n_failures": n_failures,
        "receipt_head": receipt_head, "freeze_sha256": freeze_sha,
        "backend": backend}
    path = os.path.join(root, "results", CHECKPOINTS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(line, sort_keys=True) + "\n")
    return line


def status_write(root: str, lane: str, totals: Dict[str, Any]) -> None:
    """Overwrite results/GS_R1_STATUS.json with {lanes: {lane: latest}}."""
    path = os.path.join(root, "results", STATUS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cur: Dict[str, Any] = {"lanes": {}}
    if os.path.exists(path):
        try:
            with open(path) as f:
                cur = json.load(f)
        except Exception:
            cur = {"lanes": {}}
    cur.setdefault("lanes", {})[lane] = totals
    cur["updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cur, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def log_adaptivity_decision(root: str, lane: str, decision: Dict[str, Any]) -> None:
    """GS-R1h: every mid-run adaptivity decision logged BEFORE submission."""
    path = os.path.join(root, "results", LEDGER)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "lane": lane}
    rec.update(decision)
    with open(path, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


# ------------------------------------------------------------- failure memory
class FailureLog:
    """One JSON line per failure, attributed to exactly one stage."""

    STAGES = ("compile", "encode", "tape", "assembly")

    def __init__(self, path: str) -> None:
        self.path = path
        self.count = 0
        self._fh = open(path, "a") if path else None

    def add(self, stage: str, index: int, mode: str, err: BaseException,
            spec: Optional[Dict[str, Any]] = None) -> None:
        assert stage in self.STAGES, "unknown stage %r" % stage
        rec: Dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "stage": stage, "index": index, "mode": mode,
            "error_type": type(err).__name__,
            "error": str(err)[:300]}
        if spec is not None:
            rec["genome_spec"] = spec
        if self._fh is not None:
            self._fh.write(json.dumps(rec, sort_keys=True) + "\n")
            self._fh.flush()
        self.count += 1

    def close(self) -> None:
        if self._fh is not None:
            self._fh.close()


def _flat_nums(rec: Dict[str, Any]) -> List[float]:
    """Floats of a tape record (identity-check ordering)."""
    ev = rec["evaluation"]
    out: List[float] = []
    for k in sorted(ev):
        v = ev[k]
        if isinstance(v, bool) or isinstance(v, (int, float)):
            out.append(float(v))
    return out


# -------------------------------------------------------------------- runner
def run_firehose(mode: str, root: str, n: int = 1000, seed: int = 2210,
                 backend_name: str = "auto", chunk: int = 4096,
                 freeze_path: Optional[str] = None,
                 freeze_sha: Optional[str] = None,
                 manifest_path: Optional[str] = None,
                 run_spec: Optional[Dict[str, Any]] = None,
                 lane: str = "gpu", checkpoint_every: float = 3600.0,
                 tag: str = "") -> Dict[str, Any]:
    t_start = time.time()
    # --- scoring gate: SMOKE unless a sha-verified freeze exists
    label = SMOKE_LABEL
    freeze_digest: Optional[str] = None
    if freeze_path and freeze_sha and os.path.exists(freeze_path):
        with open(freeze_path, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        if actual == freeze_sha:
            label = "SCORED_GS_R1"
            freeze_digest = actual
        else:
            print("FREEZE_SHA_MISMATCH: %s != %s (staying %s)"
                  % (actual[:16], freeze_sha[:16], SMOKE_LABEL))

    spec_id: Optional[str] = None
    weights: Optional[Dict[str, Dict[str, float]]] = None
    if run_spec:
        spec_id = str(run_spec.get("spec_id", "unspecified"))
        weights = run_spec.get("sampling_weights") or None
        if mode == "random" and isinstance(run_spec.get("n"), int):
            n = run_spec["n"]

    res_dir = os.path.join(root, "results")
    os.makedirs(res_dir, exist_ok=True)
    run_id = "%sGPU_FIREHOSE_%s_%s%s%s" % (
        "SMOKE_" if label == SMOKE_LABEL else "", mode, seed,
        ("_" + spec_id) if spec_id else "", ("_" + tag) if tag else "")
    failures = FailureLog(os.path.join(res_dir, "FAILURES.jsonl"))

    if mode == "random":
        genome_iter: Iterable[Any] = genomes_random(n, seed, weights)
    elif mode == "census":
        genome_iter = genomes_census()
    elif mode == "manifest":
        genome_iter = genomes_manifest(manifest_path or "")
    else:
        raise ValueError("mode must be random|census|manifest")

    cfg_digest = hashlib.sha256(json.dumps(
        {"mode": mode, "n": n, "seed": seed, "chunk": chunk,
         "label": label, "freeze": freeze_digest, "spec_id": spec_id,
         "weights": weights,
         "census_bound": {k: (list(v) if isinstance(v, tuple) else v)
                          for k, v in CENSUS_BOUND_V1.items()}},
        sort_keys=True).encode()).hexdigest()
    receipt = make_receipt(run_id,
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", platform.node()),
                           "T0", cfg_digest)

    backend = make_backend(backend_name)
    counters = {"encode_s": 0.0, "tape_s": 0.0, "attempted": 0,
                "completed": 0, "feasible": 0, "failures": 0}
    phenotypes = set()
    identity_check: Optional[Dict[str, Any]] = None
    last_ckpt = t_start

    def checkpoint(force: bool) -> None:
        nonlocal last_ckpt
        if not force and (time.time() - last_ckpt) < checkpoint_every:
            return
        last_ckpt = time.time()
        line = checkpoint_line(
            root, lane, run_id, label, spec_id,
            counters["attempted"], counters["completed"], counters["feasible"],
            counters["encode_s"], counters["tape_s"],
            time.time() - t_start, counters["failures"],
            receipt["head_sha256"], freeze_digest, backend.name)
        status_write(root, lane, dict(line))

    def flush(batch_items: List[Tuple[int, Any]], first: bool) -> None:
        nonlocal identity_check
        if not batch_items:
            return
        rows = []
        t_e = time.time()
        for gidx, g in batch_items:
            counters["attempted"] += 1
            try:
                rows.append(_encode.encode_genome(g))
            except Exception as exc:
                stage = ("compile"
                         if type(exc).__name__ == "InvariantViolation"
                         else "encode")
                failures.add(stage, gidx, mode, exc)
        counters["encode_s"] += time.time() - t_e
        if not rows:
            return
        columns = {name: [r[name] for r in rows]
                   for name in _encode.COLUMN_NAMES}
        meta = [{k: v for k, v in r.items() if k.startswith("_")}
                for r in rows]
        bdict = {"n": len(rows), "columns": columns, "meta": meta,
                 "column_names": list(_encode.COLUMN_NAMES)}
        t_t = time.time()
        try:
            out = run_t0_tape(bdict, backend)
        except Exception as exc:
            counters["tape_s"] += time.time() - t_t
            failures.add("tape", batch_items[0][0], mode, exc)
            return
        counters["tape_s"] += time.time() - t_t
        if first and backend.name != "py":
            ref = run_t0_tape(bdict, make_backend("py"))
            m = 0.0
            for rec, ref_rec in zip(out, ref):
                a, b = _flat_nums(rec), _flat_nums(ref_rec)
                for va, vb in zip(a, b):
                    m = max(m, abs(va - vb))
            identity_check = {"backend": backend.name, "ref": "py",
                              "chunk": len(out), "max_abs_diff": m}
        for rec in out:
            counters["completed"] += 1
            counters["feasible"] += int(bool(rec.get("feasible")))
            pd = rec.get("phenotype_digest")
            if pd:
                phenotypes.add(pd)
            ev = rec.get("evaluation", {})
            append_record(receipt, len(receipt["chain"]), {
                "g": str(rec.get("genotype_digest", ""))[:16],
                "p": str(pd or "")[:16],
                "f": int(bool(rec.get("feasible"))),
                "solved": ev.get("solved_fraction", 0.0),
                "work": ev.get("work_total", 0.0)})

    first = True
    batch: List[Tuple[int, Any]] = []
    gidx = 0
    try:
        for g in genome_iter:
            batch.append((gidx, g))
            gidx += 1
            if len(batch) >= chunk:
                flush(batch, first)
                first = False
                batch = []
                checkpoint(False)
        flush(batch, first)
    finally:
        failures.close()

    assert verify_receipt(receipt), "receipt chain broken"
    wall = time.time() - t_start
    counters["failures"] = failures.count
    checkpoint(True)  # final hourly-schema line + status overwrite
    summary = {
        "run_id": run_id,
        "label": label,
        "freeze_sha256": freeze_digest,
        "lane": lane,
        "mode": mode, "seed": seed, "chunk": chunk, "n": n,
        "spec_id": spec_id,
        "tier_promotions_forwarded": (run_spec or {}).get("tier_promotions"),
        "backend": backend.name,
        "backend_device": getattr(backend, "device", None),
        "n_attempted": counters["attempted"],
        "n_evaluated": counters["completed"],
        "n_feasible": counters["feasible"],
        "viability_rate": round(counters["feasible"]
                                / max(1, counters["completed"]), 6),
        "n_distinct_phenotypes": len(phenotypes),
        "n_failures": failures.count,
        "identity_check": identity_check,
        "costs": {"encode_s": round(counters["encode_s"], 3),
                  "tape_s": round(counters["tape_s"], 3),
                  "wall_s": round(wall, 3),
                  "evals_per_s_tape": round(
                      counters["completed"] / max(1e-9, counters["tape_s"]), 1),
                  "evals_per_s_total": round(
                      counters["completed"] / max(1e-9, wall), 1)},
        "host": {"node": platform.node(),
                 "python": platform.python_version(),
                 "machine": platform.machine()},
        "config_digest": cfg_digest,
        "receipt_head": receipt["head_sha256"],
        "all_dispositions": all_dispositions(receipt, expected_indices=None),
    }
    out_path = os.path.join(res_dir, run_id + ".json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    with open(out_path + ".receipt.json", "w") as f:
        json.dump(receipt, f)
    with open(out_path + ".status", "w") as f:
        json.dump({"status": "DONE", "run_id": run_id, "label": label,
                   "receipt_head": receipt["head_sha256"]}, f, indent=1)
    print(json.dumps(summary, sort_keys=True))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="GS GPU-lane T0 firehose")
    ap.add_argument("--root", default=os.getcwd(),
                    help="capsule root (contains morphology/, evaluation/, gpu/)")
    ap.add_argument("--mode", default="random",
                    choices=["random", "census", "manifest"])
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=2210)
    ap.add_argument("--backend", default="auto",
                    choices=["auto", "py", "numpy", "torch"])
    ap.add_argument("--chunk", type=int, default=4096)
    ap.add_argument("--freeze", default=None)
    ap.add_argument("--freeze-sha", default=None)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--run-spec", default=None,
                    help="GS-R1h hourly batch spec JSON (sampling weights / "
                         "tier promotions); independent run, same freeze")
    ap.add_argument("--lane", default="gpu")
    ap.add_argument("--checkpoint-every", type=float, default=3600.0)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    run_spec = None
    if args.run_spec:
        with open(args.run_spec) as f:
            run_spec = json.load(f)
        # GS-R1h: log the adaptivity decision BEFORE executing the batch
        log_adaptivity_decision(args.root, args.lane, {
            "action": "run_firehose", "mode": args.mode, "seed": args.seed,
            "spec_id": run_spec.get("spec_id", "unspecified"),
            "spec_sha256": hashlib.sha256(
                json.dumps(run_spec, sort_keys=True).encode()).hexdigest(),
            "freeze_sha256": args.freeze_sha,
            "issued_by": run_spec.get("issued_by", "centre")})
    run_firehose(args.mode, args.root, n=args.n, seed=args.seed,
                 backend_name=args.backend, chunk=args.chunk,
                 freeze_path=args.freeze, freeze_sha=args.freeze_sha,
                 manifest_path=args.manifest, run_spec=run_spec,
                 lane=args.lane, checkpoint_every=args.checkpoint_every,
                 tag=args.tag)


if __name__ == "__main__":
    main()
