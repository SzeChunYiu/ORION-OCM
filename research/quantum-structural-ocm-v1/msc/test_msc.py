"""MSC V1 test suite: exactness invariants the causal gate depends on.

Run from the repo root:

    python3 -m unittest discover -s research/quantum-structural-ocm-v1/msc -p 'test_*.py'

Everything here is invariant validation on small salted worlds (own test salts, disjoint
from the frozen scored salts): the instrumented closure equals production gated_closure,
the counting-block quotient refutes exactly, the confirmation stage never confirms a
negative, every arm matches production ground truth on the stream, the hostile pair has
byte-identical quotients with different correct D2 decisions, and the shuffle null runs.

Python 3.8-compatible syntax.
"""
from __future__ import annotations

import json
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for p in (str(HERE), str(REPO / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ocm.kso.navigation import gated_closure  # noqa: E402
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace  # noqa: E402
from ocm.kso.warrant import WarrantProfile  # noqa: E402

import world  # noqa: E402
from arms import (Q0FullScan, Q1Indexed, Q2Quotient, Q3Subspace, Q4Probe,  # noqa: E402
                  Q5Composed, instrumented_closure)
from probing import ProbeField, probe_decide  # noqa: E402
from quotient import Quotient, confirm_on_induced  # noqa: E402

T_SALT = "ocm-q216-msc-v1-20260909/test"
N_ATOMS, N_EDGES, N_EV = 90, 220, 12
N_TASKS, N_UPDATES = 8, 4


def small_world():
    field, meta = world.build_field(n_atoms=N_ATOMS, n_edges=N_EDGES, n_evidence=N_EV,
                                    salt=T_SALT + "/pop")
    stream = world.build_stream(field, n_tasks=N_TASKS, n_updates=N_UPDATES,
                                salt_tasks=T_SALT + "/tasks",
                                salt_updates=T_SALT + "/updates")
    return field, meta, stream


def random_revoked(field, rng, n=4):
    ev = [e for e in field.evidence_universe()]
    return frozenset(str(x) for x in rng.sample(ev, min(n, len(ev))))


class TestClosureMirror(unittest.TestCase):
    def test_instrumented_equals_production(self):
        field, meta, _ = small_world()
        rng = random.Random(17)
        ids = [a.atom_id for a in field.atoms]
        for _ in range(12):
            s = rng.choice(ids)
            t = rng.choice(ids)
            rv = random_revoked(field, rng)
            prod = gated_closure(field, [s], rv)
            for use_index in (True, False):
                res = instrumented_closure(field, [s], rv, use_index=use_index)
                self.assertEqual(res["reached"], prod,
                                 "mirror diverged (use_index=%s)" % use_index)

    def test_mirror_equals_production_after_updates(self):
        field, meta, stream = small_world()
        seen = 0
        for kind, item, ks, rv in world.stream_apply(field, stream):
            if kind != "task":
                continue
            seen += 1
            prod = gated_closure(ks, [item["s"]], rv)
            self.assertEqual(instrumented_closure(ks, [item["s"]], rv)["reached"], prod)
        self.assertEqual(seen, N_TASKS)


class TestQuotient(unittest.TestCase):
    def test_refutation_is_exact(self):
        field, meta, _ = small_world()
        q = Quotient(field)
        rng = random.Random(31)
        ids = [a.atom_id for a in field.atoms]
        checked_neg = checked_pos = 0
        for _ in range(25):
            s, t = rng.choice(ids), rng.choice(ids)
            rv = random_revoked(field, rng)
            truth = t in gated_closure(field, [s], rv)
            view = q.split_singletons([s, t])
            res = view.counting_closure(s, rv, t, early_stop=True)
            if res["refuted"]:
                self.assertFalse(truth, "quotient refuted a true positive")
                checked_neg += 1
            else:
                checked_pos += 1
        self.assertGreater(checked_neg, 0, "no negative exercised")
        self.assertGreater(checked_pos, 0, "no positive exercised")

    def test_confirmation_never_confirms_negative(self):
        field, meta, _ = small_world()
        q = Quotient(field)
        rng = random.Random(43)
        ids = [a.atom_id for a in field.atoms]
        for _ in range(25):
            s, t = rng.choice(ids), rng.choice(ids)
            rv = random_revoked(field, rng)
            truth = t in gated_closure(field, [s], rv)
            view = q.split_singletons([s, t])
            res = view.counting_closure(s, rv, t, early_stop=True)
            if res["refuted"]:
                continue
            blocks = view.path_blocks(res, s, t)
            members = [view.blocks[b] for b in blocks] or [view.blocks[view.partition[t]]]
            ok, met, witness = confirm_on_induced(field, s, t, rv, members)
            if ok:
                self.assertTrue(truth, "induced confirmation confirmed a negative")
                self.assertIn(t, witness)
                self.assertIn(s, witness)

    def test_serialize_deterministic(self):
        field, meta, _ = small_world()
        a = json.dumps(Quotient(field).serialize(), sort_keys=True)
        b = json.dumps(Quotient(field).serialize(), sort_keys=True)
        self.assertEqual(a, b)


class TestArmsExact(unittest.TestCase):
    def _replay(self, arm, field, stream):
        arm.on_field(field)
        recs = []
        for kind, item, ks, rv in world.stream_apply(field, stream):
            if kind == "task":
                truth = world.ground_truth(ks, item["s"], item["t"], rv)
                rec = arm.decide(item["s"], item["t"], rv, truth)
                self.assertTrue(rec["correct"], "%s diverged on task %s"
                                % (arm.name, item["idx"]))
                rec["task_idx"] = item["idx"]
                recs.append(rec)
            elif item["kind"] == "admission":
                arm.on_admission(ks, item["_edges"])
            else:
                arm.on_revocation(item["evidence"])
        self.assertEqual(len(recs), N_TASKS)
        return recs

    def test_q0_q1_q3(self):
        field, meta, stream = small_world()
        for arm in (Q0FullScan(), Q1Indexed(), Q3Subspace()):
            self._replay(arm, field, stream)

    def test_q2_base_and_e1(self):
        field, meta, stream = small_world()
        self._replay(Q2Quotient(), field, stream)
        self._replay(Q2Quotient(incremental=True), field, stream)

    def test_q4_policies(self):
        field, meta, stream = small_world()
        self._replay(Q4Probe(policy="rarity"), field, stream)
        self._replay(Q4Probe(policy="naive"), field, stream)
        arm = Q4Probe(policy="shuffle", salt=T_SALT + "/shuffle")
        self._replay(arm, field, stream)

    def test_q5_and_ablations(self):
        field, meta, stream = small_world()
        for kwargs in ({}, {"use_quotient": False}, {"use_cone": False},
                       {"use_probe": False}, {"incremental": True},
                       {"probe_policy": "naive"}):
            self._replay(Q5Composed(**kwargs), field, stream)

    def test_decisions_ordering_independent(self):
        field, meta, stream = small_world()

        def decisions(arm):
            return [(r["task_idx"], r["decision"]) for r in self._replay(arm, field, stream)]
        base = decisions(Q5Composed())
        self.assertEqual(base, decisions(Q5Composed(probe_policy="naive")))
        self.assertEqual(base, decisions(Q5Composed(incremental=True)))


class TestShuffleNull(unittest.TestCase):
    def test_null_at_q4_budget(self):
        field, meta, stream = small_world()
        q4 = Q4Probe(policy="rarity")
        q4recs = self._replay_and_return(q4, field, stream)
        null = Q4Probe(policy="shuffle", salt=T_SALT + "/shuffle")
        null.on_field(field)
        i = 0
        for kind, item, ks, rv in world.stream_apply(field, stream):
            if kind != "task":
                continue
            null.budget = q4recs[i]["probes"]
            truth = world.ground_truth(ks, item["s"], item["t"], rv)
            rec = null.decide(item["s"], item["t"], rv, truth)
            self.assertLessEqual(rec["probes"], q4recs[i]["probes"] + 1,
                                 "null exceeded the equal-n budget")
            i += 1

    def _replay_and_return(self, arm, field, stream):
        arm.on_field(field)
        recs = []
        for kind, item, ks, rv in world.stream_apply(field, stream):
            if kind == "task":
                truth = world.ground_truth(ks, item["s"], item["t"], rv)
                rec = arm.decide(item["s"], item["t"], rv, truth)
                self.assertTrue(rec["correct"])
                recs.append(rec)
            elif item["kind"] == "admission":
                arm.on_admission(ks, item["_edges"])
            else:
                arm.on_revocation(item["evidence"])
        return recs


class TestHostileFQ5(unittest.TestCase):
    def _pair(self):
        field, meta, _ = small_world()
        return world.hostile_pair(field, meta["planted"]), meta

    def test_quotients_byte_identical_decisions_differ(self):
        (F_A, F_B), meta = self._pair()
        ser_a = json.dumps(Quotient(F_A).serialize(), sort_keys=True)
        ser_b = json.dumps(Quotient(F_B).serialize(), sort_keys=True)
        self.assertEqual(ser_a, ser_b, "F_A/F_B quotients are not isomorphic")
        # ...while the correct D2 decisions differ:
        for p in meta["planted"]:
            amap_a, amap_b = F_A.atom_view, F_B.atom_view
            ca = [m for m in p["twins"] if amap_a[m].authority.rank("custody") >= 2]
            cb = [m for m in p["twins"] if amap_b[m].authority.rank("custody") >= 2]
            self.assertEqual(len(ca), 1)
            self.assertEqual(len(cb), 1)
            self.assertNotEqual(ca[0], cb[0])

    def test_q2_insufficient_then_reopened(self):
        (F_A, F_B), meta = self._pair()
        for F, want_twins in ((F_A, meta["planted"][0]["twins"]),
                              (F_B, meta["planted"][0]["twins"])):
            arm = Q2Quotient()
            arm.on_field(F)
            res = arm.serve_d2(F, list(want_twins), build=False)
            self.assertEqual(
                res["status"],
                "REPRESENTATION_INSUFFICIENT__MISSING_COORDINATE_FOUND")
            amap = F.atom_view
            truth = [m for m in want_twins
                     if amap[m].authority.rank("custody") >= 2][0]
            self.assertEqual(res["decision"], truth)
            self.assertTrue(res["insufficient_then_reopened"])

    def test_native_arms_separate_pair(self):
        (F_A, F_B), meta = self._pair()
        twins = list(meta["planted"][0]["twins"])
        for make in (Q0FullScan, Q1Indexed, Q3Subspace, lambda: Q4Probe(policy="rarity")):
            arm_a, arm_b = make(), make()
            arm_a.on_field(F_A)
            arm_b.on_field(F_B)
            ra = arm_a.serve_d2(F_A, twins)
            rb = arm_b.serve_d2(F_B, twins)
            self.assertNotEqual(ra["decision"], rb["decision"])
            truth_a = [m for m in twins if F_A.atom_view[m].authority.rank("custody") >= 2][0]
            truth_b = [m for m in twins if F_B.atom_view[m].authority.rank("custody") >= 2][0]
            self.assertEqual(ra["decision"], truth_a)
            self.assertEqual(rb["decision"], truth_b)
            self.assertIn(ra["status"], ("NATIVE_IDENTITY", "NATIVE_IDENTITY_VIA_PROBES"))


class TestRegressionCountingSoundness(unittest.TestCase):
    """Regressions for the counting-soundness defects found after the first scored run
    (commit f6fa0b6: every quotient-consuming arm false-refuted one true positive,
    task idx 30 s=v125 t=v258 at 480/1280; caught by the causal-gate zero-margin
    exactness item). Root cause: the counting closure skipped a whole qedge when any
    HEAD block was dead, while production gated_closure fires the edge and admits the
    live heads individually. The remap-after-split merge defect below is the second,
    latent unsoundness found by inspection in the same audit."""

    def test_dead_head_block_still_admits_live_heads(self):
        # one edge x -> (h1, h2); h2's block is dead under R, h1's is live.
        atoms = (Atom("x", "query_seed"),
                 Atom("h1", "claim"),
                 Atom("h2", "claim",
                      WarrantProfile.certified([frozenset(["ev_dead"])])))
        edges = (Hyperedge("e", ("x",), ("h1", "h2"), "SUPPORT"),)
        ks = KnowledgeSpace(atoms, edges)
        rv = frozenset(["ev_dead"])
        self.assertIn("h1", gated_closure(ks, ["x"], rv))
        self.assertNotIn("h2", gated_closure(ks, ["x"], rv))
        q = Quotient(ks)
        view = q.split_singletons(["x", "h1"])
        res = view.counting_closure("x", rv, "h1", early_stop=True)
        self.assertFalse(res["refuted"],
                         "dead head block killed the whole qedge firing")

    def test_split_regroups_classes_never_merges(self):
        # x,y bisimilar; e1: x->c1, e2: y->c2 share one quotient-edge class. Splitting
        # x and c1 out must REGROUP the class (two qedges), not merge it into one
        # qedge demanding both {x} and {y} counted before firing.
        atoms = (Atom("x", "claim"), Atom("y", "claim"),
                 Atom("c1", "observation"), Atom("c2", "observation"))
        edges = (Hyperedge("e1", ("x",), ("c1",), "SUPPORT"),
                 Hyperedge("e2", ("y",), ("c2",), "SUPPORT"))
        ks = KnowledgeSpace(atoms, edges)
        q0, q1 = Quotient(ks), Quotient(ks)
        self.assertEqual(q0.partition["x"], q0.partition["y"])
        self.assertEqual(q0.partition["c1"], q0.partition["c2"])
        self.assertEqual(len(q0.qedges), 1)  # e1, e2 in one class pre-split
        view = q0.split_singletons(["x", "c1"])
        self.assertEqual(len(view.qedges), 2)  # regrouped, not merged
        res = view.counting_closure("x", frozenset(), "c1", early_stop=True)
        self.assertIn("c1", gated_closure(ks, ["x"], frozenset()))
        self.assertFalse(res["refuted"],
                         "merged split class refuted a true positive")
        # the true negative on the same view stays exactly refuted:
        res_neg = view.counting_closure("y", frozenset(), "c1", early_stop=True)
        self.assertNotIn("c1", gated_closure(ks, ["y"], frozenset()))
        self.assertTrue(res_neg["refuted"])
        # E1 maintenance path uses the same regrouping: every maintained qedge's
        # multiset matches the multisets of its own concrete edges.
        e3 = Hyperedge("e3", ("c1",), ("x",), "SUPPORT")
        ks2 = ks.with_edges(e3)
        q1.incremental_maintain(ks2, [e3])
        for q in q1.qedges:
            for eid in q.concrete:
                e = ks2.edge_view[eid]
                tl, hd = {}, {}
                for t in e.tails:
                    tl[q1.partition[t]] = tl.get(q1.partition[t], 0) + 1
                for h in e.heads:
                    hd[q1.partition[h]] = hd.get(q1.partition[h], 0) + 1
                self.assertEqual(tuple(sorted(tl.items())), q.tails)
                self.assertEqual(tuple(sorted(hd.items())), q.heads)

    def test_q2_exact_at_scored_scale(self):
        """The scored configuration itself: Q2 base and E1 replay the frozen stream exactly."""
        field, meta = world.build_field(n_atoms=480, n_edges=1280, n_evidence=24)
        stream = world.build_stream(field, n_tasks=32, n_updates=10)
        for arm in (Q2Quotient(), Q2Quotient(incremental=True)):
            arm.on_field(field)
            n = 0
            for kind, item, ks, rv in world.stream_apply(field, stream):
                if kind == "task":
                    truth = world.ground_truth(ks, item["s"], item["t"], rv)
                    rec = arm.decide(item["s"], item["t"], rv, truth)
                    self.assertTrue(rec["correct"],
                                    "%s diverged on task %s" % (arm.name, item["idx"]))
                    n += 1
                elif item["kind"] == "admission":
                    arm.on_admission(ks, item["_edges"])
                else:
                    arm.on_revocation(item["evidence"])
            self.assertEqual(n, 32)


class TestFreezeAndDeterminism(unittest.TestCase):
    def test_stream_deterministic(self):
        f1, m1, s1 = small_world()
        f2, m2, s2 = small_world()
        self.assertEqual([t["s"] for t in s1["tasks"]], [t["s"] for t in s2["tasks"]])
        self.assertEqual([t["t"] for t in s1["tasks"]], [t["t"] for t in s2["tasks"]])
        self.assertEqual(s1["final_revoked"], s2["final_revoked"])

    def test_measure_bytes_positive_and_stable(self):
        f, m, _ = small_world()
        a = world.measure_bytes(world.field_snapshot(f))
        b = world.measure_bytes(world.field_snapshot(f))
        self.assertEqual(a, b)
        self.assertGreater(a, 1000)

    def test_freeze_file_present(self):
        self.assertTrue((HERE / "FREEZE_MSC_V1.json").exists(),
                        "FREEZE_MSC_V1.json must exist before the first scored run")


if __name__ == "__main__":
    unittest.main()
