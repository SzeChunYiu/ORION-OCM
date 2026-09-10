from __future__ import annotations

import json
import unittest
from pathlib import Path

from gate import review_proposed_work

HERE = Path(__file__).resolve().parent


class TestPublicationConstitution(unittest.TestCase):
    def test_protocol_has_required_freeze_fields(self):
        proto = json.loads((HERE / "PROTOCOL.json").read_text())
        g2 = proto["studies"]["g2-macro-operator-v1"]
        for key in (
            "decisive_question", "contribution_level", "strongest_parent", "causal_ablation",
            "prior_information_manifest", "task_family_generator", "protected_splits",
            "budgets", "negative_terminals", "independent_unit",
        ):
            self.assertIn(key, g2)
        self.assertEqual(proto["section16"]["independently_authored_families_E3"], "CANNOT_CHECK_NO_INDEPENDENT_AUTHORSHIP")

    def test_do_not_build_when_answers_are_none(self):
        self.assertEqual(review_proposed_work({k: "none" for k in ("principle", "mechanism", "prediction", "evidence", "parent", "closure")}), "DO_NOT_BUILD")
        self.assertEqual(
            review_proposed_work({
                "principle": "Machine Epistemics law",
                "mechanism": "learn/use/compose",
                "prediction": "failure memory reduces dead ends",
                "evidence": "G3.2 frozen study",
                "parent": "TMS nogood",
                "closure": "G3.2/003",
            }),
            "OK",
        )

    def test_after_execution_does_not_invent_missing_traces(self):
        proto = json.loads((HERE / "PROTOCOL.json").read_text())
        after = proto["studies"]["g2-macro-operator-v1"]["after_execution"]
        self.assertIn("MISSING", after["fresh_host_rerun"])


if __name__ == "__main__":
    unittest.main()
