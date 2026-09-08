"""One pure shadow-module regression; no real donor source is imported."""
import ast
import sys
import tempfile
from pathlib import Path
from types import ModuleType
import unittest
import donor_custody as C

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/'source/research/paid-decision-region-v1'
OBSERVATIONS=[]
NAMES=('dev6_arms','run_dev6','dev6')

def wiring(path):
    tree=ast.parse(path.read_bytes(),filename=str(path))
    picked=[]
    for n in tree.body:
        if isinstance(n,ast.Import) and any(a.name=='shortcircuit_parent' for a in n.names): break
        if isinstance(n,ast.Import) and all(a.name in NAMES for a in n.names): picked.append(n)
        elif (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and
              isinstance(n.value.func,ast.Name) and n.value.func.id=='require_module_path'): picked.append(n)
    return ast.fix_missing_locations(ast.Module(body=picked,type_ignores=[]))

class Dev6PathControl(unittest.TestCase):
    def test_cached_shadow_dev6_refuses_before_sweep_use_and_clean_case_passes(self):
        current=wiring(MODULE/'run_shortcircuit.py')
        old=wiring(ROOT/'predecessor/run_shortcircuit.py')
        paths=[n.value.args[2].value for n in current.body if isinstance(n,ast.Expr)]
        self.assertEqual(set(paths),{'research/developmental-spine/'+n+'.py' for n in NAMES})
        self.assertEqual(len(paths),3)
        with tempfile.TemporaryDirectory(dir=ROOT/'records') as temp:
            root=Path(temp); expected={}; shadow=root/'shadow/dev6.py'
            for n in NAMES:
                p=root/'research/developmental-spine'/(n+'.py');p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text('# synthetic data; never executed\n');expected[n]=p
            shadow.parent.mkdir();shadow.write_bytes(expected['dev6'].read_bytes())
            # Identical bytes at the declared path do not establish the cached module's origin.
            self.assertEqual(expected['dev6'].read_bytes(),shadow.read_bytes())
            saved={n:sys.modules.get(n) for n in NAMES}
            def attempt(tree,shadowed):
                checked=[]; consumed=[]
                for n in NAMES:
                    mod=ModuleType(n);mod.__file__=str(shadow if shadowed and n=='dev6' else expected[n])
                    sys.modules[n]=mod
                sys.modules['dev6'].DEV6_PLAN={'sweep':{'origin':'shadow' if shadowed else 'declared'}}
                sys.modules['run_dev6'].SW=sys.modules['dev6'].DEV6_PLAN['sweep']
                def check(mod,r,p):
                    checked.append((mod.__name__,str(Path(mod.__file__).resolve())))
                    C.require_module_path(mod,r,p)
                env={'REPOSITORY_ROOT':root,'require_module_path':check}
                try:
                    # Only the exact import/path-check AST nodes are evaluated, using cached synthetic modules.
                    exec(compile(tree,'<reviewed-import-path-wiring>','exec'),env)
                    consumed.append(env['D6'].SW)
                    return consumed
                finally:
                    OBSERVATIONS.append({'shadowed':shadowed,'checks':checked,'consumed':consumed})
            try:
                self.assertEqual(attempt(old,True),[{'origin':'shadow'}])
                with self.assertRaisesRegex(ValueError,'DONOR_MODULE_PATH_DRIFT:research/developmental-spine/dev6.py'):
                    attempt(current,True)
                self.assertEqual(OBSERVATIONS[-1]['consumed'],[])
                self.assertEqual(attempt(current,False),[{'origin':'declared'}])
                self.assertEqual([x[0] for x in OBSERVATIONS[-1]['checks']],list(NAMES))
            finally:
                for n,mod in saved.items():
                    if mod is None: sys.modules.pop(n,None)
                    else: sys.modules[n]=mod
