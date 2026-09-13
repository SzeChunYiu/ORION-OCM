"""Small closed witnesses, plus exact historical countercontrols."""
import importlib.util
from pathlib import Path
from typed_program_v1 import Program, Alias

ROOT = Path(__file__).resolve().parent

def historical():
    path = ROOT / 'raw/grand_gmi_delegation_invariant_cost_checks_v1.py'
    spec = importlib.util.spec_from_file_location('historical_dic', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def wrapper_program(source, partial=False):
    wrapper = 'def f(x):\n    return delegate(x)\n'
    if partial:
        return Program({'main': wrapper, 'parent': source}, {'delegate': Alias('parent')})
    return Program({'main': wrapper, 'delegate': source})

def register():
    old = historical()
    parent = old.REGISTERED['WRITTEN_SHARED_SUM_NET']
    programs = {name: Program({'main': source}) for name, source in old.REGISTERED.items()}
    programs['TRANSPARENT_PYTHON_PARENT'] = wrapper_program(parent)
    programs['TRANSPARENT_PARTIAL_PARENT'] = wrapper_program(parent, True)
    programs['TRANSPARENT_PARTIAL_XOR'] = wrapper_program(old.REGISTERED['WRITTEN_XOR'], True)
    programs['TYPED_GLOBAL_TABLE'] = Program({'main': 'def f(x):\n    a,b,c=x\n    return table[(a<<2)|(b<<1)|c]\n'},
                                           data={'table': (0,1,1,0,1,0,0,1)})
    return old, programs

def expression_census():
    expressions = ['a', '-a', '~a', 'not a', 'a+b', 'a-b', 'a*b', 'a^b',
                   'a&b', 'a|b', 'a<<b', 'a>>b', 'a==b', 'a!=b', 'a<b',
                   'a<=b', 'a>b', 'a>=b', '(a,b,c)[1]', 'int(a>=b)',
                   'sum((a,b,c))', '(a+b)*c', '(a^b)^c', '(0,1)[a]',
                   '3+4', '(-7)*a', 'a<<2', 'int(not a)']
    for expression in expressions:
        yield expression, Program({'main': 'def f(x):\n    a,b,c=x\n    return '+expression+'\n'})
