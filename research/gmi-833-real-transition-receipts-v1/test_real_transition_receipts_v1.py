"""Tests for gmi-833-real-transition-receipts-v1.

Two layers:
1. Machinery tests (always run): amended blind classification hostiles,
   selection, licensed-band filter, and receipt construction on synthetic
   test fixtures that are explicitly NOT real evidence.
2. Real-artifact consistency tests (run when REAL_RUNS/ exists): the
   committed receipts/RESULT reproduce byte-exactly, every real receipt
   passes the protocol validator, custody references resolve, and the
   promotion state matches the protocol terminal.

Usage: python -I -B test_real_transition_receipts_v1.py [-v]
"""

from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG))

import real_transition_receipts_v1 as R  # noqa: E402


def synth_runs(sid: str, e0: float, floor_del: float, persist_delay: float,
               N: int = 4000, B: int = 96, p: float = 8.0):
    """Synthetic machinery fixture (NOT real evidence; never a receipt)."""
    lam = p * 0.5 / (2 * B)  # freeze formula lambda* = p*eta/(2B), eta=1/2
    per = lambda err, derr, ierr: {
        "err_all": err, "err_delay": derr, "err_imm": ierr,
        "N_delay": N, "N_imm": N, "train_seconds": 1.0, "seed": 1,
    }
    return {
        "system_id": sid, "source_path": "synthetic-fixture", "source_sha256": "0" * 64,
        "source_bytes": 1, "fallback_used": False, "T": 2 * N, "W": 8, "H": B // 4,
        "p": p, "seed": 1, "eta_registered": 0.5, "B_gru": B,
        "lambda_star": lam, "lambda_low": lam / 2, "lambda_high": 3 * lam / 2,
        "realized_eta": 0.5, "torch": "test", "numpy": "test",
        "candidates": {
            "c1": {"carried_state_bytes": 0,
                   "seeds_runs": [per(e0, floor_del, 0.0),
                                  per(e0, floor_del, 0.0)],
                   "err_all_median": e0, "param_count": 10},
            "c2": {"carried_state_bytes": B,
                   "seeds_runs": [per(persist_delay, persist_delay, 0.0),
                                  per(persist_delay, persist_delay, 0.0)],
                   "err_all_median": persist_delay, "param_count": 20},
        },
        "floor_witness_const0": {"err_imm": 0.5, "err_delay": 0.5, "err_all": 0.5,
                                 "N_imm": N, "N_delay": N},
        "wall_seconds": 1.0,
    }


class TestAmendedBlindRule(unittest.TestCase):
    def test_floor_setter_is_stateless(self):
        self.assertEqual(R.classify(0.0, 0.0, 1000, 0.40, 1000, 0.40), "STATELESS")

    def test_trained_persistent_classified(self):
        self.assertEqual(R.classify(96.0, 0.0, 1000, 0.02, 1000, 0.40), "PERSISTENT_STATE")

    def test_ambiguous_persistent_abstains(self):
        self.assertEqual(R.classify(96.0, 0.0, 1000, 0.38, 1000, 0.40), "ABSTAIN")

    def test_untrained_abstains(self):
        self.assertEqual(R.classify(96.0, 0.5, 1000, 0.02, 1000, 0.40), "ABSTAIN")

    def test_stateless_above_own_floor_abstains(self):
        self.assertEqual(R.classify(0.0, 0.0, 1000, 0.60, 1000, 0.40), "ABSTAIN")

    def test_rule_is_numeric_only(self):
        # the rule must be a pure function of numbers; family names cannot enter
        import inspect
        src = inspect.getsource(R.classify)
        for fam in ("mlp", "gru", "lstm", "rnn"):
            self.assertNotIn(fam, src.lower())


class TestLicensedBand(unittest.TestCase):
    def _wd(self, systems):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        for runs in systems:
            d = root / runs["system_id"]
            d.mkdir()
            (d / "runs.json").write_text(json.dumps(runs))
        return tmp, root

    def test_licensed_and_unlicensed_partition(self):
        good = synth_runs("S-good", 0.25, 0.45, 0.02)
        bad_band = synth_runs("S-badband", 0.05, 0.08, 0.02)
        bad_floor = synth_runs("S-badfloor", 0.25, 0.45, 0.44)
        tmp, root = self._wd([good, bad_band, bad_floor])
        with tmp:
            licensed, unlicensed = R.licensed_systems(root)
            self.assertEqual(licensed, ["S-good"])
            reasons = {u["system_id"]: u["reason"] for u in unlicensed}
            self.assertEqual(reasons["S-badband"], "E0_OUTSIDE_LICENSED_BAND")
            self.assertEqual(reasons["S-badfloor"], "PERSISTENT_DOES_NOT_BEAT_EMPIRICAL_FLOOR")

    def test_machinery_transition_end_to_end(self):
        # E0=0.25, B=96, lam*=p*eta/(2B)=1/48 -> persistent wins low, stateless high
        good = synth_runs("S-good", 0.25, 0.45, 0.02, B=96, p=8.0)
        tmp, root = self._wd([good])
        with tmp:
            arts = R.build_eval_artifacts(root)
            self.assertEqual(arts["S-good"]["low"]["winner_classification"], "PERSISTENT_STATE")
            self.assertEqual(arts["S-good"]["high"]["winner_classification"], "STATELESS")
            receipts = R.build_receipts(root, arts, ["S-good"])
            proto = R._load_protocol(PKG.parent.parent)
            self.assertEqual(proto.real_receipt_errors(receipts[0]), [])
            ev = proto.evaluate(receipts)
            # machinery only: one shape-valid receipt qualifies but five are needed
            self.assertEqual(ev["qualifying_count"], 1)
            self.assertEqual(ev["terminal"], "INSUFFICIENT_REAL_SYSTEM_EVIDENCE")

    def test_machinery_five_receipts_flip_terminal(self):
        systems = [synth_runs("S-%d" % i, 0.25, 0.45, 0.02) for i in range(5)]
        tmp, root = self._wd(systems)
        with tmp:
            arts = R.build_eval_artifacts(root)
            licensed, _ = R.licensed_systems(root)
            self.assertEqual(len(licensed), 5)
            receipts = R.build_receipts(root, arts, licensed)
            proto = R._load_protocol(PKG.parent.parent)
            ev = proto.evaluate(receipts)
            self.assertEqual(ev["qualifying_count"], 5)
            self.assertEqual(ev["terminal"], "REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE")

    def test_protocol_fixture_never_counts(self):
        # the protocol's own synthetic fixture (non-REAL evidence kind) never qualifies
        proto = R._load_protocol(PKG.parent.parent)
        fx = proto.protocol_fixture(0)  # evidence_kind PROTOCOL_FIXTURE
        self.assertEqual(proto.evaluate([fx])["qualifying_count"], 0)


class TestRealArtifacts(unittest.TestCase):
    """Layer 2: active only when REAL_RUNS/ is present (the shipped state)."""

    def test_result_reproduces_byte_exact(self):
        runs = PKG / "REAL_RUNS"
        result = PKG / "RESULT_V1.json"
        if not runs.exists() or not result.exists():
            self.skipTest("REAL_RUNS/RESULT not present (pre-outcome state)")
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            R.main()
        self.assertEqual(buf.getvalue(), result.read_text())

    def test_receipts_pass_protocol(self):
        receipts_f = PKG / "RECEIPTS_V1.json"
        runs = PKG / "REAL_RUNS"
        if not receipts_f.exists() or not runs.exists():
            self.skipTest("receipts not present (pre-outcome state)")
        proto = R._load_protocol(PKG.parent.parent)
        receipts = json.loads(receipts_f.read_text())
        self.assertGreaterEqual(len(receipts), 1)
        for r in receipts:
            self.assertEqual(proto.real_receipt_errors(r), [])
        ids = [r["system_id"] for r in receipts]
        self.assertEqual(len(ids), len(set(ids)), "duplicate system ids")

    def test_no_promotion_without_five(self):
        result_f = PKG / "RESULT_V1.json"
        if not result_f.exists():
            self.skipTest("RESULT not present")
        res = json.loads(result_f.read_text())
        term = res["protocol_evaluation"]["terminal"]
        n = res["protocol_evaluation"]["qualifying_count"]
        if term == "REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE":
            self.assertGreaterEqual(n, 5)
            self.assertTrue(res["scientific_row_earned"])
        else:
            self.assertEqual(term, "INSUFFICIENT_REAL_SYSTEM_EVIDENCE")
            self.assertFalse(res["scientific_row_earned"])

    def test_predictions_reference_freeze(self):
        receipts_f = PKG / "RECEIPTS_V1.json"
        if not receipts_f.exists():
            self.skipTest("receipts not present")
        for r in json.loads(receipts_f.read_text()):
            self.assertIn(R.FREEZE_COMMIT, r["prediction_ref"])
            self.assertTrue(r["prediction_frozen_before_outcome"])


if __name__ == "__main__":
    verb = "-v" in sys.argv
    unittest.main(verbosity=2 if verb else 1, exit=False)
