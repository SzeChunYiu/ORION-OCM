"""Source-bound guards for the prospectively registered continual_v6.10 runs.

These tests do not establish a scientific result. They make the registered execution
path fail loudly if a later edit drops the required v6.9 base flags, changes the
registered seed windows/ablations, or disconnects the two v6.10 mechanisms from the
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

    def test_k1l_attribution_is_h_only_on_exact_gated_seed_set(self):
        text = self.text("m2_k1abl610.sbatch")
        self.assertIn("SEEDS=(658 659 660 661 662 663 664 666 667 668 669)", text)
        self.assertIn("export M2_V68D=1 M2_V68E=1 M2_V69F=1", text)
        self.assertIn("V=h", text)
        self.assertIn("export M2_V610H=1", text)
        self.assertNotIn("VARS=(h i hi)", text)

    def test_runner_contains_registered_mechanisms_and_safe_labels(self):
        text = self.text("m2p1_runner.py")
        self.assertIn('"futility_bar": os.environ.get("M2_V610H") == "1"', text)
        self.assertIn('"regime_evidence": os.environ.get("M2_V610I") == "1"', text)
        self.assertIn("cannot clear the failure-evidence bar", text)
        self.assertIn('C["failed_evidence"] = 0', text)
        self.assertIn('"evidence_reset"', text)
        # h/i on the registered v6.9 base use v6.10 labels; h/i on any other base
        # remain visibly attached to that base rather than masquerading as v6.10.
        self.assertIn('if base == "continual_v6.9"', text)
        self.assertIn('return base + ("+h" if h else "") + ("+i" if i else "")', text)

    def test_registration_documents_closed_old_claim_and_fresh_new_lineage(self):
        text = self.text("CONTINUAL.md")
        self.assertIn("K1 on mixed regimes is NOT_ESTABLISHED at this grammar", text)
        self.assertIn("K1-L confirmation (fresh seeds 658–669", text)
        self.assertIn("K1-L — lifetime advantage on mixed regimes — is established at C2 scope", text)
        self.assertIn("fresh seeds 670–681", text)
        self.assertIn("all three original bars unchanged", text)
        self.assertIn("if it fails, K1 on mixed regimes stays NOT_ESTABLISHED", text)
        self.assertIn("address regime-change detection", text)


if __name__ == "__main__":
    unittest.main()
