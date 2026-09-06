"""External sealed-capture validation; no actor, runtime or acquired-program execution."""
import copy
import hashlib
import json
from pathlib import Path
from clia_reuse_study_common import sha, verify_capture_manifest
from grade_clia_reuse import support_state
from grade_clia_reuse_audit import (COUNTS, ORDERS, PHASES, TASKS, check_events, digest,
                                    grade_rows, need, stage_audits, validate_f1)

PROTOCOL_SHA = '619218d6c5a70bc4713c89f388e80e990c571f400c9ef48731fc76c9b7aad556'
PUBLIC_SHA = 'ea1f2074eb404ba3687276183b0b3aedfa85a7190b0e1538a90a3991325faf48'


class Sealed:
    def __init__(self, root):
        self.root = Path(root).resolve(); self.files = verify_capture_manifest(self.root)['files']

    def path(self, relative):
        need(isinstance(relative, str) and not Path(relative).is_absolute() and '..' not in Path(relative).parts and relative in self.files, 'UNSEALED_CONSUMED_FILE')
        path = self.root / relative
        need(path.resolve().is_relative_to(self.root), 'OUTSIDE_CAPTURE')
        need(sha(path) == self.files[relative], 'CONSUMED_FILE_CHANGED')
        return path

    def read(self, relative, lines=False):
        text = self.path(relative).read_text()
        return [json.loads(x) for x in text.splitlines()] if lines else json.loads(text)


def model_archives(sealed, f1, model):
    for arm, binding in f1['arms'].items():
        path = sealed.path(arm + '-state/' + binding['model_file'])
        need(sha(path) == model['sha256'] and path.stat().st_size == model['bytes'], 'FINAL_MODEL_ARCHIVE_CHANGED')


def freezes(sealed):
    f0, f1, receipt = [sealed.read(name + '.json') for name in ('F0', 'F1', 'receipt')]
    need(f0['status'] == 'FROZEN_BEFORE_ACQUISITION', 'F0_STATUS')
    need(f0['protocol_sha256'] == PROTOCOL_SHA == sha(sealed.path(f0['protocol_path'])), 'PROTOCOL_BINDING')
    need(f0['public_requests_sha256'] == PUBLIC_SHA == sha(sealed.path(f0['public_requests_path'])), 'PUBLIC_BINDING')
    protocol = sealed.read(f0['protocol_path']); templates = sealed.read(f0['public_requests_path'], lines=True)
    need(len(templates) == len({i['id'] for i in templates}) == 41, 'PUBLIC_DENOMINATOR')
    need(receipt['f0_sha256'] == f1['f0_sha256'] == sha(sealed.path('F0.json')), 'F0_BINDING')
    need(receipt['f1_sha256'] == sha(sealed.path('F1.json')), 'F1_BINDING')
    need(set(f0['source_archive']) == set(f0['source_files']), 'SOURCE_ARCHIVE_DENOMINATOR')
    for rel, expected in f0['source_files'].items():
        need(sha(sealed.path(f0['source_archive'][rel])) == expected, 'SOURCE_ARCHIVE_CHANGED')
    for rel, expected in f0['protocol_files'].items(): need(sha(sealed.path(rel)) == expected, 'PROTOCOL_FILE_CHANGED')
    model = f0['model']; expected = protocol['model']
    need(model['sha256'] == expected['sha256'] and model['bytes'] == expected['bytes'], 'MODEL_BINDING')
    need(model['manifest_sha256'] == expected['manifest_sha256'] == sha(sealed.path(model['manifest_path'])), 'TRAINING_BINDING')
    need(f0['resources'] == dict(cpu=f0['resources']['cpu'], threads=1, stage_seconds=120, whole_seconds=1800,
                               address_bytes=4294967296) and type(f0['resources']['cpu']) is int, 'RESOURCE_CONTRACT')
    need(len(f0['tasks']) == 2, 'FROZEN_TASKS')
    for task, expected in zip(f0['tasks'], protocol['tasks']):
        need(task['task_sha256'] == digest({k: v for k, v in task.items() if k != 'task_sha256'}) and all(task[k] == expected[k] for k in ('task_id', 'task_sha256')) and hashlib.sha256(task['original_sygus'].encode()).hexdigest() == expected['original_sha256'], 'FROZEN_TASK_BINDING')
    validate_f1(f1); model_archives(sealed, f1, model)
    for arm, bindings in f1['arms'].items():
        need(bindings['model_sha256'] == model['sha256'], 'F1_MODEL_BINDING')
        resolved = copy.deepcopy(templates)
        for item in resolved:
            r = item['request']
            if r['kind'] == 'clia_apply': r['program_id'] = bindings['programs'][r['program_id'][1:]]['descriptor_id']
        need(resolved == f1['resolved_requests'][arm], 'ALIAS_OR_TUPLE_CHANGED')
        for b in bindings['programs'].values():
            need(b['descriptor']['task'] == next(t for t in f0['tasks'] if t['task_id'] == b['task_id']), 'F1_FROZEN_TASK')
            for rel, expected in b['descriptor']['checker_prior']['files'].items():
                need(f0['source_files']['research/ocm-prototype/' + rel] == expected, 'CHECKER_SOURCE_BINDING')
    return f0, f1, receipt


def stage_data(sealed, stage, f0, f1, phase, arm, capture_root):
    need((stage['phase'], stage['arm']) == (phase, arm), 'PROCESS_CADENCE')
    worker = sealed.read(stage['stdout_path']); config = sealed.read(stage['input_path'])
    rows = sealed.read(stage['rows_path'], lines=True); events = sealed.read(stage['events_path'], lines=True)
    process = stage['process']; need(worker == stage['worker'], 'STDOUT_RECEIPT_BINDING')
    need(worker['status'] == 'STAGE_COMPLETED' and process['exit_code'] == 0 and process['timed_out'] is False, 'INCOMPLETE_STAGE')
    need(type(worker['pid']) is int and worker['pid'] > 0 and process['pid'] == worker['pid'], 'PROCESS_ID_BINDING')
    need((worker['phase'], worker['arm']) == (phase, arm) == (config['phase'], config['arm']), 'WORKER_IDENTITY')
    need(worker['ocm_runtime_imported'] is (arm == 'ocm'), 'NATIVE_RUNTIME_CONTAMINATION')
    need(worker['source_files_before'] == worker['source_files_after'] == config['source_files'] == f0['source_files'], 'SOURCE_CHANGED')
    need(worker['f0_sha256'] == config['f0_sha256'] == sha(sealed.path('F0.json')), 'WORKER_F0')
    need(worker['bindings'] == f1['arms'][arm], 'PERSISTENT_BINDINGS_CHANGED')
    need(worker['input_sha256'] == sha(sealed.path(stage['input_path'])), 'INPUT_HASH')
    need(worker['rows_sha256'] == sha(sealed.path(stage['rows_path'])), 'ROW_HASH')
    need(worker['events_sha256'] == sha(sealed.path(stage['events_path'])), 'EVENT_HASH')
    for key in ('stdout', 'stderr'):
        need(process[key + '_sha256'] == sha(sealed.path(stage[key + '_path'])), 'PROCESS_OUTPUT_HASH')
    for key in ('rows', 'events'):
        need(Path(config[key]) == capture_root / stage[key + '_path'], 'OUTPUT_PATH_BINDING')
    need(Path(config['state']) == capture_root / (arm + '-state'), 'STATE_PATH_BINDING')
    need(worker['row_count'] == len(rows) == COUNTS[phase], 'MISSING_OR_EXTRA_ROWS')
    if phase == 'acquire':
        need(config['tasks'] == TASKS and worker['f1_sha256'] is None, 'ACQUISITION_INPUT')
        need(f1['acquisition_receipts'][arm] == process['stdout_sha256'], 'F1_ACQUISITION_BINDING')
        expected = [{'id': 'acquire.' + alias, 'request': {'kind': 'clia', 'task': next(t for t in f0['tasks'] if t['task_id'] == task)}} for alias, task in TASKS.items()]
        for row, item in zip(rows, expected):
            b = f1['arms'][arm]['programs'][item['id'].split('.')[1]]
            need(row['result']['descriptor'] == b['descriptor'], 'ACQUIRED_DESCRIPTOR_BINDING')
            need(len(b['history_records']) == 1, 'ACTUAL_HISTORY_DENOMINATOR'); h = b['history_records'][0]
            path = arm + '-state/' + h['path']; raw = sealed.read(path); history = raw['payload']
            need(sha(sealed.path(path)) == h['file_sha256'] and digest(history) == h['payload_sha256']
                 and raw['record'] == h['record'], 'ACTUAL_HISTORY_RECORD')
            need(history['kind'] == 'ACTUAL_SEARCH_HISTORY' and history['task_sha256'] == b['task_sha256'], 'HISTORY_TASK_BINDING')
            proposal = row['result']['result']['proposal' if arm == 'native' else 'answer']
            need(history['proposal_sha256'] == digest(proposal), 'HISTORY_PROPOSAL_BINDING')
            start, end = row['event_range']
            need(history['invocations'] == [e for e in worker['invocations'][start:end] if e['action'] == 'synthesize'], 'HISTORY_INVOCATION_BINDING')
    else:
        need(worker['f1_sha256'] == config['f1_sha256'] == sha(sealed.path('F1.json')), 'WORKER_F1')
        need(config['bindings_sha256'] == digest(f1['arms'][arm]), 'BINDINGS_HASH')
        expected = [i for i in f1['resolved_requests'][arm] if i['id'].startswith(phase + '.')]
        need(config['items'] == expected, 'WORKER_REQUESTS')
    need([{'id': r['id'], 'request': r['request']} for r in rows] == expected, 'ROW_REQUEST_BINDING')
    need(all((r['arm'], r['phase']) == (arm, phase) for r in rows), 'ROW_ARM_PHASE')
    started = [e['record']['index'] for e in events if e['event'] == 'started']
    finished = {e['record']['index']: e['record'] for e in events if e['event'] == 'finished'}
    need(len(events) == 2 * len(worker['invocations']) and started == list(range(len(worker['invocations'])))
         and finished == {e['index']: e for e in worker['invocations']}, 'RAW_INVOCATION_LOG')
    check_events(worker, rows, phase)
    return worker, rows


def collect(root, observed):
    """Raises on custody/completeness failure; already checked observations stay diagnostic."""
    sealed = Sealed(root); f0, f1, receipt = freezes(sealed)
    observed['receipt_status'] = receipt['status']; observed['resource_capture'] = {
        k: receipt.get(k) for k in ('outer_wall_s', 'complete_tree_cpu_verified', 'state_bytes')}
    capture_root = Path(receipt['capture_root'])
    need(capture_root.is_absolute() and '..' not in capture_root.parts, 'CAPTURE_ROOT')
    previous = {'native': None, 'ocm': None}; pids = set()
    need(len(receipt['stages']) == 12, 'INCOMPLETE_PROCESS_DENOMINATOR')
    for stage, (phase, arm) in zip(receipt['stages'], [(p, a) for p, order in zip(PHASES, ORDERS) for a in order]):
        worker, rows = stage_data(sealed, stage, f0, f1, phase, arm, capture_root)
        need(worker['pid'] not in pids, 'PROCESS_NOT_FRESH'); pids.add(worker['pid'])
        previous[arm] = stage_audits(worker, f1['arms'][arm], phase, previous[arm])
        observed['resources'].append({'arm': arm, 'phase': phase, 'process': stage['process'],
            **{k: worker.get(k) for k in ('cpu', 'worker_wall_s', 'state_bytes', 'self_peak_rss_kib', 'reaped_children_peak_rss_kib')}})
        observed['stages_checked'] += 1
        observed['audits'].append({'arm': arm, 'phase': phase, 'points': {
            point: {'records': len(worker[point]['records']),
                'registration_descendants': [k for k, r in worker[point]['records'].items() if support_state(r['support'], f1['arms'][arm]['programs']['max3']['registration']) == 'DEAD'],
                'unaffected_records': [k for k, r in worker[point]['records'].items() if support_state(r['support'], f1['arms'][arm]['programs']['max3']['registration']) == 'LIVE'],
                'programs': {k: p['liveness'] for k, p in worker[point]['programs'].items()}, 'model': worker[point]['model_liveness'], 'liveness_counts': {
                state: sum(r['liveness'] == state for r in worker[point]['records'].values()) for state in ('LIVE', 'DEAD', 'UNKNOWN')}}
            for point in ('exit_query_audit', 'final_audit')}})
        observed['invocations'].extend({'arm': arm, 'phase': phase, **e} for e in worker['invocations'])
        if phase != 'acquire':
            math, syntax = grade_rows(worker, rows, f1['arms'][arm])
            observed['arms'][arm]['math'].extend(math); observed['arms'][arm]['syntax'].extend(syntax)
    need(receipt['status'] == 'EXECUTED_NOT_GRADED', 'CAPTURE_INCOMPLETE')
    return f0
