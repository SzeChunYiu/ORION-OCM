from __future__ import annotations
import importlib.util, json, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("b1", str(HERE/"b1_derivation_protocol_v2.py"))
MOD=importlib.util.module_from_spec(SPEC); sys.modules["b1"]=MOD; SPEC.loader.exec_module(MOD)
class TestB1(unittest.TestCase):
    def test_all_green(self):
        out=MOD.run()
        self.assertTrue(out["all_remaining_protocol_boxes_green"])
        self.assertEqual(out["n_open_boxes_closed"], 13)
        self.assertEqual(out["terminal"], MOD.TERMINAL)
        committed=json.loads((HERE/"RECEIPT_V1.json").read_text())
        self.assertEqual(json.dumps(committed,sort_keys=True), json.dumps(out,sort_keys=True))
if __name__=="__main__":
    unittest.main()
