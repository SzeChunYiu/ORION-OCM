import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
import json
from fractions import Fraction as F
from retained_evidence_v1 import *
ROOT=Path(__file__).resolve().parent

class EvidenceTests(unittest.TestCase):
    def test_real_retained_no_alarm(self):
        row=retained(ROOT)["open_niche"]
        self.assertEqual(row["rows"],108)
        self.assertEqual(row["admitted"],[["E_open4","compiled_search"],["E_open4","program_search"]])
        self.assertEqual(len(row["search_top_including_ties"]),8)
        self.assertEqual(row["minimum_search"],F(9062,10000))
        self.assertEqual((row["O1_all_search_admitted"],row["O2_search_always_top"],
                          row["O3_all_search_at_least_0887"]),(False,False,True))

    def test_actual_missing_row_rejected(self):
        raw=verify_sources(ROOT)[("PR597",PREFIX+"STAGE_OPEN_NICHE_V1.json")]
        packet=json.loads(raw)
        packet["results"]["E_open1"]["rows"].pop("program_search")
        with self.assertRaises(ValueError):
            parse_niche(json.dumps(packet))

    def test_actual_flag_type_rejected(self):
        raw=verify_sources(ROOT)[("PR597",PREFIX+"STAGE_OPEN_NICHE_V1.json")]
        packet=json.loads(raw)
        packet["results"]["E_open1"]["rows"]["program_search"]["admissible"]="false"
        with self.assertRaises(ValueError):
            parse_niche(json.dumps(packet))

    def test_exact_cap_boundary_attainment(self):
        self.assertFalse(boundary(F(23,24)))
        self.assertTrue(boundary(F(23,24)+F(1,1000)))
        self.assertEqual(F(1)-F(23,24),F(1,24))

    def test_rounded_margin_does_not_certify_exact_unit(self):
        lo,hi=rounded_difference(F(9688,10000),F(9271,10000))
        self.assertLess(lo,F(1,24))
        self.assertGreater(hi,F(1,24))

    def test_sample_max_is_not_family_bound(self):
        sample=(F(1,2),F(9,10))
        extension=sample+(F(1),)
        self.assertEqual(max(sample),F(9,10))
        self.assertGreater(max(extension),max(sample))

    def test_nonattainment_not_admission(self):
        threshold=F(1,2)
        terms=[threshold-F(1,n) for n in range(3,20)]
        self.assertTrue(all(0<=x<threshold for x in terms))
        self.assertGreater(terms[-1],terms[0])
        # Limit equals threshold analytically; this finite prefix is not its proof.

if __name__=="__main__":
    unittest.main()
