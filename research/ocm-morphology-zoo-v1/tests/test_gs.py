"""GS-R0/R1 tests (#221 sec 18 + GS-R1h): successive halving honesty,
novelty archive impls (builtin + ribs factory contract), surrogate impls
(builtin + sklearn), weighted sampler (adaptive batches), checkpoint tool
on an isolated root, freeze refusal guards, gs_run batch-spec frozen-key
guard.  Run on billy-laptop, never the Mac:
  cd research/ocm-morphology-zoo-v1 && python3 -m pytest tests/test_gs.py -q
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from morphology.direct_genome import random_genome  # noqa: E402
from morphology.gs_bound import gs_uniform_sample, weighted_sampler  # noqa: E402
from search.novelty_viability import NoveltyArchive, make_novelty_archive  # noqa: E402
from search.surrogate_allocate import EnsembleSurrogate  # noqa: E402
from search.successive_halving import run_successive_halving  # noqa: E402


def _fake_rec(i, feasible=True):
    return {"feasible": feasible, "phenotype_digest": "pd%d" % i,
            "genome": {"U": ["memory"] * (1 + i % 3)},
            "evaluation": {"persistent_bytes": float(i)}}


def test_sh_counts_honest_and_progress_emitted():
    lines = []
    res = run_successive_halving(t0_budget=54, seed=0, n0=27,
                                 on_progress=lambda p: lines.append(p))
    assert res["counts"]["T0"] == 54
    assert res["eta"] == 3
    assert lines, "on_progress never fired"
    assert lines[-1]["round"] >= lines[0]["round"]
    assert all("counts" in p and "elapsed_s" in p for p in lines)


def test_builtin_archive_admission_and_tiebreak():
    a = NoveltyArchive(cap=8, floor=2)
    for i in range(6):
        assert a.consider(_fake_rec(i), (0.1 * i, 0.0, 0.0, 0.0))
    assert a.size() == 6
    assert not a.consider(_fake_rec(6), (0.1, 0.0, 0.0, 0.0))  # dup vec
    # simpler duplicate wins the slot (1 unit beats 2)
    assert a.records["pd6"]["genome"]["U"] == ["memory"]
    assert "pd1" not in a.records


def test_archive_factory_contract():
    b = make_novelty_archive("builtin", cap=16, floor=4)
    assert b.impl == "builtin"
    try:
        from ribs.archives import ProximityArchive  # noqa: F401
        have_ribs = True
    except Exception:
        have_ribs = False
    if have_ribs:
        r = make_novelty_archive("ribs", cap=16, floor=4, k=15, seed=0)
        assert r.impl == "ribs"
        for i in range(5):
            assert r.consider(_fake_rec(i),
                              (0.2 * i, 0.1 * i, 0.05 * i, 0.02 * i))
        assert r.size() == 5
    else:
        try:
            make_novelty_archive("ribs", cap=16, floor=4)
        except RuntimeError as e:
            assert "ProximityArchive" in str(e)
        else:
            raise AssertionError("ribs must raise, not silently fall back")
    try:
        make_novelty_archive("nonsense")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown impl must raise")


def test_surrogate_impls_builtin_and_sklearn():
    rng = random.Random(1)
    for impl in ("builtin", "sklearn"):
        try:
            sur = EnsembleSurrogate(seed=0, impl=impl)
        except ImportError:
            assert impl == "sklearn"
            continue
        recs = [{"genome": gs_uniform_sample(rng).to_json_obj(),
                 "feasible": (i % 2 == 0)} for i in range(20)]
        sur.train_t0(recs)
        assert sur.stats["n_train_t0"] == 20
        g = gs_uniform_sample(rng)
        pv = sur.p_viable(g)
        assert 0.0 <= pv <= 1.0
        assert 0.0 <= sur.allocation_score(g)
        assert sur.stats["surrogate_impl"] == impl


def test_weighted_sampler_allocation_only():
    rng = random.Random(7)
    sam = weighted_sampler({"units": 1.0, "farch": 0.0}, rng)
    picks = set()
    for _ in range(30):
        g = sam(rng)
        picks.add(g.F_arch)
    # lane units samples the units lane: never drifts into other lanes'
    # F_arch values outside the lane's support — all genomes remain legal
    from morphology.compile import compile_genome
    for _ in range(10):
        compile_genome(sam(rng))
    assert picks, "sampler produced nothing"
    # determinism: two fresh samplers with the same seed draw identical
    # streams (rng consumed only by the sampler itself)
    ra, rb = random.Random(9), random.Random(9)
    da = weighted_sampler({"units": 0.7, "obasis": 0.3}, ra)
    db = weighted_sampler({"units": 0.7, "obasis": 0.3}, rb)
    for _ in range(10):
        assert da(ra).to_json_obj() == db(rb).to_json_obj()


def _make_ckpt_root(tmp):
    os.makedirs(os.path.join(tmp, "manifests"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "results"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json"), tmp)
    shutil.copy(os.path.join(ROOT, "manifests", "GS_R1_TASKS.json"),
                os.path.join(tmp, "manifests"))
    fake = {"counts": {"T0": 100, "T1": 30, "T2": 9},
            "viable_counts": {"T0": 9}, "cpu_hours": 0.02,
            "deadline_hit": False, "n_archive": 7,
            "survivors": [{"phenotype_digest": "p%d" % i} for i in range(3)]}
    rid = "GS_R1_GSA1_units_s0"
    json.dump(fake, open(os.path.join(tmp, "results", rid + ".json"), "w"))
    open(os.path.join(tmp, "results", rid + ".status"), "w").write("ok\n")
    open(os.path.join(tmp, "results", rid + ".progress.jsonl"), "w").write(
        json.dumps({"ts": "2026-09-09T00:00:00Z", "round": 1,
                    "counts": {"T0": 40, "T1": 0, "T2": 0},
                    "viable_counts": {"T0": 4},
                    "novelty_archive_size": 5}) + "\n")
    return tmp


def test_checkpoint_tool_isolated_root():
    """Skips gracefully before the campaign freeze exists on this host."""
    if not os.path.exists(os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")):
        import pytest
        pytest.skip("no freeze yet on this host")
    tmp = _make_ckpt_root(tempfile.mkdtemp(prefix="gsck_test_"))
    try:
        p = subprocess.run(
            [sys.executable, os.path.join(ROOT, "hpc", "checkpoint_gs.py"),
             tmp], capture_output=True, text=True)
        assert p.returncode == 0, p.stderr[-500:]
        lines = open(os.path.join(tmp, "results",
                                  "GS_R1_CHECKPOINTS.jsonl")).read().splitlines()
        assert len(lines) == 1
        line = json.loads(lines[0])
        assert line["checkpoint"] == 1
        arm = line["arms"]["GSA1_units"]
        # completed task json wins over its stale progress line
        assert arm["tier_counts"]["T0"] == 100 and arm["completed"] == 1
        assert arm["viability_rate"] == 0.09
        st = json.load(open(os.path.join(tmp, "results", "GS_R1_STATUS.json")))
        assert st["partial_terminal_preview"].startswith("PARTIAL_")
        # second invocation appends, never rewrites
        subprocess.run([sys.executable,
                        os.path.join(ROOT, "hpc", "checkpoint_gs.py"), tmp],
                       capture_output=True, text=True, check=True)
        assert len(open(os.path.join(tmp, "results",
                                     "GS_R1_CHECKPOINTS.jsonl")).read()
                   .splitlines()) == 2
    finally:
        shutil.rmtree(tmp)


def test_freeze_refuses_without_env_probe():
    if not os.path.exists(os.path.join(ROOT, "GS_ENV_PROBE.json")):
        have = False
    else:
        have = True
    if have:
        return  # probe present on scoring hosts; refusal path untestable
    tmp = tempfile.mkdtemp(prefix="gsfrz_test_")
    try:
        os.makedirs(os.path.join(tmp, "results"), exist_ok=True)
        p = subprocess.run(
            [sys.executable, os.path.join(ROOT, "hpc", "freeze_gs.py"), tmp],
            capture_output=True, text=True)
        assert p.returncode != 0
        assert "GS_ENV_PROBE.json" in (p.stdout + p.stderr)
    finally:
        shutil.rmtree(tmp)


def test_gs_run_refuses_frozen_keys_in_batch_spec():
    if not os.path.exists(os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")):
        import pytest
        pytest.skip("no freeze yet on this host")
    tmp = tempfile.mkdtemp(prefix="gsspec_test_")
    try:
        spec = {"task_id": "GSAB1_x1", "base_arm": "GSA1",
                "eta": 2}  # frozen key — must be refused
        sp = os.path.join(tmp, "spec.json")
        json.dump(spec, open(sp, "w"))
        p = subprocess.run(
            [sys.executable, os.path.join(ROOT, "hpc", "gs_run.py"),
             ROOT, "GSA1_units", "0", sp],
            capture_output=True, text=True)
        assert p.returncode != 0, "frozen-key spec must be refused"
        assert "frozen keys" in (p.stdout + p.stderr)
    finally:
        shutil.rmtree(tmp)


def _code_digest(root):
    import hashlib
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(root, d, fn), "rb").read())
    return h.hexdigest()


def test_aggregate_folds_batch_tasks_into_arm_cells():
    """GS-R1h batch tasks are scored dispositions: a completed batch task
    with the frozen seed still missing must count in its base_arm cell
    (attempted/completed/evals/phenotypes) and must lift the aggregate out
    of CANNOT_CHECK_NO_SCORED_DISPOSITIONS; batch sweep shards beyond the
    frozen range fold into sweep totals without breaking frozen
    completeness semantics.  Self-contained: freeze fabricated here."""
    tmp = tempfile.mkdtemp(prefix="gsagg_test_")
    try:
        for d in ("morphology", "evaluation", "search", "hpc"):
            os.symlink(os.path.join(ROOT, d), os.path.join(tmp, d))
        os.makedirs(os.path.join(tmp, "manifests"))
        res = os.path.join(tmp, "results")
        os.makedirs(res)
        arms = {a: {"seeds": [0]} for a in (
            "GSA1_units", "GSA2_hetero", "GSA3_farch", "GSA4_obasis",
            "GSA5_surrogate", "GSR_random_control")}
        arms["GSE_sweep"] = {"shards": 2}
        freeze = {
            "schema": "GRAND_SEARCH_R1_FREEZE_V1", "code_digest":
                _code_digest(tmp),
            "arms": arms,
            "baselines_acceleration": {"frozen_baseline": {
                "arm": "P01_random_search_T2",
                "morphologies_per_cpu_hour": 1e-9,
                "definition": "test"}},
            "terminal_rules_first_match": [
                {"order": 1, "id": "CANNOT_CHECK_NO_SCORED_DISPOSITIONS",
                 "vocab": "CANNOT_CHECK_NO_SCORED_DISPOSITIONS"},
                {"order": 6, "id": "MIXED_INTERMEDIATE_NO_TERMINAL",
                 "vocab": "CANNOT_CHECK_PARTIAL_DISPOSITIONS"}],
            "heldout_t3": {"t3_key_id": "test", "key_sha256": "0" * 64},
            "t3_key": "gs-agg-test-key",
        }
        fpath = os.path.join(tmp, "GRAND_SEARCH_R1_FREEZE.json")
        json.dump(freeze, open(fpath, "w"))
        import hashlib
        fsha = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
        json.dump({"manifest_id": "GS_R1_TASKS_V1", "freeze_sha256": fsha,
                   "n_tasks": 8, "tasks": []},
                  open(os.path.join(tmp, "manifests", "GS_R1_TASKS.json"),
                       "w"))
        # batch task spec (per-task dir is the submission source of truth)
        bdir = os.path.join(tmp, "manifests", "GS_R1_BATCH_b1")
        os.makedirs(bdir)
        json.dump({"schema": "GS_R1_BATCH_TASK_V1", "batch_id": "b1",
                   "task_id": "GSAB1_x1", "base_arm": "GSA1_units",
                   "kind": "search"}, open(os.path.join(bdir,
                                                        "GSAB1_x1.json"),
                                            "w"))
        # batch task RESULT (frozen seed 0 deliberately absent)
        rng = random.Random(3)
        g1, g2 = gs_uniform_sample(rng), gs_uniform_sample(rng)
        rid = "GS_R1_GSAB1_x1"
        json.dump({"counts": {"T0": 50, "T1": 12, "T2": 4},
                   "viable_counts": {"T0": 10}, "cpu_hours": 0.01,
                   "survivors": [
                       {"phenotype_digest": "bp1", "genotype_digest": "g1",
                        "genome": g1.to_json_obj(), "F_arch": g1.F_arch,
                        "t2": {}},
                       {"phenotype_digest": "bp2", "genotype_digest": "g2",
                        "genome": g2.to_json_obj(), "F_arch": g2.F_arch,
                        "t2": {}}]},
                  open(os.path.join(res, rid + ".json"), "w"))
        open(os.path.join(res, rid + ".status"), "w").write("ok\n")
        # batch sweep shard BEYOND the frozen range (frozen = c0..c1)
        json.dump({"n_evaluated": 40, "n_viable": 5, "cpu_hours": 0.02,
                   "by_F_arch": {"list_field": 5}},
                  open(os.path.join(res, "GS_R1_GSE_c7.json"), "w"))
        open(os.path.join(res, "GS_R1_GSE_c7.status"), "w").write("ok\n")
        p = subprocess.run(
            [sys.executable, os.path.join(ROOT, "hpc", "aggregate_gs.py"),
             tmp], capture_output=True, text=True)
        assert p.returncode == 0, (p.stdout + p.stderr)[-800:]
        out = json.load(open(os.path.join(res, "GS_R1_AGGREGATE.json")))
        a1 = out["arms"]["GSA1_units"]
        assert a1["attempted"] == 2 and a1["completed"] == 1
        assert "GS_R1_GSAB1_x1" in a1["completed_run_ids"]
        assert a1["distinct_t2_viable_phenotypes"] == 2
        assert out["terminal_rule_id"] != "CANNOT_CHECK_NO_SCORED_DISPOSITIONS"
        sw = out["sweep"]
        assert sw["attempted"] == 3 and sw["completed"] == 1
        assert sw["frozen_attempted"] == 2 and sw["frozen_completed"] == 0
        assert "GS_R1_GSE_c7" in sw["batch_shard_run_ids"]
        assert sw["n_evaluated"] == 40 and sw["n_viable"] == 5
        assert not sw["complete"]
    finally:
        shutil.rmtree(tmp)
