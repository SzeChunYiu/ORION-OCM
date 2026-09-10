#!/usr/bin/env python3
"""EB-F0-X smoke: validate every instrument against the frozen contract.

Runs small but real workloads. Its job is to prove each instrument can both
hold and fail BEFORE any cluster launch. Exit 0 only when every instrument is
wired to the frozen contract and the no-alarm controls stay silent.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ablation          # noqa: E402
import binding           # noqa: E402
import hostiles_x        # noqa: E402
import invariance        # noqa: E402
import worlds as W       # noqa: E402


def sample_specs(n, limit, mode="MULTISET", seed=0):
    """Stride across the whole enumeration -- a prefix is degenerate."""
    return W.stride_sample(n, limit, mode=mode, seed=seed)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--sample", type=int, default=200)
    ap.add_argument("--ticks", type=int, default=W.DEFAULT_TICKS)
    ap.add_argument("--conditions", type=int, default=300)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    cdir = binding.contract_dir(HERE)
    report = {"schema": "MEX_SMOKE_V1", "n_org": a.n, "ticks": a.ticks}

    report["contract"] = binding.verify_contract(cdir)
    if report["contract"]["status"] != "OK":
        report["verdict"] = "CANNOT_CHECK_CONTRACT"
        _emit(report, a.out)
        return 3

    me = W.load_micro_earth(cdir)
    sys.path.insert(0, cdir)
    import hostiles as frozen_hostiles   # noqa: E402
    import kernels as frozen_kernels     # noqa: E402

    specs = sample_specs(a.n, a.sample)
    report["n_specs_sampled"] = len(specs)
    report["bounds"] = W.bound_table()

    report["frozen_ablation_checker"] = ablation.probe_frozen_checker(
        frozen_kernels)
    report["frozen_gate_coverage"] = hostiles_x.frozen_gate_coverage(
        cdir, frozen_hostiles)
    report["no_alarm"] = ablation.no_alarm_control(me, specs[:50], a.ticks)
    report["lattice"] = ablation.lattice_completeness(me, specs[0], a.ticks)
    report["invariance"] = invariance.probe(me, specs[:20], a.ticks)
    report["kernel_effects_lattice"] = ablation.kernel_effect_matrix(
        me, specs, a.ticks)
    report["kernel_effects_baseline"] = ablation.baseline_effect_matrix(
        me, a.n, n_conditions=a.conditions, ticks=a.ticks)
    hm = hostiles_x.run_matrix(me, cdir)
    hm.pop("cells", None)          # keep the smoke report small
    report["hostiles"] = hm

    checks = {
        "contract_verified": report["contract"]["status"] == "OK",
        "no_alarm_silent": report["no_alarm"]["silent"],
        "lattice_complete": report["lattice"]["status"] == "HOLD",
        "every_hostile_fires": not hm["hostiles_that_never_fire"],
        "clean_controls_silent": not hm["clean_controls_not_silent"],
        "ablation_independent":
            report["kernel_effects_baseline"]["verdict"]
            == "KERNELS_INDEPENDENTLY_ABLATABLE",
        "sample_not_degenerate": len({s.genomes for s in specs}) > 1,
    }
    report["checks"] = checks
    report["verdict"] = "SMOKE_OK" if all(checks.values()) else "SMOKE_FAIL"
    _emit(report, a.out)
    return 0 if report["verdict"] == "SMOKE_OK" else 1


def _emit(report, out):
    text = json.dumps(report, indent=1, sort_keys=True, default=str)
    if out:
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, out)
    print(text)


if __name__ == "__main__":
    sys.exit(main())
