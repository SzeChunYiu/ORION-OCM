"""GS GPU/laptop lane tests (#221 sec 18, worker O).

Must run on CPython 3.8.10 (billy-laptop) AND 3.14.4 (billy-old):
stdlib-only assertions, typing.Dict-style generics, no f-strings, no
match, no walrus-in-comprehension tricks.  Runnable via
`python3 tests/test_gs_gpu_laptops.py` AND pytest.

The decisive assertion: the batched T0 tape is BIT-IDENTICAL to
evaluation.evaluate.evaluate_genome / lifetime.run_lifetime over the full
schema vocabulary (per-field sweeps + frozen-seed random samples), so the
"vectorized proxy" is the exact evaluation, not a correlate.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.descriptors import DESCRIPTOR_REGISTRY, descriptors_for  # noqa: E402
from evaluation.objectives import dev_score  # noqa: E402
from gpu import encode as genc  # noqa: E402
from gpu.batch_descriptors import descriptor_matrix, descriptors_for_batch  # noqa: E402
from gpu.firehose import (SMOKE_LABEL, genomes_random,  # noqa: E402
                          run_firehose, spec_to_genome)
from gpu.surrogate import (SurrogateEnsemble, rankdata_average,  # noqa: E402
                           spearman_rho)
from gpu.t0_tape import make_backend, run_t0_tape  # noqa: E402
from morphology.direct_genome import reference_kso_genome  # noqa: E402
from morphology.schema import (EXECUTIVE_FAMILIES, FIELD_FAMILIES,  # noqa: E402
                               LEARNING_FAMILIES, MEMORY_FAMILIES,
                               REVISION_FAMILIES, TOPOLOGY_FAMILIES)
from morphology.compile import InvariantViolation  # noqa: E402

TEST_N = int(os.environ.get("TEST_N", "240"))
RNG_SEED = 2210
try:
    import numpy as _np  # noqa: F401
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False


def _tape_one(genome):
    batch = genc.encode_batch([genome])
    return run_t0_tape(batch, make_backend("py"))[0]


def _assert_same(a, b, path, errs):
    if isinstance(a, bool) or isinstance(b, bool) or isinstance(a, int) \
            or isinstance(b, int) or isinstance(a, float) or isinstance(b, float):
        if float(a) != float(b):
            errs.append("%s: %r != %r" % (path, a, b))
    elif isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                errs.append("%s.%s missing in tape" % (path, k))
            elif k not in b:
                errs.append("%s.%s missing in cpu" % (path, k))
            else:
                _assert_same(a[k], b[k], "%s.%s" % (path, k), errs)
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            errs.append("%s: len %d != %d" % (path, len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                _assert_same(x, y, "%s[%d]" % (path, i), errs)
    else:
        if a != b:
            errs.append("%s: %r != %r" % (path, a, b))


def _field_sweep_genomes():
    """One genome per vocabulary value per field (full schema vocab, beyond
    the census bound), around a legal base spec."""
    base = {"F_arch": "flat_typed_relational", "extras": ["production_rule"],
            "T_family": "layered_dag", "Pi_arch": "exact_global_queue",
            "L": "none", "R": "dependency_cone_reopen", "K": "persistent_facts"}
    sweeps = [("F_arch", sorted(FIELD_FAMILIES)),
              ("T_family", list(TOPOLOGY_FAMILIES)),
              ("Pi_arch", sorted(EXECUTIVE_FAMILIES)),
              ("L", list(LEARNING_FAMILIES)),
              ("R", list(REVISION_FAMILIES)),
              ("K", list(MEMORY_FAMILIES))]
    out = []
    for field, values in sweeps:
        for v in values:
            spec = dict(base)
            spec[field] = v
            out.append((field, v, spec))
    # theta extremes (charged-parameter edges)
    for qb in (1, 4096):
        spec = dict(base)
        g = spec_to_genome(spec)
        g.theta["queue_budget"] = float(qb)
        out.append(("theta", "queue_budget=%d" % qb, g))
    for ib in (0.1, 8.0):
        g = spec_to_genome(dict(base))
        g.theta["index_build"] = ib
        out.append(("theta", "index_build=%s" % ib, g))
    # heterogeneous multi-unit body (n_modules>1, dead-unit-prone)
    out.append(("extras", "many", dict(
        base, extras=["production_rule", "exact_index", "constraint_solver",
                      "diagnostic_probe", "abstraction_schema"])))
    return out


class T0BitIdentity(unittest.TestCase):
    def _check(self, genome):
        cpu = evaluate_genome(genome, tier="T0", use_cache=False)
        tape = _tape_one(genome)
        errs = []
        _assert_same(cpu["evaluation"], tape["evaluation"], "ev", errs)
        _assert_same(cpu["gates"], tape["gates"], "gates", errs)
        if bool(cpu["feasible"]) != bool(tape["feasible"]):
            errs.append("feasible %r != %r" % (cpu["feasible"],
                                               tape["feasible"]))
        if cpu["phenotype_digest"] != tape.get("phenotype_digest"):
            errs.append("phenotype_digest mismatch")
        if dev_score(cpu["evaluation"]) != dev_score(tape["evaluation"]):
            errs.append("dev_score mismatch")
        self.assertEqual(errs, [], "tape != cpu: %s" % errs[:8])

    def test_reference_kso_genome(self):
        self._check(reference_kso_genome())

    def test_field_sweep_full_vocab(self):
        n_ok = n_skip = 0
        for field, value, spec in _field_sweep_genomes():
            g = spec if not isinstance(spec, dict) else spec_to_genome(spec)
            try:
                evaluate_genome(g, tier="T0", use_cache=False)
            except InvariantViolation:
                n_skip += 1
                continue
            self._check(g)
            n_ok += 1
        self.assertGreater(n_ok, 20, "field sweep tested too few genomes")

    def test_random_sample(self):
        for g in genomes_random(TEST_N, RNG_SEED):
            try:
                self._check(g)
            except InvariantViolation:
                continue


class BackendEquivalence(unittest.TestCase):
    def test_py_vs_numpy(self):
        if not HAS_NUMPY:
            self.skipTest("numpy absent")
        genomes = genomes_random(64, RNG_SEED + 1)
        batch = genc.encode_batch(
            [g for g in genomes if _compiles(g)])
        a = run_t0_tape(batch, make_backend("py"))
        b = run_t0_tape(batch, make_backend("numpy"))
        self.assertEqual(len(a), len(b))
        for ra, rb in zip(a, b):
            errs = []
            _assert_same(ra["evaluation"], rb["evaluation"], "ev", errs)
            _assert_same(ra["gates"], rb["gates"], "gates", errs)
            self.assertEqual(errs, [])


def _compiles(g):
    from morphology.compile import compile_genome
    try:
        compile_genome(g)
        return True
    except InvariantViolation:
        return False


class BatchDescriptorEquality(unittest.TestCase):
    def test_descriptor_matrix_equals_descriptors_for(self):
        genomes = [g for g in genomes_random(48, RNG_SEED + 2) if _compiles(g)]
        batch = genc.encode_batch(genomes)
        tape = run_t0_tape(batch, make_backend("py"))
        from morphology.compile import compile_genome
        for archive in ("S_structural_2d", "S_structural_3d", "B_behavior_2d"):
            got = descriptor_matrix(batch, tape, archive)
            reg = DESCRIPTOR_REGISTRY[archive]
            for i, g in enumerate(genomes):
                org = compile_genome(g)
                want = descriptors_for(org, tape[i]["evaluation"], archive)
                self.assertEqual([round(v, 9) for v in got[i]],
                                 [round(float(v), 9) for v in want],
                                 "archive %s row %d" % (archive, i))


class SurrogateTests(unittest.TestCase):
    def _problem(self, n=200, d=6, seed=7):
        import random as _r
        rng = _r.Random(seed)
        X = [[rng.uniform(-1, 1) for _ in range(d)] for _ in range(n)]
        y = [3.0 * row[0] - 2.0 * row[1] + 0.5 * row[2] ** 2
             + 0.1 * rng.gauss(0, 1) for row in X]
        return X, y

    def test_determinism_and_calibration(self):
        X, y = self._problem()
        s1 = SurrogateEnsemble(seed=5)
        s2 = SurrogateEnsemble(seed=5)
        s1.fit(X[:160], y[:160])
        s2.fit(X[:160], y[:160])
        p1, p2 = s1.predict(X[160:]), s2.predict(X[160:])
        self.assertEqual(p1, p2, "surrogate not deterministic")
        cal = s1.calibrate(X[160:], y[160:])
        self.assertGreater(cal["ensemble"], 0.85,
                           "ensemble spearman too low: %s" % cal)

    def test_ridge_only_path(self):
        X, y = self._problem(n=80, seed=11)
        s = SurrogateEnsemble(seed=5, use_torch=False, use_sklearn=False)
        self.assertEqual(s.fit(X, y)["members"], ["ridge_stdlib"])
        cal = s.calibrate(X, y)
        self.assertGreater(cal["ridge_stdlib"], 0.85)

    def test_rank_and_spearman(self):
        self.assertEqual(rankdata_average([3.0, 1.0, 2.0, 2.0]), [4.0, 1.0, 2.5, 2.5])
        self.assertGreater(spearman_rho([1, 2, 3], [1, 2, 3]), 0.999)
        self.assertLess(spearman_rho([1, 2, 3], [3, 2, 1]), -0.999)


class FirehoseSmoke(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="gs_firehose_")

    def test_smoke_label_without_freeze(self):
        s = run_firehose("random", self.root, n=64, seed=RNG_SEED + 3,
                         backend_name="py", chunk=32, lane="test_laptop")
        self.assertEqual(s["label"], SMOKE_LABEL)
        self.assertGreater(s["n_evaluated"], 0)
        self.assertTrue(s["all_dispositions"])
        ck = os.path.join(self.root, "results", "GS_R1_CHECKPOINTS.jsonl")
        self.assertTrue(os.path.exists(ck))
        lines = [json.loads(x) for x in open(ck) if x.strip()]
        self.assertEqual(lines[-1]["lane"], "test_laptop")
        st = json.load(open(os.path.join(self.root, "results",
                                         "GS_R1_STATUS.json")))
        self.assertIn("test_laptop", st["lanes"])
        # receipt chain verifies
        from evaluation.receipts import verify_receipt
        rj = json.load(open(os.path.join(
            self.root, "results", s["run_id"] + ".receipt.json")))
        self.assertTrue(verify_receipt(rj))

    def test_freeze_sha_gate(self):
        fz = os.path.join(self.root, "FREEZE.json")
        with open(fz, "w") as f:
            f.write('{"v": 1}\n')
        import hashlib
        sha = hashlib.sha256(open(fz, "rb").read()).hexdigest()
        s = run_firehose("random", self.root, n=16, seed=1,
                         backend_name="py", freeze_path=fz,
                         freeze_sha="0" * 64, lane="test_laptop")
        self.assertEqual(s["label"], SMOKE_LABEL)  # wrong sha -> smoke
        s2 = run_firehose("random", self.root, n=16, seed=2,
                          backend_name="py", freeze_path=fz,
                          freeze_sha=sha, lane="test_laptop")
        self.assertEqual(s2["label"], "SCORED_GS_R1")

    def test_manifest_mode(self):
        man = os.path.join(self.root, "man.json")
        specs = [{"F_arch": "flat_typed_relational", "extras": ["production_rule"],
                  "T_family": "layered_dag", "Pi_arch": "exact_global_queue",
                  "L": "none", "R": "dependency_cone_reopen",
                  "K": "persistent_facts"},
                 {"F_arch": "kso_reference", "extras": ["exact_index"],
                  "T_family": "central_blackboard_star",
                  "Pi_arch": "blackboard_bidding_agenda",
                  "L": "scoped_nogood", "R": "full_rescan",
                  "K": "episodic_store"}]
        with open(man, "w") as f:
            json.dump(specs, f)
        s = run_firehose("manifest", self.root, manifest_path=man,
                         backend_name="py", lane="test_laptop")
        self.assertEqual(s["n_evaluated"], 2)

    def test_replicate_tagging(self):
        s = run_firehose("random", self.root, n=16, seed=2210,
                         backend_name="py", lane="laptop_billy_replicate",
                         tag="REPLICATE_NEVER_SELECTION")
        self.assertIn("REPLICATE_NEVER_SELECTION", s["run_id"])
        self.assertEqual(s["label"], SMOKE_LABEL)


class MeasureFractionTests(unittest.TestCase):
    def test_measure_writes_summary(self):
        from gpu.measure_fraction import measure
        root = tempfile.mkdtemp(prefix="gs_measure_")
        s = measure(root, n=24, seed=RNG_SEED)
        self.assertEqual(s["fidelity"]["dev_score_mismatches"], 0)
        self.assertEqual(s["fidelity"]["spearman_proxy_vs_exact"], 1.0)
        self.assertGreater(s["fraction"]["vectorizable_fraction_of_T0"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
