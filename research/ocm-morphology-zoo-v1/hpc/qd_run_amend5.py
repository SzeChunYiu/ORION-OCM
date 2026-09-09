"""AMEND-5 worker (quality-gated D-archive admission): one (arm, seed) scored
T2 run under FREEZE_V1_AMEND_5.json.

Arms (frozen in A5): G01_gate_{D2d,D3d} — map_elites.run(admission_bar=the
frozen bar, chosen mechanically from the GATE-CEILING census truth);
G00_nogate_{D2d,D3d} — the identical call with admission_bar=None (the one
varied dimension is the gate).

Determinism xchecks (hard, in-array):
  - G00: the archive must equal the frozen amend-3 twin archive
    (QDA3_P05_map_elites_D2d / QDA3_P09_map_elites_D3d, same budget/seeds/
    axis) record-for-record, best_dev must equal the frozen QDA3 value and
    raw own-axis recovery the frozen QDA3 metric — the admission_bar=None
    path is byte-identical to every prior amendment;
  - G01: every recomputed elite dev >= the frozen bar (junk-free by
    construction, junk_free_ratio == 1.0);
  - when the frozen bar == HZD9 quality_bar_T2, G00 junk-free own-axis
    recovery must equal the frozen HZD9R value for the twin arm/seed.

All metrics are recomputed uniformly at T2 from the archive records, never
taken from the search loop's bookkeeping.  Writes results/QDA5_<ARM>_s<seed>
.json (+ .status, receipt, archive dump).

Usage: python3 qd_run_amend5.py <capsule_root> <ARM_ID> <seed>
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import time

ROOT, ARM, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.path.insert(0, ROOT)
os.environ["ZOO_TIER"] = "T2"

with open(os.path.join(ROOT, "FREEZE_V1_AMEND_5.json")) as f:
    A5 = json.load(f)
SMOKE = os.environ.get("ZOO_SMOKE") == "1"
PREFIX = "SMOKE_QDA5" if SMOKE else "QDA5"
ARMCFG = {a["arm_id"]: a for a in A5["arms_amend5"]["arms"]}
if ARM not in ARMCFG:
    raise SystemExit("task %s not in amend-5 frozen arm list" % ARM)
BUDGET = 100 if SMOKE else A5["arms_amend5"]["budget"]
# production branch binds the FROZEN bar; the smoke branch only lowers it so
# the 100-eval smoke archive is non-degenerate (the binding itself is
# asserted by smoke_amend5.sbatch against the freeze + ceiling truth)
BAR = A5["quality_gate_amend5"]["admission_bar"]
GATED = bool(ARMCFG[ARM]["gated"])
_chain = [("FREEZE_V1.json", "freeze_v1_sha256"),
          ("FREEZE_V1_AMEND_1.json", "amend_1_sha256"),
          ("FREEZE_V1_AMEND_2.json", "amend_2_sha256"),
          ("FREEZE_V1_AMEND_3.json", "amend_3_sha256"),
          ("FREEZE_V1_AMEND_4.json", "amend_4_sha256")]
for fn, key in _chain:
    with open(os.path.join(ROOT, fn), "rb") as f:
        if hashlib.sha256(f.read()).hexdigest() != A5[key]:
            raise SystemExit("%s does not match amend-5 chain" % fn)
DEN = A5["census_truth_P00C"]["denominators"]

from search import map_elites  # noqa: E402
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.objectives import dev_score  # noqa: E402
from morphology.compile import compile_genome  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from hpc.census_p00 import config_digest  # noqa: E402

with open(os.path.join(ROOT, "archives", "CENSUS_P00C_TRUTH.json")) as f:
    TRUTH_C = json.load(f)
PARETO_T2 = {p["phenotype_digest"] for p in TRUTH_C["pareto"]}
D2_CELLS = {tuple(ast.literal_eval(k)) for k in TRUTH_C["cells_D2d10"]}
D3_CELLS = {tuple(ast.literal_eval(k)) for k in TRUTH_C["cells_D3d10"]}
assert len(PARETO_T2) == DEN["PARETO_T2"], "T2 pareto truth/denominator drift"
assert len(D2_CELLS) == DEN["D2d@10_occupied"], "D2d truth/denominator drift"
assert len(D3_CELLS) == DEN["D3d@10_occupied"], "D3d truth/denominator drift"

OWN_AXIS = ARMCFG[ARM]["own_axis"]
AXIS = ARMCFG[ARM]["archive"]
TWIN = ARMCFG[ARM]["nogate_twin"]


def cell_idx(d, bounds, res=10):
    return tuple(min(res - 1, max(0, int((dv - b[0]) / (b[1] - b[0] + 1e-12) * res)))
                 for dv, b in zip(d, bounds))


def main():
    t0 = time.time()
    # smoke lowers the applied bar (0.0) so the 100-eval gated archive is
    # non-degenerate; the PRODUCTION binding bar==freeze==ceiling-truth is
    # asserted by smoke_amend5.sbatch, and every production task applies BAR
    bar = (0.0 if SMOKE else BAR) if GATED else None
    res = map_elites.run(budget=BUDGET, seed=SEED, archive=AXIS, res=10,
                         admission_bar=bar)
    elapsed = time.time() - t0
    recs = res["archive"]
    OWN_CELLS = D2_CELLS if OWN_AXIS == "D2d_cell_recovery" else D3_CELLS
    OWN_DEN = DEN["D2d@10_occupied"] if OWN_AXIS == "D2d_cell_recovery" \
        else DEN["D3d@10_occupied"]
    # junk-free is measured at the gate actually applied (for G01 that is the
    # admission bar, so junk_free == raw by construction; for G00 it is the
    # frozen production bar)
    JUNK_BAR = bar if GATED else BAR

    pareto, own_cells, d2, d3 = set(), set(), set(), set()
    raw_hits, clean_hits = set(), set()
    devs, rets = [], []
    for r in recs:
        g = OCMMorphologyGenomeV1.from_json_obj(r["genome"])
        out = evaluate_genome(g, tier="T2", use_cache=False)
        if not out["feasible"]:
            continue
        ev = out["evaluation"]
        org = compile_genome(g)
        d = dev_score(ev)
        pareto.add(r["phenotype_digest"])
        c2 = cell_idx(descriptors_for(org, ev, "D_dev_2d"),
                      DESCRIPTOR_REGISTRY["D_dev_2d"]["bounds"], 10)
        c3 = cell_idx(descriptors_for(org, ev, "D_dev_3d"),
                      DESCRIPTOR_REGISTRY["D_dev_3d"]["bounds"], 10)
        d2.add(c2)
        d3.add(c3)
        c = c2 if OWN_AXIS == "D2d_cell_recovery" else c3
        raw_hits.add(c)
        if d >= JUNK_BAR:
            clean_hits.add(c)
        devs.append(d)
        rc = ev.get("reset_control", {})
        if rc.get("solved_fraction") is not None:
            rets.append((dev_score(ev),
                         ev["solved_fraction"] - rc["solved_fraction"]))
    best = max(devs) if devs else None
    min_dev = min(devs) if devs else None
    raw_recovery = len(raw_hits & OWN_CELLS) / OWN_DEN
    clean_recovery = len(clean_hits & OWN_CELLS) / OWN_DEN

    xchecks = {}
    # ---- G01: junk-free by construction --------------------------------
    if GATED and devs:
        # check the gate ACTUALLY APPLIED (production: == frozen BAR; smoke
        # lowers it so the 100-eval archive is non-degenerate — the
        # production binding is asserted by smoke_amend5.sbatch)
        xchecks["all_elites_ge_bar"] = min_dev >= bar
        assert xchecks["all_elites_ge_bar"], \
            "gate leaked: min elite dev %r < applied bar %r" % (min_dev, bar)
        xchecks["junk_free_equals_raw"] = abs(clean_recovery - raw_recovery) < 1e-9
        assert xchecks["junk_free_equals_raw"], "junk-free != raw in a gated arm"

    # ---- G00: byte-identity vs the frozen amend-3 twin ------------------
    if not GATED and not SMOKE:
        twin_tag = "%s_s%d" % (TWIN, SEED)
        with open(os.path.join(ROOT, "archives",
                               "QDA3_%s_archive.json" % twin_tag)) as f:
            twin_recs = json.load(f)
        key = lambda r: (r["genotype_digest"], r["phenotype_digest"],
                         round(r["dev_score"], 9))
        xchecks["archive_equals_QDA3_twin"] = (
            sorted(map(key, recs)) == sorted(map(key, twin_recs)))
        assert xchecks["archive_equals_QDA3_twin"], \
            "G00 archive drifted from the frozen QDA3 twin %s" % twin_tag
        with open(os.path.join(ROOT, "results", "QDA3_%s.json" % twin_tag)) as f:
            ref = json.load(f)
        if best is not None:
            xchecks["best_dev_equals_QDA3"] = \
                abs(best - ref["best_dev_T2"]) < 1e-9
            assert xchecks["best_dev_equals_QDA3"], \
                "G00 best_dev %r != frozen %r" % (best, ref["best_dev_T2"])
        frozen_own = ref[OWN_AXIS]
        xchecks["own_axis_equals_QDA3"] = \
            abs(raw_recovery - frozen_own) < 1e-6
        assert xchecks["own_axis_equals_QDA3"], \
            "G00 %s %r != frozen %r" % (OWN_AXIS, raw_recovery, frozen_own)
        # cross-check the scored HZD9R layer when the bar is the census median
        if BAR == A5["quality_gate_amend5"]["census_median_bar_hz9"]:
            hz = os.path.join(ROOT, "results", "HZD9R_%s.json" % twin_tag)
            if os.path.exists(hz):
                with open(hz) as f:
                    hzr = json.load(f)
                xchecks["junk_free_equals_HZD9R"] = \
                    abs(clean_recovery - hzr["junk_free_own_axis_recovery"]) < 1e-6
                assert xchecks["junk_free_equals_HZD9R"], \
                    "G00 junk-free %r != frozen HZD9R %r" % (
                        clean_recovery, hzr["junk_free_own_axis_recovery"])

    frontier = sorted(rets, key=lambda x: -x[0])[:32]
    frontier_retention = (sum(1 for _, r in frontier if r > 1e-9) / len(frontier)
                          if frontier else 0.0)
    receipt = make_receipt("qda5-%s-s%d" % (ARM, SEED),
                           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           os.environ.get("ZOO_HOST", "local"), "T2-amend5",
                           config_digest())
    for r in sorted(recs, key=lambda x: x["phenotype_digest"]):
        append_record(receipt, len(receipt["chain"]),
                      {"p": r["phenotype_digest"][:16]})
    assert verify_receipt(receipt), "receipt chain broken"
    out = {
        "run_id": "qda5-%s-s%d" % (ARM, SEED), "arm": ARM, "seed": SEED,
        "amendment": A5["amendment_id"], "tier": "T2",
        "gated": GATED, "admission_bar": bar,
        "algorithm": "P05_map_elites", "archive": AXIS,
        "own_axis": OWN_AXIS,
        "budget": BUDGET, "evals": res["evals"],
        "feasible_found": res["feasible_found"],
        "n_admissible_feasible": res.get("n_admissible_feasible"),
        "wall_s": round(elapsed, 3), "cpu_hours": round(elapsed / 3600.0, 6),
        "n_elites": len(recs),
        "pareto_recovery_T2": round(len(pareto & PARETO_T2) / DEN["PARETO_T2"], 6),
        "D2d_cell_recovery": round(len(d2 & D2_CELLS) / DEN["D2d@10_occupied"], 6),
        "D3d_cell_recovery": round(len(d3 & D3_CELLS) / DEN["D3d@10_occupied"], 6),
        "raw_own_axis_recovery": round(raw_recovery, 6),
        "junk_free_own_axis_recovery": round(clean_recovery, 6),
        "junk_free_ratio": round(clean_recovery / raw_recovery, 6)
        if raw_recovery > 0 else None,
        "best_dev_T2": best, "min_dev_elite": min_dev,
        "qd_score_T2": res.get("qd_score"),
        "frontier_retention_fraction": round(frontier_retention, 6),
        "retention_positive_elite_fraction": round(
            sum(1 for _, r in rets if r > 1e-9) / len(rets), 6) if rets else None,
        "xchecks_passed": xchecks,
        "receipt_head": receipt["head_sha256"],
        "host": os.environ.get("ZOO_HOST", "local"),
    }
    os.makedirs(os.path.join(ROOT, "manifests", "receipts"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    tag = "%s_s%d" % (ARM, SEED)
    with open(os.path.join(ROOT, "results", "%s_%s.json" % (PREFIX, tag)), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(ROOT, "manifests", "receipts",
                           "%s_%s.receipt.json" % (PREFIX, tag)), "w") as f:
        json.dump(receipt, f)
    with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, tag)), "w") as f:
        f.write("ok\n")
    if not SMOKE:
        with open(os.path.join(ROOT, "archives",
                               "QDA5_%s_archive.json" % tag), "w") as f:
            json.dump(recs, f)
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # retain the crash, never overwrite with success
        tag = "%s_s%d" % (ARM, SEED)
        os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
        with open(os.path.join(ROOT, "results", "%s_%s.status" % (PREFIX, tag)), "w") as f:
            f.write("fail %r\n" % e)
        raise
