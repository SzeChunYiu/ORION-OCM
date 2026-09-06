"""Launch binding and unavailable evaluator controls; no R1 target outcome here."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from campaign import prepare, inventory, public_task, run
from import_source import audit
from substrate import digest_json

class LaunchHostiles(unittest.TestCase):
    def test_launch_exclusive_and_source_bound(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'launch.json'; prepare(path); value=json.loads(path.read_text())
            self.assertEqual(value['source_inventory'],inventory())
            self.assertEqual(value['public_package_sha256'],digest_json(public_task()))
            with self.assertRaises(FileExistsError): prepare(path)
    def test_source_drift_never_runs_native(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'launch.json'; prepare(path); value=json.loads(path.read_text())
            value['source_inventory']['research/flt-kso-v1/native.py']='0'*64
            path.write_text(json.dumps(value))
            row=run(path,Path(d)/'result',None,None)
            self.assertEqual(row['terminal'],'CANNOT_CHECK_SOURCE_DRIFT')
            self.assertNotIn('native',row)
    def test_unavailable_evaluator_is_not_empty_graph_success(self):
        with tempfile.TemporaryDirectory() as d:
            row=audit(Path(d)/'absent',Path(d)/'result')
            self.assertEqual(row['terminal'],'CANNOT_CHECK_SOURCE_ACQUISITION')
            self.assertFalse(row['solver_launched'])

if __name__=='__main__':unittest.main()
