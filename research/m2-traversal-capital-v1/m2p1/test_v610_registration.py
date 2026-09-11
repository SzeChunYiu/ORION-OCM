"""Source-bound guards for the prospectively registered continual_v6.10 runs.

These tests do not establish a scientific result. They make the registered execution
path fail loudly if a later edit drops the required v6.9 base flags, changes the
fresh confirmation seed window, or disconnects the two v6.10 mechanisms from the
runner.
"""
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


class V610RegistrationTest(unittest.TestCase):
    def text(self, name: str) -> str:
        return (HERE / name).read_text(encoding="utf-8")

    def test_confirmation_binds_v69_base_and_both_v610_flags(self):
        text = self.text("m2_abc610.sbatch")
        for flag in ("M2_V68D=1", "M2_V68E=1", "M2_V69F=1", "M2_V610H=1", "M2_V610I=1"):
            self.assertIn(flag, text)
        self.assertIn("S=$((600 + SLURM_ARRAY_TASK_ID))", text)
        self.assertIn("scripts_v610", text)
        self.assertIn("CONTINUAL_OCM", text)

    def test_diagnostic_binds_v69_base_and_only_registered_variants(self):
        text = self.text("m2_k1diag610.sbatch")
        self.assertIn("export M2_V68D=1 M2_V68E=1 M2_V69F=1", text)
        self.assertIn("VARS=(h i hi)", text)
        self.assertIn("SEEDS=(623 626 628 629 636 642 647 634 640 646)", text)
        self.assertIn("case $V in h)", text)
        self.assertIn("i) export M2_V610I=1", text)
        self.assertIn("hi) export M2_V610H=1 M2_V610I=1", text)

    def test_runner_contains_registered_mechanisms(self):
        text = self.text("m2p1_runner.py")
        self.assertIn('"futility_bar": os.environ.get("M2_V610H") == "1"', text)
        self.assertIn('"regime_evidence": os.environ.get("M2_V610I") == "1"', text)
        self.assertIn("cannot clear the failure-evidence bar", text)
        self.assertIn('C["failed_evidence"] = 0', text)
        self.assertIn('"evidence_reset"', text)

    def test_registration_documents_stop_rule_and_fresh_window(self):
        text = self.text("CONTINUAL.md")
        self.assertIn("K1 on mixed regimes is NOT_ESTABLISHED at this grammar", text)
        self.assertIn("new fresh seeds 658–669", text)
        self.assertIn("if K1-L fails", text)
        self.assertIn("NOT_ESTABLISHED at this grammar too", text)


if __name__ == "__main__":
    unittest.main()
