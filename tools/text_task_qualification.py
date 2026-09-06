"""Additive text-task source closure, environment, archive and execution checks."""
from __future__ import annotations
import ast
from collections import Counter
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
import runtime_revision_receipts_v4 as V4

TESTS = ('tests/integration/test_text_task_slice.py','tests/integration/test_text_task_binding.py')
MINIMUM_TESTS = 29
MINIMUM_BY_FILE = dict(zip(TESTS,(21,8)))
PINS = {'pytest':'8.3.5','cvc5':'1.3.4','z3-solver':'5.1.0.0','sexpdata':'1.0.2'}
PROTO = 'research/ocm-prototype'


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def donor_inventory(root):
    """Resolve local imports statically; subprocess worker and fixture registry are explicit roots."""
    root=Path(root);base=root/PROTO;pending=[base/'text_task_slice.py',base/'clia_worker.py'];seen=set()
    while pending:
        path=pending.pop()
        if path in seen:continue
        if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
            raise ValueError('unsafe donor source path')
        seen.add(path)
        tree=ast.parse(path.read_text())
        modules=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):modules.extend(a.name for a in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:
                modules.append(node.module)
                modules.extend(node.module+'.'+a.name for a in node.names)
        for module in modules:
            local=base.joinpath(*module.split('.'))
            for child in (local.with_suffix('.py'),local/'__init__.py'):
                if child.is_file():pending.append(child)
    manifest=base/'clia_fixtures/manifest.json';seen.add(manifest)
    seen.add(base/'requirements-g1.txt')
    for fixture in json.loads(manifest.read_text())['fixtures'].values():
        path=base/'clia_fixtures'/fixture['file']
        if path.is_symlink() or not path.resolve().is_relative_to((base/'clia_fixtures').resolve()):
            raise ValueError('unsafe fixture source path')
        if sha(path)!=fixture['sha256']:raise ValueError('fixture source binding changed')
        seen.add(path)
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(seen)}


def git_identity(root):
    return {name:subprocess.check_output(['/usr/bin/git','-C',str(root),'rev-parse',ref],text=True).strip()
            for name,ref in [('head','HEAD'),('tree','HEAD^{tree}')]}


def environment():
    files={Path(sys.executable).resolve()}
    for name,want in PINS.items():
        dist=metadata.distribution(name)
        if dist.version!=want:raise ValueError('required dependency version mismatch: '+name)
        files.update(Path(dist.locate_file(f)) for f in dist.files or []
                     if '__pycache__' not in str(f) and (str(f).endswith(('.py','METADATA','RECORD','WHEEL')) or '.so' in str(f)))
    return {'python':sys.version,'executable':sys.executable,'resolved_executable':str(Path(sys.executable).resolve()),
            'required_versions':PINS,'installed_versions':{d.metadata['Name']:d.version for d in metadata.distributions()},
            'dependency_files':{str(p):sha(p) for p in sorted(files) if p.is_file()}}


def snapshot(root):
    inventory=V4.source_inventory(Path(root))
    return {'root_source_inventory':inventory,'root_source_id':identity(inventory),
            'donor_inventory':donor_inventory(root),'git':git_identity(root),'environment':environment()}


def archive(root,path,state):
    inventory={**state['root_source_inventory'],**state['donor_inventory']}
    with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED) as out:
        for name,expected in sorted(inventory.items()):
            data=(Path(root)/name).read_bytes()
            if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('source changed before archive')
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            out.writestr(info,data)
    verify_archive(path,state)


def verify_archive(path,state):
    inventory={**state['root_source_inventory'],**state['donor_inventory']}
    with zipfile.ZipFile(path) as archive:
        if Counter(archive.namelist())!=Counter(inventory.keys()):raise ValueError('archive inventory mismatch')
        if any(hashlib.sha256(archive.read(n)).hexdigest()!=v for n,v in inventory.items()):
            raise ValueError('archive content mismatch')
    return True


def validate_execution(output):
    output=Path(output);trace=json.loads((output/'pytest-trace.json').read_text())
    nodes=trace['collected']
    if (len(nodes)<MINIMUM_TESTS or len(set(nodes))!=len(nodes)
            or any(n.split('::',1)[0] not in TESTS for n in nodes) or trace['exit_status']!=0):
        raise ValueError('wrong or incomplete donor collection')
    per_file=Counter(n.split('::',1)[0] for n in nodes)
    if any(per_file[path]<minimum for path,minimum in MINIMUM_BY_FILE.items()):
        raise ValueError('each registered donor test file must meet its own minimum')
    expected=Counter((n,phase,'passed') for n in nodes for phase in ('setup','call','teardown'))
    if Counter((r['nodeid'],r['when'],r['outcome']) for r in trace['reports'])!=expected:
        raise ValueError('every collected donor test must actually pass all phases without skips')
    report=ET.parse(output/'junit.xml');suites=list(report.iter('testsuite'));cases=list(report.iter('testcase'))
    counts={k:sum(int(s.attrib[k]) for s in suites) for k in ('tests','failures','errors','skipped')}
    names=Counter((p[:-3].replace('/','.'),n) for p,n in (node.split('::',1) for node in nodes))
    if (not suites or counts['tests']!=len(nodes) or len(cases)!=len(nodes)
            or any(counts[k] for k in ('failures','errors','skipped'))
            or Counter((c.get('classname'),c.get('name')) for c in cases)!=names
            or any(c.find(tag) is not None for c in cases for tag in ('failure','error','skipped'))):
        raise ValueError('JUnit does not match the actual passing donor test inventory')
    return counts
