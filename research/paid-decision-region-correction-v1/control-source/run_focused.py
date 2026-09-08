"""Single fresh pure control, explicit forbidden-import guard and source identity."""
import hashlib,importlib.abc,io,json,os,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'source/research/paid-decision-region-v1'
blocked=[]
class Guard(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in {'dev6','dev6_arms','run_dev6','dev4','retain','shortcircuit_parent','run_shortcircuit','mmverify'}:
            blocked.append(fullname);raise ImportError('REAL_DONOR_IMPORT_FORBIDDEN:'+fullname)
sys.meta_path.insert(0,Guard());sys.path[:0]=[str(SOURCE),str(ROOT/'controls')]
def pins():
    paths=list((ROOT/'source').rglob('*'))+list((ROOT/'controls').glob('*.py'))+[ROOT/'predecessor/run_shortcircuit.py']
    return {str(p.relative_to(ROOT)):{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
            for p in sorted(paths) if p.is_file() for b in [p.read_bytes()]}
before=pins();log=io.StringIO()
import test_dev6_path as T
suite=unittest.defaultTestLoader.loadTestsFromTestCase(T.Dev6PathControl)
result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
after=pins();modules={n:getattr(sys.modules[n],'__file__',None) for n in ['donor_custody','test_dev6_path']}
receipt={'schema':'paid-drd.dev6-path-focused-child.v1','pid':os.getpid(),'ppid':os.getppid(),
 'cwd':os.getcwd(),'python':sys.version,'executable':sys.executable,'argv':sys.argv,
 'imports':modules,'before':before,'after':after,'source_unchanged':before==after,
 'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
 'passed':result.wasSuccessful(),'forbidden_real_import_attempts':blocked,'observations':T.OBSERVATIONS,
 'scope':'One pure wiring/path regression using synthetic cached modules. No real donor, full runner, fixture, sweep, native, learner or corpus execution.'}
dest=ROOT/'records/FOCUSED-01/child';dest.mkdir()
(dest/'stdout.txt').write_text(log.getvalue())
(dest/'RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['pid','tests_run','failures','errors','passed','forbidden_real_import_attempts','source_unchanged']}))
raise SystemExit(0 if result.wasSuccessful() and before==after and not blocked else 1)
