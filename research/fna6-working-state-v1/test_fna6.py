"""Tests for the FNA-6 working-state capsule (#214 section 4, FNA-6).

Run from the repo root:
    python3 -m unittest discover -s research/fna6-working-state-v1 -p 'test_*.py'

Covers: strict-JSON load (duplicate-key rejection) of the freeze/results files,
per-arm exactness on a hand-built conjunctive fixture through admission,
revocation and catalogue drift, the honest parent failure patterns (P1A stale
after revocation/drift, P3 stale after any update) with their pre-registered
levers recovering them (P1B, P3R), interference-detector teeth on a forced
crosstalk fixture (goal-unbinding mutant caught; goal-scoped Soar clean),
incumbent-mirror agreement with production gated_closure, and the static-world
no-alarm control.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import world as W  # noqa: E402
from actr import ActrArm  # noqa: E402
from arms import IncumbentArm, RescanArm  # noqa: E402
from blackboard import BlackboardArm  # noqa: E402
from contract import ExactChecker  # noqa: E402
from ocm.kso.navigation import gated_closure  # noqa: E402
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace  # noqa: E402
from ocm.kso.warrant import WarrantProfile  # noqa: E402
from run_fna6 import build_arms  # noqa: E402
from soar_wm import SoarArm  # noqa: E402


def _no_dupes(pairs):
    keys = [k for k, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate object key: %s" % [k for k in keys if keys.count(k) > 1])
    return dict(pairs)


def strict_loads(text: str):
    return json.loads(text, object_pairs_hook=_no_dupes)


def wp(ev):
    return WarrantProfile.certified([frozenset([ev])])


def tiny_field():
    """a0->a1->a2; a3->a4; conjunctive (a1,a3)->a5. Warrants on evidence 0."""
    atoms = tuple(Atom("a%d" % i, "claim", wp(0)) for i in range(6))
    edges = (
        Hyperedge("e1", ("a0",), ("a1",), "DEPENDENCE", warrant=wp(0)),
        Hyperedge("e2", ("a1",), ("a2",), "DEPENDENCE", warrant=wp(0)),
        Hyperedge("e3", ("a3",), ("a4",), "DEPENDENCE", warrant=wp(0)),
        Hyperedge("e4", ("a1", "a3"), ("a5",), "COMPOSITION", warrant=wp(0)),
    )
    return KnowledgeSpace(atoms, edges)


def crosstalk_field():
    atoms = tuple(Atom("b%d" % i, "claim", wp(0)) for i in range(4))
    edges = (
        Hyperedge("f1", ("b0",), ("b1",), "DEPENDENCE", warrant=wp(0)),
        Hyperedge("f2", ("b1",), ("b2",), "DEPENDENCE", warrant=wp(0)),
    )
    return KnowledgeSpace(atoms, edges)


def replay_fixture(arm):
    """10 serves around admission (a2->a3), revocation of evidence 1, drift
    (retract e1, kill a2). Returns list of (label, verdict)."""
    field = tiny_field()
    arm.open(field, ["a0", "a3"])
    checker = ExactChecker()
    rv = set()
    out = []

    def serve(ob, seed, target, ks, rvs, label):
        ans, consulted = arm.serve(ob, seed, target, ks, rvs)
        truth = target in gated_closure(ks, [seed], rvs)
        v = checker.check(len(out), ob, target, ans, truth,
                          consulted, arm.resident(1 - ob))
        arm.res.verdicts.append(v)
        out.append((label, v))
        return v

    ks = field
    serve(0, "a0", "a1", ks, rv, "A:ob0-a1")
    serve(0, "a0", "a5", ks, rv, "A:ob0-a5-conj")
    serve(1, "a3", "a4", ks, rv, "A:ob1-a4")
    serve(1, "a3", "a1", ks, rv, "A:ob1-a1")

    m1 = Hyperedge("m1", ("a2",), ("a3",), "DEPENDENCE", warrant=wp(1))
    ks = ks.with_edges(m1)
    arm.apply_admission({"kind": "admission", "after": 3, "_edges": [m1]}, ks, rv)
    checker.note_update("admission")
    serve(0, "a0", "a5", ks, rv, "B:ob0-a5-merged")
    serve(1, "a3", "a4", ks, rv, "B:ob1-a4")

    rv = {1}
    arm.apply_revocation({"kind": "revocation", "after": 5, "evidence": 1}, ks, rv)
    checker.note_update("revocation")
    serve(0, "a0", "a5", ks, rv, "C:ob0-a5-swept")
    serve(0, "a0", "a1", ks, rv, "C:ob0-a1")

    before = ks.edge_view["e1"]
    ks = ks.without(edge_ids=["e1"])
    old = ks.atom("a2")
    ks = ks.replace_atom(Atom("a2", old.atom_type, WarrantProfile.zero(),
                              quarantined=old.quarantined))
    arm.apply_drift({"kind": "drift", "after": 7, "edge_id": "e1", "atom_id": "a2",
                     "_edge_before": before}, ks, rv)
    checker.note_update("drift")
    serve(0, "a0", "a1", ks, rv, "D:ob0-a1-drifted")
    serve(1, "a3", "a4", ks, rv, "D:ob1-a4")
    return out


class StrictJson(unittest.TestCase):
    def test_freeze_loads_strict(self):
        doc = strict_loads((HERE / "FREEZE_FNA6_V1.json").read_text())
        self.assertEqual(doc["schema"], "ocm.fna6.working-state.freeze.v1")
        self.assertTrue(doc["declared_before_first_scored_run"])
        self.assertIn("P2_MUTANT_NO_GOAL_BINDING", doc["arms"])

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError):
            strict_loads('{"a": 1, "a": 2}')

    def test_results_if_present_load_strict(self):
        p = HERE / "RESULTS_FNA6_V1.json"
        if not p.exists():
            self.skipTest("no scored run yet")
        doc = strict_loads(p.read_text())
        self.assertEqual(doc["schema"], "ocm.fna6.working-state.results.v1")


class FixtureLifecycle(unittest.TestCase):
    """Exactness through build/serve/merge/sweep/drift on the conjunctive fixture."""

    def _wrong(self, arm):
        return [lbl for lbl, v in replay_fixture(arm) if not v.exact]

    def test_incumbent_exact(self):
        self.assertEqual(self._wrong(IncumbentArm()), [])

    def test_rescan_exact(self):
        self.assertEqual(self._wrong(RescanArm()), [])

    def test_soar_exact(self):
        self.assertEqual(self._wrong(SoarArm("P2_SOAR_WM", goal_scoped=True)), [])

    def test_versioned_blackboard_exact(self):
        self.assertEqual(self._wrong(BlackboardArm("P1B_BLACKBOARD_VERSIONED", True)), [])

    def test_actr_revalidate_exact(self):
        self.assertEqual(self._wrong(ActrArm("P3R_ACTR_REVALIDATE", revalidate=True)), [])

    def test_append_only_blackboard_fails_only_after_revocation(self):
        """L1 motivation: no retraction primitive -> stale after sweep/drift only."""
        wrong = self._wrong(BlackboardArm("P1A_BLACKBOARD_APPEND", False))
        self.assertEqual(sorted(wrong), ["C:ob0-a5-swept", "D:ob0-a1-drifted"])

    def test_plain_actr_fails_only_after_updates(self):
        """L2 motivation: no encoding pathway -> stale after admission onward.
        (C is accidentally right: the chunk that was never learned because the
        admission was not encoded coincides with the post-revocation truth.)"""
        wrong = self._wrong(ActrArm("P3_ACTR_STRICT_BUFFERS", revalidate=False))
        self.assertEqual(sorted(wrong),
                         ["B:ob0-a5-merged", "D:ob0-a1-drifted"])

    def test_every_arm_answers_the_conjunctive_gate_correctly_at_build(self):
        for arm in build_arms():
            res = [(lbl, v) for lbl, v in replay_fixture(arm)]
            a5 = next(v for lbl, v in res if lbl == "A:ob0-a5-conj")
            self.assertFalse(a5.answer or a5.truth, arm.code)
            merged = next(v for lbl, v in res if lbl == "B:ob0-a5-merged")
            self.assertTrue(merged.truth)


class InterferenceDetector(unittest.TestCase):
    def _run(self, arm):
        field = crosstalk_field()
        arm.open(field, ["b0", "b3"])
        checker = ExactChecker()
        v0 = None
        v1 = None
        ans, cons = arm.serve(0, "b0", "b1", field, frozenset())
        v0 = checker.check(0, 0, "b1", ans, True, cons, arm.resident(1))
        arm.res.verdicts.append(v0)
        ans, cons = arm.serve(1, "b3", "b2", field, frozenset())
        truth = "b2" in gated_closure(field, ["b3"], frozenset())
        v1 = checker.check(1, 1, "b2", ans, truth, cons, arm.resident(0))
        arm.res.verdicts.append(v1)
        return v0, v1

    def test_mutant_crosstalk_is_caught_as_interference(self):
        _, v1 = self._run(SoarArm("P2_MUTANT_NO_GOAL_BINDING", goal_scoped=False))
        self.assertFalse(v1.exact)
        self.assertTrue(v1.interference, "detector must attribute the wrong answer "
                                          "to shared working-set objects")
        self.assertTrue(v1.consulted_other)

    def test_goal_scoped_soar_is_clean_on_the_same_fixture(self):
        _, v1 = self._run(SoarArm("P2_SOAR_WM", goal_scoped=True))
        self.assertTrue(v1.exact)
        self.assertFalse(v1.consulted_other)


class HarnessAgreement(unittest.TestCase):
    def test_incumbent_mirror_agrees_with_production(self):
        field = tiny_field()
        arm = IncumbentArm()
        arm.open(field, ["a0"])
        for seed in ("a0", "a3"):
            _, consulted = arm.serve(0, seed, "a5", field, frozenset())
            self.assertEqual(consulted, set(gated_closure(field, [seed], frozenset())))
        m1 = Hyperedge("m1", ("a2",), ("a3",), "DEPENDENCE", warrant=wp(1))
        ks = field.with_edges(m1)
        arm.apply_admission({"kind": "admission", "after": 0, "_edges": [m1]}, ks, {1})
        _, consulted = arm.serve(0, "a0", "a5", ks, {1})
        self.assertEqual(consulted, set(gated_closure(ks, ["a0"], frozenset({1}))))

    def test_static_world_no_alarm(self):
        field = tiny_field()
        st = W.static_stream(field, ["a0", "a3"], serves_per_ob=4)
        for arm in build_arms():
            if "MUTANT" in arm.code:
                continue  # labelled probe: wrong by design on shared-object worlds
            arm.open(field, ["a0", "a3"])
            checker = ExactChecker()
            for i, ev in enumerate(st["events"]):
                ans, cons = arm.serve(ev["ob"], ev["seed"], ev["target"],
                                      field, frozenset())
                truth = ev["target"] in gated_closure(field, [ev["seed"]], frozenset())
                v = checker.check(i, ev["ob"], ev["target"], ans, truth,
                                  cons, arm.resident(1 - ev["ob"]))
                arm.res.verdicts.append(v)
                self.assertTrue(v.exact, "%s wrong on static world at %d" % (arm.code, i))
            self.assertFalse([v for v in arm.res.verdicts
                              if v.interference or v.stale_revocation or v.merge_failure])


if __name__ == "__main__":
    unittest.main()
