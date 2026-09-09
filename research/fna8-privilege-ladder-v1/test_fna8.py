"""FNA-8/D9 tests: harness validity, authority boundaries, ledger completeness,
no-oracle information surface, mock-never-scores, forbidden claims, determinism.

Runs the tiny configuration via the real CLI (subprocess, MOCK model mode) so
the tested artefact is the artefact the receipt comes from. Deterministic under
the frozen salt. Self-managed sys.path: no PYTHONPATH prerequisite.
"""
import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fna8_world as W                      # noqa: E402
from fna8_model import _parse_codex_tail    # noqa: E402

FORBIDDEN = ("TRANSFORMER_REPLACED", "LLM_EQUIVALENT", "GENERAL_SUPERIORITY", "AGI")


def run_cli(rung, out_path, extra=()):
    proc = subprocess.run(
        [sys.executable, str(HERE / "fna8.py"), "--rung", rung, "--model", "mock",
         "--tiny", "--out", str(out_path)] + list(extra),
        capture_output=True, text=True, timeout=900, cwd=str(HERE))
    if proc.returncode != 0:
        raise AssertionError("tiny run failed:\n%s" % proc.stderr[-4000:])
    return json.loads(Path(out_path).read_text())


def _strip_volatile(receipt):
    r = json.loads(json.dumps(receipt))
    r.pop("generated_at_utc", None)
    return r


class WorldTests(unittest.TestCase):
    def setUp(self):
        self.params = W.WorldParams.tiny_params()
        self.world = W.build_world(self.params)

    def test_determinism(self):
        w2 = W.build_world(self.params)
        self.assertEqual([q.qid for q in self.world["queries"]],
                         [q.qid for q in w2["queries"]])
        for a, b in zip(self.world["queries"], w2["queries"]):
            self.assertEqual(a.slice_ids, b.slice_ids)
            self.assertEqual(a.disp, b.disp)
            self.assertEqual(a.theta_q, b.theta_q)

    def test_splits_partition(self):
        counts = {"DEV": 0, "EVAL": 0, "DRIFT": 0}
        for q in self.world["queries"]:
            counts[W.split_of(q.qid)] += 1
        self.assertEqual(sum(counts.values()), self.params.n_queries)
        self.assertTrue(all(v > 0 for v in counts.values()))

    def test_check_exactness(self):
        atoms = self.world["atoms"]
        wrong = 0
        for q in self.world["queries"]:
            ok, _ = W.check(q, atoms, q.exact_answer(atoms))
            self.assertTrue(ok)
            bad = ("AGG", q.true_mass(atoms) + Fraction(1, 100))
            okb, _ = W.check(q, atoms, bad)
            wrong += int(okb)
        self.assertEqual(wrong, 0)

    def test_prompt_information_surface(self):
        """The controller/proposer prompt carries NO realized constants, no
        split membership, no oracle internals — structurally."""
        evalq = [q for q in self.world["queries"] if W.split_of(q.qid) == "EVAL"]
        for q in evalq[:10]:
            for propose in (False, True):
                text = W.render_prompt(q, self.world, propose=propose)
                self.assertNotIn("realized", text)
                self.assertNotIn("true_mass", text)
                for marker in ("DRIFT", "DEV", "EVAL"):
                    self.assertNotIn(marker, text)
                # declared centres are public
                self.assertIn("0.35", text)
                # realized draws differ from centres; none may appear verbatim
                for inst in self.world["catalogue"]:
                    for key in ("theta1c", "theta3s", "theta4", "theta7"):
                        val = inst.realized[key]
                        if abs(val - W.DECLARED_CENTRES[key]) > 1e-9:
                            self.assertNotIn("%.6f" % val, text)

    def test_controller_parser(self):
        q = [x for x in self.world["queries"] if x.task_flag][0]
        op_id, ans = W.parse_controller_line(q, "CTRL|scan|12.34")
        self.assertEqual(op_id, "scan")
        self.assertEqual(ans, ("AGG", Fraction("12.34")))
        with self.assertRaises(ValueError):
            W.parse_controller_line(q, "ANS|scan|12.34")
        with self.assertRaises(ValueError):
            W.parse_controller_line(q, "")
        q2 = [x for x in self.world["queries"] if not x.task_flag][0]
        op2, ans2 = W.parse_controller_line(q2, "CTRL|probe:0|5.67|HIGH")
        self.assertEqual(ans2[2], True)
        with self.assertRaises(ValueError):
            W.parse_controller_line(q2, "CTRL|probe:0|5.67|MAYBE")

    def test_proposal_parser(self):
        legal = [i.op_id for i in self.world["catalogue"]]
        self.assertEqual(W.parse_proposal("PROP|scan|probe:0|window:16", legal),
                         ["scan", "probe:0", "window:16"])
        self.assertEqual(W.parse_proposal("PROP|bogus|scan", legal), ["scan"])
        with self.assertRaises(ValueError):
            W.parse_proposal("PROP|bogus|alsobogus", legal)
        with self.assertRaises(ValueError):
            W.parse_proposal("CTRL|scan", legal)


class CodexTailTests(unittest.TestCase):
    def test_parse_probe_layout(self):
        stdout = "noise\ncodex\nCTRL|scan|12.34\ntokens used\n19,130\nCTRL|scan|12.34\n"
        r = _parse_codex_tail(stdout)
        self.assertEqual(r["tokens"], 19130)
        self.assertEqual(r["message"], "CTRL|scan|12.34")

    def test_parse_failures(self):
        self.assertIn("parse_failure", _parse_codex_tail("no markers here"))
        self.assertIn("parse_failure",
                      _parse_codex_tail("codex\nhi\ntokens used\nnot-a-number\n"))


class _ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp = tempfile.mkdtemp(prefix="fna8-test-")
        cls.r6 = run_cli("6", str(Path(cls.tmp) / "r6.json"))
        cls.r1 = run_cli("1", str(Path(cls.tmp) / "r1.json"))
        cls.r2 = run_cli("2", str(Path(cls.tmp) / "r2.json"))


class RunTests(_ReceiptTests):
    LEDGER_AXES = ("capability_source", "model_usage", "state_growth",
                   "acquisition_work", "reasoning_work", "verifier_work",
                   "maintenance_and_revision", "capability")

    def _ledgers(self, receipt, path):
        node = receipt[path]
        return node["ledgers"] if "ledgers" in node else {"arm": node["ledger"]}

    def test_ledger_axes_complete(self):
        for receipt, path in ((self.r6, "rung6"), (self.r1, "rung1"), (self.r2, "rung2")):
            for arm, led in self._ledgers(receipt, path).items():
                for axis in self.LEDGER_AXES:
                    self.assertIn(axis, led, "%s/%s missing %s" % (path, arm, axis))
                self.assertIsInstance(led["lifetime_logical_work"], int)

    def test_r6_exact_arms_perfect(self):
        for arm in ("A1_INCUMBENT", "A2_GUARDED"):
            self.assertEqual(self.r6["rung6"]["ledgers"][arm]["delivered_correct_rate"],
                             1.0, arm)

    def test_r6_determinism(self):
        again = run_cli("6", str(Path(self.tmp) / "r6b.json"))
        self.assertEqual(_strip_volatile(again), _strip_volatile(self.r6))

    def test_r1_records_and_boundary(self):
        led = self.r1["rung1"]["ledger"]
        self.assertIn("model", led["capability_source"])
        self.assertGreater(led["model_usage"]["calls"], 0)
        self.assertGreater(led["state_growth"]["event_rows"], 0)  # OCM records
        self.assertEqual(led["delivered_correct_rate"], 1.0)      # mock is a perfect ctrl

    def test_r2_commits_operator_answers(self):
        led = self.r2["rung2"]["ledger"]
        sources = set(led["capability_source"])
        self.assertNotIn("model", sources)  # model proposes; OCM commits
        self.assertTrue(sources & {"exact_probe", "exact_scan", "approx_window",
                                   "approx_sample"})
        for row in led["per_query"]:
            self.assertIn("proposal", row)

    def test_mock_never_scores(self):
        for r in (self.r1, self.r2):
            self.assertEqual(r["model_mode"], "MOCK")
            self.assertIn("no terminals evaluated", r["terminals"]["note"])

    def test_pending_rungs(self):
        for rung in ("R3", "R4", "R5"):
            self.assertEqual(self.r6["pending_rungs"][rung]["status"],
                             "RUNG_PENDING_ACTIVATION_GATE")

    def test_oracle_labelled_never_scored(self):
        self.assertIn("A0_ORACLE", self.r6["rung6"]["ledgers"])
        self.assertNotIn("A0_ORACLE", json.dumps(self.r6["terminals"]))

    def test_forbidden_tokens_absent(self):
        for r in (self.r6, self.r1, self.r2):
            blob = json.dumps(r)
            for tok in FORBIDDEN:
                self.assertNotIn(tok, blob)

    def test_r6_drift_and_revision_charged(self):
        for arm in ("A1_INCUMBENT", "A2_GUARDED"):
            led = self.r6["rung6"]["ledgers"][arm]
            self.assertGreater(led["maintenance_and_revision"]["drift_index_rebuild_work"], 0)
            self.assertGreater(led["maintenance_and_revision"]["revision_recompute_work"], 0)


class InterfaceRefusalTests(unittest.TestCase):
    """Amendment-1 classifier: a model arm whose every call was refused is an
    interface failure (CANNOT_CHECK_NO_MODEL_ACCESS), never a capability result."""

    def _refused_ledger(self):
        # shape-minimal ledger: calls placed, none ok, all queries scan-rescued
        return {"model_usage": {"calls": 29, "calls_ok": 0, "parse_failures": 29,
                                "tokens": 0, "wall_s": 968.2},
                "capability": {"n": 24, "first_pass": 0, "delivered_correct": 24,
                               "fallbacks": 24},
                "capability_source": {"exact_scan": 24},
                "delivered_correct_rate": 1.0, "per_query": []}

    def test_classifier_flags_refused_arm(self):
        from fna8 import _interface_refused
        self.assertTrue(_interface_refused(self._refused_ledger()))

    def test_classifier_passes_healthy_arm(self):
        from fna8 import _interface_refused
        led = self._refused_ledger()
        led["model_usage"]["calls_ok"] = 24
        led["model_usage"]["parse_failures"] = 5
        led["capability"]["fallbacks"] = 5
        self.assertFalse(_interface_refused(led))

    def test_refused_arm_terminal_is_cannot_check(self):
        from fna8 import evaluate_terminals
        r6 = json.loads((HERE / "FNA8_R6_FULL.json").read_text())["rung6"] \
            if (HERE / "FNA8_R6_FULL.json").exists() else {
                "ledgers": {"A1_INCUMBENT": {"delivered_correct_rate": 1.0,
                                             "lifetime_logical_work": 100},
                            "A2_GUARDED": {"delivered_correct_rate": 1.0,
                                           "lifetime_logical_work": 90}}}
        r1 = {"ledger": self._refused_ledger()}
        r2 = {"ledger": self._refused_ledger()}
        out = evaluate_terminals(r6, r1, r2, "CODEX")
        self.assertEqual(out["rungs"].get("R1"), "CANNOT_CHECK_NO_MODEL_ACCESS")
        self.assertEqual(out["rungs"].get("R2"), "CANNOT_CHECK_NO_MODEL_ACCESS")
        self.assertIn(out["rungs"].get("R6"),
                      ("PARENT_SUFFICIENT_FOR_obligation_control",
                       "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE",
                       "CANNOT_CHECK_HARNESS_FAILED_BASELINE"))

    def test_live_receipts_classified_as_refused(self):
        """The 2026-09-09 laptop receipts, verbatim, must classify as refused."""
        from fna8 import _interface_refused
        for rel in ("FNA8_R1_CODEX_INTERFACE_REFUSED.json",
                    "FNA8_R2_CODEX_INTERFACE_REFUSED.json"):
            path = HERE / rel
            if not path.exists():
                self.skipTest("refused receipt not present")
            receipt = json.loads(path.read_text())
            key = "rung1" if "R1" in rel else "rung2"
            self.assertTrue(_interface_refused(receipt[key]["ledger"]), rel)


class FreezeTests(unittest.TestCase):
    def test_freeze_hashes_match_if_present(self):
        freeze = HERE / "FREEZE_FNA8_V1.json"
        if not freeze.exists():
            self.skipTest("freeze not yet consolidated")
        import hashlib
        data = json.loads(freeze.read_text())
        for rel, want in data["sha256"].items():
            got = hashlib.sha256((HERE / rel).read_bytes()).hexdigest()
            self.assertEqual(got, want, rel)


if __name__ == "__main__":
    unittest.main()