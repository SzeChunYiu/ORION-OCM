"""Load old/corrected source closures under disjoint package identities."""
from pathlib import Path
import hashlib
import importlib
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parent

def require(condition,message):
    if not condition: raise ValueError(message)

def source_modules(version):
    require(version in ('old','corrected'),'unknown source version')
    if version=='old': path=ROOT/'raw/pr551-grad-audit-20260913/raw/gmi_microscope'
    else: path=ROOT/'corrected_source/gmi_microscope'
    name='gradient_adjoint_'+version
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    return tuple(importlib.import_module(name+'.'+part) for part in ('core','bases','morph','vm'))

def verify_corrected_sources():
    binding=json.loads((ROOT/'SOURCE_BINDINGS_V1.json').read_text())
    for name,row in binding['corrected_files'].items():
        data=(ROOT/name).read_bytes()
        require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'], 'corrected source drift')
    old=ROOT/'raw/pr551-grad-audit-20260913/raw/gmi_microscope'
    new=ROOT/'corrected_source/gmi_microscope'
    for name in ('__init__.py','core.py','bases.py','morph.py'):
        require((old/name).read_bytes()==(new/name).read_bytes(),'unrelated source changed')
    expected=(old/'vm.py').read_text().replace(
        '            w = Val(M.read(n)); prod = M.op("MUL", w.v, xv.v)',
        '            w = Val(M.read(n), [("param", n)] if tape else None); prod = M.op("MUL", w.v, xv.v)'
    ).replace('            if tape: pv.parents.append(("param", n))\n','')
    require((new/'vm.py').read_text()==expected,'repair exceeds parameter-marker change')
    return binding
