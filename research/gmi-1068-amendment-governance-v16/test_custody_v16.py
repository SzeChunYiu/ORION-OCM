"""Real git-anchored source overlays; no mutations of the live checkout."""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ledger_test_support_v16',HERE/'ledger_test_support_v16.py')
support=importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
COVERAGE={}


@contextmanager
def overlay(contract):
    with tempfile.TemporaryDirectory(prefix='gmi-v16-custody-') as temporary:
        root=Path(temporary)
        (root/'.git').symlink_to(support.ROOT/'.git')
        paths=set(contract['source_bindings'])|{support.custody.CONTRACT,support.custody.SCIENCE+'/FREEZE_V16.md'}
        for name in paths:
            target=root/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((support.ROOT/name).read_bytes())
        yield root


class CustodyTests(unittest.TestCase):
    def test_real_baseline_and_coupled_tampering(self):
        contract=support.contract()
        with overlay(contract) as root:
            self.assertEqual(support.custody.read_contract(root),contract)
        cases=('contract','freeze','snapshot','inherited-proof','coupled-scope','coupled-passage')
        for case in cases:
            with self.subTest(case=case),overlay(contract) as root:
                if case=='contract':
                    path=root/support.custody.CONTRACT
                    path.write_text(path.read_text()+'\n')
                elif case=='freeze':
                    path=root/support.custody.SCIENCE/'FREEZE_V16.md'
                    path.write_text(path.read_text()+'changed preregistration\n')
                elif case=='snapshot':
                    path=root/support.structure.SNAPSHOT
                    snapshot=json.loads(path.read_text())
                    snapshot['rounds']['R2']['obligations'][2]['status']='CLOSED'
                    path.write_text(json.dumps(snapshot))
                elif case=='inherited-proof':
                    path=root/'research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean'
                    path.write_text(path.read_text()+'\n')
                else:
                    revised=deepcopy(contract)
                    if case=='coupled-scope':
                        revised['statements'][0]['premises']=[]
                        revised['original_targets'][0]['refuted_reading']='all original process claims are false'
                    else:
                        name='research/gmi-1068-r2-context-irreducibility-v1/FREEZE_V1.md'
                        path=root/name
                        path.write_text(path.read_text().replace('physically/computationally','unconditionally'))
                        revised['source_bindings'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
                    path=root/support.custody.CONTRACT
                    path.write_text(json.dumps(revised))
                    # Attacker also rebinds its submitted ledger; the frozen git bytes still rule.
                    ledger=support.baseline(revised)
                    ledger['contract_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
                    (root/'submitted-ledger.json').write_text(json.dumps(ledger))
                with self.assertRaises(ValueError):
                    support.custody.read_contract(root)
        COVERAGE.update(valid_repository_custody_controls=1,repository_custody_rejections=len(cases))

    def test_missing_inputs_are_not_validity_verdicts(self):
        contract=support.contract()
        for name in (support.custody.CONTRACT,'research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean'):
            with overlay(contract) as root:
                (root/name).unlink()
                with self.assertRaises(OSError):
                    support.custody.read_contract(root)
        with overlay(contract) as root:
            (root/'.git').unlink()
            with self.assertRaises(support.custody.CannotCheck):
                support.custody.read_contract(root)
        COVERAGE['unavailable_custody_controls']=3

    def test_published_ledger_cannot_be_rewritten(self):
        publication=support.load('check_publication_v16')
        raw=(support.ROOT/publication.LEDGER).read_bytes()
        self.assertEqual(publication.check_published_bytes(raw,raw),'PUBLISHED_V16_UNCHANGED')
        self.assertEqual(publication.check_published_bytes(None,raw),'INITIAL_PUBLICATION')
        self.assertEqual(publication.evaluate(support.ROOT,support.structure.FREEZE),'INITIAL_PUBLICATION')
        for changed in (raw+b'\n',b'{}\n'):
            with self.assertRaises(ValueError):
                publication.check_published_bytes(raw,changed)
        with self.assertRaises(publication.CannotCheck):
            publication.evaluate(support.ROOT,'0'*40)
        COVERAGE.update(publication_positive_controls=3,published_rewrite_rejections=2,
                        unavailable_publication_base_controls=1)


if __name__=='__main__':
    program=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
