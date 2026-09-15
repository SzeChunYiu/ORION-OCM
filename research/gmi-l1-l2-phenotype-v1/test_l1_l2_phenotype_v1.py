from __future__ import annotations
import importlib.util, json, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("p", str(HERE/"l1_l2_phenotype_v1.py"))
MOD=importlib.util.module_from_spec(SPEC); sys.modules["p"]=MOD; SPEC.loader.exec_module(MOD)
class T(unittest.TestCase):
    def test(self):
        out=MOD.run(); self.assertTrue(out["all_extension_boxes_green"])
        self.assertEqual(json.dumps(json.loads((HERE/"RECEIPT_V1.json").read_text()),sort_keys=True), json.dumps(out,sort_keys=True))
if __name__=="__main__": unittest.main()
