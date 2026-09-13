"""Source-bound checks for the experimental-validation crosswalk.

Every claim in EXPERIMENTAL_VALIDATION_CROSSWALK_V1.md names a parent clause.
These checks read the parents and fail if a cited clause is absent, so the
crosswalk cannot drift away from the documents it claims to summarise.
They establish no empirical result.
"""

import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GMI = REPO / "research" / "gmi-grand-unification-v1"
ME = REPO / "research" / "machine-epistemics-lifetime-v1"
PROTOCOL = GMI / "NN_NONNN_EMPIRICAL_INSTANTIATION_PROTOCOL_V1.md"
CROSSWALK = HERE / "EXPERIMENTAL_VALIDATION_CROSSWALK_V1.md"


def read(path):
    if not path.exists():
        raise FileNotFoundError("cited parent is missing: %s" % path)
    return path.read_text(encoding="utf-8")


class CitedParentsExist(unittest.TestCase):
    def test_every_cited_parent_file_exists(self):
        for path in (PROTOCOL,
                     GMI / "CONTINUAL_SEMANTIC_RETENTION_THEOREM_V1.md",
                     GMI / "DEVELOPMENTAL_REACHABILITY_SELECTION_THEOREM_V1.md",
                     GMI / "THEOREM_REPLAY_INVENTORY_V1.json",
                     ME / "ME_COMPARATOR_MANIFEST_V1.md",
                     ME / "ME_CONFIRMATORY_PREREGISTRATION_V0.md",
                     REPO / "research" / "h5-lifetime-economics-v1" / "CORE.md"):
            self.assertTrue(path.exists(), "missing cited parent: %s" % path)


class CitedClausesArePresent(unittest.TestCase):
    def test_protocol_owns_family_robustness_generalization_compute(self):
        text = read(PROTOCOL)
        for clause in ("E1 — operational family definitions",
                       "E4 — resource vector and accounting boundary",
                       "E5 — capability and deployment evidence",
                       "E7 — hard feasibility before preference",
                       "E12 — family-neutral controls",
                       "same protected obligation for all candidates",
                       "identical deployment examples/interventions"):
            self.assertIn(clause, text, "protocol clause absent: %s" % clause)

    def test_comparator_manifest_owns_matched_parents(self):
        text = read(ME / "ME_COMPARATOR_MANIFEST_V1.md")
        self.assertIn("Parity matrix", text)
        self.assertIn("post-deployment update permission", text)
        self.assertIn("continual-adaptation parent", text)

    def test_confirmatory_prereg_owns_sample_and_uncertainty(self):
        text = read(ME / "ME_CONFIRMATORY_PREREGISTRATION_V0.md")
        self.assertIn("CANNOT_CHECK_POWER", text)
        self.assertIn("mislabeled MATCHED", text)

    def test_adaptation_is_registered_as_a_theorem(self):
        text = read(GMI / "CONTINUAL_SEMANTIC_RETENTION_THEOREM_V1.md")
        self.assertIn("Continual learning is a past-to-future semantic cut", text)


class TheResidualIsReal(unittest.TestCase):
    def test_cross_family_protocol_has_no_adaptation_coordinate(self):
        text = read(PROTOCOL).lower()
        # Control: axes the protocol demonstrably does carry.
        for present in ("robustness", "generalization", "uncertainty"):
            self.assertIn(present, text, "control failed; probe is not working")
        # The residual: no post-deployment adjustment axis.
        for absent in ("post-deployment", "continual learning",
                       "few-shot", "fine-tuning"):
            self.assertNotIn(absent, text, "residual is stale: %s" % absent)

    def test_both_protocols_are_execution_blocked(self):
        self.assertIn("CANNOT_CHECK_PROTECTED_TASK_BINDING_N3_N5_LOCKED",
                      read(ME / "ME_LIFETIME_BENCHMARK_V0.md"))
        self.assertIn("PREREGISTRATION_ONLY_NOT_MEASUREMENT",
                      read(GMI / "THEOREM_REPLAY_INVENTORY_V1.json"))

    def test_budget_parity_gate_is_already_registered_not_ours(self):
        # EV-3: recorded so the gate is not proposed a third time.
        self.assertIn("deployment-only objective can reverse its family verdict",
                      read(GMI / "DEVELOPMENTAL_REACHABILITY_SELECTION_THEOREM_V1.md"))


class CrosswalkIsNotAlreadyStated(unittest.TestCase):
    def test_no_other_unit_joins_the_two_protocols(self):
        """The crosswalk's own falsifier: if a parent already states it, this unit is redundant."""
        joiners = []
        for path in REPO.joinpath("research").rglob("*.md"):
            if HERE in path.parents or path == CROSSWALK:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if "machine-epistemics-lifetime" in text and "NN_NONNN_EMPIRICAL_INSTANTIATION" in text:
                joiners.append(str(path.relative_to(REPO)))
        self.assertEqual(joiners, [], "crosswalk already stated in: %s" % joiners)


if __name__ == "__main__":
    unittest.main()
