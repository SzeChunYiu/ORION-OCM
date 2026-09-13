"""Exact original finite scripts, full receipts, and source-scoped interventions."""
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
PREFIX='research/machine-intelligence-morphogenesis-v1/'
TIP='fc9f6169747cf45dc0562f216d74eae2d0682fdd'
BASE='77968d352141208573b54bc6f1a2980437a49523'
SOURCE_PATHS={
 'upstream':{PREFIX+'GMI_HIERARCHICAL_CHUNKING_THEOREM_V1.md',
  PREFIX+'gmi_microscope/hierarchy_witness.py',PREFIX+'gmi_microscope/hierarchy_phase_sweep.py',
  PREFIX+'microscopes/results/STAGE_HIERARCHY_WITNESS_V1.json',
  PREFIX+'microscopes/results/STAGE_HIERARCHY_PHASE_V1.json'},
 'parents':{'research/gmi-grand-unification-v1/'+name for name in
  ('PROOF_SEARCH_VERIFICATION_REUSE_THEOREM_V1.md','SHARED_DEPENDENCY_MEMORY_REUSE_THEOREM_V1.md',
   'CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md')}|{PREFIX+'DEVELOPMENTAL_QUOTIENT_THEOREM_V1.md'}}


def verified_sources(root=HERE):
    binding=json.loads((root/'SOURCE_BINDINGS_V1.json').read_bytes())
    if binding['tip']!=TIP or binding['base']!=BASE or len(binding['files'])!=9:
        raise ValueError('pinned source boundary changed')
    seen=set();out={}
    for r in binding['files']:
        key=(r['kind'],r['path'])
        if (r['kind'] not in SOURCE_PATHS or r['path'] not in SOURCE_PATHS[r['kind']] or
            r['copy']!='raw/'+r['kind']+'/'+r['path'] or
            r['commit']!=({'upstream':TIP,'parents':BASE}[r['kind']])):
            raise ValueError('source path/commit identity')
        if key in seen:raise ValueError('duplicate source')
        seen.add(key)
        p=root/r['copy'];b=p.read_bytes()
        if p.is_symlink() or len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:
            raise ValueError('source mismatch')
        out[key]=b
    return binding,out


def original_replay():
    binding,sources=verified_sources();results={}
    for stem,receipt in (('hierarchy_witness','STAGE_HIERARCHY_WITNESS_V1.json'),
                         ('hierarchy_phase_sweep','STAGE_HIERARCHY_PHASE_V1.json')):
        source=sources['upstream',PREFIX+'gmi_microscope/'+stem+'.py']
        expected=json.loads(sources['upstream',PREFIX+'microscopes/results/'+receipt])
        with tempfile.TemporaryDirectory(prefix='hierarchy-original-') as tmp:
            root=Path(tmp);(root/'microscopes/results').mkdir(parents=True)
            script=root/(stem+'.py');script.write_bytes(source)
            flags=['-I','-B']+(['-O'] if sys.flags.optimize else [])
            p=subprocess.run([sys.executable,*flags,str(script)],cwd=root,
                             capture_output=True,timeout=180)
            if p.returncode or p.stderr:raise ValueError('original finite script failed')
            actual=json.loads((root/'microscopes/results'/receipt).read_bytes())
        if actual!=expected:raise ValueError('original full receipt mismatch')
        results[stem]=dict(original_payload=actual,original_stdout=p.stdout.decode())
    return dict(sources=binding,results=results)


def source_controls():
    _,sources=verified_sources()
    source=sources['upstream',PREFIX+'gmi_microscope/hierarchy_witness.py']
    tree=ast.parse(source)
    definitions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and
                 n.name in ('cost_with','occurrences')]
    if len(definitions)!=2:raise ValueError('original function identity changed')
    scope={'C_PRIM':1,'U_REF':1,'S_PER':0,'TASKS':{'test':'abcde'},'MULT':{'test':1}}
    exec(compile(ast.Module(body=definitions,type_ignores=[]),'pinned_original_functions','exec'),scope)
    greedy=scope['cost_with'](['abc','ab','cde'])
    overlap=scope['occurrences']('aa','aaa')
    scope.update(S_PER=1,TASKS={'test':'abc'})
    omitted_first=scope['cost_with'](['abc'])
    if (greedy,overlap,omitted_first)!=(3,2,2):raise ValueError('original controls changed')
    return dict(source_greedy=greedy,overlapping_occurrences=overlap,
                source_one_request_cost=omitted_first,pvr_first_use_cost=4,fresh=3,
                source_function_intervention='only explicit TASKS/MULT/C_PRIM/U_REF/S_PER globals')
