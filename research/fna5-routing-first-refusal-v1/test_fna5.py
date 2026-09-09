"""FNA-5/D7 tests: harness validity, controls, charging, terminals, forbidden claims.

Runs the tiny configuration via the real CLI (subprocess) so the tested artefact is the
artefact the receipt comes from. Deterministic under the frozen salt.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED_TERMINALS = {
    "PARENT_SUFFICIENT_FOR_ROUTING",
    "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE",
    "REPRESENTATION_INSUFFICIENT",
    "NO_FUNCTIONAL_PARITY_ROUTING",
    "CANNOT_CHECK_HARNESS_DISAGREES_WITH_NAIVE_SCAN",
}
FORBIDDEN = ("TRANSFORMER_REPLACED", "LLM_EQUIVALENT", "GENERAL_SUPERIORITY", "AGI",
             "ROUTER_AUTHORIZED", "DEPLOYED")


def run_tiny(out_path):
    proc = subprocess.run(
        [sys.executable, str(HERE / "fna5.py"), "--tiny", "--out", str(out_path)],
        capture_output=True, text=True, timeout=600, cwd=str(HERE))
    if proc.returncode != 0:
        raise AssertionError("tiny run failed:\n" + proc.stderr[-4000:])
    return json.loads(Path(out_path).read_text())


_RECEIPT = {}


class Fna5Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not _RECEIPT:
            with tempfile.TemporaryDirectory() as td:
                r1 = run_tiny(Path(td) / "r1.json")
                r2 = run_tiny(Path(td) / "r2.json")
            _RECEIPT["r1"], _RECEIPT["r2"] = r1, r2
        cls.r = _RECEIPT["r1"]

    def test_determinism(self):
        self.assertEqual(_RECEIPT["r1"]["receipt_digest"], _RECEIPT["r2"]["receipt_digest"])
        self.assertEqual(_RECEIPT["r1"]["arms_EVAL"], _RECEIPT["r2"]["arms_EVAL"])

    def test_schema_and_salt(self):
        self.assertEqual(self.r["schema"], "ocm.fna.fna5-routing-first-refusal.v1")
        self.assertEqual(self.r["salt"], "fna5-routing-first-refusal-v1::3f9c217a")

    def test_split_disjoint_and_complete(self):
        sys.path.insert(0, str(HERE))
        sys.path.insert(0, str(HERE.parents[1] / "src"))
        from fna5_world import split_of
        qids = ["q:%05d" % i for i in range(600)]
        sets = {"DEV": set(), "EVAL": set(), "DRIFT": set()}
        for q in qids:
            sets[split_of(q)].add(q)
        self.assertEqual(len(sets["DEV"] & sets["EVAL"]), 0)
        self.assertEqual(len(sets["DEV"] & sets["DRIFT"]), 0)
        self.assertEqual(len(sets["EVAL"] & sets["DRIFT"]), 0)
        self.assertEqual(sum(len(s) for s in sets.values()), len(qids))

    def test_terminal_registered(self):
        self.assertIn(self.r["terminal"], ALLOWED_TERMINALS)

    def test_oracle_labelled_and_not_first_refusal(self):
        self.assertIn("A0_ORACLE", self.r["arms_EVAL"])
        self.assertNotEqual(self.r["first_refusal_arm"], "A0_ORACLE")
        self.assertEqual(self.r["arms_EVAL"]["A0_ORACLE"]["first_pass_rate"], 1.0)

    def test_gate_71_unchanged(self):
        self.assertIn("LEARNED_ROUTER_NOT_YET_AUTHORIZED", self.r["gate_71"])
        self.assertIn("study-only", self.r["gate_71"])

    def test_no_forbidden_claims(self):
        blob = json.dumps(self.r)
        for bad in FORBIDDEN:
            self.assertNotIn(bad, blob)

    def test_a6_diagnostic_only(self):
        self.assertTrue(self.r["build_meta"]["A6_NEURAL_REF"].get("diagnostic_only"))
        if self.r["first_refusal_arm"] is not None:
            self.assertNotEqual(self.r["first_refusal_arm"], "A6_NEURAL_REF")

    def test_feature_extractor_cannot_see_labels(self):
        sys.path.insert(0, str(HERE))
        sys.path.insert(0, str(HERE.parents[1] / "src"))
        import inspect
        import fna5_world
        src = inspect.getsource(fna5_world.extract_features)
        for token in ("run_oracle", "exec_by_id", "passed", "outcomes", "oracle"):
            self.assertNotIn(token, src)

    def test_charged_lifecycle_present(self):
        for name in ("A2_COST_MODEL", "A3A_KNN", "A4_TREE", "A5_LINUCB"):
            blk = self.r["arms_EVAL"][name]
            self.assertGreater(blk["build_work"], 0)
            self.assertGreater(blk["mean_overhead_work"], 0)
        self.assertGreater(self.r["maintenance"]["A2_COST_MODEL"]
                           ["label_acquisition_work"], 0)

    def test_oracle_not_beaten(self):
        o = self.r["oracle_exec_mean_EVAL"]
        for name, blk in self.r["arms_EVAL"].items():
            if name == "A0_ORACLE":
                continue
            self.assertGreaterEqual(blk["mean_exec_work"], o * 0.98,
                                    "%s appears to beat the oracle: harness bug" % name)

    def test_baseline_is_clean(self):
        blk = self.r["arms_EVAL"]["BASELINE_INCUMBENT"]
        self.assertGreaterEqual(blk["first_pass_rate"], 0.98,
                                "incumbent first-PASS policy must rarely fail")

    def test_a1_is_not_the_oracle(self):
        sys.path.insert(0, str(HERE))
        sys.path.insert(0, str(HERE.parents[1] / "src"))
        import fna5_world as W
        world = W.build_world(W.WorldParams.tiny_params())
        disagree = 0
        for i in range(60):
            q = W.make_query(world, i)
            insts, _ = W.applicable(world, q)
            orc = W.run_oracle(world, q, insts)
            choice, _ = W.analytic_choice(world, q, insts)
            if choice.family != orc["family"]:
                disagree += 1
        self.assertGreater(disagree, 0,
                           "A1 never disagrees with the oracle: it would be reading realized "
                           "constants, violating the non-oracle contract")

    def test_null_control_is_honest(self):
        # The null destroys feature->outcome information but RETAINS each arm's legal
        # declared-cost prior (declared costs are public knowledge, not leaked signal),
        # so the null's floor is the cost-aware marginal policy, not the constant-modal
        # one. Two pinned claims: (i) no arm's null massively exceeds its real run (the
        # null pipeline injects no information), and (ii) at least one learned arm beats
        # its null (the legal surface carries real routing signal).
        learned = ("A2_COST_MODEL", "A3A_KNN", "A3B_LOGISTIC", "A4_TREE", "A5_LINUCB")
        beats = 0
        for name in learned:
            real = self.r["arms_EVAL"][name]
            null = self.r["null_control"][name]
            self.assertTrue(null["arm"].endswith("_NULL"))
            self.assertEqual(null["n"], real["n"])
            self.assertLessEqual(null["family_agreement"],
                                 real["family_agreement"] + 0.10,
                                 "%s null massively exceeds real: control leak" % name)
            if null["family_agreement"] <= real["family_agreement"] - 0.05:
                beats += 1
        self.assertGreater(
            beats, 0,
            "no learned arm beats its null: the legal surface would carry no routing "
            "signal and the whole ladder result would be null")

    def test_sufficiency_consistent_with_frozen_rule(self):
        o = self.r["oracle_exec_mean_EVAL"]
        for name, s in self.r["sufficiency"].items():
            blk = self.r["arms_EVAL"][name]
            want = (blk["mean_total_work"] <= 1.05 * o
                    and blk["first_pass_rate"] >= 0.98)
            self.assertEqual(bool(s["sufficient"]), want, name)

    def test_first_refusal_is_smallest_sufficient(self):
        ladder = ["A1_ANALYTIC_GUARDED", "A2_COST_MODEL", "A3A_KNN", "A3B_LOGISTIC",
                  "A4_TREE", "A5_LINUCB"]
        suff = [n for n in ladder if self.r["sufficiency"].get(n, {}).get("sufficient")]
        if suff:
            self.assertEqual(self.r["first_refusal_arm"], suff[0])
        else:
            self.assertIsNone(self.r["first_refusal_arm"])


if __name__ == "__main__":
    unittest.main()
