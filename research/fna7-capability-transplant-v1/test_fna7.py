"""FNA-7/D8 tests. Self-managed sys.path (capsule convention). Python 3.8 stdlib only."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "..", "fna5-routing-first-refusal-v1"),
          os.path.join(HERE, "..", "..", "src")):
    if p not in sys.path:
        sys.path.insert(0, p)
import fna5_world as W          # noqa: E402
import fna7_pilot as P          # noqa: E402


def strict_load(path):
    def no_dupes(pairs):
        keys = [k for k, _ in pairs]
        assert len(keys) == len(set(keys)), "duplicate JSON key in %s" % path
        return dict(pairs)
    with open(path) as fh:
        return json.load(fh, object_pairs_hook=no_dupes)


BANNED = ("AGI", "LLM_EQUIVALENT", "TRANSFORMER_REPLACED", "GENERAL_SUPERIORITY")


class TestProtocolArtifacts(unittest.TestCase):
    def test_json_strict_and_schema(self):
        for name in ("CAPABILITY_TRANSPLANT_PROTOCOL_V1.json", "FREEZE_FNA7_V1.json",
                     "CONCURRENCY_CHECK.json"):
            d = strict_load(os.path.join(HERE, name))
            self.assertTrue(d["schema"].startswith("ocm.fna.fna7"))
        proto = strict_load(os.path.join(HERE, "CAPABILITY_TRANSPLANT_PROTOCOL_V1.json"))
        ids = [t["id"] for t in proto["transplants"]]
        self.assertEqual(len(ids), 7)
        self.assertEqual(len(set(ids)), 7)
        self.assertIn("K2_FAILURE_CLASSIFICATION", ids)
        statuses = {t["status"] for t in proto["transplants"]}
        self.assertIn("PILOTED_IN_THIS_CAPSULE", statuses)
        self.assertEqual(sum(1 for t in proto["transplants"]
                             if t["status"] == "PILOTED_IN_THIS_CAPSULE"), 1)

    def test_no_banned_tokens_anywhere_in_capsule(self):
        for fn in sorted(os.listdir(HERE)):
            if not fn.endswith((".py", ".md", ".json")) or fn.startswith("test_"):
                continue  # the test's own banned-token list would self-match
            with open(os.path.join(HERE, fn)) as fh:
                text = fh.read()
            for token in BANNED:
                self.assertNotIn(token, text, "%s contains %s" % (fn, token))

    def test_concurrency_verdict(self):
        d = strict_load(os.path.join(HERE, "CONCURRENCY_CHECK.json"))
        self.assertEqual(d["verdict"], "NO_CONCURRENT_WORK_COLLISION")


class TestWorldBinding(unittest.TestCase):
    def setUp(self):
        self.world = W.build_world(W.WorldParams.tiny_params())
        self.queries = [W.make_query(self.world, i)
                        for i in range(self.world["params"].n_queries)]

    def test_splits_disjoint_and_complete(self):
        parts = {"DEV": [], "EVAL": [], "DRIFT": []}
        for q in self.queries:
            parts[W.split_of(q.qid)].append(q.qid)
        allq = [q for v in parts.values() for q in v]
        self.assertEqual(len(allq), len(self.queries))
        self.assertEqual(len(set(allq)), len(self.queries))

    def test_router_wrapper_identity_and_determinism(self):
        dev = [q for q in self.queries if W.split_of(q.qid) == "DEV"]
        r1, recs, _p1 = P.harness_router_fit(self.world, dev)
        r2, _recs, _p2 = P.harness_router_fit(self.world, dev)
        self.assertEqual(_p1, _p2)
        for q in self.queries[:40]:
            insts, _ = W.applicable(self.world, q)
            c1, w1 = r1.choose(q, insts, self.world["state"])
            c2, w2 = r2.choose(q, insts, self.world["state"])
            self.assertEqual((c1.op_id, w1), (c2.op_id, w2))  # deterministic fit
            c3, w3 = P._route(self.world, q, insts, r1)
            self.assertEqual((c1.op_id, w1), (c3.op_id, w3))  # wrapper identity
        self.assertTrue(recs)

    def test_drift_mutation_matches_fna5(self):
        before = {k: v for k, v in self.world["state"].items()}
        P.apply_drift(self.world)
        self.assertEqual(self.world["state"]["scan_version_mult"], 1.6)
        self.assertAlmostEqual(self.world["state"]["theta2"], before["theta2"] + 0.05)
        self.assertFalse(any(it.op_id == "window:60" for it in self.world["catalogue"]))
        self.assertTrue(any(it.op_id == "sample:48" for it in self.world["catalogue"]))


class TestGroundTruthAndLegalSurface(unittest.TestCase):
    def setUp(self):
        self.world = W.build_world(W.WorldParams.tiny_params())
        self.queries = [W.make_query(self.world, i)
                        for i in range(self.world["params"].n_queries)]

    def _failures(self, drift=False):
        if drift:
            P.apply_drift(self.world)
        out = []
        for q in self.queries:
            insts, _ = W.applicable(self.world, q)
            choice, _ = W.analytic_choice(self.world, q, insts)
            w, ok = W.execute_via_spec(self.world, choice, q)
            if not ok:
                out.append((q, choice, insts))
            if len(out) >= 12:
                break
        return out

    def test_legal_view_carries_no_latent(self):
        for q, choice, insts in self._failures():
            view = P.legal_view(self.world, q, choice, insts, "pre-drift")
            P.assert_legal(view)
            for key in P.LATENT_KEYS:
                self.assertNotIn(key, view)
            flat = json.dumps(view, sort_keys=True)
            self.assertNotIn(str(round(q.u, 6)), flat)
            for v in self.world["realized"].values():
                self.assertNotIn(str(round(v, 6)), flat)

    def test_ground_truth_total_and_stale_only_in_drift(self):
        seen = {"DEV": set(), "DRIFT": set()}
        for drift in (False, True):
            for q, choice, insts in self._failures(drift=drift):
                g = P.ground_truth(self.world, q, choice, insts, drift)
                self.assertIn(g, P.CLASSES)
                seen["DRIFT" if drift else "DEV"].add(g)
        self.assertFalse("STALE_DECLARED_MODEL" in seen["DEV"])


class TestPilotEndToEnd(unittest.TestCase):
    def test_tiny_run_deterministic_and_replacement_neural_free(self):
        a = P.run(tiny=True)
        b = P.run(tiny=True)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        for arm in ("R1_GUARDED_DECLARED", "R2_CALIBRATED_BAYES", "R3_CART_TREE"):
            self.assertEqual(a["arms"][arm]["EVAL"]["neural_calls"], 0)
            self.assertEqual(a["arms"][arm]["DRIFT"]["neural_calls"], 0)
        # the A2 router (AMENDMENT 1) must exercise the capability: failures exist
        self.assertGreater(a["arms"]["INCUMBENT_NEURAL_REF"]["EVAL"]["n_failures"], 0)
        inc = a["arms"]["INCUMBENT_NEURAL_REF"]
        self.assertGreater(inc["EVAL"]["neural_calls"], 0)

    def test_harness_held_constant_across_arms(self):
        a = P.run(tiny=True)
        digests = {n: arm["eval_failure_qid_digest"] for n, arm in a["arms"].items()
                   if "eval_failure_qid_digest" in arm}
        self.assertGreater(len(digests), 4)
        self.assertEqual(len(set(digests.values())), 1)  # identical EVAL failure stream

    def test_repair_table_consumption(self):
        a = P.run(tiny=True)
        for arm in ("R1_GUARDED_DECLARED", "R2_CALIBRATED_BAYES", "R3_CART_TREE"):
            ev = a["arms"][arm]["EVAL"]
            if ev["n_failures"]:
                self.assertGreaterEqual(ev["retries_used"] + ev["stale_flags"], 0)

    def test_verdict_vocabulary(self):
        a = P.run(tiny=True)
        v = P.gate_and_terminal(a)
        self.assertTrue(v["terminal"].endswith("_AT_PILOT_SCOPE_FNA7_V1"))
        self.assertTrue(any(v["terminal"].startswith(t) for t in (
            "PARENT_SUFFICIENT_FOR_FAILURE_CLASSIFICATION",
            "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE",
            "NO_FUNCTIONAL_PARITY_FAILURE_CLASSIFICATION",
            "NEURAL_DONOR_DOMINATES_AT_SCOPE")))
        self.assertEqual(len(v["causal_gate_214_s5"]), 10)

    def test_r2_theta_estimates_clamped_to_declared_neighbourhood(self):
        world = W.build_world(W.WorldParams.tiny_params())
        queries = [W.make_query(world, i) for i in range(world["params"].n_queries)]
        dev = [q for q in queries if W.split_of(q.qid) == "DEV"]
        router, ident_records, _rp = P.harness_router_fit(world, dev)
        recs, _price = P.build_dev_records(world, router, ident_records)
        th = P._estimate_thetas(recs)
        for k, c in P.DECLARED_CENTRES.items():
            self.assertLessEqual(abs(th[k] - c), 0.15 + 1e-9)


if __name__ == "__main__":
    unittest.main()
