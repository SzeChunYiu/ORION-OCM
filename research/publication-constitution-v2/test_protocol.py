from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from freeze import (
    AFTER_KEYS,
    FREEZE_KEYS,
    V1_PROTOCOL,
    classify,
    is_filled,
    load_protocol,
    v1_exists_unoverwritten,
)
from gate import REQUIRED, review_proposed_work, review_publication_close

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _const(path: Path, name: str) -> str:
    match = re.search(rf'^{name}\s*=\s*"([^"]+)"', _read(path), re.M)
    if match is None:
        raise AssertionError(f"{name} not found in {path}")
    return match.group(1)


class TestPublicationConstitutionV2(unittest.TestCase):
    def setUp(self):
        self.proto = load_protocol()
        self.catalog = self.proto["section15"]["catalog"]
        self.after = self.proto["section15"]["after_execution"]
        self.report = classify(self.proto)

    def test_v1_protocol_exists_and_is_not_this_file(self):
        self.assertTrue(v1_exists_unoverwritten())
        v1 = json.loads(V1_PROTOCOL.read_text())
        self.assertEqual(v1["schema"], "ocm.publication-constitution.protocol.v1")
        self.assertNotEqual(self.proto["schema"], v1["schema"])
        self.assertNotEqual(HERE / "PROTOCOL.json", V1_PROTOCOL)

    def test_does_not_close_144_or_invent_e4(self):
        self.assertFalse(self.proto["closes_issue_144"])
        self.assertEqual(self.proto["terminal"], "PUBLICATION_CONSTITUTION_FROZEN_WITH_GAPS")
        self.assertFalse(self.report["invented_e4"])
        self.assertFalse(self.report["closes_issue_144"])
        for study in self.proto["studies"].values():
            self.assertNotIn(study["evidence_class"], {"E4", "E5"})
            after = study["after_execution"]
            self.assertTrue(str(after["fresh_host_rerun"]).startswith("CANNOT_CHECK"))
            self.assertTrue(str(after["disjoint_replication"]).startswith("MISSING"))

    def test_every_study_has_every_freeze_key_filled(self):
        for name, study in self.proto["studies"].items():
            for key in FREEZE_KEYS:
                self.assertIn(key, study, msg=f"{name} missing freeze key {key}")
                self.assertTrue(is_filled(study[key]), msg=f"{name}.{key} is not filled")
        self.assertEqual(self.report["freeze_complete"], list(FREEZE_KEYS))
        self.assertEqual(self.report["freeze_missing"], [])
        self.assertEqual(self.catalog["freeze_complete"], list(FREEZE_KEYS))

    def test_section15_catalog_matches_after_execution_statuses(self):
        complete, missing, cannot_check = [], [], []
        for key in AFTER_KEYS:
            status = self.after[key]["status"]
            if status == "FREEZE_COMPLETE":
                complete.append(key)
            elif str(status).startswith("CANNOT_CHECK"):
                cannot_check.append(key)
            else:
                missing.append(key)
        self.assertEqual(self.report["after_complete"], complete)
        self.assertEqual(self.report["after_missing"], missing)
        self.assertEqual(self.report["after_cannot_check"], cannot_check)
        self.assertEqual(set(self.catalog["still_missing"]), set(missing))
        self.assertEqual(set(self.catalog["cannot_check"]), set(cannot_check))
        self.assertIn("disjoint_replication", missing)
        self.assertIn("fresh_host_rerun", cannot_check)
        self.assertEqual(self.after["disjoint_replication"]["status"], "MISSING")
        self.assertTrue(self.after["fresh_host_rerun"]["status"].startswith("CANNOT_CHECK"))

    def test_independent_authorship_cannot_check_with_human_author_conversion(self):
        section16 = self.proto["section16"]
        self.assertEqual(
            section16["independently_authored_families_E3"],
            "CANNOT_CHECK_NO_INDEPENDENT_AUTHORSHIP",
        )
        conversion = section16["conversion"].lower()
        self.assertIn("human independent author", conversion)
        self.assertIn("internal generators remain audit-only", conversion)
        host = self.after["fresh_host_rerun"]
        self.assertIn("second machine", host["conversion"].lower())

    def test_harvested_salts_match_capsule_constants(self):
        studies = self.proto["studies"]
        g2 = studies["g2-macro-operator-v1"]["protected_splits"]
        g2_path = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
        self.assertEqual(g2["train_salt"], _const(g2_path, "TRAIN_SALT"))
        self.assertEqual(g2["validation_salt"], _const(g2_path, "VALIDATION_SALT"))
        self.assertEqual(g2["test_salt"], _const(g2_path, "TEST_SALT"))

        g32 = studies["g3-failure-memory-v1"]["protected_splits"]
        g32_path = REPO / "research" / "g3-failure-memory-v1" / "experiment.py"
        self.assertEqual(g32["train_salt"], _const(g32_path, "TRAIN_SALT"))
        self.assertEqual(g32["test_salt"], _const(g32_path, "TEST_SALT"))

        g33 = studies["g3-representation-v1"]["protected_splits"]
        g33_path = REPO / "research" / "g3-representation-v1" / "experiment.py"
        self.assertEqual(g33["train_salt"], _const(g33_path, "TRAIN_SALT"))
        self.assertEqual(g33["test_salt"], _const(g33_path, "TEST_SALT"))

        g54 = studies["g5-consolidation-v1"]["protected_splits"]
        g54_path = REPO / "research" / "g5-consolidation-v1" / "experiment.py"
        self.assertEqual(g54["train_salt"], _const(g54_path, "TRAIN_SALT"))
        self.assertEqual(g54["heldout_salt"], _const(g54_path, "HELDOUT_SALT"))

        g25 = studies["g2-strong-parents-v1"]["protected_splits"]
        g25_path = REPO / "research" / "g2-strong-parents-v1" / "experiment.py"
        self.assertEqual(g25["train_salt"], _const(g25_path, "TRAIN_SALT"))
        self.assertEqual(g25["test_salt"], _const(g25_path, "TEST_SALT"))

        g7 = studies["g7-lineage-v1"]["protected_splits"]
        g7_path = REPO / "research" / "g7-lineage-v1" / "experiment.py"
        self.assertEqual(g7["train_salt"], _const(g7_path, "TRAIN_SALT"))
        self.assertEqual(g7["trap_test_salt"], _const(g7_path, "TRAP_TEST_SALT"))

        g6 = studies["g6-intervention-lab-v1"]["protected_splits"]
        g6_path = REPO / "research" / "g6-intervention-lab-v1" / "experiment.py"
        self.assertEqual(g6["salt"], _const(g6_path, "SALT"))

        xfer = studies["cross-domain-transfer-v1"]["protected_splits"]
        xfer_path = REPO / "research" / "cross-domain-transfer-v1" / "experiment.py"
        self.assertEqual(xfer["color_salt"], _const(xfer_path, "COLOR_SALT"))

        g31 = studies["g3-independent-composition-v1"]["protected_splits"]
        g31_path = REPO / "research" / "g3-independent-composition-v1" / "experiment.py"
        self.assertEqual(g31["a_train_salt"], _const(g31_path, "A_TRAIN_SALT"))
        self.assertEqual(g31["test_salt"], _const(g31_path, "TEST_SALT"))

    def test_do_not_build_when_section20_answers_are_none(self):
        self.assertEqual(
            review_proposed_work({key: "none" for key in REQUIRED}),
            "DO_NOT_BUILD",
        )
        self.assertEqual(
            review_proposed_work({key: None for key in REQUIRED}),
            "DO_NOT_BUILD",
        )
        self.assertEqual(
            review_proposed_work({key: "" for key in REQUIRED}),
            "DO_NOT_BUILD",
        )
        filled = {
            "principle": "Machine Epistemics law",
            "mechanism": "learn/use/compose",
            "prediction": "failure memory reduces dead ends",
            "evidence": "G3.2 frozen study",
            "parent": "TMS nogood",
            "closure": "G3.2/003",
        }
        self.assertEqual(review_proposed_work(filled), "OK")

    def test_do_not_build_when_independent_authorship_or_fresh_host_are_none(self):
        filled = {
            "principle": "Machine Epistemics law",
            "mechanism": "learn/use/compose",
            "prediction": "failure memory reduces dead ends",
            "evidence": "G3.2 frozen study",
            "parent": "TMS nogood",
            "closure": "G3.2/003",
            "independent_authorship": None,
            "fresh_host": None,
        }
        self.assertEqual(review_publication_close(filled), "DO_NOT_BUILD")
        filled["independent_authorship"] = "CANNOT_CHECK_NO_INDEPENDENT_AUTHORSHIP"
        filled["fresh_host"] = "CANNOT_CHECK_NO_SECOND_MACHINE"
        self.assertEqual(review_publication_close(filled), "DO_NOT_BUILD")
        filled["independent_authorship"] = "external-author-family-X"
        filled["fresh_host"] = "host-B-rerun-receipt"
        self.assertEqual(review_publication_close(filled), "OK")

    def test_core_names_freeze_complete_and_missing(self):
        core = (HERE / "CORE.md").read_text()
        self.assertIn("Freeze-complete", core)
        self.assertIn("Still MISSING", core)
        self.assertIn("CANNOT_CHECK", core)
        self.assertIn("human independent author", core)
        self.assertIn("second machine", core)
        self.assertNotIn("#144 scientifically closed", core.lower())


if __name__ == "__main__":
    unittest.main()
