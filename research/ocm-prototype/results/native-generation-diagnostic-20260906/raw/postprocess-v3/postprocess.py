"""Additive expansion/admission of two sealed manual-macro outputs; no synthesis."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(candidate, task, macro_record):
    from generation_clia import forms, expand, dump, admit_macros, one, substitute, S
    from clia_grammar import validate
    from clia_tasks import signatures, validate_task
    validate_task(task)
    if macro_record['role'] != 'MANUAL_ENGINEERING_CONTROL_NOT_LEARNED':
        raise ValueError('wrong frozen helper role')
    library = admit_macros(macro_record['definitions'])
    nodes = forms(candidate)
    if len(nodes) == 1 and isinstance(nodes[0], list) and nodes[0] and isinstance(nodes[0][0], list):
        nodes = nodes[0]
    if len(nodes) != 1 or not isinstance(nodes[0], list) or len(nodes[0]) != 5:
        raise ValueError('one complete function required')
    original = nodes[0]

    def binder_free(node):
        if isinstance(node, list):
            if node and str(node[0]) in ('let', 'lam', 'lambda', 'forall', 'exists'):
                raise ValueError('binder-free output required in this narrow bridge')
            for child in node:
                binder_free(child)
    binder_free(original[4])
    used = []
    expanded = [*original[:4], expand(original[4], library, used)]
    text = dump(expanded)
    validate(text, signatures(task))  # unchanged complete grammar/signature guard
    # Independent solver obligation interprets the frozen helper definition.
    helpers = []
    for m in library.values():
        params = [[S('h'+str(i)), S(t)] for i, t in enumerate(m.sorts)]
        frozen = next(x for x in macro_record['definitions'] if x['name']==m.name)
        body = substitute(one(frozen['body']), {'#'+str(i): p[0] for i, p in enumerate(params)})
        helpers.append(dump([S('define-fun'), S(m.name), params, S(m.result), body]))
    left, right = list(original), list(expanded)
    left[1], right[1] = S('POST_ORIGINAL'), S('POST_EXPANDED')
    params = original[2]; args = ' '.join(dump(p[0]) for p in params)
    commands = helpers+[dump(left), dump(right)]+[f'(declare-const {dump(p[0])} Int)' for p in params]
    smt = '\n'.join(commands)+f'\n(assert (not (= (POST_ORIGINAL {args}) (POST_EXPANDED {args}))))\n'
    return {'original_candidate':candidate, 'expanded_candidate':text,
            'macro_calls':used, 'equivalence_smt2':smt,
            'equivalence_sha256':hashlib.sha256(smt.encode()).hexdigest()}


def verify_bindings(manifest):
    for name, b in manifest['bindings'].items():
        if sha(name) != b['sha256'] or Path(name).stat().st_size != b['bytes']:
            raise ValueError('binding drift: '+name)
    root = Path(manifest['capture'])
    if sha(root/'seal.json') != manifest['capture_seal_sha256']:
        raise ValueError('wrong capture seal')
    for name, b in json.loads((root/'seal.json').read_text()).items():
        if sha(root/name) != b['sha256'] or (root/name).stat().st_size != b['bytes']:
            raise ValueError('capture custody drift: '+name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    output = Path(args.output)
    output.mkdir()  # create-only; preserve partial results and refuse reruns
    (output/'manifest.json').write_bytes(Path(args.manifest).read_bytes())
    result = {'scope':manifest['scope'],'manifest_sha256':sha(args.manifest),
              'cases':[],'error':None,'synthesis_calls':0,'discovery_calls':0}
    try:
        verify_bindings(manifest)
        sys.path.insert(0, str(Path(manifest['worktree'])/'research/ocm-prototype'))
        import clia_process
        from clia_checker import check
        task = json.loads(Path(manifest['task']).read_text())
        macro = json.loads(Path(manifest['manual_macro']).read_text())
        root = Path(manifest['capture'])
        for case in manifest['cases']:
            row = {'case':case,'equivalence':None,'specification':None}
            result['cases'].append(row)
            try:
                verify_bindings(manifest)
                process = json.loads((root/case/'result.json').read_text())
                native = json.loads((root/case/'stdout').read_text())
                if process['exit_code'] != 0 or not isinstance(native,dict) or native.get('status') != 'SOLUTION':
                    raise ValueError('no sealed native solution')
                row.update(prepare(native['candidate'],task,macro))
                (output/(case+'-prepared.json')).write_text(json.dumps(row,indent=2)+'\n')
                row['equivalence'] = clia_process.invoke('verify',{'smt2':row['equivalence_smt2']},timeout_ms=5000,deadline_s=10)
                # Separate fixed original specification; never use equivalence as spec authority.
                row['specification'] = check(task,{'status':'SOLUTION','candidate':row['expanded_candidate'],
                    'task_sha256':task['task_sha256'],'grammar_id':task['grammar']['id']},timeout_ms=5000,deadline_s=10)
                row['status'] = 'ADMISSION_CHECKS_PASS' if row['equivalence']['status']=='PASS' and row['specification']['status']=='PASS' else 'CHECKS_NOT_PASSED'
                verify_bindings(manifest)
            except (OSError,ValueError,TypeError,KeyError,IndexError,RecursionError) as exc:
                row.update(status='CANNOT_CHECK',error=type(exc).__name__+': '+str(exc))
            (output/(case+'-receipt.json')).write_text(json.dumps(row,indent=2)+'\n')
    except (OSError,ValueError,TypeError,KeyError) as exc:
        result['error'] = type(exc).__name__+': '+str(exc)
    result['status'] = 'COMPLETE' if len(result['cases'])==2 and not result['error'] else 'INCOMPLETE'
    (output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    seal = {str(p.relative_to(output)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.rglob('*')) if p.is_file()}
    (output/'seal.json').write_text(json.dumps(seal,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'cases':[x.get('status') for x in result['cases']], 'seal_sha256':sha(output/'seal.json')}))
    return 0 if result['status']=='COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
