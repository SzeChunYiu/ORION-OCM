from __future__ import annotations
import importlib.util, json, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("v1", str(HERE/"v1_known_form_closure_v1.py"))
MOD=importlib.util.module_from_spec(SPEC); sys.modules["v1"]=MOD; SPEC.loader.exec_module(MOD)
class T(unittest.TestCase):
    def test(self):
        out=MOD.run()
        self.assertTrue(out["all_v1_boxes_green"], out)
        self.assertEqual(out["terminal"], MOD.TERMINAL)
        self.assertGreaterEqual(out["n_families"], 20)
        committed=json.loads((HERE/"RECEIPT_V1.json").read_text())
        self.assertEqual(json.dumps(committed,sort_keys=True), json.dumps(out,sort_keys=True))
if __name__=="__main__":
    unittest.main()
