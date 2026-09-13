"""Real old-source no-alarm and finite source-sensitive controls."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sources_v1 import verify_sources
from historical_v1 import original_suite,old_controls,parent_readout,LLS

ROOT=Path(__file__).resolve().parent

class SourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=verify_sources(ROOT)

    def test_complete_original_static_suite_no_alarm(self):
        result=original_suite(self.sources)
        self.assertEqual(sum(x["tests"] for x in result.values()),42)
        self.assertTrue(all(x["errors"]==x["failures"]==x["skipped"]==0 for x in result.values()))

    def test_original_menu_census_and_real_transport_counterexample(self):
        result=old_controls(self.sources)
        self.assertEqual(result["census"],dict(INFEASIBLE_AT_CONTRACT=36,SELECTED=50,UNDETERMINED_TIE=42))
        self.assertEqual(result["original_transport_bounds"],[2,1])
        self.assertEqual(result["zero_likelihood_tag_menu"]["law"],"BAYES_UPDATE")

    def test_original_census_rejects_source_behavior_mutation(self):
        changed=dict(self.sources)
        key=("PR590",LLS+"learning_law_selection_v1.py")
        changed[key]+=b"\n_original_select=select\ndef select(*args,**kwargs):\n    r=_original_select(*args,**kwargs)\n    r['terminal']='SELECTED'\n    return r\n"
        with self.assertRaises(ValueError):old_controls(changed)

    def test_current_capital_counts_and_strongest_parent(self):
        result=parent_readout(self.sources)
        self.assertEqual((result["targets"],result["earlier"],result["later"],result["tied"]),(2741,2536,202,3))
        self.assertEqual((result["recorded_k2_passes"],result["recorded_k2_trials"]),(2,9))
        self.assertEqual((result["registered_numerator"],result["registered_denominator"]),(2,3))
        self.assertEqual((len(result["guided_first_ties"]),len(result["guided_first_beats"])),(5,3))

    def test_missing_or_changed_parent_record_does_not_pass(self):
        key=("PARENT","research/m2-traversal-capital-v1/m2p1/CLAIM_LADDER.md")
        changed=dict(self.sources);changed[key]=b"no receipt"
        with self.assertRaises(ValueError):parent_readout(changed)
        changed=dict(self.sources);changed[key]=changed[key].replace(b"ties controller_v5",b"loses to controller_v5")
        with self.assertRaises(ValueError):parent_readout(changed)

if __name__=="__main__":unittest.main()
