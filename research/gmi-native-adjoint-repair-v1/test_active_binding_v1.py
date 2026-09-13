"""The corrected portable packet and active repository are separate claims."""
from pathlib import Path
import shutil
import json
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_active_runtime_v1 import verify,ROOT

class ActiveBindingTests(unittest.TestCase):
    def fixture(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);repo=Path(temp.name)
        target=repo/'research/machine-intelligence-morphogenesis-v1'
        (target/'gmi_microscope').mkdir(parents=True)
        for name in json.loads((ROOT/'ACTIVE_RUNTIME_BINDING_V1.json').read_text())['files']:
            relative=Path(name).relative_to('research/machine-intelligence-morphogenesis-v1')
            destination=target/relative;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/'corrected_source'/relative,destination)
        return repo,target
    def test_complete_real_source_and_test_copy_pass(self):
        repo,_=self.fixture();self.assertEqual(verify(repo)['status'],'ACTIVE_NATIVE_ADJOINT_SOURCE_MATCH')
    def test_changed_vm_fails_without_execution(self):
        repo,target=self.fixture();p=target/'gmi_microscope/vm.py';p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaises(ValueError):verify(repo)
    def test_changed_native_import_dependency_is_unverified(self):
        repo,target=self.fixture();p=target/'gmi_microscope/core.py';p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaises(ValueError):verify(repo)
    def test_missing_or_linked_test_is_unverified(self):
        repo,target=self.fixture();p=target/'test_gmi_vm_parameter_adjoint_v1.py';p.unlink()
        with self.assertRaises(ValueError):verify(repo)
        p.symlink_to(ROOT/'corrected_source/test_gmi_vm_parameter_adjoint_v1.py')
        with self.assertRaises(ValueError):verify(repo)
if __name__=='__main__':unittest.main()
