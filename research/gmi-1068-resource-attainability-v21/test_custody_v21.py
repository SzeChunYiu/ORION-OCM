"""Actual inherited contents and preregistration, with isolated mutation overlays."""
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import custody_v21 as core
COVERAGE={}


@contextmanager
def overlay(verified):
    with tempfile.TemporaryDirectory(prefix='gmi-v21-custody-') as temporary:
        root=Path(temporary)
        (root/'.git').symlink_to(ROOT/'.git')
        for relative in verified['source_bindings']:
            path=root/relative
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((ROOT/relative).read_bytes())
        yield root


class CustodyTests(unittest.TestCase):
    def test_real_inherited_inputs_and_tampering(self):
        valid=core.verify(ROOT)
        self.assertEqual(valid['amendment_carry']['qualified_revision_ids'],['GMI2-R2-003@r1','GMI2-R2-007@r1'])
        self.assertNotIn('original_fulfilled',valid['amendment_carry'])
        self.assertIn('research/gmi-1068-partial-context-v15/context_v15.py',valid['source_bindings'])
        with overlay(valid) as root:self.assertEqual(core.verify(root),valid)
        files=('research/gmi-1068-frontier-simulation-v20/maps_v20.py',
               'research/gmi-1068-partial-context-v15/context_v15.py',
               'research/gmi-1068-continuation-v8/continuation_v8.py',
               'research/gmi-1068-recursive-audit-v20/CURRENT_ACCOUNTING_V20.json',
               'research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json',
               core.RECEIPTS[0],core.RECEIPTS[1],core.RECEIPTS[2],core.PACKAGE+'/FREEZE_V21.md')
        rejected=0
        for name in files:
            with overlay(valid) as root:
                path=root/name;path.write_bytes(path.read_bytes()+b'\n')
                with self.assertRaises(ValueError):core.verify(root)
                rejected+=1
        with overlay(valid) as root:
            target=root/'research/gmi-1068-frontier-simulation-v20/maps_v20.py'
            target.write_bytes(target.read_bytes()+b'\n')
            path=root/core.RECEIPTS[0]
            receipt=json.loads(path.read_text())
            receipt['inputs']['maps_v20.py']=core.digest(target)
            path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
            with self.assertRaises(ValueError):core.verify(root)
            rejected+=1
        with overlay(valid) as root:
            name='research/gmi-1068-partial-context-v15/context_v15.py'
            target=root/name;target.write_bytes(target.read_bytes()+b'\n')
            path=root/core.RECEIPTS[0];receipt=json.loads(path.read_text())
            receipt['source_bindings'][name]=core.digest(target)
            path.write_text(json.dumps(receipt,sort_keys=True)+'\n')
            with self.assertRaises(ValueError):core.verify(root)
            rejected+=1
        self.assertEqual(rejected,11)
        COVERAGE.update(valid_inherited_custody_controls=1,inherited_custody_rejections=rejected)

    def test_unavailable_inputs_and_path_escape(self):
        valid=core.verify(ROOT)
        missing=0
        for name in ('research/gmi-1068-frontier-simulation-v20/maps_v20.py',
                     'research/gmi-1068-partial-context-v15/context_v15.py',
                     core.PACKAGE+'/FREEZE_V21.md',core.RECEIPTS[2]):
            with overlay(valid) as root:
                (root/name).unlink()
                with self.assertRaises((OSError,core.CannotCheck)):core.verify(root)
                missing+=1
        with overlay(valid) as root:
            (root/'.git').unlink()
            with self.assertRaises(core.CannotCheck):core.verify(root)
            missing+=1
        rejected=0
        for relative in ('../outside','/tmp/outside','',None):
            with self.assertRaises(ValueError):core.safe_path(ROOT,relative)
            rejected+=1
        with overlay(valid) as root:
            name='research/gmi-1068-partial-context-v15/context_v15.py'
            path=root/name;path.unlink();path.symlink_to(ROOT/name)
            with self.assertRaises(ValueError):core.verify(root)
            rejected+=1
        COVERAGE.update(unavailable_inherited_controls=missing,source_path_escape_rejections=rejected)


if __name__=='__main__':
    program=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
