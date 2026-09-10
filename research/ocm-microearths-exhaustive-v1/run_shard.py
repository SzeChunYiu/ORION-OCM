#!/usr/bin/env python3
"""One EB-F0-X array shard: exhaustive census over a stride of micro-Earths.

Three passes, each with its own declared bound:
  A  signature census   -- every world in this shard, one trajectory each
  B  baseline ablation  -- flip each kernel from the all-on baseline
  C  permutation probe  -- does the MULTISET quotient stay licensed

Determinism: the shard index selects a stride of the enumeration; it never
seeds an RNG. Two runs of the same shard must produce identical output.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ablation      # noqa: E402
import binding       # noqa: E402
import invariance    # noqa: E402
import vacuity       # noqa: E402
import worlds as W   # noqa: E402


def pass_a(me, n, mode, shard, nshards, ticks, cap):
    sigs, n_worlds, births, deaths = {}, 0, 0, 0
    t0 = time.time()
    for spec in W.enumerate_worlds(n, mode=mode, shard=(shard, nshards)):
        s = W.signature(me, spec, ticks)
        sigs[s] = sigs.get(s, 0) + 1
        n_worlds += 1
        if cap and n_worlds >= cap:
            break
    dt = time.time() - t0
    return {
        "pass": "A_signature_census", "n_worlds": n_worlds,
        "n_distinct_trajectories": len(sigs),
        "top_signatures": sorted(sigs.items(), key=lambda kv: -kv[1])[:10],
        "seconds": round(dt, 3),
        "worlds_per_sec": round(n_worlds / dt, 1) if dt > 0 else None,
        "complete": not (cap and n_worlds >= cap),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--mode", default="MULTISET")
    ap.add_argument("--ticks", type=int, default=W.DEFAULT_TICKS)
    ap.add_argument("--cap", type=int, default=0)
    ap.add_argument("--conditions", type=int, default=2000)
    ap.add_argument("--perm-specs", type=int, default=200)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    cdir = binding.contract_dir(HERE)
    rep = {"schema": "MEX_SHARD_V1", "n_org": a.n, "mode": a.mode,
           "shard": a.shard, "nshards": a.nshards, "ticks": a.ticks,
           "protocol_sha256": binding.protocol_sha(HERE),
           "code_digest": binding.code_digest(HERE),
           "host": os.uname().nodename}
    rep["contract"] = binding.verify_contract(cdir)
    if rep["contract"]["status"] != "OK":
        rep["status"] = "CANNOT_CHECK_CONTRACT"
        _write(a.out, rep, "fail contract")
        return 3

    me = W.load_micro_earth(cdir)
    rep["bounds"] = [b for b in W.bound_table([a.n])][0]
    rep["A"] = pass_a(me, a.n, a.mode, a.shard, a.nshards, a.ticks, a.cap)

    if a.shard == 0:  # shard 0 owns the non-sharded instruments
        rep["B"] = ablation.baseline_effect_matrix(
            me, a.n, n_conditions=a.conditions, ticks=a.ticks, mode=a.mode)
        specs = W.stride_sample(a.n, a.perm_specs, mode=a.mode)
        rep["C"] = invariance.probe(me, specs, a.ticks)
        rep["D_vacuity"] = vacuity.birth_reachability(
            me, a.n, n_conditions=a.conditions, ticks=a.ticks, mode=a.mode)
        rep["E_exercisability"] = vacuity.kernel_exercisability(
            me, a.n, n_conditions=a.conditions, ticks=a.ticks, mode=a.mode)
    rep["status"] = "ok"
    _write(a.out, rep, "ok")
    return 0


def _write(out, rep, status):
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True, default=str)
    os.replace(tmp, out)
    with open(out.replace(".json", "") + ".status", "w") as fh:
        fh.write(status + "\n")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:   # retain the crash, never overwrite with success
        import traceback
        traceback.print_exc()
        raise
