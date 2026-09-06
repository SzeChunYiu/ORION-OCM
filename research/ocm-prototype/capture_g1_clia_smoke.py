"""Reproducible public CLIA-only G1 smoke; INVALID_MODEL_BYTES, never syntax."""
import argparse, hashlib, json, os, resource, subprocess, sys, tempfile, time
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_audit(repo):
    git = ['/usr/bin/git', '-C', str(repo)]
    tree = subprocess.check_output(git + ['rev-parse', 'HEAD:src'], text=True).strip()
    records = subprocess.check_output(git + ['ls-tree', '-r', '-z', 'HEAD', '--', 'src']).split(b'\0')
    changed = []; count = 0
    for record in records:
        if not record:
            continue
        metadata, name = record.split(b'\t', 1); _, kind, oid = metadata.split()
        if kind != b'blob':
            continue
        path = repo / name.decode(); raw = path.read_bytes(); count += 1
        actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if actual != oid.decode():
            changed.append(name.decode())
    status = subprocess.check_output(git + ['status', '--porcelain=v1', '-z', '--', 'src'])
    raw_diff = subprocess.check_output(git + ['diff', '--raw', '--', 'src'])
    return {'head_src_tree': tree, 'tracked_blobs': count, 'changed_blobs': changed,
            'status_bytes': len(status), 'raw_diff_bytes': len(raw_diff),
            'matches_head': not changed and not status and not raw_diff}


def child(args, cwd, deadline):
    start = time.perf_counter(); before = resource.getrusage(resource.RUSAGE_CHILDREN)
    process = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=deadline)
    except subprocess.TimeoutExpired:
        process.kill(); stdout, stderr = process.communicate(); timed_out = True
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    result = {'pid': process.pid, 'exit_code': process.returncode, 'external_timeout': timed_out,
              'stdout': stdout, 'stderr': stderr, 'wall_s': time.perf_counter() - start,
              'terminated_child_cpu_s': after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime}
    try:
        result['result'] = json.loads(stdout)
    except ValueError:
        result['result'] = None
    return result


def main(repo, parent, deadline):
    start = time.perf_counter(); cpu = time.process_time(); before = resource.getrusage(resource.RUSAGE_CHILDREN)
    base = repo / 'research/ocm-prototype'; sys.path.insert(0, str(base))
    from clia_tasks import load_task
    from g1_vessel import identities
    parent.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='G1-INVALID_MODEL-CLIA-SMOKE-', dir=parent))
    state = out / 'state'; model = out / 'INVALID_MODEL_BYTES.udpipe'
    model.write_bytes(b'INVALID_MODEL_BYTES\nCLIA_ONLY_SMOKE_NO_SYNTAX_QUERY\n')
    source_before = identities(); production_before = source_audit(repo)
    commands = [{'action': 'setup', 'model': str(model), 'training_manifest': {
        'classification': 'INVALID_MODEL_BYTES_ONLY_CLIA_PLUMBING_SMOKE',
        'training_executed': False, 'syntax_never_queried': True}}]
    names = ['jmbl_fg_max3', 'jmbl_fg_array_search_4', 'jmbl_fg_mpg_guard2',
             'jmbl_fg_max10', 'jmbl_fg_array_search_10']
    commands += [{'action': 'query', 'request': {'kind': 'clia', 'task': load_task(name)}} for name in names]
    rows = []
    for index, command in enumerate(commands):
        row = child([sys.executable, str(base / 'g1_vessel.py'), str(state), json.dumps(command)], repo, deadline)
        row.update(index=index, command=command); rows.append(row)
        (out / f'worker-{index}.json').write_text(json.dumps(row, indent=2) + '\n')
        value = row['result'] or {}
        print(index, command['action'], value.get('status'), value.get('solve_status'), flush=True)
        if row['exit_code'] or row['external_timeout']:
            break
    queries = [r['result'] for r in rows[1:] if isinstance(r['result'], dict)]
    ids = [r['admitted_id'] for r in queries if r.get('admitted_id')]
    audit_code = ('import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);'
                  'from g1_vessel import CONFIG;from ocm.runtime.ocm_runtime import OCMRuntime;'
                  'r=OCMRuntime(Path(sys.argv[2]),config=CONFIG);'
                  'print(json.dumps({a:r.state.ks.atom_map()[a].liveness(r.state.revoked).value for a in json.loads(sys.argv[3])}))')
    reload = child([sys.executable, '-c', audit_code, str(base), str(state), json.dumps(ids)], repo, deadline)
    production_after = source_audit(repo); source_after = identities()
    stages = ['TASK', 'GROUNDING', 'REPRESENTATION', 'NAVIGATION', 'EXTRACTION', 'EXECUTION', 'COMPOSITION', 'CHECK', 'DECISION', 'COMMITMENT']
    checks = {
        'five_admitted': len(queries) == 5 and all(r.get('status') == 'ADMITTED' and r.get('solve_status') == 'ANSWER' and r.get('admitted_id') and r.get('answer') is not None for r in queries),
        'fresh_processes': len(rows) == 6 and len({r['pid'] for r in rows} | {reload['pid']}) == 7,
        'ten_stage_pass': all([s['stage'] for s in r['trace']['stages']] == stages and all(s['status'] == 'PASS' for s in r['trace']['stages']) for r in queries),
        'full_catalogue': all(r['catalogue'] == ['syntax:udpipe1', 'procedure:cvc5'] for r in queries),
        'procedural_only': all(r['selected'] == 'procedure:cvc5' and r['claim'] == 'SPECIFICATION_VERIFIED_PROGRAM' for r in queries),
        'independent_checks_twice': all([(c['phase'],c.get('grammar'),c.get('semantic'),c.get('solver_result')) for c in r['checks'] if c['operator'] == 'procedure:cvc5'] == [('solve','PASS','PASS','unsat'),('admission','PASS','PASS','unsat')] for r in queries),
        'pure_and_same_source': source_before == source_after and len({r['source_identity'] for r in queries}) == 1 and all(r['pure_proposals'] for r in queries),
        'all_live_after_reload': len(ids) == 5 and reload['result'] == dict.fromkeys(ids, 'LIVE'),
        'production_source_matches_head': production_before['matches_head'] and production_after['matches_head'],
    }
    files = {str(p.relative_to(out)): {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in out.rglob('*') if p.is_file()}
    archive = {k: v for k, v in files.items() if k.startswith('state/archive/')}
    checks['single_invalid_archive'] = len(archive) == 1 and sum(x['bytes'] for x in archive.values()) == model.stat().st_size
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = {'classification': 'CLIA_ONLY_INTEGRATION_SMOKE_INVALID_MODEL_BYTES', 'syntax_executed': False,
        'source_head': subprocess.check_output(['/usr/bin/git','-C',str(repo),'rev-parse','HEAD'], text=True).strip(),
        'source_before': source_before, 'source_after': source_after, 'production_before': production_before,
        'production_after': production_after, 'capture_sha256': sha(Path(__file__)), 'rows': rows, 'reload': reload,
        'checks': checks, 'passed': all(checks.values()), 'files': files, 'archive': archive,
        'durable_state_bytes': sum(v['bytes'] for k,v in files.items() if k.startswith('state/')),
        'wall_s': time.perf_counter()-start, 'host_cpu_s': time.process_time()-cpu,
        'terminated_child_cpu_s': after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
        'measurement_scope': 'Serial harness main envelope includes fixture preparation, source checks, six fresh worker processes, all their replay/donor/check/persist work, final fresh reload and artifact hashing. Excludes harness interpreter startup, dependency installation/development, energy and final receipt serialization.',
        'admission_failure_control_scope': {'status': 'NOT_EXERCISED' if all(r.get('admitted_id') for r in queries) else 'OBSERVED', 'answer_exposure_violations': sum(r.get('answer') is not None for r in queries if not r.get('admitted_id')), 'note': 'Root unit tests exercise failed-admission suppression; this positive smoke does not count a vacuous condition as an executed control.'}}
    path = out / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'receipt': str(path), 'sha256': sha(path), 'passed': receipt['passed'], 'checks': checks}), flush=True)
    return 0 if receipt['passed'] else 1

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--out-parent',type=Path,required=True);parser.add_argument('--deadline-s',type=float,default=60)
    args=parser.parse_args();sys.exit(main(args.repo.resolve(),args.out_parent.resolve(),args.deadline_s))
