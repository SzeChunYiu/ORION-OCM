from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from n1_ud_dev_eval import evaluate  # noqa: E402
from ud_induction import parse_conllu  # noqa: E402


CORPUS = """# sent_id = s1
# text = I saw her.
1\tI\ti\tPRON\tPRP\tCase=Nom\t2\tnsubj\t_\t_
2\tsaw\tsee\tVERB\tVBD\tTense=Past|VerbForm=Fin\t0\troot\t_\t_
3\ther\tshe\tPRON\tPRP\tCase=Acc\t2\tobj\t_\t_
4\t.\t.\tPUNCT\t.\t_\t2\tpunct\t_\t_
"""


class UDDevEvalTests(unittest.TestCase):
    def test_receipt_is_aggregate_and_non_protected(self):
        sentences = parse_conllu(CORPUS)
        result = evaluate(sentences, sentences, max_chart_nodes=1000)
        self.assertEqual(result["receipt"], "N1_UD_DEV_CALIBRATION_V1")
        self.assertEqual(result["study_role"], "DEVELOPMENT_CALIBRATION_ONLY")
        self.assertFalse(result["protected_claim_authority"])
        self.assertEqual(result["eval"]["sentences"], 1)
        self.assertEqual(result["eval"]["exact_gold_structure_sentences"], 1)
        # Aggregate receipt must not serialize sentence text, token forms, or tree annotations.
        flat = repr(result)
        self.assertNotIn("I saw her", flat)
        self.assertNotIn("nsubj", flat)


if __name__ == "__main__":
    unittest.main()
