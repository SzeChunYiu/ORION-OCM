"""FNA-4 invariant tests. Own salts; no shared state with the scored suite.

Run (repo root):  python3 -m unittest discover \
    -s research/functional-neural-absorption-v1/fna4_library_synthesis -p 'test_*.py'
"""
from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import fna4
from fna4 import FORBIDDEN_CLAIMS, Work, gen_task, make_macro, run_chain, simulate
from fna4_solver import MisfireRegistry, solve_task, validate_selection_mirror
import fna4_learners as L


def _r(chain):
    return {"solved": True, "solution_chain": list(chain)}


class TestHarness(unittest.TestCase):
    def test_selection_mirror(self):
        self.assertTrue(validate_selection_mirror(fna4.INDEX))

    def test_all_families_solvable_and_deterministic(self):
        rng = random.Random(7101)
        tasks = [gen_task(rng, f, "H-%s-%d" % (f, i))
                 for f in ("F1", "F2", "F3") for i in range(3)]
        for t in tasks:
            a = solve_task(t)
            b = solve_task(t)
            self.assertTrue(a["solved"], t.task_id)
            self.assertFalse(a["capped"], t.task_id)
            self.assertEqual(a["work"], b["work"])
            self.assertEqual(a["solution_chain"], b["solution_chain"])

    def test_sort_direction_is_real(self):
        rng = random.Random(7102)
        t1 = gen_task(rng, "F1", "SD-1", force={"sd": "asc", "fmt": "csv", "fk": "f1",
                                                "sk": "f2", "af": "sum", "ak": "f0",
                                                "k": "2"})
        t2 = gen_task(rng, "F1", "SD-2", force={"sd": "desc", "fmt": "csv", "fk": "f1",
                                                "sk": "f2", "af": "sum", "ak": "f0",
                                                "k": "2"})
        a1 = run_chain(t1.true_chain, t1.initial)
        asc = simulate("sort:asc:f2", [t1.initial[0][2][1]])
        desc = simulate("sort:desc:f2", [t1.initial[0][2][1]])
        self.assertNotEqual(asc, desc)


class TestParents(unittest.TestCase):
    def test_au_least_generality(self):
        c1 = ("parse:csv", "filter:eq:f0", "agg:sum:f1", "scale:2")
        c2 = ("parse:jsonl", "filter:eq:f2", "agg:sum:f1", "scale:3")
        sk = L.anti_unify(c1, c2)
        self.assertIsNotNone(sk)
        self.assertIn(("filter", ("eq", None)), list(sk))
        self.assertIn(("agg", ("sum", "f1")), list(sk))
        # both parents instantiate the skeleton (soundness of the generalization)
        self.assertIsNotNone(L.match_skeleton(sk, c1))
        self.assertIsNotNone(L.match_skeleton(sk, c2))

    def test_chunk_is_exact_only(self):
        rng = random.Random(7103)
        acq = [gen_task(rng, "F1", "C-%d" % i) for i in range(3)]
        lib = L.learn_chunk([_r(t.true_chain) for t in acq], Work())
        self.assertTrue(all(not m.domains for m in lib))
        fresh = gen_task(rng, "F1", "C-fresh",
                         force={"fk": "f2", "af": "mean", "ak": "f0", "k": "3"})
        r = solve_task(fresh, macros=lib)
        self.assertEqual(r["macro_hits"], 0)

    def test_stitch_admits_useful_pattern(self):
        rng = random.Random(7104)
        acq = [gen_task(rng, "F1", "S-%d" % i,
                        force={"fmt": "csv", "fk": "f0", "af": "sum", "ak": "f1"})
               for i in range(3)]
        w = Work()
        lib = L.learn_stitch([_r(t.true_chain) for t in acq], w)
        self.assertGreaterEqual(len(lib), 1)
        self.assertGreater(w.learner_steps, 0)
        # fresh payload, exactly the first acquisition task's parameters
        c0 = acq[0].true_chain
        force = {"fmt": c0[0].split(":")[1], "fk": c0[1].split(":")[2],
                 "sd": c0[2].split(":")[1], "sk": c0[2].split(":")[2],
                 "af": c0[3].split(":")[1], "ak": c0[3].split(":")[2],
                 "k": c0[4].split(":")[1]}
        fresh = gen_task(rng, "F1", "S-fresh", force=force)
        r = solve_task(fresh, macros=lib)
        self.assertGreaterEqual(r["macro_hits"], 1)

    def test_egraph_ac_tighter_than_raw_au(self):
        rng = random.Random(7105)
        t1 = gen_task(rng, "F2", "E-1", force={"fmt_pair": ("csv", "jsonl"),
                                               "af": "sum", "ak": "f1"})
        t2 = gen_task(rng, "F2", "E-2", force={"fmt_pair": ("jsonl", "csv"),
                                               "af": "sum", "ak": "f1"})
        c1, c2 = tuple(t1.true_chain), tuple(t2.true_chain)
        self.assertNotEqual(c1[0], c2[0])
        self.assertEqual(L.canonicalize(c1, Work()), L.canonicalize(c2, Work()))
        raw_au = L.anti_unify(c1, c2)
        eg = L.learn_egraph([_r(c1), _r(c2)], Work())
        shape = [m for m in eg if list(m.families()) ==
                 ["parse", "parse", "merge", "dedupe", "agg"]]
        self.assertTrue(shape, [m.families() for m in eg])
        eg_sk = shape[0].skeleton
        au_holes = sum(1 for _f, s in raw_au for x in s if x is None)
        eg_holes = sum(1 for _f, s in eg_sk for x in s if x is None)
        self.assertLess(eg_holes, au_holes)

    def test_macro_charges_body_physics(self):
        rng = random.Random(7106)
        t = gen_task(rng, "F1", "M-1")
        sigs = [L.step_sig(n) for n in t.true_chain]
        m = make_macro(tuple(sigs), [sigs], label="T")
        w = Work()
        r = solve_task(t, macros=[m], work=w)
        self.assertGreaterEqual(r["macro_hits"], 1)
        self.assertGreaterEqual(w.simulations, len(t.true_chain))
        self.assertGreaterEqual(w.checker_calls, 1)


class TestExperience(unittest.TestCase):
    def test_nogood_sound_and_per_batch_saves_sims(self):
        rng = random.Random(7107)
        tasks = [gen_task(rng, "F2", "N-%d" % i) for i in range(4)]
        base = [solve_task(t) for t in tasks]
        reg = MisfireRegistry("per_batch")
        withreg = [solve_task(t, registry=reg) for t in tasks]
        self.assertTrue(all(r["solved"] for r in withreg))
        self.assertLess(sum(r["work"]["simulations"] for r in withreg),
                        sum(r["work"]["simulations"] for r in base))
        for key in reg.misfires:
            self.assertEqual(key[0].split(":")[0], "parse")

    def test_revocation_cone_exact(self):
        rng = random.Random(7108)
        acq = [gen_task(rng, "F1", "R-%d" % i) for i in range(2)] + \
              [gen_task(rng, "F2", "R2-%d" % i) for i in range(2)]
        lib = L.learn_stitch([_r(t.true_chain) for t in acq], Work())
        rv = {"ev:fam:filter"}
        for m in lib:
            self.assertEqual(m.warrant.is_live(rv), "filter" not in m.families())
        survivors = [m for m in lib if "filter" not in m.families()]
        self.assertTrue(survivors)
        t2 = gen_task(rng, "F2", "R-f2")
        r = solve_task(t2, macros=lib, revoked=rv)
        self.assertTrue(r["solved"])
        t1 = gen_task(rng, "F1", "R-f1")
        r1 = solve_task(t1, macros=lib, revoked=rv)
        self.assertFalse(r1["solved"])  # revoked family = capability gone by construction

    def test_ablation_regression_exact(self):
        rng = random.Random(7109)
        acq = [gen_task(rng, "F1", "A-%d" % i) for i in range(2)]
        lib = L.learn_stitch([_r(t.true_chain) for t in acq], Work())
        test = [gen_task(rng, "F1", "A-t%d" % i) for i in range(3)]
        removed = [solve_task(t, macros=()) for t in test]
        plain = [solve_task(t) for t in test]
        for a, b in zip(removed, plain):
            self.assertEqual(a["work"], b["work"])

    def test_cegis_refuses_empty_domain(self):
        sk = (("parse", ("csv",)), ("agg", (None, None)))
        insts = [[("parse", ("csv",)), ("agg", ("sum", "f0"))],
                 [("parse", ("csv",)), ("agg", ("mean", "f2"))]]
        m = make_macro(sk, insts, label="CE")
        self.assertEqual(len(m.domains[0]), 2)
        m2, ok = L.specialize(m, ("sum", "f0"), Work())
        self.assertTrue(ok)
        self.assertEqual(m2.domains[0], ("mean",))
        _m3, ok3 = L.specialize(m2, ("mean", "f2"), Work())
        self.assertFalse(ok3)  # REFUSED_EMPTY_DOMAIN
        _m4, ok4 = L.specialize(m2, ("mean",), Work())
        self.assertFalse(ok4)  # wrong-arity counterexample: refused, not crashed


class TestClaims(unittest.TestCase):
    def test_forbidden_claims_absent(self):
        # occurrence count 1 = the FORBIDDEN_CLAIMS definition itself; any second
        # occurrence is a claim smuggled into prose or a receipt
        for p in sorted(HERE.glob("*.py")) + sorted(HERE.glob("*.md")):
            txt = p.read_text()
            for c in FORBIDDEN_CLAIMS:
                self.assertLessEqual(txt.count(c), 1, (p.name, c))


if __name__ == "__main__":
    unittest.main()
